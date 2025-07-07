from flask import session
from models import PlayerCharacter, CompanionNPC, Enemy

def get_character_class(char_type):
    """キャラクタータイプに応じて適切なクラスを返す"""
    if char_type == 'player':
        return PlayerCharacter
    if char_type == 'companion':
        return CompanionNPC
    if char_type == 'enemy':
        return Enemy
    # デフォルトまたは不明なタイプの場合はNoneを返す
    return None

def _dicts_to_objects(dict_list):
    """辞書のリストを、タイプに応じたオブジェクトのリストに変換する"""
    if not dict_list:
        return []
    obj_list = []
    for data in dict_list:
        char_type = data.get('type')
        CharClass = get_character_class(char_type)
        if CharClass:
            obj_list.append(CharClass.from_dict(data))
    return obj_list

def _objects_to_dicts(obj_list):
    """オブジェクトのリストを辞書のリストに変換する"""
    if not obj_list:
        return []
    return [obj.to_dict() for obj in obj_list]

def get_party():
    """セッションからパーティ情報を読み出し、オブジェクトのリストとして返す"""
    party_dicts = session.get('party', [])
    return _dicts_to_objects(party_dicts)

def save_party(party_objs):
    """パーティのオブジェクトリストを、セッションに保存できる辞書のリストに変換して保存"""
    session['party'] = _objects_to_dicts(party_objs)
    session.modified = True

def get_candidates():
    """セッションから仲間候補を読み出す"""
    candidate_dicts = session.get('companion_candidates', [])
    return _dicts_to_objects(candidate_dicts)

def save_candidates(candidate_objs):
    """仲間候補をセッションに保存"""
    session['companion_candidates'] = _objects_to_dicts(candidate_objs)
    session.modified = True

def get_enemies():
    """セッションから敵情報を読み出す"""
    enemy_dicts = session.get('combat_enemies', [])
    return _dicts_to_objects(enemy_dicts)

def save_enemies(enemy_objs):
    """敵情報をセッションに保存"""
    session['combat_enemies'] = _objects_to_dicts(enemy_objs)
    session.modified = True
