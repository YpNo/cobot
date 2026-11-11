# Google Cloud remote MCP servers (decision 28, amended 2026-11-11)

Proven on gcp-platform on 2026-11-11: the owner registered `gcp-logging` and `gcp-gke`, and
read-only calls answered from the main thread. cobot ships no server and no credentials; the
owner registers each one, as for Stitch (decision 27).

## What is established

- [verified 2026-11-11 · src: exp: curl -X POST https://<service>.googleapis.com/mcp tools/list, no credentials] `tools/list` answers without credentials and annotates every read tool with `readOnlyHint`. `logging` (6 tools), `monitoring` and `cloudresourcemanager` expose reads only; `container` (19 reads, 8 writes), `run`, `bigquery`, `compute`, `sqladmin`, `firestore`, `pubsub` and `iam` also expose writes. `storage`, `secretmanager`, `artifactregistry` and `cloudbuild` have no server at that URL form.
- [verified 2026-11-11 · src: exp: curl https://logging.googleapis.com/.well-known/oauth-protected-resource/mcp] The servers ask for broad OAuth scopes: `logging.admin` for Logging, `container` for GKE. The token can write, so read-only has to come from IAM or the gate, never from the scope.
- [verified 2026-11-10 · src: https://docs.cloud.google.com/mcp/enable-disable-mcp-servers] Enabling the product API (`gcloud services enable <service>.googleapis.com`) is enough; there is no separate MCP switch.
- [verified 2026-11-10 · src: https://docs.cloud.google.com/mcp/set-up-authentication-mcp-servers] Calling a tool needs `roles/mcp.toolUser` (`mcp.tools.call`) plus the service's own roles. For an app on your machine, the OAuth client type is **Desktop**. Google supports no Dynamic Client Registration.
- [verified 2026-11-10 · src: https://docs.cloud.google.com/mcp/prevent-read-write-tool-use] A server-side read-only guard is an IAM deny policy on `mcp.googleapis.com/tools.call` with `api.getAttribute('mcp.googleapis.com/tool.isReadOnly', false) == false`. `tools/list` still shows the write tools; calling one fails.
- [verified 2026-11-11 · src: exp: gcloud iam policies create on a project with no organisation, read back from its audit log] Creating that deny policy on a personal project fails. `roles/iam.denyAdmin` "is not supported for this resource" on a project, and Owner lacks `iam.googleapis.com/denypolicies.create`. A deny policy needs an organisation or a folder.
- [verified 2026-11-11 · src: exp: claude mcp add 2.1.311, then /mcp, in gcp-platform] `--client-id`, `--client-secret` (prompted) and `--callback-port` work with the header `x-goog-user-project: <project>`. `-s local` binds the server to the folder `claude mcp add` ran in. The desktop app's Reconnect does not start the OAuth flow; the CLI's `/mcp` → Authenticate does.
- [verified 2026-11-11 · src: exp: claude -p in gcp-platform, sessions 298e1988, e4ca3deb, 67e5d579] `list_log_entries` and `list_clusters` answer from the main thread with no gate prompt. `cobot:consultant` has no MCP tools, so `/cobot:consult gcp` reads files and the main thread queries live data.
- [reported 2026-11-11 · src: https://developers.google.com/identity/protocols/oauth2#expiration] With a consent screen in Testing for External users, refresh tokens expire after 7 days.

## Setup, by the owner

1. Enable the product APIs, then grant yourself `roles/mcp.toolUser` on the project:
   `gcloud projects add-iam-policy-binding <project> --member="user:<you>" --role="roles/mcp.toolUser"`.
2. Server-side read-only, when the project has an organisation or a folder: create the deny
   policy above, with `deniedPrincipals: ["principalSet://goog/public:all"]`, using
   `gcloud iam policies create mcp-read-only --attachment-point=cloudresourcemanager.googleapis.com/projects/<project> --kind=denypolicies --policy-file=<file>`.
   Without an organisation, sign in with a second Google identity that holds only
   `roles/viewer` and `roles/mcp.toolUser`. Otherwise the gate's refusals are the only guard.
3. OAuth client: Google Auth Platform → Clients → Desktop app. On the consent screen, choose
   External and Testing, and add yourself as a test user.
4. Register each server as `gcp-<service>`, from inside the repository:
   `claude mcp add --transport http --client-id <id> --client-secret --callback-port 8765 -H "x-goog-user-project: <project>" -s local gcp-logging https://logging.googleapis.com/mcp`.
5. Sign in from the CLI: `/mcp`, pick the server, Authenticate. When Claude Code runs on a
   remote host, forward the callback port from the machine with the browser first:
   `ssh -N -L 8765:localhost:8765 <host>`.

## How the cobot treats them

- **Named `gcp-*`.** The default layer refuses write tools by their first verb (`create_`,
  `update_`, `delete_`, `apply_`, `deploy_`, `cancel_`, `set_`, `publish` and the rest, with
  `execute_sql` matched exactly). An owner `allow mcp__gcp-<server>__*` cannot lift that. Reads
  stay silent; any other tool that is not a read asks.
- **Any other name.** Every tool that is not a read asks. Writes are not refused.
- **Live data stays in the main thread.** Logs, events, cluster state and query results come
  from the main thread, never from a consultant, which audits files.
- **Changes go elsewhere.** Writes to Google Cloud go through Terraform plans or `gcloud`
  commands, proposed under the gate, never through MCP.
- **Tokens stay with Claude Code.** They live in its credential store and are never pasted,
  logged or written to `.agent/`.
