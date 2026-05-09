import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── Earthy palette ──────────────────────────────────────────────
CLAY       = "#C17F59"   # site nodes
SAGE       = "#7B9E82"   # hopping bonds
SAND       = "#D4B896"   # light text / labels
BARK       = "#4A3728"   # figure background
PARCHMENT  = "#F5EDD6"   # figure face
MOSS       = "#4A6741"   # accent dark green
UMBER      = "#6B4E37"   # border tones

PAGE_BG    = "#1E1A16"
CARD_BG    = "#2A2420"
TEXT_MAIN  = "#F0E6D3"
TEXT_MUTED = "#A89478"

st.set_page_config(page_title="Hubbard Model Simulator", layout="centered")

# ── Global CSS ───────────────────────────────────────────────────
st.markdown(f"""
<style>
  /* Page background */
  .stApp {{
    background-color: {PAGE_BG};
    color: {TEXT_MAIN};
    font-family: 'Georgia', serif;
  }}

  /* Hide the default header bar */
  header[data-testid="stHeader"] {{ background: transparent; }}

  /* Hero banner */
  .hero {{
    background: linear-gradient(135deg, {CARD_BG} 0%, #3A2E25 100%);
    border: 1px solid {UMBER};
    border-radius: 16px;
    padding: 2.2rem 2.6rem 1.8rem;
    margin-bottom: 1.8rem;
  }}
  .hero h1 {{
    font-size: 2.4rem;
    color: {SAND};
    letter-spacing: 0.5px;
    margin: 0 0 0.4rem;
  }}
  .hero p {{
    color: {TEXT_MUTED};
    font-size: 1.0rem;
    margin: 0;
    line-height: 1.6;
  }}

  /* Metric cards */
  .metric-row {{
    display: flex;
    gap: 1rem;
    margin: 1.2rem 0;
  }}
  .metric-card {{
    flex: 1;
    background: {CARD_BG};
    border: 1px solid {UMBER};
    border-radius: 12px;
    padding: 1rem 1.2rem;
    text-align: center;
  }}
  .metric-card .label {{
    font-size: 0.78rem;
    color: {TEXT_MUTED};
    text-transform: uppercase;
    letter-spacing: 1px;
  }}
  .metric-card .value {{
    font-size: 2rem;
    font-weight: 700;
    color: {CLAY};
    line-height: 1.2;
  }}
  .metric-card .sub {{
    font-size: 0.82rem;
    color: {TEXT_MUTED};
  }}

  /* Section headings */
  .section-heading {{
    font-size: 1.05rem;
    color: {SAND};
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 1.6rem 0 0.6rem;
    border-left: 3px solid {CLAY};
    padding-left: 0.7rem;
  }}

  /* Slider label colour */
  label, .stSlider label p {{
    color: {TEXT_MUTED} !important;
    font-size: 0.9rem !important;
  }}
  /* Slider track */
  .stSlider [data-baseweb="slider"] [role="slider"] {{
    background-color: {CLAY} !important;
  }}

  /* Caption */
  .caption-box {{
    background: {CARD_BG};
    border-left: 3px solid {SAGE};
    border-radius: 0 8px 8px 0;
    padding: 0.75rem 1rem;
    color: {TEXT_MUTED};
    font-size: 0.85rem;
    line-height: 1.6;
    margin-top: 1rem;
  }}

  /* Hide matplotlib toolbar */
  .stPlotContainer {{ border: none; background: transparent !important; }}
</style>
""", unsafe_allow_html=True)

# ── Hero ─────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>Hubbard Model Quantum Simulator</h1>
  <p>
    Explore fermion physics on a tunable square lattice. Electrons hop between
    nearest-neighbour sites with amplitude <em>t</em> and experience on-site
    Coulomb repulsion <em>U</em> when two spin-opposite particles share a site.
  </p>
</div>
""", unsafe_allow_html=True)

# ── Dimension slider ─────────────────────────────────────────────
st.markdown('<p class="section-heading">Lattice Configuration</p>', unsafe_allow_html=True)

D = st.slider("Lattice dimension  D × D", min_value=2, max_value=8, value=2, step=1)
N = D * D
bonds = 2 * D * (D - 1)

# ── Metric cards ─────────────────────────────────────────────────
st.markdown(f"""
<div class="metric-row">
  <div class="metric-card">
    <div class="label">Lattice sites</div>
    <div class="value">{N}</div>
    <div class="sub">{D} × {D} grid</div>
  </div>
  <div class="metric-card">
    <div class="label">Hopping bonds</div>
    <div class="value">{bonds}</div>
    <div class="sub">nearest-neighbour</div>
  </div>
  <div class="metric-card">
    <div class="label">Hilbert space dim.</div>
    <div class="value">{4**N:,}</div>
    <div class="sub">4<sup>N</sup> states</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Lattice drawing ───────────────────────────────────────────────
def draw_lattice(D):
    size = max(3.5, min(D * 1.5, 7.5))
    fig, ax = plt.subplots(figsize=(size, size))
    fig.patch.set_facecolor(PARCHMENT)
    ax.set_facecolor(PARCHMENT)

    # Bonds
    for row in range(D):
        for col in range(D):
            x, y = col, row
            if col < D - 1:
                ax.plot([x, x + 1], [y, y], color=SAGE, lw=3.5, zorder=1,
                        solid_capstyle="round")
            if row < D - 1:
                ax.plot([x, x], [y, y + 1], color=SAGE, lw=3.5, zorder=1,
                        solid_capstyle="round")

    # Sites — draw shadow first for depth
    radius = max(0.12, 0.22 - D * 0.008)
    font_size = max(7, 12 - D)
    site_index = 0
    for row in range(D):
        for col in range(D):
            x, y = col, row
            # shadow
            shadow = plt.Circle((x + 0.025, y - 0.025), radius,
                                 color=BARK, alpha=0.35, zorder=2)
            ax.add_patch(shadow)
            # site
            circle = plt.Circle((x, y), radius, color=CLAY, zorder=3,
                                 linewidth=1.5, edgecolor=UMBER)
            ax.add_patch(circle)
            ax.text(x, y, str(site_index), ha="center", va="center",
                    fontsize=font_size, fontweight="bold",
                    color=PARCHMENT, zorder=4)
            site_index += 1

    ax.set_xlim(-0.6, D - 0.4)
    ax.set_ylim(-0.6, D - 0.4)
    ax.set_aspect("equal")
    ax.axis("off")

    ax.set_title(
        f"{D}×{D} Square Lattice  —  N = {D*D} sites",
        fontsize=12, pad=14, color=BARK,
        fontfamily="Georgia"
    )

    site_patch = mpatches.Patch(facecolor=CLAY, edgecolor=UMBER,
                                 linewidth=1, label="Lattice site")
    bond_patch = mpatches.Patch(color=SAGE, label="Hopping bond  (t)")
    ax.legend(handles=[site_patch, bond_patch],
                    loc="upper right", fontsize=9,
                    framealpha=0.85, facecolor=PARCHMENT,
                    edgecolor=UMBER, labelcolor=BARK)

    fig.tight_layout(pad=1.2)
    return fig


fig = draw_lattice(D)
st.pyplot(fig, use_container_width=True)
plt.close(fig)

# ── Caption ───────────────────────────────────────────────────────
st.markdown(
    f'<div class="caption-box">'
    f'<b>Site indices 0–{N-1}</b> label each lattice position. '
    f'Sage-green edges represent nearest-neighbour hopping with amplitude <em>t</em>. '
    f'On-site Coulomb repulsion <em>U</em> penalises double occupancy at each clay node.'
    f'</div>',
    unsafe_allow_html=True,
)
