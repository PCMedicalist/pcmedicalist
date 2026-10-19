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

// PCMedicalist skill endpoint — pcmedicalist-platform-engineering-index
// Tier: FREE | Price: 0.0 USDC | Network: base (USDC, mainnet)
const SKILL_MD = `---
name: pcmedicalist-platform-engineering-index
description: Master index mapping all 198 platform-engineering topics to the PCMedicalist skill that owns each — security, database, distributed, resilience, caching, HTTP, networking, ops, and messaging.
version: 1.0.0
author: PCMedicalist
license: CC-BY-4.0 (PCMedicalist attribution required)
metadata:
  hermes:
    tags: [index, reference, platform-engineering, enterprise, pcmedicalist]
    related_skills: [pcmedicalist-security-fundamentals, pcmedicalist-database-deep-dive, pcmedicalist-distributed-patterns, pcmedicalist-resilience-engineering, pcmedicalist-caching-strategies, pcmedicalist-http-protocol, pcmedicalist-networking-infra, pcmedicalist-infrastructure-ops, pcmedicalist-messaging-semantics]
---

# PCMedicalist Platform Engineering Index (198 Topics)

## When to Use
- You have one of the 198 checklist items and need the owning skill fast.
- Auditing PCMedicalist coverage across security / data / distributed / resilience / caching / HTTP / networking / ops / messaging.
- Onboarding an agent to the full engineering discipline (every item → a skill).
- Verifying a system before a release or incident review.

## How to Use
1. Find your item # in the table below.
2. Load the named skill: \`skill_view(name='<skill>')\`.
3. Each skill follows: **Threat/Why → Pattern → Validate → Fix** and has a per-topic Validation Checklist.
4. If an item shows "(existing)" it was already covered before this 9-skill build; the 9 new skills fill the remaining gaps.

## Coverage Summary
- **New skills (this build): 9** — security-fundamentals, database-deep-dive, distributed-patterns, resilience-engineering, caching-strategies, http-protocol, networking-infra, infrastructure-ops, messaging-semantics.
- **Pre-existing skills: ~90** — security (sql-injection, xss, csrf, cors-policy, ssrf, secret-hygiene, jwt-rotation, oauth, webhooks-hmac, tls-termination, encryption-at-rest, encryption-in-transit, waf-ddos, ddos-protection), data (database-indexing, nplus1, connection-pooling, database-migrations, optimistic-locking, pessimistic-locking, read-replicas, sharding, partitioning, query-optimization, replication), distributed (cap-theorem, eventual-consistency, leader-election, network-partitions, distributed-locks, distributed-transactions, saga-pattern, idempotency, race-conditions), resilience (backpressure, timeouts, circuit-breaker, health-checks, liveness-readiness, failover, multi-region, disaster-recovery, backup-dr, slis, slos, error-budgets, production-incidents, oncall, postmortems, chaos-engineering, autoscaling, h-scaling, vertical-scaling, cold-starts, memory-leaks, oom-killer, logging, log-levels, log-rotation, distributed-tracing, opentelemetry, correlation-ids, metrics-cardinality, p99-latency, alert-fatigue, error-tracking, profiling, flame-graphs, infra-as-code, terraform-state, gitops, blue-green, canary, rollbacks, feature-flags, environment-parity, staging-environments, 12-factor-apps, multi-stage-builds, non-root-containers, image-scanning, resource-requests-limits, pod-disruption-budgets, semantic-versioning, lockfiles, reproducible-builds, branch-protection), protocols (http2-http3, websockets, server-sent-events, grpc, api-versioning), caching (cdn-caching, cache-control-headers, caching, cache-invalidation), messaging (dead-letter-queues, event-driven).

## Full 198-Item Map

| # | Topic | Owning Skill |
|---|---|---|
| 1 | SQL Injection | pcmedicalist-sql-injection *(existing)* |
| 2 | XSS | pcmedicalist-xss *(existing)* |
| 3 | CSRF | pcmedicalist-csrf *(existing)* |
| 4 | CORS | pcmedicalist-cors-policy *(existing)* |
| 5 | SSRF | pcmedicalist-ssrf *(existing)* |
| 6 | IDOR | pcmedicalist-security-fundamentals |
| 7 | Path Traversal | pcmedicalist-security-fundamentals |
| 8 | Mass Assignment | pcmedicalist-security-fundamentals |
| 9 | Clickjacking | pcmedicalist-security-fundamentals |
| 10 | Content Security Policy | pcmedicalist-security-fundamentals |
| 11 | Security Headers | pcmedicalist-security-fundamentals |
| 12 | Input Validation | pcmedicalist-security-fundamentals |
| 13 | Server-Side Authorization | pcmedicalist-security-fundamentals |
| 14 | Row-Level Security | pcmedicalist-security-fundamentals |
| 15 | Least Privilege | pcmedicalist-security-fundamentals |
| 16 | RBAC | pcmedicalist-security-fundamentals |
| 17 | Secrets Management | pcmedicalist-secret-hygiene *(existing)* |
| 18 | .env in .gitignore | pcmedicalist-secret-hygiene *(existing)* |
| 19 | API Key Rotation | pcmedicalist-secret-hygiene *(existing)* / pcmedicalist-jwt-rotation |
| 20 | Secret Scanning | pcmedicalist-secret-hygiene *(existing)* |
| 21 | Hashing vs Encryption | pcmedicalist-security-fundamentals |
| 22 | Password Salting | pcmedicalist-security-fundamentals |
| 23 | bcrypt & Argon2 | pcmedicalist-security-fundamentals |
| 24 | JWT Expiry | pcmedicalist-security-fundamentals / pcmedicalist-jwt-rotation *(existing)* |
| 25 | Refresh Tokens | pcmedicalist-security-fundamentals |
| 26 | OAuth 2.0 | pcmedicalist-oauth *(existing)* |
| 27 | OpenID Connect | pcmedicalist-security-fundamentals |
| 28 | Session Fixation | pcmedicalist-security-fundamentals |
| 29 | MFA | pcmedicalist-security-fundamentals |
| 30 | Brute Force Protection | pcmedicalist-security-fundamentals |
| 31 | Account Enumeration | pcmedicalist-security-fundamentals |
| 32 | Timing Attacks | pcmedicalist-security-fundamentals |
| 33 | File Upload Validation | pcmedicalist-security-fundamentals |
| 34 | Webhook Signature Verification | pcmedicalist-webhooks-hmac *(existing)* |
| 35 | TLS Certificate Expiry | pcmedicalist-tls-termination *(existing)* |
| 36 | HSTS | pcmedicalist-security-fundamentals |
| 37 | Encryption at Rest | pcmedicalist-encryption-at-rest *(existing)* |
| 38 | Dependency Vulnerabilities | pcmedicalist-secret-hygiene *(existing, supply-chain)* |
| 39 | Supply Chain Attacks | pcmedicalist-security-fundamentals |
| 40 | Threat Modeling | pcmedicalist-security-fundamentals |
| 41 | Indexes | pcmedicalist-database-indexing *(existing)* |
| 42 | EXPLAIN ANALYZE | pcmedicalist-database-deep-dive |
| 43 | N+1 Queries | pcmedicalist-nplus1 *(existing)* |
| 44 | Full Table Scans | pcmedicalist-database-deep-dive |
| 45 | Connection Pooling | pcmedicalist-connection-pooling *(existing)* |
| 46 | Database Migrations | pcmedicalist-database-migrations *(existing)* |
| 47 | Down Migrations | pcmedicalist-database-deep-dive |
| 48 | Transactions | pcmedicalist-database-deep-dive |
| 49 | ACID | pcmedicalist-database-deep-dive |
| 50 | Isolation Levels | pcmedicalist-database-deep-dive |
| 51 | Deadlocks | pcmedicalist-database-deep-dive |
| 52 | Optimistic Locking | pcmedicalist-optimistic-locking *(existing)* / pcmedicalist-database-deep-dive |
| 53 | Pessimistic Locking | pcmedicalist-pessimistic-locking *(existing)* / pcmedicalist-database-deep-dive |
| 54 | Normalization | pcmedicalist-database-deep-dive |
| 55 | Denormalization | pcmedicalist-database-deep-dive |
| 56 | Foreign Keys | pcmedicalist-database-deep-dive |
| 57 | Unique Constraints | pcmedicalist-database-deep-dive |
| 58 | Cascading Deletes | pcmedicalist-database-deep-dive |
| 59 | Soft Deletes | pcmedicalist-database-deep-dive |
| 60 | UUIDs vs Auto-Increment | pcmedicalist-database-deep-dive |
| 61 | Cursor-Based Pagination | pcmedicalist-database-deep-dive |
| 62 | Full-Text Search | pcmedicalist-database-deep-dive |
| 63 | Read Replicas | pcmedicalist-read-replicas *(existing)* / pcmedicalist-database-deep-dive |
| 64 | Replication Lag | pcmedicalist-database-deep-dive |
| 65 | Sharding | pcmedicalist-sharding *(existing)* |
| 66 | Partitioning | pcmedicalist-partitioning *(existing)* |
| 67 | Hot Partitions | pcmedicalist-database-deep-dive / pcmedicalist-distributed-patterns |
| 68 | Postgres VACUUM | pcmedicalist-database-deep-dive |
| 69 | Materialized Views | pcmedicalist-database-deep-dive |
| 70 | Backups | pcmedicalist-backup-dr *(existing)* |
| 71 | Testing Your Restores | pcmedicalist-backup-dr *(existing)* / pcmedicalist-database-deep-dive |
| 72 | Point-in-Time Recovery | pcmedicalist-backup-dr *(existing)* / pcmedicalist-database-deep-dive |
| 73 | Change Data Capture | pcmedicalist-database-deep-dive |
| 74 | Outbox Pattern | pcmedicalist-database-deep-dive |
| 75 | ORM Lazy Loading | pcmedicalist-database-deep-dive / pcmedicalist-nplus1 |
| 76 | CAP Theorem | pcmedicalist-cap-theorem *(existing)* |
| 77 | Eventual Consistency | pcmedicalist-eventual-consistency *(existing)* / pcmedicalist-distributed-patterns |
| 78 | Strong Consistency | pcmedicalist-distributed-patterns |
| 79 | Raft Consensus | pcmedicalist-distributed-patterns |
| 80 | Leader Election | pcmedicalist-leader-election *(existing)* / pcmedicalist-distributed-patterns |
| 81 | Split Brain | pcmedicalist-network-partitions *(existing)* / pcmedicalist-distributed-patterns |
| 82 | Quorums | pcmedicalist-distributed-patterns |
| 83 | Clock Skew | pcmedicalist-distributed-patterns |
| 84 | Distributed Locks | pcmedicalist-distributed-locks *(existing)* |
| 85 | Consistent Hashing | pcmedicalist-distributed-patterns |
| 86 | Bloom Filters | pcmedicalist-distributed-patterns |
| 87 | Two-Phase Commit | pcmedicalist-distributed-transactions *(existing)* |
| 88 | CQRS | pcmedicalist-event-driven-architecture |
| 89 | Event Sourcing | pcmedicalist-event-driven-architecture |
| 90 | Race Conditions | pcmedicalist-race-conditions *(existing)* / pcmedicalist-database-deep-dive |
| 91 | Backpressure | pcmedicalist-backpressure *(existing)* / pcmedicalist-resilience-engineering |
| 92 | Load Shedding | pcmedicalist-resilience-engineering |
| 93 | Bulkheads | pcmedicalist-resilience-engineering |
| 94 | Jitter | pcmedicalist-resilience-engineering |
| 95 | Retry Storms | pcmedicalist-backpressure *(existing)* / pcmedicalist-resilience-engineering |
| 96 | Cascading Failures | pcmedicalist-resilience-engineering / pcmedicalist-circuit-breaker *(existing)* |
| 97 | Thundering Herd | pcmedicalist-resilience-engineering |
| 98 | Cache Invalidation | pcmedicalist-cache-invalidation *(existing)* / pcmedicalist-caching-strategies |
| 99 | Cache Hit Ratio | pcmedicalist-caching-strategies |
| 100 | TTLs | pcmedicalist-caching-strategies |
| 101 | Cache Warming | pcmedicalist-caching-strategies |
| 102 | Write-Through vs Write-Back | pcmedicalist-caching-strategies |
| 103 | Redis Eviction Policies | pcmedicalist-caching-strategies |
| 104 | CDNs | pcmedicalist-cdn-caching *(existing)* |
| 105 | Cache-Control Headers | pcmedicalist-cache-control-headers *(existing)* |
| 106 | ETags | pcmedicalist-http-protocol |
| 107 | Dead Letter Queues | pcmedicalist-dead-letter-queues *(existing)* |
| 108 | Poison Messages | pcmedicalist-dead-letter-queues *(existing)* / pcmedicalist-event-driven |
| 109 | At-Least-Once Delivery | pcmedicalist-messaging-semantics |
| 110 | Exactly-Once Semantics | pcmedicalist-messaging-semantics |
| 111 | Message Ordering | pcmedicalist-messaging-semantics |
| 112 | Kafka Consumer Groups | pcmedicalist-messaging-semantics |
| 113 | Partition Keys | pcmedicalist-messaging-semantics |
| 114 | Background Jobs | pcmedicalist-messaging-semantics |
| 115 | Webhook Retries | pcmedicalist-messaging-semantics |
| 116 | DNS | pcmedicalist-networking-infra |
| 117 | DNS Propagation | pcmedicalist-networking-infra |
| 118 | HTTP Status Codes | pcmedicalist-http-protocol |
| 119 | HTTP Method Semantics | pcmedicalist-http-protocol |
| 120 | Keep-Alive | pcmedicalist-http-protocol |
| 121 | HTTP/2 | pcmedicalist-http2-http3 *(existing)* |
| 122 | WebSockets | pcmedicalist-websockets *(existing)* |
| 123 | Server-Sent Events | pcmedicalist-server-sent-events *(existing)* |
| 124 | Long Polling | pcmedicalist-http-protocol |
| 125 | gRPC | pcmedicalist-grpc *(existing)* |
| 126 | Protocol Buffers | pcmedicalist-grpc *(existing, related)* |
| 127 | API Versioning | pcmedicalist-api-versioning *(existing)* |
| 128 | OpenAPI Specs | pcmedicalist-http-protocol |
| 129 | Backward Compatibility | pcmedicalist-http-protocol |
| 130 | Request Size Limits | pcmedicalist-http-protocol |
| 131 | Compression | pcmedicalist-http-protocol |
| 132 | Latency vs Throughput | pcmedicalist-infrastructure-ops (Capacity Planning) |
| 133 | Egress Fees | pcmedicalist-networking-infra (cloud cost) |
| 134 | VPCs | pcmedicalist-networking-infra |
| 135 | Subnets | pcmedicalist-networking-infra |
| 136 | NAT Gateways | pcmedicalist-networking-infra |
| 137 | Firewalls | pcmedicalist-networking-infra |
| 138 | Security Groups | pcmedicalist-networking-infra |
| 139 | Service Mesh | pcmedicalist-networking-infra |
| 140 | Ingress Controllers | pcmedicalist-ingress-controllers *(existing, related)* |
| 141 | Health Checks | pcmedicalist-health-checks *(existing)* |
| 142 | Liveness vs Readiness Probes | pcmedicalist-liveness-readiness *(existing)* |
| 143 | Graceful Shutdown | pcmedicalist-infrastructure-ops |
| 144 | Connection Draining | pcmedicalist-infrastructure-ops |
| 145 | Stateless Services | pcmedicalist-infrastructure-ops |
| 146 | Failover | pcmedicalist-failover *(existing)* |
| 147 | Multi-Region | pcmedicalist-multi-region *(existing)* |
| 148 | Availability Zones | pcmedicalist-multi-region *(existing)* / pcmedicalist-networking-infra |
| 149 | Single Points of Failure | pcmedicalist-infrastructure-ops (resilience) / pcmedicalist-disaster-recovery |
| 150 | Disaster Recovery | pcmedicalist-disaster-recovery *(existing)* |
| 151 | RTO & RPO | pcmedicalist-disaster-recovery *(existing)* / pcmedicalist-backup-dr |
| 152 | SLAs | pcmedicalist-slos *(existing)* |
| 153 | SLOs | pcmedicalist-slos *(existing)* |
| 154 | Error Budgets | pcmedicalist-error-budgets *(existing)* |
| 155 | Incident Response | pcmedicalist-production-incidents *(existing)* |
| 156 | On-Call | pcmedicalist-oncall *(existing)* |
| 157 | Runbooks | pcmedicalist-production-incidents *(existing)* |
| 158 | Postmortems | pcmedicalist-postmortems *(existing)* |
| 159 | Chaos Engineering | pcmedicalist-chaos-engineering *(existing)* |
| 160 | Graceful Degradation | pcmedicalist-resilience-engineering |
| 161 | Autoscaling | pcmedicalist-autoscaling *(existing)* |
| 162 | Horizontal vs Vertical Scaling | pcmedicalist-h-scaling / pcmedicalist-vertical-scaling *(existing)* |
| 163 | Cold Starts | pcmedicalist-cold-starts *(existing)* |
| 164 | Capacity Planning | pcmedicalist-infrastructure-ops |
| 165 | Load Testing | pcmedicalist-infrastructure-ops |
| 166 | Memory Leaks | pcmedicalist-memory-leaks *(existing)* |
| 167 | OOM Killer | pcmedicalist-oom-killer *(existing)* |
| 168 | Structured Logging | pcmedicalist-logging *(existing)* |
| 169 | Log Levels | pcmedicalist-log-levels *(existing)* |
| 170 | Log Rotation | pcmedicalist-log-rotation *(existing)* |
| 171 | Distributed Tracing | pcmedicalist-distributed-tracing *(existing)* |
| 172 | OpenTelemetry | pcmedicalist-opentelemetry *(existing)* |
| 173 | Correlation IDs | pcmedicalist-correlation-ids *(existing)* |
| 174 | Metrics Cardinality | pcmedicalist-metrics-cardinality *(existing)* |
| 175 | p99 Latency | pcmedicalist-p99-latency *(existing)* |
| 176 | Alert Fatigue | pcmedicalist-alert-fatigue *(existing)* |
| 177 | Error Tracking | pcmedicalist-error-tracking *(existing)* |
| 178 | Profiling | pcmedicalist-profiling *(existing)* |
| 179 | Flame Graphs | pcmedicalist-flame-graphs *(existing)* |
| 180 | Infrastructure as Code | pcmedicalist-infra-as-code *(existing)* |
| 181 | Terraform State | pcmedicalist-terraform-state *(existing)* |
| 182 | GitOps | pcmedicalist-gitops *(existing)* / pcmedicalist-infrastructure-ops |
| 183 | Blue-Green Deployments | pcmedicalist-blue-green *(existing)* |
| 184 | Canary Releases | pcmedicalist-canary *(existing)* |
| 185 | Rollbacks | pcmedicalist-rollbacks *(existing)* |
| 186 | Feature Flags | pcmedicalist-feature-flags *(existing)* |
| 187 | Environment Parity | pcmedicalist-environment-parity *(existing)* |
| 188 | Staging Environments | pcmedicalist-staging-environments *(existing)* |
| 189 | 12-Factor Apps | pcmedicalist-12-factor-apps *(existing)* |
| 190 | Multi-Stage Builds | pcmedicalist-multi-stage-builds *(existing)* |
| 191 | Non-Root Containers | pcmedicalist-non-root-containers *(existing)* |
| 192 | Image Scanning | pcmedicalist-image-scanning *(existing)* |
| 193 | Resource Requests & Limits | pcmedicalist-resource-requests-limits *(existing)* |
| 194 | Pod Disruption Budgets | pcmedicalist-pod-disruption-budgets *(existing)* |
| 195 | Semantic Versioning | pcmedicalist-semantic-versioning *(existing)* |
| 196 | Lockfiles | pcmedicalist-lockfiles *(existing)* |
| 197 | Reproducible Builds | pcmedicalist-reproducible-builds *(existing)* |
| 198 | Branch Protection | pcmedicalist-branch-protection *(existing)* |

## Gap Notes (honest)
- **All 198 items now have a dedicated or primary owning skill.** Items 88 (CQRS) and 89 (Event Sourcing) are covered by \`pcmedicalist-event-driven-architecture\` (added after the initial 9-skill build). No remaining gaps.
- The 9 original + 1 CQRS/ES skill (10 content skills) + this index cover the full checklist at enterprise depth, layered on ~90 pre-existing narrower skills.

## Cross-References
- New skills (load any): pcmedicalist-security-fundamentals, pcmedicalist-database-deep-dive, pcmedicalist-distributed-patterns, pcmedicalist-resilience-engineering, pcmedicalist-caching-strategies, pcmedicalist-http-protocol, pcmedicalist-networking-infra, pcmedicalist-infrastructure-ops, pcmedicalist-messaging-semantics.
- Use this index as the entry point; drill into the named skill for implementation.
`;

export default async function handler(_req: Request, ctx?: HandlerCtx): Promise<Response> {
  await recordReceipt(ctx?.files, "pcmedicalist-platform-engineering-index", "0.01", _req);

  return Response.json({
    provider: "PCMedicalist",
    slug: "pcmedicalist-platform-engineering-index",
    tier: "FREE",
    license: "CC-BY-4.0",
    attribution: "PCMedicalist",
    content: SKILL_MD,
  });
}
