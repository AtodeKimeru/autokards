# deck-targeting Specification

## Purpose
Defines how generated flashcards are bound to a target Anki deck on import — by deck name including `::` subdeck hierarchy, matched by Anki's native importer — rather than by an isolated numeric Deck ID.

## Requirements

### Requirement: Target deck bound by name not numeric ID
The system SHALL accept a deck name (including `::` subdeck hierarchy) as the target for generated flashcards rather than requiring a standalone numeric Deck ID.

#### Scenario: Deck name without subdeck is accepted
- **WHEN** the user submits a target deck name such as "Spanish" with no `::`
- **THEN** the system accepts the deck name as the target binding

#### Scenario: Deck name with `::` subdeck hierarchy is accepted
- **WHEN** the user submits a target deck name such as "Spanish::Verbs::Present"
- **THEN** the system accepts the full `::`-qualified deck name as the target binding

### Requirement: Import matches deck by name via Anki's native importer
The generated `.apkg` SHALL bind imported cards to the local deck whose name matches the target deck name, as resolved by Anki's native importer during standard manual import.

#### Scenario: Existing local deck with matching name receives cards
- **WHEN** the user's collection already contains a local deck named "Spanish::Verbs" of the same deck kind
- **THEN** Anki's importer maps the imported deck to that local deck and the new cards land there

#### Scenario: Same-name deck of different kind causes rename
- **WHEN** the user's collection already contains a local deck named "Spanish::Verbs" of a different deck kind
- **THEN** Anki's importer renames the imported deck (e.g. `Spanish::Verbs 1`) rather than merging into the existing deck; cards land under the renamed deck

#### Scenario: Matching deck absent results in Anki creating it
- **WHEN** no local deck named "Spanish::Verbs" exists in the user's collection
- **THEN** Anki's native import behavior creates the deck (including intermediate `::` subdecks) on import

### Requirement: Numeric deck ID is not the routing contract
The system SHALL NOT rely on an embedded numeric deck ID as the mechanism that determines which local deck receives imported cards.

#### Scenario: Embedded numeric ID does not override name matching
- **WHEN** a `.apkg` carries both a deck name and a numeric deck ID
- **THEN** Anki's importer routes cards by deck name, and the numeric ID is remapped to the local deck's ID rather than dictating the target

### Requirement: Deck-name boundary validation at autokards
The system SHALL validate the user-supplied deck name at the autokards boundary before writing it into the `.apkg`.

#### Scenario: Empty deck name is rejected
- **WHEN** the user submits an empty target deck name
- **THEN** autokards rejects the name and does not write it into the `.apkg`

#### Scenario: Deck name with empty `::` segment is rejected
- **WHEN** the user submits a target deck name containing an empty `::` segment (e.g. `"Spanish::"` or `"::Verbs"` or `"Spanish:::Verbs"`)
- **THEN** autokards rejects the name and does not write it into the `.apkg`

#### Scenario: Leading/trailing whitespace is stripped before packaging
- **WHEN** the user submits a target deck name with leading or trailing whitespace
- **THEN** autokards strips the whitespace before writing the name into the `.apkg`

### Requirement: Existing review history preserved on name-targeted import
Targeting an existing deck by name SHALL not disrupt the review history of cards already in that deck.

#### Scenario: Import into existing deck keeps existing cards' history
- **WHEN** cards are imported into an existing local deck that already contains cards with review history
- **THEN** the pre-existing cards retain their review history and scheduling

### Requirement: No deck-name lookup or collection access
The system SHALL NOT perform deck-name lookup or require access to the user's Anki collection.

#### Scenario: Name passed through without collection access
- **WHEN** autokards has no access to the user's Anki collection
- **THEN** the user-supplied deck name is written into the `.apkg` and Anki resolves it on import
