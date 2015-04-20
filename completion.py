"""

Created by John Armstrong
 for NWEN241 2015

"""

from html.parser import HTMLParser
from urllib.parse import urlparse
import urllib.request
import os


def pywget(url):
    """
    This function will download the file from the url specified and all files that are linked from that file

    :param url: The url of the root file to download and get all files linked in it
    :return:
    """
    print('\nProgram starting download from ' + url + '\n')

    # Get root file
    root_file_name = get_file_name(url)
    download_file(url, root_file_name)
    urlparse(url)

    # Do not try and download links if file is not an html file
    if get_extension(root_file_name) == 'html' or get_extension(root_file_name) == 'htm':
        download_links(root_file_name, url)
        print('\nAll done :)')


def download_links(root_file_name, url):
    """
    Download all the links in the provided file if they are from the same domain as the url provided

    :param root_file_name: The name of the root html file to download the links from
    :param url: The url of the root html file. Used to check if links are from the same domain
    :return:
    """

    root_url = urlparse(url)
    html_parser = get_linked_files(root_file_name)

    for index, link in enumerate(html_parser.links):
        link_type = link[0]
        link_url = link[1]

        if not same_domain(root_url.geturl(), link_url):
            continue

        link_url_obj = urlparse(link_url)
        link_file_name = get_file_name(link_url)

        if link_url_obj.netloc == '':
            # If the link is relative then get the path to the link from the root url
            path = get_path(url, get_url_file_name(url)) + link_url_obj.path
            download_file(path, link_file_name)
        elif link_url_obj.netloc == root_url.netloc:
            download_file(link_url_obj.geturl(), link_file_name)

        update_root_link(root_file_name, link_type, link_file_name, html_parser.positions[index])


def same_domain(url, link):
    """
    Check if the link is in the same domain as the url

    :param url: The url containing the domain to check against
    :param link: The link to check if in same domain
    :return: boolean whether the link is in the same domain as url
    """
    url_obj = urlparse(url)
    link_obj = urlparse(link)

    return link_obj.netloc == '' or link_obj.netloc == url_obj.netloc


def update_root_link(root_file_name, link_type, link_file_name, pos):
    """
    Update the link at pos to use the link filename.

    :param root_file_name: The name of the root html file containing the link
    :param link_type: The type of link. Either 'src' or 'href'
    :param link_file_name: The name of the local file to update link to
    :param pos: The position of the html tag that contains the link to update.
    :return:
    """

    # read the root file
    root_file = open(root_file_name, 'r')
    root_data = root_file.readlines()
    root_file.close()

    line = pos[0] - 1  # the line containing the link
    line_offset = pos[1]  # the offset from the beginning of the line
    tag = root_data[line][line_offset:]  # get the html tag
    link_start = tag.find(link_type + '="')  # Find either src=" or href=" in the tag
    index_start = tag.find('"', link_start)  # start our update after the opening double quotes for the link
    index_end = tag.find('"', index_start + 1) + 1  # end our update at the end double quotes
    updated_link = insert(index_start, index_end, tag, link_file_name)
    root_data[line] = root_data[line].replace(tag, updated_link, 1)  # replace the old tag with the updated links

    # write all the updated links back to the original file
    root_file = open(root_file_name, 'w')
    root_file.writelines(root_data)
    root_file.close()


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


def get_linked_files(file_name):
    """
    Get all files that are linked from the file specified

    :param file_name: The file name to get all the <a> and <img> links from
    :return: An htmlparser with the links stored in 'links'
    """
    file = open(file_name, 'r')
    h = HtmlLinks()
    h.feed(file.read())
    file.close()
    return h


def download_file(url, file_name):
    """
    Download a file to disk. Will make sure that the downloaded file name is unique.
    :param url: The url of the file to download
    :param file_name: What to name the downloaded file
    :return:
    """
    print('File ' + file_name + ' downloading....')
    try:
        urllib.request.urlretrieve(url, file_name)
        print('File downloaded!\n')
    except:
        print('Network error downloading from "' + url + '". Please try again')


def get_file_name(url):
    """
    This function gets the file name for the url that will be saved to disk.

    This may involve adding a number to the file name if there exists a file with
    the same name

    :param url: The url of the file
    :return: The file name
    """
    file_name = get_url_file_name(url)
    if os.path.exists(file_name):
        file_name = add_prefix_num(file_name, 0)
    return file_name


def get_url_file_name(url):
    """
    This function gets the filename from the url provided.

    If no file name is specified then it returns index.html as the file name

    :param url:
    """
    sections = url.split('/')
    if sections[len(sections) - 1].find('.') > -1:
        return sections[len(sections) - 1]


def add_prefix_num(file_name, times):
    """
    This recursive function will add a number to the file name so that is is unique. i.e index.1.html

    :param file_name: The name of the file from the url
    :param times: The prefix number to add
    :return: A unique file name for the local file system
    """

    if os.path.exists(get_prefixed_name(file_name, times)):
        return add_prefix_num(file_name, times + 1)
    return get_prefixed_name(file_name, times)


def get_prefixed_name(file_name, prefix):
    """
    This function will return the filename with the prefix added before the files extension

    :param file_name: The file name to add the prefix to
    :param prefix: The prefix to add
    :return: The filename with the prefix added before the file extension
    """

    index = len(file_name) - 1

    # loop backwards until we find the first '.' this is where the file extension starts
    while index > 0:
        if file_name[index] == '.':
            return file_name[:index] + '.' + str(prefix) + file_name[index:]
        index -= 1


def get_extension(file_name):
    """
    Get the extensino from the file name provided

    :param file_name: The file name to get the extension from
    :return: The files extension
    """
    sections = file_name.split('.')
    return sections[len(sections) - 1]


class HtmlLinks(HTMLParser):
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