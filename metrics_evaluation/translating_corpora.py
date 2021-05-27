
if __name__ == '__main__':
    from easynmt import EasyNMT

    with open(r'C:\Users\akashchi\OneDrive - Intel Corporation\Desktop\stuff\study\CW#4\parallel corpora\News '
              r'Commentary. EN-RU\news-commentary-v9.ru-en.ru', 'r', encoding='utf-8') as ru_file:
        data = [str(next(ru_file)).strip('\n') for _ in range(2000)]
        # print(data)

    model = EasyNMT('opus-mt')

    translated = model.translate(data, target_lang='en')
    with open('translated.txt', 'w', encoding='utf-8') as result_file:
        for sentence in translated:
            result_file.write(sentence + '\n')
