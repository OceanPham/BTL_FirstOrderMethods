"""
03 - SO SÁNH BATCH GD / SGD / MINI-BATCH GD (tự cài đặt bằng NumPy)

Bài toán: hồi quy tuyến tính, hàm mất mát bình phương trung bình
        J(theta) = 1/(2N) * sum_i (x_i^T theta - y_i)^2

Ba thuật toán chỉ khác nhau ở kích thước lô b (batch size):
        b = N  -> Batch Gradient Descent
        b = 1  -> Stochastic Gradient Descent
        1<b<N  -> Mini-batch Gradient Descent

Thí nghiệm A (N = 1000, 2 tham số w, b): vẽ quỹ đạo và đường cong mất mát.
Thí nghiệm B (N = 50000, 20 đặc trưng): so sánh theo thời gian chạy thực
             và khảo sát ảnh hưởng của kích thước lô.

Chạy:  python 03_so_sanh_gd_sgd_minibatch.py
Kết quả: hinh/hinh3_quy_dao.png, hinh/hinh4_mat_mat.png, hinh/hinh5_batch_size.png
"""
import os
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HINH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "hinh")
os.makedirs(HINH, exist_ok=True)


def mat_mat(X, y, theta):
    r = X @ theta - y
    return 0.5 * np.mean(r * r)


def huan_luyen(X, y, batch_size, lr, epochs, seed=0, decay=0.0,
               luu_quy_dao=False):
    """Mini-batch gradient descent tổng quát.

    batch_size = N -> Batch GD;  batch_size = 1 -> SGD.
    lr tại epoch t: lr / (1 + decay * t)   (decay = 0: tốc độ học cố định).
    Trả về: theta, lịch sử mất mát theo epoch, thời gian tích lũy, quỹ đạo.
    """
    rng = np.random.default_rng(seed)
    N, d = X.shape
    theta = np.zeros(d)
    ls_mat_mat = [mat_mat(X, y, theta)]
    ls_thoi_gian = [0.0]
    quy_dao = [theta.copy()]
    tong_tg = 0.0
    for epoch in range(epochs):
        t0 = time.perf_counter()
        eta = lr / (1.0 + decay * epoch)
        chi_so = rng.permutation(N)                 # xáo trộn dữ liệu mỗi epoch
        for bat_dau in range(0, N, batch_size):
            lo = chi_so[bat_dau:bat_dau + batch_size]
            Xb, yb = X[lo], y[lo]
            g = Xb.T @ (Xb @ theta - yb) / len(lo)  # gradient trên lô
            theta = theta - eta * g                 # bước cập nhật
            if luu_quy_dao:
                quy_dao.append(theta.copy())
        tong_tg += time.perf_counter() - t0
        ls_mat_mat.append(mat_mat(X, y, theta))
        ls_thoi_gian.append(tong_tg)
    return theta, np.array(ls_mat_mat), np.array(ls_thoi_gian), np.array(quy_dao)


# ======================================================== THÍ NGHIỆM A
print("=" * 70)
print("THÍ NGHIỆM A: y = 3x + 4 + nhiễu, N = 1000, tham số theta = (b, w)")
print("=" * 70)
rng = np.random.default_rng(42)
N = 1000
x = rng.uniform(0, 2, N)
y = 3 * x + 4 + rng.normal(0, 1.0, N)
X = np.column_stack([np.ones(N), x])              # cột 1 cho hệ số chặn b

theta_cx = np.linalg.solve(X.T @ X, X.T @ y)      # nghiệm chính xác
J_cx = mat_mat(X, y, theta_cx)
print(f"Nghiệm chính xác (phương trình chuẩn): b = {theta_cx[0]:.4f}, "
      f"w = {theta_cx[1]:.4f}, J* = {J_cx:.5f}\n")

EPOCHS = 30
cau_hinh = [
    ("Batch GD (b = N)", N, 0.1, "#1f77b4"),
    ("SGD (b = 1)", 1, 0.01, "#d62728"),
    ("Mini-batch GD (b = 32)", 32, 0.05, "#2ca02c"),
]
ket_qua = {}
print(f"{'Phương pháp':<24}{'η':>6}{'số cập nhật':>13}{'b':>9}{'w':>9}"
      f"{'J - J*':>12}{'t (ms)':>9}")
for ten, b, lr, mau in cau_hinh:
    th, ls, tg, qd = huan_luyen(X, y, b, lr, EPOCHS, seed=1, luu_quy_dao=True)
    ket_qua[ten] = (th, ls, tg, qd, mau)
    print(f"{ten:<24}{lr:>6}{len(qd) - 1:>13}{th[0]:>9.4f}{th[1]:>9.4f}"
          f"{ls[-1] - J_cx:>12.2e}{tg[-1] * 1e3:>9.1f}")

# --- Hình 3: quỹ đạo trên mặt phẳng tham số
bb, ww = np.meshgrid(np.linspace(-0.5, 5.5, 200), np.linspace(-0.5, 5.0, 200))
JJ = np.array([[mat_mat(X, y, np.array([b_, w_])) for b_, w_ in zip(rb, rw)]
               for rb, rw in zip(bb, ww)])
fig, axes = plt.subplots(1, 3, figsize=(14, 4.6), sharey=True)
for ax, (ten, (th, ls, tg, qd, mau)) in zip(axes, ket_qua.items()):
    ax.contour(bb, ww, JJ, levels=np.geomspace(J_cx * 1.02, JJ.max(), 14),
               colors="gray", linewidths=0.5)
    ax.plot(qd[:, 0], qd[:, 1], "-", color=mau, lw=0.8, alpha=0.9)
    ax.plot(qd[0, 0], qd[0, 1], "ks", ms=6)
    ax.plot(theta_cx[0], theta_cx[1], "k*", ms=13)
    ax.set(title=f"{ten}\n{len(qd) - 1} lần cập nhật", xlabel="b (hệ số chặn)")
axes[0].set_ylabel("w (hệ số góc)")
fig.suptitle("Quỹ đạo tham số của ba phương pháp sau 30 epoch (★: nghiệm tối ưu)",
             fontweight="bold")
fig.tight_layout()
fig.savefig(os.path.join(HINH, "hinh3_quy_dao.png"), dpi=160)
plt.close(fig)

# --- Hình 4: mất mát theo epoch + SGD có giảm dần tốc độ học
_, ls_decay, _, _ = huan_luyen(X, y, 1, 0.01, EPOCHS, seed=1, decay=0.3)
print(f"{'SGD + giảm dần η':<24}{'0.01':>6}{N * EPOCHS:>13}{'':>9}{'':>9}"
      f"{ls_decay[-1] - J_cx:>12.2e}")
fig, ax = plt.subplots(figsize=(7.5, 4.6))
for ten, (th, ls, tg, qd, mau) in ket_qua.items():
    ax.semilogy(ls - J_cx, color=mau, lw=1.8, label=ten)
ax.semilogy(ls_decay - J_cx, "--", color="#ff7f0e", lw=1.8,
            label="SGD, η giảm dần: η₀/(1 + 0.3t)")
ax.set(xlabel="Epoch", ylabel="$J(\\theta) - J^*$ (thang log)",
       title="Sai số hàm mất mát theo epoch")
ax.grid(alpha=0.3)
ax.legend()
fig.tight_layout()
fig.savefig(os.path.join(HINH, "hinh4_mat_mat.png"), dpi=160)
plt.close(fig)

# ======================================================== THÍ NGHIỆM B
print()
print("=" * 70)
print("THÍ NGHIỆM B: N = 50000 mẫu, d = 20 đặc trưng")
print("=" * 70)
rng = np.random.default_rng(7)
N2, d2 = 50_000, 20
X2 = rng.normal(size=(N2, d2))
theta_that = rng.normal(size=d2)
y2 = X2 @ theta_that + rng.normal(0, 0.5, N2)
J2_cx = mat_mat(X2, y2, np.linalg.solve(X2.T @ X2, X2.T @ y2))

EPOCHS2 = 5
cac_b = [1, 8, 32, 128, 1024, N2]
lr_theo_b = {1: 0.005, 8: 0.02, 32: 0.05, 128: 0.1, 1024: 0.3, N2: 0.5}
tg_epoch, sai_so, duong = [], [], {}
print(f"{'batch size':>10}{'η':>8}{'cập nhật/epoch':>16}{'t/epoch (ms)':>14}"
      f"{'J - J* sau 5 epoch':>20}")
for b in cac_b:
    th, ls, tg, _ = huan_luyen(X2, y2, b, lr_theo_b[b], EPOCHS2, seed=3)
    tg_epoch.append(tg[-1] / EPOCHS2 * 1e3)
    sai_so.append(ls[-1] - J2_cx)
    duong[b] = (tg, ls - J2_cx)
    print(f"{b:>10}{lr_theo_b[b]:>8}{int(np.ceil(N2 / b)):>16}"
          f"{tg_epoch[-1]:>14.1f}{sai_so[-1]:>20.3e}")

fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
nhan = [str(b) if b < N2 else "N=50000" for b in cac_b]
axes[0].bar(nhan, tg_epoch, color="#1f77b4")
axes[0].set(yscale="log", xlabel="Kích thước lô b",
            ylabel="Thời gian mỗi epoch (ms, thang log)",
            title="Chi phí tính toán mỗi epoch")
for i, v in enumerate(tg_epoch):
    axes[0].text(i, v * 1.1, f"{v:.0f}", ha="center", fontsize=9)
mau_b = {1: "#d62728", 32: "#2ca02c", 1024: "#9467bd", N2: "#1f77b4"}
for b, c in mau_b.items():
    tg, e = duong[b]
    axes[1].loglog(np.maximum(tg[1:], 1e-5) * 1e3, np.maximum(e[1:], 1e-12),
                   "o-", color=c, ms=4,
                   label=f"b = {b}" if b < N2 else "b = N (Batch GD)")
axes[1].set(xlabel="Thời gian chạy (ms, thang log)",
            ylabel="$J - J^*$ (thang log)",
            title="Sai số theo thời gian chạy thực (5 epoch)")
axes[1].grid(alpha=0.3, which="both")
axes[1].legend()
fig.suptitle("Ảnh hưởng của kích thước lô (N = 50000, d = 20)", fontweight="bold")
fig.tight_layout()
fig.savefig(os.path.join(HINH, "hinh5_batch_size.png"), dpi=160)
plt.close(fig)
print("\nĐã lưu: hinh3_quy_dao.png, hinh4_mat_mat.png, hinh5_batch_size.png")
