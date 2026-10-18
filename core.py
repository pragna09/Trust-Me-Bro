"""Shared logic: state parsing, keyword baseline, data prep, alert scoring."""
import json
import re

import pandas as pd

STATE_NAMES = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR", "california": "CA",
    "colorado": "CO", "connecticut": "CT", "delaware": "DE", "district of columbia": "DC",
    "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID", "illinois": "IL",
    "indiana": "IN", "iowa": "IA", "kansas": "KS", "kentucky": "KY", "louisiana": "LA",
    "maine": "ME", "maryland": "MD", "massachusetts": "MA", "michigan": "MI", "minnesota": "MN",
    "mississippi": "MS", "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
    "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY",
    "north carolina": "NC", "north dakota": "ND", "ohio": "OH", "oklahoma": "OK", "oregon": "OR",
    "pennsylvania": "PA", "puerto rico": "PR", "rhode island": "RI", "south carolina": "SC",
    "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT", "vermont": "VT",
    "virginia": "VA", "washington": "WA", "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY",
}
ALL_CODES = sorted(set(STATE_NAMES.values()))
N_JURISDICTIONS = len(ALL_CODES)  # 50 states + DC + PR

# Abbreviations that are also common English words / fragments: only accept them in list context
AMBIGUOUS = {"IN", "OR", "ME", "HI", "OK", "ID", "CO", "AL", "LA", "PA", "MA", "DE", "MS"}

_NAME_RE = re.compile(
    r"\b(" + "|".join(sorted(map(re.escape, STATE_NAMES), key=len, reverse=True)) + r")\b",
    re.I,
)
_ABBR = {c: re.compile(rf"(?<![A-Za-z]){c}(?![A-Za-z])") for c in ALL_CODES}
_ABBR_LIST = {c: re.compile(rf"(?:[,;(/]\s*{c}(?![A-Za-z])|(?<![A-Za-z]){c}\s*[,;)/])") for c in AMBIGUOUS}
NATION_RE = re.compile(
    r"nation\s*-?\s*wide|nationally|all\s+(?:50\s+)?states|throughout\s+the\s+(?:u\.?s\.?|united\s+states)",
    re.I,
)

# Rule-based baseline: the "obvious" hazards
BASELINE_RE = re.compile(
    r"listeria|salmonella|e\.?\s?coli|escherichia|botulinum|botulism|cronobacter|hepatitis\s?a|"
    r"undeclared|allergen|peanut|tree\s?nut|sesame|shellfish",
    re.I,
)


def parse_states(text):
    """Return a sorted list of state codes, or ["ALL"] for nationwide distribution."""
    t = str(text or "")
    if NATION_RE.search(t):
        return ["ALL"]
    t = re.sub(r"washington,?\s*d\.?\s*c\.?", "district of columbia", t, flags=re.I)
    found = {STATE_NAMES[m.group(1).lower()] for m in _NAME_RE.finditer(t)}
    rest = _NAME_RE.sub(" ", t)
    for c in ALL_CODES:
        pat = _ABBR_LIST[c] if c in AMBIGUOUS else _ABBR[c]
        if pat.search(rest):
            found.add(c)
    return sorted(found)


def touches_texas(states):
    return "TX" in states or "ALL" in states


def reach_fraction(states):
    if "ALL" in states:
        return 1.0
    return min(1.0, len(states) / N_JURISDICTIONS)


def alert_score(p_class1, states):
    """Severity x reach, only for recalls that reach Texas. Heuristic weights: tune them."""
    if not touches_texas(states):
        return 0.0
    return round(float(p_class1) * (0.5 + 0.5 * reach_fraction(states)), 4)


def tier(score):
    if score >= 0.75:
        return "PULL NOW"
    if score >= 0.40:
        return "REVIEW TODAY"
    if score > 0:
        return "MONITOR"
    return "NOT TEXAS"


def alert_text(firm, product, reason, states, code_info, p_class1, score):
    scope = "nationwide" if "ALL" in states else ", ".join(states[:8]) + ("..." if len(states) > 8 else "")
    lots = (code_info or "no lot codes listed").strip().replace("\n", " ")[:120]
    return (
        f"[{tier(score)}] {firm}: {str(product)[:80]}. Reason: {str(reason)[:150]}. "
        f"Reach: {scope}. Lots to pull: {lots}. Model P(Class I)={p_class1:.2f}"
    )


def load_raw(path="data/enforcement.jsonl"):
    rows = []
    with open(path) as f:
        for line in f:
            r = json.loads(line)
            r.pop("openfda", None)
            rows.append(r)
    return pd.DataFrame(rows)


def prepare(df):
    df = df.copy()
    for c in ["reason_for_recall", "product_description", "distribution_pattern", "code_info",
              "recalling_firm", "classification", "recall_number"]:
        if c not in df:
            df[c] = ""
        df[c] = df[c].fillna("").astype(str)
    for src, dst in [("recall_initiation_date", "init_dt"),
                     ("center_classification_date", "class_dt"),
                     ("report_date", "report_dt")]:
        df[dst] = pd.to_datetime(df.get(src), format="%Y%m%d", errors="coerce")
    df = df[df.classification.isin(["Class I", "Class II", "Class III"])].copy()
    df["y"] = (df.classification == "Class I").astype(int)
    df["reason"] = df.reason_for_recall
    df["product"] = df.product_description
    df["dist"] = df.distribution_pattern
    df["states"] = df.dist.map(parse_states)
    df["states_str"] = df.states.map(lambda s: ",".join(s))
    df["texas"] = df.states.map(touches_texas)
    df["days_to_class"] = (df.class_dt - df.init_dt).dt.days
    df["base_pred"] = df.reason.str.contains(BASELINE_RE).astype(int)
    return df
