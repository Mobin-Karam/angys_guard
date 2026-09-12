Investigate this performance problem: <symptom/goal>

Do not optimize by intuition alone. Establish a baseline and identify the actual bottleneck using available measurements/profiling/tests.

Analyze CPU, memory, I/O, network, startup latency, repeated work, algorithmic complexity, contention, polling, serialization, and external calls as relevant.

Propose changes ordered by expected impact vs complexity/risk. Preserve correctness/security and avoid micro-optimizations without evidence. Add a benchmark or measurable regression check where practical, and compare before/after results.