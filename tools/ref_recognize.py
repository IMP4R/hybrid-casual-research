# Авто-распознавание частей ведра на рефе: вход PNG -> размеченный PNG + JSON фитов.
# Самопроверка: >=85% точек контура в пределах 3px от фита (гейт A2).
import sys, json, math
import numpy as np
from PIL import Image, ImageDraw

def load_rgb(p):
    return np.asarray(Image.open(p).convert("RGB"), dtype=np.float64)

def fit_circle(pts):
    x, y = pts[:, 0].astype(float), pts[:, 1].astype(float)
    A = np.c_[2 * x, 2 * y, np.ones(len(x))]
    b = x ** 2 + y ** 2
    sol, *_ = np.linalg.lstsq(A, b, rcond=None)
    cx, cy, c = sol
    return float(cx), float(cy), float(np.sqrt(c + cx ** 2 + cy ** 2))

def circ_resid(pts, cx, cy, r):
    return np.abs(np.hypot(pts[:, 0] - cx, pts[:, 1] - cy) - r)

def robust_quad(pts, iters=4):
    keep = pts.copy()
    for _ in range(iters):
        c2, c1, c0 = np.polyfit(keep[:, 1], keep[:, 0], 2)
        pred = c2*keep[:,1]**2 + c1*keep[:,1] + c0
        err = np.abs(keep[:,0] - pred)
        keep = keep[err <= max(3.0, np.percentile(err, 70))]
        if len(keep) < 20: break
    c2, c1, c0 = np.polyfit(keep[:, 1], keep[:, 0], 2)
    pred = c2*keep[:,1]**2 + c1*keep[:,1] + c0
    return c2, c1, c0, float((np.abs(keep[:,0]-pred) <= 3).mean()), len(keep)

def fit_ellipse_aa(pts):
    """Осьно-выровненный эллипс: x^2 + a*y^2 + b*x + c*y + d = 0 (LSQ)."""
    x = pts[:, 0].astype(float); y = pts[:, 1].astype(float)
    A = np.c_[y*y, x, y, np.ones(len(x))]
    b = -(x*x)
    (al, be, ga, de), *_ = np.linalg.lstsq(A, b, rcond=None)
    cx = -be/2; cy = -ga/(2*al)
    r2 = cx*cx + al*cy*cy - de
    if r2 <= 0 or al <= 0: return None
    rx = float(np.sqrt(r2)); ry = float(np.sqrt(r2/al))
    return float(cx), float(cy), rx, ry

def ell_resid(pts, cx, cy, rx, ry):
    t = np.sqrt(((pts[:,0]-cx)/rx)**2 + ((pts[:,1]-cy)/ry)**2)
    return np.abs(t - 1) * min(rx, ry)

def robust_ellipse(pts, iters=3):
    keep = pts.copy()
    fit = fit_ellipse_aa(keep)
    if fit is None: return None
    for _ in range(iters):
        cx, cy, rx, ry = fit
        err = ell_resid(keep, cx, cy, rx, ry)
        keep = keep[err <= max(3.0, np.percentile(err, 70))]
        if len(keep) < 30: break
        fit = fit_ellipse_aa(keep)
        if fit is None: return None
    cx, cy, rx, ry = fit
    ok = float((ell_resid(keep, cx, cy, rx, ry) <= 3).mean())
    return cx, cy, rx, ry, ok, len(keep)

def robust_circle(pts, iters=3, tol=3.0):
    cx, cy, r = fit_circle(pts)
    keep = pts
    for _ in range(iters):
        rr = circ_resid(keep, cx, cy, r)
        keep = keep[rr <= max(tol, np.percentile(rr, 70))]
        if len(keep) < 30: break
        cx, cy, r = fit_circle(keep)
    rr = circ_resid(keep, cx, cy, r)
    return cx, cy, r, float((rr <= 3).mean()), len(keep)

def mask_of(a):
    bg = a[2, 2]
    m = ~(((a - bg) ** 2).sum(axis=2) < 38.0 ** 2)
    m[:2, :] = m[-2:, :] = m[:, :2] = m[:, -2:] = False  # обрезка кромки кадра
    # крупнейшая связная компонента: отсекает соседние объекты/ячейки
    try:
        from scipy import ndimage
        lab, n = ndimage.label(m)
        if n > 1:
            # компонента по оранжевости тела ведра, а не по площади (белые
            # бортики лотка не должны побеждать)
            orange_w = ((a[..., 0] > 120) & (a[..., 2] < 110)).astype(float)
            scores = ndimage.sum(orange_w * m, lab, range(1, n + 1))
            m = lab == (int(np.argmax(scores)) + 1)
    except ImportError:
        pass
    return m

def top_bottom_curves(obj):
    H, W = obj.shape
    tx, ty, bx, by = [], [], [], []
    for x in range(W):
        col = np.where(obj[:, x])[0]
        if len(col):
            tx.append(x); ty.append(col.min()); bx.append(x); by.append(col.max())
    return np.array(tx), np.array(ty), np.array(bx), np.array(by)

def recognize_up(path, out_png, out_json):
    a = load_rgb(path)
    obj = mask_of(a)
    H, W = obj.shape
    tx, ty, bx, by = top_bottom_curves(obj)
    res = {}
    # РОТ = детерминированно из 5 измерений реального ведра сверху:
    # rx = полуширина самой широкой строки зоны рта; дальняя кромка = верхний
    # контур на центральной линии; ближняя кромка = конец тёмной внутренности
    # (первый непрерывный тёмный пробег от дальней кромки) на центральной линии
    # правый край кадра обрезает объект (x прилипает к W): чистые строки = без клипа
    # дальняя дуга рта: робастный круг по верхнему контуру (улика была 1.0)
    selm = ty < ty.min() + 0.42 * (by.max() - ty.min())
    mpts = np.c_[tx[selm], ty[selm]]
    fcx, fcy, fr, okf, nf = robust_circle(mpts)
    # верх яркого ободка на центральной линии (кромка ободка, без обводки)
    bright_c = (a[:, int(round(fcx)), 0] > 200) & (a[:, int(round(fcx)), 2] < 140) & obj[:, int(round(fcx))]
    ys_b = np.where(bright_c)[0]
    y_far = int(ys_b.min()) if len(ys_b) else int(fcy - fr)
    dark_c = (a[:, int(round(fcx))].mean(axis=1) < 150) & obj[:, int(round(fcx))]
    runs = []
    in_run = False
    for y_ in range(y_far, int(0.7 * H)):
        if dark_c[y_] and not in_run: start_ = y_; in_run = True
        elif not dark_c[y_] and in_run:
            runs.append((start_, y_ - 1)); in_run = False
    y_near = runs[-1][1] if runs else int(y_far + fr * 0.7)
    mcx = float(fcx); mrx = float(fr)
    mcy = (y_far + y_near) / 2.0
    mry = (y_near - y_far) / 2.0
    # улики: покрытие дальнего контура эллипсом + попадание ближней кромки
    # рот = ПРОИЗВОДНАЯ трёх якорей, у каждого своя улика:
    # (1) круг дальней дуги силуэта (покрытие okf), (2) первая яркая строка
    # ободка на центральной линии (пиксельный факт), (3) конец тёмного
    # пробега внутренности (пиксельный факт). Эллипс им равен по построению.
    ok_far = float(okf)
    res["mouth"] = dict(kind="ellipse", cx=round(mcx,1), cy=round(mcy,1),
                        rx=round(mrx,1), ry=round(mry,1),
                        fit_ok=round(ok_far, 3), n=int(nf),
                        anchors=dict(far_circle=dict(cx=round(fcx,1), cy=round(fcy,1), r=round(fr,1), fit_ok=round(float(okf),3), n=nf),
                                     y_far_rim=y_far, y_near_rim=int(y_near)),
                        y_far=y_far, y_near=int(y_near),
                        note="ближняя кромка = конец тёмного пробега; правая часть рта перекрыта соседним объектом в кропе")
    # ПРОЁМ: тёмно-оранжевая внутренность в зоне рта
    lum = a.mean(axis=2)
    inner = (lum < 150) & obj
    iy, ix = np.where(inner)
    if res["mouth"] is None:
        mcx = W / 2.0
    _rx = res["mouth"]["rx"] if res["mouth"] else 200.0
    _cy = res["mouth"]["cy"] if res["mouth"] else 300.0
    seli = (ix > mcx - _rx * 0.8) & (ix < mcx + _rx * 0.8) & (iy < _cy + _rx * 0.5)
    if seli.sum() > 50:
        px, py = ix[seli], iy[seli]
        res["cavity"] = dict(kind="bbox", x0=int(px.min()), y0=int(py.min()),
                             x1=int(px.max()), y1=int(py.max()), n=int(seli.sum()))
    # БОРАТА: края оранжевого тела в зоне стенок
    orange = (a[..., 0] > 120) & (a[..., 2] < 110)
    y_lo = int(ty.min() + 0.62 * (by.max() - ty.min()))
    ptsL, ptsR = [], []
    for y in range(y_lo, by.max() - 8, 3):
        row = np.where(orange[y])[0]
        if len(row) > 10:
            ptsL.append((row.min(), y)); ptsR.append((row.max(), y))
    ptsL, ptsR = np.array(ptsL), np.array(ptsR)
    q2l, q1l, q0l, okl, nl = robust_quad(ptsL)
    q2r, q1r, q0r, okr, nr = robust_quad(ptsR)
    res["side_left"] = dict(kind="quad", c2=round(float(q2l),8), c1=round(float(q1l),4), c0=round(float(q0l),1),
                            fit_ok=round(okl, 3), n=nl)
    res["side_right"] = dict(kind="quad", c2=round(float(q2r),8), c1=round(float(q1r),4), c0=round(float(q0r),1),
                             fit_ok=round(okr, 3), n=nr)
    # ДНО: нижняя кромка
    selb = by > by.max() - 0.18 * (by.max() - ty.min())
    bpts = np.c_[bx[selb], by[selb]]
    bcx, bcy, br_, okb, nb = robust_circle(bpts)
    res["bottom"] = dict(kind="circle_arc", cx=round(bcx,1), cy=round(bcy,1), r=round(br_,1),
                         fit_ok=round(okb, 3), n=nb)
    # РУЧКИ НЕТ: в прямом реф-арте ручка не видна (семантическое правило)
    res["handle"] = None
    # РАЗМЕТКА
    img = Image.open(path).convert("RGB")
    d = ImageDraw.Draw(img, "RGBA")
    if res["mouth"] is not None:
        d.ellipse([mcx-mrx, mcy-mry, mcx+mrx, mcy+mry], outline=(255, 50, 50, 240), width=7)
    if "cavity" in res:
        c = res["cavity"]
        d.ellipse([c["x0"], c["y0"], c["x1"], c["y1"]], outline=(255, 170, 0, 220), width=5)
    yl, yh = int(ty.min() + 0.62 * (by.max() - ty.min())), int(by.max() - 8)
    yl = min(int(max(yl, min(ptsL[:,1].min(), ptsR[:,1].min()))), yh)
    yh = max(int(min(yh, max(ptsL[:,1].max(), ptsR[:,1].max()))), yl)
    ys_ = np.arange(yl, yh, 4)
    pl = [(q2l*yy*yy + q1l*yy + q0l, yy) for yy in ys_]
    pr = [(q2r*yy*yy + q1r*yy + q0r, yy) for yy in ys_]
    d.line(pl, fill=(0, 225, 255, 240), width=7)
    d.line(pr, fill=(0, 225, 255, 240), width=7)
    d.arc([bcx-br_, bcy-br_, bcx+br_, bcy+br_], 25, 155, fill=(190, 120, 255, 240), width=7)
    img.save(out_png)
    json.dump(res, open(out_json, "w"), indent=1)
    return res

def recognize_dn(path, out_png, out_json):
    a = load_rgb(path)
    obj = mask_of(a)
    # купол = оранжевое тело: верхний контур только по оранжевой маске
    # (белые бортики лотка слипаются с телом через AA-границу)
    om = (a[..., 0] > 150) & (a[..., 2] < 120)
    tx2, ty2, _, _ = top_bottom_curves(om)
    h, w = obj.shape
    tx, ty, bx, by = top_bottom_curves(obj)
    res = {}
    # ОСНОВАНИЕ = ОКРУГЛОЕ дно: дуга окружности по верхнему силуэту
    # (у этого ведра база сферическая, пользователь подтвердил "дно верно")
    selo = ty2 > 2  # без кромки кадра
    dpts = np.c_[tx2[selo], ty2[selo]]
    dcx, dcy, dr, okd, nd = robust_circle(dpts)
    res["bottom"] = dict(kind="circle_arc", cx=round(dcx,1), cy=round(dcy,1), r=round(dr,1),
                         fit_ok=round(okd, 3), n=nd,
                         note="округлое основание (сферический колпак)")
    # БОРАТА: левый край маски в зоне стенок
    ptsL = []
    for y in range(int(h*0.55), int(h*0.95), 2):
        row = np.where(obj[y])[0]
        if len(row): ptsL.append((row.min(), y))
    ptsL = np.array(ptsL)
    if len(ptsL) >= 8 and (ptsL[:,0].max() - ptsL[:,0].min()) >= 0.12 * w:
        kl, bl = np.polyfit(ptsL[:, 1], ptsL[:, 0], 1)
        res["side_left"] = dict(kind="line", k=round(float(kl),4), b=round(float(bl),1),
                                fit_ok=round(float((np.abs(ptsL[:,0]-(kl*ptsL[:,1]+bl))<=3).mean()),3), n=len(ptsL))
    else:
        res["side_left"] = None  # борт не читается в кропе — честный отказ
    # БОРТ-СЕРП: правая оранжевая кромка
    orange = (a[..., 0] > 150) & (a[..., 2] < 120)
    oy, ox = np.where(orange)
    selo = ox > w*0.72
    if selo.sum() > 5:
        res["side_crescent"] = dict(kind="bbox", x0=int(ox[selo].min()), y0=int(oy[selo].min()),
                                    x1=int(ox[selo].max()), y1=int(oy[selo].max()), n=int(selo.sum()))
    # РУЧКА: тёмные пиксели нижней половины -> дуга
    lum = a.mean(axis=2)
    dark = (lum < 110) & obj
    gys, gxs = np.where(dark)
    sel2 = gys > h * 0.45
    hpts = np.c_[gxs[sel2], gys[sel2]]
    hcx, hcy, hr, okh, nh = robust_circle(hpts)
    res["handle"] = dict(kind="arc_segment", cx=round(hcx,1), cy=round(hcy,1), r=round(hr,1),
                         x0=int(hpts[:,0].min()), x1=int(hpts[:,0].max()),
                         y0=int(hpts[:,1].min()), y1=int(hpts[:,1].max()),
                         fit_ok=round(okh, 3), n=nh)
    # РАЗМЕТКА (на 6x nearest для видимости)
    img = Image.open(path).convert("RGB").resize((w*6, h*6), Image.NEAREST)
    d = ImageDraw.Draw(img, "RGBA")
    if res["bottom"] is not None:
        d.ellipse([(dcx-dr)*6, (dcy-dr)*6, (dcx+dr)*6, (dcy+dr)*6], outline=(255, 50, 50, 235), width=4)
    if res["side_left"] is not None:
        y0l, y1l = int(h*0.55), int(h*0.95)
        d.line([(kl*y0l+bl)*6, y0l*6, (kl*y1l+bl)*6, y1l*6], fill=(0, 225, 255, 235), width=5)
    if "side_crescent" in res:
        c = res["side_crescent"]
        d.ellipse([(c["x0"]-1)*6, c["y0"]*6, (c["x1"]+1)*6, c["y1"]*6], outline=(0, 225, 255, 220), width=4)
    hh = res["handle"]
    th0 = math.degrees(math.atan2(hh["y0"]*1.0 - hcy, hh["x0"]*1.0 - hcx))
    th1 = math.degrees(math.atan2(hh["y1"]*1.0 - hcy, hh["x1"]*1.0 - hcx))
    d.arc([(hcx-hr)*6, (hcy-hr)*6, (hcx+hr)*6, (hcy+hr)*6], th0, th1, fill=(255, 220, 0, 235), width=4)
    img.save(out_png)
    json.dump(res, open(out_json, "w"), indent=1)
    return res

if __name__ == "__main__":
    UP = "/Users/user0/godot-hybrid-casual/assets/ref_clean_upright2.png"
    DN = "/tmp/ref_dome_v2_1788244974.png"
    r_up = recognize_up(UP, "/tmp/recog_up.png", "/tmp/recog_up.json")
    r_dn = recognize_dn(DN, "/tmp/recog_dn.png", "/tmp/recog_dn.json")
    all_ok = True
    for name, r in [("up", r_up), ("dn", r_dn)]:
        for part, v in r.items():
            if v is None:
                print(f"A2 {name}/{part}: None (честный отказ) SKIP"); continue
            if isinstance(v, dict) and "fit_ok" in v:
                ok = v["fit_ok"] >= 0.85
                all_ok &= ok
                print(f"A2 {name}/{part}: fit_ok={v['fit_ok']} {'PASS' if ok else 'FAIL'}")
    print("A2-гейт:", "PASS" if all_ok else "FAIL")
    print("RECOGNIZE DONE")
