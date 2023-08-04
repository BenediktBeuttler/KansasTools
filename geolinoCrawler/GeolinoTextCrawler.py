from ast import If
from fileinput import filename
from bs4 import BeautifulSoup
import requests
import codecs
import re
import os

basePath = "geolinoCrawler"
metaFileName = basePath + "/geolinometa.csv"
baseGeolinoUrl = "https://www.geo.de"
processedTextsFile = basePath + "/processed-geolino-files.txt"
logs = basePath + "/logs.txt"
geolinoLizenz = "unknown"
allowedCategories = ["berufe", "forschung-und-technik", "natur-und-umwelt",
                     "mensch", "redewendungen", "filmtipps", "spieletests"]
encoding = "utf-8"


def logIt(text):
    with codecs.open(logs, 'a', encoding) as f:
            f.write(text + "\n")
            f.close()
    print(text)

def simpleSanitizeText(textToClean):
    # textToClean = " ".join(textToClean.split())
    return textToClean.replace("·", "")

def getNewsUrl(month, year):
    newsUrl = "https://www.geo.de/geolino/archiv/?month=" + str(month) + "&year=" + str(year)
    logIt(newsUrl)
    return newsUrl

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
        f.write(f'\n{fileName};{title};;;{url};{geolinoLizenz};;{org};{orgLink}')
        f.close()

    logIt(str("added to Meta - " + title))

def cleanupBeforehand():    
    # clear log    
    with codecs.open(logs, 'w', encoding) as f:
                f.write("")
                f.close()

    # check if file exists
    if not os.path.exists(processedTextsFile):
        with codecs.open(processedTextsFile, 'w', encoding) as f:
                f.write("")
                f.close()

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
    orgLink = baseGeolinoUrl

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

cleanupBeforehand()
            
processedTexts = [] 
with codecs.open(processedTextsFile, "r", encoding) as f:
    for line in f:
        processedTexts.append(line.strip())

# year
for i in range(0, 24): # 24
    # month
    for j in range(1, 13): #13
        logIt(str("year: " + str(i) + " month: " + str(j)))
        # crawlNewsPage("https://www.geo.de/geolino/natur-und-umwelt/10697-rtkl-wanzen-milben-zecken-wer-auf-uns-so-alles-wohnt")
        # crawlNewsPage("https://www.geo.de/geolino/mensch/10006-rtkl-die-schule-der-kung-fu-maedchen")
        
        # break
        url = getNewsUrl(j, 2002 + i)
        
        req = requests.get(url)
        dataHtml = req.text
        soup = BeautifulSoup(dataHtml, features="html.parser")

        # # find news links
        allNewsDiv = soup.find_all(
            "article", {"class": "teaser teaser--plaintext group-teaserlist__item group-teaserlist__item--teaser-plaintext item--context-group-teaserlist"})
        # print(allNewsDiv)
        if len(allNewsDiv) < 1:
            continue
        
        for newsDiv in allNewsDiv:
            link = newsDiv.find("a", href=True)
            if link is not None:
                completeLink = link['href']
                # only allow certain categories
                for cat in allowedCategories:
                    # print(cat + " in " + completeLink)
                    if str("/" + cat + "/") in completeLink:
                        # print(completeLink)
                        print(cat + " in " + completeLink)
                        # crawlNewsPage(completeLink)
