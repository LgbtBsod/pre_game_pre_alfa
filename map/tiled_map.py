import json
import os
from typing import Dict, List, Tuple

class TiledMap:
    def __init__(self, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.width: int = int(data.get("width", 0))
        self.height: int = int(data.get("height", 0))
        self.tilewidth: int = int(data.get("tilewidth", 32))
        self.tileheight: int = int(data.get("tileheight", 32))
        self.infinite: bool = bool(data.get("infinite", False))
        self.layers: List[Dict] = [
            layer for layer in data.get("layers", []) if layer.get("type") == "tilelayer"
        ]

        # bounds for infinite maps
        self.min_tx = 0
        self.min_ty = 0
        self.max_tx = self.width
        self.max_ty = self.height
        self._compute_bounds()

    def _compute_bounds(self) -> None:
        if not self.infinite:
            self.min_tx, self.min_ty = 0, 0
            self.max_tx = self.width
            self.max_ty = self.height
            return
        min_tx = None
        min_ty = None
        max_tx = None
        max_ty = None
        for layer in self.layers:
            for chunk in layer.get("chunks", []):
                cx, cy = int(chunk["x"]), int(chunk["y"])
                cw, ch = int(chunk["width"]), int(chunk["height"])
                min_tx = cx if min_tx is None else min(min_tx, cx)
                min_ty = cy if min_ty is None else min(min_ty, cy)
                max_tx = cx + cw if max_tx is None else max(max_tx, cx + cw)
                max_ty = cy + ch if max_ty is None else max(max_ty, cy + ch)
        if min_tx is None:
            min_tx = min_ty = 0
            max_tx = max_ty = 0
        self.min_tx, self.min_ty, self.max_tx, self.max_ty = min_tx, min_ty, max_tx, max_ty

    def get_tile_gid(self, x: int, y: int) -> int:
        for layer in reversed(self.layers):
            gid = self._gid_from_layer(layer, x, y)
            if gid:
                return gid
        return 0

    def _gid_from_layer(self, layer: Dict, x: int, y: int) -> int:
        if self.infinite and "chunks" in layer:
            for chunk in layer["chunks"]:
                cx, cy = int(chunk["x"]), int(chunk["y"])
                cw, ch = int(chunk["width"]), int(chunk["height"])
                if cx <= x < cx + cw and cy <= y < cy + ch:
                    idx = (y - cy) * cw + (x - cx)
                    data = chunk.get("data", [])
                    return int(data[idx]) if 0 <= idx < len(data) else 0
            return 0
        else:
            w = int(layer.get("width", self.width))
            h = int(layer.get("height", self.height))
            if not (0 <= x < w and 0 <= y < h):
                return 0
            data = layer.get("data", [])
            idx = y * w + x
            return int(data[idx]) if 0 <= idx < len(data) else 0

    def draw_to_canvas(self, canvas, view_left_px: int, view_top_px: int, view_w: int, view_h: int, tag: str = "map") -> None:
        tw, th = self.tilewidth, self.tileheight
        cols = max(0, self.max_tx - self.min_tx)
        rows = max(0, self.max_ty - self.min_ty)
        first_lx = max(0, view_left_px // tw)
        first_ly = max(0, view_top_px // th)
        last_lx = min(cols, (view_left_px + view_w) // tw + 1)
        last_ly = min(rows, (view_top_px + view_h) // th + 1)
        for lty in range(first_ly, last_ly):
            for ltx in range(first_lx, last_lx):
                tx = self.min_tx + ltx
                ty = self.min_ty + lty
                gid = self.get_tile_gid(tx, ty)
                if gid == 0:
                    continue
                r = (gid * 37) % 255
                g = (gid * 57) % 255
                b = (gid * 97) % 255
                color = f"#{r:02x}{g:02x}{b:02x}"
                x0 = ltx * tw - view_left_px
                y0 = lty * th - view_top_px
                x1 = x0 + tw
                y1 = y0 + th
                canvas.create_rectangle(x0, y0, x1, y1, fill=color, width=0, tags=(tag,))


