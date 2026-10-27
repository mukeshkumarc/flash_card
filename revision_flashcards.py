import html
import random
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

CSV_PATH = Path(__file__).with_name("july-2026-news.csv")

SWIPE_JS = """
<script>
const p = window.parent;
if (!p.__flashSwipeBound) {
  p.__flashSwipeBound = true;
  const findButton = label =>
    [...p.document.querySelectorAll("button")].find(b => b.innerText.includes(label));
  let startX = 0, startY = 0, skip = false;
  p.document.addEventListener("touchstart", e => {
    const t = e.target;
    skip = !!(t.closest && t.closest("button, input, textarea, select, a, [role='slider']"));
    startX = e.touches[0].clientX;
    startY = e.touches[0].clientY;
  }, { passive: true });
  p.document.addEventListener("touchend", e => {
    if (skip) return;
    const dx = e.changedTouches[0].clientX - startX;
    const dy = e.changedTouches[0].clientY - startY;
    if (Math.abs(dx) < 60 || Math.abs(dx) < 2 * Math.abs(dy)) return;
    const btn = dx < 0 ? findButton("Next") : findButton("Previous");
    if (btn && !btn.disabled) btn.click();
  }, { passive: true });
}
</script>
"""

st.set_page_config(page_title="July 2026 Revision Cards", page_icon="🗂️", layout="centered")

st.markdown(
    """
    <style>
    .card {
        background: #ffffff;
        color: #1a1a1a;
        border: 1px solid #e3e3e3;
        border-radius: 16px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.12);
        padding: 1.25rem;
        min-height: 300px;
        line-height: 1.5;
    }
    .card-topic {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #6b6b6b;
    }
    .card-title {
        font-size: 1.3rem;
        font-weight: 700;
        margin: 0.4rem 0 0.6rem;
    }
    .card-label {
        font-weight: 700;
        color: #1f6feb;
        margin-top: 0.9rem;
    }
    .card-body {
        white-space: pre-wrap;
        font-size: 1rem;
    }
    /* remove Streamlit's default top padding */
    div.block-container {
        padding-top: 1rem;
    }
    /* keep Previous / Next in one row on phones */
    div[data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        gap: 0.5rem;
    }
    div[data-testid="stHorizontalBlock"] div[data-testid="stColumn"] {
        min-width: 0 !important;
    }
    div[data-testid="stHorizontalBlock"] button {
        padding-left: 0.25rem;
        padding-right: 0.25rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_cards(path):
    df = pd.read_csv(path, dtype=str).fillna("")
    return df.to_dict("records")


@st.cache_data
def build_order(total, shuffle, seed):
    order = list(range(total))
    if shuffle:
        random.Random(seed).shuffle(order)
    return order


def url_int(name, default):
    try:
        return int(st.query_params.get(name, default))
    except (TypeError, ValueError):
        return default


def go(index, step, total):
    new_index = min(max(index + step, 0), total - 1)
    st.query_params["card"] = str(new_index + 1)


def on_order_change(total):
    st.query_params["shuffle"] = "1" if st.session_state.shuffle else "0"
    if st.session_state.shuffle:
        st.query_params["seed"] = str(random.randrange(1, 10**6))
    st.query_params["card"] = "1"


if not CSV_PATH.exists():
    st.error(f"CSV not found: {CSV_PATH.name}")
    st.stop()

cards = load_cards(CSV_PATH)
total = len(cards)

if total == 0:
    st.warning("The CSV has no rows.")
    st.stop()

# On a fresh page load (including refresh) restore the toggle from the URL.
if "shuffle" not in st.session_state:
    st.session_state.shuffle = st.query_params.get("shuffle") == "1"

order = build_order(total, st.session_state.shuffle, url_int("seed", 0))
index = min(max(url_int("card", 1), 1), total) - 1
card = cards[order[index]]

st.toggle(
    "Random order",
    key="shuffle",
    on_change=on_order_change,
    args=(total,),
)
components.html(SWIPE_JS, height=0)
st.progress((index + 1) / total, text=f"Card {index + 1} of {total}")

topic = html.escape(card["Topic"])
title = html.escape(card["Title"])

news = html.escape(card["News"])
facts = html.escape(card["Key Facts"])
content = f'<div class="card-label">News</div><div class="card-body">{news}</div>'
if facts:
    content += f'<div class="card-label">Key Facts</div><div class="card-body">{facts}</div>'

st.markdown(
    f"""
    <div class="card">
        <div class="card-topic">{topic}</div>
        <div class="card-title">{title}</div>
        {content}
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

prev_col, next_col = st.columns(2)
with prev_col:
    st.button(
        "⬅ Previous",
        on_click=go,
        args=(index, -1, total),
        disabled=index == 0,
        key="prev",
        use_container_width=True,
    )
with next_col:
    st.button(
        "Next ➡",
        on_click=go,
        args=(index, 1, total),
        disabled=index == total - 1,
        key="next",
        use_container_width=True,
    )

st.title("July 2026 Revision Cards")
