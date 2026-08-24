---
name: grilling
description: Grill the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'grill' trigger phrases.
---

## Conversation Profile

When `codoop_flow.toml` is available, read `user_role`; a missing value means
`general`. It applies only to this conversation: use normal professional terms
inside the user's field, and explain cross-field topics in plain language. The
user may override it for the current conversation by asking for simpler or more
professional language. Never apply the profile to code, PRD, Spec, Plan, Todo,
reports, agent prompts, or other generated files; those stay precise and
professional.

Interview me relentlessly about every aspect of this until we reach a shared understanding. Walk down each branch of the decision tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time, waiting for feedback on each question before continuing. Asking multiple questions at once is bewildering.

If a *fact* can be found by exploring the environment (filesystem, tools, etc.), look it up rather than asking me. The *decisions*, though, are mine — put each one to me and wait for my answer.

Do not act on it until I confirm we have reached a shared understanding.
