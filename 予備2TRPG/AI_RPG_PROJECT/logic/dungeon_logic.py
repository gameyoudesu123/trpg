import random
from trgp import generate_trgp_keywords
from data_loader import load_master_words
from logic.combat_logic import generate_enemies # ← 今回追加

MASTER_WORDS = load_master_words()

def generate_dungeon_list():
    """挑戦可能なダンジョン3つのリストを動的に生成する。"""
    dungeons = []
    for i in range(3):
        keywords = generate_trgp_keywords(3, MASTER_WORDS)
        dungeon_name = f"{keywords[0]}の{keywords[1]}"
        dungeon_description = f"（{keywords[2]}の気配が漂う、不気味な場所だ…）"
        floor_count = (i + 1) * 10
        
        dungeons.append({
            "id": f"dungeon_{i+1}", "name": dungeon_name,
            "description": dungeon_description, "floors": floor_count
        })
    return dungeons

def process_dungeon_proceed(dungeon_state, world_tier):
    """階層進行時のランダムイベントを決定する。"""
    event_type = random.choice(["combat", "treasure", "nothing"])
    
    event_data = { "type": event_type, "message": "" }
    
    if event_type == "combat":
        event_data["message"] = "不気味な気配がする…！魔物が現れた！"
        # 【今回の更新】敵生成ロジックを呼び出す
        event_data["enemies"] = generate_enemies(dungeon_state, world_tier)
    elif event_type == "treasure":
        event_data["message"] = "古い宝箱を見つけた！"
    else: # "nothing"
        event_data["message"] = "特に何も見つからなかった。さらに奥へと進む。"
        
    print(f"--- ランダムイベント生成: {event_type} ---")
    return event_data