import time

import streamlit as st

from render import RenderConfig, render_sentence_to_image


st.set_page_config(page_title="Sentence → Image", layout="centered")
st.title("Sentence → Image")

text = st.text_area(
    "输入句子 / Enter sentence",
    height=120,
    placeholder="例如：In the quiet of that old house, every crack felt like a whisper...",
)

col1, col2 = st.columns(2)
with col1:
    width = st.number_input("宽度", min_value=200, max_value=4000, value=1080, step=10)
    height = st.number_input("高度", min_value=200, max_value=4000, value=1440, step=10)
    font_size = st.number_input("字号", min_value=10, max_value=300, value=64, step=2)
with col2:
    x = st.number_input("文字 X（像素）", min_value=0, max_value=4000, value=540, step=10)
    y = st.number_input("文字 Y（像素）", min_value=0, max_value=4000, value=720, step=10)
    max_width_px = st.number_input("文字最大宽度", min_value=100, max_value=4000, value=900, step=10)

bg = st.color_picker("背景色", value="#FFFFFF")
fg = st.color_picker("文字颜色", value="#111111")

font_path = st.text_input("字体路径（可选）", value="assets/fonts/NotoSansSC-Regular.ttf")

anchor = st.selectbox(
    "锚点 anchor（定位方式）",
    ["mm", "lt", "lm", "lb", "mt", "mb", "rt", "rm", "rb"],
    index=0,
)
align = st.selectbox("对齐 align（多行对齐）", ["left", "center", "right"], index=1)

auto_shrink = st.checkbox("自动缩小字号以适配画布", value=True)

if st.button("生成图片", type="primary", disabled=not text.strip()):
    ts = int(time.time())
    out_path = f"output/{ts}.png"
    cfg = RenderConfig(
        width=int(width),
        height=int(height),
        background=bg,
        text_color=fg,
        font_path=font_path if font_path.strip() else None,
        font_size=int(font_size),
        x=int(x),
        y=int(y),
        align=align,
        anchor=anchor,
        max_width_px=int(max_width_px),
        auto_shrink=auto_shrink,
    )
    path = render_sentence_to_image(text.strip(), cfg, out_path)
    st.success("已生成")
    st.image(path, caption=path)
    with open(path, "rb") as file:
        st.download_button("下载 PNG", file, file_name="sentence.png", mime="image/png")
