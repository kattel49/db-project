from sqlalchemy import create_engine, Column, Integer, String, or_, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from dotenv import load_dotenv
import os
import bcrypt

load_dotenv()

db_user = os.getenv("DB_USER")
db_pwd = os.getenv("DB_PASSWORD")
db_port = os.getenv("DB_PORT")
db_host = os.getenv("DB_HOST")
db_db = os.getenv("DB_DATABASE")
#bcrypt only works with byte strings
salt = os.getenv("APP_SALT").encode('utf8')

engine = create_engine(f"postgresql://{db_user}:{db_pwd}@{db_host}:{db_port}/{db_db}", echo=False)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()
# Users table
class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(32), nullable=False, unique=True)
    pwd_hash = Column(String(128), nullable=False)

    def verify_pwd(self, pwd):
        #pwd hash is a normal python string so encode it to utf8
        if bcrypt.checkpw(pwd.encode('utf8'), self.pwd_hash.encode("utf8")):
            return True
        return False

def hash_pwd(pwd):
    # databae will encode the hash to utf8, so first decode the string
    return bcrypt.hashpw(pwd.encode('utf8'), salt).decode('utf8')


class TodoList(Base):
    __tablename__ = "todo_list"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, ForeignKey=Users.id)
    title = Column(String(64), nullable=False)




Base.metadata.create_all(engine)

user1 = Users(username="shubhushan", pwd_hash=hash_pwd("shubhushan"))

session.add(user1)
session.commit()

usr = session.query(Users).filter(Users.username=="shubhushan").first()

print(usr.verify_pwd("shubhushan"))