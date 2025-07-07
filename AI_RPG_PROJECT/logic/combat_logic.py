import random

def generate_enemies(dungeon_state, world_tier):
    """
    設計書【4.2(a)ii】に基づき、敵パーティを生成する。
    """
    enemies = []
    enemy_count = random.randint(1, 4)
    
    for i in range(enemy_count):
        enemy = {
            "id": f"enemy_{i+1}",
            "name": f"ゴブリン・ウォリアー Lv{dungeon_state['current_floor']}",
            "hp": 20 + (dungeon_state['current_floor'] * 2),
            "max_hp": 20 + (dungeon_state['current_floor'] * 2),
            "type": "enemy"
        }
        enemies.append(enemy)
        
    print(f"--- 敵パーティ生成: {len(enemies)}体の{enemies[0]['name']}が出現 ---")
    return enemies

# --- 【今回の修正箇所】 ---
def determine_action_order(party, enemies):
    """
    設計書【4.2(b)i】に基づき、行動順を決定する。
    引数を2つ(party, enemies)正しく受け取るように修正。
    """
    party_combatants = []
    for member in party:
        combatant = member.__dict__.copy()
        combatant["type"] = "player"
        party_combatants.append(combatant)

    action_order = party_combatants + enemies
    random.shuffle(action_order)
    
    print(f"--- 行動順決定 ---")
    print([c['name'] for c in action_order])
    return action_order

def process_player_action(actor, target, action_type):
    """
    プレイヤーの行動を処理する。
    """
    damage = random.randint(5, 15)
    target['hp'] = max(0, target['hp'] - damage)
    
    log_message = f"「{actor['name']}」の攻撃！「{target['name']}」に{damage}のダメージ！"
    
    if target['hp'] == 0:
        log_message += f" 「{target['name']}」を倒した！"

    return target, log_message

def process_enemy_action(actor, party):
    """
    敵の行動を処理する。
    """
    alive_party_members = [member for member in party if member.hp > 0]
    if not alive_party_members:
        return None, "しかし、攻撃対象がいなかった！"
        
    target_obj = random.choice(alive_party_members)
    
    damage = random.randint(3, 10)
    target_obj.hp = max(0, target_obj.hp - damage)
    
    log_message = f"敵の「{actor['name']}」の攻撃！「{target_obj.name}」に{damage}のダメージ！"

    if target_obj.hp == 0:
        log_message += f" 「{target_obj.name}」は倒れた！"
    
    return target_obj, log_message