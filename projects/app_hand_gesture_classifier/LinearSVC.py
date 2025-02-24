import numpy as np

class LinearSVC:
    class StandardScaler:
        mean:np.ndarray
        std:np.ndarray
        def transform(self, X):
            return (X - self.mean) / self.std

        def fit_transform(self, X):
            self.mean = np.mean(X, axis=0)
            self.std = np.std(X, axis=0)
            return self.transform(X)

    def __init__(self, C=1.0, learning_rate=0.01, max_iter=1000):
        self.C = C
        self.learning_rate = learning_rate
        self.max_iter = max_iter
        self.scaler = self.StandardScaler()

    def save(self, filename: str):
        np.savez(filename,
            C = self.C,
            learning_rate = self.learning_rate,
            max_iter = self.max_iter,
            scaler_mean = self.scaler.mean,
            scaler_std = self.scaler.std,
            classes = self.classes,
            _W =  self._W,
            _B =  self._B,
        )

    @classmethod
    def load(cls, filename: str):
        npzfile = np.load(filename)
        self = cls(
            C=float(npzfile["C"]), 
            learning_rate=float(npzfile["learning_rate"]), 
            max_iter=int(npzfile["max_iter"])
        )
        self.scaler.mean = npzfile["scaler_mean"]
        self.scaler.std = npzfile["scaler_std"]
        self.classes = npzfile["classes"]
        self._W = npzfile["_W"]
        self._B = npzfile["_B"]
        return self

    def _train_binary_svm(self, X, y):
        """
        训练一个二分类 SVM。
        """
        n_samples, n_features = X.shape
        w = np.zeros(n_features)
        b = 0
        for _ in range(self.max_iter):
            scores = np.dot(X, w) + b # 计算所有样本的预测得分
            margin = y * scores  # (n_samples,) 计算每个样本的 margin
            mask = margin < 1 # 获取不满足条件的样本，满足 condition 即为支持向量
            X_support = X[mask]  # 支持向量
            y_support = y[mask]  # 支持向量的标签
            if len(X_support) > 0: # 向量化更新公式
                w -= self.learning_rate * (2 * w / n_samples - self.C * np.dot(X_support.T, y_support))  # 批量更新 w
                b -= self.learning_rate * (-self.C * np.sum(y_support))  # 批量更新 b
        return w, b

    def fit(self, X, y):
        """
        训练多分类 SVM。
        参数：
        - X: (n_samples, n_features) 的特征矩阵
        - y: (n_samples,) 的标签数组，值为多个类别
        """
        self.classes = np.unique(y)  # 提取所有类别
        self._W = np.zeros((len(self.classes), X.shape[1]))
        self._B = np.zeros(len(self.classes))
        for i, cls in enumerate(self.classes):
            binary_y = np.where(y == cls, 1, -1) # 构造一对多的标签
            w, b = self._train_binary_svm(X, binary_y)
            self._W[i] = w
            self._B[i] = b

    def forward(self, X):
        return np.dot(X, self._W.T) + self._B

    def predict(self, X):
        return self.classes[np.argmax(self.forward(X), axis=1)]  # 返回得分最高的类别

    def predict_with_confidence(self, X):
        def softmax(x):
            x_max = np.max(x, axis=-1, keepdims=True) # 处理数值稳定性：减去最大值
            exp_x = np.exp(x - x_max)
            return exp_x / np.sum(exp_x, axis=-1, keepdims=True)
        res = self.forward(X) # (n_samples, n_classes)
        confidences = softmax(res) # (n_samples, n_classes)
        return self.classes[np.argmax(res, axis=1)], np.max(confidences, axis=1)  # 返回得分最高的类别


class LinearSVCManager:
    def __init__(self, clf: LinearSVC=LinearSVC(), X=None, Y=None, pretrained=False):
        if X is None:
            X = np.empty((0, 0))
        if Y is None:
            Y = np.empty((0,))

        # 转换为 NumPy 数组
        if isinstance(X, list):
            X = np.array(X)
        if isinstance(Y, list):
            Y = np.array(Y)

        # 类型检查
        if not isinstance(X, np.ndarray):
            raise TypeError("X must be a list or numpy array.")
        if not isinstance(Y, np.ndarray):
            raise TypeError("Y must be a list or numpy array.")

        if len(X) != len(Y):
            raise ValueError("Length of X and Y must be equal.")
        if len(Y) == 0:
            raise ValueError("A classifier (clf) must be provided with training samples X and Y.")

        if pretrained:
            if clf is None:
                raise ValueError("A pretrained classifier (clf) can't be `None`.")

        if clf is None:
            if pretrained:
                raise ValueError("A pretrained classifier (clf) can't be `None`.")
            clf = LinearSVC()

        self.clf = clf
        self.samples = (X, Y)

        if not pretrained:
            self.train()

    def train(self):
        X_scaled = self.clf.scaler.fit_transform(self.samples[0])
        self.clf.fit(X_scaled, self.samples[1])
        print(f"{len(self.samples[1])} samples have been trained.")

    def test(self, X):
        X = np.array(X)
        if X.shape[-1] != self.samples[0].shape[1]:
            raise ValueError("Tested data dimension mismatch.")
        X_scaled = self.clf.scaler.transform(X)
        return self.clf.predict_with_confidence(X_scaled)

    def add(self, X, Y):
        X = np.array(X)
        Y = np.array(Y)

        if X.shape[-1] != self.samples[0].shape[1]:
            raise ValueError("Added data dimension mismatch.")

        if len(self.samples[0])>0:
            self.samples = (
                np.vstack([self.samples[0], X]),
                np.concatenate([self.samples[1], Y])
            )
        else:
            self.samples = (X, Y)

        self.train()

    def rm(self, indices):
        X, Y = self.samples

        if any(idx < 0 or idx >= len(Y) for idx in indices):
            raise IndexError("Index out of bounds.")

        mask = np.ones(len(Y), dtype=bool)
        mask[indices] = False

        self.samples = (X[mask], Y[mask])

        if len(self.samples[1]) > 0:
            self.train()
        else:
            print("Warning: All data has been removed. Model is untrained now.")

    def clear_samples(self):
        self.samples = (np.empty((0, self.samples[0].shape[1])), np.empty((0,)))
        print("All training samples have been cleared.")
