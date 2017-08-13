#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import datetime
import webbrowser
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QLabel, QInputDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer, Qt
from ComputeStats import *
import http.server
from multiprocessing import Process
from custom_server import MyHandler
from socketserver import ThreadingMixIn


class ThreadedHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    """Handle requests in a separate thread."""


class MainWindow(QWidget):
    
    def __init__(self):
        super().__init__()
        self.webThread = 0

        self.label_chrono = None 
        self.stats_computer = ComputeStats()
        self.loaded_categories = list(self.stats_computer.loaded_database.keys())
        self.the_db = self.stats_computer.loaded_database
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
            self.webThread.terminate()
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
        button_stats = QPushButton("Stats")
        grid.addWidget(button_start, 0, 0)
        grid.addWidget(button_stop, 0, 1)
        grid.addWidget(button_stats, 2, 0, 1, 2)

        # Adding label for chronometer
        self.label_chrono = QLabel(str(datetime.timedelta(microseconds=0)), self)
        self.label_chrono.setAlignment(Qt.AlignCenter)
        grid.addWidget(self.label_chrono, 1, 0, 1, 2)

        # Adding a timer for displaying the chronometer
        self.timer = QTimer()
   
        # Connecting buttons to methods
        button_start.clicked.connect(self.start_chronometer)
        button_stop.clicked.connect(self.stop_and_display)
        button_stats.clicked.connect(self.display_charts)

        # Connecting the timer
        self.timer.timeout.connect(self.display_time)

        self.show()

    def display_time(self):
        current_time = self.stats_computer.get_current_time()
        self.label_chrono.setText(str(current_time))
    def start_chronometer(self):
        self.stats_computer.start_chronometer()
        self.timer.start(100)

    def stop_and_display(self):
        time = self.stats_computer.get_current_time()
        self.timer.stop()
        self.label_chrono.setText(str(time))
        categorie, ok = QInputDialog.getItem(self, 
          "Select a category", "List of loaded categories", 
          self.loaded_categories, 0, False)
        if ok:
            self.stats_computer.update_database(categorie, time.total_seconds())

    def make_render_dict(self, the_db):
        total_time = sum(list(the_db.values()))
        scale_factors = [int(100*x/total_time) for x in list(the_db.values())]
        colors = list(self.chartColors.values())[:len(the_db)]
        labels = list(the_db.keys())
        return {'scale_factors':scale_factors, 'colors':colors, 'labels':labels}

    def display_charts(self):
        the_db = self.stats_computer.loaded_database
        if self.webThread != 0:
            self.httpd.server_close()
            self.webThread.terminate()
            self.webThread.join()
        # Initiate the server
        def handler(*args):
          MyHandler(self.make_render_dict(the_db), *args)
        server_class = ThreadedHTTPServer
        self.httpd = server_class(('localhost', 5000), handler)
        self.webThread = Process(target=self.httpd.serve_forever)
        self.webThread.start()

        url = "http://127.0.0.1:5000/"
        webbrowser.open(url, new=2)
        

def main():
  app = QApplication(sys.argv)
  my_main_window = MainWindow()
  sys.exit(app.exec_())

if __name__ == '__main__':
  main()

