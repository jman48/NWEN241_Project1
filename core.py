import urllib.request
import os

def pywget(url):
    fileName = getFileName(url)
    print('File ' + fileName + ' downloading....')
    try:
        fileInput = urllib.request.urlretrieve(url, fileName)
        print('File downloaded!')
    except:
        print('Network error. Please try again')

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
    This function will add a number to the file name so that is is unique. i.e index.1.html
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
    
            
    
