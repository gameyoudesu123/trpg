import math
import random
import trgp

# このファイルの上部は変更ありませんが、約束通り完全な形で提示します。

def calculate_base_price(item):
    """
    設計書【7.3(a)】に基づき、アイテムの基準価格を計算する
    """
    ilv = item.get('ilv', 1)
    rarity_id = item.get('rarity_id', 'COMMON')
    
    rarity_base_value = {
        "COMMON": 10, "UNCOMMON": 50, "RARE": 200, "EPIC": 1000,
        "LEGENDARY": 5000, "ANCIENT": 20000
    }.get(rarity_id, 10)

    base_price = rarity_base_value + (ilv ** 1.5)
    return math.floor(base_price)

def calculate_sell_price(item):
    """
    設計書【7.3(b)】に基づき、売却価格を計算する
    """
    base_price = calculate_base_price(item)
    return math.floor(base_price * 0.3)

def calculate_enhancement_cost(item, world_tier):
    """
    設計書【6.12(d)i】に基づき、装備強化のゴールドコストを計算する
    """
    rarity_id = item.get('rarity_id', 'COMMON')
    rarity_base_cost = {
        "COMMON": 10, "UNCOMMON": 30, "RARE": 100, "EPIC": 500,
        "LEGENDARY": 2500, "ANCIENT": 10000
    }.get(rarity_id, 10)

    ilv = item.get('ilv', 1)
    current_enhancement = item.get('enhancement', 0)

    cost = ((ilv * 2) + rarity_base_cost + (world_tier * 50)) * ((current_enhancement + 1) ** 1.8)
    
    return math.floor(cost)

def get_enhancement_preview(item):
    """
    設計書【6.12(f)】に基づき、強化後の性能上昇値をプレビューする
    """
    preview = {}
    
    if item.get('category_key') == 'WEAPON':
        current_damage = item.get('damage', '1d4+0')
        parts = current_damage.replace('+', 'd').split('d')
        increase = max(1, math.floor((int(parts[0]) * (1 + int(parts[1])) / 2) * 0.05))
        new_z = int(parts[2]) + increase
        preview['text'] = f"⚔️攻撃性能 ({current_damage}) → ({parts[0]}d{parts[1]}+{new_z})"
    else:
        current_def = item.get('defense', 10)
        increase = max(1, math.floor(current_def * 0.05))
        new_def = current_def + increase
        preview['text'] = f"🛡️物理防御 {current_def} → {new_def} (🔺+{increase})"
        
    return preview

def enhance_item(item, pc_gold, world_tier):
    """
    実際にアイテムを強化する処理
    """
    cost = calculate_enhancement_cost(item, world_tier)
    
    if pc_gold < cost:
        return None, "所持金が不足しています。", pc_gold

    item['enhancement'] = item.get('enhancement', 0) + 1
    
    if item.get('category_key') != 'WEAPON':
        current_def = item.get('defense', 10)
        increase = max(1, math.floor(current_def * 0.05))
        item['defense'] = current_def + increase
    
    remaining_gold = pc_gold - cost
    
    return item, remaining_gold, f"「{item.get('name', 'アイテム')}」の強化に成功した！"

def get_appraisal_hint(item):
    """
    設計書【6.9.1.A】に基づき、鑑定前のヒントを生成する
    """
    hints = [
        "こいつは…とんでもない業物だ。炎のような力を感じるぜ。",
        "ほう…？ なんだこの冷気は。まるで冬の神の吐息みてえだ。",
        "光と影…両方の性質を併せ持つ、稀有な一品だな。"
    ]
    return random.choice(hints)

def appraise_item(item):
    """
    設計書【6.9.1.C】に基づき、アイテムの鑑定を行う
    """
    item['name'] = item['name'].replace('封印されし', '解放されし')
    item['is_identified'] = True
    item['lore'] = "長きに渡る封印から解き放たれ、その真の力を現した伝説の武具。"
    
    item['options'].append("【固有アビリティ】神速 (行動速度+10%)")
    
    return item