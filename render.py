from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple
import os
import textwrap

from PIL import Image, ImageDraw, ImageFont


@dataclass
class RenderConfig:
    width: int = 1080
    height: int = 1440
    background: str = "#FFFFFF"
    text_color: str = "#111111"
    font_path: Optional[str] = None
    font_size: int = 64

    x: int = 540
    y: int = 720
    align: str = "center"
    anchor: str = "mm"

    max_width_px: int = 900
    line_spacing: int = 12
    wrap_chars: int = 20

    auto_shrink: bool = True
    min_font_size: int = 18


def _load_font(font_path: Optional[str], font_size: int) -> ImageFont.ImageFont:
    if font_path and os.path.exists(font_path):
        return ImageFont.truetype(font_path, font_size)
    return ImageFont.load_default()


def _measure_multiline(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
    spacing: int,
) -> Tuple[int, int]:
    bbox = draw.multiline_textbbox(
        (0, 0),
        text,
        font=font,
        spacing=spacing,
        align="left",
    )
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    return width, height


def _wrap_text_to_px(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
    max_width_px: int,
    wrap_chars: int,
) -> str:
    lines = []
    for raw_line in text.splitlines() or [""]:
        if len(raw_line) <= wrap_chars:
            lines.append(raw_line)
            continue
        chunks = textwrap.wrap(
            raw_line,
            width=wrap_chars,
            break_long_words=True,
            break_on_hyphens=False,
        )
        lines.extend(chunks or [""])

    joined = "\n".join(lines)
    width, _ = _measure_multiline(draw, joined, font, spacing=0)
    if width <= max_width_px:
        return joined

    current_width = wrap_chars
    while current_width > 5:
        lines = []
        for raw_line in text.splitlines() or [""]:
            chunks = textwrap.wrap(
                raw_line,
                width=current_width,
                break_long_words=True,
                break_on_hyphens=False,
            )
            lines.extend(chunks or [""])
        joined = "\n".join(lines)
        width, _ = _measure_multiline(draw, joined, font, spacing=0)
        if width <= max_width_px:
            return joined
        current_width -= 1

    return joined


def render_sentence_to_image(text: str, cfg: RenderConfig, out_path: str) -> str:
    image = Image.new("RGB", (cfg.width, cfg.height), cfg.background)
    draw = ImageDraw.Draw(image)

    font_size = cfg.font_size
    font = _load_font(cfg.font_path, font_size)
    wrapped = _wrap_text_to_px(draw, text, font, cfg.max_width_px, cfg.wrap_chars)

    if cfg.auto_shrink:
        while font_size > cfg.min_font_size:
            width, height = _measure_multiline(
                draw,
                wrapped,
                font,
                spacing=cfg.line_spacing,
            )
            if width <= cfg.max_width_px and height <= cfg.height - 80:
                break
            font_size -= 2
            font = _load_font(cfg.font_path, font_size)
            wrapped = _wrap_text_to_px(
                draw,
                text,
                font,
                cfg.max_width_px,
                cfg.wrap_chars,
            )

    draw.multiline_text(
        (cfg.x, cfg.y),
        wrapped,
        font=font,
        fill=cfg.text_color,
        anchor=cfg.anchor,
        align=cfg.align,
        spacing=cfg.line_spacing,
    )

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    image.save(out_path, format="PNG")
    return out_path
