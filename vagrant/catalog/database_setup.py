from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy import create_engine, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
 
Base = declarative_base()

class Category(Base):
    __tablename__ = 'category'
   
    id = Column(Integer, primary_key=True)
    title = Column(String(80), nullable=False, unique=True)

    @property
    def serialize(self):
       """Returns object in serialized format"""
       return 
       {
           'title'        : self.title,
           'id'           : self.id,
       }

    def asDict(self, items):
       """Returns object in serialized format"""
       dictObj = \
       {
           'title'        : self.title,
           'id'           : self.id,
           'item'         : [i.asDict() for i in items]
       }
       return dictObj
 

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(80), nullable=False, unique=True)
    picture = Column(String(120))


class CategoryItem(Base):
    __tablename__ = 'category_item'

    id = Column(Integer, primary_key = True)
    title =Column(String(80), nullable = False)
    description = Column(String(500))
    date_created = Column(DateTime, nullable=False, default=datetime.now)
    image = Column(String(120))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    __table_args__ = (UniqueConstraint('category_id', 'title', \
      name='_category_item_uc'),)


    @property
    def serialize(self):
       """Return object in serialized format"""
       return
       {
           'title'        : self.title,
           'description'  : self.description,
           'id'           : self.id,
       }

    def asDict(self):
       """Return object in serialized format"""
       dictObj = \
       {
           'title'        : self.title,
           'description'  : self.description,
           'id'           : self.id,
           'category_id'  : self.category_id,
           'creator_name' : self.user.name
       }
       return dictObj


engine = create_engine('sqlite:///catalog.db')
 

Base.metadata.create_all(engine)
