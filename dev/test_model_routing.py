"""What model routing must hold: `specs/instructions/model_routing.md`.

Each skill's tier, the format's two tables, the line each routed skill opens
on, the hand-off, the escalation, the hand-off message and the agent's pointer
are read as text. A copy with one thing changed is read through `copy_without`
or by passing the changed text, and the files on disk are never touched. The
last proof starts a real session and runs only where the run sets `PURLIN_AI`.
"""

import json
import os
import re

import pytest

import skill_checks
from sign_project import git, write
from skill_checks import (copy_without, flat, sentences_with, skill_path,
                          under_heading)

FORMAT = 'references/formats/routing_format.md'
AGENT = 'agents/purlin.md'
HAND_OFF = '"The hand-off"'
ROUTED = ('anchor', 'audit', 'build', 'drift', 'init', 'sign', 'spec',
          'spec-from-code', 'status', 'test')
TIERS = ('fast', 'balanced', 'performance')


def front_matter(text):
    """The front matter of a skill: the lines between its two `---`."""
    found = re.match(r'---\n(.*?)\n---\n', text, re.S)
    return found.group(1) if found else ''


def tier_of(text):
    """The `tier:` a skill's front matter names, or None."""
    found = re.search(r'^tier: *(\S+) *$', front_matter(text), re.M)
    return found.group(1) if found else None


def table_tiers(text):
    """`{skill: tier}` from the format's table of skills."""
    part = under_heading(text, 'The two tables')
    return dict(re.findall(r'^\| `([\w-]+)` \| `(%s)` \|' % '|'.join(TIERS),
                           part, re.M))


def wrong_tiers(texts, table):
    """Each skill of `{name: text}` whose tier is not the table's; `route`
    is wrong where it names any."""
    wrong = [name for name, text in texts.items()
             if name != 'route' and tier_of(text) != table.get(name)]
    if 'route' in texts and tier_of(texts['route']) is not None:
        wrong.append('route')
    return sorted(wrong)


def skill_texts():
    return {name: skill_checks.read(skill_path(name))
            for name in ROUTED + ('route',)}


# purlin: model_routing PROOF-1
def test_each_skill_names_the_tier_the_table_gives_it():
    table = table_tiers(skill_checks.read(FORMAT))
    assert sorted(table) == sorted(ROUTED)
    assert wrong_tiers(skill_texts(), table) == []


# purlin: model_routing PROOF-2
def test_a_test_skill_on_another_tier_is_listed():
    table = table_tiers(skill_checks.read(FORMAT))
    texts = skill_texts()
    texts['test'] = texts['test'].replace('tier: fast', 'tier: performance')
    assert wrong_tiers(texts, table) == ['test']


# purlin: model_routing PROOF-3
def test_the_format_gives_each_tier_its_default_model():
    part = under_heading(skill_checks.read(FORMAT), 'The two tables')
    rows = re.findall(r'^\| `(%s)` \| `([\w.-]+)` \|$' % '|'.join(TIERS),
                      part, re.M)
    assert rows == [('fast', 'haiku'), ('balanced', 'sonnet'),
                    ('performance', 'opus')]


def opening(text):
    """The text of a skill before its first `## ` heading."""
    found = re.search(r'^## ', text, re.M)
    return text[:found.start()] if found else text


def without_hand_off_line():
    """Each routed skill whose opening holds no line naming both the format
    and "The hand-off"."""
    missing = []
    for name in ROUTED:
        rel = skill_path(name)
        lines = opening(skill_checks.read(rel)).splitlines()
        if not [line for line in lines
                if FORMAT in line and HAND_OFF in line]:
            missing.append(rel)
    return missing


# purlin: model_routing PROOF-4
def test_each_routed_skill_opens_on_the_hand_off():
    assert without_hand_off_line() == []


# purlin: model_routing PROOF-5
def test_a_test_skill_without_the_line_is_listed():
    rel = skill_path('test')
    line = [line for line in skill_checks.read(rel).splitlines()
            if FORMAT in line and HAND_OFF in line][0]
    with copy_without(rel, line):
        assert without_hand_off_line() == ['skills/test/SKILL.md']


def hand_off():
    return flat(under_heading(skill_checks.read(FORMAT), 'The hand-off'))


def split(text):
    return re.split(r'(?<=\.)\s+(?=[A-Z`*])', text)


def first_of(sentence, one, other):
    return sentence.index(one) < sentence.index(other)


# purlin: model_routing PROOF-6
def test_the_hand_off_names_where_the_tier_and_model_are_read():
    text = hand_off()
    for name in ('.purlin/routing.json', '`skills`', '`tier:`',
                 '.purlin/routing.local.json', '`tiers`', '`purlin:purlin`',
                 'subagent'):
        assert name in text, name
    tier = [s for s in split(text) if '`skills`' in s and '`tier:`' in s]
    assert tier and first_of(tier[0], '`skills`', '`tier:`')
    model = [s for s in split(text)
             if '.purlin/routing.local.json' in s
             and '.purlin/routing.json`' in s.replace(
                 '.purlin/routing.local.json`', '')]
    assert model and first_of(model[0], '.purlin/routing.local.json',
                              '`.purlin/routing.json`')


# purlin: model_routing PROOF-7
def test_a_handed_over_run_and_no_routing_stay_in_this_session():
    sentences = split(hand_off())
    assert [s for s in sentences
            if 'handed over' in s and 'does not route again' in s]
    assert [s for s in sentences
            if '.purlin/routing.json' in s and '"enabled": false' in s
            and 'in this session' in s]


# purlin: model_routing PROOF-8
def test_the_asking_skills_run_in_this_session():
    assert sentences_with(FORMAT, ('`spec`', '`spec-from-code`', '`sign`',
                                   'in this session'))
    assert sentences_with(FORMAT, ('/model',))


# purlin: model_routing PROOF-9
def test_a_build_escalates_one_tier_and_never_above_performance():
    part = split(flat(under_heading(skill_checks.read(FORMAT),
                                    'Escalation')))
    assert [s for s in part if all(name in s for name in (
        'purlin:build', 'one tier up', 'failed', 'weak'))]
    assert [s for s in part if 'never above' in s and 'performance' in s]


MESSAGE = ('Command:', 'Goal:', 'Model:', 'Context:', 'Previous:', 'Read:',
           'Rules:', 'Return:')


def message_problems(text):
    """The fields of the hand-off message missing from, or out of order in,
    the fenced block of the format's part "The hand-off message"."""
    part = under_heading(text, 'The hand-off message')
    found = re.search(r'```\n(.*?)\n```', part, re.S)
    if not found:
        return ['no fenced block']
    opens = [line.split()[0] for line in found.group(1).splitlines()
             if line.split() and line.split()[0] in MESSAGE]
    missing = ['%s missing' % name for name in MESSAGE if name not in opens]
    return missing or ([] if opens == list(MESSAGE) else ['out of order'])


# purlin: model_routing PROOF-10
def test_the_hand_off_message_has_its_eight_lines_in_order():
    assert message_problems(skill_checks.read(FORMAT)) == []


# purlin: model_routing PROOF-11
def test_a_message_without_its_goal_is_reported():
    text = '\n'.join(line for line in skill_checks.read(FORMAT).splitlines()
                     if not line.startswith('Goal:'))
    assert message_problems(text) == ['Goal: missing']


# purlin: model_routing PROOF-12
def test_the_agent_points_at_the_hand_off_and_does_not_restate_it():
    text = skill_checks.read(AGENT)
    part = flat(under_heading(text, 'Model routing'))
    assert FORMAT in part and HAND_OFF in part
    assert not [line for line in text.splitlines()
                if line.lstrip().startswith('Previous:')]


# purlin: model_routing PROOF-13
def test_the_model_of_an_ai_tag_is_not_routed():
    assert len(sentences_with(FORMAT, ('@ai(', 'is not routed'))) == 1


ROUTING = {'schema': 'purlin-routing/1', 'enabled': True,
           'tiers': {'fast': 'haiku', 'balanced': 'sonnet',
                     'performance': 'opus'}}
RUN_THE_TESTS = ('Run the tests of sample_intake with purlin:test. Work only '
                 'in this folder.')


def subagent_models(transcript):
    """The model of each subagent the session's transcript started."""
    models = []
    with open(transcript, encoding='utf-8') as handle:
        for line in handle:
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if event.get('type') != 'assistant':
                continue
            for part in (event.get('message') or {}).get('content') or []:
                if (isinstance(part, dict) and part.get('type') == 'tool_use'
                        and part.get('name') in ('Agent', 'Task')):
                    models.append((part.get('input') or {}).get('model'))
    return models


# purlin: model_routing PROOF-14
@pytest.mark.skipif(not os.environ.get('PURLIN_AI'),
                    reason='Started by purlin:test --all, which sets PURLIN_AI')
def test_a_session_hands_the_test_skill_to_a_haiku_subagent(
        tmp_path, no_real_model):
    import sample_lab
    root = sample_lab.for_a_session(tmp_path, audit_first=False)
    write(os.path.join(root, '.purlin', 'routing.json'), json.dumps(ROUTING))
    git(root, 'add', '-A')
    git(root, 'commit', '-q', '-m', 'chore: model routing')
    output = sample_lab.session(root, RUN_THE_TESTS, no_real_model)
    assert 'haiku' in subagent_models(os.path.join(output, 'transcript.jsonl'))
