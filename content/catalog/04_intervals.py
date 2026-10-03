import heapq
from collections import Counter

from catalog_lib import problem

P = "intervals"


def _intervals(r, n, lo=0, hi=30, maxlen=8):
    out = []
    for _ in range(n):
        s = r.randint(lo, hi)
        out.append([s, s + r.randint(0, maxlen)])
    return out


def _disjoint_sorted(r, n, lo=0, step=6):
    out, cur = [], lo
    for _ in range(n):
        s = cur + r.randint(0, step)
        e = s + r.randint(0, step)
        out.append([s, e])
        cur = e + 1
    return out


def _merge(intervals):
    out = []
    for s, e in sorted(intervals):
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out


@problem(
    slug="insert-interval", title="Insert Interval", difficulty="Medium", pattern=P, tags=["Array", "Intervals"],
    sig="insert(self, intervals: list[list[int]], newInterval: list[int]) -> list[list[int]]",
    desc="""`intervals` is a list of non-overlapping intervals `[start, end]`, sorted by start. Insert `newInterval`, merging any intervals it overlaps (touching counts as overlapping), and return the result, still sorted and non-overlapping.""",
    constraints=["0 ≤ len(intervals) ≤ 10⁴", "0 ≤ start ≤ end ≤ 10⁵", "intervals is sorted and non-overlapping"],
    samples=[([[1, 3], [6, 9]], [2, 5]), ([[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8])],
    tests=[([], [5, 7]), ([[1, 5]], [6, 8]), ([[1, 5]], [0, 0]), ([[3, 5]], [1, 9])],
    gen=lambda r: (_disjoint_sorted(r, r.randint(0, 6)), (lambda s: [s, s + r.randint(0, 10)])(r.randint(0, 40))),
    brute=lambda intervals, new: _merge(intervals + [new]),
    hints=[
        "Intervals that end before the new one starts are untouched; so are intervals that start after it ends.",
        "Everything in between overlaps the new interval and must be merged into it.",
        "Copy intervals ending before newInterval starts, then absorb every overlapping interval by widening newInterval, add it, then copy the rest.",
    ],
    insight="Three phases over the sorted list: before, overlapping, after. One pass, no re-sorting.",
    time="O(n)", space="O(n) for the output",
    pitfalls=["Treating touching intervals like [1,5] and [5,7] as separate."],
)
def insert_interval(intervals, newInterval):
    out, i, n = [], 0, len(intervals)
    s, e = newInterval
    while i < n and intervals[i][1] < s:
        out.append(intervals[i])
        i += 1
    while i < n and intervals[i][0] <= e:
        s, e = min(s, intervals[i][0]), max(e, intervals[i][1])
        i += 1
    out.append([s, e])
    out.extend(intervals[i:])
    return out


def _rooms_brute(intervals):
    points = set(x for iv in intervals for x in iv)
    return max((sum(s <= t < e for s, e in intervals) for t in points), default=0)


@problem(
    slug="meeting-rooms-ii", title="Meeting Rooms II", difficulty="Medium", pattern=P, tags=["Array", "Intervals", "Heap", "Sorting"],
    sig="minMeetingRooms(self, intervals: list[list[int]]) -> int",
    desc="""Each meeting is `[start, end)`: it occupies a room from `start` up to, but not including, `end`. Return the minimum number of rooms needed so no two overlapping meetings share a room.""",
    constraints=["1 ≤ len(intervals) ≤ 10⁴", "0 ≤ start < end ≤ 10⁶"],
    samples=[([[0, 30], [5, 10], [15, 20]],), ([[7, 10], [2, 4]],)],
    tests=[([[1, 5], [5, 10]],), ([[1, 10], [2, 9], [3, 8]],)],
    gen=lambda r: ([[s, s + r.randint(1, 8)] for s in r.ints(r.randint(1, 12), 0, 30)],),
    brute=_rooms_brute,
    hints=[
        "The answer is the maximum number of meetings happening at the same moment.",
        "Process meetings by start time and keep track of when rooms become free.",
        "Keep a min-heap of end times. For each meeting, if the earliest end is ≤ its start, reuse that room (pop); push its end. The heap's largest size is the answer.",
    ],
    insight="A min-heap of end times always knows which room frees up first.",
    time="O(n log n)", space="O(n)",
    pitfalls=["Treating a meeting that starts exactly when another ends as overlapping."],
)
def min_meeting_rooms(intervals):
    heap = []
    for s, e in sorted(intervals):
        if heap and heap[0] <= s:
            heapq.heapreplace(heap, e)
        else:
            heapq.heappush(heap, e)
    return len(heap)


@problem(
    slug="interval-list-intersections", title="Interval List Intersections", difficulty="Medium", pattern=P,
    tags=["Array", "Two Pointers", "Intervals"],
    sig="intervalIntersection(self, firstList: list[list[int]], secondList: list[list[int]]) -> list[list[int]]",
    desc="""Each list contains closed, pairwise disjoint intervals sorted by start. Return the intersections of the two lists: every non-empty overlap between an interval of the first list and one of the second, in sorted order.""",
    constraints=["0 ≤ len(firstList), len(secondList) ≤ 1000", "0 ≤ start ≤ end ≤ 10⁹"],
    samples=[([[0, 2], [5, 10], [13, 23], [24, 25]], [[1, 5], [8, 12], [15, 24], [25, 26]]), ([[1, 3], [5, 9]], [])],
    tests=[([[1, 7]], [[3, 10]]), ([[3, 5]], [[5, 6]])],
    gen=lambda r: (_disjoint_sorted(r, r.randint(0, 6)), _disjoint_sorted(r, r.randint(0, 6))),
    brute=lambda a, b: sorted([max(x[0], y[0]), min(x[1], y[1])] for x in a for y in b if max(x[0], y[0]) <= min(x[1], y[1])),
    hints=[
        "Two closed intervals overlap when the larger start is ≤ the smaller end.",
        "Walk both lists with one pointer each.",
        "Record the overlap of the current pair if it exists, then advance the pointer whose interval ends first (it can't overlap anything else).",
    ],
    insight="Two pointers over sorted disjoint lists; the interval that ends first is finished.",
    time="O(n + m)", space="O(1) besides the output",
    pitfalls=["Advancing both pointers every time, which skips overlaps."],
)
def interval_intersection(firstList, secondList):
    i = j = 0
    out = []
    while i < len(firstList) and j < len(secondList):
        lo = max(firstList[i][0], secondList[j][0])
        hi = min(firstList[i][1], secondList[j][1])
        if lo <= hi:
            out.append([lo, hi])
        if firstList[i][1] < secondList[j][1]:
            i += 1
        else:
            j += 1
    return out


def _free_brute(schedule):
    busy = _merge([iv for person in schedule for iv in person])
    return [[busy[i][1], busy[i + 1][0]] for i in range(len(busy) - 1) if busy[i][1] < busy[i + 1][0]]


@problem(
    slug="employee-free-time", title="Employee Free Time", difficulty="Hard", pattern=P, tags=["Array", "Intervals", "Heap", "Sorting"],
    sig="employeeFreeTime(self, schedule: list[list[list[int]]]) -> list[list[int]]",
    desc="""`schedule[i]` lists employee `i`'s working intervals `[start, end]`, sorted and non-overlapping. Return the finite intervals of time when **every** employee is free, sorted. Free intervals have positive length (`start < end`).""",
    constraints=["1 ≤ len(schedule), len(schedule[i]) ≤ 50", "0 ≤ start < end ≤ 10⁸"],
    samples=[([[[1, 2], [5, 6]], [[1, 3]], [[4, 10]]],), ([[[1, 3], [6, 7]], [[2, 4]], [[2, 5], [9, 12]]],)],
    tests=[([[[1, 2]]],), ([[[1, 2], [3, 4]], [[2, 3]]],)],
    gen=lambda r: ([[iv for iv in _disjoint_sorted(r, r.randint(1, 4), 0, 5) if iv[0] < iv[1]] or [[0, 1]] for _ in range(r.randint(1, 4))],),
    brute=_free_brute,
    hints=[
        "Combine everyone's intervals: you need the gaps in the union of all working time.",
        "Sort all intervals by start (or merge the sorted lists with a heap).",
        "Sweep while tracking the furthest end seen so far; whenever the next interval starts after it, that gap is a free interval.",
    ],
    insight="Free time for everyone = gaps between the merged working intervals.",
    time="O(N log N) for N intervals", space="O(N)",
    pitfalls=["Reporting zero-length gaps where one interval ends exactly when the next begins."],
)
def employee_free_time(schedule):
    events = sorted(iv for person in schedule for iv in person)
    out, end = [], events[0][1]
    for s, e in events[1:]:
        if s > end:
            out.append([end, s])
        end = max(end, e)
    return out


def _task_brute(tasks, n):
    counts = Counter(tasks)
    time, cooldown = 0, {}
    remaining = dict(counts)
    while any(remaining.values()):
        ready = [t for t, c in remaining.items() if c and cooldown.get(t, 0) <= time]
        if ready:
            t = max(ready, key=lambda x: (remaining[x], x))
            remaining[t] -= 1
            cooldown[t] = time + n + 1
        time += 1
    return time


@problem(
    slug="task-scheduler", title="Task Scheduler", difficulty="Medium", pattern=P, tags=["Array", "Greedy", "Heap", "Counting"],
    sig="leastInterval(self, tasks: list[str], n: int) -> int",
    desc="""Each task is a letter and takes one time unit. The CPU runs one task (or idles) per unit. Two runs of the **same** task must be separated by at least `n` units.

Return the minimum number of units needed to finish all tasks, in any order.""",
    constraints=["1 ≤ len(tasks) ≤ 10⁴", "tasks[i] is an uppercase letter", "0 ≤ n ≤ 100"],
    samples=[(["A", "A", "A", "B", "B", "B"], 2), (["A", "C", "A", "B", "D", "B"], 1), (["A", "A", "A", "B", "B", "B"], 3)],
    gen=lambda r: ([r.choice("ABCD") for _ in range(r.randint(1, 15))], r.randint(0, 4)),
    brute=_task_brute,
    hints=[
        "The most frequent task decides the skeleton: it needs gaps of n between its runs.",
        "If the top frequency is f, there are f − 1 full blocks of length n + 1, plus a final block containing every task with frequency f.",
        "Answer = max(len(tasks), (f − 1) · (n + 1) + number of tasks with frequency f).",
    ],
    insight="Idle time only exists if the most frequent tasks can't be interleaved with others; otherwise the answer is just the number of tasks.",
    time="O(n)", space="O(1) for 26 letters",
    pitfalls=["Forgetting the max with len(tasks) when there are many distinct tasks."],
)
def least_interval(tasks, n):
    counts = Counter(tasks).values()
    f = max(counts)
    ties = sum(c == f for c in counts)
    return max(len(tasks), (f - 1) * (n + 1) + ties)


@problem(
    slug="remove-covered-intervals", title="Remove Covered Intervals", difficulty="Medium", pattern=P, tags=["Array", "Sorting", "Intervals"],
    sig="removeCoveredIntervals(self, intervals: list[list[int]]) -> int",
    desc="""An interval `[a, b)` is **covered** by `[c, d)` if `c ≤ a` and `b ≤ d`. Remove every interval covered by another one, and return how many remain. All intervals are distinct.""",
    constraints=["1 ≤ len(intervals) ≤ 1000", "0 ≤ start < end ≤ 10⁵", "all intervals are unique"],
    samples=[([[1, 4], [3, 6], [2, 8]],), ([[1, 4], [2, 3]],)],
    tests=[([[1, 2]],), ([[1, 2], [1, 4], [3, 4]],)],
    gen=lambda r: ([list(t) for t in {(s, s + r.randint(1, 8)) for s in r.ints(r.randint(1, 12), 0, 20)}],),
    brute=lambda iv: sum(not any(j != i and iv[j][0] <= iv[i][0] and iv[i][1] <= iv[j][1] for j in range(len(iv))) for i in range(len(iv))),
    hints=[
        "Sort so that a covering interval comes before the intervals it covers.",
        "Sort by start ascending, and by end descending when starts are equal.",
        "Scan while tracking the largest end so far: an interval whose end is ≤ that maximum is covered; otherwise it survives and updates the maximum.",
    ],
    insight="With the right sort order, an interval is covered exactly when an earlier interval reaches at least as far.",
    time="O(n log n)", space="O(1) besides sorting",
    pitfalls=["Sorting equal starts by ascending end, which misses [1,4] covering [1,2]."],
)
def remove_covered(intervals):
    count, reach = 0, -1
    for s, e in sorted(intervals, key=lambda x: (x[0], -x[1])):
        if e > reach:
            count += 1
            reach = e
    return count


@problem(
    slug="count-days-without-meetings", title="Count Days Without Meetings", difficulty="Medium", pattern=P, tags=["Array", "Sorting", "Intervals"],
    sig="countDays(self, days: int, meetings: list[list[int]]) -> int",
    desc="""An employee is available on days `1` to `days`. Each meeting `[start, end]` covers days `start` through `end` inclusive, and meetings may overlap.

Return the number of available days with no meeting.""",
    constraints=["1 ≤ days ≤ 10⁹", "1 ≤ len(meetings) ≤ 10⁵", "1 ≤ start ≤ end ≤ days"],
    samples=[(10, [[5, 7], [1, 3], [9, 10]]), (5, [[2, 4], [1, 3]]), (6, [[1, 6]])],
    gen=lambda r: (lambda d: (d, [(lambda s: [s, r.randint(s, d)])(r.randint(1, d)) for _ in range(r.randint(1, 6))]))(r.randint(1, 30)),
    brute=lambda days, meetings: sum(not any(s <= d <= e for s, e in meetings) for d in range(1, days + 1)),
    hints=[
        "Busy days are the union of all the meeting intervals.",
        "Merge the intervals after sorting by start.",
        "Subtract the total length of the merged intervals from days (or add up the gaps between them).",
    ],
    insight="Merging overlapping meetings gives the busy days in O(n log n) without touching each day.",
    time="O(n log n)", space="O(1) besides sorting",
    pitfalls=["Iterating over every day when days can be 10⁹."],
)
def count_days(days, meetings):
    busy = sum(e - s + 1 for s, e in _merge(meetings))
    return days - busy


@problem(
    slug="car-pooling", title="Car Pooling", difficulty="Medium", pattern=P, tags=["Array", "Prefix Sum", "Sorting", "Intervals"],
    sig="carPooling(self, trips: list[list[int]], capacity: int) -> bool",
    desc="""A car drives east only and has `capacity` seats. Each trip `[numPassengers, from, to]` picks up passengers at kilometre `from` and drops them at `to`.

Return `True` if every trip can be completed without ever exceeding the capacity.""",
    constraints=["1 ≤ len(trips) ≤ 1000", "1 ≤ numPassengers ≤ 100", "0 ≤ from < to ≤ 1000", "1 ≤ capacity ≤ 10⁵"],
    samples=[([[2, 1, 5], [3, 3, 7]], 4), ([[2, 1, 5], [3, 3, 7]], 5)],
    tests=[([[2, 1, 5], [3, 5, 7]], 3), ([[9, 0, 1]], 8)],
    gen=lambda r: ([[r.randint(1, 5), f, f + r.randint(1, 6)] for f in r.ints(r.randint(1, 8), 0, 15)], r.randint(1, 12)),
    brute=lambda trips, cap: all(sum(p for p, f, t in trips if f <= x < t) <= cap for x in range(0, 1001)),
    hints=[
        "Only the moments when passengers get on or off change the load.",
        "Record +passengers at each pickup point and −passengers at each drop-off point.",
        "Sweep the points in order (drop-offs before pickups at the same km), keeping a running load; fail if it ever exceeds the capacity.",
    ],
    insight="A difference array (or sorted events) turns overlapping trips into a running total.",
    time="O(n log n) or O(n + max km)", space="O(n)",
    pitfalls=["Counting passengers still on board at their drop-off point."],
)
def car_pooling(trips, capacity):
    events = []
    for p, f, t in trips:
        events.append((f, p))
        events.append((t, -p))
    load = 0
    for _, delta in sorted(events, key=lambda e: (e[0], e[1])):
        load += delta
        if load > capacity:
            return False
    return True


class _SummaryRangesRef:
    def __init__(self):
        self.vals = set()

    def addNum(self, value):
        self.vals.add(value)

    def getIntervals(self):
        out = []
        for v in sorted(self.vals):
            if out and v == out[-1][1] + 1:
                out[-1][1] = v
            else:
                out.append([v, v])
        return out


def _summary_ops(r):
    ops, args = ["SummaryRanges"], [[]]
    for _ in range(r.randint(3, 15)):
        if r.random() < 0.65:
            ops.append("addNum")
            args.append([r.randint(0, 20)])
        else:
            ops.append("getIntervals")
            args.append([])
    ops.append("getIntervals")
    args.append([])
    return ops, args


@problem(
    slug="data-stream-as-disjoint-intervals", title="Data Stream as Disjoint Intervals", difficulty="Hard", pattern=P,
    tags=["Design", "Intervals", "Binary Search", "Ordered Set"],
    design=True, cls="SummaryRanges",
    starter="""class SummaryRanges:
    def __init__(self):
        pass

    def addNum(self, value: int) -> None:
        pass

    def getIntervals(self) -> list[list[int]]:
        pass
""",
    desc="""Numbers arrive one at a time. Design `SummaryRanges`:

- `SummaryRanges()` starts with no numbers.
- `addNum(value)` adds a number to the stream (it may repeat).
- `getIntervals()` returns the numbers seen so far as a sorted list of disjoint intervals `[start, end]` covering consecutive values.

Tests call your class with a list of operations and their arguments; the expected output lists each call's return value (`None` for the constructor and `addNum`).""",
    constraints=["0 ≤ value ≤ 10⁴", "at most 3 × 10⁴ calls"],
    samples=[(["SummaryRanges", "addNum", "getIntervals", "addNum", "getIntervals", "addNum", "getIntervals", "addNum", "getIntervals"], [[], [1], [], [3], [], [7], [], [2], []]),
             (["SummaryRanges", "addNum", "addNum", "getIntervals"], [[], [5], [5], []])],
    gen=_summary_ops,
    hints=[
        "Each new number either starts a new interval, extends a neighbor, or joins two intervals into one.",
        "Keep the intervals sorted by start so you can find the neighbors of a value quickly.",
        "On addNum, find the interval just before and just after the value (binary search or an ordered map), then merge as needed. getIntervals returns the stored list.",
    ],
    insight="Maintaining merged intervals on insert keeps getIntervals cheap.",
    time="O(log n) per add with an ordered structure (O(n) with a plain list)", space="O(n)",
    pitfalls=["Adding a value already inside an interval twice.", "Not merging when a value fills the gap between two intervals."],
)
class SummaryRanges(_SummaryRangesRef):
    pass


@problem(
    slug="minimum-interval-to-include-each-query", title="Minimum Interval to Include Each Query", difficulty="Hard", pattern=P,
    tags=["Array", "Binary Search", "Heap", "Sorting", "Intervals"],
    sig="minInterval(self, intervals: list[list[int]], queries: list[int]) -> list[int]",
    desc="""Each interval `[left, right]` has size `right − left + 1`. For every query `q`, find the **smallest-size** interval that contains `q` (`left ≤ q ≤ right`), and report its size, or `-1` if none contains it.

Return the answers in the same order as `queries`.""",
    constraints=["1 ≤ len(intervals), len(queries) ≤ 10⁵", "1 ≤ left ≤ right ≤ 10⁷", "1 ≤ queries[j] ≤ 10⁷"],
    samples=[([[1, 4], [2, 4], [3, 6], [4, 4]], [2, 3, 4, 5]), ([[2, 3], [2, 5], [1, 8], [20, 25]], [2, 19, 5, 22])],
    gen=lambda r: (_intervals(r, r.randint(1, 8), 1, 20), r.ints(r.randint(1, 8), 1, 30)),
    brute=lambda iv, qs: [min((e - s + 1 for s, e in iv if s <= q <= e), default=-1) for q in qs],
    hints=[
        "Answer the queries in sorted order so intervals can be added once and removed once.",
        "Sort intervals by left. For each query (in increasing order), push every interval whose left ≤ query into a min-heap keyed by size.",
        "Pop heap entries whose right < query (they can't contain this or any later query); the heap's top is the answer. Write it back at the query's original position.",
    ],
    insight="Offline processing with sorted queries and a min-heap of sizes answers everything in O((n + q) log n).",
    time="O((n + q) log n)", space="O(n + q)",
    pitfalls=["Losing the original order of the queries after sorting them."],
)
def min_interval(intervals, queries):
    intervals = sorted(intervals)
    out = [-1] * len(queries)
    heap, i = [], 0
    for q, idx in sorted((q, i) for i, q in enumerate(queries)):
        while i < len(intervals) and intervals[i][0] <= q:
            s, e = intervals[i]
            heapq.heappush(heap, (e - s + 1, e))
            i += 1
        while heap and heap[0][1] < q:
            heapq.heappop(heap)
        if heap:
            out[idx] = heap[0][0]
    return out


@problem(
    slug="non-overlapping-intervals", title="Non-overlapping Intervals", difficulty="Medium", pattern=P,
    tags=["Array", "Greedy", "Sorting", "Intervals"],
    sig="eraseOverlapIntervals(self, intervals: list[list[int]]) -> int",
    desc="""Return the minimum number of intervals to remove so the rest don't overlap. Intervals that only touch, like `[1, 2]` and `[2, 3]`, don't overlap.""",
    constraints=["1 ≤ len(intervals) ≤ 10⁵", "-5 × 10⁴ ≤ start < end ≤ 5 × 10⁴"],
    samples=[([[1, 2], [2, 3], [3, 4], [1, 3]],), ([[1, 2], [1, 2], [1, 2]],), ([[1, 2], [2, 3]],)],
    gen=lambda r: ([[s, s + r.randint(1, 6)] for s in r.ints(r.randint(1, 10), 0, 15)],),
    brute=lambda iv: len(iv) - max(
        sum(1 for _ in [0]) * 0 + len(sub) for mask in range(1 << len(iv))
        for sub in [[iv[i] for i in range(len(iv)) if mask >> i & 1]]
        if all(max(a[0], b[0]) >= min(a[1], b[1]) for x, a in enumerate(sub) for b in sub[x + 1:])
    ),
    hints=[
        "Keeping as many intervals as possible is the same as removing as few as possible.",
        "Which interval should you keep first to leave the most room for the rest?",
        "Sort by end and greedily keep each interval that starts at or after the end of the last kept one. Removed = total − kept.",
    ],
    insight="Picking the interval that ends earliest is the classic greedy for the maximum set of non-overlapping intervals.",
    time="O(n log n)", space="O(1) besides sorting",
    pitfalls=["Sorting by start and keeping the first interval, which can block many shorter ones."],
)
def erase_overlap(intervals):
    kept, end = 0, float("-inf")
    for s, e in sorted(intervals, key=lambda x: x[1]):
        if s >= end:
            kept += 1
            end = e
    return len(intervals) - kept


@problem(
    slug="meeting-rooms", title="Meeting Rooms", difficulty="Easy", pattern=P, tags=["Array", "Sorting", "Intervals"],
    sig="canAttendMeetings(self, intervals: list[list[int]]) -> bool",
    desc="""Each meeting is `[start, end)`. Return `True` if one person could attend all of them, meaning no two meetings overlap. A meeting may start exactly when another ends.""",
    constraints=["0 ≤ len(intervals) ≤ 10⁴", "0 ≤ start < end ≤ 10⁶"],
    samples=[([[0, 30], [5, 10], [15, 20]],), ([[7, 10], [2, 4]],)],
    tests=[([],), ([[1, 5], [5, 10]],)],
    gen=lambda r: ([[s, s + r.randint(1, 5)] for s in r.ints(r.randint(0, 6), 0, 25)],),
    brute=lambda iv: all(max(a[0], b[0]) >= min(a[1], b[1]) for i, a in enumerate(iv) for b in iv[i + 1:]),
    hints=[
        "If you sort meetings by start time, an overlap must involve neighbors.",
        "Sort the meetings by their start times first.",
        "Check that each meeting starts no earlier than the previous one ends.",
    ],
    insight="After sorting, only adjacent meetings need to be compared.",
    time="O(n log n)", space="O(1) besides sorting",
    pitfalls=["Treating back-to-back meetings as overlapping."],
)
def can_attend(intervals):
    iv = sorted(intervals)
    return all(iv[i][0] >= iv[i - 1][1] for i in range(1, len(iv)))


def _disjoint(r, n, hi):
    pts = sorted(r.distinct(2 * n, 0, hi))
    return [[pts[2 * i], pts[2 * i + 1]] for i in range(n)]


def _spans(r, n, lo, hi, max_len):
    out = []
    for _ in range(n):
        a = r.randint(lo, hi - 1)
        out.append([a, min(hi, a + r.randint(1, max_len))])
    return out


def _big_summary_ops(r):
    ops, args = ["SummaryRanges"], [[]]
    for i in range(3000):
        if i % 1000 == 999:
            ops.append("getIntervals"); args.append([])
        else:
            ops.append("addNum"); args.append([r.randint(0, 10000)])
    return ops, args


EXTRA = {
    "insert-interval": {
        "edge": [([], [5, 7]), ([[1, 5]], [2, 3]), ([[1, 5]], [6, 8]), ([[3, 5]], [0, 1]), ([[1, 5]], [0, 10]), ([[1, 2], [4, 5]], [2, 4])],
        "large": [lambda r: (_disjoint(r, 7000, 100000), [30000, 60000])],
    },
    "meeting-rooms-ii": {
        "edge": [([[1, 2]],), ([[1, 5], [5, 10]],), ([[1, 10], [1, 10], [1, 10]],), ([[0, 1000000]],)],
        "large": [lambda r: (_spans(r, 7000, 0, 100000, 500),)],
    },
    "interval-list-intersections": {
        "edge": [([], [[1, 2]]), ([[1, 7]], [[3, 10]]), ([[1, 1]], [[1, 1]]), ([[0, 5]], [[5, 10]])],
        "large": [lambda r: (_disjoint(r, 1000, 10**9), _disjoint(r, 1000, 10**9))],
    },
    "employee-free-time": {
        "edge": [([[[1, 2]]],), ([[[1, 3]], [[2, 4]]],), ([[[1, 2]], [[3, 4]]],), ([[[1, 2], [2, 3]]],)],
        "large": [lambda r: ([_disjoint(r, 50, 10**8) for _ in range(50)],)],
    },
    "task-scheduler": {
        "edge": [(["A"], 0), (["A"], 100), (["A", "A", "A"], 0), (["A", "A", "A", "B", "B", "B"], 0), (["A", "B", "C", "D"], 3)],
        "large": [lambda r: ([r.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(10000)], 50), lambda r: (["A"] * 5000 + ["B"] * 4999, 100)],
    },
    "remove-covered-intervals": {
        "edge": [([[1, 2]],), ([[1, 4], [2, 3]],), ([[1, 2], [1, 4], [3, 4]],), ([[3, 10], [4, 10], [5, 11]],)],
        "large": [lambda r: ([list(p) for p in {tuple(x) for x in _spans(r, 1000, 0, 100000, 20000)}],)],
    },
    "count-days-without-meetings": {
        "edge": [(1, [[1, 1]]), (5, [[2, 4], [1, 3]]), (6, [[1, 6], [2, 3]])],
        "edge_nb": [(10**9, [[1, 10**9]]), (10**9, [[5, 5]])],
        "large": [lambda r: (10**9, [[a, b] for a, b in _spans(r, 6000, 1, 10**9, 10**5)])],
    },
    "car-pooling": {
        "edge": [([[2, 1, 5], [3, 3, 7]], 5), ([[1, 0, 1]], 1), ([[100, 0, 1000]], 99), ([[3, 2, 7], [3, 7, 9], [8, 3, 9]], 11)],
        "large": [lambda r: ([[r.randint(1, 100), a, b] for a, b in _spans(r, 1000, 0, 1000, 300)], 25000)],
    },
    "data-stream-as-disjoint-intervals": {
        "edge": [(["SummaryRanges", "addNum", "addNum", "getIntervals"], [[], [5], [5], []]),
                 (["SummaryRanges", "addNum", "addNum", "addNum", "getIntervals"], [[], [3], [1], [2], []]),
                 (["SummaryRanges", "addNum", "getIntervals"], [[], [0], []])],
        "large": [_big_summary_ops],
    },
    "minimum-interval-to-include-each-query": {
        "edge": [([[1, 1]], [1, 2]), ([[2, 3], [2, 5], [1, 8], [20, 25]], [2, 19, 5, 22])],
        "edge_nb": [([[1, 10000000]], [1, 10000000])],
        "large": [lambda r: (_spans(r, 4000, 1, 10**6, 10**4), r.ints(4000, 1, 10**6))],
    },
    "non-overlapping-intervals": {
        "edge": [([[1, 2]],), ([[1, 2], [1, 2], [1, 2]],), ([[1, 2], [2, 3]],), ([[-50000, 50000], [0, 1]],)],
        "large": [lambda r: (_spans(r, 7000, -50000, 50000, 200),)],
    },
    "meeting-rooms": {
        "edge": [([],), ([[1, 2]],), ([[1, 2], [2, 3]],), ([[1, 5], [4, 6]],)],
        "large": [lambda r: (_disjoint(r, 7000, 100000),)],
    },
}
