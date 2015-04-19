from html.parser import HTMLParser
from urllib.parse import urlparse
import urllib.request
import os

files = []


def pywget(url, depth=2):
    # create root path

    # urlobj = urlparse(getPath(url, getUrlFileName(url)))
    # urldir = urlobj.netloc + urlobj.path
    # print(urldir)
    #
    # # create main directory
    # if not os.path.exists(urldir):
    #     os.makedirs(urldir)

    downloadroot(url, 2)


def downloadroot(url, depth, cd=''):
    if depth < 0 or url in files:
        return

    # Get root file
    rootfile = File(getFileName(url), getfilelocation(url, cd), url)
    downLoadFile(rootfile)
    files.append(rootfile)

    # Do not try and download links if file is not an html file
    if rootfile.getextension() == 'html' or rootfile.getextension() == 'htm':
        downloadlinks(rootfile, depth)


def downloadlinks(rootfile, depth=0):
    """
    Download all the links in the provided file if they are from the same domain as the url provided

    :param rootfilename: The name of the root html file to download the links from
    :param url: The url of the root html file. Used to check if links are from the same domain
    :return:
    """
    htmlParser = getLinkedFiles(rootfile)
    for index, link in enumerate(htmlParser.links):
        linkurlparse = urlparse(link[1])
        linkfile = File(getFileName(rootfile.url), getfilelocation(link[1], rootfile.getdirectory()),
                        geturllocation(link[1], rootfile.url), link[0])

        if linkurlparse.netloc == '':
            # If the link is relative then get the path to the link from the root url
            downLoadFile(linkfile)
            updaterootfilelink(rootfile, linkfile.filetype, linkfile.filename, htmlParser.positions[index])
        elif linkurlparse.netloc == urlparse(rootfile.url).netloc:
            downLoadFile(linkfile)
            updaterootfilelink(rootfile, linkfile.filetype, linkfile.filename, htmlParser.positions[index])

        if linkfile.getextension() == 'html':
            downloadlinks(linkfile, depth - 1)


def updaterootfilelink(rootfile, linkType, linkFileName, pos,):
    """
    Update the link at pos to use the linkfilename.

    :param rootFileName: The name of the root html file containing the link
    :param linkType: The type of link. Either 'src' or 'href'
    :param linkFileName: The name of the local file to update link to
    :param pos: The position of the html tag that contains the link to update. pos[0] = line of link. pos[1] = line offset of link
    :return:
    """
    rootFile = open(rootfile.filelocation, 'r')
    rootData = rootFile.readlines()
    rootFile.close()

    line = pos[0] - 1
    tag = rootData[line][pos[1]:]  # pos[0] contains line number. pos[1] contains line offset
    linkStart = tag.find(linkType + '="')  # Find either src=" or href=" in the tag
    indexStart = tag.find('"', linkStart)
    indexEnd = tag.find('"', indexStart + 1) + 1
    rootData[line] = rootData[line].replace(tag, insert(indexStart, indexEnd, tag, linkFileName), 1)

    rootFile = open(rootfile.filelocation, 'w')
    rootFile.writelines(rootData)
    rootFile.close()


def insert(start, end, text, new):
    """
    Insert the string 'new' into the text based on the start and end indexes

    :param start: Where to start the text insertion
    :param end: Where to end the text insertion
    :param text: The text to insert the new text into
    :param new: The text to insert
    :return:
    """
    return text[:start] + new + text[end:]


def getPath(url, fileName):
    """
    Returns the full url minus the file name. Makes it easy to get other files in the same directory

    :param url: The url of the file
    :param fileName: The url filename. This should not be the collision renamed filename. i.e not cat.0.jpg
    :return:
    """
    index = url.find(fileName)
    return url[:index]


def getLinkedFiles(file, cd=''):
    """
    Get all files that are linked from the file specified

    :param fileName: The file name to get all the <a> and <img> links from
    :return: An htmlparser with the links stored in 'links'
    """
    file = open(file.filelocation, 'r')
    filecontent = file.read()
    file.close()

    h = HTMLlinks()
    h.feed(filecontent)
    return h


def downLoadFile(file):
    """
    Download a file to disk. Will make sure that the downloaded file name is unique.
    :param url: The url of the file to download
    :param fileName: What to name the downloaded file
    :return:
    """
    print('File ' + file.filelocation + ' downloading....')
    try:
        urllib.request.urlretrieve(file.url, file.filelocation)
        print('File downloaded!')
    except:
        print('Network error downloading from "' + file.url + '". Please try again')


def getFileName(url):
    """
    This function gets the file name for the url that will be saved to disk.

    This may involve adding a number to the file name if there exists a file with
    the same name

    :param url: The url of the file
    :return: The file name
    """
    fileName = geturlfilename(url)
    if os.path.exists(fileName):
        fileName = addprefixnum(fileName, 0)
    return fileName


def getfilelocation(filelink, cd):
    urlobj = urlparse(filelink)

    # if relative path
    if urlobj.netloc == '':
        urlobj = urlparse(cd + urlobj.path)

    return urlobj.netloc + urlobj.path


def geturllocation(filename, urlbase):
    """
    This will return the files url. This will add protocal and domain if not already added

    :param filename: the name of the file
    :param cd: the current directory.
    :return: the url for the file
    """
    urlobj = urlparse(filename)

    # if it is just the file name then attach the cd
    if urlobj.netloc == '':
        return urlbase + filename

    return filename


def geturlfilename(url):
    """
    This function gets the filename from the url provided.

    If no file name is specified then it returns index.html as the file name

    :param url:
    """
    sections = url.split('/')
    if sections[len(sections) - 1].find('.') > -1:
        return urlparse(sections[len(sections) - 1]).path
    return ''


def addprefixnum(fileName, times):
    """
    Recursively add a number before the files extension until it is unique
    """
    if os.path.exists(getprefixname(fileName, times)):
        return addprefixnum(fileName, times + 1)
    return getprefixname(fileName, times)


def getprefixname(fileName, prefix):
    """
    This function will return the filename with the prefix added before the files extension
    """

    index = len(fileName) - 1
    while index > 0:
        if fileName[index] == '.':
            return fileName[:index] + '.' + str(prefix) + fileName[index:]
        index -= 1


class File:
    def __init__(self, filename, filelocation, url, filetype=''):
        self.filename = filename
        self.filelocation = filelocation
        self.url = url
        self.filetype = filetype

    def getextension(self):
        sections = self.filelocation.split('.')
        return sections[len(sections) - 1]

    def getdirectory(self):
        index = self.filelocation.find(self.filename)
        return self.filelocation[:index]


class HTMLlinks(HTMLParser):
    """
    A custom html parser class to get and store all links in an html document
    """

    def __init__(self):
        HTMLParser.__init__(self)
        self.links = []
        self.positions = []

    def handle_starttag(self, tag, attrs):
        """ Get all links from an html document """

        # Get all href values from an 'a' tag
        if tag == 'a' and attrs[0][0] == 'href':
            self.positions.append(self.getpos())
            self.links.append(attrs[0])
        # Get all src values from all 'img' tags
        elif tag == 'img' and attrs[0][0] == 'src':
            self.positions.append(self.getpos())
            self.links.append(attrs[0])


pywget('http://homepages.ecs.vuw.ac.nz/~ian/nwen241/index.html')