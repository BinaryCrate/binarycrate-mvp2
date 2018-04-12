from fabric.api import abort, lcd, local, task, warn_only
from fabric.colors import green, red, yellow
from sys import platform
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
    command = kwargs.get('command', 'check')
    print(yellow('Running docker process...'))
    with lcd('.'):
        with warn_only():
            result = local('docker start {project_name}-chrome'.format(
                project_name=project_name))
        if result.failed:
            abort(red('Could not start chrome. Have you run '
                      '\'setup_chrome\'?'))

        local('cp binarycrate/binarycrate/settings/build_number.py front-end/binarycrate/build_number.py')
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
    print(yellow('Running docker process...'))
    with lcd('.'):
        local('docker run --tty --interactive --volume "${PWD}":/opt/project --publish=8000:8000 "${PWD##*/}" migrate')

@task
def test(testname=None):
    print(yellow('Running docker process...'))
    if testname:
        testcommand = " -k '{0}'".format(testname)
    else:
        testcommand = ""
    with lcd('.'):
        local('docker run --tty --interactive --volume "${PWD}":/opt/project --entrypoint="pytest" "${PWD##*/}"' + testcommand)

@task
def frontend_test(testname=None):
    print(yellow('Running docker process...'))
    if testname:
        testcommand = " -k '{0}'".format(testname)
    else:
        testcommand = ""
    with lcd('.'):
        local('cp binarycrate/binarycrate/settings/build_number.py front-end/binarycrate/build_number.py')
        local('docker run --tty '
              '--interactive --volume "${PWD}":/opt/project '
              #'--volume "/home/mark/cavorite":/opt/project/cavorite '
              '--entrypoint="/opt/project/run-frontend-tests" '
              '"${PWD##*/}"' + testcommand)

@task
def makemigrations():
    print(yellow('Running docker process...'))
    with lcd('.'):
        local('docker run --tty --interactive --volume "${PWD}":/opt/project --publish=8000:8000 "${PWD##*/}" makemigrations')

@task
def bash():
    print(yellow('Running docker process...'))
    with lcd('.'):
        local('docker run --tty --interactive --volume "${PWD}":/opt/project --entrypoint="bash" --publish=8000:8000 "${PWD##*/}"')

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
    with lcd('./binarycrate/binarycrate/settings'):
        local('rm -rf ./__init__.py')
        local('ln -s ./development.py ./__init__.py')


