import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

st.set_page_config(page_title="Hubbard Model Simulator", layout="centered")

st.title("Hubbard Model Quantum Simulator")
st.markdown(
    "Explore the **Hubbard Model** on a square lattice. "
    "Set the lattice dimension below to define an $N = D \\times D$ grid of sites."
)

st.divider()

st.subheader("Lattice Configuration")

D = st.slider("Lattice dimension $D$", min_value=2, max_value=8, value=2, step=1)

N = D * D
st.markdown(f"**$N = {N}$ sites** arranged in a $**{D} \\times {D}**$ square lattice.")


def draw_lattice(D):
    fig, ax = plt.subplots(figsize=(min(D * 1.4, 8), min(D * 1.4, 8)))

    # Draw edges (nearest-neighbor hopping)
    for row in range(D):
        for col in range(D):
            x, y = col, row
            # Horizontal bond
            if col < D - 1:
                ax.plot([x, x + 1], [y, y], color="#4C72B0", lw=2.5, zorder=1)
            # Vertical bond
            if row < D - 1:
                ax.plot([x, x], [y, y + 1], color="#4C72B0", lw=2.5, zorder=1)

    # Draw sites
    site_index = 0
    for row in range(D):
        for col in range(D):
            x, y = col, row
            circle = plt.Circle((x, y), 0.18, color="#DD8452", zorder=2)
            ax.add_patch(circle)
            ax.text(x, y, str(site_index), ha="center", va="center",
                    fontsize=9, fontweight="bold", color="white", zorder=3)
            site_index += 1

    ax.set_xlim(-0.5, D - 0.5)
    ax.set_ylim(-0.5, D - 0.5)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(
        f"{D}×{D} Square Lattice  ($N={D*D}$ sites)",
        fontsize=13, pad=12
    )

    site_patch = mpatches.Patch(color="#DD8452", label="Lattice site")
    line_patch = mpatches.Patch(color="#4C72B0", label="Hopping bond ($t$)")
    ax.legend(handles=[site_patch, line_patch], loc="upper right", fontsize=9,
              framealpha=0.9)

    return fig


fig = draw_lattice(D)
st.pyplot(fig)
plt.close(fig)

st.caption(
    "Each orange node represents a lattice site. "
    "Blue edges indicate nearest-neighbor hopping amplitude $t$. "
    "On-site Coulomb repulsion $U$ acts when two electrons of opposite spin occupy the same site."
)
