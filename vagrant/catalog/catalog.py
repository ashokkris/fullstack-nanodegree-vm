import os
import random, string, re
import httplib2
import json
import requests
from datetime import datetime, timedelta
from oauth2client import client
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from werkzeug import secure_filename
from werkzeug.contrib.atom import AtomFeed
from urlparse import urljoin
from flask import Flask
from flask import session as login_session
from flask import render_template, request, redirect, jsonify, url_for
from flask import flash, make_response, send_from_directory
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, User, CategoryItem

app = Flask(__name__)
CLIENT_ID = \
    json.loads(open('client_secret.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Sports Catalog App"
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['png', 'gif', 'jpg', 'jpeg'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/login')
def showLogin():
    # Create a state token to prevent request forgery. Store it in the session 
    # for later validation
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) \
        for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

@app.route('/logout')
def logout():
    response = gdisconnect()
    if response.status_code == 200:
        flash("Successfully logged out")
    else:
        flash("Error encountered during log out")
    return redirect(url_for('showCatalog'))

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        respone.headers['Content-Type'] = 'application/json'
        return response
 
    # Obtain the authorization code sent by client
    code = request.data
    # Convert autorization code to credentials object using flow exchange api
    try:
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow .redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain the access token and verify that it is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' \
        % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # if there was an error in the access token info then, abort
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
 
    # Verify that the access token is used for the intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID does not match \
            the given user ID"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client does not match \
            app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check if user is already signed in to our app  
    stored_credentials = login_session.get('credentials')      
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already \
            connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use
    login_session['credentials'] = credentials.to_json()
    login_session['gplus_id'] = gplus_id

    # Get the user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # If user does not already exist in our database, add this user
    user_id = getUserId(login_session['email'])
    if not user_id:
        user_id = addUser()
    login_session['user_id'] = user_id

    output = ''
    output += '<h4>Hello ' + login_session['username'] + '!</h4>'
    output += '<img src="' + login_session['picture'] + '" '
    output += 'style = "width: 100px; height: 100px;border-radius: 50px;">'

    flash("Successfully logged in as %s" % login_session['username'])

    return output

# Disconnect to revoke the currently logged in user's access token
@app.route('/gdisconnect')
def gdisconnect():
    credentials  = None
    if login_session.get('credentials') is not None:
        credentials = client.OAuth2Credentials.from_json( \
            login_session['credentials'])
    if credentials is None or credentials.access_token_expired:
        response = make_response(json.dumps('User not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        # Clear credential info held in current flask session to force
        # fresh signin
        clearLoginSession()
        return response
    
    # Perform a Http GET request to revoke the currently held token
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
        % access_token
    h = httplib2.Http()
    result  = h.request(url, 'GET')[0]
    if result['status'] == '200':
        # Clear credential info held in current flask session & return success
        clearLoginSession()
        response = make_response(json.dumps('Successful revocation'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # Handle any unexpected failure response from Google
        response = make_response(json.dumps('Unsuccessful revocation'), 400)
        response.headers['Content-Type'] = 'application/json'
        # Clear credential info held in current flask session to force
        # fresh signin
        clearLoginSession()
        return response

# JSON endpoint to view catalog information
@app.route('/catalog.json')
def catalogJSON():
    listObj = []
    categories = session.query(Category).all()
    for c in categories:
        items = session.query(CategoryItem).filter( \
            CategoryItem.category_id == c.id).all()
        listObj.append(c.asDict(items))
    return jsonify(Category = listObj)

# Atom Feed for latest catalog items
@app.route('/recent.atom')
def recent_feed():
    feed = AtomFeed('Latest Items from Sports Catalog App',
                    feed_url=request.url, url=request.url_root)
    newItems = session.query(CategoryItem).order_by \
        (desc(CategoryItem.date_created)).limit(12).all()
    for item in newItems:
        feed.add(item.title, unicode(item.description),
            content_type='html',
            author=item.user.name,
            url=make_external(url_for('showItemDetails', 
                category_title = item.category.title,
                item_title = item.title)),
            updated=item.date_created)

    return feed.get_response()

# Show catalog categories along with upto twelve recently added items 
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    categories = session.query(Category).all()
    newItems = session.query(CategoryItem).order_by \
        (desc(CategoryItem.date_created)).limit(12).all()

    # If user is logged in, then let the template know so as to allow
    # user to add new items to catalog
    if 'email' in login_session:
        return render_template('catalog.html', categories = categories, \
            items = newItems, canEdit = "True")
    else:
        return render_template('catalog.html', categories = categories, \
            items = newItems)

# Show items in a specific category
@app.route('/catalog/<string:category_title>/')
@app.route('/catalog/<string:category_title>/items/')
def showCategoryItems(category_title):
    sportsCategory = session.query(Category).filter(Category.title == \
        category_title).first()
    if sportsCategory == None:
        response = make_response(json.dumps("Not Found"), 404)
        response.headers['Content-Type'] = 'application/json'
        return response
    categoryItems = session.query(CategoryItem).filter( \
        CategoryItem.category_id == sportsCategory.id).order_by( \
        asc(CategoryItem.date_created)).all()

    categories = session.query(Category).all()
    return render_template('catalog.html', categories = categories, \
        categoryTitle = category_title, items = categoryItems)

# Show details of a specific item in a category
@app.route('/catalog/<string:category_title>/<string:item_title>/')
def showItemDetails(category_title, item_title):
    sportsCategory = session.query(Category).filter(Category.title == \
        category_title).first()
    if sportsCategory == None:
        response = make_response(json.dumps("Category not Found"), 404)
        response.headers['Content-Type'] = 'application/json'
        return response
    item = session.query(CategoryItem).filter(CategoryItem.category_id == \
        sportsCategory.id).filter(CategoryItem.title == item_title).first()
    if item == None:
        response = make_response(json.dumps("Item not Found"), 404)
        response.headers['Content-Type'] = 'application/json'
        return response
    # If user is logged in and is the same user that originally created the
    # item, then let the template know so as to allow edit and delete
    if 'email' in login_session and item.user_id == login_session['user_id']:
        return render_template('itemDetails.html', category = sportsCategory, \
        item = item, canEdit = "True")
    else:
        return render_template('itemDetails.html', category = sportsCategory, \
        item = item)

# Add a new item to catalog
@app.route('/catalog/add/', methods = ['GET', 'POST'])
def addItem():
    if 'email' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        itemTitle = request.form['title']
        itemDesc = request.form['description']
        # Strip any tab, newline characters from description before update
        if itemDesc:
            itemDesc = re.sub(r'\s*[\n\t\r]\s*', ' ', itemDesc)
        if itemTitle == None or itemDesc == None:
            response = make_response(json.dumps("Insufficent  input"), 404)
            response.headers['Content-Type'] = 'application/json'
            return response
        category = session.query(Category).filter(Category.title == \
                request.form['category']).first()

        imageFile = None
        file = request.files['file']
        if file and isValidImageFile(file.filename):
            imageFile = secure_filename(file.filename)

        newItem = CategoryItem(title = itemTitle, description = itemDesc, \
            category = category, image = imageFile, \
            user_id = login_session['user_id'])
            
        session.add(newItem)
        try:
            session.commit()
            # Now that the item was successfully committed to database, we
            # can now safely save the image, if any, to server's file system
            if file and imageFile:
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], imageFile))
        except:
            session.rollback()
            return ("<script>function myAlert() {alert('Operation Failed! "
                    "Check if you were attempting to add an item with a name "
                    "that already exists for this category.');}</script> "
                    "<body onload='myAlert()' >")

        flash('%s successfully added' % newItem.title)
        return redirect(url_for('showCategoryItems', category_title = \
            category.title))
    else:
        categories = session.query(Category).order_by(asc(Category.title)) \
            .all()
        return render_template('addItem.html', categories = categories)

# Edit an item
@app.route('/catalog/<string:category_title>/<string:item_title>/edit/', \
    methods = ['GET', 'POST'])
def editItem(category_title, item_title):
    if 'email' not in login_session:
        return redirect('/login')
    sportsCategory = session.query(Category).filter(Category.title == \
        category_title).first()
    if sportsCategory == None:
        response = make_response(json.dumps("Category not Found"), 404)
        response.headers['Content-Type'] = 'application/json'
        return response
    item = session.query(CategoryItem).filter(CategoryItem.category_id == \
        sportsCategory.id).filter(CategoryItem.title == item_title).first()
    if item == None:
        response = make_response(json.dumps("Item not Found"), 404)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Prevent item from being updated by user who is not the item's creator
    if item.user_id != login_session['user_id']:
        return ("<script>function myAlert() {alert('You are not authorized to "
                "edit this item. You are allowed to only edit items that you "
                "created.');}</script><body onload='myAlert()' >")

    if request.method == 'POST':
        category = session.query(Category).filter(Category.title == \
            request.form['category']).first()
        item.category = category
        if request.form['title']:
            item.title = request.form['title']
        if request.form['description']:
            # Strip tab, newline characters from description before update
            desc = request.form['description']
            item.description = re.sub(r'\s*[\n\t\r]\s*', ' ', desc)
 
        imageFile = None
        file = request.files['file']
        if file and isValidImageFile(file.filename):
            imageFile = secure_filename(file.filename)
            item.image = imageFile

        # Commit to database
        try:
            session.commit()
            # Now that the item was successfully saved to the database,
            # we can now safely save the image, if any, to server's file system
            if file and imageFile:
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], imageFile))
        except:
            session.rollback()
            return ("<script>function myAlert() {alert('Operation Failed! "
                    "Check if you were attempting to rename an item with a "
                    "name that already exists for this category.');}</script> "
                    "<body onload='myAlert()' >")

        flash('%s successfully updated' % item.title)
        return redirect(url_for('showItemDetails', category_title = \
            category.title, item_title = item.title))
    else:
        categories = session.query(Category).order_by(asc(Category.title)) \
            .all()
        return render_template('editItem.html', item = item, \
            category = sportsCategory, categories = categories)

# Delete an item
@app.route('/catalog/<string:category_title>/<string:item_title>/delete/', \
    methods = ['GET','POST'])
def deleteItem(category_title,item_title):
    if 'email' not in login_session:
        return redirect('/login')

    sportsCategory = session.query(Category).filter(Category.title == \
        category_title).first()
    if sportsCategory == None:
        response = make_response(json.dumps("Category not Found"), 404)
        response.headers['Content-Type'] = 'application/json'
        return response
    item = session.query(CategoryItem).filter(CategoryItem.category_id == \
        sportsCategory.id).filter(CategoryItem.title == item_title).first()
    if item == None:
        response = make_response(json.dumps("Item not Found"), 404)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Prevent item from being deleted by user who is not the item's creator
    if item.user_id != login_session['user_id']:
        return ("<script>function myAlert() {alert('You are not authorized to "
                "delete this item. You are allowed to only delete items that "
                "you created.');}</script><body onload='myAlert()' >")

    if request.method == 'POST':
        # Abort request if its CSRF token is invalid
        token = login_session.pop('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            abort(403)

        # Ready to delete the item from database and its associated image
        # file, if present, from the server
        imageFile = item.image
        session.delete(item)
        # Commit change to database
        try:
            session.commit()
        except:
            session.rollback()
            return ("<script>function myAlert() "
                    "{alert('Database Operation Failed! ');}</script> "
                    "<body onload='myAlert()' >")
        if imageFile:
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], imageFile))
            except OSError:
                pass
                
        flash('%s successfully deleted' % item.title)
        return redirect(url_for('showCategoryItems', category_title = \
            sportsCategory.title))
    else:
        return render_template('deleteItem.html', category = sportsCategory, \
            item = item)

# Download a file from 'uploads' folder on server
@app.route('/uploads/<path:filename>')
def downloadFile(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)


# Helper functions

# Validate the image filename before uploading to the server
def isValidImageFile(name):
    return '.' in name and name.lower().rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# Add new user to database
def addUser():
    newUser = User(name=login_session['username'],
        email=login_session['email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

 # Return a user object associated with a user id
def getUserFromId(user_id):
    try:
        return session.query(User).filter_by(id=user_id).one()
    except:
        return None

# Return user id associated with an email address
def getUserId(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# Clear credential and user informtion in flask's session
def clearLoginSession():
    if login_session.get('credentials') is not None:
        del login_session['credentials']
    if login_session.get('gplus_id') is not None:
        del login_session['gplus_id']
    if login_session.get('username') is not None:
        del login_session['username']
    if login_session.get('picture') is not None:
        del login_session['picture']
    if login_session.get('email') is not None:
        del login_session['email']
    if login_session['user_id'] is not None:
        del login_session['user_id']

#  Join the current request's root URL with the one to externalize
def make_external(url):
    return urljoin(request.url_root, url)

# Generate the token used for cross-site-request-forgery prevention.
# This function is made available to a html template to call via 
# jinja_env.globals. See 'deleteItem' HTML template to see how this function 
# is called to generate the token that is transmitted to the client as a hidden
# field in the POST
def generate_csrf_token():
    login_session['_csrf_token'] = ''.join(random.choice( \
        string.ascii_uppercase + string.digits) for x in xrange(32))
    return login_session['_csrf_token']


if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.jinja_env.globals['csrf_token'] = generate_csrf_token
  app.debug = True
  app.run(host = '0.0.0.0', port = 8000)
