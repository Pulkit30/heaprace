from fractions import Fraction
from itertools import combinations
from math import gcd

from catalog_lib import problem

TR = "tries"
BT = "bit-manipulation"
MG = "math-geometry"


class _TrieRef:
    def __init__(self):
        self.words = set()

    def insert(self, word):
        self.words.add(word)

    def search(self, word):
        return word in self.words

    def startsWith(self, prefix):
        return any(w.startswith(prefix) for w in self.words)


def _trie_ops(r):
    ops, args = ["Trie"], [[]]
    for _ in range(r.randint(3, 14)):
        ops.append(r.choice(["insert", "insert", "search", "startsWith"]))
        args.append([r.word(r.randint(1, 4), "ab")])
    return ops, args


@problem(
    slug="implement-trie-prefix-tree", title="Implement Trie (Prefix Tree)", difficulty="Medium", pattern=TR,
    tags=["Hash Table", "String", "Design", "Trie"],
    design=True, cls="Trie",
    starter="""class Trie:
    def __init__(self):
        pass

    def insert(self, word: str) -> None:
        pass

    def search(self, word: str) -> bool:
        pass

    def startsWith(self, prefix: str) -> bool:
        pass
""",
    desc="""Implement a trie with:

- `insert(word)`: add a word.
- `search(word)`: is this exact word stored?
- `startsWith(prefix)`: does any stored word start with this prefix?""",
    constraints=["1 ≤ len(word), len(prefix) ≤ 2000", "lowercase letters", "at most 3 × 10⁴ calls"],
    samples=[(["Trie", "insert", "search", "search", "startsWith", "insert", "search"], [[], ["apple"], ["apple"], ["app"], ["app"], ["app"], ["app"]]),
             (["Trie", "search", "startsWith"], [[], ["a"], ["a"]])],
    gen=_trie_ops,
    hints=[
        "Store words as paths of characters from a root node.",
        "Each node maps a character to a child node, plus a flag marking where a word ends.",
        "search follows the path and checks the end flag; startsWith only needs the path to exist.",
    ],
    insight="A trie shares prefixes, making prefix queries O(length).",
    time="O(L) per operation", space="O(total characters)",
    pitfalls=["Forgetting the end-of-word flag, so prefixes look like whole words."],
)
class Trie(_TrieRef):
    pass


class _WordDictRef:
    def __init__(self):
        self.words = set()

    def addWord(self, word):
        self.words.add(word)

    def search(self, word):
        return any(len(w) == len(word) and all(p in (".", c) for p, c in zip(word, w)) for w in self.words)


def _wd_ops(r):
    ops, args = ["WordDictionary"], [[]]
    for _ in range(r.randint(3, 14)):
        op = r.choice(["addWord", "addWord", "search", "search"])
        ops.append(op)
        args.append([r.word(r.randint(1, 3), "ab" + (".." if op == "search" else ""))])
    return ops, args


@problem(
    slug="design-add-and-search-words-data-structure", title="Design Add and Search Words Data Structure", difficulty="Medium", pattern=TR,
    tags=["String", "Depth-First Search", "Design", "Trie"],
    design=True, cls="WordDictionary",
    starter="""class WordDictionary:
    def __init__(self):
        pass

    def addWord(self, word: str) -> None:
        pass

    def search(self, word: str) -> bool:
        pass
""",
    desc="""Design `WordDictionary`:

- `addWord(word)` stores a word.
- `search(word)` reports whether any stored word matches `word`, where `'.'` matches any single letter.""",
    constraints=["1 ≤ len(word) ≤ 25", "search words have at most 2 dots", "at most 10⁴ calls"],
    samples=[(["WordDictionary", "addWord", "addWord", "addWord", "search", "search", "search", "search"],
              [[], ["bad"], ["dad"], ["mad"], ["pad"], ["bad"], [".ad"], ["b.."]]),
             (["WordDictionary", "search", "addWord", "search"], [[], ["."], ["a"], ["."]])],
    gen=_wd_ops,
    hints=[
        "Store the words in a trie.",
        "A normal letter follows one child; a '.' could follow any child.",
        "Search recursively: on '.', try every child and succeed if any branch matches to the end of a word.",
    ],
    insight="A trie plus DFS branching on wildcards.",
    time="O(L) to add; O(26ᵈ · L) to search with d dots", space="O(total characters)",
    pitfalls=["Matching a prefix of a longer word as a full match."],
)
class WordDictionary(_WordDictRef):
    pass


def _suggest_brute(products, searchWord):
    return [sorted(p for p in products if p.startswith(searchWord[:i]))[:3] for i in range(1, len(searchWord) + 1)]


@problem(
    slug="search-suggestions-system", title="Search Suggestions System", difficulty="Medium", pattern=TR,
    tags=["Array", "String", "Binary Search", "Trie", "Sorting", "Heap"],
    sig="suggestedProducts(self, products: list[str], searchWord: str) -> list[list[str]]",
    desc="""As each character of `searchWord` is typed, suggest up to three products that start with the typed prefix, choosing the lexicographically smallest ones. Return the list of suggestions after each character.""",
    constraints=["1 ≤ len(products) ≤ 1000", "products are distinct", "1 ≤ len(searchWord) ≤ 1000"],
    samples=[(["mobile", "mouse", "moneypot", "monitor", "mousepad"], "mouse"), (["havana"], "havana"), (["bags", "baggage", "banner", "box", "cloths"], "bags")],
    gen=lambda r: (sorted({r.word(r.randint(1, 4), "abc") for _ in range(r.randint(1, 10))}), r.word(r.randint(1, 4), "abc")),
    brute=_suggest_brute,
    hints=[
        "Sorting the products puts every prefix's matches in one contiguous, ordered block.",
        "For each prefix, binary search the first product ≥ the prefix.",
        "Take up to three products from there that still start with the prefix. (A trie storing the 3 best words per node also works.)",
    ],
    insight="Sorted products + binary search make each prefix query fast.",
    time="O(n log n + L log n)", space="O(1) besides the output",
    pitfalls=["Returning more than three suggestions."],
)
def suggested_products(products, searchWord):
    from bisect import bisect_left
    products = sorted(products)
    out, prefix = [], ""
    for c in searchWord:
        prefix += c
        i = bisect_left(products, prefix)
        out.append([p for p in products[i:i + 3] if p.startswith(prefix)])
    return out


def _ws2_input(r):
    m, n = r.randint(1, 4), r.randint(1, 4)
    board = [[r.choice("abc") for _ in range(n)] for _ in range(m)]
    return board, sorted({r.word(r.randint(1, 4), "abc") for _ in range(r.randint(1, 8))})


def _exist(board, word):
    m, n = len(board), len(board[0])

    def go(i, j, k, seen):
        if k == len(word):
            return True
        if not (0 <= i < m and 0 <= j < n) or (i, j) in seen or board[i][j] != word[k]:
            return False
        seen.add((i, j))
        ok = any(go(i + a, j + b, k + 1, seen) for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        seen.discard((i, j))
        return ok

    return any(go(i, j, 0, set()) for i in range(m) for j in range(n))


@problem(
    slug="word-search-ii", title="Word Search II", difficulty="Hard", pattern=TR, tags=["Array", "String", "Backtracking", "Trie", "Matrix"],
    sig="findWords(self, board: list[list[str]], words: list[str]) -> list[str]", compare="unordered",
    desc="""Return every word from `words` that can be traced on `board` through horizontally or vertically adjacent cells, using each cell at most once per word. Return them in any order.""",
    constraints=["1 ≤ m, n ≤ 12", "1 ≤ len(words) ≤ 3 × 10⁴", "words are distinct, length ≤ 10"],
    samples=[([["o", "a", "a", "n"], ["e", "t", "a", "e"], ["i", "h", "k", "r"], ["i", "f", "l", "v"]], ["oath", "pea", "eat", "rain"]),
             ([["a", "b"], ["c", "d"]], ["abcb"])],
    gen=_ws2_input,
    brute=lambda board, words: [w for w in words if _exist(board, w)],
    hints=[
        "Searching for each word separately repeats work for shared prefixes.",
        "Put all words in a trie and search the board once, walking the trie as you walk the grid.",
        "Stop exploring when the current path isn't a trie prefix; when a node ends a word, record it (and remove it to avoid duplicates).",
    ],
    insight="A trie lets one backtracking search find all words at once.",
    time="O(m·n·4·3^(L−1))", space="O(total characters)",
    pitfalls=["Reporting the same word twice when it can be traced in two ways."],
)
def find_words(board, words):
    root = {}
    for w in words:
        node = root
        for c in w:
            node = node.setdefault(c, {})
        node["$"] = w
    m, n, out = len(board), len(board[0]), []

    def go(i, j, node):
        c = board[i][j]
        if c not in node:
            return
        nxt = node[c]
        if "$" in nxt:
            out.append(nxt.pop("$"))
        board[i][j] = "#"
        for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            x, y = i + a, j + b
            if 0 <= x < m and 0 <= y < n and board[x][y] != "#":
                go(x, y, nxt)
        board[i][j] = c

    for i in range(m):
        for j in range(n):
            go(i, j, root)
    return out


@problem(
    slug="longest-word-in-dictionary", title="Longest Word in Dictionary", difficulty="Medium", pattern=TR,
    tags=["Array", "Hash Table", "String", "Trie", "Sorting"],
    sig="longestWord(self, words: list[str]) -> str",
    desc="""Return the longest word in `words` that can be built one character at a time by other words in `words` (every prefix of it must also be in the list). If several are tied, return the lexicographically smallest. Return `""` if none qualifies.""",
    constraints=["1 ≤ len(words) ≤ 1000", "1 ≤ len(words[i]) ≤ 30"],
    samples=[(["w", "wo", "wor", "worl", "world"],), (["a", "banana", "app", "appl", "ap", "apply", "apple"],)],
    gen=lambda r: (sorted({r.word(r.randint(1, 4), "ab") for _ in range(r.randint(1, 14))}),),
    brute=lambda words: min([w for w in words if all(w[:i] in words for i in range(1, len(w)))] + [""], key=lambda w: (-len(w), w)),
    hints=[
        "A word qualifies if every proper prefix is also a word.",
        "In a trie, that means every node on the word's path is marked as a word end.",
        "Alternatively sort the words and add a word to a \"buildable\" set when its prefix minus one letter is already buildable.",
    ],
    insight="Prefix closure can be checked with a trie or with sorting and a set.",
    time="O(total characters · log n)", space="O(total characters)",
    pitfalls=["Breaking ties in favor of the larger word."],
)
def longest_word(words):
    buildable, best = {""}, ""
    for w in sorted(words):
        if w[:-1] in buildable:
            buildable.add(w)
            if len(w) > len(best):
                best = w
    return best


@problem(
    slug="lexicographical-numbers", title="Lexicographical Numbers", difficulty="Medium", pattern=TR, tags=["Depth-First Search", "Trie"],
    sig="lexicalOrder(self, n: int) -> list[int]",
    desc="""Return the numbers `1..n` sorted in lexicographical (dictionary) order, in O(n) time and O(1) extra space.""",
    constraints=["1 ≤ n ≤ 5 × 10⁴"],
    samples=[(13,), (2,)],
    tests=[(1,), (100,), (215,)],
    gen=lambda r: (r.randint(1, 300),),
    brute=lambda n: sorted(range(1, n + 1), key=str),
    hints=[
        "Picture a trie of decimal digits: 1 → 10 → 100…, then 101, …",
        "After x, try going deeper to x·10 if it's ≤ n.",
        "Otherwise go to x + 1, but first climb up (x //= 10) while x ends in 9 or x + 1 exceeds n.",
    ],
    insight="A preorder walk of the implicit digit trie, done iteratively.",
    time="O(n)", space="O(1)",
    pitfalls=["Sorting string versions of all numbers (O(n log n))."],
)
def lexical_order(n):
    out, x = [], 1
    for _ in range(n):
        out.append(x)
        if x * 10 <= n:
            x *= 10
        else:
            while x % 10 == 9 or x + 1 > n:
                x //= 10
            x += 1
    return out


# ---------------------------------------------------------------- bit manipulation


@problem(
    slug="find-the-difference", title="Find the Difference", difficulty="Easy", pattern=BT,
    tags=["Hash Table", "String", "Bit Manipulation", "Sorting"],
    sig="findTheDifference(self, s: str, t: str) -> str",
    desc="""`t` is `s` shuffled with one extra letter added at a random position. Return the added letter.""",
    constraints=["0 ≤ len(s) ≤ 1000", "len(t) = len(s) + 1", "lowercase letters"],
    samples=[("abcd", "abcde"), ("", "y")],
    gen=lambda r: (lambda s, c: (s, "".join(r.sample(s + c, len(s) + 1))))(r.word(r.randint(0, 8), "abcd"), r.choice("abcde")),
    brute=lambda s, t: next(c for c in t if t.count(c) > s.count(c)),
    hints=[
        "Every letter of s appears in t too; only one letter is unpaired.",
        "XOR cancels equal values: a ^ a = 0.",
        "XOR the codes of every character in s and t; what remains is the extra letter.",
    ],
    insight="XOR of all characters leaves only the unpaired one.",
    time="O(n)", space="O(1)",
    pitfalls=["Assuming the extra letter is new; it may duplicate an existing letter."],
)
def find_the_difference(s, t):
    x = 0
    for c in s + t:
        x ^= ord(c)
    return chr(x)


@problem(
    slug="complement-of-base-10-integer", title="Complement of Base 10 Integer", difficulty="Easy", pattern=BT, tags=["Bit Manipulation"],
    sig="bitwiseComplement(self, n: int) -> int",
    desc="""Flip every bit in the binary form of `n` (without leading zeros) and return the resulting number. The complement of 0 is 1.""",
    constraints=["0 ≤ n < 10⁹"],
    samples=[(5,), (7,), (10,)],
    tests=[(0,), (1,)],
    gen=lambda r: (r.randint(0, 10 ** r.randint(1, 9) - 1),),
    brute=lambda n: int("".join("1" if c == "0" else "0" for c in bin(n)[2:]), 2),
    hints=[
        "Only the bits up to the highest set bit should flip.",
        "Build a mask of all 1s with the same bit length as n.",
        "XOR n with that mask (handle n = 0 separately).",
    ],
    insight="XOR with an all-ones mask of the right width flips exactly those bits.",
    time="O(1)", space="O(1)",
    pitfalls=["Flipping all 32 bits, which gives a negative number."],
)
def bitwise_complement(n):
    return 1 if n == 0 else n ^ ((1 << n.bit_length()) - 1)


@problem(
    slug="flipping-an-image", title="Flipping an Image", difficulty="Easy", pattern=BT,
    tags=["Array", "Two Pointers", "Bit Manipulation", "Matrix", "Simulation"],
    sig="flipAndInvertImage(self, image: list[list[int]]) -> list[list[int]]",
    desc="""Flip each row of the binary matrix horizontally, then invert it (0 ↔ 1). Return the result.""",
    constraints=["1 ≤ n ≤ 20", "image is n × n of 0s and 1s"],
    samples=[([[1, 1, 0], [1, 0, 1], [0, 0, 0]],), ([[1, 1, 0, 0], [1, 0, 0, 1], [0, 1, 1, 1], [1, 0, 1, 0]],)],
    gen=lambda r: (lambda n: ([[r.randint(0, 1) for _ in range(n)] for _ in range(n)],))(r.randint(1, 5)),
    hints=[
        "Reversing and inverting can be done in one pass per row.",
        "Use two pointers from both ends, swapping and inverting with XOR 1.",
        "When the pointers meet at the middle, just invert that element.",
    ],
    insight="XOR with 1 inverts a bit; combine it with an in-place reversal.",
    time="O(n²)", space="O(1)",
    pitfalls=["Inverting the middle element twice."],
)
def flip_and_invert(image):
    return [[b ^ 1 for b in reversed(row)] for row in image]


@problem(
    slug="single-number-iii", title="Single Number III", difficulty="Medium", pattern=BT, tags=["Array", "Bit Manipulation"],
    sig="singleNumber(self, nums: list[int]) -> list[int]", compare="unordered",
    desc="""Exactly two values in `nums` appear once; every other value appears exactly twice. Return the two single values in any order, using O(n) time and O(1) extra space.""",
    constraints=["2 ≤ len(nums) ≤ 3 × 10⁴", "-2³¹ ≤ nums[i] ≤ 2³¹ − 1"],
    samples=[([1, 2, 1, 3, 2, 5],), ([-1, 0],), ([0, 1],)],
    gen=lambda r: (lambda v: (r.sample(v[:2] + v[2:] * 2, len(v) * 2 - 2),))(r.distinct(r.randint(2, 7), -20, 20)),
    brute=lambda nums: [v for v in set(nums) if nums.count(v) == 1],
    hints=[
        "XOR of everything gives a ^ b, the XOR of the two answers.",
        "a ^ b is non-zero, so some bit differs between a and b.",
        "Split all numbers by that bit and XOR each group separately: each group yields one answer.",
    ],
    insight="A distinguishing bit partitions the array into two Single Number problems.",
    time="O(n)", space="O(1)",
    pitfalls=["Using a hash map, which breaks the O(1) space goal."],
)
def single_number_iii(nums):
    x = 0
    for v in nums:
        x ^= v
    low = x & -x
    a = 0
    for v in nums:
        if v & low:
            a ^= v
    return [a, x ^ a]


@problem(
    slug="single-number-ii", title="Single Number II", difficulty="Medium", pattern=BT, tags=["Array", "Bit Manipulation"],
    sig="singleNumber(self, nums: list[int]) -> int",
    desc="""Every value in `nums` appears exactly three times except one, which appears once. Return that value, using O(n) time and O(1) extra space.""",
    constraints=["1 ≤ len(nums) ≤ 3 × 10⁴", "-2³¹ ≤ nums[i] ≤ 2³¹ − 1"],
    samples=[([2, 2, 3, 2],), ([0, 1, 0, 1, 0, 1, 99],)],
    tests=[([-2, -2, 1, 1, 4, 1, 4, 4, -4, -2],)],
    gen=lambda r: (lambda v: (r.sample(v[:1] + v[1:] * 3, len(v) * 3 - 2),))(r.distinct(r.randint(1, 5), -20, 20)),
    brute=lambda nums: next(v for v in nums if nums.count(v) == 1),
    hints=[
        "Count how many numbers have each bit set.",
        "For every bit, the count modulo 3 is that bit of the single number.",
        "Rebuild the number bit by bit (treating bit 31 as the sign), or use the two-variable \"ones / twos\" trick.",
    ],
    insight="Bit counts modulo 3 cancel the triples.",
    time="O(32n)", space="O(1)",
    pitfalls=["Forgetting to handle the sign bit for negative numbers."],
)
def single_number_ii(nums):
    ones = twos = 0
    for v in nums:
        ones = (ones ^ v) & ~twos
        twos = (twos ^ v) & ~ones
    return ones


@problem(
    slug="reverse-bits", title="Reverse Bits", difficulty="Easy", pattern=BT, tags=["Divide and Conquer", "Bit Manipulation"],
    sig="reverseBits(self, n: int) -> int",
    desc="""`n` is a 32-bit unsigned integer. Reverse the order of its 32 bits and return the resulting unsigned integer.""",
    constraints=["0 ≤ n < 2³²"],
    samples=[(43261596,), (4294967293,)],
    tests=[(0,), (1,)],
    gen=lambda r: (r.randint(0, 2 ** 32 - 1),),
    brute=lambda n: int(format(n, "032b")[::-1], 2),
    hints=[
        "Take bits from the right end of n and push them onto the right end of the result.",
        "Repeat exactly 32 times, including leading zeros.",
        "Each step: result = (result << 1) | (n & 1), then n >>= 1.",
    ],
    insight="Shift bits out of n and into the result 32 times.",
    time="O(32)", space="O(1)",
    pitfalls=["Stopping when n becomes 0, which drops trailing zeros."],
)
def reverse_bits(n):
    out = 0
    for _ in range(32):
        out = (out << 1) | (n & 1)
        n >>= 1
    return out


@problem(
    slug="number-of-1-bits", title="Number of 1 Bits", difficulty="Easy", pattern=BT, tags=["Divide and Conquer", "Bit Manipulation"],
    sig="hammingWeight(self, n: int) -> int",
    desc="""Return the number of set bits (1s) in the binary form of the positive integer `n`.""",
    constraints=["1 ≤ n ≤ 2³¹ − 1"],
    samples=[(11,), (128,), (2147483645,)],
    gen=lambda r: (r.randint(1, 2 ** 31 - 1),),
    brute=lambda n: bin(n).count("1"),
    hints=[
        "You could test each of the 32 bits.",
        "n & (n − 1) clears the lowest set bit.",
        "Count how many times you can do that before n becomes 0.",
    ],
    insight="Brian Kernighan's trick runs once per set bit.",
    time="O(set bits)", space="O(1)",
    pitfalls=["Looping forever on negative inputs in other languages."],
)
def hamming_weight(n):
    c = 0
    while n:
        n &= n - 1
        c += 1
    return c


@problem(
    slug="power-of-two", title="Power of Two", difficulty="Easy", pattern=BT, tags=["Math", "Bit Manipulation", "Recursion"],
    sig="isPowerOfTwo(self, n: int) -> bool",
    desc="""Return `true` if `n` is a power of two (`n = 2ˣ` for some integer `x ≥ 0`).""",
    constraints=["-2³¹ ≤ n ≤ 2³¹ − 1"],
    samples=[(1,), (16,), (3,)],
    tests=[(0,), (-16,), (1073741824,)],
    gen=lambda r: (r.choice([2 ** r.randint(0, 30), r.randint(-50, 2 ** 31 - 1)]),),
    brute=lambda n: n > 0 and bin(n).count("1") == 1,
    hints=[
        "A power of two has exactly one set bit.",
        "n & (n − 1) clears the lowest set bit.",
        "So n is a power of two exactly when n > 0 and n & (n − 1) == 0.",
    ],
    insight="One set bit ⇔ n & (n − 1) == 0 (for positive n).",
    time="O(1)", space="O(1)",
    pitfalls=["Accepting 0 or negative numbers."],
)
def is_power_of_two(n):
    return n > 0 and n & (n - 1) == 0


@problem(
    slug="hamming-distance", title="Hamming Distance", difficulty="Easy", pattern=BT, tags=["Bit Manipulation"],
    sig="hammingDistance(self, x: int, y: int) -> int",
    desc="""Return the number of bit positions at which `x` and `y` differ.""",
    constraints=["0 ≤ x, y ≤ 2³¹ − 1"],
    samples=[(1, 4), (3, 1)],
    gen=lambda r: (r.randint(0, 2 ** 31 - 1), r.randint(0, 2 ** 31 - 1)),
    hints=[
        "XOR marks exactly the positions that differ.",
        "Then count the 1 bits of x ^ y.",
        "Use n & (n − 1) to clear one set bit at a time while counting.",
    ],
    insight="Hamming distance is the popcount of x XOR y.",
    time="O(1)", space="O(1)",
    pitfalls=["Comparing decimal digits instead of bits."],
)
def hamming_distance(x, y):
    return bin(x ^ y).count("1")


@problem(
    slug="minimum-flips-to-make-a-or-b-equal-to-c", title="Minimum Flips to Make a OR b Equal to c", difficulty="Medium", pattern=BT,
    tags=["Bit Manipulation"],
    sig="minFlips(self, a: int, b: int, c: int) -> int",
    desc="""Return the minimum number of single-bit flips in `a` and `b` so that `a OR b == c`.""",
    constraints=["1 ≤ a, b, c ≤ 10⁹"],
    samples=[(2, 6, 5), (4, 2, 7), (1, 2, 3)],
    gen=lambda r: (r.randint(1, 64), r.randint(1, 64), r.randint(1, 64)),
    brute=lambda a, b, c: sum(min((x != (a >> i & 1)) + (y != (b >> i & 1)) for x in (0, 1) for y in (0, 1) if (x | y) == (c >> i & 1)) for i in range(32)),
    hints=[
        "Bits are independent; handle each position separately.",
        "If c's bit is 1, you need at least one of a's or b's bits to be 1 (one flip if both are 0).",
        "If c's bit is 0, both a's and b's bits must be 0: each 1 costs one flip.",
    ],
    insight="Per-bit case analysis sums to the answer.",
    time="O(32)", space="O(1)",
    pitfalls=["Counting one flip when both a and b have a 1 where c has a 0."],
)
def min_flips(a, b, c):
    flips = 0
    for i in range(32):
        x, y, z = a >> i & 1, b >> i & 1, c >> i & 1
        flips += (1 if not (x | y) else 0) if z else x + y
    return flips


@problem(
    slug="bitwise-and-of-numbers-range", title="Bitwise AND of Numbers Range", difficulty="Medium", pattern=BT, tags=["Bit Manipulation"],
    sig="rangeBitwiseAnd(self, left: int, right: int) -> int",
    desc="""Return the bitwise AND of all integers from `left` to `right`, inclusive.""",
    constraints=["0 ≤ left ≤ right ≤ 2³¹ − 1"],
    samples=[(5, 7), (0, 0), (1, 2147483647)],
    gen=lambda r: (lambda a: (a, a + r.randint(0, 40)))(r.randint(0, 200)),
    brute=lambda l, r: __import__("functools").reduce(lambda x, y: x & y, range(l, r + 1)) if r - l < 10**5 else range_bitwise_and(l, r),
    hints=[
        "Any bit that changes somewhere in the range becomes 0 in the AND.",
        "Only the common binary prefix of left and right survives.",
        "Shift both right until they're equal, counting shifts; then shift the common value back left.",
    ],
    insight="The answer is the common prefix of left and right in binary.",
    time="O(log right)", space="O(1)",
    pitfalls=["ANDing every number in a huge range."],
)
def range_bitwise_and(left, right):
    shift = 0
    while left != right:
        left >>= 1
        right >>= 1
        shift += 1
    return left << shift


@problem(
    slug="xor-operation-in-an-array", title="XOR Operation in an Array", difficulty="Easy", pattern=BT, tags=["Math", "Bit Manipulation"],
    sig="xorOperation(self, n: int, start: int) -> int",
    desc="""Define `nums[i] = start + 2 * i` for `0 ≤ i < n`. Return the XOR of all elements of `nums`.""",
    constraints=["1 ≤ n ≤ 1000", "0 ≤ start ≤ 1000"],
    samples=[(5, 0), (4, 3)],
    gen=lambda r: (r.randint(1, 50), r.randint(0, 100)),
    hints=[
        "Generate the values one by one.",
        "Keep a running XOR starting from 0.",
        "XOR each start + 2·i into it. (An O(1) formula exists using XOR of 0..k patterns.)",
    ],
    insight="A running XOR accumulator.",
    time="O(n)", space="O(1)",
    pitfalls=["Starting the accumulator at 1 instead of 0."],
)
def xor_operation(n, start):
    x = 0
    for i in range(n):
        x ^= start + 2 * i
    return x


# ---------------------------------------------------------------- math & geometry


@problem(
    slug="powx-n", title="Pow(x, n)", difficulty="Medium", pattern=MG, tags=["Math", "Recursion"],
    sig="myPow(self, x: float, n: int) -> float", compare="approx",
    desc="""Compute `x` raised to the integer power `n` without using a built-in power function. Answers within a relative error of 10⁻⁵ are accepted.""",
    constraints=["-100 < x < 100", "-2³¹ ≤ n ≤ 2³¹ − 1", "n is an integer", "the result fits in [-10⁴, 10⁴] or x ≠ 0 when n < 0"],
    samples=[(2.0, 10), (2.1, 3), (2.0, -2)],
    tests=[(1.0, 2147483647), (-1.0, -2147483648), (0.5, 3)],
    gen=lambda r: (round(r.uniform(-2, 2), 2) or 1.5, r.randint(-8, 8)),
    brute=lambda x, n: x ** n,
    hints=[
        "Multiplying n times is too slow when n is in the billions.",
        "x^n = (x^(n/2))² for even n, and x · x^(n−1) for odd n.",
        "Use exponentiation by squaring; for negative n compute 1 / x^(−n).",
    ],
    insight="Binary exponentiation needs only O(log n) multiplications.",
    time="O(log |n|)", space="O(1)",
    pitfalls=["Overflow when negating −2³¹ in fixed-width languages."],
)
def my_pow(x, n):
    if n < 0:
        x, n = 1 / x, -n
    out = 1.0
    while n:
        if n & 1:
            out *= x
        x *= x
        n >>= 1
    return out


@problem(
    slug="plus-one", title="Plus One", difficulty="Easy", pattern=MG, tags=["Array", "Math"],
    sig="plusOne(self, digits: list[int]) -> list[int]",
    desc="""`digits` represents a non-negative integer, most significant digit first, with no leading zeros. Add one and return the resulting digits.""",
    constraints=["1 ≤ len(digits) ≤ 100", "0 ≤ digits[i] ≤ 9"],
    samples=[([1, 2, 3],), ([4, 3, 2, 1],), ([9],)],
    tests=[([9, 9, 9],), ([0],)],
    gen=lambda r: ([r.randint(1, 9)] + [r.choice([9, 9, r.randint(0, 9)]) for _ in range(r.randint(0, 6))],),
    brute=lambda d: [int(c) for c in str(int("".join(map(str, d))) + 1)],
    hints=[
        "Adding one only changes a run of trailing 9s and the digit before it.",
        "Walk from the last digit: a 9 becomes 0 and carries; anything else increments and you're done.",
        "If every digit was 9, put a 1 in front.",
    ],
    insight="Handle the carry from the right.",
    time="O(n)", space="O(1) (O(n) when all digits are 9)",
    pitfalls=["Converting to an integer, which overflows in many languages."],
)
def plus_one(digits):
    d = list(digits)
    for i in range(len(d) - 1, -1, -1):
        if d[i] < 9:
            d[i] += 1
            return d
        d[i] = 0
    return [1] + d


@problem(
    slug="multiply-strings", title="Multiply Strings", difficulty="Medium", pattern=MG, tags=["Math", "String", "Simulation"],
    sig="multiply(self, num1: str, num2: str) -> str",
    desc="""Return the product of two non-negative integers given as strings, as a string. Don't convert the inputs to integers directly.""",
    constraints=["1 ≤ len(num1), len(num2) ≤ 200", "no leading zeros except the number 0 itself"],
    samples=[("2", "3"), ("123", "456"), ("0", "52")],
    gen=lambda r: (str(r.randint(0, 10 ** r.randint(1, 12))), str(r.randint(0, 10 ** r.randint(1, 12)))),
    brute=lambda a, b: str(int(a) * int(b)),
    hints=[
        "Multiplying digit i of num1 by digit j of num2 contributes to position i + j + 1 of the result.",
        "Use an array of length m + n to accumulate these products.",
        "Handle carries from right to left, then strip leading zeros (keeping a single \"0\").",
    ],
    insight="Grade-school multiplication with a position array.",
    time="O(m·n)", space="O(m + n)",
    pitfalls=["Leaving leading zeros in the answer."],
)
def multiply(num1, num2):
    m, n = len(num1), len(num2)
    res = [0] * (m + n)
    for i in range(m - 1, -1, -1):
        for j in range(n - 1, -1, -1):
            p = (ord(num1[i]) - 48) * (ord(num2[j]) - 48) + res[i + j + 1]
            res[i + j + 1] = p % 10
            res[i + j] += p // 10
    s = "".join(map(str, res)).lstrip("0")
    return s or "0"


@problem(
    slug="robot-bounded-in-circle", title="Robot Bounded In Circle", difficulty="Medium", pattern=MG, tags=["Math", "String", "Simulation"],
    sig="isRobotBounded(self, instructions: str) -> bool",
    desc="""A robot at `(0, 0)` faces north and repeats `instructions` forever: `G` moves one step forward, `L` turns 90° left, `R` turns 90° right. Return `true` if the robot stays within some circle forever.""",
    constraints=["1 ≤ len(instructions) ≤ 100"],
    samples=[("GGLLGG",), ("GG",), ("GL",)],
    gen=lambda r: (r.word(r.randint(1, 8), "GGLR"),),
    brute=lambda ins: _robot_after(ins * 4) == (0, 0, 0),
    hints=[
        "Simulate one pass of the instructions.",
        "If the robot is back at the origin, it's bounded.",
        "If it isn't facing north after one pass, it comes back to the start within four passes, so it's bounded too.",
    ],
    insight="After one cycle, being at the origin or not facing north implies a bounded path.",
    time="O(n)", space="O(1)",
    pitfalls=["Simulating a large fixed number of steps instead of reasoning about direction."],
)
def is_robot_bounded(instructions):
    x, y, d = _robot_after(instructions)
    return (x, y) == (0, 0) or d != 0


def _robot_after(ins):
    x = y = d = 0
    dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    for c in ins:
        if c == "G":
            x, y = x + dirs[d][0], y + dirs[d][1]
        elif c == "L":
            d = (d + 3) % 4
        else:
            d = (d + 1) % 4
    return x, y, d


def _square_input(r):
    if r.random() < 0.5:
        x, y, dx, dy = r.randint(-5, 5), r.randint(-5, 5), r.randint(-4, 4), r.randint(-4, 4)
        pts = [[x, y], [x + dx, y + dy], [x + dx - dy, y + dy + dx], [x - dy, y + dx]]
        r.shuffle(pts)
        return tuple(pts)
    return tuple([r.randint(-3, 3), r.randint(-3, 3)] for _ in range(4))


def _square_brute(*pts):
    d = sorted((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 for a, b in combinations(pts, 2))
    return d[0] > 0 and d[0] == d[1] == d[2] == d[3] and d[4] == d[5] == 2 * d[0]


@problem(
    slug="valid-square", title="Valid Square", difficulty="Medium", pattern=MG, tags=["Math", "Geometry"],
    sig="validSquare(self, p1: list[int], p2: list[int], p3: list[int], p4: list[int]) -> bool",
    desc="""Given four points in any order, return `true` if they form a square with positive side length.""",
    constraints=["-10⁴ ≤ coordinates ≤ 10⁴"],
    samples=[([0, 0], [1, 1], [1, 0], [0, 1]), ([0, 0], [1, 1], [1, 0], [0, 12]), ([1, 0], [-1, 0], [0, 1], [0, -1])],
    gen=_square_input,
    brute=_square_brute,
    hints=[
        "Look at all 6 pairwise distances (squared, to stay in integers).",
        "A square has 4 equal sides and 2 equal diagonals, with diagonal² = 2 × side².",
        "Also reject zero-length sides (repeated points).",
    ],
    insight="Six squared distances fully characterize a square.",
    time="O(1)", space="O(1)",
    pitfalls=["Accepting a rhombus (4 equal sides, unequal diagonals)."],
)
def valid_square(p1, p2, p3, p4):
    return _square_brute(p1, p2, p3, p4)


def _max_points_brute(points):
    if len(points) <= 2:
        return len(points)
    best = 2
    for a, b in combinations(points, 2):
        best = max(best, sum(1 for c in points if (b[0] - a[0]) * (c[1] - a[1]) == (b[1] - a[1]) * (c[0] - a[0])))
    return best


@problem(
    slug="max-points-on-a-line", title="Max Points on a Line", difficulty="Hard", pattern=MG, tags=["Array", "Hash Table", "Math", "Geometry"],
    sig="maxPoints(self, points: list[list[int]]) -> int",
    desc="""Given distinct points on a plane, return the maximum number of them that lie on one straight line.""",
    constraints=["1 ≤ len(points) ≤ 300", "points are distinct", "-10⁴ ≤ coordinates ≤ 10⁴"],
    samples=[([[1, 1], [2, 2], [3, 3]],), ([[1, 1], [3, 2], [5, 3], [4, 1], [2, 3], [1, 4]],)],
    gen=lambda r: ([list(p) for p in {(r.randint(-4, 4), r.randint(-4, 4)) for _ in range(r.randint(1, 9))}],),
    brute=_max_points_brute,
    hints=[
        "Fix one point and group the others by the direction (slope) to them.",
        "Represent the slope exactly as a reduced fraction (dy, dx) with a normalized sign; avoid floats.",
        "The largest group plus the fixed point is a candidate answer.",
    ],
    insight="Count exact slopes from each anchor point.",
    time="O(n²)", space="O(n)",
    pitfalls=["Floating-point slopes that compare unequal for the same line."],
)
def max_points(points):
    n, best = len(points), min(len(points), 2)
    for i in range(n):
        slopes = {}
        for j in range(i + 1, n):
            dx, dy = points[j][0] - points[i][0], points[j][1] - points[i][1]
            g = gcd(dx, dy)
            dx, dy = dx // g, dy // g
            if dx < 0 or (dx == 0 and dy < 0):
                dx, dy = -dx, -dy
            slopes[dx, dy] = slopes.get((dx, dy), 0) + 1
            best = max(best, slopes[dx, dy] + 1)
    return best


@problem(
    slug="rectangle-overlap", title="Rectangle Overlap", difficulty="Easy", pattern=MG, tags=["Math", "Geometry"],
    sig="isRectangleOverlap(self, rec1: list[int], rec2: list[int]) -> bool",
    desc="""Each rectangle is axis-aligned and given as `[x1, y1, x2, y2]` (bottom-left and top-right corners). Return `true` if they overlap with **positive area** (touching edges or corners doesn't count).""",
    constraints=["x1 < x2, y1 < y2", "-10⁹ ≤ coordinates ≤ 10⁹"],
    samples=[([0, 0, 2, 2], [1, 1, 3, 3]), ([0, 0, 1, 1], [1, 0, 2, 1]), ([0, 0, 1, 1], [2, 2, 3, 3])],
    gen=lambda r: tuple((lambda x, y: [x, y, x + r.randint(1, 4), y + r.randint(1, 4)])(r.randint(-4, 4), r.randint(-4, 4)) for _ in range(2)),
    brute=lambda a, b: any(a[0] < x + 0.5 < a[2] and a[1] < y + 0.5 < a[3] and b[0] < x + 0.5 < b[2] and b[1] < y + 0.5 < b[3] for x in range(-10, 10) for y in range(-10, 10)),
    hints=[
        "Two intervals overlap with positive length if each starts before the other ends.",
        "Rectangles overlap exactly when their x-intervals overlap and their y-intervals overlap.",
        "Check min(x2s) > max(x1s) and min(y2s) > max(y1s).",
    ],
    insight="Reduce a 2D overlap test to two 1D interval tests.",
    time="O(1)", space="O(1)",
    pitfalls=["Using ≥, which counts touching edges as overlap."],
)
def is_rectangle_overlap(rec1, rec2):
    return min(rec1[2], rec2[2]) > max(rec1[0], rec2[0]) and min(rec1[3], rec2[3]) > max(rec1[1], rec2[1])


@problem(
    slug="excel-sheet-column-number", title="Excel Sheet Column Number", difficulty="Easy", pattern=MG, tags=["Math", "String"],
    sig="titleToNumber(self, columnTitle: str) -> int",
    desc="""Convert an Excel column title to its number: `A → 1`, `B → 2`, …, `Z → 26`, `AA → 27`, `AB → 28`, ….""",
    constraints=["1 ≤ len(columnTitle) ≤ 7", "uppercase letters", "the result ≤ 2³¹ − 1"],
    samples=[("A",), ("AB",), ("ZY",)],
    tests=[("FXSHRXW",), ("AZ",)],
    gen=lambda r: (r.word(r.randint(1, 5), "ABCXYZ"),),
    hints=[
        "It's like base 26, but the digits run from 1 to 26 instead of 0 to 25.",
        "Process letters left to right.",
        "result = result × 26 + (letter position, with A = 1).",
    ],
    insight="A base-26 conversion with digits 1–26.",
    time="O(n)", space="O(1)",
    pitfalls=["Using A = 0."],
)
def title_to_number(columnTitle):
    n = 0
    for c in columnTitle:
        n = n * 26 + ord(c) - 64
    return n


@problem(
    slug="excel-sheet-column-title", title="Excel Sheet Column Title", difficulty="Easy", pattern=MG, tags=["Math", "String"],
    sig="convertToTitle(self, columnNumber: int) -> str",
    desc="""Convert a positive column number to its Excel column title: `1 → A`, …, `26 → Z`, `27 → AA`, `28 → AB`, ….""",
    constraints=["1 ≤ columnNumber ≤ 2³¹ − 1"],
    samples=[(1,), (28,), (701,)],
    tests=[(2147483647,), (26,), (52,)],
    gen=lambda r: (r.randint(1, 10 ** r.randint(1, 6)),),
    brute=lambda n: next(t for t in ("".join(p) for L in range(1, 6) for p in __import__("itertools").product("ABCDEFGHIJKLMNOPQRSTUVWXYZ", repeat=L)) if title_to_number(t) == n) if n <= 2000 else convert_to_title(n),
    hints=[
        "There's no zero digit: Z means 26, not a carry.",
        "Subtract 1 before each step so the remainder maps to A–Z as 0–25.",
        "Repeat: n −= 1, take n % 26 as a letter, n //= 26; build the string backwards.",
    ],
    insight="Bijective base-26: shift by one before each division.",
    time="O(log n)", space="O(log n)",
    pitfalls=["Producing \"A@\" for 26 by not adjusting for the missing zero."],
)
def convert_to_title(columnNumber):
    out = []
    n = columnNumber
    while n:
        n -= 1
        out.append(chr(65 + n % 26))
        n //= 26
    return "".join(reversed(out))


@problem(
    slug="palindrome-number", title="Palindrome Number", difficulty="Easy", pattern=MG, tags=["Math"],
    sig="isPalindrome(self, x: int) -> bool",
    desc="""Return `true` if the integer `x` reads the same forwards and backwards. Try it without converting to a string.""",
    constraints=["-2³¹ ≤ x ≤ 2³¹ − 1"],
    samples=[(121,), (-121,), (10,)],
    tests=[(0,), (1221,), (1000021,)],
    gen=lambda r: (r.choice([int(str(v) + str(v)[::-1]) for v in [r.randint(1, 9999)]] + [r.randint(-100, 10 ** 6)]),),
    brute=lambda x: str(x) == str(x)[::-1],
    hints=[
        "Negative numbers can't be palindromes, and neither can numbers ending in 0 (except 0).",
        "Reverse only the second half of the digits.",
        "Pop digits from x into a reversed number until reversed ≥ x; compare x with reversed (or reversed // 10 for odd lengths).",
    ],
    insight="Reversing half the digits avoids overflow and string conversion.",
    time="O(log x)", space="O(1)",
    pitfalls=["Forgetting the trailing-zero case like 10."],
)
def is_palindrome_number(x):
    if x < 0 or (x % 10 == 0 and x != 0):
        return False
    rev = 0
    while x > rev:
        rev = rev * 10 + x % 10
        x //= 10
    return x == rev or x == rev // 10


@problem(
    slug="reverse-integer", title="Reverse Integer", difficulty="Medium", pattern=MG, tags=["Math"],
    sig="reverse(self, x: int) -> int",
    desc="""Reverse the digits of the signed 32-bit integer `x`. If the result falls outside the signed 32-bit range `[-2³¹, 2³¹ − 1]`, return `0`.""",
    constraints=["-2³¹ ≤ x ≤ 2³¹ − 1"],
    samples=[(123,), (-123,), (120,)],
    tests=[(1534236469,), (-2147483648,), (0,)],
    gen=lambda r: (r.randint(-2 ** 31, 2 ** 31 - 1),),
    brute=lambda x: (lambda v: v if -2 ** 31 <= v <= 2 ** 31 - 1 else 0)((-1 if x < 0 else 1) * int(str(abs(x))[::-1])),
    hints=[
        "Handle the sign separately and reverse the absolute value.",
        "Pop the last digit with % 10 and push it onto the result with × 10.",
        "Check the 32-bit range at the end (or before each push in fixed-width languages).",
    ],
    insight="Digit-by-digit reversal with an overflow check.",
    time="O(log x)", space="O(1)",
    pitfalls=["Using Python's % on negatives, which behaves differently from C-style remainder."],
)
def reverse_integer(x):
    sign = -1 if x < 0 else 1
    x, rev = abs(x), 0
    while x:
        rev = rev * 10 + x % 10
        x //= 10
    rev *= sign
    return rev if -2 ** 31 <= rev <= 2 ** 31 - 1 else 0


@problem(
    slug="count-primes", title="Count Primes", difficulty="Medium", pattern=MG, tags=["Array", "Math", "Enumeration", "Number Theory"],
    sig="countPrimes(self, n: int) -> int",
    desc="""Return the number of prime numbers strictly less than `n`.""",
    constraints=["0 ≤ n ≤ 5 × 10⁶"],
    samples=[(10,), (0,), (1,)],
    tests=[(2,), (3,), (100000,)],
    gen=lambda r: (r.randint(0, 500),),
    brute=lambda n: sum(1 for k in range(2, n) if all(k % d for d in range(2, int(k ** 0.5) + 1))),
    hints=[
        "Testing each number by trial division is too slow for millions.",
        "Sieve of Eratosthenes: every multiple of a prime is composite.",
        "For each prime p up to √n, cross out p², p² + p, … ; count what's left.",
    ],
    insight="The sieve marks composites in O(n log log n).",
    time="O(n log log n)", space="O(n)",
    pitfalls=["Counting n itself (the range is strictly less than n)."],
)
def count_primes(n):
    if n < 3:
        return 0
    sieve = bytearray([1]) * n
    sieve[0] = sieve[1] = 0
    for p in range(2, int(n ** 0.5) + 1):
        if sieve[p]:
            sieve[p * p::p] = bytearray(len(range(p * p, n, p)))
    return sum(sieve)


@problem(
    slug="add-binary", title="Add Binary", difficulty="Easy", pattern=MG, tags=["Math", "String", "Bit Manipulation", "Simulation"],
    sig="addBinary(self, a: str, b: str) -> str",
    desc="""Return the sum of two binary strings as a binary string.""",
    constraints=["1 ≤ len(a), len(b) ≤ 10⁴", "no leading zeros except \"0\" itself"],
    samples=[("11", "1"), ("1010", "1011"), ("0", "0")],
    gen=lambda r: (bin(r.randint(0, 2 ** r.randint(1, 40)))[2:], bin(r.randint(0, 2 ** r.randint(1, 40)))[2:]),
    brute=lambda a, b: bin(int(a, 2) + int(b, 2))[2:],
    hints=[
        "Add from the rightmost bits, like decimal addition.",
        "Each column's sum is bit_a + bit_b + carry, from 0 to 3.",
        "Write sum % 2 and carry sum // 2; add a final carry if one remains, then reverse.",
    ],
    insight="Column addition with a carry, in base 2.",
    time="O(max(m, n))", space="O(max(m, n))",
    pitfalls=["Forgetting the final carry."],
)
def add_binary(a, b):
    i, j, carry, out = len(a) - 1, len(b) - 1, 0, []
    while i >= 0 or j >= 0 or carry:
        s = carry + (int(a[i]) if i >= 0 else 0) + (int(b[j]) if j >= 0 else 0)
        out.append(str(s % 2))
        carry = s // 2
        i -= 1
        j -= 1
    return "".join(reversed(out))


@problem(
    slug="angle-between-hands-of-a-clock", title="Angle Between Hands of a Clock", difficulty="Medium", pattern=MG, tags=["Math"],
    sig="angleClock(self, hour: int, minutes: int) -> float", compare="approx",
    desc="""Return the smaller angle (in degrees) between the hour and minute hands at `hour:minutes`. Answers within 10⁻⁵ are accepted.""",
    constraints=["1 ≤ hour ≤ 12", "0 ≤ minutes ≤ 59"],
    samples=[(12, 30), (3, 30), (3, 15)],
    tests=[(4, 50), (12, 0)],
    gen=lambda r: (r.randint(1, 12), r.randint(0, 59)),
    brute=lambda h, m: float(min(abs(Fraction(h % 12 * 60 + m, 2) - 6 * m), 360 - abs(Fraction(h % 12 * 60 + m, 2) - 6 * m))),
    hints=[
        "The minute hand moves 6° per minute.",
        "The hour hand moves 30° per hour plus 0.5° per minute.",
        "Take the absolute difference d and answer min(d, 360 − d).",
    ],
    insight="Compute both hand angles from 12 o'clock and take the smaller gap.",
    time="O(1)", space="O(1)",
    pitfalls=["Ignoring the hour hand's movement within the hour."],
)
def angle_clock(hour, minutes):
    d = abs((hour % 12) * 30 + minutes * 0.5 - minutes * 6)
    return min(d, 360 - d)


_ROMAN = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]


@problem(
    slug="integer-to-roman", title="Integer to Roman", difficulty="Medium", pattern=MG, tags=["Hash Table", "Math", "String"],
    sig="intToRoman(self, num: int) -> str",
    desc="""Convert an integer to a Roman numeral, using the symbols I (1), V (5), X (10), L (50), C (100), D (500), M (1000) and the subtractive forms IV (4), IX (9), XL (40), XC (90), CD (400), CM (900).""",
    constraints=["1 ≤ num ≤ 3999"],
    samples=[(3749,), (58,), (1994,)],
    gen=lambda r: (r.randint(1, 3999),),
    hints=[
        "List the 13 symbol values, including the subtractive pairs, from largest to smallest.",
        "Greedily use the largest value that still fits.",
        "Append its symbol and subtract, repeating until the number reaches 0.",
    ],
    insight="Greedy over a fixed table including subtractive pairs.",
    time="O(1)", space="O(1)",
    pitfalls=["Writing IIII instead of IV."],
)
def int_to_roman(num):
    out = []
    for v, s in _ROMAN:
        while num >= v:
            out.append(s)
            num -= v
    return "".join(out)


@problem(
    slug="roman-to-integer", title="Roman to Integer", difficulty="Easy", pattern=MG, tags=["Hash Table", "Math", "String"],
    sig="romanToInt(self, s: str) -> int",
    desc="""Convert a valid Roman numeral (value 1 to 3999) to an integer. A smaller symbol before a larger one is subtracted (IV = 4, IX = 9, XL = 40, XC = 90, CD = 400, CM = 900).""",
    constraints=["1 ≤ len(s) ≤ 15", "s is a valid Roman numeral in [1, 3999]"],
    samples=[("III",), ("LVIII",), ("MCMXCIV",)],
    gen=lambda r: (int_to_roman(r.randint(1, 3999)),),
    brute=lambda s: next(v for v in range(1, 4000) if int_to_roman(v) == s),
    hints=[
        "Map each symbol to its value.",
        "A symbol is subtracted when the next symbol is larger.",
        "Scan left to right, adding or subtracting each value based on its right neighbor.",
    ],
    insight="Compare each symbol with the next to decide its sign.",
    time="O(n)", space="O(1)",
    pitfalls=["Handling only the six subtractive pairs as special strings and missing the general rule."],
)
def roman_to_int(s):
    val = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    for i, c in enumerate(s):
        if i + 1 < len(s) and val[c] < val[s[i + 1]]:
            total -= val[c]
        else:
            total += val[c]
    return total


def _big_trie_ops(r):
    ops, args = ["Trie"], [[]]
    words = [r.word(r.randint(5, 12), "abc") for _ in range(400)]
    for _ in range(4000):
        op = r.choice(["insert", "search", "startsWith"])
        w = r.choice(words)
        ops.append(op)
        args.append([w if op != "startsWith" else w[: r.randint(1, len(w))]])
    return ops, args


def _big_wd_ops(r):
    ops, args = ["WordDictionary"], [[]]
    for _ in range(3000):
        op = r.choice(["addWord", "search"])
        w = r.word(r.randint(3, 8), "abcd")
        if op == "search":
            w = "".join("." if i in r.sample(range(len(w)), 2) else c for i, c in enumerate(w))
        ops.append(op)
        args.append([w])
    return ops, args


EXTRA = {
    "implement-trie-prefix-tree": {
        "edge": [(["Trie", "search", "startsWith"], [[], ["a"], ["a"]]),
                 (["Trie", "insert", "insert", "search", "search", "startsWith"], [[], ["app"], ["apple"], ["app"], ["appl"], ["apple"]]),
                 (["Trie", "insert", "startsWith", "search"], [[], ["a" * 2000], ["a" * 1999], ["a" * 1999]])],
        "large": [_big_trie_ops],
    },
    "design-add-and-search-words-data-structure": {
        "edge": [(["WordDictionary", "addWord", "search", "search"], [[], ["a"], ["."], [".."]]),
                 (["WordDictionary", "addWord", "addWord", "search", "search"], [[], ["ab"], ["abc"], ["a."], ["a.."]]),
                 (["WordDictionary", "search"], [[], ["..."]])],
        "large": [_big_wd_ops],
    },
    "search-suggestions-system": {
        "edge": [(["a"], "a"), (["a"], "b"), (["ab", "abc", "abcd", "abcde"], "abcdef"), (["bags", "baggage", "banner", "box", "cloths"], "zzz")],
        "large": [lambda r: (sorted({r.word(r.randint(1, 12), "ab") for _ in range(1000)}), r.word(1000, "ab"))],
    },
    "word-search-ii": {
        "edge": [([["a"]], ["a"]), ([["a"]], ["b"]), ([["a", "a"]], ["aaa"]), ([["a", "b"], ["c", "d"]], ["abdc", "abcd", "acdb"])],
        "large": [lambda r: ([[r.choice("abcde") for _ in range(12)] for _ in range(12)], sorted({r.word(r.randint(3, 10), "abcde") for _ in range(3000)}))],
    },
    "longest-word-in-dictionary": {
        "edge": [(["a"],), (["b", "a"],), (["ab"],), (["a", "ab", "abc", "b", "ba", "bac"],)],
        "large": [lambda r: (sorted({r.word(r.randint(1, 6), "ab") for _ in range(1000)}),)],
    },
    "lexicographical-numbers": {"edge": [(9,), (10,), (99,), (1000,)], "large": [lambda r: (20000,)]},
    "find-the-difference": {"edge": [("", "a"), ("a", "aa"), ("ab", "bba"), ("z" * 1000, "z" * 1001)]},
    "complement-of-base-10-integer": {"edge": [(2,), (3,), (999999999,), (536870912,)]},
    "flipping-an-image": {"edge": [([[0]],), ([[1]],), ([[1, 0], [0, 1]],), ([[1] * 20 for _ in range(20)],)]},
    "single-number-iii": {
        "edge": [([1, 2],), ([-2147483648, 2147483647],), ([0, 0, 1, 2],), ([1, 1, 0, -2147483648],)],
        "large": [lambda r: (lambda v: (r.sample(v[:2] + v[2:] * 2, len(v) * 2 - 2),))(r.distinct(3000, -2**31, 2**31 - 1))],
    },
    "single-number-ii": {
        "edge": [([1],), ([-2147483648],), ([2147483647, 5, 5, 5],), ([-1, -1, -1, -2],)],
        "large": [lambda r: (lambda v: (r.sample(v[:1] + v[1:] * 3, len(v) * 3 - 2),))(r.distinct(2500, -2**31, 2**31 - 1))],
    },
    "reverse-bits": {"edge": [(4294967295,), (2147483648,), (2,), (4294967293,)]},
    "number-of-1-bits": {"edge": [(1,), (2147483647,), (1073741824,), (255,)]},
    "power-of-two": {"edge": [(2,), (-2147483648,), (2147483647,), (536870912,), (6,)]},
    "hamming-distance": {"edge": [(0, 0), (0, 2147483647), (7, 7), (2147483647, 1073741823)]},
    "minimum-flips-to-make-a-or-b-equal-to-c": {"edge": [(1, 1, 1), (1, 1, 0 + 2), (1000000000, 1000000000, 1), (8, 3, 5), (7, 7, 7)]},
    "bitwise-and-of-numbers-range": {"edge": [(0, 1), (1, 1), (2147483647, 2147483647), (6, 7), (1073741824, 2147483647)]},
    "xor-operation-in-an-array": {"edge": [(1, 7), (1000, 1000), (10, 5), (1, 0)]},
    "powx-n": {"edge": [(1.0, 0), (0.0, 1), (2.0, -2147483648), (-2.0, 3), (0.00001, 2147483647), (99.9, 1)]},
    "plus-one": {"edge": [([1],), ([8, 9],), ([9] * 100,), ([1] + [0] * 99,)]},
    "multiply-strings": {"edge": [("0", "0"), ("1", "1"), ("9" * 200, "9" * 200), ("1" + "0" * 199, "123"), ("0", "123456789")]},
    "robot-bounded-in-circle": {"edge": [("G",), ("L",), ("GR",), ("GGRGGRGGRGGR",), ("G" * 100,)]},
    "valid-square": {"edge": [([0, 0], [0, 0], [0, 0], [0, 0]), ([1, 0], [0, 1], [-1, 0], [0, -1]), ([0, 0], [1, 1], [0, 0], [1, 1]), ([0, 0], [2, 1], [3, 3], [1, 2]), ([-10000, -10000], [10000, -10000], [10000, 10000], [-10000, 10000])]},
    "max-points-on-a-line": {
        "edge": [([[0, 0]],), ([[0, 0], [1, 1]],), ([[0, 0], [0, 1], [0, 2]],), ([[0, 0], [1, 0], [5, 0], [1, 1]],), ([[-10000, -10000], [10000, 10000], [0, 0], [1, 2]],)],
        "large": [lambda r: ([list(p) for p in {(r.randint(-10000, 10000), r.randint(-10000, 10000)) for _ in range(250)} | {(i, 2 * i + 1) for i in range(40)}],)],
    },
    "rectangle-overlap": {
        "edge": [([0, 0, 1, 1], [1, 1, 2, 2]), ([0, 0, 2, 2], [1, 1, 3, 3]), ([0, 0, 10, 10], [2, 2, 3, 3]), ([-1000000000, -1000000000, 1000000000, 1000000000], [0, 0, 1, 1]), ([0, 0, 1, 1], [0, 1, 1, 2])],
    },
    "excel-sheet-column-number": {"edge": [("Z",), ("ZZ",), ("AAA",), ("FXSHRXW",)]},
    "excel-sheet-column-title": {"edge": [(26,), (27,), (702,), (703,), (18278,)]},
    "palindrome-number": {"edge": [(0,), (-1,), (11,), (2147483647,), (1000000001,), (-2147483648,)]},
    "reverse-integer": {"edge": [(1,), (-1,), (2147483647,), (1463847412,), (-1463847412,), (1000000003,)]},
    "count-primes": {"edge": [(3,), (4,), (5,), (100,)], "large": [lambda r: (5000000,), lambda r: (r.randint(10**6, 4 * 10**6),)]},
    "add-binary": {
        "edge": [("1", "1"), ("0", "1"), ("1" * 50, "1"), ("1010", "0")],
        "large": [lambda r: ("1" + r.word(9999, "01"), "1" + r.word(9999, "01")), lambda r: ("1" * 10000, "1")],
    },
    "angle-between-hands-of-a-clock": {"edge": [(1, 57), (12, 59), (6, 0), (9, 45)]},
    "integer-to-roman": {"edge": [(1,), (4,), (9,), (3999,), (1994,), (444,)]},
    "roman-to-integer": {"edge": [("I",), ("IV",), ("MMMCMXCIX",), ("CDXLIV",), ("XC",)]},
}
