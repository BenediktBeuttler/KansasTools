from ast import If
from fileinput import filename
import os
from bs4 import BeautifulSoup
import requests
import codecs
import re
import csv

basePath = "bpbCrawler"
metaFileName = basePath + "/bpbPolDemGrunGesetzmeta.csv"
baseUrl = "https://www.bpb.de"
baseBpbUrl = "https://www.bpb.de/themen/menschenrechte/grundgesetz/"
processedTextsFile = basePath + "/processed-bpbPolDemGrunGesetz-files.txt"
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
        for link in soup.find_all("a", {"class":"teaser-text__link"}):
            link_url = "https://www.bpb.de"+link.get('href')
            if link_url == "https://www.bpb.de/themen/menschenrechte/grundgesetz/212966/alqanwn-alasasy-ljmhwryt-almanya-alathadyt/":
                continue
            if link_url == "https://www.bpb.de/themen/menschenrechte/grundgesetz/213412/federal-almanya-cumhuriyeti-anayasasi/":
                continue
            file.write(link_url + '\n')
            url_list.append(link_url)
    
    return url_list
    
    #print("Links have been written to 'links.txt' file.")

    #inhalt2 = doc.find_all("a", {"class":"teaser-text__link"})
    #print(inhalt2.)

    #pattern = r'href="(/themen/menschenrechte/grundgesetz/\d+/[\w-]+/)"'
    #links = re.findall(pattern, doc)
    #for link in links:
        #print(link)

#print(get_dropdown_urls(baseBpbUrl))


#get_dropdown_links(baseBpbUrl)

    # slot=item
    # slot=submenu

def addToMetaFile(filename, title, url, mainTopic, lizenz, author, org, orgLink):
    # check if file exist
    if os.path.exists(metaFileName):
        try:
            with codecs.open(metaFileName, 'r', encoding) as file:
                # Create a CSV reader object
                csv_reader = csv.reader(file)
                
                # Check if the CSV file is empty
                is_empty = not any(row for row in csv_reader)
                
                if is_empty:
                    with codecs.open(metaFileName, 'a', encoding) as f:
                        f.write(f'\n{"File.Name"}\t{"Title"}\t{"URL"}\t\t{"Main.Topic"}\t\t{"Lizenzart"}\t{"Author"}\t\t{"Second.Author"}\t\t{"Organization"}\t{"Organization.Link"}')
                        f.close()
                else:
                    with codecs.open(metaFileName, 'a', encoding) as f:
                        f.write(f'\n{filename}\t{title}\t{url}\t\t{mainTopic}\t\t{lizenz}\t{author}\t\t{""}\t\t{org}\t{orgLink}')
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
            try:
                with codecs.open(metaFileName, 'r', encoding) as file:
                    # Create a CSV reader object
                    csv_reader = csv.reader(file)
                    
                    # Check if the CSV file is empty
                    is_empty = not any(row for row in csv_reader)
                    
                    if is_empty:
                        with codecs.open(metaFileName, 'a', encoding) as f:
                            f.write(f'\n{"File.Name"}\t{"Title"}\t{"URL"}\t\t{"Main.Topic"}\t\t{"Lizenzart"}\t{"Author"}\t\t{"Second.Author"}\t\t{"Organization"}\t{"Organization.Link"}')
                            f.close()
                    else:
                        with codecs.open(metaFileName, 'a', encoding) as f:
                            f.write(f'\n{filename}\t{title}\t{url}\t\t{mainTopic}\t\t{lizenz}\t{author}\t\t{""}\t\t{org}\t{orgLink}')
                            f.close()
            except FileNotFoundError:
                print(f"The CSV file '{metaFileName}' does not exist.")
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                
                
def saveFile(fileName, text):
    # save raw text file
    with codecs.open(basePath+"/txts/"+fileName, 'w', encoding) as f:
        f.write(f'{text}')
        f.close()


# # get url from .txt file
# def getEachUrl():
#     with codecs.open(basePath+'/urls.txt','r') as file:
#         for line in file:
#             url = line.strip() 
#             print(url)


def log_filenames(title):
    processedTexts = [] 
    with codecs.open(processedTextsFile, "r", encoding) as f:
        for line in f:
            if line == title:
                continue
            else:
                processedTexts.append(title.strip())


def crawlNewsPage():
    cleanupBeforehand()
    
    # need to call a function to get each url from the file/list
    url_list = get_dropdown_urls(baseBpbUrl)
    for url in url_list:
        #url = "https://www.bpb.de/themen/menschenrechte/grundgesetz/44186/einleitung-und-praeambel/"
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


        # add results to metacsv
        addToMetaFile(filename, title, url, "", "", "", org, orgLink)
        
        # processedTexts = []
        # #if the file exist
        #     with codecs.open(basePath+"/processedTextsFile.txt", "r", encoding) as f:
        #         for line in f:
        #             if line == title:
        #                 continue
        #             else:
        #                 processedTexts.append(title.strip())
        #else:
            #append title to file


        # find text
        text = ""
        content = soup.find("div", {"class": "text-content spacer-horizontal__inset-narrow title2margin"})
        contentChildren = content.findChildren()
        for contentChild in contentChildren:
            text += "\n" + contentChild.get_text().strip()

            text = re.sub(r'([\r\n])+', r'\r\n', text)
            fileName = re.sub('[^A-Za-zäöüÄÖÜß0-9]+', '', title) + ".txt"

        #replace with save to file later
        saveFile(filename,text)
        #print(text)
    
            
        # text_list = []

        # with codecs.open(basePath+'/text.txt', 'w', encoding) as file:
        #     for link in soup.find_all("a", {"class":"teaser-text__link"}):
        #         link_url = "https://www.bpb.de"+link.get('href')
        #         if link_url == "https://www.bpb.de/themen/menschenrechte/grundgesetz/212966/alqanwn-alasasy-ljmhwryt-almanya-alathadyt/":
        #             continue
        #         if link_url == "https://www.bpb.de/themen/menschenrechte/grundgesetz/213412/federal-almanya-cumhuriyeti-anayasasi/":
        #             continue
        #         file.write(link_url + '\n')
        #         url_list.append(link_url)
        
        # return url_list



            #if len(text) < 1:
                #return

            #while len(text[0].strip()) < 1:
                #text = text[1:]

            #saveFile(fileName, text)
            #addToMetaFile(fileName, textUrl, title, org, orgLink)

crawlNewsPage()



def crawler():
    # get urls
    # crawl for meta data and text
    # save meta data to meta file
    # save text to text files
    # 
    return





# def save_to_file(list):
#     #create file
#     with codecs.open(basePath+'/file.txt','w+') as f:
#         for url in list:
#             f.write('%s\n' %url)
#         print("success!")
#     f.close()


# def get_urls():
#     #get each url
#     file = open("file.txt","r")
#     url = file.read()
#     url_list = url.split("\n")
#     print(url_list)
#     file.close()


# l = ['Hello', 'test', 'test']
# save_to_file(l)
# print(get_urls())



#addDot = False
    #print(contentChild)
        # subtitle
    #class_name_pattern = re.compile(r'\btext-content\b', re.IGNORECASE)
    
    #print(contentChild.get_text())

    #if (contentChild.name == "p" and contentChild.get_text().split("\n").endswith(string.punctuation)):
        #addDot == False
        #print(contentChild)
    #if (contentChild.name == "p" and not contentChild.get_text().split("\n").endswith(string.punctuation)):
        #addDot == True
        #print(contentChild)

    #if addDot == False:
        #text += "\n" + contentChild.get_text().strip()
        #print(text)
    #else:
        #text += "\n" + contentChild.get_text().strip() + "."
        #print(text)



# def crawlNewsPage():
#     cleanupBeforehand()
    
    

#     # Get each url from the list
#     url_list = get_dropdown_urls(baseBpbUrl)
#     for url in url_list:
#         r = requests.get(url)
#         data = r.text
#         soup = BeautifulSoup(data, features="html.parser")

#         # search meta data
#         title = soup.find("meta", property="og:title")["content"]
#         org = soup.find("meta", property="og:site_name")["content"]
#         orgLink = baseUrl
#         filename = title+".txt"
#         filename = filename.replace(" ", "")

#         #print(filename+"\t"+title+"\t"+url+"\t"+org+"\t"+orgLink+"\t")
#         #addToMetaFile(filename, title, url, "", "", "", org, orgLink)

#         text = ""
#         content = soup.find("div", {"class": "text-content spacer-horizontal__inset-narrow title2margin"})
#         contentChildren = content.findChildren()
#         for contentChild in contentChildren:
#             text += contentChild.get_text().strip() + "\n" 

#             text = re.sub(r'([\r\n])+', r'\r\n', text)
#             fileName = re.sub('[^A-Za-zäöüÄÖÜß0-9]+', '', title) + ".txt"
        
#         lines = text.strip().split('\n')[1:]

#         # Join the lines back together with newline characters
#         new_text = '\n'.join(lines)
        
#         # check if file exist
#         if os.path.exists(metaFileName):
#             try:
#                 with codecs.open(metaFileName, 'r', encoding) as file:
#                     # Create a CSV reader object
#                     csv_reader = csv.reader(file)
                        
#                     # Check if the CSV file is empty
#                     is_empty = not any(row for row in csv_reader)
                        
#                     if is_empty:
#                         with codecs.open(metaFileName, 'a', encoding) as f:
#                             f.write(f'{"File.Name"}\t{"Title"}\t{"URL"}\t\t{"Main.Topic"}\t\t{"Lizenzart"}\t{"Author"}\t\t{"Second.Author"}\t\t{"Organization"}\t{"Organization.Link"}\n')
#                             addToMetaFile(fileName, title, url, "", "", "", org, orgLink)
#                             f.close()
#                     else:
#                         with codecs.open(metaFileName, 'a', encoding) as f:
#                             addToMetaFile(fileName, title, url, "", "", "", org, orgLink)
#                             f.close()
#             except FileNotFoundError:
#                 print(f"The CSV file '{metaFileName}' does not exist.")
#             except Exception as e:
#                 print(f"An error occurred: {str(e)}")
#         else: 
#             #write a file
#             with codecs.open(metaFileName, 'w', encoding) as file:
#                 # Create a CSV writer object
#                 csv_writer = csv.writer(file)
#                 with codecs.open(metaFileName, 'a', encoding) as f:
#                     f.write(f'{"File.Name"}\t{"Title"}\t{"URL"}\t\t{"Main.Topic"}\t\t{"Lizenzart"}\t{"Author"}\t\t{"Second.Author"}\t\t{"Organization"}\t{"Organization.Link"}\n')
#                     addToMetaFile(fileName, title, url, "", "", "", org, orgLink)
#                     f.close()
    
#         saveFile(fileName,new_text)
