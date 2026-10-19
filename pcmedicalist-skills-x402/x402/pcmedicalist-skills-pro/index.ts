type BankrX402Files = {
  readJson<T = unknown>(path: string): Promise<T>;
  writeJson(path: string, value: unknown, opts?: { pretty?: boolean }): Promise<{ path: string }>;
};
type HandlerCtx = { files?: BankrX402Files };

async function recordReceipt(files: BankrX402Files | undefined, svc: string, amountUsdc: string, req: Request): Promise<void> {
  if (!files) return;
  const payer = req.headers.get("x-402-payer");
  const receipt = { ts: new Date().toISOString(), endpoint: svc, payer, amountUsdc, note: "settled via Bankr x402" };
  try {
    const existing = (await files.readJson<{ receipts: any[] }>("/x402/" + svc + "/receipts.json").catch(() => ({ receipts: [] as any[] }))) ?? { receipts: [] };
    existing.receipts.push(receipt);
    if (existing.receipts.length > 500) existing.receipts = existing.receipts.slice(-500);
    await files.writeJson("/x402/" + svc + "/receipts.json", existing, { pretty: true });
  } catch {}
}

// PCMedicalist PRO bundle — catalog/orchestration layer for all 11 platform-engineering skills.
// Tier: PRO | Price: 4.0 USDC | Network: base
//
// Design: PRO does NOT duplicate skill bodies (that blew Bankr's handler-source cap). Instead it
// returns a curated manifest: each entry links to its live x402 endpoint + public repo so the caller
// fetches the exact skill body on demand. This is the intended PRO shape — one paid call that unlocks
// the full routing map + every endpoint URL.

const WALLET = "0xd8f369f47eba08c29a024b64a52d2bbedbe252b0";
const ENDPOINT_BASE = `https://x402.bankr.bot/${WALLET}`;
const REPO_BASE = "https://github.com/PCMedicalist";

// name -> { priceUsdc, repo, blurb }
const CATALOG: Record<string, { priceUsdc: number; repo: string; blurb: string }> = {
  "pcmedicalist-skills-discovery": {
    priceUsdc: 0,
    repo: `${REPO_BASE}/pcmedicalist-skills-discovery`,
    blurb: "FREE catalog of all PCMedicalist platform-engineering skills: tiers, prices, public repo URLs.",
  },
  "pcmedicalist-security-fundamentals": {
    priceUsdc: 0.5,
    repo: `${REPO_BASE}/pcmedicalist-security-fundamentals`,
    blurb: "26-topic security reference (access-control, auth, crypto, validation, supply-chain).",
  },
  "pcmedicalist-database-deep-dive": {
    priceUsdc: 0.5,
    repo: `${REPO_BASE}/pcmedicalist-database-deep-dive`,
    blurb: "PostgreSQL/Redis operational depth: indexing, N+1, pooling, migrations, locking, sharding.",
  },
  "pcmedicalist-distributed-patterns": {
    priceUsdc: 0.4,
    repo: `${REPO_BASE}/pcmedicalist-distributed-patterns`,
    blurb: "Sagas, distributed locks, idempotency, leader election, 2PC, partition handling.",
  },
  "pcmedicalist-resilience-engineering": {
    priceUsdc: 0.4,
    repo: `${REPO_BASE}/pcmedicalist-resilience-engineering`,
    blurb: "Circuit breakers, bulkheads, backpressure, timeouts, retries, chaos drills, error budgets.",
  },
  "pcmedicalist-caching-strategies": {
    priceUsdc: 0.4,
    repo: `${REPO_BASE}/pcmedicalist-caching-strategies`,
    blurb: "Cache hierarchies, invalidation, CDN/edge patterns, stampede protection, consistency.",
  },
  "pcmedicalist-http-protocol": {
    priceUsdc: 0.4,
    repo: `${REPO_BASE}/pcmedicalist-http-protocol`,
    blurb: "HTTP/1.1-3 semantics, status codes, headers, methods, content-negotiation, connections.",
  },
  "pcmedicalist-networking-infra": {
    priceUsdc: 0.4,
    repo: `${REPO_BASE}/pcmedicalist-networking-infra`,
    blurb: "DNS, reverse proxies, subnets, NAT, service meshes, single-host-to-cloud topology.",
  },
  "pcmedicalist-infrastructure-ops": {
    priceUsdc: 0.5,
    repo: `${REPO_BASE}/pcmedicalist-infrastructure-ops`,
    blurb: "PM2/nginx deploys, rsync delivery, GitHub Actions CI, secret hygiene, scale target practice.",
  },
  "pcmedicalist-messaging-semantics": {
    priceUsdc: 0.4,
    repo: `${REPO_BASE}/pcmedicalist-messaging-semantics`,
    blurb: "Message-queue, pub/sub, event-driven and dead-letter semantics with delivery guarantees.",
  },
  "pcmedicalist-event-driven-architecture": {
    priceUsdc: 0.4,
    repo: `${REPO_BASE}/pcmedicalist-event-driven-architecture`,
    blurb: "Event sourcing, CQRS, streaming topology, choreography vs orchestration.",
  },
  "pcmedicalist-platform-engineering-index": {
    priceUsdc: 0,
    repo: `${REPO_BASE}/pcmedicalist-platform-engineering-index`,
    blurb: "Master index routing topics to all PCMedicalist platform-engineering skills (FREE).",
  },
};

export default async function handler(_req: Request, ctx?: HandlerCtx): Promise<Response> {
  await recordReceipt(ctx?.files, "pcmedicalist-skills-pro", "4.00", _req);

  const entries = Object.entries(CATALOG).map(([name, meta]) => ({
    name,
    tier: name === "pcmedicalist-skills-pro" ? "PRO" : "STANDARD",
    priceUsdc: meta.priceUsdc,
    endpoint: `${ENDPOINT_BASE}/${name}`,
    repo: meta.repo,
    blurb: meta.blurb,
  }));

  return Response.json({
    provider: "PCMedicalist",
    tier: "PRO",
    license: "CC-BY-4.0",
    attribution: "PCMedicalist",
    wallet: WALLET,
    note: "PRO unlocks the full routing map. Call each `endpoint` to fetch that skill's full body on demand (per-skill price applies).",
    count: entries.length,
    skills: entries,
  });
}
