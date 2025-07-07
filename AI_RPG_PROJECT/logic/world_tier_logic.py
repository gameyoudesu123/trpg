import random
import trgp
# from . import dungeon_logic # 将来的に使用する

def execute_world_tier_transition(game_state):
    """
    設計書【3.1.3】のプロシージャを忠実に実行する
    """
    new_tier = game_state.get('world_tier', 1) + 1
    
    # Step 1: 旧世界のデータ消去と新世界のテーマ決定
    # TODO: WipeAllDungeonData(), WipeAllTierSpecificFlags() の実装
    
    new_theme = determine_world_theme(new_tier, game_state)
    game_state['world_theme'] = new_theme
    
    # Step 2: 新世界のダンジョン群生成
    # TODO: dungeon_logic.generate_all_new_dungeons(new_tier, new_theme) の呼び出し
    
    # Step 3: 拠点施設のラインナップ更新
    # TODO: UpdateHubFacilities(new_tier) の実装
    
    # Step 4: プレイヤーへの通知
    # メッセージはapp.py側で生成し、ログに追加する
    
    game_state['world_tier'] = new_tier
    
    return game_state

def determine_world_theme(new_tier, game_state):
    """
    設計書【3.1.3.1】に基づき、世界のテーマを決定する
    """
    if new_tier == 1:
        # (a) ティア1のテーマ固定
        return "THEME_FANTASY"
    
    # (b) ティア2以降のTRGPによるテーマ生成
    # TODO: 設計書通りのTRGPキーワード抽出、フィルタリング、最終決定ロジックを実装
    # 今回はプロトタイプとして、ランダムなテーマを返す
    
    # from logic.data_loader import MASTER_WORD_LIST # 本来はここではない
    # keyword = trgp.generate_trgp_keywords(MASTER_WORD_LIST, count=1)
    # ... フィルタリング処理 ...
    
    possible_themes = ["THEME_STEAMPUNK", "THEME_CYBERPUNK", "THEME_HORROR", "THEME_JAPANESQUE"]
    return random.choice(possible_themes)

def get_unlock_conditions():
    """
    設計書【3.1.3】に基づき、各ティアの解放条件を定義する
    """
    # 修正：深淵の回廊ではなく、次元の覇者討伐を条件とする
    return {
        2: {"flag": "cleared_ruler_of_dimension_1", "text": "第1世界の「次元の覇者」を討伐"},
        3: {"flag": "cleared_ruler_of_dimension_2", "text": "第2世界の「次元の覇者」を討伐"},
        4: {"flag": "cleared_ruler_of_dimension_3", "text": "第3世界の「次元の覇者」を討伐"},
        5: {"flag": "cleared_ruler_of_dimension_4", "text": "第4世界の「次元の覇者」を討伐"},
    }