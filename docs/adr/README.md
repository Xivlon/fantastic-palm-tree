# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records (ADRs) for the Fantastic Palm Tree framework.

## What are ADRs?
Architecture Decision Records document important architectural decisions made during the development of the framework, including the context, decision, and consequences.

## Format
We use the format proposed by Michael Nygard in his blog post [Documenting Architecture Decisions](http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions).

## Current ADRs

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-001](001-modular-architecture.md) | Modular Architecture Design | Accepted |
| [ADR-002](002-type-safety-approach.md) | Type Safety Approach | Accepted |
| [ADR-003](003-configuration-system.md) | Configuration System Design | Accepted |
| [ADR-004](004-broker-integration-pattern.md) | Broker Integration Pattern | Accepted |

## Creating New ADRs

1. Copy the [template](template.md)
2. Number sequentially (ADR-XXX)
3. Write in past tense for decisions
4. Include context, decision, and consequences
5. Update this index

## ADR Lifecycle

- **Proposed**: Decision is under consideration
- **Accepted**: Decision is approved and implemented
- **Deprecated**: Decision is no longer recommended
- **Superseded**: Decision has been replaced by a newer ADR