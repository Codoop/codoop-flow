---
name: codoop-init
description: Inspect an existing repository or create selected empty project directories, then initialize or refresh codoop-flow configuration and existing-page UI snapshots. Use when setting up codoop-flow, when existing backend/web/desktop/mobile directories use custom names, when a standalone client lives at the repository root, or when starting a new empty multi-project repository.
---

# Codoop Init

Initialize codoop-flow from the repository that exists or the empty project the
user explicitly asks to create. Use only these system project types: `backend`,
`web`, `desktop`, and `mobile`.

Locate the absolute directory containing this `SKILL.md` as `$SKILL` before
running the plugin-level Runtime commands below. Every host that installs the
whole plugin (Codex, Claude Code, Cursor, ...) keeps the Runtime at
`$SKILL/../../runtime/codoop-flow/`.

## Configuration location

Default to `<repo-root>/.codoop-flow/codoop_flow.toml`. Before reading existing
preferences, reuse an explicit `--config` or run the Runtime's
`codoop.py config-path` from the target repository (also works in subdirectories).
It prefers the new location and falls back to root `codoop_flow.toml`. If both
exist, report the selected path; do not merge their settings.

For ordinary setup omit `--config`: the Runtime migrates a lone root config to
the new location, preserving settings and unknown fields. Keep an explicitly
requested custom config path by passing it unchanged. Project paths remain
relative to `target_repo`, as does a relative `worktree_root`; moving the config
never moves application directories. A relative `target_repo` in the default
config locations is anchored at the project root, not the invoking subdirectory.
The config is local; `.codoop-flow/ui-snapshots/` is versioned project data.

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

## User Role

Preserve an existing explicit `user_role` unless the user asks to change it.
For a new config or a config without this setting, ask after resolving output
language, one plain-language question at a time. Offer: `developer` (研发 / 工程师),
`product_manager` (产品经理), `designer` (设计师), `operations` (运营 / 市场 / 销售),
`founder` (管理者 / 创业者), and `general` (普通用户 / 其他行业). Pass the answer as
`--user-role <role>`.

`user_role` changes only the live conversation: use normal professional language
within that role's field, and explain cross-field topics in plain language. It
does not measure ability. An explicit request such as “说简单点” or “讲专业一点”
overrides it for the current conversation. Never apply it to code, PRD, Spec,
Plan, Todo, reports, agent prompts, or other generated files; those stay precise
and professional.

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
  --output-language <language> \
  --user-role <role> \
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
  --output-language <language> \
  --user-role <role> \
  --project-path web=web \
  --project-path mobile=mobile \
  --create-project-dirs
```

This creates each selected directory with only `.gitkeep`. Do not generate
framework files, package manifests, build files, source code, or runnable
scaffolding. Refuse to overwrite a non-empty project directory.

## Inventory existing pages

After setup, read [UI snapshot rules](references/ui-snapshots.md). Inspect the
configured web/desktop/mobile projects, identify their existing page types and
create the index and representative self-contained HTML baselines under
`<repo-root>/.codoop-flow/ui-snapshots/`. On every later init, inspect route/page
changes and reuse unchanged baselines; refresh only added or changed pages and
those affected by shared layout/styles. Confirm deletions in source before cleanup.

Open the actual UI and generated HTML for comparison where available. Record
unverified/missing pages when runtime or tools are unavailable; do not call
source-only reconstructions verified. Skip empty and backend-only projects,
without generating an application just to capture it. Report capture counts and
unfinished pages. The setup CLI alone performs configuration, not UI capture.

## Verify

Read the resulting `codoop_flow.toml` and report the mapping, output language,
and user role in plain language.
Confirm that every path is relative and real, no unselected project was
created, and `docs/tickets/{pending,in_progress,done,failed}/` exists.
Confirm the config file is listed in the repository `.gitignore`; setup adds it
automatically because the config holds per-developer choices that must not be
committed. Tell the user the config stays local so teammates' settings never
clash. Confirm the snapshot directory is not ignored; snapshots follow the normal
project commit workflow, separately from the personal config.
