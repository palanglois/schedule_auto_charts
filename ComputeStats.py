#!/usr/bin/python3
# -*- coding: utf-8 -*-

import datetime
import csv
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base()


class Category(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    total_time = Column(Integer, nullable=False)


class ComputeStats:
    def __init__(self):
        self.current_saved_time = datetime.datetime.now()

        # Load the currently saved database
        # self.loaded_database = dict()
        self.session = self.init_orm()
        self.categories = [c.name for c in self.session.query(Category).all()]

        # Load the categories defined by the user
        with open("categories.config", "r") as input_categories:
            data_categories = csv.reader(input_categories)
            for categorie in data_categories:
                categorie_name = " ".join(categorie)
                if categorie_name not in self.categories:
                    print("Adding new categorie : %s" % categorie)
                    self.categories.append(categorie_name)
                    new_category = Category(name=categorie_name, total_time='0')
                    self.session.add(new_category)
                    self.session.commit()

    @staticmethod
    def init_orm():
        engine = create_engine('sqlite:///my_base.db')
        Base.metadata.bind = engine
        db_session = sessionmaker(bind=engine)
        return db_session()

    def start_chronometer(self):
        self.current_saved_time = datetime.datetime.now()

    def get_current_time(self):
        return datetime.datetime.now() - self.current_saved_time

    def update_database(self, categorie, value):
        to_be_modified = self.session.query(Category).filter(Category.name == categorie).one()
        to_be_modified.total_time += value
        self.session.commit()

    def get_database_dict(self):
        output_dict = dict()
        all_categories = self.session.query(Category).all()
        for categorie in all_categories:
            output_dict[categorie.name] = categorie.total_time
        return output_dict
