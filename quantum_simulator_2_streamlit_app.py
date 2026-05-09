import streamlit as st
import plotly.graph_objects as go

# ── Earthy palette (extracted from swatch image) ───────────────
SAGE      = "#7D8B5A"   # top-left  green
AMBER     = "#C9983A"   # top-3rd   golden
BUTTER    = "#C9BB68"   # mid-left  pale yellow
STEEL     = "#7A9DAC"   # mid-2nd   dusty blue
ROSE      = "#C4907E"   # mid-3rd   dusty rose
OFF_WHITE = "#E5E0D8"   # mid-right cream
DARK_BRN  = "#4E3428"   # btm-left  umber
MOSS      = "#9DA872"   # btm-2nd   muted sage
SLATE     = "#3D5F78"   # btm-3rd   slate blue
TERRA     = "#A84E3C"   # btm-right terracotta
CREAM     = "#CEC9BC"   # top-2nd   light beige

PAPER     = "#F2EBE0"   # plot canvas (warm parchment)
PAGE_BG   = "#1C1814"   # page background
CARD_BG   = "#252018"   # card background
BORDER    = "#3C3228"   # border
TXT_MAIN  = OFF_WHITE
TXT_MUTE  = "#8A7860"

# Colour scheme presets — bipartite sublattice colouring
SCHEMES = {
    "Sage & Dusty Rose":    {"even": SAGE,  "odd": ROSE,  "bond": "#9A7E60"},
    "Amber & Slate":        {"even": AMBER, "odd": SLATE, "bond": "#8A7050"},
    "Terracotta & Butter":  {"even": TERRA, "odd": BUTTER,"bond": "#9A8060"},
    "Steel & Moss":         {"even": STEEL, "odd": MOSS,  "bond": "#8A7A60"},
}

# ── Page config ────────────────────────────────────────────────
st.set_page_config(page_title="Hubbard Model Simulator", layout="wide")

st.markdown(f"""
<style>
  .stApp {{
    background-color: {PAGE_BG};
    color: {TXT_MAIN};
    font-family: 'Georgia', serif;
  }}
  header[data-testid="stHeader"] {{ background: transparent; }}

  .hero {{
    background: linear-gradient(135deg, {CARD_BG} 0%, #1F1B13 100%);
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 1.9rem 2.5rem 1.5rem;
    margin-bottom: 1.2rem;
  }}
  .hero h1 {{
    font-size: 2.2rem;
    font-weight: 700;
    color: {AMBER};
    margin: 0 0 0.4rem;
    letter-spacing: 0.2px;
  }}
  .hero p {{
    color: {TXT_MUTE};
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
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 0.82rem 1rem;
    text-align: center;
  }}
  .metric-card .lbl {{
    font-size: 0.69rem;
    color: {TXT_MUTE};
    text-transform: uppercase;
    letter-spacing: 1.3px;
  }}
  .metric-card .val {{
    font-size: 1.85rem;
    font-weight: 700;
    color: {AMBER};
    line-height: 1.15;
  }}
  .metric-card .sub {{
    font-size: 0.73rem;
    color: {TXT_MUTE};
  }}

  .sec-lbl {{
    font-size: 0.72rem;
    color: {TXT_MUTE};
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin: 1.2rem 0 0.4rem;
    border-left: 2px solid {SAGE};
    padding-left: 0.6rem;
  }}

  label p, .stSlider label p,
  .stCheckbox label p, .stSelectbox label p {{
    color: {TXT_MUTE} !important;
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
    color: {TXT_MUTE};
  }}
  .swatch {{
    width: 15px;
    height: 15px;
    border-radius: 50%;
    display: inline-block;
    border: 1.5px solid rgba(255,255,255,0.15);
  }}
  .bond-swatch {{
    display: inline-block;
    width: 22px;
    height: 3px;
    border-radius: 2px;
  }}

  .caption-box {{
    background: {CARD_BG};
    border-left: 3px solid {SAGE};
    border-radius: 0 8px 8px 0;
    padding: 0.7rem 1.1rem;
    color: {TXT_MUTE};
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
    On-site Coulomb repulsion <em>U</em> penalises double occupancy at each site.
    The two colours show the <strong>bipartite sublattice structure</strong> — a key
    symmetry driving antiferromagnetism at half-filling.
    &nbsp;<strong>Hover a site for details.</strong>
  </p>
</div>
""", unsafe_allow_html=True)

# ── Controls ───────────────────────────────────────────────────
st.markdown('<p class="sec-lbl">Lattice Configuration</p>', unsafe_allow_html=True)

col_a, col_b, col_c, col_d = st.columns([3, 2, 1, 1])
with col_a:
    D = st.slider("Lattice dimension  D × D", min_value=2, max_value=8, value=4, step=1)
with col_b:
    scheme_name = st.selectbox("Colour scheme", list(SCHEMES.keys()), index=0)
with col_c:
    show_labels = st.checkbox("Site labels", value=True)
with col_d:
    show_bonds = st.checkbox("Bonds", value=True)

scheme = SCHEMES[scheme_name]
N      = D * D
n_bonds = 2 * D * (D - 1)
hilbert_str = f"{4**N:,}" if N <= 7 else f"4<sup>{N}</sup>"

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

# ── Inline legend ──────────────────────────────────────────────
parts = scheme_name.split(" & ")
lbl_A = parts[0].strip()
lbl_B = parts[1].strip() if len(parts) > 1 else "B sublattice"

st.markdown(f"""
<div class="legend">
  <div class="legend-item">
    <span class="swatch" style="background:{scheme['even']};"></span>
    <span>{lbl_A} &mdash; A sublattice&nbsp;(row+col even)</span>
  </div>
  <div class="legend-item">
    <span class="swatch" style="background:{scheme['odd']};"></span>
    <span>{lbl_B} &mdash; B sublattice&nbsp;(row+col odd)</span>
  </div>
  <div class="legend-item">
    <span class="bond-swatch" style="background:{scheme['bond']};"></span>
    <span>Hopping bond &nbsp;<em>t</em></span>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Flat 2-D lattice ───────────────────────────────────────────
def build_figure(D, scheme, show_labels, show_bonds):
    fig = go.Figure()

    # Bonds
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
            line=dict(color=scheme["bond"], width=3.5),
            hoverinfo="none",
            showlegend=False,
        ))

    # Sites — one trace per sublattice so colours are distinct
    marker_size = max(24, 70 - D * 7)
    font_size   = max(8, 18 - D)

    for parity, sub_label in [(0, "A"), (1, "B")]:
        color = scheme["even"] if parity == 0 else scheme["odd"]
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
                        f"Grid position: ({col}, {row})<br>"
                        f"Sublattice: {sub_label}"
                    )

        fig.add_trace(go.Scatter(
            x=sx, y=sy,
            mode="markers+text" if show_labels else "markers",
            name=f"Sublattice {sub_label}",
            marker=dict(
                size=marker_size,
                color=color,
                symbol="circle",
                line=dict(color=DARK_BRN, width=1.8),
                opacity=0.93,
            ),
            text=texts if show_labels else None,
            textposition="middle center",
            textfont=dict(color=OFF_WHITE, size=font_size, family="Arial Black"),
            hovertemplate="%{customdata}<extra></extra>",
            customdata=hovers,
            showlegend=False,
        ))

    pad = 0.85
    fig.update_layout(
        paper_bgcolor=PAGE_BG,
        plot_bgcolor=PAPER,
        xaxis=dict(
            range=[-pad, D - 1 + pad],
            showgrid=False, zeroline=False, showticklabels=False,
            scaleanchor="y", scaleratio=1,
            fixedrange=True,
        ),
        yaxis=dict(
            range=[-pad, D - 1 + pad],
            showgrid=False, zeroline=False, showticklabels=False,
            fixedrange=True,
        ),
        margin=dict(l=24, r=24, t=24, b=24),
        height=520,
        hoverlabel=dict(
            bgcolor=CARD_BG,
            bordercolor=BORDER,
            font=dict(color=TXT_MAIN, size=13, family="Georgia"),
        ),
        dragmode=False,
    )
    return fig


fig = build_figure(D, scheme, show_labels, show_bonds)
st.plotly_chart(fig, use_container_width=True)

# ── Caption ────────────────────────────────────────────────────
st.markdown(
    f'<div class="caption-box">'
    f'<b>Bipartite structure</b>: the square lattice splits into two interlocking '
    f'sublattices A and B — coloured differently above. '
    f'At half-filling with strong repulsion <em>U &gg; t</em>, electrons localise '
    f'with opposite spins on A and B sites, producing <em>antiferromagnetic order</em>. '
    f'Hover any site to inspect its index and sublattice.'
    f'</div>',
    unsafe_allow_html=True,
)
