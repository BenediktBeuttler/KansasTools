from ast import If
from fileinput import filename
from bs4 import BeautifulSoup
import requests
import codecs
import re

basePath = "fluterCrawler"
metaFileName = basePath + "/flutermeta.csv"
baseFluterUrl = "https://www.fluter.de"
processedTextsFile = basePath + "/processed-fluter-files.txt"
logs = basePath + "/logs.txt"
fluterLizenz = "CC BY-NC-ND 4.0"
encoding = "utf-8"


def logIt(text):
    with codecs.open(logs, 'a', encoding) as f:
            f.write(text + "\n")
            f.close()
    print(text)

def simpleSanitizeText(textToClean):
    # textToClean = " ".join(textToClean.split())
    return textToClean.replace("·", "")

def getNewsUrl(index):
    if index == 0:
        newsUrl = "https://www.fluter.de/suche"
        return newsUrl
    else:
        newsUrl = "https://www.fluter.de/suche?page="
        return newsUrl + str(index)

def saveFile(fileName, text):
    # save raw text file
    with codecs.open(basePath+"\\txts\\"+fileName, 'w', encoding) as f:
        f.write(f'{text}')
        f.close()

    logIt("created -- " + fileName)

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

# crawler for full subpage news
# todo: meta info rausnehmen und 

# article body
# relevant!!

def crawlNewsPage(textUrl):
    r = requests.get(textUrl)
    data = r.text
    soup = BeautifulSoup(data, features="html.parser")

    title = simpleSanitizeText(
        soup.find("meta", property="og:title")["content"])
    org = simpleSanitizeText(
        soup.find("meta", property="og:site_name")["content"])
    orgLink = baseFluterUrl

    # get text
    textHeader = soup.find("div", {"class": "article__header"}).get_text()
    textContent = soup.find("div", {"class": "article__content"})
    colTextContents = textContent.find_all("div", {"class": "col-md-12"})
    text = textHeader
    for colTextContent in colTextContents:
        contentWithH2 = colTextContent.find(
            "h2", {"class": "background-title"})
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
with codecs.open(logs, 'w', encoding) as f:
            f.write("")
            f.close()

# createFileIfNotExists(processedTextsFile)
processedTexts = []  
with codecs.open(processedTextsFile, "r", encoding) as f:
    for line in f:
        processedTexts.append(line.strip())

# read processed files first and save in array
# for testing purposes only have a look at the first page
for i in range(0,1):
    logIt(str(i))
    # for testing purposes, i am crawling here the articles directly and break afterwards.
    # crawlNewsPage("https://www.sr.de/sr/home/nachrichten/nachrichten_einfach/schriftgroesse_kontrast_nachrichten_einfach100.html")
    crawlNewsPage("https://www.fluter.de/polizeigewalt-kennzeichungspflicht-behr")
    break
    url = getNewsUrl(i)

    req = requests.get(url)
    dataHtml = req.text
    soup = BeautifulSoup(dataHtml, features="html.parser")

    # find news links
    allNewsDiv = soup.find_all(
        "div", {"class": "search-result-teaser-image nomedia"})
    
    if len(allNewsDiv) < 1:
        continue
    
    for newsDiv in allNewsDiv:
        link = newsDiv.find("a", href=True)
        if link is not None:
            completeLink = baseFluterUrl + link['href']
            print(completeLink)
        # crawlNewsPage(completeLink)
