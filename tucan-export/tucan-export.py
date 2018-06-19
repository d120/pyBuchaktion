#!/usr/bin/env python3

# A cool tool accessing the not-so-cool TUCaN to retrieve the books that are
# proposed by the lecturers.

from datetime     import datetime
from json         import JSONDecoder
from robobrowser  import RoboBrowser
from sys          import argv
from threading    import Thread
from time         import sleep
from urllib.parse import urlencode
from html         import unescape
from math         import floor
from Levenshtein import distance
import csv
import http
import logging
import re

# URLs.
TUCAN_URL = 'https://www.tucan.tu-darmstadt.de'
TUCAN_STARTPAGE_URL = "%s/scripts/mgrqcgi?APPNAME=CampusNet&PRGNAME=EXTERNALPAGES&ARGUMENTS=-N1,-N,-Awelcome" % TUCAN_URL
GOOGLE_BOOKS_BASE_PATH = '/books/v1/volumes?'
# CSS Selectors.
TUCAN_CC_SELECTOR = '#pageTopNavi ul a'
#TUCAN_DEPT_SELECTOR = '#auditRegistration_list li[title="Dept. 20 - Computer Science"] a'
TUCAN_DEPT_SELECTOR = '#auditRegistration_list li[title="FB20 - Informatik"] a'
# TUCAN_DEPT_SELECTOR = '#auditRegistration_list li[title="FB04 - Mathematik"] a'

TUCAN_MODULE_CONTAINER_SELECTOR = '#auditRegistration_list li a'
TUCAN_BREADCRUMBS_SELECTOR = '.pageElementTop > h2 > a'
TUCAN_MODULE_COURSE_IDNAME_SELECTOR = '#pageContent form h1';
TUCAN_MODULE_INFORMATION_SELECTOR = '#contentlayoutleft table:nth-of-type(1) tr:nth-of-type(2) p'
TUCAN_MODULE_INFORMATION_TYPE_SELECTOR = 'b:nth-of-type(1)'
TUCAN_MODULE_SELECTOR = '.eventTable td a'
# RegEx Patterns.
TUCAN_MODULE_COURSE_IDNAME_PATTERN = re.compile(r'^\s*(\w{2,2}-\w{2,2}-\w{4,4}-\w{2,2})\s*(.+?)\s*$')
TUCAN_MODULE_COURSE_NAME_NORMALIZE_PATTERN = re.compile(r'^(?:\s|\\t)*(.*?)(?:\s|\\t)*$')
TUCAN_MODULE_LITERATURE_CONTENT_PATTERN = re.compile(r'^\s*<p><b>(.*?)</b>(.*)</p>\s*$')
TUCAN_LINK_NAME_PATTERN = re.compile(r'^<a href="(.*)">(.*)</a>$')
TUCAN_CONSIDER_PATTERN = re.compile(r'^([\w\s]+\.)*[\w\s]+[\.:]?$')
# Magic Numbers.
ISBN_RELIABILITY_BASE_VALUE = 50
ISBN_RELIABILITY_MAX_VALUE = 100
ISBN_RELIABILITY_BOOKSTRING_LENGTH = 50
ISBN_RELIABILITY_BOOKSTRING_LENGTH_MULTIPLIER = 0.5
SANITY_CHECK_STEPWIDTH = 4
SANITY_CHECK_MAXRATIO = 0.6



###################
##### Classes #####
###################

# Model class to store a book.
class Book:
    def __init__(self):
        self.isbn = None
        self.title = None
        self.author = None
        self.price = 0
        self.publisher = None
        self.year = None


    def __str__(self):
        return "Magic book string: '%s'; ISBN: %s; Title: %s" % (self.book_string, self.isbn, self.title)


    def __repr__(self):
        return str(self)


    def __eq__(self, other):
        return self.isbn == other.isbn if self.isbn else False


    def __hash__(self):
        return hash(self.isbn) if self.isbn else 0
# end: Book


# Model class to store a module.
class Module:
    def __init__(self, cid, name, name_en, category, url, candidates, semester):
        self.cid = cid
        self.name = name
        self.name_en = name_en
        self.category = category
        self.url = url
        self.books = []
        self.candidates = candidates
        # WARNING: This has to be changed every season!
        self.last_offered = semester


    def __str__(self):
        return "Course-ID: %s; Name: %s; Books: %s" % (self.cid, self.name, str(self.books))


    def __repr__(self):
        return str(self);
# end: Module


# Class to retrieve the ISBN from a book title by accessing the Google API "books".
class IsbnMagic:
    def __init__(self, api_key):
        self.http_client = http.client.HTTPSConnection('www.googleapis.com')
        self.api_key = api_key

    def sanity_check(self, book_string, book):
        print(book.title)

        len_title = len(book.title)
        len_searchstring = len(book_string)

        valid = False
        diff = len_searchstring - len_title
        if diff >= 0:
            for i in range(0, floor(diff / SANITY_CHECK_STEPWIDTH)):
                index = SANITY_CHECK_STEPWIDTH * i
                test = book_string[index: index + len_title]
                ratio = distance(test, book.title) / len_title
                if ratio < 0.7:
                    valid = True
                    break
        if not valid:
            return False

        #if not book.title in book_string:
        #    return False
        if book.title and book.author and book.isbn and book.publisher and book.year:
            return True
        print("Missing?")
        return False

    def retrieveAndSetData(self, book_string):
        print("\n" + book_string)
        isbn_reliability = 0
        if len(book_string) > ISBN_RELIABILITY_BOOKSTRING_LENGTH:
            isbn_reliability = min(int(ISBN_RELIABILITY_BASE_VALUE + len(book_string) * ISBN_RELIABILITY_BOOKSTRING_LENGTH_MULTIPLIER), ISBN_RELIABILITY_MAX_VALUE)
        path = GOOGLE_BOOKS_BASE_PATH + urlencode({
            'q': book_string,
            'key': self.api_key,
        })
        self.http_client.request('GET', path)
        response = self.http_client.getresponse()
        content = response.read().decode('UTF-8')
        data = JSONDecoder().decode(content)
        data = data.get('items', None) if data else None
        data = data[0] if data else None
        data = data.get('volumeInfo', None) if data else None

        if data:
            book = Book()
            for id_opt in data.get('industryIdentifiers', None):
                id_type = id_opt.get('type', None)
                if id_type == 'ISBN_13':
                    book.isbn = id_opt.get('identifier', None)
                    break
            book.title = data.get('title', None)
            book.author = ', '.join(data.get('authors', []))
            book.publisher = data.get('publisher', 'Unknown')
            book.year = data.get('publishedDate', '0').split('-')[0]
            book.isbn_reliability = isbn_reliability
            if self.sanity_check(book_string, book):
                return book
        return None
# end: IsbnMagic


# Class to access TUCaN and return the results as modules (see Module).
class Tucan:

    def __init__(self):
        self.categories = []

    def should_consider(self, book_string):
        if len(book_string) < 15:
            return False
        if TUCAN_CONSIDER_PATTERN.match(book_string):
            return False
        return True

    def retrieveModule(self, module_url, category, semester):
        browser = self._createBrowser()
        browser.open(TUCAN_URL + module_url)

        cidname_element = browser.select(TUCAN_MODULE_COURSE_IDNAME_SELECTOR)[0];
        cidname_match = TUCAN_MODULE_COURSE_IDNAME_PATTERN.match(cidname_element.text);
        cid = cidname_match.group(1);
        name = cidname_match.group(2);

        elements = browser.select("table:nth-of-type(1) td.tbdata > *")
        found = False
        elems = []
        for elem in elements:
            titles = elem.select("b")
            if len(titles) > 0:
                if found:
                    break
                else:
                    for tag in titles:
                        if tag.string.lower().startswith('literatur'):
                            found = True
            if found:
                elems.append(elem)

        # Flatten Elems:
        flat = False
        while not flat:
            flat = True
            new_elems = []
            for tag in elems:
                if hasattr(tag,'name') and tag.name:
                    new_elems += tag.contents
                    flat = False
                elif str(tag):
                    new_elems.append(tag)
            elems = new_elems

        # Check the remaining
        texts = []
        for tag in elems:
            tag = str(tag).strip()
            texts.append(tag)

        #information = browser.select(TUCAN_MODULE_INFORMATION_SELECTOR);
        #literature = None
        #for info in information:
        #    text = info.select(TUCAN_MODULE_INFORMATION_TYPE_SELECTOR)[0].text.lower()
        #    if text.startswith('literatur'):
        #        literature = info
        #        break

        module_url_en = module_url.replace('-N000000000000001', '-N000000000000002')
        browser.open(TUCAN_URL + module_url_en)

        cidname_element_en = browser.select(TUCAN_MODULE_COURSE_IDNAME_SELECTOR)[0];
        cidname_match_en = TUCAN_MODULE_COURSE_IDNAME_PATTERN.match(cidname_element_en.text);
        cid_en = cidname_match_en.group(1);
        name_en = cidname_match_en.group(2);

        print(name)
        print(name_en)

        candidates = []

        for text in texts:
            print(text)
            if self.should_consider(text):
                candidates.append(text)

        #if literature:
        #    # Only process if there is literature, of course.

        #   literature_content = TUCAN_MODULE_LITERATURE_CONTENT_PATTERN.sub(r'\2', str(literature).replace('\n', '').replace('\r', ''))
        #   next_book = None
        #   pause = False
        #   for char in literature_content:
        #       book = None
        #       if char == '<':
        #           if next_book:
        #               book_string = unescape(TUCAN_MODULE_COURSE_NAME_NORMALIZE_PATTERN.sub(r'\1', next_book))
        #               if self.should_consider(book_string):
        #                   candidates.append(book_string)
        #               next_book = None
        #           pause = True
        #       elif char == '>':
        #           pause = False
        #       elif not pause:
        #           next_book = next_book + char if next_book else char
        #   if next_book:
        #       book_string = unescape(TUCAN_MODULE_COURSE_NAME_NORMALIZE_PATTERN.sub(r'\1', next_book))
        #       if self.should_consider(book_string):
        #           candidates.append(book_string)

        print("")
        return Module(cid, name, name_en, category, module_url, candidates, semester)


    def retrieveModules(self, semester):
        print('Retrieving modules...')

        module_urls = tucan.retrieveModuleUrls()

        module_cids = []
        modules = {}
        i = 1
        for url, category in module_urls:
            try:
                print("Loading module %d/%d..." % (i, len(module_urls)))
                print(category)

                module = tucan.retrieveModule(url, category, semester)
                if module.cid in modules:
                    print("Skipping module %d/%d as it is a duplicate!" % (i, len(module_urls)))
                else:
                    modules[module.cid] = module

                print("Loaded module %d." % i)

                i += 1
                #if i > 5:
                #    break
            except:
                logging.warning("Failed to process module at <%s>! Error:" % url, exc_info = True)

        print("Retrieved %d modules." % len(modules))

        return modules.values()


    def retrieveModuleUrls(self):
        print('Retrieving module URLs...')

        browser = self._createBrowser();

        browser.follow_link(browser.select(TUCAN_CC_SELECTOR)[1])
        browser.follow_link(browser.select(TUCAN_DEPT_SELECTOR)[0])

        module_urls = self._retrieveModuleUrls(browser)

        print("Retrieved %d module URLs." % len(module_urls))

        return module_urls


    def _retrieveModuleUrls(self, browser):
        breadcrumbs = browser.select(TUCAN_BREADCRUMBS_SELECTOR)
        breadcrumb = ""
        #for crumb in breadcrumbs:
        crumb = breadcrumbs[-2]
        tag_text = str(crumb)
        text = TUCAN_LINK_NAME_PATTERN.match(tag_text)
        txt = unescape(text.group(2))
        breadcrumb += txt
        print(breadcrumb)
        self.categories.append(breadcrumb)
        links = [ (module['href'], breadcrumb) for module in browser.select(TUCAN_MODULE_SELECTOR) ]
        containers = browser.select(TUCAN_MODULE_CONTAINER_SELECTOR);
        for container in containers:
            if not 'Computational Engineering' in str(container):
                browser.follow_link(container)
                links += self._retrieveModuleUrls(browser)
                #browser.back()
        return links


    def _createBrowser(self):
        try:
            browser = RoboBrowser(parser = 'lxml')
            browser.open(TUCAN_STARTPAGE_URL)
            return browser
        except Exception:
            print("Could not create TUCaN browser. Exiting")
            exit(1)
# end: Tucan

##############
### SCRIPT ###
##############

if len(argv) < 3:
    print("Usage: python ./tucan-export.py <semester> <api-key>")
    exit(1)

semester = argv[1]
api_key = argv[2]

book_export_file = semester + "/books.csv"
module_export_file = semester + "/modules.csv"
category_export_file = semester + "/category.csv"

tucan = Tucan()
modules = tucan.retrieveModules(semester)
isbnMagic = IsbnMagic(api_key)
books = {}
i = 1
imax = len(modules)
count = 1
for module in modules:
    j = 1
    jmax = len(module.candidates)
    for candidate in module.candidates:
        print("Loading book %d/%d of module %d/%d..." % (j, jmax, i, imax))

        book = isbnMagic.retrieveAndSetData(candidate)
        if book:
            module.books.append(book.isbn)
            if book.isbn not in books:
                books[book.isbn] = book
                print("ADDED\n")
            else:
                print("DUPLICATE\n")
        else:
            print("IGNORED\n")

        j += 1
        count += 1

    i += 1
print("Retrieved %d books." % count)

with open(book_export_file, 'w') as file:
    writer = csv.writer(file, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
    writer.writerow(['isbn_13', 'title', 'author', 'price', 'publisher', 'year'])
    print('Writing books file...', end='')
    count = 0
    for book in books.values():
        count += 1
        writer.writerow([book.isbn, book.title, book.author, book.price, book.publisher, book.year])
    print(" Done! Wrote {} books.".format(count))

with open(module_export_file, 'w') as file:
    writer = csv.writer(file, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
    writer.writerow(['books', 'category__name_de', 'module_id', 'name_de', 'name_en', 'last_offered'])
    print('Writing modules file...')
    for module in modules:
        writer.writerow([', '.join(module.books), module.category, module.cid, module.name, module.name_en, module.last_offered])
    print(" Done!")

with open(category_export_file, 'w') as file:
    writer = csv.writer(file, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
    writer.writerow(['name_de'])
    print('Writing categories file...')
    for category in tucan.categories:
        writer.writerow([category,])
    print(" Done!")
