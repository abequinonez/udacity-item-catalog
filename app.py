#!/usr/bin/env python3
#
# An item catalog application with a user registration and authentication
# system, complete with full CRUD operations.

from flask import Flask

from database_setup import *

app = Flask(__name__)



if __name__ == '__main__':
    app.secret_key = '9?\xf8\x9b\xa2\x11\xaas\xf1r\xf3bI\xd27{\xad\xdc[s\x17'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
