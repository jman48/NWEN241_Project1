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
    fileName = getUrlFileName(url)
    if (os.path.exists(urlFileName)):
        fileName = addPrefixNum(fileName)
    return fileName

def getUrlFileName(url):
    lastIndex = 0
    fileNameDefined = False
    
    #find last '/'
    index = len(url) - 1
    
    while index > 0:
        if (url[index] == '/'):
            lastIndex = index + 1 #Plus 1 so we exclude the '/'
            break
        if (url[index] == '.'): #If we do not find a '.' before the '/' the the file name must not be defined
            fileNameDefined = True
        index = index - 1
        
    if (fileNameDefined):
        return url[lastIndex:]
    return 'index.html'

def addPrefixNum(fileName):
    
            
    
