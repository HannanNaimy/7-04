import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'
    SECRET_KEY = os.urandom(11)
    MAIL_SERVER = "smtp.office365.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = "1221106678@student.mmu.edu.my"
    MAIL_PASSWORD = "wdwdwadafafiesjf"