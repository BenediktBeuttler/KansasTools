from ast import If
from fileinput import filename
from bs4 import BeautifulSoup
import requests
import codecs
import re
import uuid

# Variables which have the same value for all articles
basePath = "learnGerman"
metaFileName = basePath + "/learnGerman_meta.csv"
metaFile2 = basePath + "/learnGerman_article_overview.csv"
logs = basePath + "/logs.txt"
processed_files = basePath +  "/processed_learnGerman_files.txt"
learnGermanLizenz = ''
encoding = "utf-8"
author = 'Deutsche Welle'
org = 'Deutsche Welle'# 
orgLink = 'https://learngerman.dw.com/de/deutsch-lernen/s-9095'
bereich = "Deine Band"
processedTexts = basePath + "/processed_learnGerman_files.txt"

#function 
def logIt(text):
 with codecs.open(logs, 'a', encoding) as f:
        f.write(text + "\n")
        f.close()
        print(text)


def add_to_metaFile(fileName, title, link):
    if fileName in processedTexts:
        logIt("already exists in Meta: " + fileName)
        return
    
    with codecs.open(metaFileName, 'a', encoding) as f:
        f.write(f'\n{fileName}\t{title}\t{link}\t\t{learnGermanLizenz}\t{author}\t\t{org}\t{orgLink}')
        f.close()



def add_to_metaFile2(fileName, meta_title, link, bereich):       
    if fileName in processedTexts:
        logIt("already exists in Meta: " + fileName)
        return
     
    with codecs.open(metaFile2, 'a', encoding) as p: 
        p.write(f'{fileName}\t{meta_title}\t{link}\t{bereich}\n')
        p.close()


def safe_text_in_file(fileName, text):
    actual_fileName = basePath+ "/txts/" + fileName
    with codecs.open(actual_fileName, 'a', encoding) as f:
        f.write(text)
        f.close()
        
    if fileName not in processedTexts:
        with codecs.open(processed_files, 'a', encoding) as f:
            f.write(f'{fileName}\n')
            f.close()



def crawl_meta_and_text_deineBand_manuskript(link):
     headers = { "X-Request-ID": str(uuid.uuid4()),
                    "From": "https://www.germ.univie.ac.at/projekt/latill/" }
     req = requests.get(link, headers = headers)
     data = req.text
     soup = BeautifulSoup(data, features="html.parser")

    # meta data: title, fileName
     input_string = soup.title.get_text()
     match_obj_manuskript = re.search(r'\|([^|]+)\|', input_string) #searches for ||
     matched_text = match_obj_manuskript.group(1) # takes group 1
     span_start, span_end = match_obj_manuskript.span() # returns tuple of index of group 1
     title  = input_string[span_start+2:span_end-1]  #takes title
     title = re.sub('[0-9]', "", title)
     

     fileName  = (re.sub('[^a-zA-ZäöüÄÖÜß \n\.]', "", title)).replace(" ", "") + "_deineBand_Manuskript.txt"
     print(fileName)
     logIt("adding manuskript to metas: " + title)
     add_to_metaFile(fileName, title, link)
     add_to_metaFile2(fileName, title, link, bereich)

     #get text 
     text = ""
     parent_manuskript = soup.find("div", {"class" : "richtext-content-container sc-bTfYFJ byzRmI sc-jQrDum heCnGO"})
     childrenP = parent_manuskript.find_all("p")
     for ptag in childrenP:
            txt = ptag.get_text()
            text += txt + "\n"
        #text = childrenP.get_text().strip()
     print(text)
     safe_text_in_file(fileName, text)




     





def crawl_article_page(link):
    # get html of article website
    headers = {
        "X-Request-ID": str(uuid.uuid4()),
        "From": "https://www.germ.univie.ac.at/projekt/latill/"
    }
    req = requests.get(link, headers=headers)
    data = req.text
    soup = BeautifulSoup(data, features="html.parser")
    nav_button = soup.find("ul", {"class": "lesson-nav-menu"})
    children = nav_button.findChildren()
    
    for c in children:
        if c.get_text() == "Manuskript":
            href = c.get('href')
            if href is not None: 
                link = "https://learngerman.dw.com" + str(href)
              #  print("---link to manuskript of song  ", link)
                logIt(str(link))
                crawl_meta_and_text_deineBand_manuskript(link)
            else: 
                 continue  


def crawl():
    basePageURL = "https://learngerman.dw.com/de/deine-band/s-60637027"
    headers = { "X-Request-ID": str(uuid.uuid4()),
                    "From": "https://www.germ.univie.ac.at/projekt/latill/" }
    req = requests.get(basePageURL, headers = headers)
    data = req.text
    soup = BeautifulSoup(data, features="html.parser")
     
   # parent_links = soup.find("div", {"class":"sc-kJpAUB gNHpMp"})
    parent_links = soup.find_all("a", {"class":"sc-ckRZPU jUoxNF teaser"})
    #print("I found the links")
    #print(parent_links) # wieso werden die Ergebnisse nicht gelistet?
    for link in parent_links: 
            #print("Found the URL: ", link.get('href'))   
            link = link.get('href')     
            link = str("https://learngerman.dw.com/"+link)
           # print("link to song", link)
            crawl_article_page(link)


processedTexts = [] 
with codecs.open(processed_files, "r", encoding) as f:
    for line in f:
        processedTexts.append(line.strip())

crawl()
    


