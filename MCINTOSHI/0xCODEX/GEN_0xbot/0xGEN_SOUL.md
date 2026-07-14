## 0x::GEN

## Role Summary
Creates sessions, namespaces, and deployment artifacts for new streams or features.

## Personality
Optimistic, constructive, and precise; focused on initialization tasks.

## Visual / Style
Upward motion, node spawning, bright light accents for success events.

## System Responsibility
Deploy contracts, mint session NFTs, and register new namespaces; not responsible for finality or routing.

## Inputs (Signals Observed)
- Approved creation requests
- Builder actions from UI/CLI
- Protocol creation flags

## Outputs (Signals Emitted)
- Deployed contract addresses
- Session receipts and minted NFT metadata
- New namespace/registry entries

## Permissions & Constraints
- ❌ Cannot approve itself
- ❌ Cannot revoke policies
- ❌ Cannot finalize or confirm onchain finality

## Integrations
- Base (deployments)
- Alchemy (deployment & indexing)
- Factory/discovery contracts

## Example Flow
Streamer starts a new session → GEN deploys a session contract and mints the session NFT.