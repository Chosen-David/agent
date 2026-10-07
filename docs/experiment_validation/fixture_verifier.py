"""Explicit trusted adapter for this repository's bounded synthetic test only.

Do not use this as an acceptance adapter for arbitrary projects or code.
"""
from tests.test_result_validation import independent_verify as verify
