# Car Sort: Color Puzzle — гайд-сайты и парсимость

Дата: 2026-08-28. Задача: найти гайд-сайт(ы) с уровнями Car Sort: Color Puzzle (Rollic Games) и
оценить парсимость.

## TL;DR

**Специализированных гайд-сайтов с уровнями НЕ СУЩЕСТВУЕТ** (проверено 2026-08-28). Ни одного
домена-фермы уровня dreamyroomlevel.com для этой игры нет: прямые паттерны не резолвятся,
крупные walkthrough-порталы игру не покрывают, в свежем индексе Common Crawl нет ни одного URL
с «carsort»/«car-sort». Единственный источник прохождений — **YouTube**: десятки каналов с
пошаговыми видео по уровням (найдены уровни от 11 до 649+, есть плейлист на 119 видео).
Текстовых решений, порядка выезда машин и скринов уровней в текстовом виде — ноль.

Ограничение сессии: поисковики (Google/DDG/Ecosia/Startpage/Brave/Mojeek/SearX) с этого IP
капчат или отдают 403/429, локальный SearXNG (127.0.0.1:8888) не запущен, Bing игнорирует
фразовые кавычки и отдаёт мусор. Поиск шёл обходными путями (внутренние поиски сайтов,
Common Crawl index, YouTube search) —coverage неполный, но четыре независимых отрицательных
проверки сходятся: ферм-гайдов нет.

## 1. Что проверено и результат

### ❌ Прямые домены-паттерны — не существуют (DNS NXDOMAIN)

| Домен | Статус |
|---|---|
| carsortlevel.com | не резолвится |
| carsortguide.com | не резолвится |
| carsortanswers.com | не резолвится |
| carsortgame.com | не резолвится |
| carsortpuzzle.com | не резолвится |
| carsortwalkthrough.com / carsortlevels.com / carsortanswers.net / carsortguide.net | не резолвятся |

### ❌ Walkthrough-порталы — игры нет (внутренний поиск по сайтам)

| Сайт | Метод проверки | Результат |
|---|---|---|
| gameanswer.net | `/?s=car+sort` (HTTP 200) | только словесные игры-совпадения (Word Hike «brutish sort», Figgerits «check and sort»); самого пазла нет |
| appcheaters.com | `/?s=car+sort` (HTTP 200) | 0 релевантных результатов |
| levelwinner.com | `/?s=car+sort` (HTTP 200) | 0 результатов (fallback-выдача на 181 страницу случайных статей) |
| levelsolved.com | sitemap + главная (537 КБ) | в sitemap один URL (корень); игр со «sort» на главной нет |
| qunb.net | `/?s=car+sort` | мёртвый/пустой ответ (163 байта) |
| walkthroughs.net | Cloudflare | 403 и curl'ом, и браузером |
| game-solver.com | Cloudflare | 403 |

### ❌ Common Crawl CC-MAIN-2026-34

Запросы `url=*carsort*` и `url=*car-sort*` — **0 захватов**. В свежем ползании (34-й сбор 2026)
нет ни одной страницы с этими подстроками в URL — т.е. ни одной фермы, которая бы хотя бы
завела под игру URL-структуру.

### ✅ YouTube — единственный источник прохождений

Поиск `car sort color puzzle level guide` на YouTube (страница отдаётся без капчи, данные
уровней видны прямо в выдаче):

- **Gamer Fox** (`@GamerFox88`) — плейлист **«Car Sort: Color Puzzle», 119 видео**, начинается с
  Level 11, Level 12 (`/playlist?list=PLJ7aTNdGDxmvMujovkL-KhK9RjKe-pWTJ`).
- **Daisy Gaming** (`@Infinty_craft`) — серии «Level N step by step walkthrough solution» со
  ссылкой на собственный плейлист «all Car Sort Color Puzzle levels»; покрыты уровни
  197, 317, 327, 364, 370, 380, 479, 487, 488, 498, 514, 517… (ролики 1–4 мин, сотни просмотров).
- **Gamerstein** (`@gamerstein17`) — «Level N Walkthrough Solution»: 210, 211, 247, 261, 299, 311…
- **Car sort game solution** (`@CarSortGaming`) — Shorts, найден уровень **649**.

Структура URL стандартная: `/watch?v=<id>`, в заголовке всегда номер уровня («Car Sort Color
Puzzle Level 498 Walkthrough») — по заголовкам можно строить индекс уровней без просмотра.
Тексты под видео содержательные описания не содержат (только «step by step walkthrough
solution» + ссылка на плейлист): вся фактура решения — внутри видеоряда. Страницы поиска
YouTube парсятся без JS (контент виден в HTML), страницы самих видео — стандартная схема
`ytInitialData`-JSON в HTML (для этой игры конкретно не проверял постранично).

## 2. Факты о механиках (тексты: Google Play + отзывы)

Страница: `play.google.com/store/apps/details?id=com.duykanbakay.carconveyortransfer`
(пакет `com.duykanbakay.carconveyortransfer` — внутренний коднейм «car conveyor transfer»).
4.4★, 12.5K отзывов, 500K+ скачиваний, PEGI 3; обновлено 2026-08-27 («новая иконка, багфиксы»).
Категории: Puzzle, Logic, Single player, **Offline**, Stylized.

1. **Ядро — тап и порядок выезда.** Описание: «Tap to send colorful cars around the track!
   Match colors, park them in the right garages, and clear the board». Т.е. одним тапом машина
   выезжает и едет по треку в гараж своего цвета; цель уровня — очистить доску без пробки.
2. **Сотни коротких уровней.** «Enjoy hundreds of quick puzzle levels» — подтверждено YouTube
   (уровни 649+ существуют на 2026-08); живые уровни докатываются обновлениями.
3. **Стены сложности — реальные и поздние.** Отзыв (позже уровня 629): «stuck on level 629…
   trying now for 3 days» — жёсткие уровни в mid/late-гейме, игроки ищут помощь (драйвер
   спроса на walkthrough'ы).
4. **Экономика: жизни + монеты.** Отзывы: 5 жизней, восстановление долгое; «you need at least
   900 [coins] to refill lives or continue the game», монет за уровень мало; застрять можно и
   без монет → фрустрация → минус в рейтинге.
5. **Монетизация с трением.** Rewarded-видео за доп. монеты есть, но отзывы жалуются, что
   реклама иногда не даёт крестик (теряются и монеты, и сессия) — фактор churn, полезный
   как антипример.

## 3. Вывод для research

- Текстовых гайд-ферм нет → **контент уровней придётся снимать с YouTube** (просмотр/кадры
  вручную или выгрузкой видео) либо играть самому; автоматического HTML-источника решений,
  как у Dreamy Room, не существует.
- Индекс уровней строится по заголовкам YouTube-роликов (плейлист Gamer Fox — готовый каркас).
- Соседняя ниша подтверждает паттерн: для hyper-casual sort-игр Rollic SEO-фермы текстовых
  гайдов не появляются вовсе — в отличие от «комнатных» пазлов (Dreamy Room).
