__author__ = 'Raf'
class NavObject:
    def __init__(self, href, text):
        self.href = href
        self.text = text

    def setmultilevel(self, navObjects):
        self.navObjects = navObjects

    def setIcon(self, icon):
        self.icon = icon


    def printNav(self):
        """"glazed with {} water beside the {} chickens".format("rain", "white")"""


    def getmultilevelHTML(self):
        """for nav in range(len(self.navObjects)):
            if hasattr(nav, 'navObjects'):

            else:"""


