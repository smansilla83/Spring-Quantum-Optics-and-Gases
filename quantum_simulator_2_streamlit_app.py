import streamlit as st
import plotly.graph_objects as go
import numpy as np

# ── Color palette (electric blue + red, black bg) ──────────────
SURFACE_COLORSCALE = [
    [0.00, "#03091C"],
    [0.25, "#082B72"],
    [0.55, "#1565D8"],
    [0.80, "#2BA5E8"],
    [1.00, "#9CDBFF"],
]

RED_SITE  = "#E82A10"
RED_EDGE  = "#FF7050"
BOND_COL  = "rgba(90, 200, 255, 0.55)"

PAGE_BG   = "#000000"
CARD_BG   = "#07101F"
BORDER    = "#0E2244"
CYAN      = "#4FC8F0"
WHITE_GLO = "#C8EEFF"
TXT_MAIN  = "#D4ECFF"
TXT_MUTED = "#4D7FA0"

# ── Page config ────────────────────────────────────────────────
st.set_page_config(page_title="Hubbard Model Simulator", layout="wide")

st.markdown(f"""
<style>
  .stApp {{
    background-color: {PAGE_BG};
    color: {TXT_MAIN};
    font-family: 'Inter', 'Segoe UI', sans-serif;
  }}
  header[data-testid="stHeader"] {{ background: transparent; }}

  /* Hero */
  .hero {{
    background: linear-gradient(135deg, {CARD_BG} 0%, #050E22 100%);
    border: 1px solid {BORDER};
    border-radius: 18px;
    padding: 2rem 2.6rem 1.7rem;
    margin-bottom: 1.4rem;
  }}
  .hero h1 {{
    font-size: 2.3rem;
    font-weight: 700;
    background: linear-gradient(90deg, {CYAN} 0%, {WHITE_GLO} 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 0.45rem;
    letter-spacing: 0.2px;
  }}
  .hero p {{
    color: {TXT_MUTED};
    font-size: 0.96rem;
    line-height: 1.7;
    margin: 0;
  }}

  /* Metric cards */
  .metric-row {{
    display: flex;
    gap: 0.85rem;
    margin: 0.9rem 0 1.1rem;
  }}
  .metric-card {{
    flex: 1;
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 0.85rem 1rem;
    text-align: center;
  }}
  .metric-card .lbl {{
    font-size: 0.70rem;
    color: {TXT_MUTED};
    text-transform: uppercase;
    letter-spacing: 1.3px;
  }}
  .metric-card .val {{
    font-size: 1.95rem;
    font-weight: 800;
    color: {CYAN};
    line-height: 1.15;
  }}
  .metric-card .sub {{
    font-size: 0.75rem;
    color: {TXT_MUTED};
  }}

  /* Section label */
  .sec-lbl {{
    font-size: 0.75rem;
    color: {TXT_MUTED};
    text-transform: uppercase;
    letter-spacing: 1.6px;
    margin: 1.3rem 0 0.45rem;
    border-left: 2px solid #1565D8;
    padding-left: 0.6rem;
  }}

  /* Slider */
  label p, .stSlider label p {{
    color: {TXT_MUTED} !important;
  }}

  /* Checkboxes */
  .stCheckbox label p {{
    color: {TXT_MUTED} !important;
    font-size: 0.88rem !important;
  }}

  /* Caption */
  .caption-box {{
    background: {CARD_BG};
    border-left: 3px solid #1565D8;
    border-radius: 0 8px 8px 0;
    padding: 0.7rem 1.1rem;
    color: {TXT_MUTED};
    font-size: 0.84rem;
    line-height: 1.65;
    margin-top: 0.6rem;
  }}
</style>
""", unsafe_allow_html=True)

# ── Hero ───────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>Hubbard Model Quantum Simulator</h1>
  <p>
    Electrons hop across a D&times;D square lattice with amplitude <em>t</em>.
    On-site Coulomb repulsion <em>U</em> acts whenever two spin-opposite electrons
    share the same site. The wavy surface represents the quantum potential landscape.
    <br><strong>Drag to rotate &nbsp;&middot;&nbsp; Scroll to zoom &nbsp;&middot;&nbsp; Hover a site for info.</strong>
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

N     = D * D
bonds = 2 * D * (D - 1)

# Hilbert dimension — display as 4^N for large N to avoid overflow display
hilbert_str = f"{4**N:,}" if N <= 7 else f"4<sup>{N}</sup>"

# ── Metric cards ───────────────────────────────────────────────
st.markdown(f"""
<div class="metric-row">
  <div class="metric-card">
    <div class="lbl">Lattice sites</div>
    <div class="val">{N}</div>
    <div class="sub">{D} × {D} grid</div>
  </div>
  <div class="metric-card">
    <div class="lbl">Hopping bonds</div>
    <div class="val">{bonds}</div>
    <div class="sub">nearest-neighbour</div>
  </div>
  <div class="metric-card">
    <div class="lbl">Hilbert dim.</div>
    <div class="val">{hilbert_str}</div>
    <div class="sub">4<sup>N</sup> states</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── 3-D figure ─────────────────────────────────────────────────
def site_z(col, row, amp=0.28, offset=0.14):
    return amp * (np.cos(np.pi * col) + np.cos(np.pi * row)) + offset


def build_figure(D, show_labels, show_bonds):
    amp = 0.28
    padding = 0.55
    res = max(50, D * 14)

    xs = np.linspace(-padding, D - 1 + padding, res)
    ys = np.linspace(-padding, D - 1 + padding, res)
    X, Y = np.meshgrid(xs, ys)
    Z = amp * (np.cos(np.pi * X) + np.cos(np.pi * Y))

    fig = go.Figure()

    # Surface
    fig.add_trace(go.Surface(
        x=X, y=Y, z=Z,
        colorscale=SURFACE_COLORSCALE,
        showscale=False,
        opacity=0.93,
        lighting=dict(
            ambient=0.30,
            diffuse=0.65,
            specular=1.6,
            roughness=0.12,
            fresnel=0.5,
        ),
        lightposition=dict(x=200, y=400, z=600),
        hoverinfo="skip",
    ))

    # Bonds
    if show_bonds:
        bx, by, bz = [], [], []
        for row in range(D):
            for col in range(D):
                z0 = site_z(col, row, amp, offset=0.05)
                if col < D - 1:
                    z1 = site_z(col + 1, row, amp, offset=0.05)
                    bx += [col, col + 1, None]
                    by += [row, row,      None]
                    bz += [z0,  z1,       None]
                if row < D - 1:
                    z1 = site_z(col, row + 1, amp, offset=0.05)
                    bx += [col, col,      None]
                    by += [row, row + 1,  None]
                    bz += [z0,  z1,       None]
        fig.add_trace(go.Scatter3d(
            x=bx, y=by, z=bz,
            mode="lines",
            line=dict(color=BOND_COL, width=5),
            hoverinfo="none",
            showlegend=False,
        ))

    # Sites
    sx, sy, sz, labels, hovers = [], [], [], [], []
    for row in range(D):
        for col in range(D):
            idx = row * D + col
            sx.append(col)
            sy.append(row)
            sz.append(site_z(col, row, amp))
            labels.append(str(idx))
            hovers.append(f"Site {idx}  |  ({col}, {row})")

    marker_size = max(8, 24 - D * 2)
    font_size   = max(7, 14 - D)

    fig.add_trace(go.Scatter3d(
        x=sx, y=sy, z=sz,
        mode="markers+text" if show_labels else "markers",
        marker=dict(
            size=marker_size,
            color=RED_SITE,
            symbol="circle",
            line=dict(color=RED_EDGE, width=2.5),
            opacity=1.0,
        ),
        text=labels if show_labels else None,
        textposition="middle center",
        textfont=dict(color="white", size=font_size, family="Arial Black"),
        hovertemplate="<b>%{customdata}</b><extra></extra>",
        customdata=hovers,
        showlegend=False,
    ))

    fig.update_layout(
        paper_bgcolor="#000000",
        plot_bgcolor="#000000",
        scene=dict(
            bgcolor="#000000",
            aspectmode="manual",
            aspectratio=dict(x=1, y=1, z=0.45),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            camera=dict(
                eye=dict(x=1.55, y=-1.55, z=1.05),
                up=dict(x=0, y=0, z=1),
            ),
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=560,
    )
    return fig


fig = build_figure(D, show_labels, show_bonds)
st.plotly_chart(fig, use_container_width=True)

# ── Caption ────────────────────────────────────────────────────
st.markdown(
    f'<div class="caption-box">'
    f'<b>Red spheres</b> are the {N} lattice sites (numbered 0–{N-1}). '
    f'<b>Blue edges</b> represent nearest-neighbour hopping bonds with amplitude <em>t</em>. '
    f'The electric-blue surface encodes the quantum potential landscape — '
    f'bright crests and dark troughs reflect alternating site energies. '
    f'On-site repulsion <em>U</em> acts at each red node when doubly occupied.'
    f'</div>',
    unsafe_allow_html=True,
)
