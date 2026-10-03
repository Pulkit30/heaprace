// The Python judge harness: runs one test of a solution and returns JSON.
// Single source of truth for both judges:
//  - the browser (Pyodide worker) loads it from /judge-harness.py, which scripts/copy-pyodide.ts writes from this file;
//  - the server judge (src/lib/judge/server) prepends it to the program it sends to Judge0.
// Keep this file free of runtime imports so scripts can load it directly with Node.

export const HARNESS_PY = `
import __future__, io, json, linecache, sys, traceback, typing
from collections import deque

MAX_STDOUT = 10_000
MAX_NODES = 100_000

# Node classes the judge builds from JSON. User code sees them as ListNode / TreeNode.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def _to_list_node(values):
    dummy = tail = ListNode()
    for v in values:
        tail.next = ListNode(v)
        tail = tail.next
    return dummy.next

def _from_list_node(node):
    out = []
    while node is not None:
        if len(out) >= MAX_NODES:
            raise ValueError("The returned linked list has a cycle or is too long")
        out.append(node.val)
        node = node.next
    return out

def _to_tree(values):
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

def _from_tree(root):
    out, queue = [], deque([root])
    while queue:
        if len(out) >= MAX_NODES:
            raise ValueError("The returned tree has a cycle or is too large")
        node = queue.popleft()
        out.append(None if node is None else node.val)
        if node is not None:
            queue.append(node.left)
            queue.append(node.right)
    while out and out[-1] is None:
        out.pop()
    return out

# Nodes created by the most recent CycleList build, so "NodeIndex" can report a node's position.
_built_nodes = []

def _to_cycle_list(spec):
    # spec = [values, pos]: a linked list whose tail points back to node pos (-1 means no cycle).
    global _built_nodes
    values, pos = spec[0], spec[1]
    _built_nodes = [ListNode(v) for v in values]
    for a, b in zip(_built_nodes, _built_nodes[1:]):
        a.next = b
    if _built_nodes and 0 <= pos < len(_built_nodes):
        _built_nodes[-1].next = _built_nodes[pos]
    return _built_nodes[0] if _built_nodes else None

def _node_index(node):
    if node is None:
        return -1
    for i, n in enumerate(_built_nodes):
        if n is node:
            return i
    raise ValueError("The returned node is not part of the input list")

_BUILD = {
    "ListNode": _to_list_node,
    "TreeNode": _to_tree,
    "CycleList": _to_cycle_list,
    "ListNodeArray": lambda lists: [_to_list_node(v) for v in lists],
}
_DUMP = {
    "ListNode": _from_list_node,
    "TreeNode": _from_tree,
    "NodeIndex": _node_index,
    "ListNodeArray": lambda heads: [_from_list_node(h) for h in heads],
    "TreeNodeArray": lambda roots: [_from_tree(r) for r in roots],
}

# Names available to solutions without importing, as on LeetCode: typing (Optional, List...) and the node classes.
_PRELUDE = {name: getattr(typing, name) for name in typing.__all__ if hasattr(typing, name)}
_PRELUDE.update(ListNode=ListNode, TreeNode=TreeNode)

def _to_json(v):
    if isinstance(v, (set, frozenset, tuple)):
        return list(v)
    raise TypeError(f"Return value of type {type(v).__name__} can't be judged")

def __heaprace_run(code, fn_name, args_json, arg_types_json="null", return_type=None, options_json="null"):
    out = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = out
    try:
        # Register the source so tracebacks can show the failing line.
        linecache.cache["solution.py"] = (len(code), None, code.splitlines(True), "solution.py")
        ns = {**_PRELUDE, "__name__": "solution"}
        exec(compile(code, "solution.py", "exec", flags=__future__.annotations.compiler_flag, dont_inherit=True), ns)
        options = json.loads(options_json) or {}
        args = json.loads(args_json)
        if options.get("design"):
            # Design problem: args = [operations, arguments]. The first operation constructs the class,
            # every later one calls a method; the result is the list of return values.
            if fn_name not in ns:
                raise NameError(f"Define class {fn_name}")
            ops, op_args = args
            obj, result = None, []
            for op, a in zip(ops, op_args):
                if op == fn_name:
                    obj = ns[fn_name](*a)
                    result.append(None)
                else:
                    result.append(getattr(obj, op)(*a))
        else:
            if "Solution" in ns:
                if not hasattr(ns["Solution"], fn_name):
                    raise AttributeError(f"class Solution has no method '{fn_name}'")
                fn = getattr(ns["Solution"](), fn_name)
            elif fn_name in ns:
                fn = ns[fn_name]
            else:
                raise NameError(f"Define class Solution with a method named '{fn_name}'")
            arg_types = json.loads(arg_types_json) or []
            args = [_BUILD[arg_types[i]](a) if i < len(arg_types) and arg_types[i] else a for i, a in enumerate(args)]
            result = fn(*args)
            out_arg = options.get("outArg")
            if out_arg is not None:
                # In-place problem: the answer is the modified input, not the return value.
                result = args[out_arg]
                if out_arg < len(arg_types) and arg_types[out_arg] in _DUMP:
                    result = _DUMP[arg_types[out_arg]](result)
            elif return_type:
                result = _DUMP[return_type](result)
        return json.dumps({"ok": True, "result": json.loads(json.dumps(result, default=_to_json)), "stdout": out.getvalue()[:MAX_STDOUT]})
    except BaseException as e:
        frames = [f for f in traceback.extract_tb(e.__traceback__) if f.filename == "solution.py"]
        lines = ["Traceback (most recent call last):\\n"] if frames else []
        lines += traceback.format_list(frames) + traceback.format_exception_only(type(e), e)
        return json.dumps({"ok": False, "error": "".join(lines).strip(), "stdout": out.getvalue()[:MAX_STDOUT]})
    finally:
        sys.stdout = old_stdout
`;
