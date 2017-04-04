#!/usr/bin/env python3

# A cool tool accessing the not-so-cool TUCaN to retrieve the books that are
# proposed by the lecturers.

from json         import JSONDecoder
from robobrowser  import RoboBrowser
from sys          import argv
from threading    import Thread
from time         import sleep
from urllib.parse import urlencode
import csv
import http
import logging
import re

# URLs.
TUCAN_URL = 'https://www.tucan.tu-darmstadt.de'
TUCAN_STARTPAGE_URL = "%s/scripts/mgrqcgi?APPNAME=CampusNet&PRGNAME=EXTERNALPAGES&ARGUMENTS=-N2,-N,-Awelcome" % TUCAN_URL
GOOGLE_BOOKS_BASE_PATH = '/books/v1/volumes?'
# CSS Selectors.
TUCAN_CC_SELECTOR = '#pageTopNavi ul a'
TUCAN_DEPT_SELECTOR = '#auditRegistration_list li[title="Dept. 20 - Computer Science"] a'
TUCAN_MODULE_CONTAINER_SELECTOR = '#auditRegistration_list li a'
TUCAN_MODULE_COURSE_IDNAME_SELECTOR = '#pageContent form h1';
TUCAN_MODULE_INFORMATION_SELECTOR = '#contentlayoutleft table:nth-of-type(1) tr:nth-of-type(2) p'
TUCAN_MODULE_INFORMATION_TYPE_SELECTOR = 'b:nth-of-type(1)'
TUCAN_MODULE_SELECTOR = '.eventTable td a'
# RegEx Patterns.
TUCAN_MODULE_COURSE_IDNAME_PATTERN = re.compile(r'^\s*(\w{2,2}-\w{2,2}-\w{4,4}-\w{2,2})\s*(.+?)\s*$')
TUCAN_MODULE_COURSE_NAME_NORMALIZE_PATTERN = re.compile(r'^(?:\s|\\t)*(.*?)(?:\s|\\t)*$')
TUCAN_MODULE_LITERATURE_CONTENT_PATTERN = re.compile(r'^\s*<p><b>(.*?)</b>(.*)</p>\s*$')
# Magic Numbers.
ISBN_RELIABILITY_BASE_VALUE = 50
ISBN_RELIABILITY_MAX_VALUE = 100
ISBN_RELIABILITY_BOOKSTRING_LENGTH = 50
ISBN_RELIABILITY_BOOKSTRING_LENGTH_MULTIPLIER = 0.5



###################
##### Classes #####
###################

# Model class to store a book.
class Book:
    def __init__(self, book_string):
        self.book_string = book_string
        self.isbn_type = None
        self.isbn = None
        self.isbn_reliability = 0


    def __str__(self):
        return "Magic book string: '%s'; ISBN Type: %s; ISBN: %s" % (self.book_string, self.isbn_type, self.isbn)


    def __repr__(self):
        return str(self)
# end: Book


# Model class to store a module.
class Module:
    def __init__(self, cid, name, url, books):
        self.cid = cid
        self.name = name
        self.url = url
        self.books = books


    def __str__(self):
        return "Course-ID: %s; Name: %s; Books: %s" % (self.cid, self.name, str(self.books))


    def __repr__(self):
        return str(self);
# end: Module


# Class to retrieve the ISBN from a book title by accessing the Google API "books".
class IsbnMagic:
    def __init__(self):
        self.http_client = http.client.HTTPSConnection('www.googleapis.com')


    def retrieveAndSetIsbn(self, book):
        book_string = book.book_string
        if len(book_string) > ISBN_RELIABILITY_BOOKSTRING_LENGTH:
            book.isbn_reliability = min(int(ISBN_RELIABILITY_BASE_VALUE + len(book_string) * ISBN_RELIABILITY_BOOKSTRING_LENGTH_MULTIPLIER), ISBN_RELIABILITY_MAX_VALUE)
        path = GOOGLE_BOOKS_BASE_PATH + urlencode({
            'q': book_string
        })
        self.http_client.request('GET', path)
        response = self.http_client.getresponse()
        content = response.read().decode('UTF-8')
        data = JSONDecoder().decode(content)
        if data:
            data = data.get('items', None)
        if data:
            data = data[0] if data else None
        if data:
            data = data.get('volumeInfo', None)
        if data:
            data = data.get('industryIdentifiers', None)
        if data:
            data = data[0] if data else None

        isbn_type = None
        isbn = None
        if data:
            isbn_type = data.get('type', None)
            isbn = data.get('identifier', None)
        book.isbn_type = isbn_type
        book.isbn = isbn
# end: IsbnMagic


# Class to access TUCaN and return the results as modules (see Module).
class Tucan:
    def retrieveModule(self, module_url):
        browser = self._createBrowser()
        browser.open(TUCAN_URL + module_url)

        cidname_element = browser.select(TUCAN_MODULE_COURSE_IDNAME_SELECTOR)[0];
        cidname_match = TUCAN_MODULE_COURSE_IDNAME_PATTERN.match(cidname_element.text);
        cid = cidname_match.group(1);
        name = cidname_match.group(2);

        information = browser.select(TUCAN_MODULE_INFORMATION_SELECTOR);
        literature = None
        for info in information:
            text = info.select(TUCAN_MODULE_INFORMATION_TYPE_SELECTOR)[0].text.lower()
            if text.startswith('literatur'):
                literature = info
                break
        books = []
        if literature:
            # Only process if there is literature, of course.

            literature_content = TUCAN_MODULE_LITERATURE_CONTENT_PATTERN.sub(r'\2', str(literature).replace('\n', '').replace('\r', ''))
            next_book = None
            pause = False
            for char in literature_content:
                book = None
                if char == '<':
                    if next_book:
                        books.append(Book(TUCAN_MODULE_COURSE_NAME_NORMALIZE_PATTERN.sub(r'\1', next_book)))
                        next_book = None
                    pause = True
                elif char == '>':
                    pause = False
                elif not pause:
                    next_book = next_book + char if next_book else char
            if next_book:
                books.append(Book(TUCAN_MODULE_COURSE_NAME_NORMALIZE_PATTERN.sub(r'\1', next_book)))

        return Module(cid, name, module_url, books)


    def retrieveModules(self):
        module_urls = tucan.retrieveModuleUrls()

        module_cids = []
        modules = []
        for url in module_urls:
            try:
                module = tucan.retrieveModule(url)
                if not module.cid in module_cids:
                    module_cids.append(module.cid)
                    modules.append(module)
            except:
                logging.warning("Failed to process module at <%s>! Error:" % url, exc_info = True)
        return modules


    def retrieveModuleUrls(self):
        browser = self._createBrowser();

        browser.follow_link(browser.select(TUCAN_CC_SELECTOR)[1])
        browser.follow_link(browser.select(TUCAN_DEPT_SELECTOR)[0])

        return self._retrieveModuleUrls(browser)


    def _retrieveModuleUrls(self, browser):
        links = [ module['href'] for module in browser.select(TUCAN_MODULE_SELECTOR) ]
        containers = browser.select(TUCAN_MODULE_CONTAINER_SELECTOR);
        for container in containers:
            browser.follow_link(container)
            links += self._retrieveModuleUrls(browser)
            browser.back()
        return links


    def _createBrowser(self):
        browser = RoboBrowser(parser = 'lxml')
        browser.open(TUCAN_STARTPAGE_URL)
        return browser
# end: Tucan



##############
### SCRIPT ###
##############

tucan = Tucan()
modules = tucan.retrieveModules()
isbnMagic = IsbnMagic()
for module in modules:
    for book in module.books:
        isbnMagic.retrieveAndSetIsbn(book)

output_file = argv[1]
with open(output_file, 'w') as file:
    writer = csv.writer(file, delimiter = ',', quotechar = '\\', quoting = csv.QUOTE_MINIMAL)
    writer.writerow(['cid', 'name', 'url', 'book_string', 'isbn_type', 'isbn', 'isbn_reliability'])
    for module in modules:
        cid = module.cid
        name = module.name
        url = module.url
        for book in module.books:
            writer.writerow([cid, name, url, book.book_string, book.isbn_type, book.isbn, book.isbn_reliability])
