import uuid

class PlayerCharacter:
    def __init__(self):
        # 全てのキャラクターがユニークなIDを持つようにする
        self.id = str(uuid.uuid4())
        
        # キャラクターのタイプを明示的に保持
        self.type = "player"

        # (その他の項目は変更なし)
        self.name, self.age, self.gender, self.appearance = "", 0, "", ""
        self.level, self.exp, self.exp_for_next_level = 1, 0, 100
        self.class_name, self.class_level, self.class_exp, self.class_exp_for_next_level = "", 1, 0, 80
        self.talent_seed, self.karma = "", 0
        self.hp, self.max_hp, self.ap, self.max_ap = 30, 30, 3, 3
        self.physical_defense, self.magic_defense = 0, 0
        self.active_skills, self.skill_vault = [], []
        self.equipment = {
            "右手": None, "左手": None, "頭部": None, "胴部": None, "脚部": None,
            "首飾り": None, "指輪1": None, "指輪2": None, "装飾品A": None
        }
        self.inventory, self.gold = [], 50

    def to_dict(self):
        """
        【バグ修正】
        オブジェクトの情報を辞書形式に変換するメソッド。
        セッションに保存する際に利用する。
        """
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        """
        【バグ修正】
        辞書からPlayerCharacterオブジェクトを復元するクラスメソッド。
        セッションから読み出す際に利用する。
        """
        instance = cls()
        instance.__dict__.update(data)
        return instance

    def __repr__(self):
        return (f"<PC: {self.name} | Lv:{self.level} | HP:{self.hp}/{self.max_hp}>")
