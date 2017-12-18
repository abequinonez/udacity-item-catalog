# Udacity Full Stack Item Catalog Project

This project, a full stack web application featuring an item catalog, was developed as part of the Udacity Full Stack Web Developer Nanodegree Program. The project guidelines called for an application with a list of items within a variety of categories, complete with a user registration and authentication system. Moreover, registered users can create, edit, and delete their own items.

A live demo is available [here](https://noodlelog.herokuapp.com).

## Technology and Resources

The application was built using Python, Flask, SQLAlchemy, JavaScript, HTML, and CSS. Third-party authentication and authorization is handled by Google Sign-In and Facebook Login. Other resources and technologies include Material Design Lite and jQuery.

## Required Software

* [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
* [Vagrant](https://www.vagrantup.com/downloads.html)

## Required Files

* [Virtual Machine Configuration](https://github.com/udacity/fullstack-nanodegree-vm)

## Setup

1. After VirtualBox and Vagrant have been installed, unzip the contents of the virtual machine configuration. This should produce a directory called fullstack-nanodegree-vm.

2. From the terminal, change to the vagrant directory inside of fullstack-nanodegree-vm.

3. Start the virtual machine by running the command ```vagrant up```. This will begin the process of downloading and installing a Linux operating system along with all of the configuration files.

4. When you get your shell prompt back, log in to the virtual machine by running the command ```vagrant ssh```.

5. Run the command ```cd /vagrant``` from within the virtual machine. Any files or directories added to the vagrant directory on your computer will be accessible from the vagrant directory on the virtual machine.

## Instructions

1. After downloading or cloning this repository, place the newly created directory, udacity-item-catalog, into the vagrant directory on your computer.

2. Back at the terminal, while logged into the virtual machine and within the vagrant directory, change to the udacity-item-catalog directory and run the command ```python3 populate_database.py```. This will create and populate the item catalog database with sample items.

3. Next, start the actual application by running the command ```python3 app.py```. The Flask server should now be running.

4. Finally, open a web browser and navigate to ```http://localhost:8000```.

## JSON API Endpoints

Apart from the regular browser experience, the application also features a few JSON API endpoints for accessing the catalog's raw data. The endpoints are as follows:

1. Catalog data (all categories and items): ```http://localhost:8000/api/catalog```

2. Category data (all items in a category): ```http://localhost:8000/api/catalog/<category_name>```

3. Item data (a single item): ```http://localhost:8000/api/catalog/<category_name>/<item_name>```