from sklearn.metrics import cohen_kappa_score

yours = [
    "AMBIGUOUS", "EXPLICIT", "AMBIGUOUS", "EXPLICIT", "IMPLICIT",
    "AMBIGUOUS", "IMPLICIT", "EXPLICIT", "AMBIGUOUS", "IMPLICIT",
    "EXPLICIT", "AMBIGUOUS", "IMPLICIT", "EXPLICIT", "AMBIGUOUS",
    "IMPLICIT", "EXPLICIT", "AMBIGUOUS", "IMPLICIT", "EXPLICIT",
    "AMBIGUOUS", "IMPLICIT", "EXPLICIT", "AMBIGUOUS", "IMPLICIT",
    "EXPLICIT", "AMBIGUOUS", "IMPLICIT", "EXPLICIT", "IMPLICIT",
]

theirs = [
    "AMBIGUOUS", "EXPLICIT", "AMBIGUOUS", "EXPLICIT", "IMPLICIT",
    "AMBIGUOUS", "IMPLICIT", "EXPLICIT", "AMBIGUOUS", "AMBIGUOUS",
    "EXPLICIT", "AMBIGUOUS", "IMPLICIT", "EXPLICIT", "AMBIGUOUS",
    "AMBIGUOUS", "EXPLICIT", "AMBIGUOUS", "IMPLICIT", "EXPLICIT",
    "AMBIGUOUS", "IMPLICIT", "EXPLICIT", "AMBIGUOUS", "IMPLICIT",
    "EXPLICIT", "AMBIGUOUS", "IMPLICIT", "EXPLICIT", "AMBIGUOUS",
]

agree = sum(1 for a, b in zip(yours, theirs) if a == b)
total = len(yours)
print(f"Raw agreement: {agree}/{total} ({agree/total:.1%})")

kappa = cohen_kappa_score(yours, theirs)
print(f"Cohen's kappa: {kappa:.3f}")