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
cleanedBereich = "Nicos Weg"

def write_to_processedFiles(fileName):  
     with codecs.open(processed_files, 'a', encoding) as f:
        f.write(fileName + '\n')
        f.close()


def logIt(text):
 with codecs.open(logs, 'a', encoding) as f:
        f.write(text + "\n")
        f.close()
        print(text)

def safe_text_in_file(fileName, text):
     actual_fileName = basePath+ "/txts/" + fileName
     with codecs.open(actual_fileName, 'a', encoding) as f:
        f.write(text)
        f.close()


def add_to_metaFile(fileName, title, link):
    with codecs.open(metaFileName, 'a', encoding) as f:
        f.write(f'\n{fileName}\t{title}\t{link}\t\t{learnGermanLizenz}\t{author}\t\t{org}\t{orgLink}')
        f.close()
        #print("Iam after close statement")    


def add_to_metaFile2(fileName, meta_title, link, bereich):        
    with codecs.open(metaFile2, 'a', encoding) as p: 
        p.write(f'{fileName}, {meta_title}, {link}, {bereich}\n')
        p.close()




def crawl_meta_and_text_NicosWeg_manuskript(link):  

    headers = { "X-Request-ID": str(uuid.uuid4()),
                    "From": "https://www.germ.univie.ac.at/projekt/latill/" }
    req = requests.get(link, headers = headers)
    data = req.text
    soup = BeautifulSoup(data, features="html.parser")

    # Sample input string
    input_string = soup.title.get_text()
    contains_manuskript = re.search(r'\bManuskript\b', input_string)
    contains_landeskunde= re.search(r'\bLandeskunde\b', input_string)

    if contains_manuskript: 
        bereich = "Nicos_Weg_Manuskript"
        text = ""
        match_obj_manuskript = re.search(r'\|([^|]+)\|', input_string) #searches for ||
        matched_text = match_obj_manuskript.group(1) # takes group 1
        span_start, span_end = match_obj_manuskript.span() # returns tuple of index of group 1
        title  = input_string[span_start+2:span_end-1]  #takes title

        fileName  = (re.sub('[^a-zA-Z0-9äöüÄÖÜß \n\.]', "", title)).replace(" ", "") + "_NicosWeg_Manuskript.txt"
        logIt("adding to metas: " + title)
        add_to_metaFile(fileName, title, link)
        add_to_metaFile2(fileName, title, link, bereich)

        #find text of manuskript
        parent_manuskript = soup.find("div", {"class" : "richtext-content-container sc-bTfYFJ byzRmI sc-jQrDum heCnGO"})
        childrenP = parent_manuskript.find_all("p")
        for ptag in childrenP:
            txt = ptag.get_text()
            text += txt + " "
        #text = childrenP.get_text().strip()
        safe_text_in_file(fileName, text)



    if contains_landeskunde: 
         text = ""
         
         bereich = "Nicos_Weg_Landeskunde"
         title = re.sub(r'\|.*', '', input_string)
         print(title)
         fileName  = (re.sub('[^a-zA-Z0-9äöüÄÖÜß \n\.]', " ", title)).replace(" ", "") + "_NicosWeg_Landeskunde.txt"
         print(fileName)
         add_to_metaFile(fileName, title, link)
         add_to_metaFile2(fileName, title, link, bereich)
   
        #find text of landeskunde
    
         parent_landeskunde = soup.find("div", {"class" : "richtext-content-container sc-bTfYFJ byzRmI"})
         print(type(parent_landeskunde))
         childrenP = parent_landeskunde.find_all("p")
         for ptag in childrenP:
            txt = ptag.get_text()
            text += txt + " "
         print("parent of landeskunde")
         safe_text_in_file(fileName, text)


def crawl_article_page(actual_link):
    # get html of article website
    headers = {
        "X-Request-ID": str(uuid.uuid4()),
        "From": "https://www.germ.univie.ac.at/projekt/latill/"
    }
    req = requests.get(actual_link, headers=headers)
    data = req.text
    soup = BeautifulSoup(data, features="html.parser")

    # get link to "landeskunde"
    nav_button = soup.find("ul", {"class": "lesson-nav-menu"})
    children = nav_button.findChildren()
    #print(type(children))
    
    for c in children:
        if c.get_text() == "Manuskript" or c.get_text() == "Landeskunde":
            #print(c.get_text())
            href = c.get('href')
            if href is not None: 
                link = "https://learngerman.dw.com" + str(href)
                print("not None   ", link)
                logIt(str(link))
                crawl_meta_and_text_NicosWeg_manuskript(link)
            else: 
                link = "https://learngerman.dw.com" + str(href)
                print("is None   ",link )      
            
          
       
     

def crawl():
    basePageURL = "https://learngerman.dw.com/de/nicos-weg/c-36519687"
    headers = { "X-Request-ID": str(uuid.uuid4()),
                    "From": "https://www.germ.univie.ac.at/projekt/latill/" }
    req = requests.get(basePageURL, headers = headers)
    data = req.text
    soup = BeautifulSoup(data, features="html.parser")
     
    links = soup.find_all("a", {"class":"sc-faUpoM lbXSjK"})
    i = 0#
    for link in links: 
         if i <2:
            print("Found the URL: ", link.get('href'))   
            link = link.get('href')     
            actual_link = str("https://learngerman.dw.com/"+link)
            crawl_article_page((actual_link))
         else: 
           exit()
    print(i)
#


#crawl_article_page("https://learngerman.dw.com/de/nehmen-sie/l-40507920")
#crawl_meta_and_text_NicosWeg_manuskript("https://learngerman.dw.com/de/hallo/l-40322767/lm")
#exit()
crawl()
