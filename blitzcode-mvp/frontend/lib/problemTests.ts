import type { SubmissionResult } from "@/lib/api";

export type ProblemTestCase = {
  input: unknown[];
  expected: unknown;
  name?: string;
  unordered?: boolean;
};

export type LocalJudgeResult = SubmissionResult & {
  testsPassed: number;
  testsTotal: number;
  failedCase?: {
    input: unknown[];
    expected: unknown;
    received: unknown;
  };
};

export type JudgeProgress = {
  current: number;
  total: number;
  phase: "queued" | "compile" | "running" | "done";
  activeTest?: number;
  passedTests: number[];
};

export const problemTestSuites: Record<string, ProblemTestCase[]> = {
  "two-sum": [
    { input: [[2, 7, 11, 15], 9], expected: [0, 1] },
    { input: [[3, 2, 4], 6], expected: [1, 2] },
    { input: [[3, 3], 6], expected: [0, 1] },
  ],
  "valid-parentheses": [
    { input: ["()[]{}"], expected: true },
    { input: ["(]"], expected: false },
    { input: ["{[]}"], expected: true },
  ],
  "binary-search": [
    { input: [[-1, 0, 3, 5, 9, 12], 9], expected: 4 },
    { input: [[-1, 0, 3, 5, 9, 12], 2], expected: -1 },
    { input: [[5], 5], expected: 0 },
  ],
  "merge-sorted-array": [
    { input: [[1, 2, 3], [2, 5, 6]], expected: [1, 2, 2, 3, 5, 6] },
    { input: [[1], []], expected: [1] },
    { input: [[], [0]], expected: [0] },
  ],
  "best-time-stock": [
    { input: [[7, 1, 5, 3, 6, 4]], expected: 5 },
    { input: [[7, 6, 4, 3, 1]], expected: 0 },
    { input: [[2, 4, 1]], expected: 2 },
  ],
  "palindrome-number": [
    { input: [121], expected: true },
    { input: [-121], expected: false },
    { input: [10], expected: false },
  ],
  "maximum-subarray": [
    { input: [[-2, 1, -3, 4, -1, 2, 1, -5, 4]], expected: 6 },
    { input: [[1]], expected: 1 },
    { input: [[5, 4, -1, 7, 8]], expected: 23 },
  ],
  "flood-fill": [
    { input: [[[1, 1, 1], [1, 1, 0], [1, 0, 1]], 1, 1, 2], expected: [[2, 2, 2], [2, 2, 0], [2, 0, 1]] },
    { input: [[[0, 0, 0], [0, 0, 0]], 0, 0, 2], expected: [[2, 2, 2], [2, 2, 2]] },
  ],
  "climbing-stairs": [
    { input: [2], expected: 2 },
    { input: [3], expected: 3 },
    { input: [5], expected: 8 },
  ],
  "contains-duplicate": [
    { input: [[1, 2, 3, 1]], expected: true },
    { input: [[1, 2, 3, 4]], expected: false },
    { input: [[1, 1, 1, 3, 3, 4, 3, 2, 4, 2]], expected: true },
  ],
  "longest-substring": [
    { input: ["abcabcbb"], expected: 3 },
    { input: ["bbbbb"], expected: 1 },
    { input: ["pwwkew"], expected: 3 },
  ],
  "course-schedule": [
    { input: [2, [[1, 0]]], expected: true },
    { input: [2, [[1, 0], [0, 1]]], expected: false },
    { input: [4, [[1, 0], [2, 1], [3, 2]]], expected: true },
  ],
  "three-sum": [
    { input: [[-1, 0, 1, 2, -1, -4]], expected: [[-1, -1, 2], [-1, 0, 1]], unordered: true },
    { input: [[0, 1, 1]], expected: [], unordered: true },
    { input: [[0, 0, 0]], expected: [[0, 0, 0]], unordered: true },
  ],
  "group-anagrams": [
    { input: [["eat", "tea", "tan", "ate", "nat", "bat"]], expected: [["bat"], ["nat", "tan"], ["ate", "eat", "tea"]], unordered: true },
    { input: [[""]], expected: [[""]], unordered: true },
    { input: [["a"]], expected: [["a"]], unordered: true },
  ],
  "product-except-self": [
    { input: [[1, 2, 3, 4]], expected: [24, 12, 8, 6] },
    { input: [[-1, 1, 0, -3, 3]], expected: [0, 0, 9, 0, 0] },
  ],
  "number-of-islands": [
    { input: [[["1", "1", "1"], ["0", "1", "0"], ["1", "1", "1"]]], expected: 1 },
    { input: [[["1", "1", "0"], ["0", "0", "1"], ["1", "0", "1"]]], expected: 3 },
  ],
  "rotting-oranges": [
    { input: [[[2, 1, 1], [1, 1, 0], [0, 1, 1]]], expected: 4 },
    { input: [[[2, 1, 1], [0, 1, 1], [1, 0, 1]]], expected: -1 },
    { input: [[[0, 2]]], expected: 0 },
  ],
  "subarray-sum-k": [
    { input: [[1, 1, 1], 2], expected: 2 },
    { input: [[1, 2, 3], 3], expected: 2 },
    { input: [[1, -1, 0], 0], expected: 3 },
  ],
  "kth-largest": [
    { input: [[3, 2, 1, 5, 6, 4], 2], expected: 5 },
    { input: [[3, 2, 3, 1, 2, 4, 5, 5, 6], 4], expected: 4 },
  ],
  "daily-temperatures": [
    { input: [[73, 74, 75, 71, 69, 72, 76, 73]], expected: [1, 1, 4, 2, 1, 1, 0, 0] },
    { input: [[30, 40, 50, 60]], expected: [1, 1, 1, 0] },
    { input: [[30, 60, 90]], expected: [1, 1, 0] },
  ],
  "coin-change": [
    { input: [[1, 2, 5], 11], expected: 3 },
    { input: [[2], 3], expected: -1 },
    { input: [[1], 0], expected: 0 },
  ],
  "decode-ways": [
    { input: ["12"], expected: 2 },
    { input: ["226"], expected: 3 },
    { input: ["06"], expected: 0 },
  ],
  "word-search": [
    { input: [[["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]], "ABCCED"], expected: true },
    { input: [[["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]], "SEE"], expected: true },
    { input: [[["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]], "ABCB"], expected: false },
  ],
  "lowest-common-ancestor": [
    { input: [[3, 5, 1, 6, 2, 0, 8, null, null, 7, 4], 5, 1], expected: 3 },
    { input: [[3, 5, 1, 6, 2, 0, 8, null, null, 7, 4], 5, 4], expected: 5 },
  ],
  "median-two-arrays": [
    { input: [[1, 3], [2]], expected: 2 },
    { input: [[1, 2], [3, 4]], expected: 2.5 },
    { input: [[], [1]], expected: 1 },
  ],
  "trapping-rain-water": [
    { input: [[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]], expected: 6 },
    { input: [[4, 2, 0, 3, 2, 5]], expected: 9 },
  ],
  "largest-rectangle": [
    { input: [[2, 1, 5, 6, 2, 3]], expected: 10 },
    { input: [[2, 4]], expected: 4 },
    { input: [[1, 1]], expected: 2 },
  ],
  "word-ladder": [
    { input: ["hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]], expected: 5 },
    { input: ["hit", "cog", ["hot", "dot", "dog", "lot", "log"]], expected: 0 },
  ],
  "serialize-tree": [
    { input: [[1, 2, 3, null, null, 4, 5]], expected: [1, 2, 3, null, null, 4, 5] },
    { input: [[]], expected: [] },
  ],
  "minimum-window-substring": [
    { input: ["ADOBECODEBANC", "ABC"], expected: "BANC" },
    { input: ["a", "a"], expected: "a" },
    { input: ["a", "aa"], expected: "" },
  ],
  "regular-expression-matching": [
    { input: ["aa", "a"], expected: false },
    { input: ["aa", "a*"], expected: true },
    { input: ["ab", ".*"], expected: true },
    { input: ["aab", "c*a*b"], expected: true },
  ],
  "valid-anagram": [
    { name: "Sample 1", input: ["anagram", "nagaram"], expected: true },
    { name: "Sample 2", input: ["rat", "car"], expected: false },
    { name: "Hidden: repeated letters", input: ["aacc", "ccac"], expected: false },
    { name: "Hidden: empty strings", input: ["", ""], expected: true },
  ],
  "reverse-linked-list": [
    { name: "Sample 1", input: [[1, 2, 3, 4, 5]], expected: [5, 4, 3, 2, 1] },
    { name: "Sample 2", input: [[1, 2]], expected: [2, 1] },
    { name: "Hidden: empty list", input: [[]], expected: [] },
  ],
  "majority-element": [
    { name: "Sample 1", input: [[3, 2, 3]], expected: 3 },
    { name: "Sample 2", input: [[2, 2, 1, 1, 1, 2, 2]], expected: 2 },
    { name: "Hidden: one item", input: [[7]], expected: 7 },
  ],
  "move-zeroes": [
    { name: "Sample 1", input: [[0, 1, 0, 3, 12]], expected: [1, 3, 12, 0, 0] },
    { name: "Sample 2", input: [[0]], expected: [0] },
    { name: "Hidden: no zeroes", input: [[1, 2, 3]], expected: [1, 2, 3] },
  ],
  "first-unique-character": [
    { name: "Sample 1", input: ["leetcode"], expected: 0 },
    { name: "Sample 2", input: ["loveleetcode"], expected: 2 },
    { name: "Hidden: none", input: ["aabb"], expected: -1 },
  ],
  "roman-to-integer": [
    { name: "Sample 1", input: ["III"], expected: 3 },
    { name: "Sample 2", input: ["LVIII"], expected: 58 },
    { name: "Hidden: subtractive", input: ["MCMXCIV"], expected: 1994 },
  ],
  "sqrtx": [
    { name: "Sample 1", input: [4], expected: 2 },
    { name: "Sample 2", input: [8], expected: 2 },
    { name: "Hidden: zero", input: [0], expected: 0 },
    { name: "Hidden: large", input: [2147395599], expected: 46339 },
  ],
  "plus-one": [
    { name: "Sample 1", input: [[1, 2, 3]], expected: [1, 2, 4] },
    { name: "Sample 2", input: [[9]], expected: [1, 0] },
    { name: "Hidden: carry chain", input: [[9, 9, 9]], expected: [1, 0, 0, 0] },
  ],
  "search-insert-position": [
    { name: "Sample 1", input: [[1, 3, 5, 6], 5], expected: 2 },
    { name: "Sample 2", input: [[1, 3, 5, 6], 2], expected: 1 },
    { name: "Sample 3", input: [[1, 3, 5, 6], 7], expected: 4 },
    { name: "Hidden: before first", input: [[1, 3, 5, 6], 0], expected: 0 },
  ],
  "remove-duplicates-sorted-array": [
    { name: "Sample 1", input: [[1, 1, 2]], expected: [1, 2] },
    { name: "Sample 2", input: [[0, 0, 1, 1, 1, 2, 2, 3, 3, 4]], expected: [0, 1, 2, 3, 4] },
    { name: "Hidden: single", input: [[1]], expected: [1] },
  ],
  "missing-number": [
    { name: "Sample 1", input: [[3, 0, 1]], expected: 2 },
    { name: "Sample 2", input: [[0, 1]], expected: 2 },
    { name: "Hidden: missing zero", input: [[1, 2, 3]], expected: 0 },
  ],
  "single-number": [
    { name: "Sample 1", input: [[2, 2, 1]], expected: 1 },
    { name: "Sample 2", input: [[4, 1, 2, 1, 2]], expected: 4 },
    { name: "Hidden: negative", input: [[-1, -1, -2]], expected: -2 },
  ],
};

export function getProblemTests(problemId: string) {
  return problemTestSuites[problemId] ?? [];
}

export async function runJavaScriptSolution(
  problemId: string,
  code: string,
  options?: {
    delayMs?: number;
    onProgress?: (progress: JudgeProgress) => void;
  }
): Promise<LocalJudgeResult> {
  const tests = getProblemTests(problemId);
  if (tests.length === 0) {
    return {
      status: "error",
      message: "No tests for this problem yet.",
      testsPassed: 0,
      testsTotal: 0,
    };
  }

  let solve: unknown;
  const delayMs = options?.delayMs ?? 420;
  const passedTests: number[] = [];

  options?.onProgress?.({ current: 0, total: tests.length, phase: "queued", passedTests });
  await wait(Math.max(350, delayMs));

  options?.onProgress?.({ current: 0, total: tests.length, phase: "compile", passedTests });
  await wait(Math.max(500, delayMs));

  try {
    solve = new Function(`${code}\nreturn typeof solve === "function" ? solve : null;`)();
  } catch (error) {
    options?.onProgress?.({ current: 0, total: tests.length, phase: "done", passedTests });
    return {
      status: "error",
      message: `Compile error: ${formatError(error)}`,
      testsPassed: 0,
      testsTotal: tests.length,
    };
  }

  if (typeof solve !== "function") {
    options?.onProgress?.({ current: 0, total: tests.length, phase: "done", passedTests });
    return {
      status: "error",
      message: "Declare a solve(...) function first.",
      testsPassed: 0,
      testsTotal: tests.length,
    };
  }

  const startedAt = performance.now();
  for (let index = 0; index < tests.length; index += 1) {
    const test = tests[index];
    let received: unknown;
    options?.onProgress?.({ current: index, total: tests.length, phase: "running", activeTest: index + 1, passedTests: [...passedTests] });
    await wait(delayMs + Math.min(index * 70, 280));

    try {
      const safeInput = clone(test.input);
      received = await Promise.resolve(solve(...safeInput));
    } catch (error) {
      options?.onProgress?.({ current: index, total: tests.length, phase: "done", activeTest: index + 1, passedTests: [...passedTests] });
      return {
        status: "error",
        message: `Runtime error on test ${index + 1}: ${formatError(error)}`,
        executionTimeMs: Math.round(performance.now() - startedAt),
        testsPassed: index,
        testsTotal: tests.length,
        failedCase: { input: test.input, expected: test.expected, received: "runtime error" },
      };
    }

    if (!isEqual(received, test.expected, test.unordered)) {
      options?.onProgress?.({ current: index, total: tests.length, phase: "done", activeTest: index + 1, passedTests: [...passedTests] });
      return {
        status: "wrong_answer",
        message: `Test ${index + 1} failed.`,
        executionTimeMs: Math.round(performance.now() - startedAt),
        testsPassed: index,
        testsTotal: tests.length,
        failedCase: { input: test.input, expected: test.expected, received },
      };
    }

    passedTests.push(index + 1);
    options?.onProgress?.({ current: index + 1, total: tests.length, phase: "running", activeTest: index + 1, passedTests: [...passedTests] });
  }

  await wait(260);
  options?.onProgress?.({ current: tests.length, total: tests.length, phase: "done", passedTests: [...passedTests] });
  return {
    status: "accepted",
    message: "All tests passed.",
    executionTimeMs: Math.round(performance.now() - startedAt),
    testsPassed: tests.length,
    testsTotal: tests.length,
  };
}

function wait(ms: number) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}
function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T;
}

function isEqual(left: unknown, right: unknown, unordered = false): boolean {
  const normalizedLeft = unordered ? normalizeUnordered(left) : normalize(left);
  const normalizedRight = unordered ? normalizeUnordered(right) : normalize(right);
  return JSON.stringify(normalizedLeft) === JSON.stringify(normalizedRight);
}

function normalize(value: unknown): unknown {
  if (typeof value === "number") {
    return Number.isInteger(value) ? value : Number(value.toFixed(6));
  }
  if (Array.isArray(value)) return value.map(normalize);
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value)
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([key, item]) => [key, normalize(item)])
    );
  }
  return value;
}

function normalizeUnordered(value: unknown): unknown {
  if (!Array.isArray(value)) return normalize(value);
  return value
    .map(normalizeUnordered)
    .sort((a, b) => JSON.stringify(a).localeCompare(JSON.stringify(b)));
}

function formatError(error: unknown) {
  return error instanceof Error ? error.message : String(error);
}

