# binary-crate
The second mvp version of binary crate

First create a virtual environment

virtualenv venv -p python3
source venv/bin/activate

pip install --upgrade pip 
pip install --upgrade setuptools urllib3[secure]

pip install fabric3==1.13.1.post1  # We use fabric3 to automate tasks
pip install django==1.11.5  # We need django in the venv to create apps in our project

fab development.build

This will create the development docker container

fab development.runserver

This will run the application. 

fab development.run:command=shell

This will start `python3 manage.py shell` inside the docker container

fab development.run

This will start `python3 manage.py check` inside the docker container.
Ie check is ther default command

