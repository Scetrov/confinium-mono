"""Pinned Grid inputs for studies that predate future edits to the live Grid."""
from pathlib import Path

GRID_REFERENCE = Path(__file__).resolve().parents[1] / 'studies/grid-token-bold/reference'
GRID_UFO = GRID_REFERENCE / 'ConfiniumMono-GridToken-Grid.ufo'
GRID_TTF = GRID_REFERENCE / 'ConfiniumMono-GridToken-Grid.ttf'
