"""Otavite Orbit — cadmium sling-gate arcade for ElbowOS. Python 3 + pygame.

Spin the boom, fire a shard through rotating ring gaps.
Space / click fires. Left / Right nudge spin. R restarts.
  python3 otavite_orbit.py --play
  python3 otavite_orbit.py --record
"""
import math
import os
import random
import subprocess
import sys

RECORD = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
PLAY = "--play" in sys.argv
if RECORD or not PLAY:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", "OTAVITE_ORBIT_ElbowOS.mp4")
TITLE, HANDLE = "OTAVITE ORBIT", "x.com/ElbowOS"
CX, CY = 540, 980
TAU = math.tau

PLUM = (18, 6, 28)
INK = (8, 2, 16)
ROSE = (255, 92, 138)
CAD = (255, 166, 186)
TEAL = (64, 255, 214)
AMBER = (255, 186, 64)
LIME = (196, 255, 72)
WHITE = (255, 244, 248)
VIOLET = (168, 92, 255)


def wrap(a):
    return (a + math.pi) % TAU - math.pi


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        flags = 0 if PLAY else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            self.screen = pygame.Surface((W, H))
        pygame.display.set_caption(TITLE)
        self.font = pygame.font.SysFont("dejavusans", 78, bold=True)
        self.mid = pygame.font.SysFont("dejavusans", 42, bold=True)
        self.small = pygame.font.SysFont("dejavusans", 32, bold=True)
        self.reset()

    def reset(self):
        self.arm = -1.2
        self.spin = 0.04
        self.rings = [
            {"r": 330, "gap": 0.6, "w": 0.55, "spd": 0.011, "col": TEAL},
            {"r": 490, "gap": 0.85, "w": 0.48, "spd": -0.007, "col": LIME},
            {"r": 650, "gap": 1.05, "w": 0.42, "spd": 0.005, "col": VIOLET},
        ]
        self.shards = []
        self.sparks = []
        self.motes = [
            [random.uniform(0, TAU), random.uniform(180, 860), random.uniform(0.004, 0.012), random.choice([ROSE, AMBER, TEAL])]
            for _ in range(28)
        ]
        self.score = 0
        self.combo = 1
        self.best = 1
        self.cd = 8
        self.tick = 0
        self.banner = "ALIGN + FIRE"
        self.flash = 0

    def launch(self):
        tip = 198
        ang = self.arm
        sp = 13.5
        self.shards.append({
            "x": CX + math.cos(ang) * tip,
            "y": CY + math.sin(ang) * tip,
            "vx": math.cos(ang) * sp,
            "vy": math.sin(ang) * sp,
            "hit": 0,
            "life": 90,
        })
        self.cd = 14
        for _ in range(8):
            self.sparks.append([CX + math.cos(ang) * tip, CY + math.sin(ang) * tip, random.uniform(-3, 3), random.uniform(-3, 3), AMBER, 12])

    def step(self, fire=False, nudge=0):
        self.tick += 1
        self.spin = max(-0.09, min(0.09, self.spin + nudge))
        self.arm += self.spin
        self.cd = max(0, self.cd - 1)
        self.flash = max(0, self.flash - 1)
        for ring in self.rings:
            ring["gap"] = (ring["gap"] + ring["spd"]) % TAU
        for mote in self.motes:
            mote[0] += mote[2]
        if fire and self.cd == 0 and len(self.shards) < 5:
            self.launch()
        alive = []
        for sh in self.shards:
            px, py = sh["x"], sh["y"]
            sh["x"] += sh["vx"]
            sh["y"] += sh["vy"]
            sh["life"] -= 1
            pr = math.hypot(px - CX, py - CY)
            rr = math.hypot(sh["x"] - CX, sh["y"] - CY)
            ang = math.atan2(sh["y"] - CY, sh["x"] - CX)
            dead = sh["life"] <= 0 or rr > 900
            for i, ring in enumerate(self.rings):
                if sh["hit"] == i and pr < ring["r"] <= rr:
                    if abs(wrap(ang - ring["gap"])) < ring["w"]:
                        sh["hit"] = i + 1
                        self.score += 40 * self.combo
                        self.combo = min(9, self.combo + 1)
                        self.best = max(self.best, self.combo)
                        self.flash = 8
                        self.banner = f"GATE {i + 1}"
                        for _ in range(10):
                            self.sparks.append([sh["x"], sh["y"], random.uniform(-4, 4), random.uniform(-4, 4), ring["col"], 16])
                    else:
                        dead = True
                        self.combo = 1
                        self.banner = "CLIPPED"
                        for _ in range(14):
                            self.sparks.append([sh["x"], sh["y"], random.uniform(-5, 5), random.uniform(-5, 5), ROSE, 18])
            if sh["hit"] == 3:
                self.score += 120 * self.combo
                self.banner = "ORBIT CLEAR"
                self.flash = 12
                dead = True
            if not dead:
                alive.append(sh)
        self.shards = alive
        self.sparks = [[s[0] + s[2], s[1] + s[3], s[2] * 0.96, s[3] * 0.96, s[4], s[5] - 1] for s in self.sparks if s[5] > 1]

    def auto(self):
        travel = (self.rings[0]["r"] - 198) / 13.5
        predict = self.rings[0]["gap"] + self.rings[0]["spd"] * travel
        diff = wrap(predict - self.arm)
        self.spin = max(-0.085, min(0.085, diff * 0.42))
        return abs(diff) < 0.06 and self.cd == 0

    def draw(self, surf):
        surf.fill(INK)
        for y in range(0, H, 8):
            t = y / H
            col = (int(28 + 20 * (1 - t)), int(6 + 18 * t), int(36 + 30 * (1 - t)))
            pygame.draw.rect(surf, col, (0, y, W, 8))
        for i in range(12):
            a = self.tick * 0.004 + i * TAU / 12
            pygame.draw.line(surf, (42, 16, 52), (CX, CY), (CX + math.cos(a) * 820, CY + math.sin(a) * 820), 2)
        for ang, rad, spd, col in self.motes:
            x = CX + math.cos(ang) * rad
            y = CY + math.sin(ang) * rad * 0.92
            pygame.draw.circle(surf, col, (int(x), int(y)), 4)
        for ring in self.rings:
            self._ring(surf, ring)
        pulse = 46 + int(8 * math.sin(self.tick * 0.18))
        pygame.draw.circle(surf, (90, 28, 48), (CX, CY), pulse + 18)
        pygame.draw.circle(surf, AMBER, (CX, CY), pulse)
        pygame.draw.circle(surf, WHITE, (CX, CY), 16)
        tipx = CX + math.cos(self.arm) * 198
        tipy = CY + math.sin(self.arm) * 198
        pygame.draw.line(surf, ROSE, (CX, CY), (tipx, tipy), 16)
        pygame.draw.line(surf, CAD, (CX, CY), (tipx, tipy), 6)
        pygame.draw.circle(surf, WHITE, (int(tipx), int(tipy)), 18)
        pygame.draw.circle(surf, ROSE, (int(tipx), int(tipy)), 10)
        for sh in self.shards:
            pygame.draw.circle(surf, CAD, (int(sh["x"]), int(sh["y"])), 12)
            pygame.draw.circle(surf, WHITE, (int(sh["x"]), int(sh["y"])), 5)
        for s in self.sparks:
            pygame.draw.circle(surf, s[4], (int(s[0]), int(s[1])), max(2, s[5] // 4))
        bar = pygame.Surface((W, 210), pygame.SRCALPHA)
        bar.fill((10, 2, 16, 170))
        surf.blit(bar, (0, 0))
        foot = pygame.Surface((W, 140), pygame.SRCALPHA)
        foot.fill((10, 2, 16, 170))
        surf.blit(foot, (0, H - 140))
        title = self.font.render(TITLE, True, CAD)
        surf.blit(title, title.get_rect(center=(W // 2, 78)))
        sub = self.small.render("CADMIUM SLING", True, TEAL)
        surf.blit(sub, sub.get_rect(center=(W // 2, 142)))
        score = self.mid.render(f"SCORE  {self.score}", True, WHITE)
        surf.blit(score, score.get_rect(center=(W // 2, 198)))
        combo = self.mid.render(self.banner if self.flash else f"COMBO x{self.combo}", True, AMBER if self.flash else LIME)
        surf.blit(combo, combo.get_rect(center=(W // 2, H - 96)))
        handle = self.small.render(HANDLE, True, ROSE)
        surf.blit(handle, handle.get_rect(center=(W // 2, H - 48)))

    def _ring(self, surf, ring):
        r, gap, width, col = ring["r"], ring["gap"], ring["w"], ring["col"]
        pts = []
        steps = 110
        for i in range(steps + 1):
            a = i / steps * TAU
            if abs(wrap(a - gap)) < width:
                if len(pts) > 1:
                    pygame.draw.lines(surf, col, False, pts, 14)
                pts = []
            else:
                pts.append((CX + math.cos(a) * r, CY + math.sin(a) * r))
        if len(pts) > 1:
            pygame.draw.lines(surf, col, False, pts, 14)
        gx = CX + math.cos(gap) * r
        gy = CY + math.sin(gap) * r
        pygame.draw.circle(surf, WHITE, (int(gx), int(gy)), 10)

    def record(self):
        os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-an",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
            "-movflags", "+faststart", OUT,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        frames = FPS * SECS
        try:
            for n in range(frames):
                self.step(fire=self.auto())
                self.draw(self.screen)
                proc.stdin.write(pygame.image.tobytes(self.screen, "RGB"))
                if n % 60 == 0:
                    print(f"frame {n}/{frames} score {self.score}", flush=True)
        finally:
            proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "ignore")
        rc = proc.wait()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed ({rc}):\n{err[-1500:]}")
        print("wrote", OUT, "score", self.score)
        pygame.quit()

    def play(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            nudge = 0
            fire = False
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                elif ev.type == pygame.KEYDOWN:
                    if ev.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                        fire = True
                    elif ev.key == pygame.K_r:
                        self.reset()
                    elif ev.key == pygame.K_ESCAPE:
                        running = False
                elif ev.type == pygame.MOUSEBUTTONDOWN:
                    fire = True
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                nudge -= 0.004
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                nudge += 0.004
            self.step(fire=fire, nudge=nudge)
            self.draw(self.screen)
            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()


def main():
    random.seed(11)
    game = Game()
    if PLAY and not RECORD:
        game.play()
    else:
        game.record()


if __name__ == "__main__":
    main()
