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
basePath = "biberCrawler_s_blog"
metaFileName = basePath + "/bibermeta.tsv"
logs = basePath + "/logs.txt"
# biberLizenz = ''
encoding = "utf-8"
biberAuthor = 'Das Biber'
org = 'das Biber'# 
orgLink = 'https://www.dasbiber.at/'
biberLizenz="licence_na#"
topic="topic_na#"
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
            first_line = lines[0].rstrip('\n')
            f.seek(0)
            f.truncate(0)
            f.write(first_line)

# Clear the log file except for the first line
clear_file_except_first_line(metaFileName, encoding)
def addToMetaFile(meta_title, url, fileName, author):
    auth = ""
    if(not author or author == "" or author == None):
        auth = biberAuthor
    else:
        auth = author
    with codecs.open(metaFileName, 'a', encoding) as f:
        f.write(f'\n{fileName}\t{meta_title}\t{url}\t{topic}\t{biberLizenz}\t{auth}\tNA\t{org}\t{orgLink}')
        f.close


def safe_text_in_file(fileName, text):
     actual_fileName = basePath+ "/txts/" + fileName
     with codecs.open(actual_fileName, 'a', encoding) as f:
        f.write(text)
        f.close()

def check_and_get_author(snippet_text):
    prefixes = ['von ', 'Von ']
    result = None

    for prefix in prefixes:
        if snippet_text.startswith(prefix):
            result = snippet_text[len(prefix):]
            break

    if result:
        result = result.replace("Collagen", "").replace("Fotos", "").replace("Foto", "").replace(":", "").strip().replace("()", "")

    return result

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

def crawl_page_meta_and_text(url__link, authorStr):
     
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
        # write_to_logs("clean title: " + clean_title)

    clean_filename = clean_title_for_filename(clean_title)+".txt"
    # is already in processedtexts, so dont do anything
    if clean_filename in processedTexts:
        write_to_logs("already processed, skipped")
        return
    # write_to_logs("clean filename: " + clean_filename)

    # find text
    text = ""
    text_to_add = ""
    author_string = authorStr
    parent = soup.find("div", {"class":"section field field-name-body field-type-text-with-summary field-label-hidden"})


    if parent:
        # write_to_logs("1")
        # Finden Sie alle <p> Tags mit der Klasse "Text" im übergeordneten div
        p_tags = parent.find_all("p")

        for p in p_tags:
            # Check if there is any descendant with class "media media-element-container media-default"
            if p.find(class_="media media-element-container media-default"):
                continue 
            
            # Get and clean the text from the <p> tag
            p_text = p.get_text().strip()

            # if any(keyword in p_text for keyword in ["Text:", "Foto:"]):
            #     continue

            # Check if the text does not end with any of the specified punctuation marks
            if all(not p_text.endswith(punct) for punct in ['.', ':', '!', '?', '"', '\'', '“']):

                # Check if the <p> tag contains a <strong> tag                
                text_to_add = f" {p_text}. "
            else:
                text_to_add = p_text
            
            # Check if the last character in text is not an empty space
            if text and not text.endswith(' '):
                text += ' '
            # if there are fewer words than 2 and less chars than 6, skip
            if len(text_to_add.split()) < 2 and len(text_to_add) < 6:
                continue

            # Append text_to_add to text
            text += text_to_add     
        
    # skip texts, shorter than 10 characters
    if len(text) < 10:  
        return
    if text.startswith(" "):
        text = text[1:]
    text = text.replace("  ", " ")

    def process_text(text):
        lines = text.split('\n')
        processed_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Add a period if the line does not end with typical sentence-ending punctuation
            if not line.endswith(('.', '!', '?', '."', '!"', '?"', ':', '."', ':"', '”', '.“')):
                line += '.'
            processed_lines.append(line)
        
        return ' '.join(processed_lines)

    text = process_text(text)
    
    # write_to_logs("Author: " + str(author_string))
    # write_to_logs(text)
    # write_to_logs("################################################\n")
    
    # only do those things, if they are not already in the processed files data (has been crawled)
    if clean_filename not in processedTexts:
        clean_filename = clean_filename.replace("..",".")
        # pass on specific author, which gets replaced with das biber if there is no spec author
        addToMetaFile(clean_title, url__link,  clean_filename, author_string)
        write_to_logs("saving: " + clean_filename)
        
        # safe text in for it created file
        safe_text_in_file(clean_filename, text)
        write_to_processedFiles(clean_filename)

def Crawl():    
    basePageURL = "https://www.dasbiber.at/schueler/blog"
    for i in range(0,73):#73
        write_to_logs("i: " + str(i))
        if i == 0:
            get_each_URL(basePageURL)
        else:            
            newPageURL = basePageURL + "?page=" +str(i)
            get_each_URL(newPageURL)
        
def get_each_URL(newPageURL):
    baseURL = "https://www.dasbiber.at"
    r = requests.get(newPageURL)
    data = r.text
    soup = BeautifulSoup(data, features="html.parser")    

    # Find the div with class containing "views-view-grid cols-3"
    div_rows = soup.find('div', class_="views-view-grid cols-3")

    # Iterate through all child elements of the div with class "views-view-grid cols-3"
    for div_row in div_rows.find_all('div', recursive=False):  # Only direct children
        for div_col in div_row.find_all('div', recursive=False):  # Only direct children
            authorStr = ""
            # Find the nested div with class "views-field views-field-title" and "views-field views-field-name"
            nested_author_div = div_col.find('div', class_="views-field views-field-name")
            # Extract and print the links in each nested div
            # for name_div in nested_author_div:
            link_tag = nested_author_div.find('a')  # Find the <a> tag
            if link_tag and 'href' in link_tag.attrs:
                authorStr = link_tag.get_text().strip()

            nested_title_div = div_col.find('div', class_="views-field views-field-title")
            # Extract and print the links in each nested div
            # for title_div in nested_title_div:
            link_tag = nested_title_div.find('a')  # Find the <a> tag
            if link_tag and 'href' in link_tag.attrs:
                link = link_tag['href']
                if "sponsoren" in link:
                    continue
                finalLink = baseURL + link
                write_to_logs(authorStr + ": " + finalLink)
                crawl_page_meta_and_text(finalLink, authorStr)
           
################# MAIN CODE #################
# crawl_page_meta_and_text("https://www.dasbiber.at//schueler/blog/liebeskummer-macht-einen-menschen-kaputt", "Test")
# crawl_page_meta_and_text("https://www.dasbiber.at/content/time-say-gudbaj")
# crawl_page_meta_and_text("https://www.dasbiber.at/content/energie-sparen-gut-fuers-geldboerserl-und-fuers-klima")
# crawl_page_meta_and_text("https://www.dasbiber.at/content/wie-ich-zum-islam-konvertiert-bin")
#get_each_URL("https://www.dasbiber.at/articles")
# exit()
Crawl()
# exit()