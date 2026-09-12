Diagnose this CI failure: <job/run/error>

Read the workflow/config and failing step, then compare with local/project requirements. Classify the failure before changing code: real regression, flaky test, dependency/environment drift, workflow/config bug, platform-specific issue, or unrelated infrastructure outage.

Use the smallest relevant log excerpt and reproduce locally when practical. Fix the underlying repo problem only if one exists; do not weaken tests or ignore failures to make CI green.

Report failing step, root cause, patch (if needed), verification, and whether rerun/manual infrastructure action is still required.