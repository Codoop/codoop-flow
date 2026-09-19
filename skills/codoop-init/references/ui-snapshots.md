# Project UI snapshots

Read this reference when init inventories existing screens, ticket prepares a
visual preview, or execute changes a user-visible page or shared UI dependency.
The agent inspects/renders the application and authors HTML; the Runtime only
checks paths and fingerprints. CLI setup alone does not capture pages.

## Location and ownership

Use `<checkout>/.codoop-flow/ui-snapshots/index.json` and
`<checkout>/.codoop-flow/ui-snapshots/pages/<page-id>.html`. For init/ticket,
`checkout` is the target project's current checkout; for execute it is the
isolated worktree, **not** `config.target_repo`. Never write to the plugin cache.
Use stable lowercase hyphenated IDs prefixed by platform, e.g. `web-orders`.

Snapshots are versioned with their implementation, not deployed-state claims.
Ignore only `.codoop-flow/codoop_flow.toml`, not `.codoop-flow/`. Preserve user
Git rules; report a broad ignore that prevents tracking snapshots instead of
force-adding. Keep new init/ticket baseline files as ordinary working-tree
changes for the project's normal commit workflow; do not silently commit them
with a ticket-only promotion. Uncommitted snapshots do not enter new worktrees.

A ticket's `preview.html` stays in its ticket directory as a proposed design.
Never overwrite the implementation baseline with proposed or merely approved UI.

## Index (schema_version 1)

Keep a compact `pages` object keyed by ID. Example shape (replace placeholders
with real paths and tool-produced hashes, never save illustrative hash strings):

```json
{
  "schema_version": 1,
  "pages": {
    "web-orders": {
      "name": "Orders",
      "project": "web",
      "entry": "/orders",
      "snapshot": ".codoop-flow/ui-snapshots/pages/web-orders.html",
      "sources": {
        "web/src/pages/orders.tsx": "<sha256>",
        "web/src/layout.tsx": "<sha256>",
        "web/src/theme.css": "<sha256>"
      },
      "snapshot_sha256": "<sha256>",
      "revision": "<git HEAD at inspection>",
      "evidence": "Rendered /orders and compared the offline HTML; mock orders",
      "viewport": [1280, 800],
      "status": "verified",
      "reason": ""
    }
  }
}
```

`status` is `verified`, `stale`, or `unverified`. Unverified entries may omit
unknown evidence, viewport, hashes or snapshot; include the reason. A source-only
reconstruction is unverified until compared to the actual rendered interface.
On refresh failure keep the previous HTML, mark the entry stale with a reason,
and list it as unfinished. Do not label it synchronized or delete it because
runtime/login access failed. Confirm route removal in source before deleting its
entry and snapshot. Preserve a damaged index before rebuilding; never reset it
silently to an empty object.

`revision` is provenance, not the sole cache key. Store repository-relative file
paths and SHA-256 hashes in `sources`, covering the page, its transitive local
components, public layout, styles/themes, visual assets and route/build manifests
that determine its appearance. No source text or real customer data in the index.

## Cheap validity checks

Resolve `$RUNTIME` to the plugin's `runtime/codoop-flow` directory. Use explicit
`--repo` so checks never accidentally inspect another checkout:

```bash
python3 "$RUNTIME/codoop.py" snapshots check --repo <checkout> web-orders
python3 "$RUNTIME/codoop.py" snapshots fingerprint --repo <checkout> \
  web/src/pages/orders.tsx web/src/layout.tsx web/src/theme.css \
  .codoop-flow/ui-snapshots/pages/web-orders.html
```

`check` returns `{page_id, reusable, reasons}` and exits 1 when unavailable,
invalid or changed; it does not mutate files. `fingerprint` prints a path→hash
object: source hashes go into `sources`, the HTML hash into `snapshot_sha256`.

Read the compact index first, then only the needed page and dependencies. A
successful hash check proves only listed files are unchanged. Inspect route
manifests and relevant changed/untracked UI paths for newly added dependencies;
when coverage is uncertain, inspect the affected module instead of trusting the
cache. Shared layout/theme changes invalidate all recorded dependent pages.
Do not use HEAD alone: hashes also detect uncommitted changes and branch switches.

## Capture / refresh

1. Identify existing pages and their actual entry points from configured client
   projects. Inventory all existing page types during init; during ticket inspect
   only the relevant page(s). Skip dependencies and build output. One representative
   dynamic detail page is enough, not one per record or every possible state.
2. Follow the page's components/styles and view the running UI when available.
   Fingerprint the inputs before reconstruction. If tools/runtime are unavailable,
   record the limitation; do not invent a verified baseline.
3. Recreate the page in a self-contained HTML file with its navigation, title,
   surrounding content, layout, typography, spacing, colors and component styles.
   Use mock content and inline required styles/assets so it opens offline. Avoid
   real API calls, credentials, private records, external tracking, dependencies
   and production-code changes. Native screens may be represented in HTML with
   platform limitations recorded in evidence. Preserve accessibility basics.
4. Open the HTML and compare it with the existing UI at the representative viewport;
   check applicable narrow layouts. A screenshot alone is not an editable HTML
   baseline. Source inspection alone cannot establish visual verification.
5. Recheck source fingerprints; if inputs changed during capture, repeat the affected
   work. Write HTML and then its index entry via temporary files and replacement,
   keeping unrelated entries. Publish `verified` only after visual comparison and
   matching input/output hashes; interrupted writes must fail the next hash check.
6. Report added/refreshed/reused/removed/unverified counts. Do not rebuild valid
   pages just to update timestamps. Empty/backend-only projects skip capture.

## Ticket and delivery boundaries

For a visual ticket, copy/recreate the relevant existing page into the ticket's
single `preview.html`, then apply the proposed changes there. Preserve the product
context; make only the ticket's key path and necessary states interactive with
mock data. For a new page reuse the existing product layout/components; design
independently only when there is no interface foundation. If actual UI and written
design guidance conflict, preserve current UI by default and surface the mismatch.
Record page IDs, revision and relevant input fingerprints in `spec.md`. Visually
check the preview and key interactions before review. If blocked, describe the
missing evidence rather than presenting a guess as a faithful reproduction.

After implementation verification and review, execute refreshes affected baselines
from the actual result, including UI fixes without a preview. Changes to shared UI
refresh dependent pages; inaccessible ones remain explicitly stale. Snapshots are
separate from `ui_capture` screenshots and never satisfy that gate.

Write only inside the isolated worktree and include snapshots in the normal finish
commit before worktree removal. Finish creates a ticket branch, not a merge: never
copy those baselines into another branch. Merge index entries together with their
corresponding source and HTML; resolve conflicts per page and recheck hashes.
Failure retains worktree evidence but must not publish a new baseline elsewhere.
