# Sand Loop (Voodoo, $19.1M) — гайд-сайты с уровнями

Дата поиска: 2026-08-28. Игра: **Sand Loop** (iOS **id6754363534**, Google Play **com.pc.sand.loop**). Позиционирование сторов/сайтов: «realistic sand physics», лить песок в стаканы на конвейере, «collect sand and unlock artworks», relaxing-жанр.

> Методологическая заметка: Google и DuckDuckGo (вкл. lite) отдают CAPTCHA с этого IP, Mojeek — Captcha, локальный SearXNG лежал, встроенный web_search без ключа, Reddit JSON заблокирован. Рабочие каналы: **Brave Search через curl** (при guesses по шаблону `sandlooplevel.com` нашёл главное) и **прямые заходы curl'ом**. YouTube открывается curl'ом (ytInitialData + oEmbed) без JS.

## 1. Найденные сайты

Экосистема SEO-сайтов вокруг игры — **8 доменов**; все переиспользуют одни и те же YouTube-проходки (один и тот же ролик уровня 350 `U3PaV0ke1zs` — «Gamer Hk» — встроен минимум на 4 сайтах). Покрытие уровнями у сайтов разное: **690 / 655 / 509 / 509 / 190+**, тогда как YouTube показывает проходки минимум до **уровня 1440** — все сайты отстают от игры.

### ✅ sandlooplevel.com — главный уровневой индекс (максимальное покрытие)
- **Главная**: `https://sandlooplevel.com/` — «Sand Loop Level Guide - Complete Walkthroughs for All Levels». Next.js (SSR), за Cloudflare, AdSense + GA4.
- **Структура URL**: `/level/{N}`, N = 1…**690** — проверены `/level/1`, `/level/350`, `/level/690` (все HTTP 200 по curl, без JS); `/levels` — полный индекс из 690 карточек. Зеркало `/zh` (hreflang en/zh/x-default, страницы вида `/zh/level/350`).
- **curl-парсинг**: полностью. Из SSR-HTML индекса `/levels` извлекается **маппинг уровень→YouTube-видео** (690/690 пар) через `/_next/image?url=https%3A%2F%2Fimg.youtube.com%2Fvi%2F{ID}%2Fsddefault.jpg`. Выжимка сохранена: `/tmp/slp_level_videos.json`.
- **Бонус-страницы**: `/find-solution` — солвер «загрузи скриншот уровня → получи видео» (требует JS, но сама механика примечательна: матчинг по скриншоту); `/tips`; `/blog` (разборы уровней 200/300/430/470 и т.п.).
- **Мягкая 404**: уровни > 690 (`/level/700`) отдают HTTP 200 с пустой Next.js-оболочкой (no title, no content) — при скрейпе фильтровать по наличию `<title>`.

### ✅ sand-loop.org — единственный сайт с пошаговым ТЕКСТОВЫМ решением
- **Структура URL**: `/levels/{a-b}/level-{N}` (диапазоны по 20: `/levels/341-360/level-350`), индекс `/levels`. Покрытие до **уровня 509**.
- **Контент уровня**: настоящий step-by-step текст («Quick answer / Step-by-Step Solution: 1 Pour the top-row Orange, Red, and Yellow cups first…»), уровень имеет название-тему («Level 350, 'The Neon Cityscape'»), метку сложности (HARD), скриншоты. Текст, судя по стилю, AI-сгенерирован, но **уровень-специфичен** (механики «Countdown Gates», квоты, последовательность покраски) — источник фактов о механиках №1.
- **curl**: HTTP 200, парсится без JS.

### ✅ sand-loop.com
- «Sand Loop Full Level Solution Walkthrough, Cheat & Tips», `/level/{N}` + индекс `/all-level-walkthrough`. Покрытие до **~509**.
- Видео через `lite-yt-embed` — ID лежит в атрибуте `videoid="U3PaV0ke1zs"` (парсится curl'ом, но лениво подгружается в браузере). Текст — навигационная сетка уровней + шаблонный совет.
- curl: 200, парсится.

### ⚠️ sandloop.org
- `/en/levels`, `/en/level/{N}` — «Sand Loop Level 350 - Walkthrough, Solution & Guide [2026]». Карточки с YouTube-превью (2 видео на уровень); картинки хостит сторонний домен `image.pixel-flow-level.com`. На индексной странице видно ~56 ссылок (max 190) — остальное лениво.
- curl: 200, парсится.

### ⚠️ sandloop.help и sandloopguide.org — близнецы (один шаблон)
- `sandloop.help/levels/{N}/` — «Sand Loop Levels 1-655 - Walkthroughs»; `sandloopguide.org/levels/{N}/` — покрытиеsparse (встречаются 100, 103, 105, 109, 121, 142, 146, 149…).
- Оба: одинаковая навигация «🏠 Home 📋 Levels 📝 Blog ⬇️ Download», одинаковый JS-jump `window.location.href='/levels/'+num`, одинаковый контент: 1 YouTube-видео + 2–3 абзаца шаблонного текста («Watch the Level 350 video walkthrough… quick tips for this Hard puzzle»). Тонкий контент, ценности кроме видео-мэппинга нет.
- curl: 200, парсится. Внимание: у sandloop.help единственный рабочий путь `/levels/{N}/` (без s → 404 с красивой страницей «Level doesn't exist yet»).

### ⚠️ sandloop.io
- Группированный индекс `/levels` → `/levels/1-50`, `/levels/51-100`… и постраничные `/levels/{N}`; на странице «Level completion time: 3min 10sec», prev/next. YouTube iframe (не ленивый) — парсится curl'ом.

### ❌ Не работают / заблокированы
- `sandloopguide.com`, `sandloopanswers.com`, `sandlooplevels.com`, `sandloopwalkthrough.com` — **не существуют** (DNS NXDOMAIN). Живой «answers»-паттерн не используется — ниша занята `.org/.help/.io/.app`.
- `sandloop.app` — Cloudflare JS-challenge («Just a moment…», HTTP 403 для curl). Содержимое недоступно без браузера.
- `gameanswer.net` — `?s=sand+loop` → «**No results found**». `levelwinner.com` — статей о Sand Loop нет (поиск выдаёт только чужие «Loop Drive 2», «Loop Taxi»). `walkthroughs.net` — Cloudflare, заблокирован.

## 2. Что на уровневых страницах (проверено: sandlooplevel 1/350/690/700, sand-loop.org 350, sandloop.help 350, sand-loop.com 350, sandloop.io 11)

| Аспект | Что есть |
|---|---|
| **Текст решения** | На sandlooplevel.com/sandloop.help/sandloop.com — шаблонная «стратегия» из одной заготовки на все уровни («three-phase flow», «lock your opening shape by ~26%») — для решений бесполезна. **Реальный текст — только на sand-loop.org**: пошаговый рецепт конкретного уровня с цветами, порядком и цифрами. |
| **Видео** | ✅ Везде. Все сайты встраивают одни и те же YouTube-проходки (каналы Gamer Hk `@gamerhk007`, Einstein Gamer `@EinsteinGamer50` и др.). Видео на уровневых страницах валидны (проверено oEmbed: «Sand loop level 350 Super hard level Walkthrough Solution», «Sand Loop level 1-10 All Levels Gameplay»). |
| **Метаданные уровня** | sandlooplevel.com: метка сложности (Easy/Medium/Hard), оценка времени (30 сек … 6-10 мин), звёзды (5/5), теги («super-hard milestone»). sand-loop.org: название уровня-темы + скриншоты. sandloop.io: «completion time». |
| **Структура URL** | Три шаблона: `/level/{N}` (sandlooplevel, sand-loop.com, sandloop.org `/en/level/{N}`), `/levels/{N}/` (sandloop.help, sandloopguide.org), `/levels/{a-b}/level-{N}` (sand-loop.org, песочницы по 20). Все — предсказуемые целые числа. |

**Вывод по парсингу**: вся экосистема парсится curl без JS (кроме sandloop.app и walkthroughs.net за Cloudflare). Самый полезный скрейп: sandlooplevel.com `/levels` → 690 пар уровень→видео; sand-loop.org → текстовые решения до 509.

## 3. Факты о механиках из текстов (кросс-сайтовый синтез)

1. **Ядро геймплея — заливка картинки цветным песком через стаканы**: «Tap to control buckets on the conveyor belt, collect falling sand at the right rhythm, and keep colors pure—no mixing allowed!» (sandlooplevel). Разбор 350-го (sand-loop.org) раскрывает детали: заливка по цветам красит зоны картины («Paint the Purple sky and the Yellow moon after the building silhouettes are outlined»), финальная точечная дорисовка («isolated taps», «patching missed pixels near the edges»).
2. **Гейт-механика с квотами**: уровни вводят «**Countdown Gates**» с числовыми счётчиками («Break the Countdown Gates '5' and '6'… by clearing the required number of cups each») и «**Key Unlocking**» — цвета/зоны недоступны, пока не выполнены квоты в заданном порядке («the game prevents you from accessing the necessary colors until you fulfill specific global quotas», «forces you to solve puzzles in a specific sequence»).
3. **Конвейер — ограниченный ресурс**: «Keep the belt at three slots, because the gated arches limit your early supply»; ловушки геометрии («the column-four dip… collects stray cups that can clog») — переполнение конвейера = проигрыш.
4. **Тайминг важнее скорости на поздних уровнях**: «Wait until the start animation fully settles before your first tap» (sandlooplevel/tips); разбор 430: «narrow recovery window after the 60% progress mark», фазы «opening trunk lock → crossover stabilization → final collector sweep»; 470 — «endgame-first planning, strict handoff timing» (блог sandlooplevel).
5. **Внутриигровые сложности**: Easy / Medium / Hard / **Super Hard** (метка в названиях роликов YouTube: уровни 40, 200, 220, 250, 290, 400, 440, 460, 530, 600, 800, 840, 870, 1000, 1440). По классификации sandlooplevel.com из 690 уровней: **96 Easy (14%) / 143 Medium (21%) / 451 Hard (65%)**.
6. **Объём контента**: игра давно перевалила за 690 уровней, которые успел проиндексировать крупнейший гайд-сайт, — YouTube-проходки существуют минимум для **уровня 1440** («Sand Loop super hard level 1440 walkthrough Solution / not use the item»). Сайты — «слепки» разных версий игры: 509, 655, 690.
7. **Платформенная вариативность**: «level layouts may vary slightly between iOS, Android, and Web versions» (sandlooplevel/tips) — при переносе уровней в клон закладывать вариативность раскладок.

## 4. Стены сложности по отзывам/комментариям

Прямые комментарии YouTube недоступны без тяжёлого innertube-скрейпа (consent-wall + смена форматов ответа) — честная фиксация: **текстов отзывов не добыто**. Косвенные сигналы:

- **Спайки «Super Hard»** — в титулах проходков метка появляется волнами: ранние пики на **40, 200, 220, 250, 290**; средние — **400, 440, 460, 530, 600**; поздние — **800, 840, 870, 1000, 1440**. Паттерн «примерно каждые 40–60 уровней + строгие кратеры» типичен для Voodoo-краулеров.
- **Спрос на помощь по уровню 290**: ролик «Level 290 SUPER HARD» набрал **3 532 просмотра** против 215–750 у соседних super-hard роликов — уровень 290 вероятный спайк отказа/поиска.
- **Уровень 350** — «a significant difficulty spike… strict resource management» из-за одновременного ввода гейтов и квот (sand-loop.org); у sandlooplevel он же помечен «5/5 stars, super-hard milestone, 5-10 minutes».
- **Классификация сайта**: 65% всех уровней — Hard; в блоге песочница сложностей описана как фазы с «узкими окнами восстановления» после 60% прогресса.

## Приложение: YouTube-плейлисты как индекс уровней (все живые, curl-парсятся)

| Плейлист | ID | Видео |
|---|---|---|
| Sand Loop All Levels | `PL5ybSa5BAcE5eWzFiJ-ZCsN29QaGXRJUc` | **405** |
| Sand Loop All Levels Gameplay Walkthrough Solution | `PLWFjkyAG_fzvrcc7wtc2efQZfFWdR24T6` | **261** |
| Sand Loop Levels 1-200 Walkthroughs | `PLpQHHEmQVXBWJ5iBeLizCi1Xw45HGF52Y` | 200 |
| Sand Loop - Levels 1-100 Walkthrough | `PLCeiqGICeA0OBn_JTIf_piY-mCJ88Fdqb` | — |
| Sand Loop Full Game Walkthrough \| Complete Puzzle Levels | `PLa1M-q-W0M1J7IEZEpZTY49qSIdyDm3t0` | — |
| + ещё ~7 плейлистов | `PLh7eDYGg4nMHXvwZYWQT-37nMhUvzTwfG`, `PLnLpHuNEu_M1t5N1grtVyFTQI2epjwNWY`, `PLDLe0Sy10aN1B1fe6hvJACcOpYQOxh1Y5`, `PLb5ivR9LWE75id_Nnb1C7l9D6K5nFSTRw`, `PLzmhSFXfhdfUPmjBouJ5_sXUlFQrx5PoX`, `PLVfOsYC_prW0`, `PLYigyVC33P2Nw0WbUSEu9jFIIyizhEyol` | — |

Поиск YouTube работает из curl: `https://www.youtube.com/results?search_query=...` → `ytInitialData`, oEmbed (`youtube.com/oembed?url=...&format=json`) даёт название/автора ролика без ключей.
