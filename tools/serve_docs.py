"""Serve docs/ at http://localhost:8766 for local preview.

    python tools/serve_docs.py [port]
"""
import functools, http.server, os, sys
port = int(sys.argv[1]) if len(sys.argv) > 1 else 8766
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs')
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=root)
print(f'Serving {os.path.normpath(root)} at http://localhost:{port}/  (Ctrl+C to stop)')
http.server.ThreadingHTTPServer(('127.0.0.1', port), handler).serve_forever()
