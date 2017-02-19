from collections import defaultdict
assignments = []

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [i+j for i in A for j in B]

rows = 'ABCDEFGHI'
cols = '123456789'
boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
col_units = [cross(rows, c) for c in cols]
square_units = [cross(i, j) for i in ['ABC', 'DEF', 'GHI'] for j in ['123', '456', '789']]
diagonal_units = [[i+j for i, j in zip(rows, cols)], [i+j for i, j in zip(rows, cols[::-1])]]
unitlist = row_units + col_units + square_units + diagonal_units
units = dict((b, [u for u in unitlist if b in u]) for b in boxes)
peers = dict((b, set(sum(units[b], [])) - set([b])) for b in boxes)

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # Find all instances of naked twins
    # Find all boxes with 2 possible values
    doubles = defaultdict(list)
    for k, v in values.items():
        if len(v) == 2:
            doubles[v].append(k)
    # For each matching pairs + in the same units (naked twins)
    # eliminate the naked twins as possibilities for their peers    
    for k, v in doubles.items():
        num_boxes = len(v)
        if num_boxes >= 2:
            pairs = [(v[i], v[j]) for i in range(num_boxes-1)
                     for j in range(i+1, num_boxes)]
            for i, j in pairs:
                mutual_units = [u for u in units[i] if j in u]
                to_eliminate = set(sum(mutual_units, [])) - set([i, j])
                for b in to_eliminate:
                    assign_value(values, b,
                                 values[b].replace(k[0], '').replace(k[1], ''))
    return values

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    values = []
    all_digits = '123456789'
    for c in grid:
        if c == '.':
            values.append(all_digits)
        elif c in all_digits:
            values.append(c)
    assert len(values) == 81
    return dict(zip(boxes, values))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    # find all single-value boxes
    singles = [(k, v) for k, v in values.items() if len(v) == 1]
    for k, v in singles:
        # eliminate its peers
        for p in peers[k]:
            assign_value(values, p, values[p].replace(v, ''))
    return values

def only_choice(values):
    for u in unitlist:
        for d in '123456789':
            d_boxes = [b for b in u if d in values[b]]
            if len(d_boxes) == 1:
                assign_value(values, d_boxes[0], d)
    return values

def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # Use the Eliminate Strategy
        values = eliminate(values)
        # Use the Only Choice Strategy
        values = only_choice(values)
        # Use the Nake Twins Strategy
        values = naked_twins(values)
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if not values:
        return False
    # Choose one of the unfilled squares with the fewest possibilities
    unsolved_boxes = [(v, k) for k, v in values.items() if len(v) > 1]
    if unsolved_boxes == []:
        return values
    choices, min_box = min(unsolved_boxes)
    # Now use recursion to solve each one of the resulting sudokus,
    # and if one returns a value (not False), return that answer!
    for d in choices:
        new_values = values.copy()
        assign_value(new_values, min_box, d)
        ans = search(new_values)
        if ans:
            return ans

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    return search(values)


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
