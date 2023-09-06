from ast import If
from fileinput import filename
from bs4 import BeautifulSoup
import requests
import codecs
import re
import uuid

# Variables which have the same value for all articles
basePath = "biberCrawler"
metaFileName = basePath + "/bibermeta.csv"
metaFile2 = basePath + "/biber_article_overview.csv"
logs = basePath + "/logs.txt"
biberLizenz = ''
encoding = "utf-8"
biberAuthor = 'das Biber'
org = 'das Biber'# 
orgLink = 'https://www.dasbiber.at/'
processed_files = basePath +  "/processed_biber_files.txt"


def write_to_logs(text):
 with codecs.open(logs, 'a', encoding) as f:
        f.write(text + "\n")
        f.close()
        print(text)


def write_to_processedFiles(fileName):  
     with codecs.open(processed_files, 'a', encoding) as f:
        f.write(f'{fileName}\n')
        f.close()


def addToMetaFile(meta_title, url, fileName, author):
    auth = ""
    if(author == ""):
        auth = biberAuthor
    else:
        auth = author
    with codecs.open(metaFileName, 'a', encoding) as f:
        f.write(f'\n{fileName}\t{meta_title}\t{url}\t\t{biberLizenz}\t{auth}\t\t{org}\t{orgLink}')
        f.close

def addToMetaFile2(meta_title, url, cleaned_bereich):        
    with codecs.open(metaFile2, 'a', encoding) as p: 
        p.write(f'{meta_title}, {url}, {cleaned_bereich}\n')
        p.close()


def safe_text_in_file(fileName, text):
     actual_fileName = basePath+ "/txts/" + fileName
     with codecs.open(actual_fileName, 'a', encoding) as f:
        f.write(text)
        f.close()



def crawl_page_meta_and_text(url__link):
     
     # get html of website
     headers = {

                    "X-Request-ID": str(uuid.uuid4()),

                    "From": "https://www.germ.univie.ac.at/projekt/latill/"

                }
     req = requests.get(url__link, headers = headers)
     data = req.text
     soup = BeautifulSoup(data, features="html.parser")
     
     # search meta data 
     meta_title = soup.title
     meta_title = meta_title.string 
     meta_title = meta_title[:-11] 
     
     bereich = soup.find("div", {"field field-name-field-bereich field-type-taxonomy-term-reference field-label-above clearfix"})
     if (bereich is not None):
        bereich = bereich.get_text()
        cleaned_bereich = re.sub(r'\n', ' ', bereich)
        ("tag with bereich found " + cleaned_bereich)
     else: 
         cleaned_bereich = "no specified category"
         print(cleaned_bereich)

     clean_fileName  = re.sub('[^a-zA-Z0-9äöüÄÖÜ \n\.]', " ", meta_title)
     real_fileName = clean_fileName.replace(" ", "") + '.txt'

    # find text
     text = ""
     parent = soup.find("div", {"class":"field-item odd"})
     pattern = r'(?i)^von.*[^.?!]$'
     authorString = ""
         
     contentChildren = parent.findChildren(recursive=False)
     for child in contentChildren:   
        # abfrage wenn div leer ist (kein text)
        if (child.name != "div", {"class":"media media-element container media-default"}):
            if (child.find("u")):
                continue
            childText = child.get_text()
            if (childText is not None):
                # check if there are authors mentioned in the text with prefix "von" regex
                if re.search(pattern, childText):
                    parenthPattern = r'\([^)]*\)'
                    authorString = childText.strip().replace("von","").replace("Von","").replace("Collagen","").replace("Fotos","").replace("Foto","").replace(":","")
                    # get specific author but remove parentheses if there are any
                    authorString = re.sub(parenthPattern, "", authorString).lstrip()
                    continue
                txt = childText.strip()
                if ((txt != "&nbsp") and (txt !="*BEZAHLTE ANZEIGE*")):
                    text += txt + " "
        else: 
            continue
        
        # skip texts, shorter than 10 characters
     if len(text) < 10:  
         return      
    
    # only do those things, if they are not already in the processed files data (has been crawled)
     if real_fileName not in processedTexts:
        real_fileName = real_fileName.replace("..",".")
        # pass on specific author, which gets replaced with das biber if there is no spec author
        addToMetaFile(meta_title, url__link,  real_fileName, authorString)
        addToMetaFile2(meta_title, url__link, cleaned_bereich)
        write_to_logs("saving: " + real_fileName)
     
        # safe text in for it created file
        safe_text_in_file(real_fileName, text)
        write_to_processedFiles(real_fileName)


def Crawl():   
    
    basePageURL = "https://www.dasbiber.at/articles"
    for i in range(0,322):
        write_to_logs("i: " + str(i))
        if i == 0:
            get_each_URL1(basePageURL)
        else:
            
            newPageURL = basePageURL + "?page=" +str(i)

            get_each_URL1(newPageURL)
         


def get_each_URL1(newPageURL ):
    baseURL = "https://www.dasbiber.at"
    r = requests.get(newPageURL)
    data = r.text
    soup = BeautifulSoup(data, features="html.parser")    

    heading_parent1 = soup.find("div", {"class": "main-group group-cols-1 group-6 grid grid-6"})
    children = heading_parent1.findChildren()
    i= 0
    # print("# " + str(children))
    for child in children:
        if (child.name == "div" and "field-content" in child.get("class", [])):
            if(child.get_text() == ""):
                # starting from 204, there are no images, which is the parent element of the first field-content
                # if no text is in the child, take the parent of its parent and look for the title element with a tag instead of the image
                final_url = baseURL + child.parent.parent.find("div", {"class", "views-field views-field-title"}).find("a", href=True)['href']      
            else:                
                tags_link = child.findChildren()
                tag_url = tags_link[0]
                final_url = baseURL + tag_url['href']
            
            write_to_logs("crawling: " + str(final_url))
            #will following method be called? 
            crawl_page_meta_and_text(final_url)
            

processedTexts = []  
# check if the text has been crawled before
with codecs.open(processed_files, "r", encoding) as f:
    for line in f:
        processedTexts.append(line.strip())

# crawl_page_meta_and_text("https://www.dasbiber.at/content/wanted-migranten-f%C3%BCr-den-h%C3%A4fn")
# crawl_page_meta_and_text("https://www.dasbiber.at/content/%C3%B6lige-tr%C3%A4ume")
# crawl_page_meta_and_text("https://www.dasbiber.at/content/3-minuten-mit-baraa-bolat")
#get_each_URL1("https://www.dasbiber.at/articles")
# exit()
Crawl()
# exit()