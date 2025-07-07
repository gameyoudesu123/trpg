from models import PlayerCharacter
from logic.session_logic import save_party

def setup_debug_session():
    """
    テスト用のパーティ情報を、正しいデータ構造で作成しセッションに保存する。
    スキル保管庫テスト用にスキル情報を追加。
    """
    pc = PlayerCharacter()
    pc.name = "モニカ"
    pc.class_name = "魔術師系"
    pc.gold = 10000
    pc.equipment["右手"] = {"id": "w001", "name": "見習いの杖", "ilv": 1, "rarity": "コモン", "enhancement": 1, "base_price": 50}
    pc.inventory = [ {"id": "item001", "name": "傷んだ剣", "type": "武器", "base_price": 20} ]
    # スキル保管庫テスト用にスキルを追加
    pc.active_skills = [ {"id": "s001", "name": "ファイアボール"}, {"id": "s002", "name": "アイスランス"} ]
    pc.skill_vault = [ {"id": "s003", "name": "サンダーボルト"}, {"id": "s004", "name": "魔力の盾"} ]
    
    npc1, npc2 = PlayerCharacter(), PlayerCharacter()
    npc1.name, npc2.name = "アッシュ", "リナ"
    
    save_party([pc, npc1, npc2])
    print("--- デバッグ用セッションをセットアップしました (スキル保管庫テスト用) ---")