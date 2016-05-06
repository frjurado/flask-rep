import re
from unidecode import unidecode


def urlize(string):
    """
    Take a Unicode string and:
      * strip special characters,
      * strip symbols,
      * lowercase,
      * substitute whitespace for '-'.
    (for generating url slugs).
    """
    string = unidecode(string)
    string = re.sub(r'[^(\w\s)]', '', string)
    string = string.lower()
    string = re.sub(r'[\s]+', '-', string)
    return string
