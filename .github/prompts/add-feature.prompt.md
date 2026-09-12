Add this feature: <feature>

Before editing, discover repository instructions and trace the existing architecture to find the correct extension point. Define acceptance criteria and identify security/privacy/config/migration implications.

Implementation rules:
- use the existing abstraction/feature mechanism;
- keep the patch narrow and reviewable;
- preserve current behavior outside the feature;
- fail safely on invalid/unauthorized/unavailable conditions;
- avoid new dependencies unless clearly justified;
- keep optional integrations degradable when appropriate.

Add focused tests for normal behavior plus meaningful failure/denial paths. Update user/developer docs when behavior or configuration changes. Run targeted tests and all applicable repository checks, then report any manual validation still required.