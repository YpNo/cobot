# Consult: homeassistant

Paths below start at the plugin root your prompt names.

Read-only. Change nothing, commit nothing, run nothing the repository supplies: no
`hass --script check_config` (it imports the integrations), no `pip install` or `uv pip install`
of a manifest's requirements, no `hass-cli` (a live instance is the main thread's). Read
`skills/expert-homeassistant/SKILL.md` and its references first; they are the baseline. Never
read `secrets.yaml` or anything under `.storage/` (the gate refuses it): `git ls-files` says
whether they are tracked. Network use is limited to documentation fetches.

## Procedure

1. **Inventory.** Run these in place, one call:

   ```bash
   git ls-files ./custom_components ./hacs.json ./.HA_VERSION ./blueprints ./automations.yaml ./configuration.yaml ./secrets.yaml ./.storage ./.github/workflows
   ```

   A custom integration (`custom_components/<domain>/manifest.json`), a configuration
   directory (`configuration.yaml`, `.HA_VERSION`) or blueprints; none of them → say so in one
   line and stop.
2. **Manifest.** For each `custom_components/*/manifest.json` (`jq . ./custom_components/*/manifest.json`):
   the keys hassfest requires and `version` (AwesomeVersion), `iot_class` and `integration_type`
   from their value lists, `config_flow: true` with a `config_flow.py` beside it, `requirements`
   that pin with `==` a package Home Assistant ships or list one of its own dependencies,
   `issue_tracker` and `codeowners` for HACS.
3. **Integration code.** `translations/en.json` present and no `strings.json`; blocking I/O
   (`requests`, `time.sleep`, `open`) inside `async def` without `async_add_executor_job`;
   `has_entity_name` on entities; runtime objects in `entry.runtime_data` rather than
   `hass.data`; a `DataUpdateCoordinator` that raises `UpdateFailed` and
   `ConfigEntryAuthFailed` rather than swallowing errors.
4. **HACS.** `hacs.json` at the root with `name`; one integration under `custom_components/`;
   releases rather than bare tags when the README says HACS.
5. **Configuration.** Credentials in YAML through `!secret` or `!env_var`, never inline;
   a tracked `secrets.yaml` or `.storage/` path (from step 1) → HIGH; packages with duplicate
   file names under `!include_dir_named`; automations without `id` (no traces, no UI rename),
   `mode` values outside single, restart, queued, parallel; blueprints without `name` and
   `domain` or with a `min_version` that is not major.minor.patch.
6. **CI.** A workflow running `home-assistant/actions/hassfest` and `hacs/action` (category
   `integration`), each pinned by commit SHA, not a branch ref; the Python job per `lang-python`.

## Report

```text
scope: <files read, of how many in the inventory; integration, configuration or both>

findings:
1. <HIGH|MEDIUM|LOW> · <file>:<line> · <what> · fix: <the change>
…

not covered: <what needs a live instance or running the integration, for the main thread>

knowledge_delta (optional, JSON, only facts verified during the audit and absent from the references):
{"topic": "homeassistant", "entries": [{"claim": "...", "status": "verified|reported", "source": "<url or exp: command>", "checked": "YYYY-MM-DD", "scope": "general|project"}], "unverified": []}
```

Never report a finding you did not anchor to a file and line; never fix anything. The
orchestrator decides what becomes a task.
