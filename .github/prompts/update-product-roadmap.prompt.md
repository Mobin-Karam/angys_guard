Update AngysGuard's product/platform roadmap for this change: <change or new goal>.

Follow `AGENTS.md`, `docs/GRAPHIFY_NAVIGATION.md`, and the `$product-roadmap-maintenance` workflow.

Requirements:
- verify the current implementation/support state with Graphify + minimal authoritative source/tests/docs;
- separate **current**, **planned**, **research**, and **user-requested** capabilities;
- update `docs/ANGYSGUARD_PRODUCT_VISION.md`, `docs/PLATFORM_SUPPORT.md`, `docs/CONTROL_MODES.md`, `docs/ROADMAP.md`, `docs/PROJECT_MANAGEMENT.md`, root `README.md`, and repository-management metadata only where the change actually affects them;
- keep self-hosted/local operation first-class and managed AngysGuard service optional;
- never propose sending/storing the protected device's OS password through Bale, Telegram, a mobile app, or the managed backend;
- never add a generic remote shell or claim unvalidated platform support;
- create/update focused GitHub issues/milestones rather than burying substantial work only in prose;
- use `$repository-presentation` if public README/About/support claims changed;
- identify target-device/provider/security validation required before any planned platform becomes Supported.

Return a concise summary of current state, roadmap changes, issue/milestone mapping, security constraints, and validation gates.
