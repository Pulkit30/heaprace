from collections import defaultdict, deque

from catalog_lib import TreeNode, from_tree, problem, to_tree

DFS = "tree-dfs"
BFS = "tree-bfs"
T = ["TreeNode"]


def _nodes(root):
    out, st = [], [root] if root else []
    while st:
        n = st.pop()
        out.append(n)
        st += [c for c in (n.left, n.right) if c]
    return out


def _height(n):
    return 0 if not n else 1 + max(_height(n.left), _height(n.right))


def _paths(root):
    if not root:
        return []
    if not root.left and not root.right:
        return [[root.val]]
    return [[root.val] + p for c in (root.left, root.right) for p in _paths(c)]


def _inorder(n):
    return _inorder(n.left) + [n.val] + _inorder(n.right) if n else []


def _levels(root):
    out, level = [], [root] if root else []
    while level:
        out.append([n.val for n in level])
        level = [c for n in level for c in (n.left, n.right) if c]
    return out


def _tree_gen(n_lo=0, n_hi=12, lo=-9, hi=9):
    return lambda r: (r.tree(r.randint(n_lo, n_hi), lo, hi),)


@problem(
    slug="diameter-of-binary-tree", title="Diameter of Binary Tree", difficulty="Easy", pattern=DFS, tags=["Tree", "Depth-First Search", "Binary Tree"],
    sig="diameterOfBinaryTree(self, root: Optional[TreeNode]) -> int", arg_types=T,
    desc="""The diameter of a binary tree is the number of **edges** on the longest path between any two nodes (the path need not pass through the root). Return it.""",
    constraints=["1 ≤ nodes ≤ 10⁴", "-100 ≤ Node.val ≤ 100"],
    samples=[([1, 2, 3, 4, 5],), ([1, 2],)],
    gen=_tree_gen(1),
    brute=lambda root: max(_height(n.left) + _height(n.right) for n in _nodes(root)),
    hints=[
        "The longest path through a node goes down its left subtree and down its right subtree.",
        "Its length is height(left) + height(right).",
        "Compute heights bottom-up in one DFS and track the best sum seen at any node.",
    ],
    insight="One post-order DFS computes heights and the best path through each node.",
    time="O(n)", space="O(h)",
    pitfalls=["Only considering paths through the root."],
)
def diameter(root):
    best = 0

    def h(n):
        nonlocal best
        if not n:
            return 0
        l, r = h(n.left), h(n.right)
        best = max(best, l + r)
        return 1 + max(l, r)

    h(root)
    return best


def _max_path_brute(root):
    nodes = _nodes(root)
    parent = {}
    for n in nodes:
        for c in (n.left, n.right):
            if c:
                parent[c] = n
    adj = defaultdict(list)
    for c, p in parent.items():
        adj[c].append(p)
        adj[p].append(c)
    best = max(n.val for n in nodes)
    for s in nodes:
        st = [(s, None, s.val)]
        while st:
            u, prev, total = st.pop()
            best = max(best, total)
            for v in adj[u]:
                if v is not prev:
                    st.append((v, u, total + v.val))
    return best


@problem(
    slug="binary-tree-maximum-path-sum", title="Binary Tree Maximum Path Sum", difficulty="Hard", pattern=DFS,
    tags=["Dynamic Programming", "Tree", "Depth-First Search", "Binary Tree"],
    sig="maxPathSum(self, root: Optional[TreeNode]) -> int", arg_types=T,
    desc="""A path is a sequence of nodes where each adjacent pair is connected by an edge; a node appears at most once and the path needn't pass through the root. Return the maximum sum of node values over all non-empty paths.""",
    constraints=["1 ≤ nodes ≤ 3 × 10⁴", "-1000 ≤ Node.val ≤ 1000"],
    samples=[([1, 2, 3],), ([-10, 9, 20, None, None, 15, 7],), ([-3],)],
    gen=_tree_gen(1),
    brute=_max_path_brute,
    hints=[
        "Every path has a highest node; the path goes down at most one branch on each side of it.",
        "Let gain(n) be the best sum of a downward path starting at n (never below 0 for children: a negative branch is just skipped).",
        "At each node, n.val + max(0, gain(left)) + max(0, gain(right)) is a candidate answer; pass up n.val + the better branch.",
    ],
    insight="Post-order DFS: candidate through the node, single branch passed upward.",
    time="O(n)", space="O(h)",
    pitfalls=["Initializing the answer to 0 when all values are negative."],
)
def max_path_sum(root):
    best = float("-inf")

    def gain(n):
        nonlocal best
        if not n:
            return 0
        l, r = max(0, gain(n.left)), max(0, gain(n.right))
        best = max(best, n.val + l + r)
        return n.val + max(l, r)

    gain(root)
    return best


@problem(
    slug="invert-binary-tree", title="Invert Binary Tree", difficulty="Easy", pattern=DFS,
    tags=["Tree", "Depth-First Search", "Breadth-First Search", "Binary Tree"],
    sig="invertTree(self, root: Optional[TreeNode]) -> Optional[TreeNode]", arg_types=T, ret="TreeNode",
    desc="""Mirror the binary tree (swap every node's left and right children) and return its root.""",
    constraints=["0 ≤ nodes ≤ 100", "-100 ≤ Node.val ≤ 100"],
    samples=[([4, 2, 7, 1, 3, 6, 9],), ([2, 1, 3],), ([],)],
    gen=_tree_gen(),
    hints=[
        "Mirroring a tree mirrors both subtrees and swaps them.",
        "That's a direct recursion.",
        "Swap the children of each node, then recurse into both (any traversal order works).",
    ],
    insight="A simple recursive swap at every node.",
    time="O(n)", space="O(h)",
    pitfalls=["Recursing on a child after overwriting it without saving it."],
)
def invert_tree(root):
    if root:
        root.left, root.right = invert_tree(root.right), invert_tree(root.left)
    return root


def _build_input(r):
    vals = r.distinct(r.randint(1, 10), -20, 20)
    root = to_tree(r.tree(len(vals), values=vals))

    def pre(n):
        return [n.val] + pre(n.left) + pre(n.right) if n else []

    return pre(root), _inorder(root)


@problem(
    slug="construct-binary-tree-from-preorder-and-inorder-traversal", title="Construct Binary Tree from Preorder and Inorder Traversal",
    difficulty="Medium", pattern=DFS, tags=["Array", "Hash Table", "Divide and Conquer", "Tree", "Binary Tree"],
    sig="buildTree(self, preorder: list[int], inorder: list[int]) -> Optional[TreeNode]", ret="TreeNode",
    desc="""Given the preorder and inorder traversals of a binary tree with **distinct** values, build the tree and return its root.""",
    constraints=["1 ≤ n ≤ 3000", "values are distinct"],
    samples=[([3, 9, 20, 15, 7], [9, 3, 15, 20, 7]), ([-1], [-1])],
    gen=_build_input,
    hints=[
        "The first preorder value is the root.",
        "In the inorder list, everything left of the root is its left subtree and everything right is its right subtree.",
        "Recurse with index ranges and a value→inorder-index map so each split is O(1).",
    ],
    insight="Preorder gives roots; inorder splits subtrees.",
    time="O(n)", space="O(n)",
    pitfalls=["Slicing lists at every step, which is O(n²)."],
)
def build_tree(preorder, inorder):
    pos = {v: i for i, v in enumerate(inorder)}
    it = iter(preorder)

    def go(lo, hi):
        if lo > hi:
            return None
        v = next(it)
        n = TreeNode(v)
        n.left = go(lo, pos[v] - 1)
        n.right = go(pos[v] + 1, hi)
        return n

    return go(0, len(inorder) - 1)


@problem(
    slug="binary-tree-right-side-view", title="Binary Tree Right Side View", difficulty="Medium", pattern=BFS,
    tags=["Tree", "Depth-First Search", "Breadth-First Search", "Binary Tree"],
    sig="rightSideView(self, root: Optional[TreeNode]) -> list[int]", arg_types=T,
    desc="""Looking at the tree from the right side, return the values you can see, from top to bottom (the last node of each level).""",
    constraints=["0 ≤ nodes ≤ 100", "-100 ≤ Node.val ≤ 100"],
    samples=[([1, 2, 3, None, 5, None, 4],), ([1, None, 3],), ([],)],
    gen=_tree_gen(),
    brute=lambda root: [lvl[-1] for lvl in _levels(root)],
    hints=[
        "Each level contributes exactly one visible node.",
        "Traverse level by level.",
        "Record the last node of each level (or do a DFS visiting right children first, recording the first node at each new depth).",
    ],
    insight="Level-order traversal keeping the last node per level.",
    time="O(n)", space="O(w)",
    pitfalls=["Only following right children, which misses left nodes that stick out deeper."],
)
def right_side_view(root):
    out, q = [], deque([root] if root else [])
    while q:
        for i in range(len(q)):
            n = q.popleft()
            if i == 0:
                out.append(n.val)
            q.extend(c for c in (n.right, n.left) if c)
    return out


@problem(
    slug="lowest-common-ancestor-of-a-binary-tree", title="Lowest Common Ancestor of a Binary Tree", difficulty="Medium", pattern=DFS,
    tags=["Tree", "Depth-First Search", "Binary Tree"],
    sig="lowestCommonAncestor(self, root: Optional[TreeNode], p: int, q: int) -> int", arg_types=T,
    desc="""The tree's values are distinct. `p` and `q` are values of two different nodes in the tree. Return the **value** of their lowest common ancestor: the deepest node that has both nodes as descendants (a node counts as its own descendant).""",
    constraints=["2 ≤ nodes ≤ 10⁵", "values are distinct", "p ≠ q, both exist in the tree"],
    samples=[([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4], 5, 1), ([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4], 5, 4), ([1, 2], 1, 2)],
    gen=lambda r: (lambda vals: (r.tree(len(vals), values=vals), *r.sample(vals, 2)))(r.distinct(r.randint(2, 12), 0, 30)),
    hints=[
        "Search for p and q in both subtrees.",
        "If one is found on the left and the other on the right, the current node is the LCA.",
        "Return the node itself when it matches p or q; otherwise pass up whichever side found something.",
    ],
    insight="A single DFS that bubbles up found targets locates the split point.",
    time="O(n)", space="O(h)",
    pitfalls=["Stopping after finding p when q is in a different subtree."],
)
def lca(root, p, q):
    def go(n):
        if not n or n.val in (p, q):
            return n
        l, r = go(n.left), go(n.right)
        return n if l and r else l or r

    return go(root).val


def _validate_input(r):
    if r.random() < 0.5:
        return (r.bst(r.randint(1, 10), -20, 20),)
    return (r.tree(r.randint(1, 8), -5, 5),)


@problem(
    slug="validate-binary-search-tree", title="Validate Binary Search Tree", difficulty="Medium", pattern=DFS,
    tags=["Tree", "Depth-First Search", "Binary Search Tree", "Binary Tree"],
    sig="isValidBST(self, root: Optional[TreeNode]) -> bool", arg_types=T,
    desc="""Return `true` if the tree is a valid binary search tree: every node's left subtree holds only **smaller** values, its right subtree only **larger** values, and both subtrees are BSTs too.""",
    constraints=["1 ≤ nodes ≤ 10⁴", "-2³¹ ≤ Node.val ≤ 2³¹ − 1"],
    samples=[([2, 1, 3],), ([5, 1, 4, None, None, 3, 6],), ([5, 4, 6, None, None, 3, 7],)],
    gen=_validate_input,
    brute=lambda root: (lambda v: all(a < b for a, b in zip(v, v[1:])))(_inorder(root)),
    hints=[
        "Checking only each node against its direct children isn't enough.",
        "Every node must lie inside a (low, high) range inherited from its ancestors.",
        "Recurse with bounds: the left child gets (low, node.val) and the right child gets (node.val, high). An in-order traversal must also be strictly increasing.",
    ],
    insight="Pass value bounds down the tree (or check that the in-order sequence increases).",
    time="O(n)", space="O(h)",
    pitfalls=["Allowing duplicates; values must be strictly ordered."],
)
def is_valid_bst(root):
    def ok(n, lo, hi):
        return not n or (lo < n.val < hi and ok(n.left, lo, n.val) and ok(n.right, n.val, hi))

    return ok(root, float("-inf"), float("inf"))


@problem(
    slug="kth-smallest-element-in-a-bst", title="Kth Smallest Element in a BST", difficulty="Medium", pattern=DFS,
    tags=["Tree", "Depth-First Search", "Binary Search Tree", "Binary Tree"],
    sig="kthSmallest(self, root: Optional[TreeNode], k: int) -> int", arg_types=T,
    desc="""Return the `k`th smallest value (1-indexed) in the binary search tree.""",
    constraints=["1 ≤ k ≤ nodes ≤ 10⁴", "0 ≤ Node.val ≤ 10⁴"],
    samples=[([3, 1, 4, None, 2], 1), ([5, 3, 6, 2, 4, None, None, 1], 3)],
    gen=lambda r: (lambda n: (r.bst(n, 0, 50), r.randint(1, n)))(r.randint(1, 12)),
    brute=lambda root, k: sorted(n.val for n in _nodes(root))[k - 1],
    hints=[
        "An in-order traversal of a BST visits values in increasing order.",
        "You only need the first k values of that traversal.",
        "Do an iterative in-order walk with a stack and stop at the kth node.",
    ],
    insight="In-order traversal of a BST is sorted, so stop after k nodes.",
    time="O(h + k)", space="O(h)",
    pitfalls=["Collecting and sorting all values."],
)
def kth_smallest(root, k):
    st, n = [], root
    while True:
        while n:
            st.append(n)
            n = n.left
        n = st.pop()
        k -= 1
        if k == 0:
            return n.val
        n = n.right


def _bst_from_sorted_ref(nums):
    def go(lo, hi):
        if lo > hi:
            return None
        mid = (lo + hi) // 2
        n = TreeNode(nums[mid])
        n.left, n.right = go(lo, mid - 1), go(mid + 1, hi)
        return n
    return go(0, len(nums) - 1)


@problem(
    slug="convert-sorted-array-to-binary-search-tree", title="Convert Sorted Array to Binary Search Tree", difficulty="Easy", pattern=DFS,
    tags=["Array", "Divide and Conquer", "Tree", "Binary Search Tree", "Binary Tree"],
    sig="sortedArrayToBST(self, nums: list[int]) -> Optional[TreeNode]", ret="TreeNode",
    desc="""`nums` is sorted with distinct values. Build a height-balanced BST from it and return the root.

To make the answer unique, always use the element at index `(lo + hi) // 2` of the current range as the root (the **left** middle when the range has even length).""",
    constraints=["1 ≤ len(nums) ≤ 10⁴", "values are distinct and sorted"],
    samples=[([-10, -3, 0, 5, 9],), ([1, 3],)],
    gen=lambda r: (sorted(r.distinct(r.randint(1, 12), -30, 30)),),
    hints=[
        "The middle element splits the array into two halves of nearly equal size.",
        "Make it the root, then build each half the same way.",
        "Recurse on index ranges [lo, mid − 1] and [mid + 1, hi] using mid = (lo + hi) // 2.",
    ],
    insight="Divide and conquer on the middle element keeps the tree balanced.",
    time="O(n)", space="O(log n)",
    pitfalls=["Picking the right middle, which builds a different (also balanced) tree than expected here."],
)
def sorted_array_to_bst(nums):
    return _bst_from_sorted_ref(nums)


@problem(
    slug="flatten-binary-tree-to-linked-list", title="Flatten Binary Tree to Linked List", difficulty="Medium", pattern=DFS,
    tags=["Linked List", "Stack", "Tree", "Depth-First Search", "Binary Tree"],
    sig="flatten(self, root: Optional[TreeNode]) -> None", arg_types=T, out_arg=0,
    desc="""Flatten the tree **in place** into a "linked list" that uses the `right` pointers, with every `left` pointer set to `None`, in preorder order. Return nothing; the judge checks the tree you modified.""",
    constraints=["0 ≤ nodes ≤ 2000", "-100 ≤ Node.val ≤ 100"],
    samples=[([1, 2, 5, 3, 4, None, 6],), ([],), ([0],)],
    gen=_tree_gen(),
    hints=[
        "The final order is preorder: node, then its left subtree, then its right subtree.",
        "For a node with a left child, the right subtree should come after the rightmost node of the left subtree.",
        "Walk down: attach the right subtree to that rightmost node, move the left subtree to the right, clear left, and continue rightward.",
    ],
    insight="Morris-style rewiring flattens in O(1) extra space.",
    time="O(n)", space="O(1)",
    pitfalls=["Forgetting to set left pointers to None."],
)
def flatten(root):
    n = root
    while n:
        if n.left:
            pre = n.left
            while pre.right:
                pre = pre.right
            pre.right = n.right
            n.right, n.left = n.left, None
        n = n.right


@problem(
    slug="path-sum-ii", title="Path Sum II", difficulty="Medium", pattern=DFS, tags=["Backtracking", "Tree", "Depth-First Search", "Binary Tree"],
    sig="pathSum(self, root: Optional[TreeNode], targetSum: int) -> list[list[int]]", arg_types=T, compare="unordered",
    desc="""Return every root-to-leaf path whose node values add up to `targetSum`, as lists of values, in any order.""",
    constraints=["0 ≤ nodes ≤ 5000", "-1000 ≤ Node.val, targetSum ≤ 1000"],
    samples=[([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1], 22), ([1, 2, 3], 5), ([1, 2], 0)],
    gen=lambda r: (r.tree(r.randint(0, 12), -3, 5), r.randint(-3, 10)),
    brute=lambda root, t: [p for p in _paths(root) if sum(p) == t],
    hints=[
        "Only complete root-to-leaf paths count.",
        "DFS while tracking the current path and the remaining sum.",
        "At a leaf, record a copy of the path if the remaining sum is zero; pop the node when going back up.",
    ],
    insight="Backtracking DFS along root-to-leaf paths.",
    time="O(n · h)", space="O(h)",
    pitfalls=["Accepting paths that end at internal nodes."],
)
def path_sum_ii(root, targetSum):
    out, path = [], []

    def go(n, left):
        if not n:
            return
        path.append(n.val)
        left -= n.val
        if not n.left and not n.right and left == 0:
            out.append(path[:])
        go(n.left, left)
        go(n.right, left)
        path.pop()

    go(root, targetSum)
    return out


@problem(
    slug="sum-root-to-leaf-numbers", title="Sum Root to Leaf Numbers", difficulty="Medium", pattern=DFS, tags=["Tree", "Depth-First Search", "Binary Tree"],
    sig="sumNumbers(self, root: Optional[TreeNode]) -> int", arg_types=T,
    desc="""Every node holds a digit `0–9`. Each root-to-leaf path spells a number (e.g. 1 → 2 → 3 is 123). Return the sum of all those numbers.""",
    constraints=["1 ≤ nodes ≤ 1000", "0 ≤ Node.val ≤ 9", "depth ≤ 10"],
    samples=[([1, 2, 3],), ([4, 9, 0, 5, 1],)],
    gen=_tree_gen(1, 12, 0, 9),
    brute=lambda root: sum(int("".join(map(str, p))) for p in _paths(root)),
    hints=[
        "Going one level down multiplies the number so far by 10 and adds the digit.",
        "Pass the number so far into the recursion.",
        "At a leaf, add the finished number to the total.",
    ],
    insight="Carry the prefix value down the DFS.",
    time="O(n)", space="O(h)",
    pitfalls=["Counting internal nodes as path ends."],
)
def sum_numbers(root):
    def go(n, cur):
        if not n:
            return 0
        cur = cur * 10 + n.val
        if not n.left and not n.right:
            return cur
        return go(n.left, cur) + go(n.right, cur)

    return go(root, 0)


@problem(
    slug="balanced-binary-tree", title="Balanced Binary Tree", difficulty="Easy", pattern=DFS, tags=["Tree", "Depth-First Search", "Binary Tree"],
    sig="isBalanced(self, root: Optional[TreeNode]) -> bool", arg_types=T,
    desc="""A binary tree is height-balanced if, at every node, the heights of the left and right subtrees differ by at most one. Return whether the tree is height-balanced.""",
    constraints=["0 ≤ nodes ≤ 5000"],
    samples=[([3, 9, 20, None, None, 15, 7],), ([1, 2, 2, 3, 3, None, None, 4, 4],), ([],)],
    gen=lambda r: (r.tree(r.randint(0, 12), 0, 9, full=r.choice([0.5, 0.75, 0.95])),),
    brute=lambda root: all(abs(_height(n.left) - _height(n.right)) <= 1 for n in _nodes(root)),
    hints=[
        "Checking every node with a separate height computation is O(n²).",
        "Compute heights bottom-up and check balance at the same time.",
        "Use a sentinel (like −1) to signal \"unbalanced\" so you can stop early.",
    ],
    insight="One post-order pass returns height or an unbalanced marker.",
    time="O(n)", space="O(h)",
    pitfalls=["Only checking the root's subtrees."],
)
def is_balanced(root):
    def h(n):
        if not n:
            return 0
        l, r = h(n.left), h(n.right)
        if l < 0 or r < 0 or abs(l - r) > 1:
            return -1
        return 1 + max(l, r)

    return h(root) >= 0


@problem(
    slug="symmetric-tree", title="Symmetric Tree", difficulty="Easy", pattern=BFS,
    tags=["Tree", "Depth-First Search", "Breadth-First Search", "Binary Tree"],
    sig="isSymmetric(self, root: Optional[TreeNode]) -> bool", arg_types=T,
    desc="""Return `true` if the tree is a mirror image of itself around its center.""",
    constraints=["1 ≤ nodes ≤ 1000", "-100 ≤ Node.val ≤ 100"],
    samples=[([1, 2, 2, 3, 4, 4, 3],), ([1, 2, 2, None, 3, None, 3],)],
    tests=[([1],), ([1, 2, 2, 2, None, 2],)],
    gen=lambda r: (lambda t: (from_tree(_mirror_join(r, t)),))(to_tree(r.tree(r.randint(0, 5), 0, 3))),
    brute=lambda root: from_tree(root.left) == from_tree(invert_tree(to_tree(from_tree(root.right)))),
    hints=[
        "Compare the left subtree with the mirror of the right subtree.",
        "Two trees mirror each other if their roots match, left matches right, and right matches left.",
        "Recurse on pairs (a.left, b.right) and (a.right, b.left), or use a queue of pairs.",
    ],
    insight="Compare pairs of nodes moving in opposite directions.",
    time="O(n)", space="O(h)",
    pitfalls=["Comparing left with left instead of left with right."],
)
def is_symmetric(root):
    q = deque([(root.left, root.right)])
    while q:
        a, b = q.popleft()
        if not a and not b:
            continue
        if not a or not b or a.val != b.val:
            return False
        q.append((a.left, b.right))
        q.append((a.right, b.left))
    return True


def _mirror_join(r, t):
    import copy
    root = TreeNode(r.randint(0, 3))
    root.left = t
    root.right = invert_tree(copy.deepcopy(t))
    if r.random() < 0.4:
        for n in _nodes(root.right)[:1]:
            n.val += 1
    return root


@problem(
    slug="binary-tree-zigzag-level-order-traversal", title="Binary Tree Zigzag Level Order Traversal", difficulty="Medium", pattern=BFS,
    tags=["Tree", "Breadth-First Search", "Binary Tree"],
    sig="zigzagLevelOrder(self, root: Optional[TreeNode]) -> list[list[int]]", arg_types=T,
    desc="""Return the level-order traversal of the tree's values, alternating direction: left to right for the first level, right to left for the next, and so on.""",
    constraints=["0 ≤ nodes ≤ 2000", "-100 ≤ Node.val ≤ 100"],
    samples=[([3, 9, 20, None, None, 15, 7],), ([1],), ([],)],
    gen=_tree_gen(),
    brute=lambda root: [l if i % 2 == 0 else l[::-1] for i, l in enumerate(_levels(root))],
    hints=[
        "Start from a normal level-order traversal.",
        "Collect each level's values in a list.",
        "Reverse every other level (or append to the front of a deque on odd levels).",
    ],
    insight="BFS by levels with alternating output direction.",
    time="O(n)", space="O(w)",
    pitfalls=["Changing the order children are enqueued, which scrambles deeper levels."],
)
def zigzag(root):
    return [l if i % 2 == 0 else l[::-1] for i, l in enumerate(_levels(root))]


def _vertical(root):
    cols = defaultdict(list)
    q = deque([(root, 0)] if root else [])
    while q:
        n, c = q.popleft()
        cols[c].append(n.val)
        if n.left:
            q.append((n.left, c - 1))
        if n.right:
            q.append((n.right, c + 1))
    return [cols[c] for c in sorted(cols)]


@problem(
    slug="binary-tree-vertical-order-traversal", title="Binary Tree Vertical Order Traversal", difficulty="Medium", pattern=BFS,
    tags=["Hash Table", "Tree", "Depth-First Search", "Breadth-First Search", "Sorting", "Binary Tree"],
    sig="verticalOrder(self, root: Optional[TreeNode]) -> list[list[int]]", arg_types=T,
    desc="""Give the root column 0; a left child is one column to the left and a right child one column to the right. Return the values column by column, from the leftmost column to the rightmost. Within a column, list values top to bottom, and left to right for nodes in the same row (i.e. BFS order).""",
    constraints=["0 ≤ nodes ≤ 100", "-100 ≤ Node.val ≤ 100"],
    samples=[([3, 9, 20, None, None, 15, 7],), ([3, 9, 8, 4, 0, 1, 7],), ([],)],
    gen=_tree_gen(),
    hints=[
        "Tag each node with its column index.",
        "BFS naturally visits nodes top to bottom and left to right.",
        "Append values to a map from column to list during BFS, then output columns from the smallest index to the largest.",
    ],
    insight="BFS with column tags gives the required order within each column.",
    time="O(n log n) or O(n) by tracking min/max columns", space="O(n)",
    pitfalls=["Using DFS, which can list a deeper node before a shallower one in the same column."],
)
def vertical_order(root):
    return _vertical(root)


@problem(
    slug="minimum-depth-of-binary-tree", title="Minimum Depth of Binary Tree", difficulty="Easy", pattern=BFS,
    tags=["Tree", "Depth-First Search", "Breadth-First Search", "Binary Tree"],
    sig="minDepth(self, root: Optional[TreeNode]) -> int", arg_types=T,
    desc="""Return the number of nodes along the shortest path from the root down to the nearest **leaf** (a node with no children). An empty tree has depth 0.""",
    constraints=["0 ≤ nodes ≤ 10⁵"],
    samples=[([3, 9, 20, None, None, 15, 7],), ([2, None, 3, None, 4, None, 5, None, 6],), ([],)],
    gen=_tree_gen(),
    brute=lambda root: min((len(p) for p in _paths(root)), default=0),
    hints=[
        "The nearest leaf is found first by a level-by-level search.",
        "BFS from the root and stop at the first node without children.",
        "In a recursive version, a node with one missing child must use the other child's depth, not 0.",
    ],
    insight="BFS stops at the shallowest leaf.",
    time="O(n)", space="O(w)",
    pitfalls=["Treating a missing child as a leaf at depth 0."],
)
def min_depth(root):
    q = deque([(root, 1)] if root else [])
    while q:
        n, d = q.popleft()
        if not n.left and not n.right:
            return d
        q.extend((c, d + 1) for c in (n.left, n.right) if c)
    return 0


@problem(
    slug="average-of-levels-in-binary-tree", title="Average of Levels in Binary Tree", difficulty="Easy", pattern=BFS,
    tags=["Tree", "Depth-First Search", "Breadth-First Search", "Binary Tree"],
    sig="averageOfLevels(self, root: Optional[TreeNode]) -> list[float]", arg_types=T, compare="approx",
    desc="""Return the average value of the nodes on each level, from top to bottom. Answers within 10⁻⁵ are accepted.""",
    constraints=["1 ≤ nodes ≤ 10⁴", "-2³¹ ≤ Node.val ≤ 2³¹ − 1"],
    samples=[([3, 9, 20, None, None, 15, 7],), ([3, 9, 20, 15, 7],)],
    gen=_tree_gen(1),
    brute=lambda root: [sum(l) / len(l) for l in _levels(root)],
    hints=[
        "Process the tree one level at a time.",
        "For each level, sum the values and count the nodes.",
        "Divide to get the average; use floating-point division.",
    ],
    insight="Level-order traversal with per-level aggregation.",
    time="O(n)", space="O(w)",
    pitfalls=["Integer division."],
)
def average_of_levels(root):
    return [sum(l) / len(l) for l in _levels(root)]


@problem(
    slug="maximum-width-of-binary-tree", title="Maximum Width of Binary Tree", difficulty="Medium", pattern=BFS,
    tags=["Tree", "Depth-First Search", "Breadth-First Search", "Binary Tree"],
    sig="widthOfBinaryTree(self, root: Optional[TreeNode]) -> int", arg_types=T,
    desc="""A level's width is the distance between its leftmost and rightmost non-null nodes, counting the null positions between them as if the level were part of a complete tree. Return the maximum width over all levels.""",
    constraints=["1 ≤ nodes ≤ 3000"],
    samples=[([1, 3, 2, 5, 3, None, 9],), ([1, 3, 2, 5, None, None, 9, 6, None, 7],), ([1, 3, 2, 5],)],
    gen=_tree_gen(1),
    hints=[
        "Number positions like a heap: the root is 0, children of i are 2i and 2i + 1.",
        "A level's width is (last position − first position + 1).",
        "BFS with positions; renumber relative to the level's first position to keep numbers small.",
    ],
    insight="Heap-style indexing measures gaps without storing nulls.",
    time="O(n)", space="O(w)",
    pitfalls=["Counting only the non-null nodes on a level."],
)
def width_of_binary_tree(root):
    best, level = 0, [(root, 0)]
    while level:
        best = max(best, level[-1][1] - level[0][1] + 1)
        base = level[0][1]
        level = [(c, 2 * (i - base) + k) for n, i in level for k, c in ((0, n.left), (1, n.right)) if c]
    return best


@problem(
    slug="find-largest-value-in-each-tree-row", title="Find Largest Value in Each Tree Row", difficulty="Medium", pattern=BFS,
    tags=["Tree", "Depth-First Search", "Breadth-First Search", "Binary Tree"],
    sig="largestValues(self, root: Optional[TreeNode]) -> list[int]", arg_types=T,
    desc="""Return the largest value on each level of the tree, from top to bottom.""",
    constraints=["0 ≤ nodes ≤ 10⁴"],
    samples=[([1, 3, 2, 5, 3, None, 9],), ([1, 2, 3],), ([],)],
    gen=_tree_gen(),
    brute=lambda root: [max(l) for l in _levels(root)],
    hints=[
        "Each level is independent.",
        "BFS one level at a time.",
        "Track the maximum while processing each level.",
    ],
    insight="Level-order traversal with a running maximum.",
    time="O(n)", space="O(w)",
    pitfalls=["Initializing the maximum to 0 when values can be negative."],
)
def largest_values(root):
    return [max(l) for l in _levels(root)]


@problem(
    slug="binary-tree-level-order-traversal-ii", title="Binary Tree Level Order Traversal II", difficulty="Medium", pattern=BFS,
    tags=["Tree", "Breadth-First Search", "Binary Tree"],
    sig="levelOrderBottom(self, root: Optional[TreeNode]) -> list[list[int]]", arg_types=T,
    desc="""Return the level-order traversal of the tree's values from the **bottom** level up to the root; within a level, values go left to right.""",
    constraints=["0 ≤ nodes ≤ 2000"],
    samples=[([3, 9, 20, None, None, 15, 7],), ([1],), ([],)],
    gen=_tree_gen(),
    hints=[
        "This is ordinary level order, just output in reverse.",
        "Collect the levels top-down with BFS.",
        "Reverse the list of levels at the end (not the values inside each level).",
    ],
    insight="BFS then reverse the level list.",
    time="O(n)", space="O(n)",
    pitfalls=["Reversing values within each level."],
)
def level_order_bottom(root):
    return _levels(root)[::-1]


def _left_chain(vals):
    """Level-order list of a tree where every node has only a left child (a deep path)."""
    out = [vals[0]]
    for v in vals[1:]:
        out += [v, None]
    return out[:-1] if out[-1] is None else out


def _big_tree(r, n, lo=-100, hi=100, full=0.75):
    return r.tree(n, lo, hi, full=full)


def _distinct_tree(r, n):
    vals = r.distinct(n, 0, 100000)
    return r.tree(n, values=vals), vals


def _preorder_inorder(r, n):
    vals = r.distinct(n, -10000, 10000)
    root = to_tree(r.tree(n, values=vals))
    pre, st = [], [root]
    while st:
        node = st.pop()
        pre.append(node.val)
        st += [c for c in (node.right, node.left) if c]
    ino, st, cur = [], [], root
    while st or cur:
        while cur:
            st.append(cur)
            cur = cur.left
        cur = st.pop()
        ino.append(cur.val)
        cur = cur.right
    return pre, ino


EXTRA = {
    "diameter-of-binary-tree": {
        "edge": [([1],), ([1, 2],), ([1, None, 2, None, 3],), ([1, 2, None, 3, 4, None, None, 5, None, None, 6],)],
        "large": [lambda r: (_big_tree(r, 10000),), lambda r: (_left_chain(r.ints(3000, -100, 100)),)],
    },
    "binary-tree-maximum-path-sum": {
        "edge": [([-1000],), ([-1, -2, -3],), ([2, -1],), ([1, -2, 3],), ([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1],)],
        "large": [lambda r: (_big_tree(r, 15000, -1000, 1000),), lambda r: (_left_chain(r.ints(3000, -1000, 1000)),)],
    },
    "invert-binary-tree": {"edge": [([1],), ([1, 2],), ([1, None, 2],), (list(range(100)),)]},
    "construct-binary-tree-from-preorder-and-inorder-traversal": {
        "edge": [([1, 2], [2, 1]), ([1, 2], [1, 2]), ([1, 2, 3], [3, 2, 1]), ([3, 1, 2, 4], [1, 2, 3, 4])],
        "large": [lambda r: _preorder_inorder(r, 3000)],
    },
    "binary-tree-right-side-view": {"edge": [([1, 2],), ([1, 2, 3, 4],), ([1, None, 2, None, 3],), (_left_chain(list(range(100))),)]},
    "lowest-common-ancestor-of-a-binary-tree": {
        "edge": [([1, 2], 2, 1), ([1, 2, 3], 2, 3), ([1, 2, None, 3], 3, 2), ([0, 1, 2, 3, 4], 3, 4)],
        "large": [lambda r: (lambda t, v: (t, *r.sample(v, 2)))(*_distinct_tree(r, 10000)), lambda r: (_left_chain(list(range(3000))), 2999, 2998)],
    },
    "validate-binary-search-tree": {
        "edge": [([1],), ([1, 1],), ([2, 2, 2],), ([5, 4, 6, None, None, 3, 7],), ([-2147483648, None, 2147483647],), ([2147483647],), ([3, 1, 5, 0, 2, 4, 6, None, None, None, 3],)],
        "large": [lambda r: (r.bst(10000, -10**6, 10**6),), lambda r: (lambda t: (t[:-1] + [10**7],))(r.bst(10000, -10**6, 10**6))],
    },
    "kth-smallest-element-in-a-bst": {
        "edge": [([1], 1), ([2, 1], 2), ([2, None, 3], 1), ([3, 1, 4, None, 2], 4)],
        "large": [lambda r: (r.bst(10000, 0, 10000), 5000), lambda r: (r.bst(10000, 0, 10000), 10000)],
    },
    "convert-sorted-array-to-binary-search-tree": {
        "edge": [([0],), ([1, 2],), ([1, 2, 3],), ([1, 2, 3, 4],)],
        "large": [lambda r: (sorted(r.distinct(10000, -10**5, 10**5)),)],
    },
    "flatten-binary-tree-to-linked-list": {
        "edge": [([1, 2],), ([1, None, 2],), ([1, 2, 3],), (_left_chain([1, 2, 3, 4]),)],
        "large": [lambda r: (_big_tree(r, 2000),), lambda r: (_left_chain(r.ints(2000, -100, 100)),)],
    },
    "path-sum-ii": {
        "edge": [([], 0), ([1], 1), ([1], 0), ([1, 2], 1), ([-2, None, -3], -5), ([0, 0, 0], 0)],
        "large": [lambda r: (_big_tree(r, 5000, -1000, 1000), 777), lambda r: (_big_tree(r, 5000, 0, 1), 9)],
    },
    "sum-root-to-leaf-numbers": {
        "edge": [([0],), ([9],), ([1, 0],), ([0, 1, 1],)],
        "large": [lambda r: (_big_tree(r, 1000, 0, 9, full=1.0),)],
    },
    "balanced-binary-tree": {
        "edge": [([1],), ([1, 2],), ([1, None, 2, None, 3],), ([1, 2, 2, 3, None, None, 3, 4, None, None, 4],)],
        "large": [lambda r: (_big_tree(r, 5000, 0, 9, full=1.0),), lambda r: (_left_chain(r.ints(2000, 0, 9)),)],
    },
    "symmetric-tree": {
        "edge": [([1, 2, 2],), ([1, 2, 3],), ([1, None, 2],), ([1, 2, 2, None, 3, 3],)],
        "large": [lambda r: (lambda t: (from_tree(_mirror_join(r, t)),))(to_tree(r.tree(500, 0, 3)))],
    },
    "binary-tree-zigzag-level-order-traversal": {
        "edge": [([1, 2],), ([1, None, 2, 3],), ([1, 2, 3, 4, None, None, 5],)],
        "large": [lambda r: (_big_tree(r, 2000),)],
    },
    "binary-tree-vertical-order-traversal": {
        "edge": [([1],), ([1, 2],), ([3, 9, 8, 4, 0, 1, 7, None, None, None, 2, 5],), (_left_chain(list(range(100))),)],
    },
    "minimum-depth-of-binary-tree": {
        "edge": [([1],), ([1, 2],), ([1, 2, 3, 4],), ([1, None, 2],)],
        "large": [lambda r: (_big_tree(r, 15000),), lambda r: (_left_chain(r.ints(3000, 0, 9)),)],
    },
    "average-of-levels-in-binary-tree": {
        "edge": [([1],), ([2147483647, 2147483647, 2147483647],), ([-2147483648, -1],)],
        "large": [lambda r: (_big_tree(r, 10000, -2**31, 2**31 - 1),)],
    },
    "maximum-width-of-binary-tree": {
        "edge": [([1],), ([1, 2],), ([1, 1, 1, 1, None, None, 1, 1, None, None, 1],), ([1, 2, 3, None, 4, 5],)],
        "large": [lambda r: (_big_tree(r, 3000, 0, 9, full=0.97),)],
    },
    "find-largest-value-in-each-tree-row": {
        "edge": [([-2147483648],), ([1, 2],), ([0, -1],)],
        "large": [lambda r: (_big_tree(r, 10000, -2**31, 2**31 - 1),)],
    },
    "binary-tree-level-order-traversal-ii": {
        "edge": [([1, 2],), ([1, None, 2],), ([1, 2, 3, 4, 5, 6, 7],)],
        "large": [lambda r: (_big_tree(r, 2000),)],
    },
}
