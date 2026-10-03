from catalog_lib import ListNode, from_list_node, problem, to_list_node

P = "linked-list"
LN = dict(arg_types=["ListNode"], ret="ListNode")


def _vals(head):
    return from_list_node(head)


@problem(
    slug="reorder-list", title="Reorder List", difficulty="Medium", pattern=P, tags=["Linked List", "Two Pointers", "Stack"],
    sig="reorderList(self, head: Optional[ListNode]) -> None", arg_types=["ListNode"], out_arg=0,
    desc="""A list `L0 → L1 → … → Ln` must be reordered **in place** to `L0 → Ln → L1 → Ln−1 → L2 → Ln−2 → …`. Change the links, not the values.

Return nothing; the judge reads the list starting from `head`.""",
    constraints=["1 ≤ number of nodes ≤ 5 × 10⁴", "1 ≤ Node.val ≤ 1000"],
    samples=[([1, 2, 3, 4],), ([1, 2, 3, 4, 5],)],
    tests=[([1],), ([1, 2],)],
    gen=lambda r: (r.ints(r.randint(1, 20), 1, 100),),
    brute=lambda head: _relink(head, (lambda v: [v[i // 2] if i % 2 == 0 else v[-(i // 2) - 1] for i in range(len(v))])(_vals(head))),
    hints=[
        "The new order alternates between the front of the list and the back.",
        "Split the list at its middle (fast and slow pointers) and reverse the second half.",
        "Weave the two halves together: take one node from the first half, then one from the reversed second half, and so on.",
    ],
    insight="Find middle, reverse second half, merge alternately: three linear passes, O(1) space.",
    time="O(n)", space="O(1)",
    pitfalls=["Forgetting to cut the first half's tail, which creates a cycle."],
)
def reorder_list(head):
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    prev, cur = None, slow.next
    slow.next = None
    while cur:
        cur.next, prev, cur = prev, cur, cur.next
    first, second = head, prev
    while second:
        first.next, first = second, first.next
        second.next, second = first, second.next


def _relink(head, values):
    node = head
    for v in values:
        node.val = v
        node = node.next


def _rev_k_brute(head, k):
    v = _vals(head)
    out = []
    for i in range(0, len(v), k):
        chunk = v[i:i + k]
        out += chunk[::-1] if len(chunk) == k else chunk
    return to_list_node(out)


@problem(
    slug="reverse-nodes-in-k-group", title="Reverse Nodes in k-Group", difficulty="Hard", pattern=P, tags=["Linked List", "Recursion"],
    sig="reverseKGroup(self, head: Optional[ListNode], k: int) -> Optional[ListNode]", **LN,
    desc="""Reverse the nodes of the list `k` at a time and return the new head. If the number of nodes left at the end is less than `k`, leave them as they are.

Change the links, not the values. Can you use O(1) extra space?""",
    constraints=["1 ≤ k ≤ n ≤ 5000", "0 ≤ Node.val ≤ 1000"],
    samples=[([1, 2, 3, 4, 5], 2), ([1, 2, 3, 4, 5], 3)],
    tests=[([1], 1), ([1, 2], 2), ([1, 2, 3], 1)],
    gen=lambda r: (lambda v: (v, r.randint(1, len(v))))(r.ints(r.randint(1, 20), 0, 50)),
    brute=_rev_k_brute,
    hints=[
        "First check that k nodes remain; if not, stop.",
        "Reverse exactly k nodes the usual way, remembering the node before the group and the node after it.",
        "Reconnect: the node before the group points to the new group head, and the old group head (now its tail) points to the rest. Use a dummy node to simplify the first group.",
    ],
    insight="Group-by-group reversal is plain reversal plus careful reconnection at both ends.",
    time="O(n)", space="O(1)",
    pitfalls=["Reversing the last incomplete group.", "Losing the connection between groups."],
)
def reverse_k_group(head, k):
    dummy = ListNode(0, head)
    group_prev = dummy
    while True:
        kth = group_prev
        for _ in range(k):
            kth = kth.next
            if not kth:
                return dummy.next
        group_next = kth.next
        prev, cur = group_next, group_prev.next
        while cur is not group_next:
            cur.next, prev, cur = prev, cur, cur.next
        first = group_prev.next
        group_prev.next = kth
        group_prev = first


@problem(
    slug="reverse-linked-list-ii", title="Reverse Linked List II", difficulty="Medium", pattern=P, tags=["Linked List"],
    sig="reverseBetween(self, head: Optional[ListNode], left: int, right: int) -> Optional[ListNode]", **LN,
    desc="""Reverse the nodes from position `left` to position `right` (1-indexed, inclusive) and return the head of the list. Do it in one pass if you can.""",
    constraints=["1 ≤ n ≤ 500", "-500 ≤ Node.val ≤ 500", "1 ≤ left ≤ right ≤ n"],
    samples=[([1, 2, 3, 4, 5], 2, 4), ([5], 1, 1)],
    tests=[([3, 5], 1, 2), ([1, 2, 3], 1, 3)],
    gen=lambda r: (lambda v: (lambda a, b: (v, min(a, b), max(a, b)))(r.randint(1, len(v)), r.randint(1, len(v))))(r.ints(r.randint(1, 15), -20, 20)),
    brute=lambda head, l, rr: (lambda v: to_list_node(v[:l - 1] + v[l - 1:rr][::-1] + v[rr:]))(_vals(head)),
    hints=[
        "Walk to the node just before position left (a dummy head handles left = 1).",
        "Then reverse the next right − left + 1 nodes.",
        "Head-insertion works neatly: repeatedly move the node after the current one to the front of the sublist, right − left times.",
    ],
    insight="Reverse a sublist in place by repeatedly moving the next node to the front of the reversed part.",
    time="O(n)", space="O(1)",
    pitfalls=["Off-by-one when left = 1 without a dummy node."],
)
def reverse_between(head, left, right):
    dummy = ListNode(0, head)
    prev = dummy
    for _ in range(left - 1):
        prev = prev.next
    cur = prev.next
    for _ in range(right - left):
        nxt = cur.next
        cur.next = nxt.next
        nxt.next = prev.next
        prev.next = nxt
    return dummy.next


@problem(
    slug="swapping-nodes-in-a-linked-list", title="Swapping Nodes in a Linked List", difficulty="Medium", pattern=P,
    tags=["Linked List", "Two Pointers"],
    sig="swapNodes(self, head: Optional[ListNode], k: int) -> Optional[ListNode]", **LN,
    desc="""Swap the **values** of the `k`th node from the beginning and the `k`th node from the end (both 1-indexed), and return the head.""",
    constraints=["1 ≤ k ≤ n ≤ 10⁵", "0 ≤ Node.val ≤ 100"],
    samples=[([1, 2, 3, 4, 5], 2), ([7, 9, 6, 6, 7, 8, 3, 0, 9, 5], 5)],
    tests=[([1], 1), ([1, 2], 1), ([1, 2, 3], 2)],
    gen=lambda r: (lambda v: (v, r.randint(1, len(v))))(r.ints(r.randint(1, 15), 0, 30)),
    brute=lambda head, k: (lambda v: (v.__setitem__(slice(None), v), _swap(v, k - 1, len(v) - k), to_list_node(v))[2])(_vals(head)),
    hints=[
        "Finding the kth node from the front is a simple walk.",
        "The kth from the end can be found in the same pass with a second pointer that starts k − 1 nodes behind.",
        "When the leading pointer reaches the last node, the trailing pointer is the kth from the end. Swap the two values.",
    ],
    insight="A fixed gap of k − 1 between pointers locates the kth node from the end in one pass.",
    time="O(n)", space="O(1)",
    pitfalls=["Off-by-one in the gap between the two pointers."],
)
def swap_nodes(head, k):
    first = head
    for _ in range(k - 1):
        first = first.next
    lead, second = first, head
    while lead.next:
        lead, second = lead.next, second.next
    first.val, second.val = second.val, first.val
    return head


def _swap(v, i, j):
    v[i], v[j] = v[j], v[i]


def _even_groups_brute(head):
    v = _vals(head)
    out, i, size = [], 0, 1
    while i < len(v):
        group = v[i:i + size]
        out += group[::-1] if len(group) % 2 == 0 else group
        i += size
        size += 1
    return to_list_node(out)


@problem(
    slug="reverse-nodes-in-even-length-groups", title="Reverse Nodes in Even Length Groups", difficulty="Medium", pattern=P, tags=["Linked List"],
    sig="reverseEvenLengthGroups(self, head: Optional[ListNode]) -> Optional[ListNode]", **LN,
    desc="""Split the list into consecutive groups of sizes 1, 2, 3, 4, … (the last group may be shorter). Reverse every group whose **actual** length is even, and return the head.""",
    constraints=["1 ≤ n ≤ 10⁵", "0 ≤ Node.val ≤ 10⁵"],
    samples=[([5, 2, 6, 3, 9, 1, 7, 3, 8, 4],), ([1, 1, 0, 6],), ([1, 1, 0, 6, 5],)],
    tests=[([1],), ([1, 2],), ([1, 2, 3, 4, 5, 6],)],
    gen=lambda r: (r.ints(r.randint(1, 25), 0, 20),),
    brute=_even_groups_brute,
    hints=[
        "Walk the list group by group, with group sizes 1, 2, 3, …",
        "Count how many nodes the current group really has (the last one may be cut short).",
        "If that count is even, reverse the group in place and reconnect it to the node before and the node after; otherwise skip over it.",
    ],
    insight="Group reversal with the length check done on the real group size.",
    time="O(n)", space="O(1)",
    pitfalls=["Deciding by the intended size instead of the actual size of the last group."],
)
def reverse_even_groups(head):
    prev, size = head, 2
    while prev.next:
        node, count = prev, 0
        while node.next and count < size:
            node, count = node.next, count + 1
        if count % 2 == 0:
            tail = prev.next
            cur, nxt_prev = tail, node.next
            p = nxt_prev
            for _ in range(count):
                cur.next, p, cur = p, cur, cur.next
            prev.next = p
            prev = tail
        else:
            prev = node
        size += 1
    return head


@problem(
    slug="swap-nodes-in-pairs", title="Swap Nodes in Pairs", difficulty="Medium", pattern=P, tags=["Linked List", "Recursion"],
    sig="swapPairs(self, head: Optional[ListNode]) -> Optional[ListNode]", **LN,
    desc="""Swap every two adjacent nodes and return the head. Change the links, not the values.""",
    constraints=["0 ≤ n ≤ 100", "0 ≤ Node.val ≤ 100"],
    samples=[([1, 2, 3, 4],), ([],), ([1, 2, 3],)],
    tests=[([1],)],
    gen=lambda r: (r.ints(r.randint(0, 15), 0, 50),),
    brute=lambda head: (lambda v: to_list_node([v[i ^ 1] if (i ^ 1) < len(v) else v[i] for i in range(len(v))]))(_vals(head)),
    hints=[
        "A dummy node before the head gives every pair a predecessor.",
        "For each pair (a, b) after `prev`, relink so that prev → b → a → rest.",
        "Move prev to a (now second in the pair) and repeat while two nodes remain.",
    ],
    insight="Each swap is three pointer updates around a predecessor.",
    time="O(n)", space="O(1)",
    pitfalls=["Losing the rest of the list during a swap."],
)
def swap_pairs(head):
    dummy = ListNode(0, head)
    prev = dummy
    while prev.next and prev.next.next:
        a, b = prev.next, prev.next.next
        prev.next, a.next, b.next = b, b.next, a
        prev = a
    return dummy.next


def _split_brute(head, k):
    v = _vals(head)
    base, extra = divmod(len(v), k)
    out, i = [], 0
    for part in range(k):
        size = base + (part < extra)
        out.append(to_list_node(v[i:i + size]))
        i += size
    return out


@problem(
    slug="split-linked-list-in-parts", title="Split Linked List in Parts", difficulty="Medium", pattern=P, tags=["Linked List"],
    sig="splitListToParts(self, head: Optional[ListNode], k: int) -> list[Optional[ListNode]]",
    arg_types=["ListNode"], ret="ListNodeArray",
    desc="""Split the list into `k` consecutive parts whose lengths differ by at most one, with earlier parts never shorter than later ones. Some parts may be empty (`None`).

Return a list of the `k` part heads. The judge prints each part as a list.""",
    constraints=["0 ≤ n ≤ 1000", "1 ≤ k ≤ 50"],
    samples=[([1, 2, 3], 5), ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 3)],
    tests=[([], 3), ([1, 2], 1)],
    gen=lambda r: (r.ints(r.randint(0, 20), 0, 9), r.randint(1, 6)),
    brute=_split_brute,
    hints=[
        "Count the nodes first to know the part sizes.",
        "With n nodes, each part gets n // k nodes, and the first n % k parts get one extra.",
        "Walk the list cutting after each part's last node (set its next to None), and record each part's head.",
    ],
    insight="Divide n by k to get the sizes, then cut the list in a second pass.",
    time="O(n + k)", space="O(k) for the output",
    pitfalls=["Forgetting to cut the links, so every part contains the rest of the list."],
)
def split_parts(head, k):
    n, node = 0, head
    while node:
        n, node = n + 1, node.next
    base, extra = divmod(n, k)
    out, node = [], head
    for part in range(k):
        out.append(node)
        size = base + (part < extra)
        for _ in range(size - 1):
            node = node.next
        if node and size:
            node.next, node = None, node.next
    return out


@problem(
    slug="remove-linked-list-elements", title="Remove Linked List Elements", difficulty="Easy", pattern=P, tags=["Linked List", "Recursion"],
    sig="removeElements(self, head: Optional[ListNode], val: int) -> Optional[ListNode]", **LN,
    desc="""Remove every node whose value equals `val`, and return the new head.""",
    constraints=["0 ≤ n ≤ 10⁴", "1 ≤ Node.val ≤ 50", "0 ≤ val ≤ 50"],
    samples=[([1, 2, 6, 3, 4, 5, 6], 6), ([], 1), ([7, 7, 7, 7], 7)],
    gen=lambda r: (r.ints(r.randint(0, 15), 1, 4), r.randint(1, 4)),
    brute=lambda head, val: to_list_node([x for x in _vals(head) if x != val]),
    hints=[
        "Removing a node means pointing its predecessor past it.",
        "The head itself might need removing; a dummy node in front avoids a special case.",
        "Walk with a pointer at the predecessor: if the next node has the value, skip it; otherwise advance.",
    ],
    insight="A dummy node gives every real node a predecessor, so one loop handles all removals.",
    time="O(n)", space="O(1)",
    pitfalls=["Advancing the pointer right after a removal, which skips the next node."],
)
def remove_elements(head, val):
    dummy = ListNode(0, head)
    cur = dummy
    while cur.next:
        if cur.next.val == val:
            cur.next = cur.next.next
        else:
            cur = cur.next
    return dummy.next


def _nm_brute(head, m, n):
    v, out, i = _vals(head), [], 0
    while i < len(v):
        out += v[i:i + m]
        i += m + n
    return to_list_node(out)


@problem(
    slug="delete-n-nodes-after-m-nodes-of-a-linked-list", title="Delete N Nodes After M Nodes of a Linked List", difficulty="Easy",
    pattern=P, tags=["Linked List"],
    sig="deleteNodes(self, head: Optional[ListNode], m: int, n: int) -> Optional[ListNode]", **LN,
    desc="""Walk the list repeating this pattern: keep the next `m` nodes, then delete the next `n` nodes. Continue until the end and return the head.""",
    constraints=["1 ≤ number of nodes ≤ 10⁴", "1 ≤ m, n ≤ 1000"],
    samples=[([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], 2, 3), ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], 1, 3)],
    gen=lambda r: (r.ints(r.randint(1, 20), 0, 9), r.randint(1, 4), r.randint(1, 4)),
    brute=_nm_brute,
    hints=[
        "This is just two counting loops repeated.",
        "Advance m − 1 steps to the last kept node of the block.",
        "From there, skip the following n nodes by relinking the kept node past them, then continue from the next node.",
    ],
    insight="Alternate counted walks: keep m, splice out n.",
    time="O(length)", space="O(1)",
    pitfalls=["Walking past the end when fewer than m or n nodes remain."],
)
def delete_nodes(head, m, n):
    cur = head
    while cur:
        for _ in range(m - 1):
            if not cur:
                break
            cur = cur.next
        if not cur:
            break
        skip = cur.next
        for _ in range(n):
            if not skip:
                break
            skip = skip.next
        cur.next = skip
        cur = skip
    return head


@problem(
    slug="remove-duplicates-from-sorted-list", title="Remove Duplicates from Sorted List", difficulty="Easy", pattern=P, tags=["Linked List"],
    sig="deleteDuplicates(self, head: Optional[ListNode]) -> Optional[ListNode]", **LN,
    desc="""`head` is a sorted linked list. Delete duplicates so that each value appears only once, and return the list (still sorted).""",
    constraints=["0 ≤ n ≤ 300", "-100 ≤ Node.val ≤ 100"],
    samples=[([1, 1, 2],), ([1, 1, 2, 3, 3],)],
    tests=[([],), ([4, 4, 4],)],
    gen=lambda r: (r.sorted_ints(r.randint(0, 15), -3, 3),),
    brute=lambda head: to_list_node(sorted(set(_vals(head)))),
    hints=[
        "Duplicates are next to each other in a sorted list.",
        "Compare each node with its next node.",
        "If they have the same value, skip the next node; otherwise move forward.",
    ],
    insight="In a sorted list, removing adjacent repeats removes all repeats.",
    time="O(n)", space="O(1)",
    pitfalls=["Advancing after a removal and missing a third copy."],
)
def delete_duplicates(head):
    cur = head
    while cur and cur.next:
        if cur.next.val == cur.val:
            cur.next = cur.next.next
        else:
            cur = cur.next
    return head


@problem(
    slug="odd-even-linked-list", title="Odd Even Linked List", difficulty="Medium", pattern=P, tags=["Linked List"],
    sig="oddEvenList(self, head: Optional[ListNode]) -> Optional[ListNode]", **LN,
    desc="""Group all nodes at odd **positions** (1st, 3rd, 5th, …) first, followed by the nodes at even positions, keeping the original order within each group. Return the head. Use O(1) extra space.""",
    constraints=["0 ≤ n ≤ 10⁴", "-10⁶ ≤ Node.val ≤ 10⁶"],
    samples=[([1, 2, 3, 4, 5],), ([2, 1, 3, 5, 6, 4, 7],)],
    tests=[([],), ([1],), ([1, 2],)],
    gen=lambda r: (r.ints(r.randint(0, 15), -9, 9),),
    brute=lambda head: (lambda v: to_list_node(v[0::2] + v[1::2]))(_vals(head)),
    hints=[
        "Positions matter here, not values.",
        "Build two chains as you walk: one of odd-position nodes and one of even-position nodes.",
        "Link odd.next = even.next and even.next = odd.next alternately, then attach the even chain's head after the odd chain's tail.",
    ],
    insight="Two interleaved chains split in one pass and join at the end.",
    time="O(n)", space="O(1)",
    pitfalls=["Grouping by odd and even values instead of positions."],
)
def odd_even(head):
    if not head:
        return None
    odd, even = head, head.next
    even_head = even
    while even and even.next:
        odd.next = even.next
        odd = odd.next
        even.next = odd.next
        even = even.next
    odd.next = even_head
    return head


@problem(
    slug="rotate-list", title="Rotate List", difficulty="Medium", pattern=P, tags=["Linked List", "Two Pointers"],
    sig="rotateRight(self, head: Optional[ListNode], k: int) -> Optional[ListNode]", **LN,
    desc="""Rotate the list to the right by `k` places: each rotation moves the last node to the front. Return the new head.""",
    constraints=["0 ≤ n ≤ 500", "-100 ≤ Node.val ≤ 100", "0 ≤ k ≤ 2 × 10⁹"],
    samples=[([1, 2, 3, 4, 5], 2), ([0, 1, 2], 4)],
    tests=[([], 3), ([1], 99), ([1, 2], 2000000000)],
    gen=lambda r: (r.ints(r.randint(0, 12), -9, 9), r.randint(0, 30)),
    brute=lambda head, k: (lambda v: to_list_node(v[-(k % len(v)):] + v[:-(k % len(v))] if v and k % len(v) else v))(_vals(head)),
    hints=[
        "Rotating by the length gives back the same list, so use k mod n.",
        "The new tail is the node at position n − (k mod n) − 1.",
        "Connect the old tail to the head (making a ring), walk to the new tail, and break the ring after it.",
    ],
    insight="Close the list into a ring, then cut it at the right place.",
    time="O(n)", space="O(1)",
    pitfalls=["Rotating k times one by one when k can be 2 × 10⁹."],
)
def rotate_right(head, k):
    if not head:
        return None
    n, tail = 1, head
    while tail.next:
        tail, n = tail.next, n + 1
    k %= n
    if k == 0:
        return head
    tail.next = head
    new_tail = head
    for _ in range(n - k - 1):
        new_tail = new_tail.next
    new_head = new_tail.next
    new_tail.next = None
    return new_head


@problem(
    slug="sort-list", title="Sort List", difficulty="Medium", pattern=P, tags=["Linked List", "Sorting", "Merge Sort", "Divide and Conquer"],
    sig="sortList(self, head: Optional[ListNode]) -> Optional[ListNode]", **LN,
    desc="""Sort the linked list in ascending order and return its head. Aim for O(n log n) time.""",
    constraints=["0 ≤ n ≤ 5 × 10⁴", "-10⁵ ≤ Node.val ≤ 10⁵"],
    samples=[([4, 2, 1, 3],), ([-1, 5, 3, 4, 0],), ([],)],
    gen=lambda r: (r.ints(r.randint(0, 30), -50, 50),),
    brute=lambda head: to_list_node(sorted(_vals(head))),
    hints=[
        "Merge sort fits linked lists well: merging needs no extra arrays.",
        "Split the list in half with fast and slow pointers.",
        "Sort each half recursively and merge the two sorted halves by relinking nodes.",
    ],
    insight="Merge sort on a linked list: split at the middle, sort halves, merge by pointers.",
    time="O(n log n)", space="O(log n) recursion",
    pitfalls=["Not cutting the list in half, which leads to infinite recursion."],
)
def sort_list(head):
    if not head or not head.next:
        return head
    slow, fast = head, head.next
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    mid, slow.next = slow.next, None
    a, b = sort_list(head), sort_list(mid)
    dummy = tail = ListNode()
    while a and b:
        if a.val <= b.val:
            tail.next, a = a, a.next
        else:
            tail.next, b = b, b.next
        tail = tail.next
    tail.next = a or b
    return dummy.next


@problem(
    slug="merge-two-sorted-lists", title="Merge Two Sorted Lists", difficulty="Easy", pattern=P, tags=["Linked List", "Recursion"],
    sig="mergeTwoLists(self, list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]",
    arg_types=["ListNode", "ListNode"], ret="ListNode",
    desc="""Merge two sorted linked lists into one sorted list by splicing their nodes together, and return its head.""",
    constraints=["0 ≤ n, m ≤ 50", "-100 ≤ Node.val ≤ 100", "both lists are sorted"],
    samples=[([1, 2, 4], [1, 3, 4]), ([], []), ([], [0])],
    gen=lambda r: (r.sorted_ints(r.randint(0, 10), -9, 9), r.sorted_ints(r.randint(0, 10), -9, 9)),
    brute=lambda a, b: to_list_node(sorted(_vals(a) + _vals(b))),
    hints=[
        "The smallest remaining node is always at the front of one of the two lists.",
        "Use a dummy node and a tail pointer for the merged list.",
        "Repeatedly attach the smaller of the two front nodes to the tail and advance that list; attach whatever remains at the end.",
    ],
    insight="Splicing with a dummy head merges in place with no new nodes.",
    time="O(n + m)", space="O(1)",
    pitfalls=["Forgetting to attach the leftover part of the longer list."],
)
def merge_two(list1, list2):
    dummy = tail = ListNode()
    while list1 and list2:
        if list1.val <= list2.val:
            tail.next, list1 = list1, list1.next
        else:
            tail.next, list2 = list2, list2.next
        tail = tail.next
    tail.next = list1 or list2
    return dummy.next


EXTRA = {
    "reorder-list": {
        "edge": [([1],), ([1, 2],), ([1, 2, 3],), ([7, 7, 7, 7],)],
        "large": [lambda r: (r.ints(20000, 1, 1000),)],
    },
    "reverse-nodes-in-k-group": {
        "edge": [([1], 1), ([1, 2], 2), ([1, 2, 3], 3), ([1, 2, 3], 1), ([1, 2, 3, 4, 5], 5)],
        "large": [lambda r: (r.ints(5000, 0, 1000), 7), lambda r: (r.ints(5000, 0, 1000), 5000)],
    },
    "reverse-linked-list-ii": {"edge": [([5], 1, 1), ([3, 5], 1, 2), ([1, 2, 3], 2, 2), ([1, 2, 3], 1, 3)]},
    "swapping-nodes-in-a-linked-list": {
        "edge": [([1], 1), ([1, 2], 1), ([1, 2], 2), ([1, 2, 3], 2)],
        "large": [lambda r: (r.ints(20000, 0, 100), 7777)],
    },
    "reverse-nodes-in-even-length-groups": {
        "edge": [([1],), ([1, 2],), ([1, 2, 3],), ([2, 1],), ([1, 1, 0, 6, 5],)],
        "large": [lambda r: (r.ints(20000, 0, 100000),)],
    },
    "swap-nodes-in-pairs": {"edge": [([],), ([1],), ([1, 2, 3],), (list(range(100)),)]},
    "split-linked-list-in-parts": {
        "edge": [([], 3), ([1], 1), ([1, 2], 50), (list(range(10)), 3), (list(range(11)), 3)],
        "large": [lambda r: (r.ints(1000, 0, 1000), 7)],
    },
    "remove-linked-list-elements": {
        "edge": [([], 1), ([7, 7, 7, 7], 7), ([1], 2), ([1, 2, 1], 1)],
        "large": [lambda r: (r.ints(10000, 1, 3), 2)],
    },
    "delete-n-nodes-after-m-nodes-of-a-linked-list": {
        "edge": [([1], 1, 1), ([1, 2, 3], 1000, 1), ([1, 2, 3, 4], 1, 1000), ([1, 2, 3, 4, 5, 6], 1, 1)],
        "large": [lambda r: (r.ints(10000, 0, 1000), 3, 2)],
    },
    "remove-duplicates-from-sorted-list": {"edge": [([],), ([1],), ([1, 1, 1],), ([-100, 100],)]},
    "odd-even-linked-list": {
        "edge": [([],), ([1],), ([1, 2],), ([2, 1, 3, 5, 6, 4, 7],)],
        "large": [lambda r: (r.ints(10000, -10**6, 10**6),)],
    },
    "rotate-list": {"edge": [([], 0), ([], 5), ([1], 99), ([1, 2], 2000000000), ([0, 1, 2], 4)]},
    "sort-list": {
        "edge": [([],), ([1],), ([2, 1],), ([5, 5, 5],), ([-100000, 100000, 0],)],
        "large": [lambda r: (r.ints(15000, -100000, 100000),), lambda r: (list(range(15000, 0, -1)),)],
    },
    "merge-two-sorted-lists": {"edge": [([], []), ([], [0]), ([5], [1, 2, 4]), ([-100, 100], [-100, 100])]},
}
