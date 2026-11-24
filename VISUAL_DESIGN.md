# Visual direction and implementation

ΠRIME remains a custom code-language workbench for application-security researchers. This revision changes its presentation; Python still owns the actual source transformation and evaluation.

## Reference review

ThreeUI was the requested visual reference. The review covered its catalogue/navigation and selected pages across landing pages, hero sections, backgrounds, buttons, text/motion treatments, technical UI and CSS navigation. Its catalogue displayed 858 components; this was a broad review, not an exhaustive inspection of every component or variant. Some live examples loaded, some exposed public preview media, and some premium renderers were gated or unavailable.

Useful references reviewed:

- [ThreeUI catalogue](https://threeui.com/browse?sort=recent)
- [Agent AI](https://threeui.com/landing-pages/agent-ai-landing-page): a product story structured as interactive chapters.
- [Photonic Interconnect](https://threeui.com/landing-pages/photonic-interconnect-landing-page): oversized typography, a central sculptural subject and technical explanation.
- [Animated Top Dock](https://threeui.com/css/animated-top-dock): focused navigation and tactile control states.
- [Shader Buttons](https://threeui.com/buttons/star-portal): material-like surfaces and interaction feedback.
- [ASCII Field](https://threeui.com/backgrounds/ascii-page-transition): typography used as spatial material.
- [Diagnostics Panel](https://threeui.com/ui-elements/diagnostics-panel): restrained spatial illustrations for technical interfaces.

ThreeUI is acknowledged as design inspiration. No ThreeUI template, paid source package, renderer code, shader or image was imported. The Π sculpture, token scene, layer diagram, page structure and CSS treatment in this package were written for ΠRIME.

## What changed

The opening now uses large typography, an original dimensional Π sculpture and real token labels from the active definition. Source and Language controls change the illustration. Verify recovery calls the same Python verification used by the workbench; successful or mismatched results are reflected in the hero. Pending rule edits disable that control.

A scroll-led section explains source, definition and recovery. Its layered panels show the current workspace's real source, aliases and representation. Scrolling changes emphasis only. The workbench retains both Creator and Builder, with a restrained dark palette, material-like buttons and clear input controls. Dataset charts retain actual measurements.

The illustration is not a model of cryptographic strength, an encryption animation or evidence of protection. An illustrated form changing shape does not itself transform source code.

## Why Canvas rather than a large 3D framework

`static/experience.js` renders mathematical 3D geometry onto Canvas 2D. It needs no additional package, WebGL capability, CDN, React, npm or build step. This makes the local Python project easier to run, inspect and explain. Source-code rendering and user controls remain ordinary HTML/CSS.

The renderer uses:

1. A polygon describing the Π outline, extruded into front, back and side faces.
2. Rotations about X, Y and Z to change the viewing angle.
3. Perspective projection: a point farther from the camera appears smaller.
4. Depth sorting to draw distant faces before near faces.
5. Clipped gradients and edges to create a material-like surface.
6. Interpolation between a solid form and orbiting fragments for the language view.
7. Labels from Python's active mapping; these labels never decode or execute source.

Students should trace `rotate`, `project`, `piFaces` and `paintScene`, then explain how the visual layer differs from the Python transformation. The code comments identify this boundary.

## Python remains the core

| Python responsibility | Browser responsibility |
|---|---|
| Parse/validate supported source with ast and tokenize | Collect inputs and display results |
| Generate/import/validate language definitions | Render interactive notation controls |
| Apply mappings with exact token boundaries | Animate geometry and scroll emphasis |
| Restore source and compare exact text/ASTs | Display Python's verification result |
| Compute frequencies, timing, bytes and benchmark summaries | Draw charts and export browser-rendered pictures |

`publishVisualState` in `static/app.js` sends a small local DOM event containing the active dictionary and its verification state to `experience.js`. This is a presentation event inside the page; it sends no data to an external service. The browser does not substitute for the Python codecs.

## Motion, usability and limits

The Pause motion control stops the canvas animation. The initial state respects `prefers-reduced-motion`; users can explicitly choose to play it. The renderer limits pixel density/frame rate and stops drawing while offscreen or when the document is hidden. Navigation uses ordinary links; there is no scroll hijacking or mandatory introduction.

The narrow layout was checked in a 390 × 844 CSS-pixel iframe, with 375 pixels of inner content width after the desktop scrollbar. Horizontal document overflow was corrected and exact recovery was tested there. This is a browser layout test, not a physical-phone or touch-performance evaluation. Reduced-motion preference handling is implemented; a full operating-system preference/accessibility audit was not performed.

## Student requirements still outstanding

The teacher requires meaningful Python logic, understanding of every used technology, individual technical contributions, real GitHub development history and comparison with 2–3 relevant existing solutions. This visual pass does not substitute for that work. The synthetic source dataset still needs teacher acceptance. The separate Word briefing's reserved Prototype page remains untouched.
