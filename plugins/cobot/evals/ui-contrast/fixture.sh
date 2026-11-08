#!/usr/bin/env bash
# Seeds the eval workspace; runs only with --scaffold. A page whose body text fails 1.4.3 by 0.02.
set -euo pipefail
mkdir -p site
cat > site/styles.css <<'CSS'
:root { color-scheme: light; }
body { font-family: system-ui, sans-serif; font-size: 16px; line-height: 1.5; color: #777777; background: #ffffff; }
a { color: #00aa00; text-decoration: underline; }
button { min-width: 48px; min-height: 48px; }
button:focus-visible { outline: 2px solid #0b57d0; outline-offset: 2px; }
CSS
cat > site/index.html <<'HTML'
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Demo</title><link rel="stylesheet" href="styles.css"></head>
<body>
<main>
<h1>Demo</h1>
<p>Body text in grey on white. <a href="/more">Read more</a></p>
<button type="button">Continue</button>
</main>
</body>
</html>
HTML
