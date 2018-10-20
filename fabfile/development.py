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
    print(yellow('Checking that celery is running...'))
    ret = local('docker ps --quiet --filter "label={project_name}-celery"'.format(project_name=project_name), capture=True)
    if len(ret) == 0:
        abort(red('Could not runserver. Have you run '
                  '\'fab development.celery\'?'))
    run(command='runserver 0.0.0.0:8000')

@task
def behave(scenario_regex=None):
    command = 'behave --verbosity=3 {}'.format('' if scenario_regex is None else '--name="{}"'.format(scenario_regex))
    run(command=command)

@task
def shell():
    run(command='shell')

@task
def run(entrypoint="/opt/project/run-django", open_port=True, extra_options = [], **kwargs):
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
        with warn_only():
            result = local('docker start {project_name}-redis'.format(
                project_name=project_name))
        if result.failed:
            abort(red('Could not start redis. Have you run '
                      '\'setup_redis\'?'))
        publish_cmd = ' --publish=8000:8000 ' if open_port else ''

        copyfile('binarycrate/binarycrate/settings/build_number.py', 'front-end/binarycrate/build_number.py')
        local('docker run --tty '
              '--interactive '
              '{publish_cmd} '
              '--volume "{local_pwd}":/opt/project '
              #'--volume "/home/mark/cavorite":/opt/project/cavorite '
              #'--volume "/home/mark/historygraph-perm":/opt/project/historygraph '
              #'--volume "/home/mark/behave-django/behave_django":/usr/local/lib/python2.7/dist-packages/behave_django '
              '--network={project_name}-network '
              '--network-alias=webserver '
              '--entrypoint="{entrypoint}" '
              '{project_name} {command}'.format(command=command,
                            local_pwd=local_pwd,
                            project_name=project_name,
                            entrypoint=entrypoint,
                            publish_cmd=publish_cmd,
                            extra_options=' '.join(extra_options)))


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
def celery():
    with lcd('.'):
        local('docker run --tty '
              '--interactive '
              '--volume "{local_pwd}":/opt/project '
              #'--volume "/home/mark/cavorite":/opt/project/cavorite '
              #'--volume "/home/mark/historygraph-perm":/opt/project/historygraph '
              #'--volume "/home/mark/behave-django/behave_django":/usr/local/lib/python2.7/dist-packages/behave_django '
              '--network={project_name}-network '
              '--network-alias=celery '
              '--label {project_name}-celery '
              '--entrypoint="/opt/project/run-celery" '
              '{project_name} '.format(local_pwd=local_pwd,
                            project_name=project_name,
                            ))

@task
def test(testname=None):
    print(yellow('Running docker process...'))
    if testname:
        testcommand = " -k '{0}'".format(testname)
    else:
        testcommand = ""
    with lcd('.'):
        local('docker run --tty --interactive --volume "' + local_pwd + '":/opt/project --entrypoint="pytest" "' + project_name + '"' + testcommand)

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
        local('docker run --tty --interactive '
              '--volume "{local_pwd}":/opt/project '
              '--entrypoint="bash" '
              '--network={project_name}-network '
              '--network-alias=webserver '
              '--publish=8000:8000 "{project_name}"'.format(
                local_pwd=local_pwd, project_name=project_name))

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
def setup_redis():
    print(yellow('Launching detached postgres docker process...'))
    with lcd('.'):
        with warn_only():
            result = local('docker run --detach --name={project_name}-redis '
                           '--network={project_name}-network '
                           '--network-alias=redis '
                           'redis:4.0'.format(
                            project_name=project_name))
            if result.failed:
                abort(red('Could not setup redis. Have you run '
                          '\'redis\'?'))

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
