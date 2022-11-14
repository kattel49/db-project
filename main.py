from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
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
    #One to Many relationship, delete all children related to users.id in the TodoList table
    children = relationship("TodoList", cascade="all, delete")

    def verify_pwd(self, pwd):
        #pwd hash is a normal python string so encode it to utf8
        if bcrypt.checkpw(pwd.encode('utf8'), self.pwd_hash.encode("utf8")):
            return True
        return False

def hash_pwd(pwd):
    # database will encode the hash to utf8, so first decode the string
    return bcrypt.hashpw(pwd.encode('utf8'), salt).decode('utf8')


class TodoList(Base):
    __tablename__ = "todo_lists"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # title of the list
    title = Column(String(64), nullable=False)
    # shareable list
    public = Column(Boolean, nullable=False, default=False)



# tests
Base.metadata.create_all(engine)

user1 = Users(username="shubhushan", pwd_hash=hash_pwd("shubhushan"))

session.add(user1)
session.commit()
session.close()

user1 = session.query(Users).filter(Users.username=="shubhushan").first()
print(user1.id)
todo1 = TodoList(user_id=user1.id, title="Groceries")

session.add(todo1)
session.commit()
session.close()

session.delete(user1)
session.commit()
session.close()