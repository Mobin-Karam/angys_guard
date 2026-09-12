# Runtime and security flows

These diagrams make control flow and security ordering explicit. They describe the current conceptual flow and the preferred target boundaries; exact function names may evolve.

## Startup

```mermaid
sequenceDiagram
    participant U as User/systemd
    participant CLI as CLI
    participant CFG as Runtime config
    participant COMP as Composition
    participant G as Guard coordinator
    participant F as Feature manager

    U->>CLI: run
    CLI->>CFG: validate config / owner / token
    CFG-->>CLI: ready configuration
    CLI->>COMP: construct runtime
    COMP->>G: inject adapters/state/services
    G->>F: register/start features
    G-->>U: running
```

Architecture requirement: configuration validation happens before remote/security-sensitive runtime actions; construction is explicit; feature startup has deterministic ownership.

## Incoming owner command

```mermaid
sequenceDiagram
    participant P as Provider adapter
    participant D as Delivery/parser
    participant A as Authorization
    participant U as Use case/feature
    participant Port as Port
    participant I as Infrastructure adapter

    P->>D: untrusted update/callback
    D->>A: normalized identity + request
    A-->>D: allow / deny
    alt denied
      D-->>P: safe denial/ignore
    else allowed
      D->>U: typed request
      U->>Port: semantic operation
      Port->>I: adapter implementation
      I-->>U: stable result
      U-->>P: response/event
    end
```

Authorization must occur before privileged side effects. Parsing/bounds checking must occur before values reach application logic.

## Intrusion/input alert

```mermaid
sequenceDiagram
    participant M as Input/camera monitor
    participant G as Guard policy/state
    participant L as Local safety response
    participant E as Event/evidence
    participant Q as Outbox/provider

    M->>G: activity signal
    G->>G: armed? grace? cooldown?
    alt ignore
      G-->>M: no action
    else security event
      par local response
        G->>L: warning / lock schedule
      and evidence
        G->>E: capture/store bounded evidence
      and notification
        G->>Q: enqueue/send owner notification
      end
    end
```

Critical property: local warning/lock correctness must not depend on network delivery or evidence upload latency.

## Protected stop

```mermaid
sequenceDiagram
    participant L as Local user
    participant G as Guard
    participant PIN as PIN verifier
    participant O as Owner confirmation
    participant W as Exit watchdog

    L->>G: Ctrl+C / stop request
    G->>PIN: verify local factor
    alt invalid
      G->>W: remain protected / lock policy
    else valid
      G->>O: request second-factor confirmation
      alt denied/timeout
        G->>W: lock/fail closed
      else confirmed
        G->>W: write/consume one-time safe-exit authorization
        G->>G: orderly shutdown
      end
    end
```

The authorization decision must remain ahead of shutdown side effects. Refactors must preserve fail-closed behavior.

## Event and owner delivery

Preferred target:

```mermaid
flowchart LR
    APP[Application event] --> EV[(Event repository)]
    APP --> Q[(Durable outbox when delivery matters)]
    Q --> WORK[Delivery worker]
    WORK --> API[RuntimeApi/provider]
    API -->|success| ACK[mark delivered]
    API -->|transient failure| RETRY[bounded retry/backoff]
    API -->|terminal failure| FAIL[retain diagnostic state]
```

Remote failure must not erase the local security event. Retrying must be bounded and observable.

## Evidence lifecycle

Preferred target:

```text
capture request
  -> capability check
  -> bounded capture
  -> local evidence metadata/event
  -> optional owner delivery reference
  -> retention/quota evaluation
  -> delete only by explicit safe policy
```

Evidence storage and remote delivery are related but separate responsibilities.

## Configuration change while running

```text
CLI/config writer
  -> atomic persistent update
  -> runtime state/config boundary
  -> running process refreshes only explicitly live fields
```

Not every configuration value should become live-reloadable. Live fields must be documented; others should require restart to avoid partial runtime reconfiguration.

## Failure ordering principles

When multiple effects happen during a security event, prioritize:

1. preserve local safety response;
2. persist the event;
3. capture bounded evidence when permitted/available;
4. notify owner;
5. enrich/secondary UI behavior.

A lower-priority failure must not cancel a higher-priority safety action.
