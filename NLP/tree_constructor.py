import spacy
from spacy.tokens import Doc
from spacy.tokens import Token


class SyntaxTreeHeadsExtractor:
    """
    Class for syntax trees heads extraction.
    Extracts ONLY HEADS from a given SpaCy Doc. From these heads 1-, 2-, 3-level trees can be built.
    """

    def __init__(self, parsed_doc: Doc):
        self.__parsed_doc = parsed_doc
        self.first_level_heads = self.__extract_heads_1_length()
        self.second_level_heads = self.__extract_heads_2_length()
        self.third_level_heads = self.__extract_heads_3_length()

    def __extract_heads_1_length(self) -> tuple:
        return tuple(token for token in self.__parsed_doc)

    def __extract_heads_2_length(self) -> tuple:
        result = []
        for token in self.__parsed_doc:
            if tuple(token.children):
                result.append(token)
        return tuple(result)

    def __extract_heads_3_length(self) -> tuple:
        result = []
        two_length: tuple = self.__extract_heads_2_length()
        for token in two_length:
            for child in token.children:
                if tuple(child.children):
                    result.append(token)
                    break

        return tuple(result)


class SyntaxTreeElementsExtractor:
    """
    Class for syntax trees elements extraction.
    Builds a syntax tree from a given head token and extracts children and grandchildren (if exist).
    """

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
    def head(self) -> Token:
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


if __name__ == '__main__':
    # Usage example
    nlp: spacy.Language = spacy.load('en_core_web_sm')
    doc: Doc = nlp(u'Diplomatic staff would go home in a fifth plane')

    heads_extractor = SyntaxTreeHeadsExtractor(doc)

    print(f'1-LENGTH: {heads_extractor.first_level_heads}')
    print('*' * 100)
    print(f'2-LENGTH: {heads_extractor.second_level_heads}')
    print(
        f'CHILDREN OF {heads_extractor.second_level_heads[0]}: {list(heads_extractor.second_level_heads[0].children)}')
    print(
        f'CHILDREN OF {heads_extractor.second_level_heads[1]}: {list(heads_extractor.second_level_heads[1].children)}')
    print('*' * 100)
    print(f'3-LENGTH: {heads_extractor.third_level_heads}')
    print('*' * 100)

    a = SyntaxTreeElementsExtractor(doc[0])
    print(a.head)
    print(a.length)
    print(a.children)
    print(a.grand_children)
    print('*' * 100)

    a = SyntaxTreeElementsExtractor(heads_extractor.second_level_heads[1])
    print(a.head)
    print(a.length)
    print(a.children)
    print(a.grand_children)
    print('*' * 100)

    a = SyntaxTreeElementsExtractor(heads_extractor.second_level_heads[1])
    print(a.head)
    print(a.length)
    print(a.children)
    print(a.grand_children)
    print('*' * 100)

    a = SyntaxTreeElementsExtractor(doc[-1])
    print(a.head)
    print(a.length)
    print(a.children)
    print(a.grand_children)
    print('*' * 100)
