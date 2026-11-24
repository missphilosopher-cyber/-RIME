# Function inventory

The Python engine implements custom source representations. The browser provides controls, symbol tools, file handling and visualisation.

## Python functions

| Module | Function | Purpose |
|---|---|---|
| `prime/engine.py` | `check_text` | Validate source type, size and UTF-8 encodability. |
| `prime/engine.py` | `inspect_python` | Parse and check the supported AST subset without execution. |
| `prime/engine.py` | `python_spans` | Find token spans while preserving original gaps. |
| `prime/engine.py` | `required_units` | Extract unique Python category/spelling units. |
| `prime/engine.py` | `_pool` | Construct candidate aliases for the chosen family. |
| `prime/engine.py` | `generate_definition` | Generate unique mappings while preserving locked aliases. |
| `prime/engine.py` | `_check_token` | Reject aliases that violate token framing constraints. |
| `prime/engine.py` | `validate_definition` | Validate the Python definition, policies, aliases and attachments. |
| `prime/engine.py` | `definition_id` | Calculate a mapping compatibility fingerprint. |
| `prime/engine.py` | `audit_definition` | Report counts and observable limitations. |
| `prime/engine.py` | `_escape` | Escape literal framing characters. |
| `prime/engine.py` | `encode` | Transform selected program tokens into framed aliases. |
| `prime/engine.py` | `read_payload` | Check the document header against the active dictionary. |
| `prime/engine.py` | `representation_parts` | Scan framed tokens and escaped literals. |
| `prime/engine.py` | `decode` | Restore original source and validate Python syntax. |
| `prime/engine.py` | `compare_recovery` | Compare exact source, first difference and AST equality. |
| `prime/engine.py` | `analyse` | Count bytes, token occurrences and visible literal characters. |
| `prime/engine.py` | `prompt_style` | Match supported code-token preferences locally. |
| `prime/engine.py` | `position` | Convert token row/column into source character offset. |
| `prime/engine.py` | `flush` | Append accumulated literal pieces. |
| `app.py` | `create_app` | Construct the local Flask application. |
| `app.py` | `protect_local_api` | Flask route, request validation, response handling or application helper; see source. |
| `app.py` | `headers` | Flask route, request validation, response handling or application helper; see source. |
| `app.py` | `invalid` | Flask route, request validation, response handling or application helper; see source. |
| `app.py` | `http_error` | Flask route, request validation, response handling or application helper; see source. |
| `app.py` | `body` | Flask route, request validation, response handling or application helper; see source. |
| `app.py` | `definition` | Flask route, request validation, response handling or application helper; see source. |
| `app.py` | `index` | Flask route, request validation, response handling or application helper; see source. |
| `app.py` | `catalog` | Flask route, request validation, response handling or application helper; see source. |
| `app.py` | `generate` | Flask route, request validation, response handling or application helper; see source. |
| `app.py` | `validate` | Flask route, request validation, response handling or application helper; see source. |
| `app.py` | `import_key` | Flask route, request validation, response handling or application helper; see source. |
| `app.py` | `encode_text` | Flask route, request validation, response handling or application helper; see source. |
| `app.py` | `decode_text` | Flask route, request validation, response handling or application helper; see source. |
| `app.py` | `verify` | Flask route, request validation, response handling or application helper; see source. |
| `app.py` | `benchmark` | Flask route, request validation, response handling or application helper; see source. |
| `app.py` | `corpus` | Flask route, request validation, response handling or application helper; see source. |
| `prime/dataset.py` | `run_benchmark` | Measure synthetic Python fixtures and separate expected errors. |
| `run_experiment.py` | `write_chart` | Write measured medians as a labelled SVG. |
| `run_experiment.py` | `export_experiment` | Save the corpus, raw records, summary and chart. |

## Browser functions

| Function | Responsibility |
|---|---|
| `toast` | Interface state, rendering or event workflow. |
| `status` | Interface state, rendering or event workflow. |
| `api` | Interface state, rendering or event workflow. |
| `on` | Interface state, rendering or event workflow. |
| `requireKey` | Interface state, rendering or event workflow. |
| `kind` | Interface state, rendering or event workflow. |
| `filename` | Interface state, rendering or event workflow. |
| `download` | File export, local definitions or rendering export. |
| `setDirty` | Interface state, rendering or event workflow. |
| `resetTest` | Interface state, rendering or event workflow. |
| `setAnalysis` | Interface state, rendering or event workflow. |
| `updateSourceCount` | Interface state, rendering or event workflow. |
| `unitLabel` | Interface state, rendering or event workflow. |
| `signNode` | Interface state, rendering or event workflow. |
| `renderHero` | Interface state, rendering or event workflow. |
| `renderCandidates` | Interface state, rendering or event workflow. |
| `renderKey` | Interface state, rendering or event workflow. |
| `renderAudit` | Interface state, rendering or event workflow. |
| `adopt` | Call the Python API and update the source workflow. |
| `generate` | Call the Python API and update the source workflow. |
| `encodeCurrent` | Call the Python API and update the source workflow. |
| `renderPaper` | Interface state, rendering or event workflow. |
| `metric` | Interface state, rendering or event workflow. |
| `renderAnalysis` | Display real measurements and token counts. |
| `decodeCurrent` | Call the Python API and update the source workflow. |
| `verifyCurrent` | Call the Python API and update the source workflow. |
| `loadExample` | Interface state, rendering or event workflow. |
| `setMode` | Interface state, rendering or event workflow. |
| `csvCell` | File export, local definitions or rendering export. |
| `mappingCsv` | File export, local definitions or rendering export. |
| `importLanguage` | Call the Python API and update the source workflow. |
| `readSaved` | File export, local definitions or rendering export. |
| `refreshSaved` | File export, local definitions or rendering export. |
| `previewEncoded` | Interface state, rendering or event workflow. |
| `resetDrawing` | Manual symbol drawing or image labelling. |
| `point` | Manual symbol drawing or image labelling. |
| `drawSheet` | Manual symbol drawing or image labelling. |
| `method` | Manual symbol drawing or image labelling. |
| `openDesigner` | Manual symbol drawing or image labelling. |
| `loadSheet` | Manual symbol drawing or image labelling. |
| `cropToSign` | Manual symbol drawing or image labelling. |
| `inkBounds` | Manual symbol drawing or image labelling. |
| `assignSign` | Manual symbol drawing or image labelling. |
| `pictureCanvas` | File export, local definitions or rendering export. |
| `chart` | Display real measurements and token counts. |
| `runBenchmark` | Display real measurements and token counts. |
| `boot` | Interface state, rendering or event workflow. |

Key libraries: Python ast, tokenize, json, csv, hashlib, Counter, statistics.median, perf_counter, base64 and secrets; Flask routes/test client; browser Fetch, Canvas, files and localStorage. The test suite uses unittest and executes only fixed trusted fixtures in a subprocess.

## Presentation event and visual renderer

`publishVisualState` in `static/app.js` passes the active mapping and Python verification state to the presentation layer. It does not encode or decode source.

| Function in `static/experience.js` | Responsibility |
|---|---|
| `rotate` | Geometry/projection, scene drawing, motion scheduling or presentation state; see the commented source. |
| `project` | Geometry/projection, scene drawing, motion scheduling or presentation state; see the commented source. |
| `path` | Geometry/projection, scene drawing, motion scheduling or presentation state; see the commented source. |
| `paintFace` | Geometry/projection, scene drawing, motion scheduling or presentation state; see the commented source. |
| `piFaces` | Geometry/projection, scene drawing, motion scheduling or presentation state; see the commented source. |
| `paintCube` | Geometry/projection, scene drawing, motion scheduling or presentation state; see the commented source. |
| `paintOrbit` | Geometry/projection, scene drawing, motion scheduling or presentation state; see the commented source. |
| `paintTokens` | Geometry/projection, scene drawing, motion scheduling or presentation state; see the commented source. |
| `paintScene` | Geometry/projection, scene drawing, motion scheduling or presentation state; see the commented source. |
| `animate` | Geometry/projection, scene drawing, motion scheduling or presentation state; see the commented source. |
| `schedule` | Geometry/projection, scene drawing, motion scheduling or presentation state; see the commented source. |
| `resize` | Geometry/projection, scene drawing, motion scheduling or presentation state; see the commented source. |
| `updateMotion` | Geometry/projection, scene drawing, motion scheduling or presentation state; see the commented source. |
| `selectPhase` | Geometry/projection, scene drawing, motion scheduling or presentation state; see the commented source. |
| `updateProcess` | Geometry/projection, scene drawing, motion scheduling or presentation state; see the commented source. |

The renderer uses rotation matrices, perspective, depth ordering and gradients. Scroll controls change presentation only.
