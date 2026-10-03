from collections import Counter, defaultdict, deque

from catalog_lib import problem

P = "sliding-window"


def _subarrays(nums):
    for i in range(len(nums)):
        for j in range(i, len(nums)):
            yield i, j, nums[i:j + 1]


@problem(
    slug="longest-repeating-character-replacement", title="Longest Repeating Character Replacement", difficulty="Medium", pattern=P,
    tags=["String", "Sliding Window", "Hash Table"],
    sig="characterReplacement(self, s: str, k: int) -> int",
    desc="""You may change at most `k` characters of the uppercase string `s` into any other uppercase letter. Return the length of the longest substring that can be made of one repeated letter.""",
    constraints=["1 ≤ len(s) ≤ 10⁵", "s has uppercase letters", "0 ≤ k ≤ len(s)"],
    samples=[("ABAB", 2), ("AABABBA", 1)],
    tests=[("A", 0), ("ABCD", 0), ("AAAA", 2)],
    gen=lambda r: (r.word(r.randint(1, 20), "ABC"), r.randint(0, 4)),
    brute=lambda s, k: max(j - i + 1 for i in range(len(s)) for j in range(i, len(s)) if (j - i + 1) - max(Counter(s[i:j + 1]).values()) <= k),
    hints=[
        "A window can become all one letter if its length minus the count of its most common letter is at most k.",
        "Grow a window to the right while tracking letter counts.",
        "When the window needs more than k changes, move its left edge forward. The largest valid window size is the answer (the max count never needs to decrease for this to work).",
    ],
    insight="Window length − most frequent letter count = changes needed; keep it ≤ k while sliding.",
    time="O(n)", space="O(1) for 26 letters",
    pitfalls=["Recomputing the most frequent count from scratch on every step, which is slower."],
)
def char_replacement(s, k):
    counts, left, top, best = Counter(), 0, 0, 0
    for right, c in enumerate(s):
        counts[c] += 1
        top = max(top, counts[c])
        while right - left + 1 - top > k:
            counts[s[left]] -= 1
            left += 1
        best = max(best, right - left + 1)
    return best


def _min_window_brute(s, t):
    need, best = Counter(t), ""
    for i in range(len(s)):
        for j in range(i, len(s)):
            sub = s[i:j + 1]
            if not (need - Counter(sub)) and (not best or len(sub) < len(best)):
                best = sub
    return best


@problem(
    slug="minimum-window-substring", title="Minimum Window Substring", difficulty="Hard", pattern=P,
    tags=["String", "Sliding Window", "Hash Table"],
    sig="minWindow(self, s: str, t: str) -> str",
    desc="""Return the **shortest substring** of `s` that contains every character of `t`, including duplicates (if `t` has two `a`s, the window needs two `a`s). If no such window exists, return `""`.

The tests are built so the shortest window is unique (if several windows tie, return the one that starts first).""",
    constraints=["1 ≤ len(s), len(t) ≤ 10⁵", "upper- and lowercase letters"],
    samples=[("ADOBECODEBANC", "ABC"), ("a", "a"), ("a", "aa")],
    tests=[("ab", "b"), ("bba", "ab"), ("aaflslflsldkalskaaa", "aaa")],
    gen=lambda r: (r.word(r.randint(1, 15), "abc"), r.word(r.randint(1, 3), "abc")),
    brute=_min_window_brute,
    hints=[
        "Expand a window until it covers t, then shrink it from the left as long as it still covers t.",
        "Track how many of t's characters (with multiplicity) are still missing from the window.",
        "Each time the window becomes valid, record it if it's shorter than the best, then drop the leftmost character and continue expanding.",
    ],
    insight="Expand to satisfy, shrink to minimize: each pointer moves at most n times.",
    time="O(len(s) + len(t))", space="O(alphabet)",
    pitfalls=["Ignoring duplicate characters in t.", "Comparing whole frequency maps on every step, which is slow."],
)
def min_window(s, t):
    need = Counter(t)
    missing, left, best = len(t), 0, (0, float("inf"))
    for right, c in enumerate(s):
        if need[c] > 0:
            missing -= 1
        need[c] -= 1
        if missing == 0:
            while need[s[left]] < 0:
                need[s[left]] += 1
                left += 1
            if right - left < best[1] - best[0]:
                best = (left, right)
            need[s[left]] += 1
            missing += 1
            left += 1
    return "" if best[1] == float("inf") else s[best[0]: best[1] + 1]


@problem(
    slug="sliding-window-maximum", title="Sliding Window Maximum", difficulty="Hard", pattern=P,
    tags=["Array", "Sliding Window", "Monotonic Queue", "Heap"],
    sig="maxSlidingWindow(self, nums: list[int], k: int) -> list[int]",
    desc="""A window of size `k` slides over `nums` from left to right, one position at a time. Return the maximum of each window.""",
    constraints=["1 ≤ len(nums) ≤ 10⁵", "-10⁴ ≤ nums[i] ≤ 10⁴", "1 ≤ k ≤ len(nums)"],
    samples=[([1, 3, -1, -3, 5, 3, 6, 7], 3), ([1], 1)],
    tests=[([9, 8, 7, 6], 2), ([1, 2, 3], 3)],
    gen=lambda r: (lambda nums: (nums, r.randint(1, len(nums))))(r.ints(r.randint(1, 30), -20, 20)),
    brute=lambda nums, k: [max(nums[i:i + k]) for i in range(len(nums) - k + 1)],
    hints=[
        "Recomputing the max for each window is O(n·k). Which elements can never be a future maximum?",
        "An element smaller than a newer element to its right can never be the max again while that newer one is in the window.",
        "Keep a deque of indices with decreasing values: pop smaller values from the back before pushing, drop the front when it leaves the window, and read the max from the front.",
    ],
    insight="A monotonic deque keeps only possible maxima, giving O(1) amortized work per element.",
    time="O(n)", space="O(k)",
    pitfalls=["Storing values instead of indices, which makes it impossible to tell when the front leaves the window."],
)
def max_sliding_window(nums, k):
    dq, out = deque(), []
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out


@problem(
    slug="subarrays-with-k-different-integers", title="Subarrays with K Different Integers", difficulty="Hard", pattern=P,
    tags=["Array", "Sliding Window", "Hash Table"],
    sig="subarraysWithKDistinct(self, nums: list[int], k: int) -> int",
    desc="""Return the number of contiguous subarrays of `nums` that contain **exactly** `k` distinct integers.""",
    constraints=["1 ≤ len(nums) ≤ 2 × 10⁴", "1 ≤ nums[i], k ≤ len(nums)"],
    samples=[([1, 2, 1, 2, 3], 2), ([1, 2, 1, 3, 4], 3)],
    tests=[([1], 1), ([1, 1, 1], 2), ([2, 2, 2], 1)],
    gen=lambda r: (r.ints(r.randint(1, 20), 1, 4), r.randint(1, 4)),
    brute=lambda nums, k: sum(len(set(sub)) == k for _, _, sub in _subarrays(nums)),
    hints=[
        "\"Exactly k\" is awkward for a sliding window, but \"at most k\" is easy.",
        "Count subarrays with at most k distinct values: for each right end, the window [left, right] is the longest valid one, contributing right − left + 1 subarrays.",
        "The answer is atMost(k) − atMost(k − 1).",
    ],
    insight="Exactly k = at most k minus at most k − 1, and each \"at most\" count is a standard window.",
    time="O(n)", space="O(n)",
    pitfalls=["Trying to maintain \"exactly k\" with a single window, which misses many subarrays."],
)
def subarrays_k_distinct(nums, k):
    def at_most(m):
        counts, left, total = defaultdict(int), 0, 0
        for right, x in enumerate(nums):
            counts[x] += 1
            while len(counts) > m:
                counts[nums[left]] -= 1
                if counts[nums[left]] == 0:
                    del counts[nums[left]]
                left += 1
            total += right - left + 1
        return total

    return at_most(k) - at_most(k - 1)


@problem(
    slug="repeated-dna-sequences", title="Repeated DNA Sequences", difficulty="Medium", pattern=P,
    tags=["String", "Sliding Window", "Hash Table", "Rolling Hash"],
    sig="findRepeatedDnaSequences(self, s: str) -> list[str]",
    desc="""A DNA string is made of the letters `A`, `C`, `G` and `T`. Return every 10-letter substring that occurs **more than once** in `s`, in any order, each listed once.""",
    constraints=["1 ≤ len(s) ≤ 10⁵", "s has only A, C, G, T"],
    samples=[("AAAAACCCCCAAAAACCCCCCAAAAAGGGTTT",), ("AAAAAAAAAAAAA",)],
    tests=[("ACGT",), ("ACGTACGTACGTACGT",)],
    gen=lambda r: (r.word(r.randint(5, 40), "AC"),),
    compare="unordered",
    brute=lambda s: sorted({s[i:i + 10] for i in range(len(s) - 9) if s.count(s[i:i + 10]) > 1 or any(s[j:j + 10] == s[i:i + 10] for j in range(len(s) - 9) if j != i)}),
    hints=[
        "Every window of length 10 is a candidate. How do you know whether you've seen it before?",
        "Slide a 10-letter window across s and store each window in a set of seen sequences.",
        "When a window is already in the seen set, add it to a result set (so it's reported once). A rolling hash or 2-bit encoding avoids building strings, but a set of strings is fine too.",
    ],
    insight="A fixed-size sliding window plus a hash set finds repeats in one pass.",
    time="O(n) windows (O(10n) with string slicing)", space="O(n)",
    pitfalls=["Reporting the same sequence several times when it appears three or more times."],
)
def repeated_dna(s):
    seen, out = set(), set()
    for i in range(len(s) - 9):
        w = s[i:i + 10]
        if w in seen:
            out.add(w)
        seen.add(w)
    return sorted(out)


def _is_subseq(t, s):
    it = iter(s)
    return all(c in it for c in t)


def _min_window_subseq_brute(s1, s2):
    best = ""
    for i in range(len(s1)):
        for j in range(i, len(s1)):
            sub = s1[i:j + 1]
            if _is_subseq(s2, sub) and (not best or len(sub) < len(best)):
                best = sub
    return best


@problem(
    slug="minimum-window-subsequence", title="Minimum Window Subsequence", difficulty="Hard", pattern=P,
    tags=["String", "Sliding Window", "Dynamic Programming"],
    sig="minWindow(self, s1: str, s2: str) -> str",
    desc="""Return the shortest substring of `s1` that contains `s2` as a **subsequence** (characters of `s2` in order, not necessarily adjacent).

If there are several shortest windows, return the one that starts first. If there is none, return `""`.""",
    constraints=["1 ≤ len(s1) ≤ 2 × 10⁴", "1 ≤ len(s2) ≤ 100", "lowercase letters"],
    samples=[("abcdebdde", "bde"), ("jmeqksfrsdcmsiwvaovztaqenprpvnbstl", "u")],
    tests=[("abc", "abc"), ("aaa", "aa"), ("cnhczmccqouqadqtmjjzl", "mm")],
    gen=lambda r: (r.word(r.randint(1, 15), "abc"), r.word(r.randint(1, 3), "abc")),
    brute=_min_window_subseq_brute,
    hints=[
        "Scan s1 forward matching s2 greedily; when s2 is fully matched, you've found a window end.",
        "From that end, walk backwards matching s2 in reverse to find the latest possible start, which gives the shortest window ending there.",
        "Record the window, then restart the forward scan just after that start. Keep the shortest window found.",
    ],
    insight="A forward pass finds a valid end; a backward pass tightens the start. Repeating covers all candidates.",
    time="O(len(s1) · len(s2))", space="O(1)",
    pitfalls=["Treating s2 as a set of characters instead of an ordered subsequence."],
)
def min_window_subsequence(s1, s2):
    best, i = "", 0
    while i < len(s1):
        k = 0
        while i < len(s1):
            if s1[i] == s2[k]:
                k += 1
                if k == len(s2):
                    break
            i += 1
        if i == len(s1):
            break
        end, k = i, len(s2) - 1
        while k >= 0:
            if s1[i] == s2[k]:
                k -= 1
            i -= 1
        start = i + 1
        if not best or end - start + 1 < len(best):
            best = s1[start:end + 1]
        i = start + 1
    return best


@problem(
    slug="minimum-size-subarray-sum", title="Minimum Size Subarray Sum", difficulty="Medium", pattern=P,
    tags=["Array", "Sliding Window", "Prefix Sum"],
    sig="minSubArrayLen(self, target: int, nums: list[int]) -> int",
    desc="""`nums` holds positive integers. Return the length of the shortest contiguous subarray whose sum is **at least** `target`, or `0` if none exists.""",
    constraints=["1 ≤ target ≤ 10⁹", "1 ≤ len(nums) ≤ 10⁵", "1 ≤ nums[i] ≤ 10⁴"],
    samples=[(7, [2, 3, 1, 2, 4, 3]), (4, [1, 4, 4]), (11, [1, 1, 1, 1, 1, 1, 1, 1])],
    gen=lambda r: (r.randint(1, 40), r.ints(r.randint(1, 20), 1, 9)),
    brute=lambda target, nums: min((j - i + 1 for i, j, sub in _subarrays(nums) if sum(sub) >= target), default=0),
    hints=[
        "All numbers are positive, so growing a window only increases its sum and shrinking only decreases it.",
        "Extend the right edge, adding to the running sum.",
        "While the sum is at least target, record the window length and remove the left element.",
    ],
    insight="Positive numbers make the window sum monotonic, so two pointers find the shortest valid window.",
    time="O(n)", space="O(1)",
    pitfalls=["Returning infinity instead of 0 when no window works."],
)
def min_subarray_len(target, nums):
    left, total, best = 0, 0, float("inf")
    for right, x in enumerate(nums):
        total += x
        while total >= target:
            best = min(best, right - left + 1)
            total -= nums[left]
            left += 1
    return 0 if best == float("inf") else best


@problem(
    slug="fruit-into-baskets", title="Fruit Into Baskets", difficulty="Medium", pattern=P, tags=["Array", "Sliding Window", "Hash Table"],
    sig="totalFruit(self, fruits: list[int]) -> int",
    desc="""Trees in a row each grow one type of fruit, `fruits[i]`. You have two baskets, and each basket holds only one type (but any amount). Starting at any tree, you pick one fruit from every tree moving right, and stop when a fruit doesn't fit in either basket.

Return the maximum number of fruits you can pick.""",
    constraints=["1 ≤ len(fruits) ≤ 10⁵", "0 ≤ fruits[i] < len(fruits)"],
    samples=[([1, 2, 1],), ([0, 1, 2, 2],), ([1, 2, 3, 2, 2],)],
    tests=[([3, 3, 3, 1, 2, 1, 1, 2, 3, 3, 4],), ([5],)],
    gen=lambda r: (r.ints(r.randint(1, 25), 0, 3),),
    brute=lambda fruits: max(len(sub) for _, _, sub in _subarrays(fruits) if len(set(sub)) <= 2),
    hints=[
        "You're looking for the longest contiguous run that contains at most two distinct values.",
        "Slide a window and count the fruit types inside it.",
        "When a third type enters, move the left edge forward until one type disappears from the window.",
    ],
    insight="Longest window with at most 2 distinct values: the classic at-most-k window.",
    time="O(n)", space="O(1)",
    pitfalls=["Resetting the window completely when a third type appears, which loses valid fruits."],
)
def total_fruit(fruits):
    counts, left, best = defaultdict(int), 0, 0
    for right, f in enumerate(fruits):
        counts[f] += 1
        while len(counts) > 2:
            counts[fruits[left]] -= 1
            if counts[fruits[left]] == 0:
                del counts[fruits[left]]
            left += 1
        best = max(best, right - left + 1)
    return best


def _freq_brute(nums, k):
    best = 0
    for target in nums:
        costs = sorted(target - x for x in nums if x <= target)
        used, count = 0, 0
        for c in costs:
            if used + c > k:
                break
            used, count = used + c, count + 1
        best = max(best, count)
    return best


@problem(
    slug="frequency-of-the-most-frequent-element", title="Frequency of the Most Frequent Element", difficulty="Medium", pattern=P,
    tags=["Array", "Sliding Window", "Sorting", "Greedy"],
    sig="maxFrequency(self, nums: list[int], k: int) -> int",
    desc="""In one operation you can increase any element of `nums` by 1. Using at most `k` operations in total, return the largest possible number of equal elements.""",
    constraints=["1 ≤ len(nums) ≤ 10⁵", "1 ≤ nums[i] ≤ 10⁵", "1 ≤ k ≤ 10⁵"],
    samples=[([1, 2, 4], 5), ([1, 4, 8, 13], 5), ([3, 9, 6], 2)],
    gen=lambda r: (r.ints(r.randint(1, 15), 1, 20), r.randint(1, 20)),
    brute=_freq_brute,
    hints=[
        "It's best to raise the elements just below some target value up to that value.",
        "Sort the array. For a window ending at index r, raising everything to nums[r] costs nums[r] · size − sum(window).",
        "Slide a window: shrink from the left while that cost exceeds k, and track the largest window size.",
    ],
    insight="After sorting, the cheapest group to equalize is a contiguous window whose top value is the target.",
    time="O(n log n)", space="O(1) besides sorting",
    pitfalls=["Integer overflow in other languages for the cost; in Python it's fine."],
)
def max_frequency(nums, k):
    nums = sorted(nums)
    left, total, best = 0, 0, 0
    for right, x in enumerate(nums):
        total += x
        while x * (right - left + 1) - total > k:
            total -= nums[left]
            left += 1
        best = max(best, right - left + 1)
    return best


@problem(
    slug="maximum-average-subarray-i", title="Maximum Average Subarray I", difficulty="Easy", pattern=P, tags=["Array", "Sliding Window"],
    sig="findMaxAverage(self, nums: list[int], k: int) -> float",
    desc="""Find the contiguous subarray of length exactly `k` with the largest average, and return that average. Answers within 10⁻⁵ are accepted.""",
    constraints=["1 ≤ k ≤ len(nums) ≤ 10⁵", "-10⁴ ≤ nums[i] ≤ 10⁴"],
    samples=[([1, 12, -5, -6, 50, 3], 4), ([5], 1)],
    tests=[([0, 4, 0, 3, 2], 1), ([-1, -2, -3], 3)],
    gen=lambda r: (lambda nums: (nums, r.randint(1, len(nums))))(r.ints(r.randint(1, 25), -50, 50)),
    compare="approx",
    brute=lambda nums, k: max(sum(nums[i:i + k]) for i in range(len(nums) - k + 1)) / k,
    hints=[
        "All windows have the same length, so the largest average belongs to the largest sum.",
        "Compute the sum of the first k elements.",
        "Slide the window: add the new element, subtract the one that left, and track the maximum sum. Divide by k at the end.",
    ],
    insight="A fixed-size window sum updates in O(1) per step.",
    time="O(n)", space="O(1)",
    pitfalls=["Using integer division."],
)
def find_max_average(nums, k):
    window = best = sum(nums[:k])
    for i in range(k, len(nums)):
        window += nums[i] - nums[i - k]
        best = max(best, window)
    return best / k


@problem(
    slug="diet-plan-performance", title="Diet Plan Performance", difficulty="Easy", pattern=P, tags=["Array", "Sliding Window"],
    sig="dietPlanPerformance(self, calories: list[int], k: int, lower: int, upper: int) -> int",
    desc="""A dieter eats `calories[i]` calories on day `i`. For every block of `k` consecutive days, let `T` be the total calories. If `T < lower` they lose a point; if `T > upper` they gain a point; otherwise nothing changes.

Starting from 0 points, return the final score.""",
    constraints=["1 ≤ k ≤ len(calories) ≤ 10⁵", "0 ≤ calories[i] ≤ 20000", "0 ≤ lower ≤ upper"],
    samples=[([1, 2, 3, 4, 5], 1, 3, 3), ([3, 2], 2, 0, 1), ([6, 5, 0, 0], 2, 1, 5)],
    gen=lambda r: (lambda c: (c, r.randint(1, len(c)), r.randint(0, 20), r.randint(20, 40)))(r.ints(r.randint(1, 20), 0, 10)),
    brute=lambda cal, k, lo, hi: sum((sum(cal[i:i + k]) > hi) - (sum(cal[i:i + k]) < lo) for i in range(len(cal) - k + 1)),
    hints=[
        "Every window of k consecutive days is scored independently.",
        "Keep a running sum for the current window instead of re-adding k values.",
        "Slide the window one day at a time, update the sum, and adjust the points against lower and upper.",
    ],
    insight="A fixed-length rolling sum scores every window in O(1).",
    time="O(n)", space="O(1)",
    pitfalls=["Scoring partial windows at the start."],
)
def diet_plan(calories, k, lower, upper):
    total = sum(calories[:k])
    points = 0
    for i in range(k - 1, len(calories)):
        if i >= k:
            total += calories[i] - calories[i - k]
        points += (total > upper) - (total < lower)
    return points


@problem(
    slug="count-subarrays-with-score-less-than-k", title="Count Subarrays With Score Less Than K", difficulty="Hard", pattern=P,
    tags=["Array", "Sliding Window", "Prefix Sum"],
    sig="countSubarrays(self, nums: list[int], k: int) -> int",
    desc="""The **score** of an array is its sum multiplied by its length. Given positive integers `nums`, return the number of non-empty contiguous subarrays with a score **strictly less than** `k`.""",
    constraints=["1 ≤ len(nums) ≤ 10⁵", "1 ≤ nums[i] ≤ 10⁵", "1 ≤ k ≤ 10¹⁵"],
    samples=[([2, 1, 4, 3, 5], 10), ([1, 1, 1], 5)],
    gen=lambda r: (r.ints(r.randint(1, 20), 1, 9), r.randint(1, 200)),
    brute=lambda nums, k: sum(sum(sub) * len(sub) < k for _, _, sub in _subarrays(nums)),
    hints=[
        "With positive numbers, extending a subarray only increases its score.",
        "For each right end, find the leftmost start whose score is still below k.",
        "Slide the window, shrinking while sum × length ≥ k; every start in the window gives a valid subarray, so add its length.",
    ],
    insight="Monotonic score means a sliding window counts all valid subarrays ending at each index.",
    time="O(n)", space="O(1)",
    pitfalls=["Using ≤ instead of < for the score limit."],
)
def count_score_less(nums, k):
    left, total, count = 0, 0, 0
    for right, x in enumerate(nums):
        total += x
        while total * (right - left + 1) >= k:
            total -= nums[left]
            left += 1
        count += right - left + 1
    return count


@problem(
    slug="count-substrings-with-k-frequency-characters-ii", title="Count Substrings With K-Frequency Characters II", difficulty="Hard",
    pattern=P, tags=["String", "Sliding Window", "Hash Table"],
    sig="numberOfSubstrings(self, s: str, k: int) -> int",
    desc="""Return the number of substrings of `s` in which **at least one** character appears **at least** `k` times.""",
    constraints=["1 ≤ len(s) ≤ 3 × 10⁵", "1 ≤ k ≤ len(s)", "lowercase letters"],
    samples=[("abacb", 2), ("abcde", 1)],
    tests=[("aaa", 2), ("ab", 3)],
    gen=lambda r: (r.word(r.randint(1, 15), "abc"), r.randint(1, 3)),
    brute=lambda s, k: sum(max(Counter(s[i:j + 1]).values()) >= k for i in range(len(s)) for j in range(i, len(s))),
    hints=[
        "If a substring qualifies, so does every longer substring with the same start.",
        "Count the complement: substrings where every character appears fewer than k times are easy to count with a window.",
        "Slide a window that never lets any character reach k occurrences; for each right end it contributes (right − left + 1) bad substrings. The answer is the total number of substrings minus the bad ones.",
    ],
    insight="Counting the substrings that fail is a clean sliding window; subtract from n(n + 1)/2.",
    time="O(n)", space="O(1) for 26 letters",
    pitfalls=["Trying to count \"at least one character ≥ k\" directly, which is much harder."],
)
def k_freq_substrings(s, k):
    counts, left, bad = Counter(), 0, 0
    for right, c in enumerate(s):
        counts[c] += 1
        while counts[c] >= k:
            counts[s[left]] -= 1
            left += 1
        bad += right - left + 1
    n = len(s)
    return n * (n + 1) // 2 - bad


def _concat_brute(s, words):
    w, total = len(words[0]), len(words[0]) * len(words)
    need = Counter(words)
    return [i for i in range(len(s) - total + 1) if Counter(s[i + j * w: i + (j + 1) * w] for j in range(len(words))) == need]


@problem(
    slug="substring-with-concatenation-of-all-words", title="Substring with Concatenation of All Words", difficulty="Hard", pattern=P,
    tags=["String", "Sliding Window", "Hash Table"],
    sig="findSubstring(self, s: str, words: list[str]) -> list[int]",
    desc="""All strings in `words` have the same length. A **concatenated substring** is a substring of `s` made of every word in `words` exactly once, in any order, back to back.

Return the starting indices of all concatenated substrings in `s`, in any order.""",
    constraints=["1 ≤ len(s) ≤ 10⁴", "1 ≤ len(words) ≤ 5000", "1 ≤ len(words[i]) ≤ 30", "lowercase letters"],
    samples=[("barfoothefoobarman", ["foo", "bar"]), ("wordgoodgoodgoodbestword", ["word", "good", "best", "word"]), ("barfoofoobarthefoobarman", ["bar", "foo", "the"])],
    tests=[("aaaaaa", ["aa", "aa"]), ("ab", ["abc"])],
    gen=lambda r: (lambda wl: (r.word(r.randint(1, 20), "ab"), r.words(r.randint(1, 3), wl, wl, "ab")))(r.randint(1, 2)),
    compare="unordered",
    brute=_concat_brute,
    hints=[
        "Every word has the same length w, so a candidate window has a fixed length: w × number of words.",
        "Split the problem by starting offset 0..w−1; for one offset, s becomes a sequence of w-length chunks.",
        "Slide a window over the chunks with a word-count map: add a chunk on the right, shrink from the left while some word is over-used, reset when a chunk isn't a word, and record windows that contain exactly all the words.",
    ],
    insight="Fixed word length lets you slide word-by-word, once per offset.",
    time="O(n · w)", space="O(number of words)",
    pitfalls=["Ignoring repeated words in the list.", "Only checking offsets that are multiples of w."],
)
def find_substring(s, words):
    w, k = len(words[0]), len(words)
    need, out = Counter(words), []
    for offset in range(w):
        left, have, used = offset, Counter(), 0
        for right in range(offset, len(s) - w + 1, w):
            chunk = s[right:right + w]
            if chunk not in need:
                have.clear()
                used, left = 0, right + w
                continue
            have[chunk] += 1
            used += 1
            while have[chunk] > need[chunk]:
                have[s[left:left + w]] -= 1
                used -= 1
                left += w
            if used == k:
                out.append(left)
                have[s[left:left + w]] -= 1
                used -= 1
                left += w
    return sorted(out)


@problem(
    slug="binary-subarrays-with-sum", title="Binary Subarrays With Sum", difficulty="Medium", pattern=P,
    tags=["Array", "Sliding Window", "Prefix Sum", "Hash Table"],
    sig="numSubarraysWithSum(self, nums: list[int], goal: int) -> int",
    desc="""`nums` contains only 0s and 1s. Return the number of non-empty contiguous subarrays whose sum equals `goal`.""",
    constraints=["1 ≤ len(nums) ≤ 3 × 10⁴", "nums[i] is 0 or 1", "0 ≤ goal ≤ len(nums)"],
    samples=[([1, 0, 1, 0, 1], 2), ([0, 0, 0, 0, 0], 0)],
    gen=lambda r: (r.ints(r.randint(1, 20), 0, 1), r.randint(0, 4)),
    brute=lambda nums, goal: sum(sum(sub) == goal for _, _, sub in _subarrays(nums)),
    hints=[
        "Zeros make \"exactly goal\" tricky for a single window.",
        "Count subarrays with sum at most goal using a window, for each right end.",
        "Answer = atMost(goal) − atMost(goal − 1). (A prefix-sum hash map also works.)",
    ],
    insight="Exactly = at most(goal) − at most(goal − 1), the same trick as \"exactly k distinct\".",
    time="O(n)", space="O(1)",
    pitfalls=["Calling atMost(−1): it should be 0."],
)
def binary_subarrays(nums, goal):
    def at_most(g):
        if g < 0:
            return 0
        left, total, count = 0, 0, 0
        for right, x in enumerate(nums):
            total += x
            while total > g:
                total -= nums[left]
                left += 1
            count += right - left + 1
        return count

    return at_most(goal) - at_most(goal - 1)


@problem(
    slug="permutation-in-string", title="Permutation in String", difficulty="Medium", pattern=P, tags=["String", "Sliding Window", "Hash Table"],
    sig="checkInclusion(self, s1: str, s2: str) -> bool",
    desc="""Return `True` if some rearrangement of `s1` appears as a contiguous substring of `s2`.""",
    constraints=["1 ≤ len(s1), len(s2) ≤ 10⁴", "lowercase letters"],
    samples=[("ab", "eidbaooo"), ("ab", "eidboaoo")],
    tests=[("abc", "ab"), ("a", "a"), ("adc", "dcda")],
    gen=lambda r: (r.word(r.randint(1, 4), "abc"), r.word(r.randint(1, 12), "abc")),
    brute=lambda s1, s2: any(Counter(s2[i:i + len(s1)]) == Counter(s1) for i in range(len(s2) - len(s1) + 1)),
    hints=[
        "A permutation of s1 has exactly the same letter counts as s1.",
        "Look at every window of s2 with length len(s1).",
        "Slide the window, updating letter counts in O(1), and compare against s1's counts (or track how many letters match).",
    ],
    insight="A fixed-size window with letter counts checks every candidate substring in O(1) each.",
    time="O(len(s2))", space="O(1) for 26 letters",
    pitfalls=["Sorting every window, which costs O(len(s1) log len(s1)) each."],
)
def check_inclusion(s1, s2):
    k = len(s1)
    if k > len(s2):
        return False
    need, window = Counter(s1), Counter(s2[:k])
    if window == need:
        return True
    for i in range(k, len(s2)):
        window[s2[i]] += 1
        window[s2[i - k]] -= 1
        if window[s2[i - k]] == 0:
            del window[s2[i - k]]
        if window == need:
            return True
    return False


@problem(
    slug="number-of-substrings-containing-all-three-characters", title="Number of Substrings Containing All Three Characters",
    difficulty="Medium", pattern=P, tags=["String", "Sliding Window", "Hash Table"],
    sig="numberOfSubstrings(self, s: str) -> int",
    desc="""`s` contains only the letters `a`, `b` and `c`. Return the number of substrings that contain **at least one** of each.""",
    constraints=["3 ≤ len(s) ≤ 5 × 10⁴", "s has only a, b, c"],
    samples=[("abcabc",), ("aaacb",), ("abc",)],
    gen=lambda r: (r.word(r.randint(3, 20), "abc"),),
    brute=lambda s: sum(set(s[i:j + 1]) >= set("abc") for i in range(len(s)) for j in range(i, len(s))),
    hints=[
        "If s[i..j] contains all three letters, so does every s[i..j'] with j' ≥ j.",
        "For each right end, find how many starts give a valid substring.",
        "Track the last index of a, b and c. Every start up to the smallest of those three indices works, so add min(last) + 1 for each right end.",
    ],
    insight="The number of valid starts for each end is 1 + the earliest of the three most recent positions.",
    time="O(n)", space="O(1)",
    pitfalls=["Counting only minimal windows instead of all substrings."],
)
def substrings_all_three(s):
    last = {"a": -1, "b": -1, "c": -1}
    total = 0
    for i, c in enumerate(s):
        last[c] = i
        total += min(last.values()) + 1
    return total


@problem(
    slug="find-the-index-of-the-first-occurrence-in-a-string", title="Find the Index of the First Occurrence in a String",
    difficulty="Medium", pattern=P, tags=["String", "Two Pointers", "String Matching"],
    sig="strStr(self, haystack: str, needle: str) -> int",
    desc="""Return the index of the first occurrence of `needle` in `haystack`, or `-1` if it doesn't occur. Don't use the built-in search (`find`, `index`, `in`).""",
    constraints=["1 ≤ len(haystack), len(needle) ≤ 10⁴", "lowercase letters"],
    samples=[("sadbutsad", "sad"), ("leetcode", "leeto")],
    tests=[("a", "a"), ("abc", "c"), ("aaa", "aaaa"), ("mississippi", "issip")],
    gen=lambda r: (r.word(r.randint(1, 20), "ab"), r.word(r.randint(1, 3), "ab")),
    brute=lambda h, n: h.find(n),
    hints=[
        "Compare needle against each window of haystack that has the same length.",
        "A window of length len(needle) slides one position at a time.",
        "For O(n + m), precompute KMP's failure table so mismatches never move the haystack pointer backwards.",
    ],
    insight="Sliding comparison works; KMP avoids re-checking characters after a mismatch.",
    time="O(n · m) simple, O(n + m) with KMP", space="O(m) for KMP",
    pitfalls=["Checking windows that run past the end of haystack."],
)
def str_str(haystack, needle):
    fail = [0] * len(needle)
    k = 0
    for i in range(1, len(needle)):
        while k and needle[i] != needle[k]:
            k = fail[k - 1]
        if needle[i] == needle[k]:
            k += 1
        fail[i] = k
    k = 0
    for i, c in enumerate(haystack):
        while k and c != needle[k]:
            k = fail[k - 1]
        if c == needle[k]:
            k += 1
            if k == len(needle):
                return i - k + 1
    return -1


@problem(
    slug="max-consecutive-ones-iii", title="Max Consecutive Ones III", difficulty="Medium", pattern=P, tags=["Array", "Sliding Window"],
    sig="longestOnes(self, nums: list[int], k: int) -> int",
    desc="""`nums` contains only 0s and 1s. You may flip at most `k` zeros into ones. Return the length of the longest run of consecutive 1s you can get.""",
    constraints=["1 ≤ len(nums) ≤ 10⁵", "nums[i] is 0 or 1", "0 ≤ k ≤ len(nums)"],
    samples=[([1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], 2), ([0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1], 3)],
    tests=[([0], 0), ([0, 0], 1)],
    gen=lambda r: (r.ints(r.randint(1, 25), 0, 1), r.randint(0, 4)),
    brute=lambda nums, k: max((len(sub) for _, _, sub in _subarrays(nums) if sub.count(0) <= k), default=0),
    hints=[
        "You need the longest window containing at most k zeros.",
        "Grow the window on the right and count zeros inside it.",
        "When there are more than k zeros, move the left edge until one zero leaves. Track the largest window.",
    ],
    insight="Longest window with at most k zeros, maintained with two pointers.",
    time="O(n)", space="O(1)",
    pitfalls=["Flipping zeros greedily from the left instead of keeping a window."],
)
def longest_ones(nums, k):
    left = zeros = best = 0
    for right, x in enumerate(nums):
        zeros += x == 0
        while zeros > k:
            zeros -= nums[left] == 0
            left += 1
        best = max(best, right - left + 1)
    return best


@problem(
    slug="longest-continuous-subarray-with-absolute-diff-less-than-or-equal-to-limit", title="Longest Subarray With Diff At Most Limit",
    difficulty="Medium", pattern=P, tags=["Array", "Sliding Window", "Monotonic Queue"],
    sig="longestSubarray(self, nums: list[int], limit: int) -> int",
    desc="""Return the length of the longest non-empty contiguous subarray in which the absolute difference between **any two** elements is at most `limit`.""",
    constraints=["1 ≤ len(nums) ≤ 10⁵", "1 ≤ nums[i] ≤ 10⁹", "0 ≤ limit ≤ 10⁹"],
    samples=[([8, 2, 4, 7], 4), ([10, 1, 2, 4, 7, 2], 5), ([4, 2, 2, 2, 4, 4, 2, 2], 0)],
    gen=lambda r: (r.ints(r.randint(1, 25), 1, 20), r.randint(0, 8)),
    brute=lambda nums, limit: max(len(sub) for _, _, sub in _subarrays(nums) if max(sub) - min(sub) <= limit),
    hints=[
        "Every pair is within limit exactly when max − min ≤ limit for the window.",
        "You need the window's max and min as it slides.",
        "Keep a decreasing deque for the max and an increasing deque for the min. Shrink from the left while max − min > limit, dropping deque fronts that leave the window.",
    ],
    insight="Two monotonic deques give the window's max and min in O(1).",
    time="O(n)", space="O(n)",
    pitfalls=["Checking all pairs in the window."],
)
def longest_limited(nums, limit):
    hi, lo = deque(), deque()
    left = best = 0
    for right, x in enumerate(nums):
        while hi and hi[-1] < x:
            hi.pop()
        while lo and lo[-1] > x:
            lo.pop()
        hi.append(x)
        lo.append(x)
        while hi[0] - lo[0] > limit:
            if hi[0] == nums[left]:
                hi.popleft()
            if lo[0] == nums[left]:
                lo.popleft()
            left += 1
        best = max(best, right - left + 1)
    return best


@problem(
    slug="subarray-product-less-than-k", title="Subarray Product Less Than K", difficulty="Medium", pattern=P, tags=["Array", "Sliding Window"],
    sig="numSubarrayProductLessThanK(self, nums: list[int], k: int) -> int",
    desc="""`nums` holds positive integers. Return the number of contiguous subarrays whose product is **strictly less than** `k`.""",
    constraints=["1 ≤ len(nums) ≤ 3 × 10⁴", "1 ≤ nums[i] ≤ 1000", "0 ≤ k ≤ 10⁶"],
    samples=[([10, 5, 2, 6], 100), ([1, 2, 3], 0)],
    tests=[([1, 1, 1], 2), ([5], 5)],
    gen=lambda r: (r.ints(r.randint(1, 20), 1, 9), r.randint(0, 100)),
    brute=lambda nums, k: sum(__import__("math").prod(sub) < k for _, _, sub in _subarrays(nums)),
    hints=[
        "With positive numbers, growing a subarray only increases its product.",
        "For each right end, keep the leftmost start whose product is still below k.",
        "Multiply in the new element; divide out from the left while the product ≥ k. Each step adds right − left + 1 subarrays.",
    ],
    insight="A shrinking window on a monotonic product counts all valid subarrays ending at each index.",
    time="O(n)", space="O(1)",
    pitfalls=["k ≤ 1: no product of positive integers is below it; handle it before shrinking past right."],
)
def product_less_than_k(nums, k):
    if k <= 1:
        return 0
    prod, left, count = 1, 0, 0
    for right, x in enumerate(nums):
        prod *= x
        while prod >= k:
            prod //= nums[left]
            left += 1
        count += right - left + 1
    return count


@problem(
    slug="count-number-of-nice-subarrays", title="Count Number of Nice Subarrays", difficulty="Medium", pattern=P,
    tags=["Array", "Sliding Window", "Hash Table", "Math"],
    sig="numberOfSubarrays(self, nums: list[int], k: int) -> int",
    desc="""A subarray is **nice** if it contains exactly `k` odd numbers. Return the number of nice contiguous subarrays.""",
    constraints=["1 ≤ len(nums) ≤ 5 × 10⁴", "1 ≤ nums[i] ≤ 10⁵", "1 ≤ k ≤ len(nums)"],
    samples=[([1, 1, 2, 1, 1], 3), ([2, 4, 6], 1), ([2, 2, 2, 1, 2, 2, 1, 2, 2, 2], 2)],
    gen=lambda r: (r.ints(r.randint(1, 20), 1, 6), r.randint(1, 4)),
    brute=lambda nums, k: sum(sum(x % 2 for x in sub) == k for _, _, sub in _subarrays(nums)),
    hints=[
        "Replace each number by 1 if it's odd and 0 if it's even. Now you need subarrays with sum exactly k.",
        "Exactly k = at most k − at most (k − 1).",
        "Count subarrays with at most m odd numbers using a sliding window, for m = k and m = k − 1.",
    ],
    insight="Odd/even turns this into binary subarrays with sum k.",
    time="O(n)", space="O(1)",
    pitfalls=["Forgetting even numbers on both sides of the odd block, which multiply the count."],
)
def nice_subarrays(nums, k):
    def at_most(m):
        left = odds = count = 0
        for right, x in enumerate(nums):
            odds += x % 2
            while odds > m:
                odds -= nums[left] % 2
                left += 1
            count += right - left + 1
        return count

    return at_most(k) - at_most(k - 1)


EXTRA = {
    "longest-repeating-character-replacement": {
        "edge": [("A", 0), ("AAAA", 0), ("ABCD", 0), ("ABCD", 4), ("AABABBA", 1)],
        "large": [lambda r: (r.word(20000, "ABC"), 50), lambda r: (r.word(20000, "AB"), 0)],
    },
    "minimum-window-substring": {
        "edge": [("a", "a"), ("a", "aa"), ("a", "b"), ("ab", "b"), ("aa", "aa")],
        "large": [lambda r: (r.word(30000, "abcdefgh"), "abcdefghhgfedcba"), lambda r: ("a" * 20000 + "b", "ab")],
    },
    "sliding-window-maximum": {
        "edge": [([1], 1), ([1, -1], 1), ([9, 11], 2), ([4, -2], 2), ([7, 2, 4], 3)],
        "large": [lambda r: (r.ints(10000, -10000, 10000), 3000), lambda r: (list(range(10000, 0, -1)), 5000)],
    },
    "subarrays-with-k-different-integers": {
        "edge": [([1], 1), ([1, 1, 1], 1), ([1, 2, 3], 3), ([1, 2], 3)],
        "large": [lambda r: (r.ints(10000, 1, 20), 5), lambda r: (r.ints(10000, 1, 3), 2)],
    },
    "repeated-dna-sequences": {
        "edge": [("A",), ("AAAAAAAAAA",), ("AAAAAAAAAAA",), ("AAAAAAAAAAAA",)],
        "large": [lambda r: (r.word(60000, "ACGT"),), lambda r: ("ACGTACGTAC" * 3000,)],
    },
    "minimum-window-subsequence": {
        "edge": [("a", "a"), ("a", "b"), ("abc", "c"), ("fgrqsqsnodwmxzkzxwqegkndaa", "kzed")],
        "large": [lambda r: (r.word(10000, "abc"), r.word(30, "abc"))],
    },
    "minimum-size-subarray-sum": {
        "edge": [(4, [1, 4, 4]), (11, [1, 1, 1, 1, 1, 1, 1, 1]), (1, [1]), (15, [1, 2, 3, 4, 5])],
        "large": [lambda r: (10**8, r.ints(15000, 1, 10000)), lambda r: (300000, r.ints(15000, 1, 100))],
    },
    "fruit-into-baskets": {
        "edge": [([0],), ([0, 1, 2, 2],), ([1, 2, 3, 2, 2],), ([3, 3, 3, 1, 2, 1, 1, 2, 3, 3, 4],)],
        "large": [lambda r: ([r.choice([r.randint(0, 2), r.randint(0, 9999)]) for _ in range(10000)],)],
    },
    "frequency-of-the-most-frequent-element": {
        "edge": [([1], 1), ([3, 9, 6], 2), ([1, 4, 8, 13], 5), ([100000, 100000], 1)],
        "large": [lambda r: (r.ints(10000, 1, 100000), 100000), lambda r: (r.ints(10000, 1, 100), 5000)],
    },
    "maximum-average-subarray-i": {
        "edge": [([5], 1), ([-1], 1), ([0, 4, 0, 3, 2], 1), ([-10000, -10000], 2)],
        "large": [lambda r: (r.ints(15000, -10000, 10000), 6000)],
    },
    "diet-plan-performance": {
        "edge": [([0], 1, 0, 0), ([3, 2], 2, 0, 1), ([6, 5, 0, 0], 2, 1, 5), ([20000], 1, 0, 20000)],
        "large": [lambda r: (r.ints(15000, 0, 20000), 5000, 40000000, 60000000)],
    },
    "count-subarrays-with-score-less-than-k": {
        "edge": [([1], 1), ([1], 2), ([1, 1, 1], 5), ([100000], 10**15)],
        "large": [lambda r: (r.ints(10000, 1, 100000), 10**15), lambda r: (r.ints(10000, 1, 10), 10**6)],
    },
    "count-substrings-with-k-frequency-characters-ii": {
        "edge": [("a", 1), ("a", 2), ("aaa", 3), ("abcde", 1)],
        "large": [lambda r: (r.word(30000, "abc"), 50), lambda r: (r.word(30000, "abcdefghijklmnopqrstuvwxyz"), 3)],
    },
    "substring-with-concatenation-of-all-words": {
        "edge": [("a", ["a"]), ("aaa", ["a", "a"]), ("ab", ["ba"]), ("wordgoodgoodgoodbestword", ["word", "good", "best", "good"])],
        "large": [lambda r: (r.word(10000, "ab"), r.words(40, 3, 3, "ab")), lambda r: ("ab" * 5000, ["ab", "ba", "ab"])],
    },
    "binary-subarrays-with-sum": {
        "edge": [([0], 0), ([1], 0), ([0, 0, 0, 0, 0], 0), ([1, 1], 3)],
        "large": [lambda r: ([r.randint(0, 1) for _ in range(15000)], 40), lambda r: ([0] * 15000, 0)],
    },
    "permutation-in-string": {
        "edge": [("a", "a"), ("ab", "a"), ("adc", "dcda"), ("hello", "ooolleoooleh")],
        "large": [lambda r: (r.word(2000, "abcdefghij"), r.word(10000, "abcdefghij")), lambda r: ("a" * 5000 + "b", "a" * 9999 + "b")],
    },
    "number-of-substrings-containing-all-three-characters": {
        "edge": [("abc",), ("aaa",), ("aaacb",), ("cba",)],
        "large": [lambda r: (r.word(50000, "abc"),), lambda r: ("a" * 25000 + "bc" + "a" * 20000,)],
    },
    "find-the-index-of-the-first-occurrence-in-a-string": {
        "edge": [("a", "a"), ("a", "b"), ("aaa", "aaaa"), ("mississippi", "issip"), ("abc", "c")],
        "large": [lambda r: ("a" * 9999 + "b", "a" * 1000 + "b")],
    },
    "max-consecutive-ones-iii": {
        "edge": [([0], 0), ([0], 1), ([1, 1, 1], 0), ([0, 0, 0], 2)],
        "large": [lambda r: ([r.choice([1, 1, 0]) for _ in range(15000)], 300)],
    },
    "longest-continuous-subarray-with-absolute-diff-less-than-or-equal-to-limit": {
        "edge": [([1], 0), ([4, 2, 2, 2, 4, 4, 2, 2], 0), ([10, 1, 2, 4, 7, 2], 5), ([1, 1000000000], 999999999)],
        "large": [lambda r: (r.ints(10000, 1, 10**9), 5 * 10**8), lambda r: (r.ints(10000, 1, 1000), 990)],
    },
    "subarray-product-less-than-k": {
        "edge": [([1, 2, 3], 0), ([1, 1, 1], 1), ([1, 1, 1], 2), ([1000], 1000)],
        "large": [lambda r: ([r.choice([1, 1, 1, 2]) for _ in range(15000)], 10**6)],
    },
    "count-number-of-nice-subarrays": {
        "edge": [([2, 4, 6], 1), ([1], 1), ([1, 1, 1], 3), ([2, 2, 2, 1, 2, 2, 1, 2, 2, 2], 2)],
        "large": [lambda r: (r.ints(15000, 1, 100000), 30), lambda r: ([r.choice([2, 2, 2, 1]) for _ in range(15000)], 1)],
    },
}
