import math
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
