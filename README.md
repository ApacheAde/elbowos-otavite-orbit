# Otavite Orbit

Full-colour Python 3 cadmium sling-gate arcade for ElbowOS.

A rose boom orbits an amber core. Fire a shard through three rotating ring gaps (teal, lime, violet). Thread a gate to build combo. Clip a ring and the streak breaks. Clear all three for an orbit bonus.

Not a Nintendo ROM, not an emulator, and not a copy of the older Ammolite Orbit reel.

Featured account: https://x.com/ElbowOS

Drive reel (9:16, 15s): https://drive.google.com/file/d/1wPm-fElqd3UNmNQXCaLmMtYiZNXhmHGY/view

## Play

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 otavite_orbit.py --play
```

Space or click fires. Left / Right (or A / D) nudge the spin. R restarts.

## Record a 9:16 reel

```bash
python3 otavite_orbit.py --record
```

Writes `OTAVITE_ORBIT_ElbowOS.mp4` (1080x1920, 15s, 30fps, libx264 yuv420p). Set `ELBOWOS_MP4` to choose the path. Headless runs use `SDL_VIDEODRIVER=dummy`.
