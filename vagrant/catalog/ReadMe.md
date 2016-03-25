# Fullstack Nanodegree P3 - Item Catalog
```
catalog/    
|---- database_setup.py    
|---- database_populate.py    
|---- catalog.py
|---- client_secret.json
|---- readme.md
|---- static/
      |---- catalog.css
      |---- body.png
      |---- top.png
      |---- content_1.png
      |---- content_2.png
|---- templates/
      |---- base.html
      |---- header.html
      |---- login.html
      |---- catalog.html
      |---- itemDetails.html
      |---- addItem.html
      |---- editItem.html
      |---- deleteItem.html
|---- uploads/
      <this folder contains item image files>
```
### Dependencies  
1. SQLite 3.x database  
2. SQLAlchemy 0.8.4 or later  
3. Flask version 0.10.1 or later  
4. Python version 2.7 or later  

### Quick Start  
1. cd to the ‘catalog’ folder  
2. Create and populate 'catalog.db': run from command line  
**>>python database_populate.py**  
3. Start the server: run from command line  
**>>python catalog.py**  
4. Launch a web browser like Chrome and open the URL  
   http://localhost:8000  
5. Explore the 'Sports Catalog App' by viewing the various pre-populated  
catalog items under the different sports categories  
6. Click the 'Home' link at top left to view the app's home page  
7. Click the 'Login' link and sign-in using your Google+ account  
8. Click the 'Add Item' link to add a new catalog item  
9. Fill the 'Add Item' form and click the 'Submit' button  
10. Verify that your item was successfully added to the catalog  
11. Edit the item you added by clicking on the item and then on the 'Edit' link  
    **Note**: The Edit and Delete links in 'Item Details' page appear only for  
    items that are created by you. You cannot edit/delete items created by  
    others  
12. In the 'Edit Item' form, make changes to the item description, associated  
    image etc and 'Submit'  
13. Verify that the changes were successfully applied in the catalog  
14. Next, try deleting the item you created and verify that the item removal  
was successful  
15. Click the 'Logout' link on the title bar to sign-out out of Sports Catalog app  
16. To test the JSON endpoint, type the following in the browser address bar:  
    http://localhost:8000/catalog.json  
17. To test the Atom end point, type the below in the browser's address bar:  
    http://localhost:8000/recent.atom  
    **Note**: You can also look for the RSS icon on your browser if it supports  
    it. If it does, notice that the RSS feed icon is enabled because our  
    Sports Catalog App website offers a RSS feed. You can click on it to  
    subscribe to that feed.  

###Documentation
* _database_setup.py_ - python module that declares classes needed to perform  
our CRUD operations with SQLAlchemy on an SQLite database (Model)  
* _database_populate.py_ - python module to create and populate 'catalog.db'  
with sample catalog items
* _catalog.py_ - python module implementing the server functionality for our  
Sports Catalog web application (Routes and Controller actions)
* _client_secret.json_ - JSON formatted file containing client ID, client secret  
and other OAuth 2.0 parameters of our Sports Catalog web application  
* _templates/_ - Folder containing the Flask html templates to render the user  
requested page (Views)
* _static/_ - Folder containing static files consumed by our web application.  
These include CSS file and other image files used to format and embellish  
our Catalog App's web pages
* _uploads/_ - Folder containing user uploaded image files that are associated  
with individual catalog items. The name of the image files are stored in  
database for file retrieval later when item details are rendered on a web page  


###Features
* Implements a JSON endpoint returning catalog contents
* Implements Atom endpoint for subscribing to RSS feed on updated content  
* Has page with form allowing logged-in user to add new items  
* Has page with form allowing logged-in user to edit item created only by that  
user  
* Has page with form allowing logged-in user to delete item created only by  
that user using POST request and nonces prevent CSRF
* Implements 3rd party authentication and authorization service. CRUD  
operations check authorization status prior to executing database modifications  


