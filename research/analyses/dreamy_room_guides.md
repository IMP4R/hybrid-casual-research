# Dreamy Room — гайд-сайты и парсимость

Дата: 2026-08-28. Задача: найти гайд-сайт(ы) с уровнями Dreamy Room (ABI Global) и оценить парсимость.

## TL;DR

Найден **один** специализированный гайд-сайт — **https://dreamyroomlevel.com** — и он **отлично парсится**:
SSR (Next.js), весь контент лежит в HTML без JS, есть sitemap.xml со всеми 576 уровневыми URL,
robots.txt явно разрешает (`Allow: /`, `ai-input: yes`). На каждой странице уровня — текстовый
пошаговый walkthrough (20–34 шага), сюжет комнаты, метаданные (сложность, число предметов, тип
комнаты) и картинка финального состояния комнаты на CDN. Текстов про механики достаточно; видео —
не единственный формат.

Остальные поисковики/сайты: Google/DDG/Ecosia/Startpage — капча или отказ; Bing — нерелевантная
выдача; другие dreamyroom*-домены не существуют или пусты; общие walkthrough-порталы гайдов по
Dreamy Room не имеют.

## 1. Найденные сайты

### ✅ dreamyroomlevel.com — основной источник

- **Что внутри:** SEO-ферма, полностью посвящённая Dreamy Room. Заявлено 578 уровней; в sitemap —
  **576 уровневых страниц** (пропущены только `/404` и `/500` — забавно, самого уровня 404 нет).
  Диапазоны на главной: 1–20 … 561–578.
- **Движок:** Next.js, SSR — `curl` без JavaScript получает полный контент (~460 КБ HTML на страницу
  уровня). `__NEXT_DATA__` нет, но он и не нужен: весь текст — обычный семантический HTML
  (h1/h2/h3/p/ul).
- **Парсимость:** отличная. sitemap.xml → список всех URL; дальше обычный HTML-парсер.
  Rate-limit не заметен: 6–7 запросов подряд без блокировок (проверены уровни 1, 100, 200, 250,
  300, 450, 560, 578 — все HTTP 200).
- **Картинки:** `https://cdn.dreamyroomlevel.com/{n}.webp` — финальное состояние комнаты уровня
  `{n}` (webp, 65–85 КБ, проверены 1/100/250 — HTTP 200). Готовые референсы «как выглядит
  собранная комната» для каждого уровня.
- **robots.txt:** `User-agent: * / search: yes / ai-input: yes / ai-train: yes / Allow: /` —
  парсинг и AI-использование прямо разрешены владельцем.
- **Качество контента:** тексты выглядят сгенерированными (шаблонные обороты, на главной висит
  «+50 Coffee Recipes» — след шаблона от другой игры; в FAQ «300+ levels», в шапке «578 levels»).
  Но предметка конкретная и правдоподобная: названия предметов, позиции, порядок сборки. Для
  референса механик и контента уровней — годится, с оговоркой о генерённости.

### ❌ Остальное (не нашлось / не годится)

| Сайт / поиск | Результат |
|---|---|
| dreamyroomlevels.com | DNS не резолвится |
| dreamyroomguide.com | не отвечает (HTTP 000) |
| dreamy-room.com | заглушка «Redirecting...» (JS-редирект, контента нет) |
| touchtapplay.com | Cloudflare 403 на поиск по сайту |
| levelwinner.com | сайт живой, но гайдов по Dreamy Room нет (поиск по сайту пуст) |
| appwalkthrough.com | живой, по «dreamy room» результатов нет |
| Google / DuckDuckGo / Ecosia / Startpage | капча / 403 (IP в бане); Bing — мусорная выдача |

Вывод: конкурентных специализированных гайд-сайтов по Dreamy Room не обнаружено; всё в одном месте.

## 2. Структура уровневых страниц

**URL-паттерн:** `https://dreamyroomlevel.com/{n}` — n = номер уровня, 1…578.
**Индекс:** `https://dreamyroomlevel.com/sitemap.xml` (все URL уровней + lastmod), также есть `/all`.

Содержимое страницы уровня (проверены 1, 100, 250, 578):

| Блок | Формат | Пример |
|---|---|---|
| H1 | `Dreamy Room Level {n}` | «Dreamy Room Level 250» |
| Метаданные (грид) | Difficulty / Time Limit (мин) / Items Count (диапазон) / Room Type | Intermediate · 3 мин · 52–58 items · «Music Concert Stage» |
| Room Story | h2 + 1 абзац сюжетного текста комнаты (персонажи, обстановка) | кошка Suki и концертная площадка MEOW MEOW (уровень 250) |
| **Step-by-Step Walkthrough** | h2 + серия `h3 «Step {k}. {действие}»` + абзац с позицией предмета | 20 шагов (ур. 1), 30+ (ур. 100), 32 (ур. 250), 34 (ур. 578) |
| Tips and Tricks | 3 буллета общих советов | «pink gradient combinations…» |
| Room Items & Furniture | тегированный список предметов уровня | Cloud Sun, Large Bed, Teddy Bear Doll… |
| Related Levels | ссылки на соседние уровни (визуальная навигация) | «Level 2» с ур. 1 |
| Video Walkthrough / Cheats & Solution | блок видео + превью-картинка (cdn `{n}.webp`) | «Click to play video guide» |

**Что извлекать на уровень:** номер, difficulty, items count (диапазон), room type, room story
(текст), шаги `Step k → предмет + позиция` (текст), список предметов (счётчик), CDN-картинку
финала. Плюс важное дисклеймерное примечание сайта о плавающих номерах уровней (см. цитату 4).

Служебное: дисклеймер на каждой странице — «номера уровней часто меняются и различаются между
платформами Android/iOS»; значит, номер уровня с сайта нельзя считать каноном — только порядковый
референс.

## 3. Есть ли тексты, или только видео?

**Тексты есть, и их много.** Видео — лишь один из блоков («Video Walkthrough»), основной контент —
текстовый пошаговый разбор + сюжет + списки предметов. Полностью текстовый парсинг возможен без
headless-браузера.

## 4. Цитаты-факты об игровых механиках (из текстов сайта)

1. **Механика распаковки тапом** (главная, «How to Play»):
   > «Tap to unpack items in Dreamy Room, revealing various personal belongings that tell a character's story. Each box contains carefully curated objects that represent different life stages.»

2. **Порядок сборки: сначала декор на стены/потолок, с проверкой конфликтов позиций** (уровень 1, Step 1):
   > «First in Dreamy Room Level 1, hang the adorable Cloud Sun decoration in the upper left area of the room's ceiling. … Make sure the position doesn't conflict with other hanging decorations.»

3. **Рост числа предметов со сложностью — и, вероятно, рандомизация количества** (метаданные уровней):
   > Уровень 1: «Items Count: 17-23 items» (Beginner, «Sunrise Cloud Nursery») → уровень 250: «52-58 items» (Intermediate, «Music Concert Stage») → уровень 578: «95-101 items» (Expert, «Space Station Base on Floating Desert Island»). Диапазоны вместо точных чисел намекают, что состав коробки варьируется между прогонами/платформами.

4. **Номера уровней плавают между платформами и версиями** (дисклеймер на каждой уровневой странице):
   > «Due to frequent level number changes in Dreamy Room and differences between platforms (Android/iOS), this walkthrough content may not completely match your current level. Please refer to the actual display in the game.»

5. **Разнородные тематики комнат: от детской к концертной сцене и космической станции** (Room Story уровней 1, 250, 578):
   > Ур. 1: «Little Amy says goodnight to her furry friends every night - first the little sheep on the bed, and then the teddy bear with a bow on the floor.» → Ур. 250: «…a talented orange cat named Suki built her dream concert venue. Every evening, as neon lights illuminate the MEOW MEOW stage, three passionate feline musicians gather under glowing stars…» → Ур. 578: «Blast off to an extraordinary space station base built on a floating yellow sand platform… the distinctive orange cat ear building frame creates a whimsical gateway to the purple dome habitat with transparent glass walls…»

## 5. Оговорки

- Контент сайта, судя по формулировкам, сгенерирован (шаблонные повторы, противоречия на главной:
  «578 levels» vs «300+ levels» vs «over 50 levels»; «+50 Coffee Recipes» от другой игры).
  Предметку и порядок сборки стоит использовать как **ориентир**, не как истину в последней
  инстанции — проверять на записях геймплея.
- «Time Limit: 3–5 min» в метаданных противоречит тексту «No time pressure, no wrong answers» —
  скорее выдумка генератора, чем реальная механика игры.
- Пропуски уровней 404 и 500 в sitemap: при массовом парсинге заложить обработку 404 (отдаёт
  страницу с title главной и кодом 404).
