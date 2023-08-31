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
metaFile2 = basePath + "biber_article_overview.csv"
logs = basePath + "/logs.txt"
biberLizenz = 'unknown'
encoding = "utf-8"
author = 'dasBiber'
org = 'dasBiber'# 
orgLink = 'https://www.dasbiber.at/'
processed_files = basePath +  "processed_biber_files.txt"


def write_to_logs(url):
 with codecs.open(logs, 'a', encoding) as f:
        f.write("checking: " + url + "\n")
        f.close()


def write_to_processedFiles(fileName):  
     with codecs.open(processed_files, 'a', encoding) as f:
        f.write(fileName)
        f.close()


def addToMetaFile(meta_title, url, fileName):
    with codecs.open(metaFileName, 'a', encoding) as f:
        f.write(f'{fileName}\t{meta_title}\t{url}\t\t{biberLizenz}\t{author}\t{author}\t{org}\t{orgLink}\n')
        f.close

def addToMetaFile2(meta_title, url, cleaned_bereich):        
    with codecs.open(metaFile2, 'a', encoding) as p: 
        p.write(f'{meta_title}, {url}, {cleaned_bereich}')
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
     #url = (soup.find('link', rel=re.compile('canonical'))['href']) 


     # get Bereich. Wo ist Bereich?
     # <div class="field field-name-field-bereich field-type-taxonomy-term-reference field-label-above clearfix">
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
     
     
    # add results to metacsv - maybe later ? 
     print(meta_title, cleaned_bereich, real_fileName, url__link)
     addToMetaFile(meta_title, url__link,  real_fileName)
     addToMetaFile2(meta_title, url__link, cleaned_bereich)

    # find text
     text = ""
     parent = soup.find("div", {"class":"field-item odd"})
         
     contentChildren = parent.findChildren(recursive=False)
     for child in contentChildren:   

        ## TODOs
        # abfrage wenn p leer ist (kein text)
        if (child.name != "div", {"class":"media media-element container media-default"}):
            txt = child.get_text().strip()
            if ((txt != "&nbsp") and (txt !="*BEZAHLTE ANZEIGE*")):
                text += txt + " "
            else: 
                continue
            
           
    # safe text in for it created file
     safe_text_in_file(real_fileName, text)
     write_to_processedFiles(real_fileName)


def Crawl():
    
    
    basePageURL = "https://www.dasbiber.at/articles"
    for i in range(0,221):
        if i == 0:
            get_each_URL1(basePageURL)
        else:
            
            newPageURL = basePageURL + "?page=" +str(i)

            get_each_URL1(newPageURL)
            if ( i == 50) or (i == 100) or (i == 200):
                print("reached page: " + i)
            else: 
                continue



def get_each_URL1(newPageURL ):
    baseURL = "https://www.dasbiber.at//"
    r = requests.get(newPageURL)
    data = r.text
    soup = BeautifulSoup(data, features="html.parser")
    

    heading_parent1 = soup.find("div", {"class": "main-group group-cols-1 group-6 grid grid-6"})
    children = heading_parent1.findChildren()
    i= 0
    for child in children:
        if (child.name == "div" and "field-content" in child.get("class", [])):
            tags_link = child.findChildren()
            tag_url = tags_link[0]
            final_url = baseURL + tag_url['href']
            
            write_to_logs(str(final_url))
            #will following method be called? 
            crawl_page_meta_and_text(final_url)
            

#crawl_txt("https://www.dasbiber.at/content/freispruch-warum-die-klage-gegen-sos-balkanroute-gesellschaftliche-folgen-hat")
#crawl_page_meta_and_text("https://www.dasbiber.at/content/%C3%B6lige-tr%C3%A4ume")
# crawl_page_meta_and_text("https://www.dasbiber.at/content/freispruch-warum-die-klage-gegen-sos-balkanroute-gesellschaftliche-folgen-hat")
#get_each_URL1("https://www.dasbiber.at/articles")
Crawl()