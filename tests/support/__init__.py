"""Reusable helpers for the FlaskDash test suite.

The modules here deliberately contain *no* pytest fixtures; fixtures live in
``tests/conftest.py``.  Keeping pure helpers separate makes them importable by
tests without pulling in application state.
"""
