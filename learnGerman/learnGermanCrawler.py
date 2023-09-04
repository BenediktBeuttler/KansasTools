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



def write_to_processedFiles(fileName):  
     with codecs.open(processed_files, 'a', encoding) as f:
        f.write(fileName)
        f.close()


def write_to_logs(url):
 with codecs.open(logs, 'a', encoding) as f:
        f.write("checking: " + url + "\n")
        f.close()

def safe_text_in_file(fileName, text):
     actual_fileName = basePath+ "/txts/" + fileName
     with codecs.open(actual_fileName, 'a', encoding) as f:
        f.write(text)
        f.close()


def add_to_metaFile(fileName, title, link):
    with codecs.open(metaFileName, 'a', encoding) as f:
        f.write(f'\n{fileName}\t{title}\t{link}\t\t{learnGermanLizenz}\t{author}\t\t{org}\t{orgLink}')
        f.close()
        print("Iam after close statement")    


def add_to_metaFile2(meta_title, url, cleaned_bereich):        
    with codecs.open(metaFile2, 'a', encoding) as p: 
        p.write(f'{meta_title}, {url}, {cleaned_bereich}\n')
        p.close()



def crawl_meta_and_text(link):  
    headers = { "X-Request-ID": str(uuid.uuid4()),
                    "From": "https://www.germ.univie.ac.at/projekt/latill/" }
    req = requests.get(link, headers = headers)
    data = req.text
    soup = BeautifulSoup(data, features="html.parser")

    print("--------------------------------------------")
    
    pre_title = soup.title.get_text()
    title = re.sub(r'\|.*', '', pre_title)
    print(title)


    fileName  = (re.sub('[^a-zA-Z0-9äöüÄÖÜß \n\.]', " ", title)).replace(" ", "") + ".txt"
    print(fileName)
    add_to_metaFile(fileName, title, link)
    add_to_metaFile2(fileName, title, link)

    
    text = ""

    print("I reached the text method")
    parent = soup.find("div", {"class" : "richtext-content-container sc-bTfYFJ byzRmI"})
    childrenP = parent.find("p")
    text = childrenP.get_text().strip()
    print(text)
    # return
    # for child in children:
    #     print("------")
    #     print(child)
    #     if (child.name != "figure"):
    #         txt = child.get_text().strip()
    #         if ((txt != "null") and (txt !="iStockphoto")):
    #             text += txt + " "
    #         else: 
    #             continue
    # # print(text)
    safe_text_in_file(fileName, text)
    write_to_processedFiles(fileName)



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
        if (c.get_text()) == "Landeskunde":
            #print(c.get_text())
            href = c.get('href')
            if href is not None: 
                link = "https://learngerman.dw.com" + str(href)
                print("not None   ", link)
                write_to_logs(str(link))
                crawl_meta_and_text(link)
            else: 
                link = "https://learngerman.dw.com" + str(href)
                print("is None   ",link )
            
          #  print("i reached the crawl_meta method. THis is the lnk: ", link)
            #crawl_meta(link)
            
            # link is None # why is that so?
         

   # print("Number of non-None links to Landeskunde:")

            
             #crawl_text(link)
             
         
       
     

def crawl():
    basePageURL = "https://learngerman.dw.com/de/nicos-weg/c-36519687"
    headers = { "X-Request-ID": str(uuid.uuid4()),
                    "From": "https://www.germ.univie.ac.at/projekt/latill/" }
    req = requests.get(basePageURL, headers = headers)
    data = req.text
    soup = BeautifulSoup(data, features="html.parser")
     
    links = soup.find_all("a", {"class":"sc-faUpoM lbXSjK"})
    i = 0
    for link in links: 
        # if i <2:
            print("Found the URL: ", link.get('href'))   
            link = link.get('href')     
            actual_link = str("https://learngerman.dw.com/"+link)
            crawl_article_page((actual_link))
        # else: 
         #   exit()
    print(i)
#


#crawl_article_page("https://learngerman.dw.com/de/nehmen-sie/l-40507920")
crawl_meta_and_text("https://learngerman.dw.com/de/verloren-gefunden/l-40375182/rs-39360345")
exit()
# crawl()