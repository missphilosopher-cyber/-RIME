# ΠRIME scope — 24 November 2026

**Audience:** application-security researchers investigating source-code obfuscation.

**Task:** create or import a custom code language, apply it to supported source, and verify that the original can be restored correctly.

**Positioning:** ΠRIME is a custom code-language workbench for source obfuscation and analysis.

**Creator mode:** start from supported source code and preferences, generate candidate token definitions, edit and lock rules, then transform and verify.

**Builder mode:** formalise an existing notation or token dictionary, check it for ambiguous aliases or missing source units, refine it and apply it through the same pipeline. Symbol-image meanings are assigned by the user.

Both modes serve the same audience and task. There is one source workspace and one Python engine. The interface starts with source code and transformation controls.

Current support is a defined Python subset and lossless token representations. A professional deployment runtime, arbitrary grammar support, additional programming languages, accounts/invitations and encrypted storage are outside the implemented scope.

**Proposed value to validate:** a reusable, editable custom language definition, source-aware application, separate restoration dictionary, and inspectable correctness/pattern results in one local workflow. This is a product hypothesis, not proven market fit, novelty or security superiority.

Potential research questions for target users: How do they currently create custom transformations? Which rule imports do they need? Is exact restoration useful in their workflow? Would they reuse ΠRIME across programs? What practical benefit would make them choose it over their present tools?

The interface, Python engine, corpus and package documentation follow this scope. The earlier standalone team briefing has not been edited; this scope note supersedes its broader audience assumptions. Its reserved Prototype page remains untouched.
