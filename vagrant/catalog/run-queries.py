# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, Category, User, Item

engine = create_engine("sqlite:///catalogapp.db")
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won"t be persisted into the database until you call
# session.commit(). If you"re not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

session.query(Item).delete()
session.query(User).delete()
session.commit()


# Populating Users
User1 = User(name="Mark Franco", email="mark.franco@outlook.com",
             picture="https://cdn-images-1.medium.com/max/1200/1*NpUUls7kjn9JhO4ChjGV7w.png")
session.add(User1)
session.commit()

User2 = User(name="Katia Frattini", email="katia.frattini@gmail.com",
             picture="https://connectcoworking.com/wp-content/uploads/img_1307.jpg")
session.add(User2)
session.commit()


# Populating Items
item1 = Item(name="MSI GT75 8RG-059IT", description="CPU Intel Core I7-8850H (2,2 GHz - 9 MB L3), "
    + "HDD: 1024 GB - SSD: 1024 GB - RAM: 32 GB, "
    + "Display 17,3\" LED - WiFi IEEE 802.11a/b/g/n/ac, "
    + "Bluetooth 5.0 - Windows 10 Home, "
    + "Graphic card: nVidia GeForce GTX 1080, 8 GB dedicata.", color="black", price="$3,999.00", 
    category_id=1, user_id=1)
session.add(item1)
session.commit()

item2 = Item(name="Lenovo L24Q-10 Silver", description="Monitor WLED Display IPS 23,8\", "
    + "Resolution: qHD 2560x1440 pixel, "
    + "Brightness: 300 cd/m2 - Tempo di risposta: 6 ms, "
    + "HDMI port.", color="black", price="$199.00", category_id=3, user_id=1)
session.add(item2)
session.commit()

item3 = Item(name="APPLE iMac 21.5\" MNDY2TA", description="PC All-In-One"
    + "Intel Quad Core i5 (3/3.5GHz), "
    + "HD 1TB - RAM 8GB - Microphone - Thunderbolt 3 Port, "
    + "Wi-Fi 802.11a/b/g/n/ac - Bluetooth 4.2 - Mac OS Sierra, "
    + "GPU AMD Radeon Pro 555(2GB Dedicata) - Integrated Audio Card, "
    + "Display retroilluminated LED 21.5\" - Videocamera FaceTime HD, "
    + "Magic Keyboard e Magic Mouse 2 included.", color="Light Grey", price="$1,249.00", 
    category_id=2, user_id=1)
session.add(item3)
session.commit()

item4 = Item(name="APPLE Macbook Pro 13\" MPXT2TA", description="CPU Intel Core i5 (2.3/3.6GHz), "
    + "HD 256GB SSD - RAM 8GB - Display 13,3\" retroilluminated LED IPS, "
    + "Wi-Fi 802.11a/b/g/n/ac - Bluetooth 4.2 - Mac OS Sierra, "
    + "Graphic Card Intel Iris Plus Graphics 640, "
    + "Trackpad Force Touch - Videocamera FaceTime HD a 720p.", color="Light Grey", price="$1,599.00", 
    category_id=1, user_id=2)
session.add(item4)
session.commit()

item5 = Item(name="MICROSOFT Surface Studio2 i7 28\"", description="All-In-One, "
    + "CPU Intel Core I7-7820HQ (2,9 GHz - 8 MB L3), "
    + "SSD 1000 GB - RAM 16 GB - Display 28"" LED, "
    + "WiFi IEEE 802.11a/b/g/n/ac - Bluetooth 4.1, "
    + "Windows 10 Pro, "
    + "Scheda grafica: nVidia GeForce GTX 1060.", color="white", price="$3,299.00", 
    category_id=2, user_id=2)
session.add(item5)
session.commit()

item6 = Item(name="SAMSUNG Monitor Led C24F390 23P", description="Monitor LED 23,5\", "
    + "Resolution Full HD 1920x1080 pixel, "
    + "Brightness: 250 cd/m2, "
    + "Response time: 4 ms, "
    + "HDMI Port.", color="black", price="$119.00", 
    category_id=3, user_id=2)
session.add(item6)
session.commit()

item7 = Item(name="Nvidia Geforce GTX 1080 Ti", description="Based on the award-winning Pascal architecture, "
    + "the GeForce GTX 1080 Ti features massive gaming, "
    + "horsepower with 3584 NVIDIA CUDA cores and 12 billion transistors.", color="Metal Grey", price="$699.00", 
    category_id=4, user_id=1)
session.add(item7)
session.commit()


print("Items added successfully!")


