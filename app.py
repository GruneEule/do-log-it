import os
import random
import string
from urllib.parse import parse_qs

# Ordner für gespeicherte Logs
STORAGE_DIR = "storage"
os.makedirs(STORAGE_DIR, exist_ok=True)

def generate_id(length=6):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def application(environ, start_response):
    path = environ.get('PATH_INFO', '/')
    method = environ.get('REQUEST_METHOD', 'GET')

    if path.startswith("/api/share") and method == 'POST':
        try:
            size = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
            size = 0
        body = environ['wsgi.input'].read(size).decode('utf-8')
        data = parse_qs(body)
        code_text = data.get('code', [''])[0]

        if not code_text.strip():
            status = '400 Bad Request'
            headers = [('Content-type', 'text/plain; charset=utf-8')]
            start_response(status, headers)
            return [b'No code provided']

        log_id = generate_id()
        file_path = os.path.join(STORAGE_DIR, f"{log_id}.txt")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code_text)

        status = '200 OK'
        headers = [('Content-type', 'text/plain; charset=utf-8')]
        start_response(status, headers)
        return [f"/view/{log_id}".encode('utf-8')]

    elif path.startswith("/view/"):
        log_id = path.split("/")[-1]
        file_path = os.path.join(STORAGE_DIR, f"{log_id}.txt")
        if not os.path.isfile(file_path):
            status = '404 Not Found'
            headers = [('Content-type', 'text/plain; charset=utf-8')]
            start_response(status, headers)
            return [b'Log not found']

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        status = '200 OK'
        headers = [('Content-type', 'text/plain; charset=utf-8')]
        start_response(status, headers)
        return [content.encode('utf-8')]

    else:  # Index
        status = '200 OK'
        headers = [('Content-type', 'text/html; charset=utf-8')]
        start_response(status, headers)
        with open('static/index.html', 'rb') as f:
            return [f.read()]
