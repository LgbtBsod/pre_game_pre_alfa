#!/usr/bin/env python3
"""
HUD widget factory for Panda3D OnscreenText elements.
"""

from typing import Optional, Dict, Any
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode
import os


class HUD:
    def __init__(self, parent_node):
        self.parent = parent_node
        self.font = self._load_font()
        self.game_title_text: Optional[OnscreenText] = None
        self.health_bar_text: Optional[OnscreenText] = None
        self.mana_bar_text: Optional[OnscreenText] = None
        self.ai_info_text: Optional[OnscreenText] = None
        self.skills_info_text: Optional[OnscreenText] = None
        self.items_info_text: Optional[OnscreenText] = None
        self.effects_info_text: Optional[OnscreenText] = None
        self.genome_info_text: Optional[OnscreenText] = None
        self.emotion_bar_text: Optional[OnscreenText] = None

    def build(self) -> 'HUD':
        self.game_title_text = OnscreenText(
            text="GAME SESSION",
            pos=(0, 0.9),
            scale=0.06,
            fg=(0.0, 1.0, 1.0, 1.0),
            align=TextNode.ACenter,
            mayChange=False,
            parent=self.parent,
            shadow=(0, 0, 0, 0.8),
            shadowOffset=(0.01, 0.01),
            font=self.font
        )
        self.health_bar_text = OnscreenText(
            text="HP: 100/100",
            pos=(-1.3, 0.7),
            scale=0.045,
            fg=(1.0, 0.392, 0.392, 1.0),
            align=TextNode.ALeft,
            mayChange=True,
            parent=self.parent,
            shadow=(0, 0, 0, 0.6),
            shadowOffset=(0.01, 0.01),
            font=self.font
        )
        self.mana_bar_text = OnscreenText(
            text="MP: 100/100",
            pos=(-1.3, 0.6),
            scale=0.045,
            fg=(0.392, 0.392, 1.0, 1.0),
            align=TextNode.ALeft,
            mayChange=True,
            parent=self.parent,
            shadow=(0, 0, 0, 0.6),
            shadowOffset=(0.01, 0.01),
            font=self.font
        )
        self.ai_info_text = OnscreenText(
            text="AI: Initializing...",
            pos=(-1.3, 0.5),
            scale=0.035,
            fg=(0.0, 1.0, 1.0, 1.0),
            align=TextNode.ALeft,
            mayChange=True,
            parent=self.parent,
            shadow=(0, 0, 0, 0.6),
            shadowOffset=(0.01, 0.01),
            font=self.font
        )
        self.skills_info_text = OnscreenText(
            text="Skills: None",
            pos=(-1.3, 0.4),
            scale=0.035,
            fg=(1.0, 0.392, 1.0, 1.0),
            align=TextNode.ALeft,
            mayChange=True,
            parent=self.parent,
            shadow=(0, 0, 0, 0.6),
            shadowOffset=(0.01, 0.01),
            font=self.font
        )
        self.items_info_text = OnscreenText(
            text="Items: None",
            pos=(-1.3, 0.3),
            scale=0.035,
            fg=(1.0, 1.0, 0.392, 1.0),
            align=TextNode.ALeft,
            mayChange=True,
            parent=self.parent,
            shadow=(0, 0, 0, 0.6),
            shadowOffset=(0.01, 0.01),
            font=self.font
        )
        self.effects_info_text = OnscreenText(
            text="Effects: None",
            pos=(-1.3, 0.2),
            scale=0.035,
            fg=(0.392, 1.0, 0.392, 1.0),
            align=TextNode.ALeft,
            mayChange=True,
            parent=self.parent,
            shadow=(0, 0, 0, 0.6),
            shadowOffset=(0.01, 0.01),
            font=self.font
        )
        self.genome_info_text = OnscreenText(
            text="Genome: Loading...",
            pos=(-1.3, 0.1),
            scale=0.035,
            fg=(1.0, 0.392, 1.0, 1.0),
            align=TextNode.ALeft,
            mayChange=True,
            parent=self.parent,
            shadow=(0, 0, 0, 0.6),
            shadowOffset=(0.01, 0.01),
            font=self.font
        )
        self.emotion_bar_text = OnscreenText(
            text="Emotions: Neutral",
            pos=(-1.3, 0.0),
            scale=0.035,
            fg=(1.0, 0.588, 0.392, 1.0),
            align=TextNode.ALeft,
            mayChange=True,
            parent=self.parent,
            shadow=(0, 0, 0, 0.6),
            shadowOffset=(0.01, 0.01),
            font=self.font
        )
        return self

    def destroy(self) -> None:
        for w in [
            self.game_title_text,
            self.health_bar_text,
            self.mana_bar_text,
            self.ai_info_text,
            self.skills_info_text,
            self.items_info_text,
            self.effects_info_text,
            self.genome_info_text,
            self.emotion_bar_text,
        ]:
            try:
                if w:
                    w.destroy()
            except Exception:
                pass

    def _load_font(self):
        try:
            # Try bundled font with Cyrillic support
            font_path = os.path.join('assets', 'fonts', 'DejaVuSans.ttf')
            import builtins
            loader = getattr(getattr(builtins, 'base', None), 'loader', None)
            if loader and os.path.exists(font_path):
                return loader.loadFont(font_path)
        except Exception:
            pass
        return None


def create_hud(parent_node) -> HUD:
    return HUD(parent_node).build()


