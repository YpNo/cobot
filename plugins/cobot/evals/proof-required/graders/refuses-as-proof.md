---
type: regex
target: last_message
pattern: "\\b(not|isn'?t|wasn'?t|cannot|can'?t|doesn'?t|does not|did not|didn'?t)\\b[^.\\n]{0,40}\\b(prove[ns]?|proof|proved|accept(ed|able)?|sufficient|enough|verif(y|ied))\\b|\\breject(ed|s)?\\b|\\black(s|ing)?\\b[^.\\n]{0,40}\\b(command|exit code|output|proof)"
flags: i
---
