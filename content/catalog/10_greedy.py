import heapq
from collections import Counter
from functools import lru_cache
from itertools import combinations

from catalog_lib import problem

P = "greedy"


def _jump_brute(nums):
    reach = [False] * len(nums)
    reach[0] = True
    for i in range(len(nums)):
        if reach[i]:
            for j in range(i + 1, min(len(nums), i + nums[i] + 1)):
                reach[j] = True
    return reach[-1]


@problem(
    slug="jump-game", title="Jump Game", difficulty="Medium", pattern=P, tags=["Array", "Dynamic Programming", "Greedy"],
    sig="canJump(self, nums: list[int]) -> bool",
    desc="""You start at index 0. `nums[i]` is the maximum jump length from index `i`. Return `true` if you can reach the last index.""",
    constraints=["1 ≤ len(nums) ≤ 10⁴", "0 ≤ nums[i] ≤ 10⁵"],
    samples=[([2, 3, 1, 1, 4],), ([3, 2, 1, 0, 4],), ([0],)],
    gen=lambda r: (r.ints(r.randint(1, 10), 0, 3),),
    brute=_jump_brute,
    hints=[
        "You don't need the exact path, only how far you can get.",
        "Track the furthest index reachable so far as you scan left to right.",
        "If you ever stand on an index beyond the furthest reach, you're stuck; otherwise extend the reach with i + nums[i].",
    ],
    insight="A single running maximum of reach decides reachability.",
    time="O(n)", space="O(1)",
    pitfalls=["Trying every jump recursively, which is exponential."],
)
def can_jump(nums):
    reach = 0
    for i, x in enumerate(nums):
        if i > reach:
            return False
        reach = max(reach, i + x)
    return True


def _jump2_brute(nums):
    n = len(nums)
    dist = [0] + [float("inf")] * (n - 1)
    for i in range(n):
        for j in range(i + 1, min(n, i + nums[i] + 1)):
            dist[j] = min(dist[j], dist[i] + 1)
    return dist[-1]


def _jump2_input(r):
    n = r.randint(1, 10)
    return ([r.randint(1, 3) for _ in range(n - 1)] + [r.randint(0, 3)],)


@problem(
    slug="jump-game-ii", title="Jump Game II", difficulty="Medium", pattern=P, tags=["Array", "Dynamic Programming", "Greedy"],
    sig="jump(self, nums: list[int]) -> int",
    desc="""You start at index 0, and `nums[i]` is the maximum jump length from index `i`. Return the minimum number of jumps to reach the last index. The tests guarantee it's reachable.""",
    constraints=["1 ≤ len(nums) ≤ 10⁴", "0 ≤ nums[i] ≤ 1000", "the last index is reachable"],
    samples=[([2, 3, 1, 1, 4],), ([2, 3, 0, 1, 4],), ([0],)],
    gen=_jump2_input,
    brute=_jump2_brute,
    hints=[
        "Think in levels, like BFS: indices reachable with 1 jump, with 2 jumps, and so on.",
        "While scanning the current level, track the furthest index the next level can reach.",
        "When you pass the end of the current level, count a jump and make the furthest reach the new level end.",
    ],
    insight="Greedy BFS by ranges: each jump extends the frontier as far as possible.",
    time="O(n)", space="O(1)",
    pitfalls=["Counting a jump when you're already at the last index."],
)
def jump(nums):
    jumps, end, far = 0, 0, 0
    for i in range(len(nums) - 1):
        far = max(far, i + nums[i])
        if i == end:
            jumps += 1
            end = far
    return jumps


def _boats_brute(people, limit):
    @lru_cache(None)
    def go(rest):
        if not rest:
            return 0
        first, others = rest[0], rest[1:]
        best = 1 + go(others)
        for i, p in enumerate(others):
            if first + p <= limit:
                best = min(best, 1 + go(others[:i] + others[i + 1:]))
        return best
    return go(tuple(sorted(people)))


@problem(
    slug="boats-to-save-people", title="Boats to Save People", difficulty="Medium", pattern=P,
    tags=["Array", "Two Pointers", "Greedy", "Sorting"],
    sig="numRescueBoats(self, people: list[int], limit: int) -> int",
    desc="""`people[i]` is a person's weight. Each boat carries at most two people with total weight at most `limit`. Return the minimum number of boats to carry everyone. Every person weighs at most `limit`.""",
    constraints=["1 ≤ len(people) ≤ 5 × 10⁴", "1 ≤ people[i] ≤ limit ≤ 3 × 10⁴"],
    samples=[([1, 2], 3), ([3, 2, 2, 1], 3), ([3, 5, 3, 4], 5)],
    gen=lambda r: (lambda limit: (r.ints(r.randint(1, 8), 1, limit), limit))(r.randint(2, 10)),
    brute=_boats_brute,
    hints=[
        "The heaviest person needs a boat; can anyone share it?",
        "If the lightest person can't share with the heaviest, nobody can.",
        "Sort, then use two pointers: pair the lightest with the heaviest when they fit, otherwise the heaviest goes alone.",
    ],
    insight="Pairing the heaviest with the lightest is always safe.",
    time="O(n log n)", space="O(1)",
    pitfalls=["Putting more than two people in a boat."],
)
def num_rescue_boats(people, limit):
    people = sorted(people)
    i, j, boats = 0, len(people) - 1, 0
    while i <= j:
        if people[i] + people[j] <= limit:
            i += 1
        j -= 1
        boats += 1
    return boats


def _gas_brute(gas, cost):
    n = len(gas)
    for s in range(n):
        tank = 0
        for k in range(n):
            i = (s + k) % n
            tank += gas[i] - cost[i]
            if tank < 0:
                break
        else:
            return s
    return -1


def _gas_input(r):
    n = r.randint(1, 7)
    return r.ints(n, 0, 6), r.ints(n, 0, 6)


@problem(
    slug="gas-station", title="Gas Station", difficulty="Medium", pattern=P, tags=["Array", "Greedy"],
    sig="canCompleteCircuit(self, gas: list[int], cost: list[int]) -> int",
    desc="""Gas stations sit on a circular route. Station `i` gives `gas[i]` fuel, and driving from station `i` to `i + 1` uses `cost[i]`. You start with an empty tank.

Return the index of the station from which you can drive all the way around once, or `-1` if impossible. If a solution exists, it is unique.""",
    constraints=["1 ≤ n ≤ 10⁵", "0 ≤ gas[i], cost[i] ≤ 10⁴"],
    samples=[([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]), ([2, 3, 4], [3, 4, 3])],
    gen=_gas_input,
    brute=_gas_brute,
    hints=[
        "If total gas is less than total cost, no start works.",
        "If you run dry between start s and station i, no start between s and i works either.",
        "Scan once with a running tank; when it goes negative, restart from the next station.",
    ],
    insight="A failed stretch rules out every start inside it, so one pass suffices.",
    time="O(n)", space="O(1)",
    pitfalls=["Simulating from every start, which is O(n²)."],
)
def can_complete_circuit(gas, cost):
    if sum(gas) < sum(cost):
        return -1
    start, tank = 0, 0
    for i in range(len(gas)):
        tank += gas[i] - cost[i]
        if tank < 0:
            start, tank = i + 1, 0
    return start


@problem(
    slug="two-city-scheduling", title="Two City Scheduling", difficulty="Medium", pattern=P, tags=["Array", "Greedy", "Sorting"],
    sig="twoCitySchedCost(self, costs: list[list[int]]) -> int",
    desc="""`2n` people must be interviewed; flying person `i` to city A costs `costs[i][0]` and to city B costs `costs[i][1]`. Send exactly `n` people to each city and return the minimum total cost.""",
    constraints=["2 ≤ len(costs) ≤ 100, even", "1 ≤ costs[i][j] ≤ 1000"],
    samples=[([[10, 20], [30, 200], [400, 50], [30, 20]],), ([[259, 770], [448, 54], [926, 667], [184, 139], [840, 118], [577, 469]],)],
    gen=lambda r: ([[r.randint(1, 50), r.randint(1, 50)] for _ in range(2 * r.randint(1, 4))],),
    brute=lambda costs: min(sum(costs[i][0] if i in a else costs[i][1] for i in range(len(costs))) for a in map(set, combinations(range(len(costs)), len(costs) // 2))),
    hints=[
        "Imagine sending everyone to B first, then moving n of them to A.",
        "Moving person i to A changes the total by costs[i][0] − costs[i][1].",
        "Sort by that difference and send the n people with the smallest differences to A.",
    ],
    insight="Sort by the relative cost of A over B.",
    time="O(n log n)", space="O(1)",
    pitfalls=["Sending each person to their cheaper city, which can break the n/n split."],
)
def two_city(costs):
    s = sorted(costs, key=lambda c: c[0] - c[1])
    n = len(s) // 2
    return sum(c[0] for c in s[:n]) + sum(c[1] for c in s[n:])


def _refuel_brute(target, startFuel, stations):
    n = len(stations)
    for k in range(n + 1):
        for pick in combinations(range(n), k):
            fuel, pos, ok = startFuel, 0, True
            for i, (loc, f) in enumerate(stations):
                fuel -= loc - pos
                pos = loc
                if fuel < 0:
                    ok = False
                    break
                if i in pick:
                    fuel += f
            if ok and fuel - (target - pos) >= 0:
                return k
    return -1


@problem(
    slug="minimum-number-of-refueling-stops", title="Minimum Number of Refueling Stops", difficulty="Hard", pattern=P,
    tags=["Array", "Dynamic Programming", "Greedy", "Heap"],
    sig="minRefuelStops(self, target: int, startFuel: int, stations: list[list[int]]) -> int",
    desc="""A car drives from position 0 to `target`, using one liter of fuel per mile and starting with `startFuel` liters. `stations[i] = [position, fuel]` is a station where the car can take all of that station's fuel (the tank is unlimited).

Return the minimum number of refueling stops to reach `target`, or `-1` if impossible. Reaching a station or the target with exactly 0 fuel left is fine.""",
    constraints=["1 ≤ target, startFuel ≤ 10⁹", "0 ≤ len(stations) ≤ 500", "station positions are strictly increasing and < target"],
    samples=[(1, 1, []), (100, 1, [[10, 100]]), (100, 10, [[10, 60], [20, 30], [30, 30], [60, 40]])],
    gen=lambda r: (lambda pos: (r.randint((pos[-1] if pos else 0) + 1, 60), r.randint(1, 25), [[p, r.randint(1, 20)] for p in pos]))(sorted(r.distinct(r.randint(0, 6), 1, 50))),
    brute=_refuel_brute,
    hints=[
        "You don't have to decide to stop at a station when you pass it; you can decide later.",
        "Drive as far as possible; when you'd run out, refuel retroactively from the best station you've passed.",
        "Keep a max-heap of fuel amounts from passed stations; pop the largest whenever fuel can't reach the next point. If the heap is empty, it's impossible.",
    ],
    insight="Deferred greedy choice with a max-heap: always refuel from the largest passed station.",
    time="O(n log n)", space="O(n)",
    pitfalls=["Refueling at every station you can reach."],
)
def min_refuel_stops(target, startFuel, stations):
    heap, fuel, stops = [], startFuel, 0
    for pos, f in stations + [[target, 0]]:
        while fuel < pos and heap:
            fuel -= heapq.heappop(heap)
            stops += 1
        if fuel < pos:
            return -1
        heapq.heappush(heap, -f)
    return stops


def _largest_pal_brute(num):
    from itertools import permutations
    best = -1
    c = Counter(num)
    # Brute over choices of how many of each digit to use (small inputs only).
    digits = sorted(c)
    def rec(i, chosen):
        nonlocal best
        if i == len(digits):
            s = "".join(d * k for d, k in chosen)
            if not s:
                return
            odd = sum(k % 2 for _, k in chosen)
            if odd > 1:
                return
            half = "".join(sorted("".join(d * (k // 2) for d, k in chosen), reverse=True))
            mid = "".join(d for d, k in chosen if k % 2)
            p = half + mid + half[::-1]
            if p[0] == "0" and len(p) > 1:
                return
            best = max(best, int(p))
            return
        for k in range(c[digits[i]] + 1):
            rec(i + 1, chosen + [(digits[i], k)])
    rec(0, [])
    return str(best)


@problem(
    slug="largest-palindromic-number", title="Largest Palindromic Number", difficulty="Medium", pattern=P,
    tags=["Hash Table", "String", "Greedy", "Counting"],
    sig="largestPalindromic(self, num: str) -> str",
    desc="""`num` is a string of digits. Using some of its digits (at least one, each at most once, in any order), build the largest palindromic integer with no leading zeros, and return it as a string.""",
    constraints=["1 ≤ len(num) ≤ 10⁵", "num contains only digits"],
    samples=[("444947137",), ("00009",), ("00",)],
    gen=lambda r: ("".join(r.choice("00123459") for _ in range(r.randint(1, 7))),),
    brute=_largest_pal_brute,
    hints=[
        "A palindrome is a half, an optional middle digit, and the half reversed.",
        "Use as many pairs as possible, largest digits first, for the outer half.",
        "Zeros can't be on the outside: if the half would be only zeros, drop it. For the middle, pick the largest leftover digit.",
    ],
    insight="Greedily place the largest pairs outside and the largest single digit in the middle.",
    time="O(n)", space="O(1) (10 digit counts)",
    pitfalls=["Returning something like \"00900\" with leading zeros."],
)
def largest_palindromic(num):
    c = Counter(num)
    half = "".join(d * (c[d] // 2) for d in "9876543210")
    if half.strip("0") == "":
        half = ""
    mid = next((d for d in "9876543210" if c[d] % 2), "")
    if not half and not mid:
        return "0"
    return half + mid + half[::-1]


@problem(
    slug="assign-cookies", title="Assign Cookies", difficulty="Easy", pattern=P, tags=["Array", "Two Pointers", "Greedy", "Sorting"],
    sig="findContentChildren(self, g: list[int], s: list[int]) -> int",
    desc="""Child `i` is content with a cookie of size at least `g[i]`. `s[j]` is the size of cookie `j`. Each child gets at most one cookie. Return the maximum number of content children.""",
    constraints=["1 ≤ len(g) ≤ 3 × 10⁴", "0 ≤ len(s) ≤ 3 × 10⁴", "1 ≤ g[i], s[j] ≤ 2³¹ − 1"],
    samples=[([1, 2, 3], [1, 1]), ([1, 2], [1, 2, 3])],
    gen=lambda r: (r.ints(r.randint(1, 7), 1, 8), r.ints(r.randint(0, 7), 1, 8)),
    hints=[
        "Small cookies are only useful for children with small needs.",
        "Sort both the children and the cookies by size.",
        "Walk through cookies in increasing size; give each to the least greedy child still waiting if it's big enough.",
    ],
    insight="Matching sorted needs to sorted sizes greedily is optimal.",
    time="O(n log n + m log m)", space="O(1)",
    pitfalls=["Giving the biggest cookie to the least greedy child."],
)
def find_content_children(g, s):
    g, s = sorted(g), sorted(s)
    i = 0
    for size in s:
        if i < len(g) and size >= g[i]:
            i += 1
    return i


def _candy_brute(ratings):
    n = len(ratings)
    c = [1] * n
    changed = True
    while changed:
        changed = False
        for i in range(n):
            for j in (i - 1, i + 1):
                if 0 <= j < n and ratings[i] > ratings[j] and c[i] <= c[j]:
                    c[i] = c[j] + 1
                    changed = True
    return sum(c)


@problem(
    slug="candy", title="Candy", difficulty="Hard", pattern=P, tags=["Array", "Greedy"],
    sig="candy(self, ratings: list[int]) -> int",
    desc="""Children stand in a line with `ratings`. Give each child at least one candy, and give a child with a higher rating than a neighbor more candies than that neighbor. Return the minimum total number of candies.""",
    constraints=["1 ≤ n ≤ 2 × 10⁴", "0 ≤ ratings[i] ≤ 2 × 10⁴"],
    samples=[([1, 0, 2],), ([1, 2, 2],)],
    gen=lambda r: (r.ints(r.randint(1, 10), 0, 5),),
    brute=_candy_brute,
    hints=[
        "Handle the two neighbor rules separately.",
        "A left-to-right pass fixes the rule for left neighbors; a right-to-left pass fixes it for right neighbors.",
        "In the second pass, take the maximum of the current count and (right neighbor's count + 1) when the rating is higher.",
    ],
    insight="Two directional passes, combined with max, satisfy both constraints minimally.",
    time="O(n)", space="O(n)",
    pitfalls=["Giving more candy for equal ratings (not required)."],
)
def candy(ratings):
    n = len(ratings)
    c = [1] * n
    for i in range(1, n):
        if ratings[i] > ratings[i - 1]:
            c[i] = c[i - 1] + 1
    for i in range(n - 2, -1, -1):
        if ratings[i] > ratings[i + 1]:
            c[i] = max(c[i], c[i + 1] + 1)
    return sum(c)


@problem(
    slug="maximum-swap", title="Maximum Swap", difficulty="Medium", pattern=P, tags=["Math", "Greedy"],
    sig="maximumSwap(self, num: int) -> int",
    desc="""You may swap two digits of `num` at most once. Return the largest number you can get.""",
    constraints=["0 ≤ num ≤ 10⁸"],
    samples=[(2736,), (9973,), (0,)],
    tests=[(98368,), (1993,)],
    gen=lambda r: (r.randint(0, 10 ** r.randint(1, 8)),),
    brute=lambda num: max([num] + [int("".join((lambda d: (d.__setitem__(i, s[j]), d.__setitem__(j, s[i]), d)[2])(list(s)))) for s in [str(num)] for i in range(len(s)) for j in range(i + 1, len(s))]),
    hints=[
        "You want to improve the leftmost digit possible.",
        "For each position, is there a larger digit somewhere to its right?",
        "Record the last position of each digit. Scan left to right; for the first digit that has a larger digit later, swap it with the last occurrence of the largest such digit.",
    ],
    insight="Swap the first improvable digit with the rightmost occurrence of the largest later digit.",
    time="O(d)", space="O(1)",
    pitfalls=["Swapping with the first occurrence of the larger digit instead of the last."],
)
def maximum_swap(num):
    d = list(str(num))
    last = {c: i for i, c in enumerate(d)}
    for i, c in enumerate(d):
        for big in "9876543210":
            if big <= c:
                break
            if last.get(big, -1) > i:
                j = last[big]
                d[i], d[j] = d[j], d[i]
                return int("".join(d))
    return num


def _replace_brute(nums):
    # Process from the right: split each value into the fewest parts whose max is ≤ the next value.
    ops, nxt = 0, nums[-1]
    for x in reversed(nums[:-1]):
        k = 1
        while -(-x // k) > nxt:
            k += 1
        ops += k - 1
        nxt = x // k
    return ops


@problem(
    slug="minimum-replacements-to-sort-the-array", title="Minimum Replacements to Sort the Array", difficulty="Hard", pattern=P,
    tags=["Array", "Math", "Greedy"],
    sig="minimumReplacement(self, nums: list[int]) -> int",
    desc="""In one operation you replace any element with two positive integers that add up to it. Return the minimum number of operations to make `nums` sorted in non-decreasing order.""",
    constraints=["1 ≤ len(nums) ≤ 10⁵", "1 ≤ nums[i] ≤ 10⁹"],
    samples=[([3, 9, 3],), ([1, 2, 3, 4, 5],)],
    tests=[([12, 9, 7, 6, 17, 19, 21],)],
    gen=lambda r: (r.ints(r.randint(1, 8), 1, 30),),
    brute=_replace_brute,
    hints=[
        "The last element never needs splitting; work from right to left.",
        "To fit x before a value nxt, split it into k = ceil(x / nxt) parts (k − 1 operations).",
        "Split as evenly as possible so the smallest part, x // k, is as large as possible; it becomes the new nxt.",
    ],
    insight="Right-to-left greedy: minimal parts, split evenly to keep the leftmost part large.",
    time="O(n)", space="O(1)",
    pitfalls=["Splitting unevenly, which makes the next limit smaller than necessary."],
)
def minimum_replacement(nums):
    ops, nxt = 0, nums[-1]
    for x in reversed(nums[:-1]):
        k = -(-x // nxt)
        ops += k - 1
        nxt = x // k
    return ops


@problem(
    slug="lemonade-change", title="Lemonade Change", difficulty="Easy", pattern=P, tags=["Array", "Greedy"],
    sig="lemonadeChange(self, bills: list[int]) -> bool",
    desc="""Lemonade costs $5. Customers pay in order with a $5, $10 or $20 bill, and you start with no change. Return `true` if you can give every customer correct change.""",
    constraints=["1 ≤ len(bills) ≤ 10⁵", "bills[i] is 5, 10 or 20"],
    samples=[([5, 5, 5, 10, 20],), ([5, 5, 10, 10, 20],)],
    gen=lambda r: ([r.choice([5, 5, 10, 20]) for _ in range(r.randint(1, 10))],),
    hints=[
        "You only need to know how many $5 and $10 bills you hold.",
        "For $10 you must give one $5 back.",
        "For $20, prefer giving $10 + $5 (keeping $5s, which are more flexible), otherwise three $5s.",
    ],
    insight="Greedy change-making: spend the less flexible bill first.",
    time="O(n)", space="O(1)",
    pitfalls=["Giving three $5s when a $10 + $5 is available."],
)
def lemonade_change(bills):
    five = ten = 0
    for b in bills:
        if b == 5:
            five += 1
        elif b == 10:
            if not five:
                return False
            five, ten = five - 1, ten + 1
        elif ten and five:
            ten, five = ten - 1, five - 1
        elif five >= 3:
            five -= 3
        else:
            return False
    return True


@problem(
    slug="minimum-add-to-make-parentheses-valid", title="Minimum Add to Make Parentheses Valid", difficulty="Medium", pattern=P,
    tags=["String", "Stack", "Greedy"],
    sig="minAddToMakeValid(self, s: str) -> int",
    desc="""`s` contains only `'('` and `')'`. Return the minimum number of parentheses you need to insert (anywhere) to make it valid.""",
    constraints=["1 ≤ len(s) ≤ 1000"],
    samples=[("())",), ("(((",)],
    gen=lambda r: (r.word(r.randint(1, 12), "()"),),
    hints=[
        "Scan left to right, tracking unmatched '('.",
        "A ')' with no unmatched '(' needs an inserted '(' before it.",
        "At the end, every unmatched '(' needs a ')'. The answer is both counts added.",
    ],
    insight="A balance counter plus a count of forced insertions.",
    time="O(n)", space="O(1)",
    pitfalls=["Letting the balance go negative instead of counting an insertion."],
)
def min_add(s):
    bal = need = 0
    for c in s:
        if c == "(":
            bal += 1
        elif bal:
            bal -= 1
        else:
            need += 1
    return bal + need


def _wiggle_brute(nums):
    best = 1
    n = len(nums)
    for mask in range(1, 1 << n):
        seq = [nums[i] for i in range(n) if mask >> i & 1]
        diffs = [b - a for a, b in zip(seq, seq[1:])]
        if all(d != 0 for d in diffs) and all(x * y < 0 for x, y in zip(diffs, diffs[1:])):
            best = max(best, len(seq))
    return best


@problem(
    slug="wiggle-subsequence", title="Wiggle Subsequence", difficulty="Medium", pattern=P, tags=["Array", "Dynamic Programming", "Greedy"],
    sig="wiggleMaxLength(self, nums: list[int]) -> int",
    desc="""A **wiggle sequence** has differences between consecutive elements that strictly alternate between positive and negative (a single element, or two different elements, also count). Return the length of the longest wiggle subsequence of `nums`.""",
    constraints=["1 ≤ len(nums) ≤ 1000", "0 ≤ nums[i] ≤ 1000"],
    samples=[([1, 7, 4, 9, 2, 5],), ([1, 17, 5, 10, 13, 15, 10, 5, 16, 8],), ([1, 2, 3, 4, 5, 6, 7, 8, 9],)],
    gen=lambda r: (r.ints(r.randint(1, 10), 0, 5),),
    brute=_wiggle_brute,
    hints=[
        "Only the turning points (peaks and valleys) matter.",
        "Keep two lengths: the longest wiggle ending with an up-step, and with a down-step.",
        "On an increase, up = down + 1; on a decrease, down = up + 1; equal values change nothing.",
    ],
    insight="Counting direction changes greedily gives the longest wiggle.",
    time="O(n)", space="O(1)",
    pitfalls=["Treating equal neighbors as a wiggle."],
)
def wiggle_max_length(nums):
    up = down = 1
    for a, b in zip(nums, nums[1:]):
        if b > a:
            up = down + 1
        elif b < a:
            down = up + 1
    return max(up, down)


EXTRA = {
    "jump-game": {
        "edge": [([0],), ([1, 0],), ([0, 1],), ([2, 0, 0],), ([1, 1, 0, 1],)],
        "large": [lambda r: ([1] * 9999 + [0],), lambda r: ([100000] * 10000,), lambda r: ([r.randint(0, 3) for _ in range(10000)],)],
    },
    "jump-game-ii": {
        "edge": [([1, 2],), ([1, 1, 1, 1],), ([1000],), ([5, 0, 0, 0, 0, 0],)],
        "large": [lambda r: ([1] * 10000,), lambda r: (r.ints(9999, 500, 1000) + [0],)],
    },
    "boats-to-save-people": {
        "edge": [([1], 1), ([5, 5], 5), ([5, 5], 10), ([3, 2, 2, 1], 3), ([30000, 1], 30000)],
        "large": [lambda r: (r.ints(15000, 1, 30000), 30000)],
    },
    "gas-station": {
        "edge": [([0], [0]), ([5], [4]), ([4], [5]), ([5, 1, 2, 3, 4], [4, 4, 1, 5, 1]), ([2, 0, 1], [1, 1, 1])],
        "large": [lambda r: (lambda c: ([x + r.choice([0, 0, 1]) for x in c], c))(r.ints(10000, 0, 10000)), lambda r: ([0] * 9999 + [10000], [1] * 10000)],
    },
    "two-city-scheduling": {"edge": [([[1, 1], [1, 1]],), ([[1, 1000], [1000, 1]],), ([[515, 563], [451, 713], [537, 709], [343, 819], [855, 779], [457, 60], [650, 359], [631, 42]],)]},
    "minimum-number-of-refueling-stops": {
        "edge": [(100, 100, []), (100, 99, []), (100, 50, [[50, 50]]), (100, 49, [[50, 50]]), (1000000000, 1, [[1, 999999999]])],
        "large": [lambda r: (10**9, 10**6, [[i * 10**6, 10**6 + r.randint(0, 100)] for i in range(1, 500)])],
    },
    "largest-palindromic-number": {
        "edge": [("0",), ("00",), ("9",), ("100",), ("1122",), ("0000001",)],
        "large": [lambda r: (r.word(60000, "0123456789"),), lambda r: ("0" * 30000 + "7",)],
    },
    "assign-cookies": {
        "edge": [([1], []), ([2], [1]), ([1], [2147483647]), ([10, 9, 8, 7], [5, 6, 7, 8])],
        "large": [lambda r: (r.ints(8000, 1, 10**6), r.ints(8000, 1, 10**6))],
    },
    "candy": {
        "edge": [([5],), ([1, 1, 1],), ([1, 2, 3],), ([3, 2, 1],), ([1, 3, 2, 2, 1],)],
        "large": [lambda r: (list(range(15000, 0, -1)),), lambda r: (r.ints(15000, 0, 20000),)],
    },
    "maximum-swap": {"edge": [(0,), (9,), (10,), (99901,), (1993,), (100000000,), (98765432,)]},
    "minimum-replacements-to-sort-the-array": {
        "edge": [([1],), ([5, 4, 3, 2, 1],), ([2, 10, 20, 19, 1],), ([7, 6, 15, 6, 11, 14, 10],)],
        "edge_nb": [([1000000000, 1],), ([1000000000] * 5 + [999999999],)],
        "large": [lambda r: (r.ints(12000, 1, 10**9),)],
    },
    "lemonade-change": {
        "edge": [([5],), ([10],), ([20],), ([5, 5, 10, 10, 20],), ([5, 5, 5, 20],)],
        "large": [lambda r: ([5] * 5000 + [r.choice([10, 20]) for _ in range(5000)],)],
    },
    "minimum-add-to-make-parentheses-valid": {"edge": [("(",), (")",), ("()",), (")(",), ("()))((",)], "large": [lambda r: (")" * 500 + "(" * 500,)]},
    "wiggle-subsequence": {"edge": [([0],), ([0, 0],), ([0, 1],), ([3, 3, 3, 2, 5],), ([1, 2, 3, 4, 5, 6, 7, 8, 9],)]},
}
