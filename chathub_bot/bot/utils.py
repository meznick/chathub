import re


def escape_markdown_v2(text: str) -> str:
    reserved_characters = r'[_\*\[\]\(\)~`>#+\-=|{}.!]'
    return re.sub(reserved_characters, r'\\\g<0>', text)
