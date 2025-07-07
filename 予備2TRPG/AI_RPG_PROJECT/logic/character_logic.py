# 設計書【1-7】及び【2.2】に基づき、ステータス計算ロジックを実装
import math

def calculate_initial_stats(character_obj, pc_level, class_type):
    """
    キャラクターの初期ステータス（特にHP）を設計書の計算式通りに算出する。
    AIの解釈は一切介在しない。
    """
    # 設計書【2.2(a)i】のクラス方向性HP倍率を定義
    hp_multipliers = {
        "盾役": 1.2,
        "攻撃的前衛": 1.1,
        "聖職者系": 1.0,
        "斥候系": 0.9,
        "魔術師系": 0.8
    }

    # クラス系統が指定されていない、またはリストにない場合のデフォルト値
    multiplier = hp_multipliers.get(class_type, 1.0)
    
    # 設計書【2.2(a)i】の計算式を忠実に実行
    base_hp = math.floor((30 + (pc_level * 5)) * multiplier)

    # 計算結果をキャラクターオブジェクトに格納
    character_obj.max_hp = base_hp
    character_obj.hp = base_hp
    
    # 設計書【2.2(c)i】に基づき、APの初期値を設定
    character_obj.max_ap = 3
    character_obj.ap = 3

    print("--- 初期ステータス計算結果 ---")
    print(f"HP: {character_obj.hp}/{character_obj.max_hp}, AP: {character_obj.ap}/{character_obj.max_ap}")
    
    return character_obj