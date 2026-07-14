FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt || true
COPY . .
RUN chmod +x /app/entrypoint.sh || true
RUN useradd --create-home appuser || true
RUN chown -R appuser:appuser /app || true
USER appuser
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 CMD grep -q main.py /proc/1/cmdline || exit 1
ENTRYPOINT ["./entrypoint.sh"]
