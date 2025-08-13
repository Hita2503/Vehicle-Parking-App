from flask import Flask #imports the FLask library which is used to create the web app
from application.database import db #step3
app = None 

def create_app():
    app = Flask(__name__) #this function creates the flask app 
    app.secret_key = "23F2003972" # this is a secret key which secures all client_side sessions, it basically excrpts the data so that its not readable by anyone else.
    app.debug = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///23F2003972.sqlite3" #step 3 a local SQLite DB that stores the entire database in a file named 23F2003972.sqlite3
    db.init_app(app) #step3 this connects the app with the database
    app.app_context().push() #this is required for flask to use the database
    return app 
app = create_app() #creates an app_instance and assigns it to app variable to prevent circular imports
from application.controllers import * #step2 from controllers in the application folder, import everything
from application.models import * #from models in the application folder, import everything

if __name__ == '__main__':
    app.run(debug=True) #very useful for fixing any errors as it reloads the app whenever the code is changed and shows the error in the terminal.