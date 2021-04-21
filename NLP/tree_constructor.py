from typing import Any

import spacy
from spacy.tokens import Doc
from spacy.tokens import Token

nlp: spacy.Language = spacy.load('en_core_web_sm')
doc: Doc = nlp(u'Diplomatic staff would go home in a fifth plane')
print('*' * 100)


def extract_1_length(parsed_doc: Doc) -> tuple[Any, ...]:
    return tuple(token for token in parsed_doc)


def extract_2_length(parsed_doc: Doc) -> tuple[Any, ...]:
    result = []
    for token in parsed_doc:
        if list(token.children):
            result.append(token)
    return tuple(result)


print(f'2-LENGTH: {extract_2_length(doc)}')
print(f'CHILDREN OF {extract_2_length(doc)[0]}: {list(extract_2_length(doc)[0].children)}')
print(f'CHILDREN OF {extract_2_length(doc)[1]}: {list(extract_2_length(doc)[1].children)}')
print('*' * 100)


def extract_3_length(parsed_doc: Doc) -> tuple[Any, ...]:
    result = []
    two_length: tuple = extract_2_length(parsed_doc)
    for token in two_length:
        for child in token.children:
            if list(child.children):
                result.append(token)
                break

    return tuple(result)


print(f'3-LENGTH: {extract_3_length(doc)}')
print('*' * 100)

print('*' * 100)


class SyntaxTreeParser:
    def __init__(self, head_token: Token):
        self.head_token = head_token
        self.children = self.__get_2_level_deep()
        self.grand_children = self.__get_3_level_deep()
        self.length = self.__determine_length()

    def __determine_length(self) -> int:
        if self.grand_children:
            return 3
        elif self.children:
            return 2
        else:
            return 1

    @property
    def head(self):
        return self.head_token

    def __get_2_level_deep(self) -> tuple:
        return tuple(self.head.children)

    def __get_3_level_deep(self) -> tuple:
        result = []
        second_level = self.__get_2_level_deep()
        if not second_level:
            return ()

        for token in second_level:
            children = tuple(token.children)
            if tuple(token.children):
                for child in children:
                    result.append(child)
        return tuple(result)


# a = SyntaxTreeParser(extract_2_length(doc)[1])
# print(a.head)
# print(a.length)
# print(a.children)
# print(a.grand_children)
# print('*' * 100)
#
# a = SyntaxTreeParser(extract_3_length(doc)[1])
# print(a.head)
# print(a.length)
# print(a.children)
# print(a.grand_children)
# print('*' * 100)
#
# a = SyntaxTreeParser(doc[0])
# print(a.head)
# print(a.length)
# print(a.children)
# print(a.grand_children)
# print('*' * 100)
