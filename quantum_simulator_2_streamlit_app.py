import math
from itertools import combinations
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# ── Earthy site/bond colours (constant across modes) ──────────
SAGE     = "#7D8B5A"
AMBER    = "#C9983A"
BUTTER   = "#C9BB68"
STEEL    = "#7A9DAC"
ROSE     = "#C4907E"
MOSS     = "#9DA872"
SLATE    = "#3D5F78"
TERRA    = "#A84E3C"
DARK_BRN = "#4E3428"
OFF_WHT  = "#E5E0D8"

SCHEME = {"even": SAGE, "odd": ROSE, "bond": "#9A7E60"}

# ── Theme definitions ──────────────────────────────────────────
THEMES = {
    "light": {
        "page_bg":   "#F5F0E8",
        "card_bg":   "#EDE7DA",
        "border":    "#C8BDA8",
        "plot_bg":   "#FAF7F2",
        "txt_main":  "#2A2018",
        "txt_mute":  "#7A6A55",
        "hero_grad": "linear-gradient(135deg, #EDE7DA 0%, #E3DDD0 100%)",
        "accent":    "#8B5E2A",
        "swatch_b":  "rgba(0,0,0,0.18)",
        "hover_bg":  "#EDE7DA",
        "hover_txt": "#2A2018",
        "label_txt": "#1A1410",
    },
    "dark": {
        "page_bg":   "#252018",
        "card_bg":   "#302A22",
        "border":    "#4A3C2C",
        "plot_bg":   "#F2EBE0",
        "txt_main":  "#E5E0D8",
        "txt_mute":  "#9A8870",
        "hero_grad": "linear-gradient(135deg, #302A22 0%, #252018 100%)",
        "accent":    ROSE,
        "swatch_b":  "rgba(255,255,255,0.15)",
        "hover_bg":  "#302A22",
        "hover_txt": "#E5E0D8",
        "label_txt": "#E5E0D8",
    },
}

# ── Page config ────────────────────────────────────────────────
st.set_page_config(page_title="Hubbard Model Simulator", layout="wide")

_, col_toggle = st.columns([6, 1])
with col_toggle:
    dark_mode = st.toggle("Dark mode", value=False)

T = THEMES["dark"] if dark_mode else THEMES["light"]

# ── CSS ────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  .stApp {{
    background-color: {T['page_bg']};
    color: {T['txt_main']};
    font-family: 'Georgia', serif;
  }}
  header[data-testid="stHeader"] {{ background: transparent; }}
  div[data-testid="stToggle"] label p {{
    color: {T['txt_mute']} !important;
    font-size: 0.82rem !important;
  }}
  .hero {{
    background: {T['hero_grad']};
    border: 1px solid {T['border']};
    border-radius: 16px;
    padding: 1.9rem 2.5rem 1.5rem;
    margin-bottom: 1.2rem;
  }}
  .hero h1 {{
    font-size: 2.2rem;
    font-weight: 700;
    color: {T['accent']};
    margin: 0 0 0.4rem;
  }}
  .hero p {{
    color: {T['txt_mute']};
    font-size: 0.95rem;
    line-height: 1.72;
    margin: 0;
  }}
  .metric-row {{
    display: flex;
    gap: 0.8rem;
    margin: 0.8rem 0 1rem;
  }}
  .metric-card {{
    flex: 1;
    background: {T['card_bg']};
    border: 1px solid {T['border']};
    border-radius: 12px;
    padding: 0.82rem 1rem;
    text-align: center;
  }}
  .metric-card .lbl {{
    font-size: 0.69rem;
    color: {T['txt_mute']};
    text-transform: uppercase;
    letter-spacing: 1.3px;
  }}
  .metric-card .val {{
    font-size: 1.85rem;
    font-weight: 700;
    color: {T['accent']};
    line-height: 1.15;
  }}
  .metric-card .sub {{
    font-size: 0.73rem;
    color: {T['txt_mute']};
  }}
  .sec-lbl {{
    font-size: 0.72rem;
    color: {T['txt_mute']};
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin: 1.2rem 0 0.4rem;
    border-left: 2px solid {SAGE};
    padding-left: 0.6rem;
  }}
  label p, .stSlider label p,
  .stCheckbox label p, .stSelectbox label p {{
    color: {T['txt_mute']} !important;
    font-size: 0.87rem !important;
  }}
  .legend {{
    display: flex;
    flex-wrap: wrap;
    gap: 1.2rem;
    margin: 0.4rem 0 0.7rem;
    align-items: center;
  }}
  .legend-item {{
    display: flex;
    align-items: center;
    gap: 0.45rem;
    font-size: 0.80rem;
    color: {T['txt_mute']};
  }}
  .swatch {{
    width: 15px; height: 15px;
    border-radius: 50%;
    display: inline-block;
    border: 1.5px solid {T['swatch_b']};
  }}
  .bond-swatch {{
    display: inline-block;
    width: 22px; height: 3px;
    border-radius: 2px;
  }}
  .caption-box {{
    background: {T['card_bg']};
    border-left: 3px solid {SAGE};
    border-radius: 0 8px 8px 0;
    padding: 0.7rem 1.1rem;
    color: {T['txt_mute']};
    font-size: 0.83rem;
    line-height: 1.65;
    margin-top: 0.6rem;
  }}
  .z-card {{
    background: {T['card_bg']};
    border: 1px solid {T['border']};
    border-radius: 12px;
    padding: 1rem 1.3rem;
    margin-bottom: 0.7rem;
  }}
</style>
""", unsafe_allow_html=True)

# ── Module-level helpers ───────────────────────────────────────
def build_figure(D, T, show_labels, show_bonds):
    fig = go.Figure()
    if show_bonds:
        bx, by = [], []
        for row in range(D):
            for col in range(D):
                if col < D - 1:
                    bx += [col, col + 1, None]
                    by += [row, row,      None]
                if row < D - 1:
                    bx += [col, col,      None]
                    by += [row, row + 1,  None]
        fig.add_trace(go.Scatter(
            x=bx, y=by, mode="lines",
            line=dict(color=SCHEME["bond"], width=3.5),
            hoverinfo="none", showlegend=False,
        ))
    marker_size = max(24, 70 - D * 7)
    font_size   = max(8, 18 - D)
    for parity, sub_label in [(0, "A"), (1, "B")]:
        color = SCHEME["even"] if parity == 0 else SCHEME["odd"]
        sx, sy, texts, hovers = [], [], [], []
        for row in range(D):
            for col in range(D):
                if (row + col) % 2 == parity:
                    idx = row * D + col
                    sx.append(col); sy.append(row)
                    texts.append(str(idx))
                    hovers.append(
                        f"<b>Site {idx}</b><br>"
                        f"Position: ({col}, {row})<br>"
                        f"Sublattice: {sub_label}"
                    )
        fig.add_trace(go.Scatter(
            x=sx, y=sy,
            mode="markers+text" if show_labels else "markers",
            marker=dict(size=marker_size, color=color, symbol="circle",
                        line=dict(color=DARK_BRN, width=1.8), opacity=0.93),
            text=texts if show_labels else None,
            textposition="middle center",
            textfont=dict(color=T["label_txt"], size=font_size, family="Arial Black"),
            hovertemplate="%{customdata}<extra></extra>",
            customdata=hovers,
            showlegend=False,
        ))
    pad = 0.85
    fig.update_layout(
        paper_bgcolor=T["page_bg"], plot_bgcolor=T["plot_bg"],
        xaxis=dict(range=[-pad, D - 1 + pad], showgrid=False, zeroline=False,
                   showticklabels=False, scaleanchor="y", scaleratio=1, fixedrange=True),
        yaxis=dict(range=[-pad, D - 1 + pad], showgrid=False, zeroline=False,
                   showticklabels=False, fixedrange=True),
        margin=dict(l=24, r=24, t=24, b=24), height=520,
        hoverlabel=dict(bgcolor=T["hover_bg"], bordercolor=T["border"],
                        font=dict(color=T["hover_txt"], size=13, family="Georgia")),
        dragmode=False,
    )
    return fig

OCC_VAL  = {(False, False): 0, (True, False): 1,
            (False, True):  2, (True, True):  3}
BADGE_BG  = ["#D8D0C4", SAGE,    ROSE,    SLATE]
BADGE_SYM = ["·",       "↑",     "↓",     "↑↓"]
BADGE_FG  = [DARK_BRN,  OFF_WHT, OFF_WHT, OFF_WHT]

def gen_states(N, limit=None):
    idx = 0
    for k in range(N + 1):
        for up in combinations(range(N), k):
            for dn in combinations(range(N), k):
                if limit is not None and idx >= limit:
                    return
                u, d = set(up), set(dn)
                yield idx, k, [OCC_VAL[(s in u, s in d)] for s in range(N)]
                idx += 1

def badge_html(v, size=30):
    return (f'<span style="display:inline-flex;align-items:center;justify-content:center;'
            f'width:{size}px;height:{size}px;border-radius:50%;background:{BADGE_BG[v]};'
            f'color:{BADGE_FG[v]};font-size:0.80rem;font-weight:700;">{BADGE_SYM[v]}</span>')

# ── Zeeman helpers (4-site Heisenberg ring) ────────────────────
_Z_BONDS = [(i, (i + 1) % 4) for i in range(4)]
_sz0_basis = [tuple(1 if i in up else 0 for i in range(4))
              for up in combinations(range(4), 2)]
_sz1_basis = [tuple(1 if i in up else 0 for i in range(4))
              for up in combinations(range(4), 3)]
_szm1_basis = [tuple(1 if i in up else 0 for i in range(4))
               for up in combinations(range(4), 1)]
_sz2_basis  = [(1, 1, 1, 1)]

def build_heisenberg(J, basis):
    n = len(basis)
    H = np.zeros((n, n))
    idx_map = {s: i for i, s in enumerate(basis)}
    for row, state in enumerate(basis):
        for (a, b) in _Z_BONDS:
            sz_a = 0.5 if state[a] else -0.5
            sz_b = 0.5 if state[b] else -0.5
            H[row, row] += J * sz_a * sz_b
            if state[a] != state[b]:
                lst = list(state)
                lst[a], lst[b] = lst[b], lst[a]
                ns = tuple(lst)
                if ns in idx_map:
                    H[row, idx_map[ns]] += J * 0.5
    return H

_H_unit = build_heisenberg(1.0, _sz0_basis)

def _spin_label(state):
    return "|" + "".join("↑" if s else "↓" for s in state) + "⟩"

# ── Hero ───────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
  <h1>Hubbard Model Quantum Simulator</h1>
  <p>
    Electrons hop across a D&times;D square lattice with amplitude <em>t</em>.
    On-site Coulomb repulsion <em>U</em> penalises double occupancy.
    The two site colours reveal the <strong>bipartite sublattice structure</strong> —
    a symmetry driving antiferromagnetism at half-filling.
    &nbsp;<strong>Hover any site for details.</strong>
  </p>
</div>
""", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────
tab_sim, tab_zeeman = st.tabs(["Hubbard Simulator", "Zeeman Analysis"])

# ══════════════════════════════════════════════════════════════
# TAB 1 — Hubbard Simulator
# ══════════════════════════════════════════════════════════════
with tab_sim:
    st.markdown('<p class="sec-lbl">Lattice Configuration</p>', unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([4, 1, 1])
    with col_a:
        D = st.slider("Lattice dimension  D × D", min_value=2, max_value=8, value=4, step=1)
    with col_b:
        show_labels = st.checkbox("Site labels", value=True)
    with col_c:
        show_bonds = st.checkbox("Bonds", value=True)

    N       = D * D
    n_bonds = 2 * D * (D - 1)
    _hval   = 4 ** N
    if _hval < 1_000_000_000:
        hilbert_str = f"{_hval:,}"
    else:
        _exp   = int(math.log10(_hval))
        _coeff = _hval / (10 ** _exp)
        hilbert_str = f"{_coeff:.2f} &times; 10<sup>{_exp}</sup>"

    st.markdown(f"""
<div class="metric-row">
  <div class="metric-card">
    <div class="lbl">Sites (N)</div>
    <div class="val">{N}</div>
    <div class="sub">{D} × {D} grid</div>
  </div>
  <div class="metric-card">
    <div class="lbl">Bonds</div>
    <div class="val">{n_bonds}</div>
    <div class="sub">nearest-neighbour</div>
  </div>
  <div class="metric-card">
    <div class="lbl">Hilbert dim.</div>
    <div class="val">{hilbert_str}</div>
    <div class="sub">4<sup>N</sup> states</div>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown(f"""
<div class="legend">
  <div class="legend-item">
    <span class="swatch" style="background:{SCHEME['even']};"></span>
    <span>Sage — A sublattice (row+col even)</span>
  </div>
  <div class="legend-item">
    <span class="swatch" style="background:{SCHEME['odd']};"></span>
    <span>Dusty rose — B sublattice (row+col odd)</span>
  </div>
  <div class="legend-item">
    <span class="bond-swatch" style="background:{SCHEME['bond']};"></span>
    <span>Hopping bond <em>t</em></span>
  </div>
</div>
""", unsafe_allow_html=True)

    fig = build_figure(D, T, show_labels, show_bonds)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        f'<div class="caption-box">'
        f'<b>Bipartite structure</b>: the square lattice splits into two interlocking '
        f'sublattices A and B. At half-filling with strong repulsion <em>U &gg; t</em>, '
        f'electrons localise with opposite spins on A and B sites, '
        f'producing <em>antiferromagnetic order</em>. '
        f'Hover any site to inspect its index and sublattice.'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Sz = 0 Subspace ────────────────────────────────────────
    st.markdown('<p class="sec-lbl" style="margin-top:2rem;">S<sub>z</sub> = 0 Subspace</p>',
                unsafe_allow_html=True)

    dim_sz0 = math.comb(2 * N, N)

    st.markdown(f"""
<div class="caption-box" style="margin-bottom:1rem;">
  Restrict to states where the total spin projection
  <b>S<sub>z</sub> = &frac12;(N<sub>&uarr;</sub> &minus; N<sub>&darr;</sub>) = 0</b>,
  i.e. equal numbers of spin-up and spin-down electrons.<br><br>
  Each site can be <b>&middot;</b>&thinsp;(empty),&ensp;
  <b>&uarr;</b>&thinsp;(spin-up),&ensp;
  <b>&darr;</b>&thinsp;(spin-down),&ensp;or&ensp;
  <b>&uarr;&darr;</b>&thinsp;(doubly occupied).<br><br>
  We label each sector by an integer <b>k</b>, defined as:<br>
  &emsp;<b>k = N<sub>&uarr;</sub> = N<sub>&darr;</sub></b>
  &ensp;&mdash;&ensp; the number of spin-up electrons,
  which must equal the number of spin-down electrons.<br>
  <em>k</em> ranges from 0 (all sites empty) to N (all sites doubly occupied).<br><br>
  For a given <em>k</em> there are C(N,k) ways to place the k spin-up electrons on N sites,
  and independently C(N,k) ways for the k spin-down electrons, giving
  C(N,k)<sup>2</sup> states. Summing over all <em>k</em>:<br>
  <span style="font-size:1.05rem;">
    <b>D = &sum;<sub>k=0</sub><sup>N</sup> C(N,k)&sup2; = C(2N, N)
    = C({2*N},&thinsp;{N}) = {dim_sz0:,}</b>
  </span>
  &nbsp;&nbsp;(by Vandermonde&rsquo;s identity)
</div>
""", unsafe_allow_html=True)

    tbl_rows_html = "".join(
        f'<tr style="border-bottom:1px solid #DDD5C8;">'
        f'<td style="padding:9px 18px;color:#2A2018;text-align:center;">{k}</td>'
        f'<td style="padding:9px 18px;color:#2A2018;text-align:center;">{math.comb(N,k)}</td>'
        f'<td style="padding:9px 18px;color:#2A2018;text-align:center;font-weight:600;">'
        f'{math.comb(N,k)**2}</td>'
        f'</tr>'
        for k in range(N + 1)
    )
    tbl_html = f"""
<div style="border-radius:10px;overflow:hidden;border:1px solid #C8BDA8;margin-bottom:0.3rem;">
<table style="width:100%;border-collapse:collapse;background:#FFFFFF;">
  <thead>
    <tr style="background:#F0E8DA;border-bottom:2px solid #C8BDA8;">
      <th style="padding:10px 18px;color:#4E3428;font-size:0.82rem;font-weight:700;text-align:center;">
        k &nbsp;=&nbsp; N<sub>↑</sub> &nbsp;=&nbsp; N<sub>↓</sub></th>
      <th style="padding:10px 18px;color:#4E3428;font-size:0.82rem;font-weight:700;text-align:center;">
        C(N, k) &nbsp;&mdash;&nbsp; ways to place k ↑ electrons on N sites</th>
      <th style="padding:10px 18px;color:#4E3428;font-size:0.82rem;font-weight:700;text-align:center;">
        C(N, k)² &nbsp;&mdash;&nbsp; states in this k-sector</th>
    </tr>
  </thead>
  <tbody>{tbl_rows_html}</tbody>
</table>
</div>
"""

    with st.expander("States per k-sector  (each row = one value of N↑ = N↓)", expanded=True):
        st.markdown(tbl_html, unsafe_allow_html=True)

    # ── N = 2 example ──────────────────────────────────────────
    with st.expander(
        "Sz = 0 Example — all 6 states on a 2-site lattice  (N = 2)", expanded=True
    ):
        ex2 = list(gen_states(2))
        SZ_STR = {0: "0", 1: "+½", 2: "−½", 3: "0"}
        PW, PH = 2.3, 1.7
        NCOLS  = 3
        SX_OFF = [0.48, 1.82]
        SY     = 0.80
        MKR    = 34
        PLOT_BG = "#FFFFFF" if not dark_mode else "#2A2420"
        K_BG = {
            0: ("#F5EFE6" if not dark_mode else "#2E2820"),
            1: ("#EBE4D8" if not dark_mode else "#272118"),
            2: ("#F5EFE6" if not dark_mode else "#2E2820"),
        }
        fig_ex = go.Figure()
        for pi, (state_idx, k_val, occ) in enumerate(ex2):
            pcol, prow = pi % NCOLS, pi // NCOLS
            ox, oy = pcol * PW, (1 - prow) * PH
            fig_ex.add_shape(
                type="rect",
                x0=ox + 0.06, y0=oy + 0.04,
                x1=ox + PW - 0.06, y1=oy + PH - 0.04,
                fillcolor=K_BG[k_val],
                line=dict(color=T["border"], width=0.8), layer="below",
            )
            prev_k = ex2[pi - 1][1] if pi > 0 else -1
            if k_val != prev_k:
                ck = math.comb(2, k_val)
                fig_ex.add_annotation(
                    x=ox + 0.14, y=oy + PH - 0.10,
                    text=f"<b>k = {k_val}</b>  (N↑=N↓={k_val},  {ck}²={ck*ck} state{'s' if ck*ck!=1 else ''})",
                    showarrow=False, xanchor="left", yanchor="top",
                    font=dict(size=8.5, color=T["txt_mute"]),
                )
            sx = [ox + SX_OFF[0], ox + SX_OFF[1]]
            sy = [oy + SY, oy + SY]
            fig_ex.add_trace(go.Scatter(
                x=sx, y=sy, mode="lines",
                line=dict(color=SCHEME["bond"], width=3),
                hoverinfo="none", showlegend=False,
            ))
            for s in range(2):
                v = occ[s]
                fig_ex.add_trace(go.Scatter(
                    x=[sx[s]], y=[sy[s]],
                    mode="markers+text",
                    marker=dict(size=MKR, color=BADGE_BG[v],
                                line=dict(color=DARK_BRN, width=1.5)),
                    text=[BADGE_SYM[v]],
                    textposition="middle center",
                    textfont=dict(color=BADGE_FG[v], size=11, family="Arial Black"),
                    hovertemplate=f"<b>Site {s}: {BADGE_SYM[v]}</b><br>Sz = {SZ_STR[v]}<extra></extra>",
                    showlegend=False,
                ))
                fig_ex.add_annotation(
                    x=sx[s], y=sy[s] + 0.24, text=f"site {s}",
                    showarrow=False, xanchor="center",
                    font=dict(size=7.5, color=T["txt_mute"]),
                )
                fig_ex.add_annotation(
                    x=sx[s], y=sy[s] - 0.24, text=f"Sz = {SZ_STR[v]}",
                    showarrow=False, xanchor="center",
                    font=dict(size=8, color=T["txt_main"]),
                )
            ket = f"|{BADGE_SYM[occ[0]]}, {BADGE_SYM[occ[1]]}⟩  #{state_idx}"
            fig_ex.add_annotation(
                x=ox + PW / 2, y=oy + 0.13, text=ket,
                showarrow=False, xanchor="center",
                font=dict(size=9, color=T["txt_main"], family="Georgia"),
            )
        fig_ex.update_layout(
            paper_bgcolor=T["page_bg"], plot_bgcolor=PLOT_BG,
            height=300, margin=dict(l=8, r=8, t=8, b=8),
            xaxis=dict(range=[0, NCOLS * PW], showgrid=False, zeroline=False,
                       showticklabels=False, fixedrange=True),
            yaxis=dict(range=[0, 2 * PH], showgrid=False, zeroline=False,
                       showticklabels=False, fixedrange=True),
            showlegend=False,
            hoverlabel=dict(bgcolor=T["hover_bg"], bordercolor=T["border"],
                            font=dict(color=T["hover_txt"], size=12)),
        )
        st.plotly_chart(fig_ex, use_container_width=True)
        st.caption(
            "Each circle is a lattice site. Color and symbol show occupation. "
            "Sz = ±½ per spin-½ electron; doubly-occupied (↑↓) and empty sites both contribute Sz = 0. "
            "Shading groups states by k = N↑ = N↓."
        )

    if N <= 4:
        by_k: dict = {}
        for idx, k, occ in gen_states(N):
            by_k.setdefault(k, []).append((idx, occ))
        legend_html = "".join(
            f'<div style="display:flex;align-items:center;gap:5px;font-size:0.78rem;'
            f'color:{T["txt_mute"]};">'
            f'{badge_html(v)}'
            f'{"Empty" if v==0 else "Spin-up" if v==1 else "Spin-down" if v==2 else "Doubly occ."}'
            f'</div>'
            for v in range(4)
        )
        rows_html = []
        for k in range(N + 1):
            ck = math.comb(N, k)
            rows_html.append(
                f'<div style="font-size:0.72rem;color:{T["txt_mute"]};text-transform:uppercase;'
                f'letter-spacing:1px;border-bottom:1px solid {T["border"]};'
                f'padding:5px 0 3px;margin:10px 0 4px;">'
                f'k = {k} &ensp;(N<sub>&uarr;</sub> = N<sub>&darr;</sub> = {k})'
                f'&ensp;&middot;&ensp; C({N},{k})<sup>2</sup> = {ck}<sup>2</sup>'
                f' = {ck*ck} states</div>'
            )
            states = by_k.get(k, [])
            for i in range(0, len(states), 4):
                cells = "".join(
                    f'<div style="display:flex;align-items:center;gap:3px;margin:2px 8px 2px 0;">'
                    f'<span style="font-size:0.66rem;color:{T["txt_mute"]};width:18px;'
                    f'text-align:right;flex-shrink:0;">{si}</span>'
                    + "".join(badge_html(v) for v in occ)
                    + f'</div>'
                    for si, occ in states[i:i+4]
                )
                rows_html.append(f'<div style="display:flex;flex-wrap:wrap;">{cells}</div>')
        full_html = (
            f'<div style="background:{T["card_bg"]};border:1px solid {T["border"]};'
            f'border-radius:12px;padding:1rem 1.4rem;max-height:560px;overflow-y:auto;">'
            f'<div style="display:flex;flex-wrap:wrap;gap:16px;margin-bottom:0.9rem;">'
            f'{legend_html}</div>'
            + "".join(rows_html)
            + f'</div>'
        )
        with st.expander(
            f"All {dim_sz0} basis states — {D}×{D} lattice, N = {N} sites", expanded=True
        ):
            st.markdown(full_html, unsafe_allow_html=True)

    elif N <= 9:
        MAX_S = 200
        z_data, x_labs, k_starts = [], [], {}
        for idx, k, occ in gen_states(N, limit=MAX_S):
            if k not in k_starts:
                k_starts[k] = idx
            z_data.append(occ)
            x_labs.append(str(idx))
        z_T      = [list(col) for col in zip(*z_data)]
        custom_T = [[BADGE_SYM[v] for v in row] for row in z_T]
        cs = [
            [0.000, "#D8D0C4"], [0.249, "#D8D0C4"],
            [0.250, SAGE],      [0.499, SAGE],
            [0.500, ROSE],      [0.749, ROSE],
            [0.750, SLATE],     [1.000, SLATE],
        ]
        fig_h = go.Figure(go.Heatmap(
            z=z_T, x=x_labs,
            y=[f"Site {s}" for s in range(N)],
            colorscale=cs, zmin=0, zmax=3, showscale=False,
            customdata=custom_T,
            hovertemplate="<b>State %{x}</b> · %{y}: <b>%{customdata}</b><extra></extra>",
            xgap=1, ygap=1,
        ))
        for k, start in sorted(k_starts.items()):
            if start > 0:
                fig_h.add_vline(x=start - 0.5, line=dict(color=T["border"], width=1.5))
            fig_h.add_annotation(
                x=start + 0.3, y=1.06,
                text=f"k={k}  (N↑=N↓={k})",
                xanchor="left", showarrow=False, yref="paper",
                font=dict(color=T["txt_mute"], size=9),
            )
        fig_h.update_layout(
            paper_bgcolor=T["page_bg"], plot_bgcolor=T["plot_bg"],
            height=50 * N + 80, margin=dict(l=65, r=20, t=35, b=45),
            xaxis=dict(title=dict(text="State index", font=dict(color=T["txt_mute"], size=11)),
                       showticklabels=len(z_data) <= 40,
                       tickfont=dict(color=T["txt_mute"], size=9)),
            yaxis=dict(tickfont=dict(color=T["txt_main"], size=10), autorange="reversed"),
            hoverlabel=dict(bgcolor=T["hover_bg"], bordercolor=T["border"],
                            font=dict(color=T["hover_txt"], size=12)),
        )
        n_shown = len(z_data)
        label = f"First {n_shown} of {dim_sz0:,}" if n_shown < dim_sz0 else f"All {dim_sz0:,}"
        with st.expander(
            f"Basis states — {D}×{D} lattice  ({label} states)", expanded=True
        ):
            st.plotly_chart(fig_h, use_container_width=True)
            if n_shown < dim_sz0:
                st.caption(f"Showing first {n_shown} of {dim_sz0:,} Sz=0 states.")

    else:
        st.markdown(
            f'<div class="caption-box">'
            f'For N = {N} sites the Sz=0 sector has <b>{dim_sz0:,}</b> states — '
            f'too large to enumerate in the browser. '
            f'See the breakdown table above for the structure by electron number <em>k</em>.'
            f'</div>',
            unsafe_allow_html=True,
        )

# ══════════════════════════════════════════════════════════════
# TAB 2 — Zeeman Analysis
# ══════════════════════════════════════════════════════════════
with tab_zeeman:

    st.markdown(f"""
<div class="hero">
  <h1 style="font-size:1.6rem;">Zeeman Analysis — 4-Site Heisenberg Ring</h1>
  <p>
    Spin-½ Heisenberg ring on <em>N = 4</em> sites with antiferromagnetic exchange <em>J &gt; 0</em>
    and external field <em>H</em>.
    Total Hamiltonian:
    <em>Ĥ = J Σ<sub>i</sub> Ŝ<sub>i</sub>·Ŝ<sub>i+1</sub> − H Σ<sub>i</sub> Ŝ<sup>z</sup><sub>i</sub></em>
    (periodic boundary conditions).
  </p>
</div>
""", unsafe_allow_html=True)

    # ── Section 0: Sz = 0 Subspace ─────────────────────────────
    st.markdown('<p class="sec-lbl">1 · S<sub>z</sub> = 0 Subspace</p>',
                unsafe_allow_html=True)

    _N4 = 4
    _dim_sz0_4 = math.comb(2 * _N4, _N4)   # C(8,4) = 70, but for spin-only: C(4,2)=6

    st.markdown(f"""
<div class="caption-box" style="margin-bottom:1rem;">
  Restrict to states where the total spin projection
  <b>S<sub>z</sub> = &frac12;(N<sub>&uarr;</sub> &minus; N<sub>&darr;</sub>) = 0</b>,
  i.e. equal numbers of spin-up and spin-down electrons.<br><br>
  For the <b>4-site spin-½ Heisenberg ring</b> each site carries one spin-½.
  Each site is either <b>&uarr;</b> or <b>&darr;</b>, so with
  N<sub>&uarr;</sub> = N<sub>&darr;</sub> = 2 the number of S<sub>z</sub> = 0
  basis states is:
  <span style="font-size:1.05rem;">
    <b>D = C(4, 2) = 6</b>
  </span><br><br>
  These 6 states span the block of the Hamiltonian that is <em>completely unaffected
  by the external field H</em> — as proved in the next section.
</div>
""", unsafe_allow_html=True)

    with st.expander("All 6 basis states of the Sz = 0 sector (N = 4 sites)", expanded=True):
        # Build a small visual grid of the 6 states using badge-style circles
        _z_labels = [_spin_label(s) for s in _sz0_basis]
        _z_sz_str  = {(1,): "↑  (Sz = +½)", (0,): "↓  (Sz = −½)"}

        # Display as an HTML table: one row per state, one column per site
        _site_cols = "".join(
            f'<th style="padding:6px 18px;color:{T["txt_mute"]};font-size:0.78rem;'
            f'font-weight:600;text-align:center;">Site {i}</th>'
            for i in range(4)
        )
        _state_rows = ""
        for si, state in enumerate(_sz0_basis):
            _cells = ""
            for spin in state:
                _bg  = SAGE  if spin else ROSE
                _sym = "↑"   if spin else "↓"
                _fg  = OFF_WHT
                _cells += (
                    f'<td style="padding:8px 18px;text-align:center;">'
                    f'<span style="display:inline-flex;align-items:center;justify-content:center;'
                    f'width:32px;height:32px;border-radius:50%;background:{_bg};'
                    f'color:{_fg};font-size:0.95rem;font-weight:700;">{_sym}</span>'
                    f'</td>'
                )
            _ket = _z_labels[si]
            _state_rows += (
                f'<tr style="border-bottom:1px solid {T["border"]};">'
                f'<td style="padding:8px 14px;color:{T["txt_mute"]};font-size:0.80rem;'
                f'text-align:center;font-family:monospace;">#{si}</td>'
                f'{_cells}'
                f'<td style="padding:8px 14px;color:{T["txt_main"]};font-size:0.85rem;'
                f'text-align:center;font-family:Georgia;">{_ket}</td>'
                f'<td style="padding:8px 14px;color:{T["txt_mute"]};font-size:0.78rem;'
                f'text-align:center;">Sz = 0</td>'
                f'</tr>'
            )

        _tbl = f"""
<div style="border-radius:10px;overflow:hidden;border:1px solid {T['border']};">
<table style="width:100%;border-collapse:collapse;background:{T['card_bg']};">
  <thead>
    <tr style="background:{T['card_bg']};border-bottom:2px solid {T['border']};">
      <th style="padding:8px 14px;color:{T['txt_mute']};font-size:0.78rem;font-weight:600;text-align:center;">#</th>
      {_site_cols}
      <th style="padding:8px 14px;color:{T['txt_mute']};font-size:0.78rem;font-weight:600;text-align:center;">Ket</th>
      <th style="padding:8px 14px;color:{T['txt_mute']};font-size:0.78rem;font-weight:600;text-align:center;">Sz total</th>
    </tr>
  </thead>
  <tbody>{_state_rows}</tbody>
</table>
</div>
"""
        st.markdown(_tbl, unsafe_allow_html=True)
        st.markdown(
            f'<div class="caption-box" style="margin-top:0.6rem;">'
            f'States #1 and #4 (<b>|↑↓↑↓⟩</b> and <b>|↓↑↓↑⟩</b>) are the two '
            f'<b>Néel states</b> — every bond is antiparallel. They give the '
            f'diagonal entry −J in the Hamiltonian matrix (Section 3). '
            f'The remaining four are "domain-wall" states with two parallel and two '
            f'antiparallel bonds, giving diagonal 0.'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Section 1: Zeeman proof ─────────────────────────────────
    st.markdown('<p class="sec-lbl">2 · Zeeman Term &nbsp; H Σ Ŝ<sup>z</sup><sub>i</sub> |φ⟩ = 0</p>',
                unsafe_allow_html=True)

    with st.expander("Proof — the external field does not shift or split the Sz = 0 sector",
                     expanded=True):
        st.markdown(r"""
The Zeeman term couples the total spin projection to the external field $H$:

$$
\hat{H}_Z = H \sum_{i=0}^{3} \hat{S}^z_i = H\,\hat{S}^z_{\mathrm{total}},
\qquad
\hat{S}^z_{\mathrm{total}} = \frac{1}{2}(\hat{N}_{\uparrow} - \hat{N}_{\downarrow}).
$$

**Claim.** For any state $|\varphi\rangle$ in the $S_z = 0$ sector, $\hat{H}_Z|\varphi\rangle = 0$.

---

**Proof.**

*Step 1 — every basis state is an eigenstate of $\hat{S}^z_{\mathrm{total}}$ with eigenvalue 0.*

The $S_z = 0$ sector contains all configurations with exactly $k = 2$ spin-up and $k = 2$
spin-down electrons ($N_\uparrow = N_\downarrow = 2$). For any such basis state $|b\rangle$:

$$
\hat{S}^z_{\mathrm{total}}\,|b\rangle
= \tfrac{1}{2}(N_{\uparrow} - N_{\downarrow})\,|b\rangle
= \tfrac{1}{2}(2 - 2)\,|b\rangle = 0.
$$

*Step 2 — linearity extends the result to the whole sector.*

Any $|\varphi\rangle \in \mathcal{H}_{S_z=0}$ is a superposition $|\varphi\rangle = \sum_b c_b\,|b\rangle$,
so by linearity:

$$
\hat{H}_Z\,|\varphi\rangle
= H \sum_b c_b\;\hat{S}^z_{\mathrm{total}}\,|b\rangle
= H \sum_b c_b \cdot 0 = 0. \qquad \blacksquare
$$

**Physical consequence.** The field $H$ **neither shifts** the energies of $S_z = 0$ eigenstates
**nor mixes** them with other sectors — the subspace is an *invariant eigenspace* of $\hat{H}_Z$
with eigenvalue $0$. In contrast, the $S_z = \pm1$ and $S_z = \pm2$ sectors receive Zeeman
shifts $\mp H$ and $\mp 2H$ respectively (Section 4).
""")

    # ── Section 2: 6×6 Hamiltonian ─────────────────────────────
    st.markdown('<p class="sec-lbl">3 · Hamiltonian Construction — 6 × 6 matrix for Sz = 0</p>',
                unsafe_allow_html=True)

    with st.expander("6 × 6 Hamiltonian H/J in the Sz = 0 basis", expanded=True):
        st.markdown(r"""
With $N = 4$ sites and half-filling, the $S_z = 0$ sector has
$D = \binom{4}{2} = 6$ basis states. The Heisenberg exchange
$J\bigl[\tfrac{1}{2}(\hat{S}^+_i\hat{S}^-_j + \hat{S}^-_i\hat{S}^+_j)
+ \hat{S}^z_i\hat{S}^z_j\bigr]$
gives diagonal $\pm J/4$ per bond and off-diagonal $J/2$ when swapping antiparallel neighbours.
Because $\hat{H}_Z = 0$ on this sector, the full Hamiltonian is:

$$
\hat{H}\big|_{S_z=0} = J \cdot \mathbf{M}, \qquad
\mathbf{M} = \begin{pmatrix}
 0 & \tfrac{1}{2} & 0 & 0 & \tfrac{1}{2} & 0 \\
\tfrac{1}{2} & -1 & \tfrac{1}{2} & \tfrac{1}{2} & 0 & \tfrac{1}{2} \\
 0 & \tfrac{1}{2} & 0 & 0 & \tfrac{1}{2} & 0 \\
 0 & \tfrac{1}{2} & 0 & 0 & \tfrac{1}{2} & 0 \\
\tfrac{1}{2} & 0 & \tfrac{1}{2} & \tfrac{1}{2} & -1 & \tfrac{1}{2} \\
 0 & \tfrac{1}{2} & 0 & 0 & \tfrac{1}{2} & 0
\end{pmatrix}
$$

The two **Néel states** $|\!\uparrow\downarrow\uparrow\downarrow\rangle$ and
$|\!\downarrow\uparrow\downarrow\uparrow\rangle$ (rows 1 and 4) have all bonds antiparallel
giving diagonal $-J$. The four "domain-wall" states have equal parallel and antiparallel bonds
giving diagonal $0$.
""")
        z_labels = [_spin_label(s) for s in _sz0_basis]
        fig_mat = go.Figure(go.Heatmap(
            z=_H_unit,
            x=z_labels, y=z_labels,
            colorscale=[[0, ROSE], [0.5, "#FAF7F2"], [1, SAGE]],
            zmid=0,
            text=[[f"{v:.2g}" for v in row] for row in _H_unit],
            texttemplate="%{text}",
            showscale=True,
            colorbar=dict(title="H/J", tickfont=dict(color=T["txt_mute"], size=10)),
        ))
        fig_mat.update_layout(
            paper_bgcolor=T["page_bg"], plot_bgcolor=T["plot_bg"],
            height=340, margin=dict(l=10, r=10, t=30, b=10),
            xaxis=dict(tickfont=dict(color=T["txt_main"], size=12)),
            yaxis=dict(tickfont=dict(color=T["txt_main"], size=12), autorange="reversed"),
        )
        st.plotly_chart(fig_mat, use_container_width=True)

    # ── Section 3: Eigenenergies ────────────────────────────────
    st.markdown('<p class="sec-lbl">4 · Eigenenergies and Sector Dimensions</p>',
                unsafe_allow_html=True)

    with st.expander("Spectrum of all Sz sectors at H = 0", expanded=True):
        st.markdown(r"""
Because $[\hat{H}_J,\,\hat{S}^z_{\mathrm{total}}] = 0$, the exchange Hamiltonian is
block-diagonal in $S_z$. Diagonalising each block independently:

| Sector $S_z$ | Dimension | Eigenvalues of $\hat{H}/J$ at $H = 0$ |
|:---:|:---:|:---|
| $+2$ | 1 | $+1$ |
| $+1$ | 4 | $-1,\ 0,\ 0,\ +1$ |
| $\;0$ | 6 | $-2,\ -1,\ 0,\ 0,\ 0,\ +1$ |
| $-1$ | 4 | $-1,\ 0,\ 0,\ +1$ |
| $-2$ | 1 | $+1$ |

The global ground state at $H = 0$ is the **singlet** in $S_z = 0$ with $E_0 = -2J$.
This is lower than the classical Néel energy $E_{\rm Néel} = -J$:
quantum fluctuations lower the energy by a factor of 2.
""")
        evals_0 = np.sort(np.linalg.eigvalsh(build_heisenberg(1.0, _sz0_basis)))
        evals_1 = np.sort(np.linalg.eigvalsh(build_heisenberg(1.0, _sz1_basis)))
        E2_0    = float(build_heisenberg(1.0, _sz2_basis)[0, 0])

        def _fmt(arr):
            return ", ".join(f"{v:.4g}" for v in arr)

        c0, c1, c2 = st.columns(3)
        with c0:
            st.markdown(f'<div class="z-card"><b>Sz = 0</b>&nbsp;<small style="color:{T["txt_mute"]}">D=6</small>'
                        f'<br><code>{_fmt(evals_0)}</code></div>', unsafe_allow_html=True)
        with c1:
            st.markdown(f'<div class="z-card"><b>Sz = ±1</b>&nbsp;<small style="color:{T["txt_mute"]}">D=4</small>'
                        f'<br><code>{_fmt(evals_1)}</code></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="z-card"><b>Sz = ±2</b>&nbsp;<small style="color:{T["txt_mute"]}">D=1</small>'
                        f'<br><code>{E2_0:.4g}</code></div>', unsafe_allow_html=True)

    # ── Section 4: Energy levels vs H ──────────────────────────
    st.markdown('<p class="sec-lbl">5 · Eigenenergies and Limiting Regimes</p>',
                unsafe_allow_html=True)

    with st.expander("Limiting cases H = 0 and J = 0", expanded=True):
        st.markdown(r"""
**Case 1 — $H = 0$ (pure Heisenberg).**
Every $S_z$ projection of a given $S_{\rm total}$ multiplet is degenerate.
Ground state: the **singlet** ($S_{\rm total} = 0$, $S_z = 0$), $E_0 = -2J$.
This is below the classical Néel state ($E_{\rm Néel} = -J$) — quantum fluctuations lower the energy.

**Case 2 — $J = 0$ (pure Zeeman).**
Without exchange the field alone governs the ground state.
For any $H > 0$ the fully polarised state $|\!\uparrow\uparrow\uparrow\uparrow\rangle$ ($S_z = +2$)
is lowest with $E = -2H$. There is no staircase — the system jumps straight to full polarisation.
""")

    with st.expander("General case H, J > 0 — energy levels vs field", expanded=True):
        st.markdown(r"""
The Zeeman term adds $-H \cdot S_z^{\rm total}$ uniformly to each sector:
$$E_n(S_z, H) = E_n^{(J)} - H\,S_z^{\rm total}.$$
The $S_z = 0$ levels are **field-independent** (horizontal). The $S_z = +1$ block shifts
down by $H$; $S_z = +2$ shifts down by $2H$.
""")
        col_j1, col_h1 = st.columns(2)
        with col_j1:
            J_val = st.slider("Exchange coupling J", 0.1, 3.0, 1.0, 0.05, key="J_diag")
        with col_h1:
            H_max = st.slider("Max field H", 0.5, 6.0, 3.0, 0.1, key="H_diag")

        H_arr = np.linspace(0, H_max, 400)
        ev0 = np.sort(np.linalg.eigvalsh(build_heisenberg(J_val, _sz0_basis)))
        ev1 = np.sort(np.linalg.eigvalsh(build_heisenberg(J_val, _sz1_basis)))
        evm1 = np.sort(np.linalg.eigvalsh(build_heisenberg(J_val, _szm1_basis)))
        E2J  = float(build_heisenberg(J_val, _sz2_basis)[0, 0])

        fig_e = go.Figure()
        for i, E in enumerate(ev0):
            fig_e.add_trace(go.Scatter(
                x=H_arr, y=np.full_like(H_arr, E), mode="lines",
                line=dict(color=SAGE, width=1.8),
                name="Sz = 0", legendgroup="sz0", showlegend=(i == 0),
            ))
        for i, E in enumerate(ev1):
            fig_e.add_trace(go.Scatter(
                x=H_arr, y=E - H_arr, mode="lines",
                line=dict(color=AMBER, width=1.8),
                name="Sz = +1", legendgroup="sz1", showlegend=(i == 0),
            ))
        fig_e.add_trace(go.Scatter(
            x=H_arr, y=E2J - 2 * H_arr, mode="lines",
            line=dict(color=SLATE, width=2.2, dash="dot"), name="Sz = +2",
        ))
        for i, E in enumerate(evm1):
            fig_e.add_trace(go.Scatter(
                x=H_arr, y=E + H_arr, mode="lines",
                line=dict(color=ROSE, width=1.2, dash="dash"),
                name="Sz = −1", legendgroup="szm1", showlegend=(i == 0),
            ))
        fig_e.add_trace(go.Scatter(
            x=H_arr, y=E2J + 2 * H_arr, mode="lines",
            line=dict(color=DARK_BRN, width=1.2, dash="dash"), name="Sz = −2",
        ))
        fig_e.update_layout(
            paper_bgcolor=T["page_bg"], plot_bgcolor=T["plot_bg"],
            height=420, margin=dict(l=55, r=20, t=30, b=45),
            xaxis=dict(title="Field H", tickfont=dict(color=T["txt_mute"], size=10),
                       title_font=dict(color=T["txt_mute"])),
            yaxis=dict(title="Energy E", tickfont=dict(color=T["txt_mute"], size=10),
                       title_font=dict(color=T["txt_mute"])),
            legend=dict(bgcolor=T["card_bg"], bordercolor=T["border"],
                        font=dict(color=T["txt_main"], size=11)),
            hoverlabel=dict(bgcolor=T["hover_bg"], font=dict(color=T["hover_txt"])),
        )
        st.plotly_chart(fig_e, use_container_width=True)

    # ── Section 5: Magnetization staircase ─────────────────────
    st.markdown('<p class="sec-lbl">6 · Magnetization Staircase and Critical Fields H<sub>c</sub></p>',
                unsafe_allow_html=True)

    with st.expander("Ground-state Sz vs H — the staircase", expanded=True):
        st.markdown(r"""
**Derivation of the critical fields:**

- $E_{\min}(S_z=0) = -2J$ (field-independent)
- $E_{\min}(S_z=+1,\,H) = -J - H$
- $E(S_z=+2,\,H) = J - 2H$

$$
H_{c1}:\ -J - H_{c1} = -2J \;\Rightarrow\; \boxed{H_{c1} = J}
\qquad
H_{c2}:\ J - 2H_{c2} = -J - H_{c2} \;\Rightarrow\; \boxed{H_{c2} = 2J}
$$

| Field range | Ground sector | $\langle S_z^{\rm total}\rangle$ |
|:---:|:---:|:---:|
| $0 \le H < J$ | $S_z = 0$ | $0$ |
| $J \le H < 2J$ | $S_z = +1$ | $+1$ |
| $H \ge 2J$ | $S_z = +2$ (full saturation) | $+2$ |
""")
        col_j2, _ = st.columns([1, 2])
        with col_j2:
            J2 = st.slider("Exchange coupling J", 0.1, 3.0, 1.0, 0.05, key="J_stair")

        Hc1 = J2
        Hc2 = 2 * J2
        H_plot = np.linspace(0, 3 * J2 + 0.2, 800)

        ev0_2 = np.sort(np.linalg.eigvalsh(build_heisenberg(J2, _sz0_basis)))
        ev1_2 = np.sort(np.linalg.eigvalsh(build_heisenberg(J2, _sz1_basis)))
        E2_2  = float(build_heisenberg(J2, _sz2_basis)[0, 0])

        gs_e  = np.minimum(
            np.minimum(ev0_2[0] * np.ones_like(H_plot), ev1_2[0] - H_plot),
            E2_2 - 2 * H_plot,
        )
        sz_gs = np.where(
            np.isclose(gs_e, ev0_2[0]), 0,
            np.where(np.isclose(gs_e, ev1_2[0] - H_plot), 1, 2),
        )

        fig_s = go.Figure()
        for sz_v, x0, x1, col in [
            (0, 0,    Hc1,           "#D8EFD8"),
            (1, Hc1,  Hc2,           "#FFF0D0"),
            (2, Hc2,  3*J2 + 0.2,   "#D0E4F0"),
        ]:
            fig_s.add_vrect(x0=x0, x1=x1, fillcolor=col, opacity=0.25,
                            layer="below", line_width=0)
            fig_s.add_annotation(
                x=(x0 + min(x1, 3*J2+0.2)) / 2, y=2.35,
                text=f"Sz = {sz_v}", showarrow=False,
                font=dict(color=T["txt_mute"], size=11),
            )
        for xc, lbl in [(Hc1, "H<sub>c1</sub> = J"), (Hc2, "H<sub>c2</sub> = 2J")]:
            fig_s.add_vline(x=xc, line_dash="dot", line_color=T["txt_mute"], line_width=1.4)
            fig_s.add_annotation(x=xc, y=-0.3, text=lbl, showarrow=False,
                                 font=dict(color=T["txt_mute"], size=10), xanchor="center")
        fig_s.add_trace(go.Scatter(
            x=H_plot, y=sz_gs.astype(float),
            mode="lines", line=dict(color=SAGE, width=3),
            name="⟨Sz⟩ ground state",
        ))
        fig_s.update_layout(
            paper_bgcolor=T["page_bg"], plot_bgcolor=T["plot_bg"],
            height=360, margin=dict(l=55, r=20, t=30, b=55),
            xaxis=dict(title="External field H", tickfont=dict(color=T["txt_mute"], size=10),
                       title_font=dict(color=T["txt_mute"])),
            yaxis=dict(title="⟨Sz⟩ total", tickvals=[0, 1, 2],
                       tickfont=dict(color=T["txt_mute"], size=11),
                       title_font=dict(color=T["txt_mute"]), range=[-0.45, 2.65]),
            hoverlabel=dict(bgcolor=T["hover_bg"], font=dict(color=T["hover_txt"])),
            legend=dict(bgcolor=T["card_bg"], bordercolor=T["border"],
                        font=dict(color=T["txt_main"], size=11)),
        )
        st.plotly_chart(fig_s, use_container_width=True)
        st.markdown(
            f'<div class="caption-box">'
            f'For J = {J2:.2f}: &nbsp;'
            f'<b>H<sub>c1</sub> = {Hc1:.2f}</b> (Sz: 0 → 1)&nbsp;|&nbsp;'
            f'<b>H<sub>c2</sub> = {Hc2:.2f}</b> (Sz: 1 → 2, full saturation). '
            f'The Sz = 0 energies are flat because Ĥ<sub>Z</sub>|φ⟩ = 0 on that sector.'
            f'</div>',
            unsafe_allow_html=True,
        )
