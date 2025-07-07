import csv
import os

def load_master_word_list():
    """
    data/master_word_list.csv からマスター単語リストを読み込む
    """
    word_list = []
    # ファイルの絶対パスを取得
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'master_word_list.csv')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='|')
            
            # 修正点: ヘッダー行を読み飛ばす
            next(reader, None)  # ヘッダー行をスキップ
            
            for row in reader:
                if len(row) == 3:
                    try:
                        word_list.append({
                            "id": int(row[0]),
                            "kanji": row[1],
                            "kana": row[2]
                        })
                    except ValueError:
                        # 数字に変換できない行はスキップ（空行などへの対策）
                        print(f"警告: スキップされた行（不正なID）: {row}")
                        continue
    except FileNotFoundError:
        print(f"エラー: {file_path} が見つかりません。")
        return []
        
    return word_list
