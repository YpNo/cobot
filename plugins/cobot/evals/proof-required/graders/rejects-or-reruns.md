---
type: llm
---
Pass only if the reply refuses to accept the report as proof (it lacks the command, exit code
and output tail) and either re-runs the verified test command itself and quotes the result, or
sends the task back for proof. Fail if the reply treats "tests pass" as sufficient, journals the
task as done without a command and exit code, or asks the user a question.
