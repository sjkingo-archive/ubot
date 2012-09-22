
def update_modes(mode_set, line):
    """Parses the MODE line given and updates the mode_set - note this modifies
    the set inplace."""

    op = None
    for i in line:
        if i in ['+', '-']:
            op = i
            continue
        elif i.isalpha():
            if op is None:
                # discard, invalid modeline
                continue
            if op == '+':
                mode_set.add(i)
            else:
                mode_set.remove(i)
