# -*- coding: utf-8 -*-
# BinaryCrate -  BinaryCrate an in browser python IDE. Design to make learning coding easy.
# Copyright (C) 2018 BinaryCrate Pty Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, print_function, unicode_literals
from fabric.api import abort, lcd, local, task, warn_only
from fabric.colors import green, red, yellow
from sys import platform
from shutil import copyfile
import os

local_pwd = os.path.realpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

project_name = os.path.split(local_pwd)[-1]

@task
def build():
    print(yellow('Building docker image...'))
    with lcd('.'):
        local('docker build --tag="{0}" .'.format(project_name))

@task
def runserver():
    run(command='runserver 0.0.0.0:8000')

@task
def behave(scenario_regex=None):
    command = 'behave --verbosity=3 {}'.format('' if scenario_regex is None else '--name="{}"'.format(scenario_regex))
    run(command=command)

@task
def shell():
    run(command='shell')

@task
def run(**kwargs):
    print(yellow('Updating version file...'))
    create_version_file()
    print(yellow('Reseting pypyjs environment...'))
    with lcd('./pypyjs-release/pypyjs-release'):
        local('git checkout -- .')#, capture=True)
    command = kwargs.get('command', 'check')
    print(yellow('Running docker process...'))
    with lcd('.'):
        with warn_only():
            result = local('docker start {project_name}-chrome'.format(
                project_name=project_name))
        if result.failed:
            abort(red('Could not start chrome. Have you run '
                      '\'setup_chrome\'?'))

        copyfile('binarycrate/binarycrate/settings/build_number.py', 'front-end/binarycrate/build_number.py')
        local('docker run --tty '
              '--interactive '
              '--publish=8000:8000 '
              '--volume "{local_pwd}":/opt/project '
              #'--volume "/home/mark/cavorite":/opt/project/cavorite '
              #'--volume "/home/mark/historygraph-perm":/opt/project/historygraph '
              #'--volume "/home/mark/behave-django/behave_django":/usr/local/lib/python2.7/dist-packages/behave_django '
              '--network={project_name}-network '
              '--network-alias=webserver '
              '{project_name} {command}'.format(command=command,
                            local_pwd=local_pwd,
                            project_name=project_name))


@task
def migrate():
    print(yellow('Updating version file...'))
    create_version_file()
    print(yellow('Reseting pypyjs environment...'))
    with lcd('./pypyjs-release/pypyjs-release'):
        local('git checkout -- .')#, capture=True)
    print(yellow('Running docker process...'))
    with lcd('.'):
        local('docker run --tty --interactive --volume "' + local_pwd + '":/opt/project --publish=8000:8000 "' + project_name + '" migrate')

@task
def test(testname=None):
    print(yellow('Running docker process...'))
    if testname:
        testcommand = " -k '{0}'".format(testname)
    else:
        testcommand = ""
    with lcd('.'):
        local('docker run --tty --interactive '
              '--volume "' + local_pwd + '":/opt/project '
              '--entrypoint="/opt/project/run-backend-tests" "' + project_name + '"' + testcommand)

@task
def frontend_test(testname=None):
    print(yellow('Running docker process...'))
    if testname:
        testcommand = " -k '{0}'".format(testname)
    else:
        testcommand = ""
    with lcd('.'):
        copyfile('binarycrate/binarycrate/settings/build_number.py', 'front-end/binarycrate/build_number.py')
        local('docker run --tty '
              '--interactive --volume "' + local_pwd + '":/opt/project '
              #'--volume "/home/mark/cavorite":/opt/project/cavorite '
              '--entrypoint="/opt/project/run-frontend-tests" '
              '"' + project_name + '"' + testcommand)

@task
def makemigrations():
    print(yellow('Running docker process...'))
    with lcd('.'):
        local('docker run --tty --interactive --volume "' + local_pwd + '":/opt/project --publish=8000:8000 "' + project_name + '" makemigrations')

@task
def bash():
    print(yellow('Running docker process...'))
    with lcd('.'):
        local('docker run --tty --interactive --volume "' + local_pwd + '":/opt/project --entrypoint="bash" --publish=8000:8000 "' + project_name + '"')

@task
def setup():
    build()
    create_symlinks()
    migrate()

@task
def setup_network():
    print(yellow('Launching detached postgres docker process...'))
    with lcd('.'):
        local('docker network create --driver bridge {project_name}-network'
              ''.format(project_name=project_name))


@task
def setup_chrome():
    print(yellow('Launching detached postgres docker process...'))
    with lcd('.'):
        with warn_only():
            result = local('docker run --detach --name={project_name}-chrome '
                           '--network={project_name}-network '
                           '--network-alias=chrome '
                           'selenium/standalone-chrome'.format(
                            project_name=project_name))
            if result.failed:
                abort(red('Could not setup chrome. Have you run '
                          '\'setup_network\'?'))

@task
def create_symlinks():
    print(yellow('Creating symlinks...'))
    print(yellow('Running docker process...'))
    with lcd('.'):
        local('docker run --tty --interactive --volume "' + local_pwd + '":/opt/project --entrypoint="/opt/project/run-create-symlinks" --publish=8000:8000 "' + project_name + '"')

@task
def create_version_file():
    with lcd('.'):
        output = local('git rev-parse HEAD', capture=True)
        with open('binarycrate/binarycrate/settings/version_hash.py', 'w') as f:
            f.write('''# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

VERSION_HASH = '{}'
'''.format(output.stdout))
