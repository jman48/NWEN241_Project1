from html.parser import HTMLParser
from urllib.parse import urlparse
import urllib.request
import os

def pywget(url):
    #Get root file
    rootFileName = getFileName(url)
    downLoadFile(url, rootFileName)
    rootUrl = urlparse(url)
    
    htmlParser = getLinkedFiles(rootFileName)
    for index, link in enumerate(htmlParser.links):
        #print(htmlParser.positions[index])
        linkUrl = urlparse(link[1])
        linkFileName = getFileName(link[1])        

        if (linkUrl.netloc == ''):
            #If the link is relative then get the path to the link from the root url
            downLoadFile(getPath(url, getUrlFileName(url)) + linkUrl.path, linkFileName)
            updateRootLink(rootFileName, link[0], linkFileName, htmlParser.positions[index])
        elif (linkUrl.netloc == rootUrl.netloc):
            downLoadFile(linkUrl.geturl(), linkFileName)
            updateRootLink(rootFileName, link[0], linkFileName, htmlParser.positions[index])
    """ Update reference in root file """

def updateRootLink(rootFileName, linkType, linkFileName, pos):
    rootFile = open(rootFileName, 'r')
    rootData = rootFile.readlines()
    rootFile.close()

    line = pos[0] - 1
    tag = rootData[line][pos[1]:] #pos[0] contains line number. pos[1] contains line offset
    linkStart = tag.find(linkType + '="')  #Find either src=" or href=" in the tag
    indexStart = tag.find('"', linkStart)
    indexEnd = tag.find('"', indexStart + 1) + 1
    rootData[line] = rootData[line].replace(tag, overWriteLink(indexStart, indexEnd, tag, linkFileName), 1)
    print(rootData[line])
    
    rootFile = open(rootFileName, 'w')
    rootFile.writelines(rootData)
    rootFile.close()

def overWriteLink(start, end, text, new):
    return text[:start] + new + text[end:]
    
def getPath(url, fileName):
    """ Returns the full url minus the file name. Makes it easy to get other files in the same directory"""
    index = url.find(fileName)
    return url[:index]

def getLinkedFiles(fileName):
    """ Get all files that are linked from the file specified """
    file = open(fileName, 'r')
    h = HTMLlinks()
    h.feed(file.read())
    file.close()
    return h
        

def downLoadFile(url, fileName):
    """
    Download a file to disk. Will nmake sure that the downloaded files name
    is unique. returns the file input stream
    """
    print('File ' + fileName + ' downloading....')
    try:
        urllib.request.urlretrieve(url, fileName)
        print('File downloaded!')
    except:
        print('Network error downloading from "' + url + '". Please try again')

def getFileName(url):
    """
    This function gets the file name for the url that will be saved to disk.
    
    This may involve adding a number to the file name if there exists a file with
    the same name
    """
    fileName = getUrlFileName(url)
    if (os.path.exists(fileName)):
        fileName = addPrefixNum(fileName, 0)
    return fileName

def getUrlFileName(url):
    """
    This function gets the filename from the url provided.

    If no file name is specified then it returns index.html as the file name
    """
    lastIndex = 0
    fileNameDefined = False
    
    #find last '/'
    index = len(url) - 1
    
    while index > 0:
        if (url[index] == '/'):
            lastIndex = index + 1 #Plus 1 so we exclude the '/'
            break
        #If we do not find a '.' before the '/' then the file name must not be defined
        if (url[index] == '.'): 
            fileNameDefined = True
        index = index - 1

    #Return the filename or index.html if the file name is not defined
    if (fileNameDefined):
        return url[lastIndex:]
    return 'index.html'

def addPrefixNum(fileName, times):
    """
    This recursive function will add a number to the file name so that is is unique. i.e index.1.html
    """
    if (os.path.exists(getPrefixedName(fileName, times))):
        return addPrefixNum(fileName, times+1)
    return getPrefixedName(fileName, times);

def getPrefixedName(fileName, prefix):
    """
    This function will return the filename with the prefix added before the files extension
    """

    index = len(fileName) - 1;
    while (index > 0):
        if (fileName[index] == '.'):
            return fileName[:index] + '.' + str(prefix) + fileName[index:]
        index = index-1
    #Do something as we did not find the file extension

class HTMLlinks(HTMLParser):
    """ A custom html parser class to get and store all links in an html ducument """
    def __init__(self):
        HTMLParser.__init__(self)
        self.links = []
        self.positions = []
        
    def handle_starttag(self, tag, attrs):
        """ Get all links from an html document """
        
        #Get all href values from an 'a' tag
        if(tag == 'a' and attrs[0][0] =='href'):
            self.positions.append(self.getpos())
            self.links.append(attrs[0])
        #Get all src values from all 'img' tags
        elif(tag == 'img' and attrs[0][0] =='src'):
            self.positions.append(self.getpos())
            self.links.append(attrs[0])
