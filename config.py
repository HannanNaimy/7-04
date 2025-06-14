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
    UPLOAD_FOLDER = os.path.join("static", "profile_pictures")
    POST_PICTURE_FOLDER = os.path.join("upload", "postpicture")
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
    MAX_POST_PIC_SIZE = 2 * 1024 * 1024  # 2MB

    # Flask-Migrate settings (if needed)
    # MIGRATE_DIR = os.path.join(os.path.dirname(__file__), 'migrations')

    # Other global settings can be added here as needed
    # Example: PAGINATION_PER_PAGE = 20
