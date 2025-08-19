import os, random, string
from urllib.parse import parse_qs

STORAGE_DIR = "storage"

def generate_id(length=6):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def application(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET")

    if path.startswith("/api/save") and method == "POST":
        try:
            size = int(environ.get("CONTENT_LENGTH", 0))
        except ValueError:
            size = 0
        body = environ["wsgi.input"].read(size).decode("utf-8")
        data = parse_qs(body)
        content = data.get("content", [""])[0]

        if not os.path.exists(STORAGE_DIR):
            os.makedirs(STORAGE_DIR)

        paste_id = generate_id()
        with open(os.path.join(STORAGE_DIR, paste_id + ".txt"), "w") as f:
            f.write(content)

        start_response("200 OK", [("Content-Type", "application/json")])
        return [f'{{"id": "{paste_id}"}}'.encode("utf-8")]

    elif path.startswith("/api/get/"):
        paste_id = path.split("/")[-1]
        file_path = os.path.join(STORAGE_DIR, paste_id + ".txt")
        if os.path.exists(file_path):
            with open(file_path) as f:
                content = f.read()
            start_response("200 OK", [("Content-Type", "text/plain; charset=utf-8")])
            return [content.encode("utf-8")]
        else:
            start_response("404 Not Found", [("Content-Type", "text/plain")])
            return [b"Not Found"]

    start_response("404 Not Found", [("Content-Type", "text/plain")])
    return [b"Not Found"]
