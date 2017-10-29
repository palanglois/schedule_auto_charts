#!/usr/bin/python3
# -*- coding: utf-8 -*-

import http.server
import json
import urllib
from jinja2 import Template


class MyHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, main_window, *args):
        self.main_window = main_window
        super().__init__(*args)

    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()

    def do_GET(s):
        """Respond to a GET request."""
        if s.path == '/':
            with open('templates/charts.html', 'r') as input_template:
                s.send_response(200)
                s.send_header("Content-type", "text/html")
                s.end_headers()
                content = Template(input_template.read())
                s.wfile.write(bytes(content.render(**s.main_window.render_dict["global_doughnut"]), "utf-8"))
        elif s.path[-2:] == 'js':
            try:
                with open(s.path[1:], 'r') as aux_file:
                    s.send_response(200)
                    s.send_header("Content-type", "application/javascript")
                    s.end_headers()
                    s.wfile.write(bytes(aux_file.read(), "utf-8"))
            except OSError as e:
                print(e)
                return
        elif s.path[-3:] == 'css':
            try:
                with open(s.path[1:], 'r') as aux_file:
                    s.send_response(200)
                    s.send_header("Content-type", "text/css")
                    s.end_headers()
                    css_file_str = aux_file.read()
                    s.wfile.write(bytes(css_file_str, "utf-8"))
            except OSError as e:
                print(e)
                return
        elif s.path.endswith('favicon.ico'):
            try:
                with open("static/favicon.ico", 'rb') as aux_file:
                    s.send_response(200)
                    s.send_header("Content-type", "image/ico")
                    s.end_headers()
                    s.wfile.write(aux_file.read())
            except OSError as e:
                print(e)
                return
        else:
            print("Error : could not load file %s" % s.path)

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
                rendered_content = content.render(**s.main_window.render_dict[label_clicked])
                s.wfile.write(bytes(rendered_content, "utf-8"))
        elif s.path == '/getMonthEvents':
            s.send_response(200)
            s.send_header("Content-type", "application/json")
            s.end_headers()
            length = int(s.headers['Content-Length'])
            post_data = urllib.parse.parse_qs(s.rfile.read(length).decode('utf-8'))
            s.wfile.write(bytes(s.main_window.stats_computer.get_events_from_mounth
                                (int(post_data["year"][0]), int(post_data["month"][0])), "utf-8"))
