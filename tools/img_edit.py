#!/usr/bin/env python3
"""img_edit.py — правка кадра через gpt-image-2 (cheapvibecode), без шелл-эха больших строк.
usage: img_edit.py SRC.png OUT.png "Edit prompt"
"""
import base64, json, pathlib, re, sys, time
import urllib.request, uuid

def key():
    m = re.search(r"CHEAPVIBECODE_API_KEY:\s*['\"]?([^'\"\n]+)",
                  (pathlib.Path.home() / ".dsh" / ".credentials.yaml").read_text())
    return m.group(1).strip()

def edit(src, out, prompt):
    boundary = uuid.uuid4().hex
    parts = []
    for name, val in (("model", "gpt-image-2"), ("size", "1024x1536"), ("quality", "low"), ("prompt", prompt)):
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{val}\r\n'.encode())
    img = pathlib.Path(src).read_bytes()
    parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="image"; filename="{pathlib.Path(src).name}"\r\n'
                 f'Content-Type: image/png\r\n\r\n'.encode() + img + b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    body = b"".join(parts)
    req = urllib.request.Request("https://ru.cheapvibecode.ru/v1/images/edits", data=body,
        headers={"Authorization": f"Bearer {key()}",
                 "Content-Type": f"multipart/form-data; boundary={boundary}"})
    r = json.loads(urllib.request.urlopen(req, timeout=170).read())
    pathlib.Path(out).write_bytes(base64.b64decode(r["data"][0]["b64_json"]))
    print(f"{out} ok ({pathlib.Path(out).stat().st_size} bytes)")

if __name__ == "__main__":
    src, out, prompt = sys.argv[1], sys.argv[2], sys.argv[3]
    for attempt in (1, 2):
        try:
            edit(src, out, prompt)
            break
        except Exception as e:
            print(f"[{out}] попытка {attempt} провалилась: {str(e)[:180]}")
            if attempt == 1:
                time.sleep(35)
