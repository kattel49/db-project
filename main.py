from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, and_
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

users_list = ["jon", "william", "skylar", "tina"]

todo_lists = ["groceries", "library", "mathematics", "school"]

item_dict = {
    "groceries" : ["eggs", "bread", "cheese", "sausage"],
    "library" : ["Biography", "Science Fiction", "Adventure"],
    "mathematics" : ["calculus", "Linear Algebra", "Number Theory"],
    "school" : ["Pen", "Notebook", "Pencil", "Eraser"]
}


for user in users_list:
    pwd = hash_pwd(user)
    usr = Users(username=user, pwd_hash=pwd)
    # add user to the database
    session.add(usr)
    session.commit()

    user_from_db = session.query(Users).filter(Users.username==user).first()
    for list in todo_lists:
        lst = TodoLists(user_id = user_from_db.id, title=list)
        # add list to the database
        session.add(lst)
        session.commit()
        list_from_db = session.query(TodoLists).filter(and_(TodoLists.title == list, TodoLists.user_id==user_from_db.id)).first()
        # add items associated to the lists
        for item in item_dict[list]:
            itm = TodoItems(todo_list_id = list_from_db.id, body=item)
            # add item to the database
            session.add(itm)
            session.commit()


# delete a few items to check cascade
tina = session.query(Users).filter(Users.username=="tina").first()

tina_grocery = session.query(TodoLists).filter(and_(TodoLists.user_id == tina.id, TodoLists.title=="groceries")).first()

session.delete(tina_grocery)
session.commit()

all_tina_lists = session.query(TodoLists).filter(TodoLists.user_id == tina.id)
print("Lists of Tina:")
for lst in all_tina_lists:
    print("   "+lst.title)

# delete user jon
jon = session.query(Users).filter(Users.username == "jon").first()

session.delete(jon)
session.commit()

print(session.query(Users).filter(Users.username=="jon").first())