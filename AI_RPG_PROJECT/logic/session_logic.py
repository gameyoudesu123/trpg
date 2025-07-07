from flask import session
from models import PlayerCharacter

def get_party():
    """セッションからパーティ情報を読み出し、オブジェクトのリストとして返す"""
    party_dicts = session.get('party', [])
    party_objs = []
    for char_dict in party_dicts:
        char = PlayerCharacter()
        char.__dict__.update(char_dict)
        party_objs.append(char)
    return party_objs

def save_party(party_objs):
    """パーティのオブジェクトリストを、セッションに保存できる辞書のリストに変換して保存"""
    session['party'] = [char.__dict__ for char in party_objs]

def get_candidates():
    """セッションから仲間候補を読み出す"""
    candidate_dicts = session.get('companion_candidates', [])
    candidate_objs = []
    for char_dict in candidate_dicts:
        char = PlayerCharacter()
        char.__dict__.update(char_dict)
        candidate_objs.append(char)
    return candidate_objs

def save_candidates(candidate_objs):
    """仲間候補をセッションに保存"""
    session['companion_candidates'] = [char.__dict__ for char in candidate_objs]