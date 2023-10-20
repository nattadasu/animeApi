def pluralize(count: int, word: str) -> str:
    """
    Pluralize a word if the count is not 1.

    :param count: The count.
    :type count: int
    :param word: The word to pluralize.
    :type word: str
    :return: The pluralized word, e.g. "1 day" or "2 days".
    :rtype: str
    """
    if count in [0, 1]:
        return f"{count} {word}"
    else:
        if word.endswith("y"):
            return f"{count} {word[:-1]}ies"
        elif word.endswith("s"):
            return f"{count} {word}es"
        else:
            return f"{count} {word}s"
