# Spec Delta

## Purpose

Accepts raw study text submitted by a learner and forwards it, byte-for-byte, toward flashcard generation, failing explicitly rather than silently truncating when a real infrastructure or provider limit is exceeded.

## ADDED Requirements

### Requirement: Complete text reaches generation
The system SHALL accept a non-empty text submission and forward the complete, unmodified text to the generation flow.

#### Scenario: Valid text submission
- **WHEN** a user submits non-empty study text through the input interface
- **THEN** the generation flow receives the complete text, byte-for-byte identical to what was submitted
- **AND** the submission proceeds to flashcard generation

#### Scenario: Large and unicode text is preserved
- **WHEN** a user submits a large multi-megabyte text containing unicode characters and mixed line endings, within infrastructure limits
- **THEN** the stored and forwarded text is identical to the submitted text, with no character loss or line-ending normalization

### Requirement: No product-defined length limit
The system SHALL NOT apply any character, word, or other product-defined length limit to text submissions. The only limits enforced SHALL be real infrastructure or model-provider constraints.

#### Scenario: Submission within infrastructure limits is accepted regardless of length
- **WHEN** a user submits text of any length up to (but not exceeding) the infrastructure byte limit
- **THEN** the system accepts the submission
- **AND** no additional product-defined length check rejects it

### Requirement: Explicit failure on infrastructure limit
The system SHALL reject, with an explicit error, any submission whose size exceeds the infrastructure limit, and SHALL NOT store or forward a partial or truncated version of that input.

#### Scenario: Submission exceeds infrastructure byte limit
- **WHEN** a user submits text whose size in bytes exceeds the configured infrastructure limit
- **THEN** the system rejects the submission with an explicit error identifying the limit and the received size
- **AND** no partial or truncated version of the input is stored or forwarded

### Requirement: Explicit failure on provider limit
The system SHALL report an explicit error when the generation provider cannot process the complete input, and SHALL NOT silently truncate the input or return a partial result.

#### Scenario: Provider rejects input as exceeding its own limit
- **WHEN** the generation provider reports that a forwarded submission exceeds its own processing limit
- **THEN** the system surfaces an explicit error to the user identifying the provider's stated limit
- **AND** does not attempt to truncate the input or return a partial generation result

### Requirement: No unlimited-capacity claims
The system SHALL NOT present any message, label, or documentation implying unlimited or infinite text-processing capacity.

#### Scenario: Error and success messaging avoids unlimited claims
- **WHEN** the system communicates the outcome of a text submission, whether accepted or rejected
- **THEN** no response or user-facing message states or implies that input size is unlimited or infinite

### Requirement: Non-empty input guard
The system SHALL reject an empty text submission at the boundary of this capability. Detailed whitespace-only validation and user-facing empty-input UX are owned by a separate capability and are out of scope here.

#### Scenario: Empty submission is rejected
- **WHEN** a user submits an empty text value
- **THEN** the system rejects the submission rather than forwarding it to generation
