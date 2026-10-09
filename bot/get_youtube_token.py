"""
get_youtube_token.py
--------------------
Utility script to generate an OAuth2 Refresh Token for the YouTube Data API v3.
Run this ONCE locally to obtain your YT_REFRESH_TOKEN for GitHub Secrets.

Usage:
    python bot/get_youtube_token.py
"""

import os
import sys
import subprocess

# Configurar soporte para caracteres UTF-8 en terminal Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    print("\n📦 Instalando librería necesaria para Google OAuth (google-auth-oauthlib)...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "google-auth-oauthlib", "python-dotenv"])
        from google_auth_oauthlib.flow import InstalledAppFlow
        print("✅ Librería instalada correctamente.\n")
    except Exception as e:
        print(f"\n❌ No se pudo instalar automáticamente: {e}")
        print("Por favor ejecuta manualmente: pip install google-auth-oauthlib python-dotenv")
        sys.exit(1)

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly"
]


def generate_refresh_token():
    client_id = input("Introduce tu YT_CLIENT_ID (o presiona ENTER para leer de .env): ").strip()
    if not client_id:
        client_id = os.getenv("YT_CLIENT_ID")

    client_secret = input("Introduce tu YT_CLIENT_SECRET (o presiona ENTER para leer de .env): ").strip()
    if not client_secret:
        client_secret = os.getenv("YT_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("\n❌ Error: Debes ingresar tu Client ID y Client Secret de Google Cloud.")
        return

    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost:8080/"]
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)
    print("\n🌐 Abriendo navegador para autorizar la aplicación en tu canal de YouTube...")
    creds = flow.run_local_server(port=8080, prompt="consent", access_type="offline")

    print("\n" + "=" * 60)
    print("✅ ¡AUTORIZACIÓN EXITOSA!")
    print("=" * 60)
    print("Copia este token y agrégalo a los Secrets de tu repositorio en GitHub:")
    print(f"\nYT_REFRESH_TOKEN = {creds.refresh_token}\n")
    print("=" * 60)


if __name__ == "__main__":
    generate_refresh_token()
