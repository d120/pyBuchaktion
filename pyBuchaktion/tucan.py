from robobrowser import RoboBrowser
from threading   import Thread
import logging
import math
import re
import time
import sys

# URLs
TUCAN_URL = 'https://www.tucan.tu-darmstadt.de'
TUCAN_STARTPAGE_URL = "%s/scripts/mgrqcgi?APPNAME=CampusNet&PRGNAME=EXTERNALPAGES&ARGUMENTS=-N2,-N,-Awelcome" % TUCAN_URL
# CSS Selectors
TUCAN_CC_SELECTOR = '#pageTopNavi ul a'
TUCAN_DEPT_SELECTOR = '#auditRegistration_list li[title="Dept. 20 - Computer Science"] a'
TUCAN_MODULE_CONTAINER_SELECTOR = '#auditRegistration_list li a'
TUCAN_MODULE_COURSE_IDNAME_SELECTOR = '#pageContent form h1';
TUCAN_MODULE_INFORMATION_SELECTOR = '#contentlayoutleft table:nth-of-type(1) tr:nth-of-type(2) p'
TUCAN_MODULE_INFORMATION_TYPE_SELECTOR = 'b:nth-of-type(1)'
TUCAN_MODULE_SELECTOR = '.eventTable td a'
# RegEx Patterns
TUCAN_MODULE_COURSE_IDNAME_PATTERN = re.compile(r'^\s*(\w{2,2}-\w{2,2}-\w{4,4}-\w{2,2})\s*(.+?)\s*$');
TUCAN_MODULE_LITERATURE_CONTENT_PATTERN = re.compile(r'^\s*<p><b>(.*?)</b>(.*)</p>\s*$');


class ModuleRequestThread(Thread):
    def __init__(self, tucan):
        super().__init__()

        self.tucan = tucan
        self.finished = False
        self.processed_entries = 0
        # do not divide by zero
        self.total_entries = -1
        self.modules = None


    def run(self):
        self.processed_entries = 0
        self.module_urls = tucan.retrieveModuleUrls()
        self.total_entries = len(self.module_urls)

        modules = []
        for url in self.module_urls:
            modules.append(tucan.retrieveModule(url))
            self.processed_entries += 1
        self.modules = modules
        self.finished = True


    def get_percentage(self):
        return (self.processed_entries / self.total_entries) * 100



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
                if char == '<':
                    if next_book:
                        books.append(next_book)
                        next_book = None
                    pause = True
                elif char == '>':
                    pause = False
                elif not pause and (next_book or (char != '-' and char != ':' and char != ' ' and char != '\t')):
                    next_book = next_book + char if next_book else char
            if next_book:
                books.append(next_book)

        return Module(cid, name, module_url, books)


    def retrieveModules(self):
        thread = ModuleRequestThread(self)
        thread.start()
        return thread


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



tucan = Tucan()
thread = tucan.retrieveModules()
while not thread.finished:
    print("Processed entries: %d/%d; %.2f%%" % (thread.processed_entries, thread.total_entries, thread.get_percentage()))
    time.sleep(10)
print(thread.modules)
