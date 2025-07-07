import random
import trgp
from . import item_logic

def create_character_from_input(player_input, word_list):
    """
    プレイヤーの入力に基づいてPCオブジェクトを生成する
    設計書【2.1.3】に基づく
    """
    keywords = trgp.generate_trgp_keywords(word_list, count=3)

    weapon = item_logic.create_random_item(1, 1, item_type_filter="片手剣", category_key_filter="WEAPON")
    armor = item_logic.create_random_item(1, 1, item_type_filter="鎧", category_key_filter="ARMOR")
    
    initial_skills = ["強打", "かばう", "応急手当"]

    pc = {
        "name": player_input.split()[0] if player_input else "名無しの冒険者",
        "level": 1,
        "class_name": "戦士系", 
        "hp": 100,
        "ap": 3,
        "skills": initial_skills[:], # 装備中スキル
        "skill_pool": initial_skills[:], # 習得済みスキル
        "equipment": {
            "weapon": weapon, "body": armor, "head": None, "legs": None,
            "amulet": None, "ring1": None, "ring2": None, "trinket": None,
        }, 
        "appearance": "ごく普通の見た目",
        "personality": "無口",
        "trgp_keywords": [k['kanji'] for k in keywords]
    }
    return pc

def create_random_character(word_list):
    """
    「完全ランダム」選択時にPC候補を生成する
    設計書【2.1.2】に基づく
    """
    keywords = trgp.generate_trgp_keywords(word_list, count=3)
    
    name = f"{keywords[0]['kanji']}{keywords[1]['kanji']}"
    class_name = random.choice(["戦士系", "魔術師系", "斥候系", "聖職者系"])

    if class_name == "戦士系":
        weapon = item_logic.create_random_item(1, 1, item_type_filter="片手剣", category_key_filter="WEAPON")
        armor = item_logic.create_random_item(1, 1, item_type_filter="鎧", category_key_filter="ARMOR")
        initial_skills = ["強打", "かばう"]
    elif class_name == "魔術師系":
        weapon = item_logic.create_random_item(1, 1, item_type_filter="魔導書", category_key_filter="WEAPON")
        armor = None
        initial_skills = ["ファイアボール", "魔力の盾"]
    else: 
        weapon = item_logic.create_random_item(1, 1, item_type_filter="短剣", category_key_filter="WEAPON")
        armor = None
        initial_skills = ["速攻", "隠れる"]

    pc = {
        "name": name,
        "level": 1,
        "class_name": class_name,
        "hp": 100,
        "ap": 3,
        "skills": initial_skills[:], # 装備中スキル
        "skill_pool": initial_skills[:], # 習得済みスキル
        "equipment": {
            "weapon": weapon, "body": armor, "head": None, "legs": None,
            "amulet": None, "ring1": None, "ring2": None, "trinket": None,
        },
        "appearance": f"{keywords[2]['kanji']}の雰囲気を纏っている。",
        "personality": "ランダム",
        "trgp_keywords": [k['kanji'] for k in keywords]
    }
    return pc