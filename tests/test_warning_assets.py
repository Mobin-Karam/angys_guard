from pathlib import Path
from PIL import Image


def test_warning_assets_are_16_9():
    root = Path(__file__).resolve().parents[1] / 'laptop_guard' / 'assets' / 'warnings'
    for n in range(1, 6):
        path = root / f'{n}.png'
        assert path.exists()
        with Image.open(path) as im:
            assert im.size == (1280, 720)
