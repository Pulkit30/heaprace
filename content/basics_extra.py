"""Extra hidden tests for the 31 hand-written problems (built by content/build_basics.py).

Per slug: edge (hand-picked edge cases, checked against brute), edge_nb (no brute check), gen + n (generated
inputs, checked against brute), large (near-limit inputs for timing; reference only), brute (slow but obviously
correct solution). Inputs must respect each problem's constraints in src/lib/problems.ts.
"""

from collections import Counter, deque
from itertools import combinations


def _two_sum_input(r, n, lo, hi):
    while True:
        nums = r.distinct(n, lo, hi)
        i, j = r.sample(range(n), 2)
        target = nums[i] + nums[j]
        seen, pairs = set(), 0
        for x in nums:
            if target - x in seen:
                pairs += 1
            seen.add(x)
        if pairs == 1:
            return nums, target


def _two_sum_brute(nums, target):
    for i, j in combinations(range(len(nums)), 2):
        if nums[i] + nums[j] == target:
            return [i, j]


def _parens_brute(s):
    while "()" in s or "[]" in s or "{}" in s:
        s = s.replace("()", "").replace("[]", "").replace("{}", "")
    return s == ""


def _balanced_parens(r, pairs):
    out, stack = [], []
    opens = {"(": ")", "[": "]", "{": "}"}
    remaining = pairs
    while remaining or stack:
        if remaining and (not stack or r.random() < 0.5):
            c = r.choice("([{")
            out.append(c)
            stack.append(opens[c])
            remaining -= 1
        else:
            out.append(stack.pop())
    return "".join(out)


def _top_k_input(r, distinct, k):
    vals = r.distinct(distinct, -1000, 1000)
    nums = []
    for rank, v in enumerate(vals):
        nums += [v] * (distinct - rank)
    r.shuffle(nums)
    return nums, k


def _top_k_brute(nums, k):
    return [v for v, _ in Counter(nums).most_common(k)]


def _merge_brute(intervals):
    out = []
    for s, e in sorted(intervals):
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out


def _trap_brute(h):
    return sum(max(0, min(max(h[: i + 1]), max(h[i:])) - h[i]) for i in range(len(h)))


def _rotated_distinct(r, n):
    a = sorted(r.distinct(n, -10000, 10000))
    k = r.randint(0, n - 1)
    return a[k:] + a[:k]


def _dup_array(r, n):
    nums = list(range(1, n + 1)) + [r.randint(1, n)]
    r.shuffle(nums)
    return (nums,)


def _disappeared_input(r, n):
    return ([r.randint(1, n) for _ in range(n)],)


def _islands_grid(r, m, n, p=0.4):
    return ([["1" if r.random() < p else "0" for _ in range(n)] for _ in range(m)],)


def _islands_brute(grid):
    seen, count = set(), 0
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == "1" and (i, j) not in seen:
                count += 1
                q = deque([(i, j)])
                seen.add((i, j))
                while q:
                    a, b = q.popleft()
                    for x, y in ((a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)):
                        if 0 <= x < len(grid) and 0 <= y < len(grid[0]) and grid[x][y] == "1" and (x, y) not in seen:
                            seen.add((x, y))
                            q.append((x, y))
    return count


def _sorted_matrix(r, n, step_hi=5):
    m = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            base = max(m[i - 1][j] if i else -10**6, m[i][j - 1] if j else -10**6)
            m[i][j] = base + r.randint(0, step_hi)
    return m


def _ipo_input(r, n):
    return r.randint(1, n), r.randint(0, 50), r.ints(n, 0, 10000), r.ints(n, 0, 1000)


def _ipo_brute(k, w, profits, capital):
    done = set()
    for _ in range(k):
        best = max((i for i in range(len(profits)) if i not in done and capital[i] <= w), key=lambda i: profits[i], default=None)
        if best is None:
            break
        done.add(best)
        w += profits[best]
    return w


def _single_input(r, pairs):
    vals = r.distinct(pairs + 1, -30000, 30000)
    nums = vals + vals[1:]
    r.shuffle(nums)
    return (nums,)


def _lcs_brute(a, b):
    from functools import lru_cache

    @lru_cache(None)
    def go(i, j):
        if i == len(a) or j == len(b):
            return 0
        if a[i] == b[j]:
            return 1 + go(i + 1, j + 1)
        return max(go(i + 1, j), go(i, j + 1))

    return go(0, 0)


def _redundant_input(r, n):
    edges = [[r.randint(1, i - 1), i] for i in range(2, n + 1)]
    while True:
        a, b = sorted(r.sample(range(1, n + 1), 2))
        if [a, b] not in edges:
            break
    edges.append([a, b])
    r.shuffle(edges)
    return ([sorted(e) for e in edges],)


def _redundant_brute(edges):
    n = len(edges)
    for skip in range(n - 1, -1, -1):
        parent = list(range(n + 1))

        def find(x):
            while parent[x] != x:
                x = parent[x]
            return x

        ok = True
        for i, (a, b) in enumerate(edges):
            if i == skip:
                continue
            ra, rb = find(a), find(b)
            if ra == rb:
                ok = False
                break
            parent[ra] = rb
        if ok:
            return edges[skip]


def _course_input(r, n, m, cyclic):
    order = r.sample(range(n), n)
    pairs = set()
    m = min(m, n * (n - 1) // 2)
    while len(pairs) < m:
        a, b = sorted(r.sample(range(n), 2))
        pairs.add((order[b], order[a]))
    pairs = [list(p) for p in pairs]
    if cyclic:
        a, b = pairs[0]
        pairs.append([b, a])
    return n, pairs


def _course_brute(n, prereqs):
    indeg, g = [0] * n, [[] for _ in range(n)]
    for a, b in prereqs:
        g[b].append(a)
        indeg[a] += 1
    done = 0
    ready = [i for i in range(n) if indeg[i] == 0]
    while ready:
        u = ready.pop()
        done += 1
        for v in g[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                ready.append(v)
    return done == n


def _network_input(r, n, m):
    edges = set()
    while len(edges) < m:
        edges.add(tuple(r.sample(range(1, n + 1), 2)))
    return [[a, b, r.randint(0, 100)] for a, b in edges], n, r.randint(1, n)


def _network_brute(times, n, k):
    inf = float("inf")
    d = [inf] * (n + 1)
    d[k] = 0
    for _ in range(n):
        for u, v, w in times:
            if d[u] + w < d[v]:
                d[v] = d[u] + w
    best = max(d[1:])
    return -1 if best == inf else best


def _happy_brute(n):
    seen = set()
    while n != 1 and n not in seen:
        seen.add(n)
        n = sum(int(c) ** 2 for c in str(n))
    return n == 1


def _replace_input(r, roots, words):
    dictionary = sorted({r.word(r.randint(1, 3), "abc") for _ in range(roots)})
    return dictionary, " ".join(r.word(r.randint(1, 8), "abc") for _ in range(words))


def _replace_brute(dictionary, sentence):
    out = []
    for w in sentence.split(" "):
        best = w
        for root in dictionary:
            if w.startswith(root) and len(root) < len(best):
                best = root
        out.append(best)
    return " ".join(out)


def _tree_levels(values):
    from catalog_lib import to_tree
    root = to_tree(values)
    out, level = [], [root] if root else []
    while level:
        out.append([n.val for n in level])
        level = [c for n in level for c in (n.left, n.right) if c]
    return out


def _left_chain(vals):
    out = [vals[0]]
    for v in vals[1:]:
        out += [v, None]
    return out[:-1] if out[-1] is None else out


EXTRA = {
    "two-sum": {
        "edge": [([1, 2], 3), ([-1000000000, 1000000000], 0), ([0, 4, 3, 0], 0), ([-3, 4, 3, 90], 0)],
        "gen": lambda r: _two_sum_input(r, r.randint(2, 12), -50, 50), "n": 2, "brute": _two_sum_brute,
        "large": [lambda r: _two_sum_input(r, 10000, -10**9, 10**9)],
    },
    "valid-parentheses": {
        "edge": [("(",), (")",), ("([)]",), ("{[]}",), ("((",), ("]",)],
        "gen": lambda r: (_balanced_parens(r, r.randint(1, 8)) if r.random() < 0.6 else r.word(r.randint(1, 10), "()[]{}"),), "n": 2, "brute": _parens_brute,
        "large": [lambda r: (_balanced_parens(r, 5000),), lambda r: ("(" * 5000 + ")" * 4999 + "]",)],
    },
    "best-time-to-buy-and-sell-stock": {
        "edge": [([1],), ([2, 4, 1],), ([3, 3, 3],), ([0, 10000],)],
        "gen": lambda r: (r.ints(r.randint(1, 15), 0, 50),), "n": 2,
        "brute": lambda p: max([0] + [p[j] - p[i] for i in range(len(p)) for j in range(i + 1, len(p))]),
        "large": [lambda r: (r.ints(15000, 0, 10000),), lambda r: (list(range(15000, 0, -1)),)],
    },
    "contains-duplicate": {
        "edge": [([1],), ([1, 1],), ([-1000000000, 1000000000],), ([0, 0, 0],)],
        "gen": lambda r: (r.ints(r.randint(1, 15), -20, 20),), "n": 2, "brute": lambda nums: len(set(nums)) < len(nums),
        "large": [lambda r: (r.distinct(12000, -10**9, 10**9),), lambda r: (r.distinct(11999, -10**9, 10**9) + [7],)],
    },
    "maximum-subarray": {
        "edge": [([-1],), ([-3, -2, -5],), ([0],), ([10000, -10000, 10000],)],
        "gen": lambda r: (r.ints(r.randint(1, 15), -20, 20),), "n": 2,
        "brute": lambda a: max(sum(a[i:j]) for i in range(len(a)) for j in range(i + 1, len(a) + 1)),
        "large": [lambda r: (r.ints(15000, -10000, 10000),), lambda r: ([-1] * 15000,)],
    },
    "longest-substring-without-repeating-characters": {
        "edge": [("",), (" ",), ("au",), ("dvdf",), ("abba",), ("tmmzuxt",)],
        "gen": lambda r: (r.word(r.randint(0, 15), "abcd "),), "n": 2,
        "brute": lambda s: max([0] + [j - i for i in range(len(s)) for j in range(i + 1, len(s) + 1) if len(set(s[i:j])) == j - i]),
        "large": [lambda r: (r.word(50000, "abcdefghijklmnopqrstuvwxyz0123456789!@# "),), lambda r: ("abcdefghijklmnopqrstuvwxyz" * 1900,)],
    },
    "kth-largest-element-in-an-array": {
        "edge": [([1], 1), ([2, 1], 1), ([2, 1], 2), ([-1, -1], 2), ([5, 5, 5, 5], 3)],
        "gen": lambda r: (lambda a: (a, r.randint(1, len(a))))(r.ints(r.randint(1, 15), -20, 20)), "n": 2,
        "brute": lambda nums, k: sorted(nums, reverse=True)[k - 1],
        "large": [lambda r: (r.ints(20000, -10000, 10000), 7000), lambda r: ([1] * 20000, 20000)],
    },
    "top-k-frequent-elements": {
        "edge": [([5], 1), ([4, 4, 1], 1), ([1, 2, 2, 3, 3, 3], 3), ([-1, -1, 7], 1)],
        "gen": lambda r: (lambda d: _top_k_input(r, d, r.randint(1, d)))(r.randint(1, 5)), "n": 2, "brute": _top_k_brute,
        "large": [lambda r: _top_k_input(r, 140, 30)],
    },
    "merge-intervals": {
        "edge": [([[1, 1]],), ([[1, 4], [0, 4]],), ([[1, 4], [2, 3]],), ([[0, 0], [1, 1]],), ([[2, 3], [4, 5], [6, 7], [8, 9], [1, 10]],)],
        "gen": lambda r: ([sorted([r.randint(0, 30), r.randint(0, 30)]) for _ in range(r.randint(1, 8))],), "n": 2, "brute": _merge_brute,
        "large": [lambda r: ([sorted([r.randint(0, 10000), r.randint(0, 10000)]) for _ in range(6000)],)],
    },
    "trapping-rain-water": {
        "edge": [([0],), ([5],), ([2, 0, 2],), ([5, 4, 1, 2],), ([0, 0, 0],)],
        "gen": lambda r: (r.ints(r.randint(1, 15), 0, 8),), "n": 2, "brute": _trap_brute,
        "large": [lambda r: (r.ints(15000, 0, 100000),), lambda r: ([100000] + [0] * 14998 + [100000],)],
    },
    "subarray-sum-equals-k": {
        "edge": [([1], 0), ([1], 1), ([0, 0, 0], 0), ([-1, -1, 1], 0), ([1, -1, 0], 0)],
        "gen": lambda r: (r.ints(r.randint(1, 15), -3, 3), r.randint(-4, 4)), "n": 2,
        "brute": lambda a, k: sum(1 for i in range(len(a)) for j in range(i + 1, len(a) + 1) if sum(a[i:j]) == k),
        "large": [lambda r: (r.ints(15000, -1000, 1000), 0), lambda r: ([0] * 15000, 0)],
    },
    "find-all-numbers-disappeared-in-an-array": {
        "edge": [([1],), ([1, 1],), ([2, 2],), ([1, 2, 3],)],
        "gen": lambda r: _disappeared_input(r, r.randint(1, 15)), "n": 2,
        "brute": lambda nums: [x for x in range(1, len(nums) + 1) if x not in nums],
        "large": [lambda r: _disappeared_input(r, 15000)],
    },
    "spiral-matrix": {
        "edge": [([[1]],), ([[1, 2, 3]],), ([[1], [2], [3]],), ([[1, 2], [3, 4], [5, 6]],), ([[i * 10 + j for j in range(10)] for i in range(10)],)],
    },
    "search-in-rotated-sorted-array": {
        "edge": [([1], 0), ([1], 1), ([3, 1], 1), ([1, 3], 3), ([5, 1, 3], 5)],
        "gen": lambda r: (lambda a: (a, r.choice(a + [r.randint(-10000, 10000)])))(_rotated_distinct(r, r.randint(1, 12))), "n": 2,
        "brute": lambda nums, t: nums.index(t) if t in nums else -1,
        "large": [lambda r: (lambda a: (a, a[r.randint(0, 4999)]))(_rotated_distinct(r, 5000))],
    },
    "reverse-linked-list": {
        "edge": [([],), ([1],), ([-5000, 5000],), ([7, 7, 7],)],
        "gen": lambda r: (r.ints(r.randint(0, 12), -50, 50),), "n": 2, "brute": None,
        "large": [lambda r: (r.ints(5000, -5000, 5000),)],
    },
    "daily-temperatures": {
        "edge": [([30],), ([100, 30],), ([30, 30, 30],), ([30, 100],), ([89, 62, 70, 58, 47, 47, 46, 76, 100, 70],)],
        "gen": lambda r: (r.ints(r.randint(1, 15), 30, 40),), "n": 2,
        "brute": lambda t: [next((j - i for j in range(i + 1, len(t)) if t[j] > t[i]), 0) for i in range(len(t))],
        "large": [lambda r: ([99] * 14999 + [100],), lambda r: ([100] * 15000,), lambda r: (r.ints(15000, 30, 100),)],
    },
    "find-the-duplicate-number": {
        "edge": [([1, 1],), ([1, 1, 2],), ([2, 2, 2],), ([1, 4, 4, 2, 4],)],
        "gen": lambda r: _dup_array(r, r.randint(1, 12)), "n": 2,
        "brute": lambda nums: next(v for v in nums if nums.count(v) > 1),
        "large": [lambda r: _dup_array(r, 15000)],
    },
    "maximum-depth-of-binary-tree": {
        "edge": [([],), ([0],), ([1, 2, None, 3],), ([1, None, 2, None, 3, None, 4],)],
        "gen": lambda r: (r.tree(r.randint(0, 12), -100, 100),), "n": 2,
        "large": [lambda r: (r.tree(10000, -100, 100),), lambda r: (_left_chain(r.ints(3000, -100, 100)),)],
    },
    "binary-tree-level-order-traversal": {
        "edge": [([],), ([1, 2],), ([1, None, 2],), ([1, 2, 3, 4, None, None, 5],)],
        "gen": lambda r: (r.tree(r.randint(0, 12), -1000, 1000),), "n": 2, "brute": None,
        "large": [lambda r: (r.tree(2000, -1000, 1000),)],
    },
    "subsets": {
        "edge": [([5],), ([-10, 10],), ([1, 2, 3, 4],), (list(range(10)),)],
    },
    "replace-words": {
        "edge": [(["a"], "a"), (["b"], "a"), (["a", "aa", "aaa"], "aaaa aa a"), (["catt", "cat", "bat", "rat"], "the cattle was rattled by the battery")],
        "gen": lambda r: _replace_input(r, r.randint(1, 4), r.randint(1, 6)), "n": 2, "brute": _replace_brute,
        "large": [lambda r: _replace_input(r, 300, 12000)],
    },
    "number-of-islands": {
        "edge": [([["0"]],), ([["1"]],), ([["1", "0", "1"]],), ([["1", "1"], ["1", "1"]],)],
        "gen": lambda r: _islands_grid(r, r.randint(1, 6), r.randint(1, 6)), "n": 2, "brute": _islands_brute,
        "large": [lambda r: _islands_grid(r, 120, 120), lambda r: ([["1"] * 120 for _ in range(120)],)],
    },
    "climbing-stairs": {"edge": [(1,), (4,), (10,), (44,), (45,)]},
    "kth-smallest-element-in-a-sorted-matrix": {
        "edge": [([[1, 2], [1, 3]], 2), ([[1, 1], [1, 1]], 4), ([[-1000000000]], 1), ([[1, 2], [3, 4]], 4)],
        "gen": lambda r: (lambda n: (_sorted_matrix(r, n), r.randint(1, n * n)))(r.randint(1, 5)), "n": 2,
        "brute": lambda m, k: sorted(v for row in m for v in row)[k - 1],
        "large": [lambda r: (_sorted_matrix(r, 120, 1000), 7000)],
    },
    "ipo": {
        "edge": [(1, 0, [1], [1]), (1, 0, [5], [0]), (3, 10, [1, 2, 3], [100, 100, 100]), (10, 0, [1, 2], [0, 0])],
        "gen": lambda r: _ipo_input(r, r.randint(1, 8)), "n": 2, "brute": _ipo_brute,
        "large": [lambda r: (5000, 0, r.ints(10000, 0, 10000), r.ints(10000, 0, 10**6))],
    },
    "single-number": {
        "edge": [([1],), ([-30000],), ([0, 1, 0],), ([30000, -30000, 30000],)],
        "gen": lambda r: _single_input(r, r.randint(0, 7)), "n": 2, "brute": lambda nums: next(v for v in nums if nums.count(v) == 1),
        "large": [lambda r: _single_input(r, 6000)],
    },
    "longest-common-subsequence": {
        "edge": [("a", "a"), ("a", "b"), ("abc", "abc"), ("bl", "yby"), ("ezupkr", "ubmrapg")],
        "gen": lambda r: (r.word(r.randint(1, 10), "abc"), r.word(r.randint(1, 10), "abc")), "n": 2, "brute": _lcs_brute,
        "large": [lambda r: (r.word(400, "abcd"), r.word(400, "abcd"))],
    },
    "redundant-connection": {
        "edge": [([[1, 2], [2, 3], [1, 3]],), ([[1, 3], [2, 3], [1, 2]],), ([[1, 2], [1, 3], [1, 4], [3, 4]],)],
        "gen": lambda r: _redundant_input(r, r.randint(3, 10)), "n": 2, "brute": _redundant_brute,
        "large": [lambda r: _redundant_input(r, 1000)],
    },
    "course-schedule": {
        "edge": [(1, []), (2, []), (3, [[1, 0], [2, 1], [0, 2]]), (2, [[0, 1]]), (4, [[1, 0], [2, 1], [3, 2]])],
        "gen": lambda r: (lambda n: _course_input(r, n, r.randint(1, n), r.random() < 0.5))(r.randint(2, 8)), "n": 2, "brute": _course_brute,
        "large": [lambda r: _course_input(r, 2000, 5000, False), lambda r: _course_input(r, 2000, 4999, True)],
    },
    "network-delay-time": {
        "edge": [([[1, 2, 0]], 2, 1), ([[1, 2, 1]], 3, 1), ([[1, 2, 1], [2, 3, 2], [1, 3, 4]], 3, 1), ([[1, 2, 100]], 2, 2)],
        "gen": lambda r: (lambda n: _network_input(r, n, r.randint(1, n * (n - 1))))(r.randint(2, 6)), "n": 2, "brute": _network_brute,
        "large": [lambda r: _network_input(r, 100, 6000)],
    },
    "happy-number": {
        "edge": [(1,), (7,), (4,), (2147483647,), (1111111,)],
        "gen": lambda r: (r.randint(1, 10**6),), "n": 2, "brute": _happy_brute,
    },
}

for _more in EXTRA.values():
    if _more.get("brute", 0) is None:
        del _more["brute"]
