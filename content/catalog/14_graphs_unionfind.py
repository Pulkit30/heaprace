import heapq
from collections import Counter, defaultdict, deque
from functools import lru_cache
from itertools import permutations

from catalog_lib import problem

G = "graphs"
AG = "advanced-graphs"
UF = "union-find"

DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def _bfs_grid(grid, starts, passable):
    m, n = len(grid), len(grid[0])
    dist = {s: 0 for s in starts}
    q = deque(starts)
    while q:
        i, j = q.popleft()
        for di, dj in DIRS:
            x, y = i + di, j + dj
            if 0 <= x < m and 0 <= y < n and (x, y) not in dist and passable(grid[x][y]):
                dist[x, y] = dist[i, j] + 1
                q.append((x, y))
    return dist


@problem(
    slug="rotting-oranges", title="Rotting Oranges", difficulty="Medium", pattern=G, tags=["Array", "Breadth-First Search", "Matrix"],
    sig="orangesRotting(self, grid: list[list[int]]) -> int",
    desc="""Each cell is empty (`0`), a fresh orange (`1`), or a rotten orange (`2`). Every minute, fresh oranges next to (4-directionally) a rotten orange become rotten. Return the minutes until no fresh orange remains, or `-1` if some never rot.""",
    constraints=["1 ≤ m, n ≤ 10"],
    samples=[([[2, 1, 1], [1, 1, 0], [0, 1, 1]],), ([[2, 1, 1], [0, 1, 1], [1, 0, 1]],), ([[0, 2]],)],
    gen=lambda r: ([[r.choice([0, 1, 1, 1, 2]) for _ in range(n)] for n in [r.randint(1, 5)] for _ in range(r.randint(1, 5))],),
    hints=[
        "All rotten oranges spread at the same time, so start from all of them at once.",
        "Multi-source BFS: put every rotten orange in the queue at minute 0.",
        "The answer is the largest BFS distance reached by a fresh orange; if any fresh orange is never reached, it's −1.",
    ],
    insight="Multi-source BFS measures time as distance from the nearest rotten orange.",
    time="O(m·n)", space="O(m·n)",
    pitfalls=["Running a separate BFS from each rotten orange."],
)
def oranges_rotting(grid):
    starts = [(i, j) for i, row in enumerate(grid) for j, v in enumerate(row) if v == 2]
    dist = _bfs_grid(grid, starts, lambda v: v == 1)
    fresh = [(i, j) for i, row in enumerate(grid) for j, v in enumerate(row) if v == 1]
    if any(f not in dist for f in fresh):
        return -1
    return max([dist[f] for f in fresh] or [0])


@problem(
    slug="01-matrix", title="01 Matrix", difficulty="Medium", pattern=G,
    tags=["Array", "Dynamic Programming", "Breadth-First Search", "Matrix"],
    sig="updateMatrix(self, mat: list[list[int]]) -> list[list[int]]",
    desc="""`mat` contains 0s and 1s, with at least one 0. Return a matrix where each cell holds the distance (in 4-directional steps) to the nearest `0`.""",
    constraints=["1 ≤ m, n ≤ 10⁴", "1 ≤ m·n ≤ 10⁴", "at least one 0"],
    samples=[([[0, 0, 0], [0, 1, 0], [0, 0, 0]],), ([[0, 0, 0], [0, 1, 0], [1, 1, 1]],)],
    gen=lambda r: (lambda g: (g if any(0 in row for row in g) else [[0] + row[1:] if i == 0 else row for i, row in enumerate(g)],))([[r.choice([0, 1, 1, 1]) for _ in range(n)] for n in [r.randint(1, 6)] for _ in range(r.randint(1, 6))]),
    brute=lambda mat: [[min(abs(i - x) + abs(j - y) for x, row in enumerate(mat) for y, v in enumerate(row) if v == 0) for j in range(len(mat[0]))] for i in range(len(mat))],
    hints=[
        "Running a BFS from every 1 is too slow.",
        "Reverse it: start from all 0s at once.",
        "Multi-source BFS from the zeros; each cell's distance is fixed the first time it's reached.",
    ],
    insight="Multi-source BFS from all zeros gives every distance in one pass.",
    time="O(m·n)", space="O(m·n)",
    pitfalls=["Starting a BFS per cell."],
)
def update_matrix(mat):
    starts = [(i, j) for i, row in enumerate(mat) for j, v in enumerate(row) if v == 0]
    dist = _bfs_grid(mat, starts, lambda v: True)
    return [[dist[i, j] for j in range(len(mat[0]))] for i in range(len(mat))]


def _reach_ocean(h, starts):
    m, n = len(h), len(h[0])
    seen, st = set(starts), list(starts)
    while st:
        i, j = st.pop()
        for di, dj in DIRS:
            x, y = i + di, j + dj
            if 0 <= x < m and 0 <= y < n and (x, y) not in seen and h[x][y] >= h[i][j]:
                seen.add((x, y))
                st.append((x, y))
    return seen


@problem(
    slug="pacific-atlantic-water-flow", title="Pacific Atlantic Water Flow", difficulty="Medium", pattern=G,
    tags=["Array", "Depth-First Search", "Breadth-First Search", "Matrix"],
    sig="pacificAtlantic(self, heights: list[list[int]]) -> list[list[int]]", compare="unordered",
    desc="""An island's cell heights are given. The Pacific touches the top and left edges; the Atlantic touches the bottom and right edges. Rain flows from a cell to a neighbor (4-directionally) with height **less than or equal** to its own, and from edge cells into the adjacent ocean.

Return every cell `[r, c]` from which water can reach **both** oceans, in any order.""",
    constraints=["1 ≤ m, n ≤ 200", "0 ≤ heights[i][j] ≤ 10⁵"],
    samples=[([[1, 2, 2, 3, 5], [3, 2, 3, 4, 4], [2, 4, 5, 3, 1], [6, 7, 1, 4, 5], [5, 1, 1, 2, 4]],), ([[1]],)],
    gen=lambda r: ([r.ints(n, 0, 5) for n in [r.randint(1, 5)] for _ in range(r.randint(1, 5))],),
    hints=[
        "Simulating rain from every cell repeats a lot of work.",
        "Work backwards: from each ocean's edge cells, climb to neighbors that are at least as high.",
        "Do one search per ocean; the answer is the cells reached by both.",
    ],
    insight="Reverse flow from the oceans: two searches instead of one per cell.",
    time="O(m·n)", space="O(m·n)",
    pitfalls=["Flowing downhill from each cell separately."],
)
def pacific_atlantic(heights):
    m, n = len(heights), len(heights[0])
    pac = _reach_ocean(heights, [(0, j) for j in range(n)] + [(i, 0) for i in range(m)])
    atl = _reach_ocean(heights, [(m - 1, j) for j in range(n)] + [(i, n - 1) for i in range(m)])
    return [[i, j] for i in range(m) for j in range(n) if (i, j) in pac and (i, j) in atl]


@problem(
    slug="surrounded-regions", title="Surrounded Regions", difficulty="Medium", pattern=G,
    tags=["Array", "Depth-First Search", "Breadth-First Search", "Union Find", "Matrix"],
    sig="solve(self, board: list[list[str]]) -> None", out_arg=0,
    desc="""`board` contains `'X'` and `'O'`. Capture every region of `'O'`s that is completely surrounded by `'X'`s (not connected 4-directionally to the border) by flipping it to `'X'`. Modify `board` in place; the judge checks it.""",
    constraints=["1 ≤ m, n ≤ 200"],
    samples=[([["X", "X", "X", "X"], ["X", "O", "O", "X"], ["X", "X", "O", "X"], ["X", "O", "X", "X"]],), ([["X"]],)],
    gen=lambda r: ([[r.choice("XXO") for _ in range(n)] for n in [r.randint(1, 6)] for _ in range(r.randint(1, 6))],),
    hints=[
        "It's easier to find the 'O's that survive than the ones that get captured.",
        "Any 'O' connected to a border 'O' survives.",
        "Mark everything reachable from border 'O's, then flip every unmarked 'O' to 'X'.",
    ],
    insight="Search from the border to find safe cells; everything else is captured.",
    time="O(m·n)", space="O(m·n)",
    pitfalls=["Flipping cells during the search before knowing if the region touches the border."],
)
def solve_surrounded(board):
    m, n = len(board), len(board[0])
    border = [(i, j) for i in range(m) for j in range(n) if (i in (0, m - 1) or j in (0, n - 1)) and board[i][j] == "O"]
    safe = _bfs_grid(board, border, lambda v: v == "O")
    for i in range(m):
        for j in range(n):
            if board[i][j] == "O" and (i, j) not in safe:
                board[i][j] = "X"


@problem(
    slug="island-perimeter", title="Island Perimeter", difficulty="Easy", pattern=G, tags=["Array", "Depth-First Search", "Matrix"],
    sig="islandPerimeter(self, grid: list[list[int]]) -> int",
    desc="""`grid` has land (`1`) and water (`0`). There is exactly one island (land cells connected 4-directionally) and it has no lakes inside. Return the island's perimeter.""",
    constraints=["1 ≤ m, n ≤ 100", "exactly one island"],
    samples=[([[0, 1, 0, 0], [1, 1, 1, 0], [0, 1, 0, 0], [1, 1, 0, 0]],), ([[1]],), ([[1, 0]],)],
    gen=lambda r: (lambda m, n: (lambda cells: ([[1 if (i, j) in cells else 0 for j in range(n)] for i in range(m)],))(_grow_island(r, m, n)))(r.randint(1, 5), r.randint(1, 5)),
    hints=[
        "Each land cell contributes 4 edges.",
        "Every shared edge between two land cells removes 2 from the total.",
        "Count land cells and land-to-land neighbors (only look right and down to count each once).",
    ],
    insight="Perimeter = 4 × land − 2 × shared edges.",
    time="O(m·n)", space="O(1)",
    pitfalls=["Counting each shared edge twice."],
)
def island_perimeter(grid):
    land = shared = 0
    for i, row in enumerate(grid):
        for j, v in enumerate(row):
            if v:
                land += 1
                if i + 1 < len(grid) and grid[i + 1][j]:
                    shared += 1
                if j + 1 < len(row) and row[j + 1]:
                    shared += 1
    return 4 * land - 2 * shared


def _grow_island(r, m, n):
    cells = {(r.randint(0, m - 1), r.randint(0, n - 1))}
    for _ in range(r.randint(0, m * n)):
        i, j = r.choice(sorted(cells))
        di, dj = r.choice(DIRS)
        if 0 <= i + di < m and 0 <= j + dj < n:
            cells.add((i + di, j + dj))
    return cells


@problem(
    slug="max-area-of-island", title="Max Area of Island", difficulty="Medium", pattern=G,
    tags=["Array", "Depth-First Search", "Breadth-First Search", "Union Find", "Matrix"],
    sig="maxAreaOfIsland(self, grid: list[list[int]]) -> int",
    desc="""An island is a group of `1`s connected 4-directionally. Return the area (number of cells) of the largest island, or `0` if there is none.""",
    constraints=["1 ≤ m, n ≤ 50"],
    samples=[([[0, 0, 1, 0, 0], [0, 1, 1, 0, 0], [0, 0, 0, 1, 1], [0, 0, 0, 1, 0]],), ([[0, 0, 0, 0]],)],
    gen=lambda r: ([[r.choice([0, 1]) for _ in range(n)] for n in [r.randint(1, 6)] for _ in range(r.randint(1, 6))],),
    hints=[
        "Each unvisited land cell starts a new island.",
        "Flood-fill from it, counting cells and marking them visited.",
        "Keep the largest count across all islands.",
    ],
    insight="Flood fill each island once and measure it.",
    time="O(m·n)", space="O(m·n)",
    pitfalls=["Counting a cell twice by not marking it visited when it's first reached."],
)
def max_area_of_island(grid):
    seen, best = set(), 0
    for i, row in enumerate(grid):
        for j, v in enumerate(row):
            if v and (i, j) not in seen:
                comp = _bfs_grid(grid, [(i, j)], lambda x: x == 1)
                seen |= set(comp)
                best = max(best, len(comp))
    return best


@problem(
    slug="shortest-path-in-binary-matrix", title="Shortest Path in Binary Matrix", difficulty="Medium", pattern=G,
    tags=["Array", "Breadth-First Search", "Matrix"],
    sig="shortestPathBinaryMatrix(self, grid: list[list[int]]) -> int",
    desc="""In an `n × n` grid of 0s (open) and 1s (blocked), return the number of cells on the shortest path from the top-left to the bottom-right cell moving in any of the **8 directions** through open cells. Return `-1` if there is no such path.""",
    constraints=["1 ≤ n ≤ 100"],
    samples=[([[0, 1], [1, 0]],), ([[0, 0, 0], [1, 1, 0], [1, 1, 0]],), ([[1, 0, 0], [1, 1, 0], [1, 1, 0]],)],
    gen=lambda r: (lambda n: ([[r.choice([0, 0, 0, 1]) for _ in range(n)] for _ in range(n)],))(r.randint(1, 6)),
    hints=[
        "Every step costs the same, so BFS finds the shortest path.",
        "Allow all 8 neighbors.",
        "If the start or the end is blocked, the answer is −1. Count cells, so the start alone has length 1.",
    ],
    insight="BFS on an unweighted 8-connected grid.",
    time="O(n²)", space="O(n²)",
    pitfalls=["Counting edges instead of cells."],
)
def shortest_path_binary(grid):
    n = len(grid)
    if grid[0][0] or grid[-1][-1]:
        return -1
    dist = {(0, 0): 1}
    q = deque([(0, 0)])
    while q:
        i, j = q.popleft()
        if (i, j) == (n - 1, n - 1):
            return dist[i, j]
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                x, y = i + di, j + dj
                if 0 <= x < n and 0 <= y < n and not grid[x][y] and (x, y) not in dist:
                    dist[x, y] = dist[i, j] + 1
                    q.append((x, y))
    return -1


def _ladder_input(r):
    words = sorted({r.word(3, "abc") for _ in range(r.randint(2, 12))})
    return r.word(3, "abc"), r.choice(words), words


@problem(
    slug="word-ladder", title="Word Ladder", difficulty="Hard", pattern=G, tags=["Hash Table", "String", "Breadth-First Search"],
    sig="ladderLength(self, beginWord: str, endWord: str, wordList: list[str]) -> int",
    desc="""A transformation sequence goes from `beginWord` to `endWord`, changing one letter at a time; every intermediate word (and `endWord`) must be in `wordList`. Return the number of words in the shortest sequence (including both ends), or `0` if none exists.""",
    constraints=["1 ≤ len(beginWord) ≤ 10", "all words have the same length", "1 ≤ len(wordList) ≤ 5000"],
    samples=[("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]), ("hit", "cog", ["hot", "dot", "dog", "lot", "log"])],
    gen=_ladder_input,
    hints=[
        "Words are nodes; two words are connected if they differ in exactly one letter.",
        "The shortest sequence is a BFS from beginWord.",
        "Generate neighbors by trying every letter at every position and checking the word set; remove words once visited.",
    ],
    insight="BFS over an implicit graph of one-letter edits.",
    time="O(N · L · 26)", space="O(N · L)",
    pitfalls=["Comparing every pair of words to build the graph (O(N²·L))."],
)
def ladder_length(beginWord, endWord, wordList):
    words = set(wordList)
    if endWord not in words:
        return 0
    if beginWord == endWord:
        return 1
    q, seen = deque([(beginWord, 1)]), {beginWord}
    while q:
        w, d = q.popleft()
        for i in range(len(w)):
            for c in "abcdefghijklmnopqrstuvwxyz":
                nw = w[:i] + c + w[i + 1:]
                if nw in words and nw not in seen:
                    if nw == endWord:
                        return d + 1
                    seen.add(nw)
                    q.append((nw, d + 1))
    return 0


@problem(
    slug="open-the-lock", title="Open the Lock", difficulty="Medium", pattern=G, tags=["Array", "Hash Table", "String", "Breadth-First Search"],
    sig="openLock(self, deadends: list[str], target: str) -> int",
    desc="""A lock has four wheels, each showing a digit 0–9; it starts at `"0000"`. One move turns one wheel one step up or down (9 wraps to 0 and back). Reaching any code in `deadends` locks it forever. Return the minimum number of moves to reach `target`, or `-1` if impossible.""",
    constraints=["1 ≤ len(deadends) ≤ 500", "codes are 4 digits"],
    samples=[(["0201", "0101", "0102", "1212", "2002"], "0202"), (["8888"], "0009"), (["0000"], "8888")],
    gen=lambda r: (sorted({"".join(r.choice("0129") for _ in range(4)) for _ in range(r.randint(1, 8))}), "".join(r.choice("0129") for _ in range(4))),
    hints=[
        "Each code has 8 neighbors (4 wheels × 2 directions).",
        "BFS from \"0000\" gives the fewest moves.",
        "Treat deadends as already visited; if \"0000\" itself is a deadend, it's impossible.",
    ],
    insight="BFS over the 10⁴ lock states.",
    time="O(10⁴ · 8)", space="O(10⁴)",
    pitfalls=["Forgetting the wrap-around between 0 and 9."],
)
def open_lock(deadends, target):
    dead = set(deadends)
    if "0000" in dead:
        return -1
    q, dist = deque(["0000"]), {"0000": 0}
    while q:
        s = q.popleft()
        if s == target:
            return dist[s]
        for i in range(4):
            for d in (1, -1):
                t = s[:i] + str((int(s[i]) + d) % 10) + s[i + 1:]
                if t not in dist and t not in dead:
                    dist[t] = dist[s] + 1
                    q.append(t)
    return -1


@problem(
    slug="keys-and-rooms", title="Keys and Rooms", difficulty="Medium", pattern=G, tags=["Depth-First Search", "Breadth-First Search", "Graph"],
    sig="canVisitAllRooms(self, rooms: list[list[int]]) -> bool",
    desc="""Rooms are numbered `0..n − 1`; only room 0 is unlocked. Room `i` contains the keys listed in `rooms[i]`. Return `true` if you can visit every room.""",
    constraints=["2 ≤ n ≤ 1000", "0 ≤ keys < n"],
    samples=[([[1], [2], [3], []],), ([[1, 3], [3, 0, 1], [2], [0]],)],
    gen=lambda r: (lambda n: ([r.distinct(r.randint(0, 2), 0, n - 1) for _ in range(n)],))(r.randint(2, 7)),
    hints=[
        "Keys are edges from a room to other rooms.",
        "Explore from room 0 with DFS or BFS.",
        "Check whether the number of visited rooms equals n.",
    ],
    insight="Reachability from room 0 in a directed graph.",
    time="O(n + keys)", space="O(n)",
    pitfalls=["Revisiting rooms in a loop."],
)
def can_visit_all_rooms(rooms):
    seen, st = {0}, [0]
    while st:
        for k in rooms[st.pop()]:
            if k not in seen:
                seen.add(k)
                st.append(k)
    return len(seen) == len(rooms)


def _dag_adj(r):
    n = r.randint(2, 6)
    return ([sorted(r.distinct(r.randint(0, n - 1 - i), i + 1, n - 1)) if i < n - 1 else [] for i in range(n)],)


@problem(
    slug="all-paths-from-source-to-target", title="All Paths From Source to Target", difficulty="Medium", pattern=G,
    tags=["Backtracking", "Depth-First Search", "Breadth-First Search", "Graph"],
    sig="allPathsSourceTarget(self, graph: list[list[int]]) -> list[list[int]]", compare="unordered",
    desc="""`graph` is a directed acyclic graph with nodes `0..n − 1`; `graph[i]` lists the nodes reachable from `i` by one edge. Return every path from node `0` to node `n − 1`, in any order.""",
    constraints=["2 ≤ n ≤ 15", "the graph is acyclic"],
    samples=[([[1, 2], [3], [3], []],), ([[4, 3, 1], [3, 2, 4], [3], [4], []],)],
    gen=_dag_adj,
    hints=[
        "No cycles means no visited set is needed.",
        "DFS from node 0, keeping the current path.",
        "When you reach n − 1, record a copy of the path; then backtrack.",
    ],
    insight="Backtracking DFS enumerates paths in a DAG.",
    time="O(2ⁿ · n)", space="O(n)",
    pitfalls=["Saving a reference to the path list instead of a copy."],
)
def all_paths(graph):
    out, path = [], [0]

    def go(u):
        if u == len(graph) - 1:
            out.append(path[:])
            return
        for v in graph[u]:
            path.append(v)
            go(v)
            path.pop()

    go(0)
    return out


@problem(
    slug="find-center-of-star-graph", title="Find Center of Star Graph", difficulty="Easy", pattern=G, tags=["Graph"],
    sig="findCenter(self, edges: list[list[int]]) -> int",
    desc="""An undirected **star** graph has one center node connected to every other node (and no other edges). Given its edges, return the center.""",
    constraints=["3 ≤ n ≤ 10⁵", "edges form a valid star"],
    samples=[([[1, 2], [2, 3], [4, 2]],), ([[1, 2], [5, 1], [1, 3], [1, 4]],)],
    gen=lambda r: (lambda n, c: ([[c, v] if r.random() < 0.5 else [v, c] for v in r.sample([x for x in range(1, n + 1) if x != c], n - 1)],))(*(lambda n: (n, r.randint(1, n)))(r.randint(3, 8))),
    hints=[
        "The center appears in every edge.",
        "So it must be in both of the first two edges.",
        "Return the node shared by edges[0] and edges[1].",
    ],
    insight="Two edges are enough to identify the center.",
    time="O(1)", space="O(1)",
    pitfalls=["Building the whole degree table when two edges suffice."],
)
def find_center(edges):
    a, b = edges[0]
    return a if a in edges[1] else b


def _dijkstra(n, adj, src):
    dist = [float("inf")] * n
    dist[src] = 0
    pq = [(0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(pq, (dist[v], v))
    return dist


def _edges_input(r, directed=True, wmax=9):
    n = r.randint(2, 6)
    edges = set()
    for _ in range(r.randint(1, n * 2)):
        a, b = r.sample(range(n), 2)
        if not directed:
            a, b = min(a, b), max(a, b)
        edges.add((a, b))
    return n, [[a, b, r.randint(1, wmax)] for a, b in sorted(edges)]


def _cheapest_brute(n, flights, src, dst, k):
    best = float("inf")
    adj = defaultdict(list)
    for a, b, w in flights:
        adj[a].append((b, w))

    def go(u, cost, flights, seen):
        nonlocal best
        if u == dst:
            best = min(best, cost)
            return
        if flights == k + 1:
            return
        for v, w in adj[u]:
            if v not in seen:
                go(v, cost + w, flights + 1, seen | {v})

    go(src, 0, 0, {src})
    return best if best < float("inf") else -1


@problem(
    slug="cheapest-flights-within-k-stops", title="Cheapest Flights Within K Stops", difficulty="Medium", pattern=AG,
    tags=["Dynamic Programming", "Depth-First Search", "Breadth-First Search", "Graph", "Heap", "Shortest Path"],
    sig="findCheapestPrice(self, n: int, flights: list[list[int]], src: int, dst: int, k: int) -> int",
    desc="""`flights[i] = [from, to, price]` is a one-way flight. Return the cheapest price from `src` to `dst` using **at most `k` stops** (intermediate cities), or `-1` if there is no such route.""",
    constraints=["1 ≤ n ≤ 100", "prices are positive", "no duplicate flights", "0 ≤ k < n"],
    samples=[(4, [[0, 1, 100], [1, 2, 100], [2, 0, 100], [1, 3, 600], [2, 3, 200]], 0, 3, 1), (3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 1),
             (3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 0)],
    gen=lambda r: (lambda n, e: (n, e, *r.sample(range(n), 2), r.randint(0, n - 1)))(*_edges_input(r)),
    brute=_cheapest_brute,
    hints=[
        "Plain Dijkstra ignores the stop limit; a cheaper path may use too many stops.",
        "At most k stops means at most k + 1 flights.",
        "Run Bellman–Ford for k + 1 rounds, relaxing every flight from a copy of the previous round's prices.",
    ],
    insight="Bounded Bellman–Ford: round i holds the cheapest prices using at most i flights.",
    time="O(k · E)", space="O(n)",
    pitfalls=["Relaxing from the current round's array, which lets one round use several flights."],
)
def find_cheapest_price(n, flights, src, dst, k):
    inf = float("inf")
    dist = [inf] * n
    dist[src] = 0
    for _ in range(k + 1):
        prev = dist[:]
        for a, b, w in flights:
            if prev[a] + w < dist[b]:
                dist[b] = prev[a] + w
    return dist[dst] if dist[dst] < inf else -1


def _prob_input(r):
    n, e = _edges_input(r, directed=False)
    return n, [[a, b] for a, b, _ in e], [round(r.randint(1, 10) / 10, 1) for _ in e], *r.sample(range(n), 2)


def _prob_brute(n, edges, probs, start, end):
    adj = defaultdict(list)
    for (a, b), p in zip(edges, probs):
        adj[a].append((b, p))
        adj[b].append((a, p))
    best = 0.0

    def go(u, p, seen):
        nonlocal best
        if u == end:
            best = max(best, p)
            return
        for v, q in adj[u]:
            if v not in seen:
                go(v, p * q, seen | {v})

    go(start, 1.0, {start})
    return best


@problem(
    slug="path-with-maximum-probability", title="Path with Maximum Probability", difficulty="Medium", pattern=AG,
    tags=["Array", "Graph", "Heap", "Shortest Path"],
    sig="maxProbability(self, n: int, edges: list[list[int]], succProb: list[float], start_node: int, end_node: int) -> float", compare="approx",
    desc="""An undirected graph has `n` nodes; edge `edges[i]` succeeds with probability `succProb[i]`. Return the maximum probability of successfully going from `start_node` to `end_node` (the product of the edge probabilities along a path), or `0` if there is no path. Answers within 10⁻⁵ are accepted.""",
    constraints=["2 ≤ n ≤ 10⁴", "0 ≤ succProb[i] ≤ 1", "no duplicate edges"],
    samples=[(3, [[0, 1], [1, 2], [0, 2]], [0.5, 0.5, 0.2], 0, 2), (3, [[0, 1], [1, 2], [0, 2]], [0.5, 0.5, 0.3], 0, 2), (3, [[0, 1]], [0.5], 0, 2)],
    gen=_prob_input,
    brute=_prob_brute,
    hints=[
        "Multiplying probabilities never increases them, just like adding positive weights never decreases a distance.",
        "So a Dijkstra-style greedy works if you always expand the most probable node first.",
        "Use a max-heap keyed by probability; relax neighbors with prob × edge probability.",
    ],
    insight="Dijkstra with max-product instead of min-sum.",
    time="O(E log V)", space="O(V + E)",
    pitfalls=["Using BFS by edge count, which ignores probabilities."],
)
def max_probability(n, edges, succProb, start_node, end_node):
    adj = defaultdict(list)
    for (a, b), p in zip(edges, succProb):
        adj[a].append((b, p))
        adj[b].append((a, p))
    best = [0.0] * n
    best[start_node] = 1.0
    pq = [(-1.0, start_node)]
    while pq:
        p, u = heapq.heappop(pq)
        p = -p
        if u == end_node:
            return p
        if p < best[u]:
            continue
        for v, q in adj[u]:
            if p * q > best[v]:
                best[v] = p * q
                heapq.heappush(pq, (-best[v], v))
    return 0.0


@problem(
    slug="swim-in-rising-water", title="Swim in Rising Water", difficulty="Hard", pattern=AG,
    tags=["Array", "Binary Search", "Depth-First Search", "Breadth-First Search", "Union Find", "Heap", "Matrix"],
    sig="swimInWater(self, grid: list[list[int]]) -> int",
    desc="""`grid` is `n × n` and holds a permutation of `0..n² − 1` (cell elevations). At time `t` the water depth everywhere is `t`, and you can swim between 4-directionally adjacent cells if both elevations are at most `t` (swimming takes no time). Return the least time to get from the top-left to the bottom-right cell.""",
    constraints=["1 ≤ n ≤ 50", "values are a permutation of 0..n² − 1"],
    samples=[([[0, 2], [1, 3]],), ([[0, 1, 2, 3, 4], [24, 23, 22, 21, 5], [12, 13, 14, 15, 16], [11, 17, 18, 19, 20], [10, 9, 8, 7, 6]],)],
    gen=lambda r: (lambda n: (lambda vals: ([vals[i * n:(i + 1) * n] for i in range(n)],))(r.sample(range(n * n), n * n)))(r.randint(1, 5)),
    brute=lambda grid: next(t for t in range(len(grid) ** 2) if grid[0][0] <= t and (len(grid) - 1, len(grid) - 1) in _bfs_grid(grid, [(0, 0)], lambda v: v <= t)),
    hints=[
        "The time needed for a path is the highest elevation on it.",
        "So you want the path that minimizes its maximum cell.",
        "Use Dijkstra with a min-heap keyed by the path's maximum so far (or binary search t with a reachability check).",
    ],
    insight="A minimax path problem: Dijkstra where the cost is the max, not the sum.",
    time="O(n² log n)", space="O(n²)",
    pitfalls=["Summing elevations instead of taking the maximum."],
)
def swim_in_water(grid):
    n = len(grid)
    pq, seen = [(grid[0][0], 0, 0)], {(0, 0)}
    while pq:
        t, i, j = heapq.heappop(pq)
        if (i, j) == (n - 1, n - 1):
            return t
        for di, dj in DIRS:
            x, y = i + di, j + dj
            if 0 <= x < n and 0 <= y < n and (x, y) not in seen:
                seen.add((x, y))
                heapq.heappush(pq, (max(t, grid[x][y]), x, y))


def _mst_brute(points):
    n = len(points)
    edges = sorted((abs(a[0] - b[0]) + abs(a[1] - b[1]), i, j) for i, a in enumerate(points) for j, b in enumerate(points) if i < j)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x

    total = 0
    for w, i, j in edges:
        a, b = find(i), find(j)
        if a != b:
            parent[a] = b
            total += w
    return total


@problem(
    slug="min-cost-to-connect-all-points", title="Min Cost to Connect All Points", difficulty="Medium", pattern=AG,
    tags=["Array", "Union Find", "Graph", "Minimum Spanning Tree"],
    sig="minCostConnectPoints(self, points: list[list[int]]) -> int",
    desc="""Connecting points `a` and `b` costs their Manhattan distance `|xa − xb| + |ya − yb|`. Return the minimum cost to connect all points so that there is exactly one path between any two.""",
    constraints=["1 ≤ n ≤ 1000", "points are distinct", "-10⁶ ≤ coordinates ≤ 10⁶"],
    samples=[([[0, 0], [2, 2], [3, 10], [5, 2], [7, 0]],), ([[3, 12], [-2, 5], [-4, 1]],)],
    gen=lambda r: ([list(p) for p in {(r.randint(-10, 10), r.randint(-10, 10)) for _ in range(r.randint(1, 7))}],),
    brute=_mst_brute,
    hints=[
        "\"Exactly one path between any two points\" describes a spanning tree.",
        "You want the minimum spanning tree of the complete graph on the points.",
        "Prim's algorithm with an O(n²) array of best distances avoids building all n² edges in a heap.",
    ],
    insight="A minimum spanning tree over Manhattan distances.",
    time="O(n²)", space="O(n)",
    pitfalls=["Sorting all n² edges, which is heavier than needed."],
)
def min_cost_connect(points):
    n = len(points)
    inf = float("inf")
    best, used, total = [inf] * n, [False] * n, 0
    best[0] = 0
    for _ in range(n):
        u = min((i for i in range(n) if not used[i]), key=lambda i: best[i])
        used[u] = True
        total += best[u]
        for v in range(n):
            if not used[v]:
                d = abs(points[u][0] - points[v][0]) + abs(points[u][1] - points[v][1])
                if d < best[v]:
                    best[v] = d
    return total


def _itinerary_input(r):
    airports = ["JFK", "ATL", "SFO", "LAX"]
    route = ["JFK"] + [r.choice(airports) for _ in range(r.randint(1, 5))]
    route = [a for i, a in enumerate(route) if i == 0 or a != route[i - 1]]
    if len(route) < 2:
        route.append("ATL")
    tickets = [[a, b] for a, b in zip(route, route[1:])]
    r.shuffle(tickets)
    return (tickets,)


def _itinerary_brute(tickets):
    n = len(tickets)
    best = None
    for order in permutations(range(n)):
        path = ["JFK"]
        ok = True
        for i in order:
            if tickets[i][0] != path[-1]:
                ok = False
                break
            path.append(tickets[i][1])
        if ok and (best is None or path < best):
            best = path
    return best


@problem(
    slug="reconstruct-itinerary", title="Reconstruct Itinerary", difficulty="Hard", pattern=AG, tags=["Depth-First Search", "Graph", "Eulerian Circuit"],
    sig="findItinerary(self, tickets: list[list[str]]) -> list[str]",
    desc="""Each ticket `[from, to]` is a flight. Starting at `"JFK"`, use every ticket exactly once. If several itineraries are possible, return the lexicographically smallest one (as a list of airports). At least one valid itinerary exists.""",
    constraints=["1 ≤ len(tickets) ≤ 300", "airport codes are 3 uppercase letters"],
    samples=[([["MUC", "LHR"], ["JFK", "MUC"], ["SFO", "SJC"], ["LHR", "SFO"]],), ([["JFK", "SFO"], ["JFK", "ATL"], ["SFO", "ATL"], ["ATL", "JFK"], ["ATL", "SFO"]],)],
    gen=_itinerary_input,
    brute=_itinerary_brute,
    hints=[
        "Using every edge exactly once is an Eulerian path.",
        "Greedily taking the smallest destination can strand you; you need a way to recover.",
        "Hierholzer's algorithm: DFS taking destinations in sorted order, append an airport after its edges are exhausted, then reverse the result.",
    ],
    insight="Hierholzer's post-order DFS builds the Eulerian path, with sorting for the smallest order.",
    time="O(E log E)", space="O(E)",
    pitfalls=["Stopping at a dead end without backtracking."],
)
def find_itinerary(tickets):
    adj = defaultdict(list)
    for a, b in sorted(tickets, reverse=True):
        adj[a].append(b)
    route, st = [], ["JFK"]
    while st:
        while adj[st[-1]]:
            st.append(adj[st[-1]].pop())
        route.append(st.pop())
    return route[::-1]


def _bus_brute(routes, source, target):
    if source == target:
        return 0
    stops = {s: {i for i, r in enumerate(routes) if s in r} for r in routes for s in r}
    q, seen = deque([(i, 1) for i in stops.get(source, ())]), set(stops.get(source, ()))
    while q:
        i, d = q.popleft()
        if target in routes[i]:
            return d
        for s in routes[i]:
            for j in stops[s]:
                if j not in seen:
                    seen.add(j)
                    q.append((j, d + 1))
    return -1


@problem(
    slug="bus-routes", title="Bus Routes", difficulty="Hard", pattern=G, tags=["Array", "Hash Table", "Breadth-First Search"],
    sig="numBusesToDestination(self, routes: list[list[int]], source: int, target: int) -> int",
    desc="""`routes[i]` lists the stops that bus `i` loops through forever. Starting at stop `source` (not on any bus yet), return the fewest buses you must take to reach stop `target`, or `-1` if impossible.""",
    constraints=["1 ≤ len(routes) ≤ 500", "stops within a route are distinct", "0 ≤ stop ≤ 10⁶"],
    samples=[([[1, 2, 7], [3, 6, 7]], 1, 6), ([[7, 12], [4, 5, 15], [6], [15, 19], [9, 12, 13]], 15, 12)],
    gen=lambda r: ([r.distinct(r.randint(1, 4), 0, 9) for _ in range(r.randint(1, 5))], r.randint(0, 9), r.randint(0, 9)),
    brute=_bus_brute,
    hints=[
        "You're counting buses, not stops, so make buses the nodes.",
        "Two buses connect if they share a stop. Map each stop to the buses that visit it.",
        "BFS starting from all buses through source; the answer is the level of the first bus that visits target. Source == target needs 0 buses.",
    ],
    insight="BFS over buses (connected through shared stops).",
    time="O(total stops)", space="O(total stops)",
    pitfalls=["BFS over stops, which counts stops instead of buses."],
)
def num_buses(routes, source, target):
    if source == target:
        return 0
    by_stop = defaultdict(list)
    for i, rt in enumerate(routes):
        for s in rt:
            by_stop[s].append(i)
    seen_bus, seen_stop = set(by_stop[source]), {source}
    q = deque((i, 1) for i in by_stop[source])
    while q:
        i, d = q.popleft()
        for s in routes[i]:
            if s == target:
                return d
            if s in seen_stop:
                continue
            seen_stop.add(s)
            for j in by_stop[s]:
                if j not in seen_bus:
                    seen_bus.add(j)
                    q.append((j, d + 1))
    return -1


# ---------------------------------------------------------------- union find


class _DSU:
    def __init__(self, n):
        self.p = list(range(n))
        self.count = n

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a == b:
            return False
        self.p[a] = b
        self.count -= 1
        return True


def _adj_matrix(r):
    n = r.randint(1, 7)
    m = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    for _ in range(r.randint(0, n)):
        a, b = r.randint(0, n - 1), r.randint(0, n - 1)
        m[a][b] = m[b][a] = 1
    return (m,)


@problem(
    slug="number-of-provinces", title="Number of Provinces", difficulty="Medium", pattern=UF,
    tags=["Depth-First Search", "Breadth-First Search", "Union Find", "Graph"],
    sig="findCircleNum(self, isConnected: list[list[int]]) -> int",
    desc="""`isConnected[i][j] = 1` means cities `i` and `j` are directly connected (the matrix is symmetric with 1s on the diagonal). A province is a group of cities connected directly or indirectly. Return the number of provinces.""",
    constraints=["1 ≤ n ≤ 200"],
    samples=[([[1, 1, 0], [1, 1, 0], [0, 0, 1]],), ([[1, 0, 0], [0, 1, 0], [0, 0, 1]],)],
    gen=_adj_matrix,
    brute=lambda M: len({frozenset(_component(M, i)) for i in range(len(M))}),
    hints=[
        "Provinces are connected components.",
        "Start with every city in its own group and merge groups for each connection.",
        "With union–find, each successful union reduces the count by one.",
    ],
    insight="Count connected components with union–find (or DFS).",
    time="O(n² α(n))", space="O(n)",
    pitfalls=["Counting connections instead of components."],
)
def find_circle_num(isConnected):
    n = len(isConnected)
    d = _DSU(n)
    for i in range(n):
        for j in range(i + 1, n):
            if isConnected[i][j]:
                d.union(i, j)
    return d.count


def _component(M, s):
    seen, st = {s}, [s]
    while st:
        u = st.pop()
        for v, c in enumerate(M[u]):
            if c and v not in seen:
                seen.add(v)
                st.append(v)
    return seen


def _accounts_input(r):
    # Each email belongs to one fixed person, so accounts sharing an email always share a name.
    people = {"Ann": ["ann%d@x.com" % i for i in range(4)], "Bob": ["bob%d@x.com" % i for i in range(4)]}
    accounts = []
    for _ in range(r.randint(1, 5)):
        name = r.choice(sorted(people))
        accounts.append([name] + r.sample(people[name], r.randint(1, 3)))
    return (accounts,)


def _accounts_brute(accounts):
    groups = [set(a[1:]) for a in accounts]
    names = [a[0] for a in accounts]
    merged = True
    while merged:
        merged = False
        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                if groups[i] & groups[j]:
                    groups[i] |= groups.pop(j)
                    names.pop(j)
                    merged = True
                    break
            if merged:
                break
    return [[n] + sorted(g) for n, g in zip(names, groups)]


@problem(
    slug="accounts-merge", title="Accounts Merge", difficulty="Medium", pattern=UF,
    tags=["Array", "Hash Table", "String", "Depth-First Search", "Breadth-First Search", "Union Find", "Sorting"],
    sig="accountsMerge(self, accounts: list[list[str]]) -> list[list[str]]", compare="unordered",
    desc="""Each account is `[name, email1, email2, …]`. Two accounts belong to the same person if they share any email (people with the same name may still be different people). Merge accounts and return them as `[name, emails in sorted order…]`; the accounts themselves may be in any order.""",
    constraints=["1 ≤ len(accounts) ≤ 1000", "2 ≤ len(accounts[i]) ≤ 10"],
    samples=[([["John", "johnsmith@mail.com", "john_newyork@mail.com"], ["John", "johnsmith@mail.com", "john00@mail.com"], ["Mary", "mary@mail.com"], ["John", "johnnybravo@mail.com"]],),
             ([["Gabe", "Gabe0@m.co", "Gabe3@m.co", "Gabe1@m.co"], ["Kevin", "Kevin3@m.co", "Kevin5@m.co", "Kevin0@m.co"]],)],
    gen=_accounts_input,
    brute=_accounts_brute,
    hints=[
        "Emails are the real identity; an account links all of its emails together.",
        "Union each account's emails with its first email.",
        "Group emails by their root, sort each group, and attach the name of any account in that group.",
    ],
    insight="Union–find over emails merges accounts transitively.",
    time="O(E log E)", space="O(E)",
    pitfalls=["Merging accounts by name."],
)
def accounts_merge(accounts):
    idx, name = {}, {}
    for acc in accounts:
        for e in acc[1:]:
            if e not in idx:
                idx[e] = len(idx)
            name[e] = acc[0]
    d = _DSU(len(idx))
    for acc in accounts:
        for e in acc[2:]:
            d.union(idx[acc[1]], idx[e])
    groups = defaultdict(list)
    for e, i in idx.items():
        groups[d.find(i)].append(e)
    return [[name[g[0]]] + sorted(g) for g in groups.values()]


@problem(
    slug="longest-consecutive-sequence", title="Longest Consecutive Sequence", difficulty="Medium", pattern=UF,
    tags=["Array", "Hash Table", "Union Find"],
    sig="longestConsecutive(self, nums: list[int]) -> int",
    desc="""Return the length of the longest run of consecutive integers (like 4, 5, 6, 7) whose values all appear in the unsorted array `nums`. Aim for O(n).""",
    constraints=["0 ≤ len(nums) ≤ 10⁵", "-10⁹ ≤ nums[i] ≤ 10⁹"],
    samples=[([100, 4, 200, 1, 3, 2],), ([0, 3, 7, 2, 5, 8, 4, 6, 0, 1],), ([],)],
    gen=lambda r: (r.ints(r.randint(0, 12), -8, 8),),
    brute=lambda nums: max([0] + [k for v in set(nums) for k in [next(k for k in range(1, 100) if v + k not in set(nums))]]),
    hints=[
        "Sorting is O(n log n). A set gives O(1) membership checks.",
        "Only start counting at a value v whose predecessor v − 1 is absent: that's the start of a run.",
        "From each start, count upward while the next value exists. (Union–find on v and v + 1 also works.)",
    ],
    insight="Counting only from run starts makes the set scan O(n).",
    time="O(n)", space="O(n)",
    pitfalls=["Counting upward from every value, which is O(n²) on one long run."],
)
def longest_consecutive(nums):
    s, best = set(nums), 0
    for v in s:
        if v - 1 not in s:
            k = 1
            while v + k in s:
                k += 1
            best = max(best, k)
    return best


def _cross_brute(row, col, cells):
    def ok(day):
        flooded = {(r - 1, c - 1) for r, c in cells[:day]}
        grid = [[1 if (i, j) in flooded else 0 for j in range(col)] for i in range(row)]
        starts = [(0, j) for j in range(col) if not grid[0][j]]
        reach = _bfs_grid(grid, starts, lambda v: v == 0)
        return any(i == row - 1 for i, _ in reach)
    return max(d for d in range(len(cells) + 1) if ok(d))


@problem(
    slug="last-day-where-you-can-still-cross", title="Last Day Where You Can Still Cross", difficulty="Hard", pattern=UF,
    tags=["Array", "Binary Search", "Depth-First Search", "Breadth-First Search", "Union Find", "Matrix"],
    sig="latestDayToCross(self, row: int, col: int, cells: list[list[int]]) -> int",
    desc="""A `row × col` grid starts as all land. On day `i` (1-indexed), cell `cells[i − 1] = [r, c]` (1-indexed) floods. Return the last day on which you can still walk from any cell in the top row to any cell in the bottom row through land, moving 4-directionally. Every cell appears in `cells` exactly once.""",
    constraints=["2 ≤ row, col ≤ 2 × 10⁴", "4 ≤ row × col ≤ 2 × 10⁴"],
    samples=[(2, 2, [[1, 1], [2, 1], [1, 2], [2, 2]]), (2, 2, [[1, 1], [1, 2], [2, 1], [2, 2]]), (3, 3, [[1, 2], [2, 1], [3, 3], [2, 2], [1, 1], [1, 3], [2, 3], [3, 2], [3, 1]])],
    gen=lambda r: (lambda R, C: (R, C, [[i + 1, j + 1] for i, j in r.sample([(i, j) for i in range(R) for j in range(C)], R * C)]))(r.randint(2, 4), r.randint(2, 4)),
    brute=_cross_brute,
    hints=[
        "Flooding only makes crossing harder, so the days you can cross form a prefix.",
        "Reverse time: start fully flooded and turn cells back into land, latest day first.",
        "Union each restored cell with its land neighbors and with virtual top/bottom nodes; the first moment top and bottom connect gives the answer.",
    ],
    insight="Reverse the flooding and use union–find with two virtual nodes.",
    time="O(row·col · α)", space="O(row·col)",
    pitfalls=["Running a full BFS for every day."],
)
def latest_day_to_cross(row, col, cells):
    n = row * col
    top, bottom = n, n + 1
    d = _DSU(n + 2)
    land = [[False] * col for _ in range(row)]
    for day in range(len(cells) - 1, -1, -1):
        r, c = cells[day][0] - 1, cells[day][1] - 1
        land[r][c] = True
        k = r * col + c
        if r == 0:
            d.union(k, top)
        if r == row - 1:
            d.union(k, bottom)
        for dr, dc in DIRS:
            x, y = r + dr, c + dc
            if 0 <= x < row and 0 <= y < col and land[x][y]:
                d.union(k, x * col + y)
        if d.find(top) == d.find(bottom):
            return day
    return 0


def _slash_brute(grid):
    n = len(grid)
    N = 3 * n
    big = [[0] * N for _ in range(N)]
    for i, row in enumerate(grid):
        for j, ch in enumerate(row):
            for k in range(3):
                if ch == "/":
                    big[3 * i + k][3 * j + 2 - k] = 1
                elif ch == "\\":
                    big[3 * i + k][3 * j + k] = 1
    seen, count = set(), 0
    for i in range(N):
        for j in range(N):
            if not big[i][j] and (i, j) not in seen:
                count += 1
                seen |= set(_bfs_grid(big, [(i, j)], lambda v: v == 0))
    return count


@problem(
    slug="regions-cut-by-slashes", title="Regions Cut By Slashes", difficulty="Medium", pattern=UF,
    tags=["Array", "Hash Table", "Depth-First Search", "Breadth-First Search", "Union Find", "Matrix"],
    sig="regionsBySlashes(self, grid: list[str]) -> int",
    desc="""An `n × n` grid of 1 × 1 squares contains `'/'`, `'\\'` or `' '` (blank) in each square; slashes divide squares diagonally. Return the number of regions.""",
    constraints=["1 ≤ n ≤ 30", "grid[i][j] is '/', '\\' or ' '"],
    samples=[([" /", "/ "],), ([" /", "  "],), (["/\\", "\\/"],)],
    gen=lambda r: (lambda n: (["".join(r.choice(" /\\") for _ in range(n)) for _ in range(n)],))(r.randint(1, 4)),
    brute=_slash_brute,
    hints=[
        "Split every square into 4 triangles: top, right, bottom, left.",
        "A blank joins all four; '/' joins top–left and bottom–right; '\\' joins top–right and bottom–left.",
        "Also join each square's right triangle with the next square's left, and bottom with the top of the square below. Count components.",
    ],
    insight="Subdivide squares into triangles and count components with union–find.",
    time="O(n² α)", space="O(n²)",
    pitfalls=["Forgetting to connect triangles across neighboring squares."],
)
def regions_by_slashes(grid):
    n = len(grid)
    d = _DSU(4 * n * n)
    for i in range(n):
        for j in range(n):
            b = 4 * (i * n + j)
            c = grid[i][j]
            if c == " ":
                d.union(b, b + 1); d.union(b + 1, b + 2); d.union(b + 2, b + 3)
            elif c == "/":
                d.union(b, b + 3); d.union(b + 1, b + 2)
            else:
                d.union(b, b + 1); d.union(b + 2, b + 3)
            if j + 1 < n:
                d.union(b + 1, 4 * (i * n + j + 1) + 3)
            if i + 1 < n:
                d.union(b + 2, 4 * ((i + 1) * n + j))
    return d.count


@problem(
    slug="number-of-operations-to-make-network-connected", title="Number of Operations to Make Network Connected", difficulty="Medium",
    pattern=UF, tags=["Depth-First Search", "Breadth-First Search", "Union Find", "Graph"],
    sig="makeConnected(self, n: int, connections: list[list[int]]) -> int",
    desc="""`n` computers are joined by cables `connections[i] = [a, b]`. You may unplug any cable and plug it between two other computers. Return the minimum number of moves to connect all computers, or `-1` if there aren't enough cables.""",
    constraints=["1 ≤ n ≤ 10⁵", "no repeated connections"],
    samples=[(4, [[0, 1], [0, 2], [1, 2]]), (6, [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3]]), (6, [[0, 1], [0, 2], [0, 3], [1, 2]])],
    gen=lambda r: (lambda n: (n, sorted({tuple(sorted(r.sample(range(n), 2))) for _ in range(r.randint(0, n + 2))})))(r.randint(2, 8)),
    hints=[
        "Connecting n computers needs at least n − 1 cables.",
        "Cables inside an already-connected group that close a cycle are spare.",
        "If there are enough cables, the answer is (number of components − 1).",
    ],
    insight="Count components with union–find; each move joins two components.",
    time="O(E α(n))", space="O(n)",
    pitfalls=["Forgetting the n − 1 cable check."],
)
def make_connected(n, connections):
    if len(connections) < n - 1:
        return -1
    d = _DSU(n)
    for a, b in connections:
        d.union(a, b)
    return d.count - 1


def _eq_brute(equations):
    letters = sorted({e[0] for e in equations} | {e[3] for e in equations})
    from itertools import product
    for vals in product(range(len(letters)), repeat=len(letters)):
        v = dict(zip(letters, vals))
        if all((v[e[0]] == v[e[3]]) == (e[1] == "=") for e in equations):
            return True
    return False


@problem(
    slug="satisfiability-of-equality-equations", title="Satisfiability of Equality Equations", difficulty="Medium", pattern=UF,
    tags=["Array", "String", "Union Find", "Graph"],
    sig="equationsPossible(self, equations: list[str]) -> bool",
    desc="""Each equation is a 4-character string `"a==b"` or `"a!=b"` with lowercase variable names. Return `true` if integers can be assigned to the variables so that all equations hold.""",
    constraints=["1 ≤ len(equations) ≤ 500"],
    samples=[(["a==b", "b!=a"],), (["b==a", "a==b"],), (["a==b", "b==c", "a==c"],), (["a==b", "b!=c", "c==a"],)],
    gen=lambda r: (["%s%s%s" % (r.choice("abcd"), r.choice(["==", "!="]), r.choice("abcd")) for _ in range(r.randint(1, 5))],),
    brute=_eq_brute,
    hints=[
        "Equalities group variables together; inequalities only check groups.",
        "First union every pair joined by '=='.",
        "Then for each '!=', fail if both sides share a root (including \"a!=a\").",
    ],
    insight="Process equalities with union–find, then verify inequalities.",
    time="O(n α)", space="O(1) (26 letters)",
    pitfalls=["Processing equations in the given order, mixing checks with unions."],
)
def equations_possible(equations):
    d = _DSU(26)
    for e in equations:
        if e[1] == "=":
            d.union(ord(e[0]) - 97, ord(e[3]) - 97)
    return all(d.find(ord(e[0]) - 97) != d.find(ord(e[3]) - 97) for e in equations if e[1] == "!")


def _similar(a, b):
    diff = [i for i in range(len(a)) if a[i] != b[i]]
    return not diff or (len(diff) == 2 and a[diff[0]] == b[diff[1]] and a[diff[1]] == b[diff[0]])


def _anagrams(r):
    base = list(r.word(r.randint(2, 5), "abcde"))
    out = []
    for _ in range(r.randint(1, 6)):
        w = base[:]
        r.shuffle(w)
        out.append("".join(w))
    return (out,)


@problem(
    slug="similar-string-groups", title="Similar String Groups", difficulty="Hard", pattern=UF,
    tags=["Array", "Hash Table", "String", "Depth-First Search", "Breadth-First Search", "Union Find"],
    sig="numSimilarGroups(self, strs: list[str]) -> int",
    desc="""All strings in `strs` are anagrams of each other. Two strings are **similar** if they're equal or swapping two letters in one gives the other. Groups are formed by connecting similar strings (directly or through a chain). Return the number of groups.""",
    constraints=["1 ≤ len(strs) ≤ 300", "1 ≤ len(strs[i]) ≤ 300", "all strings are anagrams of each other"],
    samples=[(["tars", "rats", "arts", "star"],), (["omv", "ovm"],)],
    gen=_anagrams,
    brute=lambda strs: len({frozenset(_str_component(strs, i)) for i in range(len(strs))}),
    hints=[
        "Similarity defines edges; groups are connected components.",
        "Two anagrams are similar exactly when they differ in 0 or 2 positions (with the two letters swapped).",
        "Check every pair and union the similar ones; count the components.",
    ],
    insight="Union–find over pairwise similarity checks.",
    time="O(n² · L)", space="O(n)",
    pitfalls=["Treating similarity as transitive without union–find."],
)
def num_similar_groups(strs):
    d = _DSU(len(strs))
    for i in range(len(strs)):
        for j in range(i + 1, len(strs)):
            if _similar(strs[i], strs[j]):
                d.union(i, j)
    return d.count


def _str_component(strs, s):
    seen, st = {s}, [s]
    while st:
        u = st.pop()
        for v in range(len(strs)):
            if v not in seen and _similar(strs[u], strs[v]):
                seen.add(v)
                st.append(v)
    return seen


def _swaps_brute(s, pairs):
    best, seen, q = s, {s}, deque([s])
    while q:
        cur = q.popleft()
        best = min(best, cur)
        for a, b in pairs:
            l = list(cur)
            l[a], l[b] = l[b], l[a]
            t = "".join(l)
            if t not in seen:
                seen.add(t)
                q.append(t)
    return best


@problem(
    slug="smallest-string-with-swaps", title="Smallest String With Swaps", difficulty="Medium", pattern=UF,
    tags=["Array", "Hash Table", "String", "Depth-First Search", "Breadth-First Search", "Union Find", "Sorting"],
    sig="smallestStringWithSwaps(self, s: str, pairs: list[list[int]]) -> str",
    desc="""You may swap the characters at any pair of indices in `pairs`, as many times as you like. Return the lexicographically smallest string you can reach.""",
    constraints=["1 ≤ len(s) ≤ 10⁵", "0 ≤ len(pairs) ≤ 10⁵", "lowercase letters"],
    samples=[("dcab", [[0, 3], [1, 2]]), ("dcab", [[0, 3], [1, 2], [0, 2]]), ("cba", [[0, 1], [1, 2]])],
    gen=lambda r: (lambda s: (s, [r.sample(range(len(s)), 2) for _ in range(r.randint(0, 3))] if len(s) > 1 else []))(r.word(r.randint(1, 6), "abcd")),
    brute=_swaps_brute,
    hints=[
        "Swaps chain: if you can swap (a, b) and (b, c), you can arrange a, b, c in any order.",
        "So indices in the same connected component can hold their letters in any order.",
        "Union the pairs, then within each component put its sorted letters into its sorted indices.",
    ],
    insight="Connected components of swappable indices can be sorted freely.",
    time="O(n log n)", space="O(n)",
    pitfalls=["Applying swaps greedily one at a time."],
)
def smallest_string_with_swaps(s, pairs):
    d = _DSU(len(s))
    for a, b in pairs:
        d.union(a, b)
    groups = defaultdict(list)
    for i in range(len(s)):
        groups[d.find(i)].append(i)
    out = list(s)
    for idx in groups.values():
        for i, c in zip(idx, sorted(s[i] for i in idx)):
            out[i] = c
    return "".join(out)


def _big_itinerary(r, n):
    airports = ["JFK", "ATL", "SFO", "LAX", "ORD", "SEA", "BOS", "MIA"]
    route = ["JFK"]
    while len(route) <= n:
        route.append(r.choice([a for a in airports if a != route[-1]]))
    tickets = [[a, b] for a, b in zip(route, route[1:])]
    r.shuffle(tickets)
    return (tickets,)


def _big_ladder(r):
    words = sorted({r.word(4, "abcdef") for _ in range(1200)})
    return r.word(4, "abcdef"), r.choice(words), words


def _big_accounts(r, people, accounts):
    names = ["N%d" % (i % 37) for i in range(people)]
    out = []
    for _ in range(accounts):
        p = r.randint(0, people - 1)
        out.append([names[p]] + ["p%de%d@x.co" % (p, j) for j in r.sample(range(6), r.randint(1, 4))])
    return (out,)


def _big_edges(r, n, m, weight=None):
    edges = set()
    while len(edges) < m:
        a, b = r.sample(range(n), 2)
        edges.add((min(a, b), max(a, b)))
    return [list(e) for e in sorted(edges)]


def _connected_matrix(r, n, links):
    m = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    for _ in range(links):
        a, b = r.randint(0, n - 1), r.randint(0, n - 1)
        m[a][b] = m[b][a] = 1
    return (m,)


EXTRA = {
    "rotting-oranges": {
        "edge": [([[0]],), ([[1]],), ([[2]],), ([[2, 2], [1, 1]],), ([[1, 2, 0, 1]],), ([[2] + [1] * 9 for _ in range(10)],)],
    },
    "01-matrix": {
        "edge": [([[0]],), ([[0, 1]],), ([[1], [0]],), ([[1, 1, 1], [1, 1, 1], [1, 1, 0]],)],
        "large": [lambda r: ([[0] + [1] * 99] + [[1] * 100 for _ in range(99)],), lambda r: ([[r.choice([0, 1, 1, 1, 1]) for _ in range(100)] for _ in range(100)],)],
    },
    "pacific-atlantic-water-flow": {
        "edge": [([[1]],), ([[1, 2]],), ([[2, 1], [1, 2]],), ([[3, 3, 3], [3, 1, 3], [0, 2, 4]],)],
        "large": [lambda r: ([r.ints(100, 0, 100000) for _ in range(100)],), lambda r: ([[5] * 100 for _ in range(100)],)],
    },
    "surrounded-regions": {
        "edge": [([["O"]],), ([["X"]],), ([["O", "O"], ["O", "O"]],), ([["X", "X", "X"], ["X", "O", "X"], ["X", "X", "X"]],)],
        "large": [lambda r: ([[r.choice("XXO") for _ in range(150)] for _ in range(150)],), lambda r: ([["X"] * 150] + [["X"] + ["O"] * 148 + ["X"] for _ in range(148)] + [["X"] * 150],)],
    },
    "island-perimeter": {
        "edge": [([[1]],), ([[1, 1]],), ([[0, 1], [0, 1]],), ([[1, 1], [1, 1]],)],
        "large": [lambda r: ([[1] * 100 for _ in range(100)],), lambda r: (lambda cells: ([[1 if (i, j) in cells else 0 for j in range(100)] for i in range(100)],))(_grow_island(r, 100, 100))],
    },
    "max-area-of-island": {
        "edge": [([[0]],), ([[1]],), ([[1, 0, 1]],), ([[1, 1], [1, 0]],)],
        "large": [lambda r: ([[1] * 50 for _ in range(50)],), lambda r: ([[r.choice([0, 1]) for _ in range(50)] for _ in range(50)],)],
    },
    "shortest-path-in-binary-matrix": {
        "edge": [([[0]],), ([[1]],), ([[0, 0], [0, 1]],), ([[0, 0, 0], [1, 1, 0], [1, 1, 1]],)],
        "large": [lambda r: ([[0] * 100 for _ in range(100)],), lambda r: ([[r.choice([0, 0, 0, 1]) for _ in range(100)] for _ in range(100)],)],
    },
    "word-ladder": {
        "edge": [("a", "c", ["a", "b", "c"]), ("hot", "dog", ["hot", "dog"]), ("hot", "hot", ["hot"]), ("abc", "abd", ["abd"])],
        "large": [_big_ladder],
    },
    "open-the-lock": {
        "edge": [(["8888"], "0000"), (["0000"], "0000"), (["1000", "9000", "0100", "0900", "0010", "0090", "0001", "0009"], "1111"),
                 (["8887", "8889", "8878", "8898", "8788", "8988", "7888", "9888"], "8888"), (["1234"], "5555")],
    },
    "keys-and-rooms": {
        "edge": [([[1], []],), ([[], [0]],), ([[1], [0], [0]],), ([[1, 1], [2], []],)],
        "large": [lambda r: ([[i + 1] for i in range(999)] + [[]],), lambda r: ([r.ints(3, 0, 999) for _ in range(1000)],)],
    },
    "all-paths-from-source-to-target": {
        "edge": [([[1], []],), ([[1, 2], [2], []],), ([[2], [], [1]],)],
        "edge_nb": [([list(range(i + 1, 12)) for i in range(12)],)],
    },
    "find-center-of-star-graph": {
        "edge": [([[1, 2], [2, 3]],), ([[2, 1], [3, 1]],), ([[1, 3], [2, 3]],)],
        "large": [lambda r: ([[7, v] if v % 2 else [v, 7] for v in range(1, 9002) if v != 7],)],
    },
    "cheapest-flights-within-k-stops": {
        "edge": [(1, [], 0, 0, 0), (2, [[0, 1, 5]], 0, 1, 0), (2, [[1, 0, 5]], 0, 1, 1), (3, [[0, 1, 1], [1, 2, 1], [0, 2, 5]], 0, 2, 0), (4, [[0, 1, 1], [0, 2, 5], [1, 2, 1], [2, 3, 1]], 0, 3, 1)],
        "large": [lambda r: (100, [[a, b, r.randint(1, 10000)] for a, b in {tuple(r.sample(range(100), 2)) for _ in range(3000)}], 0, 99, 20)],
    },
    "path-with-maximum-probability": {
        "edge": [(2, [[0, 1]], [0.0], 0, 1), (2, [[0, 1]], [1.0], 1, 0), (3, [[0, 1], [1, 2], [0, 2]], [1.0, 1.0, 0.5], 0, 2), (5, [[1, 4], [2, 4], [0, 4], [0, 3], [0, 2], [2, 3]], [0.37, 0.17, 0.93, 0.23, 0.39, 0.04], 3, 4)],
        "large": [lambda r: (lambda e: (4000, e, [round(r.random(), 2) for _ in e], 0, 3999))(_big_edges(r, 4000, 6000))],
    },
    "swim-in-rising-water": {
        "edge": [([[0]],), ([[3, 2], [0, 1]],), ([[0, 1], [2, 3]],)],
        "large": [lambda r: (lambda v: ([v[i * 50:(i + 1) * 50] for i in range(50)],))(r.sample(range(2500), 2500))],
    },
    "min-cost-to-connect-all-points": {
        "edge": [([[0, 0]],), ([[0, 0], [1, 1]],), ([[-1000000, -1000000], [1000000, 1000000]],), ([[0, 0], [1, 0], [2, 0], [3, 0]],)],
        "large": [lambda r: ([list(p) for p in {(r.randint(-10**6, 10**6), r.randint(-10**6, 10**6)) for _ in range(500)}],)],
    },
    "reconstruct-itinerary": {
        "edge": [([["JFK", "ATL"]],), ([["JFK", "B"], ["JFK", "A"], ["A", "JFK"]],), ([["JFK", "KUL"], ["JFK", "NRT"], ["NRT", "JFK"]],)],
        "large": [lambda r: _big_itinerary(r, 300)],
    },
    "bus-routes": {
        "edge": [([[1, 2]], 1, 1), ([[1, 2]], 1, 3), ([[1], [2]], 1, 2), ([[1, 2], [2, 3], [3, 4]], 1, 4), ([[0, 1000000]], 1000000, 0)],
        "large": [lambda r: ([r.distinct(20, 0, 5000) for _ in range(500)], 1, 4999)],
    },
    "number-of-provinces": {
        "edge": [([[1]],), ([[1, 1], [1, 1]],), ([[1, 0], [0, 1]],), ([[1, 0, 0, 1], [0, 1, 1, 0], [0, 1, 1, 1], [1, 0, 1, 1]],)],
        "large": [lambda r: _connected_matrix(r, 200, 150)],
    },
    "accounts-merge": {
        "edge": [([["A", "a@x"]],), ([["A", "a@x"], ["A", "a@x"]],), ([["A", "a@x"], ["A", "b@x"]],), ([["A", "a@x", "b@x"], ["A", "c@x"], ["A", "c@x", "b@x"]],)],
        "large": [lambda r: _big_accounts(r, 300, 1000)],
    },
    "longest-consecutive-sequence": {
        "edge": [([5],), ([1, 1, 1],), ([1, 3, 5],), ([-1000000000, 1000000000],), ([9, 1, 4, 7, 3, -1, 0, 5, 8, -1, 6],)],
        "large": [lambda r: (r.sample(range(-5000, 10000), 15000),), lambda r: (r.ints(10000, -10**9, 10**9),)],
    },
    "last-day-where-you-can-still-cross": {
        "edge": [(2, 2, [[1, 1], [2, 2], [1, 2], [2, 1]]), (2, 2, [[2, 1], [2, 2], [1, 1], [1, 2]])],
        "large": [lambda r: (100, 100, [[i + 1, j + 1] for i, j in r.sample([(i, j) for i in range(100) for j in range(100)], 10000)])],
    },
    "regions-cut-by-slashes": {
        "edge": [(["/"],), ([" "],), (["\\"],), (["//", "/ "],), (["\\/", "/\\"],)],
        "large": [lambda r: (["".join(r.choice(" /\\") for _ in range(30)) for _ in range(30)],)],
    },
    "number-of-operations-to-make-network-connected": {
        "edge": [(1, []), (2, []), (2, [[0, 1]]), (5, [[0, 1], [0, 2], [3, 4], [2, 3]]), (4, [[0, 1], [1, 2], [2, 0], [0, 3]])],
        "large": [lambda r: (10000, _big_edges(r, 10000, 10000)), lambda r: (10000, _big_edges(r, 10000, 9998))],
    },
    "satisfiability-of-equality-equations": {
        "edge": [(["a==a"],), (["a!=a"],), (["c==c", "b==d", "x!=z"],), (["a==b", "b==c", "c==d", "d!=a"],)],
        "large": [lambda r: ([f"{a}=={b}" for a, b in zip("abcdefghijklmnopqrstuvwxy", "bcdefghijklmnopqrstuvwxyz")] * 18 + ["a!=z"],)],
    },
    "similar-string-groups": {
        "edge": [(["a"],), (["ab", "ba"],), (["abc", "abc"],), (["abc", "bca", "cab"],)],
        "large": [lambda r: (lambda base: (["".join(r.sample(base, len(base))) for _ in range(200)],))(r.word(30, "abcdefgh"))],
    },
    "smallest-string-with-swaps": {
        "edge": [("a", []), ("ba", []), ("ba", [[0, 1]]), ("dcab", [[0, 3], [1, 2], [0, 2]]), ("abc", [[0, 1], [1, 0]])],
        "large": [lambda r: (lambda s: (s, [r.sample(range(len(s)), 2) for _ in range(6000)]))(r.word(30000, "abcdefghijklmnopqrstuvwxyz"))],
    },
}
