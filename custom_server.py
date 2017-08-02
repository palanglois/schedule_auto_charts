#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import http.server
from flask import render_template, Flask


HOST_NAME = 'localhost'
PORT_NUMBER = 5000


class MyHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self):
        super(MyHandler, self).__init__()
        self.app = Flask(__name__)
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
    def do_GET(s):
        """Respond to a GET request."""
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        # s.wfile.write(bytes("<html><head><title>Title goes here.</title></head>", "utf-8"))
        # s.wfile.write(bytes("<body><p>This is a test.</p>", "utf-8"))
        # If someone went to "http://something.somewhere.net/foo/bar/",
        # then s.path equals "/foo/bar/".
        # s.wfile.write(bytes("<p>You accessed path: %s</p>" % s.path, "utf-8"))
        # s.wfile.write(bytes("</body></html>", "utf-8"))
        with self.app.context():
            s.wfile.write(bytes(render_template('templates/charts2.html', **{}), "utf-8"))

if __name__ == '__main__':
    server_class = http.server.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print(time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER))
