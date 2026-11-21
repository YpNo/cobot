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
tooling: `lang-python`. Versions and dated facts: `references/versions.md`; the CI job:
`references/ci.md`; the REST and WebSocket APIs, tokens and `hass-cli`: `references/api.md`;
ZHA and the device, entity, area, floor and label registries: `references/registries.md`.
Zigbee radio and protocol facts beyond ZHA as an integration belong to a later
`expert-iot-protocols`; until it exists, say so and propose `/cobot:learn`.

## Custom integrations

`custom_components/<domain>/` with `manifest.json`, `translations/`, and `config_flow.py` when
`config_flow` is true; validated by hassfest and, for HACS, the HACS action (`references/ci.md`).

- [verified 2026-11-21 · src: https://github.com/home-assistant/core/blob/2026.11.2/script/hassfest/manifest.py; https://github.com/home-assistant/developers.home-assistant/blob/master/docs/creating_integration_manifest.md] The hassfest manifest schema requires `domain`, `name`, `codeowners` (list) and `documentation` (URL); a custom integration without `version` fails with "No 'version' key in the manifest file."; the version must parse with AwesomeVersion (SemVer or CalVer); `issue_tracker` is an optional URL; `config_flow` is a bool; `dependencies`, `after_dependencies`, `requirements` and `loggers` are string lists.
- [verified 2026-11-21 · src: https://github.com/home-assistant/developers.home-assistant/blob/master/docs/creating_integration_manifest.md] `iot_class` takes one of assumed_state, cloud_polling, cloud_push, local_polling, local_push or calculated.
- [verified 2026-11-21 · src: https://github.com/home-assistant/developers.home-assistant/blob/master/docs/creating_integration_manifest.md] `integration_type` takes device, entity, hardware, helper, hub, service, system or virtual; for custom and YAML integrations it defaults to `hub` when omitted, and the docs advise setting it explicitly (a single device or service per config entry is `device` or `service`, not `hub`).
- [verified 2026-11-21 · src: https://github.com/home-assistant/core/blob/2026.11.2/script/hassfest/requirements.py] hassfest requires `==` pins only for core integrations; a custom integration must not list a package that Home Assistant itself depends on, and must not pin exactly (`==`) a package HA ships, using a minimum (`>=`) instead.
- [verified 2026-11-21 · src: https://github.com/home-assistant/developers.home-assistant/blob/master/docs/creating_integration_manifest.md] Custom integrations may list both built-in and custom integrations in `after_dependencies` (built-in ones only built-in); `loggers` lists the names the requirements pass to logging.getLogger.
- [verified 2026-11-21 · src: https://hacs.xyz/docs/publish/integration/; https://hacs.xyz/docs/publish/start/] HACS integration repos hold exactly one integration under custom_components/<domain>/ (or the root with `content_in_root`); the manifest must have domain, documentation, issue_tracker, codeowners, name and version; hacs.json sits in the repo root with `name` required and optional content_in_root, zip_release (needs filename), filename, hide_default_branch, country, homeassistant (minimum HA version), hacs, persistent_directory; versions come from GitHub releases, not bare tags.
- [verified 2026-11-21 · src: https://github.com/home-assistant/developers.home-assistant/blob/master/docs/internationalization/custom_integration.md] Custom integrations must not use strings.json (a Core build-time feature, as are `[%key:...%]` placeholders); they ship translations/<BCP47 code>.json files, at minimum translations/en.json with full flat text, and hassfest validates them.
- [verified 2026-11-21 · src: https://github.com/home-assistant/developers.home-assistant/blob/master/docs/core/integration-quality-scale/index.md; https://github.com/home-assistant/core/blob/2026.11.2/script/hassfest/quality_scale.py] The quality scale has four scaled tiers (bronze, silver, gold, platinum; each includes the tiers below) and four special tiers (No score, Internal, Legacy, Custom); quality_scale.yaml lists `rules:` as `done` or as `status: exempt` with a `comment`; hassfest's quality-scale check returns early for non-core integrations, so a custom integration sits in the Custom tier and the file is optional.
- [verified 2026-11-21 · src: https://github.com/home-assistant/developers.home-assistant/blob/master/docs/core/integration-quality-scale/rules/runtime-data.md; https://github.com/home-assistant/developers.home-assistant/blob/master/docs/integration_fetching_data.md] Store runtime objects in a typed `entry.runtime_data` (alias `type MyConfigEntry = ConfigEntry[MyClient]`, a bronze rule); a DataUpdateCoordinator implements `_async_update_data` (optional `_async_setup`), `async_config_entry_first_refresh()` raises ConfigEntryNotReady on failure, UpdateFailed marks a failed poll (`retry_after` honours backoff), ConfigEntryAuthFailed starts reauth, and `always_update=False` skips unchanged data.
- [verified 2026-11-21 · src: https://github.com/home-assistant/developers.home-assistant/blob/master/docs/core/entity.md; https://github.com/home-assistant/developers.home-assistant/blob/master/docs/asyncio_blocking_operations.md] `has_entity_name = True` is mandatory for new integrations: the entity name names only the data point (None for the device's main feature), friendly_name becomes "<device name> <entity name>", and names should be translated via translation_key; blocking I/O must never run in the event loop (use `await hass.async_add_executor_job`), and HA detects more such calls since 2024.7.0.

## Configuration

- [verified 2026-11-21 · src: https://www.home-assistant.io/docs/configuration/packages/] Packages are declared under `homeassistant:` then `packages:`. `packages: !include_dir_named packages` uses each filename as the package name, so filenames must be unique even across subfolders. Integrations keyed by entity ID need keys unique across packages and the main configuration. Other non-platform integrations merge only if their non-list keys are defined once. `auth_providers` must stay in configuration.yaml.
- [verified 2026-11-21 · src: https://www.home-assistant.io/docs/configuration/splitting_configuration/] `!include` goes where YAML expects a value. `!include_dir_list` returns a list with one entry per file, ordered alphanumerically by filename. `!include_dir_named` returns a dict mapping filenames to file contents. `!include_dir_merge_list` merges every file's list into one list. `!include_dir_merge_named` merges every file's dict into one dict.
- [verified 2026-11-21 · src: https://www.home-assistant.io/docs/configuration/secrets/] `!secret` lookup: first the secrets.yaml in the same folder as the referencing YAML file, then parent folders, stopping at the folder that holds the main configuration.yaml. Debug logging shows where a secret was loaded from, never its value. Secrets used in automations and scripts are still visible to admins in the YAML and trace viewers.
- [verified 2026-11-21 · src: https://www.home-assistant.io/docs/configuration/yaml/] `!env_var NAME` reads a process environment variable, and an optional second word is the fallback when the variable is unset. The docs recommend `!include` instead for regular users.
- [verified 2026-11-21 · src: https://github.com/home-assistant/core/blob/dev/homeassistant/config.py ; https://github.com/home-assistant/core/blob/dev/homeassistant/helpers/storage.py ; https://github.com/home-assistant/core/blob/dev/homeassistant/auth/auth_store.py ; https://github.com/home-assistant/core/blob/dev/homeassistant/config_entries.py ; https://www.home-assistant.io/docs/authentication/providers/] Core constants: VERSION_FILE is `.HA_VERSION` and STORAGE_DIR is `.storage`, both in the config directory. The auth store's storage key is `auth` and config entries use `core.config_entries`, i.e. .storage/auth and .storage/core.config_entries. User details, with salted password hashes, live in .storage.
- [verified 2026-11-21 · src: https://www.home-assistant.io/docs/tools/check_config/ ; https://github.com/home-assistant/core/blob/dev/homeassistant/helpers/check_config.py ; https://github.com/home-assistant/core/blob/dev/homeassistant/scripts/check_config.py] `hass --script check_config` takes `-c/--config` (config directory), `-i/--info`, `-f/--files`, `-s/--secrets` (shows secret values), `--json` and `--fail-on-warnings` (non-zero exit on warnings). The script patches only YAML loading. It goes through async_check_ha_config_file, which resolves each integration with its requirements, imports the integration and its `config` platform, and runs CONFIG_SCHEMA, PLATFORM_SCHEMA and async_validate_config. So it executes integration code: it does not just parse YAML.
- [verified 2026-11-21 · src: https://www.home-assistant.io/docs/configuration/troubleshooting/ ; https://contributors.home-assistant.io/core/internals/rest-api/] UI check: Settings > Tools > YAML > Check configuration. API check: POST /api/config/core/check_config (admin only) returns `result` (valid or invalid) plus `errors` and `warnings` (text or null).
- [verified 2026-11-21 · src: https://www.home-assistant.io/docs/automation/yaml/ ; https://www.home-assistant.io/docs/automation/modes/] An automation `id` is optional in YAML but needed to rename the automation in the UI and to store traces. The editor needs it and generates it. The UI writes automations.yaml, included via `automation: !include automations.yaml`, and that file should not be edited by hand. `mode` is single (the default), restart, queued or parallel. `max` defaults to 10 with a minimum of 2. `max_exceeded` takes a log level, default warning, and `silent` suppresses it.
- [verified 2026-11-21 · src: https://www.home-assistant.io/docs/blueprint/schema/ ; https://www.home-assistant.io/docs/blueprint/tutorial/] A blueprint needs `blueprint:` with `name` and `domain` (automation, script or template). `input` is optional: a dict of inputs or sections, each with optional name, description, default and selector. `min_version` must be a full major.minor.patch string. Automation blueprints live in <config>/blueprints/automation/, subfolders allowed.

## A live instance under the gate

- The token comes from the environment: `HASS_SERVER` and `HASS_TOKEN` set in the owner's shell
  profile or from a secret manager. `--token`, `--supervisor-token` and `--password` on the
  command line are refused, and so is setting a token variable in a command; expanding one asks
  (a read-only agent is refused).
- `hass-cli` reads are silent in the main thread only, with the server from `HASS_SERVER`;
  `-s`/`--server`, `-x`/`--insecure` and `--debug` (it prints the request headers) ask. Every
  write verb asks, and the whole `ha` (Supervisor) group asks. No read-only agent has
  `hass-cli`: an investigator or a consultant names the command and the main thread runs it.
- In a configuration repository, a read-only agent excludes the secrets from recursive reads and
  history: `grep -r --exclude=secrets.yaml --exclude-dir=.storage`, `rg -g '!secrets.yaml'
  -g '!.storage'`, `git log -p -- . ':!*secrets.yaml' ':!*.storage/*'`; the gate refuses the
  unexcluded forms.
- A long-lived token acts with its user's full rights (`references/api.md`): ask for a token of a
  non-admin user when the task only reads.

## Do not

- Do not read `secrets.yaml` or `.storage/`; report a tracked `secrets.yaml` from
  `git ls-files` alone. The gate refuses a read-only agent that names them.
- Do not run an integration's code to check it (`hass --script check_config`, `pip install` of
  its requirements) in a repository you did not write: `check_config` imports the integrations.
- Do not pin a custom integration's requirement with `==` on a package Home Assistant ships, and
  do not ship `strings.json` in a custom integration.
