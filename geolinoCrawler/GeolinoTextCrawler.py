from ast import If
from fileinput import filename
from bs4 import BeautifulSoup
import requests
import codecs
import re
import os
import uuid

basePath = "geolinoCrawler"
metaFileName = basePath + "/geolinometa.csv"
baseGeolinoUrl = "https://www.geolino.de"
author = "Geolino"
processedTextsFile = basePath + "/processed-geolino-files.txt"
logs = basePath + "/logs.txt"
geolinoLizenz = "unknown"
disallowedCategories = ["kreativ, wettbewerbe, archive, spiele"]
# allowedCategories = ["berufe", "forschung-und-technik", "natur-und-umwelt",
#                      "mensch", "redewendungen", "filmtipps", "spieletests"]
encoding = "utf-8"


def logIt(text):
    with codecs.open(logs, 'a', encoding) as f:
            f.write(text + "\n")
            f.close()
    print(text)

def simpleSanitizeText(textToClean):
    # textToClean = " ".join(textToClean.split())
    return textToClean

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
        f.write(f'\n{fileName}\t{title}\t{url}\t\t{geolinoLizenz}\t{author}\t\t{org}\t{orgLink}')
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
    text = ""
    # skip podcasts
    podcast = soup.find("div", {"class": "title article__title"})
    if (podcast and "podcast" in podcast.get_text().strip().lower() ):
        return
    content = soup.find("div", {"class": "article__body js-article-body"})
    if content == None:
        content = soup.find("div",{"class":"gallery page__inner-content"})
    contentChildren = content.findChildren()
    for contentChild in contentChildren:
        skip = True
        addDot = False
        # print(contentChild)
        # subtitle
        class_name_pattern = re.compile(r'\btext-element\b', re.IGNORECASE)

        if (contentChild.name == "div" and "authors article__authors" in contentChild.get("class", [])):
            skip = True
        if (contentChild.name == "div" and "intro" in contentChild.get("class", [])):
            skip = False
            addDot = True
        if (contentChild.name=="div" and any(class_name_pattern.search(cls) for cls in contentChild.get("class", []))):
            skip = False
        if (contentChild.name=="p" and any(class_name_pattern.search(cls) for cls in contentChild.get("class", []))):
            skip = False
            
        if not skip:
            if addDot:
                text += "\n" + contentChild.get_text().strip() + "."
            else:
                text += "\n" + contentChild.get_text().strip()
        else:
            continue
    
    # print(text)
    
    fileName = re.sub('[^A-Za-zäöüÄÖÜß0-9]+', '', title) + ".txt"
    text = simpleSanitizeText(re.sub(r'([\r\n])+', r'\r\n', text))
    
    if len(text) < 1:
        return

    while len(text[0].strip()) < 1:
        text = text[1:]

    saveFile(fileName, text)
    addToMetaFile(fileName, textUrl, title, org, orgLink)

cleanupBeforehand()
            
processedTexts = [] 
with codecs.open(processedTextsFile, "r", encoding) as f:
    for line in f:
        processedTexts.append(line.strip())

# year
for i in range(11, 24): # 24
    # month
    for j in range(1, 13): #13
        logIt(str("year: " + str(i) + " month: " + str(j)))
        # crawlNewsPage("https://www.geo.de/geolino/natur-und-umwelt/10697-rtkl-wanzen-milben-zecken-wer-auf-uns-so-alles-wohnt")
        # crawlNewsPage("https://www.geo.de/geolino/natur-und-umwelt/9712-rtkl-fotoshow-geo-tag-der-artenvielfalt-2005")
        # crawlNewsPage("https://www.geo.de/geolino/wissen/fuer-kinder-erklaert--krieg-in-der-ukraine-31690312.html")
        
        # exit()
        url = getNewsUrl(j, 2002 + i)
        
        headers = {
                    "X-Request-ID": str(uuid.uuid4()),
                    "From": "https://www.germ.univie.ac.at/projekt/latill/"
                }
        req = requests.get(url, headers=headers)
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
                logIt("checking... " + completeLink)
                # skip stuff
                substrings_to_check = ["/geolino/1", "podcast", "hoerspiel", "-quiz-", "wissenstest", "fotoquiz", "-video-"]
                if any(substring in completeLink for substring in substrings_to_check):
                    logIt("skipping: " + completeLink)
                    continue
                
                pattern = r"https://www.geo.de/geolino/([^/]+)" # gives category string
                match = re.search(pattern, completeLink)
                if match:
                    extracted_string = match.group(1)
                    if extracted_string not in disallowedCategories:
                        crawlNewsPage(completeLink)
                        # print(extracted_string)
                    else:
                        logIt("skipping: " + completeLink)
                        continue
                else:
                    logIt("Pattern not found in the URL: " + completeLink)
                    continue