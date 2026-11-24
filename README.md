# ΠRIME — custom code languages

**One audience:** application-security researchers working on source-code obfuscation.

ΠRIME is a local Python workbench for creating a custom code language, digitising an existing notation, applying its rules to supported Python source and verifying exact recovery. Creator generates a definition; Builder imports and refines one. Both feed the same source transformation workflow.

This prototype explores reversible source representations. It is not a production application-protection service, secure encryption, or a new programming runtime. Product–market fit has not been established through user research.

## Open and run in VS Code

You need Python **3.11 or newer** and a modern browser. No Node.js, npm, database, cloud account or API key is needed.

1. Extract this ZIP fully.
2. In VS Code choose **File → Open Folder**, then select the folder containing `app.py`.
3. On Windows, open **Terminal → New Terminal** and enter `./START_WINDOWS.bat`. You can also double-click that file in File Explorer. On macOS/Linux use `bash start.sh` in the project folder.
4. The launcher creates a `.venv`, installs Flask and opens `http://127.0.0.1:5050`. Keep the terminal open; press Ctrl+C to stop.

The first dependency installation requires internet access. The application itself uses local processing without external services.

Manual Windows setup:

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe app.py --open
```

Manual macOS/Linux setup:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py --open
```

If port 5050 is occupied, use `app.py --port 5051 --open` with your virtual environment's Python. Opening the HTML file directly does not run the backend. `requirements-lock.txt` records the exact environment used for validation. The optional `package.json` supports this workspace's preview only; you do not need Node to run the project.

## The product workflow

| Step | What the researcher does |
|---|---|
| Creator | Paste supported Python source, choose token preferences, generate three definitions and refine one. |
| Builder | Import a code-language JSON/CSV file, edit aliases, or label symbols from an existing notation sheet. |
| Define | Choose full-token or names/operators policy, attach optional symbols and lock rules to retain. |
| Transform | Convert source into a framed custom representation using the active definition. |
| Verify | Restore with the matching definition; compare exact source and Python ASTs. |
| Analyse | Inspect repeated aliases, visible literals, output size and actual conversion timings. |
| Reuse | Export/import a language definition independently of its `.prime` document. |

Six starting families: ASCII tokens, word tokens, geometric tokens, dot patterns, frame symbols and angular symbols. The default is compact ASCII tokens. Custom pictures are alternate visual forms for source tokens; they do not change program semantics or create executable instructions.

Use the source fixture selector to try the ten supported programs. See **DEMO_GUIDE.md** for a short walkthrough.

## Language definition and public document

| Output | Contents |
|---|---|
| `*.prime-key.json` | Private definition, original source token spellings, selected policy, aliases and any attached PNG symbols. |
| `*-key.csv` | `source,typing_code` pairs. Source units look like `NAME:print`, `OP:(` or `STRING:"Passed"`. Pictures and full metadata are omitted. Choose the matching policy when importing CSV. |
| `*.prime` | Disguised source and a version/kind/dictionary-fingerprint header; no reverse mapping. |
| Rendering PNG / token reference | A visual representation for inspection; no automatic image-to-source recovery. |

Frames `⟦` and `⟧` separate aliases unambiguously. Literal brackets and backslashes are escaped. The header is `PRIME/1 python <fingerprint>`. The fingerprint identifies a compatible dictionary; it is not a signature, integrity check or authentication mechanism.

Keep definitions for old documents. Mapping or policy edits change their fingerprint; name and picture changes do not. Existing version-1 Python packs remain supported. Only Python source definitions are accepted.

A Builder image requires manual labels: select a source token, draw its symbol or crop it from a notation sheet, assign it, then apply the definition. The image does not reveal a symbol's meaning automatically. Imported rule sets must fit the documented token-mapping model; arbitrary grammar import and automatic decipherment are not implemented.

## Supported Python and correctness

The current subset includes assignments, arithmetic, comparisons, conditions, loops, basic function definitions/calls, collection literals and indexing. Imports, attributes, classes, f-strings, comprehensions and unlisted AST nodes are rejected. Limits: 10,000 source characters and 256 different mapped units.

- **All supported tokens:** maps names/keywords, operators, numbers, strings and comments. Layout remains visible.
- **Names & operators:** maps those categories; string/number literals and comments stay visible.

Source case, Unicode, comments, whitespace and line endings are preserved in recovery. New program tokens require an updated definition. Lock retained aliases while regenerating for an edited program.

The app and benchmark **never execute uploaded source**. They parse it, transform it, restore it and compare it. The test suite separately executes only ten fixed repository fixtures after checking exact source equality. This does not establish behaviour preservation for every possible program.

The disguised representation is not directly runnable Python. Distributing executable transformed applications would require a separate compiler, interpreter or build integration. Support for other programming languages needs appropriate parsers and tests; it is not claimed here.

## Local operation and handling definitions

The app binds to `127.0.0.1` by default. The server processes inputs in memory and does not persist them to a file/database. There is no analytics, external font service, AI request or remote processing. A local address is not a link you can send to another computer; teammates can run the source package themselves.

Saving a language on the device is optional, uses this browser profile's local storage and includes its source token dictionary and attachments. Definitions may include original literals/comments: treat them as source-bearing files. Editor contents are not separately saved by that action. Downloads and ordinary browser/OS behaviour are outside this persistence statement.

A hidden dictionary does not guarantee confidentiality. Patterns, layout, examples and access to the runtime can reveal meaning; someone with the definition can restore source. There are no accounts, invitations, encrypted storage, revocation or production hosting in this prototype.

## Tests and measured dataset

Use the Python executable from your `.venv`:

```sh
python -m unittest discover -s tests -v
python run_experiment.py --repetitions 3
```

The delivered code-only suite contains **30 passing test methods**. The synthetic corpus contains **16 Python fixtures: 10 supported and 6 deliberate invalid/unsupported programs**. With three repetitions the experiment performs **234 trials: 180 valid + 54 negative**. In the delivered run, all 180 recovered exactly with matching ASTs and all 54 expected failures were rejected.

`run_experiment.py` uses only the standard library and writes dataset JSON, measured JSON/CSV, SVG charts and a readable summary under `data/` and `reports/`. Rerunning replaces those generated paths. Timings are actual machine-dependent measurements, not cryptographic strength or user-study results. Negative cases are excluded from the valid-recovery denominator. Teacher acceptance of the synthetic dataset remains pending.

## Visual experience

The revised interface includes an original animated 3D token illustration, a scroll-led explanation with live source/mapping panels, material-like controls and a narrow-screen layout. The illustration uses Canvas 2D with perspective projection, so no additional runtime dependency or Node.js is required. Python still performs every source transformation, recovery check and benchmark.

Read **VISUAL_DESIGN.md** for the ThreeUI reference review, attribution, animation explanation and the Python/browser boundary. The earlier core test results remain applicable; see the current validation report for the additional browser checks.

## Source map

| File | Responsibility |
|---|---|
| `prime/engine.py` | Token parsing, definitions, validation, transformation, recovery and analysis. |
| `prime/dataset.py` | Sixteen synthetic programs and benchmark measurements. |
| `app.py` | Local Flask routes, request checks and launcher. |
| `templates/index.html` | Source-focused workspace. |
| `static/app.js` | Creator/Builder controls, drawing/cropping, file handling and charts. |
| `static/styles.css` | Responsive visual design and print styles. |
| `static/experience.js` | Original token sculpture, motion controls and scroll-led presentation; no source translation. |
| `tests/test_engine.py` | Engine/API/data and trusted-fixture verification. |
| `run_experiment.py` | Reproducible corpus and result exports. |

Read **SCOPE.md**, **COURSEWORK_NOTES.md**, **FUNCTIONS.md** and **reports/VALIDATION.md** for the agreed audience, methods and evidence. This package is an assisted starting implementation; each teammate must understand, develop and explain their own technical contribution. A GitHub repository and real development history still need to be created by the team.
