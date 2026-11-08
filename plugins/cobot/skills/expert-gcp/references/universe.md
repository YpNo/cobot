# expert-gcp — Google Cloud universes

A universe other than the public `googleapis.com` one (Google Cloud Dedicated, a partner
sovereign cloud such as S3NS in France) changes three things. Resource schemas, service names,
OAuth scopes and the Terraform resources are the same. This file supersedes the legacy
`gcd-universe` skill; every claim carries its status, and the owner's field experience that no
Google page states is marked `assumed`.

| | Public universe | Any universe | Example |
|---|---|---|---|
| API endpoints | `<service>.googleapis.com` | `<service>.<universe_domain>` | `<service>.s3nsapis.fr` |
| Project IDs | `my-project` | `<prefix>:my-project` | `s3ns:my-project`, `eu0:my-project` |
| Service-agent emails | `…@<agent>.iam.gserviceaccount.com` | `…@<agent>.<prefix>-system.iam.gserviceaccount.com` | |

Two independent values: the **universe domain** (an API host suffix) and the **universe
prefix** (a project-ID and service-agent qualifier). Neither is derivable from the other; a
shared stem is a coincidence. Configure both, never compute one from the other, and test with a
pair that shares no stem (`example-apis.test` with `zzz`) so an accidental derivation fails.

## Rule 1 — endpoints belong to whoever is the client

Terraform module: the caller sets `universe_domain` on `google` and `google-beta`; the module
configures no provider and inherits it; a reusable module needs no change for endpoints and
never hardcodes a host. Client code: hand the universe domain to the library
(`option.WithUniverseDomain`, `GOOGLE_CLOUD_UNIVERSE_DOMAIN`, the credentials file's
`universe_domain` field) and let it derive each endpoint. Precedence everywhere: explicit
setting, then the environment variable, then `googleapis.com`. An explicit endpoint override
(`WithEndpoint`, `api_endpoint=`, `setRootUrl`) silently beats the universe and keeps talking to
the public one; audit every one. A universe setting also makes the library refuse to send a
token whose credential belongs to another universe; a raw endpoint override has no such check,
which is the security argument for the setting over the override.

## Rule 2 — never hardcode a service-agent email

Read `google_project_service_identity.member` (google-beta), which is computed for the active
universe and creates the agent, fixing "member does not exist" races. Fallback when a service
has no identity resource: `service-<number>@<agent>.<INFIX>iam.gserviceaccount.com`, `INFIX`
empty in the public universe and `<prefix>-system.` in a universe; number-based agents take the
infix only; project-ID-based agents (App Engine) strip the `<prefix>:` first. Often not a code
problem: when the identity is user-supplied configuration, users already write universe-correct
values.

## Rule 3 — prefixed project IDs break identifier parsing

`s3ns:my-project:my_dataset` has three colon-separated parts; code that splits on `:` and
expects two rejects it. Domain-scoped project IDs (`example.com:my-project`) have had this
shape in public GCP for years, so the fix is a pre-existing bug fix, needs no universe
configuration and lands on its own merit: split on the **last** colon (`strings.LastIndex`),
guard both ends, prefer `/`-based parsing where the API offers it (`projects/<id>/datasets/<d>`
keeps a colon-bearing ID intact), and leave project-number-derived identifiers alone. Table-test
every parser with the plain, domain-scoped and universe-qualified forms plus the rejection
cases (no colon, empty project, empty second part, bare `:`). Reach for the configured prefix
only where the ambiguity is unresolvable otherwise; never strip a prefix that was not
configured.

## Rule 4 — what does not change (do not "fix" these)

Service names (`container.googleapis.com` in `google_project_service`), full resource and
Cloud Asset names (`//compute.googleapis.com/projects/…`), OAuth scope URLs
(`https://www.googleapis.com/auth/…`), resource and attribute schemas, self-links echoed from
API responses (echo what the server sent). Classify every `googleapis.com` hit before touching
it: endpoint (fix), service name (leave), scope (leave), constructed agent email (fix by rule 2).

## Rule 5 — some services do not exist in a universe

Gate API enablement and service identities per universe: Fabric's `unavailable_services` and
`unavailable_service_identities` lists; an operator's include and exclude filter in Kubernetes.

## Audit greps

```bash
grep -rn 'gserviceaccount\.com' --include='*.tf' . | grep -v '.terraform/'          # rule 2
grep -rn 'googleapis\.com' --include='*.tf' . | grep -v '.terraform/'               # classify (rule 4)
grep -rn 'provider "google' --include='*.tf' . | grep -v examples/                  # none inside a module
grep -rnE 'WithEndpoint|setRootUrl|setServicePath|api_endpoint|base_?url' --include='*.go' --include='*.java' --include='*.py' .
grep -rnE 'Split\(.*"[:]"' --include='*.go' --include='*.java' --include='*.py' .    # rule 3
```

Enforce with a static check that fails when an endpoint override reaches a `googleapis.com`
literal without the universe-aware helper (resolve identifiers to their assignment, or the
`fmt.Sprintf` form slips through); verify the check by reverting a fixed site. Tests: assert
the outbound `Host`, assert the public-universe path is byte-for-byte unchanged when nothing is
set and when `googleapis.com` is set explicitly, test two universes rather than one. Expect
"did you test in a real universe?" as the first review question.

## Provider and gcloud

```hcl
provider "google"      { project = "acme:my-project", universe_domain = "acme.example" }
provider "google-beta" { project = "acme:my-project", universe_domain = "acme.example" }
```

`gcloud config set core/universe_domain <domain>` switches the CLI; the project ID passed to
the provider is already the prefixed form.

- [verified 2026-11-08 · src: https://raw.githubusercontent.com/hashicorp/terraform-provider-google/main/website/docs/guides/provider_reference.html.markdown] `universe_domain` is a provider argument ("Specify the GCP universe to deploy in"); the 8.x documentation states no default and no credential check for it.
- [verified 2026-11-08 · src: https://docs.cloud.google.com/sdk/gcloud/reference/config/set] gcloud has a `core/universe_domain` property: "Sets the domain of the universe to use for API requests".
- [verified 2026-11-08 · src: https://raw.githubusercontent.com/GoogleCloudPlatform/cloud-foundation-fabric/master/modules/project/variables.tf] Fabric's `universe` variable is `{ prefix, forced_jit_service_identities, unavailable_services, unavailable_service_identities }`: "The prefix will be prepended to the project id".
- [verified 2026-11-08 · src: https://raw.githubusercontent.com/GoogleCloudPlatform/cloud-foundation-fabric/master/modules/project/main.tf] Fabric builds the project ID as `${prefix}:${name}` unless the name already contains a colon.
- [verified 2026-11-08 · src: https://raw.githubusercontent.com/GoogleCloudPlatform/cloud-foundation-fabric/master/modules/project/service-agents.tf] Fabric's agent infix is `"${prefix}-system."`; App Engine strips the project prefix with `trimprefix`; in a universe cloudservices becomes `NUMBER@cloudservices.<prefix>-system.iam.gserviceaccount.com` and a partner KMS agent `service-NUMBER@gcp-sa-ekms.<infix>iam.gserviceaccount.com` appears.
- [verified 2026-11-08 · src: https://raw.githubusercontent.com/googleapis/google-cloud-go/main/auth/internal/internal.go] Go: `GOOGLE_CLOUD_UNIVERSE_DOMAIN` is the environment variable, `googleapis.com` the default; `option.WithUniverseDomain` sets it per client; on GCE the metadata server supplies it.
- [verified 2026-11-08 · src: https://raw.githubusercontent.com/golang/oauth2/master/google/default.go] golang.org/x/oauth2: an explicit `CredentialsParams.UniverseDomain` beats the credentials file's `universe_domain`; "Authorized user credentials are only supported in the googleapis.com universe".
- [verified 2026-11-08 · src: https://sources.debian.org/src/python-google-api-core/2.23.0-1/google/api_core/universe.py] Python api-core: precedence client option, environment variable, default; `UniverseMismatchError` when the configured universe differs from the credentials' universe.
- [verified 2026-11-08 · src: https://raw.githubusercontent.com/googleapis/google-auth-library-python/main/google/oauth2/service_account.py] google-auth Python: a non-default universe forces self-signed JWT access tokens, rejects domain-wide delegation and forces the IAM endpoint for ID tokens.
- [reported 2026-11-08 · src: https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/installing_on_google_cloud/installing-gcp-dedicated] Red Hat's Google Cloud Dedicated guide (search snippet, page returns 403) shows domain-scoped project IDs such as `eu0:my-project`, a different service-account email domain, and endpoint overrides targeting `googleapis.com` as incompatible.
- [reported 2026-11-08 · src: https://cloud.google.com/products/dedicated] Google Cloud Dedicated is a partner-operated standalone universe isolated from the public cloud; S3NS (Thales) operates one in France.
- [assumed 2026-11-08 · src: legacy gcd-universe skill, owner's experience on `google.golang.org/api` v0.28x] No fetched Google page states the endpoint form `<service>.<universe_domain>` or the `<prefix>:project` convention as such; Fabric's code and the Red Hat snippet show both. Go client details (endpoint templates in `internal/cba.go`, mTLS skipped outside the default universe, DirectPath not gated on the universe in Go unlike Java) and the Java connector notes (DirectPath disabled by hand, trust store per universe, universe in client cache keys) come from the legacy skill and are to be re-read in the source before they drive a change.
