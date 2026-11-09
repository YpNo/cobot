---
type: regex
target: last_message
pattern: "python3 -m unittest[\\s\\S]{0,400}(exit( code)?\\s*[:=]?\\s*\\d|\\bOK\\b|Ran \\d+ tests?)|\\b(send|sent|sending|return|returned|hand|handed)\\b[\\s\\S]{0,40}\\bback\\b"
flags: i
---
