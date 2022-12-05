from ast import If
from fileinput import filename
from bs4 import BeautifulSoup
import os
import requests
import json
import codecs
import re

baseURL = "hurrakiCrawler"
metaFileName = baseURL + "/hurrakimeta.csv"
baseHurrakiUrl = "https://hurraki.de"
baseWikiUrl = "https://hurraki.de/wiki/Hurraki:Artikel_von_A_bis_Z"
processedTextsFile = baseURL + "/processed_files.txt"
logs = baseURL + "/logs.txt"

hurrakiLizenz = "CC-BY-SA 3.0"
org = "Hurraki Wörterbuch"
orgLink = "https://hurraki.de/wiki/Hauptseite"
author = "Hurraki"

specialIntro1 = "verschiedene Bedeutungen"
specialIntro2 = "verschiedenen Bedeutungen"
trenner1 = "Gleiche Wörter"
trenner2 = "Genaue Erklärung"
end1 = "Wort·art"
end2 = "Hilf mit!"
end3 = "Siehe auch"


def logIt (text):
    with codecs.open(logs, 'a', "utf-8") as f:
            f.write(text + "\n")
            f.close()
    print(text)

def simpleSanitizeText(textToClean):
    textToClean = " ".join(textToClean.split())
    return textToClean.replace("·","")

def simpleSanitizeLiText(textToClean):
    # textToClean = " ".join(textToClean.split())
    return textToClean.replace("·","")

def getTitle(soup):
    title = soup.find("h1", {"class": "firstHeading"})
    return title.get_text().strip()

def saveFile(fileName, text):
    # save raw text file
    with codecs.open(baseURL + "\\txts\\"+fileName, 'w', "utf-8") as f:
            f.write(f'{text}')
            f.close()
    logIt("created -- "+ fileName)

    if fileName not in processedTexts:
        with codecs.open(processedTextsFile, 'a', "utf-8") as f:
                f.write(f'{fileName}\n')
                f.close()

def addToMetaFile(fileName, url, title):    
    # if fileName in processedTexts:
    #     logIt("already exists in Meta -- " + fileName)
    #     return

    # append entry to meta collection    
    with codecs.open(metaFileName, 'a', "utf-8") as f:
            f.write(f'\n{fileName};{title};{author};;{url};{hurrakiLizenz};;{org};{orgLink}')
            f.close()
    logIt("added to Meta -- "+ title)


def isAnyListValueInString(givenString, list):
    for val in list:
            if val in givenString:            
                return True
    return False

# crawler for full subpage news
def crawlWikiPage(textUrl):    
    r1 = requests.get(textUrl)
    data1 = r1.text
    soup1 = BeautifulSoup(data1, features="html.parser")

    title = getTitle(soup1)

    contentWrapper = soup1.find("div", {"class":"mw-content-ltr"})
    relevantTags = contentWrapper.find_all(["p","h2", "h5", "ul", "h3"])
    skipNext = False
    text = ""
    success = True
    mergeNext = False
    oldText = ""
    liElements = False

    for tag in relevantTags:
        if mergeNext:
            tagText = oldText + " " + tag.get_text().strip()
            mergeNext = False
            # print(tagText)
        else:
            tagText = tag.get_text().strip()
        if specialIntro1 in tagText:
            break
        if specialIntro2 in tagText:
            break
        headlineInContent = tag.find("span", {"class":"mw-headline"})  
        if headlineInContent:
            # print(headlineInContent.get_text().strip())
            if headlineInContent.get_text().strip() == trenner1:
                skipNext = True
            if headlineInContent.get_text().strip() == trenner2:
                skipNext = False
            if headlineInContent.get_text().strip() == end1:
                skipNext = True       
            if headlineInContent.get_text().strip() == end3:
                skipNext = True       
            if headlineInContent.parent.name == "h3":
                tagText = headlineInContent.text
                headlineInContent = None
        listElements = tag.find_all("li")
        if listElements:
            liElements = True
            tagText = ""
            for li in listElements:
                if tagText == "":
                    tagText = "\u2022 " + li.get_text().strip()
                else:                    
                    tagText = tagText + "\n" + "\u2022 " + li.get_text().strip()
        if end2 in tagText:
            skipNext = True    
        # print(tagText)

        if not skipNext and not headlineInContent: # and len(tagText) > 0:
            if not liElements:
                tagText = simpleSanitizeText(tagText)
            else:
                tagText = simpleSanitizeLiText(tagText)
                liElements = False

            # print(tagText)

            # if last char is a comma, continue with tagText and add next line
            if len(tagText) > 0 and tagText[-1] == ",":
                mergeNext = True
                oldText = tagText
                # print(oldText)
                continue
                
            if text == "":
                text = tagText
            else:
                text = text + "\n" + tagText    
                
    if "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")

    # print(text)

    if text == "":
        success = False
        logIt("#### error at: " + textUrl)
    
    if success:
        fileName = re.sub('[^A-Za-zäöüÄÖÜß0-9]+', '', title) + ".txt"    
        saveFile(fileName, text)
        addToMetaFile(fileName, textUrl, simpleSanitizeLiText(title))
        # print("-----------------------------")
        # print(text)
        # print({fileName}, {textUrl}, {title}, {org}, {orgLink})
        # exit()

            
            
# clear log
with codecs.open(logs, 'w', "utf-8") as f:
            f.write("")
            f.close()


processedTexts = []
if os.path.isfile(processedTextsFile):
    with codecs.open(processedTextsFile, "r", "utf-8") as f:
        for line in f:
            processedTexts.append(line.strip())



# crawlWikiPage("https://hurraki.de/wiki/Macke")
# crawlWikiPage("https://hurraki.de/wiki/Zupfinstrument")
# crawlWikiPage("https://hurraki.de/wiki/Zombie")
# crawlWikiPage("https://hurraki.de/wiki/Maria_Sharapova")
# crawlWikiPage("https://hurraki.de/wiki/Abspann")
# crawlWikiPage("https://hurraki.de/wiki/Lügenpresse")
# crawlWikiPage("https://hurraki.de/wiki/Luftpolsterfolie")
# crawlWikiPage("https://hurraki.de/wiki/Jadehase")

# exit()

linkList = []

req = requests.get(baseWikiUrl)
dataHtml = req.text
soup = BeautifulSoup(dataHtml, features="html.parser")
tables = soup.find_all("table")
tableP = tables[len(tables)-1].find_all("p")
# fill link list with links
for p in tableP:
    pa = p(href=True)
    for a in pa:
        link = baseHurrakiUrl + a['href']
        linkList.append(link)

i = 0
for link in linkList:
    logIt("............... ")
    logIt("crawling " + str(link))
    crawlWikiPage(link)
    # i = i+1
    # if i == 10:
    #     break

