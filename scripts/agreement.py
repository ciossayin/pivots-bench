#!/usr/bin/env python3
"""Inter-annotator agreement, as reported in Appendix E.

Input is a CSV with one row per item and one column per annotator; missing values
are left blank. Ordinal Krippendorff's alpha is computed over an annotator x item
matrix, plus the exact-agreement rate the paper reports alongside it.

    python scripts/agreement.py annotations.csv --dimension-column dim
"""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=Path)
    parser.add_argument("--annotator-columns", nargs="*", default=None,
                        help="Defaults to every column named a1, a2, ... or annotator*.")
    parser.add_argument("--dimension-column", default="dimension")
    args = parser.parse_args()

    import numpy as np
    import pandas as pd
    import krippendorff

    df = pd.read_csv(args.csv)
    cols = args.annotator_columns or [
        c for c in df.columns if c.lower().startswith(("a", "annotator")) and c != args.dimension_column
    ]
    if len(cols) < 2:
        raise SystemExit(f"need at least two annotator columns, found {cols}")

    def alpha_and_exact(frame: pd.DataFrame) -> tuple[float, float]:
        matrix = frame[cols].apply(pd.to_numeric, errors="coerce").to_numpy(dtype=float).T
        alpha = krippendorff.alpha(reliability_data=matrix, level_of_measurement="ordinal")
        rows = matrix.T
        valid = ~np.isnan(rows)
        agreed = [
            len(set(row[mask])) == 1
            for row, mask in zip(rows, valid)
            if mask.sum() >= 2
        ]
        exact = 100.0 * sum(agreed) / len(agreed) if agreed else float("nan")
        return alpha, exact

    if args.dimension_column in df.columns:
        for dim, group in df.groupby(args.dimension_column):
            alpha, exact = alpha_and_exact(group)
            print(f"{dim}: exact {exact:.2f}%  alpha {alpha:.4f}  (n={len(group)})")
    alpha, exact = alpha_and_exact(df)
    print(f"overall: exact {exact:.2f}%  alpha {alpha:.4f}  (n={len(df)})")


if __name__ == "__main__":
    main()
