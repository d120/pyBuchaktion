from pyBuchaktion.models import Book
from django import template

register = template.Library()

BOOK_STATE_CLASSES = [
	('AC', 'success'),
	('RJ', 'danger'),
	('PP', 'info'),
	('OL', 'warning'),
]

def get_state_class(state):
	return [(s, v) for s, v in BOOK_STATE_CLASSES if s == state][0][1]

register.filter('get_state_class', get_state_class)