import random

def generate_party_conversation(party_members):
    """
    設計書【8.3.7】に基づき、パーティ全員での会話を生成する。
    今回はプロトタイプとして、固定のテキストを返す。
    """
    companions_in_party = [member for member in party_members if not member.get('is_pc', False)]
    if companions_in_party:
        first_companion_name = companions_in_party[0].get('name', '仲間')
        pc_name = "あなた"
        for member in party_members:
            if member.get('is_pc', False):
                pc_name = member.get('name', 'あなた')
                break
        return f"（{first_companion_name}と{pc_name}は、次のダンジョンについて言葉を交わしている…）"
    else:
        return "（今は一人、静かに酒を飲むしかなさそうだ…）"

def get_individual_topics(companion):
    """
    設計書【7.4.1.1(c)i】に基づき、仲間NPCの個別会話トピックを生成する。
    今回はプロトタイプとして、固定のトピックを返す。
    """
    topics = [
        f"{companion['name']}の故郷について",
        f"{companion['name']}が冒険者になった理由"
    ]
    return topics

def process_conversation_actions(game_state, actions):
    """
    選択された会話アクションを処理し、シナリオと好感度変動を生成する
    """
    results = []
    log = []
    
    # TODO: 設計書【7.4.1.1(c)】の複合入力解析エンジンをここに実装
    
    # 今回は簡易的に、各アクションをループ処理
    for action in actions:
        # TODO: actionの内容を解析し、対象NPCとトピックを特定する
        # 現状は仮で、最初の仲間との好感度が上がる処理のみ
        if len(game_state['party']) > 1:
            companion = game_state['party'][1] # 最初の仲間を対象とする
            pc = game_state['pc']
            
            # 設計書【8.3.7.1】ショートショートシナリオ生成
            # TODO: Gemini APIで動的生成
            scenario = f"「{action}」について、{pc['name']}と{companion['name']}は語り合った。二人の間には穏やかな時間が流れる。"
            
            # 設計書【8.3.2】好感度変動
            # 仮で+5ポイント加算
            affection_change = 5
            
            # 好感度データを更新
            # companion['affection'][pc['id']] += affection_change のような処理が必要
            # 今回はログ表示のみ
            log_message = f"【好感度変動】{companion['name']}のあなたへの好感度が +{affection_change} された。"
            
            results.append({
                "scenario": scenario,
                "log": log_message
            })
            log.append(log_message)

    return results, log