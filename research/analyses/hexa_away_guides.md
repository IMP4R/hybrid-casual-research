# Hexa Away (Goodroid) — гайд-сайты с уровнями

Дата поиска: 2026-08-28. Игра: **Hexa Away** (Goodroid, Google Play `jp.co.goodroid.hyper.hexaaway`). Контекст: ~$19M.

> Методологическая заметка: Google и DuckDuckGo отдали CAPTCHA, встроенный web_search без ключа, локальный SearXNG лежал (fetch failed), Bing отдаёт canned-выдачу (одинаковые «About 32,500 results» на любые запросы, операторы `site:`/кавычки игнорируются), Brave 429, Ecosia/Mojeek/Yandex 403/captcha. Рабочие каналы: **YouTube-поиск через браузер** (полностью открыт), **curl к sitemap и страницам** (Google Play, hexaawaylevel.com). Прямая прописка доменов-паттернов дала единственный живой сайт.

## 1. Найденные сайты

### ✅ hexaawaylevel.com — единственный уровневой гайд-сайт (авто-генерённый фан-сайт)
- Заголовок: «Hexa Away Level - Complete Walkthrough & Solutions Guide», мета обещает «all 650 levels» (цифра устарела, в sitemap уже 1040).
- Стек: Next.js на **Vercel**; самописная пометка «Independent Fan Guide»; бейдж `goodaitools.com` — признак AI-генерации контент-фермы.
- **Структура URL** (регулярная):
  - уровневые: `/en/level/{N}`, N = 1…1040 (1040 шт.) — из `sitemap-en.xml` (lastmod 2025-12-15);
  - полное испанское зеркало `/es/level/{N}` (`sitemap-es.xml`, тот же lastmod);
  - служебные: `/en/levels` (индекс), `/en/download`, `/en/privacy`, `/en/terms`.
- **curl: парсится полностью.** HTTP 200, статический HTML 77–107 KB, весь текст и YouTube-ID лежат в HTML — JS не нужен. `robots.txt` открыт, sitemap доступен.
- Каверзность: `/en/level/{N}` отвечает **200 на любой N** (проверено 9999) — за пределами sitemap страницы генерятся на лету с мусорным видео (см. §2). Валидность определять по sitemap, не по коду ответа.
- Индекс `/en/levels` в статике отдаёт только 8 ссылок (дальше клиентский рендер) — для обхода использовать sitemap, не индекс.

### ❌ Прямые паттерны: не существуют / не гайды
- `hexaawaylevel.com` — существует (редирект на www, Vercel) — единственный «попавший» паттерн.
- `hexaawayguide.com`, `hexaawayanswers.com`, `hexaawaylevels.com`, `hexaawayguide.net/.org`, `hexaawayanswers.net/.org`, `hexa-away-levels.com`, `hexaawaywalkthrough.com`, `hexaawayhelp.com`, `hexaawaysolutions.com` — **DNS не резолвится**.
- `hexaaway.net`, `hexa-away.com` — существуют, но это **играбельные веб-версии/порталы** («Play Hexa Away free online… unblocked»), уровневых гайдов нет. hexa-away.com — WordPress+Rank Math, в post-sitemap всего 4 игровых страницы, гайдов нет.

### ❌ Гайд-фермы: Hexa Away не покрыт
- `gameanswer.net` — больше не гайд-ферма (тайтл «Michael», персональный сайт); `/hexa-away-level-500/` → 404, поиск `?s=hexa+away` → 0 результатов.
- `levelwinner.com` — `/tag/hexa-away/` → 301 в никуда, `?s=hexa+away` отдаёт главную без единого материала по игре. Статей нет.
- `walkthroughs.net`, `touchtapplay.com` — Cloudflare «Just a moment» (403 и curl, и браузер).
- Reddit — по сути пусто: pullpush-поиск «hexa away» даёт 2 постера-ложняка (r/iems «blow the Hexa away», r/ToonBlast упоминание в комментарии). Комьюнити игры живёт в YouTube-комментариях и Google Play, не на форумах.

### 📺 YouTube — фактический гайд-хаб игры
- **Nova’s Puzzle Den** (`@NovasPuzzleDen`): плейлист «**Hexa Away Updated 2/2026**» — `https://www.youtube.com/playlist?list=PLTyE_QPLlSz9AeWnbWTfi_dIJnx0Oo1F_`, **121 видео** (по состоянию на 2026-08-28), батчи по 10 уровней, покрытие **до уровня 1210**, обновлялся за сутки до поиска. Тот же канал той же схемой ведёт «Wood Away Block Puzzles» — родственную игру Goodroid.
- **puzzle gamer** (`@puzzlegameplayer`): батчи по 10, 4K, **таймкоды в описании** («00:00 level 1051 … 03:50 level 1056»), версия игры в заголовках («hexa away [v3.5.0]»).
- **Go Answer** (`@goanswer8202`): **поуровневые** короткие ролики (~1:04) «🧠 Hexa Away Level N Walkthrough» — именно эти видео встроены в hexaawaylevel.com; плотное покрытие ранних/средних уровней (с дырками: на 110 видео нет, есть 108/112/113).
- **Solve State** (`@SolveState`): поуровневые (156, 476…), **Bamsi Gaming 2.0**: батчи (501–505…), плюс короткие ролики уровнями («HexaAway Level 561 *SUPER HARD LEVEL*»).
- YouTube search парсится curl'ом: `ytInitialData` присутствует в HTML.

## 2. Что на уровневых страницах (проверено 6: /en/level/6, 110, 193, 500, 1039, 1056 + проба 9999)

| Аспект | Что есть |
|---|---|
| **Текст решения (порядок тапов)** | ❌ **Нет нигде.** Только шаблонные вставки-ротаторы: 1039 — «presents risk-reward scenarios», 500 — «displays a star-burst formation radiating from a central point», 1056 — «implements chain reaction mechanics»; общий совет «Target isolated groups before tackling interconnected sections» и boilerplate «Tap to remove blocks along your planned sequence». Настоящего порядка тапов не существует в текстовом виде. |
| **Видео** | ✅ Да, YouTube-embed. Для уровней из sitemap (1–1040) видео **соответствует игре** (проверено oEmbed): 6 → «🧠 Hexa Away Level 6 Walkthrough \| Go Answer» (точный), 193 → точный 193 + соседи 191/197, 500 → точный 500 + 499/498/497/496 + батч 501–505 (Bamsi), 1039 → батч «hexa away level 1031…1040 \| puzzle gamer». Для 110 — только соседи 108/112/113 (дыра Go Answer). Для 1056 (вне sitemap) — **чужая игра** («Pixel Flow level 1,2,3,4,5 Walkthrough»): генератор подставляет рандом. |
| **Метаданные уровня** | Level Number, Difficulty (easy/medium/hard), Estimated Time («14-18 minutes»), Category («Levels 1001 - 1050», диапазоны по 50). |
| «Статистика игроков» | Completion Rate 55–60%, Average Attempts 2.5–7.8, Rating 4.0–4.9, Popularity Rank — **генерённые числа** (один шаблон на всех), реальными данными не считать. |
| **Навигация** | prev/next, Nearby Levels (окно ±10), «Popular Levels: 6 110 193 205 275 282 359» (жёсткий список, одинаков на всех страницах — вероятные «болячки» по версии генератора). |
| Языки | en + es, полные зеркала. |

**Вывод по парсингу**: сайт годится как **индекс уровень→видео** (sitemap 1040 URL + YouTube-ID из HTML + oEmbed для названия ролика/канала). Текст и «статистику» не использовать. Валидность видео сверять названием через oEmbed — за пределами уровня 1040 сайт врёт.

## 3. Факты о механиках из текстов (порядок решений!)

1. **Ядро механики — направленный тап** (официальное описание, Google Play, curl 200): «Tap the hexagon tile to move it and clear the screen. However, the hexagon tile only moves in one direction… Plan your strategy by imagining where the hex will move on the screen». Т.е. гексагон уходит по собственному направлению; порядок тапов критичен — чужой тайл на пути = блокировка.
2. **Прогрессия**: «As the game progresses, the number of hexagon tile increases and various obstacles are created» — рост числа тайлов + новые препятствия (Google Play).
3. **Лимит ходов + фейл по клику**: «limited moves means if you even accidentally touch the wrong piece, you can lose a round» — раунд можно проиграть одним неверным тапом, а не только исчерпанием лимита (Google Play отзыв).
4. **Экстра-ходы за рекламу, свежий нерф**: раньше «watching an ad gave you 5 extra moves. Now, it only gives you 1 extra move», плюс «they've added more difficulties» и «increased the prices of their goodies by over 30%» (Google Play отзывы; патч на момент поиска уже в силе).
5. **Стена под бустеры в середине**: «After you level up, some of the puzzles require using the award tools to win» (Google Play отзыв) — часть уровней среднего этапа формально непроходима без наградных бустеров.
6. **Темп ранних уровней**: «I played to level 100. Levels can be completed in 20-30 seconds» — первая сотня = мгновенные доски, монетизация рекламой с первого уровня («ad after every single level», «3-screen ads»).
7. **Кривая сложности по сэмплам hexaawaylevel** (сгенерённая, но структурированная): 5/50 → easy (2.5–3.0 tries), 150/300 → medium, 500–1040 → hard (5.0–7.0 tries). Словарь «формаций» ротатора: star-burst (500), chain reaction (1056), risk-reward (1039) — доверие низкое, но лексика совпадает с жанром tap-away.
8. **Версии**: заголовки видео puzzle gamer содержат «[v3.5.0]» — решебная версия игры на момент съёмки; Nova помечает плейлист «Updated 2/2026» и в описании признаёт: «I needed an extra move on level 534 — what did I miss?» — даже съёмщик прошел 534 с доп. ходом.
9. **Семейное родство**: та же аудитория/каналы (Nova’s Puzzle Den) тем же форматом проходят **Wood Away Block Puzzles** — Hexa Away вписывается в линейку Goodroid «tap-away» (Wood Away → Hexa Away), формулы дизайна переиспользуются.

## 4. Стены сложности по отзывам (Google Play; Reddit пуст)

- **Стена 1 (монетизационная, вся игра)**: реклама после каждого уровня, 3 экрана подряд; жалобы «spending at least as much time on ads as I am playing», «ads after every level, unplayable».
- **Стена 2 (ранняя сотня)**: уровни 1–100 проходятся за 20–30 сек — «too easy»; обучающая воронка почти без сопротивления.
- **Стена 3 (середина, ~после апдейтов)**: «some of the puzzles require using the award tools to win» — принудительные бустеры; одновременно нерф экстра-ходов 5→1 за рекламу и рост IAP на >30% (свежий патч, жалобы «now it's totally unplayable»).
- **Точечные пики по YouTube**: «HexaAway Level 561 *SUPER HARD LEVEL*» (shorts), уровень 534 не взят автором прохождения без доп. хода — косвенные маркеры пиков, но систематического «уровня-босса» в текстах нет.
- Числа hexaawaylevel для хвоста (1001–1050): completion 55–60%, 5.7–7.8 попыток — сгенерированы, использовать только как ориентировочную кривую, не как данные.

## 5. Практические выводы

1. **Текстовых решений (порядков тапов) для Hexa Away не существует в интернете** — весь гайд-контент это видео (Go Answer поуровнево; Nova/puzzle gamer батчами по 10). Для датасета «решение уровня» нужен либо свой солвер, либо видео-распознавание.
2. Единственный машиночитаемый индекс уровней — `https://www.hexaawaylevel.com/sitemap-en.xml` (1040 URL) → per-level HTML → YouTube-ID → oEmbed (название/канал без ключа). Валидность видео сверять названием через oEmbed; за уровнем 1040 сайт генерит мусор.
3. `gameanswer.net`/`levelwinner.com`/`walkthroughs.net`/`touchtapplay.com` игру не покрывают — ждать текстовой фермы не откуда.
4. Официальная страница Google Play парсится curl (описание + свежие отзывы в HTML) — источник фактов о механике и патч-нерфах.
5. Индикатор спроса на решения: активные плейлисты-батчи обновляются еженедельно до уровня 1210 при ~0.2–0.3K просмотров на батч (ядро маленькое, но стабильное).
