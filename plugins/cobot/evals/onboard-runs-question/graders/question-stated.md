---
type: regex
target: last_message
pattern: "(question|would (have )?ask)[\\s\\S]{0,200}(engine|podman|docker|distrobox|builds|where (commands|things) run)|(engine|podman|docker|distrobox|builds|where (commands|things) run)[\\s\\S]{0,200}(question|would (have )?ask)"
flags: i
---
