from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from pyBuchaktion.models import Book
from django.core.urlresolvers import reverse

def index(request):
	return render(request, 'intro.html', {'message': reverse('pyBuchaktion:books')})
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

