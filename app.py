import os
from wsgiref.simple_server import make_server

# Ordner für gespeicherte Logs
STORAGE = "storage"
if not os.path.exists(STORAGE):
    os.makedirs(STORAGE)

# Template für die Ansicht im Browser
VIEW_TEMPLATE = "static-view/view.html"

def render_template(template_path, context):
    """Lädt HTML-Template und ersetzt Platzhalter {{key}} mit context[key]."""
    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()
    for key, value in context.items():
        html = html.replace(f"{{{{{key}}}}}", value)
    return html

def application(environ, start_response):
    path = environ.get("PATH_INFO", "/")

    # API: Text teilen
    if path.startswith("/api/share"):
        try:
            size = int(environ.get("CONTENT_LENGTH", 0))
        except (ValueError, TypeError):
            size = 0
        body = environ["wsgi.input"].read(size).decode("utf-8").strip()
        if not body:
            start_response("400 Bad Request", [("Content-Type", "text/plain")])
            return [b"Kein Text übermittelt"]

        # Zufälliger 6-stelliger Hex-Code
        code = os.urandom(3).hex()
        with open(os.path.join(STORAGE, f"{code}.txt"), "w", encoding="utf-8") as f:
            f.write(body)

        start_response("200 OK", [("Content-Type", "text/plain")])
        return [code.encode("utf-8")]

    # View: Text anzeigen
    elif path.startswith("/view/"):
        code = path.split("/view/")[1]
        filepath = os.path.join(STORAGE, f"{code}.txt")
        if os.path.isfile(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            html = render_template(VIEW_TEMPLATE, {"code": code, "content": content})
            start_response("200 OK", [("Content-Type", "text/html")])
            return [html.encode("utf-8")]
        else:
            start_response("404 Not Found", [("Content-Type", "text/plain")])
            return [b"Not Found"]

    # Sonstige Pfade
    else:
        start_response("404 Not Found", [("Content-Type", "text/plain")])
        return [b"Not Found"]

# Optional: lokal testen
if __name__ == "__main__":
    port = 8000
    print(f"Running on http://localhost:{port}")
    with make_server("", port, application) as httpd:
        httpd.serve_forever()
