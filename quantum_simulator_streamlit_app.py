"""
Quantum Circuit Simulator — up to 10 qubits
"""

import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import json
import datetime

st.set_page_config(page_title="Quantum Circuit Simulator", page_icon="⚛️", layout="wide")

BG      = "#FAF8F4"
SIDEBAR = "#F3EFE8"
PANEL   = "#EEEAE2"
BORDER  = "#D4CEBF"
BLUE    = "#0070C1"
CYAN    = "#267F99"
GREEN   = "#448C31"
YELLOW  = "#795E26"
ORANGE  = "#A31515"
PURPLE  = "#AF00DB"
WHITE   = "#1E1E1E"
DIM     = "#6E6E6E"

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@400;500;600;700&display=swap');

  html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    background-color: {BG} !important;
    color: {WHITE};
  }}
  .main, .stApp {{ background: {BG} !important; }}
  section[data-testid="stMain"] > div {{ background: {BG} !important; }}
  .block-container {{ padding-top: 3.5rem; max-width: 1600px; background: {BG}; }}

  .qc-header {{
    padding-bottom: 0.7rem; margin-bottom: 1.1rem;
    border-bottom: 2px solid {BORDER};
  }}
  .qc-title {{
    font-family: 'JetBrains Mono', monospace;
    font-size: clamp(1rem, 1.8vw, 1.55rem);
    font-weight: 700; color: {CYAN};
    margin: 0 0 0.18rem 0; line-height: 1.2;
  }}
  .qc-subtitle {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem; color: {DIM}; margin: 0;
  }}
  .vsc-section {{
    color: {DIM}; font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem; letter-spacing: 2px; text-transform: uppercase;
    border-bottom: 1px solid {BORDER}; padding-bottom: 0.18rem;
    margin: 0.75rem 0 0.45rem 0;
  }}
  .vsc-card {{
    background: {PANEL}; border: 1px solid {BORDER};
    border-left: 3px solid {CYAN}; border-radius: 4px;
    padding: 0.6rem 0.85rem; margin-bottom: 0.45rem;
    font-family: 'JetBrains Mono', monospace;
  }}
  .vsc-card-label {{ color:{DIM}; font-size:0.58rem; letter-spacing:1.5px; text-transform:uppercase; }}
  .vsc-card-value {{ color:{YELLOW}; font-size:1.05rem; font-weight:700; line-height:1.3; }}
  .vsc-card-sub   {{ color:{DIM}; font-size:0.68rem; }}

  .gate-item {{
    display: flex; align-items: flex-start; gap: 8px;
    background: white; border: 1px solid {BORDER};
    border-left: 4px solid {CYAN}; border-radius: 5px;
    padding: 0.42rem 0.7rem 0.38rem 0.7rem; margin-bottom: 5px;
    font-family: 'JetBrains Mono', monospace;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  }}
  .gate-item-tq {{ border-left-color: {PURPLE} !important; background: #FDFAFF !important; }}
  .gate-item-inner {{ flex: 1; min-width: 0; }}
  .gate-item-top {{ display: flex; align-items: center; gap: 6px; margin-bottom: 2px; }}
  .gate-item-badge {{
    background: {CYAN}; color: white; border-radius: 3px;
    padding: 1px 6px; font-size: 0.62rem; font-weight: 700;
    white-space: nowrap; flex-shrink: 0;
  }}
  .gate-badge-tq {{ background: {PURPLE} !important; }}
  .gate-item-name {{ color: {YELLOW}; font-weight: 700; font-size: 0.84rem; }}
  .gate-item-name-tq {{ color: {PURPLE} !important; }}
  .gate-item-detail {{ color: {DIM}; font-size: 0.68rem; margin-top: 1px; }}
  .gate-item-qubit {{
    display: inline-block; background: {PANEL}; border: 1px solid {BORDER};
    border-radius: 3px; padding: 0px 5px;
    font-size: 0.65rem; color: {CYAN}; font-weight: 600; margin-right: 3px;
  }}
  .gate-item-qubit-tq {{ color: {PURPLE} !important; }}
  .gate-list-empty {{
    font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: {BORDER};
    text-align: center; padding: 1rem 0.5rem;
    border: 1px dashed {BORDER}; border-radius: 4px;
  }}

  /* All Streamlit buttons — neutral base */
  div[data-testid="stButton"] > button {{
    background: {BG} !important;
    border: 1.5px solid {BORDER} !important;
    color: {DIM} !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 600 !important; font-size: 0.78rem !important;
    letter-spacing: 1px !important; border-radius: 4px !important;
    padding: 0.4rem 0.5rem !important; width: 100% !important;
    transition: all 0.15s !important;
  }}
  div[data-testid="stButton"] > button:hover {{
    background: {PANEL} !important;
    border-color: {CYAN} !important; color: {CYAN} !important;
  }}

  /* Action buttons (add gate / run / reset / clear) */
  .action-btn div[data-testid="stButton"] > button {{
    background: {BG} !important;
    border-color: {BLUE} !important; color: {BLUE} !important;
  }}
  .action-btn div[data-testid="stButton"] > button:hover {{
    background: {BLUE}12 !important;
    border-color: {CYAN} !important; color: {CYAN} !important;
  }}

  /* Active SQ toggle */
  .sq-active div[data-testid="stButton"] > button {{
    background: {CYAN}1A !important;
    border-color: {CYAN} !important; color: {CYAN} !important;
  }}
  /* Active TQ toggle */
  .tq-active div[data-testid="stButton"] > button {{
    background: {PURPLE}18 !important;
    border-color: {PURPLE} !important; color: {PURPLE} !important;
  }}

  .add-gate-panel {{
    background: {SIDEBAR}; border: 1.5px solid {BORDER};
    border-top: 3px solid {BLUE}; border-radius: 6px;
    padding: 0.85rem 1rem 0.7rem 1rem; margin-bottom: 0.8rem;
  }}
  .add-gate-panel-title {{
    font-family: 'JetBrains Mono', monospace; font-size: 0.62rem;
    letter-spacing: 2px; text-transform: uppercase; color: {BLUE};
    margin-bottom: 0.6rem; font-weight: 600;
  }}
  .toggle-label {{
    font-family: 'JetBrains Mono', monospace; font-size: 0.6rem;
    letter-spacing: 1.5px; text-transform: uppercase;
    color: {DIM}; margin-bottom: 0.25rem;
  }}

  .notes-panel {{
    background: {SIDEBAR}; border: 1.5px solid {BORDER};
    border-top: 3px solid {YELLOW}; border-radius: 6px;
    padding: 0.85rem 1rem 0.9rem 1rem; margin-top: 1rem;
  }}
  .notes-panel-title {{
    font-family: 'JetBrains Mono', monospace; font-size: 0.62rem;
    letter-spacing: 2px; text-transform: uppercase; color: {YELLOW};
    margin-bottom: 0.5rem; font-weight: 600;
  }}
  .badge-running {{
    background:#EAF5EA; border:1px solid {GREEN}; border-radius:3px;
    padding:0.26rem 0.6rem; color:{GREEN};
    font-family:'JetBrains Mono',monospace; font-size:0.68rem;
    text-align:center; margin-top:0.3rem;
  }}
  .badge-idle {{
    background:{PANEL}; border:1px solid {BORDER}; border-radius:3px;
    padding:0.26rem 0.6rem; color:{DIM};
    font-family:'JetBrains Mono',monospace; font-size:0.68rem;
    text-align:center; margin-top:0.3rem;
  }}
  div[data-testid="stTabs"] button {{
    font-family:'JetBrains Mono',monospace !important; font-size:0.75rem !important; color:{DIM} !important;
  }}
  div[data-testid="stTabs"] button[aria-selected="true"] {{
    color:{CYAN} !important; border-bottom:2px solid {CYAN} !important;
  }}
  div[data-testid="stSlider"] label, div[data-testid="stSlider"] p {{
    color:{WHITE} !important; font-family:'JetBrains Mono',monospace !important; font-size:0.74rem !important;
  }}
  div[data-testid="stSelectbox"] label {{
    color:{WHITE} !important; font-family:'JetBrains Mono',monospace !important; font-size:0.72rem !important;
  }}
  div[data-testid="stSelectbox"] > div > div {{
    background:{PANEL} !important; border:1px solid {BORDER} !important;
    border-radius:4px !important; font-family:'JetBrains Mono',monospace !important;
    color:{YELLOW} !important; font-size:0.82rem !important;
  }}
  div[data-testid="stTextArea"] label {{
    color:{WHITE} !important; font-family:'JetBrains Mono',monospace !important; font-size:0.72rem !important;
  }}
  div[data-testid="stTextArea"] textarea {{
    background:{PANEL} !important; border:1px solid {BORDER} !important;
    border-radius:4px !important; color:{WHITE} !important;
    font-family:'JetBrains Mono',monospace !important; font-size:0.8rem !important; resize:vertical !important;
  }}
  div[data-testid="stTextInput"] label {{
    color:{WHITE} !important; font-family:'JetBrains Mono',monospace !important; font-size:0.72rem !important;
  }}
  div[data-testid="stTextInput"] input {{
    background:{PANEL} !important; border:1px solid {BORDER} !important;
    border-radius:4px !important; color:{WHITE} !important;
    font-family:'JetBrains Mono',monospace !important; font-size:0.82rem !important;
  }}
</style>
""", unsafe_allow_html=True)

# ── Gate library ──────────────────────────────────────────────────────────────
SQ_GATES = {
    "H":   {"label":"H",     "desc":"Hadamard",    "has_theta":False,
            "matrix": lambda t: np.array([[1,1],[1,-1]],dtype=complex)/np.sqrt(2)},
    "X":   {"label":"X",     "desc":"Pauli-X",     "has_theta":False,
            "matrix": lambda t: np.array([[0,1],[1,0]],dtype=complex)},
    "Y":   {"label":"Y",     "desc":"Pauli-Y",     "has_theta":False,
            "matrix": lambda t: np.array([[0,-1j],[1j,0]],dtype=complex)},
    "Z":   {"label":"Z",     "desc":"Pauli-Z",     "has_theta":False,
            "matrix": lambda t: np.array([[1,0],[0,-1]],dtype=complex)},
    "S":   {"label":"S",     "desc":"Phase √Z",    "has_theta":False,
            "matrix": lambda t: np.array([[1,0],[0,1j]],dtype=complex)},
    "T":   {"label":"T",     "desc":"π/8 gate",    "has_theta":False,
            "matrix": lambda t: np.array([[1,0],[0,np.exp(1j*np.pi/4)]],dtype=complex)},
    "Rx":  {"label":"Rx(θ)", "desc":"X-rotation",  "has_theta":True,
            "matrix": lambda t: np.array([[np.cos(t/2),-1j*np.sin(t/2)],
                                          [-1j*np.sin(t/2),np.cos(t/2)]],dtype=complex)},
    "Ry":  {"label":"Ry(θ)", "desc":"Y-rotation",  "has_theta":True,
            "matrix": lambda t: np.array([[np.cos(t/2),-np.sin(t/2)],
                                          [np.sin(t/2), np.cos(t/2)]],dtype=complex)},
    "Rz":  {"label":"Rz(θ)", "desc":"Z-rotation",  "has_theta":True,
            "matrix": lambda t: np.array([[np.exp(-1j*t/2),0],
                                          [0,np.exp(1j*t/2)]],dtype=complex)},
}
TQ_GATES = {
    "CNOT":  {"label":"CNOT",   "desc":"Controlled-X",  "has_theta":False},
    "CZ":    {"label":"CZ",     "desc":"Controlled-Z",  "has_theta":False},
    "SWAP":  {"label":"SWAP",   "desc":"Swap qubits",   "has_theta":False},
    "iSWAP": {"label":"iSWAP",  "desc":"i·SWAP",        "has_theta":False},
    "CRz":   {"label":"CRz(θ)", "desc":"Controlled Rz", "has_theta":True},
    "XX":    {"label":"XX(θ)",  "desc":"Ising XX",       "has_theta":True},
}

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in {"n_qubits":3,"running":False,"gate_list":[],"locked_snap":None,
             "notes":"","circuit_name":"My Circuit","gate_type":"Single-qubit"}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Simulation helpers ────────────────────────────────────────────────────────
def apply_sq(state, n, qubit, gate_key, theta):
    G = SQ_GATES[gate_key]["matrix"](theta)
    I = np.eye(2, dtype=complex)
    ops = [G if i==qubit else I for i in range(n)]
    U = ops[0]
    for op in ops[1:]: U = np.kron(U, op)
    return U @ state

def apply_tq(state, n, gate_key, ctrl, tgt, theta):
    N = 2**n; out = state.copy()
    if gate_key == "CNOT":
        for idx in range(N):
            if (idx>>(n-1-ctrl))&1:
                f=idx^(1<<(n-1-tgt))
                if idx<f: out[idx],out[f]=state[f],state[idx]
    elif gate_key == "CZ":
        for idx in range(N):
            if ((idx>>(n-1-ctrl))&1) and ((idx>>(n-1-tgt))&1): out[idx]=-state[idx]
    elif gate_key == "SWAP":
        for idx in range(N):
            cb=(idx>>(n-1-ctrl))&1; tb=(idx>>(n-1-tgt))&1
            if cb!=tb:
                f=idx^(1<<(n-1-ctrl))^(1<<(n-1-tgt))
                if idx<f: out[idx],out[f]=state[f],state[idx]
    elif gate_key == "iSWAP":
        out=state.copy()
        for idx in range(N):
            cb=(idx>>(n-1-ctrl))&1; tb=(idx>>(n-1-tgt))&1
            if cb!=tb:
                f=idx^(1<<(n-1-ctrl))^(1<<(n-1-tgt))
                if idx<f: out[idx]=1j*state[f]; out[f]=1j*state[idx]
    elif gate_key == "CRz":
        for idx in range(N):
            if (idx>>(n-1-ctrl))&1:
                tb=(idx>>(n-1-tgt))&1
                out[idx]=state[idx]*(np.exp(-1j*theta/2) if tb==0 else np.exp(1j*theta/2))
    elif gate_key == "XX":
        c,s=np.cos(theta/2),np.sin(theta/2)
        for idx in range(N):
            f=idx^(1<<(n-1-ctrl))^(1<<(n-1-tgt)); out[idx]=c*state[idx]-1j*s*state[f]
    return out

def simulate(n, gate_list):
    state=np.zeros(2**n,dtype=complex); state[0]=1.0
    for op in gate_list:
        if op["type"]=="sq": state=apply_sq(state,n,op["qubit"],op["gate"],op.get("theta",0.0))
        else: state=apply_tq(state,n,op["gate"],op["ctrl"],op["tgt"],op.get("theta",0.0))
    return state

def entanglement_matrix(state, n):
    ent=np.zeros((n,n)); N=2**n
    for i in range(n):
        for j in range(i+1,n):
            rho2=np.zeros((4,4),dtype=complex)
            for idx in range(N):
                bi=(idx>>(n-1-i))&1; bj=(idx>>(n-1-j))&1; row=bi*2+bj
                for jdx in range(N):
                    bi2=(jdx>>(n-1-i))&1; bj2=(jdx>>(n-1-j))&1; col=bi2*2+bj2
                    mask=~((1<<(n-1-i))|(1<<(n-1-j)))
                    if (idx&mask)==(jdx&mask): rho2[row,col]+=state[idx]*np.conj(state[jdx])
            rho_i=np.array([[rho2[0,0]+rho2[1,1],rho2[0,2]+rho2[1,3]],
                             [rho2[2,0]+rho2[3,1],rho2[2,2]+rho2[3,3]]])
            ent[i,j]=ent[j,i]=np.clip(1-np.real(np.trace(rho_i@rho_i)),0,0.5)
    return ent

def op_label(op, n):
    if op["type"]=="sq":
        lbl=SQ_GATES[op["gate"]]["label"]
        th=f" θ={op['theta']:.2f}" if SQ_GATES[op["gate"]]["has_theta"] else ""
        return f"{lbl}{th} → q{op['qubit']}", False
    lbl=TQ_GATES[op["gate"]]["label"]
    th=f" θ={op['theta']:.2f}" if TQ_GATES[op["gate"]]["has_theta"] else ""
    return f"{lbl}{th} → q{op['ctrl']}·q{op['tgt']}", True

def build_export(n, gate_list, notes, circuit_name, state=None, probs=None, basis=None):
    ts=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sv=([{"basis":basis[i],"prob":float(np.abs(state[i])**2),"re":float(state[i].real),
          "im":float(state[i].imag),"phase_deg":float(np.degrees(np.angle(state[i])))}
         for i in range(len(state))] if state is not None else None)
    return {"name":circuit_name,"timestamp":ts,"n_qubits":n,"notes":notes,
            "gates":[{k:v for k,v in op.items()} for op in gate_list],"state_vector":sv}

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="qc-header">
  <div class="qc-title">⚛ Quantum Circuit Simulator</div>
  <div class="qc-subtitle">// up to 10 qubits &nbsp;·&nbsp; build circuit gate by gate &nbsp;·&nbsp; run simulation</div>
</div>""", unsafe_allow_html=True)

col_ctrl, col_main = st.columns([1, 2.8], gap="large")

with col_ctrl:
    disabled = st.session_state.running
    is_sq    = st.session_state.gate_type == "Single-qubit"

    st.markdown(f"<div class='vsc-section'>System</div>", unsafe_allow_html=True)
    n = st.slider("Qubits", 2, 10, value=st.session_state.n_qubits, disabled=disabled, key="n_slider")
    st.session_state.n_qubits = n
    st.markdown(f"<p style='color:{DIM};font-family:JetBrains Mono,monospace;font-size:0.68rem;"
                f"margin-top:-0.3rem'>// 2<sup>{n}</sup> = {2**n} basis states</p>",
                unsafe_allow_html=True)

    # ── Add Gate Panel ─────────────────────────────────────────────────────
    st.markdown(f"<div class='add-gate-panel'><div class='add-gate-panel-title'>＋ Add Gate</div>",
                unsafe_allow_html=True)

    # ── Gate type toggle ──────────────────────────────────────────────────
    st.markdown(f"<div class='toggle-label'>Gate type</div>", unsafe_allow_html=True)
    col_sq, col_tq = st.columns(2)
    with col_sq:
        # Wrap in a div with the active class so CSS selector targets it
        sq_wrap_class = "sq-active" if is_sq else ""
        st.markdown(f"<div class='{sq_wrap_class}'>", unsafe_allow_html=True)
        if st.button("● Single-qubit" if is_sq else "Single-qubit", key="btn_sq", disabled=disabled):
            st.session_state.gate_type = "Single-qubit"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with col_tq:
        tq_wrap_class = "tq-active" if not is_sq else ""
        st.markdown(f"<div class='{tq_wrap_class}'>", unsafe_allow_html=True)
        if st.button("● Two-qubit" if not is_sq else "Two-qubit", key="btn_tq", disabled=disabled):
            st.session_state.gate_type = "Two-qubit"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

    # ── Gate-specific controls ─────────────────────────────────────────────
    if is_sq:
        add_gate = st.selectbox("Gate", list(SQ_GATES.keys()),
            format_func=lambda k: f"{SQ_GATES[k]['label']}  —  {SQ_GATES[k]['desc']}",
            disabled=disabled, key="add_sq_gate", label_visibility="collapsed")
        add_qubit = st.selectbox("Target qubit", list(range(n)),
            format_func=lambda x: f"q{x}", disabled=disabled, key="add_sq_qubit")
        add_theta = 0.0
        if SQ_GATES[add_gate]["has_theta"]:
            add_theta = st.slider("θ", 0.0, 2*np.pi, np.pi, 0.05,
                format="%.2f", disabled=disabled, key="add_sq_theta")
            st.markdown(f"<p style='color:{DIM};font-family:JetBrains Mono,monospace;"
                        f"font-size:0.68rem;margin-top:-6px'>{add_theta:.4f} rad = {add_theta/np.pi:.3f}π</p>",
                        unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='color:{BORDER};font-family:JetBrains Mono,monospace;"
                        f"font-size:0.68rem'>// no angle parameter</p>", unsafe_allow_html=True)
        theta_chip = (f"&nbsp;&nbsp;<span style='color:{DIM}'>θ=</span>"
                      f"<span style='color:{ORANGE}'>{add_theta:.3f}</span>"
                      if SQ_GATES[add_gate]["has_theta"] else "")
        st.markdown(
            f"<div style='background:{CYAN}0f;border:1px solid {CYAN}44;border-radius:4px;"
            f"padding:0.32rem 0.7rem;margin:0.4rem 0 0.4rem 0;"
            f"font-family:JetBrains Mono,monospace;font-size:0.74rem'>"
            f"<span style='color:{CYAN};font-weight:700'>{SQ_GATES[add_gate]['label']}</span>"
            f"<span style='color:{DIM}'>&nbsp;on&nbsp;</span>"
            f"<span style='color:{YELLOW};font-weight:600'>q{add_qubit}</span>"
            f"{theta_chip}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)   # close .add-gate-panel
        st.markdown("<div class='action-btn'>", unsafe_allow_html=True)
        if st.button("＋  ADD GATE", disabled=disabled, key="add_sq_btn"):
            st.session_state.gate_list.append({"type":"sq","gate":add_gate,"qubit":add_qubit,"theta":add_theta})
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        add_tq = st.selectbox("Gate", list(TQ_GATES.keys()),
            format_func=lambda k: f"{TQ_GATES[k]['label']}  —  {TQ_GATES[k]['desc']}",
            disabled=disabled, key="add_tq_gate", label_visibility="collapsed")
        c1, c2 = st.columns(2)
        with c1:
            add_ctrl = st.selectbox("Control", list(range(n)),
                format_func=lambda x: f"q{x}", disabled=disabled, key="add_tq_ctrl")
        with c2:
            tgt_choices = [q for q in range(n) if q!=add_ctrl]
            add_tgt = st.selectbox("Target", tgt_choices,
                format_func=lambda x: f"q{x}", disabled=disabled, key="add_tq_tgt")
        add_theta2 = 0.0
        if TQ_GATES[add_tq]["has_theta"]:
            add_theta2 = st.slider("θ", 0.0, 2*np.pi, np.pi, 0.05,
                format="%.2f", disabled=disabled, key="add_tq_theta")
            st.markdown(f"<p style='color:{DIM};font-family:JetBrains Mono,monospace;"
                        f"font-size:0.68rem;margin-top:-6px'>{add_theta2:.4f} rad = {add_theta2/np.pi:.3f}π</p>",
                        unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='color:{BORDER};font-family:JetBrains Mono,monospace;"
                        f"font-size:0.68rem'>// no angle parameter</p>", unsafe_allow_html=True)
        theta_chip2 = (f"&nbsp;&nbsp;<span style='color:{DIM}'>θ=</span>"
                       f"<span style='color:{ORANGE}'>{add_theta2:.3f}</span>"
                       if TQ_GATES[add_tq]["has_theta"] else "")
        st.markdown(
            f"<div style='background:{PURPLE}0d;border:1px solid {PURPLE}44;border-radius:4px;"
            f"padding:0.32rem 0.7rem;margin:0.4rem 0 0.4rem 0;"
            f"font-family:JetBrains Mono,monospace;font-size:0.74rem'>"
            f"<span style='color:{PURPLE};font-weight:700'>{TQ_GATES[add_tq]['label']}</span>"
            f"<span style='color:{DIM}'>&nbsp;ctrl=</span><span style='color:{YELLOW};font-weight:600'>q{add_ctrl}</span>"
            f"<span style='color:{DIM}'>&nbsp;tgt=</span><span style='color:{YELLOW};font-weight:600'>q{add_tgt}</span>"
            f"{theta_chip2}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)   # close .add-gate-panel
        st.markdown("<div class='action-btn'>", unsafe_allow_html=True)
        if st.button("＋  ADD GATE", disabled=disabled, key="add_tq_btn"):
            st.session_state.gate_list.append({"type":"tq","gate":add_tq,"ctrl":add_ctrl,"tgt":add_tgt,"theta":add_theta2})
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Gate list ─────────────────────────────────────────────────────────
    n_gates = len(st.session_state.gate_list)
    st.markdown(
        f"<div style='display:flex;align-items:center;justify-content:space-between;"
        f"border-bottom:1px solid {BORDER};padding-bottom:0.2rem;margin:0.8rem 0 0.5rem 0'>"
        f"<span style='color:{DIM};font-family:JetBrains Mono,monospace;font-size:0.6rem;"
        f"letter-spacing:2px;text-transform:uppercase'>Circuit — {n_gates} gate(s)</span>"
        f"<span style='background:{CYAN};color:white;border-radius:10px;"
        f"padding:1px 8px;font-family:JetBrains Mono,monospace;font-size:0.62rem;"
        f"font-weight:700'>{n_gates}</span></div>", unsafe_allow_html=True)

    if not st.session_state.gate_list:
        st.markdown(f"<div class='gate-list-empty'>// no gates added yet<br>"
                    f"<span style='font-size:0.62rem'>use the panel above to add gates</span></div>",
                    unsafe_allow_html=True)
    else:
        for idx, op in enumerate(st.session_state.gate_list):
            is_tq_op=op["type"]=="tq"
            tq_cls="gate-item-tq" if is_tq_op else ""
            badge_cls="gate-badge-tq" if is_tq_op else ""
            name_cls="gate-item-name-tq" if is_tq_op else ""
            if is_tq_op:
                gate_name=TQ_GATES[op["gate"]]["label"]; gate_desc=TQ_GATES[op["gate"]]["desc"]
                qubit_info=(f"<span class='gate-item-qubit gate-item-qubit-tq'>ctrl q{op['ctrl']}</span>"
                            f"<span class='gate-item-qubit gate-item-qubit-tq'>tgt q{op['tgt']}</span>")
                theta_info=(f"&nbsp;θ=<span style='color:{ORANGE}'>{op['theta']:.3f}</span>"
                            if TQ_GATES[op["gate"]]["has_theta"] else "")
            else:
                gate_name=SQ_GATES[op["gate"]]["label"]; gate_desc=SQ_GATES[op["gate"]]["desc"]
                qubit_info=f"<span class='gate-item-qubit'>q{op['qubit']}</span>"
                theta_info=(f"&nbsp;θ=<span style='color:{ORANGE}'>{op['theta']:.3f}</span>"
                            if SQ_GATES[op["gate"]]["has_theta"] else "")
            col_lbl,col_del,col_up,col_dn=st.columns([3.2,0.65,0.65,0.65])
            with col_lbl:
                st.markdown(
                    f"<div class='gate-item {tq_cls}'><div class='gate-item-inner'>"
                    f"<div class='gate-item-top'>"
                    f"<span class='gate-item-badge {badge_cls}'>#{idx+1}</span>"
                    f"<span class='gate-item-name {name_cls}'>{gate_name}</span></div>"
                    f"<div class='gate-item-detail'>{qubit_info}{theta_info}"
                    f"<span style='color:{BORDER}'>&nbsp;{gate_desc}</span></div>"
                    f"</div></div>", unsafe_allow_html=True)
            with col_del:
                if st.button("✕",key=f"del_{idx}",disabled=disabled,help="Remove"):
                    st.session_state.gate_list.pop(idx); st.rerun()
            with col_up:
                if st.button("↑",key=f"up_{idx}",disabled=(disabled or idx==0),help="Move up"):
                    gl=st.session_state.gate_list; gl[idx-1],gl[idx]=gl[idx],gl[idx-1]; st.rerun()
            with col_dn:
                if st.button("↓",key=f"dn_{idx}",disabled=(disabled or idx==len(st.session_state.gate_list)-1),help="Move down"):
                    gl=st.session_state.gate_list; gl[idx+1],gl[idx]=gl[idx],gl[idx+1]; st.rerun()
        if not disabled:
            st.markdown("<div class='action-btn'>", unsafe_allow_html=True)
            if st.button("🗑  CLEAR ALL"): st.session_state.gate_list=[]; st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # ── Run / Reset ───────────────────────────────────────────────────────
    st.markdown(f"<div class='vsc-section'>Run</div>", unsafe_allow_html=True)
    st.markdown("<div class='action-btn'>", unsafe_allow_html=True)
    if not st.session_state.running:
        if st.button("▶  RUN SIMULATION", disabled=not st.session_state.gate_list):
            st.session_state.running=True
            st.session_state.locked_snap={"n":n,"gate_list":[op.copy() for op in st.session_state.gate_list]}
            st.rerun()
    else:
        if st.button("↺  RESET"):
            st.session_state.running=False; st.session_state.locked_snap=None; st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.running:
        st.markdown("<div class='badge-running'>● circuit active</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='badge-idle'>○ awaiting input</div>", unsafe_allow_html=True)

    if st.session_state.gate_list:
        sq_c=sum(1 for op in st.session_state.gate_list if op["type"]=="sq")
        tq_c=sum(1 for op in st.session_state.gate_list if op["type"]=="tq")
        st.markdown(f"<br><div class='vsc-card'>"
                    f"<div class='vsc-card-label'>Circuit stats</div>"
                    f"<div class='vsc-card-value'>{len(st.session_state.gate_list)} ops</div>"
                    f"<div class='vsc-card-sub'>{sq_c} single-qubit · {tq_c} two-qubit</div>"
                    f"<div class='vsc-card-sub'>dim = 2<sup>{n}</sup> = {2**n}</div></div>",
                    unsafe_allow_html=True)

    # ── Notes ─────────────────────────────────────────────────────────────
    st.markdown(f"<div class='notes-panel'><div class='notes-panel-title'>📝 Notes</div>",
                unsafe_allow_html=True)
    cn=st.text_input("Circuit name",value=st.session_state.circuit_name,
        placeholder="e.g. Bell state preparation",key="circuit_name_input")
    st.session_state.circuit_name=cn
    nt=st.text_area("Notes",value=st.session_state.notes,height=120,
        placeholder="Observations, hypotheses...",label_visibility="collapsed",key="notes_textarea")
    st.session_state.notes=nt
    st.markdown("</div>", unsafe_allow_html=True)

# ── Simulation ────────────────────────────────────────────────────────────────
if st.session_state.running and st.session_state.locked_snap:
    snap=st.session_state.locked_snap; sim_n=snap["n"]; sim_gates=snap["gate_list"]
else:
    sim_n=n; sim_gates=st.session_state.gate_list

is_running=st.session_state.running
state_disp=simulate(sim_n,sim_gates)
probs_d=np.abs(state_disp)**2; phases_d=np.angle(state_disp)
basis_all=[f"|{format(i,f'0{sim_n}b')}⟩" for i in range(2**sim_n)]
top_idx=np.argsort(probs_d)[::-1][:min(32,2**sim_n)]
top_sorted=sorted(top_idx,key=lambda i:-probs_d[i])

# ── Right column ──────────────────────────────────────────────────────────────
with col_main:
    tab1,tab2,tab3=st.tabs(["Circuit Diagram","Probabilities","Entanglement"])

    with tab1:
        n_ops=len(sim_gates)
        fig_w=max(8,n_ops*1.1+2.5); fig_h=max(2.2,sim_n*0.65+1.0)
        fig,ax=plt.subplots(figsize=(fig_w,fig_h))
        fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
        top_y=(sim_n-1)*1.0
        ax.set_xlim(0,fig_w); ax.set_ylim(-0.8,top_y+0.85); ax.axis("off")
        wire_ys=[top_y-q*1.0 for q in range(sim_n)]
        for q,wy in enumerate(wire_ys):
            ax.plot([0.5,fig_w-0.3],[wy,wy],color=BORDER,lw=1.4,zorder=1)
            ax.text(0.35,wy,f"q{q}",color=CYAN,fontsize=9,fontfamily="monospace",va="center",ha="right",fontweight="bold")
            ax.text(0.55,wy+0.2,"|0⟩",color=DIM,fontsize=7,fontfamily="monospace")
        gate_xs=([] if n_ops==0 else
                 [(1.8+fig_w-1.0)/2] if n_ops==1 else
                 np.linspace(1.8,fig_w-1.0,n_ops).tolist())
        for step,(op,gx) in enumerate(zip(sim_gates,gate_xs)):
            itq=op["type"]=="tq"
            ec=PURPLE if itq else (CYAN if is_running else BLUE)
            fc=SIDEBAR if not is_running else ("#F0E8F8" if itq else "#E8F4FB")
            if not itq:
                q=op["qubit"]; wy=wire_ys[q]; gk=op["gate"]
                ax.add_patch(mpatches.FancyBboxPatch((gx-0.39,wy-0.26),0.78,0.52,
                    boxstyle="round,pad=0.03",linewidth=1.3,edgecolor=ec,facecolor=fc,zorder=3))
                ax.text(gx,wy+(0.08 if SQ_GATES[gk]["has_theta"] else 0),SQ_GATES[gk]["label"],
                        color=YELLOW,fontsize=8.5,fontfamily="monospace",ha="center",va="center",fontweight="bold",zorder=4)
                if SQ_GATES[gk]["has_theta"]:
                    ax.text(gx,wy-0.14,f"θ={op['theta']:.2f}",color=DIM,fontsize=6,fontfamily="monospace",ha="center",zorder=4)
            else:
                cy=wire_ys[op["ctrl"]]; ty=wire_ys[op["tgt"]]; gk=op["gate"]
                ylo=min(cy,ty); yhi=max(cy,ty)
                ax.plot([gx,gx],[ylo,yhi],color=ec,lw=1.6,zorder=2)
                if gk=="CNOT":
                    ax.plot(gx,cy,'o',color=ec,markersize=9,zorder=5)
                    ax.plot(gx,cy,'o',color=BG,markersize=3.5,zorder=6)
                    r=0.18; ax.add_patch(plt.Circle((gx,ty),r,color=fc,ec=ec,lw=1.6,zorder=5))
                    ax.plot([gx-r,gx+r],[ty,ty],color=ec,lw=1.6,zorder=6)
                    ax.plot([gx,gx],[ty-r,ty+r],color=ec,lw=1.6,zorder=6)
                elif gk=="CZ":
                    for yy in [cy,ty]: ax.plot(gx,yy,'o',color=ec,markersize=9,zorder=5)
                elif gk in ("SWAP","iSWAP"):
                    d=0.16
                    for yy in [cy,ty]:
                        ax.plot([gx-d,gx+d],[yy-d,yy+d],color=ec,lw=2,zorder=6)
                        ax.plot([gx-d,gx+d],[yy+d,yy-d],color=ec,lw=2,zorder=6)
                    if gk=="iSWAP": ax.text(gx+0.22,(cy+ty)/2,"i",color=ec,fontsize=7,fontfamily="monospace")
                else:
                    ax.add_patch(mpatches.FancyBboxPatch((gx-0.45,ylo-0.22),0.9,yhi-ylo+0.44,
                        boxstyle="round,pad=0.03",linewidth=1.4,edgecolor=ec,facecolor=fc,zorder=3))
                    ax.text(gx,(cy+ty)/2+(0.1 if TQ_GATES[gk]["has_theta"] else 0),TQ_GATES[gk]["label"],
                            color=PURPLE,fontsize=8,fontfamily="monospace",ha="center",va="center",fontweight="bold",zorder=4)
                    if TQ_GATES[gk]["has_theta"]:
                        ax.text(gx,(cy+ty)/2-0.14,f"θ={op['theta']:.2f}",color=DIM,fontsize=6,fontfamily="monospace",ha="center",zorder=4)
            ax.text(gx,top_y+0.62,f"#{step+1}",color=DIM,fontsize=6.5,fontfamily="monospace",ha="center")
        for q,wy in enumerate(wire_ys):
            ax.text(fig_w-0.2,wy,f"q{q}",color=CYAN,fontsize=9,fontfamily="monospace",va="center")
        if is_running: ax.text(fig_w/2,-0.6,"● simulation active",color=GREEN,fontsize=8,fontfamily="monospace",ha="center")
        if n_ops==0: ax.text(fig_w/2,top_y/2,"// add gates to build circuit",color=BORDER,fontsize=10,fontfamily="monospace",ha="center",va="center")
        plt.tight_layout(pad=0.2); st.pyplot(fig,use_container_width=True); plt.close(fig)

    with tab2:
        st.markdown(f"<p style='color:{DIM};font-family:JetBrains Mono,monospace;font-size:0.7rem;"
                    f"margin-bottom:0.3rem'>// Top {len(top_sorted)} states (of {2**sim_n} total)</p>",
                    unsafe_allow_html=True)
        fig,ax=plt.subplots(figsize=(10,4.4))
        fig.patch.set_facecolor(BG); ax.set_facecolor(SIDEBAR)
        top_probs=[probs_d[i] for i in top_sorted]; top_labels=[basis_all[i] for i in top_sorted]
        cmap_vals=plt.cm.Blues(np.linspace(0.35,0.85,len(top_sorted)))
        alpha=1.0 if is_running else 0.4
        bars=ax.bar(range(len(top_sorted)),top_probs,color=cmap_vals,edgecolor=BORDER,linewidth=0.7,alpha=alpha)
        ax.set_xticks(range(len(top_sorted)))
        ax.set_xticklabels(top_labels,rotation=55,ha="right",fontfamily="monospace",fontsize=max(6,10-sim_n),color=WHITE)
        for bar,p in zip(bars,top_probs):
            if p>0.015:
                ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+0.012,f"{p:.3f}",
                        ha="center",va="bottom",color=WHITE if is_running else DIM,
                        fontsize=max(6.5,9-sim_n),fontfamily="monospace")
        ax.set_ylim(0,1.15); ax.set_ylabel("Probability",color=DIM,fontsize=9,fontfamily="monospace")
        title_ops=" → ".join(op_label(op,sim_n)[0] for op in sim_gates) or "I"
        ax.set_title(f"// {title_ops[:80]}{'…' if len(title_ops)>80 else ''}",
                     color=GREEN,fontsize=8,fontfamily="monospace",pad=8,loc="left")
        ax.tick_params(colors=DIM,labelsize=8); ax.spines[:].set_color(BORDER)
        if not is_running:
            ax.text(0.5,0.52,"// run simulation to confirm",transform=ax.transAxes,
                    color=BORDER,fontsize=11,fontfamily="monospace",ha="center",va="center")
        plt.tight_layout(); st.pyplot(fig,use_container_width=True); plt.close(fig)

    with tab3:
        st.markdown(f"<p style='color:{DIM};font-family:JetBrains Mono,monospace;font-size:0.7rem;"
                    f"margin-bottom:0.4rem'>// Pairwise entanglement: 1−Tr(ρᵢ²) ∈ [0,0.5]</p>",
                    unsafe_allow_html=True)
        ent_mat=entanglement_matrix(state_disp,sim_n)
        sz=max(3.5,sim_n*0.62+1.0); fig,ax=plt.subplots(figsize=(sz,sz))
        fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
        alpha_e=1.0 if is_running else 0.4
        im=ax.imshow(ent_mat,cmap="YlOrRd",vmin=0,vmax=0.5,aspect="equal",alpha=alpha_e)
        cb=plt.colorbar(im,ax=ax,fraction=0.04,pad=0.04)
        cb.set_label("entanglement proxy",color=DIM,fontsize=8,fontfamily="monospace")
        cb.ax.tick_params(colors=DIM,labelsize=7)
        ax.set_xticks(range(sim_n)); ax.set_yticks(range(sim_n))
        ax.set_xticklabels([f"q{i}" for i in range(sim_n)],color=WHITE,fontfamily="monospace",fontsize=9)
        ax.set_yticklabels([f"q{i}" for i in range(sim_n)],color=WHITE,fontfamily="monospace",fontsize=9)
        for i in range(sim_n):
            for j in range(sim_n):
                if i!=j:
                    v=ent_mat[i,j]
                    ax.text(j,i,f"{v:.2f}",ha="center",va="center",
                            color="white" if v>0.28 else WHITE,fontsize=8,fontfamily="monospace",alpha=alpha_e)
        ax.set_title("// pairwise entanglement",color=GREEN,fontsize=8.5,fontfamily="monospace",loc="left",pad=8)
        ax.spines[:].set_color(BORDER); ax.tick_params(colors=DIM)
        if not is_running:
            ax.text(0.5,0.5,"// run simulation to confirm",transform=ax.transAxes,
                    color=BORDER,fontsize=10,fontfamily="monospace",ha="center",va="center")
        plt.tight_layout(); st.pyplot(fig,use_container_width=True); plt.close(fig)

# ── State vector table ────────────────────────────────────────────────────────
st.markdown(f"<div class='vsc-section'>Full state vector |ψ⟩ — all {2**sim_n} basis states</div>",
            unsafe_allow_html=True)
rows_html=""
for i in range(2**sim_n):
    p=probs_d[i]; ph=phases_d[i]; amp=state_disp[i]; lbl=basis_all[i]
    bar_pct=int(p*100); active=p>0.001
    bc=CYAN if active else DIM; pc=YELLOW if active else DIM; brc=CYAN if active else BORDER
    rows_html+=f"""<tr>
        <td style="padding:0.38rem 0.9rem;text-align:center;border-bottom:1px solid {BORDER};
                   font-size:0.88rem;font-weight:700;color:{bc};white-space:nowrap">{lbl}</td>
        <td style="padding:0.38rem 0.9rem;text-align:center;border-bottom:1px solid {BORDER}">
          <div style="background:{PANEL};border-radius:3px;height:5px;width:100px;margin:0 auto;overflow:hidden">
            <div style="background:{brc};width:{bar_pct}%;height:100%;border-radius:3px"></div></div></td>
        <td style="padding:0.38rem 0.9rem;text-align:center;border-bottom:1px solid {BORDER};
                   color:{pc};font-weight:600">{p:.6f}</td>
        <td style="padding:0.38rem 0.9rem;text-align:center;border-bottom:1px solid {BORDER};
                   color:{WHITE}">{amp.real:+.4f}&nbsp;{amp.imag:+.4f}i</td>
        <td style="padding:0.38rem 0.9rem;text-align:center;border-bottom:1px solid {BORDER};
                   color:{ORANGE}">{np.degrees(ph):+.1f}°</td></tr>"""
table_h=min(520,max(200,2**sim_n*38+50))
components.html(f"""<!DOCTYPE html><html><head><style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&display=swap');
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:{BG};font-family:'JetBrains Mono',monospace;overflow:hidden}}
  .wrap{{height:{table_h}px;overflow-y:auto;border:1px solid {BORDER};border-radius:6px}}
  table{{width:100%;border-collapse:collapse;background:{SIDEBAR}}}
  thead{{position:sticky;top:0;z-index:10}}
  thead th{{background:{PANEL};color:{DIM};font-size:0.6rem;letter-spacing:2px;text-transform:uppercase;
            padding:0.48rem 0.9rem;text-align:center;border-bottom:2px solid {BORDER};font-weight:500}}
  tbody tr:last-child td{{border-bottom:none!important}}
  tbody tr:hover td{{background:{PANEL}}}
</style></head><body><div class="wrap"><table>
  <thead><tr><th>Basis</th><th>Probability</th><th>P(|·⟩)</th><th>Amplitude</th><th>Phase φ</th></tr></thead>
  <tbody>{rows_html}</tbody></table></div></body></html>""", height=table_h+4, scrolling=False)

# ── Export ────────────────────────────────────────────────────────────────────
st.markdown(f"<div class='vsc-section'>Save &amp; Export</div>", unsafe_allow_html=True)
sc1,sc2,sc3=st.columns(3,gap="small")
exp=build_export(sim_n,sim_gates,st.session_state.notes,st.session_state.circuit_name,state_disp,probs_d,basis_all)
ej=json.dumps(exp,indent=2)
sn="".join(c if c.isalnum() or c in "-_ " else "_" for c in st.session_state.circuit_name).strip().replace(" ","_") or "circuit"
ts=datetime.datetime.now().strftime("%Y%m%d_%H%M")
with sc1: st.download_button("⬇  DOWNLOAD JSON",data=ej,file_name=f"{sn}_{ts}.json",mime="application/json")
with sc2:
    lines=[f"Quantum Circuit — {st.session_state.circuit_name}",f"Saved: {exp['timestamp']}",
           f"Qubits: {sim_n}  |  Gates: {len(sim_gates)}","","── Gates ──"]
    for i,op in enumerate(sim_gates):
        lb,_=op_label(op,sim_n); lines.append(f"  #{i+1}  {lb}")
    lines+=["","── Notes ──",st.session_state.notes or "(none)","","── State Vector (non-zero) ──"]
    for i in range(2**sim_n):
        if probs_d[i]>1e-6:
            lines.append(f"  {basis_all[i]}  P={probs_d[i]:.6f}  amp={state_disp[i].real:+.4f}{state_disp[i].imag:+.4f}i  φ={np.degrees(phases_d[i]):+.1f}°")
    st.download_button("⬇  DOWNLOAD TXT",data="\n".join(lines),file_name=f"{sn}_{ts}.txt",mime="text/plain")
with sc3:
    st.markdown(f"<div style='background:{PANEL};border:1px solid {BORDER};border-radius:4px;"
                f"padding:0.42rem 0.9rem;font-family:JetBrains Mono,monospace;font-size:0.72rem;"
                f"color:{DIM};text-align:center'><span style='color:{YELLOW}'>{sn}</span><br>"
                f"<span style='font-size:0.62rem'>{len(sim_gates)} gates · {sim_n} qubits</span></div>",
                unsafe_allow_html=True)

ops_str=" → ".join(op_label(op,sim_n)[0] for op in sim_gates) or "I"
st.markdown(f"<p style='color:{BORDER};font-family:JetBrains Mono,monospace;font-size:0.66rem;"
            f"border-top:1px solid {BORDER};padding-top:0.45rem;margin-top:0.5rem'>"
            f"// |ψ⟩ = {ops_str[:120]}{'…' if len(ops_str)>120 else ''} · "
            f"|{'0'*sim_n}⟩ &nbsp;·&nbsp; dim=2<sup>{sim_n}</sup>={2**sim_n}</p>",
            unsafe_allow_html=True)