#!/usr/bin/python3
# -*- coding: utf-8 -*-

import datetime
import csv
import os

class ComputeStats:

    def __init__(self):
        self.current_saved_time = datetime.datetime.now()

        # Load the currently saved data_base
        self.loaded_database = dict()
        if os.path.isfile("database.db"):
          with open("database.db", "r") as input_database:
            data_database = csv.reader(input_database)
            for categorie in data_database:
              if len(categorie) >= 2:
                self.loaded_database[categorie[0]] = float(" ".join(categorie[1:]))

        # Load the categories defined by the user
        with open("categories.config", "r") as input_categories:
          data_categories = csv.reader(input_categories)
          for categorie in data_categories:
            if categorie[0] not in self.loaded_database:
              print("Adding new categorie : %s" % categorie)
              self.loaded_database[categorie[0]] = 0

    def start_chronometer(self):
        self.current_saved_time = datetime.datetime.now()

    def get_current_time(self):
        return datetime.datetime.now() - self.current_saved_time

    def update_database(self, categorie, value):
        self.loaded_database[categorie] += value
        with open("database.db", "w") as output_database:
          writer = csv.writer(output_database)
          for categorie, value in self.loaded_database.items():
            writer.writerow([categorie, str(value)])

