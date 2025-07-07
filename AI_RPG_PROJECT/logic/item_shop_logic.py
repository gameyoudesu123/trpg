import random
from . import item_logic

def get_shop_inventory(pc_level, world_tier):
    """
    設計書【7.4.3(c)】に基づき、道具屋の商品リストを生成する。
    レベル・ティア別道具屋ラインナップ固定テーブルを参照する想定。
    """
    # TODO: 本格的なテーブル参照ロジックを実装
    # 今回はプロトタイプとして、基本的な消費アイテムをリストアップ
    
    shop_inventory = []
    
    # ポーション
    potion = {
        "id": "POTION_01",
        "name": "ポーション",
        "rarity_symbol": "・",
        "price": 50,
        "stock": 10,
        "description": "❤️ HPを最大値の25%回復する",
        "icon": "fas fa-flask-potion"
    }
    shop_inventory.append(potion)

    # エーテル
    ether = {
        "id": "ETHER_01",
        "name": "エーテル",
        "rarity_symbol": "・",
        "price": 80,
        "stock": 5,
        "description": "⏳ APを2回復する (仮の効果)",
        "icon": "fas fa-bolt"
    }
    # shop_inventory.append(ether) # AP関連は設計書で禁止されているためコメントアウト

    # 解毒薬
    antidote = {
        "id": "ANTIDOTE_01",
        "name": "解毒薬",
        "rarity_symbol": "・",
        "price": 30,
        "stock": 10,
        "description": "🤢 毒状態を治療する",
        "icon": "fas fa-pills"
    }
    shop_inventory.append(antidote)

    return shop_inventory