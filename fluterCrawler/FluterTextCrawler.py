from ast import If
from fileinput import filename
from bs4 import BeautifulSoup
import requests
import codecs
import re
import uuid

basePath = "fluterCrawler"
metaFileName = basePath + "/flutermeta.csv"
baseFluterUrl = "https://www.fluter.de"
processedTextsFile = basePath + "/processed-fluter-files.txt"
logs = basePath + "/logs.txt"
fluterLizenz = "CC BY-NC-ND 4.0"
encoding = "utf-8"
print("test")


def logIt(text):
    with codecs.open(logs, 'a', encoding) as f:
            f.write(text + "\n")
            f.close()
    print(text)

def simpleSanitizeText(textToClean):
    # textToClean = " ".join(textToClean.split())
    return re.sub(r'\s+', ' ', textToClean.strip().replace("Interview: ", "").replace("Fotos: ", "").replace("Text: ", "").replace('"', ''))

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

def addToMetaFile(fileName, url, title, author, org, orgLink):
    if fileName in processedTexts:
        logIt("already exists in Meta: " + fileName)
        return

    # append entry to meta collection
    with codecs.open(metaFileName, 'a', encoding) as f:
        f.write(f'\n{fileName}\t{title}\t{url}\t\t{fluterLizenz}\t{author}\t\t{org}\t{orgLink}')
        f.close()

    logIt(str("added to Meta - " + title))

def crawlNormalText(soup):
    text = ""
    textContentHtml = soup.find_all("div", {"class": "articleBlock articleBlockStandard"})
    for textContent in textContentHtml:
        contentChildren = textContent.findChildren()
        for contentChild in contentChildren:
            if (contentChild.name=="div" and "articleBlock articleBlockInsertRightFloated" in contentChild.get("class", [])):
                continue
            if (contentChild.name=="p" and len(contentChild.get_text().strip())>1 ):
                # merge texts
                text += "\n" + contentChild.get_text().strip()
    return text

def crawlNewsPage(textUrl):
    r = requests.get(textUrl)
    data = r.text
    soup = BeautifulSoup(data, features="html.parser")

    title = simpleSanitizeText(
        soup.find("meta", property="og:title")["content"])
    org = simpleSanitizeText(
        soup.find("meta", property="og:site_name")["content"])
    orgLink = baseFluterUrl
    
    authorHtml = soup.find("div", {"class": "author author-first"})
    author = simpleSanitizeText(authorHtml.get_text()).replace(" und ", ", ")
    textHeaderHtml = soup.find("div", {"class": "intro-fourth center <none>"})
    textHeader = textHeaderHtml.find("h2").get_text().strip() + "."
    text = textHeader
    
    # check if its a disput text by checking tags for "streit"
    disput = False
    tagsHtmls = soup.find_all("ul", {"class":"tags-second"})
    for tagHtml in tagsHtmls:
        if "streit" in tagHtml.get_text().strip().lower():
            disput = True
            break
        
    if disput:
        # different crawling here
        
        texts = soup.find_all("div", {"class": "left_floated"})
        i = 0
        for textDisput in texts:
            specAuthor = ""
            textChildren = textDisput.findChildren()
            for textChild in textChildren:
                if (textChild.name == "h2" and "element-invisible" in textChild.get("class", [])):
                    continue
                elif (textChild.name == "h2"):
                    text += "\n" + textChild.get_text().strip() + "."
                if (textChild.name == "h3"):
                    text += "\n" + textChild.get_text().strip() + "."
                if (textChild.name=="div" and "media media-element-container media-default" in textChild.get("class", [])):
                    continue
                if (textChild.find("em")):        
                    continue
                if (textChild.name == "p"):
                    text += "\n" + textChild.get_text().strip()
            
            specAuthor = author.split(", ")[i]
            # print(specAuthor)
            i += 1
            
            fileName = re.sub('[^A-Za-zäöüÄÖÜß0-9]+', '', str(title + specAuthor)) + ".txt" 
            text = simpleSanitizeText(re.sub(r'([\r\n])+', r'\r\n', text))

            if len(text) < 1:
                return
            
            while len(text[0].strip()) < 1:
                text = text[1:]

            saveFile(fileName, text)
            addToMetaFile(fileName, textUrl, title, specAuthor, org, orgLink)
            # print("")
            # print(text)
            # print(fileName)
            # print(textUrl, title, author, org, orgLink)
            # print("------------------------------------")
    else:
        # normal text crawling
        # get text    
        text += "\n" + crawlNormalText(soup)
    
        fileName = re.sub('[^A-Za-zäöüÄÖÜß0-9]+', '', title) + ".txt"
        text = simpleSanitizeText(re.sub(r'([\r\n])+', r'\r\n', text))

        if len(text) < 1:
            return
        
        while len(text[0].strip()) < 1:
            text = text[1:]

        saveFile(fileName, text)
        addToMetaFile(fileName, textUrl, title, author, org, orgLink)
        # print("")
        # print(text)
        # print(fileName)
        # print(textUrl, title, author, org, orgLink)
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
for i in range(0, 404): #404
    # for testing purposes, i am crawling here the articles directly and break afterwards.
    # crawlNewsPage("https://www.fluter.de/wm-katar-boykottieren-streit")
    # crawlNewsPage("https://www.fluter.de/unterwassergarten-genua-landwirtschaft")
    # crawlNewsPage("https://www.fluter.de/polizeigewalt-kennzeichungspflicht-behr")
    # exit()
    url = getNewsUrl(i)
    logIt(getNewsUrl(i))

    headers = {
                    "X-Request-ID": str(uuid.uuid4()),
                    "From": "https://www.germ.univie.ac.at/projekt/latill/"
                }
    req = requests.get(url, headers = headers)
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
            logIt("checking:" + completeLink)
            crawlNewsPage(completeLink)
