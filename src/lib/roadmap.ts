// The learning roadmap: 32 patterns arranged as a tree, NeetCode-style.
// `row` and `x` (percent of the width) place each node in the diagram; `parents` draw the connecting lines.
// Problems belong to a pattern through their own `pattern` field (problems.ts and the catalog in content/).
// Keep this file free of runtime imports so scripts can load it directly with Node.

export interface Pattern {
  id: string;
  name: string;
  /** What the pattern is, in a sentence or two. */
  summary: string;
  /** Signals in a problem statement that suggest this pattern. */
  useWhen: string;
  parents: string[];
  row: number;
  x: number;
}

export const patterns: Pattern[] = [
  // Row 0
  {
    id: "arrays-hashing",
    name: "Arrays & Hashing",
    summary: "Store what you've seen in a hash map or set so lookups take O(1) instead of rescanning the array.",
    useWhen: "You need to find pairs, duplicates or counts, or check membership quickly.",
    parents: [],
    row: 0,
    x: 50,
  },

  // Row 1
  {
    id: "prefix-sum",
    name: "Prefix Sum",
    summary: "Precompute running totals so the sum of any subarray is one subtraction.",
    useWhen: "The problem asks about sums of ranges or subarrays, often many times.",
    parents: ["arrays-hashing"],
    row: 1,
    x: 7,
  },
  {
    id: "knowing-what-to-track",
    name: "Knowing What to Track",
    summary: "Record just the right facts as you scan, such as counts, first positions or running totals, so each question is answered in one pass.",
    useWhen: "Anagrams, frequencies, \"first unique\", or comparing character counts between strings.",
    parents: ["arrays-hashing"],
    row: 1,
    x: 23,
  },
  {
    id: "cyclic-sort",
    name: "Cyclic Sort",
    summary: "When values are in the range 1..n, swap each value to its own index in one pass.",
    useWhen: "Find missing or duplicate numbers in an array of 1..n.",
    parents: ["arrays-hashing"],
    row: 1,
    x: 39,
  },
  {
    id: "two-pointers",
    name: "Two Pointers",
    summary: "Move two indices toward each other (or together) to avoid a nested loop.",
    useWhen: "The input is sorted, or you compare elements from both ends.",
    parents: ["arrays-hashing"],
    row: 1,
    x: 56,
  },
  {
    id: "stack",
    name: "Stack",
    summary: "Last in, first out: remember unfinished work and resolve the most recent first.",
    useWhen: "Matching brackets, undo operations, or evaluating nested expressions.",
    parents: ["arrays-hashing"],
    row: 1,
    x: 73,
  },
  {
    id: "matrix",
    name: "Matrix Traversal",
    summary: "Walk a 2D grid row by row, in spirals, or along diagonals while tracking boundaries.",
    useWhen: "The input is a grid and you rotate, spiral or search it.",
    parents: ["arrays-hashing"],
    row: 1,
    x: 91,
  },

  // Row 2
  {
    id: "intervals",
    name: "Intervals",
    summary: "Sort intervals by start, then merge or compare neighbours.",
    useWhen: "Meetings, ranges or time slots that may overlap.",
    parents: ["two-pointers"],
    row: 2,
    x: 10,
  },
  {
    id: "sliding-window",
    name: "Sliding Window",
    summary: "Grow and shrink a window over the array, updating the answer as it moves.",
    useWhen: "Longest or shortest contiguous subarray or substring that meets a condition.",
    parents: ["two-pointers"],
    row: 2,
    x: 27,
  },
  {
    id: "binary-search",
    name: "Binary Search",
    summary: "Halve the search space each step, on an array or on the answer itself.",
    useWhen: "Sorted input, or \"find the smallest value that works\".",
    parents: ["two-pointers"],
    row: 2,
    x: 44,
  },
  {
    id: "linked-list",
    name: "Linked List",
    summary: "Rewire next pointers carefully; a dummy head node removes most edge cases.",
    useWhen: "Reversing, merging or reordering nodes in place.",
    parents: ["two-pointers"],
    row: 2,
    x: 61,
  },
  {
    id: "monotonic-stack",
    name: "Monotonic Stack",
    summary: "Keep a stack in increasing or decreasing order to find the next greater or smaller element.",
    useWhen: "\"Next greater element\", daily temperatures, or largest rectangle problems.",
    parents: ["stack"],
    row: 2,
    x: 80,
  },

  // Row 3
  {
    id: "greedy",
    name: "Greedy",
    summary: "Make the locally best choice at each step when it provably leads to the global best.",
    useWhen: "Scheduling, jumping or choosing items where a simple rule always works.",
    parents: ["intervals"],
    row: 3,
    x: 8,
  },
  {
    id: "sort-and-search",
    name: "Sort and Search",
    summary: "Sort the input first so binary search, two pointers or a greedy sweep become possible.",
    useWhen: "Pairs or thresholds where the original order doesn't matter, or \"how many values are at most x\" questions.",
    parents: ["binary-search"],
    row: 3,
    x: 25,
  },
  {
    id: "tree-dfs",
    name: "Tree DFS",
    summary: "Recurse into subtrees and combine their answers on the way back up.",
    useWhen: "Paths, depths, or properties that depend on whole subtrees.",
    parents: ["binary-search","linked-list"],
    row: 3,
    x: 43,
  },
  {
    id: "tree-bfs",
    name: "Tree BFS",
    summary: "Visit a tree level by level with a queue.",
    useWhen: "Level order, right side view, or the shortest depth.",
    parents: ["binary-search","linked-list"],
    row: 3,
    x: 60,
  },
  {
    id: "fast-slow-pointers",
    name: "Fast & Slow Pointers",
    summary: "Move one pointer twice as fast as the other to detect cycles or find the middle.",
    useWhen: "Cycle detection, or the middle of a linked list, in O(1) space.",
    parents: ["linked-list"],
    row: 3,
    x: 77,
  },
  {
    id: "custom-data-structures",
    name: "Custom Data Structures",
    summary: "Combine hash maps, lists, stacks and heaps inside a class so several operations are all fast.",
    useWhen: "Design problems: caches, stacks with extra operations, time-based or snapshot stores.",
    parents: ["linked-list"],
    row: 3,
    x: 93,
  },

  // Row 4
  {
    id: "subsets",
    name: "Subsets",
    summary: "Generate every subset, permutation or combination by extending partial results one element at a time.",
    useWhen: "\"Return all possible…\" questions, where the answer itself is exponential in size.",
    parents: ["tree-dfs"],
    row: 4,
    x: 20,
  },
  {
    id: "tries",
    name: "Tries",
    summary: "A tree of characters for fast prefix lookups over many words.",
    useWhen: "Autocomplete, word search, or \"does any word start with…\".",
    parents: ["tree-dfs"],
    row: 4,
    x: 42,
  },
  {
    id: "heap",
    name: "Heap / Top K",
    summary: "A priority queue always gives the smallest (or largest) item in O(log n).",
    useWhen: "The k largest, smallest or most frequent items, or a running minimum.",
    parents: ["tree-bfs"],
    row: 4,
    x: 62,
  },

  // Row 5
  {
    id: "backtracking",
    name: "Backtracking",
    summary: "Build candidates one choice at a time and undo choices that can't lead to an answer.",
    useWhen: "Generate all subsets, permutations or combinations, or solve puzzles.",
    parents: ["subsets"],
    row: 5,
    x: 16,
  },
  {
    id: "two-heaps",
    name: "Two Heaps",
    summary: "A max-heap for the lower half and a min-heap for the upper half.",
    useWhen: "A running median, or balancing two halves of a stream.",
    parents: ["heap"],
    row: 5,
    x: 54,
  },
  {
    id: "k-way-merge",
    name: "K-way Merge",
    summary: "Merge k sorted lists by always taking the smallest head from a heap.",
    useWhen: "Several sorted inputs that need combining, or the kth smallest across lists.",
    parents: ["heap"],
    row: 5,
    x: 74,
  },

  // Row 6
  {
    id: "dp-1d",
    name: "1-D DP",
    summary: "Solve each smaller subproblem once, store it, and build up to the answer.",
    useWhen: "Counting ways or finding the best result, where each step depends on earlier steps.",
    parents: ["backtracking"],
    row: 6,
    x: 10,
  },
  {
    id: "graphs",
    name: "Graphs",
    summary: "Explore nodes and edges with BFS or DFS, tracking visited nodes.",
    useWhen: "Islands in a grid, connected components, or cloning a network.",
    parents: ["backtracking"],
    row: 6,
    x: 32,
  },

  // Row 7
  {
    id: "bit-manipulation",
    name: "Bit Manipulation",
    summary: "Use AND, OR, XOR and shifts to work on individual bits.",
    useWhen: "Single numbers among pairs, counting bits, or sets encoded as bitmasks.",
    parents: ["dp-1d"],
    row: 7,
    x: 7,
  },
  {
    id: "dp-2d",
    name: "2-D DP",
    summary: "A table of subproblems indexed by two things, like positions in two strings.",
    useWhen: "Grid paths, edit distance, or longest common subsequence.",
    parents: ["dp-1d","graphs"],
    row: 7,
    x: 23,
  },
  {
    id: "union-find",
    name: "Union Find",
    summary: "Track which items are connected, merging groups in near-constant time.",
    useWhen: "Dynamic connectivity, redundant connections, or counting components.",
    parents: ["graphs"],
    row: 7,
    x: 41,
  },
  {
    id: "topological-sort",
    name: "Topological Sort",
    summary: "Order the nodes of a directed acyclic graph so every edge points forward.",
    useWhen: "Prerequisites, build order, or course schedules.",
    parents: ["graphs"],
    row: 7,
    x: 58,
  },
  {
    id: "advanced-graphs",
    name: "Advanced Graphs",
    summary: "Shortest paths and minimum spanning trees: Dijkstra, Bellman-Ford, Prim, Kruskal.",
    useWhen: "Weighted edges, cheapest routes, or connecting everything at minimum cost.",
    parents: ["graphs"],
    row: 7,
    x: 75,
  },
  {
    id: "math-geometry",
    name: "Math & Geometry",
    summary: "Number properties, modular arithmetic and coordinate tricks.",
    useWhen: "Rotating matrices, powers, primes, or points on a plane.",
    parents: ["graphs"],
    row: 7,
    x: 92,
  },
];

export const ROADMAP_ROWS = Math.max(...patterns.map((p) => p.row)) + 1;
