from battle_types import Stats
from characters import PlayerCharacter, EnemyCharacter, FireDragon
from skills import SingleTargetAttackSkill, AreaAttackSkill, HealingSkill
from dungeon_env import DungeonFloorConfig
from ai_strategies import RandomAIStrategy, FocusWeakestAIStrategy # 成員 C 實作

def create_default_players() -> list:
    """設定 Kiwi 與隊友的數值與技能 [cite: 92-93, 166]"""
    # 勇者 Kiwi：平衡型
    kiwi_skills = [
        SingleTargetAttackSkill("Kiwi Slash", mp_cost=5, power=10),
        AreaAttackSkill("Kiwi Whirlwind", mp_cost=12, power=6)
    ]
    kiwi = PlayerCharacter(
        name="Kiwi", 
        team="players", 
        base_stats=Stats(max_hp=100, max_mp=30, attack=15, defense=5, speed=12),
        skills=kiwi_skills
    )
    
    # 補師隊友：支援型
    healer_skills = [HealingSkill("Holy Light", mp_cost=8, heal_power=20)]
    healer = PlayerCharacter(
        name="Healer Bird", 
        team="players", 
        base_stats=Stats(max_hp=60, max_mp=50, attack=5, defense=3, speed=10),
        skills=healer_skills,
        role="Supporter"
    )
    return [kiwi, healer]

def build_dungeon_floors() -> list:
    """建立三層地城的配置 [cite: 94-95, 168]"""
    
    def floor_1_enemies():
        # B1: Slime / Goblin [cite: 169]
        return [
            EnemyCharacter("Green Slime", "enemies", Stats(20, 0, 8, 2, 5), ai=RandomAIStrategy()),
            EnemyCharacter("Goblin", "enemies", Stats(30, 0, 10, 3, 8), ai=RandomAIStrategy())
        ]

    def floor_2_enemies():
        # B2: Orc Warrior / Dark Mage [cite: 170]
        dark_mage_skills = [SingleTargetAttackSkill("Dark Bolt", 5, 12)]
        return [
            EnemyCharacter("Orc Warrior", "enemies", Stats(60, 0, 15, 8, 7), ai=FocusWeakestAIStrategy()),
            EnemyCharacter("Dark Mage", "enemies", Stats(40, 40, 12, 4, 11), 
                           skills=dark_mage_skills, ai=FocusWeakestAIStrategy())
        ]

    def floor_3_enemies():
        # B3: FireDragon Boss [cite: 171]
        boss_skills = [
            SingleTargetAttackSkill("Flame Bite", 0, 15),
            AreaAttackSkill("Inferno Breath", 20, 25)
        ]
        return [
            FireDragon(
                name="FireDragon", 
                team="enemies", 
                base_stats=Stats(max_hp=250, max_mp=100, attack=20, defense=10, speed=15),
                skills=boss_skills,
                enraged_threshold=0.3 # 低於 30% 進入狂暴 [cite: 143]
            )
        ]

    return [
        DungeonFloorConfig("Slime Tunnels", floor_1_enemies),
        DungeonFloorConfig("Dark Ritual Hall", floor_2_enemies),
        DungeonFloorConfig("Inferno Dragon's Lair", floor_3_enemies, is_boss_floor=True)
    ]