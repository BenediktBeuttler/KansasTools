# -*- coding: utf-8 -*-
"""
Created on Tue Aug 15 10:20:51 2023

@author: henni
"""

from ast import If
from fileinput import filename
from bs4 import BeautifulSoup
import requests
import codecs
import re

basePath = "dasBiber"
metaFileName = basePath + "/dasBiber.csv"
baseBiberUrl = "https://www.dasbiber.at"
processedTextsFile = basePath + "/processed-biber-files.txt"
logs = basePath + "/logs.txt"
biberLizenz = "?"
encoding = "utf-8"

#method. takes plain text as argument. 
# Passes it to method which writes file and needs 
# 3 arguments: logs - path where to safe, a - append mode, encoding - utf-8 
# as f: can access opening method via f
# yes, use in BIBER
def logIt(text):
    with codecs.open(logs, 'a', encoding) as f:
            f.write(text + "\n")
            f.close()
    print(text)


# modify and add to BIBER 
# 5 different topics. For each topic get URLs
# yes, the same principle for BIBER. But where does the index actually increase?
def getNewsUrl(index):
    if index == 0:
        newsUrl = "https://www.dasbiber.at/bereich/3-minuten-mit"
        return newsUrl
    else:
        newsUrl = "https://www.dasbiber.at/bereich/3-minuten-mit?page="
        return newsUrl + str(index)
    
    
# save raw text file
def saveFile(fileName, text):
    # create and write file which contains text. 
    # add the file name to logit overview sheet. 
    with codecs.open(basePath+"\\txts\\"+fileName, 'w', encoding) as f:
        # write to file whatever is saved in {text}.
        f.write(f'{text}')
        f.close()

    logIt("created -- " + fileName)
    
    # where is processedTexts created?
    # if article heading not yet in file, add. 
    # overview of each processed article 
    if fileName not in processedTexts:
        with codecs.open(processedTextsFile, 'a', encoding) as f:
            f.write(f'{fileName}\n')
            f.close()
            
            

def addToMetaFile(fileName, url, title, org, orgLink):
    if fileName in processedTexts:
        logIt("already exists in Meta: " + fileName)
        return

    # append entry to meta collection
    with codecs.open(metaFileName, 'a', encoding) as f:
        f.write(f'\n{fileName};{title};;;{url};{fluterLizenz};;{org};{orgLink}')
        f.close()

    logIt(str("added to Meta - " + title))



def crawlNewsPage(textUrl):
    r = requests.get(textUrl)
    data = r.text
    soup = BeautifulSoup(data, features="html.parser")

    

# the h1 tag of class node-title contains the title
    title = soup.find('h1', id='page-title', class_='node-title')
    title = title.get_text()  # Extract the text content
    print(title)

# tag showdate contains date
    datum = soup.find('showdate',
                      class_='article node node-article node-promoted node-lange-de node-odd node-full clearfix')
    datum = datum.get_text() # Extract the date content
    print(datum)
    
    # tag 'link' has two attributes. Only get the link where first attribute is 'canonical' and please get the content of second attribute, namely href
    relative_link = soup.find('link', 'rel=canonical',)
    
    # get text
    # the div 'field-item odd' contains all text. 
    # I wonder if mistakes will happen if I search for 'field-item odd' as there might be more than one 
    # diff. approach: the third child of <div class = "node-content">, (-> namely the field item odd tag) contains all the text
    text = soup.find("div", {"class": "field-item odd"})
    # or 
    parent = soup.find("div", {"class": "node-content"})
    # get inner child <p>.get_text() get inner child <strong>.get_text()
    # omit other div elements
    # omit &nspb content
    # omit <p> *bezahlte Anzeige* </p>
        

    # get text
   
           

    saveFile(fileName, text)
    addToMetaFile(fileName, textUrl, title, org, orgLink)
    # print("")
    # print(text)
    # print(fileName)
    # print(textUrl, title, org, orgLink)
    # print("------------------------------------")

# clear log    
with codecs.open(logs, 'w', encoding) as f:
            f.write("")
            f.close()
