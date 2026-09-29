"""Reference solutions used only by scripts/verify-problems.ts to check test data.

Never import this from the app: it would ship the answers to the browser.
Reads [{slug, functionName, tests}] as JSON on stdin, prints {slug: [results]} on stdout.
"""

import heapq
import json
import sys
from collections import Counter, deque


class TwoSum:
    def twoSum(self, nums, target):
        seen = {}
        for i, x in enumerate(nums):
            if target - x in seen:
                return [seen[target - x], i]
            seen[x] = i


class ValidParentheses:
    def isValid(self, s):
        pairs = {")": "(", "]": "[", "}": "{"}
        stack = []
        for c in s:
            if c in pairs:
                if not stack or stack.pop() != pairs[c]:
                    return False
            else:
                stack.append(c)
        return not stack


class BestTime:
    def maxProfit(self, prices):
        best, low = 0, float("inf")
        for p in prices:
            low = min(low, p)
            best = max(best, p - low)
        return best


class ContainsDuplicate:
    def containsDuplicate(self, nums):
        return len(set(nums)) != len(nums)


class MaxSubarray:
    def maxSubArray(self, nums):
        best = cur = nums[0]
        for x in nums[1:]:
            cur = max(x, cur + x)
            best = max(best, cur)
        return best


class LongestSubstring:
    def lengthOfLongestSubstring(self, s):
        last, start, best = {}, 0, 0
        for i, c in enumerate(s):
            if last.get(c, -1) >= start:
                start = last[c] + 1
            last[c] = i
            best = max(best, i - start + 1)
        return best


class KthLargest:
    def findKthLargest(self, nums, k):
        heap = []
        for x in nums:
            heapq.heappush(heap, x)
            if len(heap) > k:
                heapq.heappop(heap)
        return heap[0]


class TopK:
    def topKFrequent(self, nums, k):
        return [x for x, _ in Counter(nums).most_common(k)]


class MergeIntervals:
    def merge(self, intervals):
        out = []
        for s, e in sorted(intervals):
            if out and s <= out[-1][1]:
                out[-1][1] = max(out[-1][1], e)
            else:
                out.append([s, e])
        return out


class TrappingRainWater:
    def trap(self, height):
        l, r = 0, len(height) - 1
        lmax = rmax = water = 0
        while l < r:
            if height[l] < height[r]:
                lmax = max(lmax, height[l])
                water += lmax - height[l]
                l += 1
            else:
                rmax = max(rmax, height[r])
                water += rmax - height[r]
                r -= 1
        return water



# --- Node helpers (mirror the judge in public/pyodide-worker.js) ---

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
    while node:
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
        out.append(node.val if node else None)
        if node:
            queue.append(node.left)
            queue.append(node.right)
    while out and out[-1] is None:
        out.pop()
    return out


BUILD = {"ListNode": to_list_node, "TreeNode": to_tree}
DUMP = {"ListNode": from_list_node, "TreeNode": from_tree}


class SubarraySum:
    def subarraySum(self, nums, k):
        seen, total, count = Counter({0: 1}), 0, 0
        for x in nums:
            total += x
            count += seen[total - k]
            seen[total] += 1
        return count


class Disappeared:
    def findDisappearedNumbers(self, nums):
        present = set(nums)
        return [i for i in range(1, len(nums) + 1) if i not in present]


class Spiral:
    def spiralOrder(self, matrix):
        out = []
        while matrix:
            out += matrix.pop(0)
            matrix = [list(r) for r in zip(*matrix)][::-1]
        return out


class RotatedSearch:
    def search(self, nums, target):
        lo, hi = 0, len(nums) - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if nums[mid] == target:
                return mid
            if nums[lo] <= nums[mid]:
                if nums[lo] <= target < nums[mid]:
                    hi = mid - 1
                else:
                    lo = mid + 1
            else:
                if nums[mid] < target <= nums[hi]:
                    lo = mid + 1
                else:
                    hi = mid - 1
        return -1


class ReverseList:
    def reverseList(self, head):
        prev = None
        while head:
            head.next, prev, head = prev, head, head.next
        return prev


class DailyTemps:
    def dailyTemperatures(self, temperatures):
        answer, stack = [0] * len(temperatures), []
        for i, t in enumerate(temperatures):
            while stack and temperatures[stack[-1]] < t:
                j = stack.pop()
                answer[j] = i - j
            stack.append(i)
        return answer


class FindDuplicate:
    def findDuplicate(self, nums):
        slow = fast = nums[0]
        while True:
            slow, fast = nums[slow], nums[nums[fast]]
            if slow == fast:
                break
        slow = nums[0]
        while slow != fast:
            slow, fast = nums[slow], nums[fast]
        return slow


class MaxDepth:
    def maxDepth(self, root):
        return 0 if not root else 1 + max(self.maxDepth(root.left), self.maxDepth(root.right))


class LevelOrder:
    def levelOrder(self, root):
        out, level = [], [root] if root else []
        while level:
            out.append([n.val for n in level])
            level = [c for n in level for c in (n.left, n.right) if c]
        return out


class Subsets:
    def subsets(self, nums):
        out = [[]]
        for x in nums:
            out += [s + [x] for s in out]
        return out


class ReplaceWords:
    def replaceWords(self, dictionary, sentence):
        roots = set(dictionary)
        def root(word):
            for i in range(1, len(word) + 1):
                if word[:i] in roots:
                    return word[:i]
            return word
        return " ".join(root(w) for w in sentence.split())


class Islands:
    def numIslands(self, grid):
        rows, cols, seen, count = len(grid), len(grid[0]), set(), 0
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == "1" and (r, c) not in seen:
                    count += 1
                    stack = [(r, c)]
                    seen.add((r, c))
                    while stack:
                        y, x = stack.pop()
                        for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                            if 0 <= ny < rows and 0 <= nx < cols and grid[ny][nx] == "1" and (ny, nx) not in seen:
                                seen.add((ny, nx))
                                stack.append((ny, nx))
        return count


class ClimbStairs:
    def climbStairs(self, n):
        a, b = 1, 1
        for _ in range(n):
            a, b = b, a + b
        return a


class KthSmallestMatrix:
    def kthSmallest(self, matrix, k):
        return sorted(x for row in matrix for x in row)[k - 1]


class IPO:
    def findMaximizedCapital(self, k, w, profits, capital):
        projects = sorted(zip(capital, profits))
        available, i = [], 0
        for _ in range(k):
            while i < len(projects) and projects[i][0] <= w:
                heapq.heappush(available, -projects[i][1])
                i += 1
            if not available:
                break
            w -= heapq.heappop(available)
        return w


class SingleNumber:
    def singleNumber(self, nums):
        out = 0
        for x in nums:
            out ^= x
        return out


class LCS:
    def longestCommonSubsequence(self, text1, text2):
        prev = [0] * (len(text2) + 1)
        for a in text1:
            cur = [0]
            for j, b in enumerate(text2):
                cur.append(prev[j] + 1 if a == b else max(prev[j + 1], cur[j]))
            prev = cur
        return prev[-1]


class RedundantConnection:
    def findRedundantConnection(self, edges):
        parent = list(range(len(edges) + 1))
        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        for a, b in edges:
            ra, rb = find(a), find(b)
            if ra == rb:
                return [a, b]
            parent[ra] = rb


class CourseSchedule:
    def canFinish(self, numCourses, prerequisites):
        indegree, graph = [0] * numCourses, [[] for _ in range(numCourses)]
        for a, b in prerequisites:
            graph[b].append(a)
            indegree[a] += 1
        queue = deque(i for i in range(numCourses) if indegree[i] == 0)
        done = 0
        while queue:
            node = queue.popleft()
            done += 1
            for nxt in graph[node]:
                indegree[nxt] -= 1
                if indegree[nxt] == 0:
                    queue.append(nxt)
        return done == numCourses


class NetworkDelay:
    def networkDelayTime(self, times, n, k):
        graph = {}
        for u, v, w in times:
            graph.setdefault(u, []).append((v, w))
        dist, heap = {}, [(0, k)]
        while heap:
            d, node = heapq.heappop(heap)
            if node in dist:
                continue
            dist[node] = d
            for v, w in graph.get(node, []):
                if v not in dist:
                    heapq.heappush(heap, (d + w, v))
        return max(dist.values()) if len(dist) == n else -1


class HappyNumber:
    def isHappy(self, n):
        seen = set()
        while n != 1 and n not in seen:
            seen.add(n)
            n = sum(int(d) ** 2 for d in str(n))
        return n == 1


REFERENCE = {
    "two-sum": TwoSum,
    "valid-parentheses": ValidParentheses,
    "best-time-to-buy-and-sell-stock": BestTime,
    "contains-duplicate": ContainsDuplicate,
    "maximum-subarray": MaxSubarray,
    "longest-substring-without-repeating-characters": LongestSubstring,
    "kth-largest-element-in-an-array": KthLargest,
    "top-k-frequent-elements": TopK,
    "merge-intervals": MergeIntervals,
    "trapping-rain-water": TrappingRainWater,
    "subarray-sum-equals-k": SubarraySum,
    "find-all-numbers-disappeared-in-an-array": Disappeared,
    "spiral-matrix": Spiral,
    "search-in-rotated-sorted-array": RotatedSearch,
    "reverse-linked-list": ReverseList,
    "daily-temperatures": DailyTemps,
    "find-the-duplicate-number": FindDuplicate,
    "maximum-depth-of-binary-tree": MaxDepth,
    "binary-tree-level-order-traversal": LevelOrder,
    "subsets": Subsets,
    "replace-words": ReplaceWords,
    "number-of-islands": Islands,
    "climbing-stairs": ClimbStairs,
    "kth-smallest-element-in-a-sorted-matrix": KthSmallestMatrix,
    "ipo": IPO,
    "single-number": SingleNumber,
    "longest-common-subsequence": LCS,
    "redundant-connection": RedundantConnection,
    "course-schedule": CourseSchedule,
    "network-delay-time": NetworkDelay,
    "happy-number": HappyNumber,
}

if __name__ == "__main__":
    out = {}
    for p in json.load(sys.stdin):
        cls = REFERENCE.get(p["slug"])
        if cls is None:
            out[p["slug"]] = None
            continue
        fn = getattr(cls(), p["functionName"])
        arg_types = p.get("argTypes") or []
        results = []
        for t in p["tests"]:
            args = json.loads(json.dumps(t["args"]))
            args = [BUILD[arg_types[i]](a) if i < len(arg_types) and arg_types[i] else a for i, a in enumerate(args)]
            result = fn(*args)
            results.append(DUMP[p["returnType"]](result) if p.get("returnType") else result)
        out[p["slug"]] = results
    json.dump(out, sys.stdout)
