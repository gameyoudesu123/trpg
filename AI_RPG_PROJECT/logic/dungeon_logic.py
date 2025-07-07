import random
import trgp # 変更点: from . import trgp から変更
from . import item_logic

# イベント種別の定義
EVENT_TYPE_BATTLE = "通常戦闘"
EVENT_TYPE_ELITE_BATTLE = "強敵戦闘"
EVENT_TYPE_TREASURE = "宝箱発見"
EVENT_TYPE_TRAP = "罠"
EVENT_TYPE_NPC = "NPC遭遇"
EVENT_TYPE_SPECIAL = "特殊イベント（TRGP劇場）"
EVENT_TYPE_EXIT = "次階層への道発見"

# 設計書【3.4(b)】固定ランダムイベント発生確率テーブル
EVENT_PROBABILITY_TABLE = {
    EVENT_TYPE_BATTLE: 40,
    EVENT_TYPE_ELITE_BATTLE: 15,
    EVENT_TYPE_TREASURE: 10,
    EVENT_TYPE_TRAP: 10,
    EVENT_TYPE_NPC: 5,
    EVENT_TYPE_SPECIAL: 10,
    EVENT_TYPE_EXIT: 10,
}

def get_random_event_type():
    """
    設計書【3.4(b)】に基づき、ランダムイベントの種類を確率的に決定する
    """
    total_probability = sum(EVENT_PROBABILITY_TABLE.values())
    roll = random.uniform(0, total_probability)
    
    cumulative_probability = 0
    for event_type, probability in EVENT_PROBABILITY_TABLE.items():
        cumulative_probability += probability
        if roll < cumulative_probability:
            return event_type
            
    return EVENT_TYPE_BATTLE # フォールバック

def generate_event_details(event_type, pc_level, world_tier):
    """
    イベントの種類に応じて、その詳細な内容を生成する
    設計書【3.4(c)】に基づく
    """
    details = {'type': event_type}
    if event_type == EVENT_TYPE_BATTLE:
        # TODO: 【5.0】モンスター生成プロトコルを呼び出す
        details['description'] = "前方に魔物の気配がする！"
        details['enemies'] = ["ゴブリン", "スライム"] # 仮データ
    elif event_type == EVENT_TYPE_TREASURE:
        # 設計書【6.10.3】宝箱発見
        # TODO: 罠の有無を判定
        details['description'] = "古びた宝箱を見つけた。"
        # アイテム生成ロジックを呼び出す
        item = item_logic.create_random_item(pc_level, world_tier)
        details['item'] = item
        details['is_trap'] = False # 仮データ
    elif event_type == EVENT_TYPE_TRAP:
        details['description'] = "足元に巧妙な罠が仕掛けられている！"
        details['trap_type'] = "毒矢" # 仮データ
    else:
        # その他のイベントは後ほど実装
        details['description'] = f"あなたは{event_type}に遭遇した。"

    return details


def generate_floor(dungeon_id, floor_number, pc_level, world_tier):
    """
    設計書【3.3.5】に基づき、単一の階層データを生成する
    """
    floor_data = {
        'dungeon_id': dungeon_id,
        'floor_number': floor_number,
        'description': f"{floor_number}階層。ひんやりとした空気が漂っている。",
        'events': {}
    }

    # 「幹・枝」方式
    main_path_ids = ['event_0', 'event_1', 'event_2', 'exit']
    
    for i in range(len(main_path_ids)):
        event_id = main_path_ids[i]
        
        if event_id == 'exit':
            event_details = generate_event_details(EVENT_TYPE_EXIT, pc_level, world_tier)
            event_details.update({
                'id': event_id,
                'description': "探索の末、次の階層へと続く階段を発見した。",
                'choices': {
                    "1": {"text": "次の階層へ進む", "action": "go_to_next_floor"},
                    "2": {"text": "街へ戻る", "action": "return_to_hub"}
                }
            })
            floor_data['events'][event_id] = event_details
            continue

        event_type = get_random_event_type()
        if i == len(main_path_ids) - 2:
             event_type = EVENT_TYPE_BATTLE

        event_details = generate_event_details(event_type, pc_level, world_tier)
        event_details.update({
            'id': event_id,
            'choices': {
                 "1": {"text": "先に進む", "action": "proceed", "next_event_id": main_path_ids[i+1]},
            }
        })
        floor_data['events'][event_id] = event_details

        if random.random() < 0.7:
            branch_event_id = f"branch_{i}"
            branch_event_type = get_random_event_type()
            while branch_event_type in [EVENT_TYPE_BATTLE, EVENT_TYPE_ELITE_BATTLE, EVENT_TYPE_EXIT]:
                branch_event_type = get_random_event_type()
            
            branch_event_details = generate_event_details(branch_event_type, pc_level, world_tier)
            branch_event_details.update({
                'id': branch_event_id,
                 'choices': {
                    "1": {"text": "元の道に戻る", "action": "proceed", "next_event_id": event_id}
                }
            })
            floor_data['events'][branch_event_id] = branch_event_details
            
            branch_choice_num = str(len(floor_data['events'][event_id]['choices']) + 1)
            floor_data['events'][event_id]['choices'][branch_choice_num] = {
                "text": "脇道へ進む",
                "action": "proceed",
                "next_event_id": branch_event_id
            }

    return floor_data
