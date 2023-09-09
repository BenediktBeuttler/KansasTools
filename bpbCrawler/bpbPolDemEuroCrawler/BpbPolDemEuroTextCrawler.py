from ast import If
from fileinput import filename
from bs4 import BeautifulSoup
import requests
import codecs
import re
import os
import csv

basePath = "bpbCrawler/BpbPolDemEuroCrawler"
metaFileName = basePath + "/BpbPolDemEurometa.csv"
baseUrl = "https://www.bpb.de"
baseBpbUrl = "https://www.bpb.de/shop/zeitschriften/izpb/europaeische-union-345/"
processedTextsFile = basePath + "/processed-bpbPolDemEuro-files.txt"
logs = basePath + "/logs.txt"
bpbLizenz = "CC BY-NC-ND 2.0"
encoding = "utf-8"


def cleanupBeforehand():    
    # check if file exists
    if not os.path.exists(processedTextsFile):
        with codecs.open(processedTextsFile, 'w', encoding) as f:
                f.write("")
                f.close()


def get_dropdown_urls(url):

    result = requests.get(baseBpbUrl)
    soup = BeautifulSoup(result.text, "html.parser")

    inhalt = soup.find_all("a", {"slot":"item"})
    #print(inhalt)

    url_list = []

    with codecs.open(basePath+'/urls.txt', 'w', encoding) as file:
        #for link in soup.find_all(lambda tag: tag.name == 'a' and ("teaser-text__link" in tag.get("class") or "content-index__link" in tag.get("class"))):
        #for link in soup.find_all("a", {"class":"teaser-text__link"}):

        desired_classes = ["teaser-text__link", "content-index__link"]
        found_links = [link for link in soup.find_all("a") if any(cls in link.get("class", []) for cls in desired_classes)]
        for link in found_links:    
            link_url = "https://www.bpb.de"+link.get('href')
            
            file.write(link_url + '\n')
            url_list.append(link_url)
    
    return url_list


def addToMetaFile(filename, title, url, mainTopic, lizenz, author, org, orgLink):
    with codecs.open(metaFileName, 'a', encoding) as f:
        f.write(f'{filename}\t{title}\t{url}\t\t{mainTopic}\t\t{lizenz}\t{author}\t\t{""}\t\t{org}\t{orgLink}\n')
        f.close()
                
                
def saveFile(fileName, text):
    # save raw text file
    with codecs.open(basePath+"/txts/"+fileName, 'w', encoding) as f:
        f.write(f'{text}')
        f.close()


def checkFileExist(metaFileName):
    if os.path.exists(metaFileName):
        try:
            with codecs.open(metaFileName, 'r', encoding) as file:
                # Create a CSV reader object
                csv_reader = csv.reader(file)
                        
                # Check if the CSV file is empty
                is_empty = not any(row for row in csv_reader)
                        
                if is_empty:
                    with codecs.open(metaFileName, 'a', encoding) as f:
                        f.write(f'{"File.Name"}\t{"Title"}\t{"URL"}\t\t{"Main.Topic"}\t\t{"Lizenzart"}\t{"Author"}\t\t{"Second.Author"}\t\t{"Organization"}\t{"Organization.Link"}\n')
                        f.close()
        except FileNotFoundError:
            print(f"The CSV file '{metaFileName}' does not exist.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
    else: 
        #write a file
        with codecs.open(metaFileName, 'w', encoding) as file:
            # Create a CSV writer object
            csv_writer = csv.writer(file)
            with codecs.open(metaFileName, 'a', encoding) as f:
                f.write(f'{"File.Name"}\t{"Title"}\t{"URL"}\t\t{"Main.Topic"}\t\t{"Lizenzart"}\t{"Author"}\t\t{"Second.Author"}\t\t{"Organization"}\t{"Organization.Link"}\n')
                f.close()
    

def crawlNewsPage():
    #cleanupBeforehand()
    checkFileExist(metaFileName)

    # Get each url from the list
    url_list = get_dropdown_urls(baseBpbUrl)
    for url in url_list:
        print(url)
        r = requests.get(url)
        data = r.text
        soup = BeautifulSoup(data, features="html.parser")

        # search meta data
        title = soup.find("meta", property="og:title")["content"]
        org = soup.find("meta", property="og:site_name")["content"]
        orgLink = baseUrl

        filename = title+".txt"
        filename = filename.replace(" ", "")

        #print(filename+"\t"+title+"\t"+url+"\t"+org+"\t"+orgLink+"\t")
        #addToMetaFile(filename, title, url, "", "", "", org, orgLink)

        text = ""
        content = soup.find("div", {"class": "text-content spacer-horizontal__inset-narrow title2margin"})
        br_elements = soup.find_all(['br','br/'])
        #contentChildren = content.findChildren()
        #for contentChild in contentChildren:
            #text += contentChild.get_text().strip("<br>") + "\n" 

        # Extract the parent element containing the text
        text_parent = br_elements[0].find_parent()
        # Split the text by <br> or <br/> elements
        text_parts = text_parent.get_text(separator='<br>').split('<br>')

        # Print the split text parts
        for part in text_parts:
            
            text = re.sub(r'([\r\n])+', r'\r\n', text)
            fileName = re.sub('[^A-Za-zäöüÄÖÜß0-9]+', '', title) + ".txt"
        
            new_text = part.strip()
            #print(new_text)
        #lines = text.strip().split("<br>")[1:]

        # Join the lines back together with newline characters
        #new_text = '\n'.join(lines)
        
        addToMetaFile(fileName, title, url, "", bpbLizenz, "", org, orgLink)
    
        saveFile(fileName,new_text)

crawlNewsPage()
