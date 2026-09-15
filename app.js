const runtimeConfig = window.CODE_BLITZ_CONFIG || {};
const API_BASE = runtimeConfig.apiBase ?? "http://127.0.0.1:8000";
const WS_BASE = runtimeConfig.wsBase ?? (API_BASE ? API_BASE.replace(/^http/, "ws") : window.location.origin.replace(/^http/, "ws"));
const AUTH_TOKEN_KEY = "codeBlitzToken";
const AUTH_USER_KEY = "codeBlitzUser";

const courseCatalogFallback = [
  {
    slug: "js-algorithm-start",
    title: "JavaScript Algorithm Start",
    level: "beginner",
    access_type: "free",
    price_cents: 0,
    currency: "USD",
    summary: "A fast course for learning arrays, strings and hash maps through Code Blitz style tasks.",
    tags: ["javascript", "arrays", "hash-map"],
    lesson_count: 3,
    practice_problems: [
      { slug: "pair-sprint", title: "Pair Sprint", difficulty: "easy", tags: ["array", "hash-map"], position: 1 },
      { slug: "clean-duplicates", title: "Clean Duplicates", difficulty: "easy", tags: ["array", "set"], position: 2 },
      { slug: "first-unique", title: "First Unique", difficulty: "easy", tags: ["string", "map"], position: 3 },
      { slug: "even-signal", title: "Even Signal", difficulty: "easy", tags: ["array", "counter"], position: 4 },
      { slug: "reverse-words-lite", title: "Reverse Words Lite", difficulty: "easy", tags: ["string", "parsing"], position: 5 },
      { slug: "min-gap", title: "Min Gap", difficulty: "easy", tags: ["array", "sorting"], position: 6 },
      { slug: "digit-sum", title: "Digit Sum", difficulty: "easy", tags: ["math", "number"], position: 7 },
      { slug: "anagram-groups-count", title: "Anagram Groups Count", difficulty: "medium", tags: ["hashmap", "string"], position: 8 },
    ],
    lessons: [
      { id: "local-js-1", position: 1, title: "Solve Function Contract", summary: "How Code Blitz calls solve(...) and how to return clean values.", kind: "lesson", duration_minutes: 8, completed: false },
      { id: "local-js-2", position: 2, title: "Arrays Under Timer", summary: "Linear scans, counters and fast edge-case checks.", kind: "practice", duration_minutes: 14, completed: false },
      { id: "local-js-3", position: 3, title: "Hash Map Warmups", summary: "Two-sum patterns, frequency maps and lookup thinking.", kind: "practice", duration_minutes: 18, completed: false },
    ],
  },
  {
    slug: "debugging-arena",
    title: "Debugging Arena",
    level: "beginner",
    access_type: "free",
    price_cents: 0,
    currency: "USD",
    summary: "Learn how to read failed tests, trace variables and fix solutions without guessing.",
    tags: ["debugging", "tests", "runtime"],
    lesson_count: 3,
    practice_problems: [
      { slug: "max-streak", title: "Max Streak", difficulty: "easy", tags: ["array", "counter"], position: 1 },
      { slug: "missing-level", title: "Missing Level", difficulty: "easy", tags: ["math", "array"], position: 2 },
      { slug: "prefix-alarm", title: "Prefix Alarm", difficulty: "easy", tags: ["array", "prefix-sum"], position: 3 },
      { slug: "score-normalizer", title: "Score Normalizer", difficulty: "easy", tags: ["array", "math"], position: 4 },
      { slug: "rotating-log", title: "Rotating Log", difficulty: "medium", tags: ["set", "simulation"], position: 5 },
      { slug: "matrix-ring-sum", title: "Matrix Ring Sum", difficulty: "medium", tags: ["matrix", "array"], position: 6 },
    ],
    lessons: [
      { id: "local-debug-1", position: 1, title: "Reading Test Output", summary: "Expected vs received, runtime errors and why one case matters.", kind: "lesson", duration_minutes: 10, completed: false },
      { id: "local-debug-2", position: 2, title: "Edge Case Checklist", summary: "Empty arrays, duplicates, negative values and single-item inputs.", kind: "practice", duration_minutes: 16, completed: false },
      { id: "local-debug-3", position: 3, title: "Step Through a Bad Loop", summary: "Use small inputs to find off-by-one mistakes.", kind: "lab", duration_minutes: 12, completed: false },
    ],
  },
  {
    slug: "blitz-patterns-core",
    title: "Blitz Patterns Core",
    level: "intermediate",
    access_type: "premium",
    price_cents: 1299,
    currency: "USD",
    summary: "Sliding windows, prefix sums, stacks and binary search patterns for ranked speed.",
    tags: ["patterns", "sliding-window", "binary-search"],
    lesson_count: 3,
    practice_problems: [
      { slug: "window-sum", title: "Window Sum", difficulty: "medium", tags: ["sliding-window"], position: 1 },
      { slug: "subarray-target", title: "Subarray Target", difficulty: "medium", tags: ["prefix-sum"], position: 2 },
      { slug: "longest-unique", title: "Longest Unique", difficulty: "medium", tags: ["sliding-window"], position: 3 },
      { slug: "relay-optimizer", title: "Relay Optimizer", difficulty: "hard", tags: ["binary-search"], position: 4 },
    ],
    lessons: [
      { id: "local-patterns-1", position: 1, title: "Sliding Window Control", summary: "When to expand, when to shrink and how to keep the invariant.", kind: "lesson", duration_minutes: 22, completed: false },
      { id: "local-patterns-2", position: 2, title: "Prefix Sum Signals", summary: "Range sums, target subarrays and quick transformations.", kind: "practice", duration_minutes: 18, completed: false },
      { id: "local-patterns-3", position: 3, title: "Binary Search on Answer", summary: "Use monotonic checks for optimizer-style hard tasks.", kind: "lab", duration_minutes: 25, completed: false },
    ],
  },
  {
    slug: "graph-race-lab",
    title: "Graph Race Lab",
    level: "intermediate",
    access_type: "premium",
    price_cents: 1599,
    currency: "USD",
    summary: "BFS, DFS, grids and shortest routes prepared for timed matches.",
    tags: ["graph", "bfs", "dfs", "grid"],
    lesson_count: 3,
    practice_problems: [
      { slug: "island-count", title: "Island Count", difficulty: "medium", tags: ["grid", "dfs"], position: 1 },
      { slug: "grid-escape", title: "Grid Escape", difficulty: "hard", tags: ["grid", "bfs"], position: 2 },
      { slug: "level-bridges", title: "Level Bridges", difficulty: "medium", tags: ["graph", "bfs"], position: 3 },
      { slug: "maze-checkpoints", title: "Maze Checkpoints", difficulty: "hard", tags: ["grid", "bfs"], position: 4 },
      { slug: "weighted-checkpoints", title: "Weighted Checkpoints", difficulty: "hard", tags: ["graph", "shortest_path"], position: 5 },
    ],
    lessons: [
      { id: "local-graph-1", position: 1, title: "Build the Adjacency List", summary: "Turn edges into fast traversal data structures.", kind: "lesson", duration_minutes: 16, completed: false },
      { id: "local-graph-2", position: 2, title: "BFS for Shortest Paths", summary: "Queue, distance and visited state.", kind: "practice", duration_minutes: 24, completed: false },
      { id: "local-graph-3", position: 3, title: "Grid State Tricks", summary: "Track row, column and extra state like checkpoints.", kind: "lab", duration_minutes: 28, completed: false },
    ],
  },
  {
    slug: "dp-for-finishers",
    title: "DP for Finishers",
    level: "advanced",
    access_type: "premium",
    price_cents: 1999,
    currency: "USD",
    summary: "Dynamic programming for the final hard task in a blitz match.",
    tags: ["dp", "optimization", "hard"],
    lesson_count: 3,
    practice_problems: [
      { slug: "coin-race", title: "Coin Race", difficulty: "medium", tags: ["dp"], position: 1 },
      { slug: "memory-tiles", title: "Memory Tiles", difficulty: "hard", tags: ["dp", "string"], position: 2 },
      { slug: "burst-combos", title: "Burst Combos", difficulty: "hard", tags: ["dp", "array"], position: 3 },
      { slug: "cooldown-profit", title: "Cooldown Profit", difficulty: "hard", tags: ["dp"], position: 4 },
      { slug: "partition-balance", title: "Partition Balance", difficulty: "hard", tags: ["dp", "subset"], position: 5 },
    ],
    lessons: [
      { id: "local-dp-1", position: 1, title: "State Before Code", summary: "Define what dp[i] means before writing loops.", kind: "lesson", duration_minutes: 20, completed: false },
      { id: "local-dp-2", position: 2, title: "Non-Adjacent Choices", summary: "Choose or skip patterns with rolling variables.", kind: "practice", duration_minutes: 18, completed: false },
      { id: "local-dp-3", position: 3, title: "Word Splits and Paths", summary: "Break strings and sequences into valid transitions.", kind: "lab", duration_minutes: 30, completed: false },
    ],
  },
];

const platformCourseFallback = {
  slug: "code-blitz-platform-start",
  title: "Code Blitz Platform Start",
  level: "beginner",
  access_type: "free",
  price_cents: 0,
  currency: "USD",
  summary: "A free introduction to Code Blitz: what the platform is, how arena matches work, and how to practice without getting lost.",
  tags: ["platform", "arena", "debugging", "rating"],
  lesson_count: 4,
  practice_problems: [
    { slug: "pair-sprint", title: "Pair Sprint", difficulty: "easy", tags: ["array", "hash-map"], position: 1 },
    { slug: "clean-duplicates", title: "Clean Duplicates", difficulty: "easy", tags: ["array", "set"], position: 2 },
    { slug: "first-unique", title: "First Unique", difficulty: "easy", tags: ["string", "map"], position: 3 },
    { slug: "max-streak", title: "Max Streak", difficulty: "easy", tags: ["array", "counter"], position: 4 },
    { slug: "reverse-words-lite", title: "Reverse Words Lite", difficulty: "easy", tags: ["string", "parsing"], position: 5 },
  ],
  lessons: [
    {
      id: "local-platform-1",
      position: 1,
      title: "What Code Blitz Is",
      summary: "Understand the idea of the platform before jumping into matches.",
      content: "Code Blitz is a coding arena where practice feels like a live match. You solve algorithmic tasks, see progress, run tests, submit solutions, and build rating after registration.",
      checklist: ["Know where Arena starts", "Know why tasks are randomized", "Know that rating appears after login"],
      kind: "lesson",
      duration_minutes: 7,
      completed: false,
    },
    {
      id: "local-platform-2",
      position: 2,
      title: "How Arena Matches Work",
      summary: "Learn the match payload, timer, task strip, and progress race.",
      content: "A ranked blitz match gives both players the same payload: three easy tasks, two medium tasks, and one hard task. The goal is to solve accurately under one shared match timer.",
      checklist: ["Read the current task first", "Use Run for sample tests", "Use Submit only when the idea is ready"],
      kind: "lesson",
      duration_minutes: 10,
      completed: false,
    },
    {
      id: "local-platform-3",
      position: 3,
      title: "Run, Submit, and Debug",
      summary: "Use the editor, terminal output, and test results like a real coding workflow.",
      content: "Run checks a smaller visible set of tests so you can debug quickly. Submit checks a larger hidden set and records the real result. When a case fails, compare expected and actual before changing the algorithm.",
      checklist: ["Read expected vs actual", "Fix one bug at a time", "Keep solve(...) as the entry point"],
      kind: "practice",
      duration_minutes: 12,
      completed: false,
    },
    {
      id: "local-platform-4",
      position: 4,
      title: "Your First Practice Route",
      summary: "Open linked starter tasks and learn the basic rhythm of Code Blitz.",
      content: "Start with small tasks to learn the platform rhythm: read, code, run, inspect output, submit, then move to the next task. Speed comes after the loop feels calm.",
      checklist: ["Solve one array task", "Solve one string task", "Review a failed test if one appears"],
      kind: "practice",
      duration_minutes: 15,
      completed: false,
    },
  ],
};

courseCatalogFallback.splice(0, courseCatalogFallback.length, platformCourseFallback);

const taskBank = [
  {
    title: "Pair Sprint",
    difficulty: "Easy",
    description: "Дан массив чисел и цель. Верни индексы двух элементов, сумма которых равна цели.",
    tags: ["Array", "Hash Map"],
    checks: ["Map", "seen"],
    starter: `function solve(nums, target) {
  const seen = new Map();

  for (let i = 0; i < nums.length; i++) {
    const need = target - nums[i];
    if (seen.has(need)) return [seen.get(need), i];
    seen.set(nums[i], i);
  }

  return [];
}`,
    opponent: `function solve(nums, target) {
  const seen = {};
  for (let i = 0; i < nums.length; i++) {
    const need = target - nums[i];
    if (seen[need] !== undefined) return [seen[need], i];
    seen[nums[i]] = i;
  }
}`,
    cases: [
      { input: "[2,7,11,15], 9", expected: "[0,1]" },
      { input: "[3,2,4], 6", expected: "[1,2]" },
      { input: "[3,3], 6", expected: "[0,1]" },
    ],
  },
  {
    title: "Bracket Dash",
    difficulty: "Easy",
    description: "Проверь строку со скобками: каждая открытая скобка должна закрываться правильной парой.",
    tags: ["Stack", "String"],
    checks: ["stack", "pairs"],
    starter: `function solve(s) {
  const pairs = { ")": "(", "]": "[", "}": "{" };
  const stack = [];

  for (const ch of s) {
    if ("([{".includes(ch)) stack.push(ch);
    else if (stack.pop() !== pairs[ch]) return false;
  }

  return stack.length === 0;
}`,
    opponent: `function solve(s) {
  const stack = [];
  for (const ch of s) {
    if ("([{".includes(ch)) stack.push(ch);
    if (ch === ")" && stack.pop() !== "(") return false;
  }
  return stack.length === 0;
}`,
    cases: [
      { input: '"()[]{}"', expected: "true" },
      { input: '"(]"', expected: "false" },
      { input: '"{[]}"', expected: "true" },
    ],
  },
  {
    title: "Max Streak",
    difficulty: "Easy",
    description: "Верни максимальное количество подряд идущих единиц в бинарном массиве.",
    tags: ["Array", "Counter"],
    checks: ["best", "count"],
    starter: `function solve(nums) {
  let best = 0;
  let count = 0;

  for (const n of nums) {
    count = n === 1 ? count + 1 : 0;
    best = Math.max(best, count);
  }

  return best;
}`,
    opponent: `function solve(nums) {
  let best = 0, count = 0;
  for (const n of nums) {
    if (n === 1) count++;
    else count = 0;
    best = Math.max(best, count);
  }
  return best;
}`,
    cases: [
      { input: "[1,1,0,1,1,1]", expected: "3" },
      { input: "[1,0,1,1,0,1]", expected: "2" },
      { input: "[0,0,0]", expected: "0" },
    ],
  },
  {
    title: "Clean Duplicates",
    difficulty: "Easy",
    description: "Верни массив без повторов, сохранив порядок первого появления элементов.",
    tags: ["Set", "Array"],
    checks: ["Set", "result"],
    starter: `function solve(nums) {
  const seen = new Set();
  const result = [];

  for (const n of nums) {
    if (!seen.has(n)) {
      seen.add(n);
      result.push(n);
    }
  }

  return result;
}`,
    opponent: `function solve(nums) {
  const seen = new Set();
  return nums.filter((n) => {
    if (seen.has(n)) return false;
    seen.add(n);
    return true;
  });
}`,
    cases: [
      { input: "[1,2,2,3,1]", expected: "[1,2,3]" },
      { input: "[4,4,4]", expected: "[4]" },
      { input: "[]", expected: "[]" },
    ],
  },
  {
    title: "First Unique",
    difficulty: "Easy",
    description: "Найди первый символ в строке, который встречается ровно один раз.",
    tags: ["String", "Map"],
    checks: ["freq", "for"],
    starter: `function solve(s) {
  const freq = {};

  for (const ch of s) freq[ch] = (freq[ch] || 0) + 1;
  for (const ch of s) if (freq[ch] === 1) return ch;

  return "";
}`,
    opponent: `function solve(s) {
  const freq = {};
  for (const ch of s) freq[ch] = (freq[ch] || 0) + 1;
  return [...s].find((ch) => freq[ch] === 1) || "";
}`,
    cases: [
      { input: '"leetcode"', expected: '"l"' },
      { input: '"aabbc"', expected: '"c"' },
      { input: '"aabb"', expected: '""' },
    ],
  },
  {
    title: "Merge Sorted",
    difficulty: "Easy",
    description: "Слей два отсортированных массива в один отсортированный массив.",
    tags: ["Two Pointers"],
    checks: ["i", "j", "result"],
    starter: `function solve(a, b) {
  let i = 0;
  let j = 0;
  const result = [];

  while (i < a.length || j < b.length) {
    if (j >= b.length || a[i] <= b[j]) result.push(a[i++]);
    else result.push(b[j++]);
  }

  return result;
}`,
    opponent: `function solve(a, b) {
  const result = [];
  let i = 0, j = 0;
  while (i < a.length && j < b.length) {
    result.push(a[i] < b[j] ? a[i++] : b[j++]);
  }
  return result.concat(a.slice(i), b.slice(j));
}`,
    cases: [
      { input: "[1,3], [2,4]", expected: "[1,2,3,4]" },
      { input: "[], [1]", expected: "[1]" },
      { input: "[2], []", expected: "[2]" },
    ],
  },
  {
    title: "Mirror Word",
    difficulty: "Easy",
    description: "Верни true, если строка является палиндромом после удаления пробелов и приведения к нижнему регистру.",
    tags: ["String", "Two Pointers"],
    checks: ["left", "right"],
    starter: `function solve(s) {
  const clean = s.toLowerCase().replaceAll(" ", "");
  let left = 0;
  let right = clean.length - 1;

  while (left < right) {
    if (clean[left] !== clean[right]) return false;
    left++;
    right--;
  }

  return true;
}`,
    opponent: `function solve(s) {
  const clean = s.toLowerCase().replaceAll(" ", "");
  let left = 0, right = clean.length - 1;
  while (left < right) {
    if (clean[left++] !== clean[right--]) return false;
  }
  return true;
}`,
    cases: [
      { input: '"Never odd or even"', expected: "true" },
      { input: '"race car"', expected: "true" },
      { input: '"code"', expected: "false" },
    ],
  },
  {
    title: "Missing Level",
    difficulty: "Easy",
    description: "Дан массив чисел от 0 до n без одного числа. Найди пропущенное.",
    tags: ["Math", "Array"],
    checks: ["expected", "actual"],
    starter: `function solve(nums) {
  const n = nums.length;
  const expected = (n * (n + 1)) / 2;
  const actual = nums.reduce((sum, n) => sum + n, 0);

  return expected - actual;
}`,
    opponent: `function solve(nums) {
  const n = nums.length;
  const expected = (n * (n + 1)) / 2;
  const actual = nums.reduce((sum, x) => sum + x, 0);
  return expected - actual;
}`,
    cases: [
      { input: "[3,0,1]", expected: "2" },
      { input: "[0,1]", expected: "2" },
      { input: "[9,6,4,2,3,5,7,0,1]", expected: "8" },
    ],
  },
  {
    title: "Most Frequent",
    difficulty: "Medium",
    description: "Верни число, которое встречается чаще всего. Если таких несколько, верни любое.",
    tags: ["Map", "Frequency"],
    checks: ["Map", "best"],
    starter: `function solve(nums) {
  const freq = new Map();
  let best = nums[0];

  for (const n of nums) {
    freq.set(n, (freq.get(n) || 0) + 1);
    if (freq.get(n) > (freq.get(best) || 0)) best = n;
  }

  return best;
}`,
    opponent: `function solve(nums) {
  const freq = new Map();
  let best = nums[0];
  for (const n of nums) {
    freq.set(n, (freq.get(n) || 0) + 1);
    if (freq.get(n) > freq.get(best)) best = n;
  }
  return best;
}`,
    cases: [
      { input: "[1,2,2,3]", expected: "2" },
      { input: "[5,5,1,1,1]", expected: "1" },
      { input: "[7]", expected: "7" },
    ],
  },
  {
    title: "Window Sum",
    difficulty: "Medium",
    description: "Найди максимальную сумму подмассива длины k.",
    tags: ["Sliding Window"],
    checks: ["window", "best"],
    starter: `function solve(nums, k) {
  let window = 0;
  let best = -Infinity;

  for (let i = 0; i < nums.length; i++) {
    window += nums[i];
    if (i >= k) window -= nums[i - k];
    if (i >= k - 1) best = Math.max(best, window);
  }

  return best;
}`,
    opponent: `function solve(nums, k) {
  let window = 0, best = -Infinity;
  for (let i = 0; i < nums.length; i++) {
    window += nums[i];
    if (i >= k) window -= nums[i - k];
    if (i >= k - 1) best = Math.max(best, window);
  }
  return best;
}`,
    cases: [
      { input: "[1,4,2,10,2], 3", expected: "16" },
      { input: "[5,1,3], 2", expected: "6" },
      { input: "[-1,-2,-3], 2", expected: "-3" },
    ],
  },
  {
    title: "Island Count",
    difficulty: "Medium",
    description: "Посчитай количество островов из единиц в сетке. Соседи соединяются по 4 направлениям.",
    tags: ["DFS", "Grid"],
    checks: ["dfs", "grid"],
    starter: `function solve(grid) {
  let count = 0;

  function dfs(r, c) {
    if (!grid[r] || grid[r][c] !== 1) return;
    grid[r][c] = 0;
    dfs(r + 1, c); dfs(r - 1, c); dfs(r, c + 1); dfs(r, c - 1);
  }

  for (let r = 0; r < grid.length; r++) {
    for (let c = 0; c < grid[0].length; c++) {
      if (grid[r][c] === 1) { count++; dfs(r, c); }
    }
  }

  return count;
}`,
    opponent: `function solve(grid) {
  let islands = 0;
  const dfs = (r, c) => {
    if (!grid[r] || grid[r][c] !== 1) return;
    grid[r][c] = 0;
    dfs(r+1,c); dfs(r-1,c); dfs(r,c+1); dfs(r,c-1);
  };
  for (let r = 0; r < grid.length; r++)
    for (let c = 0; c < grid[0].length; c++)
      if (grid[r][c] === 1) { islands++; dfs(r,c); }
  return islands;
}`,
    cases: [
      { input: "[[1,1,0],[0,1,0],[1,0,1]]", expected: "3" },
      { input: "[[1,1],[1,1]]", expected: "1" },
      { input: "[[0,0]]", expected: "0" },
    ],
  },
  {
    title: "Daily Temperatures",
    difficulty: "Medium",
    description: "Для каждого дня верни, сколько дней ждать до более теплой температуры.",
    tags: ["Stack"],
    checks: ["stack", "answer"],
    starter: `function solve(t) {
  const answer = Array(t.length).fill(0);
  const stack = [];

  for (let i = 0; i < t.length; i++) {
    while (stack.length && t[i] > t[stack[stack.length - 1]]) {
      const j = stack.pop();
      answer[j] = i - j;
    }
    stack.push(i);
  }

  return answer;
}`,
    opponent: `function solve(t) {
  const ans = Array(t.length).fill(0);
  const stack = [];
  for (let i = 0; i < t.length; i++) {
    while (stack.length && t[i] > t[stack.at(-1)]) {
      const j = stack.pop();
      ans[j] = i - j;
    }
    stack.push(i);
  }
  return ans;
}`,
    cases: [
      { input: "[73,74,75,71,69,72,76,73]", expected: "[1,1,4,2,1,1,0,0]" },
      { input: "[30,40,50,60]", expected: "[1,1,1,0]" },
      { input: "[30,60,90]", expected: "[1,1,0]" },
    ],
  },
  {
    title: "Subarray Target",
    difficulty: "Medium",
    description: "Верни true, если существует непрерывный подмассив с суммой target.",
    tags: ["Prefix Sum", "Set"],
    checks: ["prefix", "Set"],
    starter: `function solve(nums, target) {
  let prefix = 0;
  const seen = new Set([0]);

  for (const n of nums) {
    prefix += n;
    if (seen.has(prefix - target)) return true;
    seen.add(prefix);
  }

  return false;
}`,
    opponent: `function solve(nums, target) {
  let prefix = 0;
  const seen = new Set([0]);
  for (const n of nums) {
    prefix += n;
    if (seen.has(prefix - target)) return true;
    seen.add(prefix);
  }
  return false;
}`,
    cases: [
      { input: "[1,2,3], 5", expected: "true" },
      { input: "[1,2,3], 7", expected: "false" },
      { input: "[3,-1,2], 1", expected: "true" },
    ],
  },
  {
    title: "Longest Unique",
    difficulty: "Medium",
    description: "Верни длину самой длинной подстроки без повторяющихся символов.",
    tags: ["Sliding Window", "Set"],
    checks: ["left", "seen"],
    starter: `function solve(s) {
  const seen = new Set();
  let left = 0;
  let best = 0;

  for (let right = 0; right < s.length; right++) {
    while (seen.has(s[right])) seen.delete(s[left++]);
    seen.add(s[right]);
    best = Math.max(best, right - left + 1);
  }

  return best;
}`,
    opponent: `function solve(s) {
  const seen = new Set();
  let left = 0, best = 0;
  for (let right = 0; right < s.length; right++) {
    while (seen.has(s[right])) seen.delete(s[left++]);
    seen.add(s[right]);
    best = Math.max(best, right - left + 1);
  }
  return best;
}`,
    cases: [
      { input: '"abcabcbb"', expected: "3" },
      { input: '"bbbbb"', expected: "1" },
      { input: '"pwwkew"', expected: "3" },
    ],
  },
  {
    title: "Grid Escape",
    difficulty: "Hard",
    description: "Найди кратчайший путь из левого верхнего угла в правый нижний. 1 - стена, 0 - свободная клетка.",
    tags: ["BFS", "Grid"],
    checks: ["queue", "seen"],
    starter: `function solve(grid) {
  const rows = grid.length;
  const cols = grid[0].length;
  const queue = [[0, 0, 1]];
  const seen = new Set(["0,0"]);

  for (let head = 0; head < queue.length; head++) {
    const [r, c, dist] = queue[head];
    if (r === rows - 1 && c === cols - 1) return dist;

    for (const [dr, dc] of [[1,0],[-1,0],[0,1],[0,-1]]) {
      const nr = r + dr;
      const nc = c + dc;
      const key = nr + "," + nc;
      if (nr >= 0 && nc >= 0 && nr < rows && nc < cols && grid[nr][nc] === 0 && !seen.has(key)) {
        seen.add(key);
        queue.push([nr, nc, dist + 1]);
      }
    }
  }

  return -1;
}`,
    opponent: `function solve(grid) {
  const q = [[0, 0, 1]];
  const seen = new Set(["0,0"]);
  for (let i = 0; i < q.length; i++) {
    const [r, c, d] = q[i];
    if (r === grid.length - 1 && c === grid[0].length - 1) return d;
  }
  return -1;
}`,
    cases: [
      { input: "[[0,0,0],[1,1,0],[0,0,0]]", expected: "5" },
      { input: "[[0,1],[0,0]]", expected: "3" },
      { input: "[[0,1],[1,0]]", expected: "-1" },
    ],
  },
  {
    title: "Coin Race",
    difficulty: "Hard",
    description: "Дано число amount и монеты. Верни минимальное количество монет для суммы или -1.",
    tags: ["DP"],
    checks: ["dp", "amount"],
    starter: `function solve(coins, amount) {
  const dp = Array(amount + 1).fill(Infinity);
  dp[0] = 0;

  for (const coin of coins) {
    for (let sum = coin; sum <= amount; sum++) {
      dp[sum] = Math.min(dp[sum], dp[sum - coin] + 1);
    }
  }

  return dp[amount] === Infinity ? -1 : dp[amount];
}`,
    opponent: `function solve(coins, amount) {
  const dp = Array(amount + 1).fill(Infinity);
  dp[0] = 0;
  for (const coin of coins)
    for (let s = coin; s <= amount; s++)
      dp[s] = Math.min(dp[s], dp[s - coin] + 1);
  return dp[amount] === Infinity ? -1 : dp[amount];
}`,
    cases: [
      { input: "[1,2,5], 11", expected: "3" },
      { input: "[2], 3", expected: "-1" },
      { input: "[1], 0", expected: "0" },
    ],
  },
  {
    title: "Course Unlock",
    difficulty: "Hard",
    description: "Верни true, если можно пройти все курсы с учетом зависимостей.",
    tags: ["Graph", "Topological Sort"],
    checks: ["indegree", "queue"],
    starter: `function solve(n, prerequisites) {
  const graph = Array.from({ length: n }, () => []);
  const indegree = Array(n).fill(0);

  for (const [a, b] of prerequisites) {
    graph[b].push(a);
    indegree[a]++;
  }

  const queue = indegree.map((d, i) => d === 0 ? i : -1).filter((i) => i >= 0);
  let done = 0;

  for (let i = 0; i < queue.length; i++) {
    done++;
    for (const next of graph[queue[i]]) {
      if (--indegree[next] === 0) queue.push(next);
    }
  }

  return done === n;
}`,
    opponent: `function solve(n, prerequisites) {
  const graph = Array.from({ length: n }, () => []);
  const indegree = Array(n).fill(0);
  for (const [a, b] of prerequisites) { graph[b].push(a); indegree[a]++; }
  const queue = [];
  indegree.forEach((d, i) => d === 0 && queue.push(i));
  let done = 0;
  for (let i = 0; i < queue.length; i++) {
    done++;
    for (const next of graph[queue[i]]) if (--indegree[next] === 0) queue.push(next);
  }
  return done === n;
}`,
    cases: [
      { input: "2, [[1,0]]", expected: "true" },
      { input: "2, [[1,0],[0,1]]", expected: "false" },
      { input: "3, [[1,0],[2,1]]", expected: "true" },
    ],
  },
  {
    title: "Word Portal",
    difficulty: "Hard",
    description: "Найди минимальное число преобразований от begin до end, меняя одну букву за шаг и используя только слова из списка.",
    tags: ["BFS", "String"],
    checks: ["queue", "words"],
    starter: `function solve(begin, end, list) {
  const words = new Set(list);
  const queue = [[begin, 1]];

  for (let head = 0; head < queue.length; head++) {
    const [word, dist] = queue[head];
    if (word === end) return dist;

    for (let i = 0; i < word.length; i++) {
      for (const ch of "abcdefghijklmnopqrstuvwxyz") {
        const next = word.slice(0, i) + ch + word.slice(i + 1);
        if (words.has(next)) {
          words.delete(next);
          queue.push([next, dist + 1]);
        }
      }
    }
  }

  return 0;
}`,
    opponent: `function solve(begin, end, list) {
  const words = new Set(list);
  const queue = [[begin, 1]];
  for (let h = 0; h < queue.length; h++) {
    const [word, dist] = queue[h];
    if (word === end) return dist;
  }
  return 0;
}`,
    cases: [
      { input: '"hit", "cog", ["hot","dot","dog","lot","log","cog"]', expected: "5" },
      { input: '"hit", "cog", ["hot","dot","dog"]', expected: "0" },
      { input: '"a", "c", ["a","b","c"]', expected: "2" },
    ],
  },
];

const extraCasesByTitle = {
  "Pair Sprint": [
    { input: "[1,5,9,13], 14", expected: "[0,3]" },
    { input: "[-3,4,8,11], 8", expected: "[0,3]" },
  ],
  "Bracket Dash": [
    { input: '"([{}])"', expected: "true" },
    { input: '"((())"', expected: "false" },
  ],
  "Max Streak": [
    { input: "[1,1,1,1]", expected: "4" },
    { input: "[0,1,1,1,0,1,1]", expected: "3" },
  ],
  "Clean Duplicates": [
    { input: "[9,8,9,7,8]", expected: "[9,8,7]" },
    { input: "[1,2,3]", expected: "[1,2,3]" },
  ],
  "First Unique": [
    { input: '"swiss"', expected: '"w"' },
    { input: '"racecar"', expected: '"e"' },
  ],
  "Merge Sorted": [
    { input: "[1,2,7], [3,5]", expected: "[1,2,3,5,7]" },
    { input: "[-2,0], [-3,4]", expected: "[-3,-2,0,4]" },
  ],
  "Mirror Word": [
    { input: '"level"', expected: "true" },
    { input: '"hello world"', expected: "false" },
  ],
  "Missing Level": [
    { input: "[0]", expected: "1" },
    { input: "[1,2,3]", expected: "0" },
  ],
  "Most Frequent": [
    { input: "[4,4,2,2,4]", expected: "4" },
    { input: "[10,9,9,8,9]", expected: "9" },
  ],
  "Window Sum": [
    { input: "[2,3,4,1], 2", expected: "7" },
    { input: "[9,1,1,9], 1", expected: "9" },
  ],
  "Island Count": [
    { input: "[[1,0,1],[0,0,0],[1,1,1]]", expected: "3" },
    { input: "[[1,0],[0,1]]", expected: "2" },
  ],
  "Daily Temperatures": [
    { input: "[90,80,70]", expected: "[0,0,0]" },
    { input: "[70,71,70,72]", expected: "[1,2,1,0]" },
  ],
  "Subarray Target": [
    { input: "[5,-2,3], 3", expected: "true" },
    { input: "[2,4,6], 5", expected: "false" },
  ],
  "Longest Unique": [
    { input: '"dvdf"', expected: "3" },
    { input: '""', expected: "0" },
  ],
  "Grid Escape": [
    { input: "[[0,0],[0,0]]", expected: "3" },
    { input: "[[0]]", expected: "1" },
  ],
  "Coin Race": [
    { input: "[1,3,4], 6", expected: "2" },
    { input: "[5,7], 1", expected: "-1" },
  ],
  "Course Unlock": [
    { input: "4, [[1,0],[2,0],[3,1],[3,2]]", expected: "true" },
    { input: "3, [[0,1],[1,2],[2,0]]", expected: "false" },
  ],
  "Word Portal": [
    { input: '"lost", "cost", ["lost","cost"]', expected: "2" },
    { input: '"game", "math", ["gave","gath","math"]', expected: "0" },
  ],
};

taskBank.forEach((task) => {
  task.cases = [...task.cases, ...(extraCasesByTitle[task.title] || [])];
});

const modeMeta = {
  players: { opponent: "Online Rival", boardName: "Online Rival" },
  bot: { opponent: "CODE BOT", boardName: "CODE BOT" },
  past: { opponent: "PAST SELF", boardName: "PAST SELF" },
  room: { opponent: "FRIEND", boardName: "FRIEND ROOM" },
};

const state = {
  matchTasks: [],
  problemIndex: 0,
  mode: "players",
  botLevel: "auto",
  authMode: "signup",
  language: "javascript",
  judgeLanguages: [
    { id: "javascript", label: "JavaScript", status: "executable" },
    { id: "typescript", label: "TypeScript", status: "executable" },
    { id: "python", label: "Python", status: "executable" },
    { id: "cpp", label: "C++", status: "planned" },
    { id: "java", label: "Java", status: "planned" },
    { id: "go", label: "Go", status: "planned" },
    { id: "rust", label: "Rust", status: "planned" },
  ],
  currentUser: {
    id: null,
    name: "Player",
    rating: 1200,
    isAdmin: false,
  },
  currentMatchId: null,
  currentRoomId: null,
  roomWaitReject: null,
  roomInvitePollId: null,
  tournamentPollId: null,
  tournamentSocket: null,
  tournamentSocketTournamentId: null,
  tournamentTargetSize: 4,
  currentMatchStartedAt: null,
  matchPollId: null,
  matchSocket: null,
  currentOpponent: null,
  matchRunning: false,
  matchDuration: 1800,
  secondsLeft: 1800,
  playerProgress: 0,
  opponentProgress: 0,
  debugStep: 0,
  timerId: null,
  opponentId: null,
  adminProblems: [],
  adminSignals: [],
  adminCalibration: [],
  adminEditingProblemId: null,
  historyMatches: [],
  tournaments: [],
  selectedTournamentId: null,
  courses: [],
  courseRecommendations: [],
  courseFilter: "all",
  selectedCourse: null,
  selectedReplayId: null,
};

const els = {
  arenaView: document.querySelector("#arenaView"),
  views: {
    home: document.querySelector("#homeView"),
    arena: document.querySelector("#arenaView"),
    learn: document.querySelector("#learnView"),
    contests: document.querySelector("#contestsView"),
    history: document.querySelector("#historyView"),
    admin: document.querySelector("#adminView"),
  },
  title: document.querySelector("#problemTitle"),
  difficulty: document.querySelector("#difficulty"),
  description: document.querySelector("#problemDescription"),
  tags: document.querySelector("#problemTags"),
  cases: document.querySelector("#cases"),
  editor: document.querySelector("#codeEditor"),
  highlight: document.querySelector("#codeHighlight"),
  language: document.querySelector("#languageSelect"),
  botLevel: document.querySelector("#botLevelSelect"),
  roomPanel: document.querySelector("#roomPanel"),
  roomStatus: document.querySelector("#roomStatus"),
  roomOpponentInput: document.querySelector("#roomOpponentInput"),
  createRoom: document.querySelector("#createRoom"),
  copyRoomLink: document.querySelector("#copyRoomLink"),
  cancelRoom: document.querySelector("#cancelRoom"),
  refreshRoomInvites: document.querySelector("#refreshRoomInvites"),
  roomInviteList: document.querySelector("#roomInviteList"),
  run: document.querySelector("#runCode"),
  submit: document.querySelector("#submitCode"),
  format: document.querySelector("#formatCode"),
  solutionOpen: document.querySelector("#solutionOpen"),
  start: document.querySelector("#startMatch"),
  timer: document.querySelector("#timer"),
  problemTimerMirror: document.querySelector("#problemTimerMirror"),
  status: document.querySelector("#matchStatus"),
  playerRace: document.querySelector("#playerRace"),
  opponentRace: document.querySelector("#opponentRace"),
  playerClash: document.querySelector("#playerClash"),
  opponentClash: document.querySelector("#opponentClash"),
  playerPace: document.querySelector("#playerPace"),
  opponentPace: document.querySelector("#opponentPace"),
  opponentName: document.querySelector("#opponentName"),
  opponentBoardName: document.querySelector("#opponentBoardName"),
  playerBoardProgress: document.querySelector("#playerBoardProgress"),
  opponentBoardProgress: document.querySelector("#opponentBoardProgress"),
  arenaCircleTask: document.querySelector("#arenaCircleTask"),
  arenaCircleTitle: document.querySelector("#arenaCircleTitle"),
  taskLadder: document.querySelector("#taskLadder"),
  summary: document.querySelector("#testSummary"),
  terminal: document.querySelector("#terminalOutput"),
  consoleTabs: document.querySelectorAll(".console-tab"),
  debugStatus: document.querySelector("#debugStatus"),
  debugOutput: document.querySelector("#debugOutput"),
  step: document.querySelector("#stepDebug"),
  resetDebug: document.querySelector("#resetDebug"),
  quickPlay: document.querySelector("#quickPlay"),
  ratingPill: document.querySelector("#ratingPill"),
  themeToggle: document.querySelector("#themeToggle"),
  signupOpen: document.querySelector("#signupOpen"),
  loginOpen: document.querySelector("#loginOpen"),
  authModal: document.querySelector("#authModal"),
  authClose: document.querySelector("#authClose"),
  authTitle: document.querySelector("#authTitle"),
  authForm: document.querySelector("#authForm"),
  authName: document.querySelector("#authName"),
  authEmail: document.querySelector("#authEmail"),
  authPassword: document.querySelector("#authPassword"),
  authSubmit: document.querySelector("#authSubmit"),
  authMessage: document.querySelector("#authMessage"),
  googleAuth: document.querySelector("#googleAuth"),
  githubAuth: document.querySelector("#githubAuth"),
  nameField: document.querySelector("#nameField"),
  historyNav: document.querySelector("#historyNav"),
  historyRefresh: document.querySelector("#historyRefresh"),
  historyStatus: document.querySelector("#historyStatus"),
  historyMatchList: document.querySelector("#historyMatchList"),
  courseGrid: document.querySelector("#courseGrid"),
  courseRecommendations: document.querySelector("#courseRecommendations"),
  courseFilters: document.querySelectorAll("[data-course-filter]"),
  learnStatus: document.querySelector("#learnStatus"),
  courseDetailPanel: document.querySelector("#courseDetailPanel"),
  courseDetailTitle: document.querySelector("#courseDetailTitle"),
  courseDetailStatus: document.querySelector("#courseDetailStatus"),
  courseDetailSummary: document.querySelector("#courseDetailSummary"),
  courseLessonList: document.querySelector("#courseLessonList"),
  coursePracticeList: document.querySelector("#coursePracticeList"),
  replayStatus: document.querySelector("#replayStatus"),
  replaySummary: document.querySelector("#replaySummary"),
  replayTasks: document.querySelector("#replayTasks"),
  replayEvents: document.querySelector("#replayEvents"),
  tournamentRefresh: document.querySelector("#tournamentRefresh"),
  tournamentCreate: document.querySelector("#tournamentCreate"),
  tournamentSizeButtons: document.querySelectorAll("[data-tournament-size]"),
  tournamentName: document.querySelector("#tournamentName"),
  tournamentPlayers: document.querySelector("#tournamentPlayers"),
  tournamentPlayerHint: document.querySelector("#tournamentPlayerHint"),
  tournamentLiveStatus: document.querySelector("#tournamentLiveStatus"),
  tournamentStatus: document.querySelector("#tournamentStatus"),
  tournamentCount: document.querySelector("#tournamentCount"),
  tournamentList: document.querySelector("#tournamentList"),
  tournamentBracketPanel: document.querySelector("#tournamentBracketPanel"),
  tournamentBracketTitle: document.querySelector("#tournamentBracketTitle"),
  tournamentBracketStatus: document.querySelector("#tournamentBracketStatus"),
  tournamentChampion: document.querySelector("#tournamentChampion"),
  tournamentSeeds: document.querySelector("#tournamentSeeds"),
  tournamentRounds: document.querySelector("#tournamentRounds"),
  adminNav: document.querySelector("#adminNav"),
  adminNew: document.querySelector("#adminNew"),
  adminRefresh: document.querySelector("#adminRefresh"),
  adminSignalsRefresh: document.querySelector("#adminSignalsRefresh"),
  adminCalibrationRefresh: document.querySelector("#adminCalibrationRefresh"),
  adminSignalsStatus: document.querySelector("#adminSignalsStatus"),
  adminSignalList: document.querySelector("#adminSignalList"),
  adminCalibrationStatus: document.querySelector("#adminCalibrationStatus"),
  adminCalibrationList: document.querySelector("#adminCalibrationList"),
  adminStatus: document.querySelector("#adminStatus"),
  adminProblemList: document.querySelector("#adminProblemList"),
  adminProblemForm: document.querySelector("#adminProblemForm"),
  adminTitle: document.querySelector("#adminTitle"),
  adminSlug: document.querySelector("#adminSlug"),
  adminDifficulty: document.querySelector("#adminDifficulty"),
  adminConcept: document.querySelector("#adminConcept"),
  adminTags: document.querySelector("#adminTags"),
  adminSpeed: document.querySelector("#adminSpeed"),
  adminStatement: document.querySelector("#adminStatement"),
  adminStarter: document.querySelector("#adminStarter"),
  adminSolutionNotes: document.querySelector("#adminSolutionNotes"),
  adminTests: document.querySelector("#adminTests"),
  adminReviewStatus: document.querySelector("#adminReviewStatus"),
  adminReviewNotes: document.querySelector("#adminReviewNotes"),
  adminReviewList: document.querySelector("#adminReviewList"),
  adminMessage: document.querySelector("#adminMessage"),
  adminSubmit: document.querySelector("#adminSubmit"),
};

function shuffle(items) {
  const copy = [...items];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

function pickByDifficulty(difficulty, count) {
  return shuffle(taskBank.filter((task) => task.difficulty === difficulty)).slice(0, count);
}

function buildRandomMatch() {
  return shuffle([
    ...pickByDifficulty("Easy", 3),
    ...pickByDifficulty("Medium", 2),
    ...pickByDifficulty("Hard", 1),
  ]);
}

function makeOnlineOpponents(baseRating) {
  return [
    { name: "ArrayPilot", rating: baseRating - 82 },
    { name: "StackRunner", rating: baseRating + 46 },
    { name: "BitShift", rating: baseRating + 128 },
    { name: "HeapLine", rating: baseRating - 164 },
    { name: "GraphFlow", rating: baseRating + 238 },
  ].map((opponent) => ({
    ...opponent,
    rating: Math.max(100, opponent.rating),
  }));
}

function pickRatedOpponent(userRating) {
  return makeOnlineOpponents(userRating)
    .sort((a, b) => Math.abs(a.rating - userRating) - Math.abs(b.rating - userRating))[0];
}

function calculateRating(oldRating, opponentRating, score, kFactor = 32) {
  const expected = 1 / (1 + Math.pow(10, (opponentRating - oldRating) / 400));
  return Math.max(100, Math.round(oldRating + kFactor * (score - expected)));
}

function currentProblem() {
  return state.matchTasks[state.problemIndex];
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function getLanguageStarter(problem, language = state.language) {
  if (language === "javascript") return problem.starter;
  if (language === "typescript") return `function solve(input: unknown): unknown {\n  // ${problem.title}\n  return null;\n}`;
  if (language === "python") return `def solve(*args):\n    # ${problem.title}\n    return None\n`;
  if (language === "cpp") return `#include <bits/stdc++.h>\nusing namespace std;\n\nauto solve() {\n    // ${problem.title}\n}\n`;
  if (language === "java") return `class Solution {\n    Object solve() {\n        // ${problem.title}\n        return null;\n    }\n}`;
  if (language === "go") return `package main\n\nfunc solve() any {\n    // ${problem.title}\n    return nil\n}\n`;
  if (language === "rust") return `fn solve() {\n    // ${problem.title}\n}\n`;
  return problem.starter;
}

function isLanguageExecutable(language = state.language) {
  const item = state.judgeLanguages.find((entry) => entry.id === language);
  return !item || item.status === "executable";
}

function renderLanguageOptions() {
  const selected = state.language;
  els.language.innerHTML = state.judgeLanguages
    .map((language) => {
      const disabled = language.status !== "executable" ? " disabled" : "";
      const suffix = language.status !== "executable" ? " (planned)" : "";
      return `<option value="${escapeHtml(language.id)}"${disabled}>${escapeHtml(language.label + suffix)}</option>`;
    })
    .join("");
  els.language.value = isLanguageExecutable(selected) ? selected : "javascript";
  state.language = els.language.value;
}

function highlightLine(rawLine, hasError = false) {
  const commentIndex = rawLine.search(/\/\/|#/);
  const codePart = commentIndex >= 0 ? rawLine.slice(0, commentIndex) : rawLine;
  const commentPart = commentIndex >= 0 ? rawLine.slice(commentIndex) : "";
  const strings = [];

  let protectedCode = codePart.replace(/("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`)/g, (value) => {
    const id = `@@STR${String.fromCharCode(65 + strings.length)}@@`;
    strings.push(`<span class="tok-string">${escapeHtml(value)}</span>`);
    return id;
  });

  let line = escapeHtml(protectedCode);
  line = line.replace(/\b(\d+(?:\.\d+)?)\b/g, '<span class="tok-number">$1</span>');
  line = line.replace(/\b(function|return|const|let|var|if|else|for|while|class|new|def|import|from|in|True|False|None|auto|int|long|double|float|bool|string|void|public|private|static)\b/g, '<span class="tok-keyword">$1</span>');
  line = line.replace(/\b([A-Za-z_$][\w$]*)\s*(?=\()/g, '<span class="tok-function">$1</span>');
  line = line.replace(/\b(<span class="tok-keyword">(?:let|var|const|int|long|double|float|bool|string|auto)<\/span>|String)\s+([A-Za-z_$][\w$]*)/g, '$1 <span class="tok-variable">$2</span>');
  strings.forEach((value, index) => {
    line = line.replace(`@@STR${String.fromCharCode(65 + index)}@@`, value);
  });

  if (commentPart) {
    line += `<span class="tok-comment">${escapeHtml(commentPart)}</span>`;
  }

  return hasError ? `<span class="tok-error">${line}</span>` : line;
}

function updateCodeHighlight() {
  const errorLines = new Set(getCodeErrors(els.editor.value).map((error) => error.number));
  const highlighted = els.editor.value
    .split("\n")
    .map((line, index) => highlightLine(line, errorLines.has(index + 1)))
    .join("\n");
  els.highlight.innerHTML = `${highlighted}\n`;
  els.highlight.scrollTop = els.editor.scrollTop;
  els.highlight.scrollLeft = els.editor.scrollLeft;
}

function getCodeErrors(code) {
  const errors = [];
  const declarations = new Map();
  const pairs = { "(": ")", "[": "]", "{": "}" };
  const stack = [];

  code.split("\n").forEach((line, index) => {
    const number = index + 1;
    const clean = line.replace(/("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`)/g, "");
    const codeOnly = clean.split(/\/\/|#/)[0];

    if (/\b(?:let|var|const)\s+[A-Za-z_$][\w$]*\s*;/.test(codeOnly)) {
      errors.push({ number, message: "variable declared without value" });
    }

    if (/\b(?:int|long|double|float|bool|string|auto|String)\s+[A-Za-z_]\w*\s*;/.test(codeOnly)) {
      errors.push({ number, message: "typed variable declared without value" });
    }

    if (/^\s*[A-Za-z_]\w*\s*=\s*$/.test(codeOnly)) {
      errors.push({ number, message: "assignment has no value" });
    }

    if (/[+\-*/%=<>!&|,]\s*$/.test(codeOnly.trim())) {
      errors.push({ number, message: "line ends with unfinished operator" });
    }

    const declaration = codeOnly.match(/\b(?:let|var|const|def|function|int|long|double|float|bool|string|auto|String)\s+([A-Za-z_$][\w$]*)/);
    if (declaration) {
      if (declarations.has(declaration[1])) {
        errors.push({ number, message: `duplicate name "${declaration[1]}"` });
      }
      declarations.set(declaration[1], number);
    }

    for (const char of codeOnly) {
      if (pairs[char]) stack.push({ char, number });
      if (Object.values(pairs).includes(char)) {
        const last = stack.pop();
        if (!last || pairs[last.char] !== char) {
          errors.push({ number, message: `unexpected "${char}"` });
        }
      }
    }
  });

  stack.forEach((item) => {
    errors.push({ number: item.number, message: `unclosed "${item.char}"` });
  });

  return errors;
}

function insertEditorTab(event) {
  if (event.key !== "Tab") return;
  event.preventDefault();
  const start = els.editor.selectionStart;
  const end = els.editor.selectionEnd;
  const value = els.editor.value;
  const indent = "  ";
  els.editor.value = `${value.slice(0, start)}${indent}${value.slice(end)}`;
  els.editor.selectionStart = start + indent.length;
  els.editor.selectionEnd = start + indent.length;
  updateCodeHighlight();
}

function changeLanguage(language) {
  if (!isLanguageExecutable(language)) {
    els.status.textContent = `${language} planned`;
    return;
  }
  state.language = language;
  els.editor.value = getLanguageStarter(currentProblem(), language);
  els.status.textContent = `${els.language.options[els.language.selectedIndex].text} selected`;
  updateCodeHighlight();
}

async function loadJudgeLanguages() {
  try {
    const languages = await apiRequest("/api/judge/languages");
    if (Array.isArray(languages) && languages.length) {
      state.judgeLanguages = languages;
    }
  } catch (error) {
    console.warn("Judge language matrix unavailable.", error);
  }
  renderLanguageOptions();
}

function titleCaseDifficulty(difficulty) {
  return difficulty.charAt(0).toUpperCase() + difficulty.slice(1);
}

function formatSeedValue(value) {
  return JSON.stringify(value);
}

function normalizeSeedProblem(problem) {
  return {
    slug: problem.slug,
    title: problem.title,
    difficulty: titleCaseDifficulty(problem.difficulty),
    description: problem.statement,
    tags: problem.tags.map((tag) => tag.replaceAll("-", " ")),
    checks: ["return"],
    starter: problem.starter_code_js,
    opponent: "",
    cases: problem.cases.map((item) => ({
      input: item.input.map(formatSeedValue).join(", "),
      expected: formatSeedValue(item.expected),
    })),
  };
}

function normalizeBackendTask(task) {
  return {
    id: task.problem_id,
    matchTaskId: task.match_task_id,
    title: task.title,
    difficulty: titleCaseDifficulty(task.difficulty),
    description: task.statement || task.description,
    tags: task.tags.map((tag) => tag.replaceAll("-", " ")),
    checks: ["return"],
    starter: task.starter_code_js,
    opponent: "",
    cases: task.sample_tests.map((item) => ({
      input: Array.isArray(item.input) ? item.input.map(formatJudgeValue).join(", ") : formatJudgeValue(item.input),
      expected: formatJudgeValue(item.expected),
    })),
  };
}

async function loadSeedProblems() {
  try {
    const response = await fetch("db/seed_problems.json", { cache: "no-store" });
    if (!response.ok) throw new Error("seed not available");
    const seedProblems = await response.json();
    taskBank.splice(0, taskBank.length, ...seedProblems.map(normalizeSeedProblem));
  } catch (error) {
    console.warn("Using built-in fallback tasks.", error);
  }
}

function showView(view) {
  Object.entries(els.views).forEach(([name, element]) => {
    element.classList.toggle("active", name === view);
  });
  document.querySelectorAll(".nav-item").forEach((button) => {
    button.classList.toggle("active", button.dataset.view === view);
  });
  if (view === "history") loadMatchHistory();
  if (view === "learn") loadCourses();
  if (view === "contests") {
    loadTournaments();
    startTournamentPolling();
  } else {
    stopTournamentPolling();
  }
  if (view === "admin") loadAdminProblems();
}

function openAuth(mode = "signup") {
  state.authMode = mode;
  const isSignup = mode === "signup";
  els.authTitle.textContent = isSignup ? "Create Account" : "Login";
  els.authSubmit.textContent = isSignup ? "Create Account" : "Login";
  els.nameField.style.display = isSignup ? "grid" : "none";
  els.authPassword.autocomplete = isSignup ? "new-password" : "current-password";
  els.authMessage.textContent = "";
  els.authForm.reset();
  els.authModal.classList.add("open");
  els.authModal.setAttribute("aria-hidden", "false");
  setTimeout(() => (isSignup ? els.authName : els.authEmail).focus(), 50);
}

function closeAuth() {
  els.authModal.classList.remove("open");
  els.authModal.setAttribute("aria-hidden", "true");
}

function authHeaders() {
  const token = localStorage.getItem(AUTH_TOKEN_KEY);
  return token ? { Authorization: `Bearer ${token}` } : {};
}

class ApiError extends Error {
  constructor(message, options = {}) {
    super(message);
    this.name = "ApiError";
    this.status = options.status || 0;
    this.detail = options.detail || message;
    this.retryAfter = options.retryAfter || null;
    this.kind = options.kind || "server";
  }
}

function classifyApiError(status, detail) {
  const text = String(detail || "").toLowerCase();
  if (status === 0) return "offline";
  if (status === 401) return "auth";
  if (status === 429) return "rate-limit";
  if (text.includes("time is up") || text.includes("expired") || text.includes("already finished")) return "expired-match";
  if (status >= 500) return "server";
  return "request";
}

function describeApiError(error, context = "request") {
  if (!(error instanceof ApiError)) {
    return {
      status: "backend error",
      summary: "error",
      terminal: [`> ${context}`, error.message || "Unexpected frontend error."],
    };
  }

  if (error.kind === "offline") {
    return {
      status: "backend offline",
      summary: "offline",
      terminal: [
        `> ${context}`,
        "Backend is not reachable.",
        `Expected API: ${API_BASE}`,
        "Start the backend server and try again.",
      ],
    };
  }

  if (error.kind === "rate-limit") {
    const retry = error.retryAfter ? ` Try again in ${error.retryAfter}s.` : "";
    return {
      status: "rate limit",
      summary: "429",
      terminal: [`> ${context}`, `Too many requests.${retry}`, error.detail],
    };
  }

  if (error.kind === "expired-match") {
    return {
      status: "match expired",
      summary: "expired",
      terminal: [
        `> ${context}`,
        "This match is already over.",
        "Open Arena and start a fresh ranked queue.",
        error.detail,
      ],
    };
  }

  if (error.kind === "auth") {
    return {
      status: "login required",
      summary: "auth",
      terminal: [`> ${context}`, "Login is required for this action.", error.detail],
    };
  }

  return {
    status: error.status >= 500 ? "server error" : "request failed",
    summary: String(error.status || "error"),
    terminal: [`> ${context}`, error.detail || error.message || "Server request failed."],
  };
}

function showApiError(error, context = "request") {
  const view = describeApiError(error, context);
  els.summary.textContent = view.summary;
  els.terminal.textContent = view.terminal.join("\n");
  els.status.textContent = view.status;
  els.arenaView.classList.add("api-error-state");
  setConsoleTab("terminal");
}

function clearApiError() {
  els.arenaView.classList.remove("api-error-state");
}

async function apiRequest(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...authHeaders(),
        ...(options.headers || {}),
      },
    });
  } catch (error) {
    throw new ApiError("Backend is not reachable.", {
      status: 0,
      detail: error.message || "Network request failed.",
      kind: "offline",
    });
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = data.detail || response.statusText || "Server request failed";
    throw new ApiError(detail, {
      status: response.status,
      detail,
      retryAfter: response.headers.get("Retry-After"),
      kind: classifyApiError(response.status, detail),
    });
  }
  return data;
}

function mapProfile(profile) {
  return {
    id: profile.id,
    name: profile.username || "Player",
    rating: profile.stats?.rating || 1200,
    xp: profile.stats?.xp || 0,
    gamesPlayed: profile.stats?.games_played || 0,
    isAdmin: Boolean(profile.is_admin),
  };
}

async function fetchCurrentProfile() {
  const profile = await apiRequest("/api/profile/me");
  return mapProfile(profile);
}

async function loadUser() {
  const token = localStorage.getItem(AUTH_TOKEN_KEY);
  const saved = localStorage.getItem(AUTH_USER_KEY);
  if (!token && !saved) {
    renderAuthState(false);
    return;
  }

  if (saved) {
    const user = JSON.parse(saved);
    state.currentUser = {
      id: user.id || null,
      name: user.name || "Player",
      rating: user.rating || 1200,
      isAdmin: Boolean(user.isAdmin),
    };
    renderAuthState(Boolean(token));
  }

  if (!token) return;

  try {
    saveUser(await fetchCurrentProfile());
  } catch (error) {
    if (error instanceof ApiError && error.kind === "offline") {
      renderAuthState(true);
      return;
    }
    console.warn("Saved session is not valid anymore.", error);
    logoutUser();
  }
}

function saveUser(user) {
  const savedUser = {
    ...user,
    rating: user.rating || state.currentUser.rating || 1200,
  };
  state.currentUser = {
    id: savedUser.id || null,
    name: savedUser.name,
    rating: savedUser.rating,
    isAdmin: Boolean(savedUser.isAdmin),
  };
  localStorage.setItem(AUTH_USER_KEY, JSON.stringify(savedUser));
  renderAuthState(true);
  startRoomInvitePolling();
}

function renderRating(isVisible = Boolean(localStorage.getItem(AUTH_TOKEN_KEY))) {
  els.ratingPill.classList.toggle("hidden", !isVisible);
  els.ratingPill.textContent = `R ${state.currentUser.rating}`;
}

function renderAuthState(isLoggedIn = Boolean(localStorage.getItem(AUTH_TOKEN_KEY))) {
  renderRating(isLoggedIn);
  els.loginOpen.textContent = isLoggedIn ? "Logout" : "Login";
  els.signupOpen.textContent = isLoggedIn ? state.currentUser.name : "Sign Up";
  els.signupOpen.classList.toggle("is-profile", isLoggedIn);
  els.signupOpen.setAttribute("aria-label", isLoggedIn ? `Signed in as ${state.currentUser.name}` : "Sign up");
  els.historyNav.classList.toggle("hidden", !isLoggedIn);
  els.adminNav.classList.toggle("hidden", !(isLoggedIn && state.currentUser.isAdmin));
  if (!isLoggedIn && els.views.history.classList.contains("active")) {
    showView("home");
  }
  if (!(isLoggedIn && state.currentUser.isAdmin) && els.views.admin.classList.contains("active")) {
    showView("home");
  }
}

function logoutUser() {
  stopRoomInvitePolling();
  stopTournamentPolling();
  localStorage.removeItem(AUTH_TOKEN_KEY);
  localStorage.removeItem(AUTH_USER_KEY);
  state.currentUser = {
    id: null,
    name: "Player",
    rating: 1200,
    isAdmin: false,
  };
  state.historyMatches = [];
  state.selectedReplayId = null;
  state.tournaments = [];
  state.selectedTournamentId = null;
  renderTournamentEmpty("Login to create and view tournament rooms.");
  renderTournamentBracket(null);
  renderAuthState(false);
}

function applyTheme(theme) {
  const isLight = theme === "light";
  document.body.classList.toggle("light-theme", isLight);
  els.themeToggle.textContent = isLight ? "Dark" : "Light";
  els.themeToggle.setAttribute("aria-pressed", String(isLight));
  localStorage.setItem("codeBlitzTheme", theme);
}

function loadTheme() {
  applyTheme(localStorage.getItem("codeBlitzTheme") || "dark");
}

function toggleTheme() {
  applyTheme(document.body.classList.contains("light-theme") ? "dark" : "light");
}

async function handleAuth(event) {
  event.preventDefault();
  const email = els.authEmail.value.trim();
  const password = els.authPassword.value.trim();
  const name = els.authName.value.trim() || email.split("@")[0] || "Player";

  if (!email.includes("@")) {
    els.authMessage.textContent = "Enter a valid email.";
    return;
  }

  if (password.length < 8) {
    els.authMessage.textContent = "Password must be at least 8 characters.";
    return;
  }

  els.authSubmit.disabled = true;
  els.authMessage.textContent = state.authMode === "signup" ? "Creating account..." : "Logging in...";

  try {
    const endpoint = state.authMode === "signup" ? "/api/auth/register" : "/api/auth/login";
    const body = state.authMode === "signup" ? { username: name, email, password } : { email, password };
    const token = await apiRequest(endpoint, {
      method: "POST",
      body: JSON.stringify(body),
    });
    localStorage.setItem(AUTH_TOKEN_KEY, token.access_token);
    saveUser(await fetchCurrentProfile());
    els.authMessage.textContent = state.authMode === "signup" ? "Account created." : "Logged in.";
    setTimeout(closeAuth, 450);
  } catch (error) {
    const details = describeApiError(error, state.authMode === "signup" ? "create account" : "login");
    els.authMessage.textContent = details.status === "backend offline"
      ? "Backend is offline. Start the API server and try again."
      : (error.message || "Auth failed.");
  } finally {
    els.authSubmit.disabled = false;
  }
}

function handleProviderAuth(provider) {
  const name = provider === "google" ? "Google" : "GitHub";
  els.authMessage.textContent = `${name} login is not connected to backend yet.`;
}

function formatReplayDate(value) {
  if (!value) return "not finished";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "unknown";
  return date.toLocaleString([], {
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatReplayTime(value, fallback = "--:--") {
  if (!value) return fallback;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return fallback;
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

function formatRatingDelta(match) {
  if (match.rating_before == null || match.rating_after == null) return "R --";
  const delta = match.rating_after - match.rating_before;
  const sign = delta > 0 ? "+" : "";
  return `R ${match.rating_after} (${sign}${delta})`;
}

function getParticipantLabel(replay, userId) {
  const participant = replay.match.participants.find((item) => item.user_id === userId);
  return participant?.display_name || (userId ? "Player" : "System");
}

function describeReplayPayload(payload = {}) {
  const pieces = Object.entries(payload)
    .filter(([, value]) => value !== null && typeof value !== "undefined")
    .slice(0, 3)
    .map(([key, value]) => `${key}: ${typeof value === "object" ? JSON.stringify(value) : value}`);
  return pieces.length ? pieces.join(" · ") : "event recorded";
}

function renderHistoryEmpty(message) {
  els.historyMatchList.innerHTML = `<p class="admin-empty">${escapeHtml(message)}</p>`;
}

function renderMatchHistory(matches) {
  if (!matches.length) {
    renderHistoryEmpty("No matches yet. Play one ranked arena match first.");
    return;
  }

  els.historyMatchList.innerHTML = matches
    .map((match) => {
      const active = match.match_id === state.selectedReplayId ? " active" : "";
      return `
        <button class="history-match-card${active}" data-history-match="${escapeHtml(match.match_id)}" type="button">
          <div>
            <strong>${escapeHtml(match.mode || "ranked blitz")}</strong>
            <small>${escapeHtml(formatReplayDate(match.started_at))} · ${escapeHtml(match.status)}</small>
          </div>
          <span>${escapeHtml(`${match.solved_count || 0}/6`)}</span>
          <em>${escapeHtml(formatRatingDelta(match))}</em>
        </button>
      `;
    })
    .join("");

  document.querySelectorAll("[data-history-match]").forEach((button) => {
    button.addEventListener("click", () => loadMatchReplay(button.dataset.historyMatch));
  });
}

async function loadMatchHistory() {
  if (!localStorage.getItem(AUTH_TOKEN_KEY)) {
    els.historyStatus.textContent = "login required";
    state.historyMatches = [];
    renderHistoryEmpty("Login to see match history and replays.");
    return;
  }

  els.historyStatus.textContent = "loading";
  try {
    const matches = await apiRequest("/api/profile/me/matches?limit=30");
    state.historyMatches = matches;
    els.historyStatus.textContent = `${matches.length} matches`;
    renderMatchHistory(matches);
    if (matches.length && !state.selectedReplayId) {
      await loadMatchReplay(matches[0].match_id);
    }
  } catch (error) {
    const details = describeApiError(error, "load match history");
    els.historyStatus.textContent = details.status;
    renderHistoryEmpty(details.terminal.join(" "));
  }
}

function renderReplay(replay) {
  const match = replay.match;
  const left = match.participants.find((item) => item.side === "left") || match.participants[0];
  const right = match.participants.find((item) => item.side === "right") || match.participants[1];
  const winner = match.winner_user_id ? getParticipantLabel(replay, match.winner_user_id) : "Draw / pending";

  els.replaySummary.innerHTML = `
    <article>
      <span>Status</span>
      <strong>${escapeHtml(match.status)}</strong>
    </article>
    <article>
      <span>Left</span>
      <strong>${escapeHtml(left?.display_name || "Left")}</strong>
      <small>${Math.round(Number(left?.progress_percent || 0))}% · ${left?.solved_count || 0} solved</small>
    </article>
    <article>
      <span>Right</span>
      <strong>${escapeHtml(right?.display_name || "Right")}</strong>
      <small>${Math.round(Number(right?.progress_percent || 0))}% · ${right?.solved_count || 0} solved</small>
    </article>
    <article>
      <span>Winner</span>
      <strong>${escapeHtml(winner)}</strong>
    </article>
  `;

  els.replayTasks.innerHTML = replay.tasks
    .map((task) => `
      <article class="replay-task-card">
        <span>TASK ${String(task.position).padStart(2, "0")} · ${escapeHtml(task.difficulty)}</span>
        <strong>${escapeHtml(task.title)}</strong>
        <div>
          <small>L ${escapeHtml(formatReplayTime(task.accepted_by_left_at))}</small>
          <small>R ${escapeHtml(formatReplayTime(task.accepted_by_right_at))}</small>
        </div>
      </article>
    `)
    .join("");

  const eventRows = [
    ...replay.events.map((event) => ({
      at: event.created_at,
      kind: event.type,
      label: getParticipantLabel(replay, event.user_id),
      detail: describeReplayPayload(event.payload),
    })),
    ...replay.submissions.map((submission) => ({
      at: submission.created_at,
      kind: `submit:${submission.status}`,
      label: getParticipantLabel(replay, submission.user_id),
      detail: `${submission.kind} · ${submission.language} · ${submission.passed_count}/${submission.total_count}`,
    })),
  ].sort((a, b) => new Date(a.at).getTime() - new Date(b.at).getTime());

  els.replayEvents.innerHTML = eventRows.length
    ? eventRows.map((event) => `
        <article class="replay-event-row">
          <time>${escapeHtml(formatReplayTime(event.at))}</time>
          <div>
            <strong>${escapeHtml(event.kind)}</strong>
            <small>${escapeHtml(event.label)} · ${escapeHtml(event.detail)}</small>
          </div>
        </article>
      `).join("")
    : `<p class="admin-empty">No replay events recorded yet.</p>`;
}

async function loadMatchReplay(matchId) {
  if (!matchId) return;
  state.selectedReplayId = matchId;
  renderMatchHistory(state.historyMatches);
  els.replayStatus.textContent = "loading";
  els.replaySummary.innerHTML = "";
  els.replayTasks.innerHTML = "";
  els.replayEvents.innerHTML = "";

  try {
    const replay = await apiRequest(`/api/matches/${encodeURIComponent(matchId)}/replay`);
    els.replayStatus.textContent = `${replay.tasks.length} tasks · ${replay.submissions.length} attempts`;
    renderReplay(replay);
  } catch (error) {
    const details = describeApiError(error, "load match replay");
    els.replayStatus.textContent = details.status;
    els.replayEvents.innerHTML = `<p class="admin-empty">${escapeHtml(details.terminal.join(" "))}</p>`;
  }
}

function renderTournamentEmpty(message = "Login to create and view tournaments.") {
  if (!els.tournamentList) return;
  els.tournamentList.innerHTML = `<p class="admin-empty">${escapeHtml(message)}</p>`;
  if (els.tournamentCount) els.tournamentCount.textContent = "0 loaded";
}

function parseTournamentPlayers(value) {
  return [...new Set(
    String(value || "")
      .split(/[\s,;]+/)
      .map((item) => item.trim())
      .filter(Boolean)
  )];
}

function getTournamentTargetPlayers() {
  return Number(state.tournamentTargetSize || 4);
}

function updateTournamentPlayerHint() {
  if (!els.tournamentPlayerHint) return;
  const target = getTournamentTargetPlayers();
  const entered = parseTournamentPlayers(els.tournamentPlayers?.value || "").length;
  const needed = Math.max(0, target - 1 - entered);
  els.tournamentPlayerHint.textContent = `Target ${target} players. Creator is automatic. Add ${target - 1} other login${target === 2 ? "" : "s"}; ${needed} still needed.`;
  if (els.tournamentPlayers) {
    els.tournamentPlayers.placeholder = Array.from({ length: Math.min(target - 1, 5) }, (_, index) => `friend_${index + 1}`).join("\n")
      + (target > 6 ? "\n..." : "");
  }
  els.tournamentSizeButtons.forEach((button) => {
    button.classList.toggle("active", Number(button.dataset.tournamentSize) === target);
  });
}

function setTournamentTargetSize(size) {
  state.tournamentTargetSize = Number(size) || 4;
  updateTournamentPlayerHint();
}

function formatTournamentDate(value) {
  if (!value) return "not started";
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function renderTournaments(tournaments = state.tournaments) {
  if (!els.tournamentList) return;
  if (els.tournamentCount) els.tournamentCount.textContent = `${tournaments.length} loaded`;
  if (!tournaments.length) {
    renderTournamentEmpty("No tournaments yet. Create one with friend logins.");
    renderTournamentBracket(null);
    return;
  }
  if (!tournaments.some((item) => item.id === state.selectedTournamentId)) {
    state.selectedTournamentId = tournaments[0].id;
  }

  els.tournamentList.innerHTML = tournaments
    .map((tournament) => {
      const active = tournament.id === state.selectedTournamentId ? " active" : "";
      const champion = tournament.champion_user_id
        ? tournament.participants?.find((item) => item.user_id === tournament.champion_user_id)?.username || "champion locked"
        : "in progress";
      return `
        <button class="tournament-card${active}" data-tournament-id="${escapeHtml(tournament.id)}" type="button">
          <span>${escapeHtml(tournament.status)} · ${tournament.player_count}/${tournament.max_players}</span>
          <strong>${escapeHtml(tournament.name)}</strong>
          <small>${escapeHtml(formatTournamentDate(tournament.started_at || tournament.created_at))} · ${escapeHtml(champion)}</small>
        </button>
      `;
    })
    .join("");

  els.tournamentList.querySelectorAll("[data-tournament-id]").forEach((button) => {
    button.addEventListener("click", () => selectTournament(button.dataset.tournamentId));
  });

  const selected = tournaments.find((item) => item.id === state.selectedTournamentId);
  if (selected) {
    renderTournamentBracket(selected);
    connectTournamentStream(selected.id);
  }
}

function selectTournament(tournamentId, rerenderList = true) {
  state.selectedTournamentId = tournamentId;
  const tournament = state.tournaments.find((item) => item.id === tournamentId);
  if (rerenderList) renderTournaments();
  renderTournamentBracket(tournament);
  connectTournamentStream(tournamentId);
}

function renderTournamentBracket(tournament) {
  if (!els.tournamentBracketPanel || !els.tournamentRounds) return;
  if (!tournament) {
    els.tournamentBracketPanel.classList.add("hidden");
    els.tournamentRounds.innerHTML = "";
    if (els.tournamentSeeds) els.tournamentSeeds.innerHTML = "";
    if (els.tournamentChampion) {
      els.tournamentChampion.classList.add("hidden");
      els.tournamentChampion.innerHTML = "";
    }
    return;
  }

  els.tournamentBracketPanel.classList.remove("hidden");
  els.tournamentBracketPanel.classList.toggle("finished", tournament.status === "finished");
  els.tournamentBracketTitle.textContent = tournament.name;
  const championName = tournament.champion_user_id
    ? tournament.participants?.find((item) => item.user_id === tournament.champion_user_id)?.username || "champion"
    : "";
  const champion = championName
    ? `champion // ${championName}`
    : `${tournament.status} // ${tournament.player_count} players`;
  els.tournamentBracketStatus.textContent = champion;
  if (els.tournamentChampion) {
    els.tournamentChampion.classList.toggle("hidden", !championName);
    els.tournamentChampion.innerHTML = championName
      ? `<span>// FINAL LOCKED</span><strong>${escapeHtml(championName)}</strong><small>Champion of ${escapeHtml(tournament.name)}</small>`
      : "";
  }

  els.tournamentSeeds.innerHTML = (tournament.participants || [])
    .map((participant) => `
      <span class="seed-pill ${escapeHtml(participant.status)}">
        #${participant.seed} ${escapeHtml(participant.username)}
      </span>
    `)
    .join("");

  els.tournamentRounds.innerHTML = (tournament.rounds || [])
    .map((round) => `
      <section class="tournament-round">
        <div class="round-head">
          <strong>${escapeHtml(round.name)}</strong>
          <span>${round.match_count} match${round.match_count === 1 ? "" : "es"}</span>
        </div>
        <div class="round-matches">
          ${(round.matches || []).map(renderTournamentMatch).join("")}
        </div>
      </section>
    `)
    .join("");

  els.tournamentRounds.querySelectorAll("[data-tournament-match]").forEach((button) => {
    button.addEventListener("click", () => enterTournamentMatch(button.dataset.tournamentMatch));
  });
}

function renderTournamentMatch(match) {
  const left = match.left_username || "TBD";
  const right = match.right_username || "TBD";
  const winnerSide = match.winner_participant_id
    ? match.winner_participant_id === match.left_participant_id
      ? "left"
      : "right"
    : "";
  const canEnter = match.match_id && match.status === "active";
  return `
    <article class="bracket-match ${escapeHtml(match.status)}">
      <span>Match ${String(match.bracket_position).padStart(2, "0")} · ${escapeHtml(match.status)}</span>
      <div class="bracket-player ${winnerSide === "left" ? "winner" : ""}">
        <b>${escapeHtml(left)}</b>
      </div>
      <div class="bracket-player ${winnerSide === "right" ? "winner" : ""}">
        <b>${escapeHtml(right)}</b>
      </div>
      ${canEnter ? `<button class="primary-button" data-tournament-match="${escapeHtml(match.match_id)}" type="button">Enter Match</button>` : ""}
    </article>
  `;
}

async function loadTournaments(options = {}) {
  const silent = Boolean(options.silent);
  if (!els.tournamentList) return;
  if (!localStorage.getItem(AUTH_TOKEN_KEY)) {
    els.tournamentStatus.textContent = "login required";
    if (els.tournamentLiveStatus) els.tournamentLiveStatus.textContent = "login required";
    renderTournamentEmpty("Login to create and view tournament rooms.");
    return;
  }

  if (!silent) els.tournamentStatus.textContent = "loading";
  try {
    const tournaments = await apiRequest("/api/tournaments");
    const previousSelectedId = state.selectedTournamentId;
    state.tournaments = tournaments;
    if (previousSelectedId && tournaments.some((item) => item.id === previousSelectedId)) {
      state.selectedTournamentId = previousSelectedId;
    }
    els.tournamentStatus.textContent = "ready";
    if (els.tournamentLiveStatus) els.tournamentLiveStatus.textContent = `live refresh // ${new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
    renderTournaments(tournaments);
  } catch (error) {
    if (!silent) {
      els.tournamentStatus.textContent = error.kind === "offline" ? "backend offline" : "load failed";
      renderTournamentEmpty(error.detail || "Could not load tournaments.");
    }
    if (els.tournamentLiveStatus) els.tournamentLiveStatus.textContent = error.kind === "offline" ? "backend offline" : "refresh failed";
  }
}

function startTournamentPolling() {
  stopTournamentPolling();
  if (!localStorage.getItem(AUTH_TOKEN_KEY)) return;
  if (els.tournamentLiveStatus) els.tournamentLiveStatus.textContent = "live refresh on";
  if (state.selectedTournamentId) connectTournamentStream(state.selectedTournamentId);
  state.tournamentPollId = setInterval(() => loadTournaments({ silent: true }), 30000);
}

function stopTournamentPolling() {
  if (state.tournamentPollId) {
    clearInterval(state.tournamentPollId);
    state.tournamentPollId = null;
  }
  closeTournamentStream();
}

function closeTournamentStream() {
  if (state.tournamentSocket) {
    state.tournamentSocket.close();
    state.tournamentSocket = null;
  }
  state.tournamentSocketTournamentId = null;
}

function connectTournamentStream(tournamentId) {
  if (!tournamentId || !localStorage.getItem(AUTH_TOKEN_KEY) || !els.views.contests.classList.contains("active")) return;
  if (state.tournamentSocket && state.tournamentSocketTournamentId === tournamentId) return;
  closeTournamentStream();

  const token = localStorage.getItem(AUTH_TOKEN_KEY);
  const socket = new WebSocket(`${WS_BASE}/api/tournaments/${encodeURIComponent(tournamentId)}/stream?token=${encodeURIComponent(token)}`);
  state.tournamentSocket = socket;
  state.tournamentSocketTournamentId = tournamentId;

  socket.addEventListener("open", () => {
    if (els.tournamentLiveStatus) els.tournamentLiveStatus.textContent = "socket live";
  });

  socket.addEventListener("message", async (event) => {
    try {
      const payload = JSON.parse(event.data);
      if (payload.type === "snapshot") {
        if (els.tournamentLiveStatus) els.tournamentLiveStatus.textContent = `socket // ${payload.status}`;
        return;
      }
      if (payload.type === "tournament_updated") {
        if (els.tournamentLiveStatus) els.tournamentLiveStatus.textContent = `event // ${payload.reason}`;
        await loadTournaments({ silent: true });
      }
    } catch (error) {
      console.warn("Bad tournament event.", error);
    }
  });

  socket.addEventListener("close", () => {
    if (state.tournamentSocket === socket) {
      state.tournamentSocket = null;
      state.tournamentSocketTournamentId = null;
      if (els.tournamentLiveStatus && els.views.contests.classList.contains("active")) {
        els.tournamentLiveStatus.textContent = "socket closed";
      }
    }
  });
}

async function createTournamentFromForm() {
  if (!localStorage.getItem(AUTH_TOKEN_KEY)) {
    els.tournamentStatus.textContent = "login required";
    openAuth("login");
    return;
  }

  const name = els.tournamentName.value.trim();
  const playerUsernames = parseTournamentPlayers(els.tournamentPlayers.value);
  const expectedOthers = getTournamentTargetPlayers() - 1;
  if (!name || playerUsernames.length < 1) {
    els.tournamentStatus.textContent = "add players";
    return;
  }
  if (playerUsernames.length !== expectedOthers) {
    els.tournamentStatus.textContent = `need ${expectedOthers} login${expectedOthers === 1 ? "" : "s"}`;
    updateTournamentPlayerHint();
    return;
  }

  els.tournamentCreate.disabled = true;
  els.tournamentStatus.textContent = "creating bracket";
  try {
    const tournament = await apiRequest("/api/tournaments", {
      method: "POST",
      body: JSON.stringify({ name, player_usernames: playerUsernames }),
    });
    state.tournaments = [tournament, ...state.tournaments.filter((item) => item.id !== tournament.id)];
    state.selectedTournamentId = tournament.id;
    els.tournamentStatus.textContent = "bracket ready";
    renderTournaments();
    renderTournamentBracket(tournament);
  } catch (error) {
    els.tournamentStatus.textContent = error.kind === "offline" ? "backend offline" : "create failed";
    els.tournamentBracketPanel.classList.remove("hidden");
    els.tournamentBracketTitle.textContent = "Tournament Error";
    els.tournamentBracketStatus.textContent = "check players";
    els.tournamentRounds.innerHTML = `<p class="admin-empty">${escapeHtml(error.detail || "Could not create tournament.")}</p>`;
  } finally {
    els.tournamentCreate.disabled = false;
  }
}

async function enterTournamentMatch(matchId) {
  if (!matchId) return;
  clearInterval(state.timerId);
  clearInterval(state.opponentId);
  clearInterval(state.matchPollId);
  setMode("players");
  els.status.textContent = "joining tournament match";
  try {
    await loadBackendMatch(matchId);
    connectMatchStream(matchId);
  } catch (error) {
    els.tournamentStatus.textContent = "match load failed";
    return;
  }

  showView("arena");
  state.matchRunning = true;
  state.problemIndex = 0;
  els.arenaView.classList.add("match-live");
  els.opponentName.textContent = `${state.currentOpponent.name} (${state.currentOpponent.rating})`;
  els.opponentBoardName.textContent = `${state.currentOpponent.name} // ${state.currentOpponent.rating}`;
  els.status.textContent = `tournament match // ${state.currentOpponent.name}`;
  els.start.textContent = "Restart";
  els.start.disabled = false;
  renderProblem();
  renderTimer();
  updateRace();

  state.timerId = setInterval(async () => {
    state.secondsLeft -= 1;
    renderTimer();
    if (state.secondsLeft <= 0 && state.matchRunning) await finishBackendMatch("time expired");
  }, 1000);
}

function formatCoursePrice(course) {
  if (course.access_type === "free" || course.price_cents === 0) return "Free";
  return `${course.currency || "USD"} ${(course.price_cents / 100).toFixed(2)}`;
}

function fallbackCourseRecommendations() {
  return courseCatalogFallback
    .map((course, index) => ({
      ...course,
      score: 10 - index,
      reason: course.access_type === "free"
        ? "Start here while the backend builds your learning profile."
        : "Good next path once fundamentals feel comfortable.",
    }))
    .slice(0, 3);
}

function renderCourseRecommendations() {
  if (!els.courseRecommendations) return;
  const recommendations = state.courseRecommendations.length
    ? state.courseRecommendations
    : fallbackCourseRecommendations();

  els.courseRecommendations.innerHTML = `
    <div class="battle-head">
      <h2>Recommended</h2>
      <span>${localStorage.getItem(AUTH_TOKEN_KEY) ? "personalized" : "starter path"}</span>
    </div>
    <div class="recommendation-row">
      ${recommendations.map((course) => `
        <article class="recommendation-card">
          <div>
            <span>${escapeHtml(course.level)} · ${escapeHtml(formatCoursePrice(course))}</span>
            <strong>${escapeHtml(course.title)}</strong>
            <small>${escapeHtml(course.reason || "Recommended learning path.")}</small>
          </div>
          <button class="primary-button" data-course-open="${escapeHtml(course.slug)}" type="button">Open</button>
        </article>
      `).join("")}
    </div>
  `;

  els.courseRecommendations.querySelectorAll("[data-course-open]").forEach((button) => {
    button.addEventListener("click", () => openCourseDetail(button.dataset.courseOpen));
  });
}

function lessonChecklist(lesson) {
  return (lesson.checklist || []).length
    ? lesson.checklist
    : ["Read the idea", "Try sample tests", "Run before submit"];
}

function renderCourses() {
  if (!els.courseGrid) return;
  const courses = state.courseFilter === "all"
    ? state.courses
    : state.courses.filter((course) => course.access_type === state.courseFilter);

  if (!courses.length) {
    els.courseGrid.innerHTML = `<p class="admin-empty">No courses in this filter yet.</p>`;
    return;
  }

  els.courseGrid.innerHTML = courses
    .map((course) => {
      const premium = course.access_type === "premium";
      const cta = course.enrolled ? "Continue" : premium ? "Premium" : "Start Free";
      return `
        <article class="course-card ${premium ? "premium" : "free"}">
          <div class="course-meta">
            <span>${escapeHtml(course.level)}</span>
            <strong>${escapeHtml(formatCoursePrice(course))}</strong>
          </div>
          <h2>${escapeHtml(course.title)}</h2>
          <p>${escapeHtml(course.summary)}</p>
          <div class="course-tags">
            ${(course.tags || []).map((tag) => `<span>${escapeHtml(tag)}</span>`).join("")}
          </div>
          <div class="course-footer">
            <small>${Number(course.lesson_count || 0)} lessons · ${Number(course.progress_percent || 0)}%</small>
            <div class="course-actions">
              <button class="primary-button" data-course-open="${escapeHtml(course.slug)}" type="button">Open</button>
              <button class="primary-button" data-course-enroll="${escapeHtml(course.slug)}" type="button">${cta}</button>
            </div>
          </div>
        </article>
      `;
    })
    .join("");

  els.courseGrid.querySelectorAll("[data-course-enroll]").forEach((button) => {
    button.addEventListener("click", () => enrollCourse(button.dataset.courseEnroll));
  });
  els.courseGrid.querySelectorAll("[data-course-open]").forEach((button) => {
    button.addEventListener("click", () => openCourseDetail(button.dataset.courseOpen));
  });
}

async function loadCourses() {
  if (!els.courseGrid) return;
  if (els.learnStatus) els.learnStatus.textContent = "loading catalog";
  try {
    const [courses, recommendations] = await Promise.all([
      apiRequest("/api/learning/courses"),
      apiRequest("/api/learning/recommendations").catch(() => []),
    ]);
    state.courses = courses;
    state.courseRecommendations = recommendations;
    if (els.learnStatus) els.learnStatus.textContent = `${state.courses.length} courses`;
  } catch (error) {
    console.warn("Learning API unavailable, using local courses.", error);
    state.courses = courseCatalogFallback;
    state.courseRecommendations = fallbackCourseRecommendations();
    if (els.learnStatus) els.learnStatus.textContent = `${state.courses.length} local courses`;
  }
  renderCourseRecommendations();
  renderCourses();
}

function renderCourseDetail(course) {
  if (!els.courseDetailPanel || !course) return;
  const lessons = course.lessons || [];
  const practiceProblems = course.practice_problems || [];
  els.courseDetailPanel.classList.remove("hidden");
  els.courseDetailTitle.textContent = course.title;
  els.courseDetailSummary.textContent = course.summary;
  els.courseDetailStatus.textContent = `${formatCoursePrice(course)} · ${course.level}`;
  els.courseLessonList.innerHTML = lessons.length
    ? lessons
      .map((lesson) => `
        <article class="course-lesson-card ${lesson.completed ? "complete" : ""}">
          <div>
            <span>${String(lesson.position).padStart(2, "0")} · ${escapeHtml(lesson.kind)}</span>
            <strong>${escapeHtml(lesson.title)}</strong>
            <small>${escapeHtml(lesson.summary || "")}</small>
            <p>${escapeHtml(lesson.content || lesson.summary || "Practice the idea, then jump into linked tasks.")}</p>
            <ul>
              ${lessonChecklist(lesson).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
            </ul>
          </div>
          <button class="primary-button" data-lesson-complete="${escapeHtml(lesson.id)}" type="button">
            ${lesson.completed ? "Done" : "Mark Done"}
          </button>
        </article>
      `)
      .join("")
    : `<p class="admin-empty">Lessons will appear after the backend course seed is loaded.</p>`;

  els.courseLessonList.querySelectorAll("[data-lesson-complete]").forEach((button) => {
    button.addEventListener("click", () => completeCourseLesson(course.slug, button.dataset.lessonComplete));
  });

  if (els.coursePracticeList) {
    els.coursePracticeList.innerHTML = practiceProblems.length
      ? `
        <div class="battle-head">
          <h2>Practice Tasks</h2>
          <span>${practiceProblems.length} linked</span>
        </div>
        ${practiceProblems.map((problem) => `
          <article class="course-practice-card">
            <div>
              <span>TASK ${String(problem.position || 1).padStart(2, "0")} · ${escapeHtml(problem.difficulty)}</span>
              <strong>${escapeHtml(problem.title)}</strong>
              <small>${(problem.tags || []).map(escapeHtml).join(" · ")}</small>
            </div>
            <button class="primary-button" data-practice-problem="${escapeHtml(problem.slug || problem.id)}" type="button">Practice</button>
          </article>
        `).join("")}
      `
      : "";
    els.coursePracticeList.querySelectorAll("[data-practice-problem]").forEach((button) => {
      button.addEventListener("click", () => openPracticeProblem(button.dataset.practiceProblem));
    });
  }
}

async function openCourseDetail(courseSlug) {
  const cached = state.courses.find((item) => item.slug === courseSlug);
  if (!cached) return;
  if (els.learnStatus) els.learnStatus.textContent = "opening course";

  try {
    const course = await apiRequest(`/api/learning/courses/${encodeURIComponent(courseSlug)}`);
    state.selectedCourse = course;
    state.courses = state.courses.map((item) => item.slug === course.slug ? { ...item, ...course } : item);
    renderCourseDetail(course);
    if (els.learnStatus) els.learnStatus.textContent = `${course.lesson_count} lessons`;
  } catch (error) {
    state.selectedCourse = cached;
    renderCourseDetail(cached);
    if (els.learnStatus) els.learnStatus.textContent = "local course preview";
  }
}

async function enrollCourse(courseSlug) {
  const course = state.courses.find((item) => item.slug === courseSlug);
  if (!course) return;

  if (course.access_type === "premium") {
    if (els.learnStatus) els.learnStatus.textContent = "premium checkout planned";
    return;
  }

  if (!localStorage.getItem(AUTH_TOKEN_KEY)) {
    openAuth("login");
    return;
  }

  try {
    const enrollment = await apiRequest(`/api/learning/courses/${encodeURIComponent(courseSlug)}/enroll`, { method: "POST" });
    state.courses = state.courses.map((item) => item.slug === courseSlug
      ? { ...item, enrolled: true, progress_percent: enrollment.progress_percent }
      : item
    );
    renderCourses();
    await openCourseDetail(courseSlug);
    if (els.learnStatus) els.learnStatus.textContent = "course started";
  } catch (error) {
    const details = describeApiError(error, "enroll course");
    if (els.learnStatus) els.learnStatus.textContent = details.status;
  }
}

async function completeCourseLesson(courseSlug, lessonId) {
  const course = state.selectedCourse || state.courses.find((item) => item.slug === courseSlug);
  if (!course || course.access_type === "premium") {
    if (els.learnStatus) els.learnStatus.textContent = "premium checkout planned";
    return;
  }

  if (!localStorage.getItem(AUTH_TOKEN_KEY)) {
    openAuth("login");
    return;
  }

  try {
    const progress = await apiRequest(
      `/api/learning/courses/${encodeURIComponent(courseSlug)}/lessons/${encodeURIComponent(lessonId)}/complete`,
      { method: "POST" }
    );
    const updateCourse = (item) => item.slug === courseSlug
      ? {
          ...item,
          enrolled: true,
          progress_percent: progress.progress_percent,
          lessons: (item.lessons || []).map((lesson) => lesson.id === lessonId ? { ...lesson, completed: true } : lesson),
        }
      : item;
    state.courses = state.courses.map(updateCourse);
    state.selectedCourse = updateCourse(course);
    renderCourses();
    renderCourseDetail(state.selectedCourse);
    if (els.learnStatus) {
      els.learnStatus.textContent = `${progress.completed_lessons}/${progress.lesson_count} lessons complete`;
    }
  } catch (error) {
    const details = describeApiError(error, "complete lesson");
    if (els.learnStatus) els.learnStatus.textContent = details.status;
  }
}

function openPracticeProblem(problemRef) {
  const problem = taskBank.find((item) => item.id === problemRef || item.slug === problemRef || item.title === problemRef)
    || taskBank.find((item) => item.title.toLowerCase().replaceAll(" ", "-") === problemRef);
  if (!problem) {
    if (els.learnStatus) els.learnStatus.textContent = "practice task not loaded";
    return;
  }
  state.mode = "players";
  state.matchTasks = [problem];
  state.problemIndex = 0;
  state.matchRunning = false;
  state.currentMatchId = null;
  state.playerProgress = 0;
  state.opponentProgress = 0;
  showView("arena");
  renderProblem();
  updateRace();
  els.status.textContent = `practice // ${problem.title}`;
}

function setCourseFilter(filter) {
  state.courseFilter = filter;
  els.courseFilters.forEach((button) => {
    button.classList.toggle("active", button.dataset.courseFilter === filter);
  });
  renderCourses();
}

function formatAdminTests(tests) {
  return tests
    .map((test, index) => {
      const flags = [
        test.is_sample ? "sample" : null,
        test.is_hidden ? "hidden" : null,
      ].filter(Boolean).join(" / ");
      return `
        <div class="admin-test-row">
          <strong>Case ${test.position || index + 1}</strong>
          <span>${flags || "case"}</span>
        </div>
      `;
    })
    .join("");
}

function renderAdminProblems(problems) {
  if (!problems.length) {
    els.adminProblemList.innerHTML = `<p class="admin-empty">No tasks yet.</p>`;
    return;
  }
  els.adminProblemList.innerHTML = problems
    .map((problem) => `
      <button class="admin-problem-card${problem.id === state.adminEditingProblemId ? " active" : ""}" data-admin-problem="${problem.id}" type="button">
        <div>
          <strong>${problem.title}</strong>
          <small>${problem.difficulty} · ${problem.slug || "no-slug"}</small>
        </div>
        <span>${problem.status}</span>
      </button>
    `)
    .join("");
  document.querySelectorAll("[data-admin-problem]").forEach((button) => {
    button.addEventListener("click", () => selectAdminProblem(button.dataset.adminProblem));
  });
}

function formatSignalType(type) {
  return String(type || "signal").replaceAll("_", " ");
}

function formatSignalPayload(payload) {
  const entries = Object.entries(payload || {}).slice(0, 4);
  if (!entries.length) return "No details";
  return entries
    .map(([key, value]) => `${key}: ${typeof value === "object" ? JSON.stringify(value) : value}`)
    .join(" · ");
}

function renderAdminSignals(signals) {
  if (!els.adminSignalList) return;
  if (!signals.length) {
    els.adminSignalList.innerHTML = `<p class="admin-empty">No open signals.</p>`;
    return;
  }
  els.adminSignalList.innerHTML = signals
    .map((signal) => `
      <article class="admin-signal-card severity-${escapeHtml(signal.severity)}">
        <div>
          <strong>${escapeHtml(formatSignalType(signal.signal_type))}</strong>
          <small>${escapeHtml(signal.problem_title || "unknown task")} · ${escapeHtml(signal.username || "anonymous")}</small>
          <p>${escapeHtml(formatSignalPayload(signal.payload))}</p>
        </div>
        <button class="primary-button" data-review-signal="${escapeHtml(signal.id)}" type="button">Reviewed</button>
      </article>
    `)
    .join("");
  document.querySelectorAll("[data-review-signal]").forEach((button) => {
    button.addEventListener("click", () => markAdminSignalReviewed(button.dataset.reviewSignal));
  });
}

async function loadAdminSignals() {
  if (!state.currentUser.isAdmin || !els.adminSignalsStatus) return;
  els.adminSignalsStatus.textContent = "loading";
  try {
    const signals = await apiRequest("/api/admin/anti-cheat/signals?reviewed=false&limit=20");
    state.adminSignals = signals;
    renderAdminSignals(signals);
    els.adminSignalsStatus.textContent = `${signals.length} open`;
  } catch (error) {
    const details = describeApiError(error, "load anti-cheat signals");
    els.adminSignalsStatus.textContent = details.status;
    els.adminSignalList.innerHTML = `<p class="admin-empty">${details.terminal.join("<br>")}</p>`;
  }
}

async function markAdminSignalReviewed(signalId) {
  if (!signalId) return;
  els.adminSignalsStatus.textContent = "updating";
  try {
    await apiRequest(`/api/admin/anti-cheat/signals/${signalId}/reviewed?reviewed=true`, {
      method: "PATCH",
    });
    state.adminSignals = state.adminSignals.filter((signal) => signal.id !== signalId);
    renderAdminSignals(state.adminSignals);
    els.adminSignalsStatus.textContent = `${state.adminSignals.length} open`;
  } catch (error) {
    const details = describeApiError(error, "review anti-cheat signal");
    els.adminSignalsStatus.textContent = details.status;
  }
}

function renderAdminCalibration(items) {
  if (!els.adminCalibrationList) return;
  if (!items.length) {
    els.adminCalibrationList.innerHTML = `<p class="admin-empty">No calibration data.</p>`;
    return;
  }
  els.adminCalibrationList.innerHTML = items
    .map((item) => `
      <article class="admin-signal-card">
        <div>
          <strong>${escapeHtml(item.title)}</strong>
          <small>${escapeHtml(item.difficulty)} · ${item.accepted}/${item.attempts} accepted · ${item.acceptance_rate}%</small>
          <p>${escapeHtml(item.recommendation)}${item.average_runtime_ms ? ` · avg ${item.average_runtime_ms}ms` : ""}</p>
        </div>
      </article>
    `)
    .join("");
}

async function loadAdminCalibration() {
  if (!state.currentUser.isAdmin || !els.adminCalibrationStatus) return;
  els.adminCalibrationStatus.textContent = "loading";
  try {
    const items = await apiRequest("/api/admin/problem-calibration?limit=30");
    state.adminCalibration = items;
    renderAdminCalibration(items);
    els.adminCalibrationStatus.textContent = `${items.length} tasks`;
  } catch (error) {
    const details = describeApiError(error, "load problem calibration");
    els.adminCalibrationStatus.textContent = details.status;
    els.adminCalibrationList.innerHTML = `<p class="admin-empty">${details.terminal.join("<br>")}</p>`;
  }
}

async function loadAdminProblems() {
  if (!state.currentUser.isAdmin) return;
  els.adminStatus.textContent = "loading";
  try {
    const problems = await apiRequest("/api/admin/problems?status=active&limit=50");
    state.adminProblems = problems;
    renderAdminProblems(problems);
    els.adminStatus.textContent = `${problems.length} active`;
    loadAdminSignals();
    loadAdminCalibration();
  } catch (error) {
    const details = describeApiError(error, "load admin tasks");
    els.adminStatus.textContent = details.status;
    els.adminProblemList.innerHTML = `<p class="admin-empty">${details.terminal.join("<br>")}</p>`;
  }
}

function resetAdminForm() {
  state.adminEditingProblemId = null;
  els.adminProblemForm.reset();
  els.adminConcept.value = "arrays";
  els.adminSpeed.value = "5";
  els.adminStarter.value = "function solve() {\n  return null;\n}";
  els.adminSolutionNotes.value = "";
  els.adminTests.value = JSON.stringify([
    { input_json: [1, 2], expected_json: 3, is_sample: true, is_hidden: false },
    { input_json: [10, 5], expected_json: 15, is_sample: false, is_hidden: true },
  ], null, 2);
  els.adminSubmit.textContent = "Create Task";
  els.adminMessage.textContent = "Create a task with at least one sample and one hidden test.";
  els.adminReviewStatus.textContent = "select task";
  els.adminReviewNotes.value = "";
  els.adminReviewList.innerHTML = `<p class="admin-empty">Save or select a task before reviewing.</p>`;
  renderAdminProblems(state.adminProblems);
}

async function selectAdminProblem(problemId) {
  const problem = state.adminProblems.find((item) => item.id === problemId);
  if (!problem) return;

  state.adminEditingProblemId = problemId;
  els.adminSubmit.textContent = "Update Task";
  els.adminStatus.textContent = "loading tests";
  els.adminTitle.value = problem.title || "";
  els.adminSlug.value = problem.slug || "";
  els.adminDifficulty.value = (problem.difficulty || "easy").toLowerCase();
  els.adminConcept.value = problem.concept_group || "general";
  els.adminTags.value = (problem.tags || []).join(", ");
  els.adminSpeed.value = String(problem.speed_score || 5);
  els.adminStatement.value = problem.statement || problem.description || "";
  els.adminStarter.value = problem.starter_code_js || "function solve() {\n  return null;\n}";
  els.adminSolutionNotes.value = problem.solution_notes || "";
  renderAdminProblems(state.adminProblems);

  try {
    const tests = await apiRequest(`/api/admin/problems/${problemId}/tests`);
    els.adminTests.value = JSON.stringify(tests.map((test) => ({
      input_json: test.input_json,
      expected_json: test.expected_json,
      is_sample: test.is_sample,
      is_hidden: test.is_hidden,
      explanation: test.explanation,
    })), null, 2);
    els.adminStatus.textContent = `${tests.length} tests`;
    els.adminMessage.textContent = `Editing: ${problem.title}`;
    await loadAdminReviews(problemId);
  } catch (error) {
    const details = describeApiError(error, "load task tests");
    els.adminStatus.textContent = details.status;
    els.adminMessage.textContent = details.terminal.join(" ");
  }
}

function renderAdminReviews(reviews) {
  if (!reviews.length) {
    els.adminReviewList.innerHTML = `<p class="admin-empty">No reviews yet.</p>`;
    return;
  }
  els.adminReviewList.innerHTML = reviews
    .slice(0, 5)
    .map((review) => `
      <article class="admin-review-card">
        <strong>${escapeHtml(formatSignalType(review.status))}</strong>
        <small>${new Date(review.created_at).toLocaleString()}</small>
        <p>${escapeHtml(review.notes || "No notes")}</p>
      </article>
    `)
    .join("");
}

async function loadAdminReviews(problemId = state.adminEditingProblemId) {
  if (!problemId) {
    els.adminReviewStatus.textContent = "select task";
    return;
  }
  els.adminReviewStatus.textContent = "loading";
  try {
    const reviews = await apiRequest(`/api/admin/problems/${problemId}/reviews`);
    renderAdminReviews(reviews);
    els.adminReviewStatus.textContent = `${reviews.length} reviews`;
  } catch (error) {
    const details = describeApiError(error, "load reviews");
    els.adminReviewStatus.textContent = details.status;
    els.adminReviewList.innerHTML = `<p class="admin-empty">${details.terminal.join("<br>")}</p>`;
  }
}

async function submitAdminReview(status) {
  if (!state.adminEditingProblemId) {
    els.adminReviewStatus.textContent = "select task";
    els.adminReviewList.innerHTML = `<p class="admin-empty">Select a task before adding review.</p>`;
    return;
  }
  const notes = els.adminReviewNotes.value.trim();
  if (status === "needs_changes" && !notes) {
    els.adminReviewStatus.textContent = "notes required";
    els.adminReviewList.innerHTML = `<p class="admin-empty">Needs Changes review must include notes.</p>`;
    return;
  }
  els.adminReviewStatus.textContent = "saving";
  try {
    await apiRequest(`/api/admin/problems/${state.adminEditingProblemId}/reviews`, {
      method: "POST",
      body: JSON.stringify({
        status,
        notes,
        checklist: {
          statement_clear: true,
          samples_visible: true,
          hidden_tests_ready: true,
        },
      }),
    });
    els.adminReviewNotes.value = "";
    await loadAdminReviews();
  } catch (error) {
    const details = describeApiError(error, "save review");
    els.adminReviewStatus.textContent = details.status;
    els.adminReviewList.innerHTML = `<p class="admin-empty">${details.terminal.join("<br>")}</p>`;
  }
}

function parseAdminTests() {
  let parsed;
  try {
    parsed = JSON.parse(els.adminTests.value);
  } catch (error) {
    throw new Error(`Tests JSON is invalid: ${error.message}`);
  }
  if (!Array.isArray(parsed) || parsed.length === 0) {
    throw new Error("Tests JSON must be a non-empty array.");
  }
  return parsed.map((test, index) => {
    const inputJson = test.input_json ?? test.inputJson ?? [];
    const expectedJson = test.expected_json ?? test.expectedJson ?? null;
    return {
      position: test.position || index + 1,
      input: test.input || JSON.stringify(inputJson),
      expected_output: test.expected_output || JSON.stringify(expectedJson),
      input_json: inputJson,
      expected_json: expectedJson,
      is_sample: Boolean(test.is_sample),
      is_hidden: test.is_hidden !== false,
      explanation: test.explanation || null,
    };
  });
}

function buildAdminProblemPayload() {
  const statement = els.adminStatement.value.trim();
  const title = els.adminTitle.value.trim();
  const tests = parseAdminTests();
  return {
    title,
    slug: els.adminSlug.value.trim() || null,
    description: statement,
    statement,
    difficulty: els.adminDifficulty.value,
    status: "active",
    concept_group: els.adminConcept.value.trim() || "general",
    tags: els.adminTags.value
      .split(",")
      .map((tag) => tag.trim())
      .filter(Boolean),
    starter_code_js: els.adminStarter.value,
    solution_notes: els.adminSolutionNotes.value.trim() || null,
    estimated_seconds: 300,
    speed_score: Number(els.adminSpeed.value || 5),
    time_limit_ms: 1000,
    memory_limit_mb: 256,
    test_cases: tests,
  };
}

function buildAdminProblemUpdatePayload() {
  const payload = buildAdminProblemPayload();
  delete payload.test_cases;
  return payload;
}

async function handleAdminProblemSubmit(event) {
  event.preventDefault();
  if (!state.currentUser.isAdmin) {
    els.adminMessage.textContent = "Admin access required.";
    return;
  }

  els.adminMessage.textContent = "Creating task...";
  try {
    const tests = parseAdminTests();
    if (state.adminEditingProblemId) {
      els.adminMessage.textContent = "Updating task...";
      const updated = await apiRequest(`/api/admin/problems/${state.adminEditingProblemId}`, {
        method: "PATCH",
        body: JSON.stringify(buildAdminProblemUpdatePayload()),
      });
      await apiRequest(`/api/admin/problems/${state.adminEditingProblemId}/tests`, {
        method: "PUT",
        body: JSON.stringify(tests),
      });
      els.adminMessage.textContent = `Updated: ${updated.title}`;
    } else {
      const payload = buildAdminProblemPayload();
      payload.test_cases = tests;
      const created = await apiRequest("/api/admin/problems", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      els.adminMessage.textContent = `Created: ${created.title}`;
      state.adminEditingProblemId = created.id;
    }
    await loadAdminProblems();
  } catch (error) {
    const details = error instanceof ApiError
      ? describeApiError(error, "create admin task")
      : { terminal: [error.message || "Task form failed."] };
    els.adminMessage.textContent = details.terminal.join(" ");
  }
}

function resetArenaLobby() {
  els.arenaView.classList.remove("match-live");
  els.arenaCircleTask.textContent = "READY";
  els.arenaCircleTitle.textContent = "Choose time and press start";
  state.playerProgress = 0;
  state.opponentProgress = 0;
  updateRace();
}

function renderProblem() {
  clearApiError();
  const problem = currentProblem();
  els.title.textContent = problem.title;
  els.difficulty.textContent = problem.difficulty;
  els.description.textContent = problem.description;
  els.tags.innerHTML = problem.tags.map((tag) => `<span class="tag">${tag}</span>`).join("");
  els.cases.innerHTML = problem.cases
    .map((item, index) => `<div class="case"><strong>Case ${index + 1}</strong><br>input: ${item.input}<br>expected: ${item.expected}</div>`)
    .join("");
  els.editor.value = getLanguageStarter(problem);
  els.arenaCircleTask.textContent = `TASK ${String(state.problemIndex + 1).padStart(2, "0")}`;
  els.arenaCircleTitle.textContent = problem.title;
  renderEmptyTests();
  renderTaskLadder();
  resetDebug();
  updateRace();
  updateCodeHighlight();
}

function renderTaskLadder() {
  els.taskLadder.innerHTML = state.matchTasks
    .map((problem, index) => {
      const active = index === state.problemIndex ? " active" : "";
      return `
        <button class="task-chip${active}" data-task-index="${index}" type="button">
          <strong>TASK ${String(index + 1).padStart(2, "0")}</strong>
          <small>${problem.difficulty} · ${problem.title}</small>
          <div class="task-bars">
            <div class="tiny-track"><span class="opp" data-opp-task="${index}"></span></div>
            <div class="tiny-track"><span class="me" data-me-task="${index}"></span></div>
          </div>
        </button>
      `;
    })
    .join("");

  document.querySelectorAll("[data-task-index]").forEach((button) => {
    button.addEventListener("click", () => switchTask(Number(button.dataset.taskIndex)));
  });
}

function renderEmptyTests() {
  const problem = currentProblem();
  if (!els.summary || !els.terminal) return;
  els.summary.textContent = `${problem.cases.length} cases`;
  els.terminal.textContent = problem.id
    ? "Backend judge ready. Run checks samples; Submit checks hidden tests."
    : "Run checks 5 tests. Submit checks 50 judge tests.";
  setConsoleTab("terminal");
}

function parseCaseValue(source) {
  return Function(`"use strict"; return (${source});`)();
}

function parseCaseInput(source) {
  return Function(`"use strict"; return [${source}];`)();
}

function formatJudgeValue(value) {
  if (typeof value === "undefined") return "undefined";
  if (typeof value === "string") return JSON.stringify(value);
  const json = JSON.stringify(value);
  return typeof json === "undefined" ? String(value) : json;
}

function makeRng(seed) {
  let value = seed % 2147483647;
  if (value <= 0) value += 2147483646;
  return () => {
    value = (value * 16807) % 2147483647;
    return (value - 1) / 2147483646;
  };
}

function randInt(rng, min, max) {
  return min + Math.floor(rng() * (max - min + 1));
}

function cloneGrid(grid) {
  return grid.map((row) => [...row]);
}

const judgeSolvers = {
  "Pair Sprint": (nums, target) => {
    for (let i = 0; i < nums.length; i++) {
      for (let j = i + 1; j < nums.length; j++) {
        if (nums[i] + nums[j] === target) return [i, j];
      }
    }
    return [];
  },
  "Bracket Dash": (s) => {
    const pairs = { ")": "(", "]": "[", "}": "{" };
    const stack = [];
    for (const ch of s) {
      if ("([{".includes(ch)) stack.push(ch);
      else if (stack.pop() !== pairs[ch]) return false;
    }
    return stack.length === 0;
  },
  "Max Streak": (nums) => {
    let best = 0;
    let count = 0;
    for (const n of nums) {
      count = n === 1 ? count + 1 : 0;
      best = Math.max(best, count);
    }
    return best;
  },
  "Clean Duplicates": (nums) => [...new Set(nums)],
  "First Unique": (s) => {
    const counts = new Map();
    for (const ch of s) counts.set(ch, (counts.get(ch) || 0) + 1);
    for (const ch of s) if (counts.get(ch) === 1) return ch;
    return "";
  },
  "Merge Sorted": (a, b) => [...a, ...b].sort((x, y) => x - y),
  "Mirror Word": (s) => {
    const clean = s.replace(/\s+/g, "").toLowerCase();
    return clean === [...clean].reverse().join("");
  },
  "Missing Level": (nums) => {
    const n = nums.length;
    return (n * (n + 1)) / 2 - nums.reduce((sum, value) => sum + value, 0);
  },
  "Most Frequent": (nums) => {
    const counts = new Map();
    let answer = nums[0];
    let best = 0;
    for (const n of nums) {
      const next = (counts.get(n) || 0) + 1;
      counts.set(n, next);
      if (next > best) {
        best = next;
        answer = n;
      }
    }
    return answer;
  },
  "Window Sum": (nums, k) => {
    let sum = 0;
    for (let i = 0; i < k; i++) sum += nums[i];
    let best = sum;
    for (let i = k; i < nums.length; i++) {
      sum += nums[i] - nums[i - k];
      best = Math.max(best, sum);
    }
    return best;
  },
  "Island Count": (grid) => {
    const copy = cloneGrid(grid);
    const rows = copy.length;
    const cols = copy[0]?.length || 0;
    let count = 0;
    const dfs = (r, c) => {
      if (r < 0 || c < 0 || r >= rows || c >= cols || copy[r][c] !== 1) return;
      copy[r][c] = 0;
      dfs(r + 1, c); dfs(r - 1, c); dfs(r, c + 1); dfs(r, c - 1);
    };
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        if (copy[r][c] === 1) {
          count++;
          dfs(r, c);
        }
      }
    }
    return count;
  },
  "Daily Temperatures": (temps) => {
    const answer = Array(temps.length).fill(0);
    const stack = [];
    for (let i = 0; i < temps.length; i++) {
      while (stack.length && temps[i] > temps[stack.at(-1)]) {
        const prev = stack.pop();
        answer[prev] = i - prev;
      }
      stack.push(i);
    }
    return answer;
  },
  "Subarray Target": (nums, target) => {
    for (let start = 0; start < nums.length; start++) {
      let sum = 0;
      for (let end = start; end < nums.length; end++) {
        sum += nums[end];
        if (sum === target) return true;
      }
    }
    return false;
  },
  "Longest Unique": (s) => {
    const seen = new Map();
    let left = 0;
    let best = 0;
    for (let right = 0; right < s.length; right++) {
      if (seen.has(s[right]) && seen.get(s[right]) >= left) left = seen.get(s[right]) + 1;
      seen.set(s[right], right);
      best = Math.max(best, right - left + 1);
    }
    return best;
  },
  "Grid Escape": (grid) => {
    const rows = grid.length;
    const cols = grid[0]?.length || 0;
    if (!rows || !cols || grid[0][0] || grid[rows - 1][cols - 1]) return -1;
    const queue = [[0, 0, 1]];
    const seen = new Set(["0,0"]);
    for (let head = 0; head < queue.length; head++) {
      const [r, c, dist] = queue[head];
      if (r === rows - 1 && c === cols - 1) return dist;
      for (const [dr, dc] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const nr = r + dr;
        const nc = c + dc;
        const key = `${nr},${nc}`;
        if (nr >= 0 && nc >= 0 && nr < rows && nc < cols && grid[nr][nc] === 0 && !seen.has(key)) {
          seen.add(key);
          queue.push([nr, nc, dist + 1]);
        }
      }
    }
    return -1;
  },
  "Coin Race": (coins, amount) => {
    const dp = Array(amount + 1).fill(Infinity);
    dp[0] = 0;
    for (let current = 1; current <= amount; current++) {
      for (const coin of coins) {
        if (current >= coin) dp[current] = Math.min(dp[current], dp[current - coin] + 1);
      }
    }
    return Number.isFinite(dp[amount]) ? dp[amount] : -1;
  },
  "Course Unlock": (n, prerequisites) => {
    const graph = Array.from({ length: n }, () => []);
    const indegree = Array(n).fill(0);
    for (const [course, before] of prerequisites) {
      graph[before].push(course);
      indegree[course]++;
    }
    const queue = indegree.map((value, index) => value === 0 ? index : -1).filter((value) => value >= 0);
    let done = 0;
    for (let head = 0; head < queue.length; head++) {
      done++;
      for (const next of graph[queue[head]]) {
        indegree[next]--;
        if (indegree[next] === 0) queue.push(next);
      }
    }
    return done === n;
  },
  "Word Portal": (begin, end, list) => {
    const words = new Set(list);
    if (!words.has(end)) return 0;
    const queue = [[begin, 1]];
    const seen = new Set([begin]);
    for (let head = 0; head < queue.length; head++) {
      const [word, distance] = queue[head];
      if (word === end) return distance;
      for (let i = 0; i < word.length; i++) {
        for (let code = 97; code <= 122; code++) {
          const next = word.slice(0, i) + String.fromCharCode(code) + word.slice(i + 1);
          if (words.has(next) && !seen.has(next)) {
            seen.add(next);
            queue.push([next, distance + 1]);
          }
        }
      }
    }
    return 0;
  },
};

function makeJudgeInput(title, index) {
  const rng = makeRng((index + 17) * 7919 + title.length * 101);
  if (title === "Pair Sprint") {
    const nums = Array.from({ length: randInt(rng, 5, 12) }, (_, itemIndex) => itemIndex * 100 + randInt(rng, 1, 25));
    const i = randInt(rng, 0, nums.length - 2);
    const j = randInt(rng, i + 1, nums.length - 1);
    return [nums, nums[i] + nums[j]];
  }
  if (title === "Bracket Dash") return [["()[]{}", "([{}])", "((())", "([)]", "{[()()]}", "{[(])}"][index % 6]];
  if (title === "Max Streak") return [Array.from({ length: randInt(rng, 8, 24) }, () => randInt(rng, 0, 1))];
  if (title === "Clean Duplicates") return [Array.from({ length: randInt(rng, 8, 22) }, () => randInt(rng, -4, 9))];
  if (title === "First Unique") return [["leetcode", "aabbc", "aabb", "swiss", "racecar", "mississippi", "xxyzzq"][index % 7]];
  if (title === "Merge Sorted") {
    const a = Array.from({ length: randInt(rng, 0, 8) }, () => randInt(rng, -12, 18)).sort((x, y) => x - y);
    const b = Array.from({ length: randInt(rng, 0, 8) }, () => randInt(rng, -12, 18)).sort((x, y) => x - y);
    return [a, b];
  }
  if (title === "Mirror Word") return [["Never odd or even", "race car", "hello", "Step on no pets", "level", "code blitz"][index % 6]];
  if (title === "Missing Level") {
    const n = randInt(rng, 3, 30);
    const missing = randInt(rng, 0, n);
    return [Array.from({ length: n + 1 }, (_, value) => value).filter((value) => value !== missing).sort(() => rng() - 0.5)];
  }
  if (title === "Most Frequent") {
    const winner = randInt(rng, -5, 8);
    const nums = Array.from({ length: 5 }, () => winner);
    for (let i = 0; i < 12; i++) nums.push(randInt(rng, 10, 35));
    return [nums.sort(() => rng() - 0.5)];
  }
  if (title === "Window Sum") {
    const nums = Array.from({ length: randInt(rng, 5, 16) }, () => randInt(rng, -5, 20));
    return [nums, randInt(rng, 1, nums.length)];
  }
  if (title === "Island Count") {
    const rows = randInt(rng, 3, 7);
    const cols = randInt(rng, 3, 7);
    return [Array.from({ length: rows }, () => Array.from({ length: cols }, () => rng() > 0.55 ? 1 : 0))];
  }
  if (title === "Daily Temperatures") return [Array.from({ length: randInt(rng, 5, 18) }, () => randInt(rng, 30, 100))];
  if (title === "Subarray Target") {
    const nums = Array.from({ length: randInt(rng, 5, 14) }, () => randInt(rng, -6, 12));
    const start = randInt(rng, 0, nums.length - 1);
    const end = randInt(rng, start, nums.length - 1);
    return [nums, nums.slice(start, end + 1).reduce((sum, value) => sum + value, 0)];
  }
  if (title === "Longest Unique") {
    const letters = "abcdeffghij";
    return [Array.from({ length: randInt(rng, 6, 18) }, () => letters[randInt(rng, 0, letters.length - 1)]).join("")];
  }
  if (title === "Grid Escape") {
    const rows = randInt(rng, 3, 7);
    const cols = randInt(rng, 3, 7);
    const grid = Array.from({ length: rows }, () => Array.from({ length: cols }, () => rng() > 0.72 ? 1 : 0));
    grid[0][0] = 0;
    grid[rows - 1][cols - 1] = 0;
    return [grid];
  }
  if (title === "Coin Race") {
    const coins = [...new Set(Array.from({ length: randInt(rng, 2, 5) }, () => randInt(rng, 1, 9)))].sort((a, b) => a - b);
    return [coins, randInt(rng, 0, 45)];
  }
  if (title === "Course Unlock") {
    const n = randInt(rng, 2, 8);
    const prerequisites = [];
    if (index % 5 === 0 && n > 2) {
      for (let course = 1; course < n; course++) prerequisites.push([course, course - 1]);
      prerequisites.push([0, n - 1]);
    } else {
      for (let course = 1; course < n; course++) {
        if (rng() > 0.35) prerequisites.push([course, randInt(rng, 0, course - 1)]);
      }
    }
    return [n, prerequisites];
  }
  if (title === "Word Portal") {
    const samples = [
      ["hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]],
      ["hit", "cog", ["hot", "dot", "dog"]],
      ["cat", "dog", ["cot", "cog", "dog"]],
      ["red", "tax", ["ted", "tex", "tax", "tad", "den", "rex"]],
    ];
    return samples[index % samples.length];
  }
  return null;
}

function makeGeneratedJudgeCase(problem, index) {
  const solver = judgeSolvers[problem.title];
  const input = solver ? makeJudgeInput(problem.title, index) : null;
  if (!solver || !input) return null;
  return {
    index: index + 1,
    generated: true,
    inputText: input.map(formatJudgeValue).join(", "),
    expectedText: formatJudgeValue(solver(...input)),
    args: input,
    expected: solver(...input),
  };
}

function buildJudgeCases(problem, total = problem.cases.length) {
  const sourceCases = problem.cases.length ? problem.cases : [];
  return Array.from({ length: total }, (_, index) => {
    if (index >= sourceCases.length) {
      const generated = makeGeneratedJudgeCase(problem, index);
      if (generated) return generated;
    }
    const test = sourceCases[index % sourceCases.length];
    return {
      index: index + 1,
      sourceIndex: (index % sourceCases.length) + 1,
      repeated: index >= sourceCases.length,
    inputText: test.input,
    expectedText: test.expected,
    args: parseCaseInput(test.input),
    expected: parseCaseValue(test.expected),
    };
  });
}

function executeJavaScriptTests(code, cases, title) {
  const workerSource = `
    function formatValue(value) {
      if (typeof value === "undefined") return "undefined";
      if (typeof value === "string") return value;
      try {
        const json = JSON.stringify(value);
        return typeof json === "undefined" ? String(value) : json;
      } catch (error) {
        return String(value);
      }
    }

    function deepEqual(a, b) {
      if (Object.is(a, b)) return true;
      if (Array.isArray(a) || Array.isArray(b)) {
        if (!Array.isArray(a) || !Array.isArray(b) || a.length !== b.length) return false;
        for (let i = 0; i < a.length; i++) {
          if (!deepEqual(a[i], b[i])) return false;
        }
        return true;
      }
      if (a && b && typeof a === "object" && typeof b === "object") {
        const aKeys = Object.keys(a).sort();
        const bKeys = Object.keys(b).sort();
        if (!deepEqual(aKeys, bKeys)) return false;
        for (const key of aKeys) {
          if (!deepEqual(a[key], b[key])) return false;
        }
        return true;
      }
      return false;
    }

    function isValidResult(title, received, expected, args) {
      if (title === "Pair Sprint") {
        if (!Array.isArray(received) || received.length !== 2) return false;
        const [i, j] = received;
        const [nums, target] = args;
        return Number.isInteger(i)
          && Number.isInteger(j)
          && i !== j
          && i >= 0
          && j >= 0
          && i < nums.length
          && j < nums.length
          && nums[i] + nums[j] === target;
      }

      if (title === "Most Frequent") {
        const [nums] = args;
        const counts = new Map();
        for (const n of nums) counts.set(n, (counts.get(n) || 0) + 1);
        const best = Math.max(...counts.values());
        return counts.get(received) === best;
      }

      return deepEqual(received, expected);
    }

    self.onmessage = (event) => {
      const { code, cases, title } = event.data;
      let solve;

      try {
        solve = Function('"use strict";\\n' + code + '\\n; return typeof solve === "function" ? solve : null;')();
      } catch (error) {
        self.postMessage({ compileError: error.message || String(error) });
        return;
      }

      if (typeof solve !== "function") {
        self.postMessage({ compileError: "Function solve(...) was not found." });
        return;
      }

      const results = [];
      const logs = [];
      const originalConsole = self.console;
      self.console = {
        ...originalConsole,
        log: (...items) => logs.push(items.map(formatValue).join(" ")),
        warn: (...items) => logs.push("warn: " + items.map(formatValue).join(" ")),
        error: (...items) => logs.push("error: " + items.map(formatValue).join(" ")),
      };

      for (const test of cases) {
        try {
          const args = JSON.parse(JSON.stringify(test.args));
          const received = solve(...args);
          const passed = isValidResult(title, received, test.expected, args);
          results.push({ index: test.index, passed, received });
        } catch (error) {
          results.push({ index: test.index, passed: false, runtimeError: error.message || String(error) });
        }
      }

      self.console = originalConsole;
      self.postMessage({ results, logs });
    };
  `;

  return new Promise((resolve) => {
    const blob = new Blob([workerSource], { type: "text/javascript" });
    const workerUrl = URL.createObjectURL(blob);
    const worker = new Worker(workerUrl);
    const timeout = window.setTimeout(() => {
      worker.terminate();
      URL.revokeObjectURL(workerUrl);
      resolve({ timeout: true });
    }, 1800);

    worker.onmessage = (event) => {
      window.clearTimeout(timeout);
      worker.terminate();
      URL.revokeObjectURL(workerUrl);
      resolve(event.data);
    };

    worker.onerror = (event) => {
      window.clearTimeout(timeout);
      worker.terminate();
      URL.revokeObjectURL(workerUrl);
      resolve({ compileError: event.message || "Worker execution failed." });
    };

    worker.postMessage({ code, cases, title });
  });
}

function renderBackendJudgeResult(result, label) {
  const passed = result.passed_count || 0;
  const total = result.total_count || 0;
  els.summary.textContent = `${passed} / ${total}`;
  const detailLines = (result.case_results || []).flatMap((item) => {
    const name = `Case ${item.position}`;
    if (item.status === "accepted") return [`${name}: OK`];
    return [
      `${name}: ${item.status}`,
      `  Expected: ${formatJudgeValue(item.expected)}`,
      `  Received: ${item.error_message ? item.error_message : formatJudgeValue(item.actual)}`,
    ];
  });
  els.terminal.textContent = [
    `> ${label}`,
    `Status: ${result.status}`,
    `Passed: ${passed}`,
    `Failed: ${Math.max(0, total - passed)}`,
    "",
    ...detailLines,
    "",
    result.message || (result.status === "accepted" ? "Accepted" : "Wrong Answer"),
  ].join("\n");
  setConsoleTab("terminal");
  return total > 0 && passed === total && result.status === "accepted";
}

async function runBackendSubmission(problem, kind, label) {
  clearApiError();
  els.summary.textContent = "running";
  els.terminal.textContent = `> ${label}\nSending code to backend judge...`;

  const result = await apiRequest("/api/submissions", {
    method: "POST",
    body: JSON.stringify({
      problem_id: problem.id,
      match_id: state.currentMatchId,
      match_task_id: problem.matchTaskId,
      language: state.language,
      code: els.editor.value,
      kind,
    }),
  });
  return renderBackendJudgeResult(result, label);
}

async function loadProblemSolution() {
  const problem = currentProblem();
  if (!problem?.id) {
    els.terminal.textContent = "> editorial\nEditorials are available for backend tasks after solving.";
    setConsoleTab("terminal");
    return;
  }
  if (!localStorage.getItem(AUTH_TOKEN_KEY)) {
    els.status.textContent = "login required for editorial";
    openAuth("login");
    return;
  }
  els.summary.textContent = "editorial";
  els.terminal.textContent = "> editorial\nChecking solved status...";
  setConsoleTab("terminal");
  try {
    const solution = await apiRequest(`/api/problems/${encodeURIComponent(problem.id)}/solution`);
    els.terminal.textContent = [
      `> editorial // ${solution.title}`,
      "",
      solution.solution_notes || "No editorial notes have been written yet.",
    ].join("\n");
    els.status.textContent = "editorial opened";
  } catch (error) {
    showApiError(error, "open editorial");
  }
}

async function runCode(options = {}) {
  const {
    caseCount = 5,
    advanceOnAccepted = false,
    label = "run solution",
  } = options;
  const problem = currentProblem();
  const code = els.editor.value;

  if (!isLanguageExecutable(state.language)) {
    const language = state.judgeLanguages.find((item) => item.id === state.language);
    els.summary.textContent = "planned";
    els.terminal.textContent = [
      `> ${label}`,
      `${language?.label || state.language} is planned but not executable yet.`,
      language?.notes || "Compiled languages need a typed adapter contract before judging.",
    ].join("\n");
    setConsoleTab("terminal");
    els.status.textContent = "language planned";
    return false;
  }

  if (problem.id) {
    try {
      const accepted = await runBackendSubmission(problem, advanceOnAccepted ? "submit" : "run", label);
      if (advanceOnAccepted && accepted) {
        const taskProgress = 100;
        state.playerProgress = Math.max(
          state.playerProgress,
          Math.round(((state.problemIndex * 100) + taskProgress) / state.matchTasks.length)
        );
        if (state.problemIndex < state.matchTasks.length - 1) {
          els.status.textContent = "task complete // loading next";
          setTimeout(nextProblem, 450);
        } else {
          els.status.textContent = "task complete";
        }
        updateRace();
      } else {
        els.status.textContent = accepted ? "sample tests passed" : "wrong answer";
      }
      return accepted;
    } catch (error) {
      showApiError(error, label);
      return false;
    }
  }

  if (state.language !== "javascript") {
    els.summary.textContent = "js only";
    els.terminal.textContent = [
      `> ${label}`,
      "Real test execution is ready for JavaScript now.",
      "Switch Language to JavaScript and write function solve(...).",
      "Other languages are editor templates until backend judge is connected.",
    ].join("\n");
    setConsoleTab("terminal");
    els.status.textContent = "javascript runner only";
    return false;
  }

  const codeErrors = getCodeErrors(code);
  if (codeErrors.length > 0) {
    els.summary.textContent = "syntax";
    els.terminal.textContent = [
      `> ${label}`,
      "Syntax check failed.",
      ...codeErrors.map((error) => `Line ${error.number}: ${error.message}`),
    ].join("\n");
    setConsoleTab("terminal");
    els.status.textContent = "syntax error";
    updateCodeHighlight();
    return false;
  }

  let judgeCases;
  try {
    judgeCases = buildJudgeCases(problem, caseCount);
  } catch (error) {
    els.summary.textContent = "case error";
    els.terminal.textContent = [
      `> ${label}`,
      "Test case parser failed.",
      error.message || String(error),
    ].join("\n");
    return false;
  }

  els.summary.textContent = "running";
  els.terminal.textContent = `> ${label}\nRunning ${judgeCases.length} test cases...`;

  const judge = await executeJavaScriptTests(code, judgeCases, problem.title);
  if (judge.timeout) {
    els.summary.textContent = "timeout";
    els.terminal.textContent = [
      `> ${label}`,
      "Time Limit Exceeded.",
      "Your code did not finish in 1.8 seconds.",
    ].join("\n");
    els.status.textContent = "time limit";
    return false;
  }

  if (judge.compileError) {
    els.summary.textContent = "error";
    els.terminal.textContent = [
      `> ${label}`,
      "Code execution failed.",
      judge.compileError,
    ].join("\n");
    els.status.textContent = "runtime error";
    return false;
  }

  const passed = judge.results.filter((result) => result.passed).length;
  const total = judgeCases.length;

  if (els.summary && els.terminal) {
    els.summary.textContent = `${passed} / ${total}`;
    const detailLines = judge.results.flatMap((result, index) => {
      const test = judgeCases[index];
      const caseLabel = test.repeated
        ? `Case ${result.index} (from case ${test.sourceIndex})`
        : `Case ${result.index}`;
      if (result.passed) {
        return [`${caseLabel}: OK`];
      }
      return [
        `${caseLabel}: Failed`,
        `  Input: ${test.inputText}`,
        `  Expected: ${test.expectedText}`,
        `  Received: ${result.runtimeError ? `Runtime Error: ${result.runtimeError}` : formatJudgeValue(result.received)}`,
      ];
    });
    const logLines = judge.logs && judge.logs.length
      ? ["", "Console output:", ...judge.logs.map((line) => `  ${line}`)]
      : [];
    els.terminal.textContent = [
      `> ${label}`,
      `Running ${total} test cases...`,
      `Passed: ${passed}`,
      `Failed: ${total - passed}`,
      "",
      ...detailLines,
      ...logLines,
      "",
      passed === total ? "Accepted" : "Wrong Answer",
    ].join("\n");
    setConsoleTab("terminal");
  }

  if (advanceOnAccepted) {
    const taskProgress = Math.round((passed / total) * 100);
    state.playerProgress = Math.max(
      state.playerProgress,
      Math.round(((state.problemIndex * 100) + taskProgress) / state.matchTasks.length)
    );
  }

  if (advanceOnAccepted && passed === total && state.problemIndex < state.matchTasks.length - 1) {
    els.status.textContent = "task complete // loading next";
    setTimeout(nextProblem, 450);
  } else {
    els.status.textContent = passed === total
      ? (advanceOnAccepted ? "task complete" : "sample tests passed")
      : "wrong answer";
  }

  updateRace();
  return passed === total;
}

async function submitCode() {
  const solved = await runCode({
    caseCount: 50,
    advanceOnAccepted: true,
    label: "submit solution",
  });
  if (!solved) return;
  if (state.problemIndex === state.matchTasks.length - 1) {
    state.playerProgress = 100;
    updateRace();
    await refreshProfileAfterMatch();
    endMatch("finish // solution accepted");
  }
}

function formatCode() {
  els.editor.value = els.editor.value
    .split("\n")
    .map((line) => line.trimEnd())
    .join("\n")
    .replace(/\n{3,}/g, "\n\n");
  updateCodeHighlight();
}

async function waitForBackendMatch(initialMatchId = null) {
  if (initialMatchId) return initialMatchId;

  return new Promise((resolve, reject) => {
    let attempts = 0;
    state.matchPollId = setInterval(async () => {
      attempts += 1;
      try {
        const status = await apiRequest("/api/matchmaking/status");
        if (status.status === "matched" && status.match_id) {
          clearInterval(state.matchPollId);
          state.matchPollId = null;
          resolve(status.match_id);
        } else if (status.status === "expired") {
          clearInterval(state.matchPollId);
          state.matchPollId = null;
          reject(new ApiError("Matchmaking expired. Try again.", {
            status: 400,
            detail: "Matchmaking expired. Try again.",
            kind: "expired-match",
          }));
        } else {
          const range = status.rating_min && status.rating_max ? ` ${status.rating_min}-${status.rating_max}` : "";
          els.status.textContent = `searching opponent${range}`;
        }

        if (attempts >= 45) {
          clearInterval(state.matchPollId);
          state.matchPollId = null;
          reject(new ApiError("No opponent found yet. Keep another player in queue and try again.", {
            status: 408,
            detail: "No opponent found yet. Keep another player in queue and try again.",
            kind: "request",
          }));
        }
      } catch (error) {
        clearInterval(state.matchPollId);
        state.matchPollId = null;
        reject(error);
      }
    }, 2000);
  });
}

async function createFriendRoom() {
  const opponentUsername = els.roomOpponentInput.value.trim();
  if (!opponentUsername) {
    els.roomOpponentInput.focus();
    throw new ApiError("Enter a friend login first.", {
      status: 400,
      detail: "Enter a friend login first.",
      kind: "request",
    });
  }

  const room = await apiRequest("/api/matchmaking/rooms", {
    method: "POST",
    body: JSON.stringify({ opponent_username: opponentUsername }),
  });
  state.currentRoomId = room.id;
  els.roomStatus.textContent = `waiting for ${room.invited_username}`;
  els.status.textContent = `room created // invite sent to ${room.invited_username}`;
  writeRoomLinkToUrl(room.id);
  return room;
}

function buildRoomLink(roomId = state.currentRoomId) {
  if (!roomId) return "";
  const url = new URL(window.location.href);
  url.pathname = url.pathname.endsWith("/") ? `${url.pathname}index.html` : url.pathname;
  url.searchParams.set("room", roomId);
  return url.toString();
}

function writeRoomLinkToUrl(roomId) {
  const url = new URL(window.location.href);
  url.searchParams.set("room", roomId);
  window.history.replaceState({}, "", url);
}

function clearRoomLinkFromUrl() {
  const url = new URL(window.location.href);
  if (!url.searchParams.has("room")) return;
  url.searchParams.delete("room");
  window.history.replaceState({}, "", url);
}

async function copyCurrentRoomLink() {
  clearApiError();
  const link = buildRoomLink();
  if (!link) {
    els.roomStatus.textContent = "create a room first";
    return;
  }

  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(link);
    } else {
      const helper = document.createElement("textarea");
      helper.value = link;
      helper.setAttribute("readonly", "");
      helper.style.position = "fixed";
      helper.style.left = "-9999px";
      document.body.appendChild(helper);
      helper.select();
      document.execCommand("copy");
      helper.remove();
    }
    els.roomStatus.textContent = "room link copied";
    els.terminal.textContent = `> friend room\n${link}`;
    setConsoleTab("terminal");
  } catch (error) {
    showApiError(new ApiError("Could not copy room link.", {
      status: 400,
      detail: error.message || "Could not copy room link.",
      kind: "request",
    }), "copy room link");
  }
}

async function waitForRoomMatch(roomId, waitingMatchId) {
  let attempts = 0;
  return new Promise((resolve, reject) => {
    state.roomWaitReject = reject;
    state.matchPollId = setInterval(async () => {
      attempts += 1;
      try {
        const room = await apiRequest(`/api/matchmaking/rooms/${encodeURIComponent(roomId)}`);
        state.currentRoomId = room.id;
        els.roomStatus.textContent = `${room.status} // ${room.invited_username}`;

        if (room.status === "accepted") {
          clearInterval(state.matchPollId);
          state.matchPollId = null;
          state.roomWaitReject = null;
          clearRoomLinkFromUrl();
          resolve(room.match_id || waitingMatchId);
          return;
        }

        if (["expired", "cancelled"].includes(room.status)) {
          clearInterval(state.matchPollId);
          state.matchPollId = null;
          state.roomWaitReject = null;
          reject(new ApiError("Friend room expired. Create a new room.", {
            status: 400,
            detail: "Friend room expired. Create a new room.",
            kind: "expired-match",
          }));
          return;
        }

        els.status.textContent = `waiting for ${room.invited_username} to join`;
        if (attempts >= 120) {
          clearInterval(state.matchPollId);
          state.matchPollId = null;
          state.roomWaitReject = null;
          reject(new ApiError("Friend did not join yet. Try again when both players are ready.", {
            status: 408,
            detail: "Friend did not join yet. Try again when both players are ready.",
            kind: "request",
          }));
        }
      } catch (error) {
        clearInterval(state.matchPollId);
        state.matchPollId = null;
        state.roomWaitReject = null;
        reject(error);
      }
    }, 2000);
  });
}

async function cancelCurrentRoom() {
  clearApiError();
  if (!state.currentRoomId) {
    els.roomStatus.textContent = "no active room";
    return;
  }

  const roomId = state.currentRoomId;
  clearInterval(state.matchPollId);
  state.matchPollId = null;
  const rejectWait = state.roomWaitReject;
  state.roomWaitReject = null;
  state.currentRoomId = null;

  try {
    await apiRequest(`/api/matchmaking/rooms/${encodeURIComponent(roomId)}/cancel`, { method: "POST" });
    els.roomStatus.textContent = "room cancelled";
    els.status.textContent = "friend room cancelled";
    els.start.textContent = "Start";
    els.start.disabled = false;
    clearRoomLinkFromUrl();
    renderRoomInvites([]);
    if (rejectWait) {
      rejectWait(new ApiError("Friend room cancelled.", {
        status: 400,
        detail: "Friend room cancelled.",
        kind: "request",
      }));
    }
  } catch (error) {
    showApiError(error, "cancel friend room");
  }
}

function renderRoomInvites(invites) {
  if (!els.roomInviteList) return;
  if (!invites.length) {
    els.roomInviteList.innerHTML = `<div class="room-invite-card"><small>No pending invites</small></div>`;
    return;
  }
  els.roomInviteList.innerHTML = invites
    .map((room) => `
      <div class="room-invite-card">
        <div>
          <strong>${escapeHtml(room.creator_username)}</strong>
          <small>friend room · ${escapeHtml(room.status)}</small>
        </div>
        <button class="primary-button" data-accept-room="${escapeHtml(room.id)}" type="button">Accept</button>
      </div>
    `)
    .join("");
  els.roomInviteList.querySelectorAll("[data-accept-room]").forEach((button) => {
    button.addEventListener("click", () => acceptRoomInvite(button.dataset.acceptRoom));
  });
}

function updateRoomModeLabel(count) {
  const button = document.querySelector('[data-mode="room"]');
  if (!button) return;
  button.textContent = count > 0 ? `Room ${count}` : "Room";
}

async function loadRoomInvites() {
  clearApiError();
  if (!localStorage.getItem(AUTH_TOKEN_KEY)) {
    openAuth("login");
    return;
  }
  try {
    els.roomStatus.textContent = "loading invites";
    const invites = await apiRequest("/api/matchmaking/rooms/invites");
    renderRoomInvites(invites);
    updateRoomModeLabel(invites.length);
    els.roomStatus.textContent = `${invites.length} pending invite${invites.length === 1 ? "" : "s"}`;
  } catch (error) {
    showApiError(error, "load friend invites");
  }
}

async function refreshRoomInviteCount() {
  if (!localStorage.getItem(AUTH_TOKEN_KEY)) {
    updateRoomModeLabel(0);
    return;
  }
  try {
    const invites = await apiRequest("/api/matchmaking/rooms/invites");
    updateRoomModeLabel(invites.length);
    if (state.mode === "room" && !state.matchRunning) {
      renderRoomInvites(invites);
      els.roomStatus.textContent = `${invites.length} pending invite${invites.length === 1 ? "" : "s"}`;
    }
  } catch (error) {
    console.warn("Room invite refresh failed.", error);
  }
}

function startRoomInvitePolling() {
  stopRoomInvitePolling();
  if (!localStorage.getItem(AUTH_TOKEN_KEY)) return;
  refreshRoomInviteCount();
  state.roomInvitePollId = setInterval(refreshRoomInviteCount, 15000);
}

function stopRoomInvitePolling() {
  if (state.roomInvitePollId) {
    clearInterval(state.roomInvitePollId);
    state.roomInvitePollId = null;
  }
}

async function handleRoomLinkFromUrl() {
  const roomId = new URL(window.location.href).searchParams.get("room");
  if (!roomId) return;
  openMode("room");
  if (!localStorage.getItem(AUTH_TOKEN_KEY)) {
    els.roomStatus.textContent = "login to open invite";
    openAuth("login");
    return;
  }

  try {
    const room = await apiRequest(`/api/matchmaking/rooms/${encodeURIComponent(roomId)}`);
    state.currentRoomId = room.id;
    if (room.status === "accepted") {
      await loadBackendMatch(room.match_id);
      connectMatchStream(room.match_id);
      els.roomStatus.textContent = "room active";
      return;
    }
    if (room.invited_user_id === state.currentUser.id && room.status === "pending") {
      renderRoomInvites([room]);
      els.roomStatus.textContent = `invite from ${room.creator_username}`;
      return;
    }
    if (room.creator_user_id === state.currentUser.id && room.status === "pending") {
      els.roomStatus.textContent = `waiting for ${room.invited_username}`;
      return;
    }
    els.roomStatus.textContent = `room ${room.status}`;
  } catch (error) {
    showApiError(error, "open friend room");
  }
}

async function acceptRoomInvite(roomId) {
  clearApiError();
  if (!roomId) return;
  clearInterval(state.timerId);
  clearInterval(state.opponentId);
  clearInterval(state.matchPollId);
  state.mode = "room";
  state.currentRoomId = roomId;
  els.start.disabled = true;
  els.status.textContent = "joining friend room";
  els.roomStatus.textContent = "accepting invite";

  try {
    const room = await apiRequest(`/api/matchmaking/rooms/${encodeURIComponent(roomId)}/accept`, { method: "POST" });
    clearRoomLinkFromUrl();
    await loadBackendMatch(room.match_id);
    connectMatchStream(room.match_id);
  } catch (error) {
    showApiError(error, "accept friend room");
    els.start.disabled = false;
    return;
  }

  state.matchRunning = true;
  state.problemIndex = 0;
  els.arenaView.classList.add("match-live");
  els.opponentName.textContent = `${state.currentOpponent.name} (${state.currentOpponent.rating})`;
  els.opponentBoardName.textContent = `${state.currentOpponent.name} // ${state.currentOpponent.rating}`;
  els.status.textContent = `friend room // ${state.currentOpponent.name}`;
  els.roomStatus.textContent = "room active";
  els.start.textContent = "Restart";
  els.start.disabled = false;
  renderProblem();
  renderTimer();
  updateRace();

  state.timerId = setInterval(async () => {
    state.secondsLeft -= 1;
    renderTimer();
    if (state.secondsLeft <= 0 && state.matchRunning) await finishBackendMatch("time expired");
  }, 1000);
}

async function loadBackendMatch(matchId) {
  const [match, tasks] = await Promise.all([
    apiRequest(`/api/matches/${matchId}`),
    apiRequest(`/api/matches/${matchId}/tasks`),
  ]);
  state.currentMatchId = match.id;
  state.currentMatchStartedAt = match.started_at;
  state.matchDuration = match.duration_seconds || 1800;
  state.secondsLeft = getMatchSecondsLeft(match.started_at, state.matchDuration);
  state.matchTasks = tasks.map(normalizeBackendTask);

  const me = match.participants.find((item) => item.user_id === state.currentUser.id);
  const opponent = match.participants.find((item) => item.user_id !== state.currentUser.id) || match.participants[0];
  state.currentOpponent = {
    name: opponent?.display_name || "Online Rival",
    rating: opponent?.rating_before || state.currentUser.rating,
  };
  state.playerProgress = me?.progress_percent || 0;
  state.opponentProgress = opponent?.progress_percent || 0;
}

function getMatchSecondsLeft(startedAt, durationSeconds) {
  if (!startedAt) return durationSeconds;
  const elapsed = Math.floor((Date.now() - new Date(startedAt).getTime()) / 1000);
  return Math.max(0, durationSeconds - elapsed);
}

function closeMatchStream() {
  if (state.matchSocket) {
    state.matchSocket.close();
    state.matchSocket = null;
  }
}

function connectMatchStream(matchId) {
  closeMatchStream();
  const token = localStorage.getItem(AUTH_TOKEN_KEY);
  if (!token) return;

  const socket = new WebSocket(`${WS_BASE}/api/matches/${matchId}/stream?token=${encodeURIComponent(token)}`);
  state.matchSocket = socket;

  socket.addEventListener("message", (event) => {
    try {
      handleMatchEvent(JSON.parse(event.data));
    } catch (error) {
      console.warn("Bad match event.", error);
    }
  });

  socket.addEventListener("close", () => {
    if (state.matchSocket === socket) state.matchSocket = null;
  });
}

function handleMatchEvent(event) {
  if (event.type === "snapshot") {
    applyParticipantSnapshot(event.participants || []);
    if (event.status === "finished") {
      handleMatchFinished({ payload: { participants: event.participants || [] } });
    }
    return;
  }

  if (event.type === "task_accepted") {
    const progress = Number(event.payload?.progress_percent || 0);
    if (event.user_id === state.currentUser.id) {
      state.playerProgress = Math.max(state.playerProgress, progress);
    } else {
      state.opponentProgress = Math.max(state.opponentProgress, progress);
    }
    updateRace();
    return;
  }

  if (event.type === "match_finished") {
    handleMatchFinished(event);
  }
}

function applyParticipantSnapshot(participants) {
  const me = participants.find((item) => item.user_id === state.currentUser.id);
  const opponent = participants.find((item) => item.user_id !== state.currentUser.id) || participants[0];
  if (me) state.playerProgress = Number(me.progress_percent || 0);
  if (opponent) {
    state.opponentProgress = Number(opponent.progress_percent || 0);
    state.currentOpponent = {
      name: opponent.display_name || state.currentOpponent?.name || "Online Rival",
      rating: opponent.rating_before || state.currentOpponent?.rating || state.currentUser.rating,
    };
    els.opponentName.textContent = `${state.currentOpponent.name} (${state.currentOpponent.rating})`;
    els.opponentBoardName.textContent = `${state.currentOpponent.name} // ${state.currentOpponent.rating}`;
  }
  updateRace();
}

async function handleMatchFinished(event) {
  const participants = event.payload?.participants || [];
  if (participants.length) applyParticipantSnapshot(participants);
  await refreshProfileAfterMatch();

  const winnerId = event.payload?.winner_user_id;
  const winnerName = event.payload?.winner_display_name;
  const message = winnerId === state.currentUser.id
    ? "match finished // you won"
    : winnerName
      ? `match finished // ${winnerName} won`
      : winnerId
        ? "match finished // rival won"
        : "match finished // draw";
  endMatch(message);
}

async function finishBackendMatch(reason = "time expired") {
  if (!state.currentMatchId) {
    endMatch(reason);
    return;
  }
  try {
    await apiRequest(`/api/matches/${state.currentMatchId}/finish`, { method: "POST" });
  } catch (error) {
    console.warn("Backend finish failed.", error);
    showApiError(error, "finish match");
  } finally {
    await refreshProfileAfterMatch();
    endMatch(reason);
  }
}

async function startMatch() {
  clearApiError();
  if (!localStorage.getItem(AUTH_TOKEN_KEY)) {
    els.status.textContent = "login required for match";
    els.summary.textContent = "auth";
    els.terminal.textContent = "> start match\nLogin is required before matchmaking.";
    setConsoleTab("terminal");
    openAuth("login");
    return;
  }

  clearInterval(state.timerId);
  clearInterval(state.opponentId);
  clearInterval(state.matchPollId);
  state.matchPollId = null;
  state.currentMatchId = null;
  state.currentRoomId = null;
  els.start.disabled = true;
  const isBotMode = state.mode === "bot";
  const isPastMode = state.mode === "past";
  const isRoomMode = state.mode === "room";
  const startContext = isRoomMode ? "start friend room" : isBotMode ? "start bot match" : isPastMode ? "start past-self match" : "start ranked queue";
  els.start.textContent = isBotMode || isPastMode ? "Loading" : isRoomMode ? "Creating" : "Searching";
  els.status.textContent = isPastMode
    ? "loading past self"
    : isBotMode
      ? "starting bot match"
      : isRoomMode
        ? "creating friend room"
        : "joining rated queue";

  try {
    let matchId;
    if (isRoomMode) {
      const room = await createFriendRoom();
      els.start.textContent = "Waiting";
      matchId = await waitForRoomMatch(room.id, room.match_id);
    } else {
      const botLevel = encodeURIComponent(state.botLevel || "auto");
      const endpoint = isPastMode
        ? "/api/matchmaking/past-self"
        : isBotMode
          ? `/api/matchmaking/bot?level=${botLevel}`
          : "/api/matchmaking/join";
      const join = await apiRequest(endpoint, { method: "POST" });
      matchId = await waitForBackendMatch(join.match_id);
    }
    await loadBackendMatch(matchId);
    connectMatchStream(matchId);
  } catch (error) {
    if (error instanceof ApiError && error.detail === "Friend room cancelled.") {
      els.status.textContent = "friend room cancelled";
      els.start.textContent = "Start";
      els.start.disabled = false;
      return;
    }
    showApiError(error, startContext);
    els.start.textContent = "Start";
    els.start.disabled = false;
    return;
  }

  state.matchRunning = true;
  state.problemIndex = 0;
  els.arenaView.classList.add("match-live");
  els.opponentName.textContent = `${state.currentOpponent.name} (${state.currentOpponent.rating})`;
  els.opponentBoardName.textContent = `${state.currentOpponent.name} // ${state.currentOpponent.rating}`;
  els.status.textContent = isBotMode
    ? `bot match // ${state.currentOpponent.name}`
    : isPastMode
      ? "past-self race // beat your ghost"
      : isRoomMode
        ? `friend room // ${state.currentOpponent.name}`
        : `matched by rating // ${state.currentUser.rating} vs ${state.currentOpponent.rating}`;
  if (isRoomMode) els.roomStatus.textContent = "room active";
  els.start.textContent = "Restart";
  els.start.disabled = false;
  renderProblem();
  renderTimer();
  updateRace();

  state.timerId = setInterval(async () => {
    state.secondsLeft -= 1;
    renderTimer();
    if (state.secondsLeft <= 0 && state.matchRunning) await finishBackendMatch("time expired");
  }, 1000);

  if (isBotMode || isPastMode) {
    state.matchPollId = setInterval(refreshAutomatedMatchState, 3500);
  }
}

async function refreshAutomatedMatchState() {
  if (!state.matchRunning || !["bot", "past"].includes(state.mode) || !state.currentMatchId) return;
  try {
    const match = await apiRequest(`/api/matches/${state.currentMatchId}`);
    applyParticipantSnapshot(match.participants || []);
    if (match.status === "finished") {
      const winner = match.winner_user_id === state.currentUser.id
        ? "match finished // you won"
        : state.opponentProgress >= 100
          ? "match finished // bot won"
          : "match finished // draw";
      await refreshProfileAfterMatch();
      endMatch(winner);
    }
  } catch (error) {
    console.warn("Automated match refresh failed.", error);
  }
}

function endMatch(message) {
  clearInterval(state.timerId);
  clearInterval(state.opponentId);
  clearInterval(state.matchPollId);
  closeMatchStream();
  state.matchPollId = null;
  state.matchRunning = false;
  if (!state.currentMatchId && message.includes("solution accepted") && state.currentOpponent) {
    state.currentUser.rating = calculateRating(state.currentUser.rating, state.currentOpponent.rating, 1);
    const saved = JSON.parse(localStorage.getItem(AUTH_USER_KEY) || "{}");
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify({ ...saved, rating: state.currentUser.rating }));
    renderRating();
    message = `${message} // rating ${state.currentUser.rating}`;
  }
  els.status.textContent = message;
  els.start.textContent = "Start";
}

async function refreshProfileAfterMatch() {
  if (!localStorage.getItem(AUTH_TOKEN_KEY)) return;
  try {
    saveUser(await fetchCurrentProfile());
  } catch (error) {
    console.warn("Profile refresh failed.", error);
  }
}

function renderTimer() {
  const minutes = String(Math.floor(state.secondsLeft / 60)).padStart(2, "0");
  const seconds = String(state.secondsLeft % 60).padStart(2, "0");
  const display = `${minutes}:${seconds}`;
  els.timer.textContent = display;
  els.problemTimerMirror.textContent = display;
}

function updateRace() {
  const taskCount = state.matchTasks.length || 1;
  els.playerRace.style.width = `${state.playerProgress}%`;
  els.opponentRace.style.width = `${state.opponentProgress}%`;
  els.playerClash.style.width = `${state.playerProgress / 2}%`;
  els.opponentClash.style.width = `${state.opponentProgress / 2}%`;
  els.playerPace.textContent = `${Math.round(state.playerProgress)}% route`;
  els.opponentPace.textContent = `${Math.round(state.opponentProgress)}% route`;
  els.playerBoardProgress.textContent = `${Math.round(state.playerProgress)}%`;
  els.opponentBoardProgress.textContent = `${Math.round(state.opponentProgress)}%`;

  state.matchTasks.forEach((_, index) => {
    const start = index * (100 / taskCount);
    const end = (index + 1) * (100 / taskCount);
    const span = end - start;
    const me = Math.max(0, Math.min(100, ((state.playerProgress - start) / span) * 100));
    const opp = Math.max(0, Math.min(100, ((state.opponentProgress - start) / span) * 100));
    const meEl = document.querySelector(`[data-me-task="${index}"]`);
    const oppEl = document.querySelector(`[data-opp-task="${index}"]`);
    if (meEl) meEl.style.width = `${me}%`;
    if (oppEl) oppEl.style.width = `${opp}%`;
  });
}

function setMode(mode) {
  state.mode = mode;
  const meta = modeMeta[mode] || modeMeta.players;
  els.opponentName.textContent = meta.opponent;
  els.opponentBoardName.textContent = meta.boardName;
  if (els.roomPanel) {
    els.roomPanel.classList.toggle("hidden", mode !== "room");
    if (mode === "room" && !els.roomInviteList.innerHTML.trim()) {
      renderRoomInvites([]);
    }
    if (mode === "room" && localStorage.getItem(AUTH_TOKEN_KEY)) {
      loadRoomInvites();
    }
  }
  document.querySelectorAll(".mode").forEach((button) => {
    button.classList.toggle("active", button.dataset.mode === mode);
  });
  endMatch("awaiting launch");
  resetArenaLobby();
}

function openMode(mode) {
  setMode(mode);
  showView("arena");
}

function nextProblem() {
  state.problemIndex = Math.min(state.problemIndex + 1, state.matchTasks.length - 1);
  renderProblem();
}

function switchTask(index) {
  if (index < 0 || index >= state.matchTasks.length) return;
  state.problemIndex = index;
  renderProblem();
  els.status.textContent = `task ${String(index + 1).padStart(2, "0")} selected`;
}

function setConsoleTab(tab) {
  els.consoleTabs.forEach((button) => {
    button.classList.toggle("active", button.dataset.consoleTab === tab);
  });
  els.terminal.classList.remove("hidden");
}

function debugStep() {
  if (!els.debugStatus || !els.debugOutput) return;
  const lines = [
    "breakpoint: вход в solve(...)",
    "watch: читаем входные данные",
    "step: обновляем локальные переменные",
    "assert: сравниваем результат с expected",
    "trace: проверь цикл и крайние случаи",
  ];
  els.debugStatus.textContent = `step ${state.debugStep + 1}`;
  const prefix = state.debugStep === 0 ? "\n" : "";
  els.debugOutput.textContent += `${prefix}${lines[state.debugStep % lines.length]}\n`;
  state.debugStep += 1;
}

function resetDebug() {
  state.debugStep = 0;
  if (!els.debugStatus || !els.debugOutput) return;
  els.debugStatus.textContent = "ready";
  els.debugOutput.textContent = "Press Step to inspect the solution path.";
}

document.querySelectorAll(".nav-item").forEach((button) => {
  button.addEventListener("click", () => showView(button.dataset.view));
});

document.querySelectorAll("[data-view-link]").forEach((link) => {
  link.addEventListener("click", (event) => {
    event.preventDefault();
    showView(link.dataset.viewLink);
  });
});

document.querySelectorAll(".mode").forEach((button) => {
  button.addEventListener("click", () => setMode(button.dataset.mode));
});

els.botLevel.addEventListener("change", () => {
  state.botLevel = els.botLevel.value;
  if (state.mode === "bot" && !state.matchRunning) {
    els.status.textContent = `bot level // ${state.botLevel}`;
  }
});

document.querySelectorAll("[data-open-mode]").forEach((button) => {
  button.addEventListener("click", () => openMode(button.dataset.openMode));
});

els.consoleTabs.forEach((button) => {
  button.addEventListener("click", () => setConsoleTab(button.dataset.consoleTab));
});

els.courseFilters.forEach((button) => {
  button.addEventListener("click", () => setCourseFilter(button.dataset.courseFilter));
});

els.quickPlay.addEventListener("click", () => openMode("players"));
els.run.addEventListener("click", runCode);
els.submit.addEventListener("click", submitCode);
els.format.addEventListener("click", formatCode);
els.solutionOpen.addEventListener("click", loadProblemSolution);
els.language.addEventListener("change", () => changeLanguage(els.language.value));
els.editor.addEventListener("input", updateCodeHighlight);
els.editor.addEventListener("scroll", updateCodeHighlight);
els.editor.addEventListener("keydown", insertEditorTab);
els.start.addEventListener("click", startMatch);
if (els.createRoom) {
  els.createRoom.addEventListener("click", () => {
    setMode("room");
    startMatch();
  });
}
if (els.copyRoomLink) {
  els.copyRoomLink.addEventListener("click", copyCurrentRoomLink);
}
if (els.cancelRoom) {
  els.cancelRoom.addEventListener("click", cancelCurrentRoom);
}
if (els.refreshRoomInvites) {
  els.refreshRoomInvites.addEventListener("click", loadRoomInvites);
}
els.themeToggle.addEventListener("click", toggleTheme);
if (els.step) els.step.addEventListener("click", debugStep);
if (els.resetDebug) els.resetDebug.addEventListener("click", resetDebug);
els.signupOpen.addEventListener("click", () => {
  if (!localStorage.getItem(AUTH_TOKEN_KEY)) openAuth("signup");
});
els.loginOpen.addEventListener("click", () => {
  if (localStorage.getItem(AUTH_TOKEN_KEY)) {
    logoutUser();
  } else {
    openAuth("login");
  }
});
els.authClose.addEventListener("click", closeAuth);
els.authModal.addEventListener("click", (event) => {
  if (event.target === els.authModal) closeAuth();
});
els.authForm.addEventListener("submit", handleAuth);
els.historyRefresh.addEventListener("click", loadMatchHistory);
if (els.tournamentRefresh) els.tournamentRefresh.addEventListener("click", loadTournaments);
if (els.tournamentCreate) els.tournamentCreate.addEventListener("click", createTournamentFromForm);
if (els.tournamentPlayers) els.tournamentPlayers.addEventListener("input", updateTournamentPlayerHint);
els.tournamentSizeButtons.forEach((button) => {
  button.addEventListener("click", () => setTournamentTargetSize(button.dataset.tournamentSize));
});
els.adminNew.addEventListener("click", resetAdminForm);
els.adminRefresh.addEventListener("click", loadAdminProblems);
els.adminSignalsRefresh.addEventListener("click", loadAdminSignals);
els.adminCalibrationRefresh.addEventListener("click", loadAdminCalibration);
els.adminProblemForm.addEventListener("submit", handleAdminProblemSubmit);
document.querySelectorAll("[data-review-status]").forEach((button) => {
  button.addEventListener("click", () => submitAdminReview(button.dataset.reviewStatus));
});
els.googleAuth.addEventListener("click", () => handleProviderAuth("google"));
els.githubAuth.addEventListener("click", () => handleProviderAuth("github"));

async function initApp() {
  await loadSeedProblems();
  await loadJudgeLanguages();
  state.matchTasks = buildRandomMatch();
  loadTheme();
  await loadUser();
  startRoomInvitePolling();
  updateTournamentPlayerHint();
  renderProblem();
  renderTimer();
  resetArenaLobby();
  await handleRoomLinkFromUrl();
}

initApp();
