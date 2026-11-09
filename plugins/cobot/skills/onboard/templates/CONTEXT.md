# {{NAME}} — context

profile: {{PROFILE}}          # spike | script | cli | library | service | infra
forge: github                  # github | gitlab | gitea | other — where CI runs; ship reads it
goal: <one line: what this repository is for>
owner: <who decides> · <visibility> · <license>
governance: none               # path to the project's principles, #heading-slug for one section; every spec checks against it

## Stack

- <language and version> · <framework> · <package manager>
- <test runner> · <linter> · <formatter> · <type checker>

## Environment

- <runtime versions that matter, how they are installed>
- <anything odd about this machine or CI>

## Verified commands

| purpose | command | result | verified |
|---|---|---|---|
| unit tests | `<command>` | exit 0 | {{DATE}} |
| lint | `<command>` | exit 0 | {{DATE}} |
| build | `<command>` | exit 0 | {{DATE}} |

## Constraints

- <what must never happen here>
- <conventions the owner insists on>

## Applies / does not apply

- applies: <parts of the owner's standards that fit this repo>
- does not apply: <parts that do not, with the reason>

## Shape

- <≤ 20 lines: the main components and how they talk>
