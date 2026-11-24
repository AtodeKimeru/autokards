# Spec Delta

## Purpose

Generates one or more front/back flashcards from validated study text, enforcing
single-target Fronts, answering and grounded Backs, strict output validation, and
explicit generation-failure behavior.

## ADDED Requirements

### Requirement: Generate one or more flashcards
The system SHALL generate one or more flashcards from study text that passed input validation.

#### Scenario: Valid text produces cards
- **WHEN** the user submits text containing at least one non-whitespace character
- **THEN** the system generates one or more flashcards
- **AND** every card has a non-empty Front and a non-empty Back

#### Scenario: Zero cards is a failure
- **WHEN** the generator returns zero cards for valid study text
- **THEN** the system returns an explicit generation error
- **AND** it does not return an empty success response

### Requirement: Separate Front and Back fields
The system SHALL represent each flashcard with distinct Front and Back fields.

#### Scenario: Card exposes separate fields
- **WHEN** the system returns generated cards
- **THEN** each card exposes `front` and `back` as separate values
- **AND** neither field is derived from or embedded in the other

### Requirement: Single retrieval target per Front
The system SHALL generate every Front with exactly one identifiable question,
prompt, or concept to retrieve.

#### Scenario: Front contains one retrieval target
- **WHEN** a generated card is reviewed
- **THEN** its Front presents exactly one identifiable retrieval target
- **AND** it does not combine multiple independent questions or prompts

### Requirement: Back answers the Front
The system SHALL generate every Back as a non-empty answer to the corresponding Front.

#### Scenario: Back answers the prompt
- **WHEN** a generated card is reviewed
- **THEN** its Back provides a non-empty answer to the Front prompt

### Requirement: Back is grounded in the source text
The system SHALL ensure that every factual claim on a Back is supported by the submitted study text.

#### Scenario: Grounded Back
- **WHEN** a generated card is reviewed against the source text
- **THEN** every factual claim on the Back can be traced to the source text
- **AND** no unsupported factual claim is introduced

### Requirement: Return generated cards in the response
The system SHALL return generated cards in the success response of the generation entry point.

#### Scenario: Successful generation response
- **WHEN** generation succeeds for valid study text
- **THEN** the system returns HTTP 200
- **AND** the response contains the generated cards in `data.cards`
- **AND** no `.apkg` file or download link is included

### Requirement: Explicit generation failures
The system SHALL report generation failures explicitly and SHALL NOT return partial cards or silently truncate input.

#### Scenario: Provider cannot process the input
- **WHEN** the generation provider rejects the complete input as exceeding its own limit
- **THEN** the system returns HTTP 422 with code `INPUT_EXCEEDS_PROVIDER_LIMIT`
- **AND** no cards are returned

#### Scenario: Provider fails
- **WHEN** the generation provider times out, fails, or returns malformed output
- **THEN** the system returns HTTP 502 with code `GENERATION_ERROR`
- **AND** no cards are returned
- **AND** no internal stack trace or secret is exposed

#### Scenario: Output is structurally invalid
- **WHEN** the provider returns zero cards, empty Front/Back values, or malformed JSON
- **THEN** the system returns an explicit generation error
- **AND** no partial cards are returned
