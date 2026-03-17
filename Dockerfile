# ── Imagem base ──────────────────────────────────────────────────────────────
FROM python:3.11-slim

# Evita arquivos .pyc e buffers de saída (logs aparecem em tempo real)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ── Diretório de trabalho dentro do container ─────────────────────────────────
WORKDIR /app

# ── Dependências (copiadas antes do código para aproveitar cache do Docker) ───
RUN apt-get update && apt-get install -y sqlite3 curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Código-fonte ──────────────────────────────────────────────────────────────
COPY . .

# ── Porta exposta pela API ────────────────────────────────────────────────────
EXPOSE 8000

# ── Comando de inicialização ──────────────────────────────────────────────────
# --host 0.0.0.0 → aceita conexões de fora do container
# --reload       → hot-reload em desenvolvimento (remova em produção)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
