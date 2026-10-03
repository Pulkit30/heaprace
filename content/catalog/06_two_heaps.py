import heapq
from bisect import insort

from catalog_lib import problem

P = "two-heaps"
H = "heap"


class _MedianRef:
    def __init__(self):
        self.vals = []

    def addNum(self, num):
        insort(self.vals, num)

    def findMedian(self):
        v, n = self.vals, len(self.vals)
        return float(v[n // 2]) if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2


def _median_ops(r):
    ops, args = ["MedianFinder", "addNum"], [[], [r.randint(-20, 20)]]
    for _ in range(r.randint(3, 20)):
        if r.random() < 0.6:
            ops.append("addNum")
            args.append([r.randint(-20, 20)])
        else:
            ops.append("findMedian")
            args.append([])
    ops.append("findMedian")
    args.append([])
    return ops, args


@problem(
    slug="find-median-from-data-stream", title="Find Median from Data Stream", difficulty="Hard", pattern=P,
    tags=["Design", "Heap", "Two Heaps", "Data Stream"],
    design=True, cls="MedianFinder", compare="approx",
    starter="""class MedianFinder:
    def __init__(self):
        pass

    def addNum(self, num: int) -> None:
        pass

    def findMedian(self) -> float:
        pass
""",
    desc="""Design `MedianFinder`, which receives numbers one at a time and can report the median of everything received so far:

- `addNum(num)` adds a number.
- `findMedian()` returns the median: the middle value, or the average of the two middle values when the count is even.

Tests call the class with a list of operations and arguments; `findMedian` is never called before the first `addNum`. Answers within 10⁻⁵ are accepted.""",
    constraints=["-10⁵ ≤ num ≤ 10⁵", "at most 5 × 10⁴ calls"],
    samples=[(["MedianFinder", "addNum", "addNum", "findMedian", "addNum", "findMedian"], [[], [1], [2], [], [3], []]),
             (["MedianFinder", "addNum", "findMedian", "addNum", "findMedian"], [[], [-5], [], [5], []])],
    gen=_median_ops,
    hints=[
        "Sorting after every insert is too slow. You only ever need the middle element(s).",
        "Split the numbers into a lower half and an upper half.",
        "Keep a max-heap for the lower half and a min-heap for the upper half, balanced so their sizes differ by at most one. The median comes from the heap tops.",
    ],
    insight="Two heaps keep the two halves of the data, exposing the middle in O(1) with O(log n) inserts.",
    time="O(log n) per add, O(1) per median", space="O(n)",
    pitfalls=["Forgetting to rebalance after every insertion.", "Integer division when averaging the two middles."],
)
class MedianFinder(_MedianRef):
    pass


def _window_median_brute(nums, k):
    out = []
    for i in range(len(nums) - k + 1):
        w = sorted(nums[i:i + k])
        out.append(float(w[k // 2]) if k % 2 else (w[k // 2 - 1] + w[k // 2]) / 2)
    return out


@problem(
    slug="sliding-window-median", title="Sliding Window Median", difficulty="Hard", pattern=P,
    tags=["Array", "Sliding Window", "Heap", "Two Heaps"],
    sig="medianSlidingWindow(self, nums: list[int], k: int) -> list[float]", compare="approx",
    desc="""A window of size `k` slides across `nums` one position at a time. Return the median of every window (the middle value, or the average of the two middle values when `k` is even). Answers within 10⁻⁵ are accepted.""",
    constraints=["1 ≤ k ≤ len(nums) ≤ 10⁵", "-2³¹ ≤ nums[i] ≤ 2³¹ − 1"],
    samples=[([1, 3, -1, -3, 5, 3, 6, 7], 3), ([1, 2, 3, 4, 2, 3, 1, 4, 2], 3)],
    tests=[([1], 1), ([1, 4, 2, 3], 4), ([2147483647, 2147483647], 2)],
    gen=lambda r: (lambda nums: (nums, r.randint(1, len(nums))))(r.ints(r.randint(1, 20), -20, 20)),
    brute=_window_median_brute,
    hints=[
        "Sorting each window costs O(k log k). Can you reuse the previous window?",
        "Keep the window split into a lower max-heap and an upper min-heap, as for a stream median.",
        "Heaps can't delete arbitrary elements quickly, so delete lazily: record outgoing values and discard them when they reach a heap top, tracking each heap's real size for balancing.",
    ],
    insight="Two heaps plus lazy deletion maintain a sliding median in O(n log k).",
    time="O(n log k)", space="O(k)",
    pitfalls=["Overflow when adding two large values in other languages.", "Balancing by raw heap sizes that still contain lazily deleted items."],
)
def median_sliding_window(nums, k):
    from bisect import bisect_left
    window = sorted(nums[:k])
    out = []
    for i in range(k, len(nums) + 1):
        out.append(float(window[k // 2]) if k % 2 else (window[k // 2 - 1] + window[k // 2]) / 2)
        if i == len(nums):
            break
        window.pop(bisect_left(window, nums[i - k]))
        insort(window, nums[i])
    return out


def _rooms3_brute(n, meetings):
    rooms_free = [0] * n
    counts = [0] * n
    for s, e in sorted(meetings):
        dur = e - s
        free = [r for r in range(n) if rooms_free[r] <= s]
        if free:
            r = min(free)
            rooms_free[r] = e
        else:
            r = min(range(n), key=lambda x: (rooms_free[x], x))
            rooms_free[r] += dur
        counts[r] += 1
    return counts.index(max(counts))


@problem(
    slug="meeting-rooms-iii", title="Meeting Rooms III", difficulty="Hard", pattern=P, tags=["Array", "Heap", "Two Heaps", "Simulation"],
    sig="mostBooked(self, n: int, meetings: list[list[int]]) -> int",
    desc="""There are `n` rooms numbered `0` to `n − 1`. Meetings `[start, end)` have distinct start times and are handled in order of start time:

1. Each meeting takes the **lowest-numbered free** room.
2. If no room is free, the meeting waits for the room that frees up **earliest** (lowest number on ties) and keeps its original duration.

Return the room that held the most meetings (the lowest number on ties).""",
    constraints=["1 ≤ n ≤ 100", "1 ≤ len(meetings) ≤ 10⁵", "0 ≤ start < end ≤ 5 × 10⁵", "starts are distinct"],
    samples=[(2, [[0, 10], [1, 5], [2, 7], [3, 4]]), (3, [[1, 20], [2, 10], [3, 5], [4, 9], [6, 8]])],
    gen=lambda r: (r.randint(1, 4), [[s, s + r.randint(1, 10)] for s in r.distinct(r.randint(1, 10), 0, 30)]),
    brute=_rooms3_brute,
    hints=[
        "You need two things quickly: the lowest-numbered free room, and the busy room that frees up first.",
        "Keep a min-heap of free room numbers, and a min-heap of (end time, room) for busy rooms.",
        "For each meeting in start order, first move every busy room whose end ≤ start back to the free heap. If a room is free, use it; otherwise pop the earliest-ending busy room and delay the meeting to start then.",
    ],
    insight="One heap orders free rooms by number, the other orders busy rooms by end time.",
    time="O(m log m + m log n)", space="O(n)",
    pitfalls=["Forgetting that a delayed meeting keeps its duration, so its new end is old end + duration."],
)
def most_booked(n, meetings):
    free = list(range(n))
    busy, counts = [], [0] * n
    for s, e in sorted(meetings):
        while busy and busy[0][0] <= s:
            _, room = heapq.heappop(busy)
            heapq.heappush(free, room)
        if free:
            room = heapq.heappop(free)
            heapq.heappush(busy, (e, room))
        else:
            end, room = heapq.heappop(busy)
            heapq.heappush(busy, (end + e - s, room))
        counts[room] += 1
    return counts.index(max(counts))


def _sticks_brute(sticks):
    sticks, cost = sorted(sticks), 0
    while len(sticks) > 1:
        a, b = sticks.pop(0), sticks.pop(0)
        cost += a + b
        insort(sticks, a + b)
    return cost


@problem(
    slug="minimum-cost-to-connect-sticks", title="Minimum Cost to Connect Sticks", difficulty="Medium", pattern=H, tags=["Array", "Greedy", "Heap"],
    sig="connectSticks(self, sticks: list[int]) -> int",
    desc="""You can join any two sticks of lengths `x` and `y` into one stick of length `x + y`, paying `x + y`. Return the minimum total cost to join all the sticks into one.""",
    constraints=["1 ≤ len(sticks) ≤ 10⁴", "1 ≤ sticks[i] ≤ 10⁴"],
    samples=[([2, 4, 3],), ([1, 8, 3, 5],), ([5],)],
    gen=lambda r: (r.ints(r.randint(1, 15), 1, 30),),
    brute=_sticks_brute,
    hints=[
        "Sticks joined early are paid for again in every later join they're part of.",
        "So the shortest sticks should be joined first.",
        "Keep a min-heap; repeatedly pop the two smallest, add their sum to the cost, and push the sum back.",
    ],
    insight="This is Huffman coding: always merge the two smallest.",
    time="O(n log n)", space="O(n)",
    pitfalls=["Sorting once and joining left to right, which ignores newly created sticks."],
)
def connect_sticks(sticks):
    heap = list(sticks)
    heapq.heapify(heap)
    cost = 0
    while len(heap) > 1:
        s = heapq.heappop(heap) + heapq.heappop(heap)
        cost += s
        heapq.heappush(heap, s)
    return cost


def _pass_ratio_brute(classes, extra):
    classes = [list(c) for c in classes]
    for _ in range(extra):
        best = max(range(len(classes)), key=lambda i: (classes[i][0] + 1) / (classes[i][1] + 1) - classes[i][0] / classes[i][1])
        classes[best][0] += 1
        classes[best][1] += 1
    return sum(p / t for p, t in classes) / len(classes)


@problem(
    slug="maximum-average-pass-ratio", title="Maximum Average Pass Ratio", difficulty="Medium", pattern=H, tags=["Array", "Greedy", "Heap"],
    sig="maxAverageRatio(self, classes: list[list[int]], extraStudents: int) -> float", compare="approx",
    desc="""`classes[i] = [pass, total]`: in class `i`, `pass` of `total` students will pass the exam. You have `extraStudents` brilliant students who will pass any class they join. Assign each of them to some class to **maximize the average pass ratio** across all classes, and return that average. Answers within 10⁻⁵ are accepted.""",
    constraints=["1 ≤ len(classes) ≤ 10⁵", "1 ≤ pass ≤ total ≤ 10⁵", "1 ≤ extraStudents ≤ 10⁵"],
    samples=[([[1, 2], [3, 5], [2, 2]], 2), ([[2, 4], [3, 9], [4, 5], [2, 10]], 4)],
    gen=lambda r: ([(lambda t: [r.randint(1, t), t])(r.randint(1, 10)) for _ in range(r.randint(1, 6))], r.randint(1, 8)),
    brute=_pass_ratio_brute,
    hints=[
        "Adding one passing student to a class raises its ratio by (p + 1)/(t + 1) − p/t.",
        "That gain shrinks each time you add to the same class, so greedy works.",
        "Keep a max-heap keyed by the gain; give each extra student to the class with the largest gain, then push it back with its new gain.",
    ],
    insight="Diminishing gains make the greedy choice (largest marginal gain) optimal.",
    time="O((n + extra) log n)", space="O(n)",
    pitfalls=["Choosing the class with the lowest ratio instead of the largest gain."],
)
def max_average_ratio(classes, extraStudents):
    gain = lambda p, t: (p + 1) / (t + 1) - p / t  # noqa: E731
    heap = [(-gain(p, t), p, t) for p, t in classes]
    heapq.heapify(heap)
    for _ in range(extraStudents):
        _, p, t = heapq.heappop(heap)
        heapq.heappush(heap, (-gain(p + 1, t + 1), p + 1, t + 1))
    return sum(p / t for _, p, t in heap) / len(classes)


def _chair_brute(times, target):
    order = sorted(range(len(times)), key=lambda i: times[i][0])
    taken = {}
    for i in order:
        arrive = times[i][0]
        for f, (chair, leave) in list(taken.items()):
            if leave <= arrive:
                del taken[f]
        used = {c for c, _ in taken.values()}
        chair = next(c for c in range(len(times)) if c not in used)
        if i == target:
            return chair
        taken[i] = (chair, times[i][1])


@problem(
    slug="the-number-of-the-smallest-unoccupied-chair", title="The Number of the Smallest Unoccupied Chair", difficulty="Medium",
    pattern=P, tags=["Array", "Heap", "Two Heaps"],
    sig="smallestChair(self, times: list[list[int]], targetFriend: int) -> int",
    desc="""Chairs are numbered from 0 upward. Friend `i` arrives at `times[i][0]` and leaves at `times[i][1]`; all arrival times are distinct. An arriving friend takes the **lowest-numbered** free chair. A chair freed at time `t` can be taken by someone arriving at `t`.

Return the chair number that `targetFriend` sits on.""",
    constraints=["2 ≤ n ≤ 10⁴", "1 ≤ arrival < leaving ≤ 10⁵", "arrival times are distinct"],
    samples=[([[1, 4], [2, 3], [4, 6]], 1), ([[3, 10], [1, 5], [2, 6]], 0)],
    gen=lambda r: (lambda t: (t, r.randint(0, len(t) - 1)))([[a, a + r.randint(1, 8)] for a in r.distinct(r.randint(2, 10), 1, 30)]),
    brute=_chair_brute,
    hints=[
        "Process friends in order of arrival.",
        "You need the lowest free chair, and you need to know when occupied chairs become free.",
        "Keep a min-heap of free chair numbers and a min-heap of (leave time, chair). Before seating someone, release every chair whose leave time ≤ their arrival.",
    ],
    insight="Free chairs by number and occupied chairs by leave time: two heaps simulate it exactly.",
    time="O(n log n)", space="O(n)",
    pitfalls=["Not freeing a chair when someone arrives exactly at another's leave time."],
)
def smallest_chair(times, targetFriend):
    order = sorted(range(len(times)), key=lambda i: times[i][0])
    free = list(range(len(times)))
    busy = []
    for i in order:
        arrive, leave = times[i]
        while busy and busy[0][0] <= arrive:
            heapq.heappush(free, heapq.heappop(busy)[1])
        chair = heapq.heappop(free)
        if i == targetFriend:
            return chair
        heapq.heappush(busy, (leave, chair))


@problem(
    slug="largest-number-after-digit-swaps-by-parity", title="Largest Number After Digit Swaps by Parity", difficulty="Easy", pattern=H,
    tags=["Sorting", "Heap"],
    sig="largestInteger(self, num: int) -> int",
    desc="""You may swap any two digits of `num` that have the **same parity** (both odd or both even), as many times as you like. Return the largest number you can make.""",
    constraints=["1 ≤ num ≤ 10⁹"],
    samples=[(1234,), (65875,)],
    tests=[(1,), (2,), (247,), (1000000000,)],
    gen=lambda r: (r.randint(1, 10 ** r.randint(1, 9)),),
    hints=[
        "Odd digits can be rearranged among the odd positions, and even digits among the even positions, independently.",
        "Each position keeps its parity, but you can choose which digit of that parity goes there.",
        "Sort the odd digits and the even digits in descending order (or use two max-heaps), then fill each position with the largest remaining digit of its parity.",
    ],
    insight="Parity classes are independent: sort each class and put them back into their slots.",
    time="O(d log d) for d digits", space="O(d)",
    pitfalls=["Mixing odd and even digits."],
)
def largest_integer(num):
    digits = [int(c) for c in str(num)]
    odd = sorted((d for d in digits if d % 2), reverse=True)
    even = sorted((d for d in digits if d % 2 == 0), reverse=True)
    oi = ei = 0
    out = []
    for d in digits:
        if d % 2:
            out.append(odd[oi])
            oi += 1
        else:
            out.append(even[ei])
            ei += 1
    return int("".join(map(str, out)))


@problem(
    slug="find-right-interval", title="Find Right Interval", difficulty="Medium", pattern=P, tags=["Array", "Binary Search", "Sorting", "Two Heaps"],
    sig="findRightInterval(self, intervals: list[list[int]]) -> list[int]",
    desc="""The **right interval** of interval `i` is the interval `j` with the smallest `start_j` such that `start_j ≥ end_i` (`j` may equal `i`). All start points are distinct.

Return, for each interval, the index of its right interval, or `-1` if there isn't one.""",
    constraints=["1 ≤ len(intervals) ≤ 2 × 10⁴", "-10⁶ ≤ start ≤ end ≤ 10⁶", "starts are distinct"],
    samples=[([[1, 2]],), ([[3, 4], [2, 3], [1, 2]],), ([[1, 4], [2, 3], [3, 4]],)],
    gen=lambda r: ([[s, s + r.randint(0, 8)] for s in r.distinct(r.randint(1, 10), -10, 20)],),
    brute=lambda iv: [min((j for j in range(len(iv)) if iv[j][0] >= iv[i][1]), key=lambda j: iv[j][0], default=-1) for i in range(len(iv))],
    hints=[
        "For each end point, you need the smallest start that is ≥ it.",
        "Sort the starts with their original indices.",
        "Binary search each end among the sorted starts (or process ends and starts in sorted order with two heaps).",
    ],
    insight="Sorted starts turn each query into a lower-bound search.",
    time="O(n log n)", space="O(n)",
    pitfalls=["Requiring start > end instead of start ≥ end.", "Returning positions in the sorted array instead of original indices."],
)
def find_right_interval(intervals):
    from bisect import bisect_left
    starts = sorted((s, i) for i, (s, _) in enumerate(intervals))
    keys = [s for s, _ in starts]
    out = []
    for _, e in intervals:
        k = bisect_left(keys, e)
        out.append(starts[k][1] if k < len(keys) else -1)
    return out


def _target_brute(target):
    # Undo steps one at a time (the largest value is always the last one written).
    if max(target) > 10**5:  # one-step reversal is only practical for small values
        return is_possible(target)
    state = list(target)
    while True:
        if all(x == 1 for x in state):
            return True
        i = max(range(len(state)), key=lambda j: state[j])
        prev = state[i] - (sum(state) - state[i])
        if prev < 1 or prev == state[i]:
            return False
        state[i] = prev


@problem(
    slug="construct-target-array-with-multiple-sums", title="Construct Target Array With Multiple Sums", difficulty="Hard", pattern=H,
    tags=["Array", "Heap", "Math"],
    sig="isPossible(self, target: list[int]) -> bool",
    desc="""Start with an array of `n` ones. One step: let `x` be the sum of the current array, pick any index `i`, and set `arr[i] = x`. Return `True` if you can reach `target` this way.""",
    constraints=["1 ≤ n ≤ 5 × 10⁴", "1 ≤ target[i] ≤ 10⁹"],
    samples=[([9, 3, 5],), ([1, 1, 1, 2],), ([8, 5],)],
    tests=[([1],), ([2],), ([1, 1000000000],), ([5, 50],)],
    gen=lambda r: (r.ints(r.randint(1, 4), 1, 30),),
    brute=_target_brute,
    hints=[
        "Work backwards: the largest element must be the one written last.",
        "If the largest is m and the rest sum to r, the previous value at that position was m − r.",
        "Use a max-heap and reverse steps. Replace m − r repeated subtraction with m mod r to stay fast, and fail when the previous value would drop below 1.",
    ],
    insight="Undoing the last step is forced (the max), so a max-heap with modulo arithmetic decides it quickly.",
    time="O(n log n · log max)", space="O(n)",
    pitfalls=["Subtracting one step at a time, which times out for [1, 10⁹].", "The special case where the rest sums to 1."],
)
def is_possible(target):
    total = sum(target)
    heap = [-x for x in target]
    heapq.heapify(heap)
    while True:
        m = -heapq.heappop(heap)
        rest = total - m
        if m == 1 or rest == 1:
            return True
        if rest == 0 or m < rest or m % rest == 0:
            return False
        m %= rest
        total = rest + m
        heapq.heappush(heap, -m)


def _events_brute(events):
    from functools import lru_cache
    days = sorted({d for s, e in events for d in range(s, e + 1)})
    n = len(events)
    best = 0

    def dfs(i, used, count):
        nonlocal best
        best = max(best, count)
        if i == n:
            return
        dfs(i + 1, used, count)
        s, e = events[i]
        for d in range(s, e + 1):
            if d not in used:
                dfs(i + 1, used | {d}, count + 1)

    dfs(0, frozenset(), 0)
    return best


@problem(
    slug="maximum-number-of-events-that-can-be-attended", title="Maximum Number of Events That Can Be Attended", difficulty="Medium",
    pattern=H, tags=["Array", "Greedy", "Heap", "Sorting"],
    sig="maxEvents(self, events: list[list[int]]) -> int",
    desc="""Event `i` runs from day `start` to day `end` inclusive, and you can attend it on any **one** of those days. You can attend at most one event per day. Return the maximum number of events you can attend.""",
    constraints=["1 ≤ len(events) ≤ 10⁵", "1 ≤ start ≤ end ≤ 10⁵"],
    samples=[([[1, 2], [2, 3], [3, 4]],), ([[1, 2], [2, 3], [3, 4], [1, 2]],)],
    tests=[([[1, 1], [1, 1]],), ([[1, 5], [1, 5], [1, 5], [2, 3], [2, 3]],)],
    gen=lambda r: ([(lambda s: [s, s + r.randint(0, 2)])(r.randint(1, 6)) for _ in range(r.randint(1, 6))],),
    brute=_events_brute,
    hints=[
        "On each day, which available event should you attend?",
        "The one that ends soonest: events that last longer can still be attended later.",
        "Sweep days in order. Push the end days of events starting today into a min-heap, drop ended events from the heap, then attend the event with the earliest end (pop one).",
    ],
    insight="Earliest-deadline-first, driven by a min-heap of end days.",
    time="O(n log n + D) for D days", space="O(n)",
    pitfalls=["Attending events in order of start day, which wastes short events."],
)
def max_events(events):
    events = sorted(events)
    heap, i, day, count = [], 0, 0, 0
    n = len(events)
    while i < n or heap:
        if not heap:
            day = max(day, events[i][0])
        while i < n and events[i][0] <= day:
            heapq.heappush(heap, events[i][1])
            i += 1
        while heap and heap[0] < day:
            heapq.heappop(heap)
        if heap:
            heapq.heappop(heap)
            count += 1
        day += 1
    return count


def _building_brute(heights, bricks, ladders):
    from functools import lru_cache

    @lru_cache(None)
    def go(i, b, l):
        if i == len(heights) - 1:
            return i
        climb = heights[i + 1] - heights[i]
        if climb <= 0:
            return go(i + 1, b, l)
        best = i
        if b >= climb:
            best = max(best, go(i + 1, b - climb, l))
        if l:
            best = max(best, go(i + 1, b, l - 1))
        return best

    return go(0, bricks, ladders)


@problem(
    slug="furthest-building-you-can-reach", title="Furthest Building You Can Reach", difficulty="Medium", pattern=H,
    tags=["Array", "Greedy", "Heap"],
    sig="furthestBuilding(self, heights: list[int], bricks: int, ladders: int) -> int",
    desc="""You walk from building `0` toward the right. Moving to a building that is not taller is free. Climbing up by `d` needs either `d` bricks or one ladder.

Using your `bricks` and `ladders` optimally, return the index of the furthest building you can reach.""",
    constraints=["1 ≤ len(heights) ≤ 10⁵", "1 ≤ heights[i] ≤ 10⁶", "0 ≤ bricks ≤ 10⁹", "0 ≤ ladders ≤ len(heights)"],
    samples=[([4, 2, 7, 6, 9, 14, 12], 5, 1), ([4, 12, 2, 7, 3, 18, 20, 3, 19], 10, 2), ([14, 3, 19, 3], 17, 0)],
    gen=lambda r: (r.ints(r.randint(1, 12), 1, 20), r.randint(0, 15), r.randint(0, 3)),
    brute=_building_brute,
    hints=[
        "Ladders are most valuable on the biggest climbs.",
        "Tentatively use a ladder on every climb, keeping the climbs that use ladders in a min-heap.",
        "When you have more climbs than ladders, take the smallest laddered climb off the heap and pay for it with bricks. Stop when bricks run out.",
    ],
    insight="A min-heap of the climbs covered by ladders lets you swap the smallest one to bricks.",
    time="O(n log L)", space="O(L)",
    pitfalls=["Using ladders on the first climbs greedily."],
)
def furthest_building(heights, bricks, ladders):
    heap = []
    for i in range(len(heights) - 1):
        climb = heights[i + 1] - heights[i]
        if climb <= 0:
            continue
        heapq.heappush(heap, climb)
        if len(heap) > ladders:
            bricks -= heapq.heappop(heap)
            if bricks < 0:
                return i
    return len(heights) - 1


def _trap2_brute(heightMap):
    m, n = len(heightMap), len(heightMap[0])
    INF = float("inf")
    level = [[INF] * n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            if i in (0, m - 1) or j in (0, n - 1):
                level[i][j] = heightMap[i][j]
    changed = True
    while changed:
        changed = False
        for i in range(1, m - 1):
            for j in range(1, n - 1):
                best = min(level[i - 1][j], level[i + 1][j], level[i][j - 1], level[i][j + 1])
                v = max(heightMap[i][j], best)
                if v < level[i][j]:
                    level[i][j] = v
                    changed = True
    return sum(level[i][j] - heightMap[i][j] for i in range(m) for j in range(n))


@problem(
    slug="trapping-rain-water-ii", title="Trapping Rain Water II", difficulty="Hard", pattern=H,
    tags=["Array", "Breadth-First Search", "Heap", "Matrix"],
    sig="trapRainWater(self, heightMap: list[list[int]]) -> int",
    desc="""`heightMap` gives the height of each cell of an elevation map. After raining, how much water is trapped in total? Water flows off the edges of the map.""",
    constraints=["1 ≤ m, n ≤ 200", "0 ≤ heightMap[i][j] ≤ 2 × 10⁴"],
    samples=[([[1, 4, 3, 1, 3, 2], [3, 2, 1, 3, 2, 4], [2, 3, 3, 2, 3, 1]],), ([[3, 3, 3, 3, 3], [3, 2, 2, 2, 3], [3, 2, 1, 2, 3], [3, 2, 2, 2, 3], [3, 3, 3, 3, 3]],)],
    tests=[([[5]],), ([[1, 2], [3, 4]],)],
    gen=lambda r: (r.grid(r.randint(1, 6), r.randint(1, 6), range(0, 8)),),
    brute=_trap2_brute,
    hints=[
        "Water in a cell is limited by the lowest wall on the path from that cell to the border.",
        "Process cells from the border inward, always continuing from the lowest boundary cell.",
        "Use a min-heap of boundary cells (height = max of its own height and the water level reaching it). Pop the lowest, and for each unvisited neighbor add max(0, level − height) water and push it with level max(level, height).",
    ],
    insight="A min-heap flood from the border (like Dijkstra) finds each cell's water level.",
    time="O(m·n log(m·n))", space="O(m·n)",
    pitfalls=["Using the 1-D two-pointer idea per row, which ignores water escaping sideways."],
)
def trap_rain_water_ii(heightMap):
    m, n = len(heightMap), len(heightMap[0])
    seen = [[False] * n for _ in range(m)]
    heap = []
    for i in range(m):
        for j in range(n):
            if i in (0, m - 1) or j in (0, n - 1):
                heapq.heappush(heap, (heightMap[i][j], i, j))
                seen[i][j] = True
    water = 0
    while heap:
        level, i, j = heapq.heappop(heap)
        for x, y in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
            if 0 <= x < m and 0 <= y < n and not seen[x][y]:
                seen[x][y] = True
                water += max(0, level - heightMap[x][y])
                heapq.heappush(heap, (max(level, heightMap[x][y]), x, y))
    return water


def _stone_brute(stones):
    stones = list(stones)
    while len(stones) > 1:
        stones.sort()
        y, x = stones.pop(), stones.pop()
        if y != x:
            stones.append(y - x)
    return stones[0] if stones else 0


@problem(
    slug="last-stone-weight", title="Last Stone Weight", difficulty="Easy", pattern=H, tags=["Array", "Heap"],
    sig="lastStoneWeight(self, stones: list[int]) -> int",
    desc="""Each turn, smash the two heaviest stones `y ≥ x` together: if `x == y` both are destroyed, otherwise a stone of weight `y − x` remains. When at most one stone is left, return its weight (or `0` if none).""",
    constraints=["1 ≤ len(stones) ≤ 30", "1 ≤ stones[i] ≤ 1000"],
    samples=[([2, 7, 4, 1, 8, 1],), ([1],)],
    tests=[([2, 2],), ([3, 7, 2],)],
    gen=lambda r: (r.ints(r.randint(1, 15), 1, 20),),
    brute=_stone_brute,
    hints=[
        "You repeatedly need the two largest stones.",
        "A max-heap gives the largest element quickly (in Python, store negative weights in heapq).",
        "Pop two, push their difference back if it's non-zero, and repeat until at most one stone remains.",
    ],
    insight="A max-heap simulates the process in O(n log n).",
    time="O(n log n)", space="O(n)",
    pitfalls=["Sorting once at the start and forgetting the new stone's position."],
)
def last_stone_weight(stones):
    heap = [-s for s in stones]
    heapq.heapify(heap)
    while len(heap) > 1:
        y, x = -heapq.heappop(heap), -heapq.heappop(heap)
        if y != x:
            heapq.heappush(heap, -(y - x))
    return -heap[0] if heap else 0


def _big_median_ops(r):
    # Mostly queries: a solution that re-sorts on every findMedian does thousands of full sorts.
    ops, args = ["MedianFinder"], [[]]
    for i in range(7000):
        if i % 4 == 0:
            ops.append("addNum"); args.append([r.randint(-100000, 100000)])
        else:
            ops.append("findMedian"); args.append([])
    return ops, args


def _meetings(r, n, rooms):
    starts = r.distinct(n, 0, 400000)
    return rooms, [[s, s + r.randint(1, 5000)] for s in starts]


EXTRA = {
    "find-median-from-data-stream": {
        "edge": [(["MedianFinder", "addNum", "findMedian"], [[], [-100000], []]),
                 (["MedianFinder", "addNum", "addNum", "findMedian"], [[], [1], [1], []]),
                 (["MedianFinder", "addNum", "addNum", "addNum", "findMedian"], [[], [3], [2], [1], []])],
        "large": [_big_median_ops],
    },
    "sliding-window-median": {
        "edge": [([1], 1), ([1, 2], 2), ([2147483647, 2147483647], 2), ([-2147483648, -2147483648, 2147483647], 2), ([5, 5, 5, 5], 3)],
        "large": [lambda r: (r.ints(8000, -10**6, 10**6), 3000), lambda r: (r.ints(8000, -100, 100), 2)],
    },
    "meeting-rooms-iii": {
        "edge": [(1, [[0, 1]]), (1, [[0, 10], [1, 2]]), (3, [[1, 20], [2, 10], [3, 5], [4, 9], [6, 8]]), (2, [[0, 10], [1, 2], [12, 14], [13, 15]])],
        "large": [lambda r: _meetings(r, 8000, 100), lambda r: _meetings(r, 8000, 3)],
    },
    "minimum-cost-to-connect-sticks": {
        "edge": [([5],), ([1, 8, 3, 5],), ([10000, 10000],), ([1, 1, 1, 1],)],
        "large": [lambda r: (r.ints(10000, 1, 10000),)],
    },
    "maximum-average-pass-ratio": {
        "edge": [([[1, 1]], 1), ([[1, 2]], 100000), ([[2, 4], [3, 9], [4, 5], [2, 10]], 4)],
        "large": [lambda r: ([sorted([r.randint(1, 100000), r.randint(1, 100000)]) for _ in range(6000)], 6000)],
    },
    "the-number-of-the-smallest-unoccupied-chair": {
        "edge": [([[1, 2], [3, 4]], 1), ([[3, 10], [1, 5], [2, 6]], 0), ([[1, 100000], [2, 3]], 1)],
        "large": [lambda r: (lambda arr: ([[a, a + r.randint(1, 30000)] for a in arr], r.randint(0, len(arr) - 1)))(r.distinct(8000, 1, 60000))],
    },
    "largest-number-after-digit-swaps-by-parity": {"edge": [(1,), (10,), (1000000000,), (65875,), (247,)]},
    "find-right-interval": {
        "edge": [([[1, 2]],), ([[3, 4], [2, 3], [1, 2]],), ([[1, 4], [2, 3], [3, 4]],), ([[1, 1]],), ([[-1000000, 1000000], [1000000, 1000000]],)],
        "large": [lambda r: ([[s, s + r.randint(0, 20000)] for s in r.distinct(6500, -10**6, 10**6)],)],
    },
    "construct-target-array-with-multiple-sums": {
        "edge": [([1],), ([2],), ([1, 1, 1, 2],), ([8, 5],), ([1, 1000000000],), ([5, 2],)],
        "edge_nb": [([1000000000, 1],), ([2, 900000001],)],
        "large": [lambda r: (r.ints(12000, 1, 10**9),), lambda r: ([1] * 29999 + [30000],)],
    },
    "maximum-number-of-events-that-can-be-attended": {
        "edge": [([[1, 1]],), ([[1, 2], [1, 2], [1, 2]],), ([[1, 100000]],), ([[1, 4], [4, 4], [2, 2], [3, 4], [1, 1]],)],
        "large": [lambda r: ([[a, min(100000, a + r.randint(0, 50))] for a in r.ints(8000, 1, 100000)],), lambda r: ([[1, 100000]] * 8000,)],
    },
    "furthest-building-you-can-reach": {
        "edge": [([1], 0, 0), ([1, 2], 0, 0), ([1, 2], 1, 0), ([5, 1], 0, 0), ([1, 5, 1, 2, 3, 4, 10000], 4, 1), ([14, 3, 19, 3], 17, 0)],
        "large": [lambda r: (r.ints(15000, 1, 10**6), 10**8, 500), lambda r: (r.ints(15000, 1, 100), 0, 7000)],
    },
    "trapping-rain-water-ii": {
        "edge": [([[1]],), ([[1, 2, 3]],), ([[3, 3, 3], [3, 0, 3], [3, 3, 3]],), ([[5, 5, 5, 5], [5, 1, 1, 5], [5, 5, 5, 5]],)],
        "large": [lambda r: ([r.ints(100, 0, 20000) for _ in range(100)],)],
    },
    "last-stone-weight": {"edge": [([1],), ([2, 2],), ([1000, 1],), ([3, 7, 2],)]},
}
