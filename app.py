#!/usr/bin/env python3
#
# An item catalog application with a user registration and authentication
# system, complete with full CRUD operations.

import random
import string
from oauth2client import client
import httplib2
import json

from flask import Flask, render_template, abort, redirect, url_for, request
from flask import session as login_session, make_response
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

# Create an anti-forgery state token and show the login page
@app.route('/login')
def show_login():
    # Get the categories
    categories = session.query(Category).all()

    # Create a state token using random letters and numbers
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
            for x in range(32))

    # Store the state token in the login_session object
    login_session['state'] = state
    return render_template('login.html', categories=categories, state=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Make sure the X-Requested-With header was included in the request
    if not request.headers.get('X-Requested-With'):
        abort(403)

    # Check to see if there's a mismatch between the state token sent in the
    # request and the state token stored in the login_session object.
    if request.args.get('state') != login_session['state']:
        print('Invalid state token')
        response = make_response(json.dumps('Invalid state token'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Get the authorization code sent by the request
    auth_code = request.data

    # Try exchanging the authorization code for an access token, refresh
    # token, and ID token (all contained in a credentials object).
    try:
        # First locate the application client secret file
        CLIENT_SECRET_FILE = 'client_secret.json'

        # Now make the exchange to get the credentials object
        credentials = client.credentials_from_clientsecrets_and_code(
            CLIENT_SECRET_FILE,
            ['profile', 'email'],
            auth_code)

    # If there's a problem obtaining the credentials, send a response with a
    # 401 error code.
    except:
        print('Failed to exchange authorization code for credentials.')
        response = make_response(json.dumps('Failed to exchange authorization code for credentials.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v3/tokeninfo?access_token={}'
          .format(access_token))
    h = httplib2.Http()

    # In order to use json.loads(), it was necessary to add the .decode()
    # method. The following Stack Overflow post was helpful in finding this
    # solution: https://stackoverflow.com/q/42683478
    result = json.loads(h.request(url, 'GET')[1].decode('utf-8'))

    # If there was an error validating the access token, send a 500 error code
    if result.get('error_description')is not None:
        print(result.get('error_description'))
        response = make_response(json.dumps(result.get('error_description')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Make sure the access token is for the intended user
    g_user_id = credentials.id_token['sub']
    if result.get('sub') != g_user_id:
        print('User ID mismatch')
        response = make_response(json.dumps('User ID mismatch'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Get the client ID from the application client secret file
    CLIENT_ID = json.loads(open(CLIENT_SECRET_FILE, 'r').read())['web']['client_id']

    # We'll use the client ID to make sure the access token is valid for this
    # application.
    if result.get('azp') != CLIENT_ID:
        print('Client ID mismatch')
        response = make_response(json.dumps('Client ID mismatch'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Now check if the user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_g_user_id = login_session.get('g_user_id')
    if stored_access_token is not None and g_user_id == stored_g_user_id:
        print('You are already logged in!')
        response = make_response(json.dumps('You are already logged in!'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token and Google user ID
    login_session['access_token'] = credentials.access_token
    login_session['g_user_id'] = g_user_id

    return '<h1>Success!</h1>'

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

    # Try getting the category ID and categories
    category_id, categories = get_category_id(category_arg)

    # Get the items with the matching category ID
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

    # Try getting the requested item (along with the categories)
    item, categories = get_item(category_arg, item_arg)
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

    # Try getting the requested item (along with the categories)
    item, categories = get_item(category_arg, item_arg)

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
        return redirect(url_for('show_item', category_arg=item.category.name.lower(), item_arg=item.name.lower()))

    # Otherwise show the edit item page
    else:
        return render_template('edit_item.html', categories=categories, item=item)

# Delete an item
@app.route('/catalog/<category_arg>/<item_arg>/delete', methods=['GET', 'POST'])
def delete_item(category_arg, item_arg):
    # Check if all characters in the supplied arguments are lowercase. Python
    # docs and the following Stack Overflow post were used as references:
    # https://stackoverflow.com/a/33883584
    if category_arg.islower() and item_arg.islower():
        pass
    else:
        # Convert the supplied arguments to lowercase
        category_arg = category_arg.lower()
        item_arg = item_arg.lower()

        # Redirect back to the delete item page with the lowercased arguments
        return redirect(url_for('delete_item', category_arg=category_arg, item_arg=item_arg))

    # Try getting the requested item (along with the categories)
    item, categories = get_item(category_arg, item_arg)

    # If a POST request is received, delete the item and commit the change
    if request.method == 'POST':
        session.delete(item)
        session.commit()

        # After deleting the item, redirect to the home page
        return redirect(url_for('index'))

    # Otherwise show the delete item page
    else:
        return render_template('delete_item.html', categories=categories, item=item)

def get_category_id(category_arg):
    """Attempts to retrieve a category ID along with all categories."""

    # Get the categories from the database
    categories = session.query(Category).all()

    # See if there's a matching category name. If so, we'll get its ID and
    # break from the loop below.
    category_id = None
    for category in categories:
        if category_arg == category.name.lower():
            category_id = category.id
            break

    # If there's no match, send a 404 error code
    if category_id is None:
        abort(404)

    # Otherwise return the category ID and categories
    else:
        return category_id, categories

def get_item(category_arg, item_arg):
    """Attempts to retrieve an item along with all categories."""

    # Try getting the category ID and categories
    category_id, categories = get_category_id(category_arg)

    # Try getting the item with the matching category ID and name
    try:
        # Case insensitive query made possible with .filter() method.
        # Developed with help from the following Stack Overflow post:
        # https://stackoverflow.com/a/2128558
        item = session.query(Item).filter(Item.cat_id==category_id, Item.name.ilike(item_arg)).one()
        return item, categories

    # If there's no matching item, send a 404 error code
    except:
        abort(404)


# Run the server if the script is run directly from the Python interpreter
if __name__ == '__main__':
    app.secret_key = '9?\xf8\x9b\xa2\x11\xaas\xf1r\xf3bI\xd27{\xad\xdc[s\x17'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
