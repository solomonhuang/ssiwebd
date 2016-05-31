try:
    import http.server as http_server
except ImportError:
    import SimpleHTTPServer as http_server
import os
import os.path
import re
import argparse

SERVER_ROOT = "."
SSI_EXTENSIONS = [".shtml", ".shtm"]
ADDR = '127.0.0.1'
PORT = 8080
SSI_INCLUDE_LEVEL = 5

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
    if level > SSI_INCLUDE_LEVEL:
        return content

    # <!--#include virtual="menu.cgi" -->
    # <!--#include file="footer.html" -->
    finder = re.compile('''<!--#include (file|virtual)=(?P<quote>["'])(?P<file>.*?)(?P=quote) *?-->''')
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

    #print(ssi_lists)
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

class SSIHTTPRequestHandler(http_server.SimpleHTTPRequestHandler):
    def do_GET(self):
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
                break

        else:
            super().do_GET()

def main():
    global ADDR, PORT, SERVER_ROOT, SSI_EXTENSIONS, SSI_INCLUDE_LEVEL
    parser = argparse.ArgumentParser(prog='ssiwebd')
    parser.add_argument('--bind', type=str, default=ADDR, help='Listening address')
    parser.add_argument('-p', '--port', type=int, default=PORT, help='Listening port')
    parser.add_argument('-r', '--root', type=str, default=SERVER_ROOT, help='Document root')
    parser.add_argument('-e', type=str, nargs='*', default=SSI_EXTENSIONS, help='SSI extensions')
    parser.add_argument('-l', metavar='level', type=int, default=SSI_INCLUDE_LEVEL, help='SSI include depth level')

    args = parser.parse_args()
    ADDR = args.bind
    PORT = args.port
    SERVER_ROOT = args.root
    SSI_EXTENSIONS = args.e
    SSI_INCLUDE_LEVEL = args.l

    os.chdir(args.root)
    webd = http_server.HTTPServer((ADDR, PORT),SSIHTTPRequestHandler)
    print("SSIWebd start listen {}:{}. Document root: {}".format(ADDR, PORT, SERVER_ROOT))
    print("SSI extension: {}".format(", ".join(SSI_EXTENSIONS)))
    try:
        webd.serve_forever()
    except KeyboardInterrupt:
        print('\nssiwebd closed')

if __name__ == '__main__':
    main()
