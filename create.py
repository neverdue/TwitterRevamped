from flask import Flask
from models import *

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='postgres://llcmqqdiourazq:0a7e57b9c9d71aec4dd37d40d688b7b01115237fe7b56840b7cd80e88884cdd9@ec2-52-20-248-222.compute-1.amazonaws.com:5432/d4nteal0mkk14o'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db.init_app(app)

def main():
    db.create_all()

if __name__ == "__main__":
    with app.app_context():
        main()
