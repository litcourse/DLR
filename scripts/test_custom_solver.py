import numpy as np
import pandas as pd

from pisa_analysis import solve_wls


def test():
    rng = np.random.default_rng(2026)
    n = 1000
    x = rng.normal(size=n)
    weights = rng.uniform(0.5, 2.0, size=n)
    y = 10.0 + 2.5 * x + rng.normal(scale=0.05, size=n)
    X = pd.DataFrame({"Intercept": 1.0, "x": x})
    beta = solve_wls(X.to_numpy(dtype=float), y.reshape(-1, 1), weights).ravel()
    print("Beta:", beta)
    if not np.allclose(beta, [10.0, 2.5], atol=0.02):
        raise AssertionError("WLS solver failed to recover the known coefficients.")
    print("WLS solver test passed.")


if __name__ == "__main__":
    test()
