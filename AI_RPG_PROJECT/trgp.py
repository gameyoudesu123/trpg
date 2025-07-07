import random
import os

# data_loaderはapp.pyで読み込むため、ここでの直接参照は削除

def generate_trgp_keywords(word_list, count=1):
    """
    マスター単語リストから指定された数のTRGPキーワードをランダムに抽出する
    設計書【1.2.2】に基づく
    """
    if not word_list:
        # word_listが空の場合のフォールバック処理
        return [{"id": 0, "kanji": "無", "kana": "MU"}] * count
        
    return random.sample(word_list, k=count)
