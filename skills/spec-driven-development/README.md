# Spec-Driven Development

Design technical specifications (Spec) before coding. Establish the contract and implementation details upfront.

## How to Use

### Standalone Invocation (Generate Complete Spec)

When you have clear business requirements (PRD) and need to design technical specifications:

```
/skill spec-driven-development
Based on the user search feature requirements, design backend APIs, database schema, and frontend interaction details.
```

### As Phase 2 of Codoop-Ticket Orchestration

The `codoop-ticket` skill automatically calls this skill in phase 2:

```
【Phase 2】Technical Spec (spec.md)
6. codoop-ticket loads /skill spec-driven-development
7. Design spec.md based on module_prd.md
8. User reviews and confirms
```

## Key Outputs of Spec Design

**spec.md** should include:

- **Objective** — Technical goals and success criteria
- **Commands** — Complete build, test, and dev commands
- **Project Structure** — Directory layout and file organization
- **Code Style** — Code style examples and conventions
- **Testing Strategy** — Testing framework and coverage requirements
- **Boundaries** — Always / Ask First / Never operation boundaries

For ticket orchestration scenarios, particularly important to include:

- **API Contract** — Interface definitions for each platform (Backend/Web/Mobile/Desktop)
- **Data Schema** — Database field changes and data model design
- **UI Interactions** — Frontend interaction flows and state management
- **Editable Files** — `files_to_edit` whitelist (for Phase 3 use)

## Relationship with planning-and-task-breakdown

The output of this skill (spec.md) is the input to `planning-and-task-breakdown` skill. Spec defines "what to build", plan defines "how to build it".

## Best Practices

1. **Use tables for key information** — Use tables rather than paragraphs to describe APIs, fields, commands
2. **Include code examples** — Show actual code snippets, not just conceptual descriptions
3. **Clear boundaries** — Make Boundaries section explicit to avoid ambiguity during implementation
4. **Align with team style** — Code Style should reflect the project's existing conventions

