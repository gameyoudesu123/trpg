import random
from models import Enemy

def generate_enemies(dungeon_state, world_tier):
    """
    設計書【4.2(a)ii】に基づき、敵パーティを生成する。
    戻り値をEnemyオブジェクトのリストに変更。
    """
    enemies = []
    enemy_count = random.randint(1, 4)
    
    for _ in range(enemy_count):
        enemy = Enemy()
        enemy.level = dungeon_state.get('current_floor', 1)
        enemy.name = f"ゴブリン・ウォリアー Lv{enemy.level}"
        enemy.max_hp = 20 + (enemy.level * 2)
        enemy.hp = enemy.max_hp
        # TODO: 本来はTRGPや設計書に基づいて他のステータスも設定する
        enemies.append(enemy)
        
    print(f"--- 敵パーティ生成: {[e.name for e in enemies]} ---")
    return enemies

def determine_action_order(party, enemies):
    """
    設計書【4.2(b)i】に基づき、行動順を決定する。
    引数をパーティと敵のオブジェクトリストに��正。
    """
    combatants = party + enemies
    # TODO: 本来は各キャラクターのspeedを考慮して決定する
    random.shuffle(combatants)
    
    print(f"--- 行動順決定 ---")
    print([c.name for c in combatants])
    return combatants

def process_player_action(actor, target, action_type):
    """
    プレイヤーの行動を処理し、ログメッセージを返す。
    オブジェクトを直接変更するため、戻り値はログのみ。
    """
    # TODO: 設計書【4.4(b)】の統一ダメージ計算式をここに実装する
    damage = random.randint(5, 15)
    
    target.hp = max(0, target.hp - damage)
    
    log_message = f"「{actor.name}」の攻撃！「{target.name}」に{damage}のダメージ！"
    if target.hp == 0:
        log_message += f" ...「{target.name}」を倒した！"

    return log_message

def process_enemy_action(actor, party):
    """
    敵の行動を処理し、ログメッセージを返す。
    オブジェクトを直接変更するため、戻り値はログのみ。
    """
    # 生きている味方の中からランダムにターゲットを選択
    alive_party_members = [member for member in party if member.hp > 0]
    if not alive_party_members:
        return "しかし、攻撃対象がいなかった！"
        
    target = random.choice(alive_party_members)
    
    # TODO: 設計書【4.4(b)】の統一ダメージ計算式をここに実装する
    damage = random.randint(3, 10)

    target.hp = max(0, target.hp - damage)
    
    log_message = f"敵「{actor.name}」の攻撃！「{target.name}」に{damage}のダメージ！"
    if target.hp == 0:
        log_message += f" ...「{target.name}」は倒れた！"

    return log_message
