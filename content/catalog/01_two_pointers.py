from itertools import combinations, permutations

from catalog_lib import problem

P = "two-pointers"


@problem(
    slug="valid-palindrome", title="Valid Palindrome", difficulty="Easy", pattern=P, tags=["String", "Two Pointers"],
    sig="isPalindrome(self, s: str) -> bool",
    desc="""A phrase is a **palindrome** if, after lowercasing every letter and throwing away everything that isn't a letter or digit, it reads the same forwards and backwards.

Given a string `s`, return `True` if it is a palindrome under that rule.""",
    constraints=["1 ≤ len(s) ≤ 2 × 10⁵", "s contains printable ASCII characters"],
    samples=[("A man, a plan, a canal: Panama",), ("race a car",), (" ",)],
    tests=[("0P",), ("ab_a",), ("Was it a car or a cat I saw?",)],
    gen=lambda r: (r.word(r.randint(1, 40), "abAB01 ,.!"),),
    brute=lambda s: [c.lower() for c in s if c.isalnum()] == [c.lower() for c in s if c.isalnum()][::-1],
    hints=[
        "Only letters and digits matter, and case doesn't. Can you compare characters without building a cleaned copy?",
        "Put one pointer at each end of the string and move them toward each other.",
        "Skip characters that aren't alphanumeric on either side, then compare the two characters in lowercase. Any mismatch means it isn't a palindrome.",
    ],
    insight="Two pointers moving inward compare mirrored characters in place, using O(1) extra space.",
    time="O(n)", space="O(1)",
    pitfalls=["Forgetting that digits count as characters to compare.", "Comparing without lowercasing first."],
)
def valid_palindrome(s):
    i, j = 0, len(s) - 1
    while i < j:
        if not s[i].isalnum():
            i += 1
        elif not s[j].isalnum():
            j -= 1
        elif s[i].lower() != s[j].lower():
            return False
        else:
            i, j = i + 1, j - 1
    return True


def _three_sum_brute(nums):
    return sorted({tuple(sorted(c)) for c in combinations(nums, 3) if sum(c) == 0})


@problem(
    slug="3sum", title="3Sum", difficulty="Medium", pattern=P, tags=["Array", "Two Pointers", "Sorting"],
    sig="threeSum(self, nums: list[int]) -> list[list[int]]",
    desc="""Given an integer array `nums`, return every **unique** triplet `[a, b, c]` of values taken from three different positions such that `a + b + c == 0`.

No triplet may appear twice. You can return the triplets, and the numbers inside each, in any order.""",
    constraints=["3 ≤ len(nums) ≤ 3000", "-10⁵ ≤ nums[i] ≤ 10⁵"],
    samples=[([-1, 0, 1, 2, -1, -4],), ([0, 1, 1],), ([0, 0, 0],)],
    tests=[([-2, 0, 1, 1, 2],), ([1, -1, -1, 0],)],
    gen=lambda r: (r.ints(r.randint(3, 40), -10, 10),),
    compare="unordered-deep",
    brute=lambda nums: [list(t) for t in _three_sum_brute(nums)],
    hints=[
        "Checking every triple is O(n³). If the array were sorted, could you find pairs faster?",
        "Fix the first number, then you need two numbers after it that sum to its negation: that's a two-pointer search on a sorted array.",
        "Sort, loop over the first index, and run two pointers on the rest. Skip equal values for the first number and after each match to avoid duplicate triplets.",
    ],
    insight="Sorting turns the inner pair search into two pointers, giving O(n²) overall, and makes duplicates adjacent so they're easy to skip.",
    time="O(n²)", space="O(1) besides the output and the sort",
    pitfalls=["Returning duplicate triplets like [-1, 0, 1] twice.", "Reusing the same index twice in a triplet."],
)
def three_sum(nums):
    nums = sorted(nums)
    out = []
    for i in range(len(nums) - 2):
        if i and nums[i] == nums[i - 1]:
            continue
        lo, hi = i + 1, len(nums) - 1
        while lo < hi:
            t = nums[i] + nums[lo] + nums[hi]
            if t < 0:
                lo += 1
            elif t > 0:
                hi -= 1
            else:
                out.append([nums[i], nums[lo], nums[hi]])
                lo += 1
                while lo < hi and nums[lo] == nums[lo - 1]:
                    lo += 1
                hi -= 1
    return out


@problem(
    slug="remove-nth-node-from-end-of-list", title="Remove Nth Node From End of List", difficulty="Medium", pattern=P,
    tags=["Linked List", "Two Pointers"],
    sig="removeNthFromEnd(self, head: Optional[ListNode], n: int) -> Optional[ListNode]",
    arg_types=["ListNode"], ret="ListNode",
    desc="""Given the `head` of a linked list, remove the `n`th node **counting from the end** and return the head of the resulting list.

Lists in the tests are written as lists of values, so `[1, 2, 3]` means `1 → 2 → 3`.""",
    constraints=["1 ≤ number of nodes ≤ 30", "1 ≤ n ≤ number of nodes", "0 ≤ Node.val ≤ 100"],
    samples=[([1, 2, 3, 4, 5], 2), ([1], 1), ([1, 2], 1)],
    tests=[([1, 2], 2), ([7, 8, 9], 3)],
    gen=lambda r: (lambda vals: (vals, r.randint(1, len(vals))))(r.ints(r.randint(1, 30), 0, 100)),
    brute=lambda head, n: (lambda v: to_ln(v[: len(v) - n] + v[len(v) - n + 1:]))(from_ln(head)),
    hints=[
        "The simple way counts the length first, then walks to the node before the one to remove. Can you do it in one pass?",
        "Start a second pointer n steps behind the first, so that when the leading pointer reaches the end, the trailing one is right before the target.",
        "Use a dummy node before the head so removing the first node needs no special case. Move the lead n + 1 steps, then move both until the lead runs out, and unlink the next node of the trailing pointer.",
    ],
    insight="A fixed gap of n nodes between two pointers turns \"nth from the end\" into a single pass.",
    time="O(length)", space="O(1)",
    pitfalls=["Removing the head (n equals the length) without a dummy node.", "Off-by-one in the gap between the pointers."],
)
def remove_nth(head, n):
    from catalog_lib import ListNode
    dummy = ListNode(0, head)
    lead = trail = dummy
    for _ in range(n + 1):
        lead = lead.next
    while lead:
        lead, trail = lead.next, trail.next
    trail.next = trail.next.next
    return dummy.next


def to_ln(values):
    from catalog_lib import to_list_node
    return to_list_node(values)


def from_ln(node):
    from catalog_lib import from_list_node
    return from_list_node(node)


@problem(
    slug="sort-colors", title="Sort Colors", difficulty="Medium", pattern=P, tags=["Array", "Two Pointers", "Sorting"],
    sig="sortColors(self, nums: list[int]) -> None", out_arg=0,
    desc="""`nums` contains only the values `0`, `1` and `2` (think red, white and blue). Sort it **in place** so that all 0s come first, then all 1s, then all 2s.

Don't use a library sort, and don't return anything: the judge checks `nums` after your function runs. Try for a single pass with constant extra space.""",
    constraints=["1 ≤ len(nums) ≤ 300", "nums[i] is 0, 1 or 2"],
    samples=[([2, 0, 2, 1, 1, 0],), ([2, 0, 1],), ([0],)],
    tests=[([1, 1, 1],), ([2, 2, 0, 0],)],
    gen=lambda r: (r.ints(r.randint(1, 60), 0, 2),),
    hints=[
        "Counting how many of each value works in two passes. Can you place values as you go?",
        "Keep three regions: everything before `low` is 0, everything after `high` is 2, and a pointer scans the middle.",
        "When the scanner sees 0, swap it to `low` and advance both. When it sees 2, swap it to `high` and shrink `high` without advancing the scanner. On 1, just advance.",
    ],
    insight="The Dutch national flag partition sorts three values in one pass with three pointers.",
    time="O(n)", space="O(1)",
    pitfalls=["Advancing the scanner after swapping a 2 in from the end: the swapped-in value hasn't been checked yet.", "Returning a new list instead of changing nums."],
)
def sort_colors(nums):
    low = mid = 0
    high = len(nums) - 1
    while mid <= high:
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]
            low += 1
            mid += 1
        elif nums[mid] == 2:
            nums[mid], nums[high] = nums[high], nums[mid]
            high -= 1
        else:
            mid += 1


@problem(
    slug="reverse-words-in-a-string", title="Reverse Words in a String", difficulty="Medium", pattern=P,
    tags=["String", "Two Pointers"],
    sig="reverseWords(self, s: str) -> str",
    desc="""A **word** is a run of non-space characters. Given a string `s`, return its words in reverse order, joined by single spaces.

`s` may have leading, trailing, or repeated spaces between words; none of those should appear in the result.""",
    constraints=["1 ≤ len(s) ≤ 10⁴", "s has English letters, digits and spaces", "s has at least one word"],
    samples=[("the sky is blue",), ("  hello world  ",), ("a good   example",)],
    gen=lambda r: (" " * r.randint(0, 2) + (" " * r.randint(1, 3)).join(r.words(r.randint(1, 8), 1, 6)) + " " * r.randint(0, 2),),
    brute=lambda s: " ".join(reversed(s.split())),
    hints=[
        "Break the problem into two parts: find the words, then output them backwards.",
        "Scan with an index, skipping spaces, and collect each maximal run of non-space characters.",
        "Collect the words in order, then join them in reverse with one space. (In-place versions reverse the whole string, then reverse each word.)",
    ],
    insight="Splitting on runs of spaces removes the extra spacing; reversing the word order is then simple.",
    time="O(n)", space="O(n)",
    pitfalls=["Producing empty words from repeated spaces.", "Leaving a trailing or leading space in the answer."],
)
def reverse_words(s):
    words, i = [], 0
    while i < len(s):
        if s[i] == " ":
            i += 1
            continue
        j = i
        while j < len(s) and s[j] != " ":
            j += 1
        words.append(s[i:j])
        i = j
    return " ".join(reversed(words))


@problem(
    slug="valid-word-abbreviation", title="Valid Word Abbreviation", difficulty="Easy", pattern=P,
    tags=["String", "Two Pointers"],
    sig="validWordAbbreviation(self, word: str, abbr: str) -> bool",
    desc="""An abbreviation replaces any number of non-adjacent, non-empty runs of characters in a word by their lengths. For example `"substitution"` can become `"s10n"` or `"sub4u4"`.

Numbers in an abbreviation may not have leading zeros (`"s010n"` is invalid), and adjacent runs can't both be replaced (that would look like one bigger number).

Return `True` if `abbr` is a valid abbreviation of `word`.""",
    constraints=["1 ≤ len(word) ≤ 20", "1 ≤ len(abbr) ≤ 10", "word has lowercase letters", "abbr has lowercase letters and digits"],
    samples=[("internationalization", "i12iz4n"), ("apple", "a2e"), ("substitution", "s010n")],
    tests=[("a", "01"), ("word", "4"), ("word", "w3"), ("word", "5"), ("hi", "1i1")],
    hints=[
        "Walk through both strings at the same time: one pointer in the word and one in the abbreviation.",
        "When the abbreviation has a letter, it must equal the current letter of the word. When it has a digit, read the whole number and skip that many letters in the word.",
        "A number that starts with 0 is invalid. At the end, both pointers must have reached the ends of their strings exactly.",
    ],
    insight="Two pointers let you match letters directly and jump over the counted runs.",
    time="O(len(abbr))", space="O(1)",
    pitfalls=["Accepting a leading zero, such as \"01\".", "Skipping past the end of the word without failing."],
)
def valid_word_abbreviation(word, abbr):
    i = j = 0
    while j < len(abbr):
        if abbr[j].isdigit():
            if abbr[j] == "0":
                return False
            k = j
            while k < len(abbr) and abbr[k].isdigit():
                k += 1
            i += int(abbr[j:k])
            j = k
        else:
            if i >= len(word) or word[i] != abbr[j]:
                return False
            i, j = i + 1, j + 1
    return i == len(word)


@problem(
    slug="valid-palindrome-ii", title="Valid Palindrome II", difficulty="Easy", pattern=P, tags=["String", "Two Pointers", "Greedy"],
    sig="validPalindrome(self, s: str) -> bool",
    desc="""Given a string `s`, return `True` if it can become a palindrome after deleting **at most one** character.""",
    constraints=["1 ≤ len(s) ≤ 10⁵", "s has lowercase English letters"],
    samples=[("aba",), ("abca",), ("abc",)],
    tests=[("deeee",), ("eccer",), ("cbbcc",)],
    gen=lambda r: (lambda w: (w[: r.randint(0, len(w))] + r.word(r.randint(0, 1)) + w[::-1],))(r.word(r.randint(1, 10), "abc")),
    brute=lambda s: any((t := s[:i] + s[i + 1:]) == t[::-1] for i in range(len(s))) or s == s[::-1],
    hints=[
        "Compare characters from both ends like a normal palindrome check. What should happen at the first mismatch?",
        "At a mismatch you're allowed one deletion: either the left character or the right one goes.",
        "On the first mismatch, check whether the remaining middle is a palindrome after skipping the left character, or after skipping the right one. Either working means True.",
    ],
    insight="Only the first mismatch matters; try both deletions there with a plain palindrome check.",
    time="O(n)", space="O(1)",
    pitfalls=["Trying only one of the two possible deletions.", "Deleting characters at every mismatch instead of only once."],
)
def valid_palindrome_ii(s):
    def pal(i, j):
        while i < j:
            if s[i] != s[j]:
                return False
            i, j = i + 1, j - 1
        return True

    i, j = 0, len(s) - 1
    while i < j:
        if s[i] != s[j]:
            return pal(i + 1, j) or pal(i, j - 1)
        i, j = i + 1, j - 1
    return True


@problem(
    slug="strobogrammatic-number", title="Strobogrammatic Number", difficulty="Easy", pattern=P, tags=["String", "Two Pointers", "Hash Table"],
    sig="isStrobogrammatic(self, num: str) -> bool",
    desc="""A number is **strobogrammatic** if it looks the same after being rotated 180 degrees (turned upside down). Under rotation `0`, `1` and `8` stay the same, `6` becomes `9`, `9` becomes `6`, and every other digit becomes unreadable.

Given a number as the string `num`, return `True` if it is strobogrammatic.""",
    constraints=["1 ≤ len(num) ≤ 50", "num has digits only, with no leading zeros except \"0\" itself"],
    samples=[("69",), ("88",), ("962",)],
    tests=[("1",), ("2",), ("609",), ("6889",), ("818",)],
    gen=lambda r: (str(r.randint(1, 10 ** r.randint(1, 8))),),
    hints=[
        "Rotation reverses the order of digits and flips each digit. Which digits survive the flip?",
        "Pair each digit with its rotated partner: 0↔0, 1↔1, 8↔8, 6↔9, 9↔6.",
        "Use two pointers from both ends: the left digit's rotated partner must equal the right digit. The middle digit of an odd-length number must be its own partner.",
    ],
    insight="Compare mirrored positions through a rotation map with two pointers.",
    time="O(n)", space="O(1)",
    pitfalls=["Treating 6 and 9 as self-symmetric.", "Forgetting the middle digit of odd-length numbers."],
)
def strobogrammatic(num):
    rot = {"0": "0", "1": "1", "8": "8", "6": "9", "9": "6"}
    i, j = 0, len(num) - 1
    while i <= j:
        if rot.get(num[i]) != num[j]:
            return False
        i, j = i + 1, j - 1
    return True


def _min_moves_brute(s):
    from collections import deque
    start = s
    seen, q = {start}, deque([(start, 0)])
    while q:
        cur, d = q.popleft()
        if cur == cur[::-1]:
            return d
        for i in range(len(cur) - 1):
            nxt = cur[:i] + cur[i + 1] + cur[i] + cur[i + 2:]
            if nxt not in seen:
                seen.add(nxt)
                q.append((nxt, d + 1))


def _palindromable(r, n):
    half = r.word(n // 2, "abcd")
    mid = r.word(n % 2, "abcd")
    chars = list(half + mid + half[::-1])
    r.shuffle(chars)
    return "".join(chars)


@problem(
    slug="minimum-number-of-moves-to-make-palindrome", title="Minimum Number of Moves to Make Palindrome", difficulty="Hard",
    pattern=P, tags=["String", "Two Pointers", "Greedy"],
    sig="minMovesToMakePalindrome(self, s: str) -> int",
    desc="""You are given a string `s` whose letters can be rearranged into a palindrome. In one move you may swap two **adjacent** characters.

Return the minimum number of moves needed to turn `s` into a palindrome.""",
    constraints=["1 ≤ len(s) ≤ 2000", "s has lowercase letters", "s can always be rearranged into a palindrome"],
    samples=[("aabb",), ("letelt",), ("abcba",)],
    tests=[("a",), ("aab",), ("abab",), ("baa",)],
    gen=lambda r: (_palindromable(r, r.randint(1, 8)),),
    brute=_min_moves_brute,
    hints=[
        "Look at the leftmost character. Its partner must end up at the rightmost position.",
        "Greedily fix the outermost pair: find the closest matching character from the right side and bubble it to the end, counting the swaps.",
        "If the left character has no partner (it's the single odd one), it belongs in the middle: move it one step toward the center and try again. Repeat on the shrinking middle.",
    ],
    insight="Fixing the two ends greedily with the nearest matching character is optimal, and adjacent swaps are counted by the distance moved.",
    time="O(n²)", space="O(n)",
    pitfalls=["Handling the odd-count character too early, which wastes swaps.", "Recomputing from scratch instead of shrinking the window."],
)
def min_moves_palindrome(s):
    s, moves = list(s), 0
    while len(s) > 1:
        j = len(s) - 1
        while s[j] != s[0]:
            j -= 1
        if j == 0:  # the odd character: move it one step toward the middle
            s[0], s[1] = s[1], s[0]
            moves += 1
            continue
        moves += len(s) - 1 - j
        s.pop(j)
        s.pop(0)
    return moves


def _next_pal_brute(num):
    n = len(num)
    half = num[: n // 2]
    best = None
    for p in set(permutations(half)):
        cand_half = "".join(p)
        cand = cand_half + num[n // 2: n - n // 2] + cand_half[::-1]
        if cand > num and (best is None or cand < best):
            best = cand
    return best or ""


def _palindrome_digits(r):
    half = "".join(r.choice("123456789") for _ in range(r.randint(1, 5)))
    mid = r.choice(["", r.choice("0123456789")])
    return half + mid + half[::-1]


@problem(
    slug="next-palindrome-using-same-digits", title="Next Palindrome Using Same Digits", difficulty="Hard", pattern=P,
    tags=["String", "Two Pointers"],
    sig="nextPalindrome(self, num: str) -> str",
    desc="""`num` is a very large palindrome written as a string of digits. Return the **smallest palindrome larger than `num`** that uses exactly the same digits (rearranged). If there isn't one, return an empty string.""",
    constraints=["1 ≤ len(num) ≤ 10⁵", "num is a palindrome of digits"],
    samples=[("1221",), ("32123",), ("45544554",)],
    tests=[("1",), ("11",), ("121",), ("123321",), ("9889",)],
    gen=lambda r: (_palindrome_digits(r),),
    brute=_next_pal_brute,
    hints=[
        "A palindrome is determined by its first half (plus a middle digit when the length is odd).",
        "So the next palindrome comes from the next larger arrangement of the first half's digits.",
        "Compute the next permutation of the first half. If none exists, there's no answer. Otherwise mirror it onto the second half and keep the middle digit.",
    ],
    insight="Making the palindrome larger means making its first half larger by as little as possible: that's next permutation.",
    time="O(n)", space="O(n)",
    pitfalls=["Permuting the whole string instead of only the first half.", "Moving the middle digit of an odd-length palindrome."],
)
def next_palindrome(num):
    n = len(num)
    half = list(num[: n // 2])
    i = len(half) - 2
    while i >= 0 and half[i] >= half[i + 1]:
        i -= 1
    if i < 0:
        return ""
    j = len(half) - 1
    while half[j] <= half[i]:
        j -= 1
    half[i], half[j] = half[j], half[i]
    half[i + 1:] = reversed(half[i + 1:])
    h = "".join(half)
    return h + num[n // 2: n - n // 2] + h[::-1]


def _fixed_bounds_brute(nums, minK, maxK):
    count = 0
    for i in range(len(nums)):
        for j in range(i, len(nums)):
            sub = nums[i:j + 1]
            count += min(sub) == minK and max(sub) == maxK
    return count


@problem(
    slug="count-subarrays-with-fixed-bounds", title="Count Subarrays With Fixed Bounds", difficulty="Hard", pattern=P,
    tags=["Array", "Two Pointers", "Sliding Window"],
    sig="countSubarrays(self, nums: list[int], minK: int, maxK: int) -> int",
    desc="""A **fixed-bound subarray** of `nums` is a contiguous subarray whose minimum is exactly `minK` and whose maximum is exactly `maxK`.

Return the number of fixed-bound subarrays.""",
    constraints=["2 ≤ len(nums) ≤ 10⁵", "1 ≤ nums[i], minK, maxK ≤ 10⁶"],
    samples=[([1, 3, 5, 2, 7, 5], 1, 5), ([1, 1, 1, 1], 1, 1)],
    tests=[([2, 2, 2], 1, 2), ([5, 1, 5, 1], 1, 5)],
    gen=lambda r: (r.ints(r.randint(2, 40), 1, 6), r.randint(1, 3), r.randint(3, 6)),
    brute=_fixed_bounds_brute,
    hints=[
        "Any element outside [minK, maxK] can never be inside a valid subarray, so it splits the array.",
        "For each right end, track the latest index of minK, the latest index of maxK, and the latest invalid element.",
        "A subarray ending at the current index is valid when it starts after the last invalid element and no later than both the last minK and last maxK. Add max(0, min(lastMin, lastMax) − lastBad) each step.",
    ],
    insight="Remembering three positions per step counts all valid subarrays ending at each index in O(1).",
    time="O(n)", space="O(1)",
    pitfalls=["Counting subarrays that cross an out-of-range element.", "Forgetting the case minK == maxK."],
)
def fixed_bounds(nums, minK, maxK):
    last_min = last_max = last_bad = -1
    total = 0
    for i, x in enumerate(nums):
        if x < minK or x > maxK:
            last_bad = i
        if x == minK:
            last_min = i
        if x == maxK:
            last_max = i
        total += max(0, min(last_min, last_max) - last_bad)
    return total


def _box_brute(word, k):
    best = ""
    n = len(word)

    def split(start, parts, acc):
        nonlocal best
        if parts == 1:
            for piece in acc + [word[start:]]:
                best = max(best, piece)
            return
        for end in range(start + 1, n - parts + 2):
            split(end, parts - 1, acc + [word[start:end]])

    split(0, k, [])
    return best


@problem(
    slug="find-the-lexicographically-largest-string-from-the-box-ii", title="Find the Lexicographically Largest String From the Box II",
    difficulty="Hard", pattern=P, tags=["String", "Two Pointers"],
    sig="answerString(self, word: str, numFriends: int) -> str",
    desc="""`word` is split into exactly `numFriends` non-empty consecutive pieces, in every possible way. All pieces from all splits go into a box.

Return the **lexicographically largest** string in the box.""",
    constraints=["1 ≤ len(word) ≤ 5000", "1 ≤ numFriends ≤ len(word)", "word has lowercase letters"],
    samples=[("dbca", 2), ("gggg", 4), ("abc", 1)],
    tests=[("zza", 2), ("aba", 2), ("cbacb", 3)],
    gen=lambda r: (lambda w: (w, r.randint(1, len(w))))(r.word(r.randint(1, 9), "abc")),
    brute=_box_brute,
    hints=[
        "With one friend the answer is the whole word. Otherwise, how long can a single piece be?",
        "A piece can be at most len(word) − numFriends + 1 characters long, and a longer piece with the same prefix is larger, so the best piece starting at i is as long as allowed.",
        "Find the lexicographically largest suffix of the word (two pointers comparing candidate starts), then cut it to the maximum allowed length.",
    ],
    insight="The answer is the largest suffix, truncated to the longest length a piece can have.",
    time="O(n)", space="O(1)",
    pitfalls=["Forgetting the numFriends = 1 case.", "Comparing all substrings, which is O(n²) or worse."],
)
def answer_string(word, numFriends):
    if numFriends == 1:
        return word
    n = len(word)
    i, j, k = 0, 1, 0
    while j + k < n:
        if word[i + k] == word[j + k]:
            k += 1
        elif word[i + k] > word[j + k]:
            j, k = j + k + 1, 0
        else:
            i, j, k = max(i + k + 1, j), max(i + k + 1, j) + 1, 0
    return word[i: i + n - numFriends + 1]


def _max_score_brute(nums1, nums2):
    MOD = 10**9 + 7
    from functools import lru_cache
    pos = [{v: i for i, v in enumerate(nums1)}, {v: i for i, v in enumerate(nums2)}]
    arrs = [nums1, nums2]

    @lru_cache(None)
    def best(a, i):
        v = arrs[a][i]
        options = [v + (best(a, i + 1) if i + 1 < len(arrs[a]) else 0)]
        other = pos[1 - a].get(v)
        if other is not None:
            options.append(v + (best(1 - a, other + 1) if other + 1 < len(arrs[1 - a]) else 0))
        return max(options)

    return max(best(0, 0), best(1, 0)) % MOD


@problem(
    slug="get-the-maximum-score", title="Get the Maximum Score", difficulty="Hard", pattern=P,
    tags=["Array", "Two Pointers", "Dynamic Programming"],
    sig="maxSum(self, nums1: list[int], nums2: list[int]) -> int",
    desc="""`nums1` and `nums2` are sorted arrays of distinct integers. A **path** starts at the beginning of either array and moves left to right. Whenever you reach a value that exists in both arrays, you may switch to the other array (continuing from that value).

A path's score is the sum of the distinct values it visits. Return the maximum score, modulo `10⁹ + 7`.""",
    constraints=["1 ≤ len(nums1), len(nums2) ≤ 10⁵", "1 ≤ nums[i] ≤ 10⁷", "both arrays are strictly increasing"],
    samples=[([2, 4, 5, 8, 10], [4, 6, 8, 9]), ([1, 3, 5, 7, 9], [3, 5, 100]), ([1, 2, 3, 4, 5], [6, 7, 8, 9, 10])],
    gen=lambda r: (sorted(r.distinct(r.randint(1, 10), 1, 30)), sorted(r.distinct(r.randint(1, 10), 1, 30))),
    brute=_max_score_brute,
    hints=[
        "Shared values split both arrays into segments. Between two shared values, you're on one array or the other.",
        "Walk both arrays with two pointers, keeping the running sum of each since the last shared value.",
        "At a shared value, keep the larger of the two running sums, add the shared value, and reset both. At the end, take the larger of the two remaining sums. Apply the modulo only at the very end.",
    ],
    insight="Each segment between common values is chosen independently, so pick the heavier side every time.",
    time="O(n + m)", space="O(1)",
    pitfalls=["Taking the modulo before comparing the two sums.", "Counting a shared value twice."],
)
def max_score(nums1, nums2):
    i = j = s1 = s2 = 0
    while i < len(nums1) or j < len(nums2):
        if j == len(nums2) or (i < len(nums1) and nums1[i] < nums2[j]):
            s1 += nums1[i]
            i += 1
        elif i == len(nums1) or nums2[j] < nums1[i]:
            s2 += nums2[j]
            j += 1
        else:
            s1 = s2 = max(s1, s2) + nums1[i]
            i, j = i + 1, j + 1
    return max(s1, s2) % (10**9 + 7)


def _max_number_brute(nums1, nums2, k):
    best = []
    for a in range(0, k + 1):
        b = k - a
        if a > len(nums1) or b > len(nums2):
            continue
        for ia in combinations(range(len(nums1)), a):
            for ib in combinations(range(len(nums2)), b):
                s1 = [nums1[i] for i in ia]
                s2 = [nums2[i] for i in ib]

                def merges(x, y):
                    if not x:
                        yield list(y)
                        return
                    if not y:
                        yield list(x)
                        return
                    for rest in merges(x[1:], y):
                        yield [x[0]] + rest
                    for rest in merges(x, y[1:]):
                        yield [y[0]] + rest

                for m in merges(s1, s2):
                    best = max(best, m)
    return best


@problem(
    slug="create-maximum-number", title="Create Maximum Number", difficulty="Hard", pattern=P,
    tags=["Array", "Stack", "Greedy", "Two Pointers"],
    sig="maxNumber(self, nums1: list[int], nums2: list[int], k: int) -> list[int]",
    desc="""`nums1` and `nums2` hold the digits of two numbers. Build the **largest possible number of exactly `k` digits** by picking digits from both arrays, keeping the relative order of the digits taken from the same array.

Return the answer as a list of its `k` digits.""",
    constraints=["1 ≤ len(nums1), len(nums2) ≤ 500", "0 ≤ digits ≤ 9", "1 ≤ k ≤ len(nums1) + len(nums2)"],
    samples=[([3, 4, 6, 5], [9, 1, 2, 5, 8, 3], 5), ([6, 7], [6, 0, 4], 5), ([3, 9], [8, 9], 3)],
    gen=lambda r: (lambda a, b: (a, b, r.randint(1, len(a) + len(b))))(r.ints(r.randint(1, 4), 0, 9), r.ints(r.randint(1, 4), 0, 9)),
    brute=_max_number_brute,
    hints=[
        "Split the problem: take i digits from nums1 and k − i from nums2, for every feasible i.",
        "The largest subsequence of a fixed length from one array comes from a monotonic stack that drops smaller digits while enough digits remain.",
        "Merge the two picked subsequences greedily by always taking from the one whose remaining suffix is lexicographically larger, then keep the best result over all i.",
    ],
    insight="Combine three classic pieces: max subsequence by stack, greedy merge by comparing suffixes, and trying every split.",
    time="O(k · (m + n)²) in the simple merge", space="O(m + n)",
    pitfalls=["Merging by comparing only the next digits: ties must compare the whole remaining suffixes."],
)
def max_number(nums1, nums2, k):
    def pick(nums, t):
        drop, stack = len(nums) - t, []
        for x in nums:
            while drop and stack and stack[-1] < x:
                stack.pop()
                drop -= 1
            stack.append(x)
        return stack[:t]

    def merge(a, b):
        return [max(a, b).pop(0) for _ in a + b]

    best = []
    for i in range(max(0, k - len(nums2)), min(k, len(nums1)) + 1):
        best = max(best, merge(pick(nums1, i), pick(nums2, k - i)))
    return best


def _next_perm_brute(nums):
    perms = sorted(set(permutations(nums)))
    idx = perms.index(tuple(nums))
    nxt = perms[(idx + 1) % len(perms)]
    nums[:] = list(nxt)


@problem(
    slug="next-permutation", title="Next Permutation", difficulty="Medium", pattern=P, tags=["Array", "Two Pointers"],
    sig="nextPermutation(self, nums: list[int]) -> None", out_arg=0,
    desc="""Rearrange `nums` **in place** into the next permutation in lexicographic order: the smallest arrangement that is larger than the current one. If `nums` is already the largest arrangement, rearrange it into the smallest (sorted ascending).

Return nothing; the judge checks `nums`. Use only constant extra memory.""",
    constraints=["1 ≤ len(nums) ≤ 100", "0 ≤ nums[i] ≤ 100"],
    samples=[([1, 2, 3],), ([3, 2, 1],), ([1, 1, 5],)],
    tests=[([1],), ([1, 3, 2],), ([2, 3, 1],)],
    gen=lambda r: (r.ints(r.randint(1, 6), 0, 3),),
    brute=_next_perm_brute,
    hints=[
        "To make the number just a bit larger, change it as far to the right as possible.",
        "From the right, find the first position where nums[i] < nums[i + 1]. Everything after it is in decreasing order.",
        "Swap nums[i] with the smallest larger element to its right (scan from the end), then reverse the suffix after i. If no such i exists, reverse the whole array.",
    ],
    insight="Find the rightmost ascent, bump it up minimally, and make the suffix as small as possible.",
    time="O(n)", space="O(1)",
    pitfalls=["Sorting the suffix instead of reversing it (it's already in descending order).", "Not handling the last permutation."],
)
def next_permutation(nums):
    i = len(nums) - 2
    while i >= 0 and nums[i] >= nums[i + 1]:
        i -= 1
    if i >= 0:
        j = len(nums) - 1
        while nums[j] <= nums[i]:
            j -= 1
        nums[i], nums[j] = nums[j], nums[i]
    nums[i + 1:] = reversed(nums[i + 1:])


@problem(
    slug="rotate-array", title="Rotate Array", difficulty="Medium", pattern=P, tags=["Array", "Two Pointers", "Math"],
    sig="rotate(self, nums: list[int], k: int) -> None", out_arg=0,
    desc="""Rotate `nums` to the right by `k` steps, **in place**: each step moves the last element to the front.

Return nothing; the judge checks `nums`. Can you do it with O(1) extra space?""",
    constraints=["1 ≤ len(nums) ≤ 10⁵", "-2³¹ ≤ nums[i] ≤ 2³¹ − 1", "0 ≤ k ≤ 10⁵"],
    samples=[([1, 2, 3, 4, 5, 6, 7], 3), ([-1, -100, 3, 99], 2)],
    tests=[([1], 5), ([1, 2], 3), ([1, 2, 3], 0)],
    gen=lambda r: (r.ints(r.randint(1, 30), -50, 50), r.randint(0, 60)),
    brute=lambda nums, k: nums.__setitem__(slice(None), [nums[(i - k) % len(nums)] for i in range(len(nums))]),
    hints=[
        "Rotating by len(nums) does nothing, so only k mod n matters.",
        "Rotating right by k moves the last k elements to the front. Can reversals do that?",
        "Reverse the whole array, then reverse the first k elements, then reverse the rest.",
    ],
    insight="Three reversals rotate an array in place with O(1) space.",
    time="O(n)", space="O(1)",
    pitfalls=["Forgetting k can be larger than the length.", "Building a new list and rebinding nums instead of modifying it."],
)
def rotate_array(nums, k):
    n = len(nums)
    k %= n

    def rev(i, j):
        while i < j:
            nums[i], nums[j] = nums[j], nums[i]
            i, j = i + 1, j - 1

    rev(0, n - 1)
    rev(0, k - 1)
    rev(k, n - 1)


@problem(
    slug="append-characters-to-string-to-make-subsequence", title="Append Characters to String to Make Subsequence",
    difficulty="Medium", pattern=P, tags=["String", "Two Pointers", "Greedy"],
    sig="appendCharacters(self, s: str, t: str) -> int",
    desc="""Return the minimum number of characters you must append to the **end** of `s` so that `t` becomes a subsequence of `s`.

A subsequence keeps the order of characters but may skip some.""",
    constraints=["1 ≤ len(s), len(t) ≤ 10⁵", "s and t have lowercase letters"],
    samples=[("coaching", "coding"), ("abcde", "a"), ("z", "abcde")],
    gen=lambda r: (r.word(r.randint(1, 15), "abc"), r.word(r.randint(1, 8), "abc")),
    hints=[
        "Whatever prefix of t already appears in s as a subsequence doesn't need to be appended.",
        "Greedily match t against s from the left: each character of s either matches the next needed character of t or is skipped.",
        "Scan s with one pointer and advance a pointer in t on every match. The answer is the number of t characters left unmatched.",
    ],
    insight="Greedy matching finds the longest prefix of t that's already a subsequence of s.",
    time="O(len(s) + len(t))", space="O(1)",
    pitfalls=["Looking for t as a contiguous substring instead of a subsequence."],
)
def append_characters(s, t):
    j = 0
    for c in s:
        if j < len(t) and c == t[j]:
            j += 1
    return len(t) - j


@problem(
    slug="squares-of-a-sorted-array", title="Squares of a Sorted Array", difficulty="Easy", pattern=P,
    tags=["Array", "Two Pointers", "Sorting"],
    sig="sortedSquares(self, nums: list[int]) -> list[int]",
    desc="""`nums` is sorted in non-decreasing order and may contain negative numbers. Return the squares of its elements, also sorted in non-decreasing order.

Sorting the squares is O(n log n); try for O(n).""",
    constraints=["1 ≤ len(nums) ≤ 10⁴", "-10⁴ ≤ nums[i] ≤ 10⁴"],
    samples=[([-4, -1, 0, 3, 10],), ([-7, -3, 2, 3, 11],)],
    tests=[([1],), ([-5, -3, -2],)],
    gen=lambda r: (r.sorted_ints(r.randint(1, 40), -30, 30),),
    brute=lambda nums: sorted(x * x for x in nums),
    hints=[
        "The largest square comes from one of the two ends of the array: the most negative or the most positive number.",
        "Use two pointers at the ends and compare their absolute values.",
        "Fill the result from the back: place the larger square at the last free position and move that pointer inward.",
    ],
    insight="The biggest squares are at the ends, so filling the output from the back with two pointers gives O(n).",
    time="O(n)", space="O(n) for the output",
    pitfalls=["Assuming the squares are already sorted when negatives are present."],
)
def sorted_squares(nums):
    out = [0] * len(nums)
    i, j = 0, len(nums) - 1
    for pos in range(len(nums) - 1, -1, -1):
        if abs(nums[i]) > abs(nums[j]):
            out[pos] = nums[i] ** 2
            i += 1
        else:
            out[pos] = nums[j] ** 2
            j -= 1
    return out


@problem(
    slug="reverse-string", title="Reverse String", difficulty="Easy", pattern=P, tags=["String", "Two Pointers"],
    sig="reverseString(self, s: list[str]) -> None", out_arg=0,
    desc="""`s` is a list of characters. Reverse it **in place** using O(1) extra memory.

Return nothing; the judge checks `s`.""",
    constraints=["1 ≤ len(s) ≤ 10⁵", "s[i] is a printable ASCII character"],
    samples=[(list("hello"),), (list("Hannah"),)],
    tests=[(["a"],), (list("ab"),)],
    gen=lambda r: (list(r.word(r.randint(1, 20))),),
    brute=lambda s: s.reverse(),
    hints=[
        "The first and last characters trade places, then the second and second-to-last, and so on.",
        "Use two pointers starting at both ends.",
        "Swap the characters at the two pointers and move them toward each other until they meet.",
    ],
    insight="Swapping mirrored positions with two pointers reverses in place.",
    time="O(n)", space="O(1)",
    pitfalls=["Rebinding s to a new reversed list instead of changing the given one."],
)
def reverse_string(s):
    i, j = 0, len(s) - 1
    while i < j:
        s[i], s[j] = s[j], s[i]
        i, j = i + 1, j - 1


@problem(
    slug="partition-labels", title="Partition Labels", difficulty="Medium", pattern=P, tags=["String", "Two Pointers", "Greedy"],
    sig="partitionLabels(self, s: str) -> list[int]",
    desc="""Split `s` into as many pieces as possible so that each letter appears in **at most one** piece. Joining the pieces in order must give back `s`.

Return the sizes of the pieces, in order.""",
    constraints=["1 ≤ len(s) ≤ 500", "s has lowercase letters"],
    samples=[("ababcbacadefegdehijhklij",), ("eccbbbbdec",)],
    tests=[("a",), ("abc",), ("abab",)],
    gen=lambda r: (r.word(r.randint(1, 30), "abcdefgh"),),
    hints=[
        "A piece that contains a letter must extend at least to that letter's last occurrence.",
        "Precompute the last index of every letter.",
        "Scan left to right, stretching the current piece's end to the last occurrence of each letter you see. When the scan reaches that end, close the piece.",
    ],
    insight="The current piece ends exactly when the scan catches up to the furthest last-occurrence seen so far.",
    time="O(n)", space="O(1) for 26 letters",
    pitfalls=["Closing a piece before reaching the last occurrence of every letter in it."],
)
def partition_labels(s):
    last = {c: i for i, c in enumerate(s)}
    out, start, end = [], 0, 0
    for i, c in enumerate(s):
        end = max(end, last[c])
        if i == end:
            out.append(end - start + 1)
            start = i + 1
    return out


@problem(
    slug="remove-element", title="Remove Element", difficulty="Easy", pattern=P, tags=["Array", "Two Pointers"],
    sig="removeElement(self, nums: list[int], val: int) -> list[int]",
    desc="""Remove every occurrence of `val` from `nums` **in place**: move the elements you keep to the front of the array, in their original order, using O(1) extra space.

In this version, return the kept prefix (`nums[:k]`, where `k` is the number of kept elements).""",
    constraints=["0 ≤ len(nums) ≤ 100", "0 ≤ nums[i] ≤ 50", "0 ≤ val ≤ 100"],
    samples=[([3, 2, 2, 3], 3), ([0, 1, 2, 2, 3, 0, 4, 2], 2)],
    tests=[([], 1), ([1, 1, 1], 1), ([4, 5], 6)],
    gen=lambda r: (r.ints(r.randint(0, 25), 0, 5), r.randint(0, 5)),
    brute=lambda nums, val: [x for x in nums if x != val],
    hints=[
        "You don't need a second array: kept elements can overwrite the front of nums.",
        "Use a write pointer for the next free slot and a read pointer that scans every element.",
        "Whenever the read pointer sees a value different from val, copy it to the write position and advance the write pointer. The kept prefix ends at the write pointer.",
    ],
    insight="A read pointer and a write pointer compact an array in one pass.",
    time="O(n)", space="O(1)",
    pitfalls=["Removing elements with list.remove inside a loop, which is O(n²) and skips elements."],
)
def remove_element(nums, val):
    w = 0
    for x in nums:
        if x != val:
            nums[w] = x
            w += 1
    return nums[:w]


def _compress_brute(chars):
    out, i = [], 0
    while i < len(chars):
        j = i
        while j < len(chars) and chars[j] == chars[i]:
            j += 1
        out.append(chars[i])
        if j - i > 1:
            out.extend(str(j - i))
        i = j
    return out


@problem(
    slug="string-compression", title="String Compression", difficulty="Medium", pattern=P, tags=["String", "Two Pointers"],
    sig="compress(self, chars: list[str]) -> list[str]",
    desc="""Compress the list of characters `chars` **in place**: replace each run of a repeated character by the character, followed by the run length if it's more than 1. A length like 12 is written as the two characters `"1"` and `"2"`.

Use O(1) extra space. In this version, return the compressed prefix of `chars`.""",
    constraints=["1 ≤ len(chars) ≤ 2000", "chars[i] is a letter, digit or symbol"],
    samples=[(list("aabbccc"),), (["a"],), (list("abbbbbbbbbbbb"),)],
    gen=lambda r: (list("".join(r.choice("abc") * r.randint(1, 13) for _ in range(r.randint(1, 5)))),),
    brute=_compress_brute,
    hints=[
        "The compressed form is never longer than the original, so you can write it over the front of the same list.",
        "Read with one pointer to find the end of each run; write with another pointer.",
        "For each run, write its character, then the digits of its length if the length is more than 1. Return the written prefix.",
    ],
    insight="Run-length encoding fits in place because the output can't outrun the reader.",
    time="O(n)", space="O(1)",
    pitfalls=["Writing a count of 1.", "Writing a two-digit count as a single item instead of two characters."],
)
def compress(chars):
    w = i = 0
    while i < len(chars):
        j = i
        while j < len(chars) and chars[j] == chars[i]:
            j += 1
        chars[w] = chars[i]
        w += 1
        if j - i > 1:
            for d in str(j - i):
                chars[w] = d
                w += 1
        i = j
    return chars[:w]


@problem(
    slug="remove-duplicates-from-sorted-array", title="Remove Duplicates from Sorted Array", difficulty="Easy", pattern=P,
    tags=["Array", "Two Pointers"],
    sig="removeDuplicates(self, nums: list[int]) -> list[int]",
    desc="""`nums` is sorted in non-decreasing order. Remove the duplicates **in place** so each value appears once, keeping the order, and using O(1) extra space.

In this version, return the de-duplicated prefix of `nums`.""",
    constraints=["1 ≤ len(nums) ≤ 3 × 10⁴", "-100 ≤ nums[i] ≤ 100", "nums is sorted"],
    samples=[([1, 1, 2],), ([0, 0, 1, 1, 1, 2, 2, 3, 3, 4],)],
    tests=[([5],), ([2, 2, 2],)],
    gen=lambda r: (r.sorted_ints(r.randint(1, 30), -5, 5),),
    brute=lambda nums: sorted(set(nums)),
    hints=[
        "Because the array is sorted, duplicates sit next to each other.",
        "Keep a write pointer for where the next new value goes.",
        "Scan the array; whenever a value differs from the last written value, write it and advance the write pointer.",
    ],
    insight="Sorted input means a value is new exactly when it differs from the previous kept value.",
    time="O(n)", space="O(1)",
    pitfalls=["Comparing with the previous element of the original array after it was overwritten."],
)
def remove_duplicates(nums):
    w = 1
    for i in range(1, len(nums)):
        if nums[i] != nums[w - 1]:
            nums[w] = nums[i]
            w += 1
    return nums[:w]


@problem(
    slug="reverse-vowels-of-a-string", title="Reverse Vowels of a String", difficulty="Easy", pattern=P, tags=["String", "Two Pointers"],
    sig="reverseVowels(self, s: str) -> str",
    desc="""Reverse only the vowels of `s` (`a e i o u`, in lowercase or uppercase) and return the result. All other characters stay where they are.""",
    constraints=["1 ≤ len(s) ≤ 3 × 10⁵", "s has printable ASCII characters"],
    samples=[("IceCreAm",), ("leetcode",)],
    tests=[("a",), ("bcd",), ("aA",)],
    gen=lambda r: (r.word(r.randint(1, 25), "aeiouAEbcdxyz "),),
    brute=lambda s: (lambda v: "".join(v.pop() if c in "aeiouAEIOU" else c for c in s))([c for c in s if c in "aeiouAEIOU"]),
    hints=[
        "Only vowel positions change. Which vowel ends up at the first vowel position?",
        "Use two pointers from both ends, each stopping only at vowels.",
        "When both pointers are on vowels, swap them and move both inward. Remember uppercase vowels count too.",
    ],
    insight="Two pointers that skip consonants swap vowels pairwise from the outside in.",
    time="O(n)", space="O(n) for the result string",
    pitfalls=["Ignoring uppercase vowels."],
)
def reverse_vowels(s):
    chars, vowels = list(s), set("aeiouAEIOU")
    i, j = 0, len(chars) - 1
    while i < j:
        if chars[i] not in vowels:
            i += 1
        elif chars[j] not in vowels:
            j -= 1
        else:
            chars[i], chars[j] = chars[j], chars[i]
            i, j = i + 1, j - 1
    return "".join(chars)


@problem(
    slug="is-subsequence", title="Is Subsequence", difficulty="Easy", pattern=P, tags=["String", "Two Pointers"],
    sig="isSubsequence(self, s: str, t: str) -> bool",
    desc="""Return `True` if `s` is a **subsequence** of `t`: you can delete some (or no) characters of `t`, without reordering the rest, to get `s`.""",
    constraints=["0 ≤ len(s) ≤ 100", "0 ≤ len(t) ≤ 10⁴", "both have lowercase letters"],
    samples=[("abc", "ahbgdc"), ("axc", "ahbgdc")],
    tests=[("", "abc"), ("a", ""), ("aaa", "aa")],
    gen=lambda r: (r.word(r.randint(0, 4), "abc"), r.word(r.randint(0, 12), "abc")),
    hints=[
        "Match the characters of s in order while scanning t once.",
        "Keep a pointer to the next character of s you still need.",
        "Advance through t; whenever t's character equals the needed one, move the s pointer. s is a subsequence if that pointer reaches its end.",
    ],
    insight="Greedily matching each character at its earliest possible position is always safe.",
    time="O(len(t))", space="O(1)",
    pitfalls=["Forgetting that the empty string is a subsequence of anything."],
)
def is_subsequence(s, t):
    i = 0
    for c in t:
        if i < len(s) and s[i] == c:
            i += 1
    return i == len(s)


@problem(
    slug="merge-strings-alternately", title="Merge Strings Alternately", difficulty="Easy", pattern=P, tags=["String", "Two Pointers"],
    sig="mergeAlternately(self, word1: str, word2: str) -> str",
    desc="""Merge `word1` and `word2` by alternating their letters, starting with `word1`. If one word is longer, append its leftover letters at the end.""",
    constraints=["1 ≤ len(word1), len(word2) ≤ 100", "lowercase letters"],
    samples=[("abc", "pqr"), ("ab", "pqrs"), ("abcd", "pq")],
    gen=lambda r: (r.word(r.randint(1, 8)), r.word(r.randint(1, 8))),
    hints=[
        "Walk both words with one index at the same time.",
        "At each index, take the letter from word1 (if any) and then from word2 (if any).",
        "Continue until the index passes the end of the longer word.",
    ],
    insight="A single loop up to the longer length handles the leftover tail naturally.",
    time="O(n + m)", space="O(n + m)",
    pitfalls=["Dropping the tail of the longer word."],
)
def merge_alternately(word1, word2):
    out = []
    for i in range(max(len(word1), len(word2))):
        if i < len(word1):
            out.append(word1[i])
        if i < len(word2):
            out.append(word2[i])
    return "".join(out)


@problem(
    slug="compare-version-numbers", title="Compare Version Numbers", difficulty="Medium", pattern=P, tags=["String", "Two Pointers"],
    sig="compareVersion(self, version1: str, version2: str) -> int",
    desc="""A version number is a list of revisions separated by dots, like `"1.0.12"`. Each revision is a number that may have leading zeros (`"01"` equals `1`). Missing revisions count as 0.

Compare the versions revision by revision from the left: return `-1` if `version1` is smaller, `1` if it's larger, and `0` if they're equal.""",
    constraints=["1 ≤ length ≤ 500", "only digits and dots", "every revision fits in a 32-bit integer"],
    samples=[("1.2", "1.10"), ("1.01", "1.001"), ("1.0", "1.0.0.0")],
    tests=[("0.1", "1.1"), ("1.0.1", "1"), ("7.5.2.4", "7.5.3")],
    gen=lambda r: tuple(".".join(str(r.randint(0, 3)).zfill(r.randint(1, 2)) for _ in range(r.randint(1, 4))) for _ in range(2)),
    hints=[
        "Compare one revision at a time, as numbers rather than strings.",
        "When one version runs out of revisions, treat its missing revisions as 0.",
        "Read each revision's digits with a pointer up to the next dot, convert to an integer (which drops leading zeros), and compare. Return at the first difference.",
    ],
    insight="Parsing revisions as integers handles leading zeros, and padding with zeros handles different lengths.",
    time="O(n + m)", space="O(1) with pointers",
    pitfalls=["Comparing revisions as strings, where \"10\" < \"9\"."],
)
def compare_version(version1, version2):
    a, b = version1.split("."), version2.split(".")
    for i in range(max(len(a), len(b))):
        x = int(a[i]) if i < len(a) else 0
        y = int(b[i]) if i < len(b) else 0
        if x != y:
            return -1 if x < y else 1
    return 0


@problem(
    slug="move-zeroes", title="Move Zeroes", difficulty="Easy", pattern=P, tags=["Array", "Two Pointers"],
    sig="moveZeroes(self, nums: list[int]) -> None", out_arg=0,
    desc="""Move every `0` in `nums` to the end, **in place**, keeping the relative order of the non-zero elements.

Return nothing; the judge checks `nums`.""",
    constraints=["1 ≤ len(nums) ≤ 10⁴", "-2³¹ ≤ nums[i] ≤ 2³¹ − 1"],
    samples=[([0, 1, 0, 3, 12],), ([0],)],
    tests=[([1, 2, 3],), ([0, 0, 1],)],
    gen=lambda r: (r.ints(r.randint(1, 30), -3, 3),),
    brute=lambda nums: nums.__setitem__(slice(None), [x for x in nums if x] + [0] * nums.count(0)),
    hints=[
        "Non-zero values keep their order, so they can be packed to the front one by one.",
        "Use a write pointer marking where the next non-zero value goes.",
        "Swap each non-zero value into the write position and advance it. The zeros naturally end up behind.",
    ],
    insight="Compacting the non-zeros forward with a write pointer leaves the zeros at the end.",
    time="O(n)", space="O(1)",
    pitfalls=["Creating a new list instead of changing nums."],
)
def move_zeroes(nums):
    w = 0
    for i in range(len(nums)):
        if nums[i]:
            nums[w], nums[i] = nums[i], nums[w]
            w += 1


@problem(
    slug="longest-subarray-of-1s-after-deleting-one-element", title="Longest Subarray of 1's After Deleting One Element",
    difficulty="Medium", pattern=P, tags=["Array", "Sliding Window"],
    sig="longestSubarray(self, nums: list[int]) -> int",
    desc="""`nums` contains only 0s and 1s. You must delete **exactly one** element. Return the length of the longest non-empty run of 1s you can get afterwards (or 0 if there are no 1s).""",
    constraints=["1 ≤ len(nums) ≤ 10⁵", "nums[i] is 0 or 1"],
    samples=[([1, 1, 0, 1],), ([0, 1, 1, 1, 0, 1, 1, 0, 1],), ([1, 1, 1],)],
    tests=[([0],), ([0, 0],), ([1],)],
    gen=lambda r: (r.ints(r.randint(1, 30), 0, 1),),
    brute=lambda nums: max(max((len(run) for run in "".join(map(str, nums[:i] + nums[i + 1:])).split("0")), default=0) for i in range(len(nums))),
    hints=[
        "Deleting one zero joins the runs of 1s on its two sides.",
        "Look for the longest window that contains at most one zero.",
        "Slide a window, shrinking it from the left whenever it holds two zeros. The answer is the largest window size minus one (the deleted element).",
    ],
    insight="A window with at most one zero, minus one deleted element, is the run you can form.",
    time="O(n)", space="O(1)",
    pitfalls=["Forgetting that an all-1s array still requires deleting one element."],
)
def longest_ones_after_delete(nums):
    left = zeros = best = 0
    for right, x in enumerate(nums):
        zeros += x == 0
        while zeros > 1:
            zeros -= nums[left] == 0
            left += 1
        best = max(best, right - left)
    return best


def _backspace(s):
    out = []
    for c in s:
        if c == "#":
            if out:
                out.pop()
        else:
            out.append(c)
    return out


@problem(
    slug="backspace-string-compare", title="Backspace String Compare", difficulty="Easy", pattern=P, tags=["String", "Two Pointers", "Stack"],
    sig="backspaceCompare(self, s: str, t: str) -> bool",
    desc="""`s` and `t` are typed into empty text editors, where `#` is a backspace. Return `True` if both editors end up showing the same text.

Backspacing an empty editor does nothing. Can you solve it with O(1) extra space?""",
    constraints=["1 ≤ len(s), len(t) ≤ 200", "lowercase letters and '#'"],
    samples=[("ab#c", "ad#c"), ("ab##", "c#d#"), ("a#c", "b")],
    tests=[("a##c", "#a#c"), ("bxj##tw", "bxo#j##tw")],
    gen=lambda r: (r.word(r.randint(1, 10), "ab#"), r.word(r.randint(1, 10), "ab#")),
    brute=lambda s, t: _backspace(s) == _backspace(t),
    hints=[
        "A stack makes it easy, but uses O(n) space. Which direction lets you know whether a character survives?",
        "Read from the end: a `#` means \"skip the next real character to the left\".",
        "Walk both strings backwards, each pointer skipping characters erased by pending backspaces, and compare the surviving characters one by one.",
    ],
    insight="Scanning right-to-left, you know immediately whether each character is erased.",
    time="O(n + m)", space="O(1)",
    pitfalls=["Stopping when one string finishes while the other still has surviving characters."],
)
def backspace_compare(s, t):
    def step(x, i):
        skip = 0
        while i >= 0:
            if x[i] == "#":
                skip += 1
            elif skip:
                skip -= 1
            else:
                break
            i -= 1
        return i

    i, j = len(s) - 1, len(t) - 1
    while True:
        i, j = step(s, i), step(t, j)
        if i < 0 or j < 0:
            return i < 0 and j < 0
        if s[i] != t[j]:
            return False
        i, j = i - 1, j - 1


def _nge3_brute(n):
    digits = str(n)
    best = None
    for p in set(permutations(digits)):
        v = int("".join(p))
        if v > n and (best is None or v < best):
            best = v
    return best if best is not None and best < 2**31 else -1


@problem(
    slug="next-greater-element-iii", title="Next Greater Element III", difficulty="Medium", pattern=P, tags=["Math", "Two Pointers", "String"],
    sig="nextGreaterElement(self, n: int) -> int",
    desc="""Given a positive integer `n`, return the smallest integer that is greater than `n` and uses exactly the same digits. If there is none, or the answer doesn't fit in a signed 32-bit integer (above `2³¹ − 1`), return `-1`.""",
    constraints=["1 ≤ n ≤ 2³¹ − 1"],
    samples=[(12,), (21,), (2147483486,)],
    tests=[(1,), (115,), (230241,), (1999999999,)],
    gen=lambda r: (r.randint(1, 10**r.randint(1, 7)),),
    brute=_nge3_brute,
    hints=[
        "This is the next permutation of n's digits.",
        "Find the rightmost digit that is smaller than the digit after it; swap it with the smallest larger digit to its right.",
        "Reverse the digits after that position to make them as small as possible, then check the 32-bit limit.",
    ],
    insight="Next greater number with the same digits is exactly next permutation.",
    time="O(d) for d digits", space="O(d)",
    pitfalls=["Forgetting the 32-bit overflow check."],
)
def next_greater_iii(n):
    d = list(str(n))
    i = len(d) - 2
    while i >= 0 and d[i] >= d[i + 1]:
        i -= 1
    if i < 0:
        return -1
    j = len(d) - 1
    while d[j] <= d[i]:
        j -= 1
    d[i], d[j] = d[j], d[i]
    d[i + 1:] = reversed(d[i + 1:])
    v = int("".join(d))
    return v if v < 2**31 else -1


@problem(
    slug="rotating-the-box", title="Rotating the Box", difficulty="Medium", pattern=P, tags=["Array", "Two Pointers", "Matrix"],
    sig="rotateTheBox(self, boxGrid: list[list[str]]) -> list[list[str]]",
    desc="""An `m x n` box seen from the side holds stones `"#"`, fixed obstacles `"*"` and empty cells `"."`.

The box is rotated 90 degrees clockwise. Gravity then pulls every stone down until it lands on an obstacle, another stone, or the bottom; obstacles don't move. Return the box after the rotation, as an `n x m` grid.""",
    constraints=["1 ≤ m, n ≤ 500", "cells are '#', '*' or '.'"],
    samples=[([["#", ".", "#"]],), ([["#", ".", "*", "."], ["#", "#", "*", "."]],)],
    gen=lambda r: (r.grid(r.randint(1, 5), r.randint(1, 6), "#.*."),),
    hints=[
        "Before rotating, the stones in each row slide to the right (that becomes \"down\" after rotation).",
        "In one row, obstacles split the row into independent segments.",
        "Scan each row from right to left with a pointer to the lowest free cell; move each stone there. Reset the pointer at obstacles. Then rotate: new[j][m − 1 − i] = old[i][j].",
    ],
    insight="Simulate gravity per row with a write pointer, then rotate the grid.",
    time="O(m·n)", space="O(m·n) for the output",
    pitfalls=["Rotating counter-clockwise by mistake.", "Letting stones pass through obstacles."],
)
def rotate_the_box(boxGrid):
    m, n = len(boxGrid), len(boxGrid[0])
    grid = [row[:] for row in boxGrid]
    for row in grid:
        free = n - 1
        for j in range(n - 1, -1, -1):
            if row[j] == "*":
                free = j - 1
            elif row[j] == "#":
                row[j], row[free] = ".", "#"
                free -= 1
    return [[grid[m - 1 - i][j] for i in range(m)] for j in range(n)]


@problem(
    slug="count-the-number-of-fair-pairs", title="Count the Number of Fair Pairs", difficulty="Medium", pattern=P,
    tags=["Array", "Two Pointers", "Sorting", "Binary Search"],
    sig="countFairPairs(self, nums: list[int], lower: int, upper: int) -> int",
    desc="""A pair of indices `(i, j)` with `i < j` is **fair** if `lower ≤ nums[i] + nums[j] ≤ upper`.

Return the number of fair pairs.""",
    constraints=["1 ≤ len(nums) ≤ 10⁵", "-10⁹ ≤ nums[i] ≤ 10⁹", "-10⁹ ≤ lower ≤ upper ≤ 10⁹"],
    samples=[([0, 1, 7, 4, 4, 5], 3, 6), ([1, 7, 9, 2, 5], 11, 11)],
    gen=lambda r: (lambda lo: (r.ints(r.randint(1, 30), -10, 10), lo, lo + r.randint(0, 10)))(r.randint(-10, 10)),
    brute=lambda nums, lower, upper: sum(lower <= nums[i] + nums[j] <= upper for i in range(len(nums)) for j in range(i + 1, len(nums))),
    hints=[
        "Pairs are unordered, so sorting the array doesn't change the answer.",
        "Count pairs with sum ≤ X using two pointers on the sorted array.",
        "The answer is count(sum ≤ upper) − count(sum ≤ lower − 1).",
    ],
    insight="Counting pairs below a threshold is easy with two pointers; a range is the difference of two such counts.",
    time="O(n log n)", space="O(1) besides sorting",
    pitfalls=["Counting a pair (i, i) or counting each pair twice."],
)
def fair_pairs(nums, lower, upper):
    nums = sorted(nums)

    def at_most(x):
        i, j, c = 0, len(nums) - 1, 0
        while i < j:
            if nums[i] + nums[j] <= x:
                c += j - i
                i += 1
            else:
                j -= 1
        return c

    return at_most(upper) - at_most(lower - 1)


@problem(
    slug="remove-duplicates-from-sorted-list-ii", title="Remove Duplicates from Sorted List II", difficulty="Medium", pattern=P,
    tags=["Linked List", "Two Pointers"],
    sig="deleteDuplicates(self, head: Optional[ListNode]) -> Optional[ListNode]",
    arg_types=["ListNode"], ret="ListNode",
    desc="""`head` is a sorted linked list. Delete **every** node whose value appears more than once, so only values that occurred exactly once remain. Return the resulting list, still sorted.""",
    constraints=["0 ≤ number of nodes ≤ 300", "-100 ≤ Node.val ≤ 100", "the list is sorted"],
    samples=[([1, 2, 3, 3, 4, 4, 5],), ([1, 1, 1, 2, 3],)],
    tests=[([],), ([1, 1],), ([1],)],
    gen=lambda r: (r.sorted_ints(r.randint(0, 20), -5, 5),),
    brute=lambda head: to_ln((lambda v: [x for x in v if v.count(x) == 1])(from_ln(head))),
    hints=[
        "Duplicates are adjacent because the list is sorted. The first node itself might be removed.",
        "A dummy node before the head means you always have a predecessor to relink.",
        "Keep `prev` at the last confirmed node. If the run starting at prev.next has length more than one, skip the whole run; otherwise advance prev.",
    ],
    insight="With a dummy head, removing an entire run is a single relink of the previous node.",
    time="O(n)", space="O(1)",
    pitfalls=["Keeping one copy of a duplicated value (that's the easier version of this problem)."],
)
def delete_duplicates_ii(head):
    from catalog_lib import ListNode
    dummy = ListNode(0, head)
    prev = dummy
    while prev.next:
        cur = prev.next
        if cur.next and cur.next.val == cur.val:
            while cur.next and cur.next.val == cur.val:
                cur = cur.next
            prev.next = cur.next
        else:
            prev = cur
    return dummy.next


@problem(
    slug="sum-of-square-numbers", title="Sum of Square Numbers", difficulty="Medium", pattern=P, tags=["Math", "Two Pointers", "Binary Search"],
    sig="judgeSquareSum(self, c: int) -> bool",
    desc="""Given a non-negative integer `c`, return `True` if there are integers `a` and `b` with `a² + b² = c`.""",
    constraints=["0 ≤ c ≤ 2³¹ − 1"],
    samples=[(5,), (3,), (4,)],
    tests=[(0,), (1,), (2,), (2147483646,), (1000000,)],
    gen=lambda r: (r.randint(0, 5000),),
    brute=lambda c: any(int((c - a * a) ** 0.5 + 0.5) ** 2 == c - a * a for a in range(int(c ** 0.5) + 2) if a * a <= c),
    hints=[
        "Both a and b are between 0 and √c.",
        "Use two pointers: a starting at 0 and b starting at ⌊√c⌋.",
        "If a² + b² is too small, increase a; if too big, decrease b; if equal, you're done. Stop when a passes b.",
    ],
    insight="Searching pairs from both ends of [0, √c] is a two-pointer sum search on squares.",
    time="O(√c)", space="O(1)",
    pitfalls=["Using floating-point square roots without checking the result exactly."],
)
def judge_square_sum(c):
    from math import isqrt
    a, b = 0, isqrt(c)
    while a <= b:
        s = a * a + b * b
        if s == c:
            return True
        if s < c:
            a += 1
        else:
            b -= 1
    return False


def _pal_with_extra(r, n, alphabet="ab"):
    half = r.word(n, alphabet)
    s = half + half[::-1]
    i = r.randint(0, len(s))
    return s[:i] + "z" + s[i:]


def _big_palindrome_digits(r, n):
    half = r.word(n, "0123456789")
    return "1" + half + half[::-1] + "1"


EXTRA = {
    "valid-palindrome": {
        "edge": [(" ",), (".,",), ("0P",), ("a",), ("ab_a",)],
        "large": [lambda r: (lambda h: (h + h[::-1],))(r.word(40000, "abcAB ,:")), lambda r: (r.word(80000, "ab,. "),)],
    },
    "3sum": {
        "edge": [([0, 0, 0],), ([0, 0, 0, 0],), ([1, 2, -2, -1],), ([-2, 0, 1, 1, 2],), ([0, 1, 1],)],
        "large": [lambda r: (r.ints(1500, -100000, 100000),), lambda r: (r.ints(1200, -30000, 30000),)],
    },
    "remove-nth-node-from-end-of-list": {"edge": [([1], 1), ([1, 2], 1), ([1, 2], 2), (list(range(30)), 30)]},
    "sort-colors": {"edge": [([0],), ([2, 2, 2],), ([1, 0],), ([2, 1, 0] * 100,)]},
    "reverse-words-in-a-string": {
        "edge": [("  hello world  ",), ("a",), ("a good   example",), ("   x   ",)],
        "large": [lambda r: (" ".join(r.words(1500, 1, 5, "abc0")),)],
    },
    "valid-word-abbreviation": {"edge": [("apple", "5"), ("apple", "6"), ("a", "01"), ("word", "w0rd"), ("a", "a"), ("ab", "1b")]},
    "valid-palindrome-ii": {
        "edge": [("a",), ("abca",), ("abc",), ("deeee",), ("eeeed",), ("cbbcc",)],
        "large": [lambda r: (_pal_with_extra(r, 40000),), lambda r: ((lambda s: s[:30000] + "xy" + s[30000:])(r.word(1, "a") * 60000),)],
    },
    "strobogrammatic-number": {"edge": [("0",), ("2",), ("818",), ("6",), ("1001",), ("609",)]},
    "minimum-number-of-moves-to-make-palindrome": {
        "edge": [("a",), ("aa",), ("ab" * 2,), ("zzazz",)],
        "large": [lambda r: (lambda h: ("".join(r.sample(h + h, len(h) * 2)),))(r.word(1000, "abcdefghij"))],
    },
    "next-palindrome-using-same-digits": {
        "edge": [("1",), ("99",), ("321123",), ("45544554",), ("12321",)],
        "large": [lambda r: (_big_palindrome_digits(r, 25000),)],
    },
    "count-subarrays-with-fixed-bounds": {
        "edge": [([1, 1, 1, 1], 1, 1), ([1, 2], 3, 4), ([5, 5], 5, 5), ([2, 1], 2, 1)],
        "large": [lambda r: (r.ints(10000, 1, 5), 1, 5), lambda r: (r.ints(10000, 1, 6), 2, 4)],
    },
    "find-the-lexicographically-largest-string-from-the-box-ii": {
        "edge": [("a", 1), ("gggg", 4), ("zz", 1), ("abz", 3)],
        "large": [lambda r: (r.word(5000, "yz"), 7), lambda r: ("z" * 2500 + "y" * 2500, 2)],
    },
    "get-the-maximum-score": {
        "edge": [([1], [1]), ([1, 2, 3], [4, 5]), ([10000000], [1, 10000000])],
        "large": [lambda r: (sorted(r.distinct(8000, 1, 20000)), sorted(r.distinct(8000, 1, 20000)))],
    },
    "create-maximum-number": {"edge": [([9], [9], 2), ([0], [0, 0], 3), ([6, 7], [6, 0, 4], 5), ([1], [2], 1)]},
    "next-permutation": {"edge": [([1],), ([3, 2, 1],), ([1, 1, 5],), ([1, 5, 1],), ([2, 2, 2],)]},
    "rotate-array": {
        "edge": [([1], 0), ([1, 2], 3), ([-1], 2), ([1, 2, 3], 100000)],
        "large": [lambda r: (r.ints(10000, -1000, 1000), r.randint(40000, 100000))],
    },
    "append-characters-to-string-to-make-subsequence": {
        "edge": [("a", "a"), ("a", "b"), ("abc", "abcd"), ("z", "abcde")],
        "large": [lambda r: (r.word(50000, "ab"), r.word(20000, "ab"))],
    },
    "squares-of-a-sorted-array": {
        "edge": [([-1],), ([-5, -3, -2],), ([0, 0],), ([-10000, 10000],)],
        "large": [lambda r: (r.sorted_ints(10000, -10000, 10000),)],
    },
    "reverse-string": {"edge": [(["a"],), (["a", "b"],), (["A", " ", "z"],)], "large": [lambda r: (list(r.word(20000, "abc")),)]},
    "partition-labels": {"edge": [("a",), ("abc",), ("aaaa",), ("eccbbbbdec",)]},
    "remove-element": {"edge": [([], 0), ([1], 1), ([2, 2, 2], 3), ([4, 4], 4)]},
    "string-compression": {"edge": [(["a"],), (["a"] * 12,), (list("abbbbbbbbbbbb"),), (["a"] * 100 + ["b"],)]},
    "remove-duplicates-from-sorted-array": {
        "edge": [([1],), ([-100, -100],), ([1, 2, 3],)],
        "large": [lambda r: (r.sorted_ints(20000, -100, 100),)],
    },
    "reverse-vowels-of-a-string": {
        "edge": [("a",), ("bcd",), ("aA",), ("leetcode",)],
        "large": [lambda r: (r.word(100000, "aeIOxyz"),)],
    },
    "is-subsequence": {
        "edge": [("", "abc"), ("abc", ""), ("aaaa", "aaa"), ("", "")],
        "large": [lambda r: (r.word(100, "ab"), r.word(10000, "ab"))],
    },
    "merge-strings-alternately": {"edge": [("a", "pqrs"), ("abcd", "p"), ("x", "y")]},
    "compare-version-numbers": {"edge": [("1.0", "1"), ("1.01", "1.001"), ("0.1", "1.1"), ("1.0.0.1", "1"), ("7.5.2.4", "7.5.3")]},
    "move-zeroes": {
        "edge": [([0],), ([1],), ([0, 0, 1],), ([1, 0, 0],)],
        "large": [lambda r: ([r.choice([0, 0, 0, r.randint(-50, 50)]) for _ in range(10000)],)],
    },
    "longest-subarray-of-1s-after-deleting-one-element": {
        "edge": [([1, 1, 1],), ([0, 0, 0],), ([1],), ([0],), ([1, 0],)],
        "large": [lambda r: ([r.choice([1, 1, 1, 0]) for _ in range(10000)],)],
    },
    "backspace-string-compare": {"edge": [("a##c", "#a#c"), ("a#c", "b"), ("##", "#"), ("bxj##tw", "bxo#j##tw")]},
    "next-greater-element-iii": {"edge": [(1,), (2147483647,), (1999999999,), (230241,), (11,), (2147483486,)]},
    "rotating-the-box": {
        "edge": [([["#"]],), ([["*"]],), ([[".", "#"]],), ([["#", "#", "*", ".", "*", "."]],)],
        "large": [lambda r: (r.grid(100, 100, "#.*.."),)],
    },
    "count-the-number-of-fair-pairs": {
        "edge": [([1], 0, 10), ([1, 1], 2, 2), ([-1000000000, 1000000000], -1, 1)],
        "large": [lambda r: (r.ints(10000, -10**9, 10**9), -10**9, 10**9 // 2)],
    },
    "remove-duplicates-from-sorted-list-ii": {"edge": [([],), ([1, 1],), ([1, 1, 2],), ([1, 2, 2],)]},
    "sum-of-square-numbers": {"edge": [(0,), (1,), (3,), (2147483647,), (2147483600,), (1000000000,)]},
}
