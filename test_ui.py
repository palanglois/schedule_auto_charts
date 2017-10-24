import unittest
import sys
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from main import MainWindow
from socket import error as socket_error
from ComputeStats import Category, Base, SubCategory, ComputeStats
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
import os

app = QApplication(sys.argv)


class TestServer(unittest.TestCase):

    def testOpenClose(self):
        """
        Open and close the stats windows twice in order to check that the server restarts properly
        :return:
        """
        is_program_ok = True
        msg = ""
        try:
            my_main_window = MainWindow()
            my_main_window.display_charts()
            my_main_window.web_viewer.close()
            my_main_window.display_charts()
            my_main_window.web_viewer.close()
        except socket_error as e:
            is_program_ok = False
            msg = str(e)
        self.assertTrue(is_program_ok, msg=msg)


class TestDB(unittest.TestCase):

    def setUp(self):
        """
        Creating a default database thanks to the data in categories_test_default.config
        :return:
        """
        self.test_db_path = "sqlite:///test_base.db"
        try:
            os.remove(self.test_db_path[10:])
        except OSError as e:
            pass
        engine = create_engine(self.test_db_path)
        self.test_json_path = "categories_test_default.config"
        Base.metadata.create_all(engine)
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()
        with open(self.test_json_path, 'r') as input_file:
            data = json.load(input_file)
            # print(data)
            for cat, subcats in data.items():
                new_category = Category(name=cat, total_time='10')
                self.session.add(new_category)
                for subcat in subcats:
                    new_subcategory = SubCategory(name=subcat, total_time='5', parent=new_category)
                    self.session.add(new_subcategory)
            self.session.commit()

    def tearDown(self):
        try:
            os.remove(self.test_db_path[10:])
        except OSError as e:
            print(e, "Problem when tearing down the test")
            pass

    def testAddCategory(self):
        temp_file_path = 'temp.json'
        with open(self.test_json_path, "r") as input_file:
            data = json.load(input_file)
            # Add a brand new category
            data["New_test_category"] = ["New_test_category_general"]
            # Add a new subcategory to an already existing category
            data["Entreprise"].append("Entreprise_test")
        with open(temp_file_path, "w") as output_file:
            json.dump(data, output_file)
        my_compute_stats = ComputeStats(db_path=self.test_db_path, user_data=temp_file_path)

        # Test that New_test_category has been added
        category_in_db = my_compute_stats.session.query(Category).filter(Category.name == "New_test_category").one()
        self.assertIsNotNone(category_in_db, msg="Problem when adding a whole new category")

        # Test that Entreprise_test has been added as a subcategory of Entreprise
        subcategory_in_db = my_compute_stats.session.query(SubCategory)\
            .filter(SubCategory.name ==  "Entreprise_test").one()
        self.assertIsNotNone(subcategory_in_db, msg="Problem when adding a new subcategory to an already existing "
                                                    "category")
        self.assertEqual(subcategory_in_db.parent.name, "Entreprise", msg="Problem with parent association of the "
                                                                          "new subcategory")

        # Test that all the subcategories of Entreprise have been preserved
        entreprise_in_db = my_compute_stats.session.query(Category).filter(Category.name == "Entreprise").one()
        entreprise_subcats = [s for s in my_compute_stats.session.query(SubCategory)
            .filter(SubCategory.parent == entreprise_in_db).all()]
        self.assertEqual(len(entreprise_subcats), 4, msg="Problem with preserving the number of subcategories"
                                                         "when a subcategory is being added")

        try:
            os.remove(temp_file_path)
        except OSError:
            pass

    def testAddEvent(self):
        my_compute_stats = ComputeStats(db_path=self.test_db_path, user_data=self.test_json_path)

        # Create a test event and submit it
        category = "Entreprise"
        subcategory = "Voyages"
        note = "test note"
        begin_time = datetime(2017, 10, 24, 17, 7, 0)
        end_time = datetime(2017, 10, 24, 17, 7, 3)
        my_compute_stats.update_database(category, subcategory, note, begin_time, end_time)

        # Check that it has been included
        entreprise_in_db = my_compute_stats.session.query(Category).filter(Category.name == "Entreprise").one()
        self.assertEqual(entreprise_in_db.total_time, 13, "Problem when inserting an event")


if __name__ == '__main__':
    unittest.main()
