"""
01 - VÍ DỤ TÍNH TAY (kiểm chứng các con số trình bày trong báo cáo)

Phần A: Gradient Descent trên hàm f(x1, x2) = x1^2 + x2^2 (ví dụ trong bài giảng
        Chương 1C), x0 = (2, 2), eta = 0.1.
Phần B: Một bước lặp của GD / SGD / Mini-batch GD trên bộ dữ liệu 3 điểm,
        mô hình y = w*x, hàm mất mát J(w) = 1/(2N) * sum (w*x_i - y_i)^2.

Chạy:  python 01_vi_du_tinh_tay.py
"""
import numpy as np

np.set_printoptions(precision=4, suppress=True)

# ---------------------------------------------------------------- Phần A
print("=" * 64)
print("PHẦN A - GD trên f(x) = x1^2 + x2^2, x0 = (2, 2), eta = 0.1")
print("=" * 64)


def grad_f(x):
    return 2 * x


x = np.array([2.0, 2.0])
eta = 0.1
print(f"{'k':>2} | {'x_k':<18} | {'grad f(x_k)':<18} | f(x_k)")
for k in range(6):
    g = grad_f(x)
    print(f"{k:>2} | {str(x):<18} | {str(g):<18} | {np.sum(x**2):.4f}")
    x = x - eta * g

# ---------------------------------------------------------------- Phần B
print()
print("=" * 64)
print("PHẦN B - Dữ liệu (x, y) = (1,1), (2,3), (3,2); mô hình y = w*x")
print("=" * 64)
X = np.array([1.0, 2.0, 3.0])
Y = np.array([1.0, 3.0, 2.0])
N = len(X)
eta = 0.1
w_star = np.sum(X * Y) / np.sum(X * X)
print(f"Nghiệm chính xác w* = sum(x*y)/sum(x^2) = 13/14 = {w_star:.4f}\n")


def grad_batch(w, idx):
    """Gradient trung bình trên các mẫu có chỉ số idx."""
    return np.mean((w * X[idx] - Y[idx]) * X[idx])


# --- Batch GD: mỗi bước dùng cả 3 mẫu
print("1) Batch GD (mỗi bước dùng cả N = 3 mẫu)")
w = 0.0
for k in range(3):
    g = grad_batch(w, np.arange(N))
    w_new = w - eta * g
    print(f"   k={k}: w={w:.4f}, grad={g:.4f} -> w_new={w_new:.4f}")
    w = w_new
w_gd = w

# --- SGD: mỗi bước dùng 1 mẫu, duyệt theo thứ tự 1, 2, 3
print("\n2) SGD (mỗi bước dùng 1 mẫu, thứ tự mẫu: 1, 2, 3)")
w = 0.0
for k, i in enumerate([0, 1, 2]):
    g = grad_batch(w, np.array([i]))
    w_new = w - eta * g
    print(f"   k={k}: mẫu {i + 1} (x={X[i]:.0f}, y={Y[i]:.0f}), w={w:.4f}, "
          f"grad={g:.4f} -> w_new={w_new:.4f}")
    w = w_new
w_sgd = w

# --- Mini-batch GD: batch size = 2
print("\n3) Mini-batch GD (b = 2, các lô: {1,2}, {3,1}, {2,3})")
w = 0.0
for k, idx in enumerate([[0, 1], [2, 0], [1, 2]]):
    g = grad_batch(w, np.array(idx))
    w_new = w - eta * g
    print(f"   k={k}: lô {[i + 1 for i in idx]}, w={w:.4f}, grad={g:.4f} "
          f"-> w_new={w_new:.4f}")
    w = w_new
w_mb = w

print(f"\nSau 3 lần cập nhật:  GD = {w_gd:.4f} | SGD = {w_sgd:.4f} | "
      f"Mini-batch = {w_mb:.4f} | w* = {w_star:.4f}")
print("Số lần tính gradient thành phần: GD = 9, SGD = 3, Mini-batch = 6")
