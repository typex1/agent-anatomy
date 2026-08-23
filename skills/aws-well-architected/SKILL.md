---
name: aws-well-architected
description: Reviewing designs against the AWS Well-Architected pillars. Use when asked to review an architecture, design doc, or infrastructure choice.
---

# AWS Well-Architected review

When asked to review an architecture or infrastructure decision:

1. Load `references/pillars.md` from this skill for the six pillars and
   their key questions.
2. Assess the design against each pillar that applies; skip pillars with
   nothing to say rather than padding.
3. Output format: one short paragraph per applicable pillar, each ending
   with a single concrete recommendation.
4. Flag any single point of failure explicitly, even if not asked.

This skill demonstrates *bundled resources*: the detailed pillar
reference lives in `references/` and is only read when the skill is
active — compare with `commit-message`, which is instructions only.
