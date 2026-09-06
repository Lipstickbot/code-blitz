export type Difficulty = "easy" | "medium" | "hard";

export interface Problem {
  id: string;
  title: string;
  difficulty: Difficulty;
  tags: string[];
  solvedByMe: boolean;
  acceptanceRate: number;
  description: string;
  examples: { input: string; output: string }[];
}

export const problems: Problem[] = [
  {
    id: "two-sum",
    title: "Two Sum",
    difficulty: "easy",
    tags: ["массивы", "хеш-таблица"],
    solvedByMe: true,
    acceptanceRate: 78,
    description:
      "Дан массив целых чисел nums и число target. Верните индексы двух чисел, сумма которых равна target.",
    examples: [{ input: "nums = [2,7,11,15], target = 9", output: "[0,1]" }],
  },
  {
    id: "valid-parentheses",
    title: "Valid Parentheses",
    difficulty: "easy",
    tags: ["стек", "строки"],
    solvedByMe: false,
    acceptanceRate: 71,
    description:
      "Дана строка из скобок '(', ')', '{', '}', '[' и ']'. Определите, является ли последовательность корректной.",
    examples: [{ input: 's = "()[]{}"', output: "true" }],
  },
  {
    id: "binary-search",
    title: "Binary Search",
    difficulty: "easy",
    tags: ["бинарный поиск", "массивы"],
    solvedByMe: false,
    acceptanceRate: 82,
    description:
      "Дан отсортированный массив nums и число target. Верните индекс target или -1, если числа нет в массиве.",
    examples: [{ input: "nums = [-1,0,3,5,9,12], target = 9", output: "4" }],
  },
  {
    id: "merge-sorted-array",
    title: "Merge Sorted Array",
    difficulty: "easy",
    tags: ["массивы", "два указателя"],
    solvedByMe: false,
    acceptanceRate: 75,
    description:
      "Даны два отсортированных массива. Объедините их в один отсортированный массив без использования лишней сложной логики.",
    examples: [{ input: "nums1 = [1,2,3], nums2 = [2,5,6]", output: "[1,2,2,3,5,6]" }],
  },
  {
    id: "best-time-stock",
    title: "Best Time to Buy and Sell Stock",
    difficulty: "easy",
    tags: ["массивы", "жадный алгоритм"],
    solvedByMe: false,
    acceptanceRate: 69,
    description:
      "Дан массив цен акций по дням. Найдите максимальную прибыль от одной покупки и одной продажи.",
    examples: [{ input: "prices = [7,1,5,3,6,4]", output: "5" }],
  },
  {
    id: "palindrome-number",
    title: "Palindrome Number",
    difficulty: "easy",
    tags: ["математика"],
    solvedByMe: false,
    acceptanceRate: 62,
    description:
      "Дано целое число x. Определите, читается ли оно одинаково слева направо и справа налево.",
    examples: [{ input: "x = 121", output: "true" }],
  },
  {
    id: "maximum-subarray",
    title: "Maximum Subarray",
    difficulty: "easy",
    tags: ["динамика", "массивы"],
    solvedByMe: false,
    acceptanceRate: 66,
    description:
      "Найдите подмассив с максимальной суммой и верните эту сумму.",
    examples: [{ input: "nums = [-2,1,-3,4,-1,2,1,-5,4]", output: "6" }],
  },
  {
    id: "flood-fill",
    title: "Flood Fill",
    difficulty: "easy",
    tags: ["графы", "dfs", "bfs"],
    solvedByMe: false,
    acceptanceRate: 73,
    description:
      "Дано изображение как матрица цветов. Перекрасьте связную область, начиная с указанной клетки.",
    examples: [{ input: "image = [[1,1,1],[1,1,0],[1,0,1]], sr = 1, sc = 1", output: "область перекрашена" }],
  },
  {
    id: "climbing-stairs",
    title: "Climbing Stairs",
    difficulty: "easy",
    tags: ["динамика", "математика"],
    solvedByMe: false,
    acceptanceRate: 68,
    description:
      "Есть лестница из n ступенек. За ход можно подняться на 1 или 2 ступеньки. Найдите число способов добраться до верха.",
    examples: [{ input: "n = 3", output: "3" }],
  },
  {
    id: "contains-duplicate",
    title: "Contains Duplicate",
    difficulty: "easy",
    tags: ["массивы", "множество"],
    solvedByMe: false,
    acceptanceRate: 80,
    description:
      "Определите, есть ли в массиве хотя бы одно повторяющееся число.",
    examples: [{ input: "nums = [1,2,3,1]", output: "true" }],
  },
  {
    id: "longest-substring",
    title: "Longest Substring Without Repeating Characters",
    difficulty: "medium",
    tags: ["строки", "скользящее окно", "хеш-таблица"],
    solvedByMe: false,
    acceptanceRate: 54,
    description:
      "Дана строка s. Найдите длину самой длинной подстроки без повторяющихся символов.",
    examples: [{ input: 's = "abcabcbb"', output: "3" }],
  },
  {
    id: "course-schedule",
    title: "Course Schedule",
    difficulty: "medium",
    tags: ["графы", "топологическая сортировка"],
    solvedByMe: false,
    acceptanceRate: 47,
    description:
      "Дано количество курсов и список зависимостей. Определите, можно ли пройти все курсы.",
    examples: [{ input: "numCourses = 2, prerequisites = [[1,0]]", output: "true" }],
  },
  {
    id: "three-sum",
    title: "3Sum",
    difficulty: "medium",
    tags: ["массивы", "два указателя", "сортировка"],
    solvedByMe: false,
    acceptanceRate: 38,
    description:
      "Найдите все уникальные тройки чисел в массиве, сумма которых равна нулю.",
    examples: [{ input: "nums = [-1,0,1,2,-1,-4]", output: "[[-1,-1,2],[-1,0,1]]" }],
  },
  {
    id: "group-anagrams",
    title: "Group Anagrams",
    difficulty: "medium",
    tags: ["строки", "хеш-таблица", "сортировка"],
    solvedByMe: false,
    acceptanceRate: 61,
    description:
      "Сгруппируйте слова, которые являются анаграммами друг друга.",
    examples: [{ input: 'strs = ["eat","tea","tan","ate","nat","bat"]', output: "[[eat,tea,ate],[tan,nat],[bat]]" }],
  },
  {
    id: "product-except-self",
    title: "Product of Array Except Self",
    difficulty: "medium",
    tags: ["массивы", "префиксы"],
    solvedByMe: false,
    acceptanceRate: 64,
    description:
      "Для каждого индекса верните произведение всех элементов массива, кроме текущего, без деления.",
    examples: [{ input: "nums = [1,2,3,4]", output: "[24,12,8,6]" }],
  },
  {
    id: "number-of-islands",
    title: "Number of Islands",
    difficulty: "medium",
    tags: ["графы", "dfs", "матрица"],
    solvedByMe: false,
    acceptanceRate: 55,
    description:
      "Дана матрица из воды и земли. Посчитайте количество островов — связных областей земли.",
    examples: [{ input: "grid = [[1,1,0],[0,1,0],[1,0,1]]", output: "3" }],
  },
  {
    id: "rotting-oranges",
    title: "Rotting Oranges",
    difficulty: "medium",
    tags: ["bfs", "матрица", "очередь"],
    solvedByMe: false,
    acceptanceRate: 52,
    description:
      "В матрице есть свежие и гнилые апельсины. Найдите, сколько минут нужно, чтобы все свежие стали гнилыми.",
    examples: [{ input: "grid = [[2,1,1],[1,1,0],[0,1,1]]", output: "4" }],
  },
  {
    id: "subarray-sum-k",
    title: "Subarray Sum Equals K",
    difficulty: "medium",
    tags: ["префиксные суммы", "хеш-таблица"],
    solvedByMe: false,
    acceptanceRate: 45,
    description:
      "Посчитайте количество подмассивов, сумма которых равна k.",
    examples: [{ input: "nums = [1,1,1], k = 2", output: "2" }],
  },
  {
    id: "kth-largest",
    title: "Kth Largest Element",
    difficulty: "medium",
    tags: ["куча", "сортировка", "quickselect"],
    solvedByMe: false,
    acceptanceRate: 59,
    description:
      "Найдите k-й по величине элемент массива.",
    examples: [{ input: "nums = [3,2,1,5,6,4], k = 2", output: "5" }],
  },
  {
    id: "daily-temperatures",
    title: "Daily Temperatures",
    difficulty: "medium",
    tags: ["стек", "монотонный стек"],
    solvedByMe: false,
    acceptanceRate: 63,
    description:
      "Для каждого дня найдите, через сколько дней будет более высокая температура.",
    examples: [{ input: "temperatures = [73,74,75,71,69,72,76,73]", output: "[1,1,4,2,1,1,0,0]" }],
  },
  {
    id: "coin-change",
    title: "Coin Change",
    difficulty: "medium",
    tags: ["динамика", "рюкзак"],
    solvedByMe: false,
    acceptanceRate: 43,
    description:
      "Даны монеты разных номиналов и сумма. Найдите минимальное количество монет для набора суммы.",
    examples: [{ input: "coins = [1,2,5], amount = 11", output: "3" }],
  },
  {
    id: "decode-ways",
    title: "Decode Ways",
    difficulty: "medium",
    tags: ["динамика", "строки"],
    solvedByMe: false,
    acceptanceRate: 41,
    description:
      "Строка цифр кодирует буквы. Посчитайте количество способов расшифровать строку.",
    examples: [{ input: 's = "226"', output: "3" }],
  },
  {
    id: "word-search",
    title: "Word Search",
    difficulty: "medium",
    tags: ["backtracking", "матрица"],
    solvedByMe: false,
    acceptanceRate: 44,
    description:
      "Дана сетка символов и слово. Определите, можно ли составить слово из соседних клеток.",
    examples: [{ input: 'board = [[A,B,C,E],[S,F,C,S],[A,D,E,E]], word = "ABCCED"', output: "true" }],
  },
  {
    id: "lowest-common-ancestor",
    title: "Lowest Common Ancestor",
    difficulty: "medium",
    tags: ["деревья", "dfs"],
    solvedByMe: false,
    acceptanceRate: 58,
    description:
      "В бинарном дереве найдите наименьшего общего предка двух заданных узлов.",
    examples: [{ input: "root = [3,5,1,6,2,0,8], p = 5, q = 1", output: "3" }],
  },
  {
    id: "median-two-arrays",
    title: "Median of Two Sorted Arrays",
    difficulty: "hard",
    tags: ["бинарный поиск", "разделяй и властвуй"],
    solvedByMe: false,
    acceptanceRate: 35,
    description:
      "Даны два отсортированных массива. Найдите медиану объединённого массива за O(log(m+n)).",
    examples: [{ input: "nums1 = [1,3], nums2 = [2]", output: "2.00000" }],
  },
  {
    id: "trapping-rain-water",
    title: "Trapping Rain Water",
    difficulty: "hard",
    tags: ["два указателя", "стек", "массивы"],
    solvedByMe: false,
    acceptanceRate: 48,
    description:
      "Дан массив высот. Посчитайте, сколько воды может задержаться после дождя.",
    examples: [{ input: "height = [0,1,0,2,1,0,1,3,2,1,2,1]", output: "6" }],
  },
  {
    id: "largest-rectangle",
    title: "Largest Rectangle in Histogram",
    difficulty: "hard",
    tags: ["стек", "монотонный стек"],
    solvedByMe: false,
    acceptanceRate: 39,
    description:
      "Дан массив высот столбцов гистограммы. Найдите площадь самого большого прямоугольника.",
    examples: [{ input: "heights = [2,1,5,6,2,3]", output: "10" }],
  },
  {
    id: "word-ladder",
    title: "Word Ladder",
    difficulty: "hard",
    tags: ["bfs", "графы", "строки"],
    solvedByMe: false,
    acceptanceRate: 36,
    description:
      "Найдите длину кратчайшей цепочки преобразований от beginWord к endWord, меняя по одной букве.",
    examples: [{ input: 'begin = "hit", end = "cog", words = [hot,dot,dog,lot,log,cog]', output: "5" }],
  },
  {
    id: "serialize-tree",
    title: "Serialize and Deserialize Binary Tree",
    difficulty: "hard",
    tags: ["деревья", "дизайн", "dfs"],
    solvedByMe: false,
    acceptanceRate: 44,
    description:
      "Реализуйте кодирование бинарного дерева в строку и восстановление дерева из этой строки.",
    examples: [{ input: "root = [1,2,3,null,null,4,5]", output: "та же структура дерева" }],
  },
  {
    id: "minimum-window-substring",
    title: "Minimum Window Substring",
    difficulty: "hard",
    tags: ["строки", "скользящее окно", "хеш-таблица"],
    solvedByMe: false,
    acceptanceRate: 37,
    description:
      "Найдите минимальную подстроку s, которая содержит все символы строки t.",
    examples: [{ input: 's = "ADOBECODEBANC", t = "ABC"', output: '"BANC"' }],
  },
  {
    id: "regular-expression-matching",
    title: "Regular Expression Matching",
    difficulty: "hard",
    tags: ["динамика", "строки"],
    solvedByMe: false,
    acceptanceRate: 29,
    description:
      "Реализуйте сопоставление строки с шаблоном, где '.' означает любой символ, а '*' — повторение предыдущего элемента.",
    examples: [{ input: 's = "aab", p = "c*a*b"', output: "true" }],
  },
  {
    id: "valid-anagram",
    title: "Valid Anagram",
    difficulty: "easy",
    tags: ["строки", "хеш-таблица", "сортировка"],
    solvedByMe: false,
    acceptanceRate: 76,
    description:
      "Даны две строки s и t. Определите, являются ли они анаграммами: содержат ли одинаковые символы с одинаковой частотой.",
    examples: [{ input: 's = "anagram", t = "nagaram"', output: "true" }],
  },
  {
    id: "reverse-linked-list",
    title: "Reverse Linked List",
    difficulty: "easy",
    tags: ["связный список", "итерация", "рекурсия"],
    solvedByMe: false,
    acceptanceRate: 79,
    description:
      "Разверните связный список. В этой платформе список передаётся как массив значений, верните массив в обратном порядке.",
    examples: [{ input: "head = [1,2,3,4,5]", output: "[5,4,3,2,1]" }],
  },
  {
    id: "majority-element",
    title: "Majority Element",
    difficulty: "easy",
    tags: ["массивы", "подсчёт", "Boyer-Moore"],
    solvedByMe: false,
    acceptanceRate: 74,
    description:
      "Найдите элемент, который встречается больше половины раз в массиве.",
    examples: [{ input: "nums = [3,2,3]", output: "3" }],
  },
  {
    id: "move-zeroes",
    title: "Move Zeroes",
    difficulty: "easy",
    tags: ["массивы", "два указателя"],
    solvedByMe: false,
    acceptanceRate: 72,
    description:
      "Переместите все нули в конец массива, сохранив порядок остальных элементов. Верните новый массив.",
    examples: [{ input: "nums = [0,1,0,3,12]", output: "[1,3,12,0,0]" }],
  },
  {
    id: "first-unique-character",
    title: "First Unique Character in a String",
    difficulty: "easy",
    tags: ["строки", "очередь", "хеш-таблица"],
    solvedByMe: false,
    acceptanceRate: 62,
    description:
      "Верните индекс первого символа, который встречается в строке ровно один раз. Если такого нет — верните -1.",
    examples: [{ input: 's = "leetcode"', output: "0" }],
  },
  {
    id: "roman-to-integer",
    title: "Roman to Integer",
    difficulty: "easy",
    tags: ["строки", "математика"],
    solvedByMe: false,
    acceptanceRate: 70,
    description:
      "Преобразуйте римское число в целое, учитывая случаи IV, IX, XL, XC, CD и CM.",
    examples: [{ input: 's = "MCMXCIV"', output: "1994" }],
  },
  {
    id: "sqrtx",
    title: "Sqrt(x)",
    difficulty: "easy",
    tags: ["бинарный поиск", "математика"],
    solvedByMe: false,
    acceptanceRate: 58,
    description:
      "Верните целую часть квадратного корня числа x без использования встроенной функции sqrt.",
    examples: [{ input: "x = 8", output: "2" }],
  },
  {
    id: "plus-one",
    title: "Plus One",
    difficulty: "easy",
    tags: ["массивы", "математика"],
    solvedByMe: false,
    acceptanceRate: 77,
    description:
      "Дано число как массив цифр. Прибавьте к нему единицу и верните новый массив цифр.",
    examples: [{ input: "digits = [9,9,9]", output: "[1,0,0,0]" }],
  },
  {
    id: "search-insert-position",
    title: "Search Insert Position",
    difficulty: "easy",
    tags: ["бинарный поиск", "массивы"],
    solvedByMe: false,
    acceptanceRate: 73,
    description:
      "Дан отсортированный массив и target. Верните индекс target или позицию, куда его нужно вставить.",
    examples: [{ input: "nums = [1,3,5,6], target = 2", output: "1" }],
  },
  {
    id: "remove-duplicates-sorted-array",
    title: "Remove Duplicates from Sorted Array",
    difficulty: "easy",
    tags: ["массивы", "два указателя"],
    solvedByMe: false,
    acceptanceRate: 66,
    description:
      "Удалите дубликаты из отсортированного массива. В этой платформе верните новый массив уникальных значений.",
    examples: [{ input: "nums = [0,0,1,1,1,2,2,3,3,4]", output: "[0,1,2,3,4]" }],
  },
  {
    id: "missing-number",
    title: "Missing Number",
    difficulty: "easy",
    tags: ["массивы", "математика", "xor"],
    solvedByMe: false,
    acceptanceRate: 69,
    description:
      "В массиве есть числа от 0 до n, но одно число пропущено. Найдите его.",
    examples: [{ input: "nums = [3,0,1]", output: "2" }],
  },
  {
    id: "single-number",
    title: "Single Number",
    difficulty: "easy",
    tags: ["массивы", "битовые операции"],
    solvedByMe: false,
    acceptanceRate: 81,
    description:
      "Каждое число встречается дважды, кроме одного. Найдите число, которое встречается один раз.",
    examples: [{ input: "nums = [4,1,2,1,2]", output: "4" }],
  },
];

export interface LeaderboardEntry {
  rank: number;
  username: string;
  rating: number;
  solved: number;
  streak: number;
}

export const globalLeaderboard: LeaderboardEntry[] = [
  { rank: 1, username: "nikolay_fast", rating: 2841, solved: 612, streak: 41 },
  { rank: 2, username: "ayana.dev", rating: 2790, solved: 588, streak: 12 },
  { rank: 3, username: "quantum_qi", rating: 2705, solved: 601, streak: 7 },
  { rank: 4, username: "dark_horse", rating: 2650, solved: 540, streak: 23 },
  { rank: 5, username: "you", rating: 1980, solved: 142, streak: 5 },
];

export const blitzLeaderboard: LeaderboardEntry[] = [
  { rank: 1, username: "nikolay_fast", rating: 3120, solved: 9, streak: 41 },
  { rank: 2, username: "speedforce", rating: 2988, solved: 8, streak: 3 },
  { rank: 3, username: "ayana.dev", rating: 2870, solved: 8, streak: 12 },
  { rank: 4, username: "you", rating: 2210, solved: 5, streak: 5 },
];
