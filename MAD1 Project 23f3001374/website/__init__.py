import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'RANDOM_KEYss'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'profile_pic')
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    from .views import views
    from .auth import auth
    from .campaign import campaign
    from .ad_request import ad_request
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(campaign, url_prefix='/')
    app.register_blueprint(ad_request, url_prefix='/')
    from .models import User, Campaign, AdRequest
    create_database(app)
    
    login_manager=LoginManager()
    login_manager.login_view='auth.userlogin'
    login_manager.init_app(app)   
    @login_manager.user_loader
    def load_user(id):
        if id is None:
            return None
        try:
            return User.query.get(int(id))
        except ValueError:
            return None
    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
            print('Created database!')

