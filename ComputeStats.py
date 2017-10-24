#!/usr/bin/python3
# -*- coding: utf-8 -*-

import datetime
import csv
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
import json

Base = declarative_base()


class Category(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    total_time = Column(Integer, nullable=False)
    subcategory = relationship("SubCategory")


class SubCategory(Base):
    __tablename__ = "subcategory"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("category.id"))
    parent = relationship("Category")
    name = Column(String(250), nullable=False)
    total_time = Column(Integer, nullable=False)


class Event(Base):
    __tablename__ = "event"
    id = Column(Integer, primary_key=True)
    subcategory_id = Column(Integer, ForeignKey("subcategory.id"))
    subcategory = relationship("SubCategory")
    begin_date = Column(Integer, nullable=False)
    end_date = Column(Integer, nullable=False)
    note = Column(String(2000))


class ComputeStats:
    def __init__(self, db_path='sqlite:///my_base.db', user_data="categories_new.config"):
        self.current_saved_time = datetime.datetime.now()

        # Load the currently saved database
        # self.loaded_database = dict()
        self.user_data = user_data
        self.db_path = db_path
        self.session = self.init_orm()
        self.categories = {}
        self.load_categories_and_add_new()

    def load_categories_and_add_new(self):
        # Loading known categories
        for category in self.session.query(Category).all():
            subcategories = self.session.query(SubCategory).filter(SubCategory.parent == category)
            self.categories[category.name] = [subcategory.name for subcategory in subcategories]
        # Updating categories with the user defined
        with open(self.user_data, "r") as input_categories_file:
            user_categories = json.load(input_categories_file)
            for category in user_categories:
                # Check that category is already in db
                if category not in self.categories:
                    print("Adding new category : %s" % category)
                    self.categories[category] = []
                    new_category = Category(name=category, total_time='0')
                    self.session.add(new_category)
                for subcategory in user_categories[category]:
                    # Check that subcategory is already in db
                    if subcategory not in self.categories[category]:
                        print("Adding new subcategory %s for category %s" % (subcategory, category))
                        self.categories[category].append(subcategory)
                        category_in_db = self.session.query(Category).filter(Category.name == category).first()
                        new_subcategory = SubCategory(name=subcategory, total_time='0', parent=category_in_db)
                        self.session.add(new_subcategory)
        # print(self.categories)

    def load_categories_and_add_new_old(self):
        self.categories = [c.name for c in self.session.query(Category).all()]

        # Load the categories defined by the user
        with open("categories.config", "r") as input_categories:
            data_categories = csv.reader(input_categories)
            for categorie in data_categories:
                categorie_name = " ".join(categorie)
                if categorie_name not in self.categories:
                    print("Adding new category : %s" % categorie)
                    self.categories.append(categorie_name)
                    new_category = Category(name=categorie_name, total_time='0')
                    self.session.add(new_category)
                    self.session.commit()

    def init_orm(self):
        engine = create_engine(self.db_path)
        Base.metadata.bind = engine
        db_session = sessionmaker(bind=engine)
        return db_session()

    def start_chronometer(self):
        self.current_saved_time = datetime.datetime.now()

    def get_current_relative_time(self):
        return datetime.datetime.now() - self.current_saved_time

    @staticmethod
    def get_current_time():
        return datetime.datetime.now()

    def update_database(self, category, subcategory, note, begin_time, end_time):
        # Converting the dates for the data base
        begin_date = int((begin_time - datetime.datetime(1970, 1, 1)).total_seconds())
        end_date = int((end_time - datetime.datetime(1970, 1, 1)).total_seconds())

        # Updating the total time for the category and subcategory
        spent_time = (end_time - begin_time).total_seconds()
        category_in_db = self.session.query(Category).filter(Category.name == category).one()
        subcategory_in_db = self.session.query(SubCategory).filter(SubCategory.name == subcategory).one()
        category_in_db.total_time += spent_time
        subcategory_in_db.total_time += spent_time

        # Creating and adding the new event to the database
        new_event = Event(begin_date=begin_date, end_date=end_date, note=note)
        self.session.add(new_event)
        self.session.commit()

    def get_database_dict(self):
        output_dict = dict()
        all_categories = self.session.query(Category).all()
        for categorie in all_categories:
            output_dict[categorie.name] = categorie.total_time
        return output_dict
