import os

from distutils.cmd import Command
from distutils.command.build import build as _build

from setuptools import find_packages, setup
from setuptools.command.install_lib import install_lib as _install_lib


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

class compile_translations(Command):

    """
        The custom command to compile po files to mo binaries for i18n
        when the app is installed.
    """

    description = 'compile message catalogs to MO files via django compilemessages'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from django.core import management

        os.environ['DJANGO_SETTINGS_MODULE'] = ''
        curdir = os.getcwd()
        os.chdir(os.path.realpath('build/lib/pyBuchaktion'))
        management.call_command('compilemessages')
        os.chdir(curdir)

class build(_build):
    sub_commands = _build.sub_commands + [('compile_translations', None)]

class install_lib(_install_lib):
    def run(self):
        _install_lib.run(self)
        self.run_command('compile_translations')

setup(
    name='pyBuchaktion',
    version='1.1.3',
    packages=find_packages(),
    include_package_data=True,
    license='AGPL-3.0',
    description='App for the Buchaktion',
    #long_description=README,
    url='https://d120.de/de/studierende/buchaktion/',
    author='Buchaktionsteam D120',
    author_email='buchaktion@d120.de',
    setup_requires=[
        'django>=1.10.0',
    ],
    install_requires=[
        'django>=1.10.0',
        'django-import-export',
        'pyTUID>=1.2.0',
        'django-bootstrap3',
        'isbnlib',
    ],
    dependency_links=[
      'git+https://github.com/d120/pyTUID#egg=pyTUID-1.2.0',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    cmdclass={
        'build': build,
        'install_lib': install_lib,
        'compile_translations': compile_translations
    },
)
