import heapq
from fractions import Fraction
from itertools import combinations

from catalog_lib import ListNode, from_list_node, problem, to_list_node

KW = "k-way-merge"
TK = "heap"


@problem(
    slug="merge-sorted-array", title="Merge Sorted Array", difficulty="Easy", pattern=KW, tags=["Array", "Two Pointers", "Sorting"],
    sig="merge(self, nums1: list[int], m: int, nums2: list[int], n: int) -> None", out_arg=0,
    desc="""`nums1` has length `m + n`: its first `m` elements are sorted and the last `n` are placeholders (0). `nums2` holds `n` sorted elements.

Merge `nums2` into `nums1` **in place** so `nums1` becomes one sorted array. Return nothing; the judge checks `nums1`.""",
    constraints=["0 ≤ m, n ≤ 200", "1 ≤ m + n ≤ 200", "-10⁹ ≤ values ≤ 10⁹"],
    samples=[([1, 2, 3, 0, 0, 0], 3, [2, 5, 6], 3), ([1], 1, [], 0), ([0], 0, [1], 1)],
    gen=lambda r: (lambda a, b: (a + [0] * len(b), len(a), b, len(b)))(r.sorted_ints(r.randint(0, 8), -9, 9), r.sorted_ints(r.randint(0, 8), -9, 9)),
    brute=lambda nums1, m, nums2, n: nums1.__setitem__(slice(None), sorted(nums1[:m] + nums2)),
    hints=[
        "Filling nums1 from the front would overwrite values you still need.",
        "The free space is at the back of nums1. What belongs at the very last position?",
        "Use three pointers: the end of nums1's real values, the end of nums2, and the write position at the very end. Place the larger value and move left.",
    ],
    insight="Merging from the back uses the empty tail of nums1, so nothing is overwritten.",
    time="O(m + n)", space="O(1)",
    pitfalls=["Forgetting the leftover elements of nums2 when nums1's part runs out."],
)
def merge_sorted_array(nums1, m, nums2, n):
    i, j, w = m - 1, n - 1, m + n - 1
    while j >= 0:
        if i >= 0 and nums1[i] > nums2[j]:
            nums1[w] = nums1[i]
            i -= 1
        else:
            nums1[w] = nums2[j]
            j -= 1
        w -= 1


@problem(
    slug="merge-k-sorted-lists", title="Merge K Sorted Lists", difficulty="Hard", pattern=KW,
    tags=["Linked List", "Heap", "Divide and Conquer", "Merge Sort"],
    sig="mergeKLists(self, lists: list[Optional[ListNode]]) -> Optional[ListNode]",
    arg_types=["ListNodeArray"], ret="ListNode",
    desc="""`lists` contains `k` linked lists, each sorted in ascending order. Merge them into one sorted linked list and return its head.

In the tests, `lists` is written as a list of value lists, and the judge builds the linked lists for you.""",
    constraints=["0 ≤ k ≤ 10⁴", "0 ≤ len(lists[i]) ≤ 500", "-10⁴ ≤ values ≤ 10⁴", "total nodes ≤ 10⁴"],
    samples=[([[1, 4, 5], [1, 3, 4], [2, 6]],), ([],), ([[]],)],
    gen=lambda r: ([r.sorted_ints(r.randint(0, 6), -9, 9) for _ in range(r.randint(0, 5))],),
    brute=lambda lists: to_list_node(sorted(x for head in lists for x in from_list_node(head))),
    hints=[
        "The next node of the merged list is the smallest among the current heads of all lists.",
        "A min-heap holding one head per list gives that smallest head in O(log k).",
        "Pop the smallest (value, list index, node), attach it, and push its next node if there is one. Store the list index to break ties.",
    ],
    insight="A heap of the k list heads is a k-way merge in O(N log k).",
    time="O(N log k)", space="O(k)",
    pitfalls=["Comparing ListNode objects in the heap on ties: include a tie-breaker."],
)
def merge_k_lists(lists):
    heap = [(node.val, i, node) for i, node in enumerate(lists) if node]
    heapq.heapify(heap)
    dummy = tail = ListNode()
    while heap:
        _, i, node = heapq.heappop(heap)
        tail.next = tail = node
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))
    return dummy.next


@problem(
    slug="kth-smallest-number-in-m-sorted-lists", title="Kth Smallest Number in M Sorted Lists", difficulty="Medium", pattern=KW,
    tags=["Array", "Heap", "K-way Merge"],
    sig="kSmallestNumber(self, lists: list[list[int]], k: int) -> int",
    desc="""`lists` contains `m` sorted lists of integers. Return the `k`th smallest number among all of them (duplicates count separately). If there are fewer than `k` numbers in total, return the largest number overall; if all lists are empty, return `0`.""",
    constraints=["1 ≤ m ≤ 50", "0 ≤ len(lists[i]) ≤ 200", "-10⁹ ≤ values ≤ 10⁹", "1 ≤ k ≤ 10⁹"],
    samples=[([[2, 6, 8], [3, 6, 10], [5, 8, 11]], 5), ([[1, 2, 3], [4, 5], [6, 7, 8, 15], [10, 11, 12, 13], [5, 10]], 50), ([[], [], []], 3)],
    gen=lambda r: ([r.sorted_ints(r.randint(0, 6), -20, 20) for _ in range(r.randint(1, 5))], r.randint(1, 30)),
    brute=lambda lists, k: (lambda v: v[min(k, len(v)) - 1] if v else 0)(sorted(x for l in lists for x in l)),
    hints=[
        "Merging all lists completely is wasteful when k is small.",
        "Put the first element of each non-empty list into a min-heap, with its list and position.",
        "Pop k times, each time pushing the next element from the same list. The kth pop is the answer; stop early if the heap empties.",
    ],
    insight="Only the frontier of each list matters, so a heap of size m finds the kth smallest in O(k log m).",
    time="O(k log m)", space="O(m)",
    pitfalls=["Not handling k larger than the total count."],
)
def k_smallest_number(lists, k):
    heap = [(l[0], i, 0) for i, l in enumerate(lists) if l]
    heapq.heapify(heap)
    value, count = 0, 0
    while heap and count < k:
        value, i, j = heapq.heappop(heap)
        count += 1
        if j + 1 < len(lists[i]):
            heapq.heappush(heap, (lists[i][j + 1], i, j + 1))
    return value


def _primes_upto(n):
    return [p for p in range(2, n + 1) if all(p % d for d in range(2, int(p ** 0.5) + 1))]


@problem(
    slug="k-th-smallest-prime-fraction", title="K-th Smallest Prime Fraction", difficulty="Medium", pattern=KW,
    tags=["Array", "Binary Search", "Heap", "Sorting"],
    sig="kthSmallestPrimeFraction(self, arr: list[int], k: int) -> list[int]",
    desc="""`arr` is sorted and contains `1` followed by distinct primes. For every pair `i < j`, consider the fraction `arr[i] / arr[j]`. Return the `k`th smallest of these fractions as `[numerator, denominator]`.""",
    constraints=["2 ≤ len(arr) ≤ 1000", "arr[0] = 1, the rest are distinct primes, sorted", "1 ≤ k ≤ n(n − 1)/2"],
    samples=[([1, 2, 3, 5], 3), ([1, 7], 1)],
    gen=lambda r: (lambda arr: (arr, r.randint(1, len(arr) * (len(arr) - 1) // 2)))([1] + sorted(r.sample(_primes_upto(40), r.randint(1, 8)))),
    brute=lambda arr, k: (lambda f: [f.numerator, f.denominator])(sorted(Fraction(a, b) for a, b in combinations(arr, 2))[k - 1]),
    hints=[
        "For a fixed denominator arr[j], the fractions arr[0]/arr[j] < arr[1]/arr[j] < … are already sorted.",
        "So you have n sorted lists of fractions to merge.",
        "Push the smallest fraction of each list (numerator index 0) into a min-heap; pop k − 1 times, each time pushing the next numerator for the same denominator. The top is the answer.",
    ],
    insight="Each denominator defines a sorted list, so the kth fraction is a k-way merge.",
    time="O(k log n)", space="O(n)",
    pitfalls=["Comparing fractions with floating point; compare a·d with b·c instead (or use exact fractions)."],
)
def kth_prime_fraction(arr, k):
    n = len(arr)
    heap = [(Fraction(arr[0], arr[j]), 0, j) for j in range(1, n)]
    heapq.heapify(heap)
    for _ in range(k - 1):
        _, i, j = heapq.heappop(heap)
        if i + 1 < j:
            heapq.heappush(heap, (Fraction(arr[i + 1], arr[j]), i + 1, j))
    _, i, j = heap[0]
    return [arr[i], arr[j]]


def _super_ugly_brute(n, primes):
    # Enumerate every product of the primes up to a bound that surely contains n of them.
    bound = min(primes) ** (n - 1)
    nums = {1}
    for p in primes:
        nums |= {x * p ** e for x in nums for e in range(1, 64) if x * p ** e <= bound}
    return sorted(nums)[n - 1]


@problem(
    slug="super-ugly-number", title="Super Ugly Number", difficulty="Medium", pattern=KW, tags=["Array", "Math", "Dynamic Programming", "Heap"],
    sig="nthSuperUglyNumber(self, n: int, primes: list[int]) -> int",
    desc="""A **super ugly number** is a positive integer whose prime factors all appear in `primes` (1 counts, having no prime factors). Return the `n`th super ugly number.""",
    constraints=["1 ≤ n ≤ 10⁵", "1 ≤ len(primes) ≤ 100", "primes are distinct, sorted, and ≤ 1000"],
    samples=[(12, [2, 7, 13, 19]), (1, [2, 3, 5])],
    tests=[(5, [3]), (10, [2, 3, 5])],
    gen=lambda r: (r.randint(1, 40), sorted(r.sample([2, 3, 5, 7, 11, 13], r.randint(1, 4)))),
    brute=_super_ugly_brute,
    hints=[
        "Every super ugly number (after 1) is an earlier super ugly number times one of the primes.",
        "Think of len(primes) sorted streams: ugly[i] × p for each prime p, merged together.",
        "Keep one pointer per prime into the ugly list. The next number is the minimum of ugly[ptr[p]] × p; advance every pointer that produced it (to skip duplicates).",
    ],
    insight="Multiple pointers (or a heap) merge the prime-multiplied streams without duplicates.",
    time="O(n · len(primes))", space="O(n + len(primes))",
    pitfalls=["Producing duplicates like 2·7 and 7·2 when only one pointer advances."],
)
def nth_super_ugly(n, primes):
    ugly = [1]
    idx = [0] * len(primes)
    while len(ugly) < n:
        nxt = min(ugly[idx[i]] * p for i, p in enumerate(primes))
        ugly.append(nxt)
        for i, p in enumerate(primes):
            if ugly[idx[i]] * p == nxt:
                idx[i] += 1
    return ugly[-1]


class _KthLargestRef:
    def __init__(self, k, nums):
        self.k, self.vals = k, sorted(nums)

    def add(self, val):
        from bisect import insort
        insort(self.vals, val)
        return self.vals[-self.k]


def _kth_stream_ops(r):
    k = r.randint(1, 4)
    nums = r.ints(r.randint(k - 1, 6), -20, 20)
    ops, args = ["KthLargest"], [[k, nums]]
    for _ in range(r.randint(2, 10)):
        ops.append("add")
        args.append([r.randint(-20, 20)])
    return ops, args


@problem(
    slug="kth-largest-element-in-a-stream", title="Kth Largest Element in a Stream", difficulty="Easy", pattern=TK,
    tags=["Design", "Heap", "Data Stream"],
    design=True, cls="KthLargest",
    starter="""class KthLargest:
    def __init__(self, k: int, nums: list[int]):
        pass

    def add(self, val: int) -> int:
        pass
""",
    desc="""Design `KthLargest`, which tracks the `k`th largest value in a growing stream of scores:

- `KthLargest(k, nums)` starts with the scores in `nums`.
- `add(val)` adds a score and returns the `k`th largest score so far (duplicates count separately).

There are always at least `k` scores when `add` is called.""",
    constraints=["1 ≤ k ≤ 10⁴", "0 ≤ len(nums) ≤ 10⁴", "-10⁴ ≤ values ≤ 10⁴"],
    samples=[(["KthLargest", "add", "add", "add", "add", "add"], [[3, [4, 5, 8, 2]], [3], [5], [10], [9], [4]]),
             (["KthLargest", "add", "add"], [[1, []], [-3], [-2]])],
    gen=_kth_stream_ops,
    hints=[
        "Keeping everything sorted is overkill: only the top k scores matter.",
        "In a min-heap of size k, the root is the kth largest value.",
        "On add, push the value and pop the smallest whenever the heap grows past k; the root is the answer.",
    ],
    insight="A size-k min-heap keeps the kth largest at the root.",
    time="O(log k) per add", space="O(k)",
    pitfalls=["Forgetting to trim the initial nums down to k elements."],
)
class KthLargest(_KthLargestRef):
    pass


def _closest_points_input(r):
    seen, pts = set(), []
    while len(pts) < r.randint(1, 10):
        p = (r.randint(-10, 10), r.randint(-10, 10))
        d = p[0] ** 2 + p[1] ** 2
        if d not in seen:
            seen.add(d)
            pts.append(list(p))
    return pts, r.randint(1, len(pts))


@problem(
    slug="k-closest-points-to-origin", title="K Closest Points to Origin", difficulty="Medium", pattern=TK,
    tags=["Array", "Math", "Heap", "Sorting", "Quickselect"],
    sig="kClosest(self, points: list[list[int]], k: int) -> list[list[int]]", compare="unordered",
    desc="""Return the `k` points closest to the origin `(0, 0)` by Euclidean distance, in any order. The tests guarantee the answer is unique.""",
    constraints=["1 ≤ k ≤ len(points) ≤ 10⁴", "-10⁴ ≤ x, y ≤ 10⁴"],
    samples=[([[1, 3], [-2, 2]], 1), ([[3, 3], [5, -1], [-2, 4]], 2)],
    gen=_closest_points_input,
    brute=lambda pts, k: sorted(pts, key=lambda p: p[0] ** 2 + p[1] ** 2)[:k],
    hints=[
        "Comparing squared distances avoids square roots.",
        "Sorting all points is O(n log n). Can you keep only k candidates?",
        "Keep a max-heap of size k keyed by distance; when a closer point arrives, replace the farthest. (Quickselect also gives O(n) average.)",
    ],
    insight="A bounded max-heap of size k holds the k closest points seen so far.",
    time="O(n log k)", space="O(k)",
    pitfalls=["Using a min-heap of all points when only k are needed."],
)
def k_closest(points, k):
    heap = []
    for x, y in points:
        heapq.heappush(heap, (-(x * x + y * y), x, y))
        if len(heap) > k:
            heapq.heappop(heap)
    return [[x, y] for _, x, y in heap]


def _ceil3(x):
    return -(-x // 3)


@problem(
    slug="maximal-score-after-applying-k-operations", title="Maximal Score After Applying K Operations", difficulty="Medium", pattern=TK,
    tags=["Array", "Greedy", "Heap"],
    sig="maxKelements(self, nums: list[int], k: int) -> int",
    desc="""Starting with a score of 0, apply exactly `k` operations. One operation picks an index `i`, adds `nums[i]` to the score, and replaces `nums[i]` with `ceil(nums[i] / 3)`.

Return the maximum possible score.""",
    constraints=["1 ≤ len(nums), k ≤ 10⁵", "1 ≤ nums[i] ≤ 10⁹"],
    samples=[([10, 10, 10, 10, 10], 5), ([1, 10, 3, 3, 3], 3)],
    gen=lambda r: (r.ints(r.randint(1, 10), 1, 50), r.randint(1, 15)),
    brute=lambda nums, k: (lambda v: sum((m := max(v), v.__setitem__(v.index(m), _ceil3(m)))[0] for _ in range(k)))(list(nums)),
    hints=[
        "Taking the largest current value is always at least as good as taking a smaller one.",
        "You need the maximum repeatedly while values change.",
        "Use a max-heap: pop the largest, add it to the score, push ceil(value / 3) back, k times.",
    ],
    insight="Greedy with a max-heap: the biggest value now is never worse to take first.",
    time="O(n + k log n)", space="O(n)",
    pitfalls=["Using floor division instead of ceiling."],
)
def max_k_elements(nums, k):
    heap = [-x for x in nums]
    heapq.heapify(heap)
    score = 0
    for _ in range(k):
        x = -heapq.heappop(heap)
        score += x
        heapq.heappush(heap, -_ceil3(x))
    return score


@problem(
    slug="find-the-kth-largest-integer-in-the-array", title="Find the Kth Largest Integer in the Array", difficulty="Medium", pattern=TK,
    tags=["Array", "String", "Heap", "Sorting"],
    sig="kthLargestNumber(self, nums: list[str], k: int) -> str",
    desc="""Each string in `nums` is a non-negative integer without leading zeros, possibly far too large for a normal integer type. Return the `k`th largest of them as a string (duplicates count separately).""",
    constraints=["1 ≤ k ≤ len(nums) ≤ 10⁴", "1 ≤ len(nums[i]) ≤ 100", "no leading zeros"],
    samples=[(["3", "6", "7", "10"], 4), (["2", "21", "12", "1"], 3), (["0", "0"], 2)],
    gen=lambda r: (lambda nums: (nums, r.randint(1, len(nums))))([str(r.randint(0, 10 ** r.randint(1, 25))) for _ in range(r.randint(1, 8))]),
    brute=lambda nums, k: sorted(nums, key=int, reverse=True)[k - 1],
    hints=[
        "Comparing as strings doesn't work directly: \"9\" > \"10\" lexicographically.",
        "A longer number (no leading zeros) is always larger; equal lengths compare lexicographically.",
        "Use that comparison with a size-k min-heap (or sort with the key (length, string)) and take the kth largest.",
    ],
    insight="Compare big numbers by (length, string) without converting them.",
    time="O(n log k · L)", space="O(k)",
    pitfalls=["Comparing the strings lexicographically without considering length."],
)
def kth_largest_number(nums, k):
    heap = []
    for s in nums:
        heapq.heappush(heap, (len(s), s))
        if len(heap) > k:
            heapq.heappop(heap)
    return heap[0][1]


@problem(
    slug="third-maximum-number", title="Third Maximum Number", difficulty="Easy", pattern=TK, tags=["Array", "Sorting"],
    sig="thirdMax(self, nums: list[int]) -> int",
    desc="""Return the **third distinct** maximum number in `nums`. If there are fewer than three distinct values, return the maximum.""",
    constraints=["1 ≤ len(nums) ≤ 10⁴", "-2³¹ ≤ nums[i] ≤ 2³¹ − 1"],
    samples=[([3, 2, 1],), ([1, 2],), ([2, 2, 3, 1],)],
    tests=[([1, 1, 1],), ([5, 2, 4, 1, 3, 6, 0],)],
    gen=lambda r: (r.ints(r.randint(1, 12), -5, 5),),
    brute=lambda nums: (lambda d: d[2] if len(d) >= 3 else d[0])(sorted(set(nums), reverse=True)),
    hints=[
        "Duplicates don't count separately here.",
        "Track the three largest distinct values in one pass.",
        "For each value not already among them, shift the trio down when it beats one of them. At the end, use the third if it exists, else the first.",
    ],
    insight="Three variables (or a set of size 3) track the top three distinct values in O(n).",
    time="O(n)", space="O(1)",
    pitfalls=["Counting duplicates as separate maxima."],
)
def third_max(nums):
    top = []
    for x in nums:
        if x in top:
            continue
        top.append(x)
        top.sort(reverse=True)
        top = top[:3]
    return top[2] if len(top) == 3 else top[0]


def _hire_brute(quality, wage, k):
    best = float("inf")
    for group in combinations(range(len(quality)), k):
        ratio = max(wage[i] / quality[i] for i in group)
        best = min(best, ratio * sum(quality[i] for i in group))
    return best


@problem(
    slug="minimum-cost-to-hire-k-workers", title="Minimum Cost to Hire K Workers", difficulty="Hard", pattern=TK,
    tags=["Array", "Greedy", "Heap", "Sorting"],
    sig="mincostToHireWorkers(self, quality: list[int], wage: list[int], k: int) -> float", compare="approx",
    desc="""Worker `i` has quality `quality[i]` and a minimum wage `wage[i]`. Hire exactly `k` workers so that:

1. Everyone in the group is paid in proportion to their quality (pay ratio is the same for all), and
2. Everyone gets at least their minimum wage.

Return the least total pay. Answers within 10⁻⁵ are accepted.""",
    constraints=["1 ≤ k ≤ n ≤ 10⁴", "1 ≤ quality[i], wage[i] ≤ 10⁴"],
    samples=[([10, 20, 5], [70, 50, 30], 2), ([3, 1, 10, 10, 1], [4, 8, 2, 2, 7], 3)],
    gen=lambda r: (lambda n: (r.ints(n, 1, 10), r.ints(n, 1, 20), r.randint(1, n)))(r.randint(1, 7)),
    brute=_hire_brute,
    hints=[
        "In a group, the pay ratio (pay per unit quality) is set by the worker with the highest wage/quality ratio.",
        "Fix the captain: sort workers by wage/quality. Any group whose maximum ratio is r costs r × (sum of qualities).",
        "Scan workers by increasing ratio, keeping the k smallest qualities seen so far in a max-heap; for each captain with a full heap, the cost is ratio × heap sum.",
    ],
    insight="Sort by ratio and keep the cheapest k qualities in a max-heap.",
    time="O(n log n)", space="O(n)",
    pitfalls=["Paying each worker their own minimum wage, which breaks proportionality."],
)
def min_cost_hire(quality, wage, k):
    workers = sorted((w / q, q) for q, w in zip(quality, wage))
    heap, total, best = [], 0, float("inf")
    for ratio, q in workers:
        heapq.heappush(heap, -q)
        total += q
        if len(heap) > k:
            total += heapq.heappop(heap)
        if len(heap) == k:
            best = min(best, ratio * total)
    return best


def _range_brute(nums):
    values = sorted({x for l in nums for x in l})
    best = None
    for a in values:
        for b in values:
            if b < a:
                continue
            if all(any(a <= x <= b for x in l) for l in nums):
                if best is None or (b - a, a) < (best[1] - best[0], best[0]):
                    best = [a, b]
    return best


@problem(
    slug="smallest-range-covering-elements-from-k-lists", title="Smallest Range Covering Elements from K Lists", difficulty="Hard",
    pattern=KW, tags=["Array", "Hash Table", "Greedy", "Sliding Window", "Heap"],
    sig="smallestRange(self, nums: list[list[int]]) -> list[int]",
    desc="""You have `k` lists of integers, each sorted. Find the smallest range `[a, b]` that contains at least one number from every list.

Range `[a, b]` is smaller than `[c, d]` if `b − a < d − c`, or if they're equal and `a < c`.""",
    constraints=["1 ≤ k ≤ 3500", "1 ≤ len(nums[i]) ≤ 50", "-10⁵ ≤ values ≤ 10⁵", "each list is sorted"],
    samples=[([[4, 10, 15, 24, 26], [0, 9, 12, 20], [5, 18, 22, 30]],), ([[1, 2, 3], [1, 2, 3], [1, 2, 3]],)],
    gen=lambda r: ([r.sorted_ints(r.randint(1, 5), -10, 10) for _ in range(r.randint(1, 4))],),
    brute=_range_brute,
    hints=[
        "A valid range must include one current element from each list.",
        "Keep one pointer per list. The range they cover is [min, max] of the pointed values.",
        "Use a min-heap of the pointed values and track the maximum. Record the range, then advance the list holding the minimum. Stop when a list runs out.",
    ],
    insight="Advancing the minimum is the only move that can shrink the range: a k-way merge with a running max.",
    time="O(N log k)", space="O(k)",
    pitfalls=["Breaking ties in favor of the larger start."],
)
def smallest_range(nums):
    heap = [(l[0], i, 0) for i, l in enumerate(nums)]
    heapq.heapify(heap)
    hi = max(l[0] for l in nums)
    best = [heap[0][0], hi]
    while True:
        lo, i, j = heapq.heappop(heap)
        if hi - lo < best[1] - best[0] or (hi - lo == best[1] - best[0] and lo < best[0]):
            best = [lo, hi]
        if j + 1 == len(nums[i]):
            return best
        nxt = nums[i][j + 1]
        hi = max(hi, nxt)
        heapq.heappush(heap, (nxt, i, j + 1))


def _team_brute(n, speed, efficiency, k):
    best = 0
    for size in range(1, k + 1):
        for g in combinations(range(n), size):
            best = max(best, sum(speed[i] for i in g) * min(efficiency[i] for i in g))
    return best % (10**9 + 7)


@problem(
    slug="maximum-performance-of-a-team", title="Maximum Performance of a Team", difficulty="Hard", pattern=TK,
    tags=["Array", "Greedy", "Heap", "Sorting"],
    sig="maxPerformance(self, n: int, speed: list[int], efficiency: list[int], k: int) -> int",
    desc="""Choose **at most** `k` of the `n` engineers. A team's performance is the sum of its members' speeds multiplied by the **minimum** efficiency among them.

Return the maximum performance modulo `10⁹ + 7` (maximize first, then take the modulo).""",
    constraints=["1 ≤ k ≤ n ≤ 10⁵", "1 ≤ speed[i] ≤ 10⁵", "1 ≤ efficiency[i] ≤ 10⁸"],
    samples=[(6, [2, 10, 3, 1, 5, 8], [5, 4, 3, 9, 7, 2], 2), (6, [2, 10, 3, 1, 5, 8], [5, 4, 3, 9, 7, 2], 3)],
    gen=lambda r: (lambda n: (n, r.ints(n, 1, 10), r.ints(n, 1, 10), r.randint(1, n)))(r.randint(1, 7)),
    brute=_team_brute,
    hints=[
        "Fix the member with the lowest efficiency; everyone else must have at least that efficiency.",
        "Process engineers in decreasing efficiency, so each new one is the team's minimum.",
        "Keep the (k − 1 others +) fastest speeds in a min-heap of size k with a running sum; performance = sum × current efficiency. Take the modulo only at the end.",
    ],
    insight="Sort by efficiency descending and keep the top k speeds in a min-heap.",
    time="O(n log n)", space="O(n)",
    pitfalls=["Taking the modulo before comparing performances."],
)
def max_performance(n, speed, efficiency, k):
    heap, total, best = [], 0, 0
    for e, s in sorted(zip(efficiency, speed), reverse=True):
        heapq.heappush(heap, s)
        total += s
        if len(heap) > k:
            total -= heapq.heappop(heap)
        best = max(best, total * e)
    return best % (10**9 + 7)


@problem(
    slug="k-maximum-sum-combinations-from-two-arrays", title="K Maximum Sum Combinations From Two Arrays", difficulty="Hard", pattern=TK,
    tags=["Array", "Heap", "Sorting"],
    sig="kMaxSumCombinations(self, arr1: list[int], arr2: list[int], k: int) -> list[int]",
    desc="""Arrays `arr1` and `arr2` have the same length `n`. A combination picks one element from each array and adds them. Return the `k` largest sums over all `n²` combinations, in descending order.""",
    constraints=["1 ≤ n ≤ 10⁵", "1 ≤ k ≤ n²", "1 ≤ values ≤ 10⁴"],
    samples=[([4, 2], [3, 5], 2), ([4, 2, 5, 1], [8, 0, 3, 5], 3)],
    gen=lambda r: (lambda n: (r.ints(n, 1, 15), r.ints(n, 1, 15), r.randint(1, n * n)))(r.randint(1, 6)),
    brute=lambda a, b, k: sorted((x + y for x in a for y in b), reverse=True)[:k],
    hints=[
        "Sort both arrays in descending order: the biggest sum is a[0] + b[0].",
        "The next candidates after (i, j) are (i + 1, j) and (i, j + 1).",
        "Use a max-heap of (sum, i, j) with a visited set; pop k times, pushing the two neighbors of each popped pair.",
    ],
    insight="Exploring sums outward from (0, 0) with a heap avoids generating all n² sums.",
    time="O(n log n + k log k)", space="O(k)",
    pitfalls=["Pushing the same (i, j) twice."],
)
def k_max_sum_combos(arr1, arr2, k):
    a, b = sorted(arr1, reverse=True), sorted(arr2, reverse=True)
    heap, seen, out = [(-(a[0] + b[0]), 0, 0)], {(0, 0)}, []
    while len(out) < k:
        s, i, j = heapq.heappop(heap)
        out.append(-s)
        for x, y in ((i + 1, j), (i, j + 1)):
            if x < len(a) and y < len(b) and (x, y) not in seen:
                seen.add((x, y))
                heapq.heappush(heap, (-(a[x] + b[y]), x, y))
    return out


def _empty_slots_brute(bulbs, k):
    on = set()
    for day, pos in enumerate(bulbs, 1):
        on.add(pos)
        for p in on:
            q = p + k + 1
            if q in on and all(x not in on for x in range(p + 1, q)):
                return day
    return -1


@problem(
    slug="k-empty-slots", title="K Empty Slots", difficulty="Hard", pattern=TK, tags=["Array", "Sliding Window", "Ordered Set"],
    sig="kEmptySlots(self, bulbs: list[int], k: int) -> int",
    desc="""`n` bulbs in a row (positions 1..n) are all off. On day `i` (1-indexed) the bulb at position `bulbs[i − 1]` turns on, and stays on.

Return the earliest day on which there are two **on** bulbs with exactly `k` bulbs between them, all of which are **off**. If that never happens, return `-1`.""",
    constraints=["1 ≤ n ≤ 2 × 10⁴", "bulbs is a permutation of 1..n", "0 ≤ k ≤ 2 × 10⁴"],
    samples=[([1, 3, 2], 1), ([1, 2, 3], 1)],
    tests=[([1], 0), ([2, 1], 0)],
    gen=lambda r: (lambda n: (r.sample(range(1, n + 1), n), r.randint(0, 3)))(r.randint(1, 10)),
    brute=_empty_slots_brute,
    hints=[
        "Turn the input around: days[pos] = the day the bulb at pos turns on.",
        "A valid pair (left, right = left + k + 1) needs every bulb strictly between them to turn on later than both ends.",
        "Slide a window of length k + 2 over days: if some inner day is smaller than either end, restart the window at that position; if you reach the right end, max(days[left], days[right]) is a candidate.",
    ],
    insight="Inverting to on-days turns this into a sliding window over positions.",
    time="O(n)", space="O(n)",
    pitfalls=["Checking pairs only on the day their second bulb lights, without checking the bulbs in between."],
)
def k_empty_slots(bulbs, k):
    n = len(bulbs)
    days = [0] * n
    for day, pos in enumerate(bulbs, 1):
        days[pos - 1] = day
    best, left, right = float("inf"), 0, k + 1
    i = 1
    while right < n:
        if i == right:
            best = min(best, max(days[left], days[right]))
            left, right, i = right, right + k + 1, right + 1
            continue
        if days[i] < days[left] or days[i] < days[right]:
            left, right = i, i + k + 1
        i += 1
    return -1 if best == float("inf") else best


def _k_sum_brute(nums, k):
    sums = sorted((sum(nums[i] for i in range(len(nums)) if mask >> i & 1) for mask in range(1 << len(nums))), reverse=True)
    return sums[k - 1]


@problem(
    slug="find-the-k-sum-of-an-array", title="Find the K-Sum of an Array", difficulty="Hard", pattern=TK, tags=["Array", "Heap", "Sorting"],
    sig="kSum(self, nums: list[int], k: int) -> int",
    desc="""Consider the sums of all `2ⁿ` subsequences of `nums` (the empty subsequence has sum 0). Return the `k`th **largest** of these sums, counting equal sums separately.""",
    constraints=["1 ≤ n ≤ 10⁵", "-10⁹ ≤ nums[i] ≤ 10⁹", "1 ≤ k ≤ min(2000, 2ⁿ)"],
    samples=[([2, 4, -2], 5), ([1, -2, 3, 4, -10, 12], 16)],
    gen=lambda r: (lambda nums: (nums, r.randint(1, min(2000, 2 ** len(nums)))))(r.ints(r.randint(1, 8), -9, 9)),
    brute=_k_sum_brute,
    hints=[
        "The largest sum takes every positive number. Every other sum is that maximum minus something.",
        "Replace each number by its absolute value: removing a positive or adding a negative both cost |x|. Now find the k − 1 smallest subset costs.",
        "Sort the absolute values. Generate subset sums in increasing order with a min-heap: from (sum, i) produce (sum + a[i+1], i+1) and (sum − a[i] + a[i+1], i+1). The answer is max − (the kth smallest cost, counting 0 as the first).",
    ],
    insight="The kth largest sum is the maximum minus the kth smallest \"removal cost\", which a heap enumerates in order.",
    time="O(n log n + k log k)", space="O(k)",
    pitfalls=["Generating all 2ⁿ sums."],
)
def k_sum(nums, k):
    best = sum(x for x in nums if x > 0)
    costs = sorted(abs(x) for x in nums)
    heap, cost = [(costs[0], 0)], 0
    for _ in range(k - 1):
        cost, i = heapq.heappop(heap)
        if i + 1 < len(costs):
            heapq.heappush(heap, (cost + costs[i + 1], i + 1))
            heapq.heappush(heap, (cost - costs[i] + costs[i + 1], i + 1))
    return best - cost


def _max_product_brute(nums, k):
    v = list(nums)
    for _ in range(k):
        v[v.index(min(v))] += 1
    p = 1
    for x in v:
        p = p * x % (10**9 + 7)
    return p


@problem(
    slug="maximum-product-after-k-increments", title="Maximum Product After K Increments", difficulty="Medium", pattern=TK,
    tags=["Array", "Greedy", "Heap"],
    sig="maximumProduct(self, nums: list[int], k: int) -> int",
    desc="""`nums` holds non-negative integers. In one operation you add 1 to any element. After at most `k` operations, return the maximum product of all elements, modulo `10⁹ + 7` (maximize first, then take the modulo).""",
    constraints=["1 ≤ len(nums), k ≤ 10⁵", "0 ≤ nums[i] ≤ 10⁶"],
    samples=[([0, 4], 5), ([6, 3, 3, 2], 2)],
    gen=lambda r: (r.ints(r.randint(1, 8), 0, 10), r.randint(1, 15)),
    brute=_max_product_brute,
    hints=[
        "Adding 1 to a smaller number multiplies the product by a larger factor.",
        "So each increment should go to the current smallest element.",
        "Use a min-heap: pop the smallest, add 1, push it back, k times. Multiply everything together with the modulo at the end.",
    ],
    insight="Raising the minimum each time balances the values, which maximizes the product.",
    time="O(n + k log n)", space="O(n)",
    pitfalls=["Taking the modulo of individual elements before deciding where to add."],
)
def maximum_product(nums, k):
    heap = list(nums)
    heapq.heapify(heap)
    for _ in range(k):
        heapq.heapreplace(heap, heap[0] + 1)
    p = 1
    for x in heap:
        p = p * x % (10**9 + 7)
    return p


def _least_unique_brute(arr, k):
    from collections import Counter
    best = len(set(arr))
    for removed in combinations(range(len(arr)), k):
        rest = [arr[i] for i in range(len(arr)) if i not in removed]
        best = min(best, len(set(rest)))
    return best


@problem(
    slug="least-number-of-unique-integers-after-k-removals", title="Least Number of Unique Integers after K Removals", difficulty="Medium",
    pattern=TK, tags=["Array", "Hash Table", "Greedy", "Sorting", "Counting"],
    sig="findLeastNumOfUniqueInts(self, arr: list[int], k: int) -> int",
    desc="""Remove exactly `k` elements from `arr`. Return the least number of distinct integers that can remain.""",
    constraints=["1 ≤ len(arr) ≤ 10⁵", "1 ≤ arr[i] ≤ 10⁹", "0 ≤ k ≤ len(arr)"],
    samples=[([5, 5, 4], 1), ([4, 3, 1, 1, 3, 3, 2], 3)],
    gen=lambda r: (lambda a: (a, r.randint(0, len(a))))(r.ints(r.randint(1, 9), 1, 4)),
    brute=_least_unique_brute,
    hints=[
        "To eliminate a value you must remove all of its copies.",
        "Values with few copies are the cheapest to eliminate.",
        "Count frequencies, sort them ascending (or use a min-heap), and eliminate values while k covers their counts.",
    ],
    insight="Greedily remove the rarest values first.",
    time="O(n log n)", space="O(n)",
    pitfalls=["Removing one copy of many values instead of all copies of a few."],
)
def least_unique(arr, k):
    from collections import Counter
    counts = sorted(Counter(arr).values())
    left = len(counts)
    for c in counts:
        if k >= c:
            k -= c
            left -= 1
        else:
            break
    return left


@problem(
    slug="final-array-state-after-k-multiplication-operations-i", title="Final Array State After K Multiplication Operations I",
    difficulty="Easy", pattern=TK, tags=["Array", "Math", "Heap", "Simulation"],
    sig="getFinalState(self, nums: list[int], k: int, multiplier: int) -> list[int]",
    desc="""Repeat `k` times: find the minimum value in `nums` (the **first** one if there are ties) and multiply it by `multiplier`. Return the final array.""",
    constraints=["1 ≤ len(nums) ≤ 100", "1 ≤ nums[i] ≤ 100", "1 ≤ k ≤ 10", "1 ≤ multiplier ≤ 5"],
    samples=[([2, 1, 3, 5, 6], 5, 2), ([1, 2], 3, 4)],
    gen=lambda r: (r.ints(r.randint(1, 8), 1, 20), r.randint(1, 10), r.randint(1, 5)),
    brute=lambda nums, k, m: (lambda v: ([v.__setitem__(v.index(min(v)), min(v) * m) for _ in range(k)], v)[1])(list(nums)),
    hints=[
        "Each step needs the current minimum and its earliest position.",
        "A min-heap of (value, index) breaks ties by index automatically.",
        "Pop the top, write value × multiplier back at that index, push the new pair, k times.",
    ],
    insight="A heap keyed by (value, index) finds the first minimum quickly.",
    time="O(n + k log n)", space="O(n)",
    pitfalls=["Picking the last minimum instead of the first on ties."],
)
def final_state(nums, k, multiplier):
    nums = list(nums)
    heap = [(x, i) for i, x in enumerate(nums)]
    heapq.heapify(heap)
    for _ in range(k):
        x, i = heapq.heappop(heap)
        nums[i] = x * multiplier
        heapq.heappush(heap, (nums[i], i))
    return nums


def _big_kth_ops(r):
    k = 500
    ops, args = ["KthLargest"], [[k, r.ints(5000, -10000, 10000)]]
    for _ in range(3000):
        ops.append("add")
        args.append([r.randint(-10000, 10000)])
    return ops, args


def _unique_dist_points(r, n):
    seen, pts = set(), []
    while len(pts) < n:
        p = (r.randint(-10000, 10000), r.randint(-10000, 10000))
        d = p[0] ** 2 + p[1] ** 2
        if d not in seen:
            seen.add(d)
            pts.append(list(p))
    return pts


EXTRA = {
    "merge-sorted-array": {
        "edge": [([1], 1, [], 0), ([0], 0, [1], 1), ([2, 0], 1, [1], 1), ([4, 5, 6, 0, 0, 0], 3, [1, 2, 3], 3), ([-10**9, 0], 1, [10**9], 1)],
    },
    "merge-k-sorted-lists": {
        "edge": [([],), ([[]],), ([[], [1]],), ([[1], [1], [1]],), ([[-10000], [10000]],)],
        "large": [lambda r: ([r.sorted_ints(10, -10000, 10000) for _ in range(1000)],), lambda r: ([r.sorted_ints(500, -10000, 10000) for _ in range(20)],)],
    },
    "kth-smallest-number-in-m-sorted-lists": {
        "edge": [([[1]], 1), ([[], [], [5]], 1), ([[1, 1, 1], [1]], 4), ([[2], [1]], 10**9)],
        "large": [lambda r: ([r.sorted_ints(200, -10**9, 10**9) for _ in range(50)], 5000)],
    },
    "k-th-smallest-prime-fraction": {
        "edge": [([1, 2], 1), ([1, 2, 3], 3), ([1, 7, 23, 29, 47], 8)],
        "large": [lambda r: ([1] + _primes_upto(4000)[:500], 60000)],
    },
    "super-ugly-number": {
        "edge": [(1, [2]), (2, [997]), (15, [2]), (100, [2, 3, 5])],
        "edge_nb": [(100000, [2, 3, 5, 7, 11, 13, 17, 19, 23, 29])],
        "large": [lambda r: (30000, sorted(r.sample(_primes_upto(1000), 30)))],
    },
    "kth-largest-element-in-a-stream": {
        "edge": [(["KthLargest", "add", "add"], [[1, []], [-10000], [10000]]),
                 (["KthLargest", "add", "add", "add"], [[2, [0]], [-1], [1], [-2]]),
                 (["KthLargest", "add"], [[3, [5, 5]], [5]])],
        "large": [_big_kth_ops],
    },
    "k-closest-points-to-origin": {
        "edge": [([[0, 0]], 1), ([[1, 1], [2, 2]], 2), ([[-10000, -10000], [10000, 9999]], 1)],
        "large": [lambda r: (_unique_dist_points(r, 5000), 2500)],
    },
    "maximal-score-after-applying-k-operations": {
        "edge": [([1], 1), ([1], 100000), ([10**9], 3), ([1, 1, 1], 2)],
        "large": [lambda r: (r.ints(10000, 1, 10**9), 50000)],
    },
    "find-the-kth-largest-integer-in-the-array": {
        "edge": [(["0"], 1), (["9", "10"], 1), (["1" * 100, "9" * 99], 2), (["5", "5", "5"], 2)],
        "large": [lambda r: ([str(r.randint(0, 10 ** r.randint(1, 18))) for _ in range(8000)], 4000)],
    },
    "third-maximum-number": {
        "edge": [([1],), ([2, 2, 2],), ([1, 2],), ([-2147483648, 1, 1],), ([1, 2, -2147483648],), ([2147483647, 2147483646, 2147483645],)],
        "large": [lambda r: (r.ints(10000, -2**31, 2**31 - 1),)],
    },
    "minimum-cost-to-hire-k-workers": {
        "edge": [([1], [1], 1), ([10000], [1], 1), ([3, 1, 10, 10, 1], [4, 8, 2, 2, 7], 5), ([4, 5], [8, 10], 2)],
        "large": [lambda r: (r.ints(7000, 1, 10000), r.ints(7000, 1, 10000), 2000)],
    },
    "smallest-range-covering-elements-from-k-lists": {
        "edge": [([[1]],), ([[1], [1]],), ([[1, 2, 3], [100]],), ([[-100000], [100000]],), ([[10, 10], [11, 11]],)],
        "large": [lambda r: ([r.sorted_ints(20, -100000, 100000) for _ in range(500)],)],
    },
    "maximum-performance-of-a-team": {
        "edge": [(1, [1], [1], 1), (3, [100000, 100000, 100000], [10**8, 10**8, 10**8], 3), (2, [1, 1000], [1000, 1], 1)],
        "large": [lambda r: (7000, r.ints(7000, 1, 100000), r.ints(7000, 1, 10**8), 1500)],
    },
    "k-maximum-sum-combinations-from-two-arrays": {
        "edge": [([1], [1], 1), ([5, 5], [5, 5], 4), ([1, 2], [3, 4], 4)],
        "large": [lambda r: (r.ints(10000, 1, 10000), r.ints(10000, 1, 10000), 3000)],
    },
    "k-empty-slots": {
        "edge": [([1], 0), ([1, 2], 0), ([2, 1], 1), ([3, 1, 2], 1), ([6, 5, 8, 9, 7, 1, 10, 2, 3, 4], 2)],
        "large": [lambda r: (r.sample(range(1, 10001), 10000), 50), lambda r: (list(range(1, 10001)), 0)],
    },
    "find-the-k-sum-of-an-array": {
        "edge": [([5], 1), ([5], 2), ([-5], 1), ([0, 0], 4)],
        "large": [lambda r: (r.ints(8000, -10**9, 10**9), 2000)],
    },
    "maximum-product-after-k-increments": {
        "edge": [([0], 1), ([0, 0], 1), ([1000000], 100000), ([1, 1, 1], 3)],
        "large": [lambda r: (r.ints(10000, 0, 10**6), 100000)],
    },
    "least-number-of-unique-integers-after-k-removals": {
        "edge": [([1], 0), ([1], 1), ([2, 1, 1, 3, 3, 3], 3), ([10**9, 10**9], 1)],
        "large": [lambda r: (r.ints(15000, 1, 3000), 7000)],
    },
    "final-array-state-after-k-multiplication-operations-i": {"edge": [([1], 10, 5), ([100, 100], 1, 1), ([1, 1, 1], 3, 2)]},
}
