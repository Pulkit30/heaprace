"""Reference solutions used only by scripts/verify-problems.ts to check test data.

Never import this from the app: it would ship the answers to the browser.
Reads [{slug, functionName, tests}] as JSON on stdin, prints {slug: [results]} on stdout.
"""

import heapq
import json
import sys
from collections import Counter


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
}

if __name__ == "__main__":
    out = {}
    for p in json.load(sys.stdin):
        cls = REFERENCE.get(p["slug"])
        if cls is None:
            out[p["slug"]] = None
            continue
        fn = getattr(cls(), p["functionName"])
        out[p["slug"]] = [fn(*json.loads(json.dumps(t["args"]))) for t in p["tests"]]
    json.dump(out, sys.stdout)
