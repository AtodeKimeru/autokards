# Spec Delta

## Purpose

Validates submitted study text at generation entry so that empty or whitespace-only input is rejected with a clear message and never produces or offers a `.apkg` download.

## ADDED Requirements

### Requirement: Reject empty study text
The system SHALL reject empty study text (no characters) submitted to the generation entry point with a validation message stating readable study text is required.

#### Scenario: Empty text produces validation error and no package
- **WHEN** the user submits empty text to the generation entry point
- **THEN** the system returns a validation error with the message "Readable study text is required"
- **THEN** the system does not produce or offer a `.apkg` download

### Requirement: Reject whitespace-only study text
The system SHALL reject study text containing only whitespace characters submitted to the generation entry point with a validation message stating readable study text is required.

#### Scenario: Whitespace-only text produces validation error and no package
- **WHEN** the user submits text containing only whitespace characters to the generation entry point
- **THEN** the system returns a validation error with the message "Readable study text is required"
- **THEN** the system does not produce or offer a `.apkg` download

### Requirement: Accept valid study text
The system SHALL accept study text that contains at least one non-whitespace character and proceed to flashcard generation.

#### Scenario: Valid text proceeds to generation
- **WHEN** the user submits text with at least one non-whitespace character to the generation entry point
- **THEN** the system proceeds with flashcard generation
