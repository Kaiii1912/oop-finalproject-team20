# effects.py
"""
視覺特效系統 - 攻擊動畫、技能特效、傷害數字等
"""
from __future__ import annotations
import pygame
import math
import random
from typing import List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class Effect:
    """特效基底類別"""
    x: int
    y: int
    duration: float = 0.5
    elapsed: float = 0.0
    
    def update(self, dt: float) -> bool:
        """更新特效，返回 False 表示特效結束"""
        self.elapsed += dt
        return self.elapsed < self.duration
    
    def draw(self, surface: pygame.Surface) -> None:
        """繪製特效"""
        pass


@dataclass
class SlashEffect(Effect):
    """斬擊特效 - 炫酷刀光 + 火花 + 殘影"""
    target_x: int = 0
    target_y: int = 0
    color: Tuple[int, int, int] = (255, 220, 100)
    sparks: List[dict] = field(default_factory=list)
    
    def __post_init__(self):
        # 創建火花粒子
        self.sparks = []
        for i in range(15):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            self.sparks.append({
                'x': self.target_x,
                'y': self.target_y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': random.randint(2, 5),
                'color': random.choice([(255, 255, 100), (255, 200, 50), (255, 150, 50)])
            })
    
    def draw(self, surface: pygame.Surface) -> None:
        progress = self.elapsed / self.duration
        if progress > 1:
            return
        
        # === 殘影刀痕 ===
        for trail in range(3):
            trail_progress = max(0, progress - trail * 0.08)
            if trail_progress <= 0:
                continue
            
            angle_start = -math.pi / 3 + trail_progress * math.pi * 0.8
            angle_end = angle_start + math.pi / 2
            
            trail_alpha = int(180 * (1 - trail_progress) / (trail + 1))
            trail_size = 100 - trail * 15
            
            slash_surf = pygame.Surface((trail_size + 40, trail_size + 40), pygame.SRCALPHA)
            
            # 發光核心
            for i in range(5):
                offset = i * 4
                glow_color = (*self.color, max(0, trail_alpha - i * 30))
                pygame.draw.arc(slash_surf, glow_color,
                               (20 + offset, 20 + offset, trail_size - offset*2, trail_size - offset*2),
                               angle_start, angle_end, 6 - i)
            
            surface.blit(slash_surf, (self.target_x - trail_size // 2 - 20, 
                                       self.target_y - trail_size // 2 - 20))
        
        # === 衝擊閃光 ===
        if progress < 0.3:
            flash_alpha = int(200 * (1 - progress / 0.3))
            flash_size = int(60 * progress / 0.3)
            flash_surf = pygame.Surface((flash_size * 2, flash_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(flash_surf, (255, 255, 200, flash_alpha), 
                             (flash_size, flash_size), flash_size)
            surface.blit(flash_surf, (self.target_x - flash_size, self.target_y - flash_size))
        
        # === 飛濺火花 ===
        for spark in self.sparks:
            spark_x = spark['x'] + spark['vx'] * progress * 0.5
            spark_y = spark['y'] + spark['vy'] * progress * 0.5 + 50 * progress * progress
            spark_alpha = int(255 * (1 - progress))
            spark_size = max(1, int(spark['size'] * (1 - progress * 0.5)))
            
            spark_surf = pygame.Surface((spark_size * 2, spark_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(spark_surf, (*spark['color'], spark_alpha), 
                             (spark_size, spark_size), spark_size)
            surface.blit(spark_surf, (int(spark_x) - spark_size, int(spark_y) - spark_size))


@dataclass
class WhirlwindEffect(Effect):
    """旋風特效 - 超炫酷螺旋刀圈 + 能量波 + 落葉飛舞"""
    radius: int = 100
    particles: List[dict] = field(default_factory=list)
    blades: List[dict] = field(default_factory=list)
    
    def __post_init__(self):
        # 風粒子
        self.particles = []
        for i in range(35):
            angle = random.random() * 2 * math.pi
            dist = random.random() * self.radius * 0.8
            self.particles.append({
                'angle': angle,
                'dist': dist,
                'size': random.randint(3, 8),
                'color': random.choice([
                    (100, 220, 255), (150, 255, 200), (200, 255, 150), (255, 255, 100)
                ]),
                'speed': random.uniform(0.8, 1.5)
            })
        
        # 刀刃光環
        self.blades = []
        for i in range(6):
            self.blades.append({
                'angle': i * (math.pi / 3),
                'length': random.randint(30, 50)
            })
    
    def draw(self, surface: pygame.Surface) -> None:
        progress = self.elapsed / self.duration
        if progress > 1:
            return
        
        rotation = self.elapsed * 12  # 旋轉速度
        expansion = 0.3 + progress * 0.7  # 擴張效果
        alpha = int(220 * (1 - progress * 0.7))
        
        # === 中心漩渦 ===
        vortex_size = int(self.radius * 0.4 * (1 + progress * 0.5))
        vortex_surf = pygame.Surface((vortex_size * 2, vortex_size * 2), pygame.SRCALPHA)
        for i in range(5):
            ring_size = vortex_size - i * 8
            if ring_size > 0:
                ring_color = (100, 200, 255, max(0, alpha - i * 40))
                pygame.draw.circle(vortex_surf, ring_color, (vortex_size, vortex_size), ring_size, 3)
        surface.blit(vortex_surf, (self.x - vortex_size, self.y - vortex_size))
        
        # === 旋轉刀刃 ===
        for blade in self.blades:
            blade_angle = blade['angle'] + rotation
            blade_len = int(blade['length'] * expansion)
            
            start_dist = self.radius * 0.3
            end_dist = self.radius * expansion
            
            sx = self.x + int(math.cos(blade_angle) * start_dist)
            sy = self.y + int(math.sin(blade_angle) * start_dist * 0.5)
            ex = self.x + int(math.cos(blade_angle) * end_dist)
            ey = self.y + int(math.sin(blade_angle) * end_dist * 0.5)
            
            # 刀刃光線
            blade_color = (200, 255, 220, alpha)
            pygame.draw.line(surface, blade_color[:3], (sx, sy), (ex, ey), 4)
            
            # 刀刃尖端發光
            glow_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 255, 200, alpha), (10, 10), 8)
            surface.blit(glow_surf, (ex - 10, ey - 10))
        
        # === 風粒子 ===
        for p in self.particles:
            current_angle = p['angle'] + rotation * p['speed']
            current_dist = p['dist'] * expansion
            
            px = self.x + int(math.cos(current_angle) * current_dist)
            py = self.y + int(math.sin(current_angle) * current_dist * 0.5)
            
            particle_alpha = int(alpha * 0.8)
            wind_surf = pygame.Surface((p['size'] * 2, p['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(wind_surf, (*p['color'], particle_alpha), (p['size'], p['size']), p['size'])
            surface.blit(wind_surf, (px - p['size'], py - p['size']))
        
        # === 擴張衝擊波 ===
        if progress < 0.5:
            wave_progress = progress / 0.5
            wave_radius = int(self.radius * wave_progress * 1.2)
            wave_alpha = int(150 * (1 - wave_progress))
            
            wave_surf = pygame.Surface((wave_radius * 2 + 10, wave_radius + 10), pygame.SRCALPHA)
            pygame.draw.ellipse(wave_surf, (200, 255, 255, wave_alpha), 
                              (5, 5, wave_radius * 2, wave_radius), 3)
            surface.blit(wave_surf, (self.x - wave_radius - 5, self.y - wave_radius // 2 - 5))


@dataclass 
class HealEffect(Effect):
    """治療特效 - 上升的綠色光點"""
    particles: List[Tuple[int, int, int, float]] = field(default_factory=list)
    
    def __post_init__(self):
        self.particles = []
        for i in range(15):
            px = self.x + random.randint(-30, 30)
            py = self.y + random.randint(-10, 30)
            size = random.randint(3, 7)
            speed = random.uniform(30, 60)
            self.particles.append((px, py, size, speed))
    
    def draw(self, surface: pygame.Surface) -> None:
        progress = self.elapsed / self.duration
        if progress > 1:
            return
        
        alpha = int(255 * (1 - progress * 0.5))
        
        for base_x, base_y, size, speed in self.particles:
            py = base_y - self.elapsed * speed
            
            # 綠色光點
            colors = [(50, 255, 100), (100, 255, 150), (150, 255, 200)]
            color = random.choice(colors)
            
            heal_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(heal_surf, (*color, alpha), (size, size), size)
            surface.blit(heal_surf, (base_x - size, int(py) - size))
        
        # 十字光
        cross_alpha = int(180 * (1 - progress))
        cross_size = int(20 * (1 + progress * 0.5))
        cross_surf = pygame.Surface((cross_size * 2, cross_size * 2), pygame.SRCALPHA)
        pygame.draw.rect(cross_surf, (100, 255, 100, cross_alpha),
                        (cross_size - 3, 0, 6, cross_size * 2))
        pygame.draw.rect(cross_surf, (100, 255, 100, cross_alpha),
                        (0, cross_size - 3, cross_size * 2, 6))
        surface.blit(cross_surf, (self.x - cross_size, self.y - cross_size - int(progress * 30)))


@dataclass
class FireBreathEffect(Effect):
    """噴火特效 - 橙紅火焰粒子"""
    target_positions: List[Tuple[int, int]] = field(default_factory=list)
    particles: List[dict] = field(default_factory=list)
    duration: float = 0.8
    
    def __post_init__(self):
        self.particles = []
        # 為每個目標創建火焰粒子
        for tx, ty in self.target_positions:
            for i in range(25):
                dx = tx - self.x
                dy = ty - self.y
                dist = math.sqrt(dx*dx + dy*dy)
                
                self.particles.append({
                    'sx': self.x,
                    'sy': self.y,
                    'tx': tx + random.randint(-20, 20),
                    'ty': ty + random.randint(-15, 15),
                    'size': random.randint(5, 15),
                    'delay': random.uniform(0, 0.2),
                    'speed': random.uniform(0.8, 1.2)
                })
    
    def draw(self, surface: pygame.Surface) -> None:
        for p in self.particles:
            t = max(0, self.elapsed - p['delay']) * p['speed']
            progress = min(1.0, t / (self.duration * 0.7))
            
            if progress <= 0:
                continue
            
            # 插值位置
            px = p['sx'] + (p['tx'] - p['sx']) * progress
            py = p['sy'] + (p['ty'] - p['sy']) * progress
            
            # 火焰顏色漸變
            if progress < 0.3:
                color = (255, 255, 100)  # 黃色
            elif progress < 0.6:
                color = (255, 150, 50)   # 橙色
            else:
                color = (255, 50, 20)    # 紅色
            
            alpha = int(255 * (1 - progress * 0.8))
            size = int(p['size'] * (1 - progress * 0.5))
            
            if size > 0:
                fire_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(fire_surf, (*color, alpha), (size, size), size)
                surface.blit(fire_surf, (int(px) - size, int(py) - size))


@dataclass
class DamageNumber(Effect):
    """傷害數字 - 浮動消失"""
    damage: int = 0
    is_heal: bool = False
    font: pygame.font.Font = None
    duration: float = 1.0
    
    def draw(self, surface: pygame.Surface) -> None:
        progress = self.elapsed / self.duration
        if progress > 1:
            return
        
        if self.font is None:
            self.font = pygame.font.SysFont("arial", 24, bold=True)
        
        # 上浮 + 淡出
        float_y = self.y - int(progress * 40)
        alpha = int(255 * (1 - progress))
        
        # 顏色
        if self.is_heal:
            color = (100, 255, 100)
            text = f"+{self.damage}"
        else:
            color = (255, 80, 80)
            text = f"-{self.damage}"
        
        text_surf = self.font.render(text, True, color)
        text_surf.set_alpha(alpha)
        
        rect = text_surf.get_rect(center=(self.x, float_y))
        surface.blit(text_surf, rect)


@dataclass
class DarkBoltEffect(Effect):
    """黑暗法術特效"""
    target_x: int = 0
    target_y: int = 0
    
    def draw(self, surface: pygame.Surface) -> None:
        progress = self.elapsed / self.duration
        if progress > 1:
            return
        
        # 紫色能量球飛向目標
        current_x = self.x + (self.target_x - self.x) * min(1.0, progress * 1.5)
        current_y = self.y + (self.target_y - self.y) * min(1.0, progress * 1.5)
        
        # 拖尾效果
        for i in range(5):
            trail_progress = max(0, progress - i * 0.05)
            if trail_progress > 0:
                tx = self.x + (self.target_x - self.x) * min(1.0, trail_progress * 1.5)
                ty = self.y + (self.target_y - self.y) * min(1.0, trail_progress * 1.5)
                
                size = 12 - i * 2
                alpha = 200 - i * 40
                
                bolt_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(bolt_surf, (138, 43, 226, alpha), (size, size), size)
                surface.blit(bolt_surf, (int(tx) - size, int(ty) - size))
        
        # 撞擊時的爆發
        if progress > 0.6:
            burst_progress = (progress - 0.6) / 0.4
            burst_size = int(30 * burst_progress)
            burst_alpha = int(200 * (1 - burst_progress))
            
            burst_surf = pygame.Surface((burst_size * 2, burst_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(burst_surf, (180, 100, 255, burst_alpha), 
                             (burst_size, burst_size), burst_size)
            surface.blit(burst_surf, (self.target_x - burst_size, self.target_y - burst_size))


@dataclass
class HitFlash(Effect):
    """受擊閃爍效果"""
    duration: float = 0.15
    
    def draw(self, surface: pygame.Surface) -> None:
        progress = self.elapsed / self.duration
        if progress > 1:
            return
        
        alpha = int(180 * (1 - progress))
        size = 40
        
        flash_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(flash_surf, (255, 255, 255, alpha), (size, size), size)
        surface.blit(flash_surf, (self.x - size, self.y - size))


class ScreenShake:
    """螢幕抖動效果"""
    
    def __init__(self):
        self.intensity: float = 0
        self.duration: float = 0
        self.elapsed: float = 0
    
    def trigger(self, intensity: float = 10, duration: float = 0.3):
        self.intensity = intensity
        self.duration = duration
        self.elapsed = 0
    
    def update(self, dt: float) -> Tuple[int, int]:
        """更新並返回偏移量"""
        if self.elapsed >= self.duration:
            return (0, 0)
        
        self.elapsed += dt
        progress = self.elapsed / self.duration
        
        # 衰減的隨機抖動
        current_intensity = self.intensity * (1 - progress)
        offset_x = int(random.uniform(-current_intensity, current_intensity))
        offset_y = int(random.uniform(-current_intensity, current_intensity))
        
        return (offset_x, offset_y)


class ParticleSystem:
    """環境粒子系統 - 灰塵、火花等"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.particles: List[dict] = []
    
    def spawn_dust(self, count: int = 20):
        """產生灰塵粒子"""
        for _ in range(count):
            self.particles.append({
                'type': 'dust',
                'x': random.randint(0, self.width),
                'y': random.randint(0, self.height),
                'vx': random.uniform(-0.5, 0.5),
                'vy': random.uniform(-0.3, 0.1),
                'size': random.randint(1, 3),
                'alpha': random.randint(50, 150),
                'life': random.uniform(3, 8)
            })
    
    def spawn_ember(self, count: int = 30):
        """產生火花粒子（用於火龍巢穴）"""
        for _ in range(count):
            self.particles.append({
                'type': 'ember',
                'x': random.randint(0, self.width),
                'y': self.height + 10,
                'vx': random.uniform(-1, 1),
                'vy': random.uniform(-2, -0.5),
                'size': random.randint(2, 5),
                'alpha': random.randint(150, 255),
                'life': random.uniform(2, 5)
            })
    
    def spawn_magic(self, count: int = 15):
        """產生魔法粒子（用於黑暗神殿）"""
        for _ in range(count):
            self.particles.append({
                'type': 'magic',
                'x': random.randint(0, self.width),
                'y': random.randint(0, self.height),
                'vx': random.uniform(-0.3, 0.3),
                'vy': random.uniform(-0.5, 0.5),
                'size': random.randint(2, 4),
                'alpha': random.randint(100, 200),
                'life': random.uniform(2, 4)
            })
    
    def update(self, dt: float):
        """更新所有粒子"""
        for p in self.particles[:]:
            p['x'] += p['vx'] * dt * 60
            p['y'] += p['vy'] * dt * 60
            p['life'] -= dt
            
            if p['life'] <= 0:
                self.particles.remove(p)
    
    def draw(self, surface: pygame.Surface):
        """繪製所有粒子"""
        for p in self.particles:
            if p['type'] == 'dust':
                color = (150, 140, 130, p['alpha'])
            elif p['type'] == 'ember':
                # 火花顏色隨機
                colors = [(255, 200, 50), (255, 150, 30), (255, 100, 20)]
                base = random.choice(colors)
                color = (*base, p['alpha'])
            else:  # magic
                color = (180, 100, 255, p['alpha'])
            
            particle_surf = pygame.Surface((p['size'] * 2, p['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, color, (p['size'], p['size']), p['size'])
            surface.blit(particle_surf, (int(p['x']) - p['size'], int(p['y']) - p['size']))


class EffectManager:
    """特效管理器"""
    
    def __init__(self):
        self.effects: List[Effect] = []
        self.screen_shake = ScreenShake()
    
    def add(self, effect: Effect):
        self.effects.append(effect)
    
    def add_slash(self, x: int, y: int, target_x: int, target_y: int):
        self.effects.append(SlashEffect(x=x, y=y, target_x=target_x, target_y=target_y))
    
    def add_whirlwind(self, x: int, y: int):
        self.effects.append(WhirlwindEffect(x=x, y=y, duration=0.7))
    
    def add_heal(self, x: int, y: int):
        self.effects.append(HealEffect(x=x, y=y, duration=0.8))
    
    def add_fire_breath(self, x: int, y: int, targets: List[Tuple[int, int]]):
        self.effects.append(FireBreathEffect(x=x, y=y, target_positions=targets, duration=0.8))
        self.screen_shake.trigger(15, 0.4)
    
    def add_damage(self, x: int, y: int, damage: int, is_heal: bool = False):
        self.effects.append(DamageNumber(x=x, y=y, damage=damage, is_heal=is_heal))
    
    def add_dark_bolt(self, x: int, y: int, target_x: int, target_y: int):
        self.effects.append(DarkBoltEffect(x=x, y=y, target_x=target_x, target_y=target_y))
    
    def add_hit_flash(self, x: int, y: int):
        self.effects.append(HitFlash(x=x, y=y))
    
    def shake(self, intensity: float = 10, duration: float = 0.3):
        self.screen_shake.trigger(intensity, duration)
    
    def update(self, dt: float) -> Tuple[int, int]:
        """更新所有特效，返回螢幕抖動偏移"""
        self.effects = [e for e in self.effects if e.update(dt)]
        return self.screen_shake.update(dt)
    
    def draw(self, surface: pygame.Surface):
        """繪製所有特效"""
        for effect in self.effects:
            effect.draw(surface)
