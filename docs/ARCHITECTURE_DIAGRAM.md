# System Architecture Diagram

## Overview
This document provides visual representations of the Fantastic Palm Tree framework architecture.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Fantastic Palm Tree Framework                 │
├─────────────────────────────────────────────────────────────────┤
│                          User Interface                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   API Server    │  │     Examples    │  │   Notebooks     │ │
│  │   (FastAPI)     │  │   & Demos       │  │   & Scripts     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                        Core Framework                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │    Strategy     │  │      Risk       │  │   Indicators    │ │
│  │    Module       │  │   Management    │  │     Module      │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │     Models      │  │   Configuration │  │     Results     │ │
│  │   & Types       │  │     System      │  │   & Logging     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                    Backtesting Infrastructure                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Execution     │  │    Metrics      │  │   Parameter     │ │
│  │    Engine       │  │   Pipeline      │  │  Optimization   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                      Data & Broker Layer                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Data Providers  │  │ Broker Adapters │  │  Paper Trading  │ │
│  │ (Alpha Vantage) │  │   (Schwab)      │  │     Broker      │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Module Dependency Graph

```
Configuration System
        │
        ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   Strategy    │────│     Risk      │────│  Indicators   │
│    Module     │    │  Management   │    │    (ATR)      │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   Position    │    │   Trailing    │    │   Market      │
│    Models     │    │     Stops     │    │     Data      │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
                    ┌───────────────┐
                    │    Results    │
                    │   & Logging   │
                    └───────────────┘
```

## Data Flow Architecture

```
Market Data ──┐
              ├──► Strategy ──► Risk Management ──► Execution
Indicators ───┘                       │                │
                                     ▼                ▼
                               Position Models    Results &
                               Configuration      Metrics
```

## Broker Integration Pattern

```
┌─────────────────┐
│  Trading Logic  │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Broker Adapter │
└─────────┬───────┘
          │
    ┌─────┴─────┐
    ▼           ▼
┌─────────┐ ┌─────────┐
│  Paper  │ │ Schwab  │
│ Broker  │ │ Broker  │
└─────────┘ └─────────┘
```

## See Also
- [Architecture.md](../Architecture.md) - Detailed architecture documentation
- [ADR Documents](adr/) - Architecture decision records
- [README.md](../README.md) - Framework overview and usage