from ast import If
from fileinput import filename
from bs4 import BeautifulSoup
import requests
import codecs
import re

basePath = "bpbCrawler"
metaFileName = basePath + "/bpbmeta.csv"
baseBpbUrl = "https://www.bpb.de"
processedTextsFile = basePath + "/processed-bpb-files.txt"
logs = basePath + "/logs.txt"
bpbLizenz = "CC BY-NC-ND 2.0"
encoding = "utf-8"


def logIt(text):
    with codecs.open(logs, 'a', encoding) as f:     # 'a' = append mode; added any data written to the file to the end of the existing content. If the file does not exist, a new file is created.
            f.write(text + "\n")
            f.close()
    print(text)

def simpleSanitizeText(textToClean):
    # textToClean = " ".join(textToClean.split())
    return textToClean.replace("·", "")

def getNewsUrl(index):
    if index == 0:
        newsUrl = ""
        return newsUrl
    else:
        newsUrl = ""
        return newsUrl

def saveFile(fileName, text):
    # save raw text file
    with codecs.open(basePath+"\\txts\\"+fileName, 'w', encoding) as f:     # 'w' = write mode; opens a file for writing, and clears the existing content.
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
        f.write(f'\n{fileName};{title};;;{url};{bpbLizenz};;{org};{orgLink}')
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
    orgLink = baseBpbUrl

    # get text
    textHeader = soup.find("h2", {"class": "opening-header__title"}).get_text()
    textContent = soup.find("div", {"class": "text-content spacer-horizontal__inset-narrow title2margin"})
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



# Meeting 16-08-2023
# custom headers: inform the owner of the sites who we are when we crawl --- to get the code from Benedict
# meta: same basis for the meta files - csv files(comma) - tsv files(tab)
# categories: add categories --- nice to have, not compulsory
# 



# BPB
# themen - politik - 
# check if the text is aready registered
# 
# Crawl through all the sub-sub-sub links, 
# Dossier --- lowest level

# nav-toc
# skip Wahl-o-mat
# 


# look for Dossier, open, look for drop down () --- .parents(find tag a from link)
# do the getting links part first

# From the site map
# Themen - all sub-topics
# Lernen - bildung themen
