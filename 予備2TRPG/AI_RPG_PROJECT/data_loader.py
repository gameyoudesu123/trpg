import csv
import os

def load_master_words():
    """マスター単語リストのCSVファイルを読み込み、リストとして返す。"""
    file_path = os.path.join(os.path.dirname(__file__), 'data', 'master_word_list.csv')
    
    if not os.path.exists(file_path):
        print(f"!!! 重大なエラー: {file_path} が見つかりません。")
        return []
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            if f.read(1) != '\ufeff':
                f.seek(0)
            
            # 原因はここでした。区切り文字として'|'を指定します。
            reader = csv.DictReader(f, delimiter='|')
            
            if not reader.fieldnames or 'word' not in reader.fieldnames:
                print("!!! 重大なエラー: CSVファイルの1行目に 'id|word|kana' のヘッダーが存在しないか、形式が間違っています。")
                return []

            words = list(reader)
        
        if not words:
            print(f"警告: {file_path} にデータがありません。")
            return []
            
        print(f"正常にマスター単語リストを読み込みました。単語数: {len(words)}")
        return words
    
    except Exception as e:
        print(f"!!! 重大なエラー: {file_path} の読み込み中に予期せぬエラーが発生しました: {e}")
        return []