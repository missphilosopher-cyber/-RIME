# Validation — source-code scope

Validated on 24 November 2026 using Python 3.12.14, Flask 3.1.3, Linux and Chrome. This report covers the revised local code-language prototype.

## Automated verification

`python -m unittest discover -s tests -v`: **30 test methods passed**.

The suite checks six token families, both policies, exact recovery and AST equality across ten supported programs, Unicode/literal framing boundaries, whitespace/line endings, duplicate/reserved/invisible aliases, prefix-overlapping aliases, locked rules, malformed documents, dictionary mismatch, PNG attachment validation, JSON/CSV import, API nonce/value checks, input/complexity limits, and separation of definitions from public representations.

The API rejects non-program modes and non-Python definitions. The catalog/corpus contain Python source fixtures only. A test checks that audience-selection and symbol-composition controls are absent from the page.

Uploaded programs are not executed. A separate test executes only the ten fixed trusted repository fixtures after verifying exact source recovery; each standard output matched its stored expected output.

JavaScript syntax, Python source compilation, experiment output consistency and chart XML checks passed. The Unix launcher passed `bash -n`. The Windows launcher was retained and reviewed; it was not run on Windows.

## Browser verification

| Action | Observed result |
|---|---|
| Initial page | Source-focused headline, live program representation and Python workspace; no audience/purpose selector. |
| Six token families | Python source recovery and matching ASTs. |
| Edit current disguised document | Exact-recovery mismatch reported for an appended blank line. |
| Builder mode | Source-token import and mapping refinement controls appeared. |
| Duplicate source-token aliases | Explicit uniqueness error; prior active definition remained available. |
| Edit, apply and lock an alias | Custom alias retained through generation. |
| Export/re-import Python definition | Mapping survived and source recovered exactly. |
| Draw a custom source-token symbol | Attached PNG appeared; apply and recovery still passed. |
| Source fixture selector | Loaded P01 program into the source editor. |
| Names/operators policy | Output literal remained visible and recovery passed. |
| Full-token policy | Output literal was mapped and recovery passed. |
| Code-only experiment | 16 fixtures, 180 valid recoveries, 54 expected rejections, 234 total trials. |
| Measured CSV download | 234 actual rows; supported and expected-error results kept separate. |

The edited-document and mapping checks were repeated after replacing animated scrolling with immediate scrolling, which made button targeting stable during browser automation. No application-origin console errors were observed in the final inspected log.

The symbol image-crop implementation and optional local definitions remain available. They were not comprehensively re-tested across image formats or browser storage conditions in this revision. No mobile device, Windows/macOS runtime, cross-browser study, accessibility audit, load test, penetration test, cryptographic analysis or professional-user study was performed.

## Reproducible measurements

`python run_experiment.py --repetitions 3` produced the included `experiment.json`, `measured_trials.csv`, `experiment_charts.svg` and `experiment_summary.md` together. It measured **180/180 exact supported-source recoveries** and **54/54 expected rejections**. Metadata records that run's timestamp/environment; it is separate from the browser run and timings may differ.

These results demonstrate the declared subset and fixture behaviour. They do not establish production source protection, unrestricted language support, execution of transformed programs, security strength or product–market fit. Teacher acceptance of the synthetic dataset is pending.

The package remains local-only. No public hosting, audience permission change or remote GitHub repository was created in this revision. The separate earlier Word briefing has not been edited; SCOPE.md records the narrowed audience and supersedes its broader audience assumptions.

## Visual revision checks — 24 November 2026

The Python engine and dataset were retained. All 30 automated tests passed after the visual revision. Both JavaScript modules passed syntax checks.

Additional real browser checks:

- The dimensional Π scene rendered and showed the active Python mapping.
- Source/Language controls selected distinct presentation states.
- The hero recovery control returned actual exact-source and AST results from Python.
- Appending a blank line to the current representation produced the real mismatch in both the hero and workbench; re-encoding restored consistency.
- Pending key edits disabled hero verification; applying an edited alias and testing recovery succeeded.
- Pause motion changed its pressed state and offered Play motion.
- Scroll navigation exposed the live source/definition/representation panels.
- The benchmark still reported 180 exact supported-input recoveries and 54 expected rejections, across 234 measured trials.
- In a 390 × 844 iframe (375-pixel inner content width), navigation and recovery worked. The final document scroll width matched its 375-pixel content width. This is a narrow browser layout check, not a physical-device test.
- No application-origin browser console errors were observed in the inspected log.

The new experience is original Canvas/CSS code inspired by the requested reference. No paid ThreeUI source/assets were imported. No public deployment or audience permission change was performed.
