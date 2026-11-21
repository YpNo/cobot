---
name: expert-homeassistant
description: >-
  Home Assistant: custom integrations (manifest.json, config flow, quality scale, hassfest,
  HACS), configuration (packages, !include, !secret, blueprints, automations), the REST and
  WebSocket APIs and long-lived tokens, hass-cli under the gate, ZHA and the registries. Use on
  custom_components/, hacs.json, a configuration directory, or an API client.
paths:
  - "custom_components/**"
  - "**/hacs.json"
  - "**/.HA_VERSION"
  - "blueprints/**"
  - "**/automations.yaml"
user-invocable: false
---

# expert-homeassistant

CONTEXT.md and the governance file override it; a project's Constraints win (a repository that
keeps a live instance's values out of the transcript keeps them out). Python idiom, tests and
tooling: `lang-python`. Versions and dated facts: `references/versions.md`; the CI jobs:
`references/ci.md`. Zigbee radio and protocol facts beyond ZHA as an integration belong to a
later `expert-iot-protocols`; until it exists, say so and propose `/cobot:learn`.

## Do not

- Do not read `secrets.yaml` or `.storage/`; report a tracked `secrets.yaml` from
  `git ls-files` alone.
- Do not run an integration's code to check it (`hass --script check_config`, `pip install` of
  its requirements) in a repository you did not write.
