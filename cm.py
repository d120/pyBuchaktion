import os
import sys
import django
from django.core import management

curdir = os.getcwd()
print(os.path.realpath('pyBuchaktion'))
os.chdir(os.path.realpath('pyBuchaktion'))
management.call_command('compilemessages')
os.chdir(curdir)