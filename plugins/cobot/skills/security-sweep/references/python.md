# Python rule pack

Loads for `.py` files and applies `core.md` through Python idioms. Rule ids are `PY-<CAT>-<nn>`.

## Injection & execution

- **PY-EXEC-01** `subprocess.*` with `shell=True` and an interpolated argument. `os.system`, `os.popen` and
  `commands.*` are shell-by-construction: always flag. Argument-list form is safe unless the executable is input.
- **PY-EXEC-02** `eval`, `exec`, `compile` on data that is not a source literal. `ast.literal_eval` is the safe form.
- **PY-EXEC-03** `__import__` / `importlib.import_module` with a name from input: arbitrary module load.
- **PY-SQL-01** Query built with f-string, `%`, `.format()` or `+`. Correct form is `cur.execute("... %s", (param,))`;
  a bare string second argument silently reverts to interpolation in some drivers. SQLAlchemy `text()` with an
  f-string is the same bug. Identifiers need an allow-list, not quoting.
- **PY-PATH-01** `open`, `os.path.join`, `send_file`, `pathlib.Path` with input and no `Path.resolve()` plus
  `.is_relative_to(base)` check. Flask's `send_from_directory` is safe; `send_file(os.path.join(...))` is not.
- **PY-TMPL-01** Jinja2 `Template(user_input)` or `render_template_string`: server-side template injection,
  RCE-equivalent. Also `autoescape=False` on an HTML environment.
- **PY-INJECT-01** `|safe`, `Markup()`, `mark_safe()` applied to user data.

## Deserialization & parsing

- **PY-DESER-01** `pickle`, `cPickle`, `dill`, `shelve`, `marshal` or default `torch.load` on untrusted data. Direct
  RCE: CRITICAL, no mitigation short of not doing it.
- **PY-DESER-02** `yaml.load` without `Loader=SafeLoader`, or `yaml.unsafe_load`. `yaml.safe_load` is the fix.
- **PY-DESER-03** `xml.etree`, `minidom`, `xmlrpc` or `lxml` on untrusted XML (XXE, billion-laughs). Use `defusedxml`.
- **PY-DESER-04** `zipfile.extractall` / `tarfile.extractall` without member path validation (zip-slip) and no size
  cap. Use tarfile's `filter='data'` where available; otherwise validate manually.
- **PY-DESER-05** `jsonpickle`, or `json` decoded then fed to a dynamic object constructor.

## Crypto & secrets

- **PY-CRYPTO-01** `random`, `random.choice`, `uuid.uuid1` for a token, salt or session id. Use `secrets`
  (`uuid4` for identifiers only).
- **PY-CRYPTO-02** `hashlib.md5`/`sha1` on a security path (without `usedforsecurity=False`, which marks benign use).
- **PY-CRYPTO-03** Password hashed with anything but `argon2-cffi`, `bcrypt`, or `hashlib.scrypt`/`pbkdf2_hmac`
  with a high iteration count.
- **PY-CRYPTO-04** `pycrypto` (unmaintained, CVEs) instead of `cryptography` or `pycryptodome`; AES in ECB, or CBC
  without an HMAC.
- **PY-CRYPTO-05** `==` comparing a token or HMAC. Use `hmac.compare_digest`.
- **PY-TLS-01** `verify=False` on `requests`, `ssl._create_unverified_context`, `ssl.CERT_NONE`, or
  `urllib3.disable_warnings` silencing the resulting warning (the silencing is itself the tell).
- **PY-SEC-01** Secret in a module-level constant, a `settings.py` or a default argument; a literal `SECRET_KEY` in
  Django/Flask config.

## Web frameworks

- **PY-WEB-01** Django `DEBUG = True`, `ALLOWED_HOSTS = ['*']` or hardcoded `SECRET_KEY`. Flask `app.run(debug=True)`:
  the Werkzeug debugger is an RCE console.
- **PY-WEB-02** Django `.raw()`/`.extra()` with interpolation; `@csrf_exempt` on a state-changing view; a
  `ModelForm` with `fields = '__all__'` (mass assignment).
- **PY-WEB-03** FastAPI/Flask route with no auth dependency or decorator where auth is per-route: enumerate routes,
  diff against the protected set. Also a Pydantic model missing constraints on a size-bearing field.
- **PY-WEB-04** CORS `allow_origins=["*"]` with `allow_credentials=True`.
- **PY-WEB-05** Cookie set without `secure=True, httponly=True, samesite='Lax'`.
- **PY-WEB-06** `app.run(host='0.0.0.0')`, or a dev server (`runserver`, `app.run`) used as the production server.
- **PY-WEB-07** Response body containing a traceback or an exception `str()`.

## Requests & SSRF

- **PY-NET-01** `requests.get(url)` with `url` from input and no host allow-list; `allow_redirects=True` (the
  default) defeats pre-flight checks.
- **PY-NET-02** `requests` call with no `timeout=`: the default is no timeout, so it hangs forever. HAZARD, and a
  DoS vector under load.
- **PY-NET-03** `urllib.request.urlopen` with a `file://` or `ftp://` scheme reachable from input.

## Correctness hazards

- **PY-HAZ-01** Bare `except:` or `except Exception: pass`: swallows `KeyboardInterrupt`/`SystemExit`, hides failures.
- **PY-HAZ-02** Mutable default argument (`def f(x=[])`): shared state across calls, a cross-request leak in a handler.
- **PY-HAZ-03** File, socket or lock opened without a context manager on a path that can raise.
- **PY-HAZ-04** `assert` used to enforce a security check: stripped under `python -O`.
- **PY-HAZ-05** Blocking call inside `async def` (stalls the loop); shared state mutated across threads without a
  lock; a `create_task` whose result is never awaited (exceptions vanish).
- **PY-HAZ-06** `int()` on unbounded input (CVE-2020-10735): older Python hangs on long digit strings, newer raises.

## Supply chain & packaging

- **PY-SUP-01** `requirements.txt` with unpinned versions and no lockfile (`poetry.lock`, `Pipfile.lock`, or a
  `pip-compile` output).
- **PY-SUP-02** Dependency from a git URL, a direct HTTP URL, or an extra index that shadows PyPI names (confusion).
- **PY-SUP-03** `setup.py` executing code at install time.
- **PY-SUP-04** Known CVEs: run `pip-audit` or `safety check` if installed.

## Verification commands (read-only)

```bash
pip-audit                        # if installed
bandit -r . -ll -q               # if installed
semgrep --config=p/python .      # if installed
grep -rn "shell=True\|eval(\|exec(\|pickle\|yaml.load\|verify=False\|DEBUG *= *True" --include='*.py' .
```
