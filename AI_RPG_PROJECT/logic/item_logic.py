import random
import trgp

# 設計書【6.2.1】レアリティ定義
RARITIES = {
    "COMMON": {"name": "コモン", "symbol": "・"},
    "UNCOMMON": {"name": "アンコモン", "symbol": "◆"},
    "RARE": {"name": "レア", "symbol": "★"},
    "EPIC": {"name": "エピック", "symbol": "✨"},
    "LEGENDARY": {"name": "レジェンダリー", "symbol": "⚜️"},
    "ANCIENT": {"name": "エンシェント", "symbol": "🌈"},
}

# 設計書【6.2.3(d)】レアリティ別固定生成率
RARITY_PROBABILITY = {
    "ANCIENT": 0.5,
    "LEGENDARY": 1.0,
    "EPIC": 3.0,
    "RARE": 10.0,
    "UNCOMMON": 30.0,
    "COMMON": 55.5,
}

# 設計書【6.1.2】アイテムカテゴリ
ITEM_CATEGORIES = {
    "WEAPON": ["片手剣", "両手斧", "魔導書", "短剣", "弓"],
    "ARMOR": ["兜", "鎧", "小手", "具足"],
    "ACCESSORY": ["アミュレット", "リング"]
}

def get_random_rarity():
    """
    設計書【6.2.3(d)】に基づき、レアリティを確率的に決定する
    """
    total = sum(RARITY_PROBABILITY.values())
    roll = random.uniform(0, total)
    
    cumulative = 0
    for rarity, probability in RARITY_PROBABILITY.items():
        cumulative += probability
        if roll < cumulative:
            return rarity
    return "COMMON" # フォールバック

def create_random_item(pc_level, world_tier, item_type_filter=None, category_key_filter=None):
    """
    設計書【6.0】に基づき、ランダムなアイテムを1つ生成する
    """
    # 設計書【6.3.1】ILvの決定
    ilv = max(pc_level + random.randint(-2, 3), world_tier)
    
    # レアリティ決定
    rarity_id = get_random_rarity()
    rarity_info = RARITIES[rarity_id]
    
    # カテゴリと種別を決定
    category_key = category_key_filter if category_key_filter else random.choice(list(ITEM_CATEGORIES.keys()))
    item_type = item_type_filter if item_type_filter else random.choice(ITEM_CATEGORIES[category_key])
    
    # 設計書【6.8】命名規則（簡易版）
    name_keywords = trgp.generate_trgp_keywords(MASTER_WORD_LIST, count=2)
    item_name = f"{rarity_info['name']}の{item_type}"
    item_nickname = f"「{name_keywords[0]['kanji']}の{name_keywords[1]['kanji']}」"

    # 設計書【6.3.2】基礎性能（簡易版）
    hp_bonus = int(((ilv * 2.0) ** 1.15) * 1.0) 
    
    # 仮のダメージと防御力
    damage = "1d4+1" if category_key == "WEAPON" else None
    defense = 10 + ilv * 2 if category_key == "ARMOR" else None

    # 設計書【6.3.3】オプション（簡易版）
    options = ["HP+10", "攻撃力+5"] 
    
    item = {
        "name": item_name,
        "nickname": item_nickname,
        "rarity_id": rarity_id, # 修正点: rarity_idを追加
        "rarity_symbol": rarity_info['symbol'],
        "type": item_type,
        "category_key": category_key,
        "ilv": ilv,
        "hp_bonus": hp_bonus,
        "damage": damage,
        "defense": defense,
        "options": options,
        "description": f"{name_keywords[0]['kanji']}と{name_keywords[1]['kanji']}の力が宿っているようだ。"
    }
    return item

# trgp.pyに渡すためにグローバル変数として定義
# 本来はもっと良い方法で渡すべきだが、一旦これでエラーを解消する
try:
    MASTER_WORD_LIST = data_loader.load_master_word_list()
except NameError:
    from . import data_loader
    MASTER_WORD_LIST = data_loader.load_master_word_list()