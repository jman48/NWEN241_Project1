"""

Created by John Armstrong
 for NWEN241 2015

"""
import urllib.request
import os


def pywget(url):
    """
    Downloads the file from the url and any file referenced in it

    :param url: The url of the file to download
    :return:
    """

    filename = get_file_name(url)
    print('File ' + filename + ' downloading....')
    try:
        urllib.request.urlretrieve(url, filename)
        print('File downloaded!')
    except:
        print('Network error. Please try again')


def get_file_name(url):
    """
    This function gets the file name for the url that will be saved to disk.

    This may involve adding a number to the file name if there exists a file with
    the same name

    :param url: The url of the file
    :return: A unique file name for the local file system
    """

    filename = get_url_file_name(url)
    if os.path.exists(filename):
        filename = add_prefix_num(filename, 0)
    return filename


def get_url_file_name(url):
    """
    This function gets the filename from the url provided.

    If no file name is specified then it returns index.html as the file name

    :param url: The url of the file
    :return: The name of the file from the url
    """

    last_index = 0
    file_name_defined = False

    # find last '/'
    index = len(url) - 1

    # loop backwards over the url until we find the first '/'. This indicates the start index of the file name
    while index > 0:
        if url[index] == '/':
            last_index = index + 1  # Plus 1 so we exclude the '/'
            break
        # If we do not find a '.' before the '/' then the file name must not be defined.
        if url[index] == '.':
            file_name_defined = True
        index -= 1

    # Return the filename or index.html if the file name is not defined
    if file_name_defined:
        return url[last_index:]
    return 'index.html'


def add_prefix_num(filename, times):
    """
    This recursive function will add a number to the file name so that is is unique. i.e index.1.html

    :param filename: The name of the file from the url
    :param times: The prefix number to add
    :return: A unique file name for the local file system
    """

    if os.path.exists(get_prefixed_name(filename, times)):
        return add_prefix_num(filename, times + 1)
    return get_prefixed_name(filename, times)


def get_prefixed_name(filename, prefix):
    """
    This function will return the filename with the prefix added before the files extension

    :param filename: The file name to add the prefix to
    :param prefix: The prefix to add
    :return: The filename with the prefix added before the file extension
    """

    index = len(filename) - 1

    # loop backwards until we find the first '.' this is where the file extension starts
    while index > 0:
        if filename[index] == '.':
            return filename[:index] + '.' + str(prefix) + filename[index:]
        index -= 1