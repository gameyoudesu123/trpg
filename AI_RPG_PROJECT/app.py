from flask import Flask, render_template, request, redirect, url_for, session
import os
from logic import character_logic, dungeon_logic, item_logic, data_loader, companion_logic, conversation_logic, workshop_logic, item_shop_logic, world_tier_logic

app = Flask(__name__)
app.secret_key = os.urandom(24)

MASTER_WORD_LIST = data_loader.load_master_word_list()

# --- デバッグ用ルート ---
@app.route('/debug/start')
def debug_start():
    pc = character_logic.create_character_from_input("デバッグ勇者 20 男 伝説の始まり 戦士系 勇敢", MASTER_WORD_LIST)
    pc['is_pc'] = True
    
    companion1 = companion_logic.generate_companions({}, MASTER_WORD_LIST, 1, 1)[0]
    companion2 = companion_logic.generate_companions({}, MASTER_WORD_LIST, 1, 1)[0]
    companion1['is_pc'] = False
    companion2['is_pc'] = False

    unidentified_item = item_logic.create_random_item(10, 1)
    unidentified_item['rarity_id'] = 'ANCIENT'
    unidentified_item['name'] = '🌈封印されし古の剣'
    unidentified_item['is_identified'] = False

    session['game_state'] = {
        'pc': pc,
        'party': [pc, companion1, companion2],
        'gold': 50000,
        'inventory': [unidentified_item] + [item_logic.create_random_item(5, 1) for _ in range(10)],
        'warehouse': [item_logic.create_random_item(3, 1) for _ in range(5)],
        'skill_vault': ["渾身の一撃", "見切り", "治癒の光"],
        'location': 'hub',
        'dungeon_info': None,
        'current_event_id': None,
        'world_tier': 1,
        'log': ["【デバッグモード】テスト用のパーティでゲームを開始しました。"]
    }
    session['tavern_companions'] = []
    return redirect(url_for('hub'))
# -------------------------

@app.route('/')
def index():
    return render_template('character_creation.html')

@app.route('/create_character', methods=['POST'])
def create_character():
    player_input = request.form.get('player_input', '')
    
    if player_input == "完全ランダム":
        pc1 = character_logic.create_random_character(MASTER_WORD_LIST)
        pc2 = character_logic.create_random_character(MASTER_WORD_LIST)
        pc = pc1
    else:
        pc = character_logic.create_character_from_input(player_input, MASTER_WORD_LIST)
    
    pc['is_pc'] = True

    session['game_state'] = {
        'pc': pc,
        'party': [pc],
        'gold': 50,
        'inventory': [],
        'warehouse': [],
        'skill_vault': [],
        'location': 'hub',
        'dungeon_info': None,
        'current_event_id': None,
        'world_tier': 1,
        'log': [f"冒険者『{pc.get('name', '')}』が誕生した。"]
    }
    session['tavern_companions'] = []
    return redirect(url_for('hub'))

@app.route('/select_character', methods=['POST'])
def select_character():
    selected_pc_data = request.form.get('selected_pc')
    if not selected_pc_data:
        return redirect(url_for('index'))
    
    import json
    pc = json.loads(selected_pc_data)
    
    pc['is_pc'] = True

    session['game_state'] = {
        'pc': pc,
        'party': [pc],
        'gold': 50,
        'inventory': [],
        'warehouse': [],
        'skill_vault': [],
        'location': 'hub',
        'dungeon_info': None,
        'current_event_id': None,
        'world_tier': 1,
        'log': [f"冒険者『{pc.get('name', '')}』が誕生した。"]
    }
    session['tavern_companions'] = []
    return redirect(url_for('hub'))

@app.route('/hub')
def hub():
    if 'game_state' not in session:
        return redirect(url_for('index'))
    
    game_state = session.get('game_state', {})
    return render_template('hub.html', game_state=game_state)

# --- 拠点施設のルート ---
@app.route('/tavern')
def tavern():
    if 'game_state' not in session:
        return redirect(url_for('index'))
    
    game_state = session.get('game_state', {})
    return render_template('tavern.html', game_state=game_state)

@app.route('/tavern/action', methods=['POST'])
def tavern_action():
    if 'game_state' not in session:
        return redirect(url_for('index'))
    
    game_state = session.get('game_state', {})
    command_str = request.form.get('command', '')

    try:
        command_num = int(command_str.split()[0])
    except (ValueError, IndexError):
        return redirect(url_for('tavern'))

    if 1 <= command_num <= 6:
        pc_level = game_state['pc'].get('level', 1)
        world_tier = game_state.get('world_tier', 1)
        filters = {}
        companions = companion_logic.generate_companions(filters, MASTER_WORD_LIST, pc_level, world_tier)
        session['tavern_companions'] = companions
        return render_template('tavern_search_result.html', companions=companions, game_state=game_state)
    
    elif command_num == 9:
        return redirect(url_for('tavern_talk'))

    elif command_num == 10: return redirect(url_for('workshop'))
    elif command_num == 11: return redirect(url_for('item_shop'))
    elif command_num == 12: return redirect(url_for('warehouse'))
    elif command_num == 13: return redirect(url_for('skill_vault'))
    elif command_num == 14: return redirect(url_for('dungeon_select'))
    elif command_num == 15: return redirect(url_for('hub'))
    
    return redirect(url_for('tavern'))

@app.route('/tavern/contract', methods=['POST'])
def tavern_contract():
    if 'game_state' not in session:
        return redirect(url_for('index'))

    game_state = session.get('game_state', {})
    companions_for_hire = session.get('tavern_companions', [])
    hire_indices = request.form.getlist('hire')

    for index_str in hire_indices:
        try:
            index = int(index_str) - 1
            if not (0 <= index < len(companions_for_hire)): continue
            companion_to_hire = companions_for_hire[index]
            if game_state['gold'] < companion_to_hire['contract_fee']:
                game_state['log'].append(f"【契約失敗】{companion_to_hire['name']}との契約に失敗しました（所持金不足）")
                continue
            if len(game_state['party']) >= 4:
                game_state['log'].append(f"【契約失敗】{companion_to_hire['name']}との契約に失敗しました（パーティ満員）")
                continue
            game_state['gold'] -= companion_to_hire['contract_fee']
            game_state['party'].append(companion_to_hire)
            game_state['log'].append(f"【契約成立】{companion_to_hire['name']}が仲間に加わった！")
        except (ValueError, IndexError):
            continue

    session['tavern_companions'] = []
    session['game_state'] = game_state
    return redirect(url_for('tavern'))

@app.route('/tavern/talk')
def tavern_talk():
    if 'game_state' not in session:
        return redirect(url_for('index'))
    
    game_state = session.get('game_state', {})
    party_conversation = conversation_logic.generate_party_conversation(game_state['party'])
    
    companions_with_topics = []
    current_topic_index = 1
    companions_in_party = [member for member in game_state['party'] if not member.get('is_pc')]

    class_icons = { "戦士系": "🛡️", "攻撃的前衛": "⚔️", "斥候系": "🏹", "魔術師系": "🔮", "聖職者系": "🌿" }

    for companion in companions_in_party:
        topics = conversation_logic.get_individual_topics(companion)
        companion_data = {
            "name": companion.get('name'),
            "icon": class_icons.get(companion.get('class_name'), '❓'),
            "topics": topics,
            "topic_start_index": current_topic_index,
            "free_talk_index": current_topic_index + len(topics)
        }
        companions_with_topics.append(companion_data)
        current_topic_index += len(topics) + 1

    return render_template(
        'tavern_conversation_select.html', 
        game_state=game_state,
        party_conversation=party_conversation,
        companions=companions_with_topics
    )

@app.route('/tavern/talk/execute', methods=['POST'])
def tavern_talk_execute():
    if 'game_state' not in session:
        return redirect(url_for('index'))

    game_state = session.get('game_state', {})
    topics_input = request.form.get('topics_input', '')
    
    actions = [action.strip() for action in topics_input.replace(',', ' ').split(' ') if action.strip()]
    results, log_updates = conversation_logic.process_conversation_actions(game_state, actions)
    game_state['log'].extend(log_updates)
    session['game_state'] = game_state

    return render_template('tavern_conversation_result.html', results=results)

@app.route('/workshop')
def workshop():
    if 'game_state' not in session:
        return redirect(url_for('index'))
    return render_template('workshop.html', game_state=session['game_state'])

@app.route('/workshop/enhance/<int:character_index>')
def workshop_enhance_character_select(character_index):
    if 'game_state' not in session:
        return redirect(url_for('index'))
    
    game_state = session.get('game_state', {})
    if not (0 <= character_index < len(game_state['party'])):
        return redirect(url_for('workshop'))

    character_to_enhance = game_state['party'][character_index]
    
    for slot, item in character_to_enhance.get('equipment', {}).items():
        if item:
            item['enhancement_cost'] = workshop_logic.calculate_enhancement_cost(item, game_state['world_tier'])
            item['enhancement_preview'] = workshop_logic.get_enhancement_preview(item)

    return render_template('workshop_enhance.html', character=character_to_enhance, character_index=character_index, game_state=game_state)

@app.route('/workshop/enhance/execute/<int:character_index>', methods=['POST'])
def workshop_enhance_execute(character_index):
    if 'game_state' not in session:
        return redirect(url_for('index'))
    
    game_state = session.get('game_state', {})
    item_slot = request.form.get('item_slot')

    if not (0 <= character_index < len(game_state['party'])):
        return redirect(url_for('workshop'))
    
    character = game_state['party'][character_index]
    item_to_enhance = character.get('equipment', {}).get(item_slot)

    if not item_to_enhance:
        return redirect(url_for('workshop_enhance_character_select', character_index=character_index))

    enhanced_item, new_gold, message = workshop_logic.enhance_item(
        item_to_enhance, game_state['gold'], game_state['world_tier']
    )

    if enhanced_item:
        game_state['party'][character_index]['equipment'][item_slot] = enhanced_item
        game_state['gold'] = new_gold
    
    game_state['log'].append(message)
    session['game_state'] = game_state
    
    return redirect(url_for('workshop_enhance_character_select', character_index=character_index))

@app.route('/workshop/sell')
def workshop_sell_ui():
    if 'game_state' not in session:
        return redirect(url_for('index'))
    
    game_state = session.get('game_state', {})
    inventory_items = []
    
    for char_idx, character in enumerate(game_state['party']):
        for slot, item in character.get('equipment', {}).items():
            if item:
                item['sell_price'] = workshop_logic.calculate_sell_price(item)
                inventory_items.append((item, f"party_{char_idx}_{slot}"))

    for inv_idx, item in enumerate(game_state.get('inventory', [])):
        if item:
            item['sell_price'] = workshop_logic.calculate_sell_price(item)
            inventory_items.append((item, f"inventory_{inv_idx}"))

    return render_template('workshop_sell.html', inventory_items=inventory_items, game_state=game_state)

@app.route('/workshop/sell/execute', methods=['POST'])
def workshop_sell_execute():
    if 'game_state' not in session:
        return redirect(url_for('index'))
        
    game_state = session.get('game_state', {})
    items_to_sell = request.form.getlist('sell_items')
    
    total_earned = 0
    sold_item_names = []
    inventory_indices_to_remove = []
    
    for slot_info in items_to_sell:
        parts = slot_info.split('_')
        item_location = parts[0]
        item_to_sell = None
        
        if item_location == 'party' and len(parts) == 3:
            char_idx, slot = int(parts[1]), parts[2]
            item_to_sell = game_state['party'][char_idx]['equipment'].get(slot)
            if item_to_sell:
                game_state['party'][char_idx]['equipment'][slot] = None
        
        elif item_location == 'inventory' and len(parts) == 2:
            inv_idx = int(parts[1])
            item_to_sell = game_state['inventory'][inv_idx]
            if item_to_sell:
                inventory_indices_to_remove.append(inv_idx)

        if item_to_sell:
            sell_price = workshop_logic.calculate_sell_price(item_to_sell)
            total_earned += sell_price
            sold_item_names.append(item_to_sell.get('name', '名もなきアイテム'))

    for inv_idx in sorted(inventory_indices_to_remove, reverse=True):
        del game_state['inventory'][inv_idx]

    if total_earned > 0:
        game_state['gold'] += total_earned
        game_state['log'].append(f"【売却】{len(sold_item_names)}個のアイテムを売却し、{total_earned}G を手に入れた。")

    session['game_state'] = game_state
    return redirect(url_for('workshop_sell_ui'))

@app.route('/workshop/appraise')
def workshop_appraise_ui():
    if 'game_state' not in session:
        return redirect(url_for('index'))
    game_state = session.get('game_state', {})
    
    unidentified_items = []
    for inv_idx, item in enumerate(game_state.get('inventory', [])):
        if item and not item.get('is_identified', True):
             unidentified_items.append((item, f"inventory_{inv_idx}"))

    return render_template('workshop_appraise.html', unidentified_items=unidentified_items, game_state=game_state)

@app.route('/workshop/appraise/confirm/<slot_info>')
def workshop_appraise_confirm(slot_info):
    if 'game_state' not in session:
        return redirect(url_for('index'))
    
    game_state = session.get('game_state', {})
    item_to_appraise = None
    
    parts = slot_info.split('_')
    if parts[0] == 'inventory' and len(parts) == 2:
        inv_idx = int(parts[1])
        if 0 <= inv_idx < len(game_state['inventory']):
            item_to_appraise = game_state['inventory'][inv_idx]

    if not item_to_appraise:
        return redirect(url_for('workshop_appraise_ui'))

    hint = workshop_logic.get_appraisal_hint(item_to_appraise)
    return render_template('workshop_appraise_confirm.html', hint=hint, slot_info=slot_info)

@app.route('/workshop/appraise/execute/<slot_info>', methods=['POST'])
def workshop_appraise_execute(slot_info):
    if 'game_state' not in session:
        return redirect(url_for('index'))
    
    game_state = session.get('game_state', {})
    
    appraisal_cost = 5000
    if game_state['gold'] < appraisal_cost:
        return redirect(url_for('workshop_appraise_ui'))

    item_to_appraise = None
    item_index = -1
    parts = slot_info.split('_')
    if parts[0] == 'inventory' and len(parts) == 2:
        inv_idx = int(parts[1])
        if 0 <= inv_idx < len(game_state['inventory']):
            item_to_appraise = game_state['inventory'][inv_idx]
            item_index = inv_idx

    if not item_to_appraise:
        return redirect(url_for('workshop_appraise_ui'))

    game_state['gold'] -= appraisal_cost
    appraised_item = workshop_logic.appraise_item(item_to_appraise)
    game_state['inventory'][item_index] = appraised_item
    game_state['log'].append(f"【鑑定】{appraised_item['name']}の鑑定に成功した！")
    
    session['game_state'] = game_state
    
    return render_template('workshop_appraise_result.html', item=appraised_item)

@app.route('/item_shop')
def item_shop():
    if 'game_state' not in session:
        return redirect(url_for('index'))
    game_state = session.get('game_state', {})
    pc_level = game_state['pc'].get('level', 1)
    world_tier = game_state.get('world_tier', 1)
    
    inventory = item_shop_logic.get_shop_inventory(pc_level, world_tier)
    
    return render_template('item_shop.html', inventory=inventory, game_state=game_state)

@app.route('/item_shop/buy', methods=['POST'])
def item_shop_buy():
    if 'game_state' not in session:
        return redirect(url_for('index'))
    
    game_state = session.get('game_state', {})
    
    total_cost = 0
    items_to_buy = []
    
    pc_level = game_state['pc'].get('level', 1)
    world_tier = game_state.get('world_tier', 1)
    shop_inventory = item_shop_logic.get_shop_inventory(pc_level, world_tier)
    
    for item in shop_inventory:
        buy_amount_str = request.form.get(f"buy_amount_{item['id']}")
        if buy_amount_str and buy_amount_str.isdigit():
            buy_amount = int(buy_amount_str)
            if buy_amount > 0:
                total_cost += item['price'] * buy_amount
                items_to_buy.append({'item': item, 'amount': buy_amount})

    if game_state['gold'] >= total_cost:
        game_state['gold'] -= total_cost
        if 'inventory' not in game_state:
            game_state['inventory'] = []
        for a in items_to_buy:
            for _ in range(a['amount']):
                game_state['inventory'].append(a['item'])
            game_state['log'].append(f"【購入】{a['item']['name']}を{a['amount']}個購入した。")
    else:
        game_state['log'].append("【購入失敗】所持金が不足しています。")

    session['game_state'] = game_state
    return redirect(url_for('item_shop'))

@app.route('/warehouse')
def warehouse():
    if 'game_state' not in session:
        return redirect(url_for('index'))
    game_state = session.get('game_state', {})
    
    inventory_items = list(enumerate(game_state.get('inventory', [])))
    warehouse_items = list(enumerate(game_state.get('warehouse', [])))

    return render_template('warehouse.html', inventory_items=inventory_items, warehouse_items=warehouse_items, game_state=game_state)

@app.route('/warehouse/deposit', methods=['POST'])
def warehouse_deposit():
    if 'game_state' not in session:
        return redirect(url_for('index'))
    
    game_state = session.get('game_state', {})
    item_index_str = request.form.get('item_index')
    
    try:
        item_index = int(item_index_str)
        if 0 <= item_index < len(game_state['inventory']):
            item_to_deposit = game_state['inventory'].pop(item_index)
            game_state['warehouse'].append(item_to_deposit)
            session['game_state'] = game_state
    except (ValueError, TypeError):
        pass

    return redirect(url_for('warehouse'))

@app.route('/warehouse/withdraw', methods=['POST'])
def warehouse_withdraw():
    if 'game_state' not in session:
        return redirect(url_for('index'))
        
    game_state = session.get('game_state', {})
    item_index_str = request.form.get('item_index')

    try:
        item_index = int(item_index_str)
        if 0 <= item_index < len(game_state['warehouse']):
            item_to_withdraw = game_state['warehouse'].pop(item_index)
            game_state['inventory'].append(item_to_withdraw)
            session['game_state'] = game_state
    except (ValueError, TypeError):
        pass

    return redirect(url_for('warehouse'))
    
@app.route('/skill_vault')
def skill_vault():
    if 'game_state' not in session:
        return redirect(url_for('index'))
    
    game_state = session.get('game_state', {})
    party_members = list(enumerate(game_state.get('party', [])))
    
    return render_template('skill_vault_character_select.html', 
                           party_members=party_members, 
                           game_state=game_state)

@app.route('/skill_vault/manage/<int:character_index>')
def skill_vault_manage(character_index):
    if 'game_state' not in session:
        return redirect(url_for('index'))
    
    game_state = session.get('game_state', {})
    if not (0 <= character_index < len(game_state['party'])):
        return redirect(url_for('skill_vault'))
        
    character = game_state['party'][character_index]
    
    equipped_skills = list(enumerate(character.get('skills', [])))
    
    unequipped_skills = [skill for skill in character.get('skill_pool', []) if skill not in character.get('skills', [])]

    return render_template('skill_vault_manage.html', 
                           character=character, 
                           character_index=character_index,
                           equipped_skills=equipped_skills,
                           unequipped_skills=unequipped_skills,
                           game_state=game_state)

@app.route('/skill_vault/unequip/<int:character_index>', methods=['POST'])
def skill_vault_unequip(character_index):
    if 'game_state' not in session:
        return redirect(url_for('index'))
    
    game_state = session.get('game_state', {})
    skill_index = int(request.form.get('skill_index'))

    if 0 <= character_index < len(game_state['party']):
        character = game_state['party'][character_index]
        if 0 <= skill_index < len(character['skills']):
            character['skills'].pop(skill_index)
            session['game_state'] = game_state

    return redirect(url_for('skill_vault_manage', character_index=character_index))

@app.route('/skill_vault/equip/<int:character_index>', methods=['POST'])
def skill_vault_equip(character_index):
    if 'game_state' not in session:
        return redirect(url_for('index'))
        
    game_state = session.get('game_state', {})
    skill_name = request.form.get('skill_name')

    if 0 <= character_index < len(game_state['party']):
        character = game_state['party'][character_index]
        if len(character['skills']) < 5:
            if skill_name in character.get('skill_pool', []):
                character['skills'].append(skill_name)
                session['game_state'] = game_state

    return redirect(url_for('skill_vault_manage', character_index=character_index))

@app.route('/world_tier')
def world_tier_ui():
    if 'game_state' not in session:
        return redirect(url_for('index'))
    game_state = session.get('game_state', {})
    
    available_tiers = {}
    # 仮で3ティアまで表示
    for i in range(1, 4):
        tier_data = world_tier_logic.get_world_tier_info(i)
        tier_data['unlocked'] = (i <= game_state.get('world_tier', 1) or world_tier_logic.can_unlock_next_tier(game_state))
        tier_data['unlock_condition'] = f"PCレベル {10 * (i-1)} 到達" # 仮
        available_tiers[i] = tier_data

    return render_template('world_tier.html', 
                           current_tier=game_state.get('world_tier', 1),
                           available_tiers=available_tiers)

@app.route('/world_tier/change', methods=['POST'])
def change_world_tier():
    if 'game_state' not in session:
        return redirect(url_for('index'))
    
    game_state = session.get('game_state', {})
    new_tier = int(request.form.get('new_tier'))

    # TODO: 変更可能かどうかの再検証
    game_state['world_tier'] = new_tier
    game_state['log'].append(f"【世界変動】WorldTierが {new_tier} に変更されました。")
    session['game_state'] = game_state

    return redirect(url_for('world_tier_ui'))

@app.route('/dungeon_select')
def dungeon_select():
    if 'game_state' not in session:
        return redirect(url_for('index'))
    
    dungeons = [
        {"id": 1, "name": "忘れられた地下墓所", "floors": 10, "description": "静寂に包まれた古い墓所。アンデッドの気配が漂う。"},
        {"id": 2, "name": "蠢く森", "floors": 20, "description": "奇妙な植物が自生し、獣の咆哮が木霊する森。"},
        {"id": 3, "name": "崩壊した監視塔", "floors": 30, "description": "かつて国境を守っていた塔。今は魔物の巣窟となっている。"},
    ]
    return render_template('dungeon_select.html', dungeons=dungeons)

@app.route('/dungeon/enter/<int:dungeon_id>')
def enter_dungeon(dungeon_id):
    if 'game_state' not in session:
        return redirect(url_for('index'))
    
    game_state = session['game_state']
    pc_level = game_state['pc'].get('level', 1)
    world_tier = game_state.get('world_tier', 1)
    
    floor_number = 1
    floor_data = dungeon_logic.generate_floor(dungeon_id, floor_number, pc_level, world_tier)
    
    game_state['location'] = 'dungeon'
    game_state['dungeon_info'] = {
        'id': dungeon_id,
        'name': f"ダンジョン{dungeon_id}",
        'current_floor': floor_number
    }
    game_state['floor_data'] = floor_data
    game_state['current_event_id'] = 'event_0'
    game_state['log'].append(f"【ダンジョン{dungeon_id}】に入場した。")
    
    session['game_state'] = game_state
    
    return redirect(url_for('dungeon_view'))

@app.route('/dungeon/view')
def dungeon_view():
    if 'game_state' not in session or session['game_state'].get('location') != 'dungeon':
        return redirect(url_for('hub'))
        
    game_state = session.get('game_state', {})
    current_event_id = game_state.get('current_event_id')
    floor_data = game_state.get('floor_data', {})
    event_data = floor_data.get('events', {}).get(current_event_id)

    if not event_data:
        return redirect(url_for('hub'))

    event_type = event_data.get('type')
    if event_type == dungeon_logic.EVENT_TYPE_TREASURE:
        return render_template('dungeon_treasure.html', game_state=game_state, event_data=event_data)
    
    return render_template('dungeon_explore.html', game_state=game_state, event_data=event_data)

@app.route('/dungeon/action', methods=['POST'])
def dungeon_action():
    if 'game_state' not in session or session['game_state'].get('location') != 'dungeon':
        return redirect(url_for('hub'))

    game_state = session['game_state']
    action = request.form.get('action')
    
    current_event_id = game_state.get('current_event_id')
    floor_data = game_state.get('floor_data', {})
    event_data = floor_data.get('events', {}).get(current_event_id)

    if not event_data:
        return redirect(url_for('dungeon_view'))
        
    next_event_id = None
    for choice in event_data.get('choices', {}).values():
        if choice.get('action') == action:
            next_event_id = choice.get('next_event_id')
            break
            
    if action == "go_to_next_floor":
        dungeon_id = game_state['dungeon_info']['id']
        next_floor_number = game_state['dungeon_info']['current_floor'] + 1
        pc_level = game_state['pc'].get('level', 1)
        world_tier = game_state.get('world_tier', 1)
        
        new_floor_data = dungeon_logic.generate_floor(dungeon_id, next_floor_number, pc_level, world_tier)
        
        game_state['dungeon_info']['current_floor'] = next_floor_number
        game_state['floor_data'] = new_floor_data
        game_state['current_event_id'] = 'event_0'
        game_state['log'].append(f"{next_floor_number}階層へ進んだ。")
        
    elif action == "return_to_hub":
        return redirect(url_for('hub'))
    
    elif action == "proceed" and next_event_id:
         game_state['current_event_id'] = next_event_id
         game_state['log'].append(f"先に進んだ。")

    elif action == "open_treasure":
        item = event_data.get('item')
        if 'inventory' not in game_state:
            game_state['inventory'] = []
        game_state['inventory'].append(item)
        game_state['log'].append(f"宝箱から『{item.get('name', '')}』を手に入れた！")
        if next_event_id:
            game_state['current_event_id'] = next_event_id
        
    session['game_state'] = game_state
    return redirect(url_for('dungeon_view'))

if __name__ == '__main__':
    app.run(debug=True)