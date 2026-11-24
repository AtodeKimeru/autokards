# Spec Delta

## Purpose

Generates one or more front/back flashcards from validated study text, enforcing
single-target Fronts, answering and grounded Backs, strict output validation, a
byte ceiling on submitted text, a typed success contract, and explicit
generation-failure behavior.

## ADDED Requirements

### Requirement: Enforce a byte ceiling on submitted text
The system SHALL reject study text whose UTF-8 encoded length exceeds the configured `MAX_INPUT_BYTES` ceiling before any provider request is made.

#### Scenario: Oversized input is rejected
- **WHEN** the user submits text whose UTF-8 byte length exceeds `MAX_INPUT_BYTES`
- **THEN** the system returns HTTP 413 with code `INPUT_TOO_LARGE`
- **AND** the error details report `limit_bytes` and `received_bytes`
- **AND** no provider request is made and no cards are returned
- **AND** the submitted text is not truncated

#### Scenario: Text at the ceiling is accepted
- **WHEN** the user submits text whose UTF-8 byte length is exactly `MAX_INPUT_BYTES`
- **THEN** the system processes it normally

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

### Requirement: Documented success schema
The system SHALL expose the success response schema in OpenAPI, describing `data.cards` as an array of objects with non-empty string `front` and `back`.

#### Scenario: OpenAPI describes the card schema
- **WHEN** the OpenAPI document is generated for the generation endpoint
- **THEN** the 200 response references a schema with typed `data.cards[].front` and `data.cards[].back`
- **AND** it is not an untyped `additionalProperties` object

### Requirement: Consistent error envelope
The system SHALL return every error response using the standard envelope `{success: false, error: {message, code, details}}`, including request-schema validation failures.

#### Scenario: Missing or unknown request field
- **WHEN** the request body omits `text` or includes an unknown field
- **THEN** the system returns HTTP 422 with code `INVALID_REQUEST`
- **AND** the response uses the standard envelope
- **AND** the response does not echo the submitted input back

#### Scenario: No internals exposed
- **WHEN** any error response is returned
- **THEN** it contains no stack trace, provider credential, or upstream URL

### Requirement: Explicit generation failures
The system SHALL report generation failures explicitly and SHALL NOT return partial cards or silently truncate input.

#### Scenario: Provider cannot process the input
- **WHEN** the generation provider rejects the complete input as exceeding its own context limit, signalled either by HTTP 422 or by an HTTP 400 carrying a context-length-overflow error
- **THEN** the system returns HTTP 422 with code `INPUT_EXCEEDS_PROVIDER_LIMIT`
- **AND** no cards are returned
- **AND** the input is not truncated

#### Scenario: Provider fails
- **WHEN** the generation provider times out, fails, or returns malformed output
- **THEN** the system returns HTTP 502 with code `GENERATION_ERROR`
- **AND** no cards are returned
- **AND** no internal stack trace or secret is exposed

#### Scenario: Output is structurally invalid
- **WHEN** the provider returns zero cards, empty Front/Back values, or malformed JSON
- **THEN** the system returns an explicit generation error
- **AND** no partial cards are returned
