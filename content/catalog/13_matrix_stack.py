from collections import defaultdict
from functools import lru_cache

from catalog_lib import problem

MX = "matrix"
ST = "stack"
MS = "monotonic-stack"


def _grid(r, lo=0, hi=9, m=None, n=None):
    m = m or r.randint(1, 5)
    n = n or r.randint(1, 5)
    return [r.ints(n, lo, hi) for _ in range(m)]


@problem(
    slug="set-matrix-zeroes", title="Set Matrix Zeroes", difficulty="Medium", pattern=MX, tags=["Array", "Hash Table", "Matrix"],
    sig="setZeroes(self, matrix: list[list[int]]) -> None", out_arg=0,
    desc="""If a cell of `matrix` is `0`, set its entire row and column to `0`. Do it **in place** and return nothing; the judge checks `matrix`. Try for O(1) extra space.""",
    constraints=["1 ≤ m, n ≤ 200", "-2³¹ ≤ matrix[i][j] ≤ 2³¹ − 1"],
    samples=[([[1, 1, 1], [1, 0, 1], [1, 1, 1]],), ([[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]],)],
    gen=lambda r: (_grid(r, 0, 4),),
    brute=lambda M: (lambda zr, zc: [M[i].__setitem__(j, 0) for i in range(len(M)) for j in range(len(M[0])) if i in zr or j in zc])({i for i, row in enumerate(M) if 0 in row}, {j for j in range(len(M[0])) if any(row[j] == 0 for row in M)}),
    hints=[
        "Zeroing as you scan would spread zeros you created yourself.",
        "First record which rows and columns contain a zero, then apply.",
        "For O(1) space, use the first row and column as the markers, with two flags for whether the first row and column themselves need zeroing.",
    ],
    insight="Record first, apply second; the first row and column can hold the records.",
    time="O(m·n)", space="O(1)",
    pitfalls=["Overwriting markers in the first row or column before using them."],
)
def set_zeroes(matrix):
    m, n = len(matrix), len(matrix[0])
    row0 = any(v == 0 for v in matrix[0])
    col0 = any(matrix[i][0] == 0 for i in range(m))
    for i in range(1, m):
        for j in range(1, n):
            if matrix[i][j] == 0:
                matrix[i][0] = matrix[0][j] = 0
    for i in range(1, m):
        for j in range(1, n):
            if matrix[i][0] == 0 or matrix[0][j] == 0:
                matrix[i][j] = 0
    if row0:
        for j in range(n):
            matrix[0][j] = 0
    if col0:
        for i in range(m):
            matrix[i][0] = 0


@problem(
    slug="rotate-image", title="Rotate Image", difficulty="Medium", pattern=MX, tags=["Array", "Math", "Matrix"],
    sig="rotate(self, matrix: list[list[int]]) -> None", out_arg=0,
    desc="""Rotate the `n × n` matrix 90 degrees clockwise **in place** (no second matrix). Return nothing; the judge checks `matrix`.""",
    constraints=["1 ≤ n ≤ 20", "-1000 ≤ matrix[i][j] ≤ 1000"],
    samples=[([[1, 2, 3], [4, 5, 6], [7, 8, 9]],), ([[5, 1, 9, 11], [2, 4, 8, 10], [13, 3, 6, 7], [15, 14, 12, 16]],)],
    gen=lambda r: (lambda n: (_grid(r, -9, 9, n, n),))(r.randint(1, 5)),
    brute=lambda M: M.__setitem__(slice(None), [list(row) for row in zip(*M[::-1])]),
    hints=[
        "A clockwise rotation equals a transpose followed by reversing each row.",
        "Transpose in place by swapping matrix[i][j] with matrix[j][i] for j > i.",
        "Then reverse every row in place.",
    ],
    insight="Rotation decomposes into two easy in-place steps.",
    time="O(n²)", space="O(1)",
    pitfalls=["Transposing every pair twice (swapping back), by not restricting j > i."],
)
def rotate(matrix):
    n = len(matrix)
    for i in range(n):
        for j in range(i + 1, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    for row in matrix:
        row.reverse()


def _ball_brute(grid):
    m, n = len(grid), len(grid[0])
    out = []
    for start in range(n):
        c = start
        for i in range(m):
            d = grid[i][c]
            nc = c + d
            if nc < 0 or nc >= n or grid[i][nc] != d:
                c = -1
                break
            c = nc
        out.append(c)
    return out


@problem(
    slug="where-will-the-ball-fall", title="Where Will the Ball Fall", difficulty="Medium", pattern=MX,
    tags=["Array", "Matrix", "Simulation"],
    sig="findBall(self, grid: list[list[int]]) -> list[int]",
    desc="""A box is an `m × n` grid of diagonal boards: `1` sends a ball to the right (top-left to bottom-right) and `-1` sends it to the left. One ball is dropped above each column.

A ball gets stuck if it hits a wall or a "V" shape formed by two neighboring boards. Return a list where entry `i` is the column where ball `i` falls out of the bottom, or `-1` if it gets stuck.""",
    constraints=["1 ≤ m, n ≤ 100", "grid[i][j] is 1 or -1"],
    samples=[([[1, 1, 1, -1, -1], [1, 1, 1, -1, -1], [-1, -1, -1, 1, 1], [1, 1, 1, 1, -1], [-1, -1, -1, -1, -1]],), ([[-1]],),
             ([[1, 1, 1, 1, 1, 1], [-1, -1, -1, -1, -1, -1], [1, 1, 1, 1, 1, 1], [-1, -1, -1, -1, -1, -1]],)],
    gen=lambda r: ([[r.choice([1, -1]) for _ in range(n)] for n in [r.randint(1, 6)] for _ in range(r.randint(1, 5))],),
    hints=[
        "Simulate each ball row by row.",
        "In row i at column c, the ball moves to column c + grid[i][c].",
        "It's stuck if that column is outside the box or the neighboring board points the other way.",
    ],
    insight="A direct simulation, O(m) per ball.",
    time="O(m·n)", space="O(n)",
    pitfalls=["Forgetting the V-shape check between neighbors."],
)
def find_ball(grid):
    return _ball_brute(grid)


@problem(
    slug="transpose-matrix", title="Transpose Matrix", difficulty="Easy", pattern=MX, tags=["Array", "Matrix", "Simulation"],
    sig="transpose(self, matrix: list[list[int]]) -> list[list[int]]",
    desc="""Return the transpose of `matrix`: the matrix flipped over its main diagonal, so rows become columns.""",
    constraints=["1 ≤ m, n ≤ 1000", "-10⁹ ≤ values ≤ 10⁹"],
    samples=[([[1, 2, 3], [4, 5, 6], [7, 8, 9]],), ([[1, 2, 3], [4, 5, 6]],)],
    gen=lambda r: (_grid(r, -9, 9),),
    hints=[
        "An m × n matrix becomes n × m.",
        "Entry (i, j) of the result is entry (j, i) of the input.",
        "Build a new n × m matrix and fill it with that rule.",
    ],
    insight="Swap the roles of rows and columns.",
    time="O(m·n)", space="O(m·n)",
    pitfalls=["Transposing in place, which only works for square matrices."],
)
def transpose(matrix):
    return [list(col) for col in zip(*matrix)]


def _life_step(board):
    m, n = len(board), len(board[0])
    nxt = [[0] * n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            live = sum(board[x][y] for x in range(max(0, i - 1), min(m, i + 2)) for y in range(max(0, j - 1), min(n, j + 2))) - board[i][j]
            nxt[i][j] = 1 if live == 3 or (board[i][j] and live == 2) else 0
    return nxt


@problem(
    slug="game-of-life", title="Game of Life", difficulty="Medium", pattern=MX, tags=["Array", "Matrix", "Simulation"],
    sig="gameOfLife(self, board: list[list[int]]) -> None", out_arg=0,
    desc="""Each cell is alive (`1`) or dead (`0`). Using its eight neighbors, all cells update **simultaneously**:

1. A live cell with fewer than two live neighbors dies.
2. A live cell with two or three live neighbors lives.
3. A live cell with more than three live neighbors dies.
4. A dead cell with exactly three live neighbors becomes alive.

Update `board` to the next state in place; the judge checks `board`.""",
    constraints=["1 ≤ m, n ≤ 25"],
    samples=[([[0, 1, 0], [0, 0, 1], [1, 1, 1], [0, 0, 0]],), ([[1, 1], [1, 0]],)],
    gen=lambda r: (_grid(r, 0, 1),),
    brute=lambda b: b.__setitem__(slice(None), _life_step(b)),
    hints=[
        "Updating cells one by one would make later cells see new values instead of old ones.",
        "Encode both states in each cell, e.g. bit 0 = current, bit 1 = next.",
        "First compute every cell's next state into bit 1 using bit 0 of neighbors, then shift every cell right by one.",
    ],
    insight="Two bits per cell give a simultaneous update without a copy.",
    time="O(m·n)", space="O(1)",
    pitfalls=["Reading already-updated neighbors."],
)
def game_of_life(board):
    m, n = len(board), len(board[0])
    for i in range(m):
        for j in range(n):
            live = sum(board[x][y] & 1 for x in range(max(0, i - 1), min(m, i + 2)) for y in range(max(0, j - 1), min(n, j + 2))) - (board[i][j] & 1)
            if live == 3 or (board[i][j] & 1 and live == 2):
                board[i][j] |= 2
    for i in range(m):
        for j in range(n):
            board[i][j] >>= 1


@problem(
    slug="toeplitz-matrix", title="Toeplitz Matrix", difficulty="Easy", pattern=MX, tags=["Array", "Matrix"],
    sig="isToeplitzMatrix(self, matrix: list[list[int]]) -> bool",
    desc="""A matrix is **Toeplitz** if every diagonal from top-left to bottom-right has equal elements. Return `true` if `matrix` is Toeplitz.""",
    constraints=["1 ≤ m, n ≤ 20", "0 ≤ values ≤ 99"],
    samples=[([[1, 2, 3, 4], [5, 1, 2, 3], [9, 5, 1, 2]],), ([[1, 2], [2, 2]],)],
    gen=lambda r: (lambda base, m, n: ([[base[j - i + m] if r.random() < 0.95 else 7 for j in range(n)] for i in range(m)],))(r.ints(12, 0, 3), r.randint(1, 4), r.randint(1, 4)),
    brute=lambda M: all(len({M[i][j] for i in range(len(M)) for j in range(len(M[0])) if j - i == d}) <= 1 for d in range(-len(M), len(M[0]))),
    hints=[
        "Cells on the same diagonal share the value j − i.",
        "Equivalently, every cell must equal its top-left neighbor.",
        "Check matrix[i][j] == matrix[i − 1][j − 1] for all i, j ≥ 1.",
    ],
    insight="Comparing each cell with its top-left neighbor checks all diagonals.",
    time="O(m·n)", space="O(1)",
    pitfalls=["Collecting whole diagonals when a neighbor check suffices."],
)
def is_toeplitz(matrix):
    return all(matrix[i][j] == matrix[i - 1][j - 1] for i in range(1, len(matrix)) for j in range(1, len(matrix[0])))


@problem(
    slug="spiral-matrix-ii", title="Spiral Matrix II", difficulty="Medium", pattern=MX, tags=["Array", "Matrix", "Simulation"],
    sig="generateMatrix(self, n: int) -> list[list[int]]",
    desc="""Return an `n × n` matrix filled with `1, 2, …, n²` in clockwise spiral order, starting from the top-left.""",
    constraints=["1 ≤ n ≤ 20"],
    samples=[(3,), (1,)],
    tests=[(2,), (4,), (5,), (6,)],
    hints=[
        "Walk in the order right, down, left, up, repeating.",
        "Turn when the next cell is outside the matrix or already filled.",
        "Alternatively keep four boundaries (top, bottom, left, right) and shrink them after each side.",
    ],
    insight="Boundary-shrinking simulation fills a spiral in O(n²).",
    time="O(n²)", space="O(1) besides the output",
    pitfalls=["Overwriting cells when the boundaries cross."],
)
def generate_matrix(n):
    M = [[0] * n for _ in range(n)]
    i = j = d = 0
    dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    for v in range(1, n * n + 1):
        M[i][j] = v
        x, y = i + dirs[d][0], j + dirs[d][1]
        if not (0 <= x < n and 0 <= y < n and M[x][y] == 0):
            d = (d + 1) % 4
            x, y = i + dirs[d][0], j + dirs[d][1]
        i, j = x, y
    return M


@problem(
    slug="diagonal-traverse", title="Diagonal Traverse", difficulty="Medium", pattern=MX, tags=["Array", "Matrix", "Simulation"],
    sig="findDiagonalOrder(self, mat: list[list[int]]) -> list[int]",
    desc="""Return all elements of `mat` in zigzag diagonal order: the first diagonal goes up-right, the next goes down-left, and so on (diagonals are the anti-diagonals `i + j = constant`).""",
    constraints=["1 ≤ m, n ≤ 10⁴", "1 ≤ m·n ≤ 10⁴"],
    samples=[([[1, 2, 3], [4, 5, 6], [7, 8, 9]],), ([[1, 2], [3, 4]],)],
    gen=lambda r: (_grid(r, 0, 20),),
    hints=[
        "Cells with the same i + j lie on the same anti-diagonal.",
        "Group cells by i + j, keeping them in increasing row order.",
        "Reverse every even-numbered group (those go up-right), then concatenate.",
    ],
    insight="Grouping by i + j turns the zigzag into simple list reversals.",
    time="O(m·n)", space="O(m·n)",
    pitfalls=["Reversing the wrong parity of diagonals."],
)
def find_diagonal_order(mat):
    groups = defaultdict(list)
    for i, row in enumerate(mat):
        for j, v in enumerate(row):
            groups[i + j].append(v)
    out = []
    for k in range(len(mat) + len(mat[0]) - 1):
        out += groups[k][::-1] if k % 2 == 0 else groups[k]
    return out


# ---------------------------------------------------------------- stacks


def _calc_input(r):
    def expr(depth):
        parts = []
        for k in range(r.randint(1, 3)):
            if k:
                parts.append(r.choice([" + ", " - ", "+", "-"]))
            if depth and r.random() < 0.3:
                parts.append(("-" if r.random() < 0.2 else "") + "(" + expr(depth - 1) + ")")
            else:
                parts.append(str(r.randint(0, 30)))
        return "".join(parts)
    return (expr(2),)


@problem(
    slug="basic-calculator", title="Basic Calculator", difficulty="Hard", pattern=ST, tags=["Math", "String", "Stack", "Recursion"],
    sig="calculate(self, s: str) -> int",
    desc="""Evaluate the expression `s`, which contains non-negative integers, `+`, `-`, parentheses and spaces. `-` may also be unary before a parenthesis (like `-(2 + 3)`). Don't use `eval`.""",
    constraints=["1 ≤ len(s) ≤ 3 × 10⁵", "the expression is valid", "results fit in a 32-bit integer"],
    samples=[("1 + 1",), (" 2-1 + 2 ",), ("(1+(4+5+2)-3)+(6+8)",)],
    tests=[("-(2+3)",), ("1-(     -2)",)],
    gen=_calc_input,
    brute=lambda s: eval(s),
    hints=[
        "Without parentheses, keep a running result and the sign of the next number.",
        "An opening parenthesis starts a new sub-expression; you need to come back to the outer result and sign later.",
        "On '(', push (result, sign) and reset; on ')', finish the inner result and combine: result = pushed_result + pushed_sign × inner.",
    ],
    insight="A stack saves the outer context at each parenthesis.",
    time="O(n)", space="O(n)",
    pitfalls=["Mishandling multi-digit numbers or unary minus before '('."],
)
def calculate(s):
    stack, result, sign, num = [], 0, 1, 0
    for c in s:
        if c.isdigit():
            num = num * 10 + int(c)
        elif c in "+-":
            result += sign * num
            num, sign = 0, (1 if c == "+" else -1)
        elif c == "(":
            stack.append((result, sign))
            result, sign = 0, 1
        elif c == ")":
            result += sign * num
            num = 0
            prev, psign = stack.pop()
            result = prev + psign * result
    return result + sign * num


@problem(
    slug="remove-all-adjacent-duplicates-in-string", title="Remove All Adjacent Duplicates In String", difficulty="Easy", pattern=ST,
    tags=["String", "Stack"],
    sig="removeDuplicates(self, s: str) -> str",
    desc="""Repeatedly remove two adjacent equal letters from `s` until none remain. Return the final string (it is unique).""",
    constraints=["1 ≤ len(s) ≤ 10⁵", "lowercase letters"],
    samples=[("abbaca",), ("azxxzy",)],
    gen=lambda r: (r.word(r.randint(1, 12), "abc"),),
    hints=[
        "Removing a pair can make two new letters adjacent.",
        "Process characters left to right, keeping the surviving characters on a stack.",
        "If the next character equals the top of the stack, pop; otherwise push.",
    ],
    insight="A stack handles cascading removals in one pass.",
    time="O(n)", space="O(n)",
    pitfalls=["Repeatedly scanning the string for pairs (O(n²))."],
)
def remove_duplicates(s):
    st = []
    for c in s:
        if st and st[-1] == c:
            st.pop()
        else:
            st.append(c)
    return "".join(st)


def _logs_input(r):
    n = r.randint(1, 3)
    logs, t, stack = [], 0, []
    calls = 0
    while calls < 6 or stack:
        if stack and (calls >= 6 or r.random() < 0.5):
            logs.append(f"{stack.pop()}:end:{t}")
        else:
            f = r.randint(0, n - 1)
            logs.append(f"{f}:start:{t}")
            stack.append(f)
            calls += 1
        t += r.randint(0, 2)
    return n, logs


@problem(
    slug="exclusive-time-of-functions", title="Exclusive Time of Functions", difficulty="Medium", pattern=ST, tags=["Array", "Stack"],
    sig="exclusiveTime(self, n: int, logs: list[str]) -> list[int]",
    desc="""A single-threaded CPU runs `n` functions (ids `0..n − 1`), possibly recursively. Each log is `"id:start:t"` (the function starts at the **beginning** of time unit `t`) or `"id:end:t"` (it ends at the **end** of time unit `t`).

A function's exclusive time is the total time units it spent running, excluding time spent in functions it called. Return the exclusive time of every function.""",
    constraints=["1 ≤ n ≤ 100", "logs are sorted by time and well-formed"],
    samples=[(2, ["0:start:0", "1:start:2", "1:end:5", "0:end:6"]), (1, ["0:start:0", "0:start:2", "0:end:5", "0:start:6", "0:end:6", "0:end:7"])],
    gen=_logs_input,
    hints=[
        "Only the function on top of the call stack is running at any moment.",
        "Keep the previous event time; when a new event arrives, credit the elapsed time to the function on top.",
        "On start: credit top with t − prev, push, prev = t. On end: credit top with t − prev + 1, pop, prev = t + 1.",
    ],
    insight="A call stack plus a \"previous timestamp\" pointer splits time exactly.",
    time="O(len(logs))", space="O(n)",
    pitfalls=["Forgetting that end times are inclusive (the + 1)."],
)
def exclusive_time(n, logs):
    res, stack, prev = [0] * n, [], 0
    for log in logs:
        f, kind, t = log.split(":")
        f, t = int(f), int(t)
        if kind == "start":
            if stack:
                res[stack[-1]] += t - prev
            stack.append(f)
            prev = t
        else:
            res[stack.pop()] += t - prev + 1
            prev = t + 1
    return res


class _MinStackRef:
    def __init__(self):
        self.items = []

    def push(self, val):
        self.items.append(val)

    def pop(self):
        self.items.pop()

    def top(self):
        return self.items[-1]

    def getMin(self):
        return min(self.items)


def _min_stack_ops(r):
    ops, args, size = ["MinStack"], [[]], 0
    for _ in range(r.randint(3, 14)):
        choice = r.choice(["push", "push", "pop", "top", "getMin"]) if size else "push"
        if choice == "push":
            ops.append("push"); args.append([r.randint(-9, 9)]); size += 1
        else:
            ops.append(choice); args.append([])
            if choice == "pop":
                size -= 1
    return ops, args


@problem(
    slug="min-stack", title="Min Stack", difficulty="Medium", pattern=ST, tags=["Stack", "Design"],
    design=True, cls="MinStack",
    starter="""class MinStack:
    def __init__(self):
        pass

    def push(self, val: int) -> None:
        pass

    def pop(self) -> None:
        pass

    def top(self) -> int:
        pass

    def getMin(self) -> int:
        pass
""",
    desc="""Design a stack that supports `push(val)`, `pop()`, `top()` and `getMin()` (the smallest element in the stack), each in **O(1)** time.

`pop`, `top` and `getMin` are only called on a non-empty stack.""",
    constraints=["-2³¹ ≤ val ≤ 2³¹ − 1", "at most 3 × 10⁴ calls"],
    samples=[(["MinStack", "push", "push", "push", "getMin", "pop", "top", "getMin"], [[], [-2], [0], [-3], [], [], [], []]),
             (["MinStack", "push", "getMin", "push", "getMin"], [[], [5], [], [7], []])],
    gen=_min_stack_ops,
    hints=[
        "Scanning for the minimum is O(n). Store it instead.",
        "The minimum depends on which elements are currently on the stack.",
        "Push pairs (value, minimum so far including this value). getMin reads the top pair's minimum.",
    ],
    insight="Each stack entry remembers the minimum beneath it.",
    time="O(1) per operation", space="O(n)",
    pitfalls=["Keeping a single min variable, which breaks after popping the minimum."],
)
class MinStack(_MinStackRef):
    pass


class _QueueRef:
    def __init__(self):
        self.items = []

    def push(self, x):
        self.items.append(x)

    def pop(self):
        return self.items.pop(0)

    def peek(self):
        return self.items[0]

    def empty(self):
        return not self.items


def _queue_ops(r):
    ops, args, size = ["MyQueue"], [[]], 0
    for _ in range(r.randint(3, 14)):
        choice = r.choice(["push", "push", "pop", "peek", "empty"]) if size else r.choice(["push", "empty"])
        if choice == "push":
            ops.append("push"); args.append([r.randint(1, 9)]); size += 1
        else:
            ops.append(choice); args.append([])
            if choice == "pop":
                size -= 1
    return ops, args


@problem(
    slug="implement-queue-using-stacks", title="Implement Queue using Stacks", difficulty="Easy", pattern=ST, tags=["Stack", "Design", "Queue"],
    design=True, cls="MyQueue",
    starter="""class MyQueue:
    def __init__(self):
        pass

    def push(self, x: int) -> None:
        pass

    def pop(self) -> int:
        pass

    def peek(self) -> int:
        pass

    def empty(self) -> bool:
        pass
""",
    desc="""Implement a first-in-first-out queue using only two stacks (push to top, pop from top, peek, size, empty):

- `push(x)` adds `x` to the back.
- `pop()` removes and gives back the front element.
- `peek()` gives the front element.
- `empty()` tells whether the queue is empty.

`pop` and `peek` are only called on a non-empty queue.""",
    constraints=["1 ≤ x ≤ 9", "at most 100 calls"],
    samples=[(["MyQueue", "push", "push", "peek", "pop", "empty"], [[], [1], [2], [], [], []]),
             (["MyQueue", "empty", "push", "pop", "empty"], [[], [], [5], [], []])],
    gen=_queue_ops,
    hints=[
        "One stack receives pushes; the other serves pops.",
        "Moving every element from the inbox to the outbox reverses their order, putting the oldest on top.",
        "Only move elements when the outbox is empty; each element moves at most once, so operations are amortized O(1).",
    ],
    insight="Two stacks reverse twice, which restores FIFO order.",
    time="Amortized O(1) per operation", space="O(n)",
    pitfalls=["Moving elements back and forth on every operation."],
)
class MyQueue(_QueueRef):
    pass


@problem(
    slug="evaluate-reverse-polish-notation", title="Evaluate Reverse Polish Notation", difficulty="Medium", pattern=ST,
    tags=["Array", "Math", "Stack"],
    sig="evalRPN(self, tokens: list[str]) -> int",
    desc="""Evaluate an arithmetic expression in Reverse Polish Notation. Tokens are integers or the operators `+`, `-`, `*`, `/`. Division truncates toward zero. The expression is always valid and never divides by zero.""",
    constraints=["1 ≤ len(tokens) ≤ 10⁴", "values fit in 32-bit integers"],
    samples=[(["2", "1", "+", "3", "*"],), (["4", "13", "5", "/", "+"],), (["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"],)],
    tests=[(["7", "-2", "/"],), (["42"],)],
    hints=[
        "Numbers wait until an operator needs them.",
        "Push numbers on a stack; an operator pops two, applies itself, and pushes the result.",
        "Mind the operand order (the first pop is the right operand) and truncate division toward zero.",
    ],
    insight="RPN is evaluated with a single operand stack.",
    time="O(n)", space="O(n)",
    pitfalls=["Using floor division, which rounds −7 / 2 to −4 instead of −3."],
)
def eval_rpn(tokens):
    st = []
    for t in tokens:
        if t in "+-*/" and len(t) == 1:
            b, a = st.pop(), st.pop()
            if t == "+":
                st.append(a + b)
            elif t == "-":
                st.append(a - b)
            elif t == "*":
                st.append(a * b)
            else:
                st.append(int(a / b))
        else:
            st.append(int(t))
    return st[0]


def _decode_input(r):
    def enc(depth):
        parts = []
        for _ in range(r.randint(1, 2)):
            if depth and r.random() < 0.6:
                parts.append(f"{r.randint(1, 3)}[{enc(depth - 1)}]")
            else:
                parts.append(r.word(r.randint(1, 2), "abc"))
        return "".join(parts)
    return (enc(2),)


def _decode_brute(s):
    import re
    while "[" in s:
        s = re.sub(r"(\d+)\[([a-z]*)\]", lambda m: m.group(2) * int(m.group(1)), s)
    return s


@problem(
    slug="decode-string", title="Decode String", difficulty="Medium", pattern=ST, tags=["String", "Stack", "Recursion"],
    sig="decodeString(self, s: str) -> str",
    desc="""Decode a string encoded with the rule `k[text]`, meaning `text` repeated `k` times. Encodings may be nested. Digits only appear as repeat counts.""",
    constraints=["1 ≤ len(s) ≤ 30", "1 ≤ k ≤ 300", "the output length ≤ 10⁵"],
    samples=[("3[a]2[bc]",), ("3[a2[c]]",), ("2[abc]3[cd]ef",)],
    gen=_decode_input,
    brute=_decode_brute,
    hints=[
        "Nested brackets must be decoded inside-out.",
        "On '[', save the text built so far and the repeat count, then start a fresh string.",
        "On ']', pop the saved text and count, and set current = saved_text + count × current.",
    ],
    insight="A stack of (previous text, count) handles nesting.",
    time="O(output length)", space="O(output length)",
    pitfalls=["Reading only single-digit counts like the 1 in 12[a]."],
)
def decode_string(s):
    stack, cur, num = [], "", 0
    for c in s:
        if c.isdigit():
            num = num * 10 + int(c)
        elif c == "[":
            stack.append((cur, num))
            cur, num = "", 0
        elif c == "]":
            prev, k = stack.pop()
            cur = prev + cur * k
        else:
            cur += c
    return cur


def _asteroid_brute(a):
    a = list(a)
    changed = True
    while changed:
        changed = False
        for i in range(len(a) - 1):
            if a[i] > 0 > a[i + 1]:
                if abs(a[i]) > abs(a[i + 1]):
                    del a[i + 1]
                elif abs(a[i]) < abs(a[i + 1]):
                    del a[i]
                else:
                    del a[i:i + 2]
                changed = True
                break
    return a


@problem(
    slug="asteroid-collision", title="Asteroid Collision", difficulty="Medium", pattern=ST, tags=["Array", "Stack", "Simulation"],
    sig="asteroidCollision(self, asteroids: list[int]) -> list[int]",
    desc="""Each asteroid's absolute value is its size and its sign is its direction (positive = right, negative = left); all move at the same speed. When two meet, the smaller one explodes; equal sizes both explode. Return the asteroids that remain.""",
    constraints=["2 ≤ n ≤ 10⁴", "-1000 ≤ asteroids[i] ≤ 1000, nonzero"],
    samples=[([5, 10, -5],), ([8, -8],), ([10, 2, -5],)],
    gen=lambda r: ([r.choice([-1, 1]) * r.randint(1, 6) for _ in range(r.randint(2, 9))],),
    brute=_asteroid_brute,
    hints=[
        "Only a right-moving asteroid followed by a left-moving one can collide.",
        "Keep survivors on a stack; a new left-mover fights the right-movers on top.",
        "Pop smaller right-movers; if equal, pop and drop both; if the top is bigger, the new one dies; otherwise push it.",
    ],
    insight="Collisions only happen at the top of a stack of survivors.",
    time="O(n)", space="O(n)",
    pitfalls=["Letting a left-mover collide with left-movers already on the stack."],
)
def asteroid_collision(asteroids):
    st = []
    for a in asteroids:
        alive = True
        while alive and a < 0 and st and st[-1] > 0:
            if st[-1] < -a:
                st.pop()
            elif st[-1] == -a:
                st.pop()
                alive = False
            else:
                alive = False
        if alive:
            st.append(a)
    return st


@problem(
    slug="simplify-path", title="Simplify Path", difficulty="Medium", pattern=ST, tags=["String", "Stack"],
    sig="simplifyPath(self, path: str) -> str",
    desc="""Convert an absolute Unix-style path into its simplified canonical form:

- `.` means the current directory and `..` means the parent directory (the parent of `/` is `/`).
- Multiple slashes count as one.
- Any other name (including `...`) is a normal directory name.

The result starts with a single `/`, separates names with single slashes, and has no trailing slash.""",
    constraints=["1 ≤ len(path) ≤ 3000", "path starts with '/'"],
    samples=[("/home/",), ("/home//foo/",), ("/home/user/Documents/../Pictures",), ("/../",), ("/.../a/../b/c/../d/./",)],
    gen=lambda r: ("/" + "/".join(r.choice(["a", "b", ".", "..", "", "..."]) for _ in range(r.randint(1, 7))),),
    brute=lambda p: __import__("posixpath").normpath(p).replace("//", "/") if not p.startswith("//") else __import__("posixpath").normpath("/" + p.lstrip("/")),
    hints=[
        "Split on '/' and ignore empty pieces and '.'.",
        "Keep the directory names on a stack.",
        "'..' pops (when the stack isn't empty); any other name is pushed. Join with '/' and add the leading slash.",
    ],
    insight="A stack of directory names models moving up and down.",
    time="O(n)", space="O(n)",
    pitfalls=["Treating '...' as a special name."],
)
def simplify_path(path):
    st = []
    for part in path.split("/"):
        if part == "..":
            if st:
                st.pop()
        elif part and part != ".":
            st.append(part)
    return "/" + "/".join(st)


# ---------------------------------------------------------------- monotonic stack


def _remove_k_brute(num, k):
    from itertools import combinations
    best = None
    for keep in combinations(range(len(num)), len(num) - k):
        s = "".join(num[i] for i in keep).lstrip("0") or "0"
        if best is None or (len(s), s) < (len(best), best):
            best = s
    return best


@problem(
    slug="remove-k-digits", title="Remove K Digits", difficulty="Medium", pattern=MS, tags=["String", "Stack", "Greedy", "Monotonic Stack"],
    sig="removeKdigits(self, num: str, k: int) -> str",
    desc="""`num` is a non-negative integer as a string. Remove exactly `k` digits so the remaining number is as small as possible. Return it without leading zeros (or `"0"` if nothing remains).""",
    constraints=["1 ≤ k ≤ len(num) ≤ 10⁵", "num has no leading zeros except \"0\" itself"],
    samples=[("1432219", 3), ("10200", 1), ("10", 2)],
    gen=lambda r: (lambda s: (s, r.randint(1, len(s))))(str(r.randint(1, 9)) + "".join(r.choice("0123456789") for _ in range(r.randint(0, 7)))),
    brute=_remove_k_brute,
    hints=[
        "A digit followed by a smaller digit should be removed: that makes an earlier position smaller.",
        "Keep an increasing stack of digits; while the new digit is smaller than the top and k > 0, pop.",
        "If removals remain at the end, drop them from the back. Strip leading zeros.",
    ],
    insight="A monotonic increasing stack greedily minimizes the leftmost digits.",
    time="O(n)", space="O(n)",
    pitfalls=["Returning an empty string instead of \"0\"."],
)
def remove_k_digits(num, k):
    st = []
    for d in num:
        while k and st and st[-1] > d:
            st.pop()
            k -= 1
        st.append(d)
    if k:
        st = st[:-k]
    return "".join(st).lstrip("0") or "0"


@problem(
    slug="next-greater-element-i", title="Next Greater Element I", difficulty="Easy", pattern=MS,
    tags=["Array", "Hash Table", "Stack", "Monotonic Stack"],
    sig="nextGreaterElement(self, nums1: list[int], nums2: list[int]) -> list[int]",
    desc="""`nums1` is a subset of `nums2` (all values distinct). For each value in `nums1`, find its position in `nums2` and report the first greater value to its right there, or `-1` if none.""",
    constraints=["1 ≤ len(nums1) ≤ len(nums2) ≤ 1000", "values are distinct", "every value of nums1 is in nums2"],
    samples=[([4, 1, 2], [1, 3, 4, 2]), ([2, 4], [1, 2, 3, 4])],
    gen=lambda r: (lambda b: (r.sample(b, r.randint(1, len(b))), b))(r.distinct(r.randint(1, 9), 0, 20)),
    brute=lambda a, b: [next((y for y in b[b.index(x) + 1:] if y > x), -1) for x in a],
    hints=[
        "Precompute the next greater value for every element of nums2.",
        "Scan nums2 with a decreasing stack: when a bigger value arrives, it is the answer for everything it pops.",
        "Store the answers in a map and look up each value of nums1.",
    ],
    insight="A monotonic stack finds every next-greater element in one pass.",
    time="O(n + m)", space="O(m)",
    pitfalls=["Searching to the right for each element, which is O(n·m)."],
)
def next_greater_element(nums1, nums2):
    nxt, st = {}, []
    for x in nums2:
        while st and st[-1] < x:
            nxt[st.pop()] = x
        st.append(x)
    return [nxt.get(x, -1) for x in nums1]


@problem(
    slug="next-greater-element-ii", title="Next Greater Element II", difficulty="Medium", pattern=MS, tags=["Array", "Stack", "Monotonic Stack"],
    sig="nextGreaterElements(self, nums: list[int]) -> list[int]",
    desc="""`nums` is circular (the element after the last is the first). For each element, return the first greater element found by moving forward around the circle, or `-1` if there is none.""",
    constraints=["1 ≤ n ≤ 10⁴", "-10⁹ ≤ nums[i] ≤ 10⁹"],
    samples=[([1, 2, 1],), ([1, 2, 3, 4, 3],)],
    gen=lambda r: (r.ints(r.randint(1, 10), 0, 6),),
    brute=lambda nums: [next((nums[(i + k) % len(nums)] for k in range(1, len(nums)) if nums[(i + k) % len(nums)] > x), -1) for i, x in enumerate(nums)],
    hints=[
        "Walking around the circle once more is the same as scanning the array twice.",
        "Use a stack of indices whose answers are unknown, kept in decreasing value order.",
        "Iterate i from 0 to 2n − 1 using nums[i % n]; pop and fill answers while the current value is greater. Only push during the first pass.",
    ],
    insight="Two passes over a circular array with one monotonic stack.",
    time="O(n)", space="O(n)",
    pitfalls=["Pushing indices in the second pass, which double-counts."],
)
def next_greater_elements(nums):
    n = len(nums)
    res, st = [-1] * n, []
    for i in range(2 * n):
        x = nums[i % n]
        while st and nums[st[-1]] < x:
            res[st.pop()] = x
        if i < n:
            st.append(i)
    return res


@problem(
    slug="largest-rectangle-in-histogram", title="Largest Rectangle in Histogram", difficulty="Hard", pattern=MS,
    tags=["Array", "Stack", "Monotonic Stack"],
    sig="largestRectangleArea(self, heights: list[int]) -> int",
    desc="""`heights` are the bar heights of a histogram where every bar has width 1. Return the area of the largest rectangle within it.""",
    constraints=["1 ≤ n ≤ 10⁵", "0 ≤ heights[i] ≤ 10⁴"],
    samples=[([2, 1, 5, 6, 2, 3],), ([2, 4],)],
    gen=lambda r: (r.ints(r.randint(1, 10), 0, 8),),
    brute=lambda h: max(min(h[i:j]) * (j - i) for i in range(len(h)) for j in range(i + 1, len(h) + 1)),
    hints=[
        "For each bar, the widest rectangle of its height extends until a shorter bar on each side.",
        "An increasing stack of indices finds both boundaries: when a shorter bar arrives, it's the right boundary for every taller bar it pops.",
        "When popping bar h, its left boundary is the new stack top. Add a 0-height sentinel at the end to flush the stack.",
    ],
    insight="Each bar is pushed and popped once, and popping reveals its maximal width.",
    time="O(n)", space="O(n)",
    pitfalls=["Computing the width wrongly when the stack becomes empty."],
)
def largest_rectangle(heights):
    st, best = [], 0
    for i, h in enumerate(heights + [0]):
        while st and heights[st[-1]] >= h:
            height = heights[st.pop()]
            left = st[-1] + 1 if st else 0
            best = max(best, height * (i - left))
        st.append(i)
    return best


class _SpannerRef:
    def __init__(self):
        self.prices = []

    def next(self, price):
        self.prices.append(price)
        k = 0
        for p in reversed(self.prices):
            if p > price:
                break
            k += 1
        return k


def _span_ops(r):
    ops, args = ["StockSpanner"], [[]]
    for _ in range(r.randint(3, 12)):
        ops.append("next")
        args.append([r.randint(1, 10)])
    return ops, args


@problem(
    slug="online-stock-span", title="Online Stock Span", difficulty="Medium", pattern=MS, tags=["Stack", "Design", "Monotonic Stack", "Data Stream"],
    design=True, cls="StockSpanner",
    starter="""class StockSpanner:
    def __init__(self):
        pass

    def next(self, price: int) -> int:
        pass
""",
    desc="""Design `StockSpanner`. `next(price)` receives today's price and reports its **span**: the number of consecutive days, ending today and going backwards, on which the price was less than or equal to today's price.""",
    constraints=["1 ≤ price ≤ 10⁵", "at most 10⁴ calls"],
    samples=[(["StockSpanner", "next", "next", "next", "next", "next", "next", "next"], [[], [100], [80], [60], [70], [60], [75], [85]]),
             (["StockSpanner", "next", "next"], [[], [5], [5]])],
    gen=_span_ops,
    hints=[
        "Walking backwards day by day is O(n) per call.",
        "Once a day is covered by a later higher-or-equal price, it never needs to be checked separately again.",
        "Keep a stack of (price, span); pop while the top price ≤ today's, adding their spans to today's span.",
    ],
    insight="A decreasing stack compresses dominated days into spans.",
    time="Amortized O(1) per call", space="O(n)",
    pitfalls=["Stopping at strictly smaller prices only (equal prices count too)."],
)
class StockSpanner(_SpannerRef):
    pass


@problem(
    slug="sum-of-subarray-minimums", title="Sum of Subarray Minimums", difficulty="Medium", pattern=MS,
    tags=["Array", "Dynamic Programming", "Stack", "Monotonic Stack"],
    sig="sumSubarrayMins(self, arr: list[int]) -> int",
    desc="""Return the sum of `min(b)` over every contiguous subarray `b` of `arr`, modulo `10⁹ + 7`.""",
    constraints=["1 ≤ len(arr) ≤ 3 × 10⁴", "1 ≤ arr[i] ≤ 3 × 10⁴"],
    samples=[([3, 1, 2, 4],), ([11, 81, 94, 43, 3],)],
    gen=lambda r: (r.ints(r.randint(1, 10), 1, 6),),
    brute=lambda a: sum(min(a[i:j]) for i in range(len(a)) for j in range(i + 1, len(a) + 1)) % (10**9 + 7),
    hints=[
        "Count, for each element, how many subarrays have it as their minimum.",
        "That's (choices of left end) × (choices of right end), bounded by the nearest smaller elements on each side.",
        "Use monotonic stacks for the previous smaller and the next smaller-or-equal element, so ties are counted once.",
    ],
    insight="Contribution counting: each element's share is value × left span × right span.",
    time="O(n)", space="O(n)",
    pitfalls=["Using strict comparisons on both sides, which double-counts equal values."],
)
def sum_subarray_mins(arr):
    n = len(arr)
    left, right, st = [0] * n, [0] * n, []
    for i in range(n):
        while st and arr[st[-1]] > arr[i]:
            st.pop()
        left[i] = i - (st[-1] if st else -1)
        st.append(i)
    st = []
    for i in range(n - 1, -1, -1):
        while st and arr[st[-1]] >= arr[i]:
            st.pop()
        right[i] = (st[-1] if st else n) - i
        st.append(i)
    return sum(a * l * r for a, l, r in zip(arr, left, right)) % (10**9 + 7)


def _fleet_brute(target, position, speed):
    cars = sorted(zip(position, speed), reverse=True)
    fleets, slowest = 0, 0.0
    for p, s in cars:
        from fractions import Fraction
        t = Fraction(target - p, s)
        if t > slowest:
            fleets += 1
            slowest = t
    return fleets


@problem(
    slug="car-fleet", title="Car Fleet", difficulty="Medium", pattern=MS, tags=["Array", "Stack", "Sorting", "Monotonic Stack"],
    sig="carFleet(self, target: int, position: list[int], speed: list[int]) -> int",
    desc="""Cars drive toward `target` on a one-lane road. Car `i` starts at `position[i]` with `speed[i]`. A car can't pass the car ahead; when it catches up, they drive together as one **fleet** at the slower speed. A car catching up exactly at the target also joins the fleet.

Return how many fleets arrive at the target.""",
    constraints=["1 ≤ n ≤ 10⁵", "0 < target ≤ 10⁶", "0 ≤ position[i] < target, distinct", "0 < speed[i] ≤ 10⁶"],
    samples=[(12, [10, 8, 0, 5, 3], [2, 4, 1, 1, 3]), (10, [3], [3]), (100, [0, 2, 4], [4, 2, 1])],
    gen=lambda r: (lambda target, n: (target, r.sample(range(target), n), r.ints(n, 1, 5)))(r.randint(5, 20), r.randint(1, 5)),
    brute=_fleet_brute,
    hints=[
        "Process cars from the one closest to the target backwards.",
        "Compute each car's arrival time if unobstructed: (target − position) / speed.",
        "A car that would arrive no later than the fleet ahead joins it; a strictly later arrival starts a new fleet.",
    ],
    insight="Sorted by position, fleets correspond to a monotonic sequence of arrival times.",
    time="O(n log n)", space="O(n)",
    pitfalls=["Comparing floating-point times when exact comparisons are safer (compare fractions or cross-multiply)."],
)
def car_fleet(target, position, speed):
    st = []
    for p, s in sorted(zip(position, speed), reverse=True):
        t = (target - p) / s
        if not st or t > st[-1] + 1e-12:
            st.append(t)
    return len(st)


def _big_logs(r, calls, n):
    logs, t, stack, started = [], 0, [], 0
    while started < calls or stack:
        if stack and (started >= calls or r.random() < 0.5):
            logs.append(f"{stack.pop()}:end:{t}")
        else:
            f = r.randint(0, n - 1)
            logs.append(f"{f}:start:{t}")
            stack.append(f)
            started += 1
        t += r.randint(0, 3)
    return n, logs


def _big_expr(r, terms):
    parts, depth = [], 0
    for k in range(terms):
        if k:
            parts.append(r.choice(["+", "-", " + ", " - "]))
        while r.random() < 0.15:
            parts.append(r.choice(["(", "-("]))
            depth += 1
        parts.append(str(r.randint(0, 999)))
        while depth and r.random() < 0.15:
            parts.append(")")
            depth -= 1
    return ("".join(parts) + ")" * depth,)


def _big_rpn(r, n):
    tokens = [str(r.randint(-200, 200))]
    while len(tokens) < n:
        tokens += [str(r.randint(-200, 200)), r.choice(["+", "-", "+", "-", "*", "/"]) if len(tokens) % 50 == 0 else r.choice(["+", "-"])]
    return (tokens,)


def _big_min_stack_ops(r):
    ops, args, size = ["MinStack"], [[]], 0
    for _ in range(9000):
        choice = r.choice(["push", "push", "pop", "top", "getMin"]) if size else "push"
        ops.append(choice)
        if choice == "push":
            args.append([r.randint(-2**31, 2**31 - 1)]); size += 1
        else:
            args.append([])
            size -= choice == "pop"
    return ops, args


def _big_span_ops(r):
    prices = list(range(5000, 0, -1)) + [100000] + r.ints(3000, 1, 100000)
    return ["StockSpanner"] + ["next"] * len(prices), [[]] + [[p] for p in prices]


EXTRA = {
    "set-matrix-zeroes": {
        "edge": [([[0]],), ([[1]],), ([[1, 0]],), ([[0, 1], [1, 1]],), ([[-2147483648, 2147483647], [0, 1]],)],
        "large": [lambda r: ([[r.choice([1] * 400 + [0]) for _ in range(200)] for _ in range(200)],)],
    },
    "rotate-image": {"edge": [([[1]],), ([[1, 2], [3, 4]],), ([[i * 20 + j for j in range(20)] for i in range(20)],)]},
    "where-will-the-ball-fall": {
        "edge": [([[1]],), ([[1, -1]],), ([[1, 1], [-1, -1]],), ([[-1, -1, -1]],)],
        "large": [lambda r: ([[r.choice([1, -1]) for _ in range(100)] for _ in range(100)],), lambda r: ([[1] * 99 + [-1] for _ in range(100)],)],
    },
    "transpose-matrix": {
        "edge": [([[1]],), ([[1, 2, 3]],), ([[1], [2], [3]],), ([[-10**9, 10**9]],)],
        "large": [lambda r: ([r.ints(100, -1000, 1000) for _ in range(100)],), lambda r: ([r.ints(10000, 0, 99)],)],
    },
    "game-of-life": {
        "edge": [([[0]],), ([[1]],), ([[1, 1], [1, 1]],), ([[0, 1, 0], [0, 1, 0], [0, 1, 0]],), ([[r % 2 for r in range(i, i + 25)] for i in range(25)],)],
    },
    "toeplitz-matrix": {"edge": [([[1]],), ([[1, 2]],), ([[1], [2]],), ([[11, 74, 0, 93], [40, 11, 74, 7]],), ([[(j - i) % 100 for j in range(20)] for i in range(20)],)]},
    "spiral-matrix-ii": {"edge": [(7,), (20,)]},
    "diagonal-traverse": {
        "edge": [([[1]],), ([[1, 2]],), ([[1], [2]],), ([[1, 2, 3, 4]],)],
        "large": [lambda r: ([r.ints(100, 0, 999) for _ in range(100)],), lambda r: ([[v] for v in r.ints(10000, 0, 99)],)],
    },
    "basic-calculator": {
        "edge": [("1",), ("-1",), ("(1)",), ("-(-(-(3)))",), ("2147483647",), ("1 - (2 - (3 - 4))",), ("- (3 + (4 + 5))",)],
        "large": [lambda r: _big_expr(r, 12000), lambda r: ("(" * 5000 + "1" + ")" * 5000,)],
    },
    "remove-all-adjacent-duplicates-in-string": {
        "edge": [("a",), ("aa",), ("aaa",), ("abba",), ("abccba",)],
        "large": [lambda r: (lambda h: (h + h[::-1] + "x",))(r.word(40000, "ab")), lambda r: (r.word(80000, "abc"),)],
    },
    "exclusive-time-of-functions": {
        "edge": [(1, ["0:start:0", "0:end:0"]), (1, ["0:start:0", "0:start:1", "0:end:1", "0:end:2"]), (2, ["0:start:0", "0:start:2", "0:end:5", "1:start:6", "1:end:6", "0:end:7"])],
        "large": [lambda r: _big_logs(r, 4000, 100)],
    },
    "min-stack": {
        "edge": [(["MinStack", "push", "getMin", "top"], [[], [-2147483648], [], []]),
                 (["MinStack", "push", "push", "push", "getMin", "pop", "getMin"], [[], [0], [1], [0], [], [], []]),
                 (["MinStack", "push", "push", "pop", "getMin"], [[], [2], [1], [], []])],
        "large": [_big_min_stack_ops],
    },
    "implement-queue-using-stacks": {
        "edge": [(["MyQueue", "push", "pop", "empty"], [[], [9], [], []]),
                 (["MyQueue", "push", "push", "pop", "push", "pop", "peek"], [[], [1], [2], [], [3], [], []]),
                 (["MyQueue"] + ["push"] * 50 + ["pop"] * 49 + ["peek"], [[]] + [[i % 9 + 1] for i in range(50)] + [[]] * 50)],
    },
    "evaluate-reverse-polish-notation": {
        "edge": [(["-7", "2", "/"],), (["0", "3", "/"],), (["3", "-4", "*"],), (["-200"],), (["4", "3", "-"],), (["1", "2", "3", "4", "+", "+", "+"],)],
        "large": [lambda r: _big_rpn(r, 9999)],
    },
    "decode-string": {"edge": [("abc",), ("10[a]",), ("2[2[2[a]]]",), ("3[z]2[2[y]pq4[2[jk]e1[f]]]ef",), ("100[leetcode]",)]},
    "asteroid-collision": {
        "edge": [([1, -1],), ([-1, 1],), ([-2, -1, 1, 2],), ([1, -2, -2, -2],), ([10, 2, -5],), ([1000, -1000, 1000],)],
        "large": [lambda r: ([1000 - (i % 999) for i in range(5000)] + [-r.randint(1, 1000) for _ in range(5000)],), lambda r: ([r.choice([-1, 1]) * r.randint(1, 1000) for _ in range(10000)],)],
    },
    "simplify-path": {
        "edge": [("/",), ("//",), ("/..",), ("/./././",), ("/a//b////c/d//././/..",), ("/...",), ("/a/../../b/../c//.//",)],
        "large": [lambda r: ("/" + "/".join(r.choice(["ab", ".", "..", "", "..."]) for _ in range(800)),)],
    },
    "remove-k-digits": {
        "edge": [("9", 1), ("10", 1), ("112", 1), ("10001", 4), ("1234567890", 9), ("100", 1)],
        "large": [lambda r: ("1" + r.word(60000, "0123456789"), 30000), lambda r: ("9" * 30000 + "1" * 30000, 30000)],
    },
    "next-greater-element-i": {
        "edge": [([1], [1]), ([1], [1, 2]), ([2], [1, 2]), ([1, 3, 5, 2, 4], [6, 5, 4, 3, 2, 1, 7])],
        "large": [lambda r: (lambda b: (b[:500], b))(r.distinct(1000, 0, 10**4))],
    },
    "next-greater-element-ii": {
        "edge": [([1],), ([1, 1],), ([5, 4, 3, 2, 1],), ([-1000000000, 1000000000],)],
        "large": [lambda r: (list(range(10000, 0, -1)),), lambda r: (r.ints(10000, -10**9, 10**9),)],
    },
    "largest-rectangle-in-histogram": {
        "edge": [([0],), ([5],), ([2, 2],), ([1, 2, 3, 4, 5],), ([0, 0, 0],), ([10000, 10000],)],
        "large": [lambda r: (list(range(1, 15001)),), lambda r: (r.ints(15000, 0, 10000),)],
    },
    "online-stock-span": {
        "edge": [(["StockSpanner", "next"], [[], [1]]),
                 (["StockSpanner", "next", "next", "next"], [[], [5], [5], [5]]),
                 (["StockSpanner", "next", "next", "next", "next"], [[], [1], [2], [3], [4]])],
        "large": [_big_span_ops],
    },
    "sum-of-subarray-minimums": {
        "edge": [([1],), ([30000],), ([2, 2, 2],), ([1, 2, 3],), ([3, 2, 1],)],
        "large": [lambda r: (r.ints(15000, 1, 30000),), lambda r: ([30000] * 15000,)],
    },
    "car-fleet": {
        "edge": [(10, [0], [1]), (10, [0, 5], [1, 1]), (10, [0, 4], [2, 1]), (10, [6, 8], [3, 2]), (1000000, [0, 999999], [1000000, 1])],
        "large": [lambda r: (10**6, r.distinct(7000, 0, 10**6 - 1), r.ints(7000, 1, 10**6))],
    },
}
