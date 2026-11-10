"""
04 - SỬ DỤNG THƯ VIỆN scikit-learn

(1) Hồi quy tuyến tính bằng SGDRegressor  - so với nghiệm chính xác LinearRegression
(2) Hồi quy logistic bằng SGDClassifier   - so với LogisticRegression (L-BFGS)
(3) Học trực tuyến (dữ liệu đến theo từng khối) bằng SGDClassifier.partial_fit
(4) Mạng nơ-ron MLPClassifier(solver="sgd") với các batch_size khác nhau

Lưu ý: SGDRegressor / SGDClassifier của scikit-learn LUÔN cập nhật theo từng mẫu
(SGD thuần, b = 1). Mini-batch thực sự có trong MLPClassifier (tham số batch_size).

Cả ba bộ dữ liệu đều có sẵn trong scikit-learn (không cần tải từ Internet).

Chạy:  python 04_thu_vien_sklearn.py
Kết quả: hinh/hinh6_sklearn.png
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import load_breast_cancer, load_diabetes, load_digits
from sklearn.linear_model import (LinearRegression, LogisticRegression,
                                  SGDClassifier, SGDRegressor)
from sklearn.metrics import accuracy_score, r2_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

HINH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "hinh")
os.makedirs(HINH, exist_ok=True)


def chia_va_chuan_hoa(X, y, stratify=None):
    """Chia train/test 80/20 và chuẩn hóa đặc trưng (rất quan trọng với SGD)."""
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=0,
                                          stratify=stratify)
    sc = StandardScaler().fit(Xtr)
    return sc.transform(Xtr), sc.transform(Xte), ytr, yte


# ------------------------------------------------------------------ (1)
print("(1) HỒI QUY TUYẾN TÍNH - bộ dữ liệu diabetes (442 mẫu, 10 đặc trưng)")
X, y = load_diabetes(return_X_y=True)
Xtr, Xte, ytr, yte = chia_va_chuan_hoa(X, y)

sgd = SGDRegressor(loss="squared_error", penalty=None,
                   learning_rate="invscaling", eta0=0.01, power_t=0.25,
                   max_iter=2000, tol=1e-6, random_state=0)
sgd.fit(Xtr, ytr)
ols = LinearRegression().fit(Xtr, ytr)
print(f"    SGDRegressor     : R2 test = {r2_score(yte, sgd.predict(Xte)):.4f} "
      f"({sgd.n_iter_} epoch)")
print(f"    LinearRegression : R2 test = {r2_score(yte, ols.predict(Xte)):.4f} "
      f"(nghiệm chính xác)")

# ------------------------------------------------------------------ (2)
print("\n(2) HỒI QUY LOGISTIC - bộ dữ liệu breast_cancer (569 mẫu, 30 đặc trưng)")
X, y = load_breast_cancer(return_X_y=True)
Xtr, Xte, ytr, yte = chia_va_chuan_hoa(X, y, stratify=y)

clf = SGDClassifier(loss="log_loss", penalty="l2", alpha=1e-4,
                    learning_rate="optimal", max_iter=1000, tol=1e-4,
                    random_state=0)
clf.fit(Xtr, ytr)
lr = LogisticRegression(max_iter=1000).fit(Xtr, ytr)
print(f"    SGDClassifier(log_loss) : accuracy test = "
      f"{accuracy_score(yte, clf.predict(Xte)):.4f} ({clf.n_iter_} epoch)")
print(f"    LogisticRegression      : accuracy test = "
      f"{accuracy_score(yte, lr.predict(Xte)):.4f}")

# ------------------------------------------------------------------ (3)
print("\n(3) HỌC TRỰC TUYẾN với partial_fit - bộ dữ liệu digits (1797 ảnh 8x8, 10 lớp)")
X, y = load_digits(return_X_y=True)
Xtr, Xte, ytr, yte = chia_va_chuan_hoa(X, y, stratify=y)
cac_lop = np.unique(y)
EPOCHS = 20
rng = np.random.default_rng(0)

model = SGDClassifier(loss="log_loss", penalty=None,
                      learning_rate="constant", eta0=0.01, random_state=0)
acc_online = []
for epoch in range(EPOCHS):
    chi_so = rng.permutation(len(Xtr))
    for s in range(0, len(Xtr), 32):           # dữ liệu "đến" theo khối 32 mẫu
        khoi = chi_so[s:s + 32]
        model.partial_fit(Xtr[khoi], ytr[khoi], classes=cac_lop)
    acc_online.append(accuracy_score(yte, model.predict(Xte)))
print(f"    SGDClassifier.partial_fit (khối 32 mẫu): accuracy test sau "
      f"{EPOCHS} epoch = {acc_online[-1]:.4f}")

# ------------------------------------------------------------------ (4)
print("\n(4) MLPClassifier(solver='sgd') - mạng 64-64-10, 30 epoch, không momentum")
fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
axes[0].plot(range(1, EPOCHS + 1), acc_online, "o-", color="#d62728", ms=4)
axes[0].set(xlabel="Epoch", ylabel="Độ chính xác trên tập kiểm tra",
            title="SGDClassifier.partial_fit (học theo khối 32 mẫu)")
axes[0].grid(alpha=0.3)
for b, lr0, mau in [(len(Xtr), 0.1, "#1f77b4"), (32, 0.1, "#2ca02c"),
                    (1, 0.01, "#d62728")]:
    mlp = MLPClassifier(hidden_layer_sizes=(64,), solver="sgd", batch_size=b,
                        learning_rate_init=lr0, momentum=0.0, alpha=0.0,
                        max_iter=30, n_iter_no_change=1000, random_state=0)
    mlp.fit(Xtr, ytr)
    ten = {1: "b = 1 (SGD)", 32: "b = 32 (Mini-batch)"}.get(b, "b = N (Batch GD)")
    print(f"    {ten:<20} lr = {lr0:<5}: loss = {mlp.loss_curve_[-1]:.4f}, "
          f"accuracy test = {mlp.score(Xte, yte):.4f}")
    axes[1].semilogy(range(1, len(mlp.loss_curve_) + 1), mlp.loss_curve_,
                     color=mau, lw=1.8, label=ten)
axes[1].set(xlabel="Epoch", ylabel="Hàm mất mát huấn luyện (log)",
            title="MLPClassifier(solver='sgd') với các batch_size")
axes[1].grid(alpha=0.3)
axes[1].legend()
fig.suptitle("Tối ưu bậc một trong scikit-learn (bộ dữ liệu digits)",
             fontweight="bold")
fig.tight_layout()
fig.savefig(os.path.join(HINH, "hinh6_sklearn.png"), dpi=160)
plt.close(fig)
print("\nĐã lưu: hinh6_sklearn.png")
