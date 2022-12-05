import pandas as pd
import os
import codecs

#### if there are duplicated files, delete the one with no "-clean" in it

# set base folder path
newFilesFolderPath = "D:\\Repos\\kansas\\data\\new_corpus\\texts"
# oldFilesFolderPath = "D:\\Repos\\kansas\\data\\old_corpus\\texts"
topicFile = "CategorySelector/topic_classification-8_utf8.csv"
filenameConst = 'File_Name'
substr1 = "/Users/zweiss/Documents/Forschung/Projekte/kansas/texts/"
substr2 = "D:\\Repos\\kansas\\data\\new_corpus\\texts\\"
# substr3 = "D:\\Repos\\kansas\\data\\old_corpus\\texts\\"

logs = "DocNameChecker/logs.txt"

def logIt (text):
    with codecs.open(logs, 'a', "utf-8") as f:
            f.write(text + "\n")
            f.close()
    print(text)

# clear log
with codecs.open(logs, 'w', "utf-8") as f:
            f.write("")
            f.close()

df = pd.read_csv(topicFile, encoding='utf8', on_bad_lines='skip', usecols = [i for i in range(5)], sep='\t', dtype={"index": int, "Dominant_Topic": int, "Perc_Contribution": float, "File_Name": "string"})
df = df.reset_index()
fileNamesCsv = []
fileNamesFolder = {}

# store all filename from csv in a list
for index, row in df.iterrows():
    filenameLong = row[filenameConst]
    filename = str(filenameLong).rsplit('/',1)[-1]
    if filename not in fileNamesCsv:
        fileNamesCsv.append(filename)
        # print(filename)

# get all text names in new corpus folders
for path, subdirs, files in os.walk(newFilesFolderPath):
    for name in files:
        relPath = os.path.join(path, name).replace(substr2,"")
        fileNamesFolder[relPath] = name


for namePath in list(fileNamesFolder.keys()):
    name = str(namePath).rsplit('\\',1)[-1]
    # check if this file is in csv list
    # print("check: " + str(name))
    if name not in fileNamesCsv:
        # log what was present in folder, but not in csv
        logIt(namePath)
