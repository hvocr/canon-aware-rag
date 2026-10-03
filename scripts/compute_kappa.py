from sklearn.metrics import cohen_kappa_score

# Replace these with the actual labels.
# Order must match the query IDs above.
yours = [
    "AMBIGUOUS", "EXPLICIT", "AMBIGUOUS", "EXPLICIT", "IMPLICIT",
    "AMBIGUOUS", "IMPLICIT", "EXPLICIT", "AMBIGUOUS", "IMPLICIT",
    "EXPLICIT", "AMBIGUOUS", "IMPLICIT", "EXPLICIT", "AMBIGUOUS",
    "IMPLICIT", "EXPLICIT", "AMBIGUOUS", "IMPLICIT", "EXPLICIT",
    "AMBIGUOUS", "IMPLICIT", "EXPLICIT", "AMBIGUOUS", "IMPLICIT",
    "EXPLICIT", "AMBIGUOUS", "IMPLICIT", "EXPLICIT", "IMPLICIT",
]

# FILL THIS IN with your annotator's labels
theirs = [
    "", "", "", "", "",
    "", "", "", "", "",
    "", "", "", "", "",
    "", "", "", "", "",
    "", "", "", "", "",
    "", "", "", "", "",
]

agree = sum(1 for a, b in zip(yours, theirs) if a == b)
total = len(yours)
print(f"Raw agreement: {agree}/{total} ({agree/total:.1%})")

# Only compute kappa if all labels are filled
if all(theirs):
    kappa = cohen_kappa_score(yours, theirs)
    print(f"Cohen's kappa: {kappa:.3f}")
else:
    print("Fill in the 'theirs' list before computing kappa.")