from robobrowser import RoboBrowser
import math

TUCAN_URL = 'https://www.tucan.tu-darmstadt.de'
TUCAN_STARTPAGE_URL = "%s/scripts/mgrqcgi?APPNAME=CampusNet&PRGNAME=EXTERNALPAGES&ARGUMENTS=-N2,-N,-Awelcome" % TUCAN_URL
TUCAN_CC_SELECTOR = '#pageTopNavi ul a'
TUCAN_DEPT_SELECTOR = '#auditRegistration_list li[title="Dept. 20 - Computer Science"] a'
TUCAN_MODULE_CONTAINER_SELECTOR = '#auditRegistration_list li a'
TUCAN_MODULE_SELECTOR = '.eventTable td a'
TUCAN_MODULE_INFORMATION_SELECTOR = '#contentlayoutleft table:nth-of-type(1) tr:nth-of-type(2) p'

class Tucan:
    def retrieveModule(self, module_url):
        browser = self._createBrowser()
        browser.open(TUCAN_URL + module_url)

        information = browser.select(TUCAN_MODULE_INFORMATION_SELECTOR);
        literature = information[-1]

        print(literature.text)


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
        browser = RoboBrowser()
        browser.open(TUCAN_STARTPAGE_URL)
        return browser


tucan = Tucan()
#modules = tucan.retrieveModuleUrls();
print(tucan.retrieveModule('/scripts/mgrqcgi?APPNAME=CampusNet&PRGNAME=COURSEDETAILS&ARGUMENTS=-N000000000000002,-N000036,-N0,-N360743780025317,-N360743780096318,-N0,-N0,-N0'));
