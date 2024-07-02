from ast import If
from fileinput import filename
from bs4 import BeautifulSoup
import requests
import codecs
import re
import uuid
import unicodedata

## TODO: https://www.dasbiber.at/blog


# Variables which have the same value for all articles
basePath = "biberCrawler2"
metaFileName = basePath + "/bibermeta.csv"
logs = basePath + "/logs.txt"
biberLizenz = ''
encoding = "utf-8"
biberAuthor = 'das Biber'
org = 'das Biber'# 
orgLink = 'https://www.dasbiber.at/'
processed_files = basePath +  "/processed_biber_files.txt"


# Clear the log file contents
with codecs.open(logs, 'w', encoding) as f:
    f.truncate(0) 

def write_to_logs(text):
 with codecs.open(logs, 'a', encoding) as f:
        f.write(text + "\n")
        f.close()
        print(text)

# Clear processedTexts
processedTexts = []  
# check if the text has been crawled before
with codecs.open(processed_files, "r", encoding) as f:
    for line in f:
        processedTexts.append(line.strip())

def write_to_processedFiles(fileName):  
     with codecs.open(processed_files, 'a', encoding) as f:
        f.write(f'{fileName}\n')
        f.close()

# Clear metafile
# Function to clear the log file except for the first line
def clear_file_except_first_line(file, encoding):
    with codecs.open(file, 'r+', encoding) as f:
        lines = f.readlines()
        if lines:
            first_line = lines[0]
            f.seek(0)
            f.truncate(0)
            f.write(first_line)

# Clear the log file except for the first line
clear_file_except_first_line(metaFileName, encoding)
def addToMetaFile(meta_title, url, fileName, author):
    auth = ""
    if(author == ""):
        auth = biberAuthor
    else:
        auth = author
    with codecs.open(metaFileName, 'a', encoding) as f:
        f.write(f'\n{fileName}\t{meta_title}\t{url}\t\t{biberLizenz}\t{auth}\t\t{org}\t{orgLink}')
        f.close


def safe_text_in_file(fileName, text):
     actual_fileName = basePath+ "/txts/" + fileName
     with codecs.open(actual_fileName, 'a', encoding) as f:
        f.write(text)
        f.close()

def clean_title_for_filename(title):
    # Replace German umlauts and ß
    title = title.replace('ß', 'ss')
    title = title.replace('ü', 'ue')
    title = title.replace('ä', 'ae')
    title = title.replace('ö', 'oe')
    title = title.replace('Ü', 'Ue')
    title = title.replace('Ä', 'Ae')
    title = title.replace('Ö', 'Oe')
    
    # Normalize the unicode string and replace accented characters with non-accented equivalents
    title = unicodedata.normalize('NFKD', title).encode('ASCII', 'ignore').decode('ASCII')

    # Remove special characters
    title = re.sub(r'[^\w\s]', '', title)

    # Replace spaces and periods with underscores, except for the last period
    title = re.sub(r'(?<!\.)\.(?!$)', '_', title)  # Replace all periods except the last one
    title = title.replace(' ', '')

    # Ensure the title is a valid filename by removing any trailing period
    if title.endswith('.'):
        title = title[:-1]

    return title

def crawl_page_meta_and_text(url__link):
     
    # get html of website
    headers = {

                "X-Request-ID": str(uuid.uuid4()),

                "From": "https://www.germ.univie.ac.at/projekt/latill/"

            }
    req = requests.get(url__link, headers = headers)
    data = req.text
    soup = BeautifulSoup(data, features="html.parser")
     
    # Extract the title from the <title> tag
    title_tag = soup.find('title')
    if title_tag:
        title_text = title_tag.get_text()

        # Use regex to remove the last part and clean the title
        clean_title = re.sub(r'\s*\|\s*dasbiber$', '', title_text)

        # Print the cleaned title
        write_to_logs("clean title: " + clean_title)

    # clean_fileName  = re.sub('[^a-zA-Z0-9äöüÄÖÜ \n\.]', " ", clean_title)
    # real_fileName = clean_fileName.replace(" ", "") + '.txt'
    clean_filename = clean_title_for_filename(clean_title)+".txt"
    write_to_logs("clean filename: " + clean_filename)

    # find text
    text = ""
    parent = soup.find("div", {"class":"node-content"})
    pattern = r'(?i)^von.*[^.?!]$'
    authorString = ""

    if parent:
        # Finden Sie alle <p> Tags mit der Klasse "Text" im übergeordneten div
        p_tags = parent.find_all("p", {"class": "Text"})

        for p in p_tags:
            # Überprüfen Sie, ob das <p> Tag nur ein <strong> Tag enthält
            strong_tag = p.find("strong")
            if strong_tag and len(p.contents) == 1:
                text = text + strong_tag.get_text().strip() + '.'
                write_to_logs(strong_tag.get_text().strip() + '.')
            else:
                text = text + p.get_text().strip()
            
    else:
        write_to_logs("Kein div mit der Klasse 'node-content' gefunden")
        
    # contentChildren = parent.findChildren(recursive=False)
    # for child in contentChildren:   
    #     # abfrage wenn div leer ist (kein text)
    #     if (child.name != "div", {"class":"media media-element container media-default"}):
    #         if (child.find("u")):
    #             continue
    #         childText = child.get_text()
    #         if (childText is not None):
    #             # check if there are authors mentioned in the text with prefix "von" regex
    #             if re.search(pattern, childText):
    #                 parenthPattern = r'\([^)]*\)'
    #                 authorString = childText.strip().replace("von","").replace("Von","").replace("Collagen","").replace("Fotos","").replace("Foto","").replace(":","")
    #                 # get specific author but remove parentheses if there are any
    #                 authorString = re.sub(parenthPattern, "", authorString).lstrip()
    #                 continue
    #             txt = childText.strip()
    #             if ((txt != "&nbsp") and (txt !="*BEZAHLTE ANZEIGE*")):
    #                 text += txt + " "
    #     else: 
    #         continue
        
        # skip texts, shorter than 10 characters
    if len(text) < 10:  
        return      
    
    write_to_logs("Author: " + authorString)
    write_to_logs(text)
    write_to_logs("\n################################################")
    
    # # only do those things, if they are not already in the processed files data (has been crawled)
    # if real_fileName not in processedTexts:
    #     real_fileName = real_fileName.replace("..",".")
    #     # pass on specific author, which gets replaced with das biber if there is no spec author
    #     addToMetaFile(meta_title, url__link,  real_fileName, authorString)
    #     write_to_logs("saving: " + real_fileName)
        
    #     # safe text in for it created file
    #     safe_text_in_file(real_fileName, text)
    #     write_to_processedFiles(real_fileName)


def Crawl():    
    basePageURL = "https://www.dasbiber.at/articles"
    for i in range(1,2):#322
        write_to_logs("i: " + str(i))
        if i == 0:
            get_each_URL(basePageURL)
        else:            
            newPageURL = basePageURL + "?page=" +str(i)
            get_each_URL(newPageURL)
         


def get_each_URL(newPageURL ):
    baseURL = "https://www.dasbiber.at"
    r = requests.get(newPageURL)
    data = r.text
    soup = BeautifulSoup(data, features="html.parser")    

    # Find the div with class containing "view-display-id-page_1"
    target_div = soup.find('div', class_="view-display-id-page_1")

    if target_div:
        # Inside the target div, find the nested divs with class "views-field views-field-title"
        nested_divs = target_div.find_all('div', class_="views-field views-field-title")

        # Extract and print the links in each nested div
        for nested_div in nested_divs:
            link_tag = nested_div.find('a')  # Find the <a> tag
            if link_tag and 'href' in link_tag.attrs:
                link = link_tag['href']
                finalLink = baseURL + link
                write_to_logs(finalLink)
                crawl_page_meta_and_text(finalLink)
                
    else:
        write_to_logs("No div found with the class containing 'view-display-id-page_1'")
            

################# MAIN CODE #################
# crawl_page_meta_and_text("https://www.dasbiber.at/content/meine-freundin-die-%E2%80%9Eterrorbraut%E2%80%9C")
crawl_page_meta_and_text("https://www.dasbiber.at/content/time-say-gudbaj")
# crawl_page_meta_and_text("https://www.dasbiber.at/content/3-minuten-mit-baraa-bolat")
#get_each_URL("https://www.dasbiber.at/articles")
# exit()
# Crawl()
# exit()