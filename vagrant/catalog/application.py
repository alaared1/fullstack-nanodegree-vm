#!/usr/bin/env python3

from database import Base, Category, Item, User
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, asc, desc
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, make_response, session as login_session
import datetime, requests, random, string, json, httplib2
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"

# Connect to Database and create database session
engine = create_engine('sqlite:///catalogapp.db', connect_args={'check_same_thread': False})
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create anti-forgery state token
@app.route('/login')
def show_login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}'.format(access_token))
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1].decode('utf-8'))
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = 'Welcome, {}!'.format(login_session['username'])
    flash("you are now logged in as {}".format(login_session['username']))
    return output


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        flash("You were not logged in")
        return redirect(url_for('show_catalog'))
    url = 'https://accounts.google.com/o/oauth2/revoke?token={}'.format(access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        del login_session['gplus_id']
        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        flash("You have successfully been logged out.")
        return redirect(url_for('show_catalog'))
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON API to view Catalog Information   
@app.route('/catalog.json')
def categories_json():
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])

 
# Show all categories
@app.route('/')
@app.route('/catalog/')
def show_catalog():
    categories = session.query(Category).order_by(asc(Category.name))
    # 10 latest items ordered by modified date
    items = session.query(Item).order_by(desc(Item.modified_date)).limit(10).all()
    if 'username' not in login_session:
        # can_edit is a flag that determines if the user is logged to make edit buttons visible in the template
        return render_template('catalog.html', categories=categories, items=items, 
            latest=True, can_edit=False)
    else:
        return render_template('catalog.html', categories=categories, items=items, 
            latest=True, can_edit=True)


# Show items of a category
@app.route('/catalog/<string:category_name>/')
@app.route('/catalog/<string:category_name>/items/')
def show_items(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category_id=category.id).all()
    # Number of items in this category
    num_items = session.query(Item).filter_by(category_id=category.id).count()
    if 'username' not in login_session:
        return render_template('catalog.html', category=category, categories=get_all_categories(),
                           items=items, latest=False, can_edit=False, num_items=num_items)
    else:
        return render_template('catalog.html', category=category, categories=get_all_categories(),
                           items=items, latest=False, can_edit=True, num_items=num_items)


# Show informations of a single item
@app.route('/catalog/<string:category_name>/<string:item_name>/')
def show_item(category_name, item_name):
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Item).filter_by(name=item_name).one()
    creator = getUserInfo(item.user_id)
    if 'user_id' in login_session and creator:
        # This check determines if the user is the creator of the item or not
        if creator.id == login_session['user_id']:
            return render_template('item.html', item=item, can_edit=True)
        else:
            return render_template('item.html', item=item, can_edit=False)
    else:
        return render_template('item.html', item=item, can_edit=False)
        
# Create a new item
@app.route('/catalog/items/new/', methods=['GET', 'POST'])
@app.route('/catalog/<string:category_name>/items/new/', methods=['GET', 'POST'])
def new_item(category_name=None):
    # the optional parameter category_name is used when we access new item page from a specifed category page
    # so it can help us put that category name as a default value in the category dropdown
    categories = session.query(Category).all()
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        new_item = Item(name=request.form['name'], description=request.form['description'], color=request.form['color'], 
            price=request.form['price'], category_id=request.form['category'], user_id=login_session['user_id'])
        session.add(new_item)
        session.commit()
        flash('New "{}" Item Successfully Created'.format(new_item.name))
        return redirect(url_for('show_catalog'), )
    else:
        return render_template('new-item.html', categories=categories, category_name=category_name)

# Edit an item
@app.route('/catalog/<string:item_name>/edit', methods=['GET', 'POST'])
def edit_item(item_name):
    if 'username' not in login_session:
        return redirect('/login')
    item_to_edit = session.query(Item).filter_by(name=item_name).one()
    category = session.query(Category).filter_by(id=item_to_edit.category_id).one()
    # prevent data modification by access through the url if the user is not the creator of the item
    if login_session['user_id'] != item_to_edit.user_id:
        flash('Error: You are not authorized to edit this item. Please create your own items in order to edit')
        return redirect(url_for('show_catalog'))
    if request.method == 'POST':
        if request.form['name']:
            item_to_edit.name = request.form['name']
        if request.form['description']:
            item_to_edit.description = request.form['description']
        if request.form['color']:
            item_to_edit.description = request.form['description']
        if request.form['price']:
            item_to_edit.description = request.form['price']
        if request.form['category']:
            item_to_edit.description = request.form['category']
        item_to_edit.modified_date = datetime.datetime.utcnow()
        session.add(item_to_edit)
        session.commit()
        flash('Item has been successfully edited!')
        return redirect(url_for('show_items', category_name=category.name))
    else:
        return render_template('edit-item.html', item=item_to_edit, categories=get_all_categories())


# Delete an item
@app.route('/catalog/<string:item_name>/delete', methods=['GET', 'POST'])
def delete_item(item_name):
    if 'username' not in login_session:
        return redirect('/login')
    item_to_delete = session.query(Item).filter_by(name=item_name).one()
    category = session.query(Category).filter_by(id=item_to_delete.category_id).one()
    # prevent data modification by access through the url if the user is not the creator of the item
    if login_session['user_id'] != item_to_delete.user_id:
        flash('Error: You are not authorized to delete this item. Please create your own items in order to delete')
        return redirect(url_for('show_catalog'))
    if request.method == 'POST':
        session.delete(item_to_delete)
        session.commit()
        flash('Item has been successfully deleted!')
        num_items = session.query(Item).filter_by(category_id=category.id).count()
        return redirect(url_for('show_items', category_name=get_category_name(category.id), num_items=num_items))
    else:
        return render_template('delete-item.html', item=item_to_delete)

# Create User
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session['email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# Get User informations
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one_or_none()
    return user


# Get User Id
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Get a name of a cartegory using the category ID
def get_category_name(category_id):
    category = session.query(Category).filter_by(id=category_id).one_or_none()
    if category:
        return category.name
    else:
        return ''

# Get all categories
def get_all_categories():
    categories = session.query(Category).order_by(asc(Category.name)).all()
    if categories:
        return categories
    else:
        return ''

# custom context processor that permits to retrieve values directly into the templates
@app.context_processor
def utility_processor():
    return dict(get_category_name=get_category_name, get_all_categories=get_all_categories)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
