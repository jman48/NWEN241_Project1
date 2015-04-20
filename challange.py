from html.parser import HTMLParser
from urllib.parse import urlparse
import urllib.request
import os

downloaded_files = []  # Used to store things we download so that we do not download them again


def pywget(url, depth=25):
    """
    This function will download all files from the provided url and recursivelly download all links from the file at the specified url

    :param url: The url to get the root file from
    :param depth: The depth of recursive function before it should terminate
    :return:
    """

    print('\nProgram starting download from ' + url + '\n')

    # Get root file
    root_file = File(get_url_file_name(url), get_file_name(url, ''), url)
    download_file(root_file)
    downloaded_files.append(root_file)

    # Do not try and download links if file is not an html file
    if root_file.get_extension() == 'html' or root_file.get_extension() == 'htm':
        download_links(root_file, depth)
        print('\nAll done :)')


def download_links(root_file, depth=0):
    """
    Download all the links in the provided file if they are from the same domain as the rootfile provided

    :param root_file: The root file to download all the links from
    :param depth: The recursive depth to go to until the function should stop
    :return:
    """

    if depth < 0:
        return
    downloaded_files.append(root_file.filename)

    html_files = []  # all html file that need links downloaded
    html_parser = get_linked_files(root_file)

    for index, link in enumerate(html_parser.links):
        if get_url_file_name(link[1]) in downloaded_files:
            continue  # if we already downloaded this file then just skip it

        link_url_parse = urlparse(link[1])
        link_file = File(get_url_file_name(link[1]),
                         get_file_name(link[1], root_file.get_directory()),
                         get_url_location(link[1], root_file.url), link[0])

        # Add the file to the list so we do not download them again
        downloaded_files.append(get_url_file_name(link[1]))

        if link_url_parse.netloc == '':
            # If the link is relative then get the path to the link from the root url
            download_file(link_file)
            update_root_file_link(root_file, link_file, html_parser.positions[index])
        elif link_url_parse.netloc == urlparse(root_file.url).netloc:
            download_file(link_file)
            update_root_file_link(root_file, link_file, html_parser.positions[index])
        if link_file.get_extension() == 'html':
            html_files.append(link_file)

    for html_file in html_files:
        download_links(html_file, depth - 1)


def update_root_file_link(root_file, link_file, pos, ):
    """
    Update the link at pos to use the link filename.

    :param root_file: The root file to update all the links in
    :param link_file: The file that needs its link updated in root
    :param pos: The position of the html tag that contains the link to update.
    :return:
    """

    root_file_stream = open(root_file.file_location, 'r')
    root_file_data = root_file_stream.readlines()
    root_file_stream.close()

    line = pos[0] - 1
    line_offset = pos[1]

    tag = root_file_data[line][line_offset:]  # get the tag based on its line number and line offset
    link_start = tag.find(link_file.file_type + '="')  # Find either src=" or href=" in the tag
    index_start = tag.find('"', link_start)  # start our update after the opening double quotes for the link
    index_end = tag.find('"', index_start + 1) + 1  # end our update at the end double quotes

    updated_link = insert(index_start, index_end, tag, link_file.get_relative_dir(root_file.get_directory()))
    root_file_data[line] = root_file_data[line].replace(tag, updated_link, 1)

    # write all the updated data back to the original file
    root_file_stream = open(root_file.file_location, 'w')
    root_file_stream.writelines(root_file_data)
    root_file_stream.close()


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


def get_path(url, file_name):
    """
    Returns the full url minus the file name. Makes it easy to get other files in the same directory

    :param url: The url of the file
    :param file_name: The url filename. This should not be the collision renamed filename. i.e not cat.0.jpg
    :return:
    """

    index = url.find(file_name)
    return url[:index]


def get_linked_files(file):
    """
    Get all files that are linked from the file specified

    :param file: The file to get all links from
    :return: An html parser with the links stored in 'links' and position of each link stored in 'positions' with both same index
    """
    file = open(file.file_location, 'r')
    file_contents = file.read()
    file.close()

    h = HTMLlinks()
    h.feed(file_contents)
    return h


def download_file(file):
    """
    Download a file to disk. Will make sure that the downloaded file name is unique.

    :param file: The file to download. Will download from file.url to file.location
    :return:
    """
    print('File ' + file.file_location + ' downloading....')
    try:
        if not os.path.exists(file.get_directory()):
            os.makedirs(file.get_directory())

        urllib.request.urlretrieve(file.url, file.file_location)
        print('File downloaded!')
    except:
        print('Network error downloading from "' + file.url + '". Please try again')


def get_file_name(url, cd):
    """
    This function gets the file name for the url that will be saved to disk.

    This may involve adding a number to the file name if there exists a file with
    the same name

    :param url: The url of the file
    :return: The file name
    """
    filename = get_file_location(url, cd)
    if os.path.exists(filename):
        filename = add_prefix_num(filename, 0)
    return filename


def get_file_location(file_link, cd):
    """
    Return a files local file system location

    :param file_link: The url of the file
    :param cd: The current directory to download files to
    :return: A string file location for the local file system
    """

    url_obj = urlparse(file_link)
    file_location = url_obj.netloc + url_obj.path

    # if relative path
    if url_obj.netloc == '':
        file_location = cd + url_obj.path

    return file_location


def get_url_location(filename, url_base):
    """
    This will return the files url. This will add protocol and domain if not already added

    :param filename: the name of the file
    :param url_base: the current directory.
    :return: the url for the file
    """
    url_obj = urlparse(filename)

    # if it is just the file name then attach the cd
    if url_obj.scheme == '':
        return urllib.parse.urljoin(url_base, filename)

    return filename


def get_url_file_name(url):
    """
    This function gets the filename from the url provided.

    :param url: The url of the file
    """
    sections = url.split('/')
    if sections[len(sections) - 1].find('.') > -1:
        return urlparse(sections[len(sections) - 1]).path


def add_prefix_num(file_location, times):
    """
    Recursively add a number before the files extension until it is unique

    :param file_location: The location of the file to add prefix to. This must include the files name
    :param times: The prefix number to add before the files extension
    :return:
    """

    prefix_name = get_prefix_name(file_location, times)
    if os.path.exists(prefix_name):
        return add_prefix_num(file_location, times + 1)
    return prefix_name


def get_prefix_name(file_name, prefix):
    """
    This function will return the filename with the prefix added before the files extension

    :param file_name: The file name to add prefix to
    :param prefix: The prefix to add
    :return:
    """

    index = len(file_name) - 1

    # loop backwards until we find '.' this is then the start of the files extension
    while index > 0:
        if file_name[index] == '.':
            return file_name[:index] + '.' + str(prefix) + file_name[index:]
        index -= 1


class File:
    def __init__(self, filename, file_location, url, file_type=''):
        self.filename = filename
        self.file_location = file_location
        self.url = url
        self.file_type = file_type

    def get_extension(self):
        """
        Get the files extension
        """
        sections = self.file_location.split('.')
        return sections[len(sections) - 1]

    def get_directory(self):
        """
        Get the files directory
        """
        index = self.file_location.find(get_url_file_name(self.file_location))
        return self.file_location[:index]

    def get_relative_dir(self, cd):
        index = self.file_location.find(cd)
        return self.file_location[index + len(cd):]


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