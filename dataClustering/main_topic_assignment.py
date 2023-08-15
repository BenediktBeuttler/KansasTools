from HelperFunctions import *

import pickle
import matplotlib.pyplot as plt

# Enable logging for gensim - optional
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.ERROR)

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# ==================================================================================================================
# ==================================================================================================================
# THIS IS THE FINAL STEP IN THE PIPELINE. IT REQUIRES SOME ADJUSTMENT DEPENDING ON RESULTS FROM PREVIOUS STEPS
# ==================================================================================================================
# ==================================================================================================================

if __name__ == '__main__':

    # ==================================================================================================================
    # STEP 0: Set-up
    # ==================================================================================================================

    # output files

    # load resources from previous step
    modelListFile = "resources/topic_cluster/modelList-nouns.p"
    modelCoherenceFile = "resources/topic_cluster/modelCoherence-nouns.p"
    modelTopicFile = "resources/topic_assignment/topic_classification"
    id2wordPickleFile = "resources/nlp/id2word-nouns.p"
    textsPickleFile = "resources/nlp/texts-nouns.p"
    corpusPickleFile = "resources/nlp/corpus-nouns.p"
    lemmaPickleFile = "resources/nlp/corpusLemmas-nouns.p"
    fileNamePickleFile = "resources/nlp/corpusFileNames-nouns.p"

    # this has to be determined based on the output of the previous step
    model_number = 6  # model with 8 topics

    be_verbose = True

    # ==================================================================================================================
    # STEP 1: Load topic models and linguistic resources
    # ==================================================================================================================

    # topics
    model_list = pickle.load(open(modelListFile, "rb"))
    coherence_models = pickle.load(open(modelCoherenceFile, "rb"))

    # corpus data
    id2word = pickle.load(open(id2wordPickleFile, "rb"))
    texts = pickle.load(open(textsPickleFile, "rb"))
    corpus = pickle.load(open(corpusPickleFile, "rb"))
    corpus_lemmas = pickle.load(open(lemmaPickleFile, "rb"))
    corpus_file_names = pickle.load(open(fileNamePickleFile, "rb"))

    # ==================================================================================================================
    # STEP 2 get model with each potential topic distrubition
    # ==================================================================================================================

    best_model = model_list[model_number]
    # sanity check
    #print(get_aggregate_coherence(coherence_models[model_number]))

    print("\n".join(["{}: {}".format(t[0], t[1]) for t in best_model.show_topics(formatted=True)]))

    # Save topics for highest selected number of topics
    df_dominant_topic = format_topic_df(optimal_model=best_model,
                                        corpus=corpus,
                                        texts=corpus_lemmas,
                                        corpus_file_names=corpus_file_names,
                                        verbose=be_verbose)

    # df_dominant_topic.columns = ['Document_No', 'Topic_Dominant', 'Topic_Perc_Contrib', 'Topic_Keywords', 'Text']

    df_dominant_topic.to_csv("{}-{}.csv".format(modelTopicFile, model_number+2),
                             sep="\t", index=False)

    pickle.dump(df_dominant_topic, open("{}-{}.p".format(modelTopicFile, model_number+2), "wb"))