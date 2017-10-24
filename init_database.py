from ComputeStats import Category, Base, SubCategory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import argparse
import json
import os


def main():
    """
    This program initiates the database required in order to store the data.
    Mostly for development purpose.
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--db_name', default="")
    args = parser.parse_args()
    if args.db_name == "":
        args.db_name = 'sqlite:///my_base.db'
    try:
        os.remove(args.db_name[10:])
    except OSError:
        pass
    engine = create_engine(args.db_name)
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    with open("categories_new.config", 'r') as input_file:
        data = json.load(input_file)
        # print(data)
        for cat, subcats in data.items():
            new_category = Category(name=cat, total_time='0')
            session.add(new_category)
            for subcat in subcats:
                new_subcategory = SubCategory(name=subcat, total_time='5', parent=new_category)
                session.add(new_subcategory)
        session.commit()


if __name__ == '__main__':
    main()
