#!/usr/bin/env python3
#
# An item catalog application with a user registration and authentication
# system, complete with full CRUD operations.

from flask import Flask

from sqlalchemy import create_engine
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
    items = session.query(Item).all()
    output = ''
    for i in items:
        output += '<p><strong>Name:</strong> {}'.format(i.name)
        output += '<br><strong>Category:</strong> {}'.format(i.category.name)
        output += '<br><strong>Added by:</strong> {}'.format(i.user.name)
        output += '<br><strong>Description:</strong> {}'.format(i.description)
        output += '</p>'
    return output


# Run the server if the script is run directly from the Python interpreter
if __name__ == '__main__':
    app.secret_key = '9?\xf8\x9b\xa2\x11\xaas\xf1r\xf3bI\xd27{\xad\xdc[s\x17'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
