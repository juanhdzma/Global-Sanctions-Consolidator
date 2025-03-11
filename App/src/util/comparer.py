from collections import Counter
from src.util.data_helpers import clean_strings
from numpy import exp, array


def compare_words(word1, word2):
    """Compara dos palabras y devuelve el porcentaje de similitud entre 1 y 0"""
    counter1 = Counter(word1)
    counter2 = Counter(word2)

    intersection = sum((counter1 & counter2).values())
    smallest_length = min(len(word1), len(word2))

    if smallest_length == 0:
        return 0.0

    simililarity_score = (exp(intersection / smallest_length) - 1) / (exp(1) - 1)
    return simililarity_score


def compare_names(name1, name2):
    """Compara dos nombres y devuelve el porcentaje de similitud entre 1 y 0"""
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


def compare_names_matrix(df_names_array, transfer_names_array, n=3):
    """Devuelve una matriz de similitud basada en Jaccard con n-gramas"""

    def jaccard_similarity(s1, s2, n):
        """Calcula la similitud de Jaccard basada en n-gramas"""
        set1 = (
            set([s1[i : i + n] for i in range(len(s1) - n + 1)])
            if len(s1) >= n
            else {s1}
        )
        set2 = (
            set([s2[i : i + n] for i in range(len(s2) - n + 1)])
            if len(s2) >= n
            else {s2}
        )

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0

    df_names_array = array(df_names_array)
    transfer_names_array = array(transfer_names_array)

    return array(
        [
            [jaccard_similarity(name1, name2, n) for name2 in transfer_names_array]
            for name1 in df_names_array
        ]
    )
