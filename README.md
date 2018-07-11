# Binary Crate MVP2
The second mvp version of binary crate.

This document currently contains only the instructions for setting up Binary Crate for
local development. The deployment.md file contains instructions for updating production
servers.

## Checkout the software Linux and Mac

You need to install Python 2.7, git and docker
Go to your home directory (or another directory you want to host the software in) and type in.

```
git clone https://github.com/BinaryCrate/binarycrate-mvp2.git

cd binarycrate-mvp2

git checkout develop

git submodule update --init --recursive
```

## Checkout the software Windows

You need to install Python 2.7, git and docker
Open a git console and go to your home directory (or another directory you want to host the software in) and type in.

```
git clone https://github.com/BinaryCrate/binarycrate-mvp2.git

cd binarycrate-mvp2

git checkout develop

git submodle update --init --recursive
```

This will check out the project onthe develop branch and retrieve all of the submodules.

Note in Windows we win need to have different console open for git and python.

## Create a virtual environment Linux and Mac

Open a console and cs to the binarcrate-mvp2 directory which the code is checked out into.

Type in

```
virtualenv venv

source venv/bin/activate

pip install --upgrade pip

pip install --upgrade setuptools urllib3[secure]

pip install fabric3==1.13.1.post1  # We use fabric3 to automate tasks
```

This will create a standard python virtual environment for us a install all of the tools used outside of the docker container into it.

## Create a virtual environment Window

Open a standard windows console and cs to the binarcrate-mvp2 directory which the code is checked out into.
These instructions assume you have install Python 2.7 into the c:\python27 folder

Type in

```
c:\python27\scripts\virtualenv venv

venv\scripts\activate.bat

pip install --upgrade pip

pip install --upgrade setuptools urllib3[secure]

pip install fabric3==1.13.1.post1  # We use fabric3 to automate tasks
```

This will create a standard python virtual environment for us a install all of the tools used outside of the docker container into it.

## Go back to previously create virtual environments Linux and Mac

Open a console and cs to the binarcrate-mvp2 directory which the code is checked out into.

Type in

```
source venv/bin/activate
```

This will activate the virtual environment you created previously.

## Go back to previously create virtual environments Windows

Open a standard windows console and cs to the binarcrate-mvp2 directory which the code is checked out into.

Type in

```
venv\scripts\activate.bat
```

This will activate the virtual environment you created previously.

## Create the docker container Linux, Windows and Mac

Open a standard console and Cdcto the binarycrate-mvp2 directory the source code is checked out into.

```
fab development.setup_network

fab development.setup_redis

fab development.setup_chrome

fab development.setup
```

This will create the development docker container. Fabric3 you installed earlier is controlling docker to do this.

```
fab development.run:command=createsuperuser
```

This will create a superuser for the binarycrate django project. Enter a user name and password.

Next you will need two consoles running the binarycrate venv. This is because we will run the celery worker in one of them and the webserver in the other.

```
fab development.celery
```

This will start the celery worker, next change to the other console and start up the webserver

```
fab development.runserver
```

This will run the application. You should be able to browse to 0.0.0.0:8000 and see a login page. You should be able to login with your super user name and password
and see the binary crate Dashboard page.

## Additional useful commands

```
fab development.run:command=shell
```

This will start `python manage.py shell` inside the docker container

```
fab development.run
```

This will start `python manage.py check` inside the docker container.
Ie check is the default command

```
fab development.test
```

To run unit tests for the backend

```
fab development.frontend_test
```

To run frontend unit tests

```
fab development.behave
```

To run BDD tests
