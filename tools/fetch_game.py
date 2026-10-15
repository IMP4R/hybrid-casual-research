#!/usr/bin/env python3
"""fetch_game.py v2 — досье на игру: описания геймплея + реальные скриншоты.

Источники:
  1. iTunes Search API   — описание разработчика + скриншоты App Store
  2. Google Play         — описание из страницы тайтла
  3. YouTube (yt-dlp)    — миниатюры геймплейных роликов + их описания
  4. CrazyGames          — если у игры есть веб-порт: обложка + mp4-геймплей,
                           из которого ffmpeg нарезает кадры (реальный геймплей!)
  5. Яндекс Игры         — целевой магазин: имя, id карточки, обложка каталога

Запуск:  python3 tools/fetch_game.py "Sand Loop"
Результат: research/screens/<slug>/  (тексты + картинки + DOSSIER.md;
картинки дальше смотрит агент через read_image и вердиктит: геймплей или маркетинг)
"""
import json, re, subprocess, sys, urllib.request, urllib.parse, pathlib, html

YTDLP = "/Users/user0/.venv/ytools/bin/yt-dlp"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}

def get(url, timeout=25, binary=True):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read()

def slugify(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:40]

def save_img(data_or_url, path):
    try:
        data = data_or_url if isinstance(data_or_url, bytes) else get(data_or_url, timeout=30)
        if len(data) < 3000:  # заглушка "нет превью"
            return False
        if data[:3] == b"\xff\xd8\xff": ext = ".jpg"
        elif data[:8] == b"\x89PNG\r\n\x1a\n": ext = ".png"
        elif data[:4] == b"RIFF" and data[8:12] == b"WEBP": ext = ".webp"
        else: return False
        path.with_suffix(ext).write_bytes(data)
        return True
    except Exception as e:
        print(f"    ! img fail: {str(e)[:80]}")
        return False

def words_overlap(a, b):
    wa, wb = set(re.findall(r"[a-z0-9]+", a.lower())), set(re.findall(r"[a-z0-9]+", b.lower()))
    return len(wa & wb) / max(1, len(wa))

# ---------- источники ----------

def src_itunes(game, out, report):
    print("[1/5] iTunes Search API...")
    try:
        for country in ("us", "ru"):
            j = json.loads(get(f"https://itunes.apple.com/search?term={urllib.parse.quote(game)}&entity=software&limit=5&country={country}"))
            if j.get("resultCount"): break
        best = next((r for r in j.get("results", []) if game.lower() in r.get("trackName", "").lower()), None) or (j["results"][0] if j.get("results") else None)
        if not best: report.append("## App Store: ничего не найдено\n"); return
        print(f"    найдено: {best.get('trackName')} — {best.get('sellerName','?')}")
        report.append(f"## App Store: {best.get('trackName')} ({best.get('sellerName','?')})\n")
        report.append(f"- жанр: {best.get('primaryGenreName','?')}, рейтинг: {best.get('averageUserRating',0):.1f} ({best.get('userRatingCount',0)})\n\n### Описание разработчика\n{best.get('description','')[:3500]}\n")
        n = 0
        for u in best.get("screenshotUrls", [])[:6]:
            n += 1
            save_img(u, out / "itunes_shots" / f"shot{n}.png")
        print(f"    скринов App Store: {n}")
    except Exception as e:
        print(f"    ! itunes: {str(e)[:100]}")

def src_play(game, out, report):
    print("[2/5] Google Play (описание + галерея скриншотов)...")
    try:
        q = urllib.parse.quote(game)
        page = get(f"https://play.google.com/store/search?q={q}&c=apps&hl=en&gl=us", timeout=30).decode("utf-8", "ignore")
        pkg = re.search(r"/store/apps/details\?id=([\w.]+)", page)
        if not pkg: print("    пакет не найден"); return
        detail = get(f"https://play.google.com/store/apps/details?id={pkg.group(1)}&hl=en&gl=us", timeout=30).decode("utf-8", "ignore")
        m = re.search(r'<meta name="description" content="([^"]+)"', detail)
        t = re.search(r'<title[^>]*>([^<]+)</title>', detail)
        og = re.search(r'property="og:image" content="https://play-lh\.googleusercontent\.com/([A-Za-z0-9_-]{30,})', detail)
        icon = og.group(1) if og else ""
        if t: report.append(f"\n## Google Play: {html.unescape(t.group(1))}\n- пакет: {pkg.group(1)}\n")
        if m: report.append(f"### Описание Google Play\n{html.unescape(m.group(1))[:3500]}\n")
        print(f"    пакет: {pkg.group(1)}")
        # галерея: топовые по частоте play-lh хеши, кроме иконки; валидация:
        # >50KB (generic-фоны и заглушки меньше), не дубликат, не известный фон
        import hashlib
        GENERIC = {"93a14cbc524491b79ef7b976cf1d72f4b6fc8d0c2026e2db399ad68f3de0944c"}
        from collections import Counter
        bases = [b.split("=")[0] for b in re.findall(r'https://play-lh\.googleusercontent\.com/([A-Za-z0-9_-]{30,})', detail)]
        tops = [b for b, _ in Counter(bases).most_common(16) if b != icon]
        n = 0; seen_hash = set(GENERIC)
        for b in tops:
            if n >= 6: break
            try:
                data = get(f"https://play-lh.googleusercontent.com/{b}=w1052", timeout=30)
            except Exception:
                continue
            if len(data) < 50_000:
                continue
            h = hashlib.sha256(data).hexdigest()
            if h in seen_hash:
                continue
            seen_hash.add(h)
            if save_img(data, out / "play_shots" / f"shot{n+1}.jpg"):
                n += 1
        print(f"    скринов Google Play: {n}")
    except Exception as e:
        print(f"    ! play: {str(e)[:100]}")

def src_youtube(game, out, report):
    print("[3/5] YouTube геймплейные превью...")
    try:
        res = subprocess.run([YTDLP, "--flat-playlist", "--print", "%(id)s\t%(title)s",
                              f"ytsearch6:{game} gameplay"], capture_output=True, text=True, timeout=120).stdout
        rows = [l.split("\t", 1) for l in res.strip().splitlines() if "\t" in l]
        keep = [r for r in rows if re.search(r"gameplay|walkthrough|playthrough", r[1], re.I)][:4] or rows[:3]
        report.append("\n## YouTube-ролики геймплея (миниатюры = реальные кадры)\n")
        for vid, title in keep:
            desc = subprocess.run([YTDLP, "--skip-download", "--print", "%(description)s",
                                   f"https://www.youtube.com/watch?v={vid}"], capture_output=True, text=True, timeout=60).stdout.strip()
            ok = save_img(f"https://i.ytimg.com/vi/{vid}/maxresdefault.jpg", out / "yt_thumbs" / f"{vid}.jpg") or \
                 save_img(f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg", out / "yt_thumbs" / f"{vid}.jpg")
            report.append(f"- {title}\n  - https://youtu.be/{vid} | превью: {'ok' if ok else 'FAIL'}\n  - {desc[:500]}\n")
            print(f"    {title[:55]} -> {'ok' if ok else 'fail'}")
    except Exception as e:
        print(f"    ! yt: {str(e)[:100]}")

def src_crazygames(game, out, report):
    print("[4/5] CrazyGames (веб-порт: обложка + mp4->кадры)...")
    try:
        j = json.loads(get(f"https://api.crazygames.com/v3/en_US/search?q={urllib.parse.quote(game)}", timeout=20))
        rows = j.get("result", [])
        rows.sort(key=lambda r: -words_overlap(game, r["name"]))
        hit = rows[0] if rows and words_overlap(game, rows[0]["name"]) >= 0.5 else None
        if not hit:
            print("    веб-порта нет"); report.append("\n## CrazyGames: веб-порта нет\n"); return
        slug = hit["slug"]
        report.append(f"\n## CrazyGames веб-порт: {hit['name']}\n- https://www.crazygames.com/game/{slug}\n")
        save_img(f"https://imgs.crazygames.com/{hit['covers']['16x9']}?metadata=none&quality=75&width=640",
                 out / "crazygames_cover.jpg")
        vid = next((s["location"] for s in hit.get("videos", {}).get("sizes", []) if 300 <= s["width"] <= 700), None)
        if vid:
            for base in ("https://media.crazygames.com/", "https://imgs.crazygames.com/"):
                try:
                    mp4 = get(base + vid, timeout=40)
                    if mp4[:12] == b"\x00\x00\x00\x18ftypmp42" or b"ftyp" in mp4[:16]:
                        (out / "cg_gameplay.mp4").write_bytes(mp4)
                        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(out / "cg_gameplay.mp4"),
                                        "-vf", "fps=1", "-frames:v", "6", str(out / "cg_frames" / "f%02d.jpg")],
                                       check=True, timeout=60)
                        n = len(list((out / "cg_frames").glob("*.jpg")))
                        report.append(f"- mp4 геймплея скачан, кадров нарезано: {n}\n")
                        print(f"    mp4 ok, кадров: {n}")
                        break
                except Exception:
                    continue
        else:
            print("    mp4 нет, только обложка")
    except Exception as e:
        print(f"    ! crazygames: {str(e)[:100]}")

# ---------- main ----------

def main(game):
    out = pathlib.Path("/Users/user0/godot-hybrid-casual/research/screens") / slugify(game)
    for d in ("itunes_shots", "yt_thumbs", "cg_frames", "play_shots"): (out / d).mkdir(parents=True, exist_ok=True)
    report = [f"# Досье: {game}\n"]
    src_itunes(game, out, report)
    src_play(game, out, report)
    src_youtube(game, out, report)
    src_crazygames(game, out, report)
    # Яндекс Игры как источник убран по решению пользователя (низкое качество тамошнего контента)
    (out / "DOSSIER.md").write_text("\n".join(report))
    files = sum(1 for _ in out.rglob("*") if _.is_file())
    print(f"\nГотово: {out}/  ({files} файлов; картинки — на визуальную проверку агентом)")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "Pixel Flow")
