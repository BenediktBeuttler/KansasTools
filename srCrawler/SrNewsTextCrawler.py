from ast import If
from fileinput import filename
from bs4 import BeautifulSoup
import requests
import json
import codecs
import re

baseURL = "srCrawler"
metaFileName = baseURL + "/srmeta.csv"
baseSrUrl = "https://www.sr.de"
processedTextsFile = baseURL + "/processed-sr-files.txt"
logs = baseURL + "/logs.txt"
srLizenz = "CC BY-NC-ND 3.0"

def logIt(text):
    with codecs.open(logs, 'a', "utf-8") as f:
            f.write(text + "\n")
            f.close()
    print(text)

def simpleSanitizeText(textToClean):
    # textToClean = " ".join(textToClean.split())
    return textToClean.replace("·","")

def getNewsUrl(index):
    newsUrl = "https://www.sr.de/sr/suche.jsp?liste=archiv_nachrichten_einfach100&pfad=%2fsr%2fhome%2fnachrichten%2fnachrichten_einfach&seite="
    return newsUrl + str(index)

def saveFile(fileName, text):
    # save raw text file
    with codecs.open(baseURL+"\\txts\\"+fileName, 'w', "utf-8") as f:
            f.write(f'{text}')
            f.close()
            
    logIt("created -- " + fileName)

    if fileName not in processedTexts:
        with codecs.open(processedTextsFile, 'a', "utf-8") as f:
                f.write(f'{fileName}\n')
                f.close()

def addToMetaFile(fileName, url, title, org, orgLink):    
    if fileName in processedTexts:
        logIt("already exists in Meta: " + fileName)
        return

    # append entry to meta collection    
    with codecs.open(metaFileName, 'a', "utf-8") as f:
            f.write(f'\n{fileName};{title};;;{url};{srLizenz};;{org};{orgLink}')
            f.close()   

    logIt(str("added to Meta - " + title))

# crawler for full subpage news
def crawlNewsPage(textUrl):    
    r = requests.get(textUrl)
    data = r.text
    soup = BeautifulSoup(data, features="html.parser")

    title = simpleSanitizeText(soup.find("meta", property="og:title")["content"])
    if "Wörterbuch" in title:
        return
    if "Jahresrückblick" in title:
        return
    if "Erste Freibäder im Saarland öffnen" in title:
        return
    org = simpleSanitizeText(soup.find("meta", property="og:site_name")["content"])
    orgLink = baseSrUrl

    # get text
    textHeader = soup.find("div", {"class": "article__header"}).get_text()
    textContent = soup.find("div", {"class": "article__content"})    
    colTextContents = textContent.find_all("div", {"class": "col-md-12"})
    text = textHeader
    for colTextContent in colTextContents:
        contentWithH2 = colTextContent.find("h2", {"class":"background-title"})
        # there is a h2 in content
        if contentWithH2:            
            # print(colTextContent.findChild())
            # does it start with h2 and if so, skip
            if "h2" not in str(colTextContent.findChild()):
                psInContent = colTextContent.find_all("p")
                for pInContent in psInContent:
                    if len(pInContent.get_text()) > 1:
                        # add it
                        text += "\n" + pInContent.get_text().strip()
            break
        # merge texts
        text += "\n" + colTextContent.get_text().strip()
    
    fileName = re.sub('[^A-Za-zäöüÄÖÜß0-9]+', '', title) + ".txt"
    text = simpleSanitizeText(re.sub(r'([\r\n])+', r'\r\n', text))

    while len(text[0].strip()) < 1:
        text = text[1:]
    
    saveFile(fileName, text)
    addToMetaFile(fileName, textUrl, title, org, orgLink)
    # print("")
    # print(text)
    # print(fileName)
    # print(textUrl, title, org, orgLink)
    # print("------------------------------------")


# clear log
with codecs.open(logs, 'w', "utf-8") as f:
            f.write("")
            f.close()

processedTexts = []
with codecs.open(processedTextsFile, "r", "utf-8") as f:
    for line in f:
        processedTexts.append(line.strip())

# read processed files first and save in array
for i in range(1, 27):    
    logIt(str(i))
    # crawlNewsPage("https://www.sr.de/sr/home/nachrichten/nachrichten_einfach/schriftgroesse_kontrast_nachrichten_einfach100.html")
    # crawlNewsPage("https://www.sr.de/sr/home/nachrichten/nachrichten_einfach/ne_telefonbetrueger_100.html")
    # break
    url = getNewsUrl(i)

    req = requests.get(url)
    dataHtml = req.text
    soup = BeautifulSoup(dataHtml, features="html.parser")

    # find news links
    allNewsSpan = soup.find_all("span", {"class": "teaser__text__header__element teaser__text__header__element--headline"})
    if len(allNewsSpan) < 1:
        break
    for newsSpan in allNewsSpan:
        link = newsSpan.find("a", href=True)
        completeLink = baseSrUrl + link['href']
        # print(completeLink)
        crawlNewsPage(completeLink)
    