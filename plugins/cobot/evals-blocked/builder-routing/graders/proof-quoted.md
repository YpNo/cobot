---
type: regex
target: last_message
pattern: "cargo (test|clippy|fmt|build)[\\s\\S]{0,300}exit( code)?\\s*[:=]?\\s*\\d+|exit( code)?\\s*[:=]?\\s*\\d+[\\s\\S]{0,300}cargo (test|clippy|fmt|build)"
flags: i
---
