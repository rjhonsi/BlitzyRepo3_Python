"""Two separately callable methods that print the ``GREETING`` banner.

Both print ``GREETING`` exactly ``REPEAT_COUNT`` times and produce identical
output; they differ only in the loop construct used to repeat it.  Importing
this module emits nothing, so the caller decides when the greeting is printed.
"""

# Naming the text and the count once, rather than inlining them in both loop
# bodies, is what keeps the two methods in step: one source of truth for each.
GREETING = "Welcome to Blitzy"
REPEAT_COUNT = 5


def greet_with_for_loop():
    """Print ``GREETING`` exactly ``REPEAT_COUNT`` times using a ``for`` loop.

    ``range(REPEAT_COUNT)`` leaves the iteration count to the interpreter, so
    the loop can neither run short nor overshoot, and ``_`` marks the loop
    variable as deliberately unused -- the values iterated over are irrelevant,
    only the number of repetitions matters.
    """
    for _ in range(REPEAT_COUNT):
        print(GREETING)


def greet_with_while_loop():
    """Print ``GREETING`` exactly ``REPEAT_COUNT`` times with a ``while`` loop.

    The output is identical to :func:`greet_with_for_loop`'s -- same text, same
    number of lines.  Termination is the property to watch here: the strict
    ``<`` bound together with the unconditional increment yields exactly
    ``REPEAT_COUNT`` iterations and no more.
    """
    counter = 0
    while counter < REPEAT_COUNT:
        print(GREETING)
        counter += 1


# Guarded so that importing this module stays silent; the block exists only so
# the module also works as a script, calling both methods in turn.
if __name__ == "__main__":
    greet_with_for_loop()
    greet_with_while_loop()
