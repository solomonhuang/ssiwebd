import http.server
import os.path
import re

SERVER_ROOT = "."
SSI_EXTENSIONS = [".shtml", ".shtm"]

def resolve_file_path(root, path, indexes=["index.html", "index.htm"]):
    paths = []
    if path[-1] == "/":
        for index in indexes:
            paths.append(root + path + index)
    else:
        paths.append(root + path)
    return paths

def read_ssi_file(file):
    try:
        with open(file, "r") as f:
            content = f.read()
            return content
    except FileNotFoundError:
        return ""

def do_SSI_scan(content, level=1):
    if level > 5:
        return content

    # <!--#include virtual="menu.cgi" -->
    # <!--#include file="footer.html" -->
    finder = re.compile('''<!--#include file=(?P<quote>["'])(?P<file>.*?)(?P=quote) -->''')
    # equal: re.compile('''<!--#include file=(["'])(.*?)\\1 -->''')
    matches = re.finditer(finder, content)

    ssi_lists = []
    for matched in matches:
        span = matched.span()
        m = {}
        m['start'] = span[0]
        m['stop'] = span[1]
        m['file'] = matched.group('file')
        ssi_lists.append(m)

    print(ssi_lists)
    result = ""
    pin = 0
    for matched in ssi_lists:
        result += content[pin:matched['start']]
        result += read_ssi_file(matched['file'])
        pin = matched['stop']
    result += content[pin:]
    result = do_SSI_scan(result, level+1)
    return result

def do_SSI_file(file):
    with open(file, 'r') as f:
        content = f.read()
        return do_SSI_scan(content)

class SSIHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        print(self.path)
        files = resolve_file_path(".", self.path)
        for file in files:
            if not os.path.exists(file):
                continue
            ext = os.path.splitext(file)[1]
            if ext in SSI_EXTENSIONS:
                content = str.encode(do_SSI_file(file))
                self.protocol_version = "HTTP/1.1"
                self.send_response(200, 'OK')
                self.send_header('Content-type', 'text/html')
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)

        else:
            super().do_GET()


webd = http.server.HTTPServer(("",8080),SSIHTTPRequestHandler)
webd.serve_forever()
