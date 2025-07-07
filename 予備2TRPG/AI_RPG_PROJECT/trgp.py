import random

def generate_trgp_keywords(count, word_list):
    """
    設計書【1.2.2】に基づき、TRGPキーワードを抽出する。
    エラーチェックを強化し、デバッグ情報を出力する。
    """
    # --- ここからデバッグ情報出力 ---
    print("\n--- TRGPデバッグ情報 ---")
    if not word_list:
        print("!!! エラー: 単語リストが空です。")
        print("----------------------\n")
        return [f"エラー{i+1}" for i in range(count)]
    
    # 渡されたリストの最初の1項目の中身を確認
    print(f"単語リストの最初の項目（サンプル）: {word_list[0]}")
    # --- ここまでデバッグ情報出力 ---

    # 抽出処理
    try:
        if len(word_list) < count:
            selected_items = random.choices(word_list, k=count)
        else:
            selected_items = random.sample(word_list, k=count)
        
        # 'word'キーが存在するか安全にチェックし、存在しない場合はエラーメッセージを入れる
        keywords = [item.get('word', '---KEY_ERROR---') for item in selected_items]
        
        return keywords

    except Exception as e:
        print(f"!!! TRGPキーワード生成中に予期せぬエラー: {e}")
        return [f"エラー{i+1}" for i in range(count)]