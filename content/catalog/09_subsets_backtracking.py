from collections import Counter
from itertools import combinations, permutations, product

from catalog_lib import problem

S = "subsets"
B = "backtracking"


def _all_subsets(nums):
    return [list(c) for r in range(len(nums) + 1) for c in combinations(nums, r)]


@problem(
    slug="find-k-sum-subsets", title="Find K-Sum Subsets", difficulty="Medium", pattern=S, tags=["Array", "Backtracking", "Bit Manipulation"],
    sig="getKSumSubsets(self, setOfIntegers: list[int], targetSum: int) -> list[list[int]]", compare="unordered-deep",
    desc="""`setOfIntegers` holds distinct positive integers. Return every subset whose elements add up to `targetSum`. Subsets and the numbers inside them may be in any order.""",
    constraints=["1 ≤ len(setOfIntegers) ≤ 10", "1 ≤ values ≤ 100, distinct", "1 ≤ targetSum ≤ 1000"],
    samples=[([1, 2, 3, 4, 5], 5), ([1, 3, 5, 21, 19, 7, 2], 10)],
    gen=lambda r: (r.distinct(r.randint(1, 8), 1, 12), r.randint(1, 25)),
    brute=lambda nums, t: [s for s in _all_subsets(nums) if sum(s) == t],
    hints=[
        "Each element is either in a subset or not, so there are 2ⁿ subsets.",
        "Build subsets incrementally: for each element, branch on including it or skipping it.",
        "Track the running sum, record the subset when the sum matches, and prune when the sum already exceeds the target (all values are positive).",
    ],
    insight="Include/exclude recursion enumerates subsets; positivity allows pruning.",
    time="O(2ⁿ · n)", space="O(n) recursion",
    pitfalls=["Stopping a branch as soon as the target is hit is fine only because all values are positive."],
)
def k_sum_subsets(nums, target):
    out = []

    def go(i, cur, total):
        if total == target:
            out.append(cur[:])
        if total >= target:
            return
        for j in range(i, len(nums)):
            cur.append(nums[j])
            go(j + 1, cur, total + nums[j])
            cur.pop()

    go(0, [], 0)
    return out


@problem(
    slug="permutations", title="Permutations", difficulty="Medium", pattern=S, tags=["Array", "Backtracking"],
    sig="permute(self, nums: list[int]) -> list[list[int]]", compare="unordered",
    desc="""`nums` contains distinct integers. Return all possible orderings of them, in any order.""",
    constraints=["1 ≤ len(nums) ≤ 6", "-10 ≤ nums[i] ≤ 10, distinct"],
    samples=[([1, 2, 3],), ([0, 1],), ([1],)],
    gen=lambda r: (r.distinct(r.randint(1, 5), -10, 10),),
    brute=lambda nums: [list(p) for p in permutations(nums)],
    hints=[
        "Choose the first element, then permute the rest.",
        "Track which elements are already used in the current arrangement.",
        "Backtrack: add an unused element, recurse, then remove it. Record the arrangement when it has n elements.",
    ],
    insight="Backtracking over unused elements generates all n! orderings.",
    time="O(n · n!)", space="O(n)",
    pitfalls=["Appending the same mutable list instead of a copy."],
)
def permute(nums):
    out, cur, used = [], [], [False] * len(nums)

    def go():
        if len(cur) == len(nums):
            out.append(cur[:])
            return
        for i, x in enumerate(nums):
            if not used[i]:
                used[i] = True
                cur.append(x)
                go()
                cur.pop()
                used[i] = False

    go()
    return out


_PHONE = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl", "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}


@problem(
    slug="letter-combinations-of-a-phone-number", title="Letter Combinations of a Phone Number", difficulty="Medium", pattern=S,
    tags=["Hash Table", "String", "Backtracking"],
    sig="letterCombinations(self, digits: str) -> list[str]", compare="unordered",
    desc="""Each digit 2–9 maps to letters as on a phone keypad (2 → abc, 3 → def, 4 → ghi, 5 → jkl, 6 → mno, 7 → pqrs, 8 → tuv, 9 → wxyz). Return every letter string the digits could represent, in any order. An empty input gives an empty list.""",
    constraints=["0 ≤ len(digits) ≤ 4", "digits contains only 2–9"],
    samples=[("23",), ("",), ("2",)],
    gen=lambda r: ("".join(r.choice("23456789") for _ in range(r.randint(1, 4))),),
    brute=lambda d: ["".join(p) for p in product(*(_PHONE[c] for c in d))] if d else [],
    hints=[
        "Each digit contributes one letter to every result.",
        "Think of a tree: level i chooses a letter for digit i.",
        "Recurse digit by digit, appending each possible letter; at the end of the digits, record the string.",
    ],
    insight="A Cartesian product built by backtracking.",
    time="O(4ⁿ · n)", space="O(n)",
    pitfalls=["Returning [\"\"] for empty input instead of []."],
)
def letter_combinations(digits):
    if not digits:
        return []
    out = []

    def go(i, cur):
        if i == len(digits):
            out.append(cur)
            return
        for c in _PHONE[digits[i]]:
            go(i + 1, cur + c)

    go(0, "")
    return out


def _balanced(s):
    bal = 0
    for c in s:
        bal += 1 if c == "(" else -1
        if bal < 0:
            return False
    return bal == 0


@problem(
    slug="generate-parentheses", title="Generate Parentheses", difficulty="Medium", pattern=S,
    tags=["String", "Dynamic Programming", "Backtracking"],
    sig="generateParenthesis(self, n: int) -> list[str]", compare="unordered",
    desc="""Return every well-formed string made of `n` pairs of parentheses, in any order.""",
    constraints=["1 ≤ n ≤ 8"],
    samples=[(3,), (1,)],
    tests=[(2,), (4,), (5,), (6,)],
    brute=lambda n: ["".join(p) for p in product("()", repeat=2 * n) if _balanced(p)],
    hints=[
        "A string stays valid as long as you never close more than you've opened.",
        "Track how many '(' and ')' you've placed.",
        "Add '(' while opens < n; add ')' while closes < opens. Record the string at length 2n.",
    ],
    insight="Constraint-guided backtracking only builds valid prefixes.",
    time="O(4ⁿ / √n)", space="O(n)",
    pitfalls=["Generating all 2²ⁿ strings and filtering, which is far slower."],
)
def generate_parenthesis(n):
    out = []

    def go(cur, opened, closed):
        if len(cur) == 2 * n:
            out.append(cur)
            return
        if opened < n:
            go(cur + "(", opened + 1, closed)
        if closed < opened:
            go(cur + ")", opened, closed + 1)

    go("", 0, 0)
    return out


@problem(
    slug="letter-case-permutation", title="Letter Case Permutation", difficulty="Medium", pattern=S,
    tags=["String", "Backtracking", "Bit Manipulation"],
    sig="letterCasePermutation(self, s: str) -> list[str]", compare="unordered",
    desc="""You may switch any letter in `s` to lowercase or uppercase. Return every string you can create this way, in any order. Digits stay as they are.""",
    constraints=["1 ≤ len(s) ≤ 12", "s contains letters and digits"],
    samples=[("a1b2",), ("3z4",)],
    tests=[("12345",), ("C",)],
    gen=lambda r: ("".join(r.choice("abXY0123") for _ in range(r.randint(1, 6))),),
    brute=lambda s: sorted({"".join(p) for p in product(*({c.lower(), c.upper()} for c in s))}),
    hints=[
        "Digits have one option; letters have two.",
        "Start from [\"\"] and extend each partial string one character at a time.",
        "For a letter, extend with both cases; for a digit, extend with the digit only.",
    ],
    insight="Each letter doubles the set of results: 2^(letters) strings.",
    time="O(2ᴸ · n)", space="O(2ᴸ · n)",
    pitfalls=["Producing duplicates for digits by trying two \"cases\"."],
)
def letter_case_permutation(s):
    out = [""]
    for c in s:
        if c.isalpha():
            out = [p + x for p in out for x in (c.lower(), c.upper())]
        else:
            out = [p + c for p in out]
    return out


@problem(
    slug="letter-tile-possibilities", title="Letter Tile Possibilities", difficulty="Medium", pattern=S,
    tags=["Hash Table", "String", "Backtracking", "Counting"],
    sig="numTilePossibilities(self, tiles: str) -> int",
    desc="""Each character of `tiles` is a tile with that letter. Return how many distinct **non-empty** letter sequences you can make using the tiles (each tile at most once).""",
    constraints=["1 ≤ len(tiles) ≤ 7", "tiles contains uppercase letters"],
    samples=[("AAB",), ("AAABBC",), ("V",)],
    gen=lambda r: ("".join(r.choice("ABC") for _ in range(r.randint(1, 6))),),
    brute=lambda t: len({p for k in range(1, len(t) + 1) for p in permutations(t, k)}),
    hints=[
        "Equal tiles are interchangeable, so work with letter counts, not positions.",
        "Each step picks a letter with a remaining count to append.",
        "Recurse: for each letter with count > 0, count 1 for the new sequence, decrement, recurse, and restore.",
    ],
    insight="Backtracking over counts avoids generating duplicate sequences.",
    time="O(n!) worst case", space="O(n)",
    pitfalls=["Counting the empty sequence."],
)
def num_tile_possibilities(tiles):
    counts = Counter(tiles)

    def go():
        total = 0
        for c in counts:
            if counts[c]:
                counts[c] -= 1
                total += 1 + go()
                counts[c] += 1
        return total

    return go()


@problem(
    slug="subsets-ii", title="Subsets II", difficulty="Medium", pattern=S, tags=["Array", "Backtracking", "Bit Manipulation"],
    sig="subsetsWithDup(self, nums: list[int]) -> list[list[int]]", compare="unordered-deep",
    desc="""`nums` may contain duplicates. Return all **distinct** subsets, in any order (elements inside a subset may also be in any order).""",
    constraints=["1 ≤ len(nums) ≤ 10", "-10 ≤ nums[i] ≤ 10"],
    samples=[([1, 2, 2],), ([0],)],
    gen=lambda r: (r.ints(r.randint(1, 7), -3, 3),),
    brute=lambda nums: [list(t) for t in {tuple(sorted(s)) for s in _all_subsets(nums)}],
    hints=[
        "Sort first so equal values sit next to each other.",
        "Duplicates appear when you pick the 2nd copy of a value at a position where you skipped the 1st.",
        "In the loop that picks the next element, skip nums[j] when j > start and nums[j] == nums[j − 1].",
    ],
    insight="Sorting plus a skip-equal-siblings rule removes duplicate subsets.",
    time="O(2ⁿ · n)", space="O(n)",
    pitfalls=["Deduplicating with a set of lists, which is slow and needs sorting each subset anyway."],
)
def subsets_with_dup(nums):
    nums = sorted(nums)
    out = []

    def go(start, cur):
        out.append(cur[:])
        for j in range(start, len(nums)):
            if j > start and nums[j] == nums[j - 1]:
                continue
            cur.append(nums[j])
            go(j + 1, cur)
            cur.pop()

    go(0, [])
    return out


@problem(
    slug="permutations-ii", title="Permutations II", difficulty="Medium", pattern=S, tags=["Array", "Backtracking", "Sorting"],
    sig="permuteUnique(self, nums: list[int]) -> list[list[int]]", compare="unordered",
    desc="""`nums` may contain duplicates. Return all **distinct** orderings, in any order.""",
    constraints=["1 ≤ len(nums) ≤ 8", "-10 ≤ nums[i] ≤ 10"],
    samples=[([1, 1, 2],), ([1, 2, 3],)],
    gen=lambda r: (r.ints(r.randint(1, 6), 0, 3),),
    brute=lambda nums: [list(p) for p in set(permutations(nums))],
    hints=[
        "Plain permutation backtracking produces duplicates when equal values swap places.",
        "Choose by value instead of by position: use a count of each remaining value.",
        "At each position, try each distinct value with count > 0, decrement, recurse, restore.",
    ],
    insight="Branching on distinct values (via counts) never creates the same ordering twice.",
    time="O(n · n!)", space="O(n)",
    pitfalls=["Using a set of tuples at the end, which still explores n! branches."],
)
def permute_unique(nums):
    counts = Counter(nums)
    out, cur = [], []

    def go():
        if len(cur) == len(nums):
            out.append(cur[:])
            return
        for v in counts:
            if counts[v]:
                counts[v] -= 1
                cur.append(v)
                go()
                cur.pop()
                counts[v] += 1

    go()
    return out


@problem(
    slug="combinations", title="Combinations", difficulty="Medium", pattern=S, tags=["Backtracking"],
    sig="combine(self, n: int, k: int) -> list[list[int]]", compare="unordered-deep",
    desc="""Return all combinations of `k` numbers chosen from `1..n`, in any order.""",
    constraints=["1 ≤ n ≤ 20", "1 ≤ k ≤ n"],
    samples=[(4, 2), (1, 1)],
    gen=lambda r: (lambda n: (n, r.randint(1, n)))(r.randint(1, 8)),
    brute=lambda n, k: [list(c) for c in combinations(range(1, n + 1), k)],
    hints=[
        "A combination is an increasing sequence of k numbers.",
        "Pick the next number only from values larger than the last one picked.",
        "Prune: if there aren't enough numbers left to reach k, stop that branch.",
    ],
    insight="Increasing-order backtracking produces each combination exactly once.",
    time="O(k · C(n, k))", space="O(k)",
    pitfalls=["Generating both [1, 2] and [2, 1]."],
)
def combine(n, k):
    out, cur = [], []

    def go(start):
        if len(cur) == k:
            out.append(cur[:])
            return
        for v in range(start, n - (k - len(cur)) + 2):
            cur.append(v)
            go(v + 1)
            cur.pop()

    go(1)
    return out


# ---------------------------------------------------------------- backtracking


def _queens(n):
    out, cols, d1, d2, cur = [], set(), set(), set(), []

    def go(r):
        if r == n:
            out.append(["." * c + "Q" + "." * (n - c - 1) for c in cur])
            return
        for c in range(n):
            if c in cols or r - c in d1 or r + c in d2:
                continue
            cols.add(c); d1.add(r - c); d2.add(r + c); cur.append(c)
            go(r + 1)
            cols.remove(c); d1.remove(r - c); d2.remove(r + c); cur.pop()

    go(0)
    return out


def _queens_brute(n):
    out = []
    for p in permutations(range(n)):
        if len({r - c for r, c in enumerate(p)}) == n and len({r + c for r, c in enumerate(p)}) == n:
            out.append(["." * c + "Q" + "." * (n - c - 1) for c in p])
    return out


@problem(
    slug="n-queens", title="N-Queens", difficulty="Hard", pattern=B, tags=["Array", "Backtracking"],
    sig="solveNQueens(self, n: int) -> list[list[str]]", compare="unordered",
    desc="""Place `n` queens on an `n × n` chessboard so that no two attack each other (no shared row, column or diagonal). Return every distinct board, in any order. Each board is a list of strings where `'Q'` is a queen and `'.'` is empty.""",
    constraints=["1 ≤ n ≤ 9"],
    samples=[(4,), (1,)],
    tests=[(2,), (3,), (5,), (6,)],
    brute=_queens_brute,
    hints=[
        "Each row holds exactly one queen, so place them row by row.",
        "A square is attacked if its column, its (row − col) diagonal, or its (row + col) anti-diagonal is taken.",
        "Keep three sets for those, try every free column in the current row, recurse, then undo.",
    ],
    insight="Row-by-row backtracking with O(1) conflict checks via sets.",
    time="O(n!)", space="O(n)",
    pitfalls=["Checking conflicts by scanning the whole board each time."],
)
def solve_n_queens(n):
    return _queens(n)


@problem(
    slug="n-queens-ii", title="N-Queens II", difficulty="Hard", pattern=B, tags=["Backtracking"],
    sig="totalNQueens(self, n: int) -> int",
    desc="""Return the number of distinct ways to place `n` non-attacking queens on an `n × n` board.""",
    constraints=["1 ≤ n ≤ 9"],
    samples=[(4,), (1,)],
    tests=[(5,), (6,), (8,), (9,)],
    brute=lambda n: len(_queens_brute(n)),
    hints=[
        "Same search as N-Queens, but you only need to count.",
        "Track used columns and both diagonal directions.",
        "Count 1 whenever you successfully place a queen in the last row.",
    ],
    insight="Counting version of row-by-row backtracking.",
    time="O(n!)", space="O(n)",
    pitfalls=["Building board strings you don't need."],
)
def total_n_queens(n):
    return len(_queens(n))


def _word_board(r):
    m, n = r.randint(1, 4), r.randint(1, 4)
    board = [[r.choice("ABC") for _ in range(n)] for _ in range(m)]
    return board, "".join(r.choice("ABC") for _ in range(r.randint(1, 5)))


def _exist(board, word):
    m, n = len(board), len(board[0])

    def go(i, j, k, seen):
        if k == len(word):
            return True
        if not (0 <= i < m and 0 <= j < n) or (i, j) in seen or board[i][j] != word[k]:
            return False
        seen.add((i, j))
        found = any(go(i + di, j + dj, k + 1, seen) for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        seen.discard((i, j))
        return found

    return any(go(i, j, 0, set()) for i in range(m) for j in range(n))


@problem(
    slug="word-search", title="Word Search", difficulty="Medium", pattern=B, tags=["Array", "String", "Backtracking", "Matrix"],
    sig="exist(self, board: list[list[str]], word: str) -> bool",
    desc="""Return `true` if `word` can be traced through `board` by moving between horizontally or vertically adjacent cells, using each cell at most once.""",
    constraints=["1 ≤ m, n ≤ 6", "1 ≤ len(word) ≤ 15", "letters only"],
    samples=[([["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]], "ABCCED"),
             ([["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]], "ABCB")],
    gen=_word_board,
    hints=[
        "Try every cell as the starting point for the first letter.",
        "From a matching cell, explore the four neighbors for the next letter.",
        "Mark the cell as used before recursing and unmark it after, so paths don't reuse cells.",
    ],
    insight="DFS with backtracking over the grid, undoing marks on the way back.",
    time="O(m·n·3ᴸ)", space="O(L)",
    pitfalls=["Forgetting to unmark a cell, which blocks other paths."],
)
def exist(board, word):
    return _exist(board, word)


def _sudoku_solve(board):
    empty = [(i, j) for i in range(9) for j in range(9) if board[i][j] == "."]
    rows = [set(r) for r in board]
    cols = [set(board[i][j] for i in range(9)) for j in range(9)]
    boxes = [set(board[i][j] for i in range(b // 3 * 3, b // 3 * 3 + 3) for j in range(b % 3 * 3, b % 3 * 3 + 3)) for b in range(9)]

    def go(k):
        if k == len(empty):
            return True
        i, j = empty[k]
        b = i // 3 * 3 + j // 3
        for d in "123456789":
            if d not in rows[i] and d not in cols[j] and d not in boxes[b]:
                board[i][j] = d
                rows[i].add(d); cols[j].add(d); boxes[b].add(d)
                if go(k + 1):
                    return True
                rows[i].discard(d); cols[j].discard(d); boxes[b].discard(d)
        board[i][j] = "."
        return False

    go(0)


_SUDOKU_SOLVED = [
    "534678912", "672195348", "198342567", "859761423", "426853791", "713924856", "961537284", "287419635", "345286179",
]


def _sudoku_puzzle(r):
    # Relabel digits and shuffle rows inside bands to get a different valid grid, then blank some cells.
    perm = dict(zip("123456789", r.sample("123456789", 9)))
    rows = []
    for band in range(3):
        idx = r.sample(range(3), 3)
        rows += [_SUDOKU_SOLVED[band * 3 + i] for i in idx]
    board = [[perm[c] for c in row] for row in rows]
    for i in range(9):
        for j in range(9):
            if r.random() < 0.45:
                board[i][j] = "."
    return (board,)


def _sudoku_unique(board):
    count = [0]
    b = [row[:] for row in board]

    def ok(i, j, d):
        if d in b[i] or any(b[k][j] == d for k in range(9)):
            return False
        bi, bj = i // 3 * 3, j // 3 * 3
        return all(b[x][y] != d for x in range(bi, bi + 3) for y in range(bj, bj + 3))

    def go(k):
        if count[0] > 1:
            return
        if k == 81:
            count[0] += 1
            return
        i, j = divmod(k, 9)
        if b[i][j] != ".":
            go(k + 1)
            return
        for d in "123456789":
            if ok(i, j, d):
                b[i][j] = d
                go(k + 1)
                b[i][j] = "."

    go(0)
    return count[0] == 1


def _sudoku_gen(r):
    while True:
        board = _sudoku_puzzle(r)
        if _sudoku_unique(board[0]):
            return board


@problem(
    slug="sudoku-solver", title="Sudoku Solver", difficulty="Hard", pattern=B, tags=["Array", "Hash Table", "Backtracking", "Matrix"],
    sig="solveSudoku(self, board: list[list[str]]) -> None", out_arg=0, n=6,
    desc="""Fill the empty cells (`'.'`) of a 9 × 9 Sudoku so that each row, each column, and each of the nine 3 × 3 boxes contains the digits `1`–`9` exactly once.

Modify `board` **in place** and return nothing; the judge checks `board`. Every puzzle has exactly one solution.""",
    constraints=["board is 9 × 9", "cells are digits '1'–'9' or '.'", "the puzzle has exactly one solution"],
    samples=[([list("53..7...."), list("6..195..."), list(".98....6."), list("8...6...3"), list("4..8.3..1"),
               list("7...2...6"), list(".6....28."), list("...419..5"), list("....8..79")],),
             ([list(r) for r in ["534678912", "672195348", "198342567", "859761423", "426853791", "713924856", "961537284", "287419635", "3452861.."]],)],
    gen=_sudoku_gen,
    hints=[
        "List the empty cells and fill them one at a time.",
        "Keep sets of digits already used in each row, column and box so a check is O(1).",
        "Try each allowed digit in the current cell, recurse, and undo it if the rest can't be completed.",
    ],
    insight="Classic constraint backtracking: place, recurse, undo.",
    time="O(9ᵉ) worst case (e = empty cells)", space="O(81)",
    pitfalls=["Rescanning the row, column and box for every candidate digit."],
)
def solve_sudoku(board):
    _sudoku_solve(board)


@problem(
    slug="combination-sum", title="Combination Sum", difficulty="Medium", pattern=B, tags=["Array", "Backtracking"],
    sig="combinationSum(self, candidates: list[int], target: int) -> list[list[int]]", compare="unordered-deep",
    desc="""`candidates` holds distinct positive integers. Return every unique combination that sums to `target`, where each candidate may be used **any number of times**. Order doesn't matter (inside or between combinations).""",
    constraints=["1 ≤ len(candidates) ≤ 30", "2 ≤ candidates[i] ≤ 40, distinct", "1 ≤ target ≤ 40"],
    samples=[([2, 3, 6, 7], 7), ([2, 3, 5], 8), ([2], 1)],
    gen=lambda r: (r.distinct(r.randint(1, 5), 2, 9), r.randint(1, 20)),
    hints=[
        "To avoid both [2, 3] and [3, 2], only pick candidates at or after the last one chosen.",
        "Staying on the same index lets you reuse a candidate.",
        "Recurse with the remaining target; record when it hits 0 and stop when it goes negative (or sort and break early).",
    ],
    insight="Index-ordered backtracking with reuse allowed by not advancing the index.",
    time="O(n^(target / min))", space="O(target / min)",
    pitfalls=["Advancing the index after choosing, which forbids reuse."],
)
def combination_sum(candidates, target):
    out, cur = [], []
    cand = sorted(candidates)

    def go(start, left):
        if left == 0:
            out.append(cur[:])
            return
        for i in range(start, len(cand)):
            if cand[i] > left:
                break
            cur.append(cand[i])
            go(i, left - cand[i])
            cur.pop()

    go(0, target)
    return out


@problem(
    slug="combination-sum-ii", title="Combination Sum II", difficulty="Medium", pattern=B, tags=["Array", "Backtracking"],
    sig="combinationSum2(self, candidates: list[int], target: int) -> list[list[int]]", compare="unordered-deep",
    desc="""`candidates` may contain duplicates. Return every unique combination that sums to `target`, using each element **at most once**. The result must not contain duplicate combinations; order doesn't matter.""",
    constraints=["1 ≤ len(candidates) ≤ 100", "1 ≤ candidates[i] ≤ 50", "1 ≤ target ≤ 30"],
    samples=[([10, 1, 2, 7, 6, 1, 5], 8), ([2, 5, 2, 1, 2], 5)],
    gen=lambda r: (r.ints(r.randint(1, 9), 1, 6), r.randint(1, 15)),
    brute=lambda c, t: [list(x) for x in {tuple(sorted(s)) for s in _all_subsets(c) if sum(s) == t}],
    hints=[
        "Sort the candidates so duplicates are adjacent.",
        "Advance the index after choosing an element, since each can be used once.",
        "At one level of the recursion, skip a candidate equal to the previous one you tried at that same level.",
    ],
    insight="Sorting plus skip-equal-siblings avoids duplicate combinations.",
    time="O(2ⁿ)", space="O(n)",
    pitfalls=["Skipping duplicates across levels, which loses valid combinations like [1, 1, 6]."],
)
def combination_sum2(candidates, target):
    cand = sorted(candidates)
    out, cur = [], []

    def go(start, left):
        if left == 0:
            out.append(cur[:])
            return
        for i in range(start, len(cand)):
            if i > start and cand[i] == cand[i - 1]:
                continue
            if cand[i] > left:
                break
            cur.append(cand[i])
            go(i + 1, left - cand[i])
            cur.pop()

    go(0, target)
    return out


def _partitions(s):
    if not s:
        return [[]]
    return [[s[:i]] + rest for i in range(1, len(s) + 1) for rest in _partitions(s[i:])]


@problem(
    slug="palindrome-partitioning", title="Palindrome Partitioning", difficulty="Medium", pattern=B,
    tags=["String", "Dynamic Programming", "Backtracking"],
    sig="partition(self, s: str) -> list[list[str]]", compare="unordered",
    desc="""Split `s` into pieces so that every piece is a palindrome. Return every such split, in any order (pieces stay in their original order inside each split).""",
    constraints=["1 ≤ len(s) ≤ 16", "lowercase letters"],
    samples=[("aab",), ("a",)],
    gen=lambda r: (r.word(r.randint(1, 8), "ab"),),
    brute=lambda s: [p for p in _partitions(s) if all(x == x[::-1] for x in p)],
    hints=[
        "Choose the first piece, then partition the rest.",
        "Only continue when the chosen first piece is a palindrome.",
        "Backtrack over end positions; precomputing which substrings are palindromes makes each check O(1).",
    ],
    insight="Backtracking over cut positions, pruned by palindrome checks.",
    time="O(n · 2ⁿ)", space="O(n²) with the palindrome table",
    pitfalls=["Rechecking the same substrings many times without memoization."],
)
def palindrome_partition(s):
    out, cur = [], []

    def go(i):
        if i == len(s):
            out.append(cur[:])
            return
        for j in range(i + 1, len(s) + 1):
            piece = s[i:j]
            if piece == piece[::-1]:
                cur.append(piece)
                go(j)
                cur.pop()

    go(0)
    return out


def _ip_ok(part):
    return 1 <= len(part) <= 3 and (part == "0" or part[0] != "0") and int(part) <= 255


@problem(
    slug="restore-ip-addresses", title="Restore IP Addresses", difficulty="Medium", pattern=B, tags=["String", "Backtracking"],
    sig="restoreIpAddresses(self, s: str) -> list[str]", compare="unordered",
    desc="""A valid IP address has four numbers between 0 and 255 separated by dots, with no leading zeros (except a single `0`). Insert three dots into the digit string `s` to form every possible valid IP address, and return them in any order. Don't reorder or drop digits.""",
    constraints=["1 ≤ len(s) ≤ 20", "s contains only digits"],
    samples=[("25525511135",), ("0000",), ("101023",)],
    gen=lambda r: ("".join(r.choice("0125") for _ in range(r.randint(4, 12))),),
    brute=lambda s: [".".join(p) for p in ([s[:a], s[a:b], s[b:c], s[c:]] for a in range(1, len(s)) for b in range(a + 1, len(s)) for c in range(b + 1, len(s))) if all(_ip_ok(x) for x in p)],
    hints=[
        "Each of the four parts has 1 to 3 digits.",
        "A part is valid if it's ≤ 255 and has no leading zero (unless it's exactly \"0\").",
        "Backtrack over the length of each part; after four parts, accept only if all digits are used.",
    ],
    insight="A depth-4 backtrack with at most 3 choices per level.",
    time="O(3⁴)", space="O(1)",
    pitfalls=["Allowing parts like \"01\" or \"256\"."],
)
def restore_ip(s):
    out = []

    def go(i, parts):
        if len(parts) == 4:
            if i == len(s):
                out.append(".".join(parts))
            return
        for L in range(1, 4):
            part = s[i:i + L]
            if len(part) == L and _ip_ok(part):
                go(i + L, parts + [part])

    go(0, [])
    return out


def _word_break_brute(s, words):
    ws = set(words)
    out = []
    for cuts in product([0, 1], repeat=max(len(s) - 1, 0)):
        pieces, start = [], 0
        for i, c in enumerate(cuts, 1):
            if c:
                pieces.append(s[start:i])
                start = i
        pieces.append(s[start:])
        if all(p in ws for p in pieces):
            out.append(" ".join(pieces))
    return out


@problem(
    slug="word-break-ii", title="Word Break II", difficulty="Hard", pattern=B,
    tags=["Array", "Hash Table", "String", "Dynamic Programming", "Backtracking", "Memoization"],
    sig="wordBreak(self, s: str, wordDict: list[str]) -> list[str]", compare="unordered",
    desc="""Add spaces to `s` so that every resulting word is in `wordDict` (words may be reused). Return all such sentences, in any order.""",
    constraints=["1 ≤ len(s) ≤ 20", "1 ≤ len(wordDict) ≤ 1000", "words are distinct, lowercase"],
    samples=[("catsanddog", ["cat", "cats", "and", "sand", "dog"]), ("pineapplepenapple", ["apple", "pen", "applepen", "pine", "pineapple"]),
             ("catsandog", ["cats", "dog", "sand", "and", "cat"])],
    gen=lambda r: (r.word(r.randint(1, 10), "ab"), sorted({r.word(r.randint(1, 3), "ab") for _ in range(r.randint(1, 6))})),
    brute=_word_break_brute,
    hints=[
        "Try every dictionary word that is a prefix of the string, then solve the rest.",
        "The same suffix gets solved many times; memoize the sentences for each start index.",
        "For a start index, the sentences are word + \" \" + each sentence of the remaining suffix (or just the word when it reaches the end).",
    ],
    insight="Memoized backtracking over suffixes.",
    time="O(2ⁿ) output-bound", space="O(2ⁿ)",
    pitfalls=["Recomputing the same suffix exponentially often."],
)
def word_break_ii(s, wordDict):
    words, memo = set(wordDict), {}

    def go(i):
        if i == len(s):
            return [""]
        if i in memo:
            return memo[i]
        out = []
        for j in range(i + 1, len(s) + 1):
            w = s[i:j]
            if w in words:
                out += [w + (" " + rest if rest else "") for rest in go(j)]
        memo[i] = out
        return out

    return go(0)


def _matchsticks_brute(sticks):
    total = sum(sticks)
    if total % 4:
        return False
    side = total // 4
    for assign in product(range(4), repeat=len(sticks)):
        sums = [0] * 4
        for s, a in zip(sticks, assign):
            sums[a] += s
        if all(x == side for x in sums):
            return True
    return False


@problem(
    slug="matchsticks-to-square", title="Matchsticks to Square", difficulty="Medium", pattern=B,
    tags=["Array", "Dynamic Programming", "Backtracking", "Bit Manipulation", "Bitmask"],
    sig="makesquare(self, matchsticks: list[int]) -> bool",
    desc="""Use **all** the matchsticks (without breaking any) to form one square. Return `true` if that's possible.""",
    constraints=["1 ≤ len(matchsticks) ≤ 15", "1 ≤ matchsticks[i] ≤ 10⁸"],
    samples=[([1, 1, 2, 2, 2],), ([3, 3, 3, 3, 4],)],
    tests=[([5, 5, 5, 5],), ([1, 1, 1],)],
    gen=lambda r: (r.ints(r.randint(1, 7), 1, 6),),
    brute=_matchsticks_brute,
    hints=[
        "The side length must be sum / 4, and that must be an integer.",
        "Assign each stick to one of four sides without exceeding the side length.",
        "Sort sticks in descending order to fail fast, and skip trying a side whose current length equals a side you already tried for this stick.",
    ],
    insight="Backtracking over side assignments with strong pruning.",
    time="O(4ⁿ) worst case", space="O(n)",
    pitfalls=["Not checking that the total is divisible by 4 first."],
)
def makesquare(matchsticks):
    total = sum(matchsticks)
    if total % 4:
        return False
    side = total // 4
    sticks = sorted(matchsticks, reverse=True)
    if sticks[0] > side:
        return False
    sides = [0] * 4

    def go(i):
        if i == len(sticks):
            return True
        tried = set()
        for k in range(4):
            if sides[k] + sticks[i] <= side and sides[k] not in tried:
                tried.add(sides[k])
                sides[k] += sticks[i]
                if go(i + 1):
                    return True
                sides[k] -= sticks[i]
        return False

    return go(0)


def _min_transfers_brute(transactions):
    bal = Counter()
    for a, b, amt in transactions:
        bal[a] -= amt
        bal[b] += amt
    debts = [v for v in bal.values() if v]
    # Answer = n − (max number of disjoint zero-sum groups).
    n = len(debts)
    from functools import lru_cache

    @lru_cache(None)
    def best(mask):
        if mask == 0:
            return 0
        res = 0
        sub = mask
        while sub:
            if sum(debts[i] for i in range(n) if sub >> i & 1) == 0:
                res = max(res, 1 + best(mask ^ sub))
            sub = (sub - 1) & mask
        return res

    return n - best((1 << n) - 1)


@problem(
    slug="optimal-account-balancing", title="Optimal Account Balancing", difficulty="Hard", pattern=B,
    tags=["Array", "Dynamic Programming", "Backtracking", "Bit Manipulation", "Bitmask"],
    sig="minTransfers(self, transactions: list[list[int]]) -> int",
    desc="""Each transaction `[from, to, amount]` means person `from` gave `amount` to person `to`. Return the minimum number of transactions needed to settle all debts.""",
    constraints=["1 ≤ len(transactions) ≤ 8", "0 ≤ from, to < 12, from ≠ to", "1 ≤ amount ≤ 100"],
    samples=[([[0, 1, 10], [2, 0, 5]],), ([[0, 1, 10], [1, 0, 1], [1, 2, 5], [2, 0, 5]],)],
    gen=lambda r: ([(lambda a: [a, r.choice([x for x in range(6) if x != a]), r.randint(1, 10)])(r.randint(0, 5)) for _ in range(r.randint(1, 6))],),
    brute=_min_transfers_brute,
    hints=[
        "Only each person's net balance matters; people with balance 0 can be ignored.",
        "Settle the first non-zero balance by pairing it with a later balance of the opposite sign, then recurse.",
        "Take the minimum over all choices, skipping duplicate balances at the same step to prune.",
    ],
    insight="Reduce to net balances, then backtrack: each step zeroes out at least one person.",
    time="O(n!) worst case", space="O(n)",
    pitfalls=["Simulating the original transactions instead of working with net balances."],
)
def min_transfers(transactions):
    bal = Counter()
    for a, b, amt in transactions:
        bal[a] -= amt
        bal[b] += amt
    debts = [v for v in bal.values() if v]

    def go(i):
        while i < len(debts) and debts[i] == 0:
            i += 1
        if i == len(debts):
            return 0
        best, tried = float("inf"), set()
        for j in range(i + 1, len(debts)):
            if debts[i] * debts[j] < 0 and debts[j] not in tried:
                tried.add(debts[j])
                debts[j] += debts[i]
                best = min(best, 1 + go(i + 1))
                debts[j] -= debts[i]
        return best

    return go(0)


@problem(
    slug="flood-fill", title="Flood Fill", difficulty="Easy", pattern=B, tags=["Array", "Depth-First Search", "Breadth-First Search", "Matrix"],
    sig="floodFill(self, image: list[list[int]], sr: int, sc: int, color: int) -> list[list[int]]",
    desc="""Starting from pixel `(sr, sc)`, recolor it and every pixel connected to it (4-directionally) through pixels of the **same original color** to `color`. Return the modified image.""",
    constraints=["1 ≤ m, n ≤ 50", "0 ≤ pixel values, color < 2¹⁶"],
    samples=[([[1, 1, 1], [1, 1, 0], [1, 0, 1]], 1, 1, 2), ([[0, 0, 0], [0, 0, 0]], 0, 0, 0)],
    gen=lambda r: (lambda m, n: ([[r.randint(0, 2) for _ in range(n)] for _ in range(m)], r.randint(0, m - 1), r.randint(0, n - 1), r.randint(0, 3)))(r.randint(1, 5), r.randint(1, 5)),
    hints=[
        "Remember the original color of the start pixel.",
        "Visit neighbors that still have the original color, and recolor as you go.",
        "If the new color equals the original color, nothing changes; handle that first to avoid looping forever.",
    ],
    insight="DFS or BFS over same-colored neighbors.",
    time="O(m·n)", space="O(m·n)",
    pitfalls=["Infinite recursion when the new color equals the old one."],
)
def flood_fill(image, sr, sc, color):
    old = image[sr][sc]
    if old == color:
        return image
    stack = [(sr, sc)]
    while stack:
        i, j = stack.pop()
        if 0 <= i < len(image) and 0 <= j < len(image[0]) and image[i][j] == old:
            image[i][j] = color
            stack += [(i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)]
    return image


EXTRA = {
    "find-k-sum-subsets": {
        "edge": [([1], 1), ([1], 2), ([2, 3], 5), ([5, 10], 3)],
        "edge_nb": [(list(range(1, 11)), 15), ([100, 99, 98, 97, 96, 95, 94, 93, 92, 91], 1000)],
    },
    "permutations": {"edge": [([0],), ([-10, 10],), ([1, 2, 3, 4, 5, 6],)]},
    "letter-combinations-of-a-phone-number": {"edge": [("",), ("7",), ("79",), ("9999",), ("2345",)]},
    "generate-parentheses": {"edge": [(7,)], "edge_nb": [(8,)]},
    "letter-case-permutation": {"edge": [("1",), ("C",), ("0a0",), ("abcdefghijk",)]},
    "letter-tile-possibilities": {"edge": [("A",), ("AAAAAAA",), ("ABCDEFG",), ("AABBCCD",)]},
    "subsets-ii": {"edge": [([0],), ([1, 1],), ([4, 4, 4, 1, 4],), ([1, 2, 2, 3, 3, 3, 4, 4, 4, 4],)]},
    "permutations-ii": {"edge": [([1],), ([2, 2, 2],), ([1, 1, 1, 1, 2, 2, 3, 3],), ([3, 3, 0, 3],)]},
    "combinations": {"edge": [(1, 1), (5, 5), (20, 1), (20, 19), (6, 3)]},
    "n-queens": {"edge": [(2,), (3,), (7,)], "edge_nb": [(8,), (9,)]},
    "n-queens-ii": {"edge": [(2,), (3,), (7,)], "edge_nb": [(9,)]},
    "word-search": {
        "edge": [([["A"]], "A"), ([["A"]], "AA"), ([["A", "B"]], "BA"), ([["A", "A"]], "AAA"), ([["C", "A", "A"], ["A", "A", "A"], ["B", "C", "D"]], "AAB")],
        "edge_nb": [([["A"] * 6 for _ in range(6)], "AAAAAAAAAAAAAAB")],
    },
    "combination-sum": {
        "edge": [([2], 2), ([3], 2), ([2, 3, 5], 1), ([7, 3, 2], 18)],
        "edge_nb": [([2, 3, 5], 40), (list(range(2, 32)), 12)],
    },
    "combination-sum-ii": {
        "edge": [([1], 1), ([2], 1), ([1, 1, 1, 1], 2), ([2, 5, 2, 1, 2], 5)],
        "edge_nb": [([1] * 100, 30), ([r for r in range(1, 51)] + [r for r in range(1, 51)], 30)],
    },
    "palindrome-partitioning": {"edge": [("a",), ("aa",), ("ab",), ("racecar",)], "edge_nb": [("aaaaaaaaaa",), ("abacabadabacabae",)]},
    "restore-ip-addresses": {"edge": [("1",), ("1111",), ("0000",), ("010010",), ("255255255255",), ("2552552552551",)]},
    "word-break-ii": {
        "edge": [("a", ["a"]), ("a", ["b"]), ("aaaa", ["a", "aa"]), ("catsandog", ["cats", "dog", "sand", "and", "cat"])],
        "edge_nb": [("aaaaaaaaaaaaaaaaaaab", ["a", "aa", "aaa", "aaaa", "aaaaa"]), ("aaaaaaaaaa", ["a", "aa", "aaa"])],
    },
    "matchsticks-to-square": {
        "edge": [([1],), ([1, 1, 1, 1],), ([2, 2, 2, 2, 2, 2],), ([5, 5, 5, 5, 4, 4, 4, 4, 3, 3, 3, 3],)],
        "edge_nb": [([100000000] * 4 + [1] * 8 + [2, 2, 2],), ([5, 5, 5, 5, 16, 4, 4, 4, 4, 4, 3, 3, 3, 3, 4],), ([1] * 15,)],
    },
    "optimal-account-balancing": {
        "edge": [([[0, 1, 1]],), ([[0, 1, 5], [1, 0, 5]],), ([[0, 1, 2], [1, 2, 2], [2, 3, 2]],)],
        "edge_nb": [([[0, 1, 10], [2, 3, 10], [4, 5, 10], [6, 7, 10], [8, 9, 10], [10, 11, 10], [1, 2, 3], [3, 4, 7]],),
                    ([[i, i + 1, i + 1] for i in range(8)],)],
    },
    "flood-fill": {
        "edge": [([[0]], 0, 0, 0), ([[0]], 0, 0, 65535), ([[1, 1], [1, 1]], 1, 1, 1), ([[0, 0, 0], [0, 1, 1]], 1, 1, 1)],
        "large": [lambda r: ([[1] * 50 for _ in range(50)], 25, 25, 2), lambda r: ([[r.choice([0, 0, 1]) for _ in range(50)] for _ in range(50)], 0, 0, 9)],
    },
}
