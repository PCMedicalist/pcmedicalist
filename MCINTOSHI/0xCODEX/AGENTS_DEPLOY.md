## Deploying Agents with Docker Compose

Overview
- Each agent builds from its folder and expects a local `.env` file at the agent root with runtime secrets (do NOT commit `.env`).

Build and run locally

```bash
# build and start all agents
docker compose up --build -d

# build a single agent (example)
docker build -t ghcr.io/<org>/<repo>/0xcodexbot:latest ./0xCODEXbot
docker compose up --build 0xcodexbot
```

Push to GitHub Container Registry

1. Authenticate: `echo $CR_PAT | docker login ghcr.io -u <username> --password-stdin`
2. Build and tag each image and push:

```bash
docker build -t ghcr.io/<org>/<repo>/0xcodexbot:latest ./0xCODEXbot
docker push ghcr.io/<org>/<repo>/0xcodexbot:latest
```

Notes
- Ensure `.env` files are populated from `CHARACTER_REGISTRY.json` or your secrets manager.
- Remove committed secrets and rotate tokens before building/pushing images.
- For production, consider Kubernetes manifests in `k8s/` and use Secrets for credentials.
