Fix these failing tests: <tests/errors>

Determine first whether the production code is wrong, the test expectation is stale, the fixture/environment is wrong, or the test is flaky. Do not automatically change tests to match current output.

Trace the intended contract from source/docs/history. Make the smallest correct fix at the owning layer, preserve meaningful coverage, and add a regression assertion if the failure exposed an uncovered case.

Run the failing tests repeatedly when flakiness is suspected, then run nearby/full applicable checks. Explain why the chosen fix is correct.