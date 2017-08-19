from ComputeStats import Category, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import argparse


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
    engine = create_engine(args.db_name)
    Base.metadata.create_all(engine)
    # Base.metadata.bind = engine
    # DBSession = sessionmaker(bind=engine)
    # session = DBSession()
    # new_category = Category(name='Entreprise', total_time='10')
    # session.add(new_category)
    # session.commit()


if __name__ == '__main__':
    main()
