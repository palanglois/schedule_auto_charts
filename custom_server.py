#!/usr/bin/python3
# -*- coding: utf-8 -*-

import http.server
import urllib
from jinja2 import Template


class MyHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, the_dict, *args):
        self.the_dict = the_dict
        super().__init__(*args)

    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()

    def do_GET(s):
        """Respond to a GET request."""
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        if s.path == '/':
            with open('templates/charts.html', 'r') as input_template:
                content = Template(input_template.read())
                s.wfile.write(bytes(content.render(**s.the_dict["global_doughnut"]), "utf-8"))
        elif s.path[-2:] == 'js':
            try:
                with open(s.path[1:], 'r') as aux_file:
                    s.wfile.write(bytes(aux_file.read(), "utf-8"))
            except OSError as e:
                print(e)
                return

    def do_POST(s):
        """Respond to a POST request."""
        if s.path == '/getDoughnutScript.html':
            s.send_response(200)
            s.send_header("Content-type", "application/json")
            s.end_headers()
            length = int(s.headers['Content-Length'])
            post_data = urllib.parse.parse_qs(s.rfile.read(length).decode('utf-8'))
            label_clicked = post_data["label"][0]
            with open('templates/getDoughnutScript.html', 'r') as input_template:
                input_string = input_template.read()
                content = Template(input_string)
                rendered_content = content.render(**s.the_dict[label_clicked])
                s.wfile.write(bytes(rendered_content, "utf-8"))
