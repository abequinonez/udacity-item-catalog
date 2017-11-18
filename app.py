#!/usr/bin/env python3
#
# An item catalog application with a user registration and authentication
# system, complete with full CRUD operations.

from flask import Flask, render_template, abort, redirect, url_for, request

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

# Show the home page (displays most recently added item listings)
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
    return render_template('listings.html', categories=categories, items=recent_items)

# Show the desired category (if it exists)
@app.route('/catalog/<category_arg>')
def show_category(category_arg):
    # Check if all characters in the supplied argument are lowercase. Python
    # docs and the following Stack Overflow post were used as references:
    # https://stackoverflow.com/a/33883584
    if category_arg.islower():
        pass
    else:
        # Convert the supplied argument to lowercase
        category_arg = category_arg.lower()

        # Redirect back to the category page with the lowercased argument
        return redirect(url_for('show_category', category_arg=category_arg))

    # Get the categories from the database
    categories = session.query(Category).all()

    # See if there's a matching category name. If so, we'll get its id and
    # break from the loop below.
    category_id = None
    for category in categories:
        if category_arg == category.name.lower():
            category_id = category.id
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
    return render_template('listings.html', categories=categories, items=items)

# Show the desired item (if it exists under the supplied category)
@app.route('/catalog/<category_arg>/<item_arg>')
def show_item(category_arg, item_arg):
    # Check if all characters in the supplied arguments are lowercase. Python
    # docs and the following Stack Overflow post were used as references:
    # https://stackoverflow.com/a/33883584
    if category_arg.islower() and item_arg.islower():
        pass
    else:
        # Convert the supplied arguments to lowercase
        category_arg = category_arg.lower()
        item_arg = item_arg.lower()

        # Redirect back to the item page with the lowercased arguments
        return redirect(url_for('show_item', category_arg=category_arg, item_arg=item_arg))

    # Get the categories from the database
    categories = session.query(Category).all()

    # See if there's a matching category name. If so, we'll get its id and
    # break from the loop below.
    category_id = None
    for category in categories:
        if category_arg == category.name.lower():
            category_id = category.id
            break

    # If there's no match, send a 404 error code
    if category_id is None:
        abort(404)

    # Try getting the item with the matching category id and name
    try:
        # Case insensitive query made possible with .filter() method.
        # Developed with help from the following Stack Overflow post:
        # https://stackoverflow.com/a/2128558
        item = session.query(Item).filter(Item.cat_id==category_id, Item.name.ilike(item_arg)).one()

    # If there's no matching item, send a 404 error code
    except:
        abort(404)
    return render_template('item.html', categories=categories, item=item)

# Add a new item
@app.route('/catalog/new', methods=['GET', 'POST'])
def new_item():
    # Get the categories
    categories = session.query(Category).all()

    # If a POST request is received, process the form data
    if request.method == 'POST':
        user = session.query(User).filter_by(name='Robo Admin').one()
        new_item = Item(
            user=user,
            cat_id=request.form['category-id'],
            name=request.form['name'],
            description=request.form['description'],
            image_url=request.form['image-url'])
        session.add(new_item)
        session.commit()
        return redirect(url_for('index'))

    # Otherwise show the new item page
    else:
        return render_template('new_item.html', categories=categories)

# Edit an item
@app.route('/catalog/<category_arg>/<item_arg>/edit', methods=['GET', 'POST'])
def edit_item(category_arg, item_arg):
    # Check if all characters in the supplied arguments are lowercase. Python
    # docs and the following Stack Overflow post were used as references:
    # https://stackoverflow.com/a/33883584
    if category_arg.islower() and item_arg.islower():
        pass
    else:
        # Convert the supplied arguments to lowercase
        category_arg = category_arg.lower()
        item_arg = item_arg.lower()

        # Redirect back to the edit item page with the lowercased arguments
        return redirect(url_for('edit_item', category_arg=category_arg, item_arg=item_arg))

    # Get the categories from the database
    categories = session.query(Category).all()

    # See if there's a matching category name. If so, we'll get its id and
    # break from the loop below.
    category_id = None
    for category in categories:
        if category_arg == category.name.lower():
            category_id = category.id
            break

    # If there's no match, send a 404 error code
    if category_id is None:
        abort(404)

    # Try getting the item with the matching category id and name
    try:
        # Case insensitive query made possible with .filter() method.
        # Developed with help from the following Stack Overflow post:
        # https://stackoverflow.com/a/2128558
        item = session.query(Item).filter(Item.cat_id==category_id, Item.name.ilike(item_arg)).one()

    # If there's no matching item, send a 404 error code
    except:
        abort(404)

    # If a POST request is received, process the form data
    if request.method == 'POST':
        # Compare each of the properties below with the form data received. If
        # there is a difference, assign the new value. Finally, commit the
        # changes to the database.
        if request.form['category-id'] != str(item.cat_id):
            item.cat_id = request.form['category-id']
        if request.form['name'] != item.name:
            item.name = request.form['name']
        if request.form['description'] != item.description:
            item.description = request.form['description']
        if request.form['image-url'] != item.image_url:
            item.image_url = request.form['image-url']
        session.add(item)
        session.commit()

        # Redirect to the item page
        return redirect(url_for('show_item', category_arg=item.category.name, item_arg=item.name))

    # Otherwise show the edit item page
    else:
        return render_template('edit_item.html', categories=categories, item=item)


# Run the server if the script is run directly from the Python interpreter
if __name__ == '__main__':
    app.secret_key = '9?\xf8\x9b\xa2\x11\xaas\xf1r\xf3bI\xd27{\xad\xdc[s\x17'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
