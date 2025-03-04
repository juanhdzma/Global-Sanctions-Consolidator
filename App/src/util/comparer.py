from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
from src.util.data_helpers import clean_strings
from numpy import exp, concatenate


def compare_words(word1, word2):
    '''Compara dos palabras y devuelve el porcentaje de similitud entre 1 y 0'''
    counter1 = Counter(word1)
    counter2 = Counter(word2)

    intersection = sum((counter1 & counter2).values())
    smallest_length = min(len(word1), len(word2))

    if smallest_length == 0:
        return 0.0

    simililarity_score = (
        exp(intersection / smallest_length) - 1) / (exp(1) - 1)
    return simililarity_score


def compare_names(name1, name2):
    '''Compara dos nombres y devuelve el porcentaje de similitud entre 1 y 0'''
    name1 = clean_strings(name1).lower()
    name2 = clean_strings(name2).lower()

    words1 = name1.split()
    words2 = name2.split()

    scores = []

    for word1 in words1:
        word_scores = [compare_words(word1, word2) for word2 in words2]
        if word_scores:
            scores.append(max(word_scores))

    if not scores:
        return 0.0

    final_score = sum(scores) / len(scores)
    return final_score


def compare_names_vectorized_transfer(df_names_array, transfer_names_array):
    '''Compara una matriz de nombres y devuelve una matriz de simulitud'''
    vectorizer = TfidfVectorizer().fit(
        concatenate([df_names_array, transfer_names_array]))
    df_vectors = vectorizer.transform(df_names_array)
    transfer_vectors = vectorizer.transform(transfer_names_array)

    score_matrix = cosine_similarity(df_vectors, transfer_vectors)
    return score_matrix
