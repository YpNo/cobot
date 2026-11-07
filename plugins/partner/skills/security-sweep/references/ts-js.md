# TypeScript / JavaScript rule pack

Loads for `.ts`, `.tsx`, `.js` and `.jsx` files and applies `core.md` through JS/TS idioms, Node and browser.
Rule ids are `JS-<CAT>-<nn>`.

## Injection & execution

- **JS-EXEC-01** `child_process.exec`/`execSync` with an interpolated argument (these spawn a shell). `execFile` or
  `spawn` with an argument array is the fix, unless the binary path itself is input.
- **JS-EXEC-02** `eval`, `new Function(str)`, `setTimeout("string")` or `vm.runInNewContext` on non-literal data.
  `vm` is not a security sandbox; flag any use as an isolation boundary.
- **JS-SQL-01** Query built by template literal or `+`. Use `db.query('... WHERE id = $1', [id])`. Knex `.raw()`,
  Sequelize `sequelize.query`, TypeORM/Prisma raw helpers (`$queryRawUnsafe`) with interpolation are the same bug.
- **JS-NOSQL-01** MongoDB query built from a request object without type checks: `{ password: req.body.pw }` where
  `pw` is `{$ne: null}` is auth bypass. Validate that operands are primitives.
- **JS-PATH-01** `fs.readFile`/`res.sendFile`/`path.join` with request input and no `path.resolve` plus containment
  check. `express.static` is safe; manual joins are not.
- **JS-PROTO-01** Prototype pollution: recursive merge/clone/set-by-path over untrusted objects without rejecting
  `__proto__`, `constructor`, `prototype`. Check `lodash.merge`, `deepmerge`, custom helpers, query-string parsers.

## XSS & DOM

- **JS-XSS-01** `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write` with non-constant data.
- **JS-XSS-02** React `dangerouslySetInnerHTML`; Vue `v-html`; Angular `bypassSecurityTrustHtml`/`TrustedHtml`. Each
  disables the framework's escaping and needs DOMPurify on the input, verified.
- **JS-XSS-03** `href`/`src` set from input without a scheme allow-list: `javascript:` and `data:` URLs.
- **JS-XSS-04** SSR interpolating into a `<script>` block or inline event handler; HTML escaping does not cover JS.
- **JS-XSS-05** `postMessage` handler with no `event.origin` check, or `postMessage(msg, '*')` carrying sensitive data.

## Auth, sessions, tokens

- **JS-AUTH-01** `jwt.verify` with `algorithms` unspecified (allows `none` and HS/RS confusion in older
  `jsonwebtoken`), or `jwt.decode` used where `verify` was meant: `decode` checks nothing.
- **JS-AUTH-02** Token in `localStorage`/`sessionStorage`: reachable by any XSS. An `httpOnly` cookie is safer.
- **JS-AUTH-03** Cookie without `httpOnly`, `secure`, `sameSite`. Express session with a hardcoded `secret`, or
  `resave`/`saveUninitialized` defaults creating sessions for anonymous users.
- **JS-AUTH-04** Route registered without the auth middleware in a per-route scheme, or ordered before the guard.
- **JS-AUTH-05** `bcrypt` cost below 10, or a password hashed with `crypto.createHash`.

## Crypto & secrets

- **JS-CRYPTO-01** `Math.random()` for a token, id or salt. Use `crypto.randomBytes`/`randomUUID`/`getRandomValues`.
- **JS-CRYPTO-02** `crypto.createHash('md5'|'sha1')` on a security path; `createCipher` (deprecated, derives a key
  badly) instead of `createCipheriv`.
- **JS-CRYPTO-03** Token compared with `===`. Use `crypto.timingSafeEqual` (throws on length mismatch; hash first).
- **JS-CRYPTO-04** `NODE_TLS_REJECT_UNAUTHORIZED=0`, or `rejectUnauthorized: false` in an https/axios/node-fetch agent.
- **JS-SEC-01** Secret in source, in a committed `.env`, or in a `NEXT_PUBLIC_*`/`VITE_*`/`REACT_APP_*` variable:
  those are compiled into the client bundle. A secret behind such a prefix is CRITICAL.
- **JS-SEC-02** Secret referenced in client-side code at all: check the import graph from the browser entrypoint.

## Node runtime & Express

- **JS-NODE-01** No body size limit: `express.json()` defaults to 100kb but `bodyParser` with a large or absent
  `limit` is a DoS vector. Also check upload caps (`multer` limits).
- **JS-NODE-02** `helmet` absent on an Express app or CSP unset; no HSTS, `X-Content-Type-Options`, frame options.
- **JS-NODE-03** CORS with `origin: true` (reflects any origin) or `origin: '*'` alongside `credentials: true`.
- **JS-NODE-04** Error handler returning `err.stack` or `err.message` to the client; default Express handler in prod.
- **JS-NODE-05** SSRF: `fetch`/`axios` with a URL from input; `fetch` follows redirects by default. Block
  `169.254.169.254` and private ranges.
- **JS-NODE-06** No timeout on an outbound request (`axios` has none by default); no `server.timeout`/`headersTimeout`.
- **JS-NODE-07** Rate limiting absent on auth or expensive endpoints.
- **JS-NODE-08** `zlib` inflate on untrusted input without `maxOutputLength`.

## Correctness hazards

- **JS-HAZ-01** Floating promise: an `async` call not awaited and with no `.catch`; in Node this can kill the process.
- **JS-HAZ-02** `try/catch` swallowing, or `.catch(() => {})`.
- **JS-HAZ-03** `any`, `as`, `@ts-ignore` or `!` at a trust boundary: the type guarantee is void where it mattered.
  Input crossing into typed code must be validated at runtime (zod, io-ts), not merely typed.
- **JS-HAZ-04** `==` where `===` is meant, on a security comparison.
- **JS-HAZ-05** Unbounded concurrency: `Promise.all` over a caller-sized array.
- **JS-HAZ-06** `process.exit()` in library code; an `uncaughtException` handler that continues in a corrupted state.
- **JS-HAZ-07** ReDoS: user input against a regex with nested quantifiers.

## Supply chain

- **JS-SUP-01** No lockfile committed, or a lockfile inconsistent with `package.json`.
- **JS-SUP-02** `postinstall`/`preinstall` scripts in the project or a direct dependency (check `npm ls` output).
- **JS-SUP-03** Dependency from a git URL, a tarball URL, or an unscoped name shadowing an internal package.
- **JS-SUP-04** `npm audit` HIGH/CRITICAL, rated by reachability: a dev-dependency advisory is no production CRITICAL.
- **JS-SUP-05** Vast transitive tree for a trivial need; abandoned packages on a security path.

## Verification commands (read-only)

```bash
npm audit --omit=dev                      # or pnpm/yarn equivalent
npx --yes eslint . --no-eslintrc -c <cfg> # only if a config exists
semgrep --config=p/javascript .           # if installed
grep -rn "eval(\|innerHTML\|dangerouslySetInnerHTML\|child_process\|Math.random()\|rejectUnauthorized" \
  --include='*.{ts,tsx,js,jsx}' .
grep -rn "NEXT_PUBLIC_\|VITE_\|REACT_APP_" -r . | grep -iE 'secret|key|token|password'
```
