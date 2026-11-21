---
description: Backend development standards, best practices, and conventions for the Python application including Domain-Driven Design, SOLID principles, architecture patterns, API design, and testing practices
globs: ["backend/**/*.py", "backend/pyproject.toml", "backend/alembic/**", "backend/tests/**/*.py"]
alwaysApply: true
---

# Backend Project Standards and Best Practices

## Table of Contents

- [Overview](#overview)
- [Technology Stack](#technology-stack)
  - [Core Technologies](#core-technologies)
  - [Database & ORM](#database--orm)
  - [Testing Framework](#testing-framework)
  - [Development Tools](#development-tools)
- [Architecture Overview](#architecture-overview)
  - [Domain-Driven Design (DDD)](#domain-driven-design-ddd)
  - [Layered Architecture](#layered-architecture)
  - [Project Structure](#project-structure)
- [Domain-Driven Design Principles](#domain-driven-design-principles)
  - [Entities](#entities)
  - [Value Objects](#value-objects)
  - [Aggregates](#aggregates)
  - [Repositories](#repositories)
  - [Domain Services](#domain-services)
  - [Additional Recommendations](#additional-recommendations)
- [SOLID and DRY Principles](#solid-and-dry-principles)
  - [Single Responsibility Principle (SRP)](#single-responsibility-principle-srp)
  - [Open/Closed Principle (OCP)](#openclosed-principle-ocp)
  - [Liskov Substitution Principle (LSP)](#liskov-substitution-principle-lsp)
  - [Interface Segregation Principle (ISP)](#interface-segregation-principle-isp)
  - [Dependency Inversion Principle (DIP)](#dependency-inversion-principle-dip)
  - [DRY (Don't Repeat Yourself)](#dry-dont-repeat-yourself)
- [Coding Standards](#coding-standards)
  - [Naming Conventions](#naming-conventions)
  - [Type Hints & Typing](#type-hints--typing)
  - [Error Handling](#error-handling)
  - [Validation Patterns](#validation-patterns)
  - [Logging Standards](#logging-standards)
- [API Design Standards](#api-design-standards)
  - [REST Endpoints](#rest-endpoints)
  - [Request/Response Patterns](#requestresponse-patterns)
  - [Error Response Format](#error-response-format)
  - [CORS Configuration](#cors-configuration)
- [Database Patterns](#database-patterns)
  - [ORM Models & Schema](#orm-models--schema)
  - [Migrations](#migrations)
  - [Repository Pattern](#repository-pattern)
- [Testing Standards](#testing-standards)
  - [Test File Structure](#test-file-structure)
  - [Test Organization Pattern](#test-organization-pattern)
  - [Test Case Naming Convention](#test-case-naming-convention)
  - [Test Structure (AAA Pattern)](#test-structure-aaa-pattern)
- [Performance Best Practices](#performance-best-practices)
  - [Database Query Optimization](#database-query-optimization)
  - [Async & I/O Patterns](#async--io-patterns)
  - [Error Handling Performance](#error-handling-performance)
- [Security Best Practices](#security-best-practices)
  - [Input Validation](#input-validation)
  - [Environment Variables](#environment-variables)
  - [Dependency Injection](#dependency-injection)
- [Development Workflow](#development-workflow)
  - [Git Workflow](#git-workflow)
  - [Development Scripts](#development-scripts)
  - [Code Quality](#code-quality)

---

## Overview

This document outlines the best practices, conventions, and standards for the Python backend application. The backend follows Domain-Driven Design (DDD) principles and implements a layered architecture to ensure code consistency, testability, maintainability, and scalability.

## Technology Stack

### Core Technologies
- **Python**: Python 3.11+ with full type annotations
- **Web Framework**: FastAPI (or your chosen async/sync HTTP framework)
- **Validation & Serialization**: Pydantic v2

### Database & ORM
- **Database**: PostgreSQL (or SQLite for local/embedded workflows)
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic

### Testing Framework
- **Test Runner**: `pytest` (with `pytest-asyncio` where async endpoints/services are tested)
- **Coverage Threshold**: 90% for branches, functions/lines, and statements (`pytest --cov`)
- **Test Location**: `tests/` directory mirroring `src/` using `test_*.py` files

### Development Tools
- **Linter & Formatter**: Ruff (`ruff check`, `ruff format`)
- **Static Type Checker**: mypy (`mypy src`)
- **Package & Environment Management**: `uv` or `poetry` configured in `pyproject.toml`

## Architecture Overview

### Domain-Driven Design (DDD)

Domain-Driven Design centers software modeling on business logic and domain rules rather than framework or database mechanics.

**Benefits:**
- **Shared Ubiquitous Language**: Aligns code terms with domain concepts across engineers and stakeholders.
- **Clear Domain Models**: Keeps business invariants and state transitions explicit in domain types.
- **High Maintainability**: Isolates core business rules from transport, serialization, and persistence details.

### Layered Architecture

The backend follows a layered DDD architecture:

**Presentation Layer** (`src/presentation/`)
- Routers/controllers parse HTTP requests and format HTTP responses
- Delegates use cases to the Application layer
- Maps domain/application errors to HTTP status codes

**Application Layer** (`src/application/`)
- Use-case/application services orchestrate workflows and transactions
- Request/response schemas and input validators live here or at the boundary
- Services depend on domain models and repository protocols/interfaces

**Domain Layer** (`src/domain/`)
- Entities, value objects, aggregates, and domain services
- Repository interfaces (`typing.Protocol` or `abc.ABC`) defining persistence contracts
- Pure business logic without HTTP or ORM framework coupling

**Infrastructure Layer** (`src/infrastructure/`)
- ORM models, database session/engine setup, and repository implementations
- External integrations (APIs, file storage, queues) and structured logging

### Project Structure

```text
backend/
├── src/
│   ├── domain/
│   │   ├── models/          # Domain entities, value objects, aggregates
│   │   ├── repositories/    # Repository protocols/interfaces
│   │   └── services/        # Pure domain services
│   ├── application/
│   │   ├── services/        # Application / use-case services
│   │   ├── schemas/         # DTOs / Pydantic schemas
│   │   └── validators.py    # Domain/input validation helpers
│   ├── presentation/
│   │   ├── api/             # Route handlers / controllers
│   │   └── middleware/      # Auth, error handling, request logging middleware
│   ├── infrastructure/
│   │   ├── db/              # Engine, session factory, ORM models, repositories
│   │   └── logging.py       # Structured logger setup
│   ├── config.py            # Settings loaded from environment
│   └── main.py              # Application entry point
├── alembic/
│   └── versions/            # Database migration scripts
├── tests/
│   ├── unit/                # Unit tests (test_*.py)
│   ├── integration/         # Repository / API integration tests
│   └── conftest.py          # Shared fixtures and test helpers
├── pyproject.toml           # Dependencies, ruff, mypy, pytest config
└── alembic.ini              # Alembic configuration

```

## Domain-Driven Design Principles

### Entities

Entities represent domain concepts with a distinct identity that persists across state changes.

**Before:**

```python
# Raw dictionary without encapsulated domain rules
item = {
    "id": 1,
    "title": "Draft notes",
    "completed": False,
}

```

**After:**

```python
from dataclasses import dataclass


@dataclass
class TaskItem:
    id: int | None
    title: str
    completed: bool = False

    def mark_completed(self) -> None:
        if not self.title.strip():
            raise ValueError("Cannot complete a task with an empty title")
        self.completed = True

```

**Explanation**: `TaskItem` has a unique `id` identity and encapsulates state transition rules (`mark_completed`) instead of exposing mutable dictionaries everywhere.

**Best Practice**: Keep invariants inside domain entities and raise domain/value errors when state rules are violated.

### Value Objects

Value Objects are immutable objects defined by their attributes rather than an identity.

**Before:**

```python
# Loose tuple or dict representing an external identifier
deck_ref = {"deck_id": 42}

```

**After:**

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class DeckId:
    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError("Deck ID must be a positive integer")

```

**Explanation**: `DeckId` is immutable (`frozen=True`), self-validating, and compared by value rather than object identity.

**Recommendation**: Use `@dataclass(frozen=True)` for value objects and validate constraints in `__post_init__`.

### Aggregates

Aggregates group related entities and value objects behind an aggregate root that enforces consistency boundaries.

**Before:**

```python
# Mutating child records directly outside the parent boundary
cards.append({"deck_id": 1, "front": "Q", "back": "A"})

```

**After:**

```python
from dataclasses import dataclass, field


@dataclass
class Flashcard:
    front: str
    back: str


@dataclass
class Deck:
    id: int | None
    name: str
    cards: list[Flashcard] = field(default_factory=list)

    def add_card(self, front: str, back: str) -> Flashcard:
        if not front.strip() or not back.strip():
            raise ValueError("Front and back text must be non-empty")
        card = Flashcard(front=front.strip(), back=back.strip())
        self.cards.append(card)
        return card

```

**Explanation**: `Deck` acts as the aggregate root, ensuring every added card satisfies domain rules before entering the collection.

**Recommendation**: Modify child entities through aggregate root methods rather than mutating internal lists directly from outside.

### Repositories

Repositories abstract data access behind domain interfaces so application services do not depend on SQL or ORM specifics.

**Before:**

```python
# Direct ORM query inside a business service
def get_user(session, user_id: int):
    return session.query(UserORM).filter(UserORM.id == user_id).first()

```

**After:**

```python
from typing import Protocol


class UserRepository(Protocol):
    async def get_by_id(self, user_id: int) -> User | None: ...
    async def save(self, user: User) -> User: ...

```

**Explanation**: Defining `UserRepository` as a `Protocol` in the domain layer lets infrastructure provide concrete implementations while keeping services decoupled.

**Recommendation**: Keep repository interfaces focused on domain collections and aggregates, and inject implementations into application services.

### Domain Services

Domain Services hold stateless domain logic that spans multiple entities or does not naturally belong to a single entity.

**Before:**

```python
# Procedural helper scattered across modules
def calc_score(correct: int, total: int) -> float:
    return (correct / total) * 100 if total else 0.0

```

**After:**

```python
class ScoringPolicy:
    @staticmethod
    def calculate_percentage(correct: int, total: int) -> float:
        if total < 0 or correct < 0:
            raise ValueError("Counts cannot be negative")
        if total == 0:
            return 0.0
        return round((correct / total) * 100, 2)

```

**Explanation**: Centralizes domain calculation rules in one place with explicit guard conditions.

### Additional Recommendations

* **Factories**: Use factory functions or classmethods when constructing complex aggregates that require multi-step validation or default setup.
* **Relationship Modeling**: Model only relationships needed by business invariants and queries; avoid bidirectional cycles unless required.
* **Domain Events**: Emit domain events from aggregates/services when side effects (notifications, audit logs, downstream jobs) should stay decoupled.

## SOLID and DRY Principles

### Single Responsibility Principle (SRP)

Each class, module, or function should have one clear reason to change.

**Before:**

```python
def create_and_notify_user(payload: dict, db, mailer):
    if "@" not in payload.get("email", ""):
        raise ValueError("Invalid email")
    record = db.add_user(payload)
    mailer.send_welcome(record.email)
    return record

```

**After:**

```python
class UserRegistrationService:
    def __init__(self, repo: UserRepository, notifier: WelcomeNotifier) -> None:
        self._repo = repo
        self._notifier = notifier

    async def register(self, email: str, name: str) -> User:
        user = User.create(email=email, name=name)
        saved = await self._repo.save(user)
        await self._notifier.send_welcome(saved)
        return saved

```

**Explanation**: Validation/creation lives in `User`, persistence in `UserRepository`, notification in `WelcomeNotifier`, and orchestration in `UserRegistrationService`.

### Open/Closed Principle (OCP)

Software modules should be open for extension without modifying existing tested code.

**Before:**

```python
def export_deck(fmt: str, deck: Deck) -> bytes:
    if fmt == "json":
        return b"..."
    if fmt == "csv":
        return b"..."
    raise ValueError(f"Unsupported format: {fmt}")

```

**After:**

```python
from typing import Protocol


class DeckExporter(Protocol):
    def export(self, deck: Deck) -> bytes: ...


class JsonDeckExporter:
    def export(self, deck: Deck) -> bytes:
        return b"..."

```

**Explanation**: Adding a new export format means adding a new `DeckExporter` implementation rather than editing a growing `if/elif` branch.

### Liskov Substitution Principle (LSP)

Subtypes and protocol implementations must be usable wherever their base type or protocol is expected without breaking invariants or raising unexpected errors.

**Before:**

```python
class ReadOnlyStore:
    def save(self, item: object) -> None:
        raise NotImplementedError("Read-only store cannot save")

```

**After:**

```python
class ItemReader(Protocol):
    def get(self, item_id: int) -> object | None: ...


class ItemWriter(Protocol):
    def save(self, item: object) -> None: ...

```

**Explanation**: Splitting read and write protocols avoids forcing read-only implementations to throw `NotImplementedError`.

### Interface Segregation Principle (ISP)

Prefer small, focused protocols/interfaces over large ones that force callers or implementations to depend on unused methods.

**Before:**

```python
class StorageClient(Protocol):
    def upload(self, path: str, data: bytes) -> None: ...
    def download(self, path: str) -> bytes: ...
    def delete(self, path: str) -> None: ...
    def list_buckets(self) -> list[str]: ...

```

**After:**

```python
class FileUploader(Protocol):
    def upload(self, path: str, data: bytes) -> None: ...


class FileDownloader(Protocol):
    def download(self, path: str) -> bytes: ...

```

**Explanation**: Consumers only declare the exact capability (`FileUploader` or `FileDownloader`) they need, making fakes and mocks smaller in tests.

### Dependency Inversion Principle (DIP)

High-level policy and application logic should depend on abstractions (`Protocol`/`ABC`), not concrete infrastructure clients.

**Before:**

```python
class ReportService:
    def __init__(self) -> None:
        self.client = httpx.AsyncClient()  # Tightly coupled concrete dependency

```

**After:**

```python
class ReportService:
    def __init__(self, fetcher: MetricsFetcher) -> None:
        self._fetcher = fetcher

```

**Explanation**: Injecting `MetricsFetcher` makes `ReportService` easy to test and swap across environments.

### DRY (Don't Repeat Yourself)

Consolidate repeated business rules, queries, or serialization logic into shared helpers or base components.

**Before:**

```python
def create_item(name: str) -> str:
    cleaned = name.strip()
    if not cleaned:
        raise ValueError("Name is required")
    return cleaned

def rename_item(name: str) -> str:
    cleaned = name.strip()
    if not cleaned:
        raise ValueError("Name is required")
    return cleaned

```

**After:**

```python
def normalize_required_name(name: str) -> str:
    cleaned = name.strip()
    if not cleaned:
        raise ValueError("Name is required")
    return cleaned

```

**Explanation**: Centralizes normalization and validation in a single helper function.

## Coding Standards

### Naming Conventions

* **Variables & Functions**: `snake_case` (e.g., `deck_id`, `get_user_by_id`)
* **Classes & Protocols**: `PascalCase` (e.g., `TaskItem`, `UserRepository`)
* **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_BATCH_SIZE`)
* **Modules & Packages**: `snake_case` (e.g., `task_service.py`, `user_repository.py`)
* **Language**: Write code, identifiers, docstrings, comments, error messages, and logs in English consistently.

```python
# Good
async def find_candidate_by_id(candidate_id: int, repo: CandidateRepository) -> Candidate | None:
    return await repo.get_by_id(candidate_id)

# Avoid: Non-English identifiers, comments, or log messages
async def buscar_candidato(id_candidato: int):
    # Buscar candidato por ID
    return None

```

### Type Hints & Typing

* **Strict Typing**: Enable strict/ thorough checking in `mypy` (`disallow_untyped_defs = true`, `warn_return_any = true`).
* **Explicit Signatures**: Annotate all function parameters and return types.
* **Modern Syntax**: Use `X | None`, `list[str]`, and `dict[str, Any]` (Python 3.11+).
* **Avoid `Any**`: Prefer explicit models, `Protocol`s, or narrowing over `Any`.

```python
# Good
def parse_ids(raw_ids: list[str]) -> list[int]:
    return [int(item) for item in raw_ids]

# Avoid
def parse_ids(raw_ids):
    return [int(item) for item in raw_ids]

```

### Error Handling

* **Custom Exceptions**: Define explicit domain/application exception classes (`NotFoundError`, `ValidationError`, `ConflictError`).
* **Centralized Translation**: Map custom exceptions to HTTP status codes in a single global exception handler/middleware rather than repeating `try/except` HTTP responses in every route.
* **Preserve Context**: Use `raise ... from exc` when chaining exceptions.

```python
class NotFoundError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

```

### Validation Patterns

* **Boundary Validation**: Validate incoming payloads and query parameters at the API/application boundary using Pydantic schemas.
* **Domain Invariants**: Enforce business rules inside domain models/services before persisting state.

```python
from pydantic import BaseModel, Field


class CreateDeckRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    target_deck_id: int = Field(gt=0)

```

### Logging Standards

* **Centralized Logger**: Use `logging.getLogger(__name__)` configured via `src/infrastructure/logging.py`.
* **Appropriate Levels**: Use `debug`, `info`, `warning`, and `error` accurately.
* **Structured Context**: Include relevant IDs and context without logging secrets, tokens, or PII.

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Deck export completed", extra={"deck_id": 42, "card_count": 15})
logger.error("Failed to generate deck export", extra={"deck_id": 42})

```

## API Design Standards

### REST Endpoints

* **Resource Nouns**: Use plural nouns for collections (`/api/v1/decks`, `/api/v1/decks/{deck_id}`).
* **HTTP Verbs**: Use `GET`, `POST`, `PUT`/`PATCH`, and `DELETE` according to semantics.
* **Versioning**: Prefix routes under `/api/v1`.

```text
GET    /api/v1/decks              # List decks
GET    /api/v1/decks/{deck_id}    # Retrieve a single deck
POST   /api/v1/decks              # Create a deck
PATCH  /api/v1/decks/{deck_id}    # Update deck fields
DELETE /api/v1/decks/{deck_id}    # Delete a deck

```

### Request/Response Patterns

* **JSON Payloads**: Use JSON for request and response bodies.
* **Consistent Envelope**: Return a consistent response structure across endpoints.
* **Status Codes**: Use accurate HTTP status codes (`200`, `201`, `204`, `400`, `404`, `422`, `500`).

```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Biology 101"
  },
  "message": "Deck created successfully"
}

```

### Error Response Format

* **Standardized Error Shape**: Return consistent error payloads with a clear message, machine-readable code, and optional field/validation details.
* **No Internal Leaks**: Never expose raw SQL queries, stack traces, or internal secrets in responses.

```json
{
  "success": false,
  "error": {
    "message": "Deck not found",
    "code": "NOT_FOUND",
    "details": []
  }
}

```

### CORS Configuration

* **Explicit Origins**: Configure allowed origins explicitly via environment variables instead of wildcard `*` with credentials in production.
* **Methods & Headers**: Restrict allowed methods and headers to what the client actually uses.

## Database Patterns

### ORM Models & Schema

* **Single Source of Truth**: Define schema changes in migrations and keep ORM models aligned with the database schema.
* **Explicit Relationships & Constraints**: Declare foreign keys, indexes, and constraints explicitly.
* **No Raw SQL in Services**: Encapsulate database queries inside repository implementations.

### Migrations

* **Versioned Migrations**: Every schema change must have a corresponding migration script in `alembic/versions/`.
* **Descriptive Naming**: Name migrations after the schema change (e.g., `add_decks_table`).
* **Review Before Applying**: Inspect generated migration scripts before running them in shared or production environments.

```bash
alembic revision --autogenerate -m "add_decks_table"
alembic upgrade head

```

### Repository Pattern

* **Protocol in Domain, Implementation in Infrastructure**: Keep the contract in `src/domain/repositories/` and the SQLAlchemy implementation in `src/infrastructure/db/`.
* **Explicit Session Injection**: Inject the database session/connection rather than instantiating global sessions inside repository methods.

## Testing Standards

### Test File Structure

* Name test files `test_<module_or_feature>.py` inside `tests/unit/` or `tests/integration/`.
* Use `pytest` and fixtures defined in `tests/conftest.py`.
* Target at least 90% coverage across branches, lines, and statements.

### Test Organization Pattern

```python
def test_mark_completed_sets_flag_when_title_is_present() -> None:
    # Arrange
    task = TaskItem(id=1, title="Review chapter 3", completed=False)

    # Act
    task.mark_completed()

    # Assert
    assert task.completed is True

```

### Test Case Naming Convention

* Use descriptive names explaining behavior and condition: `test_<expected_behavior>_when_<condition>`.
* Group related tests in classes (`TestTaskItem`) or modules by feature.

### Test Structure (AAA Pattern)

Always structure tests clearly into **Arrange**, **Act**, and **Assert**:

* **Arrange**: Prepare domain objects, inputs, and test doubles/fakes.
* **Act**: Invoke the single function, service method, or endpoint under test.
* **Assert**: Verify return values, state changes, raised exceptions, and collaborator calls.

## Performance Best Practices

### Database Query Optimization

* **Avoid N+1 Queries**: Eager-load or batch-fetch related records instead of querying inside loops.
* **Select Needed Columns**: Avoid fetching unneeded columns or large payloads when listing records.
* **Index Filter & Join Columns**: Ensure foreign keys and frequent filter predicates are indexed.

### Async & I/O Patterns

* **Non-Blocking I/O**: Use async I/O (`async def` + async clients/drivers) consistently in async endpoints and services; do not call blocking I/O inside an async event loop without offloading.
* **Bounded Concurrency**: Use bounded task groups/semaphores when running parallel external calls.

### Error Handling Performance

* **Use Control Flow, Not Exceptions**: Do not use exceptions for normal branching or expected empty/missing checks where returning `None` or a result is clearer.
* **Validate Early**: Fail fast on invalid inputs before opening expensive I/O or transactions.

## Security Best Practices

### Input Validation

* **Strict Boundary Parsing**: Reject unexpected or malformed inputs at the API boundary.
* **Safe File & Path Handling**: Validate file types, sizes, and paths; prevent path traversal (`../`) when handling uploads or exports.

### Environment Variables

* **Never Hardcode Secrets**: Load API keys, database URLs, and signing secrets from environment variables / secret stores.
* **Fail Fast on Missing Config**: Validate required environment settings at startup rather than failing mid-request.

### Dependency Injection

* **Explicit Wiring**: Wire dependencies explicitly via framework DI or constructor injection so test doubles can be injected cleanly without monkeypatching internals.

## Development Workflow

### Git Workflow

* **Feature Branches**: Create a dedicated branch from the base branch for each task (`feat/<slug>` or `fix/<slug>`).
* **Small, Scoped Commits**: Keep commits focused on the task with clear commit messages.

### Development Scripts

Run standard development commands from `backend/`:

```bash
# Install dependencies
uv sync

# Run dev server
uvicorn src.main:app --reload

# Run tests with coverage
pytest --cov=src

# Lint & format
ruff check .
ruff format --check .

# Type check
mypy src

```

### Code Quality

Before marking a task complete, ensure linting, formatting, type checking, and tests pass without unresolved errors.

```
