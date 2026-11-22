# Home Assistant — CI for a custom integration

The Python job is `lang-python`'s `references/ci.md`. A custom integration adds one job:

- Home Assistant components: a second job with `home-assistant/actions/hassfest@<sha>` and
  `hacs/action@<sha>` with `category: integration`; both upstreams publish branch refs, so pin
  the commit and let Dependabot (`github-actions`) move it.
