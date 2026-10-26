import html
import random
from pathlib import Path

import pandas as pd
import streamlit as st

CSV_PATH = Path(__file__).with_name("july-2026-news.csv")

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


def go(step, total):
    st.session_state.index = min(max(st.session_state.index + step, 0), total - 1)


def build_order(total, shuffle):
    order = list(range(total))
    if shuffle:
        random.shuffle(order)
    return order


def on_order_change(total):
    st.session_state.index = 0
    st.session_state.order = build_order(total, st.session_state.shuffle)


if not CSV_PATH.exists():
    st.error(f"CSV not found: {CSV_PATH.name}")
    st.stop()

cards = load_cards(CSV_PATH)
total = len(cards)

if total == 0:
    st.warning("The CSV has no rows.")
    st.stop()

if "index" not in st.session_state:
    st.session_state.index = 0
if "shuffle" not in st.session_state:
    st.session_state.shuffle = False
if len(st.session_state.get("order", [])) != total:
    st.session_state.order = build_order(total, st.session_state.shuffle)

st.session_state.index = min(st.session_state.index, total - 1)
index = st.session_state.index
card = cards[st.session_state.order[index]]

st.title("July 2026 Revision Cards")
st.toggle(
    "Random order",
    key="shuffle",
    on_change=on_order_change,
    args=(total,),
)
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
        args=(-1, total),
        disabled=index == 0,
        key="prev",
        use_container_width=True,
    )
with next_col:
    st.button(
        "Next ➡",
        on_click=go,
        args=(1, total),
        disabled=index == total - 1,
        key="next",
        use_container_width=True,
    )
