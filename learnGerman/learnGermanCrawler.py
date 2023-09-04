from ast import If
from fileinput import filename
from bs4 import BeautifulSoup
import requests
import codecs
import re
import uuid

# Variables which have the same value for all articles
basePath = "learnGerman"
metaFileName = basePath + "/learngerman.csv"
metaFile2 = basePath + "learngerman_article_overview.csv"
logs = basePath + "/logs.txt"
biberLizenz = 'unknown'
encoding = "utf-8"
author = 'learngerman'
org = 'learngerman'# 
orgLink = 'https://learngerman.dw.com'
processed_files = basePath +  "processed_biber_files.txt"


def crawl_meta(link):
    real_link= str("https://learngerman.dw.com"+link)
    headers = { "X-Request-ID": str(uuid.uuid4()),
                    "From": "https://www.germ.univie.ac.at/projekt/latill/" }
    req = requests.get(real_link, headers = headers)
    data = req.text
    soup = BeautifulSoup(data, features="html.parser")

    print("I reached the meta method")



def crawl_text(link):
    real_link= str("https://learngerman.dw.com"+link)
    headers = { "X-Request-ID": str(uuid.uuid4()),
                    "From": "https://www.germ.univie.ac.at/projekt/latill/" }
    req = requests.get(real_link, headers = headers)
    data = req.text
    soup = BeautifulSoup(data, features="html.parser")
    print("I reached the text method")

def crawl_article_page(actual_link):
     # get html of article website
     real_link= str("https://learngerman.dw.com"+actual_link)
     headers = { "X-Request-ID": str(uuid.uuid4()),
                    "From": "https://www.germ.univie.ac.at/projekt/latill/" }
     req = requests.get(real_link, headers = headers)
     data = req.text
     soup = BeautifulSoup(data, features="html.parser")

    # get link to "landeskunde"
     nav_button = soup.find("ul", {"class" : "lesson-nav-menu"})
     children = nav_button.findChildren(recursive=False)
     print("current link", actual_link)
     for c in children:
         print("---------------------------")
         try:
            text = c.get_text()
            print(text)
            if (text == "Landeskunde"):
                print("found link to Landeskunde")
                childLink = c.find("a",href=True)
                if childLink is not None:
                    link=childLink['href']
                    print("link: ", link)
                    crawl_meta(link)
                    crawl_text(link)
         except:
             print("NoneType Landeskunde")
             
         
       
     

def Crawl():
    basePageURL = "https://learngerman.dw.com/de/nicos-weg/c-36519687"
    headers = { "X-Request-ID": str(uuid.uuid4()),
                    "From": "https://www.germ.univie.ac.at/projekt/latill/" }
    req = requests.get(basePageURL, headers = headers)
    data = req.text
    soup = BeautifulSoup(data, features="html.parser")
     
    links = soup.find_all("a", {"class":"sc-faUpoM lbXSjK"})
    i = 0
    for link in links: 
         if i <2:
            print("Found the URL: ", link.get('href'))   
            actual_link = link.get('href')     
            i = i+1   
            crawl_article_page(str(actual_link))
         else: 
            exit()
#


    

Crawl()
