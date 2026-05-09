import numpy as np
from itertools import combinations
import streamlit as st
import plotly.graph_objects as go

# ── Colours (same as main app) ─────────────────────────────────
SAGE     = "#7D8B5A"
ROSE     = "#C4907E"
SLATE    = "#3D5F78"
DARK_BRN = "#4E3428"
OFF_WHT  = "#E5E0D8"
AMBER    = "#C9983A"
STEEL    = "#7A9DAC"

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
        "hover_bg":  "#EDE7DA",
        "hover_txt": "#2A2018",
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
        "hover_bg":  "#302A22",
        "hover_txt": "#E5E0D8",
    },
}

st.set_page_config(page_title="Zeeman Analysis", layout="wide")

_, col_toggle = st.columns([6, 1])
with col_toggle:
    dark_mode = st.toggle("Dark mode", value=False)

T = THEMES["dark"] if dark_mode else THEMES["light"]

st.markdown(f"""
<style>
  .stApp {{ background-color:{T['page_bg']}; color:{T['txt_main']}; font-family:'Georgia',serif; }}
  header[data-testid="stHeader"] {{ background:transparent; }}
  div[data-testid="stToggle"] label p {{ color:{T['txt_mute']} !important; font-size:0.82rem !important; }}
  .hero {{
    background:{T['hero_grad']}; border:1px solid {T['border']};
    border-radius:16px; padding:1.9rem 2.5rem 1.5rem; margin-bottom:1.2rem;
  }}
  .hero h1 {{ font-size:2rem; font-weight:700; color:{T['accent']}; margin:0 0 0.4rem; }}
  .hero p  {{ color:{T['txt_mute']}; font-size:0.95rem; line-height:1.72; margin:0; }}
  .sec-lbl {{
    font-size:0.72rem; color:{T['txt_mute']}; text-transform:uppercase;
    letter-spacing:1.5px; margin:1.4rem 0 0.4rem;
    border-left:2px solid {SAGE}; padding-left:0.6rem;
  }}
  .card {{
    background:{T['card_bg']}; border:1px solid {T['border']};
    border-radius:12px; padding:1rem 1.3rem; margin-bottom:0.7rem;
  }}
  .caption-box {{
    background:{T['card_bg']}; border-left:3px solid {SAGE};
    border-radius:0 8px 8px 0; padding:0.7rem 1.1rem;
    color:{T['txt_mute']}; font-size:0.83rem; line-height:1.65; margin-top:0.6rem;
  }}
  label p, .stSlider label p {{ color:{T['txt_mute']} !important; font-size:0.87rem !important; }}
</style>
""", unsafe_allow_html=True)

# ── Hero ───────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
  <h1>Zeeman Analysis — 4-Site Heisenberg Ring</h1>
  <p>
    We study the spin-½ Heisenberg ring on <em>N = 4</em> sites with an external magnetic field <em>H</em>
    and antiferromagnetic exchange coupling <em>J &gt; 0</em>.
    The total Hamiltonian is
    <em>Ĥ = J Σ<sub>i</sub> Ŝ<sub>i</sub>·Ŝ<sub>i+1</sub> − H Σ<sub>i</sub> Ŝ<sup>z</sup><sub>i</sub></em>
    with periodic boundary conditions.
    We analyze each S<sub>z</sub> sector and derive the <strong>magnetization staircase</strong>.
  </p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# SECTION 1 — Zeeman term proof
# ══════════════════════════════════════════════════════════════════
st.markdown('<p class="sec-lbl">1 · Zeeman Term: H Σ Ŝ<sup>z</sup><sub>i</sub> |φ⟩ = 0</p>',
            unsafe_allow_html=True)

with st.expander("Proof that the external field does not shift or split the Sz = 0 sector", expanded=True):
    st.markdown(r"""
The Zeeman term couples the total spin projection to the external field $H$:

$$
\hat{H}_Z \;=\; H \sum_{i=0}^{3} \hat{S}^z_i \;=\; H\,\hat{S}^z_{\mathrm{total}},
\qquad
\hat{S}^z_{\mathrm{total}} = \sum_i \hat{S}^z_i = \frac{1}{2}(\hat{N}_{\uparrow} - \hat{N}_{\downarrow}).
$$

**Claim.** For any state $|\varphi\rangle$ in the $S_z = 0$ sector, $\;\hat{H}_Z|\varphi\rangle = 0$.

---

**Proof.**

*Step 1 — every basis state is an eigenstate of $\hat{S}^z_{\mathrm{total}}$ with eigenvalue 0.*

The $S_z = 0$ sector is built from all configurations with exactly $k = 2$ spin-up and $k = 2$ spin-down electrons
on the 4 sites ($N_\uparrow = N_\downarrow = 2$). Applying $\hat{S}^z_{\mathrm{total}}$ to any such basis state $|b\rangle$:

$$
\hat{S}^z_{\mathrm{total}}\,|b\rangle
  = \frac{1}{2}(N_{\uparrow} - N_{\downarrow})\,|b\rangle
  = \frac{1}{2}(2 - 2)\,|b\rangle = 0.
$$

*Step 2 — linearity extends the result to the whole sector.*

Any $|\varphi\rangle \in \mathcal{H}_{S_z=0}$ is a superposition $|\varphi\rangle = \sum_b c_b\,|b\rangle$. By linearity:

$$
\hat{H}_Z\,|\varphi\rangle
  = H \sum_b c_b\;\hat{S}^z_{\mathrm{total}}\,|b\rangle
  = H \sum_b c_b \cdot 0
  = 0. \qquad \blacksquare
$$

**Physical consequence.** The Zeeman energy is identically zero for every state in $\mathcal{H}_{S_z=0}$.
The field $H$ **neither shifts** the energies of $S_z = 0$ eigenstates **nor mixes** them with
states in other sectors — the subspace is an *invariant eigenspace* of $\hat{H}_Z$ with eigenvalue $0$.
In contrast, the $S_z = \pm 1$ and $S_z = \pm 2$ sectors do feel the field (see Section 4).
""")

# ══════════════════════════════════════════════════════════════════
# SECTION 2 — Hamiltonian construction
# ══════════════════════════════════════════════════════════════════
st.markdown('<p class="sec-lbl">2 · Hamiltonian Construction — the 6 × 6 matrix for Sz = 0</p>',
            unsafe_allow_html=True)

# Build the 6×6 Hamiltonian numerically (J=1 for display)
N_SITES = 4
BONDS   = [(i, (i + 1) % N_SITES) for i in range(N_SITES)]

# Sz=0 basis: C(4,2) = 6 states (2 ups, 2 downs)
_sz0_basis = [
    tuple(1 if i in up else 0 for i in range(N_SITES))
    for up in combinations(range(N_SITES), 2)
]

def build_heisenberg(J, basis):
    n = len(basis)
    H = np.zeros((n, n))
    idx = {s: i for i, s in enumerate(basis)}
    for row, state in enumerate(basis):
        for (a, b) in BONDS:
            sz_a = 0.5 if state[a] else -0.5
            sz_b = 0.5 if state[b] else -0.5
            H[row, row] += J * sz_a * sz_b
            if state[a] != state[b]:
                lst = list(state)
                lst[a], lst[b] = lst[b], lst[a]
                ns = tuple(lst)
                if ns in idx:
                    H[row, idx[ns]] += J * 0.5
    return H

def spin_label(state):
    syms = {1: "↑", 0: "↓"}
    return "|" + "".join(syms[s] for s in state) + "⟩"

_labels = [spin_label(s) for s in _sz0_basis]
_H_unit = build_heisenberg(1.0, _sz0_basis)   # H/J matrix

with st.expander("6 × 6 Hamiltonian matrix H/J in the Sz = 0 basis", expanded=True):
    st.markdown(r"""
With $N = 4$ sites and half-filling ($k = 2$ electrons of each spin), the $S_z = 0$ sector has
$D = \binom{4}{2} = 6$ basis states. The Heisenberg exchange term
$J\bigl(\tfrac{1}{2}(\hat{S}^+_i\hat{S}^-_j + \hat{S}^-_i\hat{S}^+_j) + \hat{S}^z_i\hat{S}^z_j\bigr)$
gives diagonal contributions $\pm J/4$ per bond and off-diagonal $J/2$ when swapping antiparallel neighbours.
The $S_z = 0$ Zeeman block is **identically zero** (Section 1), so:

$$
\hat{H}\big|_{S_z=0} = J \cdot \mathbf{M},\qquad
\mathbf{M} = \begin{pmatrix}
 0 & \tfrac{1}{2} & 0 & 0 & \tfrac{1}{2} & 0 \\
\tfrac{1}{2} & -1 & \tfrac{1}{2} & \tfrac{1}{2} & 0 & \tfrac{1}{2} \\
 0 & \tfrac{1}{2} & 0 & 0 & \tfrac{1}{2} & 0 \\
 0 & \tfrac{1}{2} & 0 & 0 & \tfrac{1}{2} & 0 \\
\tfrac{1}{2} & 0 & \tfrac{1}{2} & \tfrac{1}{2} & -1 & \tfrac{1}{2} \\
 0 & \tfrac{1}{2} & 0 & 0 & \tfrac{1}{2} & 0
\end{pmatrix}
$$

The two **Néel states** $|\!\uparrow\downarrow\uparrow\downarrow\rangle$ and $|\!\downarrow\uparrow\downarrow\uparrow\rangle$ (rows/cols 1 and 4)
are the only ones with all bonds antiparallel — giving the diagonal $-J$.
The remaining four "domain-wall" states have two parallel and two antiparallel bonds → diagonal $0$.
""")

    # Heatmap of the matrix
    fig_mat = go.Figure(go.Heatmap(
        z=_H_unit,
        x=_labels, y=_labels,
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
        font=dict(color=T["txt_main"]),
    )
    st.plotly_chart(fig_mat, use_container_width=True)

# ══════════════════════════════════════════════════════════════════
# SECTION 3 — Eigenenergies of all sectors
# ══════════════════════════════════════════════════════════════════
st.markdown('<p class="sec-lbl">3 · Eigenenergies and Sector Dimensions</p>',
            unsafe_allow_html=True)

with st.expander("Spectrum of all Sz sectors at H = 0", expanded=True):
    st.markdown(r"""
We diagonalise each $S_z$ block independently.  Because $[\hat{H}_J, \hat{S}^z_{\mathrm{total}}] = 0$,
the exchange Hamiltonian is block-diagonal in the $S_z$ quantum number.

| Sector $S_z$ | Dimension | Eigenvalues of $\hat{H}/J$ (at $H = 0$) |
|:---:|:---:|:---|
| $+2$ | 1 | $+1$ (all bonds parallel) |
| $+1$ | 4 | $-1,\;0,\;0,\;+1$ |
| $\;0$ | 6 | $-2,\;-1,\;0,\;0,\;0,\;+1$ |
| $-1$ | 4 | $-1,\;0,\;0,\;+1$ |
| $-2$ | 1 | $+1$ |

The global ground state at $H = 0$ lies in the $S_z = 0$ sector with energy $E_0 = -2J$.
This is lower than the classical Néel energy $E_{\rm Néel} = J \times 4\times(-\tfrac{1}{4}) = -J$,
illustrating how **quantum fluctuations lower the energy** of the antiferromagnet.
""")

    # Verify numerically
    evals_0 = np.sort(np.linalg.eigvalsh(_H_unit))

    # Sz=+1 sector
    _sz1_basis = [
        tuple(1 if i in up else 0 for i in range(N_SITES))
        for up in combinations(range(N_SITES), 3)
    ]
    _H1 = build_heisenberg(1.0, _sz1_basis)
    evals_1 = np.sort(np.linalg.eigvalsh(_H1))

    # Sz=+2 (1 state, all up)
    _sz2_basis = [(1, 1, 1, 1)]
    E2 = float(build_heisenberg(1.0, _sz2_basis)[0, 0])

    col_a, col_b, col_c = st.columns(3)
    def _fmt(arr):
        return ", ".join(f"{v:.4g}" for v in arr)

    with col_a:
        st.markdown(f'<div class="card"><b>Sz = 0</b><br><small style="color:{T["txt_mute"]}">D = 6</small>'
                    f'<br><code>{_fmt(evals_0)}</code></div>', unsafe_allow_html=True)
    with col_b:
        st.markdown(f'<div class="card"><b>Sz = ±1</b><br><small style="color:{T["txt_mute"]}">D = 4 each</small>'
                    f'<br><code>{_fmt(evals_1)}</code></div>', unsafe_allow_html=True)
    with col_c:
        st.markdown(f'<div class="card"><b>Sz = ±2</b><br><small style="color:{T["txt_mute"]}">D = 1 each</small>'
                    f'<br><code>{E2:.4g}</code></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# SECTION 4 — Limiting regimes + interactive energy diagram
# ══════════════════════════════════════════════════════════════════
st.markdown('<p class="sec-lbl">4 · Eigenenergies and Limiting Regimes</p>',
            unsafe_allow_html=True)

with st.expander("Limiting cases H = 0 and J = 0", expanded=True):
    st.markdown(r"""
**Case 1 — $H = 0$ (pure Heisenberg).**

With no field every $S_z$ sector of a given $S_{\rm total}$ multiplet is degenerate.
The ground state is the **singlet** ($S_{\rm total} = 0$, $S_z = 0$) with energy

$$E_0 = -2J.$$

Its energy is lower than the classical Néel state ($E_{\rm Néel} = -J$) by a factor of 2,
confirming that zero-point quantum fluctuations in the Heisenberg model reduce the energy below
the classical limit.

**Case 2 — $J = 0$ (pure Zeeman).**

Without exchange all spin configurations cost zero exchange energy, so the field alone sets
the ground state. For any $H > 0$, the fully polarised state $|\!\uparrow\uparrow\uparrow\uparrow\rangle$
($S_z = +2$) is favoured:

$$E = -H \cdot S_z^{\rm total} = -2H \quad (S_z = +2).$$

There is no magnetisation staircase — the system jumps directly to full polarisation.
""")

with st.expander("General case H, J > 0 — energy levels vs field", expanded=True):
    st.markdown(r"""
The Zeeman term adds $-H \cdot S_z^{\rm total}$ to each sector uniformly:

$$E_{n}(S_z, H) = E_n^{(J)} - H\, S_z^{\rm total},$$

where $E_n^{(J)}$ is the $n$-th eigenvalue of the exchange Hamiltonian in sector $S_z$.
Because every state in $\mathcal{H}_{S_z=0}$ has $S_z^{\rm total} = 0$, those energies are
**field-independent** (horizontal lines). The $S_z = +1$ levels uniformly shift down by $H$,
and $S_z = +2$ shifts down by $2H$.
""")

    col_j, col_h = st.columns([1, 1])
    with col_j:
        J_val = st.slider("Exchange coupling J", 0.1, 3.0, 1.0, 0.05)
    with col_h:
        H_max = st.slider("Max field H to display", 0.5, 6.0, 3.0 * J_val, 0.1)

    H_arr = np.linspace(0, H_max, 400)

    evals_0_J = np.sort(np.linalg.eigvalsh(build_heisenberg(J_val, _sz0_basis)))
    evals_1_J = np.sort(np.linalg.eigvalsh(build_heisenberg(J_val, _sz1_basis)))
    E2_J = float(build_heisenberg(J_val, _sz2_basis)[0, 0])

    fig_e = go.Figure()
    palette = {0: SAGE, 1: AMBER, 2: SLATE, -1: ROSE, -2: DARK_BRN}

    for E in evals_0_J:
        fig_e.add_trace(go.Scatter(
            x=H_arr, y=np.full_like(H_arr, E),
            mode="lines", line=dict(color=palette[0], width=1.8),
            name="Sz = 0", legendgroup="sz0", showlegend=(E == evals_0_J[0]),
        ))
    for E in evals_1_J:
        fig_e.add_trace(go.Scatter(
            x=H_arr, y=E - H_arr,
            mode="lines", line=dict(color=palette[1], width=1.8),
            name="Sz = +1", legendgroup="sz1", showlegend=(E == evals_1_J[0]),
        ))
    fig_e.add_trace(go.Scatter(
        x=H_arr, y=E2_J - 2 * H_arr,
        mode="lines", line=dict(color=palette[2], width=2.2, dash="dot"),
        name="Sz = +2",
    ))
    for E in np.sort(np.linalg.eigvalsh(build_heisenberg(J_val, [
        tuple(1 if i in up else 0 for i in range(N_SITES))
        for up in combinations(range(N_SITES), 1)
    ]))):
        fig_e.add_trace(go.Scatter(
            x=H_arr, y=E + H_arr,
            mode="lines", line=dict(color=palette[-1], width=1.2, dash="dash"),
            name="Sz = −1", legendgroup="szm1", showlegend=(E == np.sort(np.linalg.eigvalsh(build_heisenberg(J_val, [
                tuple(1 if i in up else 0 for i in range(N_SITES))
                for up in combinations(range(N_SITES), 1)
            ])))[0]),
        ))
    fig_e.add_trace(go.Scatter(
        x=H_arr, y=E2_J + 2 * H_arr,
        mode="lines", line=dict(color=palette[-2], width=1.2, dash="dash"),
        name="Sz = −2",
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

# ══════════════════════════════════════════════════════════════════
# SECTION 5 — Magnetisation staircase
# ══════════════════════════════════════════════════════════════════
st.markdown('<p class="sec-lbl">5 · Magnetization Staircase and Critical Fields H<sub>c</sub></p>',
            unsafe_allow_html=True)

with st.expander("Ground-state Sz vs H — the staircase", expanded=True):
    st.markdown(r"""
As $H$ increases, the ground state transitions between $S_z$ sectors when the lowest energy
level of an adjacent sector crosses the current ground-state energy.

**Derivation of the critical fields** (using eigenvalues computed above at coupling $J$):

- $E_{\min}(S_z=0) = -2J$ (independent of $H$)
- $E_{\min}(S_z=+1,\,H) = -J - H$ (shifts down by $H$)
- $E(S_z=+2,\,H) = J - 2H$ (shifts down by $2H$)

$$
H_{c1}: \quad -J - H_{c1} = -2J \;\;\Rightarrow\;\; \boxed{H_{c1} = J}
$$

$$
H_{c2}: \quad J - 2H_{c2} = -J - H_{c2} \;\;\Rightarrow\;\; \boxed{H_{c2} = 2J}
$$

| Field range | Ground sector | $\langle S_z^{\rm total}\rangle$ |
|:---:|:---:|:---:|
| $0 \le H < J$ | $S_z = 0$ | $0$ |
| $J \le H < 2J$ | $S_z = +1$ | $+1$ |
| $H \ge 2J$ | $S_z = +2$ | $+2$ (full saturation) |
""")

    col_j2, _ = st.columns([1, 2])
    with col_j2:
        J2 = st.slider("Exchange coupling J (staircase)", 0.1, 3.0, 1.0, 0.05,
                       key="J_stair")

    Hc1 = J2
    Hc2 = 2 * J2
    H_plot = np.linspace(0, 3 * J2 + 0.2, 800)

    evals_0_J2 = np.sort(np.linalg.eigvalsh(build_heisenberg(J2, _sz0_basis)))
    evals_1_J2 = np.sort(np.linalg.eigvalsh(build_heisenberg(J2, _sz1_basis)))
    E2_J2 = float(build_heisenberg(J2, _sz2_basis)[0, 0])

    gs_energies = np.minimum(
        np.minimum(evals_0_J2[0] * np.ones_like(H_plot),
                   evals_1_J2[0] - H_plot),
        E2_J2 - 2 * H_plot
    )
    sz_gs = np.where(
        gs_energies == evals_0_J2[0],
        0,
        np.where(gs_energies == evals_1_J2[0] - H_plot, 1, 2)
    )

    fig_s = go.Figure()

    # Shaded regions
    for sz_val, x0, x1, col in [
        (0,   0,    Hc1,             "#D8EFD8"),
        (1,   Hc1,  Hc2,             "#FFF0D0"),
        (2,   Hc2,  3 * J2 + 0.2,   "#D0E4F0"),
    ]:
        fig_s.add_vrect(x0=x0, x1=x1, fillcolor=col, opacity=0.25,
                        layer="below", line_width=0)
        fig_s.add_annotation(
            x=(x0 + min(x1, 3*J2+0.2)) / 2, y=2.35,
            text=f"Sz = {sz_val}", showarrow=False,
            font=dict(color=T["txt_mute"], size=11),
        )

    # Vertical lines at critical fields
    for xc, label in [(Hc1, "H<sub>c1</sub> = J"), (Hc2, "H<sub>c2</sub> = 2J")]:
        fig_s.add_vline(x=xc, line_dash="dot", line_color=T["txt_mute"], line_width=1.4)
        fig_s.add_annotation(x=xc, y=-0.25, text=label, showarrow=False,
                              font=dict(color=T["txt_mute"], size=10),
                              xanchor="center")

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
                   title_font=dict(color=T["txt_mute"]), range=[-0.4, 2.6]),
        hoverlabel=dict(bgcolor=T["hover_bg"], font=dict(color=T["hover_txt"])),
        legend=dict(bgcolor=T["card_bg"], bordercolor=T["border"],
                    font=dict(color=T["txt_main"], size=11)),
    )
    st.plotly_chart(fig_s, use_container_width=True)

    st.markdown(
        f'<div class="caption-box">'
        f'For J = {J2:.2f}: &nbsp;'
        f'<b>H<sub>c1</sub> = {Hc1:.2f}</b> (Sz: 0 → 1) &nbsp;|&nbsp; '
        f'<b>H<sub>c2</sub> = {Hc2:.2f}</b> (Sz: 1 → 2, full saturation). &nbsp;'
        f'The Sz = 0 energies are flat (field-independent) because '
        f'Ĥ<sub>Z</sub>|φ⟩ = 0 for all states in that sector.'
        f'</div>',
        unsafe_allow_html=True,
    )
