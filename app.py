#!/usr/bin/env python3
#
# An item catalog application with a user registration and authentication
# system, complete with full CRUD operations.

import random
import string
import json

from flask import Flask, render_template, abort, redirect, url_for, request
from flask import session as login_session, make_response, flash, jsonify
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from oauth2client import client
import httplib2
import requests

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

# API endpoint that returns JSONified catalog data
@app.route('/api/catalog')
def catalog_json():
    # Get the categories
    categories = session.query(Category).all()

    # Get the items
    items = session.query(Item).all()

    # Return the JSONified data
    return jsonify(categories=[category.serialize(items) for category in categories])

# API endpoint that returns JSONified category data (if the category exists)
@app.route('/api/catalog/<category_arg>')
def category_json(category_arg):
    # Try getting the category
    category = session.query(Category).filter(Category.name.ilike(category_arg)).first()

    # If the category doesn't exist, send a 404 error code
    if category is None:
        abort(404)

    # Get the items
    items = session.query(Item).all()

    # Return the JSONified data
    return jsonify(category=category.serialize(items))

# API endpoint that returns JSONified item data (if the item exists under the
# supplied category).
@app.route('/api/catalog/<category_arg>/<item_arg>')
def item_json(category_arg, item_arg):
    # Try getting the item
    item = session.query(Item).filter(Category.name.ilike(category_arg), Item.name.ilike(item_arg)).first()

    # If the item doesn't exist (at least under the supplied category), send a
    # 404 error code.
    if item is None:
        abort(404)

    # Return the JSONified data
    return jsonify(item=item.serialize())

# Create an anti-forgery state token and show the login page
@app.route('/login')
def show_login():
    # If the user is already logged in, redirect them to the home page
    if login_session.get('username') is not None:
        flash('You are already logged in!')
        return redirect(url_for('index'))

    # Get the categories
    categories = session.query(Category).all()

    # Create a state token using random letters and numbers
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
            for x in range(32))

    # Store the state token in the login_session object
    login_session['state'] = state
    return render_template('login.html', categories=categories, state=state)

# Log in using Google Sign-In
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Make sure the X-Requested-With header was included in the request
    if not request.headers.get('X-Requested-With'):
        print('Missing header')
        response = make_response(json.dumps('Missing header'), 403)
        response.headers['Content-Type'] = 'application/json'
        return response

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

    # Try verifying that the access token is valid
    try:
        access_token = credentials.access_token
        url = ('https://www.googleapis.com/oauth2/v3/tokeninfo?access_token={}'
              .format(access_token))
        h = httplib2.Http()

        # In order to use json.loads(), it was necessary to add the .decode()
        # method. The following Stack Overflow post was helpful in finding this
        # solution: https://stackoverflow.com/q/42683478
        result = json.loads(h.request(url, 'GET')[1].decode('utf-8'))

    # If there's a problem trying to verify the access token, send a response
    # with a 500 error code.
    except:
        print('Failed to verify access token')
        response = make_response(json.dumps('Failed to verify access token'), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

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
        flash('You are already logged in!')
        return response

    # Try getting user info from Google
    try:
        url = 'https://www.googleapis.com/oauth2/v3/userinfo'
        params = {'access_token': credentials.access_token, 'alt': 'json'}
        r = requests.get(url, params=params)
        user_data = r.json()

    # If there's a problem trying to get user info, send a response with a 500
    # error code.
    except:
        print('Failed to get user info')
        response = make_response(json.dumps('Failed to get user info'), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # If the request for user info is denied by Google, send a 500 error code
    if user_data.get('error_description')is not None:
        print(user_data.get('error_description'))
        response = make_response(json.dumps(user_data.get('error_description')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token and Google user ID
    login_session['access_token'] = credentials.access_token
    login_session['g_user_id'] = g_user_id

    # Store user info in the login_session object
    login_session['username'] = user_data['given_name']
    login_session['email'] = user_data['email']
    login_session['picture'] = user_data['picture']
    login_session['provider'] = 'google'

    # Check if the user is already in the database. If not, add them.
    user_id = get_user_id(login_session['email'])
    if not user_id:
        user_id = add_user(login_session)
    login_session['user_id'] = user_id

    # Prepare and send the login confirmation response
    print('Login successful')
    response = make_response(json.dumps('Login successful'), 200)
    response.headers['Content-Type'] = 'application/json'
    flash('Welcome, {}'.format(login_session['username']))
    return response

# Log in using Facebook Login
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    # Make sure the X-Requested-With header was included in the request
    if not request.headers.get('X-Requested-With'):
        print('Missing header')
        response = make_response(json.dumps('Missing header'), 403)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if there's a mismatch between the state token sent in the
    # request and the state token stored in the login_session object.
    if request.args.get('state') != login_session['state']:
        print('Invalid state token')
        response = make_response(json.dumps('Invalid state token'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Get the access token sent by the request
    access_token = request.data.decode('utf-8')

    # Try exchanging the access token for a long-lived server-side token
    try:
        # First locate the application client secret file
        CLIENT_SECRET_FILE = 'fb_client_secret.json'

        # Get the app ID and app secret from the client secret file
        APP_ID = json.loads(open(CLIENT_SECRET_FILE, 'r').read())['web']['app_id']
        APP_SECRET = json.loads(open(CLIENT_SECRET_FILE, 'r').read())['web']['app_secret']
        url = (
            'https://graph.facebook.com/oauth/access_token?grant_type='
            'fb_exchange_token&client_id={}&client_secret={}&'
            'fb_exchange_token={}'.format(APP_ID, APP_SECRET, access_token))
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1].decode('utf-8'))

    # If there's a problem obtaining the long-lived token, send a response
    # with a 401 error code.
    except:
        print('Failed to exchange access token for long-lived token.')
        response = make_response(json.dumps('Failed to exchange access token for long-lived token.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # If there was an error making the exchange, send a 500 error code
    if result.get('error')is not None:
        print(result['error'].get('message'))
        response = make_response(json.dumps(result['error'].get('message')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the long-lived token
    token = result.get('access_token')

    # Now check if the user is already logged in
    stored_access_token = login_session.get('access_token')
    if stored_access_token is not None:
        print('You are already logged in!')
        response = make_response(json.dumps('You are already logged in!'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash('You are already logged in!')
        return response

    # Try getting user info from Facebook
    try:
        url = 'https://graph.facebook.com/me'
        params = {'fields': 'id,first_name,email', 'access_token': token}
        r = requests.get(url, params=params)
        user_data = r.json()

    # If there's a problem trying to get user info, send a response with a 500
    # error code.
    except:
        print('Failed to get user info')
        response = make_response(json.dumps('Failed to get user info'), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # If the request for user info is denied by Facebook, send a 500 error code
    if user_data.get('error')is not None:
        print(user_data['error'].get('message'))
        response = make_response(json.dumps(user_data['error'].get('message')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Try getting the user's profile picture
    try:
        url = 'https://graph.facebook.com/me/picture'
        params = {'redirect': 'false', 'width': '200', 'height': '200','access_token': token}
        r = requests.get(url, params=params)
        picture_data = r.json()

    # If there's a problem trying to get the picture, send a response with a
    # 500 error code.
    except:
        print('Failed to get user picture')
        response = make_response(json.dumps('Failed to get user picture'), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # If the request for the picture is denied by Facebook, send a 500 error code
    if picture_data.get('error')is not None:
        print(picture_data['error'].get('message'))
        response = make_response(json.dumps(picture_data['error'].get('message')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store user info in the login_session object
    login_session['access_token'] = token
    login_session['fb_user_id'] = user_data['id']
    login_session['username'] = user_data['first_name']
    login_session['email'] = user_data['email']
    login_session['picture'] = picture_data['data']['url']
    login_session['provider'] = 'facebook'

    # Check if the user is already in the database. If not, add them.
    user_id = get_user_id(login_session['email'])
    if not user_id:
        user_id = add_user(login_session)
    login_session['user_id'] = user_id

    # Prepare and send the login confirmation response
    print('Login successful')
    response = make_response(json.dumps('Login successful'), 200)
    response.headers['Content-Type'] = 'application/json'
    flash('Welcome, {}'.format(login_session['username']))
    return response

# Log out. After clicking on a link (which is actually a button element) with
# the .logout-link class, the associated click handler will call the provider-
# specific logout function that sends an AJAX POST request to this route.
@app.route('/logout', methods=['POST'])
def logout():
    # Check to see if the user is actually logged in
    access_token = login_session.get('access_token')
    if access_token is None:
        flash_message = 'You were not logged in to begin with!'
        response = make_response(json.dumps('You were not logged in!'), 200)
    else:
        flash_message = 'You have successfully logged out'
        response = make_response(json.dumps('Logout successful'), 200)

    # Either way, clear the login_session
    login_session.clear()

    # Prepare and send the response
    response.headers['Content-Type'] = 'application/json'
    flash(flash_message)
    return response

# Show the delete account page (if the user is logged in)
@app.route('/delete-account')
def delete_account():
    # If the user is not logged in, redirect them to the login page
    if 'username' not in login_session:
        flash('Please login first')
        return redirect(url_for('show_login'))

    # Get the categories
    categories = session.query(Category).all()

    # Show the page
    return render_template('delete_account.html', categories=categories)

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

    # Create a string variable to store the page heading
    page_heading = 'Newest noodles'
    return render_template('listings.html', categories=categories, items=recent_items, page_heading=page_heading)

# Show the items that have been added by the user (if the user is logged in)
@app.route('/my-noodles')
def show_user_items():
    # If the user is not logged in, redirect them to the login page
    if 'username' not in login_session:
        flash('Please login first')
        return redirect(url_for('show_login'))

    # Get the categories
    categories = session.query(Category).all()

    # Get the items added by the user
    user_items = session.query(Item).filter_by(user_id=login_session['user_id']).order_by(desc(Item.id)).all()

    # Truncate each item's description for its listing
    for item in user_items:
        if len(item.description) > 80:
            item.description = item.description[:80] + '...'

    # Create a string variable to store the page heading
    page_heading = 'My noodles'
    return render_template('listings.html', categories=categories, items=user_items, page_heading=page_heading)

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

    # Create a string variable to store the page heading
    page_heading = '{} noodles'.format(category_arg.title())
    return render_template('listings.html', categories=categories, items=items, page_heading=page_heading)

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
    # If the user is not logged in, redirect them to the login page
    if 'username' not in login_session:
        flash('Please login first')
        return redirect(url_for('show_login'))

    # Get the categories
    categories = session.query(Category).all()

    # If a POST request is received, process the form data
    if request.method == 'POST':
        new_item = Item(
            user_id=login_session['user_id'],
            cat_id=request.form['category-id'],
            name=request.form['name'],
            description=request.form['description'],
            image_url=request.form['image-url'])
        session.add(new_item)
        session.commit()

        # Redirect to the home page (with a flash message)
        flash('New item added')
        return redirect(url_for('index'))

    # Otherwise show the new item page
    else:
        return render_template('new_item.html', categories=categories)

# Edit an item
@app.route('/catalog/<category_arg>/<item_arg>/edit', methods=['GET', 'POST'])
def edit_item(category_arg, item_arg):
    # If the user is not logged in, redirect them to the login page
    if 'username' not in login_session:
        flash('Please login first')
        return redirect(url_for('show_login'))

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

    # If the user did not add this item, redirect them to the item page
    if login_session['user_id'] != item.user_id:
        flash('Sorry, you cannot edit this item')
        return redirect(url_for('show_item', category_arg=category_arg, item_arg=item_arg))

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

        # Redirect to the item page (with a flash message)
        flash('Edit successful')
        return redirect(url_for('show_item', category_arg=item.category.name.lower(), item_arg=item.name.lower()))

    # Otherwise show the edit item page
    else:
        return render_template('edit_item.html', categories=categories, item=item)

# Delete an item
@app.route('/catalog/<category_arg>/<item_arg>/delete', methods=['GET', 'POST'])
def delete_item(category_arg, item_arg):
    # If the user is not logged in, redirect them to the login page
    if 'username' not in login_session:
        flash('Please login first')
        return redirect(url_for('show_login'))

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

    # If the user did not add this item, redirect them to the item page
    if login_session['user_id'] != item.user_id:
        flash('Sorry, you cannot delete this item')
        return redirect(url_for('show_item', category_arg=category_arg, item_arg=item_arg))

    # If a POST request is received, delete the item and commit the change
    if request.method == 'POST':
        session.delete(item)
        session.commit()

        # After deleting the item, redirect to the home page (with a flash message)
        flash('Item deleted')
        return redirect(url_for('index'))

    # Otherwise show the delete item page
    else:
        return render_template('delete_item.html', categories=categories, item=item)

def get_user_id(email):
    """Attempts to retrieve a user ID."""

    # Try getting the user with the matching email
    try:
        user = session.query(User).filter_by(email=email).one()

        # Return the user ID
        return user.id

    # Otherwise return None
    except:
        return None

def add_user(login_session):
    """Adds a new user to the database. The user's ID is then returned."""

    # Add the new user using the info stored in the login_session object
    new_user = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture'])
    session.add(new_user)
    session.commit()

    # Return the newly added user's ID
    return new_user.id

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
