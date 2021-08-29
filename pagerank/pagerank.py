import os
import random
import re
import sys
from typing import Counter

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}
    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1    - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # getting linked pages of page
    linked_pages = corpus[page]
    number_linked_pages = len(linked_pages)
    number_pages_corpus = len(corpus)
    try:
        probability_linked_pages = damping_factor / number_linked_pages
    except:
        probability_linked_pages = 0
    probability_other_pages = (1 - damping_factor) / number_pages_corpus

    # creating dictionary to store the probability of page
    transition_model_dict = dict()
    for filename in corpus:
        probability = probability_other_pages
        if filename in linked_pages:
            probability += probability_linked_pages
        transition_model_dict[filename] = probability

    return transition_model_dict


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # first random pick
    probability = 1 / len(corpus)
    start_model = dict()
    for filename in corpus:
        start_model[filename] = probability

    state = random.choices(list(start_model.keys()),
                           weights=start_model.values(), k=1)[0]

    # dictionary to store number of occurence of page
    pagerank = dict()
    # loop in n times
    for _ in range(n):
        # init
        if state not in pagerank:
            pagerank[state] = 0
        pagerank[state] += 1
        transition_model_dict = transition_model(corpus, state, damping_factor)
        state = random.choices(
            list(transition_model_dict.keys()), weights=transition_model_dict.values(), k=1)[0]

    # normalize
    for filename in pagerank:
        pagerank[filename] /= n

    return pagerank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # page has no links
    for filename in corpus:
        if len(corpus[filename]) == 0:
            for _filename in corpus:
                corpus[filename].add(_filename)
    # creating reversed corpus to store the others page that link to current page
    reversed_corpus = dict()
    for filename in corpus:
        linked_pages = corpus[filename]
        for page in linked_pages:
            if page not in reversed_corpus:
                reversed_corpus[page] = set()
            reversed_corpus[page].add(filename)
    # crearing dictionary to store probability of page
    pageranks = dict()
    number_pages_corpus = len(corpus)
    # add 1 / n to all pages
    for filename in corpus:
        pageranks[filename] = 1 / number_pages_corpus

    while True:
        # variable for checking if they are converged
        converged = 0
        for state in pageranks:
            pagerank = pageranks[state]
            new_pagerank = (1 - damping_factor) / number_pages_corpus
            if state in reversed_corpus:
                for link_to_state in reversed_corpus[state]:
                    numlinks = len(corpus[link_to_state])
                    new_pagerank += (damping_factor *
                                     pageranks[link_to_state] / numlinks)
            # update information of converging
            converged += (abs(new_pagerank - pagerank) <= 0.001)
            pageranks[state] = new_pagerank

        # if all pages are converged, breaking
        if converged == number_pages_corpus:
            break

    return pageranks


if __name__ == "__main__":
    main()
