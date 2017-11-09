#!/usr/bin/env python3
#
# Sample data for populating the item catalog database. Adds a user and items.

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Item

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

def addSampleData():
    """Adds sample data to the User and Item tables"""

    # Add a user
    user1 = User(
        name='Robo Admin',
        email='roboadmin@email.com',
        # Robo Admin picture courtesy of Udacity (as found on OAuth course)
        picture=(
            'https://pbs.twimg.com/profile_images/2671170543/'
            '18debd694829ed78203a5a36dd364160_400x400.png'))
    session.add(user1)
    session.commit()

    # Add an item to the Chinese category
    item1 = Item(
        user=user1,
        cat_id=1,
        name='Wonton Noodles',
        # Description source: https://en.wikipedia.org/wiki/Wonton_noodles
        description=(
            'Wonton noodles (pinyin: Yúntūn miàn; Cantonese Yale: wàhn tān '
            'mihn, sometimes called wanton mee ("wanton" is a Cantonese word '
            'for dumpling while noodles in Hokkien is "mee" or in Cantonese, '
            '"min") is a Cantonese noodle dish which is popular in Guangzhou'
            ', Hong Kong, Malaysia, Singapore and Thailand. The dish is '
            'usually served in a hot broth, garnished with leafy vegetables, '
            'and wonton dumplings. The types of leafy vegetables used are '
            'usually kai-lan also known as Chinese kale. Another type of '
            'dumpling known as shui jiao is sometimes served in place of '
            'wonton. It contains prawns, chicken or pork, spring onions with '
            'some chefs adding mushroom and black fungus.'))
    session.add(item1)
    session.commit()

    # Add an item to the Japanese category
    item2 = Item(
        user=user1,
        cat_id=2,
        name='Udon',
        # Description source: https://en.wikipedia.org/wiki/Udon
        description=(
            'Udon (饂飩, usually written as うどん) is a type of thick wheat '
            'flour noodle of Japanese cuisine. Udon is often served hot as a '
            'noodle soup in its simplest form, as kake udon, in a mildly '
            'flavoured broth called kakejiru, which is made of dashi, soy '
            'sauce, and mirin. It is usually topped with thinly chopped '
            'scallions. Other common toppings include tempura, often prawn '
            'or kakiage (a type of mixed tempura fritter), or aburaage, a '
            'type of deep-fried tofu pockets seasoned with sugar, mirin, and '
            'soy sauce. A thin slice of kamaboko, a halfmoon-shaped fish '
            'cake, is often added. Shichimi can be added to taste.'))
    session.add(item2)
    session.commit()

    print('Sample data added!')

# Populate the database with sample data (if it hasn't already been added)
if session.query(User).filter_by(email='roboadmin@email.com').first() is None:
    addSampleData()
else:
    print('Error. Sample data has already been added.')
