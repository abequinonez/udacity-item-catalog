#!/usr/bin/env python3
#
# An item catalog application with a user registration and authentication
# system, complete with full CRUD operations.

from flask import Flask, render_template, abort

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

# Close the session after each request
@app.teardown_appcontext
def shutdown_session(exception=None):
    session.close()

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

@app.route('/catalog/<category>')
def show_category(category):
    # Convert the supplied category to lowercase
    category = category.lower()

    # Get the categories from the database
    categories = session.query(Category).all()

    # See if there's a matching category name. If so, we'll get its id and
    # break from the loop below.
    category_id = None
    for i in categories:
        if category == i.name.lower():
            category_id = i.id
            break

    # If there's no match, send a 404 error code
    if category_id is None:
        abort(404)

    # Get the items with the matching category id
    items = session.query(Item).filter_by(cat_id=category_id).order_by(desc(Item.id)).all()

    # Truncate each item's description for its listing
    for item in items:
        if len(item.description) > 80:
            item.description = item.description[:80] + '...'
    return render_template('index.html', categories=categories, items=items)


# Run the server if the script is run directly from the Python interpreter
if __name__ == '__main__':
    app.secret_key = '9?\xf8\x9b\xa2\x11\xaas\xf1r\xf3bI\xd27{\xad\xdc[s\x17'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
