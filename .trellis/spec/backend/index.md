# Backend Development Guidelines

> Best practices for backend development in this project.

---

## Overview

This directory contains guidelines for backend development. Fill in each file with your project's specific conventions.

---

## Guidelines Index

| Guide | Description | Status |
|-------|-------------|--------|
| [Directory Structure](./directory-structure.md) | Script and deployment layout | Filled |
| [Persistence Guidelines](./database-guidelines.md) | JSON contract and atomic writes | Filled |
| [Error Handling](./error-handling.md) | CLI failures and source isolation | Filled |
| [Quality Guidelines](./quality-guidelines.md) | Tests, privacy, and live gates | Filled |
| [Logging Guidelines](./logging-guidelines.md) | Current CLI output conventions | Filled |
| [Real-Data Publish Contract](./real-data-publish-contract.md) | Source, projection, locking, install, and scheduler contract | Filled |

---

## Pre-Development Checklist

Read `directory-structure.md` and `quality-guidelines.md` for every Python or
deployment change. Also read `database-guidelines.md` for JSON writes,
`error-handling.md` for external sources, and `logging-guidelines.md` when
changing operator output. Read `real-data-publish-contract.md` when changing a
real source, shared widget contract, publisher, installer, or scheduler.

---

**Language**: All documentation should be written in **English**.
