from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

# Return a new base class and store its value in the Base variable
Base = declarative_base()

class User(Base):
    """Model class for storing user information."""
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

class Category(Base):
    """Model class for storing a category."""
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

class Item(Base):
    """Model class for storing an item."""
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(800))
    cat_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

# Create (if it doesn't exist) and connect to the database
engine = create_engine('sqlite:///catalog.db')

# Add the model classes as new tables in the database
Base.metadata.create_all(engine)

# Bind the engine to the Base class
Base.metadata.bind = engine

# Create a link of communication between the code executions and the engine
DBSession = sessionmaker(bind=engine)

# Create an instance of DBSession() and store it in the session variable
session = DBSession()

def addCategories():
    """Adds categories to the Category table."""

    # Add the Chinese category
    cat1 = Category(name='Chinese')
    session.add(cat1)
    session.commit()

    # Add the Japanese category
    cat2 = Category(name='Japanese')
    session.add(cat2)
    session.commit()

    # Add the Korean category
    cat3 = Category(name='Korean')
    session.add(cat3)
    session.commit()

    # Add the Thai category
    cat4 = Category(name='Thai')
    session.add(cat4)
    session.commit()

    # Add the Vietnamese category
    cat5 = Category(name='Vietnamese')
    session.add(cat5)
    session.commit()

    # Add the Other category
    cat6 = Category(name='Other')
    session.add(cat6)
    session.commit()

    print('Categories added!')

# Populate the database with categories (if they don't exist)
if len(session.query(Category).all()) == 0:
    addCategories()
