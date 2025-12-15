from agents import HeuristicDungeonAgent
from battle_types import Stats, Team
from characters import PlayerCharacter, EnemyCharacter, FireDragon
from skills import SingleTargetAttackSkill, AreaAttackSkill, HealingSkill
from dungeon_env import DungeonFloorConfig
from ai_strategies import RandomAIStrategy, FocusWeakestAIStrategy # 成員 C 實作

def create_default_players() -> list:
    kiwi_skills = [
        SingleTargetAttackSkill("Kiwi Slash", mp_cost=3, power=12),  # 降低 MP 消耗
        AreaAttackSkill("Kiwi Whirlwind", mp_cost=8, power=8)  # 降低 MP 消耗
    ]
    # 大幅提升 Kiwi 數值
    kiwi = PlayerCharacter(
        name="Kiwi", 
        team=Team.PLAYERS,
        base_stats=Stats(max_hp=150, max_mp=80, attack=18, defense=8, speed=14),
        skills=kiwi_skills,
        agent=HeuristicDungeonAgent()
    )
    
    healer_skills = [HealingSkill("Holy Light", mp_cost=6, heal_power=35)]  # 更強的治療
    healer = PlayerCharacter(
        name="Healer Bird", 
        team=Team.PLAYERS,
        base_stats=Stats(max_hp=80, max_mp=100, attack=6, defense=5, speed=12),
        skills=healer_skills,
        role="Supporter",
        agent=HeuristicDungeonAgent()
    )
    return [kiwi, healer]

def build_dungeon_floors() -> list:
    """建立三層地城的配置 [cite: 94-95, 168]"""
    
    def floor_1_enemies():
        # B1: Slime / Goblin [cite: 169]
        return [
            EnemyCharacter("Green Slime", Team.ENEMIES, Stats(20, 0, 8, 2, 5), ai=RandomAIStrategy()),
            EnemyCharacter("Goblin", Team.ENEMIES, Stats(30, 0, 10, 3, 8), ai=RandomAIStrategy())
        ]

    def floor_2_enemies():
        # B2: Orc Warrior / Dark Mage [cite: 170]
        dark_mage_skills = [SingleTargetAttackSkill("Dark Bolt", 5, 12)]
        return [
            EnemyCharacter("Orc Warrior", Team.ENEMIES, Stats(60, 0, 15, 8, 7), ai=FocusWeakestAIStrategy()),
            EnemyCharacter("Dark Mage", Team.ENEMIES, Stats(40, 40, 12, 4, 11), 
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
                team=Team.ENEMIES, 
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