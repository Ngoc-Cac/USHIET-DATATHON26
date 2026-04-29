"""Data Model — schema graph + interactive table joins.

Power BI-style: visualize FK relationships, preview tables, run sample joins.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import math
import pandas as pd
import plotly.graph_objects as go
import networkx as nx
import streamlit as st

from data import load, available_tables, SCHEMA
from theme import (style, inject_css, page_header,
                   LIME, LIME_STRONG, LIME_DARK, DARK, AMBER, GREY, BG, BORDER)

st.set_page_config(page_title="Data Model", page_icon="🧬", layout="wide")
inject_css()
page_header("MODEL", "Data Schema & Joins",
            "13 prepared tables · FK relationships · live join playground")

# ---- Build graph ----
def build_graph():
    G = nx.DiGraph()
    for tbl, meta in SCHEMA.items():
        G.add_node(tbl, kind=meta["kind"], pk=meta["pk"], desc=meta["desc"])
    for tbl, meta in SCHEMA.items():
        for fk_col, ref_tbl, ref_col in meta["fks"]:
            if ref_tbl in SCHEMA:
                G.add_edge(tbl, ref_tbl, fk=fk_col, ref=ref_col)
    return G

G = build_graph()

# ---- Layout: facts in center column, dims outer ring, aggs below ----
def layout(G):
    pos = {}
    facts = [n for n, d in G.nodes(data=True) if d["kind"] == "fact"]
    dims = [n for n, d in G.nodes(data=True) if d["kind"] == "dimension"]
    aggs = [n for n, d in G.nodes(data=True) if d["kind"] == "agg"]

    for i, t in enumerate(dims):
        angle = 2 * math.pi * i / max(len(dims), 1)
        pos[t] = (3.5 * math.cos(angle), 2.6 * math.sin(angle) + 0.5)
    for i, t in enumerate(facts):
        pos[t] = (1.4 * (i - (len(facts) - 1) / 2), 0)
    for i, t in enumerate(aggs):
        pos[t] = (1.6 * (i - (len(aggs) - 1) / 2), -2.4)
    return pos

pos = layout(G)
KIND_COLOR = {"fact": LIME_DARK, "dimension": LIME, "agg": AMBER}

# Edges
edge_x, edge_y, edge_text = [], [], []
for u, v, data in G.edges(data=True):
    x0, y0 = pos[u]
    x1, y1 = pos[v]
    edge_x += [x0, x1, None]
    edge_y += [y0, y1, None]

edge_trace = go.Scatter(
    x=edge_x, y=edge_y, mode="lines",
    line=dict(color="#B0B7A2", width=1.2),
    hoverinfo="none", showlegend=False,
)

# Nodes
node_x, node_y, node_text, node_hover, node_color = [], [], [], [], []
for n, data in G.nodes(data=True):
    x, y = pos[n]
    node_x.append(x); node_y.append(y)
    node_text.append(n)
    node_hover.append(f"<b>{n}</b><br>{data['kind']} · PK: {data['pk']}<br>{data['desc']}")
    node_color.append(KIND_COLOR[data["kind"]])

node_trace = go.Scatter(
    x=node_x, y=node_y, mode="markers+text",
    marker=dict(size=44, color=node_color, line=dict(color=DARK, width=1.5),
                symbol="square"),
    text=node_text, textposition="middle center",
    textfont=dict(size=9, color=DARK, family="Inter"),
    hovertext=node_hover, hoverinfo="text",
    showlegend=False,
)

fig = go.Figure([edge_trace, node_trace])
fig.update_layout(
    title="Schema Graph (lime = fact · light = dim · amber = agg)",
    xaxis=dict(visible=False), yaxis=dict(visible=False),
)
style(fig, height=460, show_legend=False)
fig.update_layout(margin=dict(l=10, r=10, t=46, b=10))

st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})

st.markdown("---")

# ---- Interactive join playground ----
st.subheader("🔗 Join Playground")
left, right = st.columns(2)
with left:
    t1 = st.selectbox("Left table", list(SCHEMA.keys()), index=4, key="m_t1")
with right:
    # Suggest tables that have edge to t1 or t1 has edge to
    suggested = list(set([v for u, v in G.edges(t1)] + [u for u, v in G.in_edges(t1)]))
    options = list(SCHEMA.keys())
    default_idx = options.index(suggested[0]) if suggested else 0
    t2 = st.selectbox("Right table", options, index=default_idx, key="m_t2")

# Find candidate join keys (intersection of column names + declared FKs)
candidates: list[tuple[str, str]] = []
fk_decl = []
for u, v, d in G.edges(data=True):
    if (u == t1 and v == t2) or (u == t2 and v == t1):
        fk_decl.append((d["fk"], d["ref"]))

c1, c2 = st.columns(2)
with c1:
    sample_n = st.number_input("Sample rows per table", 1000, 100000, 5000, step=1000)
with c2:
    how = st.selectbox("Join type", ["inner", "left", "right", "outer"], index=0)

if st.button("Run join", type="primary"):
    df1 = load(t1).head(sample_n)
    df2 = load(t2).head(sample_n)
    common_cols = list(set(df1.columns) & set(df2.columns))

    if fk_decl:
        left_key, right_key = fk_decl[0]
    elif common_cols:
        left_key = right_key = common_cols[0]
    else:
        st.error(f"No common column between {t1} and {t2}.")
        st.stop()

    st.caption(f"Joining on: `{t1}.{left_key}` ⟷ `{t2}.{right_key}`  ·  type: {how}")
    try:
        merged = df1.merge(df2, left_on=left_key, right_on=right_key,
                           how=how, suffixes=(f"_{t1}", f"_{t2}"))
        c1, c2, c3 = st.columns(3)
        c1.metric(f"{t1} rows", f"{len(df1):,}")
        c2.metric(f"{t2} rows", f"{len(df2):,}")
        c3.metric("Joined rows", f"{len(merged):,}")
        st.dataframe(merged.head(200), use_container_width=True, height=320)
    except Exception as e:
        st.error(f"Join failed: {e}")

st.markdown("---")

# ---- Table catalog ----
st.subheader("📚 Table Catalog")
for kind in ["fact", "dimension", "agg"]:
    items = [(t, m) for t, m in SCHEMA.items() if m["kind"] == kind]
    with st.expander(f"{kind.capitalize()} tables ({len(items)})"):
        for t, m in items:
            st.markdown(f"**`{t}`** · PK: `{m['pk']}` — {m['desc']}")
            if m["fks"]:
                fks = ", ".join(f"`{fk}`→`{rt}.{rc}`" for fk, rt, rc in m["fks"])
                st.caption(f"FK: {fks}")
