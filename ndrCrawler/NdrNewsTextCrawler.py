from ast import If
from fileinput import filename
from bs4 import BeautifulSoup
import requests
import json
import codecs
import re

baseURL = "ndrCrawler"
metaFileName = baseURL + "/ndrmeta.csv"
baseNdrUrl = "https://www.ndr.de"
textEndCutoffs = {"Diese Nachricht ist vom", "Diese Nachrichten sind"}
processedTextsFile = baseURL + "/processed_files.txt"
logs = baseURL + "/logs.txt"
ndrLizenz = "CC BY-NC-ND 3.0"

def logIt (text):
    with codecs.open(logs, 'a', "utf-8") as f:
            f.write(text + "\n")
            f.close()
    print(text)

def getNewsUrl(index):
    newsUrl = "https://www.ndr.de/fernsehen/barrierefreie_angebote/leichte_sprache/leichtesprachearchiv110_page-"
    return newsUrl + str(index) + ".html"

def simpleSanitizeText(textToClean):
    textToClean = " ".join(textToClean.split())
    return textToClean.replace("·","")

def getMetaTextJson(soup):
    metaInfo = soup.find('script', attrs={'type': 'application/ld+json'})
    metaText = metaInfo.find(text=True)
    jsonObjMeta = json.loads(metaText, strict=False)
    return jsonObjMeta

def getOrg(soup):
    jsonObjMeta = getMetaTextJson(soup)
    org = jsonObjMeta['publisher']['name']
    return org

def getOrgLink(soup):
    jsonObjMeta = getMetaTextJson(soup)
    orgLink = jsonObjMeta['publisher']['url']
    return orgLink

def getTitleForSingleNewsPage(soup):
    jsonObjMeta = getMetaTextJson(soup)
    title = simpleSanitizeText(jsonObjMeta['headline'])
    return title

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

def addToMetaFile(fileName, url, title, org, orgLink):    
    if fileName in processedTexts:
        logIt("already exists in Meta -- " + fileName)
        return

    # append entry to meta collection    
    with codecs.open(metaFileName, 'a', "utf-8") as f:
            f.write(f'\n{fileName};{title};;;{url};{ndrLizenz};;{org};{orgLink}')
            f.close()
    logIt("added to Meta -- "+ title)


def isAnyListValueInString(givenString, list):
    for val in list:
            if val in givenString:            
                return True
    return False

# crawler for full subpage news
def crawlNewsPage(textUrl):    
    r1 = requests.get(textUrl)
    data1 = r1.text
    soup1 = BeautifulSoup(data1, features="html.parser")

    title = getTitleForSingleNewsPage(soup1)
    org = getOrg(soup1)
    orgLink = getOrgLink(soup1)

    # skip special news page jahresrückblick
    if "Jahresrückblick in Leichter Sprache" in title:
        return

    # get text
    text = ""
    for allText in soup1.find_all('p'):
        # if not len(allText.get_text().strip()) > 0:
        #     continue
        strippedText = allText.get_text().strip()  
        if isAnyListValueInString(strippedText, textEndCutoffs):
            # print("ist drin, break")
            break
        text += simpleSanitizeText(strippedText) + "\n"
    
    while len(text[0].strip()) < 1:
        text = text[1:]
    fileName = re.sub('[^A-Za-zäöüÄÖÜß0-9]+', '', title) + ".txt"
    
    saveFile(fileName, text)
    addToMetaFile(fileName, textUrl, title, org, orgLink)
    # print("-----------------------------")
    # print(text)
    # print({fileName}, {textUrl}, {title}, {org}, {orgLink})



def crawlAggregatedNewsPage(textUrl):            
    r2 = requests.get(textUrl)
    data2 = r2.text
    soup2 = BeautifulSoup(data2, features="html.parser")

    newsSeparator = "###+"
    title = "" # there are multiple titles, don't rely on meta description in source code
    org = getOrg(soup2)
    orgLink = getOrgLink(soup2)
    
    myArticle = soup2.find("article", {"class": "w100 idxvorspann"})
    if not myArticle:
        myArticle = soup2.find("article", {"class": "w100"})
    allNewsTags = myArticle.find_all(['h2', 'p'])
    newsTextsWithSeparator = ""
    for allNewsTag in allNewsTags:
        tmpStrippedText = allNewsTag.get_text().strip()
        if isAnyListValueInString(tmpStrippedText, textEndCutoffs):
            # print("ist drin, break")
            break
              
        if "<em>---" in str(allNewsTag):
            newsTextsWithSeparator += newsSeparator
        else:            
            sanText = simpleSanitizeText(str(allNewsTag))
            newsTextsWithSeparator += sanText + "\n"

    newsTexts = newsTextsWithSeparator.split(newsSeparator)
    for newsText in newsTexts:
        if len(newsText) > 0:
            newsTextBs4 = BeautifulSoup(newsText, features="html.parser") 
            # print(len(newsText))
            # print("-----")
            # print(newsTextBs4)
            headlineTag = newsTextBs4.find('h2') 
            if not headlineTag:
                continue
            strongTag = headlineTag.find('strong')
            if strongTag:
                title = simpleSanitizeText(strongTag.find(text=True))
            else:
                title = simpleSanitizeText(headlineTag.find(text=True))
            if len(title) < 2:
                continue
            # # print(title)
            fileName = re.sub('[^A-Za-zäöüÄÖÜß0-9]+', '', title) + ".txt"   
            finaleNewsText = newsTextBs4.get_text().strip()
            saveFile(fileName, finaleNewsText)
            addToMetaFile(fileName, textUrl, title, org, orgLink)
            # print("-----------------------------")
            # print(finaleNewsText)
            # print({fileName}, {textUrl}, {title}, {org}, {orgLink})
                    
            
            
# clear log
with codecs.open(logs, 'w', "utf-8") as f:
            f.write("")
            f.close()


# there are only 100 pages of news
processedTexts = []
with codecs.open(processedTextsFile, "r", "utf-8") as f:
    for line in f:
        processedTexts.append(line.strip())

# read processed files first and save in array
for i in range(1, 190):    
    logIt(str(i))
    # crawlAggregatedNewsPage("https://www.ndr.de/fernsehen/barrierefreie_angebote/leichte_sprache/Mehr-Nachrichten-vom-14092018,nils1284.html")
    # break
    url = getNewsUrl(i)

    req = requests.get(url)
    dataHtml = req.text
    soup = BeautifulSoup(dataHtml, features="html.parser")

    # check for normal news
    myArticle = soup.find("article", {"class": "w100 idxvorspann"})
    myDivs = myArticle.find_all("div", {"class": "module w100 list"})
    if len(myDivs) < 1:
        break
    for myDiv in myDivs:
        link = myDiv.find("a", href=True)
        completeLink = baseNdrUrl + link['href']

        teaserImgDiv = myDiv.find("div", {"class": "teaserimage"})
        if not teaserImgDiv:
            # it's an aggregated news page
            crawlAggregatedNewsPage(completeLink)
        else:
            # print("Found the URL:", completeLink)
            crawlNewsPage(completeLink)
    
    # check for aggregated news in subpage
