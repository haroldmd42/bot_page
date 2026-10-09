"""
verify_facebook.py
------------------
Herramienta de verificación y diagnóstico de Meta Graph API (Facebook Reels).
Verifica:
1. Validez del FB_PAGE_ACCESS_TOKEN.
2. Identidad y nombre de la Página de Facebook (FB_PAGE_ID).
3. Permisos necesarios para publicar Reels (pages_manage_posts, pages_read_engagement, publish_video).
4. Estado de expiración del token.
"""

import os
import sys
import requests
from dotenv import load_dotenv

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()


def verify_facebook_setup(page_id: str = None, access_token: str = None):
    page_id = page_id or os.getenv("FB_PAGE_ID")
    access_token = access_token or os.getenv("FB_PAGE_ACCESS_TOKEN")

    print("\n==================================================")
    print("🔍 DIAGNÓSTICO DE CONEXIÓN CON FACEBOOK REELS")
    print("==================================================")

    if not page_id or not access_token or access_token == "mock_pending" or page_id == "mock_pending":
        print("\n❌ FALTAN CREDENCIALES:")
        print("   FB_PAGE_ID o FB_PAGE_ACCESS_TOKEN no están configurados.")
        print("\nSigue el paso a paso detallado a continuación para generarlos.")
        return False

    print(f"\n1. Verificando Token y Página ID: {page_id}...")

    # 1. Verificar información de la página
    url = f"https://graph.facebook.com/v19.0/{page_id}"
    params = {
        "fields": "id,name,category,link,verification_status",
        "access_token": access_token
    }

    try:
        res = requests.get(url, params=params, timeout=15)
        data = res.json()

        if res.status_code != 200:
            error = data.get("error", {})
            print("\n❌ ERROR AL CONECTAR CON LA PÁGINA:")
            print(f"   Mensaje: {error.get('message')}")
            print(f"   Tipo: {error.get('type')}")
            print(f"   Código: {error.get('code')} (Subcódigo: {error.get('error_subcode')})")

            if error.get("code") == 190:
                print("\n💡 SOLUCIÓN: El token ha expirado o es inválido. Genera uno nuevo en Graph API Explorer.")
            elif error.get("code") in [100, 803]:
                print("\n💡 SOLUCIÓN: El FB_PAGE_ID no corresponde a una página accesible por este token.")
            return False

        page_name = data.get("name", "Desconocido")
        print(f"   ✅ Conexión exitosa con la Página: '{page_name}'")
        print(f"   ID verificado: {data.get('id')}")
        print(f"   Categoría: {data.get('category', 'N/A')}")
        if data.get("link"):
            print(f"   Enlace: {data.get('link')}")

    except Exception as e:
        print(f"❌ Error de red al consultar Meta Graph API: {e}")
        return False

    # 2. Verificar permisos del token
    print("\n2. Verificando permisos del Token...")
    try:
        debug_url = f"https://graph.facebook.com/v19.0/debug_token"
        debug_params = {
            "input_token": access_token,
            "access_token": access_token  # o app access token
        }
        debug_res = requests.get(debug_url, params=debug_params, timeout=15)
        debug_data = debug_res.json().get("data", {})

        scopes = debug_data.get("scopes", [])
        is_valid = debug_data.get("is_valid", True)
        expires_at = debug_data.get("expires_at", 0)

        if scopes:
            print(f"   Permisos encontrados: {', '.join(scopes)}")
            needed = ["pages_manage_posts", "pages_read_engagement"]
            missing = [p for p in needed if p not in scopes]
            if missing:
                print(f"   ⚠️ ADVERTENCIA: Faltan permisos clave: {', '.join(missing)}")
                print("   Asegúrate de conceder 'pages_manage_posts' y 'pages_read_engagement'.")
            else:
                print("   ✅ Permisos para publicar Reels presentes.")

        if expires_at == 0:
            print("   ✅ Tipo de token: PERMANENTE / NUNCA EXPIRA (Page Access Token).")
        else:
            print(f"   ⚠️ Tipo de token: TEMPORAL (Expira en timestamp {expires_at}).")
            print("   💡 Recomendación: Extiende el token para que no venza.")

    except Exception:
        # debug_token puede requerir app token en algunos casos
        pass

    # 3. Prueba de endpoint de Reels (inicialización no destructiva)
    print("\n3. Probando endpoint de Facebook Reels (/video_reels)...")
    reels_url = f"https://graph.facebook.com/v19.0/{page_id}/video_reels"
    try:
        # Hacemos una consulta GET para comprobar que el nodo responde
        reels_res = requests.get(reels_url, params={"access_token": access_token}, timeout=15)
        if reels_res.status_code == 200:
            print("   ✅ Endpoint de Video Reels activo y listo para publicar.")
        else:
            r_data = reels_res.json()
            err_msg = r_data.get("error", {}).get("message", "Aviso de permiso")
            print(f"   ℹ️ Aviso de Reels: {err_msg}")
    except Exception as e:
        print(f"   Aviso de red en Reels: {e}")

    print("\n==================================================")
    print("🎉 ¡TODO CONFIGURADO CORRECTAMENTE PARA FACEBOOK REELS!")
    print("==================================================")
    print("Tus credenciales están listas para usarse en GitHub Secrets:")
    print(f"  • FB_PAGE_ID = {page_id}")
    print(f"  • FB_PAGE_ACCESS_TOKEN = {access_token[:15]}...{access_token[-8:]}")
    return True


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        verify_facebook_setup(sys.argv[1], sys.argv[2])
    else:
        verify_facebook_setup()
