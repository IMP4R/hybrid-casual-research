# Yarn Loop: Knit Puzzle (Combo Games) — гайд-сайты с уровнями

Дата проверки: 2026-08-28. Метод: прямые curl-запросы + visit_page (Google/DDG/Mojeek/Ecosia отдавали CAPTCHA или 403, Bing — нерелевантный шум; вывод построен на прямом парсинге HTML).

## 1. Найденный сайт (один, но он закрывает весь паттерн)

### yarnlooplevel.com — SEO-ферма уровней, ровно по гипотезе `<game>level.com`

- **Титул главной:** «Yarn Loop Answers, Walkthrough & Solutions Guide»; мета: «answers, spoiler-free tips and full solutions for Yarn Loop Levels 1-800».
- **Структура URL:** `/level/{N}/` для N = 1…800 (проверены 1, 5, 50, 120, 250, 300, 500, 650, 800 — все HTTP 200). Индекс `/levels/` с «50-level range browser». Служебные: `/blog/`, `/blog/how-to-solve-hard-yarn-loop-levels/`, `/update-log/`, `/about/`, `/download/`, `/contact/`, `/disclaimer/`, `/privacy/`.
- **Парсится ли curl без JS: ДА, полностью.** Статический генератор Astro: главная ~158 KB, уровневая страница 43–46 KB чистого HTML, весь текст решения — прямо в разметке. Видео — только lazy-эмбед (lite-youtube, iframe собирается из `videoId` при клике), поэтому curl-текст не теряет ничего. `sitemap.xml` — 404.
- **Принадлежность:** сам сайт пишет «part of the **LevelSolve network**» (levelsolve.com) — та же ферма держит 57+ однотипных сайтов `/game/level/N/` (yarn-fever, loop-sort, loop-master, wool-crush, brain-out, cookingdom…). Авторы — безликий «YarnLoopLevel.com Editorial Team».
- **Счётчики/соцдоказательства:** нет просмотров, комментариев, рейтингов. На уровневых нет дат; на блоге даты есть (Apr 20/27, 2026).

### Update Log (полезно для понимания жизненного цикла фермы)

Покрытие расширялось волнами: 400 → 500 → 600 → 687 → 705 → 750 → 800 уровней. Формулировки: «matching the latest available playlist coverage», «705-item Yarn Loop walkthrough playlist» — **ферма собрана под готовый YouTube-плейлист прохождений**, 705 из 800 страниц имеют привязанное видео. Это маркер того, что игра свежая и контент-кап (800) догоняет актуальный контент игры.

## 2. Что содержат уровневые страницы (проверены 1 / 250 / 800 + 6 дополнительных)

Типовой шаблон страницы `/level/N/`:

1. **H1** «Yarn Loop Level N Walkthrough» + бейдж сложности (easy → medium ~120 → hard 250–500 → expert 650 → «super hard» 800).
2. **Вводный абзац-резюме** (2–3 предложения).
3. **«Verified Board Notes»** — 5 пунктов: Initial Layout Geometry, Goal/Target Area, Opening Moves, **Danger Zone с таймкодами** (напр. «04:20–05:10»), Unique Mechanics. Похоже на расшифровку видео-прохождения по таймкодам.
4. **«Quick Tips for Level N (spoiler-free)»** — 3 буллета.
5. **«How to Solve Yarn Loop Level N — Full Solution»** — ровно 5 шагов текстом (не пошаговые ходы, а порядок «что открывать первым»).
6. **«Common Mistakes to Avoid»** — 3 буллета.
7. **FAQ** — 3–4 Q&A (дублируют текст выше — это JSON-LD FAQPage для rich snippets).
8. **Видео-эмбед**: 705 из 800 страниц. На level 800 — «Video walkthrough coming soon. This guide is text-first for now».

**Схема.org:** каждая страница отдаёт JSON-LD `BreadcrumbList` + `VideoObject` + `FAQPage` — стандартный SEO-набор фермы под Google rich results.

**Важно про качество видео:** метаданные фермы частично склеивают Yarn Loop с похожей игрой. Проверка oEmbed: level 1/5/50 — реальные «Yarn Loop Level N» (канал Android Games), level 120 — «Yarn Loop Knit Puzzle - level 120» (Chum Game Time), но level 250/300/500 — видео **«Yarn Flow» Level N Walkthrough** (Rock Gaming Channel) — т.е. соседняя игра подшита под страницы Yarn Loop. Текстовые «Board Notes» тоже местами описывают «Yarn Flow»-стиль досок. Вывод: тексты и видео сгенерированы/подобраны автоматически, доверять деталям досок можно только как «правдоподобному шаблону», не как дословному прохождению.

## 3. Факты о механиках из текстов сайта

1. **Сортировка снаружи-внутрь по цветам:** «the exposed outer color must go first» — верхний открытый слой цвета разгребается первым, нижний цвет становится доступен, только когда внешний край «открывается» (level 1: жёлтая половина — «shell», синяя под ней).
2. **Лоток катушек с лимитом:** катушки (spools) поступают в tray, переполнение лотка — главный риск-тайминг («the tray briefly climbs toward the limit» на 00:08–00:12 уровня 1) — механика давления очереди, как в sort-играх.
3. **Поздние уровни — «сцены», а не абстрактные доски:** level 250 описан как комната (книжная полка, луна-светильник, обои, растение), все элементы «shrinks away»; длинные тонкие элементы (полки) и мелкие «крошки» (книжные блоки) живут дольше крупных объектов — финал уровня это зачистка крошки.
4. **Chain clears и choke points:** сильный ход обязан открывать следующий («If it closes the next route, it is bait»); есть точки, где «two colors cross and block each other» — пересечения маршрутов цветов как основной источник струка.
5. **Hard-уровни — dependency puzzles:** цвет ранжируется по числу выходов («the urgent color is the one with the fewest exits, not always the one closest to clearing»); свободное место — ресурс («treat open space as a resource»); бустеры тратить только после определения бутылочного горлышка.
6. **Длительность и рост:** таймкоды прохождений — от 5 минут (level 250, видео PT5M29S) до ~8,5 минут (level 800, «07:39–08:36»); сложность растёт ступенями easy → medium → hard → expert → super hard к капу 800.

## 4. Другие гайд-сайты

Не найдены. Прямые домены `yarnloopguide.com`, `yarnlooplevels.com`, `yarnloopanswers.com`, `yarnloopsolution.com`, `yarnloopwalkthrough.com`, `yarnloop.io`, `yarnloopguide.io`, `yarnloopgame.com`, `playyarnloop.com` — не существуют (DNS/curl 000). Поисковики в момент проверки были недоступны для автоматики (Google и DuckDuckGo — CAPTCHA, Ecosia и Mojeek — 403, Bing — нерелевантный мусор), поэтому исключить существование второй мелкой фермы нельзя, но yarnlooplevel.com — единственный обнаруженный и фактически монопольный гайд-ресурс по игре. В сети LevelSolve у самой игры отдельного сайта на материнском домене нет (там yarn-fever и другие yarn-игры).

## 5. Вывод для конкурентного анализа

- Игра **уже не «слишком свежа» для SEO-ферм**: монополист-ферма успела закрыть все 800 уровней и гонится за капом контента волнами по 50–100 уровней. Это значит: объём «гайдового спроса» уже монетизируется третьей стороной, и окно «занять выдачу собственным контентом» (официальные решения, UGC) частично упущено, но качество конкурента низкое (генерённый текст, чужие видео Yarn Flow) — выбить его из выдачи реалистично.
- Для парсинга/дата-сборки сайт идеален: статики Astro, всё в HTML, предсказуемый URL `/level/{N}/` — 800 страниц собираются простым curl-циклом без JS.
