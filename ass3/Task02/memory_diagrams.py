"""Draws the memory diagrams of [[0]*3]*3 and of the corrected grid -> memory_diagrams.png"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))


def box(ax, x, y, w, h, text, fc="#e8eef9"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02", fc=fc, ec="#223"))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=9)


def arrow(ax, p, q):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="->", color="#a00", lw=1.4))


for ax, title, shared in ((axes[0], "bad = [[0] * 3] * 3\n(three references to ONE inner list)", True),
                          (axes[1], "good = [[0 for _ in range(3)] for _ in range(3)]\n(three separate inner lists)", False)):
    ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off"); ax.set_title(title, fontsize=10)
    ax.text(0.2, 5.5, "name", fontsize=8); box(ax, 0.2, 4.6, 1.0, 0.6, "bad" if shared else "good", "#fff2cc")
    box(ax, 2.0, 4.6, 2.2, 0.6, "outer list: 3 refs", "#e2f0d9")
    arrow(ax, (1.25, 4.9), (2.0, 4.9))
    if shared:
        box(ax, 6.0, 2.2, 3.4, 1.0, "inner list\n[0, 7, 0]", "#fce4d6")
        for k in range(3):
            xs = 2.4 + 0.7 * k
            arrow(ax, (xs, 4.6), (6.0 + 0.4 * k + 0.3, 3.2))
        ax.text(0.3, 1.2, "bad[0][1] = 7 changes the one shared list,\nso every row shows the 7.", fontsize=9, color="#a00")
    else:
        for k in range(3):
            y = 3.5 - 1.3 * k
            box(ax, 6.0, y - 0.3, 3.4, 0.9, "[0, 7, 0]" if k == 0 else "[0, 0, 0]", "#fce4d6")
            arrow(ax, (2.4 + 0.7 * k, 4.6), (6.0, y + 0.15))
        ax.text(0.3, 1.2, "good[0][1] = 7 changes only the first row.", fontsize=9, color="#070")
plt.tight_layout()
plt.savefig("memory_diagrams.png", dpi=150)
print("saved memory_diagrams.png")
