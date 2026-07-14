#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

function usage() {
  console.error('Usage: node verify_mch.js <file>');
  process.exit(2);
}

const forbidden = [
  'mockup', 'placeholder', 'simulated', 'example', 'automatically', 'seamlessly integrates', 'backend handles', 'ai decides'
];

function readFile(p) {
  try {
    return fs.readFileSync(p, 'utf8');
  } catch (e) {
    console.error('Could not read', p);
    process.exit(2);
  }
}

if (process.argv.length < 3) usage();
const target = path.resolve(process.argv[2]);
const content = readFile(target);
const lower = content.toLowerCase();

const issues = [];

// Gate 5: No-Magic Language Gate (forbidden phrases)
for (const ph of forbidden) {
  if (lower.includes(ph)) issues.push({ gate: 'No-Magic Language Gate', reason: `Found forbidden phrase: ${ph}` });
}

// Gate 0: Verdict present
if (!/VERDICT:\s*(APPROVED|REJECTED)/i.test(content)) {
  issues.push({ gate: 'Verdict Gate', reason: 'Missing or malformed VERDICT line (must be VERDICT: APPROVED|REJECTED)' });
}

// Gate: mandatory end sections
const requiredSections = ['THREAT MODEL:', 'ASSUMPTIONS:', 'KNOWN LIMITATIONS:', 'RED-TEAM ATTACK ANALYSIS:'];
for (const s of requiredSections) {
  if (!content.includes(s)) issues.push({ gate: 'Sections Gate', reason: `Missing section: ${s}` });
}

// Gate 1: Execution Gate
// Require explicit execution environment and runtime keywords
const execTriggers = ['execution environment', 'runtime', 'executes on', 'where does this execute', 'execution:'];
const runtimeKeywords = ['node', 'python', 'evm', 'solidity', 'docker', 'vercel', 'serverless', 'aws lambda', 'gcp', 'azure'];
let hasExecPhrase = execTriggers.some(t => lower.includes(t));
let hasRuntimeKeyword = runtimeKeywords.some(k => lower.includes(k));
if (!hasExecPhrase && !hasRuntimeKeyword) {
  issues.push({ gate: 'Execution Gate', reason: 'Missing explicit execution environment/runtime description' });
} else if (!hasRuntimeKeyword) {
  issues.push({ gate: 'Execution Gate', reason: 'Execution described but no concrete runtime keyword found (e.g. Node, Python, EVM, Docker, Vercel)' });
}

// Gate 2: Trigger Gate
const triggerTokens = ['trigger', 'triggers', 'onchain', 'api request', 'api call', 'scheduled', 'cron', 'webhook', 'user action', 'http request', 'tx', 'transaction', 'button click'];
const hasTrigger = triggerTokens.some(t => lower.includes(t));
if (!hasTrigger) issues.push({ gate: 'Trigger Gate', reason: 'Missing explicit trigger (onchain event, API request, scheduled job, or user action)' });

// Gate 3: Input / Output Gate
const hasInputs = /\binputs?:/i.test(content);
const hasOutputs = /\boutputs?:/i.test(content);
if (!hasInputs || !hasOutputs) {
  issues.push({ gate: 'Input/Output Gate', reason: 'Missing `Inputs:` and/or `Outputs:` sections with typed, explicit descriptions' });
}

// Gate 4: Side-Effect Proof Gate
const sideEffectTokens = ['tx hash', 'transaction hash', 'log entry', 'db mutation', 'state change', 'persist', 'emitted event', 'audit log'];
const sideEffectMention = sideEffectTokens.some(t => lower.includes(t));
if (!sideEffectMention) {
  // If the doc mentions onchain or persistent state, require a proof token
  const onchainMention = /onchain|smart contract|mint|contract call|mutate state|oracle/.test(lower);
  if (onchainMention) {
    issues.push({ gate: 'Side-Effect Proof Gate', reason: 'Onchain/stateful operations mentioned but no verifiable side-effect proof (tx hash, log, or DB mutation) present' });
  }
}

// Gate 6: Security-First Ordering Gate
// Ensure THREAT MODEL appears before FUNCTIONAL or FUNCTIONALITY sections
const idxThreat = content.indexOf('THREAT MODEL:');
const funcKeywords = ['FUNCTIONAL', 'FUNCTIONALITY', 'FUNCTIONAL DESIGN', 'FUNCTIONAL DESIGN:'];
let idxFunc = -1;
for (const k of funcKeywords) {
  const i = content.indexOf(k);
  if (i !== -1 && (idxFunc === -1 || i < idxFunc)) idxFunc = i;
}
if (idxFunc !== -1) {
  if (idxThreat === -1) {
    issues.push({ gate: 'Security-First Ordering Gate', reason: 'Functionality section present but THREAT MODEL is missing' });
  } else if (idxThreat > idxFunc) {
    issues.push({ gate: 'Security-First Ordering Gate', reason: 'THREAT MODEL appears after functionality; security must precede features' });
  }
}

// Gate 7: Verifiability Gate
// If onchain or AI-critical operations are mentioned, require explicit verifiability language
const aiOrOnchain = /\b(ai|model|onchain|oracle|smart contract|mutate state|transaction)\b/.test(lower);
if (aiOrOnchain) {
  const verifiableTokens = ['tx hash', 'transaction hash', 'cryptographic proof', 'signature', 'proof', 'merkle', 'audit log', 'verifiable'];
  const hasVerifiable = verifiableTokens.some(t => lower.includes(t));
  if (!hasVerifiable) {
    issues.push({ gate: 'Verifiability Gate', reason: 'AI or onchain operations mentioned but no verifiable output/proof language present' });
  }
}

if (issues.length === 0) {
  console.log('VERIFIER: PASS');
  process.exit(0);
} else {
  console.log('VERIFIER: FAIL');
  for (const it of issues) console.log(`- ${it.gate}: ${it.reason}`);
  process.exit(3);
}
