import os
from setuptools import find_packages, setup


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='pyBuchaktion',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    license='AGPL-3.0',  # example license
    description='App for the Buchaktion',
    #long_description=README,
    #url='https://www.example.com/',
    author='Buchaktionsteam D120',
    author_email='buchaktion@d120.de',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
)
