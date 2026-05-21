---
name: minimax-docx
metadata:
  version: "4.0.0"
  category: document-processing
  status: stable
  author: MiniMaxAI
  sources:
    - "ECMA-376 Office Open XML File Formats"
    - "GB/T 9704-2012 Layout Standard for Official Documents"
    - "IEEE / ACM / APA / MLA / Chicago / Turabian Style Guides"
    - "Springer LNCS / Nature / HBR Document Templates"
description: >
  Unified DOCX skill — create, template-apply, edit/fill, read, repair, and compare Word
  documents. CREATE / GENERATE / DRAFT / WRITE triggers include “write a report”, “draft a
  proposal”, “make a contract”, “生成 Word”, “写文档”, “做个 DOCX”. APPLY_TEMPLATE triggers
  include “套模板”, “match this format”, “按学校模板排版”, “改成公文格式”. READ / REPAIR
  triggers include “read this DOCX”, “extract text”, “why does this Word look wrong”, “修目录”,
  “修页眉页脚”. Use this skill for formal Word deliverables and DOCX diagnosis; do not use it for
  PDF / PPT tasks or for casual plain-text drafting with no DOCX output.
triggers:
  - Word
  - docx
  - document
  - 文档
  - Word文档
  - 报告
  - 合同
  - 公文
  - 套模板
  - 排版
  - 修目录
  - 修页眉页脚
---

# minimax-docx

Replace `<skill_dir>` with the actual skill path shown by the loader.

Unified DOCX skill. `SKILL.md` is the dispatch layer. Pick the route that matches the user’s intent,
read that route guide, then go straight into execution. Do not front-load every task with the full
evidence/backend/acceptance waterfall.

## Environment gates — MANDATORY before any execution

> ⛔ **STEP 0 (BLOCKING). Before any other tool call, you MUST invoke the shell tool to run the
> environment check script for the route you're about to take. This is non-negotiable. Do not skip,
> do not assume, do not infer from OS.** The check ships in two dialects — `env_check.sh` for Linux
> container / macOS / WSL, and `env_check.ps1` for Windows PowerShell 5.1+ — and is the single
> authority on whether the required dependencies are present.
>
> Use the agent runtime's shell tool (e.g. `mcp_inner.matrix.bash.v1` or the equivalent in your
> runtime) to run **one** of the commands below — picked by route — as the very first action after
> route selection:
>
> ```bash
> # macOS / Linux / WSL
> # Read routes only (READ_CONTENT / READ_STRUCTURE / COMPARE_TWO_DOCX):
> bash <skill_dir>/scripts/env_check.sh --level read
>
> # READ_RENDERED route:
> bash <skill_dir>/scripts/env_check.sh --level render
>
> # CREATE_DOCX / APPLY_TEMPLATE / EDIT_FILL_DOCX / REPAIR_LAYOUT routes:
> bash <skill_dir>/scripts/env_check.sh --level full
> ```
>
> ```powershell
> # Windows (PowerShell 5.1+ shipped with Windows, or pwsh 7+)
> # Read routes:
> powershell -ExecutionPolicy Bypass -File <skill_dir>\scripts\env_check.ps1 -Level Read
>
> # READ_RENDERED route:
> powershell -ExecutionPolicy Bypass -File <skill_dir>\scripts\env_check.ps1 -Level Render
>
> # CREATE / APPLY_TEMPLATE / EDIT / REPAIR routes:
> powershell -ExecutionPolicy Bypass -File <skill_dir>\scripts\env_check.ps1 -Level Full
> ```
>
> Both dialects emit the same `[OK] / [FAIL] / Status: READY|NOT READY` lines and the same exit
> codes (0 = ready, 1 = NOT READY, 2 = bad CLI args), so the route may be gated on either one.
>
> If the script exits non-zero, **stop and report** which dependency is missing — do not silently
> fall back to a degraded path (e.g. raw `pandoc` or `python-docx` for a CREATE_DOCX request). The
> script first run will also print a one-line setup hint when something is missing.

First-run convenience (installs missing pieces where it can; **not** a substitute for the per-route
gate above):

```bash
# macOS / Linux / WSL
bash <skill_dir>/scripts/setup.sh
```

```powershell
# Windows — do NOT run setup.sh under git-bash / MSYS / Cygwin; it will refuse and exit 2.
powershell -ExecutionPolicy Bypass -File <skill_dir>\scripts\setup.ps1
```

### Read gate

Required before: `READ_CONTENT`, `READ_STRUCTURE`, `COMPARE_TWO_DOCX`.

```bash
# macOS / Linux / WSL
bash <skill_dir>/scripts/env_check.sh --level read
```

```powershell
# Windows
powershell -ExecutionPolicy Bypass -File <skill_dir>\scripts\env_check.ps1 -Level Read
```

Requires: `python3` (or `python` / `py -3` on Windows), `unzip` (or `tar.exe` / `Expand-Archive`
on Windows 10+), UTF-8 locale or UTF-8 console code page (chcp 65001), executable scripts
(no Mark-of-the-Web on Windows — `setup.ps1` will unblock them).

(The skill loader also runs this gate at load time, but you should still invoke it explicitly —
loader-time success does not prove the runtime container still has the tools.)

### Render gate

Required before: `READ_RENDERED`. Includes all read-level checks plus:

```bash
# macOS / Linux / WSL
bash <skill_dir>/scripts/env_check.sh --level render
```

```powershell
# Windows
powershell -ExecutionPolicy Bypass -File <skill_dir>\scripts\env_check.ps1 -Level Render
```

Requires (in addition to read): `soffice` / `soffice.exe`, `pdftoppm` (or `pdftocairo` on Windows).

If the render gate fails, stop and report. Do not silently fall back to structure-only reads.

### Full gate

Required before: `CREATE_DOCX`, `APPLY_TEMPLATE`, `EDIT_FILL_DOCX`, `REPAIR_LAYOUT`.

```bash
# macOS / Linux / WSL
bash <skill_dir>/scripts/env_check.sh --level full
```

```powershell
# Windows
powershell -ExecutionPolicy Bypass -File <skill_dir>\scripts\env_check.ps1 -Level Full
```

Requires (in addition to render): `dotnet` >= 9, `pandoc`, `zip` (or `Compress-Archive` on Windows),
dotnet project built.

If the full gate fails, stop and report. Do not attempt generation with missing dependencies. In
particular, **do not "downgrade" the request to a one-shot `pandoc <md> -o <docx>`** — that is
explicitly disallowed by Operational Rule §3 below.

### Cross-platform path & temp-dir convention

The route guides under `docs/` and `references/` were written for *nix shells. When you execute on
Windows, do these substitutions consistently:

| In the example | Windows substitute |
|---|---|
| `<skill_dir>/scripts/foo.sh` | `<skill_dir>\scripts\foo.ps1` (every `.sh` has a `.ps1` peer) |
| `python3 <skill_dir>/scripts/foo.py` | `python <skill_dir>\scripts\foo.py` (the `.py` files are cross-platform) |
| `/tmp/minimax-docx-<thing>` | `$env:TEMP\minimax-docx-<thing>` |
| `bash <skill_dir>/scripts/setup.sh` | `powershell -ExecutionPolicy Bypass -File <skill_dir>\scripts\setup.ps1` |
| forward slashes in paths | backslashes; quote any path containing spaces |

Never invoke a `.sh` script through git-bash on Windows — `setup.sh` will refuse to install
anything on `MINGW*/MSYS*/CYGWIN*` and exit 2, telling you to switch to `powershell.exe` / `pwsh.exe`.

## Operational rules — read before doing anything

> **0. Run the env gate via the shell tool first.** See "Environment gates" above. No tool call
> from this skill may execute before the route's `env_check.sh --level <gate>` (or
> `env_check.ps1 -Level <Gate>` on Windows) returned exit 0. If the runtime does not expose a
> shell-execution tool, stop and tell the user the skill cannot run here.

> **1. Dispatch by user intent, not by backend.**
>
> Start with the shortest route choice:
>
> - creating a new formal Word deliverable -> `CREATE_DOCX`
> - preserving content but changing template / institutional style -> `APPLY_TEMPLATE`
> - editing an existing DOCX in place -> `EDIT_FILL_DOCX`
> - reading text / structure / rendered pages -> matching read route
> - fixing visible defects -> `REPAIR_LAYOUT`
> - comparing two DOCX files -> `COMPARE_TWO_DOCX`
>
> Read `docs/router.md` only to settle the route. Do not read `docs/evidence.md`, `docs/backends.md`,
> and `docs/acceptance.md` before route selection.

> **2. For generation routes, choose style family / recipe before backend.**
>
> The old benchmarked generation core stays in this skill. For `CREATE_DOCX` and `APPLY_TEMPLATE`,
> the first substantive decision is the visual system, not the backend. Reuse these files as the
> generation core:
>
> - `references/typography_guide.md`
> - `references/design_principles.md`
> - `references/cjk_typography.md`
> - `scripts/dotnet/MiniMaxAIDocx.Core/Samples/AestheticRecipeSamples*.cs`
>
> These are not optional decoration. They are the quality-preserving recipe layer.

> **3. Backend comes after route + recipe — and never `pandoc` for `CREATE_DOCX`.**
>
> - `D` is the default write backend for formal DOCX creation, template application, and most edits.
> - `S` is only for OpenXML graph work beyond the builtin CLI surface.
> - `X` is only for deterministic local XML patch / inspection work.
> - ⛔ Formal `CREATE_DOCX` is **never** routed to a one-shot `pandoc <md> -o <docx>`. That bypasses
>   typography / recipe selection / dotnet rendering and ships a low-fidelity file. If the
>   environment gate (Step 0) reports `dotnet` missing, **stop and report** — do not silently
>   downgrade to pandoc.
> - If a chosen backend gate fails, stop and report it. Do not silently switch.

> **4. Rendered acceptance is a post-write gate, not a pre-dispatch hop.**
>
> For template, layout, TOC, multi-section, header/footer, and page-number work, finish the write
> first, then run rendered acceptance from `docs/acceptance.md` / `docs/rendered-delivery.md`.

> **5. Keep DOCX execution inside this skill.**
>
> Do not bounce rendered diagnosis to another skill. Do not treat raw XML string replace as a valid
> editing strategy. Do not use `readlink`, `$0`, or shell path tricks in skill docs; use `<skill_dir>` only.

> **6. DOCX→PDF is native to this skill.**
> If the user asks to convert an existing Word/DOCX document to PDF while
> preserving layout, do it here via `python3 <skill_dir>/scripts/docx_to_pdf.py`
> (or `soffice --headless --convert-to pdf` as fallback), then verify the PDF.
> Do not route DOCX→Markdown/HTML→PDF for a preservation task: DOCX already
> carries page geometry, sections, headers/footers, fields, numbering, and table
> layout. HTML/PDF belongs to redesign/recomposition after native render fails
> or when explicitly requested.

## Routes — pick one, then read that guide

### WRITE / GENERATE a DOCX

| Intent | Guide | What happens next |
|---|---|---|
| **CREATE_DOCX** — author a new report / proposal / contract / memo / thesis / 公文 | `docs/task-create.md` | normalize source -> choose recipe family -> choose `D`/`S` -> write -> acceptance |
| **APPLY_TEMPLATE** — preserve content but move into a template / institutional visual system | `docs/task-apply-template.md` | choose template mode -> align recipe family -> read only the needed structure -> choose `D`/`S` -> write -> strict rendered acceptance |
| **EDIT_FILL_DOCX** — mutate content in an existing DOCX while keeping it the same document | `docs/task-edit-fill.md` | choose edit mode -> choose `X`/`D`/`S` -> mutate -> acceptance |

### READ / DIAGNOSE / REPAIR a DOCX

| Intent | Guide | Primary truth |
|---|---|---|
| **READ_CONTENT** — summarize / quote / retrieve text | `docs/task-read-content.md` | content |
| **READ_STRUCTURE** — inspect styles / sections / numbering / TOC / comments / revisions | `docs/task-read-structure.md` | structure |
| **READ_RENDERED** — inspect what the pages actually look like | `docs/task-read-rendered.md` | rendered + structure |
| **REPAIR_LAYOUT** — fix page-level defects | `docs/task-repair-layout.md` | rendered -> structure -> rendered |
| **COMPARE_TWO_DOCX** — explain before/after or source/template differences | `docs/task-compare-two-docx.md` | content + structure + rendered |

## Deep docs — only after the route is clear

| File | Use when |
|---|---|
| `docs/router.md` | settle route choice |
| `docs/evidence.md` | the selected route needs truth-source clarification |
| `docs/backends.md` | the selected route needs backend arbitration |
| `docs/acceptance.md` | you are ready to validate deliverables |
| `docs/rendered-delivery.md` | rendered issue report shape is required |

## Generation core references

Use these after `CREATE_DOCX` / `APPLY_TEMPLATE` is selected:

| File | Role |
|---|---|
| `references/scenario_a_create.md` | create-from-scratch mechanics |
| `references/scenario_c_apply_template.md` | template transfer and multi-section rules |
| `references/typography_guide.md` | font pairings, sizes, spacing, page layout, table rules |
| `references/design_principles.md` | visual judgment rules when exact specs are missing |
| `references/cjk_typography.md` | CJK fonts, 字号, mixed-script rules, 公文 defaults |
| `scripts/dotnet/MiniMaxAIDocx.Core/Samples/AestheticRecipeSamples*.cs` | benchmarked recipe families; choose one instead of inventing values |

## Runtime shorthands

```bash
# macOS / Linux / WSL
CLI="dotnet run --project <skill_dir>/scripts/dotnet/MiniMaxAIDocx.Cli --"
TMPDIR_DOCX="${TMPDIR:-/tmp}"
```

```powershell
# Windows PowerShell
$CLI = "dotnet run --project <skill_dir>\scripts\dotnet\MiniMaxAIDocx.Cli --"
$TmpDocx = $env:TEMP
```

Common commands (substitute `$TMPDIR_DOCX` / `$TmpDocx` for the literal `/tmp` examples elsewhere
in `docs/`):

```bash
$CLI analyze --input in.docx --json
$CLI diff --before before.docx --after after.docx
$CLI merge-runs --input out.docx
$CLI validate --input out.docx --xsd <skill_dir>/assets/xsd/wml-subset.xsd
$CLI validate --input out.docx --business
$CLI validate --input out.docx --gate-check <skill_dir>/assets/xsd/business-rules.xsd
python3 <skill_dir>/scripts/docx_to_pdf.py --input in.docx --output "$TMPDIR_DOCX/docx-render.pdf"
python3 <skill_dir>/scripts/render_docx_pages.py in.docx --output-dir "$TMPDIR_DOCX/docx-pages"
```

On Windows substitute `python3` -> `python`, forward slashes -> backslashes, and `$TMPDIR_DOCX` ->
`$env:TEMP`. The underlying `.py` scripts use `tempfile.TemporaryDirectory` and
`Path(...).expanduser().resolve()`, so they do not care which slash style you pass in.

## Structural non-negotiables

- `w:p` = `pPr` -> runs
- `w:r` = `rPr` -> text-like children
- `w:tbl` = `tblPr` -> `tblGrid` -> rows
- `w:body` ends with `sectPr`
- heading styles need `OutlineLevel`
- direct formatting contamination must be stripped unless explicitly preserved
- template and multi-section work must preserve section graph, `titlePg`, and per-section headers/footers

## Out of scope

- PDF / PPT deliverables -> use `minimax-pdf` / `minimax-pptx`
- casual plain-text drafting with no DOCX output
- pretending a Word-authored DOCX can be safely round-tripped through pandoc for formal output
