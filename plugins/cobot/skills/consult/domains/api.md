# Consult: api

Paths below start at the plugin root your prompt names.

Read-only. Change nothing, generate nothing, call no live API. Read `skills/expert-api/SKILL.md`
and its `references/` first: they are the baseline. `spectral lint` and `redocly lint` are
read-only and run only when installed; `redocly bundle` and any code generator write files and
are never run here. A missing linter is a line in the summary, not something to install.

## Procedure

1. **Inventory by search, not by reading.** Find `*openapi*.json`, `*openapi*.y*ml`,
   `swagger*.json`, `*.proto` (Glob), then for each: its size (`wc -l`), its version line
   (`grep -m1 -E '"?(swagger|openapi)"?\s*:'`), and whether it is **generated**: a
   `*.generated.*` name, placeholder values such as `0.0.0+…-VERSION`, a Makefile or script
   target that writes it (`grep -n` the file name in `Makefile`, `package.json`, `scripts/`). A
   repository linter config (`.spectral.yaml`, `redocly.yaml`) is the house rule set: note it.
2. **Large documents** (over about 3 000 lines): never read whole. Count and sample with `jq`
   when present, else `grep`: operations (`operationId`), operations without a 4xx response,
   security schemes and where tokens travel (`"in": "query"`), arrays without `maxItems`,
   `default`-only responses. Report counts with one representative location each.
3. **Contract checks** against the expert: unique `operationId` and summaries; typed error
   responses (4xx, problem details) and not only `default`; security on every operation and no
   token in a query string; precise status codes and the safe and idempotent methods used as
   such; pagination and its bound; schemas (`nullable` only in 3.0, discriminators,
   `additionalProperties`, bounded arrays); deprecation signalled; examples valid. Judge a 3.0
   document by 3.0, a 2.0 document by 2.0 (`securityDefinitions`, `definitions`, `host` and
   `basePath`): never report 3.1-only features missing from it.
4. **Generated documents:** the fix location is the source annotation or the generator config
   the target names, not the generated file; say which file regenerates it.
5. **Linter**, when installed and a config exists: run it read-only on each document and fold
   its errors in, deduplicated against your own findings.

## Report

```text
summary: <one line — documents found (version, generated or hand-written, size), linter run or missing, worst severity>

findings:
1. <severity> · <file>:<line or JSON pointer> · <what> · fix: <exact change, at the source annotation for a generated document> · confidence: <high|medium|low>
…

knowledge_delta:            # optional — only facts verified during this audit and absent from expert-api
{"topic": "api", "skill": "expert-api", "entries": [{"claim": "...", "status": "verified|reported", "source": "<url or exp: command>", "checked": "YYYY-MM-DD", "scope": "general|project"}], "unverified": []}
```

No finding without a location. Gateway or runtime behaviour you cannot read from the tree goes in
the summary as "not verifiable from the tree". Zero findings is a valid result; say what was
checked.
