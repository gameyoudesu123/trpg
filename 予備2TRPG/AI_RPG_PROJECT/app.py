import os
import re
from flask import Flask, render_template, request, redirect, url_for, session

# --- 外部ファイルの読み込み ---
from data_loader import load_master_words
from models import PlayerCharacter
from logic.session_logic import get_party, save_party, get_candidates, save_candidates
from logic.companion_logic import generate_new_companions
from logic.item_logic import calculate_sell_price, generate_initial_equipment, calculate_enhancement_cost, get_enhancement_preview
from logic.dungeon_logic import generate_dungeon_list, process_dungeon_proceed
from logic.combat_logic import determine_action_order, process_player_action, process_enemy_action
from logic.debug_logic import setup_debug_session

# --- Flaskアプリケーションの初期設定 ---
app = Flask(__name__)
app.secret_key = 'a_very_secret_and_secure_key_that_is_long_and_random'
MASTER_WORDS = load_master_words()

# --- 仮の商品リスト ---
ITEM_SHOP_CATALOG = [
    {"id": "item002", "name": "ポーション", "price": 50, "stock": 10, "effect": "HPを最大値の25%回復する", "type": "消費アイテム"},
    {"id": "item004", "name": "毒消し", "price": 30, "stock": 10, "effect": "毒状態を治療する", "type": "消費アイテム"}
]

# --- 共通処理 ---
@app.before_request
def setup_session():
    if 'party' not in session:
        setup_debug_session()
    if 'world_tier' not in session:
        session['world_tier'] = 1

# --- 各ページのルート定義 ---

@app.route('/')
def index():
    return redirect(url_for('hub'))

@app.route('/character_creation', methods=['GET', 'POST'])
def character_creation():
    if request.method == 'POST':
        session.clear()
        pc = PlayerCharacter()
        pc.name = request.form.get('player_input', '主人公').split()[0]
        pc = generate_initial_equipment(pc)
        save_party([pc])
        return redirect(url_for('hub'))
    return render_template('character_creation.html')

@app.route('/hub')
def hub():
    world_tier = session.get('world_tier', 1)
    return render_template('hub.html', world_tier=world_tier)

# --- 酒場関連 ---
@app.route('/tavern')
def tavern():
    return render_template('tavern.html')

@app.route('/tavern/find_companions')
def find_companions():
    candidates = generate_new_companions(3)
    save_candidates(candidates)
    party = get_party()
    return render_template('companion_list.html', companions=candidates, party_size=len(party))

@app.route('/tavern/hire', methods=['POST'])
def hire_companions():
    party = get_party()
    candidates = get_candidates()
    input_str = request.form.get('hire_input', '')
    indices_to_hire = [int(s) - 1 for s in re.findall(r'\d+', input_str)]
    hired_ids = []
    for index in sorted(indices_to_hire, reverse=True):
        if len(party) >= 4: break
        if 0 <= index < len(candidates):
            companion_to_add = candidates[index]
            party.append(companion_to_add)
            hired_ids.append(companion_to_add.id)
    updated_candidates = [c for c in candidates if c.id not in hired_ids]
    save_party(party)
    save_candidates(updated_candidates)
    return redirect(url_for('tavern'))

# --- 工房関連 ---
@app.route('/workshop')
def workshop():
    party = get_party()
    return render_template('workshop.html', party=party)

@app.route('/workshop/enhance/<character_id>')
def workshop_enhance_character(character_id):
    party = get_party()
    character = next((member for member in party if member.id == character_id), None)
    if not character: return redirect(url_for('workshop'))
    equipment_details = {}
    for slot, item in character.equipment.items():
        if item:
            equipment_details[slot] = {
                'name': item['name'], 'enhancement': item.get('enhancement', 0),
                'cost': calculate_enhancement_cost(item, 1), 'preview': get_enhancement_preview(item)
            }
    player_gold = party[0].gold if party else 0
    return render_template('workshop_enhance.html', character=character, equipment_details=equipment_details, gold=player_gold)

@app.route('/workshop/enhance/execute', methods=['POST'])
def execute_enhance():
    character_id = request.form.get('character_id')
    slot = request.form.get('slot_to_enhance')
    party = get_party()
    pc = party[0]
    character_to_enhance = next((member for member in party if member.id == character_id), None)
    if character_to_enhance and slot and character_to_enhance.equipment.get(slot):
        item_to_enhance = character_to_enhance.equipment[slot]
        cost = calculate_enhancement_cost(item_to_enhance, 1)
        if pc.gold >= cost:
            pc.gold -= cost
            item_to_enhance['enhancement'] += 1
    save_party(party)
    return redirect(url_for('workshop_enhance_character', character_id=character_id))
    
@app.route('/workshop/appraise')
def workshop_appraise():
    party = get_party()
    pc = party[0]
    appraisable_items = [item for item in pc.inventory if not item.get('identified', True)]
    return render_template('workshop_appraise.html', appraisable_items=appraisable_items)

@app.route('/workshop/appraise/execute', methods=['POST'])
def appraise_item():
    item_id = request.form.get('item_id')
    party = get_party()
    pc = party[0]
    item_to_appraise = next((item for item in pc.inventory if item.get('id') == item_id), None)
    if item_to_appraise and not item_to_appraise.get('identified', True):
        item_to_appraise['identified'] = True
        item_to_appraise['name'] = "真実の指輪"
        save_party(party)
        return render_template('workshop_appraise_result.html', item=item_to_appraise)
    return redirect(url_for('workshop_appraise'))

@app.route('/workshop/sell')
def workshop_sell():
    party = get_party()
    pc = party[0] if party else None
    if pc:
        for item in pc.inventory: item['sell_price'] = calculate_sell_price(item)
    return render_template('workshop_sell.html', pc=pc, return_to='workshop')

@app.route('/workshop/sell_item', methods=['POST'])
def workshop_sell_item():
    item_id_to_sell = request.form.get('item_id')
    party = get_party()
    pc = party[0]
    item_found = next((item for item in pc.inventory if item.get('id') == item_id_to_sell), None)
    if item_found:
        sell_price = calculate_sell_price(item_found)
        if 'stack' in item_found and item_found['stack'] > 1: item_found['stack'] -= 1
        else: pc.inventory.remove(item_found)
        pc.gold += sell_price
    save_party(party)
    return redirect(url_for('workshop_sell'))

# --- スキル保管庫関連 ---
@app.route('/skill_vault')
def skill_vault():
    party = get_party()
    return render_template('skill_vault_character_select.html', party=party)

@app.route('/skill_vault/manage/<character_id>')
def skill_vault_manage(character_id):
    party = get_party()
    character = next((member for member in party if member.id == character_id), None)
    if character: return render_template('skill_vault_manage.html', character=character)
    return redirect(url_for('skill_vault'))

@app.route('/skill_vault/move', methods=['POST'])
def skill_vault_move():
    character_id = request.form.get('character_id')
    skill_id = request.form.get('skill_id')
    direction = request.form.get('direction')
    party = get_party()
    character = next((member for member in party if member.id == character_id), None)
    if not character: return redirect(url_for('skill_vault'))
    if direction == 'to_vault':
        skill_to_move = next((s for s in character.active_skills if s['id'] == skill_id), None)
        if skill_to_move:
            character.active_skills.remove(skill_to_move)
            character.skill_vault.append(skill_to_move)
    elif direction == 'to_active' and len(character.active_skills) < 10:
        skill_to_move = next((s for s in character.skill_vault if s['id'] == skill_id), None)
        if skill_to_move:
            character.skill_vault.remove(skill_to_move)
            character.active_skills.append(skill_to_move)
    save_party(party)
    return redirect(url_for('skill_vault_manage', character_id=character_id))
    
# --- 道具屋関連 ---
@app.route('/item_shop')
def item_shop():
    party = get_party()
    pc = party[0] if party else None
    return render_template('item_shop.html', pc=pc, item_list=ITEM_SHOP_CATALOG)

@app.route('/item_shop/command', methods=['POST'])
def item_shop_command():
    input_str = request.form.get('command_input', '').strip().lower()
    if input_str == 's': return redirect(url_for('item_shop_sell'))
    if input_str == 'e': return redirect(url_for('hub'))
    party = get_party()
    pc = party[0]
    parts = re.split(r'[, ]+', input_str)
    if len(parts) == 2:
        try:
            item_index, quantity = int(parts[0]) - 1, int(parts[1])
            if 0 <= item_index < len(ITEM_SHOP_CATALOG) and quantity > 0:
                item_to_buy = ITEM_SHOP_CATALOG[item_index]
                total_cost = item_to_buy['price'] * quantity
                if item_to_buy['stock'] >= quantity and pc.gold >= total_cost:
                    pc.gold -= total_cost
                    item_to_buy['stock'] -= quantity
                    existing_item = next((item for item in pc.inventory if item.get('id') == item_to_buy['id']), None)
                    if existing_item and 'stack' in existing_item: existing_item['stack'] += quantity
                    else:
                        new_item = item_to_buy.copy()
                        new_item.pop('stock', None); new_item['stack'] = quantity
                        pc.inventory.append(new_item)
                    save_party(party)
        except (ValueError, IndexError): pass
    return redirect(url_for('item_shop'))

@app.route('/item_shop/sell')
def item_shop_sell():
    party = get_party()
    pc = party[0] if party else None
    if pc:
        for item in pc.inventory: item['sell_price'] = calculate_sell_price(item)
    return render_template('workshop_sell.html', pc=pc, return_to='item_shop')

@app.route('/item_shop/sell_item', methods=['POST'])
def item_shop_sell_item():
    item_id_to_sell = request.form.get('item_id')
    party = get_party()
    pc = party[0]
    item_found = next((item for item in pc.inventory if item.get('id') == item_id_to_sell), None)
    if item_found:
        sell_price = calculate_sell_price(item_found)
        if 'stack' in item_found and item_found['stack'] > 1: item_found['stack'] -= 1
        else: pc.inventory.remove(item_found)
        pc.gold += sell_price
    save_party(party)
    return redirect(url_for('item_shop_sell'))

# --- ダンジョン関連 ---
@app.route('/dungeon_select')
def dungeon_select():
    dungeons = generate_dungeon_list()
    session['dungeon_options'] = dungeons
    return render_template('dungeon_select.html', dungeons=dungeons)

@app.route('/dungeon/enter/<dungeon_id>')
def dungeon_enter(dungeon_id):
    dungeon_options = session.get('dungeon_options', [])
    selected_dungeon = next((d for d in dungeon_options if d['id'] == dungeon_id), None)
    if not selected_dungeon:
        return redirect(url_for('dungeon_select'))
    session['dungeon_state'] = {
        "id": selected_dungeon['id'], "name": selected_dungeon['name'],
        "total_floors": selected_dungeon['floors'], "current_floor": 1,
        "description": selected_dungeon['description']
    }
    return redirect(url_for('dungeon_floor'))

@app.route('/dungeon/floor')
def dungeon_floor():
    dungeon_state = session.get('dungeon_state')
    if not dungeon_state:
        return redirect(url_for('hub'))
    return render_template('dungeon_floor.html', dungeon_state=dungeon_state)

@app.route('/dungeon/action', methods=['POST'])
def dungeon_action():
    action = request.form.get('action')
    dungeon_state = session.get('dungeon_state')
    if not dungeon_state: return redirect(url_for('hub'))
    if action == 'proceed':
        world_tier = session.get('world_tier', 1)
        event = process_dungeon_proceed(dungeon_state, world_tier)
        if event['type'] == 'combat':
            session['combat_enemies'] = event["enemies"]
            return redirect(url_for('combat_start'))
        dungeon_state['current_floor'] += 1
    session['dungeon_state'] = dungeon_state
    return redirect(url_for('dungeon_floor'))

# --- 戦闘関連 ---
@app.route('/combat/start')
def combat_start():
    party = get_party()
    enemies = session.get('combat_enemies', [])
    action_order = determine_action_order(party, enemies)
    
    # 【今回の修正】重複していた「戦闘開始！」をログの初期値から削除
    combat_state = {
        "enemies": enemies, "action_order": action_order, "turn": 1,
        "current_actor_index": 0, "current_actor": action_order[0],
        "log": ["戦闘開始！"]
    }
    session['combat_state'] = combat_state
    return redirect(url_for('combat_turn'))

@app.route('/combat/turn')
def combat_turn():
    combat_state = session.get('combat_state')
    party = get_party()
    if not combat_state: return redirect(url_for('hub'))
    return render_template('dungeon_combat.html', combat_state=combat_state, party=party)

# --- 【今回の更新箇所】 ---
@app.route('/combat/action', methods=['POST'])
def combat_action():
    """戦闘中の行動を処理し、戦闘の継続・終了を判定する"""
    combat_state = session.get('combat_state')
    if not combat_state: return redirect(url_for('hub'))
        
    actor = combat_state['current_actor']
    party = get_party()
    
    # 行動処理
    if actor['type'] == 'player':
        input_str = request.form.get('command_input', '')
        parts = re.split(r'[, ]+', input_str)
        if len(parts) == 2:
            try:
                action_type, target_index = int(parts[0]), int(parts[1]) - 1
                enemies = combat_state['enemies']
                if 0 <= target_index < len(enemies) and enemies[target_index]['hp'] > 0:
                    target = enemies[target_index]
                    if action_type == 1: # 通常攻撃
                        updated_target, log_message = process_player_action(actor, target, 'attack')
                        combat_state['enemies'][target_index] = updated_target
                        combat_state['log'].append(log_message)
                else:
                    combat_state['log'].append("無効なターゲットです。")
            except (ValueError, IndexError):
                combat_state['log'].append("無効なコマンドです。")
        else:
            combat_state['log'].append(f"「{actor['name']}」は、どうするか迷っている...")

    elif actor['type'] == 'enemy':
        target_obj, log_message = process_enemy_action(actor, party)
        if target_obj: save_party(party)
        combat_state['log'].append(log_message)

    # 勝利判定
    if all(enemy['hp'] <= 0 for enemy in combat_state['enemies']):
        return redirect(url_for('combat_result', result='victory'))

    # 敗北判定
    if all(member.hp <= 0 for member in get_party()):
        return redirect(url_for('combat_result', result='defeat'))
        
    # 次の行動者へ
    while True:
        combat_state['current_actor_index'] = (combat_state['current_actor_index'] + 1) % len(combat_state['action_order'])
        next_actor = combat_state['action_order'][combat_state['current_actor_index']]
        
        if next_actor['type'] == 'enemy':
            enemy_in_state = next((e for e in combat_state['enemies'] if e['id'] == next_actor['id']), None)
            if enemy_in_state and enemy_in_state['hp'] > 0:
                break
        else: # player
            player_in_party = next((p for p in party if p.id == next_actor['id']), None)
            if player_in_party and player_in_party.hp > 0:
                break
        
        if combat_state['current_actor_index'] == 0:
            break
            
    combat_state['current_actor'] = combat_state['action_order'][combat_state['current_actor_index']]
    
    if combat_state['current_actor_index'] == 0:
        combat_state['turn'] += 1
        combat_state['log'].append(f"--- {combat_state['turn']}ターン目 ---")

    session['combat_state'] = combat_state
    return redirect(url_for('combat_turn'))

@app.route('/combat/result/<result>')
def combat_result(result):
    """戦闘結果画面を表示する"""
    session.pop('combat_state', None)
    session.pop('combat_enemies', None)
    if result == 'victory':
        dungeon_state = session.get('dungeon_state')
        if dungeon_state:
            print(f"--- 戦闘勝利！ダンジョン探索を継続できます ---")
        return render_template('combat_result.html', victory=True, result_title="戦闘勝利")
    else: # defeat
        return render_template('combat_result.html', victory=False, result_title="全滅")

# --- デバッグ用ルート ---
@app.route('/debug/hub')
def debug_to_hub():
    setup_debug_session()
    return redirect(url_for('hub'))
    
@app.route('/debug/workshop')
def debug_to_workshop():
    setup_debug_session()
    return redirect(url_for('workshop'))

@app.route('/debug/item_shop')
def debug_to_item_shop():
    setup_debug_session()
    return redirect(url_for('item_shop'))
    
# --- サーバー起動 ---
if __name__ == '__main__':
    print("--- サーバー起動プロセス開始 ---")
    app.run(host='0.0.0.0', port=5000, debug=True)