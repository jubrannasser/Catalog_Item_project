#!/usr/bin/env python

from flask import Flask, render_template, request,\
 redirect, url_for, jsonify, abort, session as session_login
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import User, Category, Item, Base
from werkzeug.utils import secure_filename
import os
from flask_httpauth import HTTPBasicAuth

# set upload folder and allowed extendions
UPLOAD_FOLDER = "static/img"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
auth = HTTPBasicAuth()

# configure upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# create and Bind the engine to access database
engine = create_engine('sqlite:///categitems.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# return True for allowed file extention
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# verify if user login
@auth.verify_password
def verify_password(username,password):
    if 'username' in session_login:
        return True


# log in page
@app.route('/login')
def login():
    user = session.query(User).filter_by(id=1).one()
    session_login['username'] = user.username
    session_login['id'] = user.id
    session_login['email'] = user.email
    return redirect(url_for('showCategories'))


# log out  url delete session
@app.route('/logout')
def logout():
    del session_login['username']
    del session_login['id']
    del session_login['email']
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
    if session_login.get('id') is not None and \
       session_login['id'] == item.user_id:
        return render_template('iteminfo_log.html', item=item)
    return render_template('iteminfo.html', item=item)


# edit item
@app.route('/catalog/<string:item>/edit/', methods=['POST', 'GET'])
@auth.login_required
def editItem(item):
    item_id = request.args.get('item_id')
    item = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        if session_login['id'] != item.user_id:
            abort(400)
        item.name = request.form.get('name')
        item.description = request.form.get('description')
        item.category_id = request.form.get('Category')
        session.add(item)
        session.commit()
        # upload img and add to database
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
                    category_id=category_id, user_id=session_login['id'])
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
        if session_login['id'] != item.user_id:
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
