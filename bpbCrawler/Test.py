from ast import If
from fileinput import filename
from bs4 import BeautifulSoup
import requests
import codecs
import re

basePath = "bpbPolDemGrunGesetzCrawler"
metaFileName = basePath + "/bpbPolDemGrunGesetzmeta.csv"
baseBpbUrl = "https://www.bpb.de/themen/menschenrechte/grundgesetz/"
processedTextsFile = basePath + "/processed-bpbPolDemGrunGesetz-files.txt"
logs = basePath + "/logs.txt"
bpbLizenz = " "
encoding = "utf-8"

# def logIt(text):
#     with codecs.open(logs, 'a', encoding) as f:
#         f.write(text + "\n")
#         f.close()
#     print(text)

# def simpleSanitizeText(textToClean):
#     textToClean = " ".join(textToClean.split())
#     return textToClean.replace("·", "")

# def get_dropdown_links(url):
#     result = requests.get(baseBpbUrl)
#     doc = BeautifulSoup(result.text, "html.parser")

#     inhalt = doc.find_all("a", {"slot":"item"})
#     #print(inhalt)

#     for link in doc.find_all("a", {"class":"teaser-text__link"}):
#         return "https://www.bpb.de"+link.get('href')
    


# def saveFile(fileName, text):
#     with codecs.open(basePath + "\\txts\\" + fileName, 'w', encoding) as f:
#         f.write(f'{text}')
#         f.close()
    
#     logIt("created - -" + fileName)

#     if fileName not in processedTexts:
#         with codecs.open(metaFileName, 'a', encoding) as f:
#             f.write(f'{fileName}\n')
#             f.close()
    
# def addToMetaFile(fileName, url, title, org, orgLink):
#     if fileName in processedTexts:
#         logIt("already exists in Meta: " + fileName)
#         return
    
#     with codecs.open(metaFileName, 'a', encoding) as f:
#         f.write(f'\n{fileName}\t{title}\t{url}\t\t{bpbLizenz}\t{author}\t\t{org}\t{orgLink}')
#         f.close()
    
#     logIt(str("added to Meta - " + title))


# def crawlNormalText(soup):
#     text = ""
#     textContentHtml = soup.find_all("div", {"class": ""})
#     for textContent in textContentHtml:
#         contentChildren = text.findChildren()
#         for contentChild in contentChildren:
#             if(contentChild.name=="" and "" in contentChild.get("class", [])):
#                 continue
#             if(contentChild.name=="p" and len(contentChild.get_text().strip())>1):
#                 text += "\n" + contentChild.get_text().strip()
#     return text


# def crawlNewsPage(textUrl):
#     r = requests.get(textUrl)
#     data = r.text
#     soup = BeautifulSoup(data, features="html.parser")

#     title = simpleSanitizeText(
#         soup.find("meta", property="og:title")["content"])
#     org = simpleSanitizeText(
#         soup.find("meta", property="og:site_name")["content"])
#     orgLink = baseBpbUrl

#     authorHtml = soup.find("div", {"class": "author author-first"})
#     author = simpleSanitizeText(authorHtml.get_text()).replace(" und ", ", ")
    
#     # get text
#     textHeaderHtml = soup.find("div", {"class": "nav-toc__header"})
#     textHeader = textHeaderHtml.find("h2").get_text().strip() + "."
#     text = textHeader

#     if disput:
#         # different crawling here
        
#         texts = soup.find_all("div", {"class": "left_floated"})
#         i = 0
#         for textDisput in texts:
#             specAuthor = ""
#             textChildren = textDisput.findChildren()
#             for textChild in textChildren:
#                 if (textChild.name == "h2" and "element-invisible" in textChild.get("class", [])):
#                     continue
#                 elif (textChild.name == "h2"):
#                     text += "\n" + textChild.get_text().strip() + "."
#                 if (textChild.name == "h3"):
#                     text += "\n" + textChild.get_text().strip() + "."
#                 if (textChild.name=="div" and "media media-element-container media-default" in textChild.get("class", [])):
#                     continue
#                 if (textChild.find("em")):        
#                     continue
#                 if (textChild.name == "p"):
#                     text += "\n" + textChild.get_text().strip()
            
#             specAuthor = author.split(", ")[i]
#             # print(specAuthor)
#             i += 1
            
#             fileName = re.sub('[^A-Za-zäöüÄÖÜß0-9]+', '', str(title + specAuthor)) + ".txt" 
#             text = simpleSanitizeText(re.sub(r'([\r\n])+', r'\r\n', text))

#             if len(text) < 1:
#                 return
            
#             while len(text[0].strip()) < 1:
#                 text = text[1:]

#             saveFile(fileName, text)
#             addToMetaFile(fileName, textUrl, title, specAuthor, org, orgLink)
#             # print("")
#             # print(text)
#             # print(fileName)
#             # print(textUrl, title, author, org, orgLink)
#             # print("------------------------------------")
#     else:
#         # normal text crawling
#         # get text    
#         text += "\n" + crawlNormalText(soup)
    
#         fileName = re.sub('[^A-Za-zäöüÄÖÜß0-9]+', '', title) + ".txt"
#         text = simpleSanitizeText(re.sub(r'([\r\n])+', r'\r\n', text))

#         if len(text) < 1:
#             return
        
#         while len(text[0].strip()) < 1:
#             text = text[1:]

#         saveFile(fileName, text)
#         addToMetaFile(fileName, textUrl, title, author, org, orgLink)
#         # print("")
#         # print(text)
#         # print(fileName)
#         # print(textUrl, title, author, org, orgLink)
#         # print("------------------------------------")
    

# get_dropdown_links("https://www.bpb.de/themen/menschenrechte/grundgesetz")



# 
url = "https://www.bpb.de/shop/zeitschriften/izpb/europaeische-union-345/324568/editorial/"
r = requests.get(url)
data = r.text
soup = BeautifulSoup(data, features="html.parser")

text = ""
content = soup.find("div", {"class": "text-content spacer-horizontal__inset-narrow title2margin"})

br_elements = soup.find_all(['br', 'br/'])
# Extract the parent element containing the text
text_parent = br_elements[0].find_parent()
# Split the text by <br> or <br/> elements
text_parts = text_parent.get_text(separator='<br>').split('<br>')

# Print the split text parts
for part in text_parts:
    print(part.strip())
    




#contentChildren = content.findChildren()
#for contentChild in contentChildren:
    #text += contentChild.get_text().strip() + "\n" 
    #text = re.sub(r'([\r\n])+', r'\r\n', text)
        
#lines = text.strip().split('\n')[1:]

# Join the lines back together with newline characters
#new_text = '\n'.join(lines)

#print(text)