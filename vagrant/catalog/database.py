import os, sys, datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
 
Base = declarative_base()

# User table
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable = False)
    email = Column(String(250))
    picture = Column(String(1000))
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    modified_date = Column(DateTime, default=datetime.datetime.utcnow)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'picture': self.picture,
            'created_date': self.created_date,
            'modified_date': self.modified_date
        }


# Catgeory table
class Category(Base):
    __tablename__ = 'category'
   
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    items = relationship('Item')
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    modified_date = Column(DateTime, default=datetime.datetime.utcnow)

    # Json serializer
    @property
    def serialize(self):
        items = {}

        # serialize items object
        if self.items:
            items = [item.serialize for item in self.items]
            
        return {
            'name': self.name,
            'id': self.id,
            'items': items
        }


# Item table
class Item(Base):
    __tablename__ = 'item'


    name =Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    description = Column(String(10000))
    color = Column(String(50))
    price = Column(String(10))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category, backref=backref("children", cascade="all,delete"))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    modified_date = Column(DateTime, default=datetime.datetime.utcnow) 

    # Json serializer
    @property
    def serialize(self):
       
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'price': self.price,
            'cat_id': self.category_id
        }
 

engine = create_engine('sqlite:///catalogapp.db')
 

Base.metadata.create_all(engine)