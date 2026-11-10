"""
05 - ÁP DỤNG TRONG HỌC MÁY: HUẤN LUYỆN MẠNG NƠ-RON BẰNG PyTorch

Bài toán: phân loại chữ số viết tay (bộ digits của scikit-learn, ảnh 8x8, 10 lớp).
Mô hình : mạng MLP 64 -> 64 -> 10, hàm mất mát cross-entropy.
Tối ưu  : torch.optim.SGD. Trong PyTorch, cả ba phương pháp dùng chung một
          optimizer; khác nhau duy nhất là batch_size của DataLoader:
              batch_size = N_train -> Batch GD
              batch_size = 1       -> SGD
              batch_size = 32      -> Mini-batch GD

Chạy:  python 05_pytorch_mang_no_ron.py
Kết quả: hinh/hinh7_pytorch_mlp.png
"""
import os
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

HINH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "hinh")
os.makedirs(HINH, exist_ok=True)

# ------------------------------------------------------------ dữ liệu
X, y = load_digits(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=0,
                                      stratify=y)
sc = StandardScaler().fit(Xtr)
Xtr = torch.tensor(sc.transform(Xtr), dtype=torch.float32)
Xte = torch.tensor(sc.transform(Xte), dtype=torch.float32)
ytr = torch.tensor(ytr, dtype=torch.long)
yte = torch.tensor(yte, dtype=torch.long)
N = len(Xtr)
tap_train = TensorDataset(Xtr, ytr)
ham_mat_mat = nn.CrossEntropyLoss()


def huan_luyen(batch_size, lr, epochs=30, seed=0):
    torch.manual_seed(seed)
    model = nn.Sequential(nn.Linear(64, 64), nn.ReLU(), nn.Linear(64, 10))
    optimizer = torch.optim.SGD(model.parameters(), lr=lr)
    loader = DataLoader(tap_train, batch_size=batch_size, shuffle=True)
    ls_loss, ls_acc = [], []
    t0 = time.perf_counter()
    for _ in range(epochs):
        for xb, yb in loader:                 # mỗi vòng lặp = 1 lần cập nhật
            optimizer.zero_grad()             # xóa gradient cũ
            loss = ham_mat_mat(model(xb), yb) # lan truyền tiến
            loss.backward()                   # lan truyền ngược -> gradient
            optimizer.step()                  # theta <- theta - lr * gradient
        with torch.no_grad():
            ls_loss.append(ham_mat_mat(model(Xtr), ytr).item())
            ls_acc.append((model(Xte).argmax(1) == yte).float().mean().item())
    return ls_loss, ls_acc, time.perf_counter() - t0


cau_hinh = [
    ("Batch GD (b = N)", N, 0.1, "#1f77b4"),
    ("SGD (b = 1)", 1, 0.01, "#d62728"),
    ("Mini-batch GD (b = 32)", 32, 0.1, "#2ca02c"),
]
EPOCHS = 30
print(f"Tập huấn luyện: {N} mẫu, tập kiểm tra: {len(Xte)} mẫu, {EPOCHS} epoch\n")
print(f"{'Phương pháp':<24}{'lr':>6}{'cập nhật':>10}{'loss train':>12}"
      f"{'acc test':>10}{'thời gian (s)':>15}")
fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
for ten, b, lr, mau in cau_hinh:
    ls_loss, ls_acc, tg = huan_luyen(b, lr, EPOCHS)
    so_cap_nhat = EPOCHS * -(-N // b)
    print(f"{ten:<24}{lr:>6}{so_cap_nhat:>10}{ls_loss[-1]:>12.4f}"
          f"{ls_acc[-1]:>10.4f}{tg:>15.2f}")
    ep = range(1, EPOCHS + 1)
    axes[0].semilogy(ep, ls_loss, color=mau, lw=1.8, label=ten)
    axes[1].plot(ep, ls_acc, color=mau, lw=1.8, label=ten)
axes[0].set(xlabel="Epoch", ylabel="Cross-entropy trên tập huấn luyện (log)",
            title="Hàm mất mát")
axes[1].set(xlabel="Epoch", ylabel="Độ chính xác trên tập kiểm tra",
            title="Độ chính xác", ylim=(0.5, 1.0))
for ax in axes:
    ax.grid(alpha=0.3)
    ax.legend()
fig.suptitle("Huấn luyện MLP 64-64-10 bằng torch.optim.SGD với các batch size",
             fontweight="bold")
fig.tight_layout()
fig.savefig(os.path.join(HINH, "hinh7_pytorch_mlp.png"), dpi=160)
plt.close(fig)
print("\nĐã lưu: hinh7_pytorch_mlp.png")
