Map the architecture relevant to this goal: <goal>

Do not edit files. Read applicable repository instructions/docs, then trace the real call/data flow through current source.

Identify:
- entry points and execution path;
- owning modules/classes/functions;
- interfaces/protocols/extension points;
- state/config/storage boundaries;
- external/network/OS/hardware boundaries;
- callers and downstream dependents;
- authorization/security/privacy checks;
- tests that cover the path;
- likely change points and areas that should not be touched.

End with the smallest safe implementation boundary and the verification that would be required.