#!/usr/bin/env python3
"""Positive: Godot URI schemes and URLs are NOT host absolute paths.
The scanner MUST report no hits for this file.
"""
from pathlib import Path

scene = "res://Scenes/Menu.tscn"
save = "user://_0_6_0.dat"
link = "https://discord.gg/TzF3aRWnhZ"
http = "http://example.com/page"
rel = Path("00_original/Mutagenic.exe")