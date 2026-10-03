from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict, deque
from functools import lru_cache
from itertools import combinations, permutations

from catalog_lib import problem

CY = "cyclic-sort"
TP = "topological-sort"
SS = "sort-and-search"


def _missing_input(r):
    n = r.randint(1, 10)
    nums = list(range(n + 1))
    nums.remove(r.randint(0, n))
    r.shuffle(nums)
    return (nums,)


@problem(
    slug="missing-number", title="Missing Number", difficulty="Easy", pattern=CY, tags=["Array", "Hash Table", "Math", "Bit Manipulation", "Sorting"],
    sig="missingNumber(self, nums: list[int]) -> int",
    desc="""`nums` contains `n` distinct numbers from the range `[0, n]`. Return the one number in the range that is missing. Try for O(n) time and O(1) extra space.""",
    constraints=["1 ≤ n ≤ 10⁴", "values are distinct and in [0, n]"],
    samples=[([3, 0, 1],), ([0, 1],), ([9, 6, 4, 2, 3, 5, 7, 0, 1],)],
    gen=_missing_input,
    brute=lambda nums: next(x for x in range(len(nums) + 1) if x not in nums),
    hints=[
        "Each value v belongs at index v, except the value n, which has no slot.",
        "Cyclic sort: swap each value into its own index (skipping n), then look for the index whose value doesn't match.",
        "Alternatively, the expected sum n(n + 1)/2 minus the actual sum (or an XOR trick) gives the answer directly.",
    ],
    insight="When values map to indices, cyclic sort places each in O(1) amortized swaps.",
    time="O(n)", space="O(1)",
    pitfalls=["Swapping the value n out of range."],
)
def missing_number(nums):
    nums = list(nums)
    i, n = 0, len(nums)
    while i < n:
        v = nums[i]
        if v < n and nums[v] != v:
            nums[i], nums[v] = nums[v], nums[i]
        else:
            i += 1
    return next((i for i in range(n) if nums[i] != i), n)


def _dups_input(r):
    n = r.randint(1, 10)
    nums = []
    for v in r.sample(range(1, n + 1), n):
        nums += [v] * r.choice([0, 1, 1, 2])
    nums = nums[:n] or [1]
    while len(nums) < n:
        nums.append(next(v for v in range(1, n + 1) if nums.count(v) < 2))
    r.shuffle(nums)
    return (nums,)


@problem(
    slug="find-all-duplicates-in-an-array", title="Find All Duplicates in an Array", difficulty="Medium", pattern=CY,
    tags=["Array", "Hash Table"],
    sig="findDuplicates(self, nums: list[int]) -> list[int]", compare="unordered",
    desc="""`nums` has length `n`, every value is in `[1, n]`, and each value appears once or twice. Return every value that appears twice, in any order, using O(n) time and O(1) extra space (the output doesn't count).""",
    constraints=["1 ≤ n ≤ 10⁵", "1 ≤ nums[i] ≤ n", "each value appears at most twice"],
    samples=[([4, 3, 2, 7, 8, 2, 3, 1],), ([1, 1, 2],), ([1],)],
    gen=_dups_input,
    brute=lambda nums: [v for v, c in Counter(nums).items() if c == 2],
    hints=[
        "Value v belongs at index v − 1.",
        "Cyclic sort the array: swap each value toward its home index unless the home already holds that value.",
        "After sorting, any index i whose value isn't i + 1 holds a duplicate.",
    ],
    insight="Cyclic sort leaves duplicates sitting in the slots of missing values.",
    time="O(n)", space="O(1)",
    pitfalls=["Swapping forever when the home index already contains the same value."],
)
def find_duplicates(nums):
    nums = list(nums)
    i = 0
    while i < len(nums):
        h = nums[i] - 1
        if nums[h] != nums[i]:
            nums[i], nums[h] = nums[h], nums[i]
        else:
            i += 1
    return [nums[i] for i in range(len(nums)) if nums[i] != i + 1]


@problem(
    slug="first-missing-positive", title="First Missing Positive", difficulty="Hard", pattern=CY, tags=["Array", "Hash Table"],
    sig="firstMissingPositive(self, nums: list[int]) -> int",
    desc="""Return the smallest positive integer that does **not** appear in the unsorted array `nums`, in O(n) time and O(1) extra space.""",
    constraints=["1 ≤ n ≤ 10⁵", "-2³¹ ≤ nums[i] ≤ 2³¹ − 1"],
    samples=[([1, 2, 0],), ([3, 4, -1, 1],), ([7, 8, 9, 11, 12],)],
    gen=lambda r: (r.ints(r.randint(1, 10), -3, 9),),
    brute=lambda nums: next(k for k in range(1, len(nums) + 2) if k not in nums),
    hints=[
        "The answer is between 1 and n + 1.",
        "Only values in [1, n] matter; place each such value v at index v − 1 with cyclic swaps.",
        "Then the first index i with nums[i] ≠ i + 1 gives i + 1; if all match, the answer is n + 1.",
    ],
    insight="Cyclic sort restricted to the useful range [1, n].",
    time="O(n)", space="O(1)",
    pitfalls=["Infinite swapping when a duplicate is already in its home slot."],
)
def first_missing_positive(nums):
    nums = list(nums)
    n, i = len(nums), 0
    while i < n:
        v = nums[i]
        if 1 <= v <= n and nums[v - 1] != v:
            nums[i], nums[v - 1] = nums[v - 1], nums[i]
        else:
            i += 1
    return next((i + 1 for i in range(n) if nums[i] != i + 1), n + 1)


def _mismatch_input(r):
    n = r.randint(2, 10)
    nums = list(range(1, n + 1))
    a, b = r.sample(range(n), 2)
    nums[a] = nums[b]
    r.shuffle(nums)
    return (nums,)


@problem(
    slug="set-mismatch", title="Set Mismatch", difficulty="Easy", pattern=CY, tags=["Array", "Hash Table", "Bit Manipulation", "Sorting"],
    sig="findErrorNums(self, nums: list[int]) -> list[int]",
    desc="""`nums` was meant to contain each number from `1` to `n` once, but one number was overwritten by a copy of another. Return `[duplicate, missing]`.""",
    constraints=["2 ≤ n ≤ 10⁴", "1 ≤ nums[i] ≤ n"],
    samples=[([1, 2, 2, 4],), ([1, 1],), ([3, 1, 3],)],
    gen=_mismatch_input,
    brute=lambda nums: [next(v for v in nums if nums.count(v) == 2), next(v for v in range(1, len(nums) + 1) if v not in nums)],
    hints=[
        "One value appears twice and one value in 1..n is absent.",
        "Cyclic sort the values into their home slots (v at index v − 1).",
        "The slot that holds the wrong value reveals both: its value is the duplicate and its index + 1 is the missing number.",
    ],
    insight="The single misplaced slot after cyclic sort contains both answers.",
    time="O(n)", space="O(1)",
    pitfalls=["Returning the answer in the order [missing, duplicate]."],
)
def find_error_nums(nums):
    nums = list(nums)
    i = 0
    while i < len(nums):
        h = nums[i] - 1
        if nums[h] != nums[i]:
            nums[i], nums[h] = nums[h], nums[i]
        else:
            i += 1
    for i, v in enumerate(nums):
        if v != i + 1:
            return [v, i + 1]


@problem(
    slug="kth-missing-positive-number", title="Kth Missing Positive Number", difficulty="Easy", pattern=CY, tags=["Array", "Binary Search"],
    sig="findKthPositive(self, arr: list[int], k: int) -> int",
    desc="""`arr` is a strictly increasing list of positive integers. Return the `k`th positive integer that is missing from it.""",
    constraints=["1 ≤ len(arr) ≤ 1000", "1 ≤ arr[i] ≤ 1000, strictly increasing", "1 ≤ k ≤ 1000"],
    samples=[([2, 3, 4, 7, 11], 5), ([1, 2, 3, 4], 2)],
    gen=lambda r: (sorted(r.distinct(r.randint(1, 8), 1, 20)), r.randint(1, 10)),
    brute=lambda arr, k: [x for x in range(1, 3000) if x not in arr][k - 1],
    hints=[
        "Before arr[i], exactly arr[i] − (i + 1) positive numbers are missing.",
        "That count never decreases as i grows.",
        "Binary search the first index where the missing count reaches k; the answer is that index + k.",
    ],
    insight="The missing-count formula turns this into a binary search (or a simple scan).",
    time="O(log n)", space="O(1)",
    pitfalls=["Off-by-one when all missing numbers come after the array."],
)
def find_kth_positive(arr, k):
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] - mid - 1 < k:
            lo = mid + 1
        else:
            hi = mid
    return lo + k


def _first_k_missing_brute(nums, k):
    s, out, x = set(nums), [], 1
    while len(out) < k:
        if x not in s:
            out.append(x)
        x += 1
    return out


@problem(
    slug="first-k-missing-positive-numbers", title="First K Missing Positive Numbers", difficulty="Hard", pattern=CY, tags=["Array", "Hash Table", "Sorting"],
    sig="firstKMissingNumbers(self, arr: list[int], k: int) -> list[int]",
    desc="""Return the `k` smallest positive integers that do not appear in the unsorted array `arr`, in increasing order.""",
    constraints=["1 ≤ len(arr) ≤ 10³", "-10⁴ ≤ arr[i] ≤ 10⁴", "1 ≤ k ≤ 10³"],
    samples=[([3, -1, 4, 5, 5], 3), ([2, 3, 4], 3), ([-2, -3, 4], 2)],
    gen=lambda r: (r.ints(r.randint(1, 10), -3, 12), r.randint(1, 6)),
    brute=_first_k_missing_brute,
    hints=[
        "Use cyclic sort to place each value v in [1, n] at index v − 1.",
        "Scan the indices: a slot without its own value is a missing number. Remember the values sitting there.",
        "If you still need more, continue with n + 1, n + 2, … skipping the out-of-place values you remembered (they may be larger than n).",
    ],
    insight="Cyclic sort finds the missing values inside [1, n]; the extra values seen tell you which bigger numbers exist.",
    time="O(n + k)", space="O(k)",
    pitfalls=["Forgetting that values larger than n can block numbers after n."],
)
def first_k_missing(arr, k):
    nums = list(arr)
    n, i = len(nums), 0
    while i < n:
        v = nums[i]
        if 1 <= v <= n and nums[v - 1] != v:
            nums[i], nums[v - 1] = nums[v - 1], nums[i]
        else:
            i += 1
    out, extra = [], set()
    for i in range(n):
        if len(out) < k and nums[i] != i + 1:
            out.append(i + 1)
            extra.add(nums[i])
    x = n + 1
    while len(out) < k:
        if x not in extra:
            out.append(x)
        x += 1
    return out


def _couples_brute(row):
    # BFS over swaps (small inputs only).
    start = tuple(row)
    goal_ok = lambda t: all(t[i] // 2 == t[i + 1] // 2 for i in range(0, len(t), 2))  # noqa: E731
    seen, q = {start}, deque([(start, 0)])
    while q:
        t, d = q.popleft()
        if goal_ok(t):
            return d
        for i, j in combinations(range(len(t)), 2):
            u = list(t)
            u[i], u[j] = u[j], u[i]
            u = tuple(u)
            if u not in seen:
                seen.add(u)
                q.append((u, d + 1))


@problem(
    slug="couples-holding-hands", title="Couples Holding Hands", difficulty="Hard", pattern=CY,
    tags=["Greedy", "Depth-First Search", "Union Find", "Graph"],
    sig="minSwapsCouples(self, row: list[int]) -> int",
    desc="""`2n` people sit in a row of seats; `row[i]` is the person in seat `i`. Couples are `(0, 1)`, `(2, 3)`, …, `(2n − 2, 2n − 1)`. In one swap, any two people exchange seats. Return the minimum swaps so that every couple sits side by side in seats `(0, 1)`, `(2, 3)`, ….""",
    constraints=["2 ≤ len(row) ≤ 60, even", "row is a permutation of 0..len − 1"],
    samples=[([0, 2, 1, 3],), ([3, 2, 0, 1],)],
    gen=lambda r: (lambda n: (r.sample(range(n), n),))(2 * r.randint(1, 3)),
    brute=_couples_brute,
    hints=[
        "Look at each seat pair (2i, 2i + 1). If the two people aren't partners, someone must move.",
        "Fixing a pair greedily (swap the partner of the first person into the second seat) never hurts.",
        "Keep a position map to find partners in O(1); count one swap for each pair you fix.",
    ],
    insight="Greedily fixing each seat pair is optimal (it's counting cycles of couples).",
    time="O(n)", space="O(n)",
    pitfalls=["Forgetting to update the position map after a swap."],
)
def min_swaps_couples(row):
    row = list(row)
    pos = {p: i for i, p in enumerate(row)}
    swaps = 0
    for i in range(0, len(row), 2):
        partner = row[i] ^ 1
        if row[i + 1] != partner:
            j = pos[partner]
            row[i + 1], row[j] = row[j], row[i + 1]
            pos[row[j]], pos[row[i + 1]] = j, i + 1
            swaps += 1
    return swaps


# ---------------------------------------------------------------- topological sort


def _recipes_brute(recipes, ingredients, supplies):
    have, made = set(supplies), []
    changed = True
    while changed:
        changed = False
        for r, ing in zip(recipes, ingredients):
            if r not in have and all(x in have for x in ing):
                have.add(r)
                made.append(r)
                changed = True
    return made


def _recipes_input(r):
    names = ["r%d" % i for i in range(r.randint(1, 5))]
    supplies = ["s%d" % i for i in range(r.randint(1, 4))]
    pool = names + supplies + ["x"]
    ingredients = [sorted(set(r.sample([p for p in pool if p != nm], r.randint(1, 3)))) for nm in names]
    return names, ingredients, supplies


@problem(
    slug="find-all-possible-recipes-from-given-supplies", title="Find All Possible Recipes from Given Supplies", difficulty="Medium", pattern=TP,
    tags=["Array", "Hash Table", "String", "Graph", "Topological Sort"],
    sig="findAllRecipes(self, recipes: list[str], ingredients: list[list[str]], supplies: list[str]) -> list[str]", compare="unordered",
    desc="""Recipe `recipes[i]` needs every item in `ingredients[i]`. An ingredient may be a basic supply (you have infinite amounts of everything in `supplies`) or another recipe. Return every recipe you can make, in any order.""",
    constraints=["1 ≤ n ≤ 100", "names are distinct lowercase strings", "a recipe never lists itself"],
    samples=[(["bread"], [["yeast", "flour"]], ["yeast", "flour", "corn"]),
             (["bread", "sandwich"], [["yeast", "flour"], ["bread", "meat"]], ["yeast", "flour", "meat"])],
    gen=_recipes_input,
    brute=_recipes_brute,
    hints=[
        "Think of a graph: an edge from each ingredient to every recipe that needs it.",
        "A recipe becomes makeable when all of its ingredients are available, i.e. its in-degree drops to 0.",
        "Run Kahn's algorithm starting from the supplies; every recipe popped from the queue is makeable.",
    ],
    insight="Topological processing from known supplies finds everything reachable; cycles never complete.",
    time="O(V + E)", space="O(V + E)",
    pitfalls=["Infinite recursion on recipes that depend on each other."],
)
def find_all_recipes(recipes, ingredients, supplies):
    need = {r: len(set(ing)) for r, ing in zip(recipes, ingredients)}
    users = defaultdict(list)
    for r, ing in zip(recipes, ingredients):
        for x in set(ing):
            users[x].append(r)
    q, out = deque(supplies), []
    while q:
        x = q.popleft()
        for r in users[x]:
            need[r] -= 1
            if need[r] == 0:
                out.append(r)
                q.append(r)
    return out


def _random_tree(r, n):
    return [[i, r.randint(0, i - 1)] for i in range(1, n)]


def _mht_brute(n, edges):
    g = defaultdict(list)
    for a, b in edges:
        g[a].append(b)
        g[b].append(a)

    def height(s):
        seen, q, h = {s}, deque([(s, 0)]), 0
        while q:
            u, d = q.popleft()
            h = max(h, d)
            for v in g[u]:
                if v not in seen:
                    seen.add(v)
                    q.append((v, d + 1))
        return h

    hs = [height(i) for i in range(n)]
    return [i for i in range(n) if hs[i] == min(hs)]


@problem(
    slug="minimum-height-trees", title="Minimum Height Trees", difficulty="Medium", pattern=TP,
    tags=["Depth-First Search", "Breadth-First Search", "Graph", "Topological Sort"],
    sig="findMinHeightTrees(self, n: int, edges: list[list[int]]) -> list[int]", compare="unordered",
    desc="""A tree has `n` nodes labelled `0..n − 1` and the given undirected `edges`. Choosing a node as the root gives a rooted tree with some height. Return every root that gives the minimum height, in any order.""",
    constraints=["1 ≤ n ≤ 2 × 10⁴", "edges form a tree"],
    samples=[(4, [[1, 0], [1, 2], [1, 3]]), (6, [[3, 0], [3, 1], [3, 2], [3, 4], [5, 4]]), (1, [])],
    gen=lambda r: (lambda n: (n, _random_tree(r, n)))(r.randint(1, 10)),
    brute=_mht_brute,
    hints=[
        "Leaves are never the best roots (unless n ≤ 2).",
        "Remove all current leaves, then the new leaves, layer by layer, like peeling an onion.",
        "Stop when at most two nodes remain: they are the centers of the tree.",
    ],
    insight="Topological peeling of leaves finds the tree's center(s).",
    time="O(n)", space="O(n)",
    pitfalls=["Computing the height from every node, which is O(n²)."],
)
def find_min_height_trees(n, edges):
    if n <= 2:
        return list(range(n))
    g = defaultdict(set)
    for a, b in edges:
        g[a].add(b)
        g[b].add(a)
    leaves = [i for i in range(n) if len(g[i]) == 1]
    left = n
    while left > 2:
        left -= len(leaves)
        nxt = []
        for leaf in leaves:
            nb = g[leaf].pop()
            g[nb].discard(leaf)
            if len(g[nb]) == 1:
                nxt.append(nb)
        leaves = nxt
    return leaves


def _dag_input(r, n=None):
    n = n or r.randint(1, 7)
    order = r.sample(range(1, n + 1), n)
    rel = set()
    for _ in range(r.randint(0, n * 2)):
        a, b = sorted(r.sample(range(n), 2)) if n > 1 else (0, 0)
        if a != b:
            rel.add((order[a], order[b]))
    return n, [list(p) for p in sorted(rel)]


def _semesters_brute(n, relations):
    pre = defaultdict(set)
    for a, b in relations:
        pre[b].add(a)
    done, sem = set(), 0
    while len(done) < n:
        ready = {c for c in range(1, n + 1) if c not in done and pre[c] <= done}
        if not ready:
            return -1
        done |= ready
        sem += 1
    return sem


def _with_cycle(r):
    n, rel = _dag_input(r)
    if n > 1 and r.random() < 0.4:
        a, b = r.sample(range(1, n + 1), 2)
        rel = rel + [[a, b], [b, a]]
    return n, rel


@problem(
    slug="parallel-courses", title="Parallel Courses", difficulty="Medium", pattern=TP, tags=["Graph", "Topological Sort"],
    sig="minimumSemesters(self, n: int, relations: list[list[int]]) -> int",
    desc="""There are `n` courses labelled `1..n`. `relations[i] = [prev, next]` means `prev` must be taken before `next`. In one semester you may take any number of courses whose prerequisites were all finished in earlier semesters. Return the minimum number of semesters, or `-1` if it's impossible (a cycle).""",
    constraints=["1 ≤ n ≤ 5000", "1 ≤ len(relations) ≤ 5000", "pairs are distinct"],
    samples=[(3, [[1, 3], [2, 3]]), (3, [[1, 2], [2, 3], [3, 1]])],
    gen=_with_cycle,
    brute=_semesters_brute,
    hints=[
        "Courses with no prerequisites can all go in semester 1.",
        "Taking a course lowers the in-degree of the courses that depend on it.",
        "Run Kahn's algorithm level by level; count levels, and if some course is never reached, there's a cycle.",
    ],
    insight="The answer is the number of BFS levels in a topological sort.",
    time="O(n + E)", space="O(n + E)",
    pitfalls=["Not detecting cycles."],
)
def minimum_semesters(n, relations):
    indeg = [0] * (n + 1)
    g = defaultdict(list)
    for a, b in relations:
        g[a].append(b)
        indeg[b] += 1
    level = [c for c in range(1, n + 1) if indeg[c] == 0]
    taken, sem = 0, 0
    while level:
        sem += 1
        taken += len(level)
        nxt = []
        for c in level:
            for d in g[c]:
                indeg[d] -= 1
                if indeg[d] == 0:
                    nxt.append(d)
        level = nxt
    return sem if taken == n else -1


def _course4_input(r):
    n, rel = _dag_input(r, r.randint(2, 7))
    pre = [[a - 1, b - 1] for a, b in rel]
    queries = [r.sample(range(n), 2) for _ in range(r.randint(1, 5))]
    return n, pre, queries


def _course4_brute(n, pre, queries):
    reach = [[False] * n for _ in range(n)]
    for a, b in pre:
        reach[a][b] = True
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if reach[i][k] and reach[k][j]:
                    reach[i][j] = True
    return [reach[a][b] for a, b in queries]


@problem(
    slug="course-schedule-iv", title="Course Schedule IV", difficulty="Medium", pattern=TP,
    tags=["Depth-First Search", "Breadth-First Search", "Graph", "Topological Sort"],
    sig="checkIfPrerequisite(self, numCourses: int, prerequisites: list[list[int]], queries: list[list[int]]) -> list[bool]",
    desc="""Courses are labelled `0..numCourses − 1`. `prerequisites[i] = [a, b]` means `a` must be taken before `b`. Prerequisites are transitive. For each query `[u, v]`, answer whether `u` is a (direct or indirect) prerequisite of `v`.""",
    constraints=["2 ≤ numCourses ≤ 100", "the prerequisite graph has no cycles", "1 ≤ len(queries) ≤ 10⁴"],
    samples=[(2, [[1, 0]], [[0, 1], [1, 0]]), (2, [], [[1, 0], [0, 1]]), (3, [[1, 2], [1, 0], [2, 0]], [[1, 0], [1, 2]])],
    gen=_course4_input,
    brute=_course4_brute,
    hints=[
        "With many queries, precompute reachability once.",
        "Process courses in topological order; each course's prerequisite set is the union of its direct prerequisites and their sets.",
        "Store the sets (or a boolean matrix / bitmasks) and answer each query in O(1).",
    ],
    insight="Propagate ancestor sets along a topological order.",
    time="O(n³) worst case or O(n · E) with bitsets", space="O(n²)",
    pitfalls=["Running a DFS per query, which is slow with 10⁴ queries."],
)
def check_if_prerequisite(numCourses, prerequisites, queries):
    g = defaultdict(list)
    indeg = [0] * numCourses
    for a, b in prerequisites:
        g[a].append(b)
        indeg[b] += 1
    anc = [set() for _ in range(numCourses)]
    q = deque(i for i in range(numCourses) if indeg[i] == 0)
    while q:
        u = q.popleft()
        for v in g[u]:
            anc[v] |= anc[u] | {u}
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return [u in anc[v] for u, v in queries]


def _safe_brute(graph):
    n = len(graph)

    def leads_to_cycle(s):
        # DFS looking for a cycle reachable from s.
        color = {}

        def dfs(u):
            color[u] = 1
            for v in graph[u]:
                if color.get(v) == 1 or (v not in color and dfs(v)):
                    return True
            color[u] = 2
            return False

        return dfs(s)

    return [i for i in range(n) if not leads_to_cycle(i)]


@problem(
    slug="find-eventual-safe-states", title="Find Eventual Safe States", difficulty="Medium", pattern=TP,
    tags=["Depth-First Search", "Breadth-First Search", "Graph", "Topological Sort"],
    sig="eventualSafeNodes(self, graph: list[list[int]]) -> list[int]",
    desc="""`graph[i]` lists the nodes that node `i` has directed edges to. A node is **safe** if every path starting from it ends at a terminal node (a node with no outgoing edges). Return all safe nodes in ascending order.""",
    constraints=["1 ≤ n ≤ 10⁴", "0 ≤ graph[i][j] < n", "graph[i] is sorted and has no duplicates"],
    samples=[([[1, 2], [2, 3], [5], [0], [5], [], []],), ([[1, 2, 3, 4], [1, 2], [3, 4], [0, 4], []],)],
    gen=lambda r: (lambda n: ([sorted(r.distinct(r.randint(0, 2), 0, n - 1)) if n > 1 else [] for _ in range(n)],))(r.randint(1, 7)),
    brute=_safe_brute,
    hints=[
        "Terminal nodes are safe. A node is safe if all its successors are safe.",
        "Reverse the edges and count, for each node, how many outgoing edges still lead to unconfirmed nodes.",
        "Start a queue with the terminal nodes; when a node's count drops to 0, it's safe too. Sort at the end.",
    ],
    insight="Kahn's algorithm on the reversed graph finds nodes that can't reach a cycle.",
    time="O(V + E)", space="O(V + E)",
    pitfalls=["Marking a node unsafe just because it's on a path that passes near a cycle."],
)
def eventual_safe_nodes(graph):
    n = len(graph)
    rev = defaultdict(list)
    out = [len(set(g)) for g in graph]
    for u, vs in enumerate(graph):
        for v in set(vs):
            rev[v].append(u)
    q = deque(i for i in range(n) if out[i] == 0)
    safe = [False] * n
    while q:
        v = q.popleft()
        safe[v] = True
        for u in rev[v]:
            out[u] -= 1
            if out[u] == 0:
                q.append(u)
    return [i for i in range(n) if safe[i]]


def _lip_brute(matrix):
    m, n = len(matrix), len(matrix[0])

    @lru_cache(None)
    def go(i, j):
        best = 1
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            x, y = i + di, j + dj
            if 0 <= x < m and 0 <= y < n and matrix[x][y] > matrix[i][j]:
                best = max(best, 1 + go(x, y))
        return best

    return max(go(i, j) for i in range(m) for j in range(n))


@problem(
    slug="longest-increasing-path-in-a-matrix", title="Longest Increasing Path in a Matrix", difficulty="Hard", pattern=TP,
    tags=["Array", "Dynamic Programming", "Depth-First Search", "Breadth-First Search", "Graph", "Topological Sort", "Memoization", "Matrix"],
    sig="longestIncreasingPath(self, matrix: list[list[int]]) -> int",
    desc="""From any cell, you may move up, down, left or right to a cell with a **strictly larger** value. Return the length (number of cells) of the longest such path.""",
    constraints=["1 ≤ m, n ≤ 200", "0 ≤ matrix[i][j] ≤ 2³¹ − 1"],
    samples=[([[9, 9, 4], [6, 6, 8], [2, 1, 1]],), ([[3, 4, 5], [3, 2, 6], [2, 2, 1]],), ([[1]],)],
    gen=lambda r: (lambda m, n: ([r.ints(n, 0, 9) for _ in range(m)],))(r.randint(1, 5), r.randint(1, 5)),
    brute=_lip_brute,
    hints=[
        "Edges go from smaller to larger values, so the graph has no cycles.",
        "The longest path starting at a cell depends only on the longest paths of its larger neighbors.",
        "Memoize a DFS (or peel cells in topological order by out-degree and count layers).",
    ],
    insight="Strictly increasing moves form a DAG, so memoized DFS gives the longest path.",
    time="O(m·n)", space="O(m·n)",
    pitfalls=["Running an unmemoized DFS from every cell, which is exponential."],
)
def longest_increasing_path(matrix):
    m, n = len(matrix), len(matrix[0])
    memo = {}

    def go(i, j):
        if (i, j) in memo:
            return memo[i, j]
        best = 1
        for x, y in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
            if 0 <= x < m and 0 <= y < n and matrix[x][y] > matrix[i][j]:
                best = max(best, 1 + go(x, y))
        memo[i, j] = best
        return best

    return max(go(i, j) for i in range(m) for j in range(n))


# ---------------------------------------------------------------- sort and search


@problem(
    slug="two-sum-less-than-k", title="Two Sum Less Than K", difficulty="Easy", pattern=SS,
    tags=["Array", "Two Pointers", "Binary Search", "Sorting"],
    sig="twoSumLessThanK(self, nums: list[int], k: int) -> int",
    desc="""Return the largest sum `nums[i] + nums[j]` with `i < j` that is **less than** `k`, or `-1` if no pair qualifies.""",
    constraints=["1 ≤ len(nums) ≤ 100", "1 ≤ nums[i] ≤ 1000", "1 ≤ k ≤ 2000"],
    samples=[([34, 23, 1, 24, 75, 33, 54, 8], 60), ([10, 20, 30], 15)],
    gen=lambda r: (r.ints(r.randint(1, 10), 1, 30), r.randint(1, 60)),
    brute=lambda nums, k: max([a + b for a, b in combinations(nums, 2) if a + b < k] or [-1]),
    hints=[
        "Sort the numbers first.",
        "With two pointers at both ends, a sum that's too big means the right value is too large for any partner.",
        "If the sum is below k, record it and move the left pointer up; otherwise move the right pointer down.",
    ],
    insight="Sorting enables a two-pointer sweep for the best sum under a bound.",
    time="O(n log n)", space="O(1)",
    pitfalls=["Accepting sums equal to k."],
)
def two_sum_less_than_k(nums, k):
    a = sorted(nums)
    i, j, best = 0, len(a) - 1, -1
    while i < j:
        s = a[i] + a[j]
        if s < k:
            best = max(best, s)
            i += 1
        else:
            j -= 1
    return best


@problem(
    slug="valid-triangle-number", title="Valid Triangle Number", difficulty="Medium", pattern=SS,
    tags=["Array", "Two Pointers", "Binary Search", "Greedy", "Sorting"],
    sig="triangleNumber(self, nums: list[int]) -> int",
    desc="""Return the number of triplets (by index) in `nums` that could be the side lengths of a triangle with positive area.""",
    constraints=["1 ≤ len(nums) ≤ 1000", "0 ≤ nums[i] ≤ 1000"],
    samples=[([2, 2, 3, 4],), ([4, 2, 3, 4],)],
    gen=lambda r: (r.ints(r.randint(1, 10), 0, 10),),
    brute=lambda nums: sum(1 for a, b, c in combinations(sorted(nums), 3) if a + b > c),
    hints=[
        "For sorted sides a ≤ b ≤ c, the only condition to check is a + b > c.",
        "Sort, then fix the largest side c.",
        "With two pointers below c: if nums[i] + nums[j] > c, every i' in [i, j) works with j, so add j − i and move j down; otherwise move i up.",
    ],
    insight="Sorting reduces the triangle test to one inequality, counted with two pointers.",
    time="O(n²)", space="O(1)",
    pitfalls=["Counting triplets that include a zero-length side."],
)
def triangle_number(nums):
    a = sorted(nums)
    count = 0
    for k in range(len(a) - 1, 1, -1):
        i, j = 0, k - 1
        while i < j:
            if a[i] + a[j] > a[k]:
                count += j - i
                j -= 1
            else:
                i += 1
    return count


@problem(
    slug="minimum-absolute-difference", title="Minimum Absolute Difference", difficulty="Easy", pattern=SS, tags=["Array", "Sorting"],
    sig="minimumAbsDifference(self, arr: list[int]) -> list[list[int]]",
    desc="""`arr` has distinct integers. Return every pair `[a, b]` with `a < b` whose difference `b − a` equals the minimum absolute difference of any two elements. List the pairs in ascending order.""",
    constraints=["2 ≤ len(arr) ≤ 10⁵", "-10⁶ ≤ arr[i] ≤ 10⁶, distinct"],
    samples=[([4, 2, 1, 3],), ([1, 3, 6, 10, 15],), ([3, 8, -10, 23, 19, -4, -14, 27],)],
    gen=lambda r: (r.distinct(r.randint(2, 10), -20, 20),),
    brute=lambda arr: (lambda d: sorted([a, b] for a, b in combinations(sorted(arr), 2) if b - a == d))(min(abs(a - b) for a, b in combinations(arr, 2))),
    hints=[
        "After sorting, the closest pair is always adjacent.",
        "One pass finds the minimum adjacent difference.",
        "A second pass (or the same one) collects every adjacent pair with that difference.",
    ],
    insight="Sorting makes the minimum difference an adjacent-pair property.",
    time="O(n log n)", space="O(n)",
    pitfalls=["Comparing all pairs, which is O(n²)."],
)
def minimum_abs_difference(arr):
    a = sorted(arr)
    d = min(y - x for x, y in zip(a, a[1:]))
    return [[x, y] for x, y in zip(a, a[1:]) if y - x == d]


@problem(
    slug="count-pairs-whose-sum-is-less-than-target", title="Count Pairs Whose Sum is Less than Target", difficulty="Easy", pattern=SS,
    tags=["Array", "Two Pointers", "Binary Search", "Sorting"],
    sig="countPairs(self, nums: list[int], target: int) -> int",
    desc="""Return the number of index pairs `i < j` with `nums[i] + nums[j] < target`.""",
    constraints=["1 ≤ len(nums) ≤ 50", "-50 ≤ nums[i], target ≤ 50"],
    samples=[([-1, 1, 2, 3, 1], 2), ([-6, 2, 5, -2, -7, -1, 3], -2)],
    gen=lambda r: (r.ints(r.randint(1, 10), -10, 10), r.randint(-10, 10)),
    brute=lambda nums, t: sum(1 for a, b in combinations(nums, 2) if a + b < t),
    hints=[
        "Pair order (by index) doesn't affect the sum, so you may sort.",
        "With two pointers at the ends of the sorted array, if a[i] + a[j] < target then i pairs with every index in (i, j].",
        "Add j − i and move i right; otherwise move j left.",
    ],
    insight="Sorting plus two pointers counts pairs in O(n log n).",
    time="O(n log n)", space="O(1)",
    pitfalls=["Counting pairs with sum equal to target."],
)
def count_pairs(nums, target):
    a = sorted(nums)
    i, j, count = 0, len(a) - 1, 0
    while i < j:
        if a[i] + a[j] < target:
            count += j - i
            i += 1
        else:
            j -= 1
    return count


@problem(
    slug="find-target-indices-after-sorting-array", title="Find Target Indices After Sorting Array", difficulty="Easy", pattern=SS,
    tags=["Array", "Binary Search", "Sorting"],
    sig="targetIndices(self, nums: list[int], target: int) -> list[int]",
    desc="""After sorting `nums` in non-decreasing order, return the indices where `target` appears, in increasing order (an empty list if none).""",
    constraints=["1 ≤ len(nums) ≤ 100", "1 ≤ nums[i], target ≤ 100"],
    samples=[([1, 2, 5, 2, 3], 2), ([1, 2, 5, 2, 3], 3), ([1, 2, 5, 2, 3], 4)],
    gen=lambda r: (r.ints(r.randint(1, 10), 1, 5), r.randint(1, 5)),
    brute=lambda nums, t: [i for i, v in enumerate(sorted(nums)) if v == t],
    hints=[
        "You don't actually need to sort.",
        "The first index of target after sorting equals how many values are smaller than it.",
        "Count the smaller values and the equal values; the indices are a consecutive range.",
    ],
    insight="Counting replaces sorting: O(n) instead of O(n log n).",
    time="O(n)", space="O(1) besides the output",
    pitfalls=["Returning indices from the unsorted array."],
)
def target_indices(nums, target):
    less = sum(1 for v in nums if v < target)
    equal = sum(1 for v in nums if v == target)
    return list(range(less, less + equal))


@problem(
    slug="sort-array-by-increasing-frequency", title="Sort Array by Increasing Frequency", difficulty="Easy", pattern=SS,
    tags=["Array", "Hash Table", "Sorting"],
    sig="frequencySort(self, nums: list[int]) -> list[int]",
    desc="""Sort `nums` by how often each value occurs, rarest first. Values with the same frequency go in **decreasing** order.""",
    constraints=["1 ≤ len(nums) ≤ 100", "-100 ≤ nums[i] ≤ 100"],
    samples=[([1, 1, 2, 2, 2, 3],), ([2, 3, 1, 3, 2],), ([-1, 1, -6, 4, 5, -6, 1, 4, 1],)],
    gen=lambda r: (r.ints(r.randint(1, 12), -4, 4),),
    hints=[
        "Count each value's frequency first.",
        "Sort with a key that combines both rules.",
        "Use the key (frequency, −value): low frequency first, and higher values first among ties.",
    ],
    insight="A composite sort key encodes both ordering rules.",
    time="O(n log n)", space="O(n)",
    pitfalls=["Breaking ties in increasing order."],
)
def frequency_sort(nums):
    c = Counter(nums)
    return sorted(nums, key=lambda v: (c[v], -v))


@problem(
    slug="most-profit-assigning-work", title="Most Profit Assigning Work", difficulty="Medium", pattern=SS,
    tags=["Array", "Two Pointers", "Binary Search", "Greedy", "Sorting"],
    sig="maxProfitAssignment(self, difficulty: list[int], profit: list[int], worker: list[int]) -> int",
    desc="""Job `i` has `difficulty[i]` and pays `profit[i]`. Worker `j` can do jobs with difficulty at most `worker[j]` and does at most one job; a job can be done by many workers. Return the maximum total profit.""",
    constraints=["1 ≤ n, m ≤ 10⁴", "1 ≤ values ≤ 10⁵"],
    samples=[([2, 4, 6, 8, 10], [10, 20, 30, 40, 50], [4, 5, 6, 7]), ([85, 47, 57], [24, 66, 99], [40, 25, 25])],
    gen=lambda r: (lambda n: (r.ints(n, 1, 10), r.ints(n, 1, 20), r.ints(r.randint(1, 6), 1, 12)))(r.randint(1, 6)),
    brute=lambda d, p, w: sum(max([p[i] for i in range(len(d)) if d[i] <= x] or [0]) for x in w),
    hints=[
        "Each worker simply takes the best-paying job they can do.",
        "Sort jobs by difficulty and keep a running maximum profit.",
        "Sort workers too and sweep both lists with one pointer, or binary search each worker's ability.",
    ],
    insight="Sorted jobs with a prefix maximum answer each worker quickly.",
    time="O(n log n + m log m)", space="O(n)",
    pitfalls=["Assuming harder jobs always pay more."],
)
def max_profit_assignment(difficulty, profit, worker):
    jobs = sorted(zip(difficulty, profit))
    total, best, i = 0, 0, 0
    for w in sorted(worker):
        while i < len(jobs) and jobs[i][0] <= w:
            best = max(best, jobs[i][1])
            i += 1
        total += best
    return total


@problem(
    slug="h-index", title="H-Index", difficulty="Medium", pattern=SS, tags=["Array", "Sorting", "Counting Sort"],
    sig="hIndex(self, citations: list[int]) -> int",
    desc="""`citations[i]` is the number of citations of a researcher's `i`th paper. The h-index is the largest `h` such that at least `h` papers have at least `h` citations each. Return it.""",
    constraints=["1 ≤ n ≤ 5000", "0 ≤ citations[i] ≤ 1000"],
    samples=[([3, 0, 6, 1, 5],), ([1, 3, 1],)],
    gen=lambda r: (r.ints(r.randint(1, 10), 0, 10),),
    brute=lambda c: max(h for h in range(len(c) + 1) if sum(x >= h for x in c) >= h),
    hints=[
        "Sort the citations in descending order.",
        "At position i (0-based), i + 1 papers have at least citations[i] citations.",
        "The h-index is the number of positions where citations[i] ≥ i + 1.",
    ],
    insight="After sorting, the h-index is where the curve crosses the diagonal.",
    time="O(n log n)", space="O(1)",
    pitfalls=["Returning a citation count instead of a paper count."],
)
def h_index(citations):
    c = sorted(citations, reverse=True)
    return sum(1 for i, x in enumerate(c) if x >= i + 1)


def _perm_missing(r, n):
    nums = list(range(n + 1))
    nums.remove(r.randint(0, n))
    r.shuffle(nums)
    return (nums,)


def _big_dups(r, n):
    vals = r.sample(range(1, n + 1), n)
    twice = vals[: n // 3]
    nums = twice * 2 + vals[n // 3: n - n // 3]
    r.shuffle(nums)
    return (nums,)


def _big_mismatch(r, n):
    nums = list(range(1, n + 1))
    a, b = r.sample(range(n), 2)
    nums[a] = nums[b]
    r.shuffle(nums)
    return (nums,)


def _recipe_chain(n):
    names = ["r%d" % i for i in range(n)]
    ingredients = [["flour"] if i == 0 else [names[i - 1], "salt"] for i in range(n)]
    return names, ingredients, ["flour", "salt"]


def _big_dag(r, n, m):
    order = r.sample(range(n), n)
    edges = set()
    while len(edges) < m:
        a, b = sorted(r.sample(range(n), 2))
        edges.add((order[a], order[b]))
    return [list(e) for e in edges]


def _safe_graph(r, n):
    return ([sorted(set(r.ints(r.randint(0, 3), 0, n - 1))) for _ in range(n)],)


EXTRA = {
    "missing-number": {
        "edge": [([0],), ([1],), ([1, 2],), ([0, 1],)],
        "large": [lambda r: _perm_missing(r, 10000)],
    },
    "find-all-duplicates-in-an-array": {
        "edge": [([1],), ([1, 1],), ([2, 2],), ([2, 1, 2, 1],)],
        "large": [lambda r: _big_dups(r, 15000)],
    },
    "first-missing-positive": {
        "edge": [([1],), ([2],), ([2147483647],), ([-2147483648],), ([1, 1],), ([1, 2, 3],)],
        "large": [lambda r: (lambda p: (p[0],))(_perm_missing(r, 12000)), lambda r: (r.ints(12000, -2**31, 2**31 - 1),)],
    },
    "set-mismatch": {
        "edge": [([2, 2],), ([1, 1],), ([3, 2, 2],), ([1, 3, 3],)],
        "large": [lambda r: _big_mismatch(r, 10000)],
    },
    "kth-missing-positive-number": {"edge": [([1], 1), ([2], 1), ([1000], 1000), (list(range(1, 1001)), 1000), ([1, 2, 3], 1)]},
    "first-k-missing-positive-numbers": {
        "edge": [([1], 1), ([-1], 3), ([1, 2, 3], 2), ([2, 2, 2], 2), ([10000], 5)],
        "large": [lambda r: (r.ints(1000, -10000, 10000), 1000)],
    },
    "couples-holding-hands": {
        "edge": [([0, 1],), ([1, 0],), ([0, 2, 1, 3],), ([5, 4, 2, 6, 3, 1, 0, 7],)],
        "edge_nb": [(list(range(59, -1, -1)),), ([(i * 7) % 60 for i in range(60)],)],
    },
    "find-all-possible-recipes-from-given-supplies": {
        "edge": [(["a"], [["a"]], ["x"]), (["a", "b"], [["b"], ["a"]], ["x"]), (["a"], [["x", "x"]], ["x"]), (["a"], [["y"]], ["x"])],
        "large": [lambda r: _recipe_chain(100)],
    },
    "minimum-height-trees": {
        "edge": [(1, []), (2, [[0, 1]]), (3, [[0, 1], [1, 2]]), (4, [[0, 1], [1, 2], [2, 3]])],
        "large": [lambda r: (10000, [[i, i + 1] for i in range(9999)]), lambda r: (10000, _random_tree(r, 10000))],
    },
    "parallel-courses": {
        "edge": [(1, []), (2, [[1, 2]]), (2, [[1, 2], [2, 1]]), (3, [[1, 2], [1, 3]]), (4, [[1, 2], [2, 3], [3, 1]])],
        "large": [lambda r: (5000, [[i, i + 1] for i in range(1, 5000)]), lambda r: (5000, [[a + 1, b + 1] for a, b in _big_dag(r, 5000, 5000)])],
    },
    "course-schedule-iv": {
        "edge": [(2, [], [[0, 1]]), (3, [[0, 1], [1, 2]], [[0, 2], [2, 0]]), (4, [[2, 3], [2, 1], [0, 3], [0, 1]], [[0, 1], [0, 3], [2, 3], [3, 0], [2, 0], [0, 2]])],
        "large": [lambda r: (100, _big_dag(r, 100, 1500), [r.sample(range(100), 2) for _ in range(5000)])],
    },
    "find-eventual-safe-states": {
        "edge": [([[]],), ([[0]],), ([[1], [0]],), ([[1], []],), ([[], [0, 2], [1]],)],
        "large": [lambda r: _safe_graph(r, 8000), lambda r: ([[i + 1] for i in range(9999)] + [[]],)],
    },
    "longest-increasing-path-in-a-matrix": {
        "edge": [([[1]],), ([[1, 1], [1, 1]],), ([[1, 2], [4, 3]],), ([[7, 8, 9], [9, 7, 6], [7, 2, 3]],)],
        "large": [lambda r: ([r.ints(100, 0, 9999) for _ in range(100)],), lambda r: ([[i * 60 + (j if i % 2 == 0 else 59 - j) for j in range(60)] for i in range(60)],)],
    },
    "two-sum-less-than-k": {"edge": [([1], 2), ([1, 1], 2), ([1, 1], 3), ([1000, 1000], 2000), ([254, 914, 110, 900, 147, 441, 209, 122, 571, 942, 136, 350, 160, 127, 178, 839, 201, 386, 462, 45, 735, 467, 153, 415, 875, 282, 204, 534, 639, 994, 284, 320, 865, 468, 1, 838, 275, 370, 295, 574, 309, 268, 415, 385, 786, 62, 359, 78, 854, 944], 200)]},
    "valid-triangle-number": {
        "edge": [([1],), ([0, 0, 0],), ([1, 1, 1],), ([1, 1, 2],), ([0, 1, 1, 1],)],
        "large": [lambda r: (r.ints(1000, 0, 1000),)],
    },
    "minimum-absolute-difference": {
        "edge": [([1, 2],), ([-1000000, 1000000],), ([1, 3, 5],), ([40, 11, 26, 27, -20],)],
        "large": [lambda r: (r.distinct(10000, -10**6, 10**6),)],
    },
    "count-pairs-whose-sum-is-less-than-target": {"edge": [([1], 5), ([-50, -50], -50), ([50, 50], 50), ([-1, 1], 0)]},
    "find-target-indices-after-sorting-array": {"edge": [([1], 1), ([1], 2), ([5, 5, 5], 5), ([100, 1], 100)]},
    "sort-array-by-increasing-frequency": {"edge": [([1],), ([-100, 100],), ([2, 2, 1, 1],), ([5, 5, 5, 5],)]},
    "most-profit-assigning-work": {
        "edge": [([1], [1], [1]), ([5], [10], [1]), ([2, 2], [5, 9], [2]), ([13, 37, 58], [4, 90, 96], [34, 73, 45])],
        "large": [lambda r: (r.ints(7000, 1, 100000), r.ints(7000, 1, 100000), r.ints(7000, 1, 100000))],
    },
    "h-index": {
        "edge": [([0],), ([1000],), ([0, 0, 0],), ([1, 1, 1],), ([100, 100],)],
        "large": [lambda r: (r.ints(5000, 0, 1000),)],
    },
}
