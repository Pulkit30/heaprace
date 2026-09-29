// Source of truth for problem content. `npm run db:seed` loads it into the database, which the app reads from.
// Keep this file free of runtime imports so the scripts can load it directly with Node.

export type Difficulty = "Easy" | "Medium" | "Hard";

/** How a returned value is compared with the expected one. */
export type CompareMode =
  | "exact" // deep equality
  | "unordered" // top-level list order doesn't matter
  | "unordered-deep"; // order doesn't matter at either level (list of lists)

export interface TestCase {
  /** Positional arguments passed to the solution method, as JSON values. */
  args: unknown[];
  expected: unknown;
  /** Sample tests are shown to the user and used by "Run". Hidden tests only run on "Submit". */
  sample?: boolean;
}

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
  tests: TestCase[];
}

export const problems: Problem[] = [
  {
    id: 1,
    slug: "two-sum",
    title: "Two Sum",
    difficulty: "Easy",
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
];
