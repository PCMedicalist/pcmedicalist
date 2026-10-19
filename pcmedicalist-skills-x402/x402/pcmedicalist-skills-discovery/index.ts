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

// FREE discovery endpoint — no payment required.
// Lists every PCMedicalist platform-engineering skill with its tier + price.
const SKILLS = [
  { slug: "pcmedicalist-security-fundamentals", tier: "STANDARD", priceUsdc: 0.50, topics: 26 },
  { slug: "pcmedicalist-database-deep-dive", tier: "STANDARD", priceUsdc: 0.50, topics: 29 },
  { slug: "pcmedicalist-distributed-patterns", tier: "STANDARD", priceUsdc: 0.40, topics: 8 },
  { slug: "pcmedicalist-resilience-engineering", tier: "STANDARD", priceUsdc: 0.40, topics: 9 },
  { slug: "pcmedicalist-caching-strategies", tier: "STANDARD", priceUsdc: 0.40, topics: 9 },
  { slug: "pcmedicalist-http-protocol", tier: "STANDARD", priceUsdc: 0.40, topics: 12 },
  { slug: "pcmedicalist-networking-infra", tier: "STANDARD", priceUsdc: 0.40, topics: 6 },
  { slug: "pcmedicalist-infrastructure-ops", tier: "STANDARD", priceUsdc: 0.50, topics: 14 },
  { slug: "pcmedicalist-messaging-semantics", tier: "STANDARD", priceUsdc: 0.40, topics: 7 },
  { slug: "pcmedicalist-event-driven-architecture", tier: "STANDARD", priceUsdc: 0.40, topics: 11 },
  { slug: "pcmedicalist-platform-engineering-index", tier: "FREE", priceUsdc: 0.0, topics: 11 },
];

export default async function handler(_req: Request, ctx?: HandlerCtx): Promise<Response> {
  await recordReceipt(ctx?.files, "pcmedicalist-skills-discovery", "0.01", _req);

  return Response.json({
    provider: "PCMedicalist",
    network: "base",
    currency: "USDC",
    tiers: {
      FREE: "discovery + index only",
      STANDARD: "individual skill SKILL.md fetch (paid per call)",
      PRO: "all 11 skills as a bundle (paid per call)",
    },
    skills: SKILLS,
    bundle: { slug: "pcmedicalist-skills-pro", tier: "PRO", priceUsdc: 4.0 },
    publicRepos: SKILLS.map((s) => `https://github.com/PCMedicalist/${s.slug}`),
  });
}
