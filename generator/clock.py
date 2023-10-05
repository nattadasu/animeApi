from datetime import timedelta

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

def convert_float_to_time(
    total_seconds: float | int,
    show_weeks: bool = False,
    show_milliseconds: bool = True,
) -> str:
    """
    Convert a float representing a number of days to a string representing the
    number of days, hours, and minutes.
    
    :param time_float: The number of days.
    :type time_float: float | int
    :param show_weeks: Whether to show weeks in the output, defaults to False
    :type show_weeks: bool, optional
    :param show_milliseconds: Whether to show milliseconds in the output, defaults to True
    :type show_milliseconds: bool, optional
    :return: A string representing the number of months, days, hours, and minutes.
    :rtype: str
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
        pluralize(years, "year") if years else "",
        pluralize(months, "month") if months else "",
        pluralize(weeks, "week") if weeks else "",
        pluralize(days, "day") if days else "",
        pluralize(hours, "hour") if hours else "",
        pluralize(minutes, "minute") if minutes else "",
        pluralize(seconds, "second") if seconds else "",
        pluralize(milliseconds, "millisecond") if milliseconds else "",
    ]

    result = ""
    # except the last word, add a comma after each word
    for word in words[:-1]:
        if word:
            result += f"{word}, "
    # add the last word
    result += f"and {words[-1]}"

    return result
