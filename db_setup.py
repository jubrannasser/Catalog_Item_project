#!/usr/bin/env python

import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), nullable=False)
    email = Column(String(80), nullable=False)
    password_hash = Column(String(64))

    def hash_password(self, password):
        self.password_hash = custom_app_context.encrypt(password)

    def verify_password(self, password):
        return custom_app_context.verify(password, self.password_hash)


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    item = relationship("Item", back_populates="category", cascade="delete")

    @property
    def serialize(self):
        data = {
            'id': self.id,
            'name': self.name,
        }

        # Bring all the items in the category
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        m = session.query(Item).filter_by(category_id=self.id).all()
        if m != []:
            items = [i.serialize for i in m]
            data['items'] = items

        return data


class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    photo = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship("Category", back_populates="item")
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return{
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'photo_name': self.photo,
        }

    # return item info with its category
    @property
    def serialize_withcategory(self):
        return{
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'photo_name': self.photo,
            'category': self.category.name,
        }
engine = create_engine('sqlite:///categitems.db')

Base.metadata.create_all(engine)
