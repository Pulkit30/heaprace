from catalog_lib import ListNode, from_list_node, problem, to_list_node

P = "fast-slow-pointers"


def _cycle_spec(r, n_max=20):
    n = r.randint(1, n_max)
    return [r.ints(n, -50, 50), r.choice([-1, r.randint(0, n - 1)])]


def _circular_brute(nums):
    n = len(nums)
    for start in range(n):
        seen, i = [], start
        direction = nums[start] > 0
        for _ in range(n + 1):
            if (nums[i] > 0) != direction:
                break
            seen.append(i)
            j = (i + nums[i]) % n
            if j == i:
                break
            if j in seen:
                cycle = seen[seen.index(j):]
                if len(cycle) > 1:
                    return True
                break
            i = j
    return False


@problem(
    slug="circular-array-loop", title="Circular Array Loop", difficulty="Medium", pattern=P, tags=["Array", "Two Pointers", "Hash Table"],
    sig="circularArrayLoop(self, nums: list[int]) -> bool",
    desc="""`nums` is a circular array of non-zero integers. Standing at index `i`, you move `nums[i]` steps: forward if it's positive, backward if it's negative, wrapping around the ends.

A **cycle** is a sequence of indices you keep repeating such that it has **more than one** index and every move in it goes in the **same direction**. Return `True` if `nums` contains such a cycle.""",
    constraints=["1 ≤ len(nums) ≤ 5000", "-1000 ≤ nums[i] ≤ 1000", "nums[i] ≠ 0"],
    samples=[([2, -1, 1, 2, 2],), ([-1, -2, -3, -4, -5, 6],), ([1, -1, 5, 1, 4],)],
    tests=[([1, 1],), ([2],), ([-2, 1, -1, -2, -2],), ([3, 1, 2],)],
    gen=lambda r: ([r.choice([-1, 1]) * r.randint(1, 6) for _ in range(r.randint(1, 10))],),
    brute=_circular_brute,
    hints=[
        "Following the moves from any index is like walking a linked list: you eventually repeat an index.",
        "Use fast and slow pointers from each start, but stop as soon as the direction changes or a move lands on itself (a one-element loop).",
        "If slow and fast meet, a valid cycle exists. Mark every index visited from a failed start as dead so it's never explored again, which keeps the total work O(n).",
    ],
    insight="Each start is a cycle-detection problem on an implicit linked list; direction changes and self-loops disqualify a path.",
    time="O(n)", space="O(1) when marking in place",
    pitfalls=["Accepting a single index that jumps back to itself.", "Accepting a loop that mixes forward and backward moves."],
)
def circular_array_loop(nums):
    n = len(nums)

    def nxt(i, forward):
        if (nums[i] > 0) != forward:
            return -1
        j = (i + nums[i]) % n
        return -1 if j == i else j

    for i in range(n):
        forward = nums[i] > 0
        slow = fast = i
        while True:
            slow = nxt(slow, forward)
            fast = nxt(fast, forward)
            if fast != -1:
                fast = nxt(fast, forward)
            if slow == -1 or fast == -1:
                break
            if slow == fast:
                return True
    return False


@problem(
    slug="linked-list-cycle", title="Linked List Cycle", difficulty="Easy", pattern=P, tags=["Linked List", "Two Pointers"],
    sig="hasCycle(self, head: Optional[ListNode]) -> bool", arg_types=["CycleList"],
    desc="""Given the `head` of a linked list, return `True` if the list has a cycle, meaning some node can be reached again by following `next` pointers.

In the tests a list is written as `[values, pos]`: the nodes hold `values`, and the last node links back to the node at index `pos` (`-1` means no cycle). Your function only receives `head`.""",
    constraints=["0 ≤ number of nodes ≤ 10⁴", "-10⁵ ≤ Node.val ≤ 10⁵", "pos is -1 or a valid index"],
    samples=[([[3, 2, 0, -4], 1],), ([[1, 2], 0],), ([[1], -1],)],
    tests=[([[], -1],), ([[1], 0],), ([[1, 2, 3], -1],)],
    gen=lambda r: (_cycle_spec(r),),
    brute=lambda head: (lambda seen: any(id(n) in seen or seen.add(id(n)) for n in _walk(head, 10**5)))(set()),
    hints=[
        "A set of visited nodes works, but uses O(n) memory.",
        "Two runners on a circular track meet if one is faster than the other.",
        "Move slow one step and fast two steps. If fast reaches the end, there's no cycle; if they ever point to the same node, there is.",
    ],
    insight="Floyd's tortoise and hare detects a cycle in O(1) space.",
    time="O(n)", space="O(1)",
    pitfalls=["Dereferencing fast.next when fast is already None."],
)
def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow is fast:
            return True
    return False


def _walk(head, limit):
    n = head
    for _ in range(limit):
        if n is None:
            return
        yield n
        n = n.next


@problem(
    slug="linked-list-cycle-ii", title="Linked List Cycle II", difficulty="Medium", pattern=P, tags=["Linked List", "Two Pointers"],
    sig="detectCycle(self, head: Optional[ListNode]) -> Optional[ListNode]", arg_types=["CycleList"], ret="NodeIndex",
    desc="""Return the node where the cycle in the linked list **begins**, or `None` if there is no cycle. Don't modify the list.

Lists are written as `[values, pos]` (the tail links back to index `pos`). The judge reports the position of the node you return, so the expected answer is that index, or `-1` for `None`.""",
    constraints=["0 ≤ number of nodes ≤ 10⁴", "-10⁵ ≤ Node.val ≤ 10⁵"],
    samples=[([[3, 2, 0, -4], 1],), ([[1, 2], 0],), ([[1], -1],)],
    tests=[([[], -1],), ([[5], 0],), ([[1, 2, 3, 4], 3],)],
    gen=lambda r: (_cycle_spec(r),),
    hints=[
        "First detect the cycle with fast and slow pointers.",
        "When they meet, the distance from the head to the cycle start equals the distance from the meeting point to the cycle start (going forward).",
        "After meeting, move one pointer back to the head and advance both one step at a time; they meet exactly at the start of the cycle.",
    ],
    insight="Floyd's algorithm finds not just a cycle but its entrance, using the distance equality at the meeting point.",
    time="O(n)", space="O(1)",
    pitfalls=["Returning the meeting point instead of the cycle's entrance."],
)
def detect_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow is fast:
            slow = head
            while slow is not fast:
                slow, fast = slow.next, fast.next
            return slow
    return None


@problem(
    slug="linked-list-cycle-iii", title="Linked List Cycle III", difficulty="Medium", pattern=P, tags=["Linked List", "Two Pointers"],
    sig="countCycleLength(self, head: Optional[ListNode]) -> int", arg_types=["CycleList"],
    desc="""Return the **number of nodes in the cycle** of the linked list, or `0` if there is no cycle.

Lists are written as `[values, pos]`: the last node links back to index `pos` (`-1` means no cycle).""",
    constraints=["0 ≤ number of nodes ≤ 10⁴"],
    samples=[([[3, 2, 0, -4], 1],), ([[1, 2, 3], -1],), ([[7], 0],)],
    tests=[([[], -1],), ([[1, 2], 0],)],
    gen=lambda r: (_cycle_spec(r),),
    hints=[
        "First find out whether there's a cycle at all.",
        "Fast and slow pointers meet somewhere inside the cycle.",
        "From the meeting node, walk around the cycle counting steps until you come back to it.",
    ],
    insight="Once you're inside the cycle, one lap measures its length.",
    time="O(n)", space="O(1)",
    pitfalls=["Counting the nodes before the cycle too."],
)
def cycle_length(head):
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow is fast:
            count, cur = 1, slow.next
            while cur is not slow:
                cur, count = cur.next, count + 1
            return count
    return 0


@problem(
    slug="linked-list-cycle-iv", title="Linked List Cycle IV", difficulty="Medium", pattern=P, tags=["Linked List", "Two Pointers"],
    sig="removeCycle(self, head: Optional[ListNode]) -> Optional[ListNode]", arg_types=["CycleList"], ret="ListNode",
    desc="""The linked list may contain a cycle. **Remove the cycle** by setting the `next` pointer of the last node in the cycle to `None`, keeping every node, and return the head.

Lists are written as `[values, pos]` (the tail links back to index `pos`). If there's no cycle, return the list unchanged.""",
    constraints=["0 ≤ number of nodes ≤ 10⁴"],
    samples=[([[3, 2, 0, -4], 1],), ([[1, 2], 0],), ([[1, 2, 3], -1],)],
    tests=[([[], -1],), ([[9], 0],)],
    gen=lambda r: (_cycle_spec(r),),
    hints=[
        "Find the node where the cycle starts, using fast and slow pointers.",
        "The node to cut is the one inside the cycle whose next is the cycle's start.",
        "From the cycle start, walk around until the next pointer returns to the start, then set that node's next to None.",
    ],
    insight="Finding the cycle's entrance tells you exactly which link closes the loop.",
    time="O(n)", space="O(1)",
    pitfalls=["Cutting the link at the meeting point, which can drop nodes.", "Forgetting a cycle that starts at the head."],
)
def remove_cycle(head):
    entrance = detect_cycle(head)
    if entrance is None:
        return head
    cur = entrance
    while cur.next is not entrance:
        cur = cur.next
    cur.next = None
    return head


@problem(
    slug="maximum-twin-sum-of-a-linked-list", title="Maximum Twin Sum of a Linked List", difficulty="Medium", pattern=P,
    tags=["Linked List", "Two Pointers", "Stack"],
    sig="pairSum(self, head: Optional[ListNode]) -> int", arg_types=["ListNode"],
    desc="""A linked list has an **even** length `n`. Node `i` (0-indexed) and node `n − 1 − i` are **twins**. A twin sum is the sum of a node and its twin.

Return the maximum twin sum.""",
    constraints=["n is even, 2 ≤ n ≤ 10⁵", "1 ≤ Node.val ≤ 10⁵"],
    samples=[([5, 4, 2, 1],), ([4, 2, 2, 3],), ([1, 100000],)],
    gen=lambda r: (r.ints(2 * r.randint(1, 15), 1, 100),),
    brute=lambda head: (lambda v: max(v[i] + v[len(v) - 1 - i] for i in range(len(v) // 2)))(from_list_node(head)),
    hints=[
        "Twins pair the first half with the reversed second half.",
        "Find the middle with fast and slow pointers.",
        "Reverse the second half in place, then walk both halves together, taking the largest sum of paired values.",
    ],
    insight="Middle + reverse second half turns twin pairs into a parallel walk, with O(1) extra space.",
    time="O(n)", space="O(1)",
    pitfalls=["Copying the list into an array is fine, but uses O(n) extra space."],
)
def pair_sum(head):
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    prev = None
    while slow:
        slow.next, prev, slow = prev, slow, slow.next
    best = 0
    while prev:
        best = max(best, head.val + prev.val)
        head, prev = head.next, prev.next
    return best


@problem(
    slug="middle-of-the-linked-list", title="Middle of the Linked List", difficulty="Easy", pattern=P, tags=["Linked List", "Two Pointers"],
    sig="middleNode(self, head: Optional[ListNode]) -> Optional[ListNode]", arg_types=["ListNode"], ret="ListNode",
    desc="""Return the **middle node** of the linked list. If there are two middle nodes, return the second one.

The judge prints the list starting from the node you return.""",
    constraints=["1 ≤ number of nodes ≤ 100", "1 ≤ Node.val ≤ 100"],
    samples=[([1, 2, 3, 4, 5],), ([1, 2, 3, 4, 5, 6],)],
    tests=[([1],), ([1, 2],)],
    gen=lambda r: (r.ints(r.randint(1, 20), 1, 100),),
    brute=lambda head: (lambda v: to_list_node(v[len(v) // 2:]))(from_list_node(head)),
    hints=[
        "Counting the length first works in two passes. Can you find the middle in one?",
        "If one pointer moves twice as fast as another, where is the slow one when the fast one finishes?",
        "Move slow one step and fast two steps while fast and fast.next exist; slow ends on the (second) middle.",
    ],
    insight="A two-speed walk finds the middle in a single pass.",
    time="O(n)", space="O(1)",
    pitfalls=["Returning the first middle for even lengths."],
)
def middle_node(head):
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    return slow


@problem(
    slug="palindrome-linked-list", title="Palindrome Linked List", difficulty="Easy", pattern=P, tags=["Linked List", "Two Pointers"],
    sig="isPalindrome(self, head: Optional[ListNode]) -> bool", arg_types=["ListNode"],
    desc="""Return `True` if the values of the linked list read the same forwards and backwards. Try for O(n) time and O(1) extra space.""",
    constraints=["1 ≤ number of nodes ≤ 10⁵", "0 ≤ Node.val ≤ 9"],
    samples=[([1, 2, 2, 1],), ([1, 2],), ([1, 2, 1],)],
    tests=[([1],), ([1, 1, 2, 1],)],
    gen=lambda r: (lambda h: (h + r.ints(r.randint(0, 1), 0, 3) + h[::-1] if r.random() < 0.6 else r.ints(r.randint(1, 10), 0, 3),))(r.ints(r.randint(0, 6), 0, 3)),
    brute=lambda head: (lambda v: v == v[::-1])(from_list_node(head)),
    hints=[
        "Copying values to an array makes it easy but uses O(n) space.",
        "Find the middle with fast and slow pointers.",
        "Reverse the second half, compare it with the first half node by node, and (optionally) reverse it back.",
    ],
    insight="Reversing the second half lets you compare mirrored values in place.",
    time="O(n)", space="O(1)",
    pitfalls=["Handling odd lengths: the middle node doesn't need a partner."],
)
def palindrome_list(head):
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    prev = None
    while slow:
        slow.next, prev, slow = prev, slow, slow.next
    while prev:
        if prev.val != head.val:
            return False
        prev, head = prev.next, head.next
    return True


def _big_cycle(r, n, cyclic=True):
    return ([r.randint(-100000, 100000) for _ in range(n)], r.randint(0, n - 1) if cyclic else -1)


def _circular_big(r, n):
    return ([r.choice([-1, 1]) * r.randint(1, 1000) for _ in range(n)],)


EXTRA = {
    "circular-array-loop": {
        "edge": [([1],), ([1, 1],), ([-1, -1],), ([2, -1, 1, -2, -2],), ([-2, 1, -1, -2, -2],), ([1, 1, 2],)],
        "large": [lambda r: _circular_big(r, 5000), lambda r: ([r.choice([2, 3, -1000]) for _ in range(4999)] + [1],)],
    },
    "linked-list-cycle": {
        "edge": [([[], -1],), ([[1], -1],), ([[1], 0],), ([[1, 2], 0],)],
        "large": [lambda r: (_big_cycle(r, 10000),), lambda r: (_big_cycle(r, 10000, False),)],
    },
    "linked-list-cycle-ii": {
        "edge": [([[], -1],), ([[1], -1],), ([[1], 0],), ([[1, 2], 1],)],
        "large": [lambda r: (_big_cycle(r, 10000),)],
    },
    "linked-list-cycle-iii": {
        "edge": [([[], -1],), ([[1], 0],), ([[1, 2], 0],), ([[1, 2, 3], -1],)],
        "large": [lambda r: (_big_cycle(r, 10000),)],
    },
    "linked-list-cycle-iv": {
        "edge": [([[], -1],), ([[1], 0],), ([[1, 2], 0],), ([[1, 2, 3], 2],)],
        "large": [lambda r: (_big_cycle(r, 10000),)],
    },
    "maximum-twin-sum-of-a-linked-list": {
        "edge": [([1, 100000],), ([1, 1, 1, 1],), ([5, 1, 1, 5],)],
        "large": [lambda r: (r.ints(10000, 1, 100000),)],
    },
    "middle-of-the-linked-list": {"edge": [([1],), ([1, 2],), ([1, 2, 3],), (list(range(1, 101)),)]},
    "palindrome-linked-list": {
        "edge": [([1],), ([1, 2],), ([1, 1],), ([1, 0, 1],), ([1, 2, 3, 1],)],
        "large": [lambda r: (lambda h: (h + h[::-1],))(r.ints(5000, 0, 9)), lambda r: (lambda h: (h + [5] + h[::-1][:-1] + [8],))(r.ints(5000, 0, 9))],
    },
}
