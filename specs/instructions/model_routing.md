# Feature: model_routing

> Description: Which model each Purlin skill runs on. Every skill names its tier in its own front
>   matter, a project gives each tier a model in `.purlin/routing.json`, and a skill whose tier
>   names a model other than the session's runs as a subagent on that model. No script decides:
>   `references/formats/routing_format.md` is the one home of the tables, the hand-off, the
>   escalation and the hand-off message, every routed skill opens on a line that points at it, and
>   the agent definition points at it once.
> Scope: references/formats/routing_format.md, skills/, agents/purlin.md
> Stack: markdown, Claude Code skill and agent definitions
> Highest-Rule: 10
> Highest-Proof: 14

## Rules

- RULE-1: Each skill but `route` names one tier in its front matter, `tier: fast`, `tier: balanced` or `tier: performance`, the tier the format's table gives it, and `route` names none
- RULE-2: The format gives each tier its default model: `fast` is `haiku`, `balanced` is `sonnet` and `performance` is `opus`
- RULE-3: Each skill that names a tier opens, before its first `## ` heading, on one line naming `references/formats/routing_format.md` and "The hand-off"
- RULE-4: The hand-off names where the tier and the model are read and what is started: the `skills` entry of `.purlin/routing.json` before the skill's own `tier:`, the `tiers` of `.purlin/routing.local.json` before those of `.purlin/routing.json`, and a `purlin:purlin` subagent on that model where it is not the session's
- RULE-5: The hand-off says a run handed over by the hand-off does not route again, and that with no `.purlin/routing.json`, or with `"enabled": false`, every skill runs in this session
- RULE-6: The format says `spec`, `spec-from-code` and `sign` run in this session, because each stops to ask the person, and that the person switches the session's model with `/model`
- RULE-7: The format says a build of one rule takes the tier one above its own when that rule's tests failed in its last run or the audit read its test weak, and never takes a tier above `performance`
- RULE-8: The format gives the hand-off message, a fenced block whose lines open on `Command:`, `Goal:`, `Model:`, `Context:`, `Previous:`, `Read:`, `Rules:` and `Return:`, in that order
- RULE-9: The agent definition has a part `Model routing` naming `references/formats/routing_format.md` and "The hand-off", and does not restate the hand-off message; the format says the model in an `@ai(...)` tag is not routed
- RULE-10: A session that runs a skill whose tier names another model starts a subagent on that model

## Proof

- PROOF-1 (RULE-1): The tier in the front matter of each of the ten skills other than `route` is the one the format's table "The two tables" gives that skill, and `skills/route/SKILL.md` has no `tier:` line in its front matter; the check lists no skill
- PROOF-2 (RULE-1): The same check on a copy of the test skill whose front matter reads `tier: performance` lists exactly `test`
- PROOF-3 (RULE-2): The format's table of tiers holds exactly three rows: `fast` with `haiku`, `balanced` with `sonnet` and `performance` with `opus`
- PROOF-4 (RULE-3): Each of the ten skills that names a tier holds, before its first `## ` heading, one line naming both `references/formats/routing_format.md` and `"The hand-off"`; the check lists no skill
- PROOF-5 (RULE-3): The same check on a copy of the test skill with that line taken out lists exactly `skills/test/SKILL.md`
- PROOF-6 (RULE-4): The format's part "The hand-off" names `.purlin/routing.json`, `skills`, `tier:`, `.purlin/routing.local.json`, `tiers`, `purlin:purlin` and `subagent`, the sentence naming `skills` and `tier:` names `skills` first, and the sentence naming `.purlin/routing.local.json` and `.purlin/routing.json` names the local file first
- PROOF-7 (RULE-5): The format's part "The hand-off" holds a sentence with both `handed over` and `does not route again`, and a sentence with `.purlin/routing.json`, `"enabled": false` and `in this session`
- PROOF-8 (RULE-6): One sentence of the format holds `spec`, `spec-from-code`, `sign` and `in this session`, and one sentence holds `/model`
- PROOF-9 (RULE-7): The format's part "Escalation" holds a sentence with `purlin:build`, `one tier up`, `failed` and `weak`, and a sentence with `never above` and `performance`
- PROOF-10 (RULE-8): The format's part "The hand-off message" holds a fenced block whose lines open, in order, on `Command:`, `Goal:`, `Model:`, `Context:`, `Previous:`, `Read:`, `Rules:` and `Return:`
- PROOF-11 (RULE-8): The same check on a copy of the format with every line opening on `Goal:` taken out reports `Goal:` missing
- PROOF-12 (RULE-9): The part `Model routing` of `agents/purlin.md` names `references/formats/routing_format.md` and `"The hand-off"`, and no line of `agents/purlin.md` opens on `Previous:`
- PROOF-13 (RULE-9): One sentence of the format holds both `@ai(` and `is not routed`
- PROOF-14 (RULE-10): On the sample lab with a `.purlin/routing.json` giving `fast` the model `haiku`, a session on `claude-sonnet-5-5` with the plugin is given `Run the tests of sample_intake with purlin:test. Work only in this folder.`; its transcript holds a start of a subagent whose model is `haiku` @ai(claude-sonnet-5-5)
