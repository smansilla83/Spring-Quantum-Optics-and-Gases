import math
from itertools import combinations
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

# Fixed bipartite colour scheme (sage A / dusty-rose B)
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

# Mode toggle — must come before CSS so re-run picks up new value
_, col_toggle = st.columns([6, 1])
with col_toggle:
    dark_mode = st.toggle("Dark mode", value=False)

T = THEMES["dark"] if dark_mode else THEMES["light"]

# ── CSS (injected after mode is known) ────────────────────────
st.markdown(f"""
<style>
  .stApp {{
    background-color: {T['page_bg']};
    color: {T['txt_main']};
    font-family: 'Georgia', serif;
  }}
  header[data-testid="stHeader"] {{ background: transparent; }}

  /* push the toggle to look like a top-right control */
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
</style>
""", unsafe_allow_html=True)

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

# ── Controls ───────────────────────────────────────────────────
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
_hval = 4 ** N
if _hval < 1_000_000_000:
    hilbert_str = f"{_hval:,}"
else:
    _exp = int(math.log10(_hval))
    _coeff = _hval / (10 ** _exp)
    hilbert_str = f"{_coeff:.2f} &times; 10<sup>{_exp}</sup>"

# ── Metric cards ───────────────────────────────────────────────
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


# ── 2-D lattice figure ─────────────────────────────────────────
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
            x=bx, y=by,
            mode="lines",
            line=dict(color=SCHEME["bond"], width=3.5),
            hoverinfo="none",
            showlegend=False,
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
                    sx.append(col)
                    sy.append(row)
                    texts.append(str(idx))
                    hovers.append(
                        f"<b>Site {idx}</b><br>"
                        f"Position: ({col}, {row})<br>"
                        f"Sublattice: {sub_label}"
                    )

        fig.add_trace(go.Scatter(
            x=sx, y=sy,
            mode="markers+text" if show_labels else "markers",
            marker=dict(
                size=marker_size,
                color=color,
                symbol="circle",
                line=dict(color=DARK_BRN, width=1.8),
                opacity=0.93,
            ),
            text=texts if show_labels else None,
            textposition="middle center",
            textfont=dict(color=T["label_txt"], size=font_size, family="Arial Black"),
            hovertemplate="%{customdata}<extra></extra>",
            customdata=hovers,
            showlegend=False,
        ))

    pad = 0.85
    fig.update_layout(
        paper_bgcolor=T["page_bg"],
        plot_bgcolor=T["plot_bg"],
        xaxis=dict(
            range=[-pad, D - 1 + pad],
            showgrid=False, zeroline=False, showticklabels=False,
            scaleanchor="y", scaleratio=1, fixedrange=True,
        ),
        yaxis=dict(
            range=[-pad, D - 1 + pad],
            showgrid=False, zeroline=False, showticklabels=False,
            fixedrange=True,
        ),
        margin=dict(l=24, r=24, t=24, b=24),
        height=520,
        hoverlabel=dict(
            bgcolor=T["hover_bg"],
            bordercolor=T["border"],
            font=dict(color=T["hover_txt"], size=13, family="Georgia"),
        ),
        dragmode=False,
    )
    return fig


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

# ── Sz = 0 Subspace ────────────────────────────────────────────
st.markdown('<p class="sec-lbl" style="margin-top:2rem;">S<sub>z</sub> = 0 Subspace</p>',
            unsafe_allow_html=True)

dim_sz0 = math.comb(2 * N, N)

# Dimension formula card
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

# ── Breakdown table by k (white) ───────────────────────────────
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

# ── N = 2 example ───────────────────────────────────────────────
with st.expander("Example: Sz = 0 states for N = 2 sites", expanded=True):
    st.markdown(
        f'<div class="caption-box" style="margin-bottom:0.9rem;">'
        f'A 2-site chain (N = 2) is the simplest case. '
        f'The Sz = 0 sector has C(4, 2) = <b>6 states</b>, grouped by '
        f'k = N<sub>↑</sub> = N<sub>↓</sub> below. '
        f'Each node shows the occupation of one lattice site.'
        f'</div>',
        unsafe_allow_html=True,
    )

    ex_states: dict = {}
    for idx, k2, occ in gen_states(2):
        ex_states.setdefault(k2, []).append((idx, occ))

    def mini_card(state_idx, occ):
        s0, s1 = badge_html(occ[0], size=38), badge_html(occ[1], size=38)
        ket = f"|{BADGE_SYM[occ[0]]}, {BADGE_SYM[occ[1]]}⟩"
        return (
            f'<div style="display:flex;flex-direction:column;align-items:center;'
            f'background:{T["card_bg"]};border:1px solid {T["border"]};'
            f'border-radius:10px;padding:10px 14px;min-width:130px;">'
            f'<div style="font-size:0.64rem;color:{T["txt_mute"]};margin-bottom:5px;">'
            f'state {state_idx}</div>'
            f'<div style="display:flex;align-items:center;gap:6px;">'
            f'{s0}'
            f'<div style="width:22px;height:2px;background:{T["border"]};flex-shrink:0;"></div>'
            f'{s1}</div>'
            f'<div style="font-size:0.9rem;color:{T["txt_main"]};margin-top:6px;'
            f'font-family:Georgia,serif;">{ket}</div>'
            f'<div style="display:flex;gap:28px;margin-top:3px;">'
            f'<span style="font-size:0.62rem;color:{T["txt_mute"]};">site 0</span>'
            f'<span style="font-size:0.62rem;color:{T["txt_mute"]};">site 1</span>'
            f'</div></div>'
        )

    for k2 in sorted(ex_states):
        ck = math.comb(2, k2)
        st.markdown(
            f'<div style="font-size:0.72rem;color:{T["txt_mute"]};text-transform:uppercase;'
            f'letter-spacing:1px;border-bottom:1px solid {T["border"]};'
            f'padding:4px 0 2px;margin:10px 0 6px;">'
            f'k = {k2} &nbsp;(N<sub>↑</sub> = N<sub>↓</sub> = {k2})'
            f'&ensp;&middot;&ensp; C(2,{k2})² = {ck}² = {ck*ck} state'
            f'{"s" if ck*ck != 1 else ""}</div>',
            unsafe_allow_html=True,
        )
        cards = "".join(mini_card(idx, occ) for idx, occ in ex_states[k2])
        st.markdown(
            f'<div style="display:flex;flex-wrap:wrap;gap:10px;margin-bottom:4px;">'
            f'{cards}</div>',
            unsafe_allow_html=True,
        )

# ── Basis state visualization ──────────────────────────────────
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

if N <= 4:
    # ── Badge grid (all states, grouped by k) ──────────────────
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
    # ── Plotly heatmap (sampled) ────────────────────────────────
    MAX_S = 200
    z_data, x_labs, k_starts = [], [], {}
    for idx, k, occ in gen_states(N, limit=MAX_S):
        if k not in k_starts:
            k_starts[k] = idx
        z_data.append(occ)
        x_labs.append(str(idx))

    z_T = [list(col) for col in zip(*z_data)]
    custom_T = [[BADGE_SYM[v] for v in row] for row in z_T]

    cs = [
        [0.000, "#D8D0C4"], [0.249, "#D8D0C4"],
        [0.250, SAGE],      [0.499, SAGE],
        [0.500, ROSE],      [0.749, ROSE],
        [0.750, SLATE],     [1.000, SLATE],
    ]

    fig_h = go.Figure(go.Heatmap(
        z=z_T,
        x=x_labs,
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
        height=50 * N + 80,
        margin=dict(l=65, r=20, t=35, b=45),
        xaxis=dict(
            title=dict(text="State index", font=dict(color=T["txt_mute"], size=11)),
            showticklabels=len(z_data) <= 40,
            tickfont=dict(color=T["txt_mute"], size=9),
        ),
        yaxis=dict(tickfont=dict(color=T["txt_main"], size=10), autorange="reversed"),
        hoverlabel=dict(
            bgcolor=T["hover_bg"], bordercolor=T["border"],
            font=dict(color=T["hover_txt"], size=12),
        ),
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
