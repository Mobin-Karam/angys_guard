Fix this reproducible bug: <bug and reproduction>

First confirm the reproduction and trace it to the owning code path. Add or identify a regression test that fails for the bug before changing production behavior when practical.

Fix the root cause with the smallest coherent patch. Do not bypass validation/auth/security, swallow unexpected errors, retry forever, or create a second implementation path just to avoid the failure.

Run the focused regression test, nearby tests, and all applicable repository checks. Report root cause, changed behavior, tests, compatibility/security impact, and manual validation still required.