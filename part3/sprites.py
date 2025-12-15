# sprites.py
"""
角色精靈繪製模組 - 可愛風格版
根據參考圖重新設計：圓滾滾的奇異鳥 + 帥氣的龍
"""
from __future__ import annotations
import pygame
import math
from typing import Tuple

# 顏色定義
KIWI_BROWN = (165, 130, 100)
KIWI_DARK = (120, 90, 65)
KIWI_BEAK = (240, 220, 180)
HEALER_WHITE = (250, 248, 245)
HEALER_CREAM = (255, 240, 220)
HEALER_PINK = (255, 200, 200)
SLIME_GREEN = (100, 220, 120)
SLIME_LIGHT = (150, 255, 170)
GOBLIN_GREEN = (90, 120, 70)
GOBLIN_SKIN = (120, 155, 90)
ORC_GREEN = (70, 100, 60)
ORC_ARMOR = (80, 75, 70)
MAGE_ROBE = (50, 35, 70)
MAGE_PURPLE = (160, 80, 220)
# 龍的顏色 - 類似 Mega Charizard X
DRAGON_BODY = (55, 65, 80)
DRAGON_BELLY = (150, 180, 200)
DRAGON_FLAME = (80, 180, 255)
DRAGON_DARK = (35, 40, 50)


class SpriteRenderer:
    """精靈繪製器"""
    
    @staticmethod
    def draw_kiwi(surface: pygame.Surface, x: int, y: int, size: int = 60, 
                  alive: bool = True, animation_offset: float = 0) -> None:
        """繪製超可愛奇異鳥 - 極簡風格，圓圓身體+長嘴巴+點點眼"""
        if not alive:
            body_color = (120, 110, 100)
            outline = (80, 75, 70)
            beak_color = (180, 170, 160)
        else:
            body_color = (180, 145, 115)  # 溫暖的棕色
            outline = (60, 50, 40)         # 深色輪廓
            beak_color = (245, 225, 180)   # 奶油色嘴巴
        
        # 可愛的呼吸動畫
        breathe = math.sin(animation_offset * 2) * 2
        squish = 1.0 + math.sin(animation_offset * 2.5) * 0.03  # 微微壓扁
        cy = y + int(breathe)
        
        # === 圓圓的身體 ===
        body_w = int(size * 0.65 * squish)
        body_h = int(size * 0.58 / squish)
        body_rect = pygame.Rect(x - body_w, cy - body_h, body_w * 2, body_h * 2)
        
        # 用多層圓形營造柔軟感
        pygame.draw.ellipse(surface, body_color, body_rect)
        
        # 可愛風格的粗輪廓線
        pygame.draw.ellipse(surface, outline, body_rect, 4)
        
        # === 長長彎彎的嘴巴 ===
        beak_len = int(size * 0.55)
        beak_start_x = x + body_w // 2
        beak_start_y = cy + 2
        
        # 優雅的曲線嘴巴
        beak_points = [
            (beak_start_x - 8, beak_start_y - 5),   # 上緣
            (beak_start_x + beak_len, beak_start_y),  # 尖端
            (beak_start_x - 8, beak_start_y + 8),   # 下緣
        ]
        pygame.draw.polygon(surface, beak_color, beak_points)
        pygame.draw.polygon(surface, outline, beak_points, 3)
        
        # 嘴巴中線（微笑感）
        pygame.draw.line(surface, outline, 
                        (beak_start_x - 3, beak_start_y + 1),
                        (beak_start_x + int(beak_len * 0.85), beak_start_y), 2)
        
        # === 超可愛的點點眼 ===
        eye_x = x + 5
        eye_y = cy - body_h // 3
        
        # 小小的圓眼睛
        pygame.draw.circle(surface, (15, 15, 15), (eye_x, eye_y), 5)
        # 閃亮高光
        pygame.draw.circle(surface, (255, 255, 255), (eye_x + 1, eye_y - 1), 2)
        
        # === 迷你小腳 ===
        foot_y = cy + body_h - 3
        foot_color = outline
        
        # 簡單的小爪子
        pygame.draw.line(surface, foot_color, (x - 10, foot_y), (x - 10, foot_y + 10), 3)
        pygame.draw.line(surface, foot_color, (x + 10, foot_y), (x + 10, foot_y + 10), 3)
        # 小爪尖
        pygame.draw.circle(surface, foot_color, (x - 13, foot_y + 10), 2)
        pygame.draw.circle(surface, foot_color, (x - 7, foot_y + 10), 2)
        pygame.draw.circle(surface, foot_color, (x + 7, foot_y + 10), 2)
        pygame.draw.circle(surface, foot_color, (x + 13, foot_y + 10), 2)
        
        # === 頭頂小毛（僅存活時顯示）===
        if alive:
            tuft_x = x - 8
            tuft_y = cy - body_h + 3
            # 簡單兩根呆毛
            pygame.draw.line(surface, outline, (tuft_x, tuft_y), (tuft_x - 4, tuft_y - 12), 3)
            pygame.draw.line(surface, outline, (tuft_x + 5, tuft_y), (tuft_x + 2, tuft_y - 10), 3)

    @staticmethod
    def draw_healer(surface: pygame.Surface, x: int, y: int, size: int = 50,
                    alive: bool = True, animation_offset: float = 0) -> None:
        """繪製可愛的白色補師鳥"""
        if not alive:
            color = (100, 100, 100)
            cream = (80, 80, 80)
        else:
            color = HEALER_WHITE
            cream = HEALER_CREAM
        
        float_y = int(math.sin(animation_offset * 3) * 3)
        cy = y + float_y
        
        # 光環
        if alive:
            halo_pulse = int(abs(math.sin(animation_offset * 4)) * 30) + 50
            halo_surf = pygame.Surface((80, 40), pygame.SRCALPHA)
            pygame.draw.ellipse(halo_surf, (255, 230, 150, halo_pulse), (5, 5, 70, 25), 3)
            surface.blit(halo_surf, (x - 40, cy - size // 2 - 20))
        
        # 身體（圓形）
        body_r = size // 2
        pygame.draw.circle(surface, color, (x, cy), body_r)
        pygame.draw.circle(surface, (200, 195, 190), (x, cy), body_r, 2)
        
        # 臉頰紅暈
        if alive:
            pygame.draw.circle(surface, HEALER_PINK, (x - body_r // 2, cy + 5), 6)
            pygame.draw.circle(surface, HEALER_PINK, (x + body_r // 2, cy + 5), 6)
        
        # 眼睛
        pygame.draw.circle(surface, (30, 30, 30), (x - 8, cy - 5), 4)
        pygame.draw.circle(surface, (30, 30, 30), (x + 8, cy - 5), 4)
        pygame.draw.circle(surface, (255, 255, 255), (x - 7, cy - 6), 2)
        pygame.draw.circle(surface, (255, 255, 255), (x + 9, cy - 6), 2)
        
        # 小嘴
        pygame.draw.polygon(surface, (255, 200, 150), 
                           [(x, cy + 5), (x - 4, cy + 10), (x + 4, cy + 10)])
        
        # 翅膀
        wing_offset = int(math.sin(animation_offset * 5) * 3)
        pygame.draw.ellipse(surface, cream, 
                           (x - body_r - 8, cy - 10 + wing_offset, 15, 25))
        pygame.draw.ellipse(surface, cream, 
                           (x + body_r - 7, cy - 10 - wing_offset, 15, 25))
        
        # 治療十字
        if alive:
            cross_color = (100, 220, 100)
            pygame.draw.rect(surface, cross_color, (x + body_r - 5, cy - body_r, 8, 20))
            pygame.draw.rect(surface, cross_color, (x + body_r - 11, cy - body_r + 6, 20, 8))

    @staticmethod
    def draw_slime(surface: pygame.Surface, x: int, y: int, size: int = 40,
                   alive: bool = True, animation_offset: float = 0) -> None:
        """繪製 Q 彈史萊姆"""
        if not alive:
            color = (80, 80, 80)
            light = (100, 100, 100)
        else:
            color = SLIME_GREEN
            light = SLIME_LIGHT
        
        # 彈跳變形
        squish = math.sin(animation_offset * 5)
        w = int(size * (1.0 + squish * 0.1))
        h = int(size * 0.7 * (1.0 - squish * 0.1))
        
        # 主體
        slime_rect = pygame.Rect(x - w // 2, y - h + 10, w, h)
        pygame.draw.ellipse(surface, color, slime_rect)
        
        # 高光
        if alive:
            pygame.draw.ellipse(surface, light, 
                               (x - w // 3, y - h + 15, w // 3, h // 3))
        
        # 眼睛
        eye_y = y - h // 2 + 5
        pygame.draw.ellipse(surface, (255, 255, 255), (x - 10, eye_y - 5, 10, 14))
        pygame.draw.ellipse(surface, (255, 255, 255), (x + 2, eye_y - 5, 10, 14))
        pygame.draw.circle(surface, (20, 20, 20), (x - 4, eye_y + 2), 3)
        pygame.draw.circle(surface, (20, 20, 20), (x + 8, eye_y + 2), 3)
        
        # 水滴效果
        pygame.draw.circle(surface, color, (x - w // 2 + 5, y + 5), 4)
        pygame.draw.circle(surface, color, (x + w // 2 - 8, y + 3), 3)

    @staticmethod
    def draw_goblin(surface: pygame.Surface, x: int, y: int, size: int = 45,
                    alive: bool = True, animation_offset: float = 0) -> None:
        """繪製哥布林 - 尖耳綠皮小怪"""
        if not alive:
            skin = (80, 80, 80)
            dark = (60, 60, 60)
        else:
            skin = GOBLIN_SKIN
            dark = GOBLIN_GREEN
        
        bob = int(math.sin(animation_offset * 3) * 2)
        cy = y + bob
        
        # 身體
        pygame.draw.ellipse(surface, dark, (x - 18, cy - 5, 36, 30))
        
        # 頭
        head_y = cy - 25
        pygame.draw.circle(surface, skin, (x, head_y), 18)
        
        # 尖耳朵
        ear_l = [(x - 15, head_y - 5), (x - 28, head_y - 22), (x - 10, head_y - 12)]
        ear_r = [(x + 15, head_y - 5), (x + 28, head_y - 22), (x + 10, head_y - 12)]
        pygame.draw.polygon(surface, skin, ear_l)
        pygame.draw.polygon(surface, skin, ear_r)
        pygame.draw.polygon(surface, dark, ear_l, 2)
        pygame.draw.polygon(surface, dark, ear_r, 2)
        
        # 邪惡的眼睛
        pygame.draw.circle(surface, (255, 80, 80), (x - 7, head_y - 3), 5)
        pygame.draw.circle(surface, (255, 80, 80), (x + 7, head_y - 3), 5)
        pygame.draw.circle(surface, (20, 20, 20), (x - 6, head_y - 2), 2)
        pygame.draw.circle(surface, (20, 20, 20), (x + 8, head_y - 2), 2)
        
        # 獠牙
        pygame.draw.polygon(surface, (255, 255, 230),
                           [(x - 5, head_y + 10), (x - 3, head_y + 18), (x - 1, head_y + 10)])
        pygame.draw.polygon(surface, (255, 255, 230),
                           [(x + 5, head_y + 10), (x + 3, head_y + 18), (x + 1, head_y + 10)])
        
        # 武器
        pygame.draw.line(surface, (100, 70, 50), (x + 20, cy - 15), (x + 30, cy + 10), 4)
        pygame.draw.circle(surface, (80, 60, 40), (x + 30, cy + 10), 8)

    @staticmethod
    def draw_orc(surface: pygame.Surface, x: int, y: int, size: int = 60,
                 alive: bool = True, animation_offset: float = 0) -> None:
        """繪製獸人戰士"""
        if not alive:
            skin = (70, 70, 70)
            armor = (50, 50, 50)
        else:
            skin = ORC_GREEN
            armor = ORC_ARMOR
        
        sway = int(math.sin(animation_offset * 2) * 2)
        cy = y + sway
        
        # 身體（胸甲）
        pygame.draw.ellipse(surface, armor, (x - 25, cy - 15, 50, 40))
        # 盔甲紋路
        pygame.draw.line(surface, (60, 55, 50), (x, cy - 15), (x, cy + 20), 3)
        
        # 頭
        head_y = cy - 35
        pygame.draw.circle(surface, skin, (x, head_y), 22)
        
        # 頭盔
        pygame.draw.arc(surface, armor, (x - 22, head_y - 30, 44, 40), 
                       math.pi, 2 * math.pi, 5)
        
        # 眼睛（黃色）
        pygame.draw.circle(surface, (255, 200, 50), (x - 8, head_y - 3), 6)
        pygame.draw.circle(surface, (255, 200, 50), (x + 8, head_y - 3), 6)
        pygame.draw.circle(surface, (0, 0, 0), (x - 7, head_y - 2), 3)
        pygame.draw.circle(surface, (0, 0, 0), (x + 9, head_y - 2), 3)
        
        # 獠牙
        pygame.draw.polygon(surface, (255, 250, 240),
                           [(x - 12, head_y + 10), (x - 10, head_y + 22), (x - 8, head_y + 10)])
        pygame.draw.polygon(surface, (255, 250, 240),
                           [(x + 12, head_y + 10), (x + 10, head_y + 22), (x + 8, head_y + 10)])
        
        # 大斧頭
        axe_x = x + 30
        pygame.draw.line(surface, (80, 60, 40), (axe_x, cy - 25), (axe_x + 5, cy + 15), 5)
        pygame.draw.polygon(surface, (160, 160, 170),
                           [(axe_x, cy - 25), (axe_x + 25, cy - 15), (axe_x + 5, cy)])

    @staticmethod
    def draw_dark_mage(surface: pygame.Surface, x: int, y: int, size: int = 50,
                       alive: bool = True, animation_offset: float = 0) -> None:
        """繪製黑暗法師"""
        if not alive:
            robe = (40, 40, 40)
            magic = (60, 60, 60)
        else:
            robe = MAGE_ROBE
            magic = MAGE_PURPLE
        
        float_y = int(math.sin(animation_offset * 2.5) * 4)
        cy = y + float_y
        
        # 魔法光球環繞
        if alive:
            for i in range(4):
                angle = animation_offset * 2 + i * (math.pi / 2)
                orb_x = x + int(math.cos(angle) * 35)
                orb_y = cy + int(math.sin(angle) * 20)
                
                orb_surf = pygame.Surface((16, 16), pygame.SRCALPHA)
                pygame.draw.circle(orb_surf, (*magic, 150), (8, 8), 6)
                pygame.draw.circle(orb_surf, (255, 200, 255, 200), (8, 8), 3)
                surface.blit(orb_surf, (orb_x - 8, orb_y - 8))
        
        # 袍子
        robe_points = [(x, cy - 30), (x - 25, cy + 25), (x + 25, cy + 25)]
        pygame.draw.polygon(surface, robe, robe_points)
        
        # 兜帽陰影
        pygame.draw.circle(surface, robe, (x, cy - 20), 18)
        
        # 發光眼睛
        pygame.draw.circle(surface, magic, (x - 6, cy - 22), 5)
        pygame.draw.circle(surface, magic, (x + 6, cy - 22), 5)
        pygame.draw.circle(surface, (255, 200, 255), (x - 6, cy - 22), 2)
        pygame.draw.circle(surface, (255, 200, 255), (x + 6, cy - 22), 2)
        
        # 法杖
        pygame.draw.line(surface, (60, 45, 30), (x + 20, cy - 10), (x + 25, cy + 25), 4)
        pygame.draw.circle(surface, magic, (x + 22, cy - 15), 10)
        pygame.draw.circle(surface, (255, 150, 255), (x + 22, cy - 15), 5)

    @staticmethod
    def draw_fire_dragon(surface: pygame.Surface, x: int, y: int, size: int = 100,
                         alive: bool = True, animation_offset: float = 0,
                         enraged: bool = False) -> None:
        """繪製帥氣噴火龍 - Mega Charizard X 風格（藍焰）"""
        if not alive:
            body = (60, 60, 60)
            belly = (80, 80, 80)
            flame = (100, 100, 100)
            dark = (40, 40, 40)
        else:
            body = DRAGON_BODY
            belly = DRAGON_BELLY
            flame = DRAGON_FLAME if not enraged else (255, 100, 50)
            dark = DRAGON_DARK
        
        breathe = int(math.sin(animation_offset * 2) * 3)
        cy = y + breathe
        
        # === 翅膀（大而有力）===
        wing_flap = math.sin(animation_offset * 3) * 12
        
        # 左翅
        left_wing = [
            (x - 25, cy - 20),
            (x - 80, cy - 60 - wing_flap),
            (x - 70, cy - 30 - wing_flap // 2),
            (x - 55, cy - 40 - wing_flap // 2),
            (x - 35, cy)
        ]
        pygame.draw.polygon(surface, body, left_wing)
        pygame.draw.polygon(surface, dark, left_wing, 2)
        
        # 右翅
        right_wing = [
            (x + 25, cy - 20),
            (x + 80, cy - 60 - wing_flap),
            (x + 70, cy - 30 - wing_flap // 2),
            (x + 55, cy - 40 - wing_flap // 2),
            (x + 35, cy)
        ]
        pygame.draw.polygon(surface, body, right_wing)
        pygame.draw.polygon(surface, dark, right_wing, 2)
        
        # === 尾巴 ===
        tail_points = [
            (x - 15, cy + 25),
            (x - 50, cy + 35),
            (x - 70, cy + 25),
            (x - 45, cy + 20)
        ]
        pygame.draw.polygon(surface, body, tail_points)
        
        # 尾巴火焰
        if alive:
            flame_points = [
                (x - 65, cy + 28),
                (x - 85, cy + 20),
                (x - 75, cy + 35),
                (x - 90, cy + 30),
                (x - 70, cy + 32)
            ]
            pygame.draw.polygon(surface, flame, flame_points)
            # 火焰核心
            pygame.draw.circle(surface, (200, 255, 255) if not enraged else (255, 255, 150), 
                             (x - 75, cy + 28), 5)
        
        # === 身體 ===
        pygame.draw.ellipse(surface, body, (x - 35, cy - 15, 70, 55))
        
        # 腹部
        pygame.draw.ellipse(surface, belly, (x - 20, cy - 5, 40, 40))
        # 腹部條紋
        for i in range(4):
            stripe_y = cy + i * 8
            pygame.draw.line(surface, (120, 150, 170), 
                           (x - 15, stripe_y), (x + 15, stripe_y), 2)
        
        # === 頭部 ===
        head_x = x + 5
        head_y = cy - 35
        pygame.draw.circle(surface, body, (head_x, head_y), 25)
        
        # 下顎
        pygame.draw.ellipse(surface, body, (head_x - 15, head_y + 5, 30, 20))
        
        # === 角（藍色火焰角）===
        horn_color = flame
        # 左角
        horn_l = [(head_x - 12, head_y - 15), 
                  (head_x - 25, head_y - 45),
                  (head_x - 5, head_y - 20)]
        pygame.draw.polygon(surface, horn_color, horn_l)
        # 右角
        horn_r = [(head_x + 12, head_y - 15), 
                  (head_x + 25, head_y - 45),
                  (head_x + 5, head_y - 20)]
        pygame.draw.polygon(surface, horn_color, horn_r)
        
        # 角的發光效果
        if alive:
            glow_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*flame, 100), (10, 10), 8)
            surface.blit(glow_surf, (head_x - 25, head_y - 45))
            surface.blit(glow_surf, (head_x + 15, head_y - 45))
        
        # === 眼睛（發光紅眼）===
        eye_color = (255, 50, 50) if enraged else (255, 150, 50)
        pygame.draw.circle(surface, eye_color, (head_x - 10, head_y - 5), 7)
        pygame.draw.circle(surface, eye_color, (head_x + 10, head_y - 5), 7)
        # 瞳孔
        pygame.draw.circle(surface, (20, 20, 20), (head_x - 8, head_y - 5), 3)
        pygame.draw.circle(surface, (20, 20, 20), (head_x + 12, head_y - 5), 3)
        # 眼睛高光
        pygame.draw.circle(surface, (255, 255, 255), (head_x - 12, head_y - 7), 2)
        pygame.draw.circle(surface, (255, 255, 255), (head_x + 8, head_y - 7), 2)
        
        # === 嘴巴 ===
        mouth_points = [(head_x + 15, head_y + 5),
                       (head_x + 30, head_y + 15),
                       (head_x + 15, head_y + 18)]
        pygame.draw.polygon(surface, dark, mouth_points)
        
        # 牙齒
        pygame.draw.polygon(surface, (255, 255, 255),
                           [(head_x + 18, head_y + 8), (head_x + 20, head_y + 14), (head_x + 22, head_y + 8)])
        pygame.draw.polygon(surface, (255, 255, 255),
                           [(head_x + 24, head_y + 10), (head_x + 26, head_y + 15), (head_x + 28, head_y + 10)])
        
        # === 嘴角火焰（持續吐息）===
        if alive:
            flame_intensity = abs(math.sin(animation_offset * 4))
            for i in range(3):
                fx = head_x + 28 + i * 8
                fy = head_y + 12 + int(math.sin(animation_offset * 6 + i) * 3)
                fsize = int(6 + flame_intensity * 4 - i * 2)
                
                flame_surf = pygame.Surface((fsize * 2, fsize * 2), pygame.SRCALPHA)
                pygame.draw.circle(flame_surf, (*flame, 200 - i * 50), (fsize, fsize), fsize)
                surface.blit(flame_surf, (fx - fsize, fy - fsize))
        
        # === 狂暴模式特效 ===
        if alive and enraged:
            # 全身火焰環繞
            for i in range(6):
                angle = animation_offset * 4 + i * (math.pi / 3)
                fx = x + int(math.cos(angle) * 55)
                fy = cy + int(math.sin(angle) * 35)
                
                enrage_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.circle(enrage_surf, (255, 100, 50, 150), (10, 10), 8)
                pygame.draw.circle(enrage_surf, (255, 200, 100, 200), (10, 10), 4)
                surface.blit(enrage_surf, (fx - 10, fy - 10))
            
            # 眼睛強化發光
            eye_glow = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(eye_glow, (255, 50, 50, 100), (15, 15), 12)
            surface.blit(eye_glow, (head_x - 22, head_y - 17))
            surface.blit(eye_glow, (head_x - 2, head_y - 17))


def get_sprite_drawer(character_name: str):
    """根據角色名稱返回對應的繪製函數"""
    sprite_map = {
        "Kiwi": SpriteRenderer.draw_kiwi,
        "Healer Bird": SpriteRenderer.draw_healer,
        "Green Slime": SpriteRenderer.draw_slime,
        "Goblin": SpriteRenderer.draw_goblin,
        "Orc Warrior": SpriteRenderer.draw_orc,
        "Dark Mage": SpriteRenderer.draw_dark_mage,
        "FireDragon": SpriteRenderer.draw_fire_dragon,
    }
    return sprite_map.get(character_name, SpriteRenderer.draw_slime)
