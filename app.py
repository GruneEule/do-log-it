import os
import random
import string
from urllib.parse import unquote

STORAGE_DIR = "./storage"
VIEW_DIR = "./static-view"

if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def application(environ, start_response):
    path = environ.get("PATH_INFO", "")
    method = environ.get("REQUEST_METHOD", "GET")

    # Domain aus den Umgebungsvariablen ermitteln
    http_host = environ.get('HTTP_HOST', 'localhost')
    server_name = environ.get('SERVER_NAME', 'localhost')
    server_port = environ.get('SERVER_PORT', '80')

    # Vollständige Domain-URL erstellen
    domain = f"http://{http_host or server_name}"
    if server_port not in ['80', '443']:
        domain += f":{server_port}"

    # --- API: Text hochladen ---
    if path == "/api/share" and method == "POST":
        try:
            size = int(environ.get("CONTENT_LENGTH", 0))
        except (ValueError):
            size = 0

        body = environ["wsgi.input"].read(size).decode("utf-8").strip()
        # Entferne "code=" Präfix falls vorhanden
        if body.startswith("code="):
            body = body[5:]

        if not body:
            start_response("200 OK", [("Content-Type", "text/plain; charset=utf-8")])
            return ["Kein Text übermittelt".encode("utf-8")]

        code = generate_code()
        filename = os.path.join(STORAGE_DIR, f"{code}.txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(body)

        # Vollständige URL zurückgeben
        full_url = f"{domain}/{code}"
        start_response("200 OK", [("Content-Type", "text/plain; charset=utf-8")])
        return [full_url.encode("utf-8")]

    # --- Direkter Zugriff auf Code im Root-Path ---
    if path != "/" and len(path) > 1:  # Alles außer root path
        code = unquote(path[1:])  # Entferne das führende "/"
        filename = os.path.join(STORAGE_DIR, f"{code}.txt")

        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()

            html_path = os.path.join(VIEW_DIR, "view.html")
            if os.path.exists(html_path):
                with open(html_path, "r", encoding="utf-8") as f:
                    template = f.read()
                html = template.replace("{{CONTENT}}", content).replace("{{CODE}}", code)
                start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
                return [html.encode("utf-8")]
            else:
                start_response("200 OK", [("Content-Type", "text/plain; charset=utf-8")])
                return [content.encode("utf-8")]
        else:
            # Für nicht existierende Codes - NGINX wird 404 handeln
            start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
            return ["".encode("utf-8")]

    # --- Root: Hauptseite ---
    index_file = os.path.join("./static", "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            html = f.read()
        start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
        return [html.encode("utf-8")]

    # --- Für alle anderen Pfade - NGINX wird 404 handeln ---
    start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
    return ["".encode("utf-8")]