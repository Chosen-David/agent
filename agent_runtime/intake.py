"""Structured intake: a bounded confirmation request, not a silent guess.

Absorbs npu_kernel_agent's ``NEEDS_CONFIRMATION`` pattern: when a requirement is
ambiguous, the main AI emits a small set of multiple-choice questions (<=5
options each) instead of assuming an answer, then re-injects the user's answers
and re-checks completeness. ``build_intake`` normalizes the questions;
``apply_intake`` validates answers, applies defaults and reports what is still
missing or rejected. Answers never enter the request's own questions object —
the caller owns where the ``confirmed`` block is persisted.
"""
from __future__ import annotations

INTAKE_SCHEMA = 'intake/v1'
MAX_OPTIONS = 5
MAX_QUESTIONS = 20


class IntakeError(ValueError):
    pass


def _normalize_question(item):
    if not isinstance(item, dict):
        raise IntakeError('each question must be an object')
    qid = item.get('id')
    if not isinstance(qid, str) or not qid.strip():
        raise IntakeError('question requires a nonempty string id')
    text = item.get('question')
    if not isinstance(text, str) or not text.strip():
        raise IntakeError(f'question {qid} requires nonempty text')
    options = item.get('options')
    if not isinstance(options, list) or not options:
        raise IntakeError(f'question {qid} requires at least one option')
    if len(options) > MAX_OPTIONS:
        raise IntakeError(f'question {qid} has more than {MAX_OPTIONS} options')
    if any(not isinstance(option, str) or not option for option in options):
        raise IntakeError(f'question {qid} options must be nonempty strings')
    if len(set(options)) != len(options):
        raise IntakeError(f'question {qid} options must be unique')
    allow_free_text = item.get('allow_free_text', False)
    if type(allow_free_text) is not bool:
        raise IntakeError(f'question {qid} allow_free_text must be a boolean')
    default = item.get('default')
    if default is not None:
        if not isinstance(default, str) or not default:
            raise IntakeError(f'question {qid} default must be a nonempty string')
        if not allow_free_text and default not in options:
            raise IntakeError(f'question {qid} default is not one of its options')
    return {'id': qid.strip(), 'question': text.strip(), 'options': options,
            'allow_free_text': allow_free_text,
            'default': default if default is None else default}


def build_intake(questions):
    """Validate and normalize a question list into a bounded intake request."""
    if not isinstance(questions, list) or not questions:
        raise IntakeError('intake requires a nonempty question list')
    if len(questions) > MAX_QUESTIONS:
        raise IntakeError(f'intake exceeds {MAX_QUESTIONS} questions')
    normalized = [_normalize_question(q) for q in questions]
    ids = [q['id'] for q in normalized]
    if len(set(ids)) != len(ids):
        raise IntakeError('question ids must be unique')
    return {'schema_version': INTAKE_SCHEMA, 'status': 'NEEDS_CONFIRMATION',
            'questions': normalized,
            'scope': 'bounded confirmation request; confirmed answers are held '
                     'separately by the caller and never mutate this request'}


def apply_intake(request, answers=None):
    """Validate answers against a request; re-check completeness after re-injection.

    Returns ``complete`` only when every question is resolved (answered or
    defaulted) and no answer was rejected. ``missing`` lists unresolved question
    ids and ``errors`` lists invalid or unknown answers.
    """
    if not (isinstance(request, dict) and request.get('schema_version') == INTAKE_SCHEMA):
        raise IntakeError('apply_intake requires an intake/v1 request')
    questions = request.get('questions')
    if not isinstance(questions, list):
        raise IntakeError('intake request has invalid questions')
    if answers is not None and not isinstance(answers, dict):
        raise IntakeError('answers must be a mapping of question id -> string')
    answers = answers or {}
    if any(not isinstance(value, str) for value in answers.values()):
        raise IntakeError('answer values must be strings')
    by_id = {q['id']: q for q in questions}
    confirmed, missing, errors = {}, [], []
    for q in questions:
        value = answers.get(q['id'], q['default'])
        if value is None:
            missing.append(q['id'])
            continue
        if not q['allow_free_text'] and value not in q['options']:
            errors.append({'question': q['id'], 'value': value, 'reason': 'not in options'})
            continue
        confirmed[q['id']] = value
    for key in answers:
        if key not in by_id:
            errors.append({'question': key, 'reason': 'unknown question id'})
    complete = not missing and not errors
    return {'schema_version': INTAKE_SCHEMA,
            'status': 'CONFIRMED' if complete else 'NEEDS_CONFIRMATION',
            'complete': complete, 'confirmed': confirmed,
            'missing': missing, 'errors': errors}
