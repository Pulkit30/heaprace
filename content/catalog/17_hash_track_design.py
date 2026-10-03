from bisect import bisect_right
from collections import Counter, OrderedDict, defaultdict
from fractions import Fraction

from catalog_lib import problem

HM = "arrays-hashing"
KT = "knowing-what-to-track"
CD = "custom-data-structures"


def _design_ops(r, cls, ctor_args, makers, count=(4, 14)):
    """Random op sequence: makers maps op name to a function r -> argument list."""
    ops, args = [cls], [ctor_args]
    names = sorted(makers)
    for _ in range(r.randint(*count)):
        op = r.choice(names)
        ops.append(op)
        args.append(makers[op](r))
    return ops, args


# ---------------------------------------------------------------- hash maps


class _HashMapRef:
    def __init__(self):
        self.d = {}

    def put(self, key, value):
        self.d[key] = value

    def get(self, key):
        return self.d.get(key, -1)

    def remove(self, key):
        self.d.pop(key, None)


@problem(
    slug="design-hashmap", title="Design HashMap", difficulty="Easy", pattern=HM, tags=["Array", "Hash Table", "Linked List", "Design", "Hash Function"],
    design=True, cls="MyHashMap",
    starter="""class MyHashMap:
    def __init__(self):
        pass

    def put(self, key: int, value: int) -> None:
        pass

    def get(self, key: int) -> int:
        pass

    def remove(self, key: int) -> None:
        pass
""",
    desc="""Design a hash map **without** using a built-in hash table:

- `put(key, value)` inserts or updates a key.
- `get(key)` gives the value for `key`, or `-1` if it's absent.
- `remove(key)` deletes the key if present.""",
    constraints=["0 ≤ key, value ≤ 10⁶", "at most 10⁴ calls"],
    samples=[(["MyHashMap", "put", "put", "get", "get", "put", "get", "remove", "get"], [[], [1, 1], [2, 2], [1], [3], [2, 1], [2], [2], [2]]),
             (["MyHashMap", "get", "remove", "get"], [[], [7], [7], [7]])],
    gen=lambda r: _design_ops(r, "MyHashMap", [], {"put": lambda r: [r.randint(0, 9), r.randint(0, 99)], "get": lambda r: [r.randint(0, 9)], "remove": lambda r: [r.randint(0, 9)]}),
    hints=[
        "Use an array of buckets and map each key to a bucket with a hash function (like key % size).",
        "Different keys can land in the same bucket, so each bucket holds a small list of (key, value) pairs.",
        "put updates an existing pair or appends; get and remove scan only that bucket.",
    ],
    insight="Separate chaining: buckets of short lists keep operations fast on average.",
    time="O(1) average per operation", space="O(n + buckets)",
    pitfalls=["Appending a duplicate pair instead of updating an existing key."],
)
class MyHashMap(_HashMapRef):
    pass


def _fraction_brute(n, d):
    sign = "-" if n * d < 0 else ""
    n, d = abs(n), abs(d)
    whole, rem = divmod(n, d)
    if rem == 0:
        return sign + str(whole) if whole or not sign else "0"
    digits, seen = [], {}
    while rem and rem not in seen:
        seen[rem] = len(digits)
        rem *= 10
        digits.append(str(rem // d))
        rem %= d
    if rem:
        i = seen[rem]
        frac = "".join(digits[:i]) + "(" + "".join(digits[i:]) + ")"
    else:
        frac = "".join(digits)
    return f"{sign}{whole}.{frac}"


@problem(
    slug="fraction-to-recurring-decimal", title="Fraction to Recurring Decimal", difficulty="Medium", pattern=HM, tags=["Hash Table", "Math", "String"],
    sig="fractionToDecimal(self, numerator: int, denominator: int) -> str",
    desc="""Return `numerator / denominator` as a decimal string. If the fractional part repeats, put the repeating part in parentheses (e.g. `"0.(6)"`, `"0.1(6)"`). The answer is unique.""",
    constraints=["-2³¹ ≤ numerator, denominator ≤ 2³¹ − 1", "denominator ≠ 0"],
    samples=[(1, 2), (2, 1), (4, 333)],
    tests=[(-50, 8), (0, -5), (1, 6), (-2147483648, -1), (7, -12)],
    gen=lambda r: (r.randint(-60, 60), r.choice([x for x in range(-30, 31) if x])),
    hints=[
        "Long division: each step multiplies the remainder by 10 and divides.",
        "The decimal starts repeating exactly when a remainder repeats.",
        "Map each remainder to the position of the digit it produced; when you see it again, wrap from that position in parentheses. Handle the sign separately.",
    ],
    insight="Remainders determine the digits, so a hash map of remainders detects the cycle.",
    time="O(denominator)", space="O(denominator)",
    pitfalls=["Getting the sign wrong when exactly one input is negative, or printing \"-0\"."],
)
def fraction_to_decimal(numerator, denominator):
    return _fraction_brute(numerator, denominator)


class _LoggerRef:
    def __init__(self):
        self.last = {}

    def shouldPrintMessage(self, timestamp, message):
        if timestamp - self.last.get(message, -10) >= 10:
            self.last[message] = timestamp
            return True
        return False


def _logger_ops(r):
    ops, args, t = ["Logger"], [[]], 0
    for _ in range(r.randint(4, 14)):
        t += r.randint(0, 6)
        ops.append("shouldPrintMessage")
        args.append([t, r.choice(["foo", "bar", "baz"])])
    return ops, args


@problem(
    slug="logger-rate-limiter", title="Logger Rate Limiter", difficulty="Easy", pattern=HM, tags=["Hash Table", "Design", "Data Stream"],
    design=True, cls="Logger",
    starter="""class Logger:
    def __init__(self):
        pass

    def shouldPrintMessage(self, timestamp: int, message: str) -> bool:
        pass
""",
    desc="""Messages arrive in non-decreasing timestamp order (in seconds). A message should be printed only if the same message hasn't been **printed** in the last 10 seconds: a message printed at time `t` blocks identical messages until time `t + 10`.

`shouldPrintMessage(timestamp, message)` reports whether to print it.""",
    constraints=["0 ≤ timestamp ≤ 10⁹", "timestamps never decrease", "at most 10⁴ calls"],
    samples=[(["Logger", "shouldPrintMessage", "shouldPrintMessage", "shouldPrintMessage", "shouldPrintMessage", "shouldPrintMessage", "shouldPrintMessage"],
              [[], [1, "foo"], [2, "bar"], [3, "foo"], [8, "bar"], [10, "foo"], [11, "foo"]]),
             (["Logger", "shouldPrintMessage", "shouldPrintMessage"], [[], [0, "a"], [0, "a"]])],
    gen=_logger_ops,
    hints=[
        "You only need the last time each message was actually printed.",
        "A dictionary from message to that time does it.",
        "Print (and update the time) if the message is new or at least 10 seconds have passed; otherwise refuse without updating.",
    ],
    insight="A map of last-printed times answers each call in O(1).",
    time="O(1) per call", space="O(distinct messages)",
    pitfalls=["Updating the timestamp for messages that were not printed."],
)
class Logger(_LoggerRef):
    pass


def _bijection(a, b):
    return len(a) == len(b) and len(set(a)) == len(set(b)) == len(set(zip(a, b)))


@problem(
    slug="isomorphic-strings", title="Isomorphic Strings", difficulty="Easy", pattern=HM, tags=["Hash Table", "String"],
    sig="isIsomorphic(self, s: str, t: str) -> bool",
    desc="""Two strings are isomorphic if the characters of `s` can be replaced to get `t`, where every occurrence of a character is replaced by the same character and no two different characters map to the same character. Return whether `s` and `t` are isomorphic.""",
    constraints=["1 ≤ len(s) = len(t) ≤ 5 × 10⁴", "printable ASCII"],
    samples=[("egg", "add"), ("foo", "bar"), ("paper", "title")],
    tests=[("badc", "baba"),],
    gen=lambda r: (lambda n: (r.word(n, "abc"), r.word(n, "xyz")))(r.randint(1, 6)),
    brute=lambda s, t: _bijection(s, t),
    hints=[
        "The mapping must be consistent in both directions.",
        "Keep one map from s to t and another from t to s.",
        "For each position, if either map already sends the character somewhere else, fail.",
    ],
    insight="A bijection needs two maps (or matching first-occurrence patterns).",
    time="O(n)", space="O(alphabet)",
    pitfalls=["Checking only the s → t direction, which accepts \"badc\" vs \"baba\"."],
)
def is_isomorphic(s, t):
    st, ts = {}, {}
    for a, b in zip(s, t):
        if st.setdefault(a, b) != b or ts.setdefault(b, a) != a:
            return False
    return True


@problem(
    slug="word-pattern", title="Word Pattern", difficulty="Easy", pattern=HM, tags=["Hash Table", "String"],
    sig="wordPattern(self, pattern: str, s: str) -> bool",
    desc="""`s` is a sequence of words separated by single spaces. Return `true` if `s` follows `pattern`: there is a one-to-one match between the letters of `pattern` and the words of `s`.""",
    constraints=["1 ≤ len(pattern) ≤ 300", "1 ≤ len(s) ≤ 3000"],
    samples=[("abba", "dog cat cat dog"), ("abba", "dog cat cat fish"), ("aaaa", "dog cat cat dog")],
    tests=[("aaa", "aa aa aa aa"), ("abba", "dog dog dog dog")],
    gen=lambda r: (lambda n: (r.word(n, "ab"), " ".join(r.choice(["dog", "cat"]) for _ in range(n + r.choice([0, 0, 0, 1])))))(r.randint(1, 5)),
    brute=lambda p, s: _bijection(p, s.split()),
    hints=[
        "First, the number of letters must equal the number of words.",
        "Each letter maps to one word, and each word to one letter.",
        "Keep two dictionaries and check both directions at every position.",
    ],
    insight="Same bijection check as isomorphic strings, at the word level.",
    time="O(n)", space="O(n)",
    pitfalls=["Ignoring a length mismatch between pattern and words."],
)
def word_pattern(pattern, s):
    words = s.split()
    if len(words) != len(pattern):
        return False
    a, b = {}, {}
    for c, w in zip(pattern, words):
        if a.setdefault(c, w) != w or b.setdefault(w, c) != c:
            return False
    return True


@problem(
    slug="contains-duplicate-ii", title="Contains Duplicate II", difficulty="Easy", pattern=HM, tags=["Array", "Hash Table", "Sliding Window"],
    sig="containsNearbyDuplicate(self, nums: list[int], k: int) -> bool",
    desc="""Return `true` if there are two distinct indices `i` and `j` with `nums[i] == nums[j]` and `|i − j| ≤ k`.""",
    constraints=["1 ≤ len(nums) ≤ 10⁵", "0 ≤ k ≤ 10⁵"],
    samples=[([1, 2, 3, 1], 3), ([1, 0, 1, 1], 1), ([1, 2, 3, 1, 2, 3], 2)],
    gen=lambda r: (r.ints(r.randint(1, 10), 0, 5), r.randint(0, 4)),
    brute=lambda nums, k: any(nums[i] == nums[j] for i in range(len(nums)) for j in range(i + 1, min(len(nums), i + k + 1))),
    hints=[
        "Only the most recent index of each value matters.",
        "Keep a map from value to its last index.",
        "For each i, if the value was seen at j with i − j ≤ k, answer true; then update the index.",
    ],
    insight="A last-seen map (or a size-k window set) finds nearby duplicates in O(n).",
    time="O(n)", space="O(n)",
    pitfalls=["Comparing every pair, which is O(n·k)."],
)
def contains_nearby_duplicate(nums, k):
    last = {}
    for i, v in enumerate(nums):
        if v in last and i - last[v] <= k:
            return True
        last[v] = i
    return False


@problem(
    slug="bulls-and-cows", title="Bulls and Cows", difficulty="Medium", pattern=HM, tags=["Hash Table", "String", "Counting"],
    sig="getHint(self, secret: str, guess: str) -> str",
    desc="""`secret` and `guess` are digit strings of the same length. **Bulls** are digits in the correct position. **Cows** are digits in the guess that appear in the secret but in the wrong position (each secret digit can be matched at most once, and bulls are matched first). Return `"xAyB"` with `x` bulls and `y` cows.""",
    constraints=["1 ≤ len ≤ 1000", "digits only"],
    samples=[("1807", "7810"), ("1123", "0111")],
    gen=lambda r: (lambda n: (r.word(n, "0123"), r.word(n, "0123")))(r.randint(1, 8)),
    brute=lambda s, g: (lambda b: f"{b}A{sum((Counter(s) & Counter(g)).values()) - b}B")(sum(a == c for a, c in zip(s, g))),
    hints=[
        "Count bulls by comparing positions directly.",
        "For the remaining (non-bull) positions, count digits of the secret and of the guess separately.",
        "Cows = sum over digits of min(secret count, guess count).",
    ],
    insight="Bulls by position; cows by the overlap of the leftover digit counts.",
    time="O(n)", space="O(1)",
    pitfalls=["Counting a bull again as a cow."],
)
def get_hint(secret, guess):
    bulls = sum(a == b for a, b in zip(secret, guess))
    rest_s = Counter(a for a, b in zip(secret, guess) if a != b)
    rest_g = Counter(b for a, b in zip(secret, guess) if a != b)
    return f"{bulls}A{sum((rest_s & rest_g).values())}B"


@problem(
    slug="jewels-and-stones", title="Jewels and Stones", difficulty="Easy", pattern=HM, tags=["Hash Table", "String"],
    sig="numJewelsInStones(self, jewels: str, stones: str) -> int",
    desc="""Each character of `jewels` is a type of stone that's a jewel (all distinct). Return how many of the stones in `stones` are jewels. Letters are case-sensitive.""",
    constraints=["1 ≤ len(jewels), len(stones) ≤ 50", "letters only"],
    samples=[("aA", "aAAbbbb"), ("z", "ZZ")],
    gen=lambda r: ("".join(r.sample("abAB", r.randint(1, 3))), r.word(r.randint(1, 10), "abAB")),
    hints=[
        "Checking each stone against the jewel string is O(j·s).",
        "Put the jewel types in a set.",
        "Count the stones whose character is in that set.",
    ],
    insight="A set makes each membership check O(1).",
    time="O(j + s)", space="O(j)",
    pitfalls=["Ignoring case."],
)
def num_jewels(jewels, stones):
    j = set(jewels)
    return sum(c in j for c in stones)


# ---------------------------------------------------------------- knowing what to track


@problem(
    slug="palindrome-permutation", title="Palindrome Permutation", difficulty="Easy", pattern=KT, tags=["Hash Table", "String", "Bit Manipulation"],
    sig="canPermutePalindrome(self, s: str) -> bool",
    desc="""Return `true` if some rearrangement of `s` is a palindrome.""",
    constraints=["1 ≤ len(s) ≤ 5000", "lowercase letters"],
    samples=[("code",), ("aab",), ("carerac",)],
    gen=lambda r: (r.word(r.randint(1, 9), "abc"),),
    brute=lambda s: any(p == p[::-1] for p in {"".join(x) for x in __import__("itertools").permutations(s)}) if len(s) <= 7 else sum(v % 2 for v in Counter(s).values()) <= 1,
    hints=[
        "In a palindrome, characters pair up around the center.",
        "So at most one character can appear an odd number of times.",
        "Count the characters (or toggle membership in a set) and check how many counts are odd.",
    ],
    insight="Track only the parity of each character's count.",
    time="O(n)", space="O(alphabet)",
    pitfalls=["Generating permutations."],
)
def can_permute_palindrome(s):
    return sum(v % 2 for v in Counter(s).values()) <= 1


@problem(
    slug="valid-anagram", title="Valid Anagram", difficulty="Easy", pattern=KT, tags=["Hash Table", "String", "Sorting"],
    sig="isAnagram(self, s: str, t: str) -> bool",
    desc="""Return `true` if `t` is an anagram of `s` (it uses exactly the same letters, the same number of times).""",
    constraints=["1 ≤ len(s), len(t) ≤ 5 × 10⁴", "lowercase letters"],
    samples=[("anagram", "nagaram"), ("rat", "car")],
    gen=lambda r: (lambda s: (s, "".join(r.sample(s, len(s))) if r.random() < 0.5 else r.word(len(s) + r.choice([0, 0, 1]), "abc")))(r.word(r.randint(1, 7), "abc")),
    brute=lambda s, t: sorted(s) == sorted(t),
    hints=[
        "Anagrams have identical letter counts.",
        "Count letters of s up and letters of t down.",
        "If every count ends at zero, they're anagrams.",
    ],
    insight="Compare frequency counts rather than orderings.",
    time="O(n)", space="O(alphabet)",
    pitfalls=["Forgetting to check that the lengths match."],
)
def is_anagram(s, t):
    return Counter(s) == Counter(t)


@problem(
    slug="group-anagrams", title="Group Anagrams", difficulty="Medium", pattern=KT, tags=["Array", "Hash Table", "String", "Sorting"],
    sig="groupAnagrams(self, strs: list[str]) -> list[list[str]]", compare="unordered-deep",
    desc="""Group the strings that are anagrams of each other. Return the groups in any order (strings within a group in any order too).""",
    constraints=["1 ≤ len(strs) ≤ 10⁴", "0 ≤ len(strs[i]) ≤ 100", "lowercase letters"],
    samples=[(["eat", "tea", "tan", "ate", "nat", "bat"],), ([""],), (["a"],)],
    gen=lambda r: ([r.word(r.randint(0, 3), "abc") for _ in range(r.randint(1, 8))],),
    hints=[
        "Anagrams share the same multiset of letters.",
        "Turn each string into a key that is identical for anagrams: its sorted letters, or a tuple of 26 counts.",
        "Group strings in a dictionary by that key.",
    ],
    insight="A canonical key per anagram class makes grouping a single pass.",
    time="O(n · L log L)", space="O(n · L)",
    pitfalls=["Comparing every pair of strings."],
)
def group_anagrams(strs):
    groups = defaultdict(list)
    for s in strs:
        groups["".join(sorted(s))].append(s)
    return list(groups.values())


class _TicTacToeRef:
    def __init__(self, n):
        self.n = n
        self.board = [[0] * n for _ in range(n)]

    def move(self, row, col, player):
        b, n = self.board, self.n
        b[row][col] = player
        lines = [b[row], [b[i][col] for i in range(n)], [b[i][i] for i in range(n)], [b[i][n - 1 - i] for i in range(n)]]
        return player if any(all(v == player for v in line) for line in lines) else 0


def _ttt_ops(r):
    n = r.randint(2, 4)
    cells = [(i, j) for i in range(n) for j in range(n)]
    r.shuffle(cells)
    ops, args, ref = ["TicTacToe"], [[n]], _TicTacToeRef(n)
    for k, (i, j) in enumerate(cells):
        p = 1 + k % 2
        ops.append("move")
        args.append([i, j, p])
        if ref.move(i, j, p):
            break
    return ops, args


@problem(
    slug="design-tic-tac-toe", title="Design Tic-Tac-Toe", difficulty="Medium", pattern=KT, tags=["Array", "Hash Table", "Design", "Matrix", "Simulation"],
    design=True, cls="TicTacToe",
    starter="""class TicTacToe:
    def __init__(self, n: int):
        pass

    def move(self, row: int, col: int, player: int) -> int:
        pass
""",
    desc="""Two players (1 and 2) play on an `n × n` board. A player wins by filling an entire row, column, or one of the two diagonals.

`move(row, col, player)` places the player's mark on an empty cell and reports `0` if nobody has won yet, or the player's number if this move wins. Moves are always valid, and no moves are made after a win. Aim for O(1) per move.""",
    constraints=["2 ≤ n ≤ 100", "at most n² calls"],
    samples=[(["TicTacToe", "move", "move", "move", "move", "move", "move", "move"], [[3], [0, 0, 1], [0, 2, 2], [2, 2, 1], [1, 1, 2], [2, 0, 1], [1, 0, 2], [2, 1, 1]]),
             (["TicTacToe", "move", "move", "move"], [[2], [0, 0, 1], [1, 1, 2], [0, 1, 1]])],
    gen=_ttt_ops,
    hints=[
        "Scanning the whole row, column and diagonals each move is O(n).",
        "Track a running count per row, per column and per diagonal: +1 for player 1, −1 for player 2.",
        "After a move, a count reaching ±n means that player has filled the line.",
    ],
    insight="Track signed line counts instead of the board.",
    time="O(1) per move", space="O(n)",
    pitfalls=["Updating the anti-diagonal for every cell instead of only when row + col == n − 1."],
)
class TicTacToe(_TicTacToeRef):
    pass


class _FreqStackRef:
    def __init__(self):
        self.items = []

    def push(self, val):
        self.items.append(val)

    def pop(self):
        c = Counter(self.items)
        top = max(c.values())
        for i in range(len(self.items) - 1, -1, -1):
            if c[self.items[i]] == top:
                return self.items.pop(i)


def _freq_ops(r):
    ops, args, size = ["FreqStack"], [[]], 0
    for _ in range(r.randint(4, 16)):
        if size and r.random() < 0.4:
            ops.append("pop"); args.append([]); size -= 1
        else:
            ops.append("push"); args.append([r.randint(1, 4)]); size += 1
    return ops, args


@problem(
    slug="maximum-frequency-stack", title="Maximum Frequency Stack", difficulty="Hard", pattern=KT, tags=["Hash Table", "Stack", "Design", "Ordered Set"],
    design=True, cls="FreqStack",
    starter="""class FreqStack:
    def __init__(self):
        pass

    def push(self, val: int) -> None:
        pass

    def pop(self) -> int:
        pass
""",
    desc="""Design a stack-like structure:

- `push(val)` adds a value.
- `pop()` removes and gives back the **most frequent** value currently in the stack. If several values are tied, it removes the one closest to the top (pushed most recently).

`pop` is only called on a non-empty structure.""",
    constraints=["0 ≤ val ≤ 10⁹", "at most 2 × 10⁴ calls"],
    samples=[(["FreqStack", "push", "push", "push", "push", "push", "push", "pop", "pop", "pop", "pop"], [[], [5], [7], [5], [7], [4], [5], [], [], [], []]),
             (["FreqStack", "push", "pop"], [[], [1], []])],
    gen=_freq_ops,
    hints=[
        "Track each value's current frequency.",
        "Keep a stack for every frequency level: when a value reaches frequency f, push it onto stack f.",
        "pop takes from the stack of the highest frequency, decrements that value's count, and lowers the max level if the stack empties.",
    ],
    insight="Stacks per frequency level give O(1) push and pop with recency tie-breaking.",
    time="O(1) per operation", space="O(n)",
    pitfalls=["Using a heap and losing the most-recent tie-break."],
)
class FreqStack(_FreqStackRef):
    pass


@problem(
    slug="first-unique-character-in-a-string", title="First Unique Character in a String", difficulty="Easy", pattern=KT,
    tags=["Hash Table", "String", "Queue", "Counting"],
    sig="firstUniqChar(self, s: str) -> int",
    desc="""Return the index of the first character in `s` that appears exactly once, or `-1` if there is none.""",
    constraints=["1 ≤ len(s) ≤ 10⁵", "lowercase letters"],
    samples=[("leetcode",), ("loveleetcode",), ("aabb",)],
    gen=lambda r: (r.word(r.randint(1, 10), "abcd"),),
    brute=lambda s: next((i for i, c in enumerate(s) if s.count(c) == 1), -1),
    hints=[
        "You need every character's total count before you can decide.",
        "Count all characters in one pass.",
        "In a second pass, find the first index whose character has count 1.",
    ],
    insight="Two passes: count, then find.",
    time="O(n)", space="O(alphabet)",
    pitfalls=["Calling count() inside the loop, which is O(n²)."],
)
def first_uniq_char(s):
    c = Counter(s)
    return next((i for i, ch in enumerate(s) if c[ch] == 1), -1)


@problem(
    slug="longest-palindrome", title="Longest Palindrome", difficulty="Easy", pattern=KT, tags=["Hash Table", "String", "Greedy"],
    sig="longestPalindrome(self, s: str) -> int",
    desc="""Return the length of the longest palindrome that can be built from the letters of `s` (each letter used at most as many times as it appears). Letters are case-sensitive.""",
    constraints=["1 ≤ len(s) ≤ 2000", "letters only"],
    samples=[("abccccdd",), ("a",)],
    gen=lambda r: (r.word(r.randint(1, 12), "abAB"),),
    brute=lambda s: sum(v // 2 * 2 for v in Counter(s).values()) + (1 if any(v % 2 for v in Counter(s).values()) else 0),
    hints=[
        "Pairs of equal letters can go on both sides.",
        "Use every letter's count rounded down to an even number.",
        "If any letter has an odd count, one extra letter can sit in the middle.",
    ],
    insight="Count pairs, plus one center if anything is left over.",
    time="O(n)", space="O(alphabet)",
    pitfalls=["Adding one for every odd count instead of only once."],
)
def longest_palindrome_build(s):
    odd = sum(v % 2 for v in Counter(s).values())
    return len(s) - odd + (1 if odd else 0)


@problem(
    slug="ransom-note", title="Ransom Note", difficulty="Easy", pattern=KT, tags=["Hash Table", "String", "Counting"],
    sig="canConstruct(self, ransomNote: str, magazine: str) -> bool",
    desc="""Return `true` if `ransomNote` can be built from the letters of `magazine`, using each magazine letter at most once.""",
    constraints=["1 ≤ len(ransomNote), len(magazine) ≤ 10⁵", "lowercase letters"],
    samples=[("a", "b"), ("aa", "ab"), ("aa", "aab")],
    gen=lambda r: (r.word(r.randint(1, 5), "abc"), r.word(r.randint(1, 9), "abc")),
    brute=lambda a, b: not (Counter(a) - Counter(b)),
    hints=[
        "Only letter counts matter.",
        "Count the magazine letters.",
        "Spend one count per note letter; fail if any count would go negative.",
    ],
    insight="Compare letter frequencies.",
    time="O(m + n)", space="O(alphabet)",
    pitfalls=["Checking only that each letter exists, not how many times."],
)
def can_construct(ransomNote, magazine):
    have = Counter(magazine)
    for c in ransomNote:
        if have[c] == 0:
            return False
        have[c] -= 1
    return True


@problem(
    slug="majority-element", title="Majority Element", difficulty="Easy", pattern=KT, tags=["Array", "Hash Table", "Divide and Conquer", "Sorting", "Counting"],
    sig="majorityElement(self, nums: list[int]) -> int",
    desc="""Return the element that appears more than `n / 2` times. It always exists. Try for O(n) time and O(1) space.""",
    constraints=["1 ≤ n ≤ 5 × 10⁴", "-10⁹ ≤ nums[i] ≤ 10⁹"],
    samples=[([3, 2, 3],), ([2, 2, 1, 1, 1, 2, 2],)],
    gen=lambda r: (lambda n, m: (r.sample([m] * (n // 2 + 1) + r.ints(n - n // 2 - 1, -5, 5), n),))(r.randint(1, 11), r.randint(-5, 5)),
    brute=lambda nums: Counter(nums).most_common(1)[0][0],
    hints=[
        "Pair each majority element with a different element and cancel them; the majority still survives.",
        "Track a candidate and a counter.",
        "When the counter is 0, take the current element as the candidate; add 1 for a match and subtract 1 otherwise.",
    ],
    insight="Boyer–Moore voting tracks just one candidate and one count.",
    time="O(n)", space="O(1)",
    pitfalls=["Assuming the most frequent element is a majority when none is guaranteed (here it always is)."],
)
def majority_element(nums):
    cand, cnt = None, 0
    for v in nums:
        if cnt == 0:
            cand = v
        cnt += 1 if v == cand else -1
    return cand


@problem(
    slug="number-of-good-pairs", title="Number of Good Pairs", difficulty="Easy", pattern=KT, tags=["Array", "Hash Table", "Math", "Counting"],
    sig="numIdenticalPairs(self, nums: list[int]) -> int",
    desc="""A pair `(i, j)` is good if `nums[i] == nums[j]` and `i < j`. Return the number of good pairs.""",
    constraints=["1 ≤ len(nums) ≤ 100", "1 ≤ nums[i] ≤ 100"],
    samples=[([1, 2, 3, 1, 1, 3],), ([1, 1, 1, 1],), ([1, 2, 3],)],
    gen=lambda r: (r.ints(r.randint(1, 12), 1, 4),),
    brute=lambda nums: sum(nums[i] == nums[j] for i in range(len(nums)) for j in range(i + 1, len(nums))),
    hints=[
        "When a value appears for the k-th time, it forms a pair with each of its k − 1 earlier copies.",
        "Keep a running count per value.",
        "Add the current count before incrementing it.",
    ],
    insight="Tracking counts turns pair counting into a single pass.",
    time="O(n)", space="O(n)",
    pitfalls=["Double-counting pairs (i, j) and (j, i)."],
)
def num_identical_pairs(nums):
    seen, total = Counter(), 0
    for v in nums:
        total += seen[v]
        seen[v] += 1
    return total


@problem(
    slug="rank-teams-by-votes", title="Rank Teams by Votes", difficulty="Medium", pattern=KT, tags=["Array", "Hash Table", "String", "Sorting", "Counting"],
    sig="rankTeams(self, votes: list[str]) -> str",
    desc="""Each vote is a string ranking all teams (uppercase letters) from first place to last. Order the teams by first-place votes; break ties with second-place votes, and so on. If teams are still tied after all positions, order them alphabetically. Return the teams as a string in final order.""",
    constraints=["1 ≤ len(votes) ≤ 1000", "1 ≤ len(votes[i]) ≤ 26", "all votes rank the same set of teams"],
    samples=[(["ABC", "ACB", "ABC", "ACB", "ACB"],), (["WXYZ", "XYZW"],), (["ZMNAGUEDSJYLBOPHRQICWFXTVK"],)],
    gen=lambda r: (lambda teams: (["".join(r.sample(teams, len(teams))) for _ in range(r.randint(1, 5))],))(r.sample("ABCDE", r.randint(1, 5))),
    hints=[
        "For each team, track how many votes it got at each position.",
        "Two teams compare by their position counts, from first place onward.",
        "Sort with the key (negated counts per position, then the letter).",
    ],
    insight="A per-team count vector makes ranking a single sort.",
    time="O(V · n + n² log n)", space="O(n²)",
    pitfalls=["Breaking final ties in reverse alphabetical order."],
)
def rank_teams(votes):
    n = len(votes[0])
    counts = {t: [0] * n for t in votes[0]}
    for v in votes:
        for i, t in enumerate(v):
            counts[t][i] += 1
    return "".join(sorted(counts, key=lambda t: ([-c for c in counts[t]], t)))


# ---------------------------------------------------------------- custom data structures


class _LRURef:
    def __init__(self, capacity):
        self.cap, self.d = capacity, OrderedDict()

    def get(self, key):
        if key not in self.d:
            return -1
        self.d.move_to_end(key)
        return self.d[key]

    def put(self, key, value):
        self.d[key] = value
        self.d.move_to_end(key)
        if len(self.d) > self.cap:
            self.d.popitem(last=False)


@problem(
    slug="lru-cache", title="LRU Cache", difficulty="Medium", pattern=CD, tags=["Hash Table", "Linked List", "Design", "Doubly-Linked List"],
    design=True, cls="LRUCache",
    starter="""class LRUCache:
    def __init__(self, capacity: int):
        pass

    def get(self, key: int) -> int:
        pass

    def put(self, key: int, value: int) -> None:
        pass
""",
    desc="""Design a Least Recently Used cache with a fixed `capacity`:

- `get(key)` gives the value, or `-1` if absent. It counts as a use.
- `put(key, value)` inserts or updates the key (also a use). If this makes the cache exceed its capacity, evict the least recently used key.

Both operations should run in O(1) on average.""",
    constraints=["1 ≤ capacity ≤ 3000", "0 ≤ key ≤ 10⁴", "at most 2 × 10⁵ calls"],
    samples=[(["LRUCache", "put", "put", "get", "put", "get", "put", "get", "get", "get"], [[2], [1, 1], [2, 2], [1], [3, 3], [2], [4, 4], [1], [3], [4]]),
             (["LRUCache", "put", "put", "get"], [[1], [2, 1], [2, 2], [2]])],
    gen=lambda r: _design_ops(r, "LRUCache", [r.randint(1, 3)], {"get": lambda r: [r.randint(0, 5)], "put": lambda r: [r.randint(0, 5), r.randint(0, 50)]}),
    hints=[
        "You need O(1) lookup by key and O(1) updates to the usage order.",
        "Combine a hash map (key → node) with a doubly linked list ordered by recency.",
        "On every use, move the node to the front; on overflow, remove the node at the back and delete its key from the map.",
    ],
    insight="Hash map + doubly linked list gives O(1) access and O(1) recency updates.",
    time="O(1) per operation", space="O(capacity)",
    pitfalls=["Forgetting that updating an existing key also makes it most recently used."],
)
class LRUCache(_LRURef):
    pass


class _LFURef:
    def __init__(self, capacity):
        self.cap, self.vals, self.freq, self.tick, self.used = capacity, {}, {}, 0, {}

    def _touch(self, key):
        self.tick += 1
        self.freq[key] = self.freq.get(key, 0) + 1
        self.used[key] = self.tick

    def get(self, key):
        if key not in self.vals:
            return -1
        self._touch(key)
        return self.vals[key]

    def put(self, key, value):
        if self.cap == 0:
            return
        if key not in self.vals and len(self.vals) == self.cap:
            victim = min(self.vals, key=lambda k: (self.freq[k], self.used[k]))
            for d in (self.vals, self.freq, self.used):
                del d[victim]
        self.vals[key] = value
        self._touch(key)


@problem(
    slug="lfu-cache", title="LFU Cache", difficulty="Hard", pattern=CD, tags=["Hash Table", "Linked List", "Design", "Doubly-Linked List"],
    design=True, cls="LFUCache",
    starter="""class LFUCache:
    def __init__(self, capacity: int):
        pass

    def get(self, key: int) -> int:
        pass

    def put(self, key: int, value: int) -> None:
        pass
""",
    desc="""Design a Least Frequently Used cache with a fixed `capacity`:

- `get(key)` gives the value, or `-1` if absent; a successful get increases the key's use count.
- `put(key, value)` inserts or updates the key (also increasing its use count; a new key starts at 1). If inserting a **new** key while the cache is full, first evict the key with the smallest use count; among ties, evict the least recently used one.

Both operations should run in O(1) on average.""",
    constraints=["1 ≤ capacity ≤ 10⁴", "0 ≤ key ≤ 10⁵", "at most 2 × 10⁵ calls"],
    samples=[(["LFUCache", "put", "put", "get", "put", "get", "get", "put", "get", "get", "get"], [[2], [1, 1], [2, 2], [1], [3, 3], [2], [3], [4, 4], [1], [3], [4]]),
             (["LFUCache", "put", "get", "put", "get", "get"], [[1], [1, 1], [1], [2, 2], [1], [2]])],
    gen=lambda r: _design_ops(r, "LFUCache", [r.randint(1, 3)], {"get": lambda r: [r.randint(0, 5)], "put": lambda r: [r.randint(0, 5), r.randint(0, 50)]}),
    hints=[
        "You need to find the least frequent key quickly, and among those the least recent.",
        "Group keys by frequency, with each group ordered by recency (an ordered dict or linked list), and track the current minimum frequency.",
        "On a use, move the key from group f to group f + 1 (bumping the minimum if group f empties). New keys go to group 1 and reset the minimum to 1.",
    ],
    insight="Frequency buckets of recency-ordered keys, plus a min-frequency pointer.",
    time="O(1) per operation", space="O(capacity)",
    pitfalls=["Evicting before checking whether the key already exists."],
)
class LFUCache(_LFURef):
    pass


class _SnapshotRef:
    def __init__(self, length):
        self.cur, self.snaps = [0] * length, []

    def set(self, index, val):
        self.cur[index] = val

    def snap(self):
        self.snaps.append(self.cur[:])
        return len(self.snaps) - 1

    def get(self, index, snap_id):
        return self.snaps[snap_id][index]


def _snap_ops(r):
    n = r.randint(1, 4)
    ops, args, snaps = ["SnapshotArray"], [[n]], 0
    for _ in range(r.randint(4, 14)):
        choice = r.choice(["set", "set", "snap"] + (["get"] if snaps else []))
        ops.append(choice)
        if choice == "set":
            args.append([r.randint(0, n - 1), r.randint(0, 9)])
        elif choice == "snap":
            args.append([])
            snaps += 1
        else:
            args.append([r.randint(0, n - 1), r.randint(0, snaps - 1)])
    return ops, args


@problem(
    slug="snapshot-array", title="Snapshot Array", difficulty="Medium", pattern=CD, tags=["Array", "Hash Table", "Binary Search", "Design"],
    design=True, cls="SnapshotArray",
    starter="""class SnapshotArray:
    def __init__(self, length: int):
        pass

    def set(self, index: int, val: int) -> None:
        pass

    def snap(self) -> int:
        pass

    def get(self, index: int, snap_id: int) -> int:
        pass
""",
    desc="""Design an array of `length` zeros that supports snapshots:

- `set(index, val)` sets an element.
- `snap()` takes a snapshot and gives back its id (the number of snaps taken before it, starting at 0).
- `get(index, snap_id)` gives the value at `index` as of snapshot `snap_id`.

Copying the whole array on every snap is too slow for the full constraints.""",
    constraints=["1 ≤ length ≤ 5 × 10⁴", "at most 5 × 10⁴ calls", "snap_id < number of snaps taken"],
    samples=[(["SnapshotArray", "set", "snap", "set", "get"], [[3], [0, 5], [], [0, 6], [0, 0]]),
             (["SnapshotArray", "snap", "snap", "get", "set", "snap", "get"], [[1], [], [], [0, 1], [0, 4], [], [0, 2]])],
    gen=_snap_ops,
    hints=[
        "Most elements don't change between snapshots.",
        "For each index, store only its history: a list of (snap_id, value) pairs recorded when it changes.",
        "To read, binary search the index's history for the last entry with snap_id ≤ the requested one.",
    ],
    insight="Per-index change logs plus binary search avoid copying the array.",
    time="O(log S) per get, O(1) otherwise", space="O(changes)",
    pitfalls=["Copying the full array on every snap."],
)
class SnapshotArray(_SnapshotRef):
    pass


class _TimeMapRef:
    def __init__(self):
        self.d = defaultdict(list)

    def set(self, key, value, timestamp):
        self.d[key].append((timestamp, value))

    def get(self, key, timestamp):
        best = ""
        for t, v in self.d[key]:
            if t <= timestamp:
                best = v
        return best


def _time_ops(r):
    ops, args, t = ["TimeMap"], [[]], 0
    for _ in range(r.randint(4, 14)):
        if r.random() < 0.5:
            t += r.randint(1, 3)
            ops.append("set")
            args.append([r.choice(["a", "b"]), r.word(2, "xyz"), t])
        else:
            ops.append("get")
            args.append([r.choice(["a", "b", "c"]), r.randint(0, t + 2)])
    return ops, args


@problem(
    slug="time-based-key-value-store", title="Time Based Key-Value Store", difficulty="Medium", pattern=CD,
    tags=["Hash Table", "String", "Binary Search", "Design"],
    design=True, cls="TimeMap",
    starter="""class TimeMap:
    def __init__(self):
        pass

    def set(self, key: str, value: str, timestamp: int) -> None:
        pass

    def get(self, key: str, timestamp: int) -> str:
        pass
""",
    desc="""Design a key-value store that keeps every version of a key:

- `set(key, value, timestamp)` stores `value` for `key` at time `timestamp`. Timestamps across all `set` calls are strictly increasing.
- `get(key, timestamp)` gives the value from the latest `set` of `key` with time ≤ `timestamp`, or `""` if there is none.""",
    constraints=["1 ≤ timestamp ≤ 10⁷", "at most 2 × 10⁵ calls"],
    samples=[(["TimeMap", "set", "get", "get", "set", "get", "get"], [[], ["foo", "bar", 1], ["foo", 1], ["foo", 3], ["foo", "bar2", 4], ["foo", 4], ["foo", 5]]),
             (["TimeMap", "get", "set", "get"], [[], ["k", 1], ["k", "v", 5], ["k", 4]])],
    gen=_time_ops,
    hints=[
        "Each key's history is appended in increasing time order.",
        "So every key's list of (timestamp, value) is already sorted.",
        "Binary search for the last timestamp ≤ the query.",
    ],
    insight="Sorted per-key histories make each lookup a binary search.",
    time="O(1) set, O(log n) get", space="O(n)",
    pitfalls=["Scanning a key's whole history on every get."],
)
class TimeMap(_TimeMapRef):
    pass


class _BrowserRef:
    def __init__(self, homepage):
        self.pages, self.i = [homepage], 0

    def visit(self, url):
        self.pages = self.pages[:self.i + 1] + [url]
        self.i += 1

    def back(self, steps):
        self.i = max(0, self.i - steps)
        return self.pages[self.i]

    def forward(self, steps):
        self.i = min(len(self.pages) - 1, self.i + steps)
        return self.pages[self.i]


@problem(
    slug="design-browser-history", title="Design Browser History", difficulty="Medium", pattern=CD,
    tags=["Array", "Linked List", "Stack", "Design", "Doubly-Linked List", "Data Stream"],
    design=True, cls="BrowserHistory",
    starter="""class BrowserHistory:
    def __init__(self, homepage: str):
        pass

    def visit(self, url: str) -> None:
        pass

    def back(self, steps: int) -> str:
        pass

    def forward(self, steps: int) -> str:
        pass
""",
    desc="""Design a browser tab's history, starting at `homepage`:

- `visit(url)` opens `url` from the current page and clears all forward history.
- `back(steps)` moves back up to `steps` pages (stopping at the first page) and gives the current url.
- `forward(steps)` moves forward up to `steps` pages (stopping at the last page) and gives the current url.""",
    constraints=["1 ≤ steps ≤ 100", "at most 5000 calls"],
    samples=[(["BrowserHistory", "visit", "visit", "visit", "back", "back", "forward", "visit", "forward", "back", "back"],
              [["leetcode.com"], ["google.com"], ["facebook.com"], ["youtube.com"], [1], [1], [1], ["linkedin.com"], [2], [2], [7]]),
             (["BrowserHistory", "back", "forward"], [["a.com"], [3], [2]])],
    gen=lambda r: _design_ops(r, "BrowserHistory", ["home.com"], {"visit": lambda r: [r.word(1, "abc") + ".com"], "back": lambda r: [r.randint(1, 3)], "forward": lambda r: [r.randint(1, 3)]}),
    hints=[
        "Keep the pages in a list with a pointer to the current page.",
        "back and forward only move the pointer, clamped to the list bounds.",
        "visit overwrites the slot after the pointer and forgets everything beyond it (track a separate \"last valid index\" to do this in O(1)).",
    ],
    insight="An array plus current and last-valid indices gives O(1) for all operations.",
    time="O(1) per operation", space="O(n)",
    pitfalls=["Keeping forward history after a visit."],
)
class BrowserHistory(_BrowserRef):
    pass


class _HitRef:
    def __init__(self):
        self.hits = []

    def hit(self, timestamp):
        self.hits.append(timestamp)

    def getHits(self, timestamp):
        return sum(1 for t in self.hits if timestamp - 300 < t <= timestamp)


def _hit_ops(r):
    ops, args, t = ["HitCounter"], [[]], 1
    for _ in range(r.randint(4, 14)):
        t += r.choice([0, 1, 50, 120, 299, 300])
        ops.append(r.choice(["hit", "hit", "getHits"]))
        args.append([t])
    return ops, args


@problem(
    slug="design-hit-counter", title="Design Hit Counter", difficulty="Medium", pattern=CD,
    tags=["Array", "Binary Search", "Design", "Queue", "Data Stream"],
    design=True, cls="HitCounter",
    starter="""class HitCounter:
    def __init__(self):
        pass

    def hit(self, timestamp: int) -> None:
        pass

    def getHits(self, timestamp: int) -> int:
        pass
""",
    desc="""Count hits over the past 5 minutes (300 seconds). Calls arrive in non-decreasing timestamp order (seconds):

- `hit(timestamp)` records a hit (several hits may share a timestamp).
- `getHits(timestamp)` gives the number of hits in the window `(timestamp − 300, timestamp]`.""",
    constraints=["1 ≤ timestamp ≤ 2 × 10⁹", "timestamps never decrease", "at most 300 calls"],
    samples=[(["HitCounter", "hit", "hit", "hit", "getHits", "hit", "getHits", "getHits"], [[], [1], [2], [3], [4], [300], [300], [301]]),
             (["HitCounter", "getHits"], [[], [5]])],
    gen=_hit_ops,
    hints=[
        "Old hits never come back into the window.",
        "Keep hit timestamps in a queue.",
        "On getHits, pop timestamps ≤ timestamp − 300 from the front, then report the queue size.",
    ],
    insight="A queue of timestamps trimmed from the front implements a sliding time window.",
    time="Amortized O(1)", space="O(hits in window)",
    pitfalls=["Using < instead of ≤ at the window's old edge."],
)
class HitCounter(_HitRef):
    pass


class _UndergroundRef:
    def __init__(self):
        self.inside, self.trips = {}, defaultdict(list)

    def checkIn(self, id, stationName, t):
        self.inside[id] = (stationName, t)

    def checkOut(self, id, stationName, t):
        s, t0 = self.inside.pop(id)
        self.trips[s, stationName].append(t - t0)

    def getAverageTime(self, startStation, endStation):
        v = self.trips[startStation, endStation]
        return sum(v) / len(v)


def _underground_ops(r):
    ops, args, t, inside = ["UndergroundSystem"], [[]], 0, {}
    done = set()
    for _ in range(r.randint(6, 16)):
        t += r.randint(1, 5)
        choice = r.random()
        free = [i for i in range(1, 4) if i not in inside]
        if inside and choice < 0.4:
            i = r.choice(sorted(inside))
            end = r.choice("XYZ")
            ops.append("checkOut"); args.append([i, end, t])
            done.add((inside.pop(i), end))
        elif done and choice < 0.6:
            s, e = r.choice(sorted(done))
            ops.append("getAverageTime"); args.append([s, e])
        elif free:
            i = r.choice(free)
            s = r.choice("ABC")
            inside[i] = s
            ops.append("checkIn"); args.append([i, s, t])
    return ops, args


@problem(
    slug="design-underground-system", title="Design Underground System", difficulty="Medium", pattern=CD, tags=["Hash Table", "String", "Design"],
    design=True, cls="UndergroundSystem", compare="approx",
    starter="""class UndergroundSystem:
    def __init__(self):
        pass

    def checkIn(self, id: int, stationName: str, t: int) -> None:
        pass

    def checkOut(self, id: int, stationName: str, t: int) -> None:
        pass

    def getAverageTime(self, startStation: str, endStation: str) -> float:
        pass
""",
    desc="""Track travel times between stations:

- `checkIn(id, stationName, t)`: card `id` enters a station at time `t`.
- `checkOut(id, stationName, t)`: card `id` leaves at time `t`.
- `getAverageTime(startStation, endStation)`: the average time of all completed trips that went directly from `startStation` to `endStation`.

Calls are consistent (a card checks out only after checking in), and `getAverageTime` is only asked about routes with at least one trip. Answers within 10⁻⁵ are accepted.""",
    constraints=["at most 2 × 10⁴ calls", "1 ≤ t ≤ 10⁶"],
    samples=[(["UndergroundSystem", "checkIn", "checkIn", "checkOut", "checkOut", "getAverageTime", "checkIn", "checkOut", "getAverageTime"],
              [[], [45, "Leyton", 3], [32, "Paradise", 8], [45, "Waterloo", 15], [32, "Cambridge", 22], ["Paradise", "Cambridge"], [10, "Leyton", 24], [10, "Waterloo", 38], ["Leyton", "Waterloo"]]),
             (["UndergroundSystem", "checkIn", "checkOut", "getAverageTime"], [[], [1, "A", 3], [1, "B", 8], ["A", "B"]])],
    gen=_underground_ops,
    hints=[
        "Remember where and when each card checked in.",
        "On checkout, the trip belongs to the (start, end) route.",
        "Keep a running (total time, count) per route so averages are O(1).",
    ],
    insight="Two hash maps: open trips by card, and totals by route.",
    time="O(1) per call", space="O(cards + routes)",
    pitfalls=["Mixing up the direction of a route: A → B differs from B → A."],
)
class UndergroundSystem(_UndergroundRef):
    pass


class _RangeModuleRef:
    def __init__(self):
        self.covered = set()

    def addRange(self, left, right):
        self.covered |= set(range(left, right))

    def queryRange(self, left, right):
        return all(x in self.covered for x in range(left, right))

    def removeRange(self, left, right):
        self.covered -= set(range(left, right))


def _range_ops(r):
    def lr(r):
        a = r.randint(1, 15)
        return [a, a + r.randint(1, 6)]
    return _design_ops(r, "RangeModule", [], {"addRange": lr, "queryRange": lr, "removeRange": lr})


@problem(
    slug="range-module", title="Range Module", difficulty="Hard", pattern=CD, tags=["Design", "Segment Tree", "Ordered Set"],
    design=True, cls="RangeModule",
    starter="""class RangeModule:
    def __init__(self):
        pass

    def addRange(self, left: int, right: int) -> None:
        pass

    def queryRange(self, left: int, right: int) -> bool:
        pass

    def removeRange(self, left: int, right: int) -> None:
        pass
""",
    desc="""Track a set of numbers using half-open intervals `[left, right)`:

- `addRange(left, right)` starts tracking every real number in `[left, right)`.
- `queryRange(left, right)` reports whether every number in `[left, right)` is currently tracked.
- `removeRange(left, right)` stops tracking every number in `[left, right)`.""",
    constraints=["1 ≤ left < right ≤ 10⁹", "at most 10⁴ calls"],
    samples=[(["RangeModule", "addRange", "removeRange", "queryRange", "queryRange", "queryRange"], [[], [10, 20], [14, 16], [10, 14], [13, 15], [16, 17]]),
             (["RangeModule", "queryRange", "addRange", "queryRange"], [[], [1, 2], [1, 5], [2, 4]])],
    gen=_range_ops,
    hints=[
        "Keep the tracked numbers as a sorted list of disjoint intervals.",
        "Binary search finds the intervals that overlap [left, right).",
        "add merges the overlapping intervals into one; remove cuts them and keeps any leftover pieces; query checks that one interval covers the whole range.",
    ],
    insight="A sorted list of disjoint intervals with binary search handles all three operations.",
    time="O(n) per update, O(log n) per query", space="O(n)",
    pitfalls=["Treating ranges as closed, which merges [1, 2) and [3, 4) incorrectly or misses [1, 2) + [2, 3) adjacency."],
)
class RangeModule(_RangeModuleRef):
    pass


def _big_ops(r, cls, ctor, makers, n):
    return _design_ops(r, cls, ctor, makers, (n, n))


def _big_logger(r):
    ops, args, t = ["Logger"], [[]], 0
    for _ in range(3000):
        t += r.randint(0, 3)
        ops.append("shouldPrintMessage")
        args.append([t, "m%d" % r.randint(0, 30)])
    return ops, args


def _big_freq_ops(r):
    ops, args, size = ["FreqStack"], [[]], 0
    for _ in range(6000):
        if size and r.random() < 0.4:
            ops.append("pop"); args.append([]); size -= 1
        else:
            ops.append("push"); args.append([r.randint(1, 50)]); size += 1
    return ops, args


def _big_ttt(r):
    n = 100
    ops, args, ref = ["TicTacToe"], [[n]], _TicTacToeRef(n)
    cells = [(i, j) for i in range(n) for j in range(n)]
    r.shuffle(cells)
    for k, (i, j) in enumerate(cells[:5000]):
        p = 1 + k % 2
        ops.append("move"); args.append([i, j, p])
        if ref.move(i, j, p):
            break
    return ops, args


def _big_snap_ops(r):
    n = 5000
    ops, args, snaps = ["SnapshotArray"], [[n]], 0
    for _ in range(6000):
        choice = r.choice(["set", "set", "snap"] + (["get", "get"] if snaps else []))
        ops.append(choice)
        if choice == "set":
            args.append([r.randint(0, n - 1), r.randint(0, 10**6)])
        elif choice == "snap":
            args.append([]); snaps += 1
        else:
            args.append([r.randint(0, n - 1), r.randint(0, snaps - 1)])
    return ops, args


def _big_time_ops(r):
    ops, args, t = ["TimeMap"], [[]], 0
    for _ in range(5000):
        if r.random() < 0.5:
            t += r.randint(1, 5)
            ops.append("set"); args.append(["k%d" % r.randint(0, 9), r.word(3, "xyz"), t])
        else:
            ops.append("get"); args.append(["k%d" % r.randint(0, 10), r.randint(0, t + 5)])
    return ops, args


def _big_hits(r):
    ops, args, t = ["HitCounter"], [[]], 1
    for _ in range(300):
        t += r.choice([0, 1, 2, 7, 150, 301])
        ops.append(r.choice(["hit", "hit", "getHits"])); args.append([t])
    return ops, args


def _big_underground(r):
    ops, args, t, inside, done = ["UndergroundSystem"], [[]], 0, {}, set()
    for _ in range(4000):
        t += r.randint(1, 3)
        free = [i for i in range(1, 200) if i not in inside]
        roll = r.random()
        if inside and roll < 0.4:
            i = r.choice(sorted(inside))
            end = "S%d" % r.randint(0, 9)
            ops.append("checkOut"); args.append([i, end, t])
            done.add((inside.pop(i), end))
        elif done and roll < 0.6:
            s, e = r.choice(sorted(done))
            ops.append("getAverageTime"); args.append([s, e])
        elif free:
            i = r.choice(free)
            s = "S%d" % r.randint(0, 9)
            inside[i] = s
            ops.append("checkIn"); args.append([i, s, t])
    return ops, args


def _big_range_ops(r):
    def lr(r):
        a = r.randint(1, 1000)
        return [a, a + r.randint(1, 50)]
    return _big_ops(r, "RangeModule", [], {"addRange": lr, "queryRange": lr, "removeRange": lr}, 1500)


EXTRA = {
    "design-hashmap": {
        "edge": [(["MyHashMap", "put", "put", "get"], [[], [0, 0], [0, 1000000], [0]]),
                 (["MyHashMap", "remove", "get"], [[], [5], [5]]),
                 (["MyHashMap", "put", "remove", "put", "get"], [[], [1000000, 1], [1000000], [1000000, 2], [1000000]])],
        "large": [lambda r: _big_ops(r, "MyHashMap", [], {"put": lambda r: [r.randint(0, 10**6), r.randint(0, 10**6)], "get": lambda r: [r.randint(0, 10**6)], "remove": lambda r: [r.randint(0, 10**6)]}, 6000),
                  lambda r: _big_ops(r, "MyHashMap", [], {"put": lambda r: [r.randint(0, 200) * 1000, r.randint(0, 99)], "get": lambda r: [r.randint(0, 200) * 1000], "remove": lambda r: [r.randint(0, 200) * 1000]}, 6000)],
    },
    "fraction-to-recurring-decimal": {"edge": [(0, 1), (1, 3), (22, 7), (1, 333), (1, 214748364), (2147483647, 1), (-1, -2147483648)]},
    "logger-rate-limiter": {
        "edge": [(["Logger", "shouldPrintMessage", "shouldPrintMessage"], [[], [0, "a"], [10, "a"]]),
                 (["Logger", "shouldPrintMessage", "shouldPrintMessage", "shouldPrintMessage"], [[], [0, "a"], [9, "a"], [10, "a"]]),
                 (["Logger", "shouldPrintMessage", "shouldPrintMessage"], [[], [1000000000, "x"], [1000000000, "y"]])],
        "large": [_big_logger],
    },
    "isomorphic-strings": {"edge": [("a", "a"), ("ab", "aa"), ("aa", "ab"), ("abcd", "dcba"), ("13", "42")], "large": [lambda r: (lambda s: (s, s.translate(str.maketrans("abcdefgh", "hgfedcba"))))(r.word(40000, "abcdefgh"))]},
    "word-pattern": {"edge": [("a", "dog"), ("a", "dog dog"), ("ab", "dog dog"), ("abc", "b c a"), ("aaa", "aa aa aa")]},
    "contains-duplicate-ii": {
        "edge": [([1], 0), ([1, 1], 0), ([1, 1], 1), ([99, 99], 2), ([1, 2, 1], 1)],
        "large": [lambda r: (list(range(15000)), 10000), lambda r: (r.ints(10000, 0, 10**9), 10000)],
    },
    "bulls-and-cows": {"edge": [("1", "0"), ("1", "1"), ("11", "11"), ("1122", "2211"), ("1234", "0111")], "large": [lambda r: (r.word(1000, "0123456789"), r.word(1000, "0123456789"))]},
    "jewels-and-stones": {"edge": [("a", "A"), ("abc", "abc"), ("z", "z" * 50), ("Aa", "b")]},
    "palindrome-permutation": {"edge": [("a",), ("ab",), ("aab",), ("aabbccd",), ("aabbccdd",)], "large": [lambda r: (r.word(5000, "abcdefghijklmnopqrstuvwxyz"),)]},
    "valid-anagram": {"edge": [("a", "a"), ("a", "b"), ("ab", "a"), ("aacc", "ccac")], "large": [lambda r: (lambda s: (s, "".join(r.sample(s, len(s)))))(r.word(40000, "abcdefghijklmnopqrstuvwxyz"))]},
    "group-anagrams": {
        "edge": [(["", ""],), (["a", "b"],), (["ab", "ba", "abc"],), (["ddddddddddg", "dgggggggggg"],)],
        "large": [lambda r: ([r.word(r.randint(1, 6), "abc") for _ in range(6000)],)],
    },
    "design-tic-tac-toe": {
        "edge": [(["TicTacToe", "move", "move", "move", "move"], [[2], [0, 1, 1], [1, 1, 2], [1, 0, 1], [0, 0, 2]]),
                 (["TicTacToe", "move", "move", "move", "move", "move"], [[3], [0, 2, 1], [1, 1, 2], [1, 1 - 1, 1], [2, 0, 2], [0, 0, 1]]),
                 (["TicTacToe", "move", "move", "move", "move", "move"], [[3], [0, 0, 1], [1, 0, 2], [0, 1, 1], [1, 1, 2], [0, 2, 1]])],
        "large": [_big_ttt],
    },
    "maximum-frequency-stack": {
        "edge": [(["FreqStack", "push", "push", "pop", "pop"], [[], [1], [2], [], []]),
                 (["FreqStack", "push", "push", "push", "pop", "pop", "pop"], [[], [4], [4], [4], [], [], []]),
                 (["FreqStack", "push", "push", "push", "push", "pop", "pop"], [[], [1], [2], [1], [2], [], []])],
        "large": [_big_freq_ops],
    },
    "first-unique-character-in-a-string": {"edge": [("a",), ("aa",), ("ab",), ("aabbc",)], "large": [lambda r: ("ab" * 30000 + "c",)]},
    "longest-palindrome": {"edge": [("a",), ("Aa",), ("bb",), ("ccc",), ("abcABC",)]},
    "ransom-note": {"edge": [("a", "a"), ("aa", "a"), ("abc", "cba"), ("z", "abc")], "large": [lambda r: (r.word(20000, "abc"), r.word(30000, "abc"))]},
    "majority-element": {
        "edge": [([1],), ([2, 2],), ([1, 2, 2],), ([-1000000000, -1000000000, 1000000000],)],
        "large": [lambda r: (r.sample([7] * 8001 + r.ints(7999, -10**9, 10**9), 16000),)],
    },
    "number-of-good-pairs": {"edge": [([1],), ([1, 1],), ([100] * 100,), ([1, 2, 1, 2],)]},
    "rank-teams-by-votes": {"edge": [(["A"],), (["AB", "BA"],), (["BCA", "CAB", "CBA", "ABC", "ACB", "BAC"],), (["ABC", "ABC"],)],
                            "large": [lambda r: (["".join(r.sample("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 26)) for _ in range(1000)],)]},
    "lru-cache": {
        "edge": [(["LRUCache", "put", "get", "put", "get", "get"], [[1], [1, 1], [1], [2, 2], [1], [2]]),
                 (["LRUCache", "put", "put", "put", "get"], [[2], [1, 1], [1, 5], [2, 2], [1]]),
                 (["LRUCache", "get"], [[3], [0]]),
                 (["LRUCache", "put", "put", "get", "put", "get", "get"], [[2], [2, 1], [1, 1], [2], [4, 1], [1], [2]])],
        "large": [lambda r: _big_ops(r, "LRUCache", [500], {"get": lambda r: [r.randint(0, 1000)], "put": lambda r: [r.randint(0, 1000), r.randint(0, 10**4)]}, 6000)],
    },
    "lfu-cache": {
        "edge": [(["LFUCache", "put", "put", "get", "put", "get", "get"], [[2], [1, 1], [2, 2], [1], [3, 3], [2], [3]]),
                 (["LFUCache", "put", "put", "put", "get"], [[1], [1, 1], [1, 2], [2, 3], [1]]),
                 (["LFUCache", "get", "put", "get"], [[1], [5], [5, 5], [5]])],
        "large": [lambda r: _big_ops(r, "LFUCache", [100], {"get": lambda r: [r.randint(0, 300)], "put": lambda r: [r.randint(0, 300), r.randint(0, 10**4)]}, 6000)],
    },
    "snapshot-array": {
        "edge": [(["SnapshotArray", "snap", "get"], [[1], [], [0, 0]]),
                 (["SnapshotArray", "set", "set", "snap", "get"], [[1], [0, 1], [0, 2], [], [0, 0]]),
                 (["SnapshotArray", "snap", "snap", "set", "snap", "get", "get"], [[2], [], [], [1, 9], [], [1, 1], [1, 2]])],
        "large": [_big_snap_ops],
    },
    "time-based-key-value-store": {
        "edge": [(["TimeMap", "set", "get"], [[], ["a", "x", 5], ["a", 4]]),
                 (["TimeMap", "set", "set", "get", "get"], [[], ["a", "x", 1], ["a", "y", 2], ["a", 10000000], ["a", 1]]),
                 (["TimeMap", "set", "get"], [[], ["a", "x", 1], ["b", 1]])],
        "large": [_big_time_ops],
    },
    "design-browser-history": {
        "edge": [(["BrowserHistory", "visit", "back", "forward", "forward"], [["a.com"], ["b.com"], [100], [1], [100]]),
                 (["BrowserHistory", "visit", "visit", "back", "visit", "forward"], [["a.com"], ["b.com"], ["c.com"], [1], ["d.com"], [1]])],
        "large": [lambda r: _big_ops(r, "BrowserHistory", ["home.com"], {"visit": lambda r: ["p%d.com" % r.randint(0, 99)], "back": lambda r: [r.randint(1, 100)], "forward": lambda r: [r.randint(1, 100)]}, 4000)],
    },
    "design-hit-counter": {
        "edge": [(["HitCounter", "hit", "getHits"], [[], [1], [301]]),
                 (["HitCounter", "hit", "getHits"], [[], [1], [300]]),
                 (["HitCounter", "hit", "hit", "hit", "getHits"], [[], [5], [5], [5], [5]])],
        "large": [_big_hits],
    },
    "design-underground-system": {
        "edge": [(["UndergroundSystem", "checkIn", "checkOut", "checkIn", "checkOut", "getAverageTime"], [[], [1, "A", 1], [1, "B", 4], [1, "B", 5], [1, "A", 6], ["A", "B"]]),
                 (["UndergroundSystem", "checkIn", "checkIn", "checkOut", "checkOut", "getAverageTime"], [[], [1, "A", 1], [2, "A", 2], [2, "B", 4], [1, "B", 9], ["A", "B"]])],
        "large": [_big_underground],
    },
    "range-module": {
        "edge": [(["RangeModule", "addRange", "queryRange", "queryRange"], [[], [1, 2], [1, 2], [1, 3]]),
                 (["RangeModule", "addRange", "addRange", "queryRange"], [[], [1, 2], [2, 3], [1, 3]]),
                 (["RangeModule", "addRange", "removeRange", "queryRange", "queryRange"], [[], [1, 10], [5, 6], [1, 5], [6, 10]])],
        "large": [_big_range_ops],
    },
}
