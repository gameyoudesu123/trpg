import random
import trgp
from . import character_logic # 既存のキャラクターロジックを再利用

def generate_companions(filters, word_list, pc_level, world_tier):
    """
    指定された条件に基づき、仲間NPCを3人生成する
    設計書【7.4.1(b)】に基づく
    """
    companions = []
    for _ in range(3):
        # 設計書【2.5(b)】仲間NPCの生成プロトコル
        # フィルター条件を考慮してキャラクターを生成
        # create_random_characterをベースに、フィルター機能を追加する必要がある
        # 今回は簡易的に、フィルターを無視してランダム生成
        
        # TODO: filters（クラス系統、性別）を反映させるロジックを後ほど実装
        
        npc = character_logic.create_random_character(word_list)
        
        # 設計書【2.5(b)i.7】レベルはPCと同期
        npc['level'] = pc_level
        
        # 設計書【7.4.1(b)iii】契約金の計算
        if pc_level < 10:
            npc['contract_fee'] = 15
        else:
            npc['contract_fee'] = (pc_level * 10) + (world_tier * 50)
            
        # 設計書【2.5(b)iv】自己紹介文の生成
        # TODO: 性格や背景に基づいた動的生成ロジックを後ほど実装
        npc['introduction'] = f"「{npc['name']}だ。{npc['class_name']}として腕を磨いている。あんたの旅、面白そうだな。一口乗らせてくれよ。」"

        companions.append(npc)
        
    return companions
