---
name: codoop-init
description: Inspect an existing repository or create selected empty project directories, then initialize or refresh codoop-flow configuration. Use when setting up codoop-flow, when existing backend/web/desktop/mobile directories use custom names, when a standalone client lives at the repository root, or when starting a new empty multi-project repository.
---

# Codoop Init

Initialize codoop-flow from the repository that exists or the empty project the
user explicitly asks to create. Use only these system project types: `backend`,
`web`, `desktop`, and `mobile`.

Locate the absolute directory containing this `SKILL.md` as `$SKILL` before
running the plugin-level Runtime commands below. Every host that installs the
whole plugin (Codex, Claude Code, Cursor, ...) keeps the Runtime at
`$SKILL/../../runtime/codoop-flow/`.

## Output Language

Preserve an existing explicit `output_language` unless the user asks to change
it. When it is missing or a new config is being created, ask which output
language to use before running setup. Ask one plain-language question, recommend
the current conversation language, mention `"auto"`, and accept any BCP 47
language tag. Common choices include `"zh-CN"`, `"zh-TW"`, `"en"`, `"ja"`,
`"ko"`, `"es"`, `"fr"`, `"de"`, `"pt-BR"`, `"it"`, `"ru"`, `"ar"`, `"hi"`,
`"id"`, `"tr"`, `"vi"`, and `"th"`; do not present this as a closed list.
Pass the answer as `--output-language <language>`.
Use the configured language for user-facing prose. `"auto"` follows the user's
current language. An explicit request for the current task overrides the config.

## Existing project

1. Locate the Git root and inspect top-level directories, build manifests,
   source files, and existing project docs. Ignore dependencies and generated
   output.
2. Map each owned system project type to its real relative directory. Preserve
   custom names: `backend=server`, `web=admin-console`, and similar mappings are
   valid. If one client is the repository itself, map its type to `.`.
3. Omit projects outside this repository. An external backend may appear in
   client contracts, but it is not a `backend` project path.
4. Ask one plain-language question only when repository evidence cannot resolve
   a project type or ownership boundary.
5. Do not move, rename, wrap, or create application directories in this mode.

Run the sibling setup CLI with one mapping per owned project:

```bash
python3 "$SKILL/../../runtime/codoop-flow/codoop.py" setup <repo-root> \
  --config <repo-root>/codoop_flow.toml \
  --output-language <language> \
  --project-path backend=server \
  --project-path web=admin-console
```

## New project

Use this mode only when the user explicitly asks to create a new project. If
the requested project types are missing, ask which of `backend`, `web`,
`desktop`, and `mobile` they need.

1. Use the fixed directory name matching each selected type. Do not ask for or
   accept custom names.
2. Create only selected types; never create every platform by default.
3. Initialize Git in the target directory when needed.
4. Run setup with `--create-project-dirs`:

```bash
python3 "$SKILL/../../runtime/codoop-flow/codoop.py" setup <repo-root> \
  --config <repo-root>/codoop_flow.toml \
  --output-language <language> \
  --project-path web=web \
  --project-path mobile=mobile \
  --create-project-dirs
```

This creates each selected directory with only `.gitkeep`. Do not generate
framework files, package manifests, build files, source code, or runnable
scaffolding. Refuse to overwrite a non-empty project directory.

## Verify

Read the resulting `codoop_flow.toml` and report the mapping and output language
in plain language.
Confirm that every path is relative and real, no unselected project was
created, and `docs/tickets/{pending,in_progress,done,failed}/` exists.
Confirm the config file is listed in the repository `.gitignore`; setup adds it
automatically because the config holds per-developer choices that must not be
committed. Tell the user the config stays local so teammates' settings never
clash.
