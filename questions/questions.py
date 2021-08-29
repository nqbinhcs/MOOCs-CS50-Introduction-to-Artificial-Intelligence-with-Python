import nltk
import sys
import os
import string
import math
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn
from nltk.stem import PorterStemmer
from vectors import *

FILE_MATCHES = 1
SENTENCE_MATCHES = 1
lemmatizer = WordNetLemmatizer()
stemmer = PorterStemmer()


def main():
    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)
    # Prompt user for query
    query = set(tokenize(input("Query: ")))
    _query = query.copy()
    for word in _query:
        query.update(extend_words(word))
    print(query)

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)
    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences

    idfs = compute_idfs(sentences)
    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    files = dict()
    for filename in os.listdir(directory):
        with open(os.path.join(directory, filename)) as f:
            files[filename] = f.read()
    return files


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    # lowering and removing punctuation
    words = [word.lower().rstrip(string.punctuation)
             for word in nltk.word_tokenize(document) if any(c.isalpha() for c in word)]
    # filter out stopwords
    stopwords = set(nltk.corpus.stopwords.words("english"))
    words = [
        lemmatizer.lemmatize(word) for word in words if word not in stopwords]
    return words


def extend_words(_word):
    return set(closest_words(words[_word]))


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    # copy documents
    documents_copy = documents.copy()
    # initial set of words which are in documents
    words = set()
    for filename in documents_copy:
        for word_file in documents_copy[filename]:
            words.add(word_file)

    # initial frequency of word
    file_idfs = {word: 0 for word in words}

    # calculate the document which has a specific word
    for word in words:
        for filename in documents_copy:
            if word in documents_copy[filename]:
                file_idfs[word] += 1

    # number of document
    number_document = len(documents_copy)
    # calculate idf
    for word in file_idfs:
        file_idfs[word] = math.log(number_document / file_idfs[word])

    return file_idfs


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    # initial list of top n files which match to query
    top_files = []
    for file in files:
        # initial tf-idf for each document
        tf_idf_file = {word: 0 for word in query}
        # calculate frequency
        for word in files[file]:
            if word in query:
                tf_idf_file[word] += 1

        # calculate tf-idf
        for word in query:
            if word in idfs:
                tf_idf_file[word] *= idfs[word]

        # calcute score
        score = sum(tf_idf_file.values())

        top_files.append((file, score))

    # sorting by score
    top_files = sorted(top_files, key=lambda x: x[1], reverse=True)

    return [x[0] for x in top_files[:n]]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    # initial list of top sentences
    top_sentences = []
    for sentence in sentences:
        # calculate score
        score = sum(idfs[word]
                    for word in set(sentences[sentence]) if word in query)
        # calculate density
        density = sum(1 for word in set(sentences[sentence]) if word in query
                      ) / len(set(sentences[sentence]))
        top_sentences.append((score, density, sentence))

    # sorting by order: score, density
    top_sentences = sorted(top_sentences, reverse=True)
    return [x[2] for x in top_sentences[:n]]


if __name__ == "__main__":
    main()
