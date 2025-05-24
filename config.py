import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'
    SECRET_KEY = os.urandom(11) 

    # Mail Configuration
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = "hannannaimy@gmail.com"
    MAIL_PASSWORD = "wjuy nxha nrlf knvw"

    # Profile Picture Upload Configuration
    UPLOAD_FOLDER = "static/profile_pictures/"
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
