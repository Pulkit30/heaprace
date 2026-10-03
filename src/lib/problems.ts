// Source of truth for problem content. `npm run db:seed` loads it into the database, which the app reads from.
// Keep this file free of runtime imports so the scripts can load it directly with Node.

export type Difficulty = "Easy" | "Medium" | "Hard";

/** How a returned value is compared with the expected one. */
export type CompareMode =
  | "exact" // deep equality
  | "unordered" // top-level list order doesn't matter
  | "unordered-deep" // order doesn't matter at either level (list of lists)
  | "approx"; // deep equality, numbers within 1e-5 (decimal answers)

export interface TestCase {
  /** Positional arguments passed to the solution method, as JSON values. */
  args: unknown[];
  expected: unknown;
  /** Sample tests are shown to the user and used by "Run". Hidden tests only run on "Submit". */
  sample?: boolean;
}

/**
 * Data structures the judge converts. Arguments: a list becomes a linked list ("ListNode"), a level-order list
 * becomes a tree ("TreeNode"), [values, pos] becomes a linked list whose tail links back to node pos ("CycleList").
 * Returns: "ListNode"/"TreeNode" convert back to lists; "NodeIndex" reports a returned node's position in the input.
 */
export type NodeType = "ListNode" | "TreeNode" | "CycleList" | "NodeIndex" | "ListNodeArray" | "TreeNodeArray";

export interface Example {
  input: string;
  output: string;
  explanation?: string;
}

export interface Problem {
  id: number;
  slug: string;
  title: string;
  difficulty: Difficulty;
  tags: string[];
  /** Light markdown: paragraphs separated by blank lines, `code` and **bold**. */
  description: string;
  examples: Example[];
  constraints: string[];
  /** Method name on class Solution that the judge calls. */
  functionName: string;
  /** Names of the arguments, used to label test inputs in the console. */
  params: string[];
  starterCode: string;
  compare: CompareMode;
  /** Per argument: build this node type from the JSON value, or null to pass it as is. */
  argTypes?: (NodeType | null)[];
  /** Convert a returned node back to a list before comparing. */
  returnType?: NodeType;
  /** In-place problems: judge this (modified) argument instead of the return value. */
  outArg?: number;
  /**
   * Design problems: functionName is a class; each test's args are [operations, arguments] and the expected
   * value lists every call's return (null for the constructor), LeetCode-style.
   */
  design?: boolean;
  /** Roadmap pattern id (see roadmap.ts). */
  pattern: string;
  tests: TestCase[];
}

export const problems: Problem[] = [
  {
    id: 1,
    slug: "two-sum",
    title: "Two Sum",
    difficulty: "Easy",
    pattern: "arrays-hashing",
    tags: ["Array", "Hash Table"],
    description: `Given an array of integers \`nums\` and an integer \`target\`, return the **indices** of the two numbers that add up to \`target\`.

Each input has exactly one valid answer, and you may not use the same element twice. You can return the two indices in any order.`,
    examples: [
      { input: "nums = [2, 7, 11, 15], target = 9", output: "[0, 1]", explanation: "nums[0] + nums[1] = 2 + 7 = 9" },
      { input: "nums = [3, 2, 4], target = 6", output: "[1, 2]" },
    ],
    constraints: ["2 ≤ len(nums) ≤ 10⁴", "-10⁹ ≤ nums[i], target ≤ 10⁹", "Exactly one valid answer exists"],
    functionName: "twoSum",
    params: ["nums", "target"],
    starterCode: `class Solution:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        pass
`,
    compare: "unordered",
    tests: [
      { args: [[2, 7, 11, 15], 9], expected: [0, 1], sample: true },
      { args: [[3, 2, 4], 6], expected: [1, 2], sample: true },
      { args: [[3, 3], 6], expected: [0, 1], sample: true },
      { args: [[-1, -2, -3, -4, -5], -8], expected: [2, 4] },
      { args: [[0, 4, 3, 0], 0], expected: [0, 3] },
      { args: [[1, 5, 9, 13, 21, 34], 55], expected: [4, 5] },
      { args: [[1000000000, -999999993, 5], 7], expected: [0, 1] },
    ],
  },
  {
    id: 2,
    slug: "valid-parentheses",
    title: "Valid Parentheses",
    difficulty: "Easy",
    pattern: "stack",
    tags: ["String", "Stack"],
    description: `Given a string \`s\` made only of the characters \`()[]{}\`, decide whether it is **valid**.

A string is valid when every opening bracket is closed by the same type of bracket, and brackets are closed in the correct order.`,
    examples: [
      { input: 's = "()[]{}"', output: "True" },
      { input: 's = "(]"', output: "False" },
      { input: 's = "([{}])"', output: "True" },
    ],
    constraints: ["1 ≤ len(s) ≤ 10⁴", "s contains only ()[]{}"],
    functionName: "isValid",
    params: ["s"],
    starterCode: `class Solution:
    def isValid(self, s: str) -> bool:
        pass
`,
    compare: "exact",
    tests: [
      { args: ["()[]{}"], expected: true, sample: true },
      { args: ["(]"], expected: false, sample: true },
      { args: ["([{}])"], expected: true, sample: true },
      { args: ["("], expected: false },
      { args: [")("], expected: false },
      { args: ["([)]"], expected: false },
      { args: ["{[]}(())"], expected: true },
      { args: ["(((((((((())))))))))"], expected: true },
      { args: ["]"], expected: false },
    ],
  },
  {
    id: 3,
    slug: "best-time-to-buy-and-sell-stock",
    title: "Best Time to Buy and Sell Stock",
    difficulty: "Easy",
    pattern: "sliding-window",
    tags: ["Array", "Greedy"],
    description: `You are given \`prices\`, where \`prices[i]\` is a stock's price on day \`i\`.

Choose one day to buy and a **later** day to sell. Return the maximum profit you can make. If no profit is possible, return \`0\`.`,
    examples: [
      { input: "prices = [7, 1, 5, 3, 6, 4]", output: "5", explanation: "Buy on day 1 (price 1), sell on day 4 (price 6)." },
      { input: "prices = [7, 6, 4, 3, 1]", output: "0", explanation: "Prices only fall, so don't trade." },
    ],
    constraints: ["1 ≤ len(prices) ≤ 10⁵", "0 ≤ prices[i] ≤ 10⁴"],
    functionName: "maxProfit",
    params: ["prices"],
    starterCode: `class Solution:
    def maxProfit(self, prices: list[int]) -> int:
        pass
`,
    compare: "exact",
    tests: [
      { args: [[7, 1, 5, 3, 6, 4]], expected: 5, sample: true },
      { args: [[7, 6, 4, 3, 1]], expected: 0, sample: true },
      { args: [[5]], expected: 0 },
      { args: [[1, 2]], expected: 1 },
      { args: [[2, 4, 1, 7]], expected: 6 },
      { args: [[3, 3, 3, 3]], expected: 0 },
      { args: [[9, 2, 8, 1, 5]], expected: 6 },
    ],
  },
  {
    id: 4,
    slug: "contains-duplicate",
    title: "Contains Duplicate",
    difficulty: "Easy",
    pattern: "arrays-hashing",
    tags: ["Array", "Hash Table"],
    description: `Given an integer array \`nums\`, return \`True\` if any value appears **at least twice**, and \`False\` if every element is distinct.`,
    examples: [
      { input: "nums = [1, 2, 3, 1]", output: "True" },
      { input: "nums = [1, 2, 3, 4]", output: "False" },
    ],
    constraints: ["1 ≤ len(nums) ≤ 10⁵", "-10⁹ ≤ nums[i] ≤ 10⁹"],
    functionName: "containsDuplicate",
    params: ["nums"],
    starterCode: `class Solution:
    def containsDuplicate(self, nums: list[int]) -> bool:
        pass
`,
    compare: "exact",
    tests: [
      { args: [[1, 2, 3, 1]], expected: true, sample: true },
      { args: [[1, 2, 3, 4]], expected: false, sample: true },
      { args: [[1]], expected: false },
      { args: [[0, 0]], expected: true },
      { args: [[-5, 3, 8, -5]], expected: true },
      { args: [[10, 20, 30, 40, 50, 60]], expected: false },
    ],
  },
  {
    id: 5,
    slug: "maximum-subarray",
    title: "Maximum Subarray",
    difficulty: "Medium",
    pattern: "greedy",
    tags: ["Array", "Dynamic Programming"],
    description: `Given an integer array \`nums\`, find the contiguous, non-empty subarray with the largest sum and return **that sum**.`,
    examples: [
      { input: "nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]", output: "6", explanation: "The subarray [4, -1, 2, 1] has sum 6." },
      { input: "nums = [5, 4, -1, 7, 8]", output: "23" },
    ],
    constraints: ["1 ≤ len(nums) ≤ 10⁵", "-10⁴ ≤ nums[i] ≤ 10⁴"],
    functionName: "maxSubArray",
    params: ["nums"],
    starterCode: `class Solution:
    def maxSubArray(self, nums: list[int]) -> int:
        pass
`,
    compare: "exact",
    tests: [
      { args: [[-2, 1, -3, 4, -1, 2, 1, -5, 4]], expected: 6, sample: true },
      { args: [[5, 4, -1, 7, 8]], expected: 23, sample: true },
      { args: [[1]], expected: 1 },
      { args: [[-3, -1, -2]], expected: -1 },
      { args: [[2, -1, 2, -1, 2]], expected: 4 },
      { args: [[-1, 0, -2]], expected: 0 },
    ],
  },
  {
    id: 6,
    slug: "longest-substring-without-repeating-characters",
    title: "Longest Substring Without Repeating Characters",
    difficulty: "Medium",
    pattern: "sliding-window",
    tags: ["String", "Sliding Window", "Hash Table"],
    description: `Given a string \`s\`, return the length of the longest **substring** (contiguous) that contains no repeated characters.`,
    examples: [
      { input: 's = "abcabcbb"', output: "3", explanation: 'The answer is "abc".' },
      { input: 's = "bbbbb"', output: "1" },
      { input: 's = "pwwkew"', output: "3", explanation: '"wke" works. "pwke" is a subsequence, not a substring.' },
    ],
    constraints: ["0 ≤ len(s) ≤ 5 × 10⁴", "s contains letters, digits, symbols and spaces"],
    functionName: "lengthOfLongestSubstring",
    params: ["s"],
    starterCode: `class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        pass
`,
    compare: "exact",
    tests: [
      { args: ["abcabcbb"], expected: 3, sample: true },
      { args: ["bbbbb"], expected: 1, sample: true },
      { args: ["pwwkew"], expected: 3, sample: true },
      { args: [""], expected: 0 },
      { args: [" "], expected: 1 },
      { args: ["dvdf"], expected: 3 },
      { args: ["abba"], expected: 2 },
      { args: ["tmmzuxt"], expected: 5 },
    ],
  },
  {
    id: 7,
    slug: "kth-largest-element-in-an-array",
    title: "Kth Largest Element in an Array",
    difficulty: "Medium",
    pattern: "heap",
    tags: ["Array", "Heap", "Sorting"],
    description: `Given an integer array \`nums\` and an integer \`k\`, return the \`k\`th largest element.

This is the \`k\`th largest in sorted order, not the \`k\`th distinct value. Try solving it without sorting the whole array: a heap of size \`k\` is enough.`,
    examples: [
      { input: "nums = [3, 2, 1, 5, 6, 4], k = 2", output: "5" },
      { input: "nums = [3, 2, 3, 1, 2, 4, 5, 5, 6], k = 4", output: "4" },
    ],
    constraints: ["1 ≤ k ≤ len(nums) ≤ 10⁵", "-10⁴ ≤ nums[i] ≤ 10⁴"],
    functionName: "findKthLargest",
    params: ["nums", "k"],
    starterCode: `import heapq

class Solution:
    def findKthLargest(self, nums: list[int], k: int) -> int:
        pass
`,
    compare: "exact",
    tests: [
      { args: [[3, 2, 1, 5, 6, 4], 2], expected: 5, sample: true },
      { args: [[3, 2, 3, 1, 2, 4, 5, 5, 6], 4], expected: 4, sample: true },
      { args: [[1], 1], expected: 1 },
      { args: [[7, 7, 7, 7], 3], expected: 7 },
      { args: [[-1, -5, -3], 3], expected: -5 },
      { args: [[9, 1, 8, 2, 7, 3], 1], expected: 9 },
    ],
  },
  {
    id: 8,
    slug: "top-k-frequent-elements",
    title: "Top K Frequent Elements",
    difficulty: "Medium",
    pattern: "heap",
    tags: ["Array", "Heap", "Hash Table"],
    description: `Given an integer array \`nums\` and an integer \`k\`, return the \`k\` most frequent elements. You may return them in any order.

The answer is guaranteed to be unique.`,
    examples: [
      { input: "nums = [1, 1, 1, 2, 2, 3], k = 2", output: "[1, 2]" },
      { input: "nums = [1], k = 1", output: "[1]" },
    ],
    constraints: ["1 ≤ len(nums) ≤ 10⁵", "1 ≤ k ≤ number of distinct elements", "The answer is unique"],
    functionName: "topKFrequent",
    params: ["nums", "k"],
    starterCode: `class Solution:
    def topKFrequent(self, nums: list[int], k: int) -> list[int]:
        pass
`,
    compare: "unordered",
    tests: [
      { args: [[1, 1, 1, 2, 2, 3], 2], expected: [1, 2], sample: true },
      { args: [[1], 1], expected: [1], sample: true },
      { args: [[4, 4, 4, 6, 6, 5], 1], expected: [4] },
      { args: [[5, 3, 5, 3, 5, 3, 9], 2], expected: [3, 5] },
      { args: [[-1, -1, 2, 2, 2, 7], 2], expected: [-1, 2] },
    ],
  },
  {
    id: 9,
    slug: "merge-intervals",
    title: "Merge Intervals",
    difficulty: "Medium",
    pattern: "intervals",
    tags: ["Array", "Sorting"],
    description: `Given a list of \`intervals\` where \`intervals[i] = [start, end]\`, merge every group of overlapping intervals and return the result sorted by start.

Intervals that only touch (like \`[1, 4]\` and \`[4, 5]\`) count as overlapping.`,
    examples: [
      { input: "intervals = [[1, 3], [2, 6], [8, 10], [15, 18]]", output: "[[1, 6], [8, 10], [15, 18]]" },
      { input: "intervals = [[1, 4], [4, 5]]", output: "[[1, 5]]" },
    ],
    constraints: ["1 ≤ len(intervals) ≤ 10⁴", "0 ≤ start ≤ end ≤ 10⁴"],
    functionName: "merge",
    params: ["intervals"],
    starterCode: `class Solution:
    def merge(self, intervals: list[list[int]]) -> list[list[int]]:
        pass
`,
    compare: "exact",
    tests: [
      { args: [[[1, 3], [2, 6], [8, 10], [15, 18]]], expected: [[1, 6], [8, 10], [15, 18]], sample: true },
      { args: [[[1, 4], [4, 5]]], expected: [[1, 5]], sample: true },
      { args: [[[5, 7]]], expected: [[5, 7]] },
      { args: [[[8, 9], [1, 2], [3, 5]]], expected: [[1, 2], [3, 5], [8, 9]] },
      { args: [[[1, 10], [2, 3], [4, 5]]], expected: [[1, 10]] },
      { args: [[[2, 3], [1, 2], [6, 8], [5, 6]]], expected: [[1, 3], [5, 8]] },
    ],
  },
  {
    id: 10,
    slug: "trapping-rain-water",
    title: "Trapping Rain Water",
    difficulty: "Hard",
    pattern: "two-pointers",
    tags: ["Array", "Two Pointers", "Stack"],
    description: `You are given \`height\`, a list of non-negative integers describing an elevation map where each bar has width 1.

Return how many units of rain water are trapped between the bars after it rains.`,
    examples: [
      { input: "height = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]", output: "6" },
      { input: "height = [4, 2, 0, 3, 2, 5]", output: "9" },
    ],
    constraints: ["1 ≤ len(height) ≤ 2 × 10⁴", "0 ≤ height[i] ≤ 10⁵"],
    functionName: "trap",
    params: ["height"],
    starterCode: `class Solution:
    def trap(self, height: list[int]) -> int:
        pass
`,
    compare: "exact",
    tests: [
      { args: [[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]], expected: 6, sample: true },
      { args: [[4, 2, 0, 3, 2, 5]], expected: 9, sample: true },
      { args: [[1]], expected: 0 },
      { args: [[3, 0, 3]], expected: 3 },
      { args: [[1, 2, 3, 4, 5]], expected: 0 },
      { args: [[5, 1, 1, 1, 5]], expected: 12 },
      { args: [[2, 0, 1, 0, 3]], expected: 5 },
    ],
  },
  {
    id: 11,
    slug: "subarray-sum-equals-k",
    title: "Subarray Sum Equals K",
    difficulty: "Medium",
    pattern: "prefix-sum",
    tags: ["Array", "Prefix Sum", "Hash Table"],
    description: `Given an integer array \`nums\` and an integer \`k\`, return how many **contiguous subarrays** have a sum equal to \`k\`.

Numbers can be negative, so a sliding window won't work. Track running (prefix) sums instead.`,
    examples: [
      { input: "nums = [1, 1, 1], k = 2", output: "2", explanation: "[1, 1] appears twice." },
      { input: "nums = [1, 2, 3], k = 3", output: "2", explanation: "[1, 2] and [3]." },
    ],
    constraints: ["1 ≤ len(nums) ≤ 2 × 10⁴", "-1000 ≤ nums[i] ≤ 1000", "-10⁷ ≤ k ≤ 10⁷"],
    functionName: "subarraySum",
    params: ["nums", "k"],
    starterCode: `class Solution:
    def subarraySum(self, nums: list[int], k: int) -> int:
        pass
`,
    compare: "exact",
    tests: [
      { args: [[1, 1, 1], 2], expected: 2, sample: true },
      { args: [[1, 2, 3], 3], expected: 2, sample: true },
      { args: [[1], 0], expected: 0 },
      { args: [[1, -1, 0], 0], expected: 3 },
      { args: [[0, 0, 0], 0], expected: 6 },
      { args: [[3, 4, 7, 2, -3, 1, 4, 2], 7], expected: 4 },
      { args: [[-1, -1, 1], 0], expected: 1 },
    ],
  },
  {
    id: 12,
    slug: "find-all-numbers-disappeared-in-an-array",
    title: "Find All Numbers Disappeared in an Array",
    difficulty: "Easy",
    pattern: "cyclic-sort",
    tags: ["Array", "Cyclic Sort"],
    description: `You are given an array \`nums\` of \`n\` integers where each value is in the range \`1\` to \`n\`. Some values appear twice and others are missing.

Return every number in \`1..n\` that does not appear in \`nums\`, in any order. Try to do it with O(1) extra space besides the output.`,
    examples: [
      { input: "nums = [4, 3, 2, 7, 8, 2, 3, 1]", output: "[5, 6]" },
      { input: "nums = [1, 1]", output: "[2]" },
    ],
    constraints: ["1 ≤ n = len(nums) ≤ 10⁵", "1 ≤ nums[i] ≤ n"],
    functionName: "findDisappearedNumbers",
    params: ["nums"],
    starterCode: `class Solution:
    def findDisappearedNumbers(self, nums: list[int]) -> list[int]:
        pass
`,
    compare: "unordered",
    tests: [
      { args: [[4, 3, 2, 7, 8, 2, 3, 1]], expected: [5, 6], sample: true },
      { args: [[1, 1]], expected: [2], sample: true },
      { args: [[1]], expected: [] },
      { args: [[2, 2, 2]], expected: [1, 3] },
      { args: [[5, 4, 3, 2, 1]], expected: [] },
      { args: [[3, 3, 1, 1]], expected: [2, 4] },
    ],
  },
  {
    id: 13,
    slug: "spiral-matrix",
    title: "Spiral Matrix",
    difficulty: "Medium",
    pattern: "matrix",
    tags: ["Array", "Matrix", "Simulation"],
    description: `Given an \`m x n\` matrix, return all of its elements in **spiral order**: start at the top-left, go right along the top row, down the right column, left along the bottom row, up the left column, then repeat on the inner layer.`,
    examples: [
      { input: "matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]", output: "[1, 2, 3, 6, 9, 8, 7, 4, 5]" },
      { input: "matrix = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]", output: "[1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]" },
    ],
    constraints: ["1 ≤ m, n ≤ 10", "-100 ≤ matrix[i][j] ≤ 100"],
    functionName: "spiralOrder",
    params: ["matrix"],
    starterCode: `class Solution:
    def spiralOrder(self, matrix: list[list[int]]) -> list[int]:
        pass
`,
    compare: "exact",
    tests: [
      { args: [[[1, 2, 3], [4, 5, 6], [7, 8, 9]]], expected: [1, 2, 3, 6, 9, 8, 7, 4, 5], sample: true },
      { args: [[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]], expected: [1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7], sample: true },
      { args: [[[7]]], expected: [7] },
      { args: [[[1], [2], [3]]], expected: [1, 2, 3] },
      { args: [[[1, 2], [3, 4]]], expected: [1, 2, 4, 3] },
      { args: [[[1, 2, 3]]], expected: [1, 2, 3] },
    ],
  },
  {
    id: 14,
    slug: "search-in-rotated-sorted-array",
    title: "Search in Rotated Sorted Array",
    difficulty: "Medium",
    pattern: "binary-search",
    tags: ["Array", "Binary Search"],
    description: `An array of **distinct** integers was sorted in ascending order and then rotated at some unknown pivot, so \`[0, 1, 2, 4, 5, 6, 7]\` might become \`[4, 5, 6, 7, 0, 1, 2]\`.

Given the rotated array \`nums\` and a \`target\`, return the index of \`target\`, or \`-1\` if it isn't there. Your solution should run in O(log n).`,
    examples: [
      { input: "nums = [4, 5, 6, 7, 0, 1, 2], target = 0", output: "4" },
      { input: "nums = [4, 5, 6, 7, 0, 1, 2], target = 3", output: "-1" },
    ],
    constraints: ["1 ≤ len(nums) ≤ 5000", "All values are distinct", "-10⁴ ≤ nums[i], target ≤ 10⁴"],
    functionName: "search",
    params: ["nums", "target"],
    starterCode: `class Solution:
    def search(self, nums: list[int], target: int) -> int:
        pass
`,
    compare: "exact",
    tests: [
      { args: [[4, 5, 6, 7, 0, 1, 2], 0], expected: 4, sample: true },
      { args: [[4, 5, 6, 7, 0, 1, 2], 3], expected: -1, sample: true },
      { args: [[1], 0], expected: -1 },
      { args: [[1], 1], expected: 0 },
      { args: [[5, 1, 3], 5], expected: 0 },
      { args: [[3, 1], 1], expected: 1 },
      { args: [[6, 7, 1, 2, 3, 4, 5], 6], expected: 0 },
      { args: [[1, 3, 5], 5], expected: 2 },
    ],
  },
  {
    id: 15,
    slug: "reverse-linked-list",
    title: "Reverse Linked List",
    difficulty: "Easy",
    pattern: "linked-list",
    tags: ["Linked List"],
    description: `Given the \`head\` of a singly linked list, reverse the list and return the new head.

In the tests, a linked list is written as a list of its values, so \`[1, 2, 3]\` means \`1 → 2 → 3\`. The judge builds the \`ListNode\` objects for you.`,
    examples: [
      { input: "head = [1, 2, 3, 4, 5]", output: "[5, 4, 3, 2, 1]" },
      { input: "head = []", output: "[]" },
    ],
    constraints: ["0 ≤ number of nodes ≤ 5000", "-5000 ≤ Node.val ≤ 5000"],
    functionName: "reverseList",
    params: ["head"],
    starterCode: `# ListNode is provided by the judge:
# class ListNode:
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next

class Solution:
    def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        pass
`,
    compare: "exact",
    argTypes: ["ListNode"],
    returnType: "ListNode",
    tests: [
      { args: [[1, 2, 3, 4, 5]], expected: [5, 4, 3, 2, 1], sample: true },
      { args: [[1, 2]], expected: [2, 1], sample: true },
      { args: [[]], expected: [] },
      { args: [[7]], expected: [7] },
      { args: [[3, 3, 1]], expected: [1, 3, 3] },
    ],
  },
  {
    id: 16,
    slug: "daily-temperatures",
    title: "Daily Temperatures",
    difficulty: "Medium",
    pattern: "monotonic-stack",
    tags: ["Array", "Stack", "Monotonic Stack"],
    description: `Given daily \`temperatures\`, return a list \`answer\` where \`answer[i]\` is how many days you must wait after day \`i\` for a **warmer** temperature. If no warmer day comes, use \`0\`.`,
    examples: [
      { input: "temperatures = [73, 74, 75, 71, 69, 72, 76, 73]", output: "[1, 1, 4, 2, 1, 1, 0, 0]" },
      { input: "temperatures = [30, 60, 90]", output: "[1, 1, 0]" },
    ],
    constraints: ["1 ≤ len(temperatures) ≤ 10⁵", "30 ≤ temperatures[i] ≤ 100"],
    functionName: "dailyTemperatures",
    params: ["temperatures"],
    starterCode: `class Solution:
    def dailyTemperatures(self, temperatures: list[int]) -> list[int]:
        pass
`,
    compare: "exact",
    tests: [
      { args: [[73, 74, 75, 71, 69, 72, 76, 73]], expected: [1, 1, 4, 2, 1, 1, 0, 0], sample: true },
      { args: [[30, 60, 90]], expected: [1, 1, 0], sample: true },
      { args: [[30, 40, 50, 60]], expected: [1, 1, 1, 0] },
      { args: [[90, 80, 70]], expected: [0, 0, 0] },
      { args: [[50]], expected: [0] },
      { args: [[70, 70, 71]], expected: [2, 1, 0] },
    ],
  },
  {
    id: 17,
    slug: "find-the-duplicate-number",
    title: "Find the Duplicate Number",
    difficulty: "Medium",
    pattern: "fast-slow-pointers",
    tags: ["Array", "Two Pointers", "Fast & Slow Pointers"],
    description: `\`nums\` has \`n + 1\` integers, each in the range \`1\` to \`n\`. Exactly one value is repeated (possibly more than twice). Return that value.

Don't modify \`nums\`, and use only O(1) extra space. Hint: treat each value as a pointer to an index, and the array becomes a linked list with a cycle.`,
    examples: [
      { input: "nums = [1, 3, 4, 2, 2]", output: "2" },
      { input: "nums = [3, 1, 3, 4, 2]", output: "3" },
    ],
    constraints: ["1 ≤ n ≤ 10⁵", "len(nums) = n + 1", "1 ≤ nums[i] ≤ n", "Only one value repeats"],
    functionName: "findDuplicate",
    params: ["nums"],
    starterCode: `class Solution:
    def findDuplicate(self, nums: list[int]) -> int:
        pass
`,
    compare: "exact",
    tests: [
      { args: [[1, 3, 4, 2, 2]], expected: 2, sample: true },
      { args: [[3, 1, 3, 4, 2]], expected: 3, sample: true },
      { args: [[3, 3, 3, 3, 3]], expected: 3 },
      { args: [[1, 1]], expected: 1 },
      { args: [[2, 5, 9, 6, 9, 3, 8, 9, 7, 1]], expected: 9 },
      { args: [[1, 4, 4, 2, 4]], expected: 4 },
    ],
  },
  {
    id: 18,
    slug: "maximum-depth-of-binary-tree",
    title: "Maximum Depth of Binary Tree",
    difficulty: "Easy",
    pattern: "tree-dfs",
    tags: ["Tree", "Depth-First Search"],
    description: `Given the \`root\` of a binary tree, return its **maximum depth**: the number of nodes on the longest path from the root down to a leaf.

In the tests, a tree is written in level order with \`None\` for missing children, so \`[3, 9, 20, None, None, 15, 7]\` is a root 3 with children 9 and 20, and 20 has children 15 and 7. The judge builds the \`TreeNode\` objects for you.`,
    examples: [
      { input: "root = [3, 9, 20, None, None, 15, 7]", output: "3" },
      { input: "root = [1, None, 2]", output: "2" },
    ],
    constraints: ["0 ≤ number of nodes ≤ 10⁴", "-100 ≤ Node.val ≤ 100"],
    functionName: "maxDepth",
    params: ["root"],
    starterCode: `# TreeNode is provided by the judge:
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right

class Solution:
    def maxDepth(self, root: Optional[TreeNode]) -> int:
        pass
`,
    compare: "exact",
    argTypes: ["TreeNode"],
    tests: [
      { args: [[3, 9, 20, null, null, 15, 7]], expected: 3, sample: true },
      { args: [[1, null, 2]], expected: 2, sample: true },
      { args: [[]], expected: 0 },
      { args: [[1]], expected: 1 },
      { args: [[1, 2, null, 3, null, 4]], expected: 4 },
      { args: [[1, 2, 3, 4, 5, 6, 7]], expected: 3 },
    ],
  },
  {
    id: 19,
    slug: "binary-tree-level-order-traversal",
    title: "Binary Tree Level Order Traversal",
    difficulty: "Medium",
    pattern: "tree-bfs",
    tags: ["Tree", "Breadth-First Search"],
    description: `Given the \`root\` of a binary tree, return its values **level by level**, left to right, as a list of lists.

Trees in the tests are written in level order with \`None\` for missing children.`,
    examples: [
      { input: "root = [3, 9, 20, None, None, 15, 7]", output: "[[3], [9, 20], [15, 7]]" },
      { input: "root = []", output: "[]" },
    ],
    constraints: ["0 ≤ number of nodes ≤ 2000", "-1000 ≤ Node.val ≤ 1000"],
    functionName: "levelOrder",
    params: ["root"],
    starterCode: `# TreeNode is provided by the judge:
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right

class Solution:
    def levelOrder(self, root: Optional[TreeNode]) -> list[list[int]]:
        pass
`,
    compare: "exact",
    argTypes: ["TreeNode"],
    tests: [
      { args: [[3, 9, 20, null, null, 15, 7]], expected: [[3], [9, 20], [15, 7]], sample: true },
      { args: [[1]], expected: [[1]], sample: true },
      { args: [[]], expected: [] },
      { args: [[1, 2, 3, 4, null, null, 5]], expected: [[1], [2, 3], [4, 5]] },
      { args: [[1, null, 2, null, 3]], expected: [[1], [2], [3]] },
    ],
  },
  {
    id: 20,
    slug: "subsets",
    title: "Subsets",
    difficulty: "Medium",
    pattern: "backtracking",
    tags: ["Array", "Backtracking"],
    description: `Given an array \`nums\` of **distinct** integers, return every possible subset (the power set), including the empty subset.

The result must not contain duplicate subsets. You can return the subsets, and the numbers inside each one, in any order.`,
    examples: [
      { input: "nums = [1, 2, 3]", output: "[[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]]" },
      { input: "nums = [0]", output: "[[], [0]]" },
    ],
    constraints: ["1 ≤ len(nums) ≤ 10", "-10 ≤ nums[i] ≤ 10", "All values are distinct"],
    functionName: "subsets",
    params: ["nums"],
    starterCode: `class Solution:
    def subsets(self, nums: list[int]) -> list[list[int]]:
        pass
`,
    compare: "unordered-deep",
    tests: [
      { args: [[1, 2, 3]], expected: [[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]], sample: true },
      { args: [[0]], expected: [[], [0]], sample: true },
      { args: [[1, 2]], expected: [[], [1], [2], [1, 2]] },
      { args: [[9, -4]], expected: [[], [9], [-4], [-4, 9]] },
      { args: [[5, 6, 7, 8]], expected: [[], [5], [6], [7], [8], [5, 6], [5, 7], [5, 8], [6, 7], [6, 8], [7, 8], [5, 6, 7], [5, 6, 8], [5, 7, 8], [6, 7, 8], [5, 6, 7, 8]] },
    ],
  },
  {
    id: 21,
    slug: "replace-words",
    title: "Replace Words",
    difficulty: "Medium",
    pattern: "tries",
    tags: ["String", "Trie", "Hash Table"],
    description: `You are given a \`dictionary\` of word **roots** and a \`sentence\` of words separated by single spaces.

Replace every word that starts with a root by that root. If several roots match, use the **shortest**. Words with no matching root stay the same. Return the new sentence.`,
    examples: [
      {
        input: 'dictionary = ["cat", "bat", "rat"], sentence = "the cattle was rattled by the battery"',
        output: '"the cat was rat by the bat"',
      },
      { input: 'dictionary = ["a", "b", "c"], sentence = "aadsfasf absbs bbab cadsfafs"', output: '"a a b c"' },
    ],
    constraints: ["1 ≤ len(dictionary) ≤ 1000", "1 ≤ len(sentence) ≤ 10⁶", "Only lowercase letters and spaces"],
    functionName: "replaceWords",
    params: ["dictionary", "sentence"],
    starterCode: `class Solution:
    def replaceWords(self, dictionary: list[str], sentence: str) -> str:
        pass
`,
    compare: "exact",
    tests: [
      { args: [["cat", "bat", "rat"], "the cattle was rattled by the battery"], expected: "the cat was rat by the bat", sample: true },
      { args: [["a", "b", "c"], "aadsfasf absbs bbab cadsfafs"], expected: "a a b c", sample: true },
      { args: [["catt", "cat", "bat", "rat"], "the cattle was rattled by the battery"], expected: "the cat was rat by the bat" },
      { args: [["ab", "abc"], "abcd ab a"], expected: "ab ab a" },
      { args: [["x"], "hello world"], expected: "hello world" },
    ],
  },
  {
    id: 22,
    slug: "number-of-islands",
    title: "Number of Islands",
    difficulty: "Medium",
    pattern: "graphs",
    tags: ["Graph", "Breadth-First Search", "Depth-First Search", "Matrix"],
    description: `You are given an \`m x n\` grid of \`"1"\` (land) and \`"0"\` (water). Return the number of **islands**.

An island is a group of land cells connected horizontally or vertically (not diagonally). Everything outside the grid is water.`,
    examples: [
      {
        input: 'grid = [["1","1","0","0"], ["1","1","0","0"], ["0","0","1","0"], ["0","0","0","1"]]',
        output: "3",
      },
      { input: 'grid = [["1","1","1"], ["0","1","0"]]', output: "1" },
    ],
    constraints: ["1 ≤ m, n ≤ 300", 'grid[i][j] is "0" or "1"'],
    functionName: "numIslands",
    params: ["grid"],
    starterCode: `class Solution:
    def numIslands(self, grid: list[list[str]]) -> int:
        pass
`,
    compare: "exact",
    tests: [
      { args: [[["1", "1", "0", "0"], ["1", "1", "0", "0"], ["0", "0", "1", "0"], ["0", "0", "0", "1"]]], expected: 3, sample: true },
      { args: [[["1", "1", "1"], ["0", "1", "0"]]], expected: 1, sample: true },
      { args: [[["0"]]], expected: 0 },
      { args: [[["1"]]], expected: 1 },
      { args: [[["1", "0", "1"], ["0", "1", "0"], ["1", "0", "1"]]], expected: 5 },
      { args: [[["1", "1", "1", "1", "0"], ["1", "1", "0", "1", "0"], ["1", "1", "0", "0", "0"], ["0", "0", "0", "0", "0"]]], expected: 1 },
    ],
  },
  {
    id: 23,
    slug: "climbing-stairs",
    title: "Climbing Stairs",
    difficulty: "Easy",
    pattern: "dp-1d",
    tags: ["Dynamic Programming", "Math"],
    description: `A staircase has \`n\` steps. Each move you climb either **1 or 2** steps. In how many distinct ways can you reach the top?`,
    examples: [
      { input: "n = 2", output: "2", explanation: "1 + 1, or 2." },
      { input: "n = 3", output: "3", explanation: "1 + 1 + 1, 1 + 2, or 2 + 1." },
    ],
    constraints: ["1 ≤ n ≤ 45"],
    functionName: "climbStairs",
    params: ["n"],
    starterCode: `class Solution:
    def climbStairs(self, n: int) -> int:
        pass
`,
    compare: "exact",
    tests: [
      { args: [2], expected: 2, sample: true },
      { args: [3], expected: 3, sample: true },
      { args: [1], expected: 1 },
      { args: [5], expected: 8 },
      { args: [10], expected: 89 },
      { args: [45], expected: 1836311903 },
    ],
  },
  {
    id: 24,
    slug: "kth-smallest-element-in-a-sorted-matrix",
    title: "Kth Smallest Element in a Sorted Matrix",
    difficulty: "Medium",
    pattern: "k-way-merge",
    tags: ["Matrix", "Heap", "K-way Merge"],
    description: `Every row and every column of the \`n x n\` \`matrix\` is sorted in ascending order. Return the \`k\`th smallest element overall (counting duplicates).

Treat each row as a sorted list and merge them with a heap: you only need to pop \`k\` times.`,
    examples: [
      { input: "matrix = [[1, 5, 9], [10, 11, 13], [12, 13, 15]], k = 8", output: "13" },
      { input: "matrix = [[-5]], k = 1", output: "-5" },
    ],
    constraints: ["1 ≤ n ≤ 300", "-10⁹ ≤ matrix[i][j] ≤ 10⁹", "1 ≤ k ≤ n²"],
    functionName: "kthSmallest",
    params: ["matrix", "k"],
    starterCode: `import heapq

class Solution:
    def kthSmallest(self, matrix: list[list[int]], k: int) -> int:
        pass
`,
    compare: "exact",
    tests: [
      { args: [[[1, 5, 9], [10, 11, 13], [12, 13, 15]], 8], expected: 13, sample: true },
      { args: [[[-5]], 1], expected: -5, sample: true },
      { args: [[[1, 2], [1, 3]], 2], expected: 1 },
      { args: [[[1, 2], [1, 3]], 4], expected: 3 },
      { args: [[[1, 3, 5], [6, 7, 12], [11, 14, 14]], 6], expected: 11 },
    ],
  },
  {
    id: 25,
    slug: "ipo",
    title: "IPO",
    difficulty: "Hard",
    pattern: "two-heaps",
    tags: ["Array", "Greedy", "Heap", "Two Heaps"],
    description: `You start with capital \`w\` and may complete at most \`k\` projects. Project \`i\` needs at least \`capital[i]\` to start and adds \`profits[i]\` to your capital when finished.

Pick projects one at a time to **maximise your final capital**, and return it.

Keep the projects you can't afford yet in a min-heap by capital, and the affordable ones in a max-heap by profit.`,
    examples: [
      {
        input: "k = 2, w = 0, profits = [1, 2, 3], capital = [0, 1, 1]",
        output: "4",
        explanation: "Do project 0 (capital becomes 1), then project 2 (capital becomes 4).",
      },
      { input: "k = 3, w = 0, profits = [1, 2, 3], capital = [0, 1, 2]", output: "6" },
    ],
    constraints: ["1 ≤ k ≤ 10⁵", "0 ≤ w ≤ 10⁹", "1 ≤ n ≤ 10⁵", "0 ≤ profits[i] ≤ 10⁴", "0 ≤ capital[i] ≤ 10⁹"],
    functionName: "findMaximizedCapital",
    params: ["k", "w", "profits", "capital"],
    starterCode: `import heapq

class Solution:
    def findMaximizedCapital(self, k: int, w: int, profits: list[int], capital: list[int]) -> int:
        pass
`,
    compare: "exact",
    tests: [
      { args: [2, 0, [1, 2, 3], [0, 1, 1]], expected: 4, sample: true },
      { args: [3, 0, [1, 2, 3], [0, 1, 2]], expected: 6, sample: true },
      { args: [1, 0, [1, 2, 3], [1, 1, 2]], expected: 0 },
      { args: [10, 5, [1, 2, 3], [0, 0, 0]], expected: 11 },
      { args: [2, 1, [2, 3, 5], [1, 2, 6]], expected: 6 },
    ],
  },
  {
    id: 26,
    slug: "single-number",
    title: "Single Number",
    difficulty: "Easy",
    pattern: "bit-manipulation",
    tags: ["Array", "Bit Manipulation"],
    description: `Every element of \`nums\` appears **twice** except for one, which appears once. Return that one.

Aim for O(n) time and O(1) extra space. Think about what \`x ^ x\` equals.`,
    examples: [
      { input: "nums = [2, 2, 1]", output: "1" },
      { input: "nums = [4, 1, 2, 1, 2]", output: "4" },
    ],
    constraints: ["1 ≤ len(nums) ≤ 3 × 10⁴", "-3 × 10⁴ ≤ nums[i] ≤ 3 × 10⁴"],
    functionName: "singleNumber",
    params: ["nums"],
    starterCode: `class Solution:
    def singleNumber(self, nums: list[int]) -> int:
        pass
`,
    compare: "exact",
    tests: [
      { args: [[2, 2, 1]], expected: 1, sample: true },
      { args: [[4, 1, 2, 1, 2]], expected: 4, sample: true },
      { args: [[1]], expected: 1 },
      { args: [[-3, 7, 7]], expected: -3 },
      { args: [[0, 5, 5]], expected: 0 },
    ],
  },
  {
    id: 27,
    slug: "longest-common-subsequence",
    title: "Longest Common Subsequence",
    difficulty: "Medium",
    pattern: "dp-2d",
    tags: ["String", "Dynamic Programming"],
    description: `Given two strings \`text1\` and \`text2\`, return the length of their longest **common subsequence**, or \`0\` if there is none.

A subsequence keeps the original order but may skip characters: \`"ace"\` is a subsequence of \`"abcde"\`.`,
    examples: [
      { input: 'text1 = "abcde", text2 = "ace"', output: "3", explanation: '"ace"' },
      { input: 'text1 = "abc", text2 = "def"', output: "0" },
    ],
    constraints: ["1 ≤ len(text1), len(text2) ≤ 1000", "Only lowercase English letters"],
    functionName: "longestCommonSubsequence",
    params: ["text1", "text2"],
    starterCode: `class Solution:
    def longestCommonSubsequence(self, text1: str, text2: str) -> int:
        pass
`,
    compare: "exact",
    tests: [
      { args: ["abcde", "ace"], expected: 3, sample: true },
      { args: ["abc", "def"], expected: 0, sample: true },
      { args: ["abc", "abc"], expected: 3 },
      { args: ["a", "a"], expected: 1 },
      { args: ["bsbininm", "jmjkbkjkv"], expected: 1 },
      { args: ["abcba", "abcbcba"], expected: 5 },
    ],
  },
  {
    id: 28,
    slug: "redundant-connection",
    title: "Redundant Connection",
    difficulty: "Medium",
    pattern: "union-find",
    tags: ["Graph", "Union Find"],
    description: `A tree with \`n\` nodes (labelled \`1\` to \`n\`) had one extra edge added, creating exactly one cycle. The edges are given in \`edges\`, where \`edges[i] = [a, b]\`.

Return an edge you can remove so the graph becomes a tree again. If several edges work, return the one that appears **last** in \`edges\`.`,
    examples: [
      { input: "edges = [[1, 2], [1, 3], [2, 3]]", output: "[2, 3]" },
      { input: "edges = [[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]]", output: "[1, 4]" },
    ],
    constraints: ["3 ≤ n = len(edges) ≤ 1000", "1 ≤ a < b ≤ n", "No repeated edges", "The graph is connected"],
    functionName: "findRedundantConnection",
    params: ["edges"],
    starterCode: `class Solution:
    def findRedundantConnection(self, edges: list[list[int]]) -> list[int]:
        pass
`,
    compare: "exact",
    tests: [
      { args: [[[1, 2], [1, 3], [2, 3]]], expected: [2, 3], sample: true },
      { args: [[[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]]], expected: [1, 4], sample: true },
      { args: [[[1, 2], [2, 3], [1, 3]]], expected: [1, 3] },
      { args: [[[3, 4], [1, 2], [2, 4], [3, 5], [2, 5]]], expected: [2, 5] },
      { args: [[[1, 4], [3, 4], [1, 3], [1, 2], [4, 5]]], expected: [1, 3] },
    ],
  },
  {
    id: 29,
    slug: "course-schedule",
    title: "Course Schedule",
    difficulty: "Medium",
    pattern: "topological-sort",
    tags: ["Graph", "Topological Sort"],
    description: `There are \`numCourses\` courses, labelled \`0\` to \`numCourses - 1\`. Each pair \`[a, b]\` in \`prerequisites\` means you must take course \`b\` before course \`a\`.

Return \`True\` if you can finish every course, or \`False\` if the prerequisites form a cycle.`,
    examples: [
      { input: "numCourses = 2, prerequisites = [[1, 0]]", output: "True" },
      { input: "numCourses = 2, prerequisites = [[1, 0], [0, 1]]", output: "False", explanation: "Each course needs the other first." },
    ],
    constraints: ["1 ≤ numCourses ≤ 2000", "0 ≤ len(prerequisites) ≤ 5000", "All pairs are unique"],
    functionName: "canFinish",
    params: ["numCourses", "prerequisites"],
    starterCode: `class Solution:
    def canFinish(self, numCourses: int, prerequisites: list[list[int]]) -> bool:
        pass
`,
    compare: "exact",
    tests: [
      { args: [2, [[1, 0]]], expected: true, sample: true },
      { args: [2, [[1, 0], [0, 1]]], expected: false, sample: true },
      { args: [1, []], expected: true },
      { args: [3, [[1, 0], [2, 1]]], expected: true },
      { args: [3, [[0, 1], [1, 2], [2, 0]]], expected: false },
      { args: [4, [[1, 0], [2, 0], [3, 1], [3, 2]]], expected: true },
    ],
  },
  {
    id: 30,
    slug: "network-delay-time",
    title: "Network Delay Time",
    difficulty: "Medium",
    pattern: "advanced-graphs",
    tags: ["Graph", "Shortest Path", "Heap"],
    description: `A network has \`n\` nodes labelled \`1\` to \`n\`. Each \`times[i] = [u, v, w]\` is a **directed** edge: a signal takes \`w\` time to travel from \`u\` to \`v\`.

A signal is sent from node \`k\`. Return the time it takes for **every** node to receive it, or \`-1\` if some node never does.`,
    examples: [
      { input: "times = [[2, 1, 1], [2, 3, 1], [3, 4, 1]], n = 4, k = 2", output: "2" },
      { input: "times = [[1, 2, 1]], n = 2, k = 2", output: "-1" },
    ],
    constraints: ["1 ≤ k ≤ n ≤ 100", "1 ≤ len(times) ≤ 6000", "0 ≤ w ≤ 100", "No repeated edges"],
    functionName: "networkDelayTime",
    params: ["times", "n", "k"],
    starterCode: `import heapq

class Solution:
    def networkDelayTime(self, times: list[list[int]], n: int, k: int) -> int:
        pass
`,
    compare: "exact",
    tests: [
      { args: [[[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2], expected: 2, sample: true },
      { args: [[[1, 2, 1]], 2, 2], expected: -1, sample: true },
      { args: [[[1, 2, 1]], 2, 1], expected: 1 },
      { args: [[[1, 2, 1], [2, 3, 2], [1, 3, 4]], 3, 1], expected: 3 },
      { args: [[[1, 2, 5], [2, 1, 5]], 2, 1], expected: 5 },
    ],
  },
  {
    id: 31,
    slug: "happy-number",
    title: "Happy Number",
    difficulty: "Easy",
    pattern: "math-geometry",
    tags: ["Math", "Hash Table"],
    description: `Start with a positive integer \`n\` and repeatedly replace it with the **sum of the squares of its digits**. If this process reaches \`1\`, the number is **happy**. Otherwise it loops forever in a cycle that never includes 1.

Return \`True\` if \`n\` is happy.`,
    examples: [
      { input: "n = 19", output: "True", explanation: "1² + 9² = 82, 8² + 2² = 68, 6² + 8² = 100, 1² + 0² + 0² = 1" },
      { input: "n = 2", output: "False" },
    ],
    constraints: ["1 ≤ n ≤ 2³¹ - 1"],
    functionName: "isHappy",
    params: ["n"],
    starterCode: `class Solution:
    def isHappy(self, n: int) -> bool:
        pass
`,
    compare: "exact",
    tests: [
      { args: [19], expected: true, sample: true },
      { args: [2], expected: false, sample: true },
      { args: [1], expected: true },
      { args: [7], expected: true },
      { args: [4], expected: false },
      { args: [100], expected: true },
    ],
  },
];
