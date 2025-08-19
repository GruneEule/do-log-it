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

    # --- API: Text hochladen ---
    if path == "/api/share" and method == "POST":
        try:
            size = int(environ.get("CONTENT_LENGTH", 0))
        except (ValueError):
            size = 0

        body = environ["wsgi.input"].read(size).decode("utf-8").strip()
        if not body:
            start_response("200 OK", [("Content-Type", "text/plain; charset=utf-8")])
            return ["Kein Text übermittelt".encode("utf-8")]

        code = generate_code()
        filename = os.path.join(STORAGE_DIR, f"{code}.txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(body)

        start_response("200 OK", [("Content-Type", "text/plain; charset=utf-8")])
        return [f"/view/{code}".encode("utf-8")]

    # --- GUI /view/{code} ---
    if path.startswith("/view/"):
        code = unquote(path[len("/view/"):])
        filename = os.path.join(STORAGE_DIR, f"{code}.txt")
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = "Datei nicht gefunden"

        html_path = os.path.join(VIEW_DIR, "view.html")
        if os.path.exists(html_path):
            with open(html_path, "r", encoding="utf-8") as f:
                template = f.read()
            # Korrekte Zuordnung der Platzhalter
            html = template.replace("{{CONTENT}}", content).replace("{{CODE}}", code)
            start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
            return [html.encode("utf-8")]
        else:
            start_response("200 OK", [("Content-Type", "text/plain; charset=utf-8")])
            return [content.encode("utf-8")]

    # --- Root ---
    index_file = os.path.join("./static", "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            html = f.read()
        start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
        return [html.encode("utf-8")]

    # --- Default ---
    start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
    return ["404 Not Found".encode("utf-8")]