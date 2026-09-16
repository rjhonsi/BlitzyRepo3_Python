"""Contract tests for the two greeting methods published by :mod:`welcome`.

Seven behaviours are asserted, one test per behaviour: the output of the
for-loop method, the output of the while-loop method, the equality of those two
outputs, the return value of each method, the loop construct each method
actually uses, and the silence of the module's import.  Splitting them this way
is what makes a failure diagnosable from the list of failing tests alone.

The suite deliberately uses the standard library only, so running it adds no
dependency to a project that has none.  ``contextlib.redirect_stdout`` is the
sole seam available: :mod:`welcome` calls the built-in ``print`` directly, and
there is nothing to inject, monkeypatch or configure.
"""

import ast
import contextlib
import importlib
import io
import unittest

# The capture has to begin *before* the suite's first import of the module
# under test, not merely around the reload in the last test.  By the time any
# test runs, ``welcome`` is already in ``sys.modules``, so a regression making
# the import emit output would have leaked its lines into the terminal during
# collection -- printed before a single assertion ran -- and the reload check
# would only report the problem afterwards, against a log already polluted.
# Importing inside the redirect keeps that output captured and turns it into an
# ordinary assertion in ``test_importing_module_prints_nothing``.
_IMPORT_CAPTURE = io.StringIO()
with contextlib.redirect_stdout(_IMPORT_CAPTURE):
    import welcome

IMPORT_OUTPUT = _IMPORT_CAPTURE.getvalue()

# Written out as an explicit literal, with an explicit newline escape, rather
# than assembled from ``welcome.GREETING`` and ``welcome.REPEAT_COUNT``: an
# oracle derived from the very constants it is meant to police cannot detect a
# change to them.  Reading the expectation off disk would be worse still, since
# this repository mixes CRLF and LF endings with no ``.gitattributes`` to
# normalise them, while ``print`` terminates every line with a bare LF.
EXPECTED_OUTPUT = "Welcome to Blitzy\n" * 5


def capture(method):
    """Call ``method`` with stdout redirected and return everything it printed.

    Args:
        method: A zero-argument callable whose printed output is under test.

    Returns:
        str: The exact text ``method`` wrote to stdout, line terminators
        included, or an empty string if it printed nothing.
    """
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        method()
    return stream.getvalue()


def capture_return(method):
    """Call ``method`` with stdout redirected and return its return value.

    Only the value handed back matters here; the redirect exists so that the
    greeting lines produced along the way stay out of the test log.

    Args:
        method: A zero-argument callable whose return value is under test.

    Returns:
        Whatever ``method`` returns.
    """
    with contextlib.redirect_stdout(io.StringIO()):
        return method()


def loop_nodes(module):
    """Return the loop constructs used by each top-level function in ``module``.

    Args:
        module: An imported module whose ``__file__`` identifies its source.

    Returns:
        dict[str, set[str]]: Each top-level function name mapped to the set of
        ``"For"`` and ``"While"`` node type names found within it. Functions
        without loops map to an empty set.
    """
    with open(module.__file__, encoding="utf-8") as source_file:
        tree = ast.parse(source_file.read())
    return {
        node.name: {
            type(inner).__name__
            for inner in ast.walk(node)
            if isinstance(inner, (ast.For, ast.While))
        }
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    }


class WelcomeGreetingContract(unittest.TestCase):
    """The contract :mod:`welcome` owes its callers, one clause per test.

    Both per-method output tests compare against the same ``EXPECTED_OUTPUT``,
    which makes the failure patterns determinate: a defect in one method's
    bound or literal fails that method's output test together with the equality
    test while the other method's test still passes, whereas a defect at a
    shared constant fails both output tests and leaves the equality test green.
    """

    def test_for_loop_method_prints_greeting_five_times(self):
        self.assertEqual(
            capture(welcome.greet_with_for_loop), EXPECTED_OUTPUT
        )

    def test_while_loop_method_prints_greeting_five_times(self):
        self.assertEqual(
            capture(welcome.greet_with_while_loop), EXPECTED_OUTPUT
        )

    def test_both_methods_produce_identical_output(self):
        self.assertEqual(
            capture(welcome.greet_with_for_loop),
            capture(welcome.greet_with_while_loop),
        )

    def test_for_loop_method_returns_none(self):
        self.assertIsNone(capture_return(welcome.greet_with_for_loop))

    def test_while_loop_method_returns_none(self):
        self.assertIsNone(capture_return(welcome.greet_with_while_loop))

    def test_methods_use_their_required_loop_constructs(self):
        self.assertIsNot(
            welcome.greet_with_for_loop, welcome.greet_with_while_loop
        )
        constructs = loop_nodes(welcome)
        self.assertEqual(constructs.get("greet_with_for_loop"), {"For"})
        self.assertEqual(constructs.get("greet_with_while_loop"), {"While"})

    def test_importing_module_prints_nothing(self):
        self.assertEqual(IMPORT_OUTPUT, "")
        # A reload is the only way to observe a second execution of the module
        # body, and so the only check that the guarded call stays guarded.
        self.assertEqual(capture(lambda: importlib.reload(welcome)), "")
