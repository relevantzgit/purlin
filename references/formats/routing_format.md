# Routing format

> Format-Version: 1

Model routing gives each Purlin skill a tier and each tier a model, so a skill that runs a script
and reads its output does not spend what a skill that writes rules spends. Each skill names its
tier in its own front matter, the project gives each tier a model in `.purlin/routing.json`, and
the session runs a skill whose tier names another model as a subagent on that model. No script
decides. This page is the one home of the tables, the file, the hand-off, the escalation and the
hand-off message; `purlin:route` writes the file.

## The two tables

Each skill's tier is the `tier:` line of its front matter, `skills/<name>/SKILL.md`:

| Skill | Tier | Where it runs |
|-------|------|---------------|
| `status` | `fast` | A subagent on the tier's model, where that is not the session's |
| `drift` | `fast` | A subagent on the tier's model, where that is not the session's |
| `test` | `fast` | A subagent on the tier's model, where that is not the session's |
| `build` | `balanced` | A subagent on the tier's model, where that is not the session's |
| `init` | `balanced` | A subagent on the tier's model, where that is not the session's |
| `anchor` | `balanced` | A subagent on the tier's model, where that is not the session's |
| `audit` | `performance` | A subagent on the tier's model, where that is not the session's |
| `spec` | `performance` | This session |
| `spec-from-code` | `performance` | This session |
| `sign` | `performance` | This session |

`route` names no tier and runs in this session.

Each tier's default model, the name Claude Code gives the slot:

| Tier | Model |
|------|-------|
| `fast` | `haiku` |
| `balanced` | `sonnet` |
| `performance` | `opus` |

The tier names say the size of the work, not the provider. In Claude Code `haiku`, `sonnet` and
`opus` are slots a gateway may fill with another provider's models; another harness names its own
models in `tiers`.

## The file

`.purlin/routing.json` is committed and the team's:

```json
{
  "schema": "purlin-routing/1",
  "enabled": true,
  "tiers": { "fast": "haiku", "balanced": "sonnet", "performance": "opus" },
  "skills": { "build": "performance" }
}
```

| Field | Required | What it holds |
|-------|----------|---------------|
| `schema` | yes | `purlin-routing/1` |
| `enabled` | yes | `true` routes; `false` runs every skill in this session |
| `tiers` | yes | Each tier's model. A tier left out takes its default |
| `skills` | no | A skill whose tier in this project differs from its front matter, and that tier |

`.purlin/routing.local.json` holds `tiers` alone and is one person's: a person whose models differ
writes theirs there, and git ignores it.

A file that cannot be read, names a tier other than the three, or gives a tier no model is not
used: say which, run the skill in this session, and name `purlin:route setup` as the fix.

## The hand-off

Each skill that names a tier opens on a line naming this part. Before anything else:

1. With no `.purlin/routing.json`, or with `"enabled": false`, every skill runs in this session
   and nothing below applies.
2. A run handed over by the hand-off does not route again: its message says the model is chosen.
3. The tier: the `skills` entry of `.purlin/routing.json` for this skill where there is one,
   before the skill's own `tier:`. Then "Escalation" below, for a build of one rule.
4. The model: the tier's entry in the `tiers` of `.purlin/routing.local.json` where there is one,
   before the `tiers` of `.purlin/routing.json`, before the default.
5. Say the line `<skill>: <tier> (<model>). <reason>`, the reason `Default for <skill>`,
   `Set for <skill> in .purlin/routing.json` or the escalation's.
6. Where that model is this session's, or the skill runs in this session, go on here.
7. Otherwise start a `purlin:purlin` subagent on that model, the way the harness starts work on
   another model, with the hand-off message below. Report what it returns, and stop. A question it
   hands back is the person's: ask it, then continue the same run with the answer.

`spec`, `spec-from-code` and `sign` run in this session, because each stops to ask the person more
than once. Where their tier names a model other than the session's, say once that the person can
switch this session's model with `/model`, and go on.

The model in an `@ai(...)` tag is not routed: it is the model that proof's test runs on.

## Escalation

`purlin:build` of one rule builds one tier up when that rule's tests failed in its last run, or
the audit read its test weak, as the status gives both. It goes one tier at a time and never above
`performance`. The
reason is `Its tests failed in the last run` or `The audit read its test weak`. Escalation lasts
for that run and that rule alone, changes no file, and applies to no other skill.

## The hand-off message

The whole message a subagent starts with. It holds no conversation: what it needs is in the files
it names.

```
Purlin hand-off
Command:  purlin:<skill> <arguments>
Goal:     <the rule's own sentence from the spec, or the person's request in one line>
Model:    <model> (<tier>). Why: <the reason from step 5>
Context:  <one or two lines: what the person asked and what was decided>
Previous: <skill> on <model> (<tier>): <passed | failed | weak>; <one-line cause>, or none
Read:     <the spec>; <the test file>; <the evidence file>; any other file, by path
Rules:    The model is chosen; do not route again. If the person must answer, stop and return the question.
Return:   Up to 5 lines: result, files changed, commits, left to do, and the paths that hold the detail.
          Anything that exists nowhere else, such as open questions or choices you made: add it as Notes.
```

## The session

The session reads each request and runs `spec`, `spec-from-code` and `sign` itself, so it runs on
the `balanced` model. `purlin:route setup` writes this into the project's Claude Code settings,
keeping every other setting:

```json
{ "agent": "purlin:purlin", "model": "sonnet" }
```

It writes `.claude/settings.json`, or `.claude/settings.local.json` where the models are one
person's. `purlin:route off` takes the two out. A `--model` given when a session starts, or
`/model` in it, wins for that session.

## Limits

- The hand-off is a step the session follows, not code: nothing forces it, and nothing but the
  line in step 5 records it.
- `purlin:route setup` starts no model, so a model the harness does not know fails at the first
  skill that names it.
- A subagent starts with its own instructions and the hand-off message, so each hand-off loads a
  context of its own. On a small change a hand-off can cost more than the smaller model saves.
