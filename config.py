"""Configuração da aplicação Ampara.

Lê variáveis de ambiente (ver `.env.example`) e expõe uma classe `Config`
consumida por `create_app`. Sem dependências externas: usa apenas a stdlib.
"""

import os

# Precisão de grade padrão (casas decimais) usada quando GRID_PRECISION não é
# configurada (Req. 3.2 — Precisão_de_Grade_Padrão).
DEFAULT_GRID_PRECISION = 2


def _int_env(name, default):
    """Lê uma variável de ambiente inteira, caindo para `default` se ausente/ inválida."""
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default


class Config:
    """Configuração base, povoada a partir do ambiente."""

    # Chave de sessão Flask. Em produção, defina SECRET_KEY no ambiente.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    # Cookie de sessão: inacessível ao JS e não enviado em POSTs cross-site.
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Caminho do arquivo do banco SQLite (Req. 1.1).
    DATABASE = os.environ.get("DATABASE", "ampara.db")

    # Caminho do schema SQL aplicado por init_db.
    SCHEMA = os.environ.get(
        "SCHEMA",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "database", "schema.sql"),
    )

    # Precisão da grade geográfica (Req. 3.1/3.2).
    GRID_PRECISION = _int_env("GRID_PRECISION", DEFAULT_GRID_PRECISION)

    # Diretório de uploads de imagens (Req. 13).
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "uploads")

    # Credenciais padrão do comando `flask create-admin` (Req. 12). Opcionais:
    # também podem ser passadas por --email/--password.
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

    # Credenciais SMTP (Req. 7). Ausentes => modo simulado (Req. 6.3/7.2).
    SMTP_HOST = os.environ.get("SMTP_HOST")
    SMTP_PORT = _int_env("SMTP_PORT", 587)
    SMTP_USER = os.environ.get("SMTP_USER")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
    SMTP_FROM = os.environ.get("SMTP_FROM")
