import os
import codecs
from fnmatch import fnmatch
import pandas as pd

file = "CategorySelector/topic_classification-8_utf8.csv"
newFilesFolderPath = "D:\\Repos\\kansas\\data\\new_corpus\\texts"
catList = ["*politi*", "*wirtschaft*", "*verkehr*", "*sicherheit*", "nachrichten", "*medien*", "kommunikation", "*gesellschaft*", "*gesund*", "*sport*", "*kultur*", "*nat?r*", "*umwelt*", "*geograf*", "*geschicht*"]
# catList = ["*wirtschaft*"]
substr = "/Users/zweiss/Documents/Forschung/Projekte/kansas/texts/"
substr2 = "D:\\Repos\\kansas\\data\\new_corpus\\texts\\"
filenameConst = 'File_Name'
topicConst = 'Dominant_Topic'
percConst = 'Perc_Contribution'

logs = "DocNameCatChecker/logs.txt"

def logIt (text):
    with codecs.open(logs, 'a', "utf-8") as f:
            f.write(text + "\n")
            f.close()
    print(text)

# clear log
with codecs.open(logs, 'w', "utf-8") as f:
            f.write("")
            f.close()


df = pd.read_csv(file, encoding='utf8', on_bad_lines='skip', usecols = [i for i in range(5)], sep='\t', dtype={"index": int, "Dominant_Topic": int, "Perc_Contribution": float, "File_Name": "string"})
df = df.reset_index()
# zarahs link : cat_nr
processedFiles = {}


for index, row in df.iterrows():
    filename = row[filenameConst]
    if filename not in processedFiles:           
        currFn = df[filenameConst]== filename
        currDf = df[currFn]
        maxVal = currDf[percConst].max()
        maxEntry = currDf[currDf[percConst] == maxVal]
        # line = str(filename) + "," + str(maxEntry['Dominant_Topic'].iloc[0]) + "," + str(maxEntry['Perc_Contribution'].iloc[0])
        processedFiles[filename] = str(maxEntry[topicConst].iloc[0])

# get all text names in new corpus folders
for path, subdirs, files in os.walk(newFilesFolderPath):
    for name in files:
        # logIt(name)
        for cat in catList:
            # print("2")
            if fnmatch(name.lower(), cat.lower()):
                # logIt("check: " + name.lower() + " ---- " + cat.lower())
                for key in processedFiles:
                    # print("3")
                    relFilePath = os.path.join(path, name).replace(substr2,"").replace("\\","/")
                    # logIt(relFilePath)
                    relKey = key.replace(substr, "")
                    # logIt(relKey)
                    if relFilePath.__eq__(relKey):
                        logIt(relKey + "\t" + cat + "\t" + str(processedFiles[key]) )

