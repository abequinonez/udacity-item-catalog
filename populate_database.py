#!/usr/bin/env python3
#
# Sample data for populating the item catalog database. Adds a user and items.

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Item

# Connect to the database and bind the engine to the Base class
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

# Create a session
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
            'some chefs adding mushroom and black fungus.'),
        image_url=(
            'https://steamykitchen.com/wp-content/uploads/2008/08/'
            'image_2144web2.jpg'))
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
            'cake, is often added. Shichimi can be added to taste.'),
        image_url=(
            'https://japancentre-images.freetls.fastly.net/recipes/pics/733/'
            'main/733-udon-noodles.jpg'))
    session.add(item2)
    session.commit()

    # Add an item to the Korean category
    item3 = Item(
        user=user1,
        cat_id=3,
        name='Janchi Guksu',
        # Description source: https://en.wikipedia.org/wiki/Janchi-guksu
        description=(
            'Janchi-guksu (Korean: 잔치국수) or banquet noodles is a Korean '
            'noodle dish consisting of wheat flour noodles in a light broth '
            'made from anchovy and sometimes also dasima (kelp). Beef broth '
            'may be substituted for the anchovy broth. It is served with a '
            'sauce made from sesame oil, ganjang, and small amounts of chili '
            'pepper powder and scallions. Thinly sliced jidan (지단, fried egg)'
            ', gim (laver), and zucchini are added on top of the dish as '
            'garnishes.'),
        image_url=(
            'http://www.futuredish.com/wp-content/uploads/2017/02/'
            'Janchi-Guksu.png'))
    session.add(item3)
    session.commit()

    # Add an item to the Thai category
    item4 = Item(
        user=user1,
        cat_id=4,
        name='Boat Noodles',
        # Description source: https://en.wikipedia.org/wiki/Boat_noodles
        description=(
            'Boat noodles or kuaitiao ruea (Thai: ก๋วยเตี๋ยวเรือ, pronounced '
            '[kǔa̯j.tǐa̯w rɯ̄a̯]) is a Thai style noodle dish, which has a '
            'strong flavor. It contains both pork and beef, as well as dark '
            'soy sauce, pickled bean curd and some other spices, and is '
            'normally served with meatballs and pig’s liver. The soup also '
            'contains nam tok (Thai: น้ำตก), which is cow or pigs blood '
            'mixed with salt and spices, to season the soup. The color of '
            'the soup is similar to beef noodles soup (Thai: '
            'ก๋วยเตี๋ยวเนื้อ) but considerably thicker due to the blood '
            'added. It is commonly served in a small bowl.'),
        image_url=(
            'https://www.saveur.com/sites/saveur.com/files/styles/medium_1x_/'
            'public/thaiboatnoodlesoup_2000x1500.jpg?itok=OKdjcIuA'))
    session.add(item4)
    session.commit()

    # Add an item to the Vietnamese category
    item5 = Item(
        user=user1,
        cat_id=5,
        name='Pho',
        # Description source: https://en.wikipedia.org/wiki/Pho
        description=(
            'Phở or pho (pronounced variously as /fɜːr/, /fʌ/, or /foʊ/; '
            'Vietnamese: [fəː˧˩˧]) is a Vietnamese noodle soup consisting of '
            'broth, rice noodles called bánh phở, a few herbs, and meat, '
            'primarily made with either beef (phở bò) or chicken (phở gà). '
            'Pho is a popular street food in Vietnam and the specialty of a '
            'number of restaurant chains around the world. Pho originated in '
            'the early 20th century in northern Vietnam, and was popularized '
            'throughout the rest of the world by refugees after the Vietnam '
            'War. Because pho\'s origins are poorly documented, there is '
            'significant disagreement over the cultural influences that led '
            'to its development in Vietnam, as well as the etymology of the '
            'word itself. The Hanoi and Saigon styles of pho differ by '
            'noodle width, sweetness of broth, and choice of herbs.'),
        image_url=(
            'https://d1doqjmisr497k.cloudfront.net/-/media/mccormick-us/'
            'recipes/kitchen-basics/v/800/vietnamese_beef_noodle_soup.ashx?'
            'vd=20171018T134637Z&hash='
            '7D6E1C193DFC641586A7E9A45B11FA048D42542F'))
    session.add(item5)
    session.commit()

    # Add an item to the Other category
    item6 = Item(
        user=user1,
        cat_id=6,
        name='Hae Mee',
        # Description source: https://en.wikipedia.org/wiki/Hae_mee
        description=(
            'Hae mee (also called prawn mee) is a noodle soup dish popular '
            'in Malaysia and Singapore. It can also refer to a fried noodle '
            'dish known as Hokkien mee. The dish\'s name literally means '
            '"prawn noodles" in Hokkien. Egg noodles are served in richly '
            'flavoured dark soup stock with prawns, pork slices, fish cake '
            'slices and bean sprouts, topped with fried shallots and spring '
            'onion. The stock is made using dried shrimp, plucked heads of '
            'prawns, white pepper, garlic and other spices. Traditionally, '
            'lard is added to the soup, but this is now less common due to '
            'health concerns.'),
        image_url=(
            'https://i1.wp.com/angsarap.net/wp-content/uploads/2014/12/'
            'Penang-Prawn-Mee-Wide.jpg'))
    session.add(item6)
    session.commit()

    # Add another item to the Japanese category
    item7 = Item(
        user=user1,
        cat_id=2,
        name='Pork Ramen',
        # Description information source:
        # https://www.williams-sonoma.com/recipe/pork-ramen.html
        description=(
            'Ramen noodles served in chicken broth and topped with braised '
            'boneless pork. Additional toppings include eggs, green onions, '
            'and garlic cloves. Soy sauce and sesame oil are added for '
            'seasoning.'),
        image_url=(
            'https://www.williams-sonoma.com/wsimgs/rk/images/dp/recipe/'
            '201707/0063/img97l.jpg'))
    session.add(item7)
    session.commit()

    # Add another item to the Other category
    item8 = Item(
        user=user1,
        cat_id=6,
        name='Chicken Curry Laksa',
        # Description information source:
        # http://themacadames.com/2014/07/12/chicken-curry-laksa/
        description=(
            'Egg noodles served in a spicy coconut-based curry soup and '
            'topped with chicken. Other toppings include eggplant, bean '
            'sprouts, and tofu puffs.'),
        image_url=(
            'https://i2.wp.com/themacadames.com/wp-content/uploads/2014/07/'
            'Laksa-Lead-image.jpg'))
    session.add(item8)
    session.commit()

    print('Sample data added!')

# Populate the database with sample data (if it hasn't already been added)
if session.query(User).filter_by(email='roboadmin@email.com').first() is None:
    addSampleData()
else:
    print('Error. Sample data has already been added.')
