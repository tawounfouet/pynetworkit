# M0 architectural boundaries

The project is a modular Python package organized by **capabilities**, not a
literal reimplementation of the seven OSI layers.

```text
public API / CLI / learning labs
             |
        application (as needed)
             |
       domain + ports
             ^
             |
    infrastructure adapters
```

- `domain`: pure types, invariant checks and lifecycle state transitions.
- `ports`: narrow capability contracts independent of concrete libraries.
- `adapters`: actual transport and deterministic test implementations.
- The composition root selects concrete adapters; domain objects do not.

M0 E0 contains importable placeholders only. The domain model arrives in M0 E1,
followed by the async stream contract and memory adapter in E2. TCP/UDP
sockets remain M1 deliverables.
