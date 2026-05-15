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

    Returns dict: Sz_int → {"E0": float|None, "evals": ndarray, "dim": int,
                             "skipped": bool, "evecs_top": list}
    evecs_top[j] = list of (coeff, state_tuple) for the top-8 components of eigenvector j,
    sorted by |coeff| descending.
    Each undirected bond is listed as both (a,b) and (b,a), so all matrix elements
    carry an implicit ×2 relative to the single-sum convention; all E/J ratios and
    plateau positions are internally consistent.
    Sectors with dim > 2_000_000 are recorded but not diagonalised (skipped=True).
    """
    import scipy.sparse as _sp
    import scipy.sparse.linalg as _spla
    N = D * D
    _MAX_BLOCK = 2_000_000
    _N_TOP     = 8          # dominant components to store per eigenvector
    bonds = []
    for r in range(D):
        for c in range(D):
            s = r * D + c
            bonds.append((s, r * D + (c + 1) % D))
            bonds.append((s, ((r + 1) % D) * D + c))
    _J0 = abs(J) < 1e-8    # flag: treat as non-interacting (all eigenvalues = 0)
    result = {}
    for Nup in range(math.ceil(N / 2), N + 1):
        Sz_int = 2 * Nup - N
        dim = math.comb(N, Nup)
        if dim > _MAX_BLOCK:
            result[Sz_int] = {"E0": None, "evals": np.array([]), "dim": dim,
                              "skipped": True, "evecs_top": []}
            continue
        basis = [tuple(1 if i in up else 0 for i in range(N))
                 for up in combinations(range(N), Nup)]
        idx_map = {s: i for i, s in enumerate(basis)}
        k = min(6, dim)
        if _J0:
            # J = 0: all basis states are degenerate eigenstates at E = 0
            ev    = np.zeros(k)
            evecs = np.eye(dim, k)
        else:
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
            if dim <= 500:
                ev_all, evec_all = np.linalg.eigh(H_mat.toarray())
                ev    = ev_all[:k]
                evecs = evec_all[:, :k]
            else:
                ev_raw, evecs = _spla.eigsh(H_mat, k=k, which='SA')
                order = np.argsort(ev_raw)
                ev    = ev_raw[order]
                evecs = evecs[:, order]
        # Store top-_N_TOP components (by |coeff|) for each eigenvector
        n_top = min(_N_TOP, dim)
        evecs_top = []
        for j in range(evecs.shape[1]):
            col      = evecs[:, j]
            top_idx  = np.argsort(-np.abs(col))[:n_top]
            evecs_top.append([(float(col[ii]), basis[ii]) for ii in top_idx])
        result[Sz_int] = {"E0": float(ev[0]), "evals": ev, "dim": dim,
                          "skipped": False, "evecs_top": evecs_top}
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


    # ══════════════════════════════════════════════════════════════
    # SECTION A — Energy Eigenvalue Spectrum
    # ══════════════════════════════════════════════════════════════
    st.markdown(
        '<p class="sec-lbl" style="margin-top:2rem;">'
        'Energy Eigenvalue Spectrum &mdash; E / J &nbsp;vs&nbsp; H / J</p>',
        unsafe_allow_html=True,
    )

    _sa_lat_opts = {"2 × 2  (N = 4)": 2,
                    "4 × 4  (N = 16)": 4,
                    "6 × 6  (N = 36)": 6}
    _sa_lat_str  = st.radio("Lattice (PBC)", list(_sa_lat_opts), horizontal=True, key="sa_lat")
    _sa_D        = _sa_lat_opts[_sa_lat_str]
    _sa_N        = _sa_D ** 2

    _sac1, _sac2, _sac3 = st.columns(3)
    with _sac1:
        _sa_J    = st.slider("Exchange coupling  J", 0.0, 3.0, 1.0, 0.05, key="sa_J")
    with _sac2:
        _sa_H    = st.slider("Applied field  H", 0.0, 12.0, 0.0, 0.1, key="sa_H",
                             help="Vertical marker on the plot; identifies the ground state.")
    with _sac3:
        _sa_nlev = st.slider("Levels per Sᵣ sector", 1, 6, 3, 1, key="sa_nlev")

    with st.spinner(f"Diagonalising {_sa_D}×{_sa_D} Heisenberg model…"):
        _sa_spec = _ed_spectrum(_sa_D, _sa_J)

    _sa_J_norm  = max(float(_sa_J), 1e-6)
    _sa_sorted  = sorted(_sa_spec.items())
    _HJ_fan     = np.linspace(0.0, 10.0, 600)
    _fan_clrs   = [SAGE, AMBER, BUTTER, STEEL, ROSE, MOSS, SLATE, TERRA, DARK_BRN]
    _gs_env     = np.full(len(_HJ_fan), np.inf)

    _fig_es = go.Figure()
    for _si, (Sz_int, _dat) in enumerate(_sa_sorted):
        if _dat["skipped"] or _dat["E0"] is None:
            continue
        _Sz  = Sz_int / 2.0
        _col = _fan_clrs[_si % len(_fan_clrs)]
        for _ni, _Ev in enumerate(_dat["evals"][:_sa_nlev]):
            _EJ_line = _Ev / _sa_J_norm - _HJ_fan * _Sz
            _gs_env  = np.minimum(_gs_env, _EJ_line)
            _fig_es.add_trace(go.Scatter(
                x=_HJ_fan, y=_EJ_line, mode="lines",
                line=dict(color=_col,
                          width=1.2 if _ni > 0 else 2.0,
                          dash="dot" if _ni > 0 else "solid"),
                name=f"Sᵣ={_sz_label(Sz_int)}, n={_ni}" if _ni > 0
                     else f"Sᵣ={_sz_label(Sz_int)}",
                showlegend=(_ni == 0),
                legendgroup=f"Sz{Sz_int}",
                hovertemplate=(
                    f"Sᵣ={_sz_label(Sz_int)}, n={_ni}"
                    "<br>H/J=%{x:.2f}<br>E/J=%{y:.4f}<extra></extra>"
                ),
            ))

    if not np.all(np.isinf(_gs_env)):
        _fig_es.add_trace(go.Scatter(
            x=_HJ_fan, y=_gs_env, mode="lines",
            line=dict(color=DARK_BRN if not dark_mode else OFF_WHT, width=3.0),
            name="Ground-state envelope", showlegend=True,
        ))

    _sa_HJ_marker = float(_sa_H) / _sa_J_norm
    _fig_es.add_vline(
        x=_sa_HJ_marker, line_dash="dash",
        line_color=ROSE, line_width=1.8, opacity=0.85,
        annotation_text=f"H = {_sa_H:.2f}",
        annotation_font_color=ROSE,
        annotation_position="top right",
    )
    _fig_es.update_layout(
        paper_bgcolor=T["page_bg"], plot_bgcolor=T["plot_bg"],
        height=440, margin=dict(l=60, r=20, t=20, b=50),
        xaxis=dict(title="H / J", range=[0, 10],
                   tickfont=dict(color=T["txt_mute"], size=10),
                   title_font=dict(color=T["txt_mute"]),
                   gridcolor=T["border"]),
        yaxis=dict(title="E / J" if _sa_J > 1e-6 else "E  (J = 0)",
                   tickfont=dict(color=T["txt_mute"], size=10),
                   title_font=dict(color=T["txt_mute"]),
                   gridcolor=T["border"]),
        legend=dict(bgcolor=T["card_bg"], bordercolor=T["border"],
                    font=dict(color=T["txt_main"], size=9), tracegroupgap=1),
        hoverlabel=dict(bgcolor=T["hover_bg"], font=dict(color=T["hover_txt"])),
    )
    st.plotly_chart(_fig_es, use_container_width=True)

    # ── Ground state at selected (J, H) ──────────────────────────
    _H_abs_sel   = float(_sa_H)
    _best_E_sel  = np.inf
    _best_Sz_sel = None
    for _Sz_int_s, _dat_s in _sa_spec.items():
        if _dat_s["E0"] is None:
            continue
        _Ecand = _dat_s["E0"] - _H_abs_sel * (_Sz_int_s / 2.0)
        if _Ecand < _best_E_sel:
            _best_E_sel  = _Ecand
            _best_Sz_sel = _Sz_int_s

    if _best_Sz_sel is not None:
        _gs_dat  = _sa_spec[_best_Sz_sel]
        _top     = _gs_dat["evecs_top"][0] if _gs_dat["evecs_top"] else []
        _rows_gs = ""
        for _coeff_g, _state_g in _top[:8]:
            if abs(_coeff_g) < 5e-5:
                continue
            _spins_g = "".join("↑" if s else "↓" for s in _state_g)
            _sign_g  = "+" if _coeff_g >= 0 else "−"
            _rows_gs += (
                f'<tr>'
                f'<td style="font-family:monospace;font-size:0.85rem;'
                f'color:{T["txt_main"]};padding:0.1rem 0.8rem 0.1rem 0;">'
                f'{_sign_g} {abs(_coeff_g):.4f}</td>'
                f'<td style="font-family:monospace;font-size:0.85rem;'
                f'color:{T["accent"]};letter-spacing:0.04em;">'
                f'| {_spins_g} ⟩</td>'
                f'</tr>'
            )
        _more_g      = _gs_dat["dim"] - min(len(_top), 8)
        _more_note_g = (
            f'<tr><td colspan="2" style="font-size:0.75rem;color:{T["txt_mute"]};">'
            f'… {_more_g:,} more basis states</td></tr>'
        ) if _more_g > 0 else ""
        _j0_note_g = (
            f'<br><small style="color:{T["txt_mute"]};">'
            f'J = 0: all basis states degenerate; one representative shown.</small>'
            if _sa_J < 1e-6 else ""
        )
        # Eigenvalue at selected (J, H): total = exchange part - Zeeman shift
        _E0_J   = _gs_dat["E0"] / _sa_J_norm           # H=0 sector eigenvalue / J
        _HzSz_J = _sa_HJ_marker * (_best_Sz_sel / 2.0) # (H/J) * Sz  (Zeeman contribution)
        _Etot_J = _E0_J - _HzSz_J                      # full eigenvalue / J at selected (J,H)
        st.markdown(
            f'<div class="caption-box" style="border-left:4px solid {ROSE};">' 
            f'<table style="border-collapse:collapse;width:100%;"><tr>'
            f'<td style="padding-right:2.5rem;vertical-align:top;white-space:nowrap;">'
            f'<div style="font-size:0.74rem;font-weight:600;letter-spacing:0.06em;'
            f'color:{T["txt_mute"]};margin-bottom:0.5rem;">'
            f'GROUND STATE &nbsp;&mdash;&nbsp; '
            f'J = {_sa_J:.3g} &ensp; H = {_sa_H:.3g} &ensp; H/J = {_sa_HJ_marker:.3g}'
            f'</div>'
            f'<div style="font-size:1.0rem;font-weight:700;color:{T["txt_main"]};">'
            f'S<sub>z</sub> = {_sz_label(_best_Sz_sel)}'
            f'</div>'
            f'<div style="font-size:1.3rem;font-weight:800;color:{ROSE};margin-top:0.35rem;">'
            f'E(J,H) / J = {_Etot_J:.5g}'
            f'</div>'
            f'<div style="font-size:0.82rem;color:{T["txt_mute"]};margin-top:0.3rem;line-height:1.65;">'
            f'E<sub>0</sub>/J = {_E0_J:.5g}'
            f'&ensp;<span style="font-size:0.75rem;">(exchange only, H=0)</span><br>'
            f'&minus; (H/J)&thinsp;&middot;&thinsp;S<sub>z</sub> = &minus;{_HzSz_J:.5g}'
            f'&ensp;<span style="font-size:0.75rem;">(Zeeman shift)</span>'
            f'</div>'
            f'<div style="font-size:0.78rem;color:{T["txt_mute"]};margin-top:0.3rem;">'
            f'dim = {_gs_dat["dim"]:,}'
            f'</div>'
            f'{_j0_note_g}'
            f'</td>'
            f'<td style="vertical-align:top;">'
            f'<div style="font-size:0.74rem;font-weight:600;letter-spacing:0.06em;'
            f'color:{T["txt_mute"]};margin-bottom:0.5rem;">'
            f'DOMINANT AMPLITUDES &nbsp;|\u03c8\u27e9'
            f'</div>'
            f'<table style="border-collapse:collapse;">{_rows_gs}{_more_note_g}</table>'
            f'</td></tr></table></div>',
            unsafe_allow_html=True,
        )

    with st.expander("Computation: Sz Subspace Blocking & Sparse ED", expanded=False):
        _blk_rows = "\n".join(
            f"| {_bd}×{_bd} | {_bd*_bd} | {2**(_bd*_bd):,} | "
            f"{math.comb(_bd*_bd, _bd*_bd//2):,} |"
            for _bd in (2, 4, 6)
        )
        st.markdown(
            "**Key identity:** $[\\hat{H}, \\hat{S}^z_{\\rm tot}] = 0$\n\n"
            "Only $S_z\\ge 0$ blocks are solved (time-reversal symmetry gives "
            "$E(S_z)=E(-S_z)$).\n\n"
            "| Lattice | N | Full dim | Sz = 0 block |\n"
            "|---------|---|----------|-------------|\n"
            + _blk_rows + "\n\n"
            "**Dense** (NumPy `eigh`, LAPACK): block dim ≤ 500.  \n"
            "**Sparse** (SciPy `eigsh`, Lanczos, $k=6$): 500 < dim ≤ 2 000 000.  \n"
            "**Skipped** (dim > 2M): low-$S_z$ sectors of 6×6; full solution needs QuSpin."
        )

    # ══════════════════════════════════════════════════════════════
    # SECTION B — Magnetisation Plateaus
    # ══════════════════════════════════════════════════════════════
    st.divider()
    st.markdown(
        '<p class="sec-lbl">Magnetisation Plateaus &mdash; '
        '⟨Mᵣ⟩ = Sᵣ / N &nbsp;vs&nbsp; H / J</p>',
        unsafe_allow_html=True,
    )

    _sb_lat_opts = {"2 × 2  (N = 4)": 2,
                    "4 × 4  (N = 16)": 4,
                    "6 × 6  (N = 36)": 6}
    _sb_lat_str  = st.radio("Lattice (PBC)", list(_sb_lat_opts), horizontal=True, key="sb_lat")
    _sb_D        = _sb_lat_opts[_sb_lat_str]
    _sb_N        = _sb_D ** 2

    _sbc1, _sbc2 = st.columns(2)
    with _sbc1:
        _sb_J    = st.slider("Exchange coupling  J", 0.05, 3.0, 1.0, 0.05, key="sb_J")
    with _sbc2:
        _sb_Hmax = st.slider("H / J  axis maximum", 1.0, 14.0, 8.0, 0.5, key="sb_Hmax")

    with st.spinner(f"Solving {_sb_D}×{_sb_D} for magnetisation…"):
        _sb_spec = _ed_spectrum(_sb_D, _sb_J)

    _sb_n_skip = sum(1 for d in _sb_spec.values() if d["skipped"])
    _H_arr_J   = np.linspace(0.0, float(_sb_Hmax), 900)
    _Mz_arr    = np.zeros(len(_H_arr_J))
    _Sz_gs_arr = np.zeros(len(_H_arr_J))

    for _i, _hj in enumerate(_H_arr_J):
        _H_abs   = _hj * _sb_J
        _best_E  = np.inf
        _best_Sz = 0.0
        for _Sz_int, _data in _sb_spec.items():
            if _data["E0"] is None:
                continue
            _Sz = _Sz_int / 2.0
            _E  = _data["E0"] - _H_abs * _Sz
            if _E < _best_E:
                _best_E  = _E
                _best_Sz = _Sz
        _Mz_arr[_i]    = _best_Sz / _sb_N
        _Sz_gs_arr[_i] = _best_Sz

    _diff      = np.diff(_Sz_gs_arr)
    _trans_idx = np.where(_diff != 0)[0]
    _trans_HJ  = _H_arr_J[_trans_idx + 1]

    _fig_mag = go.Figure()
    _fig_mag.add_trace(go.Scatter(
        x=_H_arr_J, y=_Mz_arr, mode="lines",
        line=dict(color=SAGE, width=2.5, shape="hv"),
        name="⟨Mᵣ⟩ = Sᵣ / N",
        hovertemplate="H/J = %{x:.3f}<br>⟨Mz⟩ = %{y:.4f}<extra></extra>",
    ))
    for _th in _trans_HJ:
        _fig_mag.add_vline(x=float(_th), line_dash="dot",
                           line_color=AMBER, line_width=1.3, opacity=0.75)

    _annotated_sz = set()
    for _i, _sz in enumerate(_Sz_gs_arr):
        if _sz not in _annotated_sz:
            _annotated_sz.add(_sz)
            _fig_mag.add_annotation(
                x=_H_arr_J[_i] + 0.05 * _sb_Hmax,
                y=_sz / _sb_N + 0.013,
                text=f"Sᵣ={int(_sz)}",
                showarrow=False,
                font=dict(size=8.5, color=T["txt_mute"]),
                xanchor="left",
            )

    _fig_mag.update_layout(
        paper_bgcolor=T["page_bg"], plot_bgcolor=T["plot_bg"],
        height=400, margin=dict(l=60, r=30, t=20, b=50),
        xaxis=dict(
            title="H / J", range=[0, _sb_Hmax],
            tickfont=dict(color=T["txt_mute"], size=10),
            title_font=dict(color=T["txt_mute"]),
            gridcolor=T["border"],
        ),
        yaxis=dict(
            title="⟨Mᵣ⟩ = Sᵣ / N",
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

    _sb_skip_note = (
        f"&bull; {_sb_n_skip} low-S<sub>z</sub> sector(s) skipped (dim > 2M). "
        if _sb_n_skip else ""
    )
    st.markdown(
        f'<div class="caption-box">'
        f'Amber dotted lines: critical fields '
        f'H<sub>c</sub>/J = [E<sub>0</sub>(S<sub>z</sub>+1)−'
        f'E<sub>0</sub>(S<sub>z</sub>)] / J. '
        f'⟨M<sub>z</sub>⟩ saturates at 1/2 at H<sub>sat</sub>/J = 4. '
        f'Each plateau step = 1/N. '
        f'{_sb_skip_note}'
        f'</div>',
        unsafe_allow_html=True,
    )

    with st.expander(
        "Thermodynamic Limit N → ∞ : AFM–FM Transition & Critical Field",
        expanded=False,
    ):
        st.markdown(
            "**Finite-size plateaus vs. the thermodynamic limit**\n\n"
            "For a finite lattice the magnetisation curve is a staircase with $N/2$ discrete "
            "steps of height $\\Delta\\langle M_z\\rangle = 1/N$. "
            "As $N\\to\\infty$ the steps become infinitely dense and merge into a "
            "**smooth, continuous curve** from $\\langle M_z\\rangle = 0$ (at $H=0$) to "
            "$\\langle M_z\\rangle = 1/2$ (full polarisation at $H = H_{sat}$).\n\n"
            "---\n\n"
            "**AFM $\\to$ FM transition**\n\n"
            "At $H=0$ the isotropic Heisenberg antiferromagnet has $\\langle M_z\\rangle=0$. "
            "As the field grows it becomes energetically favourable for the ground state to "
            "jump to successive $S_z$ sectors. "
            "In the thermodynamic limit these crossings converge to a single "
            "**quantum phase transition** at\n"
            "$$\\left(\\frac{H}{J}\\right)_c = \\lim_{N\\to\\infty}"
            "\\frac{E_0(S_z^*+1) - E_0(S_z^*)}{J}$$\n"
            "where $S_z^*$ is the last sector before the transition. "
            "For the 2-D square-lattice Heisenberg model (spin-$1/2$, four nearest neighbours) "
            "linear spin-wave theory gives\n"
            "$$\\left(\\frac{H}{J}\\right)_c = H_{sat}/J = 4$$\n"
            "There is **no intermediate spin-flop phase** at $T=0$: the system goes directly "
            "from the **AFM phase** ($\\langle M_z\\rangle=0$) to the **FM (polarised) phase** "
            "($\\langle M_z\\rangle=1/2$) at a single critical field.\n\n"
            "---\n\n"
            "**Finite-size extrapolation**\n\n"
            "Plot the lowest critical field $H_c^{(1)}/J = [E_0(S_z=1)-E_0(S_z=0)]/J$ "
            "vs $1/\\sqrt{N}$ for the lattices available here ($N=4,16,36$). "
            "Extrapolating to $1/\\sqrt{N}\\to 0$ converges to $(H/J)_c \\approx 4$, "
            "consistent with the spin-wave result."
        )


# ══════════════════════════════════════════════════════════════
# TAB 2 — BEC Mixture Calculator
# ══════════════════════════════════════════════════════════════
with tab_bec:
    import scipy.constants as _sc
    from scipy.optimize import fsolve as _fsolve
    import matplotlib.pyplot as _plt

    # ── Physics solver ────────────────────────────────────────────
    @st.cache_data(show_spinner=False)
    def _solve_tf(mB_amu, mF_amu, fB_Hz, fF_Hz, NB, NF, aB_nm, aF_nm, aBF_nm, n_pts=500):
        """
        Thomas-Fermi solver for a two-component BEC mixture in a 3-D spherical trap.

        Regime map (D = gBB*gFF - gBF**2):
          aBF = 0              : Non-interacting  (independent TF parabolas)
          aBF < 0, D > 0       : Attractive – stable  (coupled TF, profiles compressed)
          aBF < 0, D <= 0      : Attractive – collapse risk  (single-species, warning)
          aBF > 0, D > 0       : Miscible repulsive  (coupled TF, profiles expanded)
          aBF > 0, D <= 0      : Phase-separated  (exclusive-occupation / core-shell)

        Phase-separated local density: at each r the species with the higher
        intraspecies pressure P_i = g_ii * n_i_ss^2 occupies that point exclusively.
        This is the correct LDA treatment of demixing in the TF limit.
        """
        hbar = _sc.hbar
        amu  = _sc.u
        mB   = mB_amu * amu
        mF   = mF_amu * amu
        wB   = 2 * np.pi * fB_Hz
        wF   = 2 * np.pi * fF_Hz
        aB   = aB_nm  * 1e-9
        aF   = aF_nm  * 1e-9
        aBF  = aBF_nm * 1e-9

        gBB = 4 * np.pi * hbar**2 * aB  / mB
        gFF = 4 * np.pi * hbar**2 * aF  / mF
        gBF = 2 * np.pi * hbar**2 * aBF * (1.0/mB + 1.0/mF)

        D = gBB * gFF - gBF**2

        # ── Regime classification ─────────────────────────────────
        if abs(aBF_nm) < 1e-3:
            regime    = "Non-interacting"
            miscible  = True
        elif aBF_nm < 0:
            if D > 0:
                regime   = "Attractive (stable)"
                miscible = True
            else:
                regime   = "Attractive (collapse risk)"
                miscible = False
        else:
            if D > 0:
                regime   = "Miscible (repulsive)"
                miscible = True
            else:
                regime   = "Phase-separated"
                miscible = False

        # ── Harmonic oscillator length & initial mu guesses ───────
        a_ho_B = np.sqrt(hbar / (mB * wB))
        a_ho_F = np.sqrt(hbar / (mF * wF))
        mu_B0  = hbar * wB / 2 * max((15 * NB * abs(aB) / a_ho_B)**(2/5), 0.1)
        mu_F0  = hbar * wF / 2 * max((15 * NF * abs(aF) / a_ho_F)**(2/5), 0.1)
        r_max  = max(np.sqrt(2*mu_B0 / (mB*wB**2)),
                     np.sqrt(2*mu_F0 / (mF*wF**2))) * 2.0
        r = np.linspace(0.0, r_max, n_pts)

        # ── Local density at radius ri ────────────────────────────
        def _local(ri, muB, muF):
            VB    = 0.5 * mB * wB**2 * ri**2
            VF    = 0.5 * mF * wF**2 * ri**2
            nBss  = max(0.0, (muB - VB) / gBB)   # single-species TF
            nFss  = max(0.0, (muF - VF) / gFF)

            if regime == "Non-interacting":
                return nBss, nFss

            if regime == "Phase-separated":
                # Exclusive occupation: species with higher intraspecies pressure wins
                # P_i = g_ii * n_i^2 / 2  (energy density of that species alone)
                PB = gBB * nBss * nBss
                PF = gFF * nFss * nFss
                return (nBss, 0.0) if PB >= PF else (0.0, nFss)

            if regime == "Attractive (collapse risk)":
                # Mean-field is unstable; show single-species profiles as approximation
                return nBss, nFss

            # Miscible regimes: coupled TF equations (D > 0 guaranteed here)
            nB = (gFF * (muB - VB) - gBF * (muF - VF)) / D
            nF = (gBB * (muF - VF) - gBF * (muB - VB)) / D

            if nB < 0 and nF < 0:
                return 0.0, 0.0
            if nB < 0:
                return 0.0, nFss
            if nF < 0:
                return nBss, 0.0
            return nB, nF

        def _profiles(muB, muF):
            nb = np.zeros(n_pts)
            nf = np.zeros(n_pts)
            for i, ri in enumerate(r):
                nb[i], nf[i] = _local(ri, muB, muF)
            return nb, nf

        def _res(mus):
            nb, nf = _profiles(mus[0], mus[1])
            NB_got = 4 * np.pi * np.trapz(nb * r**2, r)
            NF_got = 4 * np.pi * np.trapz(nf * r**2, r)
            dB = (NB_got - NB) / NB if NB > 0 else 0.0
            dF = (NF_got - NF) / NF if NF > 0 else 0.0
            return [dB, dF]

        try:
            sol, _, flag, _ = _fsolve(_res, [mu_B0, mu_F0], full_output=True)[:4]
            muB, muF = sol if flag == 1 else (mu_B0, mu_F0)
        except Exception:
            muB, muF = mu_B0, mu_F0

        nb, nf = _profiles(muB, muF)

        def _rtf(n_arr):
            mx = n_arr.max()
            if mx <= 0:
                return 0.0
            mask = n_arr > mx * 1e-4
            return float(r[mask][-1]) * 1e6 if mask.any() else 0.0

        return dict(
            r_um      = r * 1e6,
            nB        = nb * 1e-6,
            nF        = nf * 1e-6,
            R_B       = _rtf(nb),
            R_F       = _rtf(nf),
            n0_B      = float(nb[0]) * 1e-6,
            n0_F      = float(nf[0]) * 1e-6,
            muB_nK    = muB / (_sc.k * 1e-9),
            muF_nK    = muF / (_sc.k * 1e-9),
            gBF       = gBF,
            gBB       = gBB,
            gFF       = gFF,
            D         = D,
            miscible  = miscible,
            regime    = regime,
            a_ho_B_um = float(np.sqrt(_sc.hbar / (mB_amu*_sc.u * 2*np.pi*fB_Hz))) * 1e6,
        )

    # ── Header ────────────────────────────────────────────────────
    st.markdown("""
<div class="hero">
  <h1 style="font-size:1.6rem;">4 · Numerical Validation — BEC Mixture Density Profiles</h1>
  <p>
    Two-component Bose-Einstein condensate in a 3-D spherical harmonic trap.
    Solve the coupled Thomas-Fermi equations to obtain density profiles n<sub>B</sub>(r),
    n<sub>F</sub>(r) and compare four physically distinct regimes:
    non-interacting, attractive (stable), miscible repulsive, and phase-separated.
  </p>
</div>
""", unsafe_allow_html=True)

    # ── Assumptions expander ──────────────────────────────────────
    with st.expander("Model & Assumptions", expanded=False):
        st.markdown(r"""
**Thomas-Fermi (TF) approximation** — kinetic energy neglected; valid when $N\,a/a_{ho}\gg 1$.

**Coupling constants (SI):**
$$g_{BB}=\frac{4\pi\hbar^2 a_B}{m_B},\quad g_{FF}=\frac{4\pi\hbar^2 a_F}{m_F},\quad
g_{BF}=2\pi\hbar^2 a_{BF}\!\left(\frac{1}{m_B}+\frac{1}{m_F}\right)$$

**Regime map** — let $D = g_{BB}g_{FF}-g_{BF}^2$:

| $a_{BF}$ | sign of $g_{BF}$ | $D$ | Regime |
|----------|-----------------|-----|--------|
| 0 | — | + | Non-interacting |
| < 0 | negative (attractive) | > 0 | Attractive – stable (miscible) |
| < 0 | negative (attractive) | ≤ 0 | Attractive – collapse risk |
| > 0 | positive (repulsive) | > 0 | Miscible repulsive |
| > 0 | positive (repulsive) | ≤ 0 | **Phase-separated** (core-shell) |

**Phase-separation solver:** In the immiscible ($D\le 0$, $g_{BF}>0$) regime the species demix
spatially. At each radius $r$ only the species with the higher intraspecies pressure
$P_i = g_{ii}\,n_i^{(0)}(r)^2$ occupies that point; the other is zero.
This exclusive-occupation rule is the LDA implementation of the Thomas-Fermi demixing condition
and produces the experimentally observed core-shell structure.

**Chemical potentials** $\mu_B,\mu_F$ are found by enforcing
$4\pi\!\int_0^\infty n_i(r)\,r^2\,dr=N_i$.
""")

    # ── Parameter inputs ──────────────────────────────────────────
    st.markdown('<p class="sec-lbl">Parameters</p>', unsafe_allow_html=True)
    _c1, _c2, _c3 = st.columns(3)
    with _c1:
        st.markdown("**Species B** (e.g. ⁸⁷Rb)")
        _mB = st.number_input("m_B (amu)",       1.0,  300.0,  87.0, 1.0,  key="bec_mB")
        _fB = st.number_input("ω_B / 2π  (Hz)", 1.0, 2000.0, 100.0, 10.0, key="bec_fB")
        _NB = st.number_input("N_B  (atoms)",    100,  500000, 50000, 1000, key="bec_NB")
        _aB = st.number_input("a_B (nm)",        0.01, 50.0,   5.29,  0.1,  key="bec_aB",
                               help="⁸⁷Rb: a_B ≈ 5.29 nm (100 a₀)")
    with _c2:
        st.markdown("**Species F** (e.g. ⁴¹K)")
        _mF = st.number_input("m_F (amu)",       1.0,  300.0,  41.0, 1.0,  key="bec_mF")
        _fF = st.number_input("ω_F / 2π  (Hz)", 1.0, 2000.0, 150.0, 10.0, key="bec_fF")
        _NF = st.number_input("N_F  (atoms)",    100,  500000, 30000, 1000, key="bec_NF")
        _aF = st.number_input("a_F (nm)",        0.01, 50.0,   3.39,  0.1,  key="bec_aF",
                               help="⁴¹K: a_F ≈ 3.39 nm (64 a₀)")
    with _c3:
        st.markdown("**Interspecies scattering lengths**")
        _aBF_neg  = st.number_input(
            "a_BF attractive (nm)", -300.0, -0.01, -3.0, 0.5, key="bec_n",
            help="Negative: g_BF < 0. Stable while |g_BF| < sqrt(g_BB*g_FF).")
        _aBF_weak = st.number_input(
            "a_BF miscible repulsive (nm)", 0.01, 300.0, 2.0, 0.5, key="bec_w",
            help="Positive and small: g_BF > 0, D > 0 (miscible).")
        _aBF_sep  = st.number_input(
            "a_BF phase-sep (nm)", 0.01, 500.0, 10.0, 1.0, key="bec_s",
            help="Large positive: g_BF^2 > g_BB*g_FF triggers phase separation.")
        st.caption("a_BF = 0 (non-interacting) is always included as the baseline.")
        _scan_lo = st.number_input("Scan min (nm)", -50.0,  0.0, -10.0, 1.0, key="bec_slo")
        _scan_hi = st.number_input("Scan max (nm)",   0.0, 300.0, 15.0, 1.0, key="bec_shi")
        _n_scan  = st.slider("Scan points", 5, 60, 30, key="bec_nscan")

    # ── Solve four representative cases ───────────────────────────
    _case_aBF    = [0.0, float(_aBF_neg), float(_aBF_weak), float(_aBF_sep)]
    _case_labels = [
        "Non-interacting\n(a_BF = 0)",
        f"Attractive\n(a_BF = {_aBF_neg:.1f} nm)",
        f"Miscible repulsive\n(a_BF = {_aBF_weak:.1f} nm)",
        f"Phase separation\n(a_BF = {_aBF_sep:.1f} nm)",
    ]

    with st.spinner("Solving Thomas-Fermi equations…"):
        _results = {
            lbl: _solve_tf(_mB, _mF, _fB, _fF, _NB, _NF, _aB, _aF, abf)
            for lbl, abf in zip(_case_labels, _case_aBF)
        }

    # ── Coupling constants & miscibility display ──────────────────
    st.markdown('<p class="sec-lbl">Coupling Constants &amp; Miscibility</p>',
                unsafe_allow_html=True)
    _ref0      = _results[_case_labels[0]]
    _gBB_SI    = _ref0["gBB"]
    _gFF_SI    = _ref0["gFF"]
    _misc_thr  = float(np.sqrt(_gBB_SI * _gFF_SI))

    def _g_fmt(g):
        if g == 0:
            return "0 J·m³"
        exp      = int(np.floor(np.log10(abs(g))))
        mantissa = g / 10**exp
        return f"{mantissa:.3f}&thinsp;&times;&thinsp;10<sup>{exp}</sup> J·m³"

    # Compute critical aBF for display
    _aBF_crit_nm = None
    if _gBB_SI > 0 and _gFF_SI > 0:
        _coeff = 2 * np.pi * _sc.hbar**2 * (1.0/(_mB*_sc.u) + 1.0/(_mF*_sc.u))
        _aBF_crit_nm = float(_misc_thr / _coeff) * 1e9

    _gbf_rows = ""
    for lbl in _case_labels:
        _res = _results[lbl]
        _sym = "✓" if _res["miscible"] else "✗"
        _col = "#5a8a5a" if _res["miscible"] else "#a84e3c"
        _gbf_rows += (
            f'<li><b>{lbl.replace(chr(10), " ")}</b>: '
            f'g<sub>BF</sub> = {_g_fmt(_res["gBF"])}&ensp;&mdash;&ensp;'
            f'<span style="color:{_col};font-weight:600;">'
            f'{_sym} {_res["regime"]}</span></li>'
        )

    _crit_str = (
        f'Critical |a<sub>BF</sub>| = {_aBF_crit_nm:.2f} nm '
        f'(above this threshold: attractive side → collapse risk; '
        f'repulsive side → phase separation)'
        if _aBF_crit_nm else ""
    )
    st.markdown(
        f'<div class="caption-box">'
        f'<b>g<sub>BB</sub></b> = {_g_fmt(_gBB_SI)}&ensp;&ensp;'
        f'<b>g<sub>FF</sub></b> = {_g_fmt(_gFF_SI)}<br>'
        f'Miscibility threshold &nbsp;√(g<sub>BB</sub> g<sub>FF</sub>) = '
        f'{_g_fmt(_misc_thr)}'
        f'{"<br>" + _crit_str if _crit_str else ""}'
        f'<ul style="margin:0.6rem 0 0;padding-left:1.4rem;">{_gbf_rows}</ul>'
        f'<small style="color:{T["txt_mute"]};">'
        f'Phase separation only for <em>positive</em> g<sub>BF</sub> exceeding the threshold. '
        f'Negative g<sub>BF</sub> drives attraction, not demixing.</small>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Plot 1: density profiles ──────────────────────────────────
    st.markdown('<p class="sec-lbl">Density Profiles</p>', unsafe_allow_html=True)

    _fig1, _axes = _plt.subplots(1, 4, figsize=(16, 4.2), sharey=False)
    _fig1.patch.set_facecolor("none")
    for _ax, (_lbl, _res) in zip(_axes, _results.items()):
        _r   = _res["r_um"]
        _nBp = _res["nB"]
        _nFp = _res["nF"]
        _ax.plot(_r, _nBp, color=SAGE, lw=2.2, label="Species B (⁸⁷Rb)")
        _ax.plot(_r, _nFp, color=ROSE, lw=2.2, label="Species F (⁴¹K)", ls="--")
        _ax.set_facecolor("none")
        for _sp in _ax.spines.values():
            _sp.set_color(OFF_WHT)
        _ax.tick_params(colors=DARK_BRN, labelsize=7)
        _ax.set_xlabel("r  (μm)", fontsize=8, color=DARK_BRN)
        _ax.set_ylabel("n  (cm⁻³)", fontsize=8, color=DARK_BRN)
        _title = _lbl.replace("\n", "  ") + f"\n[{_res['regime']}]"
        _ax.set_title(_title, fontsize=7.5, color=DARK_BRN, pad=4)
        _ax.legend(fontsize=6.5, facecolor=OFF_WHT, edgecolor=OFF_WHT, labelcolor=DARK_BRN)
        for _R, _col in [(_res["R_B"], SAGE), (_res["R_F"], ROSE)]:
            if _R > 0:
                _ax.axvline(_R, color=_col, lw=0.8, ls=":", alpha=0.65)
        # Collapse-risk warning banner
        if _res["regime"] == "Attractive (collapse risk)":
            _ax.text(0.5, 0.92, "⚠ Collapse risk", transform=_ax.transAxes,
                     ha="center", va="top", fontsize=7, color=TERRA,
                     bbox=dict(boxstyle="round,pad=0.2", fc=OFF_WHT, ec=TERRA, lw=0.8))
    _fig1.tight_layout()
    st.pyplot(_fig1, use_container_width=True)
    _plt.close(_fig1)
    st.caption(
        f"Species B: ⁸⁷Rb ({_mB} amu, ω_B/2π = {_fB} Hz, "
        f"N_B = {int(_NB)}, a_B = {_aB} nm).  "
        f"Species F: ⁴¹K ({_mF} amu, ω_F/2π = {_fF} Hz, "
        f"N_F = {int(_NF)}, a_F = {_aF} nm).  "
        "Dotted verticals: Thomas-Fermi radii.  "
        "Phase-separated panel uses exclusive-occupation LDA: at each r only the "
        "species with higher intraspecies pressure P = g_ii × n_i² is present, "
        "producing the core-shell structure."
    )

    # ── Plot 2: scan over a_BF ────────────────────────────────────
    st.markdown('<p class="sec-lbl">TF Radius &amp; Peak Density vs a<sub>BF</sub></p>',
                unsafe_allow_html=True)
    _aBF_arr = np.linspace(float(_scan_lo), float(_scan_hi), int(_n_scan))
    with st.spinner("Running a_BF scan…"):
        _scan = [_solve_tf(_mB, _mF, _fB, _fF, _NB, _NF, _aB, _aF, float(_a), n_pts=300)
                 for _a in _aBF_arr]

    _fig2, (_ax_r, _ax_n) = _plt.subplots(1, 2, figsize=(12, 4))
    _fig2.patch.set_facecolor("none")
    for _axx in (_ax_r, _ax_n):
        _axx.set_facecolor("none")
        _axx.tick_params(colors=DARK_BRN, labelsize=8)
        for _sp in _axx.spines.values():
            _sp.set_color(OFF_WHT)
        _axx.axvline(0, color=DARK_BRN, lw=0.7, ls="--", alpha=0.5, label="a_BF = 0")
        if _aBF_crit_nm:
            _axx.axvline( _aBF_crit_nm, color=AMBER, lw=0.9, ls=":", alpha=0.8,
                          label=f"a_crit = +{_aBF_crit_nm:.1f} nm")
            _axx.axvline(-_aBF_crit_nm, color=AMBER, lw=0.9, ls=":", alpha=0.8)

    _ax_r.plot(_aBF_arr, [s["R_B"] for s in _scan], color=SAGE,  lw=2.0, label="R_TF (B)")
    _ax_r.plot(_aBF_arr, [s["R_F"] for s in _scan], color=ROSE,  lw=2.0, ls="--", label="R_TF (F)")
    _ax_r.set_xlabel("a_BF  (nm)", color=DARK_BRN)
    _ax_r.set_ylabel("Thomas-Fermi radius  (μm)", color=DARK_BRN)
    _ax_r.set_title("TF Radii vs a_BF", color=DARK_BRN)
    _ax_r.legend(facecolor=OFF_WHT, edgecolor=OFF_WHT, labelcolor=DARK_BRN, fontsize=8)

    _ax_n.plot(_aBF_arr, [s["n0_B"] for s in _scan], color=SAGE,  lw=2.0, label="n₀ (B)")
    _ax_n.plot(_aBF_arr, [s["n0_F"] for s in _scan], color=ROSE,  lw=2.0, ls="--", label="n₀ (F)")
    _ax_n.set_xlabel("a_BF  (nm)", color=DARK_BRN)
    _ax_n.set_ylabel("Peak density  (cm⁻³)", color=DARK_BRN)
    _ax_n.set_title("Peak Density vs a_BF", color=DARK_BRN)
    _ax_n.legend(facecolor=OFF_WHT, edgecolor=OFF_WHT, labelcolor=DARK_BRN, fontsize=8)

    _fig2.tight_layout()
    st.pyplot(_fig2, use_container_width=True)
    _plt.close(_fig2)
    _crit_note = (
        f"Amber dotted verticals mark the miscibility threshold |a_BF| = {_aBF_crit_nm:.1f} nm.  "
        if _aBF_crit_nm else ""
    )
    st.caption(
        f"Scan over a_BF ∈ [{_scan_lo:.0f}, {_scan_hi:.0f}] nm.  "
        + _crit_note
        + "Left of zero (attractive): both clouds compress — R_TF shrinks, n₀ rises. "
        "Beyond the negative threshold the mean-field becomes unstable (collapse).  "
        "Right of zero (repulsive): clouds swell until the threshold, then demix into "
        "core-shell geometry — the core species peak density jumps while the shell species "
        "density at r = 0 drops toward zero."
    )

    # ── Summary table ─────────────────────────────────────────────
    st.markdown('<p class="sec-lbl">Summary Table</p>', unsafe_allow_html=True)
    _tbl = []
    for _lbl, _res in _results.items():
        _abf_v = _case_aBF[_case_labels.index(_lbl)]
        _tbl.append({
            "Case":          _lbl.replace("\n", " "),
            "a_BF (nm)":     f"{_abf_v:.1f}",
            "Regime":        _res["regime"],
            "R_TF B (μm)": f"{_res['R_B']:.2f}",
            "R_TF F (μm)": f"{_res['R_F']:.2f}",
            "n₀_B (cm⁻³)": f"{_res['n0_B']:.3e}",
            "n₀_F (cm⁻³)": f"{_res['n0_F']:.3e}",
            "μ_B (nK)":  f"{_res['muB_nK']:.1f}",
            "μ_F (nK)":  f"{_res['muF_nK']:.1f}",
        })
    st.dataframe(pd.DataFrame(_tbl), use_container_width=True, hide_index=True)

    # ── Physics commentary ────────────────────────────────────────
    with st.expander("Physics Commentary", expanded=True):
        _a_ho_str = f"{_results[_case_labels[0]]['a_ho_B_um']:.3f}"
        _crit_str2 = (
            f"The miscibility threshold is $|a_{{BF}}^{{\\rm crit}}| \\approx {_aBF_crit_nm:.2f}$~nm."
            if _aBF_crit_nm else ""
        )
        st.markdown(f"""
**Chosen parameters** &mdash; B: $^{{87}}$Rb ({_mB} amu, $\\omega_B/2\\pi={_fB}$ Hz,
$N_B={int(_NB)}$, $a_B={_aB}$ nm); F: $^{{41}}$K ({_mF} amu, $\\omega_F/2\\pi={_fF}$ Hz,
$N_F={int(_NF)}$, $a_F={_aF}$ nm).
Harmonic oscillator length $a_{{ho}}^B \\approx {_a_ho_str}\\,\\mu$m.
{_crit_str2}

---

**Non-interacting ($a_{{BF}}=0$):** Species B and F are completely independent.
Each forms its own Thomas-Fermi inverted-parabola profile
$n_i(r) = \\max\\!\\left(0,\\,\\frac{{\\mu_i - V_i(r)}}{{g_{{ii}}}}\\right)$.
The TF radius is $R_{{TF}}^i = a_{{ho}}^i(15N_ia_i/a_{{ho}}^i)^{{1/5}}$.

**Attractive ($a_{{BF}}<0$, $g_{{BF}}<0$):** Interspecies attraction is a
*negative* contribution to the interaction energy matrix.  The species pull each
other toward the trap centre: both $R_{{TF}}$ **shrink** and peak densities
**rise** as $|a_{{BF}}|$ increases.  The system remains stable as long as
$g_{{BF}}^2 < g_{{BB}}g_{{FF}}$ (i.e. $D>0$).  Once $D\\le 0$ the mean-field is
mechanically unstable and the mixture **collapses** &mdash; this is not phase
separation.  (Profiles shown in the collapse-risk panel are single-species TF
curves used as an approximation; the true solution diverges.)

**Miscible repulsive ($a_{{BF}}>0$, $D>0$):** Interspecies repulsion pushes the
clouds apart.  Both $R_{{TF}}$ **expand** and peak densities **decrease**
moderately relative to the non-interacting baseline.  Spatial overlap is reduced
but both species still co-exist everywhere.

**Phase-separated ($a_{{BF}}>0$, $D\\le 0$):** The repulsive cross-interaction
exceeds the geometric mean of the intraspecies interactions.  The coupled
Thomas-Fermi equations no longer have a positive-definite solution at every
point; the energetically favoured state is **spatial demixing**.  In the LDA
implementation, at each radius $r$ only the species with the higher intraspecies
pressure $P_i = g_{{ii}}\\,n_i^{{(0)}}(r)^2$ is present.  The result is a
**core-shell structure**: the species with stronger self-repulsion (larger
$g_{{ii}}N_i$) occupies the centre, while the other is expelled to a surrounding
shell.  The core-species density at $r=0$ rises; the expelled-species density
there drops toward zero.
""")
