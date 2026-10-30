from predictor import predict

tests = [
    ("will you come for a one night stand", "sexual"),
    ("send me your nudes",                  "sexual"),
    ("wanna hook up tonight",               "sexual"),
    ("are you horny",                       "sexual"),
    ("dtf?",                                "sexual"),
    ("i will fuck you",                     "threat"),
    ("i want to kidnap you",                "threat"),
    ("go fuck yourself",                    "abuse"),
    ("you are a bastard",                   "abuse"),
    ("i hate you so much",                  "abuse"),
    ("hey see you tomorrow",                "ham"),
    ("your team report is due friday",      "ham"),
]

print(f"{'RESULT':<6} {'TYPE':<10} {'EXPECTED':<10}  MESSAGE")
print("-" * 65)
for msg, expected in tests:
    r = predict(msg)
    got = r["override_type"] or ("-" if not r["is_spam"] else "spam")
    ok  = "✓" if (r["is_spam"] and got == expected) or (not r["is_spam"] and expected == "ham") else "✗"
    print(f"{ok} {r['label'].upper():<5} {got:<10} {expected:<10}  {msg}")
