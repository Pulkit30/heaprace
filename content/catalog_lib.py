"""HeapRace problem catalog: tiny DSL for writing problems at scale.

Each problem is registered with @problem(...) on its reference solution. Expected outputs are never typed by
hand: build_catalog.py runs the reference solution on every test (and cross-checks a brute-force solution when
one is given). Descriptions, hints and guides are written in our own words.
"""

import copy
import json
import random
import re
from collections import deque

REGISTRY = []


def problem(**meta):
    def register(solution):
        meta["solve"] = solution
        REGISTRY.append(meta)
        return solution

    return register


# ---------- Node helpers (must match the judge harness in src/lib/judge/harness.ts) ----------

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def to_list_node(values):
    dummy = tail = ListNode()
    for v in values:
        tail.next = ListNode(v)
        tail = tail.next
    return dummy.next


def from_list_node(node):
    out = []
    while node is not None:
        if len(out) > 100_000:
            raise ValueError("cycle in returned list")
        out.append(node.val)
        node = node.next
    return out


def to_tree(values):
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue, i = deque([root]), 1
    while queue and i < len(values):
        node = queue.popleft()
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i += 1
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i += 1
    return root


def from_tree(root):
    out, queue = [], deque([root])
    while queue:
        node = queue.popleft()
        out.append(None if node is None else node.val)
        if node is not None:
            queue.append(node.left)
            queue.append(node.right)
    while out and out[-1] is None:
        out.pop()
    return out


class _CycleBuilder:
    nodes = []


def to_cycle_list(spec):
    values, pos = spec
    nodes = [ListNode(v) for v in values]
    for a, b in zip(nodes, nodes[1:]):
        a.next = b
    if nodes and 0 <= pos < len(nodes):
        nodes[-1].next = nodes[pos]
    _CycleBuilder.nodes = nodes
    return nodes[0] if nodes else None


def node_index(node):
    if node is None:
        return -1
    for i, n in enumerate(_CycleBuilder.nodes):
        if n is node:
            return i
    raise ValueError("returned node not in input")


BUILD = {
    "ListNode": to_list_node,
    "TreeNode": to_tree,
    "CycleList": to_cycle_list,
    "ListNodeArray": lambda lists: [to_list_node(v) for v in lists],
}
DUMP = {
    "ListNode": from_list_node,
    "TreeNode": from_tree,
    "NodeIndex": node_index,
    "ListNodeArray": lambda heads: [from_list_node(h) for h in heads],
    "TreeNodeArray": lambda roots: [from_tree(r) for r in roots],
}


# ---------- Random input helpers for generators ----------

class Gen(random.Random):
    def ints(self, n, lo, hi):
        return [self.randint(lo, hi) for _ in range(n)]

    def distinct(self, n, lo, hi):
        return self.sample(range(lo, hi + 1), n)

    def sorted_ints(self, n, lo, hi):
        return sorted(self.ints(n, lo, hi))

    def word(self, n, alphabet="abcdefghijklmnopqrstuvwxyz"):
        return "".join(self.choice(alphabet) for _ in range(n))

    def words(self, k, lo, hi, alphabet="abcdefghijklmnopqrstuvwxyz"):
        return [self.word(self.randint(lo, hi), alphabet) for _ in range(k)]

    def grid(self, rows, cols, choices):
        return [[self.choice(choices) for _ in range(cols)] for _ in range(rows)]

    def tree(self, n, lo=-100, hi=100, values=None, full=0.75):
        """Level-order list for a random binary tree with n nodes (None marks gaps)."""
        if n == 0:
            return []
        vals = list(values) if values is not None else self.ints(n, lo, hi)
        out, slots, used = [vals[0]], 0, 1
        frontier = 1
        while used < n:
            nxt = 0
            for _ in range(frontier * 2):
                if used < n and (self.random() < full or nxt == 0):
                    out.append(vals[used])
                    used += 1
                    nxt += 1
                else:
                    out.append(None)
            frontier = nxt
            if frontier == 0:
                break
        while out and out[-1] is None:
            out.pop()
        return out

    def bst(self, n, lo=-1000, hi=1000):
        """Level-order list for a random BST with n distinct values."""
        vals = self.distinct(n, lo, hi)
        root = None

        def insert(node, v):
            if node is None:
                return TreeNode(v)
            if v < node.val:
                node.left = insert(node.left, v)
            else:
                node.right = insert(node.right, v)
            return node

        for v in vals:
            root = insert(root, v)
        return from_tree(root)


# ---------- Formatting for examples ----------

def fmt(v):
    if v is None:
        return "None"
    if v is True:
        return "True"
    if v is False:
        return "False"
    if isinstance(v, str):
        return json.dumps(v)
    if isinstance(v, float):
        return repr(v)
    if isinstance(v, (list, tuple)):
        return "[" + ", ".join(fmt(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{" + ", ".join(f"{json.dumps(k)}: {fmt(x)}" for k, x in v.items()) + "}"
    return str(v)


def parse_signature(sig):
    """'twoSum(self, nums: list[int], target: int) -> list[int]' -> ('twoSum', ['nums', 'target'])"""
    name, rest = sig.split("(", 1)
    inside = rest.rsplit(")", 1)[0]
    params, depth, cur = [], 0, ""
    for ch in inside:
        if ch in "[(":
            depth += 1
        elif ch in "])":
            depth -= 1
        if ch == "," and depth == 0:
            params.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        params.append(cur.strip())
    names = [p.split(":")[0].split("=")[0].strip() for p in params]
    return name.strip(), [n for n in names if n != "self"]


CODE_LIKE = re.compile(r"\bdef |\breturn |class Solution|\n\s{4}|\bimport ")


def looks_like_code(text):
    return bool(CODE_LIKE.search(text))
