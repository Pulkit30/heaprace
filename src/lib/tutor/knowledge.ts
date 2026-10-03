// The tutor's knowledge base (the "R" in RAG). `npm run db:seed` loads it into the kb_chunks table,
// where Postgres full-text search retrieves it. Everything here is written as guidance in words:
// there is deliberately no solution code anywhere, so the tutor has nothing to leak.
// Keep this file free of runtime imports so scripts can load it directly with Node.

export interface ProblemGuide {
  slug: string;
  /** Progressive hints, from a gentle nudge to the full idea in words. */
  hints: [string, string, string];
  /** The key idea, shown after all hints. */
  insight: string;
  complexity: { time: string; space: string; note?: string };
  pitfalls: string[];
}

export interface ErrorGuide {
  id: string;
  title: string;
  /** Substrings that identify this error in a traceback or verdict (case-insensitive). */
  match: string[];
  body: string;
}

export interface PatternNote {
  patternId: string;
  /** How to apply the pattern, step by step, in words. */
  howTo: string;
  pitfalls: string;
}

export const problemGuides: ProblemGuide[] = [
  {
    slug: "two-sum",
    hints: [
      "The simplest approach checks every pair, which is O(n²). Can you avoid the inner loop?",
      "For each number x, the partner you need is exactly target − x. Which data structure answers \"have I seen this value before?\" in O(1)?",
      "Walk the array once. Before remembering the current number, check whether its partner (target − x) is already stored in a dictionary that maps value → index.",
    ],
    insight: "Turn \"find a pair\" into \"look up the complement\": a hash map of values seen so far gives each lookup in O(1).",
    complexity: { time: "O(n)", space: "O(n)" },
    pitfalls: [
      "Using the same element twice: check for the partner before inserting the current number.",
      "Returning the values instead of their indices.",
    ],
  },
  {
    slug: "valid-parentheses",
    hints: [
      "The most recently opened bracket must be the first one closed. Which structure is last-in, first-out?",
      "Push opening brackets. When you see a closing bracket, the item on top must be its matching opener.",
      "Fail immediately on a closer when the stack is empty or the top doesn't match, and at the end the stack must be empty.",
    ],
    insight: "A stack mirrors nesting: every closer must match the latest unmatched opener.",
    complexity: { time: "O(n)", space: "O(n)" },
    pitfalls: [
      "Forgetting the final check that nothing is left open, e.g. \"((\".",
      "Popping from an empty stack when the string starts with a closer.",
    ],
  },
  {
    slug: "best-time-to-buy-and-sell-stock",
    hints: [
      "For any selling day, the best buying day is the cheapest price that came before it.",
      "You don't need to look back each time: keep the minimum price seen so far as you scan.",
      "On each day, the profit from selling today is today's price minus the running minimum. Track the best such profit.",
    ],
    insight: "One pass with a running minimum turns every day into a candidate sell day.",
    complexity: { time: "O(n)", space: "O(1)" },
    pitfalls: ["Selling before buying.", "Returning a negative profit instead of 0 when prices only fall."],
  },
  {
    slug: "contains-duplicate",
    hints: [
      "If you sort the array, equal values end up next to each other. That's O(n log n). Can you do it in one pass?",
      "A set remembers every value you've already seen.",
      "Return True the moment a value is already in the set. (Or compare the size of the set with the length of the array.)",
    ],
    insight: "Membership checks in a set are O(1) on average, so one scan is enough.",
    complexity: { time: "O(n)", space: "O(n)" },
    pitfalls: ["Comparing every pair with nested loops, which is too slow for 10⁵ elements."],
  },
  {
    slug: "maximum-subarray",
    hints: [
      "Think about the best subarray that ends exactly at index i. How does it relate to the best one ending at i − 1?",
      "At each index you have two choices: extend the previous subarray, or start fresh from the current element.",
      "Track two values while scanning: the best sum of a subarray ending at the current index, and the best seen anywhere. Update the first by choosing the better of extending or restarting.",
    ],
    insight: "Kadane's idea: a running sum that has become worse than the current element on its own should be dropped.",
    complexity: { time: "O(n)", space: "O(1)" },
    pitfalls: [
      "Starting the best sum at 0: if every number is negative, the answer is the largest (least negative) element.",
    ],
  },
  {
    slug: "longest-substring-without-repeating-characters",
    hints: [
      "Keep a window of characters with no repeats, and grow its right end one character at a time.",
      "When a repeated character enters the window, move the left end just past that character's previous occurrence.",
      "Store the last index of every character. On a repeat, set the left edge to the larger of its current value and last index + 1, then update the best length.",
    ],
    insight: "A sliding window plus a map of last positions lets the left edge jump instead of creeping.",
    complexity: { time: "O(n)", space: "O(k), where k is the alphabet size" },
    pitfalls: [
      "Moving the left edge backwards. Always take the maximum (try \"abba\").",
      "Forgetting the empty string, whose answer is 0.",
    ],
  },
  {
    slug: "kth-largest-element-in-an-array",
    hints: [
      "Sorting works in O(n log n). Can you keep only the k largest numbers seen so far?",
      "In a min-heap of size k, the smallest element is exactly the kth largest of everything seen.",
      "Push each number into the heap and pop the smallest whenever the heap grows past k. The top of the heap is the answer.",
    ],
    insight: "A bounded min-heap keeps the top k items, so each step costs O(log k).",
    complexity: { time: "O(n log k)", space: "O(k)" },
    pitfalls: ["Python's heapq is a min-heap: don't expect heap[0] to be the largest.", "Counting distinct values instead of positions."],
  },
  {
    slug: "top-k-frequent-elements",
    hints: [
      "Start by counting how often each value appears.",
      "Now you need the k values with the largest counts: a heap of size k, or buckets indexed by frequency.",
      "Bucket idea: make a list of buckets where bucket f holds the values that appear f times, then collect values from the highest bucket down until you have k.",
    ],
    insight: "Counting plus bucket sort avoids a full sort, because frequencies are at most n.",
    complexity: { time: "O(n)", space: "O(n)", note: "O(n log k) with a heap is also fine." },
    pitfalls: ["Returning the counts instead of the values.", "Sorting the whole array rather than the counts."],
  },
  {
    slug: "merge-intervals",
    hints: [
      "If you sort the intervals by start, overlapping ones end up next to each other.",
      "Compare each interval only with the last interval in your merged result.",
      "They overlap if the new start is ≤ the last end: extend the last end to the larger of the two ends. Otherwise append the new interval.",
    ],
    insight: "After sorting by start, one linear pass merges everything.",
    complexity: { time: "O(n log n)", space: "O(n)" },
    pitfalls: [
      "Touching intervals like [1, 4] and [4, 5] count as overlapping here.",
      "Replacing the end instead of taking the maximum. It breaks when one interval contains another.",
    ],
  },
  {
    slug: "trapping-rain-water",
    hints: [
      "Water above bar i equals min(tallest bar on its left, tallest bar on its right) − height[i], when that's positive.",
      "Precomputing left-max and right-max arrays gives an O(n) time, O(n) space solution.",
      "For O(1) space, use two pointers: whichever side has the smaller max so far is limited by that max, so you can settle its water and move that pointer inward.",
    ],
    insight: "Each bar's water depends only on the shorter of the two tallest walls around it.",
    complexity: { time: "O(n)", space: "O(1) with two pointers" },
    pitfalls: ["Adding negative water when a bar is taller than its walls.", "Recomputing maxima for every bar, which is O(n²)."],
  },
  {
    slug: "subarray-sum-equals-k",
    hints: [
      "The sum of nums[i..j] equals prefix[j] − prefix[i − 1], where prefix[x] is the running total up to x.",
      "For each running total p, the number of subarrays ending here with sum k equals how many earlier running totals equal p − k.",
      "Keep a dictionary from running total to how many times you've seen it, starting with {0: 1}, and add the matching count at every step.",
    ],
    insight: "Prefix sums turn \"subarray sum\" into \"pair of prefixes\", and a hash map counts pairs in one pass.",
    complexity: { time: "O(n)", space: "O(n)" },
    pitfalls: [
      "Forgetting the initial {0: 1}, which misses subarrays that start at index 0.",
      "Trying a sliding window: with negative numbers the window can't know when to shrink.",
    ],
  },
  {
    slug: "find-all-numbers-disappeared-in-an-array",
    hints: [
      "Values are between 1 and n, so each value can point to an index of the array itself.",
      "Use the array as your notebook: for every value v, mark position v − 1 as \"seen\" (for example by making it negative).",
      "After marking, every index that is still unmarked (positive) tells you that index + 1 never appeared.",
    ],
    insight: "When values map onto indices, the input array can store the \"seen\" flags, so no extra set is needed.",
    complexity: { time: "O(n)", space: "O(1) extra (the output doesn't count)" },
    pitfalls: ["Reading an already-negated value: use its absolute value to find the index."],
  },
  {
    slug: "spiral-matrix",
    hints: [
      "Keep four boundaries: top row, bottom row, left column, right column.",
      "Walk the top row left to right, then the right column downward, then the bottom row right to left, then the left column upward, shrinking the matching boundary after each walk.",
      "Before walking the bottom row and the left column, check that the boundaries haven't crossed. Single rows and columns are where this goes wrong.",
    ],
    insight: "Simulate layer by layer with shrinking boundaries, and check them between each side.",
    complexity: { time: "O(m·n)", space: "O(1) extra" },
    pitfalls: ["Visiting the middle row or column twice in non-square matrices."],
  },
  {
    slug: "search-in-rotated-sorted-array",
    hints: [
      "If you split the array at mid, at least one half is still properly sorted.",
      "Compare nums[lo] with nums[mid] to find out which half is sorted.",
      "If the target lies within the sorted half's range, search that half. Otherwise search the other half. Repeat like a normal binary search.",
    ],
    insight: "Binary search still works because one side of every split is sorted and easy to reason about.",
    complexity: { time: "O(log n)", space: "O(1)" },
    pitfalls: ["Using < instead of ≤ when lo == mid (two-element ranges).", "A linear scan passes small tests but ignores the O(log n) goal."],
  },
  {
    slug: "reverse-linked-list",
    hints: [
      "Every node's next pointer needs to point to the node before it.",
      "Walk the list with two references, prev and curr, and remember curr.next before you change it.",
      "Rewire curr.next to prev, then move both references forward. When curr runs out, prev is the new head.",
    ],
    insight: "Reversal is three pointer moves per node: save next, rewire, advance.",
    complexity: { time: "O(n)", space: "O(1) iterative, O(n) recursive" },
    pitfalls: ["Losing the rest of the list by overwriting next before saving it.", "Returning the old head instead of prev."],
  },
  {
    slug: "daily-temperatures",
    hints: [
      "The direct way looks ahead from every day, which is O(n²). Can each day be resolved only once?",
      "Keep a stack of the days still waiting for a warmer temperature. Their temperatures are non-increasing from bottom to top.",
      "When today is warmer than the day on top of the stack, pop it and record the gap (today − that day). Repeat, then push today.",
    ],
    insight: "A monotonic stack answers \"next greater element\" for every position in one pass.",
    complexity: { time: "O(n)", space: "O(n)" },
    pitfalls: ["Storing temperatures instead of indices, so the distance is lost.", "Treating an equal temperature as warmer."],
  },
  {
    slug: "find-the-duplicate-number",
    hints: [
      "Treat the array as a function i → nums[i]. Starting from index 0 and following it, a repeated value means two indices lead to the same place.",
      "Two arrows into one node create a cycle, and the duplicate is where the cycle begins. Floyd's tortoise and hare finds cycles in O(1) space.",
      "Move slow one step and fast two steps until they meet. Then restart one pointer from the beginning and move both one step at a time: they meet at the cycle entrance.",
    ],
    insight: "The array is secretly a linked list with a cycle, and cycle detection finds the duplicate.",
    complexity: { time: "O(n)", space: "O(1)" },
    pitfalls: ["A set works but uses O(n) space.", "Sorting or marking changes the array, which the problem forbids."],
  },
  {
    slug: "maximum-depth-of-binary-tree",
    hints: [
      "The depth of a tree is 1 plus the depth of its deeper subtree.",
      "What is the depth of an empty tree? That's your base case.",
      "Recurse on the left and right children and combine the results, or do a level-by-level BFS and count the levels.",
    ],
    insight: "Tree answers usually come from combining the answers of the two subtrees.",
    complexity: { time: "O(n)", space: "O(h), the height of the tree" },
    pitfalls: ["Reading .left or .right of None without a base case."],
  },
  {
    slug: "binary-tree-level-order-traversal",
    hints: [
      "A queue visits nodes in the order they were discovered, which is level by level.",
      "At the start of each level, the queue's length is exactly the number of nodes in that level.",
      "Pop that many nodes, collect their values into one list, and push their children for the next level.",
    ],
    insight: "BFS with a per-level count groups nodes by depth.",
    complexity: { time: "O(n)", space: "O(n)" },
    pitfalls: ["Returning [[]] instead of [] for an empty tree.", "Pushing None children into the queue."],
  },
  {
    slug: "subsets",
    hints: [
      "Every element is either in a subset or not, so there are 2ⁿ subsets.",
      "Backtracking: at index i, try the branch that includes nums[i] and the branch that skips it.",
      "Or build it up: start with the empty subset, and for each number add a copy of every existing subset with that number appended.",
    ],
    insight: "Subsets are the leaves of an include/skip decision tree.",
    complexity: { time: "O(n·2ⁿ)", space: "O(n) recursion depth, plus the output" },
    pitfalls: ["Appending the same list object and mutating it later: save a copy."],
  },
  {
    slug: "replace-words",
    hints: [
      "For each word, you need the shortest root that is a prefix of it.",
      "A trie built from the roots lets you walk a word one character at a time and stop at the first place where a root ends.",
      "Insert every root into the trie with an end marker. For each word, walk until you hit an end marker (replace the word with that prefix) or fall off the trie (keep the word).",
    ],
    insight: "A trie shares common prefixes, so each word costs only its own length to check.",
    complexity: { time: "O(total characters)", space: "O(total root characters)" },
    pitfalls: ["Choosing the longest matching root instead of the shortest.", "Checking every root against every word, which is slow."],
  },
  {
    slug: "number-of-islands",
    hints: [
      "Every land cell you haven't visited yet starts a new island.",
      "From that cell, flood-fill (DFS or BFS) through neighbouring land, up, down, left and right, marking cells as visited.",
      "The answer is the number of flood fills you had to start.",
    ],
    insight: "Counting connected components is counting how many traversals you start.",
    complexity: { time: "O(m·n)", space: "O(m·n) worst case for the visited set or stack" },
    pitfalls: [
      "The grid holds strings \"1\" and \"0\", not integers.",
      "Not marking visited cells causes infinite loops.",
      "Deep recursion on big grids: an explicit stack avoids hitting Python's recursion limit.",
    ],
  },
  {
    slug: "climbing-stairs",
    hints: [
      "Think about your last move: it was either 1 step or 2 steps.",
      "So the ways to reach step n = the ways to reach n − 1 + the ways to reach n − 2.",
      "Compute it bottom-up, keeping just the previous two values. It's the Fibonacci sequence in disguise.",
    ],
    insight: "Splitting on the last choice gives a recurrence, and remembering results avoids repeated work.",
    complexity: { time: "O(n)", space: "O(1)" },
    pitfalls: ["Plain recursion without memoization is exponential and exceeds the time limit around n = 35."],
  },
  {
    slug: "kth-smallest-element-in-a-sorted-matrix",
    hints: [
      "Each row is sorted, so this is really \"merge n sorted lists and take the kth element\".",
      "Keep a min-heap holding the smallest unused element from each row.",
      "Pop k times. When you pop the element at (row, col), push (row, col + 1) if it exists. The kth pop is the answer.",
    ],
    insight: "K-way merge with a heap only ever looks at the frontier of each list.",
    complexity: { time: "O(k log n)", space: "O(n)", note: "Binary search on the value range is another O(n log(range)) option." },
    pitfalls: ["Flattening and sorting works but costs O(n² log n)."],
  },
  {
    slug: "ipo",
    hints: [
      "At any moment you may only start projects whose capital requirement is ≤ your current capital. Among those, which one should you pick?",
      "Sort projects by required capital, and move each project into a max-heap by profit as soon as you can afford it.",
      "Repeat k times: push every newly affordable project, pop the most profitable, and add its profit to your capital. Stop early if nothing is affordable.",
    ],
    insight: "Two heaps (or one sorted list plus one heap) separate \"can't afford yet\" from \"affordable, pick the best\".",
    complexity: { time: "O(n log n + k log n)", space: "O(n)" },
    pitfalls: ["Python's heapq is a min-heap: store negative profits.", "Re-scanning every project each round is O(k·n)."],
  },
  {
    slug: "single-number",
    hints: [
      "What is x XOR x? And x XOR 0?",
      "XOR is commutative and associative, so the order of operations doesn't matter.",
      "XOR every number together: each pair cancels to 0, leaving the single number.",
    ],
    insight: "XOR cancels pairs, giving O(1) extra space.",
    complexity: { time: "O(n)", space: "O(1)" },
    pitfalls: ["Using a dictionary works but uses O(n) space."],
  },
  {
    slug: "longest-common-subsequence",
    hints: [
      "Compare the last characters of both strings. If they match, they can end the common subsequence.",
      "If they match, the answer is 1 + the LCS of both strings without that character. If not, it's the better of dropping the last character from one string or the other.",
      "Fill a (len1 + 1) × (len2 + 1) table from the smallest prefixes up. Only the previous row is needed at any time.",
    ],
    insight: "Two strings means a 2-D table of prefix pairs, and each cell depends on three neighbours.",
    complexity: { time: "O(m·n)", space: "O(n) with a rolling row" },
    pitfalls: ["Confusing subsequence (gaps allowed) with substring (contiguous)."],
  },
  {
    slug: "redundant-connection",
    hints: [
      "Add the edges one by one. The first edge that joins two nodes which are already connected is what creates the cycle.",
      "Union-Find tracks which component each node belongs to, with near-constant-time checks.",
      "For each edge, if both ends already have the same root, that edge is your answer. Otherwise union their components.",
    ],
    insight: "Cycle detection in an undirected graph is \"are these already connected?\", which is exactly what Union-Find answers.",
    complexity: { time: "O(n · α(n)) ≈ O(n)", space: "O(n)" },
    pitfalls: ["Nodes are labelled from 1, so size the parent array n + 1.", "Without path compression, find can get slow."],
  },
  {
    slug: "course-schedule",
    hints: [
      "Finishing every course is impossible exactly when the prerequisites contain a cycle.",
      "Kahn's algorithm: start with the courses that have no prerequisites (in-degree 0).",
      "Take such a course, reduce the in-degree of the courses that depend on it, and queue any that drop to 0. If you process all courses, there's no cycle.",
    ],
    insight: "A topological order exists if and only if the directed graph has no cycle.",
    complexity: { time: "O(V + E)", space: "O(V + E)" },
    pitfalls: ["Reversing the edge direction: [a, b] means b comes before a."],
  },
  {
    slug: "network-delay-time",
    hints: [
      "The time for everyone to hear the signal is the time taken to reach the farthest node by its shortest path.",
      "Edges have non-negative weights, so Dijkstra's algorithm with a min-heap finds the shortest times.",
      "Pop the closest unvisited node, record its time, and push its neighbours with the updated times. At the end, the answer is the largest time if every node was reached, otherwise −1.",
    ],
    insight: "Shortest paths from one source to all nodes: Dijkstra, then take the maximum.",
    complexity: { time: "O(E log V)", space: "O(V + E)" },
    pitfalls: ["Plain BFS ignores edge weights.", "Not skipping nodes that were already finalized."],
  },
  {
    slug: "happy-number",
    hints: [
      "Repeatedly replacing n with the sum of the squares of its digits either reaches 1 or repeats forever.",
      "So you only need to detect a repeat: a set of seen values works, and so does Floyd's fast and slow pointers.",
      "Keep computing the next value until it's 1 (happy) or a value you've seen before (not happy).",
    ],
    insight: "Any sequence that must end or cycle can be solved with cycle detection.",
    complexity: { time: "O(log n) per step, with few steps", space: "O(1) with fast and slow pointers" },
    pitfalls: ["Looping forever without checking for a repeat."],
  },
];

export const errorGuides: ErrorGuide[] = [
  {
    id: "index-error",
    title: "IndexError: list index out of range",
    match: ["indexerror", "index out of range"],
    body: "You read a position that doesn't exist, often an off-by-one error. Check loop bounds (range(len(x)) stops at len − 1), access to i + 1 on the last item, and empty inputs. Print the index and len(...) right before the failing line.",
  },
  {
    id: "key-error",
    title: "KeyError",
    match: ["keyerror"],
    body: "A dictionary lookup used a key that isn't there. Check with `key in d` first, use d.get(key, default), or use collections.defaultdict for counters.",
  },
  {
    id: "none-type",
    title: "'NoneType' object has no attribute / is not subscriptable",
    match: ["nonetype", "none"],
    body: "Something you expected to be a value is None. Common causes: a helper function without a return statement, or reading .val / .next / .left on a missing node. Check for None before using a node, and make sure every code path returns.",
  },
  {
    id: "recursion-error",
    title: "RecursionError: maximum recursion depth exceeded",
    match: ["recursionerror", "maximum recursion depth"],
    body: "Your recursion never reaches a base case, or the input is deeper than Python's limit of about 1000. Check the base case first. For deep inputs (long lists, big grids) switch to an explicit stack or a loop.",
  },
  {
    id: "type-error",
    title: "TypeError",
    match: ["typeerror"],
    body: "An operation got the wrong kind of value: adding str and int, calling len() on a number, or using a list as a dictionary key (lists are unhashable, so convert to a tuple). Read the last line of the traceback; it names both types.",
  },
  {
    id: "name-error",
    title: "NameError: name is not defined",
    match: ["nameerror"],
    body: "A variable or function is used before it's defined, or there's a typo. Inside a class method, call other methods as self.method(...). ListNode, TreeNode, Optional and List are already provided by the judge.",
  },
  {
    id: "attribute-error",
    title: "AttributeError",
    match: ["attributeerror"],
    body: "The object doesn't have the attribute or method you used. If the message mentions class Solution, your method name must match the one in the starter code exactly. On None, see the NoneType guide.",
  },
  {
    id: "zero-division",
    title: "ZeroDivisionError",
    match: ["zerodivisionerror"],
    body: "You divided or took a modulo by zero. Guard the divisor, or handle the empty or zero case before the division.",
  },
  {
    id: "syntax-error",
    title: "SyntaxError / IndentationError",
    match: ["syntaxerror", "indentationerror"],
    body: "Python couldn't parse your code. Look at the line shown and the line before it: a missing colon after if/for/def, unbalanced brackets, or mixed tabs and spaces. The editor uses 4 spaces per level.",
  },
  {
    id: "time-limit",
    title: "Time Limit Exceeded",
    match: ["time limit exceeded", "timeout", "took too long"],
    body: "Your code is either stuck in a loop or too slow for the input size. First check that every while loop moves toward its exit (pointers advance, the queue shrinks). Then compare your complexity with the target: with n = 10⁵, an O(n²) nested loop is about 10¹⁰ steps, far too many. Look for a hash map, two pointers, a heap, or sorting to remove the inner loop.",
  },
  {
    id: "wrong-answer",
    title: "Wrong Answer",
    match: ["wrong answer"],
    body: "Your code ran, but the output differs. Compare your output with the expected output on the failing input, then test edge cases by hand: empty or single-element input, duplicates, negative numbers, all equal values, and the largest or smallest answer. Make sure you return the right thing (indices vs values, a count vs a list) and don't print the answer instead of returning it.",
  },
  {
    id: "returns-none",
    title: "Your output is None",
    match: ["output: none", "returned none"],
    body: "The method finished without returning. Replace `pass` with your logic and make sure every branch ends with a `return`. print() shows output in the console but doesn't return a value.",
  },
];

export const patternNotes: PatternNote[] = [
  { patternId: "arrays-hashing", howTo: "Scan once and keep what you've seen in a dict or set: counts, first index, or complements. Ask: what do I need to remember about the past to answer now?", pitfalls: "Nested loops where a lookup would do; mutating a dict while iterating it." },
  { patternId: "prefix-sum", howTo: "Build running totals so any range sum is prefix[r] − prefix[l − 1]. Combine with a hash map of earlier prefixes to count subarrays with a target sum.", pitfalls: "Off-by-one on the prefix index; forgetting the empty prefix (sum 0)." },
  { patternId: "cyclic-sort", howTo: "When values are 1..n, value v belongs at index v − 1. Swap elements into place, or mark indices, then scan for positions that don't match.", pitfalls: "Infinite swapping when the target slot already holds the same value." },
  { patternId: "two-pointers", howTo: "Place pointers at both ends (or both at the start) and move the one whose side can't produce a better answer. Works best on sorted data or symmetric problems.", pitfalls: "Moving the wrong pointer; forgetting to sort first when the logic needs order." },
  { patternId: "stack", howTo: "Push work you can't finish yet; pop when the current item resolves the most recent unfinished one. Great for brackets, undo, and nested structure.", pitfalls: "Popping an empty stack; not checking that the stack is empty at the end." },
  { patternId: "matrix", howTo: "Track boundaries or directions explicitly (top, bottom, left, right, or dr/dc arrays), and keep row and column indices clearly separated.", pitfalls: "Swapping rows and columns; visiting cells twice in non-square grids." },
  { patternId: "intervals", howTo: "Sort by start, then compare each interval with the last kept one. Overlap means start ≤ last end.", pitfalls: "Replacing the end instead of taking the max; forgetting whether touching counts as overlapping." },
  { patternId: "sliding-window", howTo: "Expand the right edge every step and shrink the left edge while the window breaks the rule, updating the answer when it's valid. A dict or counter tracks the window's contents.", pitfalls: "Using it when negative numbers break monotonicity; moving the left edge backwards." },
  { patternId: "binary-search", howTo: "Maintain a range [lo, hi] that always contains the answer, and halve it by testing mid. You can binary search on an answer value, not just on an array.", pitfalls: "Infinite loops from mid rounding; mixing < and ≤ in the loop condition." },
  { patternId: "linked-list", howTo: "Draw the pointers. Use a dummy head to avoid special cases, and always save next before rewiring.", pitfalls: "Losing the rest of the list; returning the wrong head." },
  { patternId: "monotonic-stack", howTo: "Keep indices in a stack whose values stay increasing or decreasing. When a new value breaks the order, pop and resolve those elements: that's their next greater (or smaller) element.", pitfalls: "Storing values instead of indices; deciding whether equal values pop." },
  { patternId: "greedy", howTo: "Find a local rule (take the best available, or restart when the running total hurts) and convince yourself with an exchange argument that it never loses.", pitfalls: "Greedy rules that look right but fail a counterexample; try small cases by hand." },
  { patternId: "tree-dfs", howTo: "Write the answer for a node in terms of its children's answers, with an empty-tree base case. Return values up, or pass state down as parameters.", pitfalls: "Missing the None base case; very deep trees hitting the recursion limit." },
  { patternId: "tree-bfs", howTo: "Use a queue; process one level at a time by reading the queue's length before the loop.", pitfalls: "Adding None children; mixing levels together." },
  { patternId: "fast-slow-pointers", howTo: "Move one pointer twice as fast as the other. They meet inside a cycle, and a restart from the head finds the cycle's start. The fast pointer also finds the middle.", pitfalls: "Checking fast and fast.next for None in the right order." },
  { patternId: "backtracking", howTo: "Build a candidate step by step: choose, recurse, un-choose. Save a copy of the candidate when it's complete, and prune branches that can't work.", pitfalls: "Saving a reference to a list you keep mutating; forgetting to undo the choice." },
  { patternId: "tries", howTo: "Store words character by character in nested maps, with an end-of-word marker. Walking a word costs its length, however many words are stored.", pitfalls: "Forgetting the end marker, so prefixes and words get confused." },
  { patternId: "heap", howTo: "A heap gives the minimum in O(1) and push or pop in O(log n). Keep a heap of size k for top-k problems; negate values in Python for a max-heap.", pitfalls: "Expecting heapq to be a max-heap; sorting everything when k is small." },
  { patternId: "dp-1d", howTo: "Define dp[i] clearly in words, write how it depends on smaller i, set base cases, and fill in order. Often only the last one or two values are needed.", pitfalls: "Recursion without memoization (exponential time); wrong base cases." },
  { patternId: "graphs", howTo: "Build an adjacency list (or treat the grid as a graph), then BFS or DFS with a visited set. Count components by counting how many traversals you start.", pitfalls: "Revisiting nodes without a visited set; recursion depth on large grids." },
  { patternId: "two-heaps", howTo: "Split data into two heaps: a max-heap for the lower half and a min-heap for the upper half (or \"not yet available\" vs \"available\"). Rebalance after each change.", pitfalls: "Letting the heaps' sizes drift by more than one; forgetting to negate for a max-heap." },
  { patternId: "k-way-merge", howTo: "Put the first element of each sorted list into a min-heap along with its list and position. Pop the smallest, then push the next element from the same list.", pitfalls: "Pushing the whole input at once, which loses the benefit." },
  { patternId: "bit-manipulation", howTo: "Remember the identities: x ^ x = 0, x ^ 0 = x, x & (x − 1) clears the lowest set bit, and 1 << i isolates bit i.", pitfalls: "Python integers are unbounded: negative numbers behave differently than in 32-bit languages." },
  { patternId: "dp-2d", howTo: "Index states by two things (two positions, or a position and a capacity), write the transition from neighbouring cells, and fill the table in an order where dependencies come first.", pitfalls: "Off-by-one with the extra empty row and column; wrong fill order." },
  { patternId: "union-find", howTo: "Keep a parent array; find follows parents to the root (with path compression) and union links two roots. Same root means already connected.", pitfalls: "Forgetting path compression; 1-based labels." },
  { patternId: "topological-sort", howTo: "Count in-degrees, start from every node with in-degree 0, and remove nodes one by one, decrementing their neighbours. If some nodes never reach in-degree 0, there's a cycle.", pitfalls: "Edge direction mistakes; forgetting nodes with no edges." },
  { patternId: "advanced-graphs", howTo: "For weighted shortest paths with non-negative weights use Dijkstra (a min-heap of distance and node). For a minimum spanning tree use Prim or Kruskal with Union-Find.", pitfalls: "Using BFS on weighted edges; not skipping already-finalized nodes." },
  { patternId: "knowing-what-to-track", howTo: "Decide what single fact answers the question (a count per character, the first index of each value, a running balance) and update it in one pass. Compare or look up those facts instead of rescanning.", pitfalls: "Tracking more than you need; forgetting to decrement counts when something leaves a window." },
  { patternId: "sort-and-search", howTo: "Sort first, then exploit the order: binary search for thresholds, two pointers for pairs, or a greedy sweep. Sorting is fine whenever the answer doesn't depend on the original positions.", pitfalls: "Sorting when the problem needs original indices (keep (value, index) pairs instead)." },
  { patternId: "custom-data-structures", howTo: "List the operations and their target costs, then combine structures so each one is fast: a hash map for lookups, a linked list or deque for order, a heap for min or max, an extra stack for running minimums.", pitfalls: "Keeping two structures out of sync after an update or delete." },
  { patternId: "subsets", howTo: "Start from an empty result and extend every partial answer with the next element (or each unused element for permutations). For duplicates, sort first and skip equal choices at the same level.", pitfalls: "Saving references to lists you keep mutating; generating duplicate results when the input has repeated values." },
  { patternId: "math-geometry", howTo: "Look for a mathematical property first: digit sums, modular arithmetic, symmetry, or a cycle in a sequence of states. Simulate carefully once you know what to watch for.", pitfalls: "Infinite loops in simulations; overflow is rare in Python, but precision issues with floats aren't." },
];
