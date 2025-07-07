from models import PlayerCharacter
from logic.session_logic import save_party

def setup_debug_session():
    """
    テスト用のパーティ情報を、正しいデータ構造で作成しセッションに保存する。
    HPを最大値にリセットする処理を追加。
    """
    # PCを作成
    pc = PlayerCharacter()
    pc.name = "モニカ"
    pc.class_name = "魔術師系"
    pc.gold = 10000
    pc.max_hp = 100 # デバッグ用にHPを多めに設定
    pc.hp = pc.max_hp # HPを最大値にリセット
    pc.equipment["右手"] = {"id": "w001", "name": "見習いの杖", "ilv": 1, "rarity": "コモン", "enhancement": 1, "base_price": 50}
    pc.inventory = [ {"id": "item001", "name": "傷んだ剣", "type": "武器", "base_price": 20} ]
    pc.active_skills = [ {"id": "s001", "name": "ファイアボール"}, {"id": "s002", "name": "アイスランス"} ]
    pc.skill_vault = [ {"id": "s003", "name": "サンダーボルト"}, {"id": "s004", "name": "魔力の盾"} ]
    
    # 仲間1を作成
    npc1 = PlayerCharacter()
    npc1.name = "アッシュ"
    npc1.max_hp = 150
    npc1.hp = npc1.max_hp

    # 仲間2を作成
    npc2 = PlayerCharacter()
    npc2.name = "リナ"
    npc2.max_hp = 120
    npc2.hp = npc2.max_hp

    save_party([pc, npc1, npc2])
    print("--- デバッグ用セッションをセットアップしました (HPリセット済) ---")