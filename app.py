#!/usr/bin/env python3
#
# An item catalog application with a user registration and authentication
# system, complete with full CRUD operations.

from flask import Flask, render_template

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Category, Item

# Connect to the database and bind the engine to the Base class
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

# Create a session
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

@app.route('/')
def index():
    # Get the categories
    categories = session.query(Category).all()

    # Get the most recently added items
    recent_items = session.query(Item).order_by(desc(Item.id)).limit(8).all()

    # Truncate each item's description for its listing
    for item in recent_items:
        if len(item.description) > 80:
            item.description = item.description[:80] + '...'
    return render_template('index.html', categories=categories, items=recent_items)


# Run the server if the script is run directly from the Python interpreter
if __name__ == '__main__':
    app.secret_key = '9?\xf8\x9b\xa2\x11\xaas\xf1r\xf3bI\xd27{\xad\xdc[s\x17'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
