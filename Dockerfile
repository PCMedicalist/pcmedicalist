# Base Docker build for PCMedicalist with Hermes runtime
FROM ubuntu:22.04

# Update and install necessary dependencies
RUN apt-get update && \
    apt-get install -y wget software-properties-common python3 python3-pip git curl

# Copy PCMedicalist workspace configuration
COPY .pcmedicalist /root/.pcmedicalist

# Install Python dependencies from requirements (if present)
RUN if [ -f /root/.pcmedicalist/requirements.txt ]; then \
    pip install -q -r /root/.pcmedicalist/requirements.txt 2>&1 | tail -5; \
    else echo "No requirements.txt found, skipping Python deps"; fi

WORKDIR /root

# Install Ollama-specific requirements if script exists
RUN if [ -f /root/.pcmedicalist/scripts/install-ollama.sh ]; then \
    chmod +x /root/.pcmedicalist/scripts/install-ollama.sh && \
    /root/.pcmedicalist/scripts/install-ollama.sh 0xpcmedicalist:8b 2>&1 | tail -10; \
    else echo "Ollama install script not found, skipping"; fi

# Expose standard ports for gateway, dashboard, Ollama
EXPOSE 11434 8642 9119 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8642/health || exit 1

# Default command: serve gateway (can be overridden)
CMD ["hermes", "gateway"]
