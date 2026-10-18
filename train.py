"""Train the Class I classifier with a time-based split, compare to the keyword baseline, write replay data."""
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (confusion_matrix, f1_score, precision_recall_curve,
                             precision_recall_fscore_support, roc_auc_score)
from sklearn.pipeline import Pipeline

from core import alert_score, alert_text, load_raw, prepare, tier


def make_pipe():
    pre = ColumnTransformer([
        ("reason", TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True, stop_words="english"), "reason"),
        ("product", TfidfVectorizer(ngram_range=(1, 2), min_df=3, sublinear_tf=True), "product"),
        ("dist", TfidfVectorizer(min_df=5, sublinear_tf=True), "dist"),
    ])
    return Pipeline([("pre", pre), ("clf", LogisticRegression(C=4, max_iter=3000, class_weight="balanced"))])


def metrics(y, pred):
    p, r, f, _ = precision_recall_fscore_support(y, pred, labels=[1], zero_division=0)
    return {
        "class1_precision": round(float(p[0]), 4),
        "class1_recall": round(float(r[0]), 4),
        "class1_f1": round(float(f[0]), 4),
        "macro_f1": round(float(f1_score(y, pred, average="macro")), 4),
        "confusion_[[TN,FP],[FN,TP]]": confusion_matrix(y, pred, labels=[0, 1]).tolist(),
    }


def main():
    df = prepare(load_raw())
    df = df[df.class_dt.notna()].sort_values("class_dt").reset_index(drop=True)
    print("records:", len(df), "| Class I share:", round(df.y.mean(), 3))

    n = len(df)
    test_start = int(n * 0.80)
    val_start = int(test_start * 0.85)
    fit, val, test = df.iloc[:val_start], df.iloc[val_start:test_start], df.iloc[test_start:].copy()
    print("fit", len(fit), "val", len(val), "test", len(test),
          "| test period:", test.class_dt.min().date(), "->", test.class_dt.max().date())

    cols = ["reason", "product", "dist"]
    pipe = make_pipe().fit(fit[cols], fit.y)

    # Pick the highest threshold that still catches >=95% of Class I on validation
    pv = pipe.predict_proba(val[cols])[:, 1]
    prec, rec, thr = precision_recall_curve(val.y, pv)
    ok = np.where(rec[:-1] >= 0.95)[0]
    threshold = float(thr[ok[-1]]) if len(ok) else 0.5
    print("chosen threshold:", round(threshold, 3))

    test["p_class1"] = pipe.predict_proba(test[cols])[:, 1]
    test["pred_class1"] = (test.p_class1 >= threshold).astype(int)

    out = {
        "n_records": int(n), "class1_share": round(float(df.y.mean()), 4),
        "test_period": [str(test.class_dt.min().date()), str(test.class_dt.max().date())],
        "threshold": round(threshold, 4),
        "baseline_keyword": metrics(test.y, test.base_pred),
        "model_at_0.5": metrics(test.y, (test.p_class1 >= 0.5).astype(int)),
        "model_tuned_threshold": metrics(test.y, test.pred_class1),
        "model_roc_auc": round(float(roc_auc_score(test.y, test.p_class1)), 4),
        "texas_subset_model": metrics(test[test.texas].y, test[test.texas].pred_class1),
        "texas_subset_baseline": metrics(test[test.texas].y, test[test.texas].base_pred),
        "state_parse_coverage": round(float((df.states.map(len) > 0).mean()), 4),
        "nationwide_share": round(float(df.states.map(lambda s: "ALL" in s).mean()), 4),
        "texas_reaching_share": round(float(df.texas.mean()), 4),
    }
    d = df.days_to_class.dropna()
    d = d[d >= 0]
    out["days_initiation_to_classification"] = {
        "median": float(d.median()), "p25": float(d.quantile(0.25)), "p75": float(d.quantile(0.75)),
        "note": "Potential time a model could save, not achieved time saved.",
    }
    names = pipe.named_steps["pre"].get_feature_names_out()
    coef = pipe.named_steps["clf"].coef_[0]
    order = np.argsort(coef)
    out["top_class1_terms"] = [names[i] for i in order[::-1][:15]]
    out["top_class23_terms"] = [names[i] for i in order[:15]]

    with open("metrics.json", "w") as f:
        json.dump(out, f, indent=2)
    joblib.dump({"pipe": pipe, "threshold": threshold}, "model.joblib")

    test["alert_score"] = [alert_score(p, s) for p, s in zip(test.p_class1, test.states)]
    test["tier"] = test.alert_score.map(tier)
    test["alert"] = [
        alert_text(r.recalling_firm, r.product, r.reason, r.states, r.code_info, r.p_class1, r.alert_score)
        for r in test.itertuples()
    ]
    test["init_date"] = test.init_dt.dt.strftime("%Y-%m-%d")
    test["class_date"] = test.class_dt.dt.strftime("%Y-%m-%d")
    keep = ["recall_number", "recalling_firm", "product", "reason", "dist", "code_info", "classification",
            "init_date", "class_date", "days_to_class", "states_str", "texas", "p_class1", "pred_class1",
            "base_pred", "alert_score", "tier", "alert"]
    test[keep].to_csv("data/replay.csv", index=False)
    print(json.dumps({k: out[k] for k in ["baseline_keyword", "model_tuned_threshold", "model_roc_auc"]}, indent=2))
    print("saved model.joblib, metrics.json, data/replay.csv")


if __name__ == "__main__":
    main()
