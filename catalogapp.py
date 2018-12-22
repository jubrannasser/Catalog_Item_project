#!/usr/bin/env python

from flask import Flask, render_template, request, flash,\
 redirect, url_for, jsonify, abort, session as session_login
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import User, Category, Item, Base
from werkzeug.utils import secure_filename
import os
import random
import string
from flask_httpauth import HTTPBasicAuth
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

# set upload folder and allowed extendions
UPLOAD_FOLDER = "static/img"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
auth = HTTPBasicAuth()

# configure upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# create and Bind the engine to access database
engine = create_engine('sqlite:///categitems.db?check_same_thread=false')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


# return True for allowed file extention
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# this code from udacity class room
def getUserId(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def createUser(data):
    user = User(email=data['email'], username=data['name'])
    session.add(user)
    session.commit()
    return user.id


# git user info from google acount and create user in db
def guser_info(access_token):
    url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    result = requests.get(url, params=params)
    data = result.json()

    # fill session_login
    session_login['username'] = data['name']
    session_login['email'] = data['email']
    user_id = getUserId(data['email'])
    if user_id is None:
        user_id = createUser(data)
    session_login['user_id'] = user_id
    flash(' welcom, %s' % session_login['username'])
    return 'ok'


# connect with google Oauth2
def gconnect(code):
    # Exchange authorization code for tokens
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        flash('Failed to get token.')
        return 'error'

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        flash(result.get('error'))
        return 'error'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        flash("Token's user ID doesn't match given user ID.")
        return 'error'

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        flash("Token's client ID does not match app's.")
        return 'error'

    # Verify user is not already connect
    stored_access_token = session_login.get('access_token')
    stored_gplus_id = session_login.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        flash('Current user is already connected.')
        return 'ok'

    # Store the access token in the session for later use.
    session_login['access_token'] = access_token
    session_login['gplus_id'] = gplus_id

    # get user info from google
    return guser_info(access_token)


# revoke token
def gdisconnect():
    access_token = session_login.get('access_token')
    if access_token is None:
        flash('Current user not connected.')
        return False
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        del session_login['access_token']
        del session_login['gplus_id']
        flash('Successfully disconnected.')
        return True
    else:
        flash('Failed to revoke token for given user.')
        return False
# End udacity class room code


# verify if user login
@auth.verify_password
def verify_password(username, password):
    if 'username' in session_login:
        return True


# log in page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        state = request.args.get('state_token')
        if state is None or state != session_login.get('state_token'):
            flash('Invalid state_token.')
            flash('Please Try agin')
            return "error"
        code = request.data
        return gconnect(code)

    # GET method response
    state_token = ''.join(random.choice(string.digits + string.ascii_uppercase)
                          for x in xrange(32))
    session_login['state_token'] = state_token
    print session_login['state_token']
    return render_template('login.html', state_token=state_token)


# log out  url delete session
@app.route('/logout')
def logout():
    result = gdisconnect()  # revoke token
    if result:
        username = session_login['username']
        del session_login['username']
        del session_login['user_id']
        del session_login['email']
        flash('good bye, %s' % username)
        return redirect(url_for('showCategories'))
    else:
        return redirect(url_for('showCategories'))


# show all categorys
@app.route('/')
@app.route('/catalog/')
def showCategories():
    items = session.query(Item).join(Item.category).\
        order_by(Item.id.desc()).limit(6)
    categories = session.query(Category).all()
    return render_template('home.html', categories=categories, items=items)


# list all items for a specific category
@app.route('/catalog/<string:category>/items/')
def showItems(category):
    category_id = request.args.get('category_id')
    categories = session.query(Category).all()
    items = session.query(Item).filter_by(category_id=category_id).all()
    return render_template('items.html', categories=categories,
                           items=items, categoryname=category)


# display item's information
@app.route('/catalog/<string:category>/<string:item>/info')
def itemInfo(category, item):
    item_id = request.args.get('item_id')
    item = session.query(Item).filter_by(id=item_id).one()
    if session_login.get('user_id') is not None and \
       session_login['user_id'] == item.user_id:
        return render_template('iteminfo_log.html', item=item)
    return render_template('iteminfo.html', item=item)


# edit item
@app.route('/catalog/<string:item>/edit/', methods=['POST', 'GET'])
@auth.login_required
def editItem(item):
    item_id = request.args.get('item_id')
    item = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        if session_login['user_id'] != item.user_id:
            abort(400)
        item.name = request.form.get('name')
        item.description = request.form.get('description')
        item.category_id = request.form.get('Category')
        session.add(item)
        session.commit()
        # upload img and adding to database
        if request.files.get('photo') is not None:
            file = request.files['photo']
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                extension = filename.rsplit('.', 1)[1].lower()
                filename = '%s.%s' % (item.id, extension)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                item.photo = filename
                session.add(item)
                session.commit()
        return redirect(url_for('showCategories'))
    categories = session.query(Category).all()
    return render_template('itemedit.html', categories=categories, item=item)


# add new item
@app.route('/catalog/item/add/', methods=['POST', 'GET'])
@auth.login_required
def addItem():
    categories = session.query(Category).all()
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        category_id = request.form.get('Category')
        item = Item(name=name, description=description,
                    category_id=category_id, user_id=session_login['user_id'])
        session.add(item)
        session.commit()
        # upload img
        if request.files.get('photo') is not None:
            file = request.files['photo']
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                extension = filename.rsplit('.', 1)[1].lower()
                filename = '%s.%s' % (item.id, extension)  # rename file
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                item.photo = filename  # add filename to database
                session.add(item)
                session.commit()
        return redirect(url_for('showCategories'))
    return render_template('itemadd.html', categories=categories)


# delete item
@app.route('/catalog/<string:item>/delete/', methods=['POST', 'GET'])
@auth.login_required
def deleteItem(item):
    item_id = request.args.get('item_id')
    item = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        if session_login['user_id'] != item.user_id:
            abort(400)
        session.delete(item)
        session.commit()
        return redirect(url_for('showCategories'))
    return render_template('itemdelete.html', item=item)


# json endpoint
@app.route('/catalog.json')
def catalogJson():
    categories = session.query(Category).all()
    return jsonify(Category=[c.serialize for c in categories])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
