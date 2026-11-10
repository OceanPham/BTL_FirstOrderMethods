"""
02 - GRADIENT DESCENT TRÊN HÀM HAI BIẾN

Hàm mục tiêu (Bài tập 1.4 trong bộ bài tập của môn học):
        f(x1, x2) = 3*x1^2 + 2*x1*x2 + 4*x2^2 + 10,   x0 = (1, 1)
Nghiệm tối ưu x* = (0, 0), f* = 10.

Thí nghiệm 1: ảnh hưởng của tốc độ học (learning rate) cố định.
Thí nghiệm 2: so sánh 3 cách chọn độ dài bước:
              cố định / chính xác theo tia / quay lui (Armijo).

Chạy:  python 02_gd_ham_hai_bien.py
Kết quả: hinh/hinh1_learning_rate.png, hinh/hinh2_chon_buoc.png
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HINH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "hinh")
os.makedirs(HINH, exist_ok=True)

H = np.array([[6.0, 2.0], [2.0, 8.0]])          # ma trận Hessian (hằng số)
F_STAR = 10.0


def f(x):
    return 3 * x[0] ** 2 + 2 * x[0] * x[1] + 4 * x[1] ** 2 + 10


def grad(x):
    return np.array([6 * x[0] + 2 * x[1], 2 * x[0] + 8 * x[1]])


def gradient_descent(x0, chon_buoc, eps=1e-2, max_iter=200):
    """GD tổng quát. `chon_buoc(x, g)` trả về độ dài bước tại x.
    Dừng khi ||grad f(x)|| < eps."""
    x = np.array(x0, dtype=float)
    quy_dao = [x.copy()]
    for _ in range(max_iter):
        g = grad(x)
        if np.linalg.norm(g) < eps:
            break
        x = x - chon_buoc(x, g) * g
        quy_dao.append(x.copy())
        if not np.all(np.isfinite(x)) or np.linalg.norm(x) > 1e6:
            break
    return np.array(quy_dao)


# ----------------------------------------------------- 3 cách chọn bước
def buoc_co_dinh(eta):
    return lambda x, g: eta


def buoc_chinh_xac(x, g):
    """Với hàm toàn phương: lambda = g^T g / (g^T H g)."""
    return g @ g / (g @ H @ g)


def buoc_quay_lui(x, g, m1=0.01, alpha=0.5):
    """Thủ tục quay lui (quy tắc Armijo) như trong bài giảng."""
    lam = 1.0
    while f(x - lam * g) - f(x) > -m1 * lam * (g @ g):
        lam *= alpha
    return lam


x0 = (1.0, 1.0)
L = np.linalg.eigvalsh(H).max()
mu = np.linalg.eigvalsh(H).min()
print(f"Trị riêng Hessian: mu = {mu:.4f}, L = {L:.4f}")
print(f"GD bước cố định hội tụ khi eta < 2/L = {2 / L:.4f}\n")

# =========================================================== Thí nghiệm 1
cac_eta = [0.02, 0.1, 0.2, 0.23]
mau = ["#1f77b4", "#2ca02c", "#ff7f0e", "#d62728"]
fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))

g1, g2 = np.meshgrid(np.linspace(-1.6, 1.6, 300), np.linspace(-1.6, 1.6, 300))
Z = 3 * g1 ** 2 + 2 * g1 * g2 + 4 * g2 ** 2 + 10
axes[0].contour(g1, g2, Z, levels=[10.1, 10.5, 11, 12, 14, 17, 21, 26],
                colors="gray", linewidths=0.6)

print("THÍ NGHIỆM 1 - bước cố định (dừng khi ||grad|| < 0.01, tối đa 200 bước)")
for eta, c in zip(cac_eta, mau):
    qd = gradient_descent(x0, buoc_co_dinh(eta))
    fx = np.array([f(p) for p in qd])
    hoi_tu = np.linalg.norm(grad(qd[-1])) < 1e-2
    print(f"  eta = {eta:<5}: {len(qd) - 1:>3} bước, f cuối = {fx[-1]:.6g}, "
          f"{'HỘI TỤ' if hoi_tu else 'KHÔNG hội tụ'}")
    ve = qd[:40]
    ve = ve[(np.abs(ve) < 1.6).all(axis=1)]
    axes[0].plot(ve[:, 0], ve[:, 1], "o-", color=c, ms=3, lw=1.1,
                 label=f"η = {eta}")
    axes[1].semilogy(np.maximum(fx[:60] - F_STAR, 1e-12), color=c, lw=1.6,
                     label=f"η = {eta}")
axes[0].plot(0, 0, "k*", ms=12)
axes[0].set(xlabel="$x_1$", ylabel="$x_2$", xlim=(-1.6, 1.6), ylim=(-1.6, 1.6),
            title="Quỹ đạo nghiệm trên đường mức")
axes[0].legend(loc="lower left")
axes[1].set(xlabel="Bước lặp k", ylabel="$f(x_k) - f^*$ (thang log)",
            title="Sai số hàm mục tiêu theo bước lặp")
axes[1].grid(alpha=0.3)
axes[1].legend()
fig.suptitle("Ảnh hưởng của tốc độ học η đến Gradient Descent", fontweight="bold")
fig.tight_layout()
fig.savefig(os.path.join(HINH, "hinh1_learning_rate.png"), dpi=160)
plt.close(fig)

# =========================================================== Thí nghiệm 2
print("\nTHÍ NGHIỆM 2 - ba cách chọn độ dài bước (eps = 0.01)")
cach = [("Bước cố định η = 0.1", buoc_co_dinh(0.1), "#2ca02c"),
        ("Chính xác theo tia", buoc_chinh_xac, "#9467bd"),
        ("Quay lui Armijo (m₁=0.01, α=0.5)", buoc_quay_lui, "#d62728")]
fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
axes[0].contour(g1, g2, Z, levels=[10.1, 10.5, 11, 12, 14, 17, 21, 26],
                colors="gray", linewidths=0.6)
for ten, ham, c in cach:
    qd = gradient_descent(x0, ham)
    fx = np.array([f(p) for p in qd])
    print(f"  {ten:<34}: {len(qd) - 1:>3} bước, x cuối = "
          f"({qd[-1][0]:.5f}, {qd[-1][1]:.5f}), f = {fx[-1]:.6f}")
    axes[0].plot(qd[:, 0], qd[:, 1], "o-", color=c, ms=3, lw=1.1, label=ten)
    axes[1].semilogy(np.maximum(fx - F_STAR, 1e-12), "o-", color=c, ms=3,
                     lw=1.4, label=ten)
axes[0].plot(0, 0, "k*", ms=12)
axes[0].set(xlabel="$x_1$", ylabel="$x_2$", xlim=(-0.6, 1.2), ylim=(-0.6, 1.2),
            title="Quỹ đạo nghiệm")
axes[0].legend(loc="lower right", fontsize=8)
axes[1].set(xlabel="Bước lặp k", ylabel="$f(x_k) - f^*$ (thang log)",
            title="Tốc độ hội tụ")
axes[1].grid(alpha=0.3)
axes[1].legend(fontsize=8)
fig.suptitle("So sánh các cách chọn độ dài bước trong Gradient Descent",
             fontweight="bold")
fig.tight_layout()
fig.savefig(os.path.join(HINH, "hinh2_chon_buoc.png"), dpi=160)
plt.close(fig)

# In chi tiết 3 bước đầu của phương pháp chính xác theo tia (đối chiếu tính tay)
print("\nChi tiết GD với bước chính xác theo tia (3 bước đầu):")
x = np.array(x0)
for k in range(3):
    g = grad(x)
    lam = buoc_chinh_xac(x, g)
    print(f"  k={k}: x=({x[0]:.5f}, {x[1]:.5f}), grad=({g[0]:.5f}, {g[1]:.5f}), "
          f"||grad||={np.linalg.norm(g):.5f}, lambda={lam:.5f}")
    x = x - lam * g
print("\nĐã lưu: hinh1_learning_rate.png, hinh2_chon_buoc.png")
