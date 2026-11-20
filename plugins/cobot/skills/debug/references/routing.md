# Debug routing — symptom to expert skill and reads

The lead picks a domain from the evidence, gives each investigator the one skill on its row,
and runs a `Needs:` command only when it is a read listed here. `Read` means the investigator's
read list covers it (silent); `asks` means the gate asks the lead at the prompt. Anything not
listed is printed for the owner.

| signal | skill | reads |
|---|---|---|
| red CI run, workflow error | `expert-gha`, `expert-gitlab-ci` | `gh run view --log-failed`, `gh run list`, `glab ci view`, `glab ci trace` |
| compile, test or runtime error in a language | `lang-*` (the repository's) | the verified test command (asks), `git log -S <text> <a>..<b>`, `git show`, `git blame` |
| image will not build or start | `expert-containers` | `docker ps`, `docker inspect` (asks), `docker logs --tail 50` (asks) |
| pod Pending, CrashLoopBackOff, OOMKilled | `expert-kubernetes` | `kubectl describe`, `kubectl logs --previous --tail 50`, `kubectl get events`, `kubectl get <kind> -o wide` |
| 503, mTLS or RBAC denial in the mesh | `expert-service-mesh` | `istioctl analyze`, `istioctl proxy-status`, `istioctl proxy-config`, `istioctl x describe` (asks) |
| permission denied, quota, API not enabled on GCP | `expert-gcp` | `gcloud logging read --limit 50`, `gcloud … get-iam-policy`, `gcloud services list` |
| plan drift, state lock | `lang-terraform` | `terraform providers`, `terraform state list` (asks); `terraform plan` is printed for the owner |
| regression after a dependency bump | `lang-*` (the repository's) | `git diff <a>..<b> -- <lockfile>`, `cobot-deps check`, the advisory pages |
| unknown domain | `lang-fallback` | the read list only; propose `/cobot:learn` after the incident |

On this path, never `git bisect` (it checks out commits: use `git log -S` over a range), never
`terraform apply`, `force-unlock` or `state` surgery, never a restart, delete, scale or rollout
to "see what happens", never an output format that prints values (`-o yaml`, `-o json`) without
the owner's word at the prompt.

When the owner has registered Google's remote Cloud MCP servers, the lead may use their read
tools from the main thread (expert-gcp); a probe does not.
