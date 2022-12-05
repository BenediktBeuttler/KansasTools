# fill dict with filname-catIndex from cat_mapping_slim.txt/adjustment file
# go through tsv line by line
# check if filename is in key of dict and get value (translated into correct category)

import pandas as pd
import codecs

metaFile = "D:\\Repos\\kansas\\data\\new_corpus\\alpha-corpus-meta_full_cat_matched.tsv"
metaFilenameConst = 'File.Name'
metaTopicConst = 'Main.Topic'
metaDf = pd.read_csv(metaFile, encoding='UTF-8', on_bad_lines='skip', sep='\t', names=["File.Name",	"Title", "URL",	"Main.Topic", "Lizenzart", "Author", "Second.Author", "Organisation", "Organisation.Link"])
metaDf.fillna("NA", inplace=True)
# metaDf = metaDf.reset_index()
# , dtype={"File.Name": "string", "Title": "string", "URL": "string", "Main.Topic": "string", "Lizenzart": "string", "Author": "string", "Second.Author": "string", "Organisation": "string", "Organisation.Link": "string"}

mapFile = "DocNameCatChecker/cat_adjustments.txt"
# mapFile = "CategorySelector/cat_mapping_slim.txt"
mapFilenameConst = 'name'
mapFileTopicConst = 'cat'
mapDf = pd.read_csv(mapFile, encoding='ISO-8859-1', on_bad_lines='skip', sep='\t', dtype={"name": "string", "cat": "string"})
# mapDf = mapDf.reset_index()
# create dict from this df
mapDict = dict(zip(mapDf.name, mapDf.cat))
# print(list(mapDict.items())[:4])
# exit()

sourcesToSkip = ["bpb", "curve ii", "stiftung lesen", "aok", "giz", "evideo", "knotenpunkte", "alphagrund", "dgb mento pro"]
catMapping = {
    "0":"Politik und Wirtschaft",
    "1":"Verkehr, Sicherheit und Nachrichten",
    "2":"Medien und Kommunikation",
    "3":"Gesellschaft und Lebenswelten",
    "4":"Gesundheit",
    "5":"Geografie und Geschichte",
    "6":"Sport und Kultur",
    "7":"Natur und Umwelt",
    "8":"Arbeit"
}

logs = "TsvCatMapping/logs.txt"
def logIt (text):
    with codecs.open(logs, 'a', "utf-8") as f:
            f.write(text + "\n")
            f.close()
    print(text)

# print(metaDf.iloc[1])

for metaIndex, metaRow in metaDf.iterrows():
    metaFilename = metaRow[metaFilenameConst]
    logIt("meta filename: " + metaFilename)
    if metaFilename.split("/",1)[0].lower() not in sourcesToSkip:
        if metaFilename in mapDict:
            # get value of found key (cat_nr from dict)
            mapCat = mapDict[metaFilename]
            # set new value in metafile
            metaDf.at[metaIndex, metaTopicConst] = catMapping[mapCat]
            logIt("for " + metaFilename + ": " + str(metaRow[metaTopicConst]))
            logIt("______")
        
        # for mapIndex, mapRow in mapDf.iterrows():
        #     mapFilename = mapRow[mapFilenameConst]
        #     mapCat = mapRow[mapFileTopicConst]
        #     if metaFilename == mapFilename:
        #         # logIt("convert " + str(mapCat) + " to " + str(catMapping[mapCat]))
        #         metaDf.at[metaIndex, metaTopicConst] = catMapping[mapCat]
        #         # metaRow[metaTopicConst] = catMapping[mapCat]
        #         logIt("for " + metaFilename + ": " + str(metaRow[metaTopicConst]))
        #         logIt("______")


# print(metaDf.iloc[1])
metaDf.to_csv("alpha-corpus-meta_full_cat_matched_adjusted.tsv", header=None, encoding='utf-8', index=False, sep='\t', mode='a')
