# Deployment Guide for BinaryCrate

### About this document

This document discusses how to deploy an update for BinaryCrate, it does not yet discuss how that server is configured or why.

### Before you start

BinaryCrate currently has a single development server running inside AWS specifically an EC2 instance running Ubuntu 16.04 in the us-west2 Oregon region.
Oregon is chosen because it is the cheapest region. The production system will probably be run in another region.

You will need to have been given access to this server. This will require you supplying a SSH public key.

### Preparing the code

All coding should happen on the develop branch. If we are happy that we want to deploy to production we should enact this procedure.

Check on changes in on the develop branch.

```
git checkout master
```

Now the are on the master branch. First we want to update from the develop branch.

```
git merge develop --no-ff
```

Next update the build number in the binarycrate/binarycrate/settings/build_number.py file.
Build numbers are always an incrementing six digit number. Prepended with zeros to make it six digits long. So the first
build number was 000001 and the current build number as of writing is 000003.

Start up the development server locally (if not already running) and check the build number has updated correctly.

Navigate to the dashboard and login if necessary.

We check the build number in two different places.

1. For the backend view the page source and search for the text "Build number = " this should show the build number you just set

2. The pypyjs/cavorite front end program will output the current Build Number to the console when the program startup up. In chrome open the
javascript console and reload the page. Once the dashboard displays in should have printed the build number to the console.

If we are happy with that use `git add` and `git commit` to check the changes into the master branch.

Push the master branch to the git server

```
git push origin master
```

Tag the current commit with the build number.

```
git tag -a Build000004
```

Please note in the tag we use the Build and then the number with no space.

Push the tag to the git server.

```
git push origin Build000004
```

Lastly we want to have the new build number available in the develop branch and have git describe report the correct version.

First checkout the develop branch

```
git checkout develop
```

Then merge the master branch into develop.

```
git merge master
```

And push our new develop branch back to the server.

```
git push origin develop
```

### Deploying the update

Connect to the server in the cloud.

```
ssh ubuntu@dev.binarycrate.com
```

Turn off the webserver while we are performing the upgrade this version. These instructions could cause clients to immutabilty cache the wrong version of the static files otherwise.
```
sudo service nginx stop
```

Go to the correct directory

```
cd /srv/binarycrate-mvp2
```

Pull in the code update.

```
sudo git fetch

sudo git checkout Build000004

sudo git submodule sync

sudo git submodule update
```

Production specific config values are stored in binarycrate/binarycrate/settings/production.py however this file is not stored in git for security reasons.
Instead we have binarycrate/binarycrate/settings/production_template.py if this update requires to the production config you must make them now manually with

```
sudo pico binarycrate/binarycrate/settings/production.py
```

We now update the deployed virtual environment with any new module versions
```
sudo ./binarycrate/bin/pip install -r requirements.txt
```

Next we need to manually copy the build_number.py file so it is available and up to date in the front end code

```
sudo cp binarycrate/binarycrate/settings/build_number.py front-end/binarycrate/build_number.py
```

We now load the new frontend code into the pypysjs-release area.

```
sudo python pypyjs-release/pypyjs-release/tools/module_bundler.py add pypyjs-release/pypyjs-release/lib/modules/ cavorite/cavorite/
sudo python pypyjs-release/pypyjs-release/tools/module_bundler.py add pypyjs-release/pypyjs-release/lib/modules/ front-end/binarycrate/
sudo python pypyjs-release/pypyjs-release/tools/module_bundler.py add pypyjs-release/pypyjs-release/lib/modules/ historygraph/historygraph/
```

Next we tell pypyjs to preload all of our modules - this greatly improves the load time

```
sudo python pypyjs-release/pypyjs-release/tools/module_bundler.py preload pypyjs-release/pypyjs-release/lib/modules/ cavorite
sudo python pypyjs-release/pypyjs-release/tools/module_bundler.py preload pypyjs-release/pypyjs-release/lib/modules/ binarycrate
sudo python pypyjs-release/pypyjs-release/tools/module_bundler.py preload pypyjs-release/pypyjs-release/lib/modules/ historygraph

We need to update the version hash used for the static files
```
sudo ./binarycrate/bin/fab development.create_version_file
```

We now update the django static. Note this is different to the above step in that we put all pypyjs files including standard modules and the pypyjs interpreter
in the correct Django static area.
```
sudo ./binarycrate/bin/python binarycrate/manage.py collectstatic
```

Run the migrations
```
sudo ./binarycrate/bin/python binarycrate/manage.py migrate
```

Restart uwsgi to force it to reload our changes.
```
sudo service uwsgi-emperor restart
```

Turn the webserver back on
```
sudo service nginx start
```

We are now deployed, you can use the method above to check the build number.

We is useful to update the ubuntu requirements on the erver as frequently as possible. Whenever we are logged into it that is a good time.

```
sudo apt-get update
sudo apt-get dist-upgrade
sudo apt-get autoremove
```

If apt-get updated the kernel version the server will need a reboot.
```
sudo reboot
```
