from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker 
from db_setup import User, Category, Item, Base
 
engine = create_engine('sqlite:///categitems.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

user1=User(username='jubran nasser', email='jubrannasser@gmail.com')
session.add(user1)
session.commit()


#items for soccer categ
categ1 = Category(name = "soccer")

session.add(categ1)
session.commit()


item1 = Item(name = "two shingurads", description = "thatis warse for body gras", category = categ1, user_id= 1)

session.add(item1)
session.commit()

item2 = Item(name = "shingurands", description = "Juicy grilled chicken patty with tomato mayo and lettuce", category = categ1, user_id = 1)

session.add(item2)
session.commit()

item3 = Item(name = "jersy", description = "fresh baked and served with ice cream", category = categ1, user_id = 1)

session.add(item3)
session.commit()

#items for bascetball categ
categ2 = Category(name = "bascetball")

session.add(categ2)
session.commit()

item1 = Item(name = "Bat", description = "thatis warse for body gras", category = categ2, user_id= 1)

session.add(item1)
session.commit()

#items for baseball categ
categ3 = Category(name = "baseball")

session.add(categ3)
session.commit()

#items for fresbee categ
categ4 = Category(name = "fresbee")

session.add(categ4)
session.commit()

item1 = Item(name = "fresbee", description = "thatis warse for body gras", category = categ4, user_id= 1)

session.add(item1)
session.commit()

#items for snowboarding categ
categ5 = Category(name = "snowboarding")

session.add(categ5)
session.commit()

item1 = Item(name = "snowboard", description = "thatis warse for body gras", category = categ5, user_id= 1)

session.add(item1)
session.commit()

item2 = Item(name = "Goggles", description = "thatis warse for body gras", category = categ5, user_id= 1)

session.add(item2)
session.commit()



print "added menu items!"

