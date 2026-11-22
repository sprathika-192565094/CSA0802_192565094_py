"""Venn diagrams for each result of Q4 -> venn_diagrams.png"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

x, y = np.meshgrid(np.linspace(0, 10, 600), np.linspace(0, 6, 360))
A = (x - 4) ** 2 + (y - 3) ** 2 <= 1.9 ** 2
B = (x - 6) ** 2 + (y - 3) ** 2 <= 1.9 ** 2
panels = [("AI only   A - B", A & ~B, "{001, 007}"), ("IoT only   B - A", B & ~A, "{002, 010}"),
          ("Both (clash)   A & B", A & B, "{004, 009}"), ("Exactly one   A ^ B", A ^ B, "{001, 002, 007, 010}"),
          ("Registered   A | B", A | B, "{001, 002, 004, 007, 009, 010}"), ("Neither   U - (A | B)", ~(A | B), "{003, 005, 006, 008}")]
fig, axes = plt.subplots(2, 3, figsize=(12, 6))
for ax, (title, region, items) in zip(axes.ravel(), panels):
    ax.imshow(np.where(region, 1.0, 0.0), extent=(0, 10, 0, 6), origin="lower", cmap="Blues", vmin=0, vmax=1.6, alpha=.9)
    for cx, name in ((4, "AI"), (6, "IoT")):
        ax.add_patch(plt.Circle((cx, 3), 1.9, fill=False, ec="black", lw=1.5))
        ax.text(cx + (-1.2 if cx == 4 else 1.2), 5.4, name, ha="center", fontsize=10)
    ax.add_patch(plt.Rectangle((0.02, 0.02), 9.96, 5.96, fill=False, ec="gray"))
    ax.text(0.3, 0.3, "U = all students", fontsize=7)
    ax.set_title(title + "\n" + items + "  (last 3 digits)", fontsize=9)
    ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off")
plt.tight_layout(); plt.savefig("venn_diagrams.png", dpi=140)
print("saved venn_diagrams.png")
