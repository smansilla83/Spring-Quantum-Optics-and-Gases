import numpy as np
import matplotlib.pyplot as plt

# ---------- Basic gates ----------
I = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
H = (1 / np.sqrt(2)) * np.array([[1, 1], [1, -1]], dtype=complex)

def Rz(theta):
    return np.array([
        [np.exp(-1j * theta / 2), 0],
        [0, np.exp(1j * theta / 2)]
    ], dtype=complex)

# ---------- Helpers ----------
def kron_n(ops):
    out = ops[0]
    for op in ops[1:]:
        out = np.kron(out, op)
    return out

def apply_single_qubit_gate(state, gate, qubit, n_qubits=4):
    ops = []
    for q in range(n_qubits):
        ops.append(gate if q == qubit else I)
    U = kron_n(ops)
    return U @ state

def apply_cnot(state, control, target, n_qubits=4):
    dim = 2 ** n_qubits
    out = np.zeros_like(state)
    for i in range(dim):
        bits = list(format(i, f"0{n_qubits}b"))
        if bits[control] == '1':
            bits[target] = '0' if bits[target] == '1' else '1'
        j = int("".join(bits), 2)
        out[j] += state[i]
    return out

# ---------- Circuit for one tau ----------
def run_circuit(tau):
    n_qubits = 4
    dim = 2 ** n_qubits

    # Start in |0000>
    state = np.zeros(dim, dtype=complex)
    state[0] = 1.0

    # Prepare |1000>
    state = apply_single_qubit_gate(state, X, qubit=0, n_qubits=n_qubits)

    # Hopping circuit:
    # H q0
    # H q2
    # CNOT 0->2
    # Rz(2*tau) on q2
    # CNOT 0->2
    # H q0
    # H q2

    state = apply_single_qubit_gate(state, H, qubit=0, n_qubits=n_qubits)
    state = apply_single_qubit_gate(state, H, qubit=2, n_qubits=n_qubits)

    state = apply_cnot(state, control=0, target=2, n_qubits=n_qubits)
    state = apply_single_qubit_gate(state, Rz(2 * tau), qubit=2, n_qubits=n_qubits)
    state = apply_cnot(state, control=0, target=2, n_qubits=n_qubits)

    state = apply_single_qubit_gate(state, H, qubit=0, n_qubits=n_qubits)
    state = apply_single_qubit_gate(state, H, qubit=2, n_qubits=n_qubits)

    return state

# ---------- Sweep tau ----------
taus = np.linspace(0, np.pi, 300)
probs_site2 = []

# |0010> has index 2 in q0 q1 q2 q3 ordering
target_index = int("0010", 2)

for tau in taus:
    psi = run_circuit(tau)
    prob = np.abs(psi[target_index]) ** 2
    probs_site2.append(prob)

# ---------- Plot ----------
plt.figure(figsize=(7, 4.5))
plt.plot(taus, probs_site2)
plt.xlabel(r'$\tau$')
plt.ylabel(r'$P(|0010\rangle)$')
plt.title(r'Probability of finding the electron at Site 2')
plt.grid(True)
plt.show()