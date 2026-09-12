Add meaningful tests for: <behavior/component>

First identify the contract and existing test style. Test observable behavior rather than implementation details where practical.

Cover the highest-value cases:
- happy path;
- boundary/invalid input;
- expected failures/timeouts/unavailable dependency;
- authorization/denial when applicable;
- regression case for the reported bug;
- cleanup/state persistence/concurrency where material.

Use fake credentials, temporary paths/data, deterministic time/randomness, and mocks/fakes for hardware/network where appropriate. Avoid brittle sleeps and over-mocking the logic under test. Run the new tests and relevant suite.