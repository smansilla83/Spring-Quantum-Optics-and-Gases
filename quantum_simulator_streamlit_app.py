"""
Quantum Circuit Simulator — up to 10 qubits
Includes: measurement gates, teleportation protocol tab
"""

import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import json, datetime, random

st.set_page_config(page_title="Quantum Circuit Simulator", page_icon="⚛️", layout="wide")

BG     = "#FAF8F4"
SIDEBAR= "#F3EFE8"
PANEL  = "#EEEAE2"
BORDER = "#D4CEBF"
BLUE   = "#0070C1"
CYAN   = "#267F99"
GREEN  = "#448C31"
YELLOW = "#795E26"
ORANGE = "#A31515"
PURPLE = "#AF00DB"
WHITE  = "#1E1E1E"
DIM    = "#6E6E6E"
RED    = "#C2185B"

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@400;500;600;700&display=swap');
  html,body,[class*="css"]{{font-family:'Inter',sans-serif;background-color:{BG}!important;color:{WHITE}}}
  .main,.stApp{{background:{BG}!important}}
  section[data-testid="stMain"]>div{{background:{BG}!important}}
  .block-container{{padding-top:3.5rem;max-width:1600px;background:{BG}}}
  .qc-header{{padding-bottom:0.7rem;margin-bottom:1.1rem;border-bottom:2px solid {BORDER}}}
  .qc-title{{font-family:'JetBrains Mono',monospace;font-size:clamp(1rem,1.8vw,1.55rem);font-weight:700;color:{CYAN};margin:0 0 0.18rem 0;line-height:1.2}}
  .qc-subtitle{{font-family:'JetBrains Mono',monospace;font-size:0.72rem;color:{DIM};margin:0}}
  .vsc-section{{color:{DIM};font-family:'JetBrains Mono',monospace;font-size:0.6rem;letter-spacing:2px;text-transform:uppercase;border-bottom:1px solid {BORDER};padding-bottom:0.18rem;margin:0.75rem 0 0.45rem 0}}
  .vsc-card{{background:{PANEL};border:1px solid {BORDER};border-left:3px solid {CYAN};border-radius:4px;padding:0.6rem 0.85rem;margin-bottom:0.45rem;font-family:'JetBrains Mono',monospace}}
  .vsc-card-label{{color:{DIM};font-size:0.58rem;letter-spacing:1.5px;text-transform:uppercase}}
  .vsc-card-value{{color:{YELLOW};font-size:1.05rem;font-weight:700;line-height:1.3}}
  .vsc-card-sub{{color:{DIM};font-size:0.68rem}}
  .gate-item{{display:flex;align-items:flex-start;gap:8px;background:white;border:1px solid {BORDER};border-left:4px solid {CYAN};border-radius:5px;padding:0.42rem 0.7rem 0.38rem 0.7rem;margin-bottom:5px;font-family:'JetBrains Mono',monospace;box-shadow:0 1px 3px rgba(0,0,0,0.05)}}
  .gate-item-tq{{border-left-color:{PURPLE}!important;background:#FDFAFF!important}}
  .gate-item-meas{{border-left-color:{RED}!important;background:#FFF5F8!important}}
  .gate-item-inner{{flex:1;min-width:0}}
  .gate-item-top{{display:flex;align-items:center;gap:6px;margin-bottom:2px}}
  .gate-item-badge{{background:{CYAN};color:white;border-radius:3px;padding:1px 6px;font-size:0.62rem;font-weight:700;white-space:nowrap;flex-shrink:0}}
  .gate-badge-tq{{background:{PURPLE}!important}}
  .gate-badge-meas{{background:{RED}!important}}
  .gate-item-name{{color:{YELLOW};font-weight:700;font-size:0.84rem}}
  .gate-item-name-tq{{color:{PURPLE}!important}}
  .gate-item-name-meas{{color:{RED}!important}}
  .gate-item-detail{{color:{DIM};font-size:0.68rem;margin-top:1px}}
  .gate-item-qubit{{display:inline-block;background:{PANEL};border:1px solid {BORDER};border-radius:3px;padding:0px 5px;font-size:0.65rem;color:{CYAN};font-weight:600;margin-right:3px}}
  .gate-item-qubit-tq{{color:{PURPLE}!important}}
  .gate-item-qubit-meas{{color:{RED}!important}}
  .gate-list-empty{{font-family:'JetBrains Mono',monospace;font-size:0.72rem;color:{BORDER};text-align:center;padding:1rem 0.5rem;border:1px dashed {BORDER};border-radius:4px}}
  div[data-testid="stButton"]>button{{background:{BG}!important;border:1.5px solid {BORDER}!important;color:{DIM}!important;font-family:'JetBrains Mono',monospace!important;font-weight:600!important;font-size:0.78rem!important;letter-spacing:1px!important;border-radius:4px!important;padding:0.4rem 0.5rem!important;width:100%!important;transition:all 0.15s!important}}
  div[data-testid="stButton"]>button:hover{{background:{PANEL}!important;border-color:{CYAN}!important;color:{CYAN}!important}}
  .action-btn div[data-testid="stButton"]>button{{background:{BG}!important;border-color:{BLUE}!important;color:{BLUE}!important}}
  .action-btn div[data-testid="stButton"]>button:hover{{background:{BLUE}12!important;border-color:{CYAN}!important;color:{CYAN}!important}}
  .sq-active div[data-testid="stButton"]>button{{background:{CYAN}1A!important;border-color:{CYAN}!important;color:{CYAN}!important}}
  .tq-active div[data-testid="stButton"]>button{{background:{PURPLE}18!important;border-color:{PURPLE}!important;color:{PURPLE}!important}}
  .meas-active div[data-testid="stButton"]>button{{background:{RED}18!important;border-color:{RED}!important;color:{RED}!important}}
  .add-gate-panel{{background:{SIDEBAR};border:1.5px solid {BORDER};border-top:3px solid {BLUE};border-radius:6px;padding:0.85rem 1rem 0.7rem 1rem;margin-bottom:0.8rem}}
  .add-gate-panel-title{{font-family:'JetBrains Mono',monospace;font-size:0.62rem;letter-spacing:2px;text-transform:uppercase;color:{BLUE};margin-bottom:0.6rem;font-weight:600}}
  .toggle-label{{font-family:'JetBrains Mono',monospace;font-size:0.6rem;letter-spacing:1.5px;text-transform:uppercase;color:{DIM};margin-bottom:0.25rem}}
  .notes-panel{{background:{SIDEBAR};border:1.5px solid {BORDER};border-top:3px solid {YELLOW};border-radius:6px;padding:0.85rem 1rem 0.9rem 1rem;margin-top:1rem}}
  .notes-panel-title{{font-family:'JetBrains Mono',monospace;font-size:0.62rem;letter-spacing:2px;text-transform:uppercase;color:{YELLOW};margin-bottom:0.5rem;font-weight:600}}
  .badge-running{{background:#EAF5EA;border:1px solid {GREEN};border-radius:3px;padding:0.26rem 0.6rem;color:{GREEN};font-family:'JetBrains Mono',monospace;font-size:0.68rem;text-align:center;margin-top:0.3rem}}
  .badge-idle{{background:{PANEL};border:1px solid {BORDER};border-radius:3px;padding:0.26rem 0.6rem;color:{DIM};font-family:'JetBrains Mono',monospace;font-size:0.68rem;text-align:center;margin-top:0.3rem}}
  .tele-box{{background:{SIDEBAR};border:1.5px solid {BORDER};border-radius:6px;padding:0.8rem 1rem;margin-bottom:0.6rem;font-family:'JetBrains Mono',monospace}}
  .tele-box-title{{font-size:0.6rem;letter-spacing:2px;text-transform:uppercase;color:{DIM};margin-bottom:0.4rem;font-weight:600}}
  .tele-result{{background:white;border:1px solid {BORDER};border-left:4px solid {GREEN};border-radius:4px;padding:0.6rem 0.9rem;font-family:'JetBrains Mono',monospace;margin-top:0.5rem}}
  div[data-testid="stTabs"] button{{font-family:'JetBrains Mono',monospace!important;font-size:0.75rem!important;color:{DIM}!important}}
  div[data-testid="stTabs"] button[aria-selected="true"]{{color:{CYAN}!important;border-bottom:2px solid {CYAN}!important}}
  div[data-testid="stSlider"] label,div[data-testid="stSlider"] p{{color:{WHITE}!important;font-family:'JetBrains Mono',monospace!important;font-size:0.74rem!important}}
  div[data-testid="stSelectbox"] label{{color:{WHITE}!important;font-family:'JetBrains Mono',monospace!important;font-size:0.72rem!important}}
  div[data-testid="stSelectbox"]>div>div{{background:{PANEL}!important;border:1px solid {BORDER}!important;border-radius:4px!important;font-family:'JetBrains Mono',monospace!important;color:{YELLOW}!important;font-size:0.82rem!important}}
  div[data-testid="stTextArea"] label{{color:{WHITE}!important;font-family:'JetBrains Mono',monospace!important;font-size:0.72rem!important}}
  div[data-testid="stTextArea"] textarea{{background:{PANEL}!important;border:1px solid {BORDER}!important;border-radius:4px!important;color:{WHITE}!important;font-family:'JetBrains Mono',monospace!important;font-size:0.8rem!important;resize:vertical!important}}
  div[data-testid="stTextInput"] label{{color:{WHITE}!important;font-family:'JetBrains Mono',monospace!important;font-size:0.72rem!important}}
  div[data-testid="stNumberInput"] label{{color:{WHITE}!important;font-family:'JetBrains Mono',monospace!important;font-size:0.72rem!important}}
  div[data-testid="stNumberInput"] input{{background:{PANEL}!important;border:1px solid {BORDER}!important;border-radius:4px!important;color:{YELLOW}!important;font-family:'JetBrains Mono',monospace!important;font-size:0.88rem!important;font-weight:600!important}}
  div[data-testid="stNumberInput"] div[data-testid="stNumberInputStepDown"] button,
  div[data-testid="stNumberInput"] div[data-testid="stNumberInputStepUp"] button{{width:auto!important;padding:0.2rem 0.4rem!important;font-size:0.7rem!important;border:1px solid {BORDER}!important;color:{DIM}!important}}
  div[data-testid="stTextInput"] input{{background:{PANEL}!important;border:1px solid {BORDER}!important;border-radius:4px!important;color:{WHITE}!important;font-family:'JetBrains Mono',monospace!important;font-size:0.82rem!important}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# GATE LIBRARY
# ─────────────────────────────────────────────────────────────────────────────
SQ_GATES = {
    "H":   {"label":"H",      "desc":"Hadamard",       "has_theta":False, "color":CYAN,
            "matrix": lambda t: np.array([[1,1],[1,-1]],dtype=complex)/np.sqrt(2)},
    "X":   {"label":"X",      "desc":"Pauli-X (NOT)",  "has_theta":False, "color":CYAN,
            "matrix": lambda t: np.array([[0,1],[1,0]],dtype=complex)},
    "Y":   {"label":"Y",      "desc":"Pauli-Y",        "has_theta":False, "color":CYAN,
            "matrix": lambda t: np.array([[0,-1j],[1j,0]],dtype=complex)},
    "Z":   {"label":"Z",      "desc":"Pauli-Z",        "has_theta":False, "color":CYAN,
            "matrix": lambda t: np.array([[1,0],[0,-1]],dtype=complex)},
    "S":   {"label":"S",      "desc":"Phase √Z",       "has_theta":False, "color":CYAN,
            "matrix": lambda t: np.array([[1,0],[0,1j]],dtype=complex)},
    "Sdg": {"label":"S†",     "desc":"Phase √Z†",      "has_theta":False, "color":CYAN,
            "matrix": lambda t: np.array([[1,0],[0,-1j]],dtype=complex)},
    "T":   {"label":"T",      "desc":"π/8 gate",       "has_theta":False, "color":CYAN,
            "matrix": lambda t: np.array([[1,0],[0,np.exp(1j*np.pi/4)]],dtype=complex)},
    "Tdg": {"label":"T†",     "desc":"π/8 gate†",      "has_theta":False, "color":CYAN,
            "matrix": lambda t: np.array([[1,0],[0,np.exp(-1j*np.pi/4)]],dtype=complex)},
    "SX":  {"label":"√X",     "desc":"Sqrt-X gate",    "has_theta":False, "color":CYAN,
            "matrix": lambda t: np.array([[1+1j,1-1j],[1-1j,1+1j]],dtype=complex)/2},
    "Rx":  {"label":"Rx(θ)",  "desc":"X-rotation",     "has_theta":True,  "color":CYAN,
            "matrix": lambda t: np.array([[np.cos(t/2),-1j*np.sin(t/2)],[-1j*np.sin(t/2),np.cos(t/2)]],dtype=complex)},
    "Ry":  {"label":"Ry(θ)",  "desc":"Y-rotation",     "has_theta":True,  "color":CYAN,
            "matrix": lambda t: np.array([[np.cos(t/2),-np.sin(t/2)],[np.sin(t/2),np.cos(t/2)]],dtype=complex)},
    "Rz":  {"label":"Rz(θ)",  "desc":"Z-rotation",     "has_theta":True,  "color":CYAN,
            "matrix": lambda t: np.array([[np.exp(-1j*t/2),0],[0,np.exp(1j*t/2)]],dtype=complex)},
}

TQ_GATES = {
    "CNOT":  {"label":"CNOT",   "desc":"Controlled-X",  "has_theta":False},
    "CZ":    {"label":"CZ",     "desc":"Controlled-Z",  "has_theta":False},
    "SWAP":  {"label":"SWAP",   "desc":"Swap qubits",   "has_theta":False},
    "iSWAP": {"label":"iSWAP",  "desc":"i·SWAP",        "has_theta":False},
    "CRz":   {"label":"CRz(θ)", "desc":"Controlled Rz", "has_theta":True},
    "XX":    {"label":"XX(θ)",  "desc":"Ising XX",       "has_theta":True},
    "CY":    {"label":"CY",     "desc":"Controlled-Y",  "has_theta":False},
    "CH":    {"label":"CH",     "desc":"Controlled-H",  "has_theta":False},
}

# Measurement gates — handled specially (collapse, not unitary)
MEAS_GATES = {
    "M":     {"label":"M",      "desc":"Measure (Z-basis)",    "has_theta":False},
    "Mx":    {"label":"Mx",     "desc":"Measure (X-basis)",    "has_theta":False},
    "Reset": {"label":"Reset",  "desc":"Reset to |0⟩",         "has_theta":False},
}

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
for k,v in {"n_qubits":3,"running":False,"gate_list":[],"locked_snap":None,
            "notes":"","circuit_name":"My Circuit","gate_type":"Single-qubit",
            "meas_results":{}}.items():
    if k not in st.session_state: st.session_state[k]=v

# ─────────────────────────────────────────────────────────────────────────────
# SIMULATION ENGINE
# ─────────────────────────────────────────────────────────────────────────────
def apply_sq(state, n, qubit, gate_key, theta):
    G=SQ_GATES[gate_key]["matrix"](theta)
    I=np.eye(2,dtype=complex)
    ops=[G if i==qubit else I for i in range(n)]
    U=ops[0]
    for op in ops[1:]: U=np.kron(U,op)
    return U@state

def apply_tq(state, n, gate_key, ctrl, tgt, theta):
    N=2**n; out=state.copy()
    def _cx(s,o,c,t):
        for idx in range(N):
            if (idx>>(n-1-c))&1:
                f=idx^(1<<(n-1-t))
                if idx<f: o[idx],o[f]=s[f],s[idx]
    if gate_key=="CNOT": _cx(state,out,ctrl,tgt)
    elif gate_key=="CZ":
        for idx in range(N):
            if ((idx>>(n-1-ctrl))&1) and ((idx>>(n-1-tgt))&1): out[idx]=-state[idx]
    elif gate_key=="CY":
        for idx in range(N):
            if (idx>>(n-1-ctrl))&1:
                tb=(idx>>(n-1-tgt))&1; f=idx^(1<<(n-1-tgt))
                out[idx]  = (-1j if tb==1 else 1j)*state[f] if idx!=f else state[idx]
        # redo cleanly
        out=state.copy()
        for idx in range(N):
            if (idx>>(n-1-ctrl))&1:
                f=idx^(1<<(n-1-tgt)); tb=(idx>>(n-1-tgt))&1
                if idx<f:
                    out[idx]= 1j*state[f]
                    out[f]  =-1j*state[idx]
    elif gate_key=="CH":
        H2=np.array([[1,1],[1,-1]],dtype=complex)/np.sqrt(2)
        for idx in range(N):
            if (idx>>(n-1-ctrl))&1:
                f=idx^(1<<(n-1-tgt)); tb=(idx>>(n-1-tgt))&1
                if idx<f:
                    v0,v1=state[idx],state[f]
                    out[idx]=H2[0,0]*v0+H2[0,1]*v1
                    out[f]  =H2[1,0]*v0+H2[1,1]*v1
    elif gate_key=="SWAP":
        for idx in range(N):
            cb=(idx>>(n-1-ctrl))&1; tb=(idx>>(n-1-tgt))&1
            if cb!=tb:
                f=idx^(1<<(n-1-ctrl))^(1<<(n-1-tgt))
                if idx<f: out[idx],out[f]=state[f],state[idx]
    elif gate_key=="iSWAP":
        out=state.copy()
        for idx in range(N):
            cb=(idx>>(n-1-ctrl))&1; tb=(idx>>(n-1-tgt))&1
            if cb!=tb:
                f=idx^(1<<(n-1-ctrl))^(1<<(n-1-tgt))
                if idx<f: out[idx]=1j*state[f]; out[f]=1j*state[idx]
    elif gate_key=="CRz":
        for idx in range(N):
            if (idx>>(n-1-ctrl))&1:
                tb=(idx>>(n-1-tgt))&1
                out[idx]=state[idx]*(np.exp(-1j*theta/2) if tb==0 else np.exp(1j*theta/2))
    elif gate_key=="XX":
        c,s=np.cos(theta/2),np.sin(theta/2)
        for idx in range(N):
            f=idx^(1<<(n-1-ctrl))^(1<<(n-1-tgt)); out[idx]=c*state[idx]-1j*s*state[f]
    return out

def apply_measure(state, n, qubit, basis="Z"):
    """Collapse qubit in Z or X basis. Returns (new_state, outcome 0/1)."""
    N=2**n
    if basis=="X":
        # rotate to X basis first (apply H), measure, rotate back
        H=SQ_GATES["H"]["matrix"](0)
        I=np.eye(2,dtype=complex); ops=[H if i==qubit else I for i in range(n)]
        U=ops[0]
        for op in ops[1:]: U=np.kron(U,op)
        state=U@state
    # compute P(0) and P(1) for qubit
    p0=sum(abs(state[idx])**2 for idx in range(N) if not ((idx>>(n-1-qubit))&1))
    p1=1-p0
    outcome=0 if (random.random()<p0) else 1
    # project
    new_state=state.copy()
    norm=np.sqrt(p0 if outcome==0 else p1)
    for idx in range(N):
        bit=(idx>>(n-1-qubit))&1
        if bit!=outcome: new_state[idx]=0
    if norm>1e-10: new_state/=norm
    if basis=="X":
        state2=U@new_state  # rotate back
        return state2, outcome
    return new_state, outcome

def apply_reset(state, n, qubit):
    """Reset qubit to |0⟩ by measuring and applying X if needed."""
    state, outcome = apply_measure(state, n, qubit)
    if outcome==1: state=apply_sq(state,n,qubit,"X",0)
    return state

def simulate(n, gate_list):
    state=np.zeros(2**n,dtype=complex); state[0]=1.0
    meas_results={}
    for step_i, op in enumerate(gate_list):
        if op["type"]=="sq":
            state=apply_sq(state,n,op["qubit"],op["gate"],op.get("theta",0.0))
        elif op["type"]=="tq":
            state=apply_tq(state,n,op["gate"],op["ctrl"],op["tgt"],op.get("theta",0.0))
        elif op["type"]=="meas":
            gk=op["gate"]
            if gk=="Reset":
                state=apply_reset(state,n,op["qubit"])
            else:
                basis="X" if gk=="Mx" else "Z"
                state,outcome=apply_measure(state,n,op["qubit"],basis)
                meas_results[f"step{step_i}_q{op['qubit']}"]=outcome
    return state, meas_results

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
    elif op["type"]=="meas":
        return f"{MEAS_GATES[op['gate']]['label']} → q{op['qubit']}", False
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

# ─────────────────────────────────────────────────────────────────────────────
# TELEPORTATION ENGINE
# ─────────────────────────────────────────────────────────────────────────────
def run_teleportation(alpha, beta):
    """
    Quantum teleportation of |ψ⟩ = alpha|0⟩ + beta|1⟩
    q0 = sender (Alice's qubit to teleport)
    q1 = Alice's half of Bell pair
    q2 = Bob's half of Bell pair

    Returns full state evolution as list of (label, state_3q) tuples,
    measurement outcomes, and verification of q2 final state.
    """
    n=3; N=8
    # Normalize
    norm=np.sqrt(abs(alpha)**2+abs(beta)**2)
    a,b=alpha/norm, beta/norm

    history=[]

    # Step 0: Initial state |ψ⟩|00⟩  = (a|0⟩+b|1⟩)|00⟩
    state=np.zeros(N,dtype=complex)
    state[0b000]=a   # |000⟩
    state[0b100]=b   # |100⟩
    history.append(("Initial |ψ⟩⊗|00⟩", state.copy()))

    # Step 1: H on q1 → create superposition for Bell pair
    H=SQ_GATES["H"]["matrix"](0); I=np.eye(2,dtype=complex)
    U=np.kron(np.kron(I,H),I)
    state=U@state
    history.append(("H on q1", state.copy()))

    # Step 2: CNOT(q1→q2) → Bell pair between q1,q2
    state2=state.copy()
    for idx in range(N):
        if (idx>>(n-1-1))&1:  # q1 is ctrl
            f=idx^(1<<(n-1-2))
            if idx<f: state2[idx],state2[f]=state[f],state[idx]
    state=state2
    history.append(("CNOT q1→q2 (Bell pair)", state.copy()))

    # Step 3: CNOT(q0→q1) — Alice's encoding
    state2=state.copy()
    for idx in range(N):
        if (idx>>(n-1-0))&1:
            f=idx^(1<<(n-1-1))
            if idx<f: state2[idx],state2[f]=state[f],state[idx]
    state=state2
    history.append(("CNOT q0→q1 (Alice encodes)", state.copy()))

    # Step 4: H on q0 — Alice's second operation
    U=np.kron(np.kron(H,I),I)
    state=U@state
    history.append(("H on q0 (Alice encodes)", state.copy()))

    # Step 5: Measure q0 and q1
    state,m0=apply_measure(state,n,0)
    state,m1=apply_measure(state,n,1)
    history.append((f"Measure q0={m0}, q1={m1}", state.copy()))

    # Step 6: Classical correction on q2
    # If m1==1: apply X to q2
    # If m0==1: apply Z to q2
    corrections=[]
    if m1==1:
        state=apply_sq(state,n,2,"X",0); corrections.append("X on q2")
    if m0==1:
        state=apply_sq(state,n,2,"Z",0); corrections.append("Z on q2")
    label="Corrections: "+", ".join(corrections) if corrections else "No corrections needed"
    history.append((label, state.copy()))

    # Extract q2 reduced state
    rho2=np.zeros((2,2),dtype=complex)
    for idx in range(N):
        b2=(idx>>(n-1-2))&1
        for jdx in range(N):
            b22=(jdx>>(n-1-2))&1
            mask=~(1<<(n-1-2))&(N-1)
            if (idx&mask)==(jdx&mask):
                rho2[b2,b22]+=state[idx]*np.conj(state[jdx])

    # Expected: rho2 should be |a|²|0⟩⟨0| + ab*|0⟩⟨1| + a*b|1⟩⟨0| + |b|²|1⟩⟨1|
    # i.e. outer product of (a,b) with itself
    expected=np.outer([a,b],np.conj([a,b]))
    fidelity=float(np.real(np.trace(expected@rho2)))

    return history, m0, m1, corrections, fidelity, rho2, a, b

# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="qc-header">
  <div class="qc-title">⚛ Quantum Circuit Simulator</div>
  <div class="qc-subtitle">// up to 10 qubits · build circuit gate by gate · measurement · teleportation</div>
</div>""", unsafe_allow_html=True)

col_ctrl, col_main = st.columns([1, 2.8], gap="large")

# ─────────────────────────────────────────────────────────────────────────────
# LEFT COLUMN — CIRCUIT BUILDER
# ─────────────────────────────────────────────────────────────────────────────
with col_ctrl:
    disabled=st.session_state.running
    is_sq=st.session_state.gate_type=="Single-qubit"
    is_tq=st.session_state.gate_type=="Two-qubit"
    is_meas=st.session_state.gate_type=="Measurement"

    st.markdown(f"<div class='vsc-section'>System</div>", unsafe_allow_html=True)
    n=st.slider("Qubits",2,10,value=st.session_state.n_qubits,disabled=disabled,key="n_slider")
    st.session_state.n_qubits=n
    st.markdown(f"<p style='color:{DIM};font-family:JetBrains Mono,monospace;font-size:0.68rem;"
                f"margin-top:-0.3rem'>// 2<sup>{n}</sup> = {2**n} basis states</p>",
                unsafe_allow_html=True)

    # ── Add Gate Panel ────────────────────────────────────────────────────
    st.markdown(f"<div class='add-gate-panel'><div class='add-gate-panel-title'>＋ Add Gate</div>",
                unsafe_allow_html=True)
    st.markdown(f"<div class='toggle-label'>Gate type</div>", unsafe_allow_html=True)

    col_sq, col_tq, col_meas = st.columns(3)
    with col_sq:
        st.markdown(f"<div class='{'sq-active' if is_sq else ''}'>", unsafe_allow_html=True)
        if st.button("● Single" if is_sq else "Single", key="btn_sq", disabled=disabled):
            st.session_state.gate_type="Single-qubit"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with col_tq:
        st.markdown(f"<div class='{'tq-active' if is_tq else ''}'>", unsafe_allow_html=True)
        if st.button("● Two-q" if is_tq else "Two-q", key="btn_tq", disabled=disabled):
            st.session_state.gate_type="Two-qubit"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with col_meas:
        st.markdown(f"<div class='{'meas-active' if is_meas else ''}'>", unsafe_allow_html=True)
        if st.button("● Meas" if is_meas else "Meas", key="btn_meas", disabled=disabled):
            st.session_state.gate_type="Measurement"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:0.35rem'></div>", unsafe_allow_html=True)

    if is_sq:
        add_gate=st.selectbox("Gate",list(SQ_GATES.keys()),
            format_func=lambda k:f"{SQ_GATES[k]['label']}  —  {SQ_GATES[k]['desc']}",
            disabled=disabled,key="add_sq_gate",label_visibility="collapsed")
        add_qubit=st.selectbox("Target qubit",list(range(n)),
            format_func=lambda x:f"q{x}",disabled=disabled,key="add_sq_qubit")
        add_theta=0.0
        if SQ_GATES[add_gate]["has_theta"]:
            st.markdown(f"<p style='color:{DIM};font-family:JetBrains Mono,monospace;"
                        f"font-size:0.62rem;margin-bottom:0.15rem;letter-spacing:1px'>"
                        f"rotation angle (radians)</p>", unsafe_allow_html=True)
            if "sq_theta_val" not in st.session_state:
                st.session_state.sq_theta_val = np.pi
            _presets_sq = [("0", 0.0), ("π/6", np.pi/6), ("π/4", np.pi/4),
                           ("π/3", np.pi/3), ("π/2", np.pi/2), ("π", np.pi),
                           ("3π/2", 3*np.pi/2), ("2π", 2*np.pi)]
            _pcols = st.columns(len(_presets_sq))
            for _pc, (_pl, _pv) in zip(_pcols, _presets_sq):
                _active = abs(st.session_state.sq_theta_val - _pv) < 1e-9
                if _pc.button(_pl, key=f"sq_pre_{_pl}", disabled=disabled,
                              help=f"{_pv:.6f} rad"):
                    st.session_state.sq_theta_val = _pv; st.rerun()
            add_theta = st.number_input(
                "theta_sq", min_value=-4*float(np.pi), max_value=4*float(np.pi),
                value=float(st.session_state.sq_theta_val),
                step=0.001, format="%.6f",
                disabled=disabled, key="add_sq_theta",
                label_visibility="collapsed")
            st.session_state.sq_theta_val = add_theta
            _frac = add_theta / np.pi
            st.markdown(f"<p style='color:{CYAN};font-family:JetBrains Mono,monospace;"
                        f"font-size:0.68rem;margin-top:-2px'>"
                        f"{add_theta:.6f} rad &nbsp;=&nbsp; {_frac:.4f}\u03c0"
                        f" &nbsp;=&nbsp; {float(np.degrees(add_theta)):.3f}\u00b0</p>",
                        unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='color:{BORDER};font-family:JetBrains Mono,monospace;"
                        f"font-size:0.68rem'>// no angle parameter</p>",unsafe_allow_html=True)
        theta_chip=(f"&nbsp;&nbsp;<span style='color:{DIM}'>θ=</span><span style='color:{ORANGE}'>{add_theta:.3f}</span>"
                    if SQ_GATES[add_gate]["has_theta"] else "")
        st.markdown(f"<div style='background:{CYAN}0f;border:1px solid {CYAN}44;border-radius:4px;"
                    f"padding:0.32rem 0.7rem;margin:0.4rem 0 0.4rem 0;"
                    f"font-family:JetBrains Mono,monospace;font-size:0.74rem'>"
                    f"<span style='color:{CYAN};font-weight:700'>{SQ_GATES[add_gate]['label']}</span>"
                    f"<span style='color:{DIM}'>&nbsp;on&nbsp;</span>"
                    f"<span style='color:{YELLOW};font-weight:600'>q{add_qubit}</span>{theta_chip}</div>",
                    unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)
        st.markdown("<div class='action-btn'>",unsafe_allow_html=True)
        if st.button("＋  ADD GATE",disabled=disabled,key="add_sq_btn"):
            st.session_state.gate_list.append({"type":"sq","gate":add_gate,"qubit":add_qubit,"theta":add_theta})
            st.rerun()
        st.markdown("</div>",unsafe_allow_html=True)

    elif is_tq:
        add_tq=st.selectbox("Gate",list(TQ_GATES.keys()),
            format_func=lambda k:f"{TQ_GATES[k]['label']}  —  {TQ_GATES[k]['desc']}",
            disabled=disabled,key="add_tq_gate",label_visibility="collapsed")
        c1,c2=st.columns(2)
        with c1:
            add_ctrl=st.selectbox("Control",list(range(n)),
                format_func=lambda x:f"q{x}",disabled=disabled,key="add_tq_ctrl")
        with c2:
            tgt_choices=[q for q in range(n) if q!=add_ctrl]
            add_tgt=st.selectbox("Target",tgt_choices,
                format_func=lambda x:f"q{x}",disabled=disabled,key="add_tq_tgt")
        add_theta2=0.0
        if TQ_GATES[add_tq]["has_theta"]:
            st.markdown(f"<p style='color:{DIM};font-family:JetBrains Mono,monospace;"
                        f"font-size:0.62rem;margin-bottom:0.15rem;letter-spacing:1px'>"
                        f"rotation angle (radians)</p>", unsafe_allow_html=True)
            if "tq_theta_val" not in st.session_state:
                st.session_state.tq_theta_val = np.pi
            _presets_tq = [("0", 0.0), ("π/6", np.pi/6), ("π/4", np.pi/4),
                           ("π/3", np.pi/3), ("π/2", np.pi/2), ("π", np.pi),
                           ("3π/2", 3*np.pi/2), ("2π", 2*np.pi)]
            _pcols2 = st.columns(len(_presets_tq))
            for _pc2, (_pl2, _pv2) in zip(_pcols2, _presets_tq):
                _active2 = abs(st.session_state.tq_theta_val - _pv2) < 1e-9
                if _pc2.button(_pl2, key=f"tq_pre_{_pl2}", disabled=disabled,
                               help=f"{_pv2:.6f} rad"):
                    st.session_state.tq_theta_val = _pv2; st.rerun()
            add_theta2 = st.number_input(
                "theta_tq", min_value=-4*float(np.pi), max_value=4*float(np.pi),
                value=float(st.session_state.tq_theta_val),
                step=0.001, format="%.6f",
                disabled=disabled, key="add_tq_theta",
                label_visibility="collapsed")
            st.session_state.tq_theta_val = add_theta2
            _frac2 = add_theta2 / np.pi
            st.markdown(f"<p style='color:{PURPLE};font-family:JetBrains Mono,monospace;"
                        f"font-size:0.68rem;margin-top:-2px'>"
                        f"{add_theta2:.6f} rad &nbsp;=&nbsp; {_frac2:.4f}\u03c0"
                        f" &nbsp;=&nbsp; {float(np.degrees(add_theta2)):.3f}\u00b0</p>",
                        unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='color:{BORDER};font-family:JetBrains Mono,monospace;"
                        f"font-size:0.68rem'>// no angle parameter</p>",unsafe_allow_html=True)
        theta_chip2=(f"&nbsp;&nbsp;<span style='color:{DIM}'>θ=</span><span style='color:{ORANGE}'>{add_theta2:.3f}</span>"
                     if TQ_GATES[add_tq]["has_theta"] else "")
        st.markdown(f"<div style='background:{PURPLE}0d;border:1px solid {PURPLE}44;border-radius:4px;"
                    f"padding:0.32rem 0.7rem;margin:0.4rem 0 0.4rem 0;"
                    f"font-family:JetBrains Mono,monospace;font-size:0.74rem'>"
                    f"<span style='color:{PURPLE};font-weight:700'>{TQ_GATES[add_tq]['label']}</span>"
                    f"<span style='color:{DIM}'>&nbsp;ctrl=</span><span style='color:{YELLOW};font-weight:600'>q{add_ctrl}</span>"
                    f"<span style='color:{DIM}'>&nbsp;tgt=</span><span style='color:{YELLOW};font-weight:600'>q{add_tgt}</span>"
                    f"{theta_chip2}</div>",unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)
        st.markdown("<div class='action-btn'>",unsafe_allow_html=True)
        if st.button("＋  ADD GATE",disabled=disabled,key="add_tq_btn"):
            st.session_state.gate_list.append({"type":"tq","gate":add_tq,"ctrl":add_ctrl,"tgt":add_tgt,"theta":add_theta2})
            st.rerun()
        st.markdown("</div>",unsafe_allow_html=True)

    else:  # Measurement
        add_meas=st.selectbox("Gate",list(MEAS_GATES.keys()),
            format_func=lambda k:f"{MEAS_GATES[k]['label']}  —  {MEAS_GATES[k]['desc']}",
            disabled=disabled,key="add_meas_gate",label_visibility="collapsed")
        add_mq=st.selectbox("Target qubit",list(range(n)),
            format_func=lambda x:f"q{x}",disabled=disabled,key="add_meas_qubit")
        st.markdown(f"<div style='background:{RED}0d;border:1px solid {RED}44;border-radius:4px;"
                    f"padding:0.32rem 0.7rem;margin:0.4rem 0 0.4rem 0;"
                    f"font-family:JetBrains Mono,monospace;font-size:0.74rem'>"
                    f"<span style='color:{RED};font-weight:700'>{MEAS_GATES[add_meas]['label']}</span>"
                    f"<span style='color:{DIM}'>&nbsp;on&nbsp;</span>"
                    f"<span style='color:{YELLOW};font-weight:600'>q{add_mq}</span>"
                    f"<span style='color:{DIM};font-size:0.65rem'>&nbsp;—&nbsp;{MEAS_GATES[add_meas]['desc']}</span></div>",
                    unsafe_allow_html=True)
        st.markdown(f"<p style='color:{DIM};font-family:JetBrains Mono,monospace;font-size:0.65rem;"
                    f"margin:0.1rem 0 0.2rem 0'>// measurement collapses the state — outcome is random</p>",
                    unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)
        st.markdown("<div class='action-btn'>",unsafe_allow_html=True)
        if st.button("＋  ADD GATE",disabled=disabled,key="add_meas_btn"):
            st.session_state.gate_list.append({"type":"meas","gate":add_meas,"qubit":add_mq})
            st.rerun()
        st.markdown("</div>",unsafe_allow_html=True)

    # ── Gate list ─────────────────────────────────────────────────────────
    n_gates=len(st.session_state.gate_list)
    st.markdown(f"<div style='display:flex;align-items:center;justify-content:space-between;"
                f"border-bottom:1px solid {BORDER};padding-bottom:0.2rem;margin:0.8rem 0 0.5rem 0'>"
                f"<span style='color:{DIM};font-family:JetBrains Mono,monospace;font-size:0.6rem;"
                f"letter-spacing:2px;text-transform:uppercase'>Circuit — {n_gates} gate(s)</span>"
                f"<span style='background:{CYAN};color:white;border-radius:10px;"
                f"padding:1px 8px;font-family:JetBrains Mono,monospace;font-size:0.62rem;"
                f"font-weight:700'>{n_gates}</span></div>",unsafe_allow_html=True)

    if not st.session_state.gate_list:
        st.markdown(f"<div class='gate-list-empty'>// no gates added yet<br>"
                    f"<span style='font-size:0.62rem'>use the panel above to add gates</span></div>",
                    unsafe_allow_html=True)
    else:
        for idx,op in enumerate(st.session_state.gate_list):
            ot=op["type"]
            is_tq_op=ot=="tq"; is_meas_op=ot=="meas"
            tq_cls="gate-item-tq" if is_tq_op else ("gate-item-meas" if is_meas_op else "")
            badge_cls="gate-badge-tq" if is_tq_op else ("gate-badge-meas" if is_meas_op else "")
            name_cls="gate-item-name-tq" if is_tq_op else ("gate-item-name-meas" if is_meas_op else "")
            if is_tq_op:
                gate_name=TQ_GATES[op["gate"]]["label"]; gate_desc=TQ_GATES[op["gate"]]["desc"]
                qubit_info=(f"<span class='gate-item-qubit gate-item-qubit-tq'>ctrl q{op['ctrl']}</span>"
                            f"<span class='gate-item-qubit gate-item-qubit-tq'>tgt q{op['tgt']}</span>")
                theta_info=(f"&nbsp;θ=<span style='color:{ORANGE}'>{op['theta']:.3f}</span>"
                            if TQ_GATES[op["gate"]]["has_theta"] else "")
            elif is_meas_op:
                gate_name=MEAS_GATES[op["gate"]]["label"]; gate_desc=MEAS_GATES[op["gate"]]["desc"]
                qubit_info=f"<span class='gate-item-qubit gate-item-qubit-meas'>q{op['qubit']}</span>"
                theta_info=""
            else:
                gate_name=SQ_GATES[op["gate"]]["label"]; gate_desc=SQ_GATES[op["gate"]]["desc"]
                qubit_info=f"<span class='gate-item-qubit'>q{op['qubit']}</span>"
                theta_info=(f"&nbsp;θ=<span style='color:{ORANGE}'>{op['theta']:.3f}</span>"
                            if SQ_GATES[op["gate"]]["has_theta"] else "")
            col_lbl,col_del,col_up,col_dn=st.columns([3.2,0.65,0.65,0.65])
            with col_lbl:
                st.markdown(f"<div class='gate-item {tq_cls}'><div class='gate-item-inner'>"
                            f"<div class='gate-item-top'>"
                            f"<span class='gate-item-badge {badge_cls}'>#{idx+1}</span>"
                            f"<span class='gate-item-name {name_cls}'>{gate_name}</span></div>"
                            f"<div class='gate-item-detail'>{qubit_info}{theta_info}"
                            f"<span style='color:{BORDER}'>&nbsp;{gate_desc}</span></div>"
                            f"</div></div>",unsafe_allow_html=True)
            with col_del:
                if st.button("✕",key=f"del_{idx}",disabled=disabled,help="Remove"):
                    st.session_state.gate_list.pop(idx); st.rerun()
            with col_up:
                if st.button("↑",key=f"up_{idx}",disabled=(disabled or idx==0),help="Move up"):
                    gl=st.session_state.gate_list; gl[idx-1],gl[idx]=gl[idx],gl[idx-1]; st.rerun()
            with col_dn:
                if st.button("↓",key=f"dn_{idx}",disabled=(disabled or idx==n_gates-1),help="Move down"):
                    gl=st.session_state.gate_list; gl[idx+1],gl[idx]=gl[idx],gl[idx+1]; st.rerun()
        if not disabled:
            st.markdown("<div class='action-btn'>",unsafe_allow_html=True)
            if st.button("🗑  CLEAR ALL"): st.session_state.gate_list=[]; st.rerun()
            st.markdown("</div>",unsafe_allow_html=True)

    # ── Run / Reset ───────────────────────────────────────────────────────
    st.markdown(f"<div class='vsc-section'>Run</div>",unsafe_allow_html=True)
    st.markdown("<div class='action-btn'>",unsafe_allow_html=True)
    if not st.session_state.running:
        if st.button("▶  RUN SIMULATION",disabled=not st.session_state.gate_list):
            st.session_state.running=True
            st.session_state.locked_snap={"n":n,"gate_list":[op.copy() for op in st.session_state.gate_list]}
            st.rerun()
    else:
        if st.button("↺  RESET"):
            st.session_state.running=False; st.session_state.locked_snap=None
            st.session_state.meas_results={}; st.rerun()
    st.markdown("</div>",unsafe_allow_html=True)
    if st.session_state.running:
        st.markdown("<div class='badge-running'>● circuit active</div>",unsafe_allow_html=True)
    else:
        st.markdown("<div class='badge-idle'>○ awaiting input</div>",unsafe_allow_html=True)

    if st.session_state.gate_list:
        sq_c=sum(1 for op in st.session_state.gate_list if op["type"]=="sq")
        tq_c=sum(1 for op in st.session_state.gate_list if op["type"]=="tq")
        mc_c=sum(1 for op in st.session_state.gate_list if op["type"]=="meas")
        st.markdown(f"<br><div class='vsc-card'>"
                    f"<div class='vsc-card-label'>Circuit stats</div>"
                    f"<div class='vsc-card-value'>{n_gates} ops</div>"
                    f"<div class='vsc-card-sub'>{sq_c} single · {tq_c} two-qubit · {mc_c} meas</div>"
                    f"<div class='vsc-card-sub'>dim = 2<sup>{n}</sup> = {2**n}</div></div>",
                    unsafe_allow_html=True)

    # ── Notes ─────────────────────────────────────────────────────────────
    st.markdown(f"<div class='notes-panel'><div class='notes-panel-title'>📝 Notes</div>",
                unsafe_allow_html=True)
    cn=st.text_input("Circuit name",value=st.session_state.circuit_name,
        placeholder="e.g. Bell state preparation",key="circuit_name_input")
    st.session_state.circuit_name=cn
    nt=st.text_area("Notes",value=st.session_state.notes,height=110,
        placeholder="Observations, hypotheses...",label_visibility="collapsed",key="notes_textarea")
    st.session_state.notes=nt
    st.markdown("</div>",unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SIMULATION
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.running and st.session_state.locked_snap:
    snap=st.session_state.locked_snap; sim_n=snap["n"]; sim_gates=snap["gate_list"]
else:
    sim_n=n; sim_gates=st.session_state.gate_list

is_running=st.session_state.running
state_disp, meas_results=simulate(sim_n,sim_gates)
probs_d=np.abs(state_disp)**2; phases_d=np.angle(state_disp)
basis_all=[f"|{format(i,f'0{sim_n}b')}⟩" for i in range(2**sim_n)]
top_idx=np.argsort(probs_d)[::-1][:min(32,2**sim_n)]
top_sorted=sorted(top_idx,key=lambda i:-probs_d[i])

# ─────────────────────────────────────────────────────────────────────────────
# RIGHT COLUMN — TABS
# ─────────────────────────────────────────────────────────────────────────────
with col_main:
    tab1,tab2,tab3,tab4=st.tabs(["Circuit Diagram","Probabilities","Entanglement","Teleportation"])

    # ── Tab 1: Circuit Diagram ────────────────────────────────────────────
    with tab1:
        n_ops=len(sim_gates)
        fig_w=max(9,n_ops*1.15+2.5); fig_h=max(2.4,sim_n*0.72+1.2)
        fig,ax=plt.subplots(figsize=(fig_w,fig_h))
        fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
        top_y=(sim_n-1)*1.0
        ax.set_xlim(0,fig_w); ax.set_ylim(-1.0,top_y+0.95); ax.axis("off")
        wire_ys=[top_y-q*1.0 for q in range(sim_n)]
        meas_x={}  # track where measurements happen per qubit
        for q,wy in enumerate(wire_ys):
            ax.plot([0.5,fig_w-0.3],[wy,wy],color=BORDER,lw=1.4,zorder=1)
            ax.text(0.35,wy,f"q{q}",color=CYAN,fontsize=9,fontfamily="monospace",va="center",ha="right",fontweight="bold")
            ax.text(0.55,wy+0.22,"|0⟩",color=DIM,fontsize=7,fontfamily="monospace")
        gate_xs=([] if n_ops==0 else
                 [(1.9+fig_w-1.0)/2] if n_ops==1 else
                 np.linspace(1.9,fig_w-1.0,n_ops).tolist())
        for step,(op,gx) in enumerate(zip(sim_gates,gate_xs)):
            ot=op["type"]
            if ot=="sq":
                q=op["qubit"]; wy=wire_ys[q]; gk=op["gate"]
                ec=CYAN if is_running else BLUE
                fc=SIDEBAR if not is_running else "#E8F4FB"
                ax.add_patch(mpatches.FancyBboxPatch((gx-0.39,wy-0.26),0.78,0.52,
                    boxstyle="round,pad=0.03",linewidth=1.3,edgecolor=ec,facecolor=fc,zorder=3))
                ax.text(gx,wy+(0.08 if SQ_GATES[gk]["has_theta"] else 0),SQ_GATES[gk]["label"],
                        color=YELLOW,fontsize=8.5,fontfamily="monospace",ha="center",va="center",fontweight="bold",zorder=4)
                if SQ_GATES[gk]["has_theta"]:
                    ax.text(gx,wy-0.14,f"θ={op['theta']:.2f}",color=DIM,fontsize=6,fontfamily="monospace",ha="center",zorder=4)
            elif ot=="tq":
                cy=wire_ys[op["ctrl"]]; ty=wire_ys[op["tgt"]]; gk=op["gate"]
                ec=PURPLE if is_running else "#8B00B3"
                fc="#F0E8F8" if is_running else SIDEBAR
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
            else:  # measurement
                q=op["qubit"]; wy=wire_ys[q]; gk=op["gate"]
                ec=RED; fc="#FFF0F4" if is_running else SIDEBAR
                # meter box
                ax.add_patch(mpatches.FancyBboxPatch((gx-0.39,wy-0.28),0.78,0.56,
                    boxstyle="round,pad=0.03",linewidth=1.5,edgecolor=ec,facecolor=fc,zorder=3))
                # arc inside meter
                arc_cx,arc_cy=gx,wy-0.04
                theta_arc=np.linspace(0,np.pi,40)
                ax.plot(arc_cx+0.23*np.cos(theta_arc),arc_cy+0.18*np.sin(theta_arc),color=ec,lw=1.2,zorder=4)
                ax.annotate("",xy=(arc_cx+0.19,arc_cy+0.14),xytext=(arc_cx,arc_cy),
                            arrowprops=dict(arrowstyle="-|>",color=ec,lw=1.1),zorder=4)
                if gk=="Mx": ax.text(gx,wy+0.22,"X",color=ec,fontsize=6,fontfamily="monospace",ha="center",va="center",zorder=5)
                elif gk=="Reset": ax.text(gx,wy,"RST",color=ec,fontsize=6.5,fontfamily="monospace",ha="center",va="center",fontweight="bold",zorder=5)
                # double wire after measurement
                meas_x[q]=gx
                ax.plot([gx+0.39,fig_w-0.3],[wy+0.05,wy+0.05],color=RED,lw=0.8,linestyle="--",zorder=2,alpha=0.5)
                ax.plot([gx+0.39,fig_w-0.3],[wy-0.05,wy-0.05],color=RED,lw=0.8,linestyle="--",zorder=2,alpha=0.5)

            ax.text(gx,top_y+0.72,f"#{step+1}",color=DIM,fontsize=6.5,fontfamily="monospace",ha="center")

        for q,wy in enumerate(wire_ys):
            ax.text(fig_w-0.2,wy,f"q{q}",color=CYAN,fontsize=9,fontfamily="monospace",va="center")
        if is_running: ax.text(fig_w/2,-0.8,"● simulation active",color=GREEN,fontsize=8,fontfamily="monospace",ha="center")
        if n_ops==0: ax.text(fig_w/2,top_y/2,"// add gates to build circuit",color=BORDER,fontsize=10,fontfamily="monospace",ha="center",va="center")
        if meas_results and is_running:
            res_str="  ".join(f"q{k.split('_q')[1]}={v}" for k,v in meas_results.items())
            ax.text(fig_w/2,-0.55,f"// measurements: {res_str}",color=RED,fontsize=7.5,fontfamily="monospace",ha="center")
        plt.tight_layout(pad=0.2); st.pyplot(fig,use_container_width=True); plt.close(fig)

        # Show measurement results if any
        if meas_results and is_running:
            cols_m=st.columns(len(meas_results))
            for ci,(k,v) in enumerate(meas_results.items()):
                q_id=k.split('_q')[1]
                cols_m[ci].markdown(
                    f"<div style='background:white;border:1px solid {BORDER};border-left:4px solid {RED};"
                    f"border-radius:4px;padding:0.4rem 0.7rem;font-family:JetBrains Mono,monospace;text-align:center'>"
                    f"<div style='color:{DIM};font-size:0.58rem;letter-spacing:1px'>q{q_id} outcome</div>"
                    f"<div style='color:{RED};font-size:1.4rem;font-weight:700'>|{v}⟩</div></div>",
                    unsafe_allow_html=True)

    # ── Tab 2: Probabilities ──────────────────────────────────────────────
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

    # ── Tab 3: Entanglement ───────────────────────────────────────────────
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

    # ── Tab 4: Teleportation ──────────────────────────────────────────────
    with tab4:
        st.markdown(f"""
        <div style='background:{SIDEBAR};border:1.5px solid {BORDER};border-top:3px solid {PURPLE};
        border-radius:6px;padding:0.8rem 1rem 0.6rem 1rem;margin-bottom:0.8rem;
        font-family:JetBrains Mono,monospace'>
          <div style='color:{PURPLE};font-size:0.62rem;letter-spacing:2px;text-transform:uppercase;font-weight:600;margin-bottom:0.4rem'>Quantum Teleportation Protocol</div>
          <div style='color:{DIM};font-size:0.72rem;line-height:1.6'>
            Teleports an arbitrary qubit state <b style='color:{YELLOW}'>|ψ⟩ = α|0⟩ + β|1⟩</b> from
            Alice (q0) to Bob (q2) using a shared Bell pair on (q1,q2).<br>
            Alice performs a Bell measurement and sends 2 classical bits to Bob,
            who applies corrections. No information travels faster than light.
          </div>
        </div>""", unsafe_allow_html=True)

        # Input state configuration
        st.markdown(f"<div class='vsc-section'>Configure state to teleport |ψ⟩</div>",unsafe_allow_html=True)

        tele_col1, tele_col2 = st.columns([1.2,1])
        with tele_col1:
            tele_mode=st.radio("State input mode",
                ["Preset states","Custom amplitudes"],
                horizontal=True,key="tele_mode",label_visibility="collapsed")

            if tele_mode=="Preset states":
                preset=st.selectbox("Choose preset",
                    ["|0⟩","  |1⟩","|+⟩  (1/√2)(|0⟩+|1⟩)",
                     "|−⟩  (1/√2)(|0⟩−|1⟩)",
                     "|i⟩  (1/√2)(|0⟩+i|1⟩)",
                     "Custom 30°  cos(15°)|0⟩+sin(15°)|1⟩"],
                    key="tele_preset")
                preset_map={
                    "|0⟩":                       (1.0,0.0),
                    "  |1⟩":                      (0.0,1.0),
                    "|+⟩  (1/√2)(|0⟩+|1⟩)":     (1/np.sqrt(2),1/np.sqrt(2)),
                    "|−⟩  (1/√2)(|0⟩−|1⟩)":     (1/np.sqrt(2),-1/np.sqrt(2)),
                    "|i⟩  (1/√2)(|0⟩+i|1⟩)":    (1/np.sqrt(2),1j/np.sqrt(2)),
                    "Custom 30°  cos(15°)|0⟩+sin(15°)|1⟩":(np.cos(np.pi/12),np.sin(np.pi/12)),
                }
                alpha_val,beta_val=preset_map[preset]
            else:
                st.markdown("<p style='color:#6E6E6E;font-family:JetBrains Mono,monospace;"
                            "font-size:0.62rem;margin-bottom:0.1rem'>"
                            "polar angle θ (0 = |0⟩, π = |1⟩)</p>",
                            unsafe_allow_html=True)
                tele_theta=st.number_input(
                    "theta_tele", min_value=0.0, max_value=float(np.pi),
                    value=float(np.pi/3), step=0.001, format="%.6f",
                    key="tele_theta", label_visibility="collapsed")
                st.markdown(f"<p style='color:#6E6E6E;font-family:JetBrains Mono,monospace;"
                            f"font-size:0.65rem;margin-top:-2px'>"
                            f"{tele_theta:.6f} rad = {tele_theta/np.pi:.4f}π = {float(np.degrees(tele_theta)):.3f}°</p>",
                            unsafe_allow_html=True)
                st.markdown("<p style='color:#6E6E6E;font-family:JetBrains Mono,monospace;"
                            "font-size:0.62rem;margin-bottom:0.1rem;margin-top:0.3rem'>"
                            "azimuth φ (phase, 0–2π)</p>",
                            unsafe_allow_html=True)
                tele_phi=st.number_input(
                    "phi_tele", min_value=0.0, max_value=float(2*np.pi),
                    value=0.0, step=0.001, format="%.6f",
                    key="tele_phi", label_visibility="collapsed")
                st.markdown(f"<p style='color:#6E6E6E;font-family:JetBrains Mono,monospace;"
                            f"font-size:0.65rem;margin-top:-2px'>"
                            f"{tele_phi:.6f} rad = {tele_phi/np.pi:.4f}π = {float(np.degrees(tele_phi)):.3f}°</p>",
                            unsafe_allow_html=True)
                alpha_val=np.cos(tele_theta/2)
                beta_val =np.exp(1j*tele_phi)*np.sin(tele_theta/2)

            # Normalize and display
            norm=np.sqrt(abs(alpha_val)**2+abs(beta_val)**2)
            a,b=alpha_val/norm,beta_val/norm
            st.markdown(
                f"<div style='background:{PANEL};border:1px solid {BORDER};"
                f"border-left:3px solid {PURPLE};border-radius:4px;"
                f"padding:0.5rem 0.8rem;margin-top:0.4rem;font-family:JetBrains Mono,monospace'>"
                f"<div style='color:{DIM};font-size:0.6rem;letter-spacing:1.5px;text-transform:uppercase'>State to teleport</div>"
                f"<div style='color:{PURPLE};font-size:0.88rem;font-weight:700;margin-top:0.2rem'>"
                f"|ψ⟩ = ({a.real:+.3f}{a.imag:+.3f}i)|0⟩ + ({b.real:+.3f}{b.imag:+.3f}i)|1⟩</div>"
                f"<div style='color:{DIM};font-size:0.65rem'>P(|0⟩)={abs(a)**2:.3f}  P(|1⟩)={abs(b)**2:.3f}</div>"
                f"</div>",unsafe_allow_html=True)

            run_tele=st.button("▶  RUN TELEPORTATION",key="run_tele_btn")

        with tele_col2:
            # Bloch sphere preview of input state
            fig_b,ax_b=plt.subplots(figsize=(3.2,3.2),subplot_kw={"projection":"3d"})
            fig_b.patch.set_facecolor(BG); ax_b.set_facecolor(BG)
            # Draw sphere wireframe
            u_s=np.linspace(0,2*np.pi,30); v_s=np.linspace(0,np.pi,20)
            xs_=np.outer(np.cos(u_s),np.sin(v_s))
            ys_=np.outer(np.sin(u_s),np.sin(v_s))
            zs_=np.outer(np.ones(30),np.cos(v_s))
            ax_b.plot_wireframe(xs_,ys_,zs_,color=BORDER,alpha=0.2,linewidth=0.4)
            # Bloch vector of state
            bx=2*(a*np.conj(b)).real; by=-2*(a*np.conj(b)).imag; bz=(abs(a)**2-abs(b)**2).real
            ax_b.quiver(0,0,0,bx,by,bz,color=PURPLE,linewidth=2.5,arrow_length_ratio=0.15)
            ax_b.scatter([bx],[by],[bz],color=PURPLE,s=60,zorder=5)
            for axis,lbl in [([1,0,0],"|+⟩"),([0,1,0],"|i⟩"),([0,0,1],"|0⟩"),
                              ([-1,0,0],"|−⟩"),([0,-1,0],"|−i⟩"),([0,0,-1],"|1⟩")]:
                ax_b.text(1.25*axis[0],1.25*axis[1],1.25*axis[2],lbl,
                          color=DIM,fontsize=7,fontfamily="monospace",ha="center",va="center")
            ax_b.set_xlim(-1.2,1.2); ax_b.set_ylim(-1.2,1.2); ax_b.set_zlim(-1.2,1.2)
            ax_b.set_box_aspect([1,1,1]); ax_b.axis("off")
            ax_b.set_title("Bloch sphere",color=DIM,fontsize=8,fontfamily="monospace",pad=0)
            fig_b.tight_layout(pad=0.1)
            st.pyplot(fig_b,use_container_width=True); plt.close(fig_b)

        # ── Run and show results ──────────────────────────────────────────
        if run_tele or "tele_history" in st.session_state:
            if run_tele:
                history,m0,m1,corrections,fidelity,rho2,a_res,b_res=run_teleportation(a,b)
                st.session_state.tele_history=(history,m0,m1,corrections,fidelity,rho2,a_res,b_res)
            else:
                history,m0,m1,corrections,fidelity,rho2,a_res,b_res=st.session_state.tele_history

            st.markdown(f"<div class='vsc-section'>Protocol execution — step by step</div>",unsafe_allow_html=True)

            # Step-by-step circuit diagram
            steps_labels=["Initial |ψ⟩⊗|00⟩","H on q1","CNOT q1→q2\n(Bell pair)",
                          "CNOT q0→q1\n(Alice encodes)","H on q0\n(Alice encodes)",
                          f"Measure\nq0={m0}, q1={m1}",
                          "Corrections\non q2"]
            fig_tele,axes_tele=plt.subplots(1,len(history),figsize=(14,3.5))
            fig_tele.patch.set_facecolor(BG)
            if len(history)==1: axes_tele=[axes_tele]
            for ai,(ax_t,(lbl,st_h)) in enumerate(zip(axes_tele,history)):
                ax_t.set_facecolor(SIDEBAR if ai<len(history)-1 else "#EAF5EA")
                probs_h=np.abs(st_h)**2
                basis_3=["000","001","010","011","100","101","110","111"]
                colors_h=[GREEN if i==np.argmax(probs_h) else CYAN for i in range(8)]
                bars_h=ax_t.bar(range(8),probs_h,color=colors_h,edgecolor=BORDER,linewidth=0.5,width=0.7)
                ax_t.set_ylim(0,1.05)
                ax_t.set_xticks(range(8))
                ax_t.set_xticklabels(basis_3,rotation=70,ha="right",fontfamily="monospace",fontsize=6,color=WHITE)
                title_col=GREEN if ai==len(history)-1 else CYAN
                ax_t.set_title(lbl,color=title_col,fontsize=6.5,fontfamily="monospace",pad=3,wrap=True)
                ax_t.tick_params(colors=DIM,labelsize=6); ax_t.spines[:].set_color(BORDER)
                if ai==0:
                    ax_t.set_ylabel("P",color=DIM,fontsize=7,fontfamily="monospace")
            plt.tight_layout(pad=0.3)
            st.pyplot(fig_tele,use_container_width=True); plt.close(fig_tele)

            # Results cards
            st.markdown(f"<div class='vsc-section'>Results</div>",unsafe_allow_html=True)
            rc1,rc2,rc3,rc4=st.columns(4)
            for col_r,label_r,val_r,col_v in zip(
                [rc1,rc2,rc3,rc4],
                ["Alice m0","Alice m1","Corrections","Fidelity F"],
                [f"|{m0}⟩",f"|{m1}⟩",", ".join(corrections) if corrections else "none",f"{fidelity:.4f}"],
                [RED,RED,ORANGE,GREEN if fidelity>0.99 else YELLOW]):
                col_r.markdown(
                    f"<div style='background:{PANEL};border:1px solid {BORDER};"
                    f"border-left:3px solid {col_v};border-radius:4px;"
                    f"padding:0.5rem 0.75rem;font-family:JetBrains Mono,monospace'>"
                    f"<div style='color:{DIM};font-size:0.58rem;letter-spacing:1.2px;text-transform:uppercase'>{label_r}</div>"
                    f"<div style='color:{col_v};font-size:1.1rem;font-weight:700'>{val_r}</div>"
                    f"</div>",unsafe_allow_html=True)

            # Compare input vs output state
            st.markdown(f"<div class='vsc-section'>State comparison — input vs Bob's received state</div>",
                        unsafe_allow_html=True)
            fig_comp,axes_comp=plt.subplots(1,2,figsize=(8,3.2))
            fig_comp.patch.set_facecolor(BG)
            for ax_c,state_vec,title_c,col_c in zip(
                    axes_comp,
                    [[abs(a_res)**2,abs(b_res)**2],[rho2[0,0].real,rho2[1,1].real]],
                    ["Input |ψ⟩  (Alice's qubit)","Bob's q2  (after corrections)"],
                    [PURPLE,GREEN]):
                ax_c.set_facecolor(SIDEBAR)
                ax_c.bar(["P(|0⟩)","P(|1⟩)"],state_vec,color=[col_c,col_c],
                         edgecolor=BORDER,linewidth=0.7,alpha=0.85,width=0.5)
                for xi,(label_x,val_x) in enumerate(zip(["P(|0⟩)","P(|1⟩)"],state_vec)):
                    ax_c.text(xi,val_x+0.02,f"{val_x:.4f}",ha="center",
                              color=WHITE,fontsize=9,fontfamily="monospace")
                ax_c.set_ylim(0,1.15)
                ax_c.set_title(title_c,color=col_c,fontsize=9,fontfamily="monospace",pad=5)
                ax_c.tick_params(colors=DIM,labelsize=8); ax_c.spines[:].set_color(BORDER)
                ax_c.set_yticklabels([f"{v:.1f}" for v in ax_c.get_yticks()],
                                     fontfamily="monospace",fontsize=7,color=DIM)
            fig_comp.suptitle(f"// Teleportation fidelity F = {fidelity:.4f}",
                              color=GREEN if fidelity>0.99 else YELLOW,
                              fontsize=9,fontfamily="monospace",x=0.5,ha="center")
            plt.tight_layout(pad=0.4)
            st.pyplot(fig_comp,use_container_width=True); plt.close(fig_comp)

            if fidelity>0.99:
                st.markdown(f"<div class='tele-result'>"
                            f"<span style='color:{GREEN};font-weight:700'>✓ Teleportation successful</span>"
                            f"<span style='color:{DIM}'>&nbsp;—&nbsp;Bob's qubit matches Alice's original state "
                            f"with fidelity {fidelity:.4f} ≈ 1.0</span></div>",unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='tele-result' style='border-left-color:{YELLOW}'>"
                            f"<span style='color:{YELLOW};font-weight:700'>⚠ Partial fidelity {fidelity:.4f}</span>"
                            f"<span style='color:{DIM}'>&nbsp;—&nbsp;numerical precision or intermediate measurement noise</span></div>",
                            unsafe_allow_html=True)

            # Protocol explanation
            with st.expander("// How the protocol works — step by step explanation"):
                st.markdown(f"""
**Step 1 — Bell pair creation**
A Hadamard gate on q1 followed by CNOT(q1→q2) creates the maximally entangled Bell state
|Φ⁺⟩ = (|00⟩ + |11⟩)/√2 between Alice (q1) and Bob (q2).

**Step 2 — Alice's encoding**
Alice applies CNOT(q0→q1) then H on q0. This entangles her qubit-to-send (q0) with her
half of the Bell pair (q1), effectively encoding α and β into the joint system.

**Step 3 — Bell measurement**
Alice measures both her qubits (q0, q1) in the computational basis, collapsing the 3-qubit
state. She gets classical bits m0 and m1 (results: m0={m0}, m1={m1}).

**Step 4 — Classical communication**
Alice sends m0 and m1 to Bob over a classical channel (phone, radio, etc). This is the
speed-of-light limit — no FTL communication occurs.

**Step 5 — Bob's corrections**
Bob applies: {"X gate (bit flip) on q2" if m1==1 else "no X gate"} and
{"Z gate (phase flip) on q2" if m0==1 else "no Z gate"} based on Alice's bits.
After corrections: {", ".join(corrections) if corrections else "no corrections were needed"}.

**Result:** Bob's q2 is now in state |ψ⟩ = ({a_res.real:+.3f}{a_res.imag:+.3f}i)|0⟩ + ({b_res.real:+.3f}{b_res.imag:+.3f}i)|1⟩ — identical to Alice's original.
Alice's original qubit is destroyed (no-cloning theorem is satisfied). Fidelity = **{fidelity:.4f}**.
""")

# ─────────────────────────────────────────────────────────────────────────────
# STATE VECTOR TABLE
# ─────────────────────────────────────────────────────────────────────────────
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

# ─────────────────────────────────────────────────────────────────────────────
# EXPORT
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"<div class='vsc-section'>Save &amp; Export</div>",unsafe_allow_html=True)
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
    lines+=["","── Notes ──",st.session_state.notes or "(none)","","── State Vector ──"]
    for i in range(2**sim_n):
        if probs_d[i]>1e-6:
            lines.append(f"  {basis_all[i]}  P={probs_d[i]:.6f}  amp={state_disp[i].real:+.4f}{state_disp[i].imag:+.4f}i")
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