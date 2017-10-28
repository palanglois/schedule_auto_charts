#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QLabel, QInputDialog, QLineEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer, Qt, QUrl
from threading import Thread
import platform
if platform.system() == "Windows":
    from qtpy.QtWebEngineWidgets import QWebEngineView
else:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
from ComputeStats import *
import http.server
from custom_server import MyHandler
from socketserver import ThreadingMixIn
from OpenGL import GLU
from OpenGL import GL


class ThreadedHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    """Handle requests in a separate thread."""


class MainWindow(QWidget):
    
    def __init__(self):
        super().__init__()
        self.webThread = 0
        self.httpd = None

        self.label_chrono = None 
        self.stats_computer = ComputeStats()
        self.loaded_categories = self.stats_computer.categories
        self.chartColors = {
          "red": u"rgb(255, 99, 132)",
          "orange": u"rgb(255, 159, 64)",
          "yellow": u"rgb(255, 205, 86)",
          "green": u"rgb(75, 192, 192)",
          "blue": u"rgb(54, 162, 235)",
          "purple": u"rgb(153, 102, 255)",
          "grey": u"rgb(201, 203, 207)"
        }
        self.initUI()
       
    def closeEvent(self, event):
        if self.webThread != 0:
            self.httpd.shutdown()
            self.webThread.join()
        event.accept()
        
    def initUI(self):
        
        self.setGeometry(300, 300, 300, 220)
        self.setWindowTitle('Zouze time computer v1.0')
        self.setWindowIcon(QIcon('web.png'))        

        # Create a layout
        grid = QGridLayout()
        self.setLayout(grid)

        # Adding buttons
        button_start = QPushButton("START")
        button_stop = QPushButton("STOP")
        self.button_stats = QPushButton("Stats")
        grid.addWidget(button_start, 0, 0)
        grid.addWidget(button_stop, 0, 1)
        grid.addWidget(self.button_stats, 2, 0, 1, 2)

        # Adding label for chronometer
        self.label_chrono = QLabel(str(datetime.timedelta(microseconds=0)), self)
        self.label_chrono.setAlignment(Qt.AlignCenter)
        grid.addWidget(self.label_chrono, 1, 0, 1, 2)

        # Adding a timer for displaying the chronometer
        self.timer = QTimer()

        # Adding a web viewer
        self.web_viewer = QWebEngineView()
   
        # Connecting buttons to methods
        button_start.clicked.connect(self.start_chronometer)
        button_stop.clicked.connect(self.stop_and_display)
        self.button_stats.clicked.connect(self.display_charts)

        # Connecting the timer
        self.timer.timeout.connect(self.display_time)

        self.show()

    def display_time(self):
        current_time = self.stats_computer.get_current_relative_time()
        self.label_chrono.setText(".".join(str(current_time).split(".")[:-1]))

    def start_chronometer(self):
        self.stats_computer.start_chronometer()
        self.timer.start(100)

    def stop_and_display(self):
        begin_time = self.stats_computer.current_saved_time
        end_time = self.stats_computer.get_current_time()
        time = self.stats_computer.get_current_time()
        self.timer.stop()
        category, ok = QInputDialog.getItem(self,
                                            "Select a category", "List of loaded categories",
                                            [c for c in self.loaded_categories], 0, False)
        if not ok:
            return
        subcategory, ok = QInputDialog.getItem(self,
                                               "Select a subcategory", "List of loaded subcategories",
                                               self.loaded_categories[category], 0, False)
        if not ok:
            return
        note, ok = QInputDialog.getText(self, "Note", "Enter the note:", QLineEdit.Normal, "")
        if not ok:
            return
        self.stats_computer.update_database(category, subcategory, note, begin_time, end_time)

    def make_chart_dict(self, input_dict):
        total_time = sum(list(input_dict.values()))
        scale_factors = [int(100*x/total_time) if total_time != 0 else 0 for x in list(input_dict.values())]
        colors = list(self.chartColors.values())[:len(input_dict)]
        labels = list(input_dict.keys())
        return {'scale_factors': scale_factors, 'colors': colors, 'labels': labels}

    def make_render_dict(self, the_db):
        # total_time = sum(list(the_db.values()))
        # scale_factors = [int(100*x/total_time) if total_time != 0 else 0 for x in list(the_db.values())]
        # colors = list(self.chartColors.values())[:len(the_db)]
        # labels = list(the_db.keys())
        output_dict = {}
        output_dict["global_doughnut"] = self.make_chart_dict(the_db["global_doughnut"])
        for category in self.loaded_categories:
            output_dict[category] = self.make_chart_dict(the_db[category])
        return output_dict

    def display_charts(self):
        the_db = self.stats_computer.get_database_dict()
        if self.webThread != 0:
            self.httpd.shutdown()
            self.httpd.server_close()
            self.webThread.join()

        # Initiate the server
        def handler(*args):
            MyHandler(self.make_render_dict(the_db), *args)

        server_class = ThreadedHTTPServer
        self.httpd = server_class(('localhost', 5000), handler)
        self.webThread = Thread(target=self.httpd.serve_forever)
        self.webThread.daemon = True

        # Start the server
        self.webThread.start()

        # Display the charts on the web viewer
        url = "http://localhost:5000/"
        self.web_viewer.load(QUrl(url))
        self.web_viewer.setGeometry(300, 300, 600, 600)
        self.web_viewer.show()
        

def main():
    app = QApplication(sys.argv)
    my_main_window = MainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

