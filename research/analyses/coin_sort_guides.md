# Coin Sort (MoodGames / Lion Studios) — гайд-сайты с уровнями

Дата поиска: 2026-08-28. Игра: **Coin Sort** (iOS id **6446354191**, Lion Studios Plus LLC; Google Play **com.MoodGames.CoinSort**, Mood Games Oü, релиз март 2023). Play: **4.4★, ~5.9K отзывов**.

> Методологическая заметка: Google/DDG отдали CAPTCHA, web_search без ключа, локальный SearXNG лежал. Рабочий канал — **Brave Search через curl** + прямые заходы. В выдаче много КЛОНОВ («Coin Sort Puzzle» от tian.games, madajans, ACTIONFIT «Pocket Chip», SayGames «Pocket Sort») — все найденные источники проверены на принадлежность к MoodGames/Lion Studios версии.

## 1. Найденные сайты

### ✅ appsmenow.com — главный уровневой индекс (видео-проходки)
- **Главная игры**: `https://appsmenow.com/walkthrough/187624-coin-sort` — «Coin Sort: Walkthrough, Guides And Tips», явно атрибутирована: «Coin Sort by Mood Games Ou., Casual/Puzzle, iOS+Android, released 2023-03-30». Совпадение с досье.
- **Структура URL** (регулярная, парсится):
  - уровневые страницы: `/walkthrough/187624-coin-sort/level-{N}` (level-10, level-11, … level-238)
  - «gameplays»-страницы: `/gameplays/187624/level-{N}` (вплоть до level-2667)
- **curl**: HTTP 200, статический HTML (главная 65KB, уровневая 35KB), парсится без JS.
- **Покрытие**: 43 уникальных уровневых ссылки на главной; страницы существуют только для уровней с загруженным видео — **level-150 даёт 404**, т.е. покрытие дырявое, не «все уровни подряд».

### ⚠️ tap-guides.com — tips-статьи (WordPress, похоже на AI-генерацию)
- `https://tap-guides.com/2025/10/24/coin-sort-beginner-tips/`
- `https://tap-guides.com/2025/10/24/coin-sort-earn-coins-quickly/`
- `https://tap-guides.com/2025/10/24/unlocking-skip-it-strategies-in-coin-sort-how-to-use-skip-its-effectively/`
- curl 200 (163KB), парсится. Уровней НЕТ — только механики/монетизация. Атрибутика верная («Coin Sort, developed by Lion Studios»), но текст шаблонный («At A Glance», общие советы) — использовать только для списка фич, не для стратегии.

### ⚠️ puzzlechallengehub.com — контент-ферма, ЧУЖАЯ игра
- `https://puzzlechallengehub.com/recommendation/coin-sort-puzzle-guide` — «Master the 1-to-15 Infinite Loop»: описывает **числовой** merge 1→15 с 5-слотовым гридом. Это описание другой игры из клоунады «Coin Sort Puzzle» (числовой merge, жанр «Logic/Merge»), НЕ denominational Coin Sort от MoodGames. Не использовать для фактов о целевой игре. curl 200.

### ❌ Не работают / заблокированы
- `coinsortlevel.com`, `coinsortguide.com`, `coinsortanswers.com` — **не существуют** (DNS NXDOMAIN).
- `gameanswer.net/coin-sort/` — 404; `?s=coin+sort` редиректит на Bing с чужим запросом. Coin Sort там нет.
- `levelwinner.com` — тега coin-sort нет (`/tag/coin-sort/` отдаёт главную); `?s=` падает ERR_ABORTED. Про Coin Sort статей нет.
- `kashkick.com/guide/game-tips/coin-sort-tips/` — 403 (Cloudflare, curl не парсится). Контекст: Coin Sort используется в reward-приложениях (тред `r/KashKickapp/comments/1nud3sr` «Coin Sort heads up», Reddit блокирует ботов).
- Google/DDG/Bing — CAPTCHA/мусорная локализованная выдача.

### 📺 YouTube-плейлист-индекс
- **`https://www.youtube.com/playlist?list=PLgY8dj1aA-jjBVSUPP0NBSvk6K4twtw0M`** — «**Coin Sort (Lion Studios Plus) – All Levels, Tricks & Gameplay Walkthroughs**» — единственный найденный индекс «all levels» именно целевой игры. Это же видео крутит appsmenow (канал 23Games, ролики уровня 24.08.2025).
- Остальные найденные плейлисты — клоны (Pocket Sort: Coin Merge Puzzle и т.п.).
- TikTok имеет discover-страницы по конкретным уровням (`/discover/how-to-win-level-20-on-coin-sort`, `/content/how-to-solve-level-119-coin-sort`) — косвенный признак, что игроки ищут уровни 15/20/41/99/119.

## 2. Что на уровневых страницах (проверено 3 страницы)

Проверены: главная walkthrough + `level-10` + `gameplays/level-2667` (+ 404-проба level-150).

| Аспект | Что есть |
|---|---|
| **Текст решения** | ❌ Нет. На `level-10` только шаблонная вступительная фраза («Are you stuck on level 10… I'll guide you step-by-step») + **встроенное YouTube-видео** («Walkthrough played by 23Games, uploaded August 24, 2025»). Решение — только в видео. |
| **Мердж-механика описана** | ❌ На уровневых страницах нет. Механики — только в tips-статьях (см. ниже) и косвенно в темах gameplays: «Frozen coins», «Frozen coins with a 3 on them», «Daily challenge july 25». |
| **Навигация** | ✅ prev/next (Level 9 → Level 11), блок «Related Walkthroughs» с хэштегами `#sortwalkthrough`/`#sortlevel`, блок «Ask a Question» (Q&A). |
| **Структура URL** | Предсказуемая: `/walkthrough/187624-coin-sort/level-{N}`; но валидность страницы надо проверять по коду ответа (404 для уровней без видео). |

**Вывод по парсингу**: curl-парсится всё; программный сбор списка решённых уровней = перебор `level-{N}` с фильтром по 404 + извлечение YouTube-ID видео (oEmbed по ролику даст название уровня). Текстовых решений нет — только видео-индекс.

## 3. Факты о механиках из текстов

1. **Мердж по номиналу**: сортировка/мердж монет «based on color, size, and denomination»; базовый совет — «merge smaller coins to form higher-value ones», мерджи освобождают место (tap-guides, beginner tips).
2. **Буферный слот — ключевая стратегия**: конечное число мест на доске; «Always aim to keep at least one empty space available» — запасной слот под «неподходящую» монету (tap-guides; у контент-фермы про 5 слотов та же идея, но это уже другая игра).
3. **Кнопка Deal (раздача)**: новые монеты выдаются «руками»; wildcards существуют; проваленные раздачи = потеря жизни (Google Play отзывы: «Deal again, no more matches, then lose a life»).
4. **Особые элементы**: **frozen coins** (замороженные монеты, в т.ч. «frozen coins with a 3 on them» — вероятно, счётчик разморозки), «ties/ropes» вокруг стеков которые «can't remove» и при мердже с ними «SIGNIFICANTLY decreased your progress», «ice part» с туториалом, который нельзя пересмотреть (gameplays-темы appsmenow + Play-отзывы).
5. **Skip-its (монетизация Lion Studios)**: бесплатная вводная «билет» в начале игры; дальше Skip-its пропускают рекламу за награды, продаются пачками по IAP и выдаются ежедневно по подписке; совет «копить на сложные уровни» (tap-guides, skip-it статья).
6. **Режимы**: Daily challenge («Daily challenge july 25» в gameplays), «player race» — соревновательный попап (Play-отзыв). Дома-экран после апдейта отделён: выход на него из уровня стоит жизнь (Play-отзыв).

## 4. Стены сложности по отзывам (Google Play, 4.4★ / 5.9K)

- **~уровень 34**: «after a while (I got to "level" 34) the game just starts dealing you hands you can't beat without paying for something» — первый платёжный фильтр рано.
- **~уровень 219**: точка массового отвала: «got to level 219 before I had enough. EVERY LEVEL I'd have to watch an ad to proceed» — стена «реклама за каждый уровень».
- **Жалобы на честность RNG**: «The deal button is literally designed to screw over the player… deals are in fact not random… Getting the same coins that you didn't want in the same exact spot… until you're forced to restart» — игроки читают раздачу как адаптивную против игрока.
- **Принудительные проигрыши/расходы**: «if you can make more moves, the game will sometimes tell you that you lost»; «if you have coins (бонусы), the game will force you to use them by dealing in a way where you HAVE to use coins»; «decides you are out of space when you aren't» — ложный «out of space» при возможном мердже.
- **Обратный прогресс**: мердж с «ties» (верёвками) уменьшает прогресс уровня — источник фрустрации и «непонятных» проигрышей.
- **Реклама**: interstitial'ы на старте симулируют клик («tricked into clicking… almost charged my card») — конкретный UX-паттерн раздражения.

## 5. Итог для автоматизации гайдов

- Единственный структурный веб-источник уровней целевой игры — **appsmenow** (`/walkthrough/187624-coin-sort/level-{N}`), но контент там = YouTube-видео, не текст. Для текстовых решений брать YouTube-плейлист `PLgY8dj1aA-jjBVSUPP0NBSvk6K4twtw0M` (метаданные видео → номера уровней).
- Гайд-ферма на целевую игру **не пишет текстовые уровневые решения** (в отличие от Water Sort и им подобных) — ниша пуста: специализированного сайта уровня «coinsortanswers.com» для Coin Sort от MoodGames не существует.
- Все числовые «стратегии» с farming-сайтов проверять на принадлежность к игре: tap-guides — про целевую, puzzlechallengehub — про числовой клон.
