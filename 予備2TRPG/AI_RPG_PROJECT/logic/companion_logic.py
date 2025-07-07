from models import PlayerCharacter

def generate_new_companions(count=3):
    """
    指定された人数の仲間候補を生成する。
    仮のIDを追加して、各キャラクターを区別できるようにする。
    """
    companions = []
    for i in range(count):
        char = PlayerCharacter()
        char.id = f"temp_npc_{i+1}" # ← 各仲間を識別するための仮IDを追加
        char.name = f"仮の仲間{i+1}"
        char.class_name = "戦士系"
        char.hp = 35
        char.max_hp = 35
        char.active_skills = ["仮のスキルA", "仮のスキルB"]
        char.equipment["右手"] = "錆びた剣"
        companions.append(char)
        
    print(f"--- {count}人の仲間候補を生成しました ---")
    return companions

# 現時点ではセッションに保存するため、簡易的な仲間データ管理
# TODO: 本来はデータベースで管理する
COMPANION_CANDIDATES = {}