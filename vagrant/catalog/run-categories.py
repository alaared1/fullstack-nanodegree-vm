# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, Category, User, Item

engine = create_engine("sqlite:///catalogapp.db")
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won"t be persisted into the database until you call
# session.commit(). If you"re not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

session.query(Item).delete()
session.query(Category).delete()
session.query(User).delete()
session.commit()
# Populating the categories


category1 = Category(name="Laptops")
session.add(category1)
session.commit()

category2 = Category(name="Desktop PC's")
session.add(category2)
session.commit()

category3 = Category(name="Monitors")
session.add(category3)
session.commit()

category4 = Category(name="Graphic Cards")
session.add(category4)
session.commit()

category5 = Category(name="CPU's")
session.add(category5)
session.commit()

category6 = Category(name="Tablets")
session.add(category6)
session.commit()

category7 = Category(name="Smartphones")
session.add(category7)
session.commit()

category8 = Category(name="Consoles")
session.add(category8)
session.commit()

category9 = Category(name="TV's")
session.add(category9)
session.commit()

category10 = Category(name="Accessories")
session.add(category10)
session.commit()


print("Categories added successfully!")