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

# ── Numerical ED (cached, square-lattice PBC) ─────────────────
@st.cache_data(show_spinner=False)
def _ed_spectrum(D, J):
    """
    Lowest eigenvalues per Sz>=0 sector for D×D Heisenberg square lattice (PBC).

    Returns dict: Sz_int → {"E0": float|None, "evals": ndarray, "dim": int, "skipped": bool}
    Each undirected bond is listed as both (a,b) and (b,a), so all matrix elements
    carry an implicit ×2 relative to the single-sum convention; all E/J ratios and
    plateau positions are internally consistent.
    Sectors with dim > 2_000_000 are recorded but not diagonalised (skipped=True).
    """
    import scipy.sparse as _sp
    import scipy.sparse.linalg as _spla
    N = D * D
    _MAX_BLOCK = 2_000_000
    bonds = []
    for r in range(D):
        for c in range(D):
            s = r * D + c
            bonds.append((s, r * D + (c + 1) % D))
            bonds.append((s, ((r + 1) % D) * D + c))
    result = {}
    for Nup in range(math.ceil(N / 2), N + 1):
        Sz_int = 2 * Nup - N
        dim = math.comb(N, Nup)
        if dim > _MAX_BLOCK:
            result[Sz_int] = {"E0": None, "evals": np.array([]), "dim": dim, "skipped": True}
            continue
        basis = [tuple(1 if i in up else 0 for i in range(N))
                 for up in combinations(range(N), Nup)]
        idx_map = {s: i for i, s in enumerate(basis)}
        ri, ci, di = [], [], []
        for row_i, state in enumerate(basis):
            for (a, b) in bonds:
                sza = 0.5 if state[a] else -0.5
                szb = 0.5 if state[b] else -0.5
                ri.append(row_i); ci.append(row_i); di.append(J * sza * szb)
                if state[a] != state[b]:
                    lst = list(state); lst[a], lst[b] = lst[b], lst[a]
                    ns = tuple(lst)
                    if ns in idx_map:
                        ri.append(row_i); ci.append(idx_map[ns]); di.append(J * 0.5)
        H_mat = _sp.csr_matrix((di, (ri, ci)), shape=(dim, dim))
        k = min(6, dim)
        if dim <= 500:
            ev = np.sort(np.linalg.eigvalsh(H_mat.toarray()))[:k]
        else:
            ev, _ = _spla.eigsh(H_mat, k=k, which='SA')
            ev = np.sort(ev)
        result[Sz_int] = {"E0": float(ev[0]), "evals": ev, "dim": dim, "skipped": False}
    return result



def _sz_label(Sz_int):
    if Sz_int == 0: return "0"
    if Sz_int % 2 == 0: return f"+{Sz_int // 2}"
    return f"+{Sz_int}/2"

# ── Tabs ───────────────────────────────────────────────────────
tab_sim, tab_bec = st.tabs(["Hubbard Simulator", "4 · Numerical Validation — BEC Mixture"])

# ══════════════════════════════════════════════════════════════
# TAB 1 — Hubbard Simulator
# ══════════════════════════════════════════════════════════════
with tab_sim:
    # placeholder renders the chart FIRST, before sliders/title
    _fig3d_slot = st.empty()

    # ── Hero title (after image) ────────────────────────────────
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

    # ── Controls for 3D visualisation ──────────────────────────
    _c_np, _c_v0 = st.columns(2)
    with _c_np:
        _n_part = st.slider("Number of particles", 1, 25, 12, key="vis_np")
    with _c_v0:
        _v0 = st.slider("Potential scale  V₀", 0.5, 3.0, 1.5, 0.1, key="vis_v0")

    # ── Build 3D surface ────────────────────────────────────────
    _G   = 5
    _res = 220   # high res → smooth curves, no jagged edges
    _xs  = np.linspace(-0.6, _G - 0.4, _res)
    _ys  = np.linspace(-0.6, _G - 0.4, _res)
    _Xg, _Yg = np.meshgrid(_xs, _ys)
    # Smooth product-of-cosines well: minima at integer sites
    _Zg = -_v0 * (np.cos(2 * np.pi * _Xg) + np.cos(2 * np.pi * _Yg))

    # Deterministic particle placement
    _all_sites = [(i, j) for i in range(_G) for j in range(_G)]
    _perm      = np.random.default_rng(42).permutation(len(_all_sites))
    _chosen    = [_all_sites[_perm[k]] for k in range(min(_n_part, len(_all_sites)))]
    _px  = [float(s[0]) for s in _chosen]
    _py  = [float(s[1]) for s in _chosen]
    # Place particles one-third up from well floor so they're visible from the side
    _z_floor = -2.0 * _v0
    _z_range =  4.0 * _v0
    _pz  = [_z_floor + _z_range * 0.18] * len(_chosen)

    _fig3d = go.Figure()
    _fig3d.add_trace(go.Surface(
        x=_xs, y=_ys, z=_Zg,
        colorscale=[
            [0.00, '#000833'],
            [0.20, '#001f99'],
            [0.45, '#0055EE'],
            [0.70, '#00AAFF'],
            [0.88, '#55DDFF'],
            [1.00, '#CCEFFF'],
        ],
        showscale=False,
        # no contours → clean smooth surface
        lighting=dict(ambient=0.18, diffuse=0.50, specular=1.4,
                      roughness=0.12, fresnel=1.0),
        lightposition=dict(x=1, y=1, z=3),
    ))
    _fig3d.add_trace(go.Scatter3d(
        x=_px, y=_py, z=_pz,
        mode='markers',
        marker=dict(
            size=13,
            color='#FF2200',
            symbol='circle',
            line=dict(color='#FF9977', width=1.2),
            opacity=1.0,
        ),
        hovertemplate='Site (%{x:.0f}, %{y:.0f})<extra></extra>',
        showlegend=False,
    ))
    _fig3d.update_layout(
        paper_bgcolor='#000000',
        scene=dict(
            bgcolor='#000000',
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            # Low side-view camera so wells and particles are clearly visible
            camera=dict(
                eye=dict(x=1.9, y=0.25, z=0.28),
                up=dict(x=0, y=0, z=1),
            ),
            aspectmode='manual',
            aspectratio=dict(x=1.1, y=1.1, z=0.38),
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=520,
    )
    # Fill placeholder → chart appears above title/sliders
    _fig3d_slot.plotly_chart(_fig3d, use_container_width=True)

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

    # ── Numerical Analysis: Square Lattice Heisenberg Model ──────
    st.markdown(
        '<p class="sec-lbl" style="margin-top:2rem;">'
        'Numerical Analysis &mdash; Square Lattice Heisenberg Model</p>',
        unsafe_allow_html=True,
    )

    # ── Limiting regimes ──────────────────────────────────────────
    with st.expander("Eigenenergies in Limiting Regimes", expanded=True):
        st.markdown(r"""
**Hamiltonian:**
$$\hat{H} = J\!\sum_{\langle i,j\rangle}\hat{\mathbf{S}}_i\cdot\hat{\mathbf{S}}_j
           - H\!\sum_i \hat{S}_i^z$$

#### Case A — $J = 0$ (no exchange coupling)
| Field | Ground state | Energy |
|-------|-------------|--------|
| $H = 0$ | All $2^N$ states **degenerate** | $E = 0$ |
| $H > 0$ | Fully polarised $\lvert{\uparrow\cdots\uparrow}\rangle$, $S_z^{tot}=N/2$ | $E_{GS}=-HN/2$ |

A single spin-flip costs energy $+H$; the excitation gap equals $H$.

#### Case B — $H = 0$ (no external field)
- **Ferromagnetic ($J < 0$):** All spins align. Ground state $S_z^{tot}=\pm N/2$,
  $E_{GS}=JN/2$. (The bond list counts each undirected bond twice, so $2N$
  directed bonds each contribute $J/4$, giving $JN/2$.)
- **Antiferromagnetic ($J > 0$):** Ground state is a **quantum singlet** ($S_z^{tot}=0$,
  even $N$), $E_{GS}<0$. For the 2×2 lattice (N=4, 8 directed bonds): $E_{GS}/J=-4$.

#### General case $H, J > 0$
As $H/J$ rises from 0, level crossings drive the ground state:
$S_z=0\!\to\!1\!\to\!\cdots\!\to\!N/2$, producing **magnetisation plateaus**.
Saturation field (square lattice, double-bond convention): $H_{sat}/J = 4$.
        """)

    # ── Controls ──────────────────────────────────────────────────
    _lat_opts = {"2 × 2  (N = 4)": 2,
                 "4 × 4  (N = 16)": 4,
                 "6 × 6  (N = 36)": 6}
    _lat_str  = st.radio("Lattice (PBC)", list(_lat_opts), horizontal=True, key="heis_lat")
    _ed_D2    = _lat_opts[_lat_str]
    _ed_N2    = _ed_D2 ** 2

    _hc1, _hc2 = st.columns(2)
    with _hc1:
        _heis_J    = st.slider("Exchange coupling  J", 0.1, 3.0, 1.0, 0.05, key="heis_J")
    with _hc2:
        _heis_Hmax = st.slider("H / J  axis maximum", 1.0, 14.0, 8.0, 0.5,  key="heis_Hmax")

    _n_bonds_h = 2 * _ed_N2
    _hilbert_h = 2 ** _ed_N2
    _sz0_dim_h = math.comb(_ed_N2, _ed_N2 // 2) if _ed_N2 % 2 == 0 else 0
    st.markdown(
        f'<p style="color:{T["txt_mute"]};font-size:0.84rem;margin:0.2rem 0 0.6rem;">'
        f'{_ed_D2}&times;{_ed_D2} PBC lattice &nbsp;&middot;&nbsp; N = {_ed_N2} sites '
        f'&nbsp;&middot;&nbsp; {_n_bonds_h} directed bonds '
        f'&nbsp;&middot;&nbsp; Full dim = 2<sup>{_ed_N2}</sup> = {_hilbert_h:,}'
        f'&nbsp;&middot;&nbsp; S<sub>z</sub>=0 block dim = {_sz0_dim_h:,}'
        f'</p>',
        unsafe_allow_html=True,
    )

    # ── Solve ─────────────────────────────────────────────────────
    with st.spinner(f"Diagonalising {_ed_D2}×{_ed_D2} Heisenberg model (S_z blocks)…"):
        _heis_spec = _ed_spectrum(_ed_D2, _heis_J)

    _ev_sorted = sorted(_heis_spec.items())
    _n_skip    = sum(1 for d in _heis_spec.values() if d["skipped"])

    # ── Computed limiting-regime values ───────────────────────────
    _E0_afm = _heis_spec.get(0,       {}).get("E0")
    _E0_sat = _heis_spec.get(_ed_N2,  {}).get("E0")
    _lim_parts = []
    if _E0_afm is not None:
        _lim_parts.append(
            f'<b>H = 0, J = {_heis_J:.2f} (AFM):</b> '
            f'E<sub>GS</sub> = {_E0_afm:.4g} = ({_E0_afm/_heis_J:.4g}) J '
            f'&nbsp;— S<sub>z</sub> = 0 sector, numerical'
        )
    if _E0_sat is not None:
        _fm_val = _heis_J * _ed_N2 / 2
        _lim_parts.append(
            f'<b>H = 0, FM analytical:</b> '
            f'E = J·N/2 = {_fm_val:.4g} '
            f'&nbsp;— S<sub>z</sub> = {_ed_N2//2} fully polarised; '
            f'computed E<sub>0</sub> = {_E0_sat:.4g}'
        )
    if _lim_parts:
        st.markdown(
            f'<div class="caption-box">' + '<br>'.join(_lim_parts) + '</div>',
            unsafe_allow_html=True,
        )

    # ── Eigenvalue sector cards ────────────────────────────────────
    st.markdown('<p class="sec-lbl">Eigenvalues by S<sub>z</sub> Sector  (S<sub>z</sub> ≥ 0)</p>',
                unsafe_allow_html=True)
    _CARD_COLORS = [SAGE, AMBER, BUTTER, STEEL, ROSE, MOSS, SLATE, TERRA, DARK_BRN]
    _ncols_h  = min(len(_ev_sorted), 6)
    _ev_cols_h = st.columns(_ncols_h)
    for _ci, (Sz_int, _data) in enumerate(_ev_sorted):
        _lbl = _sz_label(Sz_int)
        _cc  = _CARD_COLORS[_ci % len(_CARD_COLORS)]
        if _data["skipped"]:
            _body = (
                f'<span style="font-size:0.78rem;color:{T["txt_mute"]};">'
                f'dim = {_data["dim"]:,}<br>'
                f'<em>skipped (dim &gt; 2M)</em></span>'
            )
        else:
            _ev_str = ",&ensp;".join(f"{v / _heis_J:.4g}" for v in _data["evals"])
            _body = (
                f'<small style="color:{T["txt_mute"]}">dim = {_data["dim"]:,}</small><br>'
                f'<small style="color:{T["txt_mute"]}">E / J =</small><br>'
                f'<span style="font-size:0.78rem;font-family:monospace;">{_ev_str}</span>'
            )
        with _ev_cols_h[_ci % _ncols_h]:
            st.markdown(
                f'<div class="z-card" style="border-left:3px solid {_cc};">'
                f'<b>Sz = {_lbl}</b>&nbsp;{_body}'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── Magnetisation plateau plot ─────────────────────────────────
    st.markdown(
        '<p class="sec-lbl">'
        'Average Magnetisation ⟨Mᵣ⟩ = Sᵣ / N &nbsp;vs&nbsp; H / J</p>',
        unsafe_allow_html=True,
    )
    _H_arr_J   = np.linspace(0.0, float(_heis_Hmax), 900)
    _Mz_arr    = np.zeros(len(_H_arr_J))
    _Sz_gs_arr = np.zeros(len(_H_arr_J))
    for _i, _hj in enumerate(_H_arr_J):
        _H_abs   = _hj * _heis_J
        _best_E  = np.inf
        _best_Sz = 0.0
        for _Sz_int, _data in _heis_spec.items():
            if _data["E0"] is None:
                continue
            _Sz = _Sz_int / 2.0
            _E  = _data["E0"] - _H_abs * _Sz
            if _E < _best_E:
                _best_E  = _E
                _best_Sz = _Sz
        _Mz_arr[_i]    = _best_Sz / _ed_N2
        _Sz_gs_arr[_i] = _best_Sz

    _diff      = np.diff(_Sz_gs_arr)
    _trans_idx = np.where(_diff != 0)[0]
    _trans_HJ  = _H_arr_J[_trans_idx + 1]

    _fig_mag = go.Figure()
    _fig_mag.add_trace(go.Scatter(
        x=_H_arr_J, y=_Mz_arr,
        mode="lines",
        line=dict(color=SAGE, width=2.5, shape="hv"),
        name="⟨M_z⟩ = S_z / N",
        hovertemplate="H/J = %{x:.3f}<br>⟨Mz⟩ = %{y:.4f}<extra></extra>",
    ))
    for _th in _trans_HJ:
        _fig_mag.add_vline(x=float(_th), line_dash="dot",
                           line_color=AMBER, line_width=1.3, opacity=0.75)

    _annotated_sz = set()
    for _i, _sz in enumerate(_Sz_gs_arr):
        if _sz not in _annotated_sz:
            _annotated_sz.add(_sz)
            _mz = _sz / _ed_N2
            _fig_mag.add_annotation(
                x=_H_arr_J[_i] + 0.06 * _heis_Hmax,
                y=_mz + 0.013,
                text=f"S_z={int(_sz)}",
                showarrow=False,
                font=dict(size=8.5, color=T["txt_mute"]),
                xanchor="left",
            )

    _fig_mag.update_layout(
        paper_bgcolor=T["page_bg"], plot_bgcolor=T["plot_bg"],
        height=420, margin=dict(l=60, r=30, t=30, b=50),
        xaxis=dict(
            title="H / J",
            range=[0, _heis_Hmax],
            tickfont=dict(color=T["txt_mute"], size=10),
            title_font=dict(color=T["txt_mute"]),
            gridcolor=T["border"],
        ),
        yaxis=dict(
            title="⟨M_z⟩ = S_z / N",
            range=[-0.03, 0.57],
            tickfont=dict(color=T["txt_mute"], size=10),
            title_font=dict(color=T["txt_mute"]),
            gridcolor=T["border"],
        ),
        legend=dict(bgcolor=T["card_bg"], bordercolor=T["border"],
                    font=dict(color=T["txt_main"], size=10)),
        hoverlabel=dict(bgcolor=T["hover_bg"], font=dict(color=T["hover_txt"])),
    )
    st.plotly_chart(_fig_mag, use_container_width=True)

    _skip_note = (
        f"&nbsp;&bull;&nbsp;{_n_skip} low-S<sub>z</sub> sector(s) with dim &gt; 2M "
        f"skipped — curve shows only S<sub>z</sub> ≥ N/2 − 6; "
        f"full 6×6 result requires QuSpin."
        if _n_skip else ""
    )
    st.markdown(
        f'<div class="caption-box">'
        f'Amber dotted lines mark critical fields '
        f'H<sub>c</sub>/J = [E<sub>0</sub>(S<sub>z</sub>+1) − '
        f'E<sub>0</sub>(S<sub>z</sub>)] / J '
        f'at which the ground state jumps to the next S<sub>z</sub> sector '
        f'— the <em>magnetisation plateaus</em>. '
        f'⟨M<sub>z</sub>⟩ saturates at 1/2 (all spins aligned). '
        f'Each plateau step has height 1/N. '
        f'{_skip_note}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Computation notes ─────────────────────────────────────────
    with st.expander("Computation: Sᵣ Subspace Blocking & Sparse ED", expanded=False):
        _blk_rows = "\n".join(
            f"| {_bd}×{_bd} | {_bd*_bd} | {2**(_bd*_bd):,} | "
            f"{math.comb(_bd*_bd, _bd*_bd//2):,} |"
            for _bd in (2, 4, 6)
        )
        st.markdown(
            "**Key identity:** $[\\hat{H}, \\hat{S}^z_{\\rm tot}] = 0$\n\n"
            "The Hamiltonian conserves $S_z^{\\rm tot}$, so the full $2^N\\!\\times\\!2^N$ "
            "matrix block-diagonalises into sectors labelled by "
            "$S_z = -N/2,\\ldots,+N/2$. "
            "Only $S_z\\ge 0$ blocks are solved (time-reversal symmetry gives "
            "$E(S_z)=E(-S_z)$).\n\n"
            f"| Lattice | N | Full dim | Sᵣ = 0 block |\n"
            f"|---------|---|----------|-------------|\n"
            f"{_blk_rows}\n\n"
            "**Dense** (NumPy `eigvalsh`, LAPACK): block dim ≤ 500.  \n"
            "**Sparse** (SciPy `eigsh`, Lanczos): 500 < dim ≤ 2\\,000\\,000 "
            "— finds $k=6$ lowest eigenvalues; memory $\\mathcal{O}(k\\cdot\\text{dim})$.  \n"
            "**Skipped** (dim > 2M): low-$S_z$ sectors of the 6×6 lattice. "
            "Full treatment needs QuSpin (translational + point-group symmetry reduces "
            "the $S_z=0$ block from $\\sim$9\\u202f×\\u202f10⁹ to "
            "$\\sim$2.5\\u202f×\\u202f10⁸$ states).\n\n"
            "**Magnetisation plateaus:** critical fields satisfy\n"
            "$$\\frac{H_c^{(S_z)}}{J} = "
            "\\frac{E_0(S_z+1) - E_0(S_z)}{J}$$\n"
            "At saturation $H_{sat}/J=4$ (square lattice, double-bond convention)."
        )


# ══════════════════════════════════════════════════════════════
# TAB 2 — BEC Mixture Calculator
# ══════════════════════════════════════════════════════════════
with tab_bec:
    import scipy.constants as _sc
    from scipy.optimize import fsolve as _fsolve
    import matplotlib.pyplot as _plt
    import matplotlib.patches as _mp

    # ── Physics solver ────────────────────────────────────────────
    @st.cache_data(show_spinner=False)
    def _solve_tf(mB_amu, mF_amu, fB_Hz, fF_Hz, NB, NF, aB_nm, aF_nm, aBF_nm, n_pts=400):
        """
        Thomas-Fermi solver for a two-component BEC mixture in a 3-D spherical trap.

        Assumptions
        -----------
        * Thomas-Fermi approximation (kinetic energy << interaction energy; valid when N·a/a_ho >> 1).
        * Spherically symmetric harmonic traps (ω_x = ω_y = ω_z = ω_i).
        * Zero temperature, ground state only.
        * Both components are weakly interacting bosons (mean-field GPE).
        * Local density approximation: interspecies coupling is treated pointwise.

        Coupling constants (SI)
        -----------------------
          g_BB = 4π ℏ² a_B  / m_B
          g_FF = 4π ℏ² a_F  / m_F
          g_BF = 2π ℏ² a_BF (1/m_B + 1/m_F)

        Miscibility condition: g_BF² < g_BB · g_FF

        Chemical potentials μ_B, μ_F are found by enforcing ∫4πr² n_i dr = N_i.
        """
        hbar = _sc.hbar;  kB = _sc.k;  amu = _sc.u
        mB  = mB_amu * amu;  mF  = mF_amu * amu
        wB  = 2*np.pi*fB_Hz; wF  = 2*np.pi*fF_Hz
        aB  = aB_nm * 1e-9;  aF  = aF_nm * 1e-9;  aBF = aBF_nm * 1e-9

        gBB = 4*np.pi*hbar**2 * aB  / mB
        gFF = 4*np.pi*hbar**2 * aF  / mF
        gBF = 2*np.pi*hbar**2 * aBF * (1/mB + 1/mF)

        a_ho_B = np.sqrt(hbar / (mB*wB))
        a_ho_F = np.sqrt(hbar / (mF*wF))

        # Initial μ guess from single-species TF result
        mu_B0 = hbar*wB/2 * max((15*NB*abs(aB)/a_ho_B)**(2/5), 0.1)
        mu_F0 = hbar*wF/2 * max((15*NF*abs(aF)/a_ho_F)**(2/5), 0.1)
        r_max = max(np.sqrt(2*mu_B0/(mB*wB**2)), np.sqrt(2*mu_F0/(mF*wF**2))) * 1.8
        r = np.linspace(0, r_max, n_pts)

        def _local(ri, muB, muF):
            VB = 0.5*mB*wB**2*ri**2;  VF = 0.5*mF*wF**2*ri**2
            D  = gBB*gFF - gBF**2
            if abs(D) < 1e-55:
                return max(0., (muB-VB)/gBB), max(0., (muF-VF)/gFF)
            nB = (gFF*(muB-VB) - gBF*(muF-VF)) / D
            nF = (gBB*(muF-VF) - gBF*(muB-VB)) / D
            if nB < 0 and nF < 0:  return 0., 0.
            if nB < 0:             return 0., max(0., (muF-VF)/gFF)
            if nF < 0:             return max(0., (muB-VB)/gBB), 0.
            return nB, nF

        def _profiles(muB, muF):
            nb, nf = np.zeros(n_pts), np.zeros(n_pts)
            for i, ri in enumerate(r):
                nb[i], nf[i] = _local(ri, muB, muF)
            return nb, nf

        def _res(mus):
            nb, nf = _profiles(mus[0], mus[1])
            return [(4*np.pi*np.trapz(nb*r**2, r) - NB)/NB,
                    (4*np.pi*np.trapz(nf*r**2, r) - NF)/NF]

        try:
            sol, _, flag, _ = _fsolve(_res, [mu_B0, mu_F0], full_output=True)[:4]
            muB, muF = sol if flag == 1 else (mu_B0, mu_F0)
        except Exception:
            muB, muF = mu_B0, mu_F0

        nb, nf = _profiles(muB, muF)

        def _rtf(n_arr):
            m = n_arr > n_arr.max()*1e-4
            return float(r[m][-1])*1e6 if m.any() else 0.

        miscible = bool(gBF**2 < gBB*gFF)
        return dict(
            r_um   = r*1e6,
            nB     = nb*1e-6,   # cm⁻³
            nF     = nf*1e-6,
            R_B    = _rtf(nb),  # µm
            R_F    = _rtf(nf),
            n0_B   = float(nb[0])*1e-6,
            n0_F   = float(nf[0])*1e-6,
            muB_nK = muB/(_sc.k*1e-9),
            muF_nK = muF/(_sc.k*1e-9),
            gBF    = gBF, gBB=gBB, gFF=gFF,
            miscible = miscible,
            regime   = "Miscible" if miscible else "Phase-separated",
            a_ho_B_um = float(np.sqrt(_sc.hbar/(mB_amu*_sc.u * 2*np.pi*fB_Hz)))*1e6,
        )

    # ── Header ────────────────────────────────────────────────────
    st.markdown("""
<div class="hero">
  <h1 style="font-size:1.6rem;">4 · Numerical Validation — BEC Mixture Density Profiles</h1>
  <p>
    Two-component Bose-Einstein condensate in a 3-D spherical harmonic trap.
    Solve the coupled Thomas-Fermi equations to obtain density profiles n<sub>B</sub>(r),
    n<sub>F</sub>(r) and compare the non-interacting, weak-interacting, and phase-separation
    regimes for negative, zero, and positive interspecies scattering length a<sub>BF</sub>.
  </p>
</div>
""", unsafe_allow_html=True)

    # ── Assumptions expander ──────────────────────────────────────
    with st.expander("Model & Assumptions", expanded=False):
        st.markdown(r"""
**Thomas-Fermi (TF) approximation** — kinetic energy is neglected; valid when
$N\,a/a_{ho} \gg 1$.  The Gross-Pitaevskii energy functional reduces to local algebraic
equations for the densities.

**Coupled TF equations** (spherical trap, 3-D):

$$
n_B(r) = \frac{g_{FF}\bigl(\mu_B - V_B(r)\bigr) - g_{BF}\bigl(\mu_F - V_F(r)\bigr)}{g_{BB}g_{FF} - g_{BF}^2},
\qquad
n_F(r) = \frac{g_{BB}\bigl(\mu_F - V_F(r)\bigr) - g_{BF}\bigl(\mu_B - V_B(r)\bigr)}{g_{BB}g_{FF} - g_{BF}^2}
$$

with $V_i(r)=\tfrac{1}{2}m_i\omega_i^2 r^2$.  Densities are clamped to zero where negative
(phase-separated boundary approximation).

**Coupling constants (SI):**
$\;g_{BB}=4\pi\hbar^2 a_B/m_B,\quad g_{FF}=4\pi\hbar^2 a_F/m_F,\quad
g_{BF}=2\pi\hbar^2 a_{BF}(m_B^{-1}+m_F^{-1}).$

**Miscibility condition:** $g_{BF}^2 < g_{BB}\,g_{FF}$. Violation → phase separation.

**Chemical potentials** $\mu_B,\,\mu_F$ are found numerically by enforcing
$4\pi\int_0^\infty n_i(r)\,r^2\,dr = N_i$.
        """)

    # ── Parameter inputs ──────────────────────────────────────────
    st.markdown('<p class="sec-lbl">Parameters</p>', unsafe_allow_html=True)
    _c1, _c2, _c3 = st.columns(3)
    with _c1:
        st.markdown("**Species B** (e.g. ⁸⁷Rb)")
        _mB  = st.number_input("m_B (amu)",          1.0,  300.0, 87.0,  1.0,  key="bec_mB")
        _fB  = st.number_input("ω_B / 2π  (Hz)",     1.0, 2000.0, 100.0, 10.0, key="bec_fB")
        _NB  = st.number_input("N_B  (atoms)",        100, 500000, 50000, 1000, key="bec_NB")
        _aB  = st.number_input("a_B (nm)",            0.01, 50.0,  5.29,  0.1,  key="bec_aB",
                                help="⁸⁷Rb: a_B ≈ 5.29 nm (100 a₀)")
    with _c2:
        st.markdown("**Species F** (e.g. ⁴¹K)")
        _mF  = st.number_input("m_F (amu)",          1.0,  300.0, 41.0,  1.0,  key="bec_mF")
        _fF  = st.number_input("ω_F / 2π  (Hz)",     1.0, 2000.0, 150.0, 10.0, key="bec_fF")
        _NF  = st.number_input("N_F  (atoms)",        100, 500000, 30000, 1000, key="bec_NF")
        _aF  = st.number_input("a_F (nm)",            0.01, 50.0,  3.39,  0.1,  key="bec_aF",
                                help="⁴¹K: a_F ≈ 3.39 nm (64 a₀)")
    with _c3:
        st.markdown("**Interspecies a_BF values**")
        _aBF_neg  = st.number_input("a_BF  attractive (nm)", -300.0, -0.01, -5.0,  0.5, key="bec_n")
        _aBF_weak = st.number_input("a_BF  weak repulsive (nm)", 0.01, 50.0,  5.0,  0.5, key="bec_w")
        _aBF_sep  = st.number_input("a_BF  phase-sep (nm)",      1.0, 500.0, 50.0, 5.0, key="bec_s")
        st.caption("a_BF = 0 (non-interacting) is always included.")
        _scan_lo = st.number_input("Scan min (nm)", -100.0,  0.0, -30.0, 1.0, key="bec_slo")
        _scan_hi = st.number_input("Scan max (nm)",   0.0, 300.0,  60.0, 1.0, key="bec_shi")
        _n_scan  = st.slider("Scan points", 5, 40, 20, key="bec_nscan")

    # ── Solve four cases ──────────────────────────────────────────
    _case_labels = [
        "Non-interacting\n(a_BF = 0)",
        f"Attractive\n(a_BF = {_aBF_neg:.1f} nm)",
        f"Weak repulsive\n(a_BF = {_aBF_weak:.1f} nm)",
        f"Phase separation\n(a_BF = {_aBF_sep:.1f} nm)",
    ]
    _case_aBF = [0.0, float(_aBF_neg), float(_aBF_weak), float(_aBF_sep)]

    with st.spinner("Solving Thomas-Fermi equations…"):
        _results = {
            lbl: _solve_tf(_mB, _mF, _fB, _fF, _NB, _NF, _aB, _aF, abf)
            for lbl, abf in zip(_case_labels, _case_aBF)
        }

    # ── Coupling constants display ────────────────────────────────
    st.markdown('<p class="sec-lbl">Coupling Constants  g = 4πℏ²a/m</p>',
                unsafe_allow_html=True)
    _ref0 = _results[_case_labels[0]]
    _gBB_SI, _gFF_SI = _ref0["gBB"], _ref0["gFF"]
    _misc_g = float(np.sqrt(_gBB_SI * _gFF_SI))

    def _g_fmt(g):
        if g == 0:
            return "0 J·m³"
        exp = int(np.floor(np.log10(abs(g))))
        mantissa = g / 10**exp
        return f"{mantissa:.3f}&thinsp;&times;&thinsp;10<sup>{exp}</sup> J·m³"

    _gbf_rows = "".join(
        f'<li><b>{lbl.replace(chr(10), " ")}</b>: '
        f'g<sub>BF</sub> = {_g_fmt(_results[lbl]["gBF"])} '
        f'&rarr; <em>{"miscible" if _results[lbl]["miscible"] else "phase-separated"}</em></li>'
        for lbl in _case_labels
    )
    st.markdown(
        f'<div class="caption-box">'
        f'<b>g<sub>BB</sub></b> = {_g_fmt(_gBB_SI)} &nbsp;&nbsp;'
        f'<b>g<sub>FF</sub></b> = {_g_fmt(_gFF_SI)}<br>'
        f'Miscibility threshold &nbsp;√(g<sub>BB</sub>&thinsp;g<sub>FF</sub>) = {_g_fmt(_misc_g)}'
        f'<ul style="margin:0.5rem 0 0;padding-left:1.4rem;">{_gbf_rows}</ul>'
        f'<small style="color:{T["txt_mute"]}">g<sub>BB</sub>=4πℏ²a<sub>B</sub>/m<sub>B</sub>, '
        f'g<sub>FF</sub>=4πℏ²a<sub>F</sub>/m<sub>F</sub>, '
        f'g<sub>BF</sub>=2πℏ²a<sub>BF</sub>(m<sub>B</sub><sup>-1</sup>+m<sub>F</sub><sup>-1</sup>). '
        f'Phase separation when g<sub>BF</sub>² &gt; g<sub>BB</sub>g<sub>FF</sub>.</small>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Plot 1: density profiles ──────────────────────────────────
    st.markdown('<p class="sec-lbl">Density Profiles</p>', unsafe_allow_html=True)

    _fig1, _axes = _plt.subplots(1, 4, figsize=(16, 4))
    _fig1.patch.set_facecolor("none")
    for _ax, (_lbl, _res) in zip(_axes, _results.items()):
        _ax.plot(_res["r_um"], _res["nB"], color=SAGE,  lw=2.0, label="Species B")
        _ax.plot(_res["r_um"], _res["nF"], color=ROSE,  lw=2.0, label="Species F", ls="--")
        _ax.set_facecolor("none")
        _ax.set_xlabel("r  (μm)", fontsize=8)
        _ax.set_ylabel("n  (cm⁻³)", fontsize=8)
        _ax.tick_params(labelsize=7)
        for _sp in _ax.spines.values(): _sp.set_color(OFF_WHT)
        _ax.tick_params(colors=DARK_BRN)
        _ax.set_xlabel("r  (μm)", fontsize=8, color=DARK_BRN)
        _ax.set_ylabel("n  (cm⁻³)", fontsize=8, color=DARK_BRN)
        _title = _lbl.replace("\n", "  ") + f"\n[{_res['regime']}]"
        _ax.set_title(_title, fontsize=7.5, color=DARK_BRN, pad=4)
        _ax.legend(fontsize=6.5, facecolor=OFF_WHT, edgecolor=OFF_WHT, labelcolor=DARK_BRN)
        for _R, _col in [(_res["R_B"], SAGE), (_res["R_F"], ROSE)]:
            if _R > 0:
                _ax.axvline(_R, color=_col, lw=0.8, ls=":", alpha=0.7)
    _fig1.tight_layout()
    st.pyplot(_fig1, use_container_width=True)
    _plt.close(_fig1)
    st.caption(
        f"Fixed parameters — B ({_mB} amu, ω_B/2π = {_fB} Hz, N_B = {int(_NB)}, "
        f"a_B = {_aB} nm); F ({_mF} amu, ω_F/2π = {_fF} Hz, N_F = {int(_NF)}, a_F = {_aF} nm). "
        "Dotted vertical lines: Thomas-Fermi radii R_TF for each species. "
        "Assumption: 3-D spherical trap, zero temperature, Thomas-Fermi approximation (N·a/a_ho ≫ 1)."
    )

    # ── Plot 2: scan over a_BF ────────────────────────────────────
    st.markdown('<p class="sec-lbl">TF Radius & Peak Density vs a_BF</p>',
                unsafe_allow_html=True)
    _aBF_arr = np.linspace(_scan_lo, _scan_hi, int(_n_scan))
    with st.spinner("Running a_BF scan…"):
        _scan = [_solve_tf(_mB, _mF, _fB, _fF, _NB, _NF, _aB, _aF, float(_a), n_pts=250)
                 for _a in _aBF_arr]

    _fig2, (_ax_r, _ax_n) = _plt.subplots(1, 2, figsize=(12, 4))
    _fig2.patch.set_facecolor("none")
    for _axx in (_ax_r, _ax_n):
        _axx.set_facecolor("none")
        _axx.tick_params(colors=DARK_BRN, labelsize=8)
        for _sp in _axx.spines.values(): _sp.set_color(OFF_WHT)
        _axx.axvline(0, color=OFF_WHT, lw=0.8, ls="--")

    _ax_r.plot(_aBF_arr, [s["R_B"] for s in _scan], color=SAGE, lw=2, label="R_TF  (B)")
    _ax_r.plot(_aBF_arr, [s["R_F"] for s in _scan], color=ROSE, lw=2, ls="--", label="R_TF  (F)")
    _ax_r.set_xlabel("a_BF  (nm)", color=DARK_BRN)
    _ax_r.set_ylabel("Thomas-Fermi radius  (μm)", color=DARK_BRN)
    _ax_r.set_title("TF Radii vs a_BF", color=DARK_BRN)
    _ax_r.legend(facecolor=OFF_WHT, edgecolor=OFF_WHT, labelcolor=DARK_BRN, fontsize=8)

    _ax_n.plot(_aBF_arr, [s["n0_B"] for s in _scan], color=SAGE, lw=2, label="n₀  (B)")
    _ax_n.plot(_aBF_arr, [s["n0_F"] for s in _scan], color=ROSE, lw=2, ls="--", label="n₀  (F)")
    _ax_n.set_xlabel("a_BF  (nm)", color=DARK_BRN)
    _ax_n.set_ylabel("Peak density  (cm⁻³)", color=DARK_BRN)
    _ax_n.set_title("Peak Density vs a_BF", color=DARK_BRN)
    _ax_n.legend(facecolor=OFF_WHT, edgecolor=OFF_WHT, labelcolor=DARK_BRN, fontsize=8)

    _fig2.tight_layout()
    st.pyplot(_fig2, use_container_width=True)
    _plt.close(_fig2)
    st.caption(
        f"Scan over a_BF ∈ [{_scan_lo:.0f}, {_scan_hi:.0f}] nm with all other parameters fixed "
        f"(same as density-profile plots above). "
        "Left: as a_BF → negative (attractive, g_BF < 0) both R_TF shrink and peak densities rise — "
        "mutual attraction compresses the clouds; beyond a critical |a_BF| the mixture collapses. "
        "As a_BF → positive (repulsive, g_BF > 0) R_TF expand and peak densities fall; "
        "once g_BF² > g_BB·g_FF the clouds demix (phase separation) and the profiles split "
        "into core/shell geometry — evident as a kink or plateau in the curves."
    )

    # ── Summary table ─────────────────────────────────────────────
    st.markdown('<p class="sec-lbl">Summary Table</p>', unsafe_allow_html=True)
    _tbl = []
    for _lbl, _res in _results.items():
        _abf_v = _case_aBF[_case_labels.index(_lbl)]
        _tbl.append({
            "Case":           _lbl.replace("\n", " "),
            "a_BF (nm)":      f"{_abf_v:.1f}",
            "Regime":         _res["regime"],
            "R_TF B (μm)":   f"{_res['R_B']:.2f}",
            "R_TF F (μm)":   f"{_res['R_F']:.2f}",
            "n₀_B (cm⁻³)":   f"{_res['n0_B']:.3e}",
            "n₀_F (cm⁻³)":   f"{_res['n0_F']:.3e}",
            "μ_B (nK)":      f"{_res['muB_nK']:.1f}",
            "μ_F (nK)":      f"{_res['muF_nK']:.1f}",
        })
    st.dataframe(pd.DataFrame(_tbl), use_container_width=True, hide_index=True)

    # ── Physics commentary ────────────────────────────────────────
    with st.expander("Physics Commentary", expanded=True):
        st.markdown(f"""
**Chosen parameters** — Species B: $^{{87}}$Rb ({_mB} amu, $\\omega_B/2\\pi={_fB}$ Hz,
$N_B={_NB}$, $a_B={_aB}$ nm); Species F: $^{{41}}$K ({_mF} amu, $\\omega_F/2\\pi={_fF}$ Hz,
$N_F={_NF}$, $a_F={_aF}$ nm). Harmonic oscillator length
$a_{{ho}}^B \\approx {_results[_case_labels[0]]['a_ho_B_um']:.3f}\\,\\mu$m.

---

**Non-interacting ($a_{{BF}}=0$):** Each species forms an independent inverted-parabola profile.
The TF radius is $R_{{TF}}^i = a_{{ho}}^i\\,(15 N_i a_i/a_{{ho}}^i)^{{1/5}}$ and the peak density
$n_0^i = \\mu_i / g_{{ii}}$ depends only on intraspecies interactions.

**Attractive ($a_{{BF}}<0$, $g_{{BF}}<0$):** Interspecies attraction pulls the clouds together,
increasing spatial overlap.  The effective chemical potential rises for both species, *compressing*
each cloud.  $R_{{TF}}$ **decreases** and $n_0$ **increases** as $|a_{{BF}}|$ grows.
Beyond a critical attraction the mixture becomes mechanically unstable (mean-field collapse).

**Weak repulsion ($a_{{BF}}>0$, small):** Mutual repulsion swells each cloud outward.
$R_{{TF}}$ **increases** and $n_0$ **decreases** moderately relative to the non-interacting case.

**Phase separation ($g_{{BF}}^2 > g_{{BB}}g_{{FF}}$, large positive $a_{{BF}}$):**
The miscibility condition is violated.  The species demix: one occupies the core, the other
a surrounding shell.  The species with the smaller TF radius (tighter confinement or fewer atoms)
is typically squeezed to the centre.  The peak density of the *expelled* species at $r=0$ drops
toward zero, while the *core* species density there rises.  The TF radius of the core species
*shrinks* and that of the shell species *expands*.
        """)
