from datetime import timedelta

def pluralize(word: str, count: int = 2) -> str:
    """
    Pluralize a word if the count is not 1.
    
    Args:
        word (str): The word to pluralize.
        count (int, optional): The count. Defaults to 2.

    Returns:
        str: The pluralized word.
    """
    if count == 1:
        return word
    else:
        if word.endswith("y"):
            return word[:-1] + "ies"
        elif word.endswith("s"):
            return word + "es"
        else:
            return word + "s"

def convert_float_to_time(
    total_seconds: float | int,
    show_weeks: bool = False,
    show_milliseconds: bool = True,
) -> str:
    """
    Convert a float representing a number of days to a string representing the number of days, hours, and minutes.

    Args:
        time_float (float, int): The number of days.
        show_weeks (bool, optional): Whether to show weeks in the output. Defaults to False.
        show_milliseconds (bool, optional): Whether to show milliseconds in the output. Defaults to True.

    Returns:
        str: A string representing the number of months, days, hours, and minutes.
    """
    # Create a timedelta object with the total seconds
    delta = timedelta(seconds=total_seconds)

    # Extract years, months, days, hours, minutes, and seconds from the
    # timedelta object
    years = delta.days // 365
    months = delta.days % 365 // 30
    if show_weeks:
        weeks = delta.days % 365 % 30 // 7
        days = delta.days % 365 % 30 % 7
    else:
        weeks = None
        days = delta.days % 365 % 30
    hours = delta.seconds // 3600
    minutes = delta.seconds // 60 % 60
    seconds = delta.seconds % 60
    if show_milliseconds:
        milliseconds = delta.microseconds // 1000
    else:
        milliseconds = None

    words = [
        f"{years} {pluralize('year', years)}" if years else "",
        f"{months} {pluralize('month', months)}" if months else "",
        f"{weeks} {pluralize('week', weeks)}" if weeks else "",
        f"{days} {pluralize('day', days)}" if days else "",
        f"{hours} {pluralize('hour', hours)}" if hours else "",
        f"{minutes} {pluralize('minute', minutes)}" if minutes else "",
        f"{seconds} {pluralize('second', seconds)}" if seconds else "",
        f"{milliseconds} {pluralize('millisecond', milliseconds)}" if milliseconds else "",
    ]

    result = ""
    # except the last word, add a comma after each word
    for word in words[:-1]:
        if word:
            result += f"{word}, "
    # add the last word
    result += f"and {words[-1]}"

    return result
