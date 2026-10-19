#!/usr/bin/env python3
"""
PCMedicalist x402 Skills — Receipts Ledger (local, durable).

Records every settled x402 payment for the PCMedicalist skills endpoints.
Source of truth for "receipts logs": each entry is a canonical receipt.

Feeding it:
  1. From a per-call payment object (bankr x402 call returns `payment`):
        ledger.record(payment_obj, product="pcmedicalist-security-fundamentals")
  2. From bankr x402 revenue (aggregate):
        ledger.reconcile(revenue_json)
  3. Query:
        ledger.query(wallet="0x...", tier="PRO")

Storage: SQLite (receipts.db) + JSONL (receipts.jsonl) — both on a persistent
path, NOT /tmp.
"""
import json, os, sqlite3, hashlib, uuid
from datetime import datetime, timezone

LEDGER_DIR = os.environ.get("PCMEDICALIST_LEDGER_DIR", "/home/pcmedicalist/pcmedicalist/pcmedicalist-skills-x402/.ledger")
DB = os.path.join(LEDGER_DIR, "receipts.db")
JSONL = os.path.join(LEDGER_DIR, "receipts.jsonl")

os.makedirs(LEDGER_DIR, exist_ok=True)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS receipts (
    receipt_id      TEXT PRIMARY KEY,
    product         TEXT NOT NULL,
    network         TEXT NOT NULL,
    payer           TEXT,
    payee           TEXT,
    amount_micro    INTEGER,
    amount_usdc     REAL,
    tx_hash         TEXT,
    status          TEXT,
    issued_at       TEXT,
    raw             TEXT
);
CREATE INDEX IF NOT EXISTS idx_payer ON receipts(payer);
CREATE INDEX IF NOT EXISTS idx_product ON receipts(product);
"""


def _conn():
    c = sqlite3.connect(DB)
    c.executescript(_SCHEMA)
    return c


def _canonical_payment(payment: dict, product: str) -> dict:
    """Normalize a bankr/payment object (or bankr x402 call payment) into a receipt."""
    amount_micro = int(payment.get("amount") or payment.get("value") or 0)
    # bankr returns amount in USDC micro (6 decimals) typically
    return {
        "receipt_id": payment.get("receiptId") or payment.get("id") or f"rcpt_{uuid.uuid4().hex}",
        "product": product,
        "network": payment.get("network") or payment.get("chainId") or "base",
        "payer": payment.get("from") or payment.get("payer") or payment.get("sender"),
        "payee": payment.get("to") or payment.get("payee") or payment.get("recipient"),
        "amount_micro": amount_micro,
        "amount_usdc": round(amount_micro / 1_000_000, 6) if amount_micro else float(payment.get("amountUsdc") or payment.get("usdc") or 0),
        "tx_hash": payment.get("txHash") or payment.get("hash") or payment.get("transactionHash"),
        "status": payment.get("status") or "settled",
        "issued_at": payment.get("timestamp") or payment.get("createdAt") or datetime.now(timezone.utc).isoformat(),
        "raw": json.dumps(payment),
    }


def record(payment: dict, product: str) -> dict:
    r = _canonical_payment(payment, product)
    c = _conn()
    c.execute(
        "INSERT OR REPLACE INTO receipts VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (r["receipt_id"], r["product"], r["network"], r["payer"], r["payee"],
         r["amount_micro"], r["amount_usdc"], r["tx_hash"], r["status"], r["issued_at"], r["raw"]),
    )
    c.commit(); c.close()
    with open(JSONL, "a", encoding="utf-8") as f:
        f.write(json.dumps(r) + "\n")
    return r


def reconcile(revenue: dict):
    """revenue from `bankr x402 revenue` is aggregate; store a daily rollup receipt."""
    rows = revenue.get("services") or revenue.get("items") or []
    recs = []
    for s in rows:
        recs.append(record({
            "id": f"rev_{s.get('name')}_{datetime.now(timezone.utc).date()}",
            "amount": int(float(s.get("revenueUsdc", 0)) * 1_000_000),
            "amountUsdc": s.get("revenueUsdc", 0),
            "from": "aggregate",
            "to": revenue.get("payee"),
            "status": "reconciled",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }, product=s.get("name", "unknown")))
    return recs


def query(wallet=None, product=None, tier=None) -> list:
    c = _conn()
    sql = "SELECT receipt_id,product,network,payer,payee,amount_usdc,tx_hash,status,issued_at FROM receipts WHERE 1=1"
    args = []
    if wallet:
        sql += " AND payer=?"; args.append(wallet)
    if product:
        sql += " AND product=?"; args.append(product)
    sql += " ORDER BY issued_at DESC"
    rows = c.execute(sql, args).fetchall(); c.close()
    return [dict(zip(["receipt_id","product","network","payer","payee","amount_usdc","tx_hash","status","issued_at"], r)) for r in rows]


def totals() -> dict:
    c = _conn()
    total_usdc = c.execute("SELECT COALESCE(SUM(amount_usdc),0) FROM receipts").fetchone()[0]
    n = c.execute("SELECT COUNT(*) FROM receipts").fetchone()[0]
    by_product = dict(c.execute("SELECT product, COALESCE(SUM(amount_usdc),0) FROM receipts GROUP BY product").fetchall())
    c.close()
    return {"count": n, "total_usdc": round(total_usdc, 6), "by_product": by_product}


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "totals":
        print(json.dumps(totals(), indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == "query":
        print(json.dumps(query(wallet=sys.argv[2] if len(sys.argv) > 2 else None), indent=2))
    else:
        print(json.dumps(totals(), indent=2))
