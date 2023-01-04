# coding: UTF-8
import MeCab

if __name__=='__main__':
    t=MeCab.Tagger(r' -d /usr/lib/mecab/dic/mecab-ipadic-neologd')
    print(t.parse("トランプ大統領"))
