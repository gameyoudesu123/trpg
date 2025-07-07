import math

def generate_initial_equipment(character_obj):
    initial_equipment = {
        "右手": {"id": "initial_sword", "name": "訓練用の剣", "ilv": 1, "rarity": "コモン", "enhancement": 0, "base_price": 50},
        "頭部": {"id": "initial_hat", "name": "革の帽子", "ilv": 1, "rarity": "コモン", "enhancement": 0, "base_price": 30},
        "胴部": {"id": "initial_cloth", "name": "布の服", "ilv": 1, "rarity": "コモン", "enhancement": 0, "base_price": 40}
    }
    character_obj.equipment.update(initial_equipment)
    return character_obj

# --- 【今回の実装箇所】 ---
def calculate_sell_price(item):
    """設計書【7.3(b)】に基づき、売却価格を計算する (基準価格の30%)"""
    base_price = item.get('base_price', 0)
    # 小数点以下は切り捨て
    return math.floor(base_price * 0.3)

# (強化関連の関数は変更なし)
def calculate_enhancement_cost(item, world_tier):
    rarity_base_cost = {"コモン": 10, "アンコモン": 30, "レア": 100, "エピック": 500, "レジェンド": 2500, "エンシェント": 10000}
    cost = ((item['ilv'] * 2) + rarity_base_cost.get(item['rarity'], 10) + (world_tier * 50)) * (1.8 ** item['enhancement'])
    return math.floor(cost)

def get_enhancement_preview(item):
    return "+5"