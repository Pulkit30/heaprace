from bisect import bisect_left, bisect_right
from math import gcd

from catalog_lib import problem

P = "binary-search"


@problem(
    slug="binary-search", title="Binary Search", difficulty="Easy", pattern=P, tags=["Array", "Binary Search"],
    sig="search(self, nums: list[int], target: int) -> int",
    desc="""`nums` is sorted in ascending order and has no duplicates. Return the index of `target`, or `-1` if it isn't there. Aim for O(log n).""",
    constraints=["1 ≤ len(nums) ≤ 10⁴", "-10⁴ ≤ nums[i], target ≤ 10⁴", "values are distinct"],
    samples=[([-1, 0, 3, 5, 9, 12], 9), ([-1, 0, 3, 5, 9, 12], 2)],
    tests=[([5], 5), ([5], -5)],
    gen=lambda r: (lambda a: (a, r.choice(a + [r.randint(-30, 30)])))(sorted(r.distinct(r.randint(1, 12), -30, 30))),
    brute=lambda nums, t: nums.index(t) if t in nums else -1,
    hints=[
        "Compare the target with the middle element to rule out half the array.",
        "Keep a range [lo, hi] that would contain the target if it exists.",
        "If the middle is too small, move lo past it; if too big, move hi before it; stop when lo > hi.",
    ],
    insight="Each comparison halves the search range, giving O(log n).",
    time="O(log n)", space="O(1)",
    pitfalls=["Off-by-one loops: with inclusive bounds, loop while lo ≤ hi."],
)
def binary_search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


@problem(
    slug="search-in-rotated-sorted-array-ii", title="Search in Rotated Sorted Array II", difficulty="Medium", pattern=P,
    tags=["Array", "Binary Search"],
    sig="search(self, nums: list[int], target: int) -> bool",
    desc="""A sorted array (which **may contain duplicates**) was rotated at some unknown pivot. Return `true` if `target` appears in it.""",
    constraints=["1 ≤ len(nums) ≤ 5000", "-10⁴ ≤ nums[i], target ≤ 10⁴"],
    samples=[([2, 5, 6, 0, 0, 1, 2], 0), ([2, 5, 6, 0, 0, 1, 2], 3)],
    tests=[([1, 0, 1, 1, 1], 0), ([1, 1, 1, 1], 2)],
    gen=lambda r: (lambda a, k: (a[k:] + a[:k], r.randint(-6, 6)))(r.sorted_ints(r.randint(1, 10), -5, 5), r.randint(0, 9)),
    brute=lambda nums, t: t in nums,
    hints=[
        "Without duplicates, one half around mid is always sorted, and you can tell which.",
        "Duplicates break that when nums[lo] == nums[mid] == nums[hi]: you can't tell which half is sorted.",
        "In that case shrink both ends by one and continue; otherwise use the sorted half to decide where the target can be.",
    ],
    insight="Rotated search works on the sorted half; duplicates force a linear step in the worst case.",
    time="O(log n) average, O(n) worst", space="O(1)",
    pitfalls=["Assuming nums[lo] ≤ nums[mid] means the left half is sorted when they are equal duplicates."],
)
def search_rotated_ii(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return True
        if nums[lo] == nums[mid] == nums[hi]:
            lo += 1
            hi -= 1
        elif nums[lo] <= nums[mid]:
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return False


@problem(
    slug="find-minimum-in-rotated-sorted-array", title="Find Minimum in Rotated Sorted Array", difficulty="Medium", pattern=P,
    tags=["Array", "Binary Search"],
    sig="findMin(self, nums: list[int]) -> int",
    desc="""A sorted array of **distinct** integers was rotated between 1 and n times. Return its minimum element in O(log n).""",
    constraints=["1 ≤ len(nums) ≤ 5000", "-5000 ≤ nums[i] ≤ 5000", "values are distinct"],
    samples=[([3, 4, 5, 1, 2],), ([4, 5, 6, 7, 0, 1, 2],), ([11, 13, 15, 17],)],
    gen=lambda r: (lambda a, k: (a[k:] + a[:k],))(sorted(r.distinct(r.randint(1, 12), -50, 50)), r.randint(0, 11)),
    brute=lambda nums: min(nums),
    hints=[
        "The minimum is the only element smaller than the one before it.",
        "Compare nums[mid] with nums[hi] to decide which side the drop is on.",
        "If nums[mid] > nums[hi], the minimum is to the right of mid; otherwise it is at mid or to its left. Narrow until lo meets hi.",
    ],
    insight="Comparing with the right end tells you which side of the rotation point you're on.",
    time="O(log n)", space="O(1)",
    pitfalls=["Comparing with nums[lo] instead, which fails when the array isn't rotated."],
)
def find_min(nums):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1
        else:
            hi = mid
    return nums[lo]


@problem(
    slug="find-k-closest-elements", title="Find K Closest Elements", difficulty="Medium", pattern=P,
    tags=["Array", "Two Pointers", "Binary Search", "Sliding Window", "Heap"],
    sig="findClosestElements(self, arr: list[int], k: int, x: int) -> list[int]",
    desc="""`arr` is sorted. Return the `k` integers closest to `x`, sorted ascending.

`a` is closer than `b` if `|a − x| < |b − x|`, or if they're equally close and `a < b`.""",
    constraints=["1 ≤ k ≤ len(arr) ≤ 10⁴", "arr is sorted", "-10⁴ ≤ arr[i], x ≤ 10⁴"],
    samples=[([1, 2, 3, 4, 5], 4, 3), ([1, 1, 2, 3, 4, 5], 4, -1)],
    gen=lambda r: (lambda a: (a, r.randint(1, len(a)), r.randint(-25, 25)))(r.sorted_ints(r.randint(1, 12), -20, 20)),
    brute=lambda arr, k, x: sorted(sorted(arr, key=lambda v: (abs(v - x), v))[:k]),
    hints=[
        "The answer is always a contiguous window of length k.",
        "Binary search for the window's left edge in [0, n − k].",
        "For a candidate left edge mid, if x − arr[mid] > arr[mid + k] − x, the window should move right; otherwise keep mid as a candidate.",
    ],
    insight="Searching for the window's start instead of x itself gives O(log(n − k) + k).",
    time="O(log(n − k) + k)", space="O(1)",
    pitfalls=["Using absolute values in the comparison, which breaks with duplicates."],
)
def find_closest(arr, k, x):
    lo, hi = 0, len(arr) - k
    while lo < hi:
        mid = (lo + hi) // 2
        if x - arr[mid] > arr[mid + k] - x:
            lo = mid + 1
        else:
            hi = mid
    return arr[lo:lo + k]


def _single_input(r):
    vals = sorted(r.distinct(r.randint(1, 8), -20, 20))
    lone = r.choice(vals)
    return (sorted([v for v in vals for _ in range(1 if v == lone else 2)]),)


@problem(
    slug="single-element-in-a-sorted-array", title="Single Element in a Sorted Array", difficulty="Medium", pattern=P,
    tags=["Array", "Binary Search"],
    sig="singleNonDuplicate(self, nums: list[int]) -> int",
    desc="""In the sorted array `nums`, every value appears exactly twice except one, which appears once. Find it in O(log n) time and O(1) space.""",
    constraints=["1 ≤ len(nums) ≤ 10⁵", "0 ≤ nums[i] ≤ 10⁵ (tests may use negatives)"],
    samples=[([1, 1, 2, 3, 3, 4, 4, 8, 8],), ([3, 3, 7, 7, 10, 11, 11],)],
    gen=_single_input,
    brute=lambda nums: next(v for v in nums if nums.count(v) == 1),
    hints=[
        "Before the single element, pairs start at even indices. After it, they start at odd indices.",
        "Look at an even index mid: is nums[mid] equal to nums[mid + 1]?",
        "If it is, the single element is to the right of the pair; otherwise it is at mid or to its left.",
    ],
    insight="The single element shifts the pair alignment, which binary search can detect.",
    time="O(log n)", space="O(1)",
    pitfalls=["Forgetting to force mid to an even index."],
)
def single_non_duplicate(nums):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if mid % 2:
            mid -= 1
        if nums[mid] == nums[mid + 1]:
            lo = mid + 2
        else:
            hi = mid
    return nums[lo]


def _split_brute(nums, k):
    from functools import lru_cache

    @lru_cache(None)
    def go(i, parts):
        if parts == 1:
            return sum(nums[i:])
        best, run = float("inf"), 0
        for j in range(i, len(nums) - parts + 1):
            run += nums[j]
            best = min(best, max(run, go(j + 1, parts - 1)))
        return best

    return go(0, k)


def _feasible_parts(nums, cap):
    parts, run = 1, 0
    for x in nums:
        if run + x > cap:
            parts += 1
            run = 0
        run += x
    return parts


@problem(
    slug="split-array-largest-sum", title="Split Array Largest Sum", difficulty="Hard", pattern=P,
    tags=["Array", "Binary Search", "Dynamic Programming", "Greedy", "Prefix Sum"],
    sig="splitArray(self, nums: list[int], k: int) -> int",
    desc="""Split `nums` into exactly `k` non-empty contiguous subarrays so that the largest subarray sum is as small as possible. Return that smallest possible largest sum.""",
    constraints=["1 ≤ len(nums) ≤ 1000", "0 ≤ nums[i] ≤ 10⁶", "1 ≤ k ≤ min(50, len(nums))"],
    samples=[([7, 2, 5, 10, 8], 2), ([1, 2, 3, 4, 5], 2), ([1, 4, 4], 3)],
    gen=lambda r: (lambda a: (a, r.randint(1, len(a))))(r.ints(r.randint(1, 9), 0, 20)),
    brute=_split_brute,
    hints=[
        "Flip the question: given a cap, can you split into at most k parts with every sum ≤ cap?",
        "That check is greedy: extend the current part until adding the next number would exceed the cap.",
        "The feasible caps form a range starting at some value between max(nums) and sum(nums). Binary search for the smallest feasible cap.",
    ],
    insight="Binary search on the answer with a greedy feasibility check.",
    time="O(n log(sum))", space="O(1)",
    pitfalls=["Starting the search below max(nums), where no split works."],
)
def split_array(nums, k):
    lo, hi = max(nums), sum(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if _feasible_parts(nums, mid) <= k:
            hi = mid
        else:
            lo = mid + 1
    return lo


@problem(
    slug="search-a-2d-matrix", title="Search a 2D Matrix", difficulty="Medium", pattern=P, tags=["Array", "Binary Search", "Matrix"],
    sig="searchMatrix(self, matrix: list[list[int]], target: int) -> bool",
    desc="""Each row of `matrix` is sorted, and each row's first value is greater than the previous row's last value. Return `true` if `target` is in the matrix, in O(log(m·n)).""",
    constraints=["1 ≤ m, n ≤ 100", "-10⁴ ≤ values, target ≤ 10⁴"],
    samples=[([[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 3), ([[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 13)],
    gen=lambda r: (lambda m, n: (lambda flat: ([flat[i * n:(i + 1) * n] for i in range(m)], r.choice(flat + [r.randint(-60, 60)])))(sorted(r.distinct(m * n, -60, 60))))(r.randint(1, 4), r.randint(1, 4)),
    brute=lambda matrix, t: any(t in row for row in matrix),
    hints=[
        "Read row by row, the whole matrix is one sorted list.",
        "Index k of that list is matrix[k // n][k % n].",
        "Run an ordinary binary search over k from 0 to m·n − 1.",
    ],
    insight="Treat the matrix as a flattened sorted array.",
    time="O(log(m·n))", space="O(1)",
    pitfalls=["Using m instead of n (the column count) to map the index."],
)
def search_matrix(matrix, target):
    m, n = len(matrix), len(matrix[0])
    lo, hi = 0, m * n - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        v = matrix[mid // n][mid % n]
        if v == target:
            return True
        if v < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return False


@problem(
    slug="find-first-and-last-position-of-element-in-sorted-array", title="Find First and Last Position of Element in Sorted Array",
    difficulty="Medium", pattern=P, tags=["Array", "Binary Search"],
    sig="searchRange(self, nums: list[int], target: int) -> list[int]",
    desc="""`nums` is sorted ascending. Return `[first, last]`, the first and last indices of `target`, or `[-1, -1]` if it's absent. Use O(log n) time.""",
    constraints=["0 ≤ len(nums) ≤ 10⁵", "-10⁹ ≤ nums[i], target ≤ 10⁹"],
    samples=[([5, 7, 7, 8, 8, 10], 8), ([5, 7, 7, 8, 8, 10], 6), ([], 0)],
    gen=lambda r: (lambda a: (a, r.randint(-6, 6)))(r.sorted_ints(r.randint(0, 12), -5, 5)),
    brute=lambda nums, t: [nums.index(t), len(nums) - 1 - nums[::-1].index(t)] if t in nums else [-1, -1],
    hints=[
        "Two binary searches: one for the leftmost position, one for the rightmost.",
        "For the leftmost, keep searching left even after finding the target.",
        "The first index with value ≥ target and the first index with value > target (minus one) bound the range.",
    ],
    insight="Lower-bound and upper-bound searches find both edges in O(log n).",
    time="O(log n)", space="O(1)",
    pitfalls=["Expanding linearly from a found index, which is O(n) on long runs."],
)
def search_range(nums, target):
    lo = bisect_left(nums, target)
    if lo == len(nums) or nums[lo] != target:
        return [-1, -1]
    return [lo, bisect_right(nums, target) - 1]


@problem(
    slug="search-insert-position", title="Search Insert Position", difficulty="Easy", pattern=P, tags=["Array", "Binary Search"],
    sig="searchInsert(self, nums: list[int], target: int) -> int",
    desc="""`nums` is sorted and has distinct values. Return the index of `target` if present, otherwise the index where it would be inserted to keep the order.""",
    constraints=["1 ≤ len(nums) ≤ 10⁴", "values are distinct", "-10⁴ ≤ nums[i], target ≤ 10⁴"],
    samples=[([1, 3, 5, 6], 5), ([1, 3, 5, 6], 2), ([1, 3, 5, 6], 7)],
    gen=lambda r: (sorted(r.distinct(r.randint(1, 10), -20, 20)), r.randint(-25, 25)),
    brute=lambda nums, t: sum(1 for v in nums if v < t),
    hints=[
        "You want the first position whose value is at least the target.",
        "That's a lower-bound binary search.",
        "Keep hi = len(nums) so that \"after everything\" is a valid result; shrink until lo == hi.",
    ],
    insight="The insert position is the lower bound of the target.",
    time="O(log n)", space="O(1)",
    pitfalls=["Using hi = n − 1 and missing the after-the-end case."],
)
def search_insert(nums, target):
    lo, hi = 0, len(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo


@problem(
    slug="sqrtx", title="Sqrt(x)", difficulty="Easy", pattern=P, tags=["Math", "Binary Search"],
    sig="mySqrt(self, x: int) -> int",
    desc="""Return the square root of the non-negative integer `x`, rounded down. Don't use a built-in power or square root function.""",
    constraints=["0 ≤ x ≤ 2³¹ − 1"],
    samples=[(4,), (8,), (0,)],
    tests=[(1,), (2147395599,), (2147483647,)],
    gen=lambda r: (r.randint(0, 10 ** r.randint(1, 9)),),
    brute=lambda x: next(i for i in range(int(x ** 0.5) + 2, -1, -1) if i * i <= x),
    hints=[
        "You want the largest integer r with r·r ≤ x.",
        "The condition r·r ≤ x is true for small r and false for large r.",
        "Binary search r in [0, x], keeping the last mid that satisfied the condition.",
    ],
    insight="A monotone condition (r² ≤ x) lets binary search find the boundary.",
    time="O(log x)", space="O(1)",
    pitfalls=["Overflow in other languages when squaring mid; compare mid with x / mid instead."],
)
def my_sqrt(x):
    lo, hi = 0, x
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if mid * mid <= x:
            lo = mid
        else:
            hi = mid - 1
    return lo


@problem(
    slug="koko-eating-bananas", title="Koko Eating Bananas", difficulty="Medium", pattern=P, tags=["Array", "Binary Search"],
    sig="minEatingSpeed(self, piles: list[int], h: int) -> int",
    desc="""There are `piles` of bananas and `h` hours. Each hour Koko picks one pile and eats `k` bananas from it (or the rest of the pile if fewer remain); she doesn't move on to another pile in the same hour.

Return the minimum integer speed `k` that lets her finish everything within `h` hours.""",
    constraints=["1 ≤ len(piles) ≤ h ≤ 10⁹", "1 ≤ piles[i] ≤ 10⁹"],
    samples=[([3, 6, 7, 11], 8), ([30, 11, 23, 4, 20], 5), ([30, 11, 23, 4, 20], 6)],
    gen=lambda r: (lambda p: (p, r.randint(len(p), len(p) * 4)))(r.ints(r.randint(1, 8), 1, 30)),
    brute=lambda piles, h: next(k for k in range(1, max(piles) + 1) if sum(-(-p // k) for p in piles) <= h),
    hints=[
        "At speed k, a pile p takes ceil(p / k) hours.",
        "Faster speeds never take more hours, so feasibility is monotone in k.",
        "Binary search k in [1, max(piles)], checking whether the total hours fit in h.",
    ],
    insight="Binary search on the answer: the smallest speed whose total hours ≤ h.",
    time="O(n log max)", space="O(1)",
    pitfalls=["Using floor division for hours per pile."],
)
def min_eating_speed(piles, h):
    lo, hi = 1, max(piles)
    while lo < hi:
        mid = (lo + hi) // 2
        if sum(-(-p // mid) for p in piles) <= h:
            hi = mid
        else:
            lo = mid + 1
    return lo


@problem(
    slug="capacity-to-ship-packages-within-d-days", title="Capacity To Ship Packages Within D Days", difficulty="Medium", pattern=P,
    tags=["Array", "Binary Search"],
    sig="shipWithinDays(self, weights: list[int], days: int) -> int",
    desc="""Packages must ship in the given order. Each day the ship is loaded with consecutive packages whose total weight doesn't exceed its capacity. Return the least capacity that ships everything within `days` days.""",
    constraints=["1 ≤ days ≤ len(weights) ≤ 5 × 10⁴", "1 ≤ weights[i] ≤ 500"],
    samples=[([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5), ([3, 2, 2, 4, 1, 4], 3), ([1, 2, 3, 1, 1], 4)],
    gen=lambda r: (lambda w: (w, r.randint(1, len(w))))(r.ints(r.randint(1, 10), 1, 15)),
    brute=lambda w, d: next(c for c in range(max(w), sum(w) + 1) if _feasible_parts(w, c) <= d),
    hints=[
        "The capacity is at least the heaviest package and at most the total weight.",
        "For a given capacity, load greedily day by day and count the days needed.",
        "A larger capacity never needs more days, so binary search for the smallest capacity that fits.",
    ],
    insight="Same shape as Split Array Largest Sum: binary search with a greedy day count.",
    time="O(n log(sum))", space="O(1)",
    pitfalls=["Starting the search at 1, below the heaviest package."],
)
def ship_within_days(weights, days):
    lo, hi = max(weights), sum(weights)
    while lo < hi:
        mid = (lo + hi) // 2
        if _feasible_parts(weights, mid) <= days:
            hi = mid
        else:
            lo = mid + 1
    return lo


def _median_brute(a, b):
    m = sorted(a + b)
    n = len(m)
    return m[n // 2] if n % 2 else (m[n // 2 - 1] + m[n // 2]) / 2


@problem(
    slug="median-of-two-sorted-arrays", title="Median of Two Sorted Arrays", difficulty="Hard", pattern=P,
    tags=["Array", "Binary Search", "Divide and Conquer"],
    sig="findMedianSortedArrays(self, nums1: list[int], nums2: list[int]) -> float", compare="approx",
    desc="""Given two sorted arrays, return the median of all their elements combined. Aim for O(log(m + n)). Answers within 10⁻⁵ are accepted.""",
    constraints=["0 ≤ m, n ≤ 1000", "1 ≤ m + n ≤ 2000", "-10⁶ ≤ values ≤ 10⁶"],
    samples=[([1, 3], [2]), ([1, 2], [3, 4])],
    tests=[([], [1]), ([2], [])],
    gen=lambda r: (lambda a, b: (a, b) if a or b else (a, [1]))(r.sorted_ints(r.randint(0, 7), -9, 9), r.sorted_ints(r.randint(0, 7), -9, 9)),
    brute=_median_brute,
    hints=[
        "The median splits the combined elements into a left half and a right half of equal size.",
        "If you take i elements from the shorter array for the left half, you must take half − i from the other.",
        "Binary search i so that the largest left element of each array is ≤ the smallest right element of the other. The median comes from the elements around the cut.",
    ],
    insight="Binary search the partition point of the shorter array.",
    time="O(log min(m, n))", space="O(1)",
    pitfalls=["Not handling empty halves; use ±infinity for missing neighbors."],
)
def median_two(nums1, nums2):
    a, b = (nums1, nums2) if len(nums1) <= len(nums2) else (nums2, nums1)
    m, n = len(a), len(b)
    half = (m + n + 1) // 2
    lo, hi = 0, m
    inf = float("inf")
    while True:
        i = (lo + hi) // 2
        j = half - i
        al = a[i - 1] if i else -inf
        ar = a[i] if i < m else inf
        bl = b[j - 1] if j else -inf
        br = b[j] if j < n else inf
        if al <= br and bl <= ar:
            if (m + n) % 2:
                return max(al, bl)
            return (max(al, bl) + min(ar, br)) / 2
        if al > br:
            hi = i - 1
        else:
            lo = i + 1


@problem(
    slug="minimum-time-to-complete-trips", title="Minimum Time to Complete Trips", difficulty="Medium", pattern=P,
    tags=["Array", "Binary Search"],
    sig="minimumTime(self, time: list[int], totalTrips: int) -> int",
    desc="""Bus `i` needs `time[i]` units for one trip and starts the next trip immediately. All buses run at once, independently. Return the minimum time for them to complete at least `totalTrips` trips in total.""",
    constraints=["1 ≤ len(time) ≤ 10⁵", "1 ≤ time[i], totalTrips ≤ 10⁷"],
    samples=[([1, 2, 3], 5), ([2], 1)],
    gen=lambda r: (r.ints(r.randint(1, 6), 1, 10), r.randint(1, 30)),
    brute=lambda time, total: next(t for t in range(1, 10**6) if sum(t // x for x in time) >= total),
    hints=[
        "By time t, bus i has finished t // time[i] trips.",
        "The total number of trips only grows with t.",
        "Binary search t between 1 and min(time) × totalTrips, checking whether the trip count reaches totalTrips.",
    ],
    insight="Binary search on time with a counting check.",
    time="O(n log(min(time) · totalTrips))", space="O(1)",
    pitfalls=["Using the max bus time for the upper bound when the min suffices (both work, but max is larger)."],
)
def minimum_time(time, totalTrips):
    lo, hi = 1, min(time) * totalTrips
    while lo < hi:
        mid = (lo + hi) // 2
        if sum(mid // x for x in time) >= totalTrips:
            hi = mid
        else:
            lo = mid + 1
    return lo


def _magical_brute(n, a, b):
    if n > 10**4:
        return nth_magical(n, a, b)
    count, x = 0, 0
    while count < n:
        x += 1
        if x % a == 0 or x % b == 0:
            count += 1
    return x % (10**9 + 7)


@problem(
    slug="nth-magical-number", title="Nth Magical Number", difficulty="Hard", pattern=P, tags=["Math", "Binary Search"],
    sig="nthMagicalNumber(self, n: int, a: int, b: int) -> int",
    desc="""A positive integer is **magical** if it is divisible by `a` or by `b`. Return the `n`th magical number modulo `10⁹ + 7`.""",
    constraints=["1 ≤ n ≤ 10⁹", "2 ≤ a, b ≤ 4 × 10⁴"],
    samples=[(1, 2, 3), (4, 2, 3)],
    tests=[(1000000000, 40000, 40000)],
    gen=lambda r: (r.randint(1, 60), r.randint(2, 12), r.randint(2, 12)),
    brute=_magical_brute,
    hints=[
        "Count magical numbers up to x with inclusion–exclusion: x // a + x // b − x // lcm(a, b).",
        "That count never decreases as x grows.",
        "Binary search the smallest x whose count reaches n, then take it modulo 10⁹ + 7.",
    ],
    insight="Inclusion–exclusion counting plus binary search on the value.",
    time="O(log(n · min(a, b)))", space="O(1)",
    pitfalls=["Double-counting multiples of both a and b."],
)
def nth_magical(n, a, b):
    l = a * b // gcd(a, b)
    lo, hi = 1, n * min(a, b)
    while lo < hi:
        mid = (lo + hi) // 2
        if mid // a + mid // b - mid // l >= n:
            hi = mid
        else:
            lo = mid + 1
    return lo % (10**9 + 7)


def _bounded_brute(n, index, maxSum):
    best = 0
    for v in range(1, maxSum + 1):
        if _bounded_sum(n, index, v) <= maxSum:
            best = v
    return best


def _bounded_sum(n, index, v):
    def side(length):
        # Values v-1, v-2, ... down to 1, then 1s.
        if v - 1 >= length:
            return (v - 1 + v - length) * length // 2
        return (v - 1) * v // 2 + (length - (v - 1))
    return v + side(index) + side(n - index - 1)


@problem(
    slug="maximum-value-at-a-given-index-in-a-bounded-array", title="Maximum Value at a Given Index in a Bounded Array",
    difficulty="Medium", pattern=P, tags=["Binary Search", "Greedy"],
    sig="maxValue(self, n: int, index: int, maxSum: int) -> int",
    desc="""Build an array `nums` of length `n` such that:

- every element is a positive integer,
- neighboring elements differ by at most 1,
- the sum of all elements is at most `maxSum`.

Return the largest possible value of `nums[index]`.""",
    constraints=["1 ≤ n ≤ maxSum ≤ 10⁹", "0 ≤ index < n"],
    samples=[(4, 2, 6), (6, 1, 10)],
    gen=lambda r: (lambda n: (n, r.randint(0, n - 1), r.randint(n, 40)))(r.randint(1, 8)),
    brute=_bounded_brute,
    hints=[
        "For a peak value v at index, the cheapest array decreases by 1 on each side until it hits 1.",
        "That minimal sum can be computed with arithmetic series, and it grows with v.",
        "Binary search the largest v whose minimal sum is ≤ maxSum.",
    ],
    insight="The minimal sum for a peak is a closed-form formula, so binary search the peak.",
    time="O(log maxSum)", space="O(1)",
    pitfalls=["Forgetting that values can't drop below 1."],
)
def max_value(n, index, maxSum):
    lo, hi = 1, maxSum
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if _bounded_sum(n, index, mid) <= maxSum:
            lo = mid
        else:
            hi = mid - 1
    return lo


def _neg_grid(r):
    m, n = r.randint(1, 5), r.randint(1, 5)
    grid = [[0] * n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            cap = min(grid[i - 1][j] if i else 6, grid[i][j - 1] if j else 6)
            grid[i][j] = cap - r.randint(0, 3)
    return (grid,)


@problem(
    slug="count-negative-numbers-in-a-sorted-matrix", title="Count Negative Numbers in a Sorted Matrix", difficulty="Easy", pattern=P,
    tags=["Array", "Binary Search", "Matrix"],
    sig="countNegatives(self, grid: list[list[int]]) -> int",
    desc="""Every row and every column of `grid` is sorted in **non-increasing** order. Return how many negative numbers it contains.""",
    constraints=["1 ≤ m, n ≤ 100", "-100 ≤ grid[i][j] ≤ 100"],
    samples=[([[4, 3, 2, -1], [3, 2, 1, -1], [1, 1, -1, -2], [-1, -1, -2, -3]],), ([[3, 2], [1, 0]],)],
    gen=_neg_grid,
    tests=[([[-1]],), ([[5, 1, 0], [-5, -5, -5]],)],
    brute=lambda grid: sum(1 for row in grid for v in row if v < 0),
    hints=[
        "Within a row, the negatives form a suffix.",
        "Going down a row, the first negative can only move left.",
        "Walk the rows from top to bottom, moving a column pointer left only while it points at a negative, counting whole row suffixes at a time.",
    ],
    insight="The sorted rows and columns allow an O(m + n) staircase walk.",
    time="O(m + n)", space="O(1)",
    pitfalls=["Scanning every cell, which ignores the ordering."],
)
def count_negatives(grid):
    n = len(grid[0])
    col, count = n, 0
    for row in grid:
        while col > 0 and row[col - 1] < 0:
            col -= 1
        count += n - col
    return count


@problem(
    slug="arranging-coins", title="Arranging Coins", difficulty="Easy", pattern=P, tags=["Math", "Binary Search"],
    sig="arrangeCoins(self, n: int) -> int",
    desc="""You build a staircase with `n` coins: row `i` needs exactly `i` coins. Return the number of **complete** rows.""",
    constraints=["1 ≤ n ≤ 2³¹ − 1"],
    samples=[(5,), (8,), (1,)],
    tests=[(2147483647,), (3,)],
    gen=lambda r: (r.randint(1, 10 ** r.randint(1, 9)),),
    brute=lambda n: next(k for k in range(int((2 * n) ** 0.5) + 2, -1, -1) if k * (k + 1) // 2 <= n),
    hints=[
        "k complete rows need k(k + 1) / 2 coins.",
        "That number grows with k.",
        "Binary search the largest k with k(k + 1) / 2 ≤ n.",
    ],
    insight="Binary search on a triangular-number condition.",
    time="O(log n)", space="O(1)",
    pitfalls=["Counting the last partial row."],
)
def arrange_coins(n):
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if mid * (mid + 1) // 2 <= n:
            lo = mid
        else:
            hi = mid - 1
    return lo


def _rotated(r, n, lo, hi):
    a = sorted(r.distinct(n, lo, hi))
    k = r.randint(0, n - 1)
    return a[k:] + a[:k]


def _pairs_with_single(r, n):
    vals = sorted(r.distinct(n, 0, 100000))
    lone = r.choice(vals)
    return ([v for v in vals for _ in range(1 if v == lone else 2)],)


EXTRA = {
    "binary-search": {
        "edge": [([5], 5), ([5], 6), ([1, 2], 1), ([1, 2], 2), ([-10000, 10000], 10000), ([1, 3, 5], 4)],
        "large": [lambda r: (lambda a: (a, a[-1]))(sorted(r.distinct(10000, -10000, 10000)))],
    },
    "search-in-rotated-sorted-array-ii": {
        "edge": [([1], 1), ([1], 0), ([1, 1, 1, 1, 1, 2, 1, 1], 2), ([2, 2, 2, 0, 2, 2], 0), ([3, 1], 1)],
        "large": [lambda r: ([1] * 2500 + [0] + [1] * 2499, 0)],
    },
    "find-minimum-in-rotated-sorted-array": {
        "edge": [([1],), ([2, 1],), ([1, 2],), ([5000, -5000],), ([2, 3, 4, 5, 1],)],
        "large": [lambda r: (_rotated(r, 5000, -5000, 5000),)],
    },
    "find-k-closest-elements": {
        "edge": [([1], 1, 5), ([1, 1, 1, 10, 10, 10], 1, 9), ([1, 2], 2, -10000), ([1, 3], 1, 2), ([0, 0, 1, 2, 3, 3, 4, 7, 7, 8], 3, 5)],
        "large": [lambda r: (r.sorted_ints(10000, -10000, 10000), 3000, r.randint(-10000, 10000))],
    },
    "single-element-in-a-sorted-array": {
        "edge": [([1],), ([1, 2, 2],), ([1, 1, 2],), ([0, 0, 1, 1, 2],)],
        "large": [lambda r: _pairs_with_single(r, 9001)],
    },
    "split-array-largest-sum": {
        "edge": [([0], 1), ([0, 0, 0], 2), ([1000000], 1), ([1, 2, 3], 3), ([1, 4, 4], 3)],
        "edge_nb": [([1000000] * 1000, 50)],
        "large": [lambda r: (r.ints(1000, 0, 10**6), 37)],
    },
    "search-a-2d-matrix": {
        "edge": [([[1]], 1), ([[1]], 2), ([[1, 3]], 3), ([[1], [3]], 2), ([[-10000, 10000]], 10000)],
        "large": [lambda r: (lambda flat: ([flat[i * 100:(i + 1) * 100] for i in range(100)], flat[-1]))(sorted(r.distinct(10000, -10000, 10000)))],
    },
    "find-first-and-last-position-of-element-in-sorted-array": {
        "edge": [([1], 1), ([1], 0), ([2, 2], 2), ([1, 2, 3], 3), ([-10**9, 10**9], 10**9)],
        "large": [lambda r: ([7] * 20000, 7), lambda r: (r.sorted_ints(15000, -100, 100), 5)],
    },
    "search-insert-position": {
        "edge": [([1], 0), ([1], 2), ([1], 1), ([1, 3], 2), ([-10000], 10000)],
        "large": [lambda r: (sorted(r.distinct(10000, -10000, 10000)), 1)],
    },
    "sqrtx": {"edge": [(2,), (3,), (9,), (2147395600,), (2147395599,)]},
    "koko-eating-bananas": {
        "edge": [([1], 1), ([312884470], 312884469), ([3, 6, 7, 11], 4), ([30, 11, 23, 4, 20], 30)],
        "edge_nb": [([1000000000], 2), ([1000000000], 1000000000), ([805306368, 805306368, 805306368], 1000000000)],
        "large": [lambda r: (r.ints(10000, 1, 10**9), 10**9)],
    },
    "capacity-to-ship-packages-within-d-days": {
        "edge": [([1], 1), ([500, 500], 1), ([500, 500], 2), ([1, 2, 3, 1, 1], 5)],
        "large": [lambda r: (r.ints(20000, 1, 500), 3), lambda r: (r.ints(20000, 1, 500), 9999)],
    },
    "median-of-two-sorted-arrays": {
        "edge": [([1], []), ([], [2, 3]), ([1, 2], [3, 4, 5]), ([1, 1], [1, 1]), ([-1000000], [1000000])],
        "large": [lambda r: (r.sorted_ints(1000, -10**6, 10**6), r.sorted_ints(1000, -10**6, 10**6))],
    },
    "minimum-time-to-complete-trips": {
        "edge": [([1], 1), ([5, 10, 10], 9), ([2], 3)],
        "edge_nb": [([10000000] * 3, 10000000), ([10000000], 10000000)],
        "large": [lambda r: (r.ints(15000, 1, 10**7), 10**7)],
    },
    "nth-magical-number": {
        "edge": [(1, 2, 2), (5, 2, 4), (3, 6, 4)],
        "edge_nb": [(1000000000, 39999, 40000), (999999999, 2, 3)],
    },
    "maximum-value-at-a-given-index-in-a-bounded-array": {
        "edge": [(1, 0, 1), (1, 0, 10), (3, 2, 18), (6, 1, 10)],
        "edge_nb": [(1, 0, 1000000000), (1000000000, 0, 1000000000), (3, 1, 1000000000), (8257285, 4828516, 850015631)],
    },
    "count-negative-numbers-in-a-sorted-matrix": {
        "edge": [([[1]],), ([[-1, -1], [-1, -1]],), ([[3, 2], [1, 0]],), ([[5, 1, 0], [-5, -5, -5]],)],
        "large": [lambda r: ([[100 - i - j for j in range(100)] for i in range(100)],)],
    },
    "arranging-coins": {"edge": [(1,), (2,), (3,), (6,), (1804289383,)]},
}
