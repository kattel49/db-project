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
    children = relationship("TodoLists", cascade="all, delete")

    def verify_pwd(self, pwd):
        #pwd hash is a normal python string so encode it to utf8
        if bcrypt.checkpw(pwd.encode('utf8'), self.pwd_hash.encode("utf8")):
            return True
        return False

def hash_pwd(pwd):
    # database will encode the hash to utf8, so first decode the string
    return bcrypt.hashpw(pwd.encode('utf8'), salt).decode('utf8')


class TodoLists(Base):
    __tablename__ = "todo_lists"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # title of the list
    title = Column(String(64), nullable=False)
    # shareable list
    public = Column(Boolean, nullable=False, default=False)
    # One to many relationship, cascade on delete
    children = relationship("TodoItems", cascade="all, delete")


class TodoItems(Base):
    __tablename__ = "todo_items"

    id = Column(Integer, primary_key=True)
    todo_list_id = Column(Integer, ForeignKey('todo_lists.id'), nullable=False)
    body = Column(String(128), nullable=False)


# tests
Base.metadata.create_all(engine)

user1 = Users(username="shubhushan", pwd_hash=hash_pwd("shubhushan"))

session.add(user1)
session.commit()
session.close()

user1 = session.query(Users).filter(Users.username=="shubhushan").first()
print(user1.id)
todo1 = TodoLists(user_id=user1.id, title="Groceries")

session.add(todo1)
session.commit()
session.close()

todo1 = session.query(TodoLists).filter(TodoLists.title == "Groceries").first()

for i in range(10):
    item = TodoItems(body="x", todo_list_id=todo1.id)
    session.add(item)
    session.commit()
session.close()
