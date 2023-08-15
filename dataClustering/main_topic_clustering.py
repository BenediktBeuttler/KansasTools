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
# THIS IS THE SECOND STEP IN THE PIPELINE. IT CAN BE RUN FROM THE COMMAND LINE
# ==================================================================================================================
# ==================================================================================================================

if __name__ == '__main__':

    # ==================================================================================================================
    # STEP 0: Set-up
    # ==================================================================================================================

    # output files
    modelListFile = "resources/topic_cluster/modelList-nouns.p"
    modelCoherenceFile = "resources/topic_cluster/modelCoherence-nouns.p"
    modelTopicFile = "resources/topic_cluster/topic_classification-"
    plotFile = "resources/topic_cluster/n_topics.png"
    coherenceTableFile = "resources/topic_cluster/coherence_table.csv"

    # settings
    nTopics = 30
    nSteps = 1
    nStart = 2
    be_verbose = True
    showPlot = True

    # external resource
    malletPath = "/Users/zweiss/Documents/mallet-2.0.8/bin/mallet"

    # load files from previous step
    id2wordPickleFile = "resources/nlp/id2word-nouns.p"
    textsPickleFile = "resources/nlp/texts-nouns.p"
    corpusPickleFile = "resources/nlp/corpus-nouns.p"
    lemmaPickleFile = "resources/nlp/corpusLemmas-nouns.p"


    # ==================================================================================================================
    # STEP 1: Load NLP annotated corpus data
    # ==================================================================================================================

    id2word = pickle.load(open(id2wordPickleFile, "rb"))
    texts = pickle.load(open(textsPickleFile, "rb"))
    corpus = pickle.load(open(corpusPickleFile, "rb"))
    corpus_lemmas = pickle.load(open(lemmaPickleFile, "rb"))

    # ==================================================================================================================
    # STEP 2: Calculate coherence of different topic clusterings
    #         Note: This can take a long time to run.
    # ==================================================================================================================

    #model_list, coherence_models = compute_coherence_values(dictionary=id2word, corpus=corpus, texts=corpus_lemmas,
    #                                                        mallet_path=malletPath, start=nStart, limit=nTopics,
    #                                                        step=nSteps, be_verbose=False)

    if be_verbose:
        print("Pickling topic models")
    #pickle.dump(model_list, open(modelListFile, "wb"))
    #pickle.dump(coherence_models, open(modelCoherenceFile, "wb"))

    model_list = pickle.load(open(modelListFile, "rb"))
    coherence_models = pickle.load(open(modelCoherenceFile, "rb"))

    coherence_values = [get_aggregate_coherence(c_cohm) for c_cohm in coherence_models]

    # ==================================================================================================================
    # STEP 3: Determine the right number of topics (manual step)
    # ==================================================================================================================

    # Show graph
    limit = nTopics;
    start = nStart;
    step = nSteps;
    x = range(start, limit, step)
    plt.plot(x, coherence_values)
    plt.xlabel("Num Topics")
    plt.ylabel("Coherence score")
    plt.legend(("coherence_values"), loc='best')
    if showPlot:
        plt.show()
    plt.savefig(plotFile)

    # Print the coherence scores
    if be_verbose:
        print("Saving coherence table")
    with open(coherenceTableFile, "w") as outstr:
        outstr.write("N.Topics; Coherence.Score"+os.linesep)
        for m, cv in zip(x, coherence_values):
            outstr.write("{}; {}{}".format(m, cv, os.linesep))
            print("Num Topics =", m, " has Coherence Value of", round(cv, 4))
