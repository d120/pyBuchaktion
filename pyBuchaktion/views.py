from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from pyBuchaktion.models import Book, TucanModule
from django.core.urlresolvers import reverse, resolve


def index(request):
	return render(request, 'intro.html', {'message': 'Hi'})
	#return HttpResponse("Hello, world. You're at the pyBuchaktion index.")

def books_all(request):
	books = Book.objects.all()
	return render(request, 'books.html', {'books': books, 'showtag': True})

def books(request):
	books = Book.objects.all().filter(state=Book.ACCEPTED)
	return render(request, 'books.html', {'books': books})

def book(request, book_id):
	book = get_object_or_404(Book, pk=book_id)
	return render(request, 'book.html', {'book': book})

def modules(request):
	modules = TucanModule.objects.all()
	return render(request, 'modules.html', {'modules': modules})

def module(request, module_id):
	module = get_object_or_404(TucanModule, pk=module_id)
	return render(request, 'module.html', {'module': module})

