from functools import lru_cache
from itertools import combinations, product

from catalog_lib import problem

D1 = "dp-1d"
D2 = "dp-2d"


def _subsets_idx(n):
    return (c for r in range(n + 1) for c in combinations(range(n), r))


@problem(
    slug="0-1-knapsack", title="0/1 Knapsack", difficulty="Medium", pattern=D2, tags=["Array", "Dynamic Programming"],
    sig="findMaxKnapsackProfit(self, capacity: int, weights: list[int], values: list[int]) -> int",
    desc="""Item `i` has weight `weights[i]` and value `values[i]`. Choose items (each at most once) with total weight at most `capacity`, and return the maximum total value.""",
    constraints=["1 ≤ n ≤ 100", "1 ≤ weights[i] ≤ 1000", "0 ≤ values[i] ≤ 10⁴", "0 ≤ capacity ≤ 1000"],
    samples=[(6, [1, 2, 3, 5], [1, 5, 4, 8]), (3, [4], [2])],
    gen=lambda r: (lambda n: (r.randint(0, 20), r.ints(n, 1, 10), r.ints(n, 0, 15)))(r.randint(1, 8)),
    brute=lambda cap, w, v: max(sum(v[i] for i in s) for s in _subsets_idx(len(w)) if sum(w[i] for i in s) <= cap),
    hints=[
        "For each item you either take it or skip it.",
        "Let best[c] be the best value with capacity c using the items seen so far.",
        "For each item, update best[c] = max(best[c], best[c − w] + v) with c going downward, so the item is used at most once.",
    ],
    insight="Take-or-skip DP over capacity; iterate capacity backwards for 0/1 items.",
    time="O(n · capacity)", space="O(capacity)",
    pitfalls=["Iterating capacity upward, which lets an item be taken many times."],
)
def knapsack(capacity, weights, values):
    best = [0] * (capacity + 1)
    for w, v in zip(weights, values):
        for c in range(capacity, w - 1, -1):
            best[c] = max(best[c], best[c - w] + v)
    return best[capacity]


def _coin_brute(coins, amount):
    @lru_cache(None)
    def go(a):
        if a == 0:
            return 0
        opts = [go(a - c) for c in coins if c <= a]
        opts = [o for o in opts if o >= 0]
        return 1 + min(opts) if opts else -1
    return go(amount)


@problem(
    slug="coin-change", title="Coin Change", difficulty="Medium", pattern=D1, tags=["Array", "Dynamic Programming", "Breadth-First Search"],
    sig="coinChange(self, coins: list[int], amount: int) -> int",
    desc="""Return the fewest coins needed to make `amount` using unlimited coins of the given denominations, or `-1` if it can't be made.""",
    constraints=["1 ≤ len(coins) ≤ 12", "1 ≤ coins[i] ≤ 2³¹ − 1", "0 ≤ amount ≤ 10⁴"],
    samples=[([1, 2, 5], 11), ([2], 3), ([1], 0)],
    gen=lambda r: (r.distinct(r.randint(1, 4), 1, 12), r.randint(0, 40)),
    brute=_coin_brute,
    hints=[
        "Greedy (largest coin first) fails, e.g. coins [1, 3, 4] for amount 6.",
        "Let dp[a] be the fewest coins for amount a.",
        "dp[a] = 1 + min(dp[a − c]) over coins c ≤ a, with dp[0] = 0 and unreachable amounts marked as infinity.",
    ],
    insight="Unbounded DP over amounts, building each from smaller amounts.",
    time="O(amount · len(coins))", space="O(amount)",
    pitfalls=["Using a greedy choice."],
)
def coin_change(coins, amount):
    inf = float("inf")
    dp = [0] + [inf] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    return dp[amount] if dp[amount] != inf else -1


def _change_brute(amount, coins):
    @lru_cache(None)
    def go(i, a):
        if a == 0:
            return 1
        if i == len(coins):
            return 0
        return sum(go(i + 1, a - k * coins[i]) for k in range(a // coins[i] + 1))
    return go(0, amount)


@problem(
    slug="coin-change-ii", title="Coin Change II", difficulty="Medium", pattern=D1, tags=["Array", "Dynamic Programming"],
    sig="change(self, amount: int, coins: list[int]) -> int",
    desc="""Return the number of **combinations** of coins (unlimited of each denomination) that add up to `amount`. Different orders of the same coins count once.""",
    constraints=["1 ≤ len(coins) ≤ 300", "1 ≤ coins[i] ≤ 5000, distinct", "0 ≤ amount ≤ 5000"],
    samples=[(5, [1, 2, 5]), (3, [2]), (10, [10])],
    gen=lambda r: (r.randint(0, 30), r.distinct(r.randint(1, 4), 1, 10)),
    brute=_change_brute,
    hints=[
        "Counting orderings would count [1, 2] and [2, 1] separately; you want combinations.",
        "Process coins one at a time in the outer loop.",
        "ways[a] += ways[a − coin] for amounts from coin upward, starting with ways[0] = 1.",
    ],
    insight="Putting coins in the outer loop counts each combination once.",
    time="O(amount · len(coins))", space="O(amount)",
    pitfalls=["Swapping the loops, which counts permutations."],
)
def change(amount, coins):
    ways = [1] + [0] * amount
    for c in coins:
        for a in range(c, amount + 1):
            ways[a] += ways[a - c]
    return ways[amount]


@problem(
    slug="n-th-tribonacci-number", title="N-th Tribonacci Number", difficulty="Easy", pattern=D1, tags=["Math", "Dynamic Programming", "Memoization"],
    sig="tribonacci(self, n: int) -> int",
    desc="""The Tribonacci sequence is T₀ = 0, T₁ = 1, T₂ = 1, and Tₙ₊₃ = Tₙ + Tₙ₊₁ + Tₙ₊₂. Return Tₙ.""",
    constraints=["0 ≤ n ≤ 37"],
    samples=[(4,), (25,), (0,)],
    tests=[(1,), (2,), (37,)],
    gen=lambda r: (r.randint(3, 37),),
    brute=lambda n: (lambda f: f(f, n))(lambda f, k: [0, 1, 1][k] if k < 3 else f(f, k - 1) + f(f, k - 2) + f(f, k - 3)) if n < 20 else tribonacci(n),
    hints=[
        "Each term depends only on the three before it.",
        "Plain recursion recomputes the same terms over and over.",
        "Keep three rolling variables and shift them n times.",
    ],
    insight="Rolling variables turn the recurrence into O(n) time and O(1) space.",
    time="O(n)", space="O(1)",
    pitfalls=["Naive recursion, which is exponential."],
)
def tribonacci(n):
    a, b, c = 0, 1, 1
    for _ in range(n):
        a, b, c = b, c, a + b + c
    return a


@problem(
    slug="partition-equal-subset-sum", title="Partition Equal Subset Sum", difficulty="Medium", pattern=D1, tags=["Array", "Dynamic Programming"],
    sig="canPartition(self, nums: list[int]) -> bool",
    desc="""Return `true` if `nums` can be split into two subsets with equal sums.""",
    constraints=["1 ≤ len(nums) ≤ 200", "1 ≤ nums[i] ≤ 100"],
    samples=[([1, 5, 11, 5],), ([1, 2, 3, 5],)],
    gen=lambda r: (r.ints(r.randint(1, 10), 1, 12),),
    brute=lambda nums: any(2 * sum(nums[i] for i in s) == sum(nums) for s in _subsets_idx(len(nums))),
    hints=[
        "If the total is odd, it's impossible.",
        "Otherwise you need a subset that sums to total / 2.",
        "Track the set of reachable sums (a boolean array or a bitset), adding each number once.",
    ],
    insight="Reduces to subset-sum for half the total.",
    time="O(n · sum)", space="O(sum)",
    pitfalls=["Forgetting the odd-total shortcut."],
)
def can_partition(nums):
    total = sum(nums)
    if total % 2:
        return False
    reach = 1
    for x in nums:
        reach |= reach << x
    return bool(reach >> (total // 2) & 1)


@problem(
    slug="counting-bits", title="Counting Bits", difficulty="Easy", pattern=D1, tags=["Dynamic Programming", "Bit Manipulation"],
    sig="countBits(self, n: int) -> list[int]",
    desc="""Return a list `ans` of length `n + 1` where `ans[i]` is the number of `1` bits in the binary form of `i`.""",
    constraints=["0 ≤ n ≤ 10⁵"],
    samples=[(2,), (5,), (0,)],
    tests=[(16,), (31,)],
    gen=lambda r: (r.randint(1, 200),),
    brute=lambda n: [bin(i).count("1") for i in range(n + 1)],
    hints=[
        "i and i // 2 have the same bits except the last one.",
        "So the count for i builds on the count for i // 2.",
        "ans[i] = ans[i >> 1] + (i & 1).",
    ],
    insight="Each answer reuses the answer for i shifted right by one.",
    time="O(n)", space="O(n)",
    pitfalls=["Counting bits of each number from scratch, which is O(n log n)."],
)
def count_bits(n):
    ans = [0] * (n + 1)
    for i in range(1, n + 1):
        ans[i] = ans[i >> 1] + (i & 1)
    return ans


def _rob_line(nums):
    a = b = 0
    for x in nums:
        a, b = b, max(b, a + x)
    return b


def _rob_brute(nums, circular):
    n = len(nums)
    best = 0
    for mask in range(1 << n):
        if mask & (mask >> 1):
            continue
        if circular and n > 1 and mask & 1 and mask >> (n - 1) & 1:
            continue
        best = max(best, sum(nums[i] for i in range(n) if mask >> i & 1))
    return best


@problem(
    slug="house-robber", title="House Robber", difficulty="Medium", pattern=D1, tags=["Array", "Dynamic Programming"],
    sig="rob(self, nums: list[int]) -> int",
    desc="""Houses on a street hold `nums[i]` money. You can't rob two adjacent houses. Return the most money you can rob.""",
    constraints=["1 ≤ len(nums) ≤ 100", "0 ≤ nums[i] ≤ 400"],
    samples=[([1, 2, 3, 1],), ([2, 7, 9, 3, 1],)],
    gen=lambda r: (r.ints(r.randint(1, 12), 0, 20),),
    brute=lambda nums: _rob_brute(nums, False),
    hints=[
        "At each house, you either rob it (and skip the previous one) or skip it.",
        "best(i) = max(best(i − 1), best(i − 2) + nums[i]).",
        "Only the last two values are needed, so two variables suffice.",
    ],
    insight="A two-state DP over houses.",
    time="O(n)", space="O(1)",
    pitfalls=["Greedily picking every other house."],
)
def rob(nums):
    return _rob_line(nums)


@problem(
    slug="house-robber-ii", title="House Robber II", difficulty="Medium", pattern=D1, tags=["Array", "Dynamic Programming"],
    sig="rob(self, nums: list[int]) -> int",
    desc="""Same as House Robber, but the houses are arranged in a **circle**: the first and last houses are neighbors. Return the most money you can rob without robbing two adjacent houses.""",
    constraints=["1 ≤ len(nums) ≤ 100", "0 ≤ nums[i] ≤ 1000"],
    samples=[([2, 3, 2],), ([1, 2, 3, 1],), ([1, 2, 3],)],
    tests=[([5],)],
    gen=lambda r: (r.ints(r.randint(1, 12), 0, 20),),
    brute=lambda nums: _rob_brute(nums, True),
    hints=[
        "You can't rob both the first and the last house.",
        "So either the first house is excluded or the last house is excluded.",
        "Run the straight-line House Robber on nums[1:] and on nums[:-1], and take the better result (a single house is a special case).",
    ],
    insight="Break the circle into two linear problems.",
    time="O(n)", space="O(1)",
    pitfalls=["Forgetting the single-house case, where both slices are empty."],
)
def rob_circle(nums):
    if len(nums) == 1:
        return nums[0]
    return max(_rob_line(nums[1:]), _rob_line(nums[:-1]))


@problem(
    slug="maximum-product-subarray", title="Maximum Product Subarray", difficulty="Medium", pattern=D1, tags=["Array", "Dynamic Programming"],
    sig="maxProduct(self, nums: list[int]) -> int",
    desc="""Return the largest product of a non-empty contiguous subarray of `nums`.""",
    constraints=["1 ≤ len(nums) ≤ 2 × 10⁴", "-10 ≤ nums[i] ≤ 10"],
    samples=[([2, 3, -2, 4],), ([-2, 0, -1],), ([-2, 3, -4],)],
    gen=lambda r: (r.ints(r.randint(1, 10), -4, 4),),
    brute=lambda nums: max(__import__("math").prod(nums[i:j]) for i in range(len(nums)) for j in range(i + 1, len(nums) + 1)),
    hints=[
        "A negative number turns the smallest product into the largest.",
        "Track both the maximum and minimum product of a subarray ending at each index.",
        "For each x, the new max and min come from x, max·x and min·x.",
    ],
    insight="Keep max and min together because multiplying by a negative swaps them.",
    time="O(n)", space="O(1)",
    pitfalls=["Tracking only the maximum, as in Kadane's sum version."],
)
def max_product(nums):
    hi = lo = best = nums[0]
    for x in nums[1:]:
        hi, lo = max(x, hi * x, lo * x), min(x, hi * x, lo * x)
        best = max(best, hi)
    return best


def _wb_brute(s, words):
    ws = set(words)

    @lru_cache(None)
    def go(i):
        return i == len(s) or any(s[i:j] in ws and go(j) for j in range(i + 1, len(s) + 1))
    return go(0)


@problem(
    slug="word-break", title="Word Break", difficulty="Medium", pattern=D1,
    tags=["Array", "Hash Table", "String", "Dynamic Programming", "Trie", "Memoization"],
    sig="wordBreak(self, s: str, wordDict: list[str]) -> bool",
    desc="""Return `true` if `s` can be split into a sequence of one or more words from `wordDict` (words may be reused).""",
    constraints=["1 ≤ len(s) ≤ 300", "1 ≤ len(wordDict) ≤ 1000", "lowercase letters"],
    samples=[("leetcode", ["leet", "code"]), ("applepenapple", ["apple", "pen"]), ("catsandog", ["cats", "dog", "sand", "and", "cat"])],
    gen=lambda r: (r.word(r.randint(1, 12), "ab"), sorted({r.word(r.randint(1, 3), "ab") for _ in range(r.randint(1, 5))})),
    brute=_wb_brute,
    hints=[
        "Let ok[i] mean the prefix s[:i] can be split.",
        "ok[0] is true (the empty prefix).",
        "ok[j] is true if some i < j has ok[i] true and s[i:j] in the dictionary.",
    ],
    insight="Prefix DP over split points.",
    time="O(n² · L)", space="O(n)",
    pitfalls=["Trying words greedily from the left without backtracking."],
)
def word_break(s, wordDict):
    words = set(wordDict)
    ok = [True] + [False] * len(s)
    for j in range(1, len(s) + 1):
        ok[j] = any(ok[i] and s[i:j] in words for i in range(j))
    return ok[-1]


@problem(
    slug="palindromic-substrings", title="Palindromic Substrings", difficulty="Medium", pattern=D2,
    tags=["Two Pointers", "String", "Dynamic Programming"],
    sig="countSubstrings(self, s: str) -> int",
    desc="""Return how many substrings of `s` are palindromes. Substrings at different positions count separately even if equal.""",
    constraints=["1 ≤ len(s) ≤ 1000", "lowercase letters"],
    samples=[("abc",), ("aaa",)],
    gen=lambda r: (r.word(r.randint(1, 12), "abc"),),
    brute=lambda s: sum(s[i:j] == s[i:j][::-1] for i in range(len(s)) for j in range(i + 1, len(s) + 1)),
    hints=[
        "Every palindrome has a center: a character or the gap between two characters.",
        "From each center, expand outwards while both ends match.",
        "There are 2n − 1 centers; count one palindrome for each successful expansion.",
    ],
    insight="Expanding around 2n − 1 centers counts all palindromes in O(n²) with O(1) space.",
    time="O(n²)", space="O(1)",
    pitfalls=["Forgetting even-length centers."],
)
def count_substrings(s):
    count = 0
    for c in range(2 * len(s) - 1):
        i, j = c // 2, c // 2 + c % 2
        while i >= 0 and j < len(s) and s[i] == s[j]:
            count += 1
            i -= 1
            j += 1
    return count


@problem(
    slug="longest-palindromic-substring", title="Longest Palindromic Substring", difficulty="Medium", pattern=D2,
    tags=["Two Pointers", "String", "Dynamic Programming"],
    sig="longestPalindrome(self, s: str) -> str",
    desc="""Return the longest palindromic substring of `s`. If several have the maximum length, return the one that starts **earliest**.""",
    constraints=["1 ≤ len(s) ≤ 1000", "letters and digits"],
    samples=[("babad",), ("cbbd",), ("a",)],
    gen=lambda r: (r.word(r.randint(1, 12), "abc"),),
    brute=lambda s: max((s[i:j] for i in range(len(s)) for j in range(i + 1, len(s) + 1) if s[i:j] == s[i:j][::-1]), key=lambda t: (len(t), -s.find(t))),
    hints=[
        "Each palindrome grows outward from a center.",
        "Expand around all 2n − 1 centers and remember the longest span.",
        "Keep the best (start, end) span; on equal length, prefer the span with the smaller start index.",
    ],
    insight="Center expansion finds the longest palindrome in O(n²).",
    time="O(n²)", space="O(1)",
    pitfalls=["Missing even-length palindromes like \"bb\"."],
)
def longest_palindrome(s):
    best = (0, 1)
    for c in range(2 * len(s) - 1):
        i, j = c // 2, c // 2 + c % 2
        while i >= 0 and j < len(s) and s[i] == s[j]:
            i -= 1
            j += 1
        i, j = i + 1, j
        if j - i > best[1] - best[0] or (j - i == best[1] - best[0] and i < best[0]):
            best = (i, j)
    return s[best[0]:best[1]]


def _lis_brute(nums):
    best = 0
    for s in _subsets_idx(len(nums)):
        seq = [nums[i] for i in s]
        if all(a < b for a, b in zip(seq, seq[1:])):
            best = max(best, len(seq))
    return best


@problem(
    slug="longest-increasing-subsequence", title="Longest Increasing Subsequence", difficulty="Medium", pattern=D1,
    tags=["Array", "Binary Search", "Dynamic Programming"],
    sig="lengthOfLIS(self, nums: list[int]) -> int",
    desc="""Return the length of the longest **strictly** increasing subsequence of `nums`.""",
    constraints=["1 ≤ len(nums) ≤ 2500", "-10⁴ ≤ nums[i] ≤ 10⁴"],
    samples=[([10, 9, 2, 5, 3, 7, 101, 18],), ([0, 1, 0, 3, 2, 3],), ([7, 7, 7, 7, 7, 7, 7],)],
    gen=lambda r: (r.ints(r.randint(1, 11), -5, 5),),
    brute=_lis_brute,
    hints=[
        "An O(n²) DP: lis[i] = 1 + max(lis[j]) for j < i with nums[j] < nums[i].",
        "Faster: keep tails[k], the smallest possible tail of an increasing subsequence of length k + 1.",
        "For each number, binary search the first tail ≥ it and replace it (or append). The answer is the length of tails.",
    ],
    insight="Patience sorting: smallest tails stay sorted, so binary search applies.",
    time="O(n log n)", space="O(n)",
    pitfalls=["Using bisect_right, which allows equal values (non-strict)."],
)
def length_of_lis(nums):
    from bisect import bisect_left
    tails = []
    for x in nums:
        i = bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)


@problem(
    slug="edit-distance", title="Edit Distance", difficulty="Medium", pattern=D2, tags=["String", "Dynamic Programming"],
    sig="minDistance(self, word1: str, word2: str) -> int",
    desc="""Return the minimum number of operations to turn `word1` into `word2`, where one operation inserts a character, deletes a character, or replaces a character.""",
    constraints=["0 ≤ len(word1), len(word2) ≤ 500", "lowercase letters"],
    samples=[("horse", "ros"), ("intention", "execution"), ("", "a")],
    gen=lambda r: (r.word(r.randint(0, 7), "abc"), r.word(r.randint(0, 7), "abc")),
    brute=lambda a, b: (lambda f: f(f, len(a), len(b)))(lru_cache(None)(lambda f, i, j: j if i == 0 else i if j == 0 else min(f(f, i - 1, j) + 1, f(f, i, j - 1) + 1, f(f, i - 1, j - 1) + (a[i - 1] != b[j - 1])))),
    hints=[
        "Compare prefixes: let d[i][j] be the cost to turn word1[:i] into word2[:j].",
        "Base cases: d[i][0] = i (delete everything) and d[0][j] = j (insert everything).",
        "If the last characters match, d[i][j] = d[i−1][j−1]; otherwise 1 + min of delete, insert, replace.",
    ],
    insight="A classic 2D DP over prefix pairs.",
    time="O(m·n)", space="O(n) with a rolling row",
    pitfalls=["Forgetting the empty-string base cases."],
)
def min_distance(word1, word2):
    m, n = len(word1), len(word2)
    prev = list(range(n + 1))
    for i in range(1, m + 1):
        cur = [i] + [0] * n
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                cur[j] = prev[j - 1]
            else:
                cur[j] = 1 + min(prev[j], cur[j - 1], prev[j - 1])
        prev = cur
    return prev[n]


@problem(
    slug="unique-paths", title="Unique Paths", difficulty="Medium", pattern=D2, tags=["Math", "Dynamic Programming", "Combinatorics"],
    sig="uniquePaths(self, m: int, n: int) -> int",
    desc="""A robot starts in the top-left cell of an `m × n` grid and moves only right or down. Return the number of distinct paths to the bottom-right cell.""",
    constraints=["1 ≤ m, n ≤ 100", "the answer fits in 2 × 10⁹ for the tested sizes"],
    samples=[(3, 7), (3, 2)],
    tests=[(1, 1), (10, 10)],
    gen=lambda r: (r.randint(1, 15), r.randint(1, 15)),
    brute=lambda m, n: __import__("math").comb(m + n - 2, m - 1),
    hints=[
        "Paths into a cell come from the cell above or the cell to the left.",
        "paths[i][j] = paths[i−1][j] + paths[i][j−1], with the first row and column all 1.",
        "One row of length n is enough: update it left to right m times.",
    ],
    insight="Grid DP (or the binomial coefficient C(m + n − 2, m − 1)).",
    time="O(m·n)", space="O(n)",
    pitfalls=["Recursing without memoization."],
)
def unique_paths(m, n):
    row = [1] * n
    for _ in range(m - 1):
        for j in range(1, n):
            row[j] += row[j - 1]
    return row[-1]


def _decode_brute(s):
    @lru_cache(None)
    def go(i):
        if i == len(s):
            return 1
        total = 0
        for L in (1, 2):
            part = s[i:i + L]
            if len(part) == L and part[0] != "0" and 1 <= int(part) <= 26:
                total += go(i + L)
        return total
    return go(0)


@problem(
    slug="decode-ways", title="Decode Ways", difficulty="Medium", pattern=D1, tags=["String", "Dynamic Programming"],
    sig="numDecodings(self, s: str) -> int",
    desc="""Letters are encoded as numbers: `'A' → "1"`, …, `'Z' → "26"`. Given a digit string `s`, return how many ways it can be decoded. A group like `"06"` is invalid (no leading zeros).""",
    constraints=["1 ≤ len(s) ≤ 100", "s contains only digits"],
    samples=[("12",), ("226",), ("06",)],
    gen=lambda r: ("".join(r.choice("0122367") for _ in range(r.randint(1, 10))),),
    brute=_decode_brute,
    hints=[
        "The last step of a decoding uses either one digit or two digits.",
        "One digit works if it isn't '0'; two digits work if they form 10–26.",
        "ways[i] = (ways[i−1] if s[i−1] valid) + (ways[i−2] if s[i−2:i] valid), with ways[0] = 1.",
    ],
    insight="A Fibonacci-like DP with validity checks.",
    time="O(n)", space="O(1)",
    pitfalls=["Treating \"0\" alone as a valid letter."],
)
def num_decodings(s):
    a, b = 1, 1 if s[0] != "0" else 0
    for i in range(2, len(s) + 1):
        cur = 0
        if s[i - 1] != "0":
            cur += b
        if s[i - 2] != "0" and int(s[i - 2:i]) <= 26:
            cur += a
        a, b = b, cur
    return b


def _path_cells(moves):
    i = j = 0
    yield 0, 0
    for mv in moves:
        if mv == "D":
            i += 1
        else:
            j += 1
        yield i, j


@problem(
    slug="minimum-path-sum", title="Minimum Path Sum", difficulty="Medium", pattern=D2, tags=["Array", "Dynamic Programming", "Matrix"],
    sig="minPathSum(self, grid: list[list[int]]) -> int",
    desc="""Moving only right or down from the top-left to the bottom-right of `grid`, return the minimum possible sum of the numbers along the path.""",
    constraints=["1 ≤ m, n ≤ 200", "0 ≤ grid[i][j] ≤ 200"],
    samples=[([[1, 3, 1], [1, 5, 1], [4, 2, 1]],), ([[1, 2, 3], [4, 5, 6]],)],
    gen=lambda r: (lambda m, n: ([r.ints(n, 0, 9) for _ in range(m)],))(r.randint(1, 5), r.randint(1, 5)),
    brute=lambda g: min(sum(g[i][j] for i, j in _path_cells(p)) for p in set(__import__("itertools").permutations("D" * (len(g) - 1) + "R" * (len(g[0]) - 1)))),
    hints=[
        "The best path into a cell comes from its top or left neighbor.",
        "best[i][j] = grid[i][j] + min(best[i−1][j], best[i][j−1]).",
        "The first row and column have only one way in; fill them as running sums.",
    ],
    insight="Grid DP choosing the cheaper predecessor.",
    time="O(m·n)", space="O(n)",
    pitfalls=["Using greedy local choices."],
)
def min_path_sum(grid):
    n = len(grid[0])
    row = [0] + [float("inf")] * (n - 1)
    for r in grid:
        for j in range(n):
            row[j] = r[j] + (min(row[j], row[j - 1]) if j else row[j])
    return row[-1]


@problem(
    slug="longest-palindromic-subsequence", title="Longest Palindromic Subsequence", difficulty="Medium", pattern=D2,
    tags=["String", "Dynamic Programming"],
    sig="longestPalindromeSubseq(self, s: str) -> int",
    desc="""Return the length of the longest subsequence of `s` that reads the same forwards and backwards.""",
    constraints=["1 ≤ len(s) ≤ 1000", "lowercase letters"],
    samples=[("bbbab",), ("cbbd",)],
    gen=lambda r: (r.word(r.randint(1, 11), "abc"),),
    brute=lambda s: max(len(t) for t in ("".join(s[i] for i in c) for c in _subsets_idx(len(s))) if t == t[::-1]),
    hints=[
        "Let L[i][j] be the answer for the substring s[i..j].",
        "If s[i] == s[j], both ends join the palindrome: L[i][j] = L[i+1][j−1] + 2.",
        "Otherwise drop one end: L[i][j] = max(L[i+1][j], L[i][j−1]). Fill by increasing length.",
    ],
    insight="Interval DP (equivalently, the LCS of s and its reverse).",
    time="O(n²)", space="O(n²) or O(n)",
    pitfalls=["Confusing it with the longest palindromic substring (contiguous)."],
)
def longest_palindrome_subseq(s):
    n = len(s)
    L = [0] * n
    for i in range(n - 1, -1, -1):
        prev_diag, L[i] = 0, 1
        for j in range(i + 1, n):
            old = L[j]
            L[j] = prev_diag + 2 if s[i] == s[j] else max(L[j], L[j - 1])
            prev_diag = old
    return L[-1]


def _interleave_brute(a, b, c):
    @lru_cache(None)
    def go(i, j):
        if i + j == len(c):
            return i == len(a) and j == len(b)
        return (i < len(a) and a[i] == c[i + j] and go(i + 1, j)) or (j < len(b) and b[j] == c[i + j] and go(i, j + 1))
    return len(a) + len(b) == len(c) and go(0, 0)


@problem(
    slug="interleaving-string", title="Interleaving String", difficulty="Medium", pattern=D2, tags=["String", "Dynamic Programming"],
    sig="isInterleave(self, s1: str, s2: str, s3: str) -> bool",
    desc="""Return `true` if `s3` can be formed by interleaving `s1` and `s2`: merging their characters while keeping each string's own order.""",
    constraints=["0 ≤ len(s1), len(s2) ≤ 100", "0 ≤ len(s3) ≤ 200", "lowercase letters"],
    samples=[("aabcc", "dbbca", "aadbbcbcac"), ("aabcc", "dbbca", "aadbbbaccc"), ("", "", "")],
    gen=lambda r: (lambda a, b: (a, b, "".join(r.sample(a + b, len(a + b))) if r.random() < 0.5 else _shuffle_keep(r, a, b)))(r.word(r.randint(0, 5), "ab"), r.word(r.randint(0, 5), "ab")),
    brute=_interleave_brute,
    hints=[
        "If lengths don't add up, the answer is false.",
        "Let ok[i][j] mean s3[:i+j] is an interleaving of s1[:i] and s2[:j].",
        "ok[i][j] is true if (ok[i−1][j] and s1[i−1] == s3[i+j−1]) or (ok[i][j−1] and s2[j−1] == s3[i+j−1]).",
    ],
    insight="2D DP over how many characters of each string have been used.",
    time="O(m·n)", space="O(n)",
    pitfalls=["Greedy matching, which fails when both strings offer the same next character."],
)
def is_interleave(s1, s2, s3):
    m, n = len(s1), len(s2)
    if m + n != len(s3):
        return False
    ok = [False] * (n + 1)
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0 and j == 0:
                ok[j] = True
            else:
                ok[j] = (i > 0 and ok[j] and s1[i - 1] == s3[i + j - 1]) or (j > 0 and ok[j - 1] and s2[j - 1] == s3[i + j - 1])
    return ok[n]


def _shuffle_keep(r, a, b):
    out, i, j = [], 0, 0
    while i < len(a) or j < len(b):
        if j == len(b) or (i < len(a) and r.random() < 0.5):
            out.append(a[i]); i += 1
        else:
            out.append(b[j]); j += 1
    return "".join(out)


@problem(
    slug="distinct-subsequences", title="Distinct Subsequences", difficulty="Hard", pattern=D2, tags=["String", "Dynamic Programming"],
    sig="numDistinct(self, s: str, t: str) -> int",
    desc="""Return the number of distinct ways to pick a subsequence of `s` that equals `t` (different index choices count separately).""",
    constraints=["1 ≤ len(s), len(t) ≤ 1000", "letters only", "the answer fits in a 32-bit signed integer"],
    samples=[("rabbbit", "rabbit"), ("babgbag", "bag")],
    gen=lambda r: (r.word(r.randint(1, 10), "ab"), r.word(r.randint(1, 3), "ab")),
    brute=lambda s, t: sum(1 for c in combinations(range(len(s)), len(t)) if "".join(s[i] for i in c) == t),
    hints=[
        "Let ways[j] be the number of ways to form t[:j] from the part of s processed so far.",
        "ways[0] = 1: the empty target can always be formed.",
        "For each character of s, update j from high to low: if s[i] == t[j−1], ways[j] += ways[j−1].",
    ],
    insight="Count subsequence matches with a 1D DP updated right to left.",
    time="O(|s| · |t|)", space="O(|t|)",
    pitfalls=["Updating left to right, which reuses the same character of s twice."],
)
def num_distinct(s, t):
    ways = [1] + [0] * len(t)
    for c in s:
        for j in range(len(t), 0, -1):
            if t[j - 1] == c:
                ways[j] += ways[j - 1]
    return ways[-1]


def _balloons_brute(nums):
    @lru_cache(None)
    def go(state):
        if not state:
            return 0
        best = 0
        for i in range(len(state)):
            left = state[i - 1] if i else 1
            right = state[i + 1] if i + 1 < len(state) else 1
            best = max(best, left * state[i] * right + go(state[:i] + state[i + 1:]))
        return best
    return go(tuple(nums))


@problem(
    slug="burst-balloons", title="Burst Balloons", difficulty="Hard", pattern=D2, tags=["Array", "Dynamic Programming"],
    sig="maxCoins(self, nums: list[int]) -> int",
    desc="""Balloon `i` has the number `nums[i]`. Bursting balloon `i` earns `left × nums[i] × right`, where `left` and `right` are its current neighbors (a missing neighbor counts as 1). Burst all balloons and return the maximum total coins.""",
    constraints=["1 ≤ n ≤ 300", "0 ≤ nums[i] ≤ 100"],
    samples=[([3, 1, 5, 8],), ([1, 5],)],
    gen=lambda r: (r.ints(r.randint(1, 7), 0, 9),),
    brute=_balloons_brute,
    hints=[
        "Choosing the first balloon to burst changes everyone's neighbors, which is messy.",
        "Instead choose the LAST balloon to burst in an interval: its neighbors are then the interval's boundaries.",
        "Pad with 1s; best(l, r) = max over k of best(l, k) + best(k, r) + v[l]·v[k]·v[r], for open intervals (l, r).",
    ],
    insight="Interval DP on the last balloon burst between two fixed boundaries.",
    time="O(n³)", space="O(n²)",
    pitfalls=["Choosing the first balloon to burst, which doesn't split into independent subproblems."],
)
def max_coins(nums):
    v = [1] + list(nums) + [1]
    n = len(v)
    best = [[0] * n for _ in range(n)]
    for length in range(2, n):
        for l in range(n - length):
            r = l + length
            best[l][r] = max(best[l][k] + best[k][r] + v[l] * v[k] * v[r] for k in range(l + 1, r))
    return best[0][n - 1]


@problem(
    slug="maximal-square", title="Maximal Square", difficulty="Medium", pattern=D2, tags=["Array", "Dynamic Programming", "Matrix"],
    sig="maximalSquare(self, matrix: list[list[str]]) -> int",
    desc="""`matrix` contains `'0'` and `'1'` characters. Return the **area** of the largest square containing only `'1'`s.""",
    constraints=["1 ≤ m, n ≤ 300"],
    samples=[([["1", "0", "1", "0", "0"], ["1", "0", "1", "1", "1"], ["1", "1", "1", "1", "1"], ["1", "0", "0", "1", "0"]],),
             ([["0", "1"], ["1", "0"]],), ([["0"]],)],
    gen=lambda r: (lambda m, n: ([[r.choice("0111") for _ in range(n)] for _ in range(m)],))(r.randint(1, 5), r.randint(1, 5)),
    brute=lambda M: max([0] + [k * k for i in range(len(M)) for j in range(len(M[0])) for k in range(1, min(len(M) - i, len(M[0]) - j) + 1) if all(M[x][y] == "1" for x in range(i, i + k) for y in range(j, j + k))]),
    hints=[
        "Let side[i][j] be the largest square of 1s whose bottom-right corner is (i, j).",
        "A square at (i, j) is limited by the squares ending above, to the left, and diagonally up-left.",
        "side[i][j] = 1 + min(top, left, top-left) for a '1' cell, else 0. The answer is the max side squared.",
    ],
    insight="Each square's size depends on its three neighbors' squares.",
    time="O(m·n)", space="O(n)",
    pitfalls=["Returning the side length instead of the area."],
)
def maximal_square(matrix):
    n = len(matrix[0])
    prev = [0] * (n + 1)
    best = 0
    for row in matrix:
        cur = [0] * (n + 1)
        for j in range(1, n + 1):
            if row[j - 1] == "1":
                cur[j] = 1 + min(prev[j], cur[j - 1], prev[j - 1])
                best = max(best, cur[j])
        prev = cur
    return best * best


@problem(
    slug="triangle", title="Triangle", difficulty="Medium", pattern=D2, tags=["Array", "Dynamic Programming"],
    sig="minimumTotal(self, triangle: list[list[int]]) -> int",
    desc="""Return the minimum path sum from the top of `triangle` to the bottom. From index `i` in one row you may move to index `i` or `i + 1` in the next row.""",
    constraints=["1 ≤ rows ≤ 200", "row i has i + 1 numbers", "-10⁴ ≤ values ≤ 10⁴"],
    samples=[([[2], [3, 4], [6, 5, 7], [4, 1, 8, 3]],), ([[-10]],)],
    gen=lambda r: ([r.ints(i + 1, -9, 9) for i in range(r.randint(1, 6))],),
    brute=lambda t: min(sum(t[i][p] for i, p in enumerate(path)) for path in product(*[range(len(row)) for row in t]) if path[0] == 0 and all(b - a in (0, 1) for a, b in zip(path, path[1:]))),
    hints=[
        "Going top-down, each cell has up to two parents; going bottom-up, each cell has exactly two children.",
        "Start from the last row and move upward.",
        "best[i] = row[i] + min(best[i], best[i + 1]); after the top row, best[0] is the answer.",
    ],
    insight="Bottom-up DP needs no special edge cases.",
    time="O(n²)", space="O(n)",
    pitfalls=["Greedily taking the smaller child at each step."],
)
def minimum_total(triangle):
    best = list(triangle[-1])
    for row in reversed(triangle[:-1]):
        best = [row[i] + min(best[i], best[i + 1]) for i in range(len(row))]
    return best[0]


@problem(
    slug="min-cost-climbing-stairs", title="Min Cost Climbing Stairs", difficulty="Easy", pattern=D1, tags=["Array", "Dynamic Programming"],
    sig="minCostClimbingStairs(self, cost: list[int]) -> int",
    desc="""Stepping on stair `i` costs `cost[i]`; from there you can climb one or two stairs. You may start on stair 0 or 1. Return the minimum cost to reach the top (just past the last stair).""",
    constraints=["2 ≤ len(cost) ≤ 1000", "0 ≤ cost[i] ≤ 999"],
    samples=[([10, 15, 20],), ([1, 100, 1, 1, 1, 100, 1, 1, 100, 1],)],
    gen=lambda r: (r.ints(r.randint(2, 10), 0, 20),),
    brute=lambda cost: (lambda f: f(f, len(cost)))(lru_cache(None)(lambda f, i: 0 if i < 2 else min(f(f, i - 1) + cost[i - 1], f(f, i - 2) + cost[i - 2]))),
    hints=[
        "Reaching step i costs the cheaper of coming from i − 1 or i − 2.",
        "reach[i] = min(reach[i−1] + cost[i−1], reach[i−2] + cost[i−2]), with reach[0] = reach[1] = 0.",
        "The top is index len(cost); keep only the last two values.",
    ],
    insight="A Fibonacci-shaped DP with costs.",
    time="O(n)", space="O(1)",
    pitfalls=["Treating the last stair as the top."],
)
def min_cost_climbing(cost):
    a = b = 0
    for i in range(2, len(cost) + 1):
        a, b = b, min(b + cost[i - 1], a + cost[i - 2])
    return b


def _cooldown_brute(prices):
    @lru_cache(None)
    def go(i, holding):
        if i >= len(prices):
            return 0
        skip = go(i + 1, holding)
        if holding:
            return max(skip, prices[i] + go(i + 2, False))
        return max(skip, -prices[i] + go(i + 1, True))
    return go(0, False)


@problem(
    slug="best-time-to-buy-and-sell-stock-with-cooldown", title="Best Time to Buy and Sell Stock with Cooldown", difficulty="Medium",
    pattern=D1, tags=["Array", "Dynamic Programming"],
    sig="maxProfit(self, prices: list[int]) -> int",
    desc="""`prices[i]` is a stock's price on day `i`. You may complete any number of buy/sell transactions, but hold at most one share at a time, and after selling you must wait one day (cooldown) before buying again. Return the maximum profit.""",
    constraints=["1 ≤ len(prices) ≤ 5000", "0 ≤ prices[i] ≤ 1000"],
    samples=[([1, 2, 3, 0, 2],), ([1],)],
    gen=lambda r: (r.ints(r.randint(1, 12), 0, 10),),
    brute=_cooldown_brute,
    hints=[
        "Each day you're in one of three states: holding a share, just sold (cooldown), or free to buy.",
        "Write how each state's best profit carries over to the next day.",
        "hold = max(hold, free − price); sold = hold + price; free = max(free, previous sold). Answer is max(sold, free).",
    ],
    insight="A small state machine DP models the cooldown.",
    time="O(n)", space="O(1)",
    pitfalls=["Allowing a buy on the day right after a sell."],
)
def max_profit_cooldown(prices):
    hold, sold, free = float("-inf"), 0, 0
    for p in prices:
        hold, sold, free = max(hold, free - p), hold + p, max(free, sold)
    return max(sold, free)


def _bounded_product_input(r, n):
    nums = [r.choice([1, -1, 1, -1, 0]) for _ in range(n)]
    for i in r.sample(range(n), 20):
        nums[i] = r.choice([2, -2])
    return (nums,)


EXTRA = {
    "0-1-knapsack": {
        "edge": [(0, [1], [5]), (5, [5], [10]), (4, [5], [10]), (10, [1, 1, 1], [0, 0, 0])],
        "edge_nb": [(1000, [r % 97 + 1 for r in range(100)], [(r * 37) % 10001 for r in range(100)])],
        "large": [lambda r: (1000, r.ints(100, 1, 1000), r.ints(100, 0, 10000))],
    },
    "coin-change": {
        "edge": [([2], 1), ([1], 1), ([2147483647], 2), ([186, 419, 83, 408], 6249), ([3, 7], 11)],
        "large": [lambda r: ([1], 10000), lambda r: (r.distinct(12, 1, 500), 10000)],
    },
    "coin-change-ii": {
        "edge": [(0, [7]), (1, [2]), (5000, [5000]), (7, [2, 3, 5])],
        "large": [lambda r: (5000, r.distinct(100, 1, 5000)), lambda r: (5000, [1, 2])],
    },
    "n-th-tribonacci-number": {"edge": [(3,), (10,)]},
    "partition-equal-subset-sum": {
        "edge": [([1],), ([1, 1],), ([2, 2, 3, 5],), ([100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 99, 97],)],
        "large": [lambda r: (r.ints(200, 1, 100),), lambda r: ([100] * 199 + [1],)],
    },
    "counting-bits": {"edge": [(1,), (3,), (8,)], "large": [lambda r: (40000,)]},
    "house-robber": {
        "edge": [([0],), ([400],), ([2, 1, 1, 2],), ([0, 0, 0],)],
        "edge_nb": [([r * 7 % 401 for r in range(100)],)],
    },
    "house-robber-ii": {
        "edge": [([1, 2],), ([0],), ([200, 3, 140, 20, 10],), ([1, 3, 1, 3, 100],)],
        "edge_nb": [([r * 13 % 1001 for r in range(100)],)],
    },
    "maximum-product-subarray": {
        "edge": [([-2],), ([0],), ([-2, 0, -1],), ([-1, -1],), ([2, -5, -2, -4, 3],), ([0, 2],)],
        "large": [lambda r: _bounded_product_input(r, 15000)],
    },
    "word-break": {
        "edge": [("a", ["a"]), ("a", ["b"]), ("aaaaaaa", ["aaaa", "aaa"]), ("cars", ["car", "ca", "rs"])],
        "edge_nb": [("a" * 299 + "b", ["a", "aa", "aaa", "aaaa", "aaaaa", "aaaaaa", "aaaaaaa", "aaaaaaaa", "aaaaaaaaa", "aaaaaaaaaa"])],
    },
    "palindromic-substrings": {
        "edge": [("a",), ("aa",), ("ab",), ("aba",)],
        "large": [lambda r: ("a" * 1000,), lambda r: (r.word(1000, "ab"),)],
    },
    "longest-palindromic-substring": {
        "edge": [("a",), ("ac",), ("bb",), ("abacdfgdcaba",), ("aaaa",)],
        "large": [lambda r: ("a" * 1000,), lambda r: (r.word(1000, "abc"),)],
    },
    "longest-increasing-subsequence": {
        "edge": [([1],), ([2, 2],), ([1, 2],), ([5, 4, 3, 2, 1],), ([4, 10, 4, 3, 8, 9],)],
        "large": [lambda r: (r.ints(2500, -10000, 10000),), lambda r: (list(range(2500)),)],
    },
    "edit-distance": {
        "edge": [("", ""), ("a", ""), ("", "abc"), ("a", "a"), ("abc", "cba")],
        "large": [lambda r: (r.word(400, "abc"), r.word(400, "abc"))],
    },
    "unique-paths": {"edge": [(1, 100), (100, 1), (2, 2), (17, 17)]},
    "decode-ways": {
        "edge": [("0",), ("1",), ("10",), ("27",), ("100",), ("2101",), ("226",)],
        "large": [lambda r: ("1" * 40,), lambda r: ("10" * 50,)],
    },
    "minimum-path-sum": {
        "edge": [([[0]],), ([[5, 1, 1]],), ([[1], [2], [3]],), ([[200, 0], [0, 200]],)],
        "large": [lambda r: ([r.ints(150, 0, 200) for _ in range(150)],)],
    },
    "longest-palindromic-subsequence": {
        "edge": [("a",), ("ab",), ("aaaa",), ("abcba",)],
        "large": [lambda r: (r.word(700, "abc"),)],
    },
    "interleaving-string": {
        "edge": [("", "", "a"), ("a", "", "a"), ("", "b", "b"), ("a", "b", "ab"), ("a", "b", "ba"), ("a", "b", "aa"), ("aa", "ab", "aaba")],
        "edge_nb": [("a" * 100, "a" * 99 + "b", "a" * 199 + "b"), ("a" * 100, "a" * 100, "a" * 199 + "b")],
    },
    "distinct-subsequences": {
        "edge": [("a", "a"), ("a", "b"), ("aaa", "a"), ("aaa", "aaaa"), ("ddd", "dd")],
        "edge_nb": [("a" * 1000, "a" * 997)],
    },
    "burst-balloons": {
        "edge": [([5],), ([0],), ([0, 0, 0],), ([100, 100],), ([7, 9, 8, 0, 7, 1, 3, 5, 5, 2, 3],)],
        "large": [lambda r: (r.ints(90, 0, 100),)],
    },
    "maximal-square": {
        "edge": [([["1"]],), ([["0", "0"]],), ([["1", "1"], ["1", "1"]],), ([["1", "1", "1"], ["1", "1", "0"]],)],
        "large": [lambda r: ([[r.choice("1111110") for _ in range(150)] for _ in range(150)],)],
    },
    "triangle": {
        "edge": [([[5]],), ([[-1], [2, 3]],), ([[-1], [-2, -3]],), ([[0], [10000, -10000]],)],
        "large": [lambda r: ([r.ints(i + 1, -9999, 9999) for i in range(150)],)],
    },
    "min-cost-climbing-stairs": {
        "edge": [([0, 0],), ([999, 999],), ([0, 1, 2, 2],), ([1, 0, 0, 1],)],
        "large": [lambda r: (r.ints(1000, 0, 999),)],
    },
    "best-time-to-buy-and-sell-stock-with-cooldown": {
        "edge": [([5],), ([1, 2],), ([2, 1],), ([1, 2, 4],), ([6, 1, 6, 4, 3, 0, 2],)],
        "large": [lambda r: (r.ints(5000, 0, 1000),)],
    },
}
