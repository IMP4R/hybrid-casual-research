#!/bin/bash
# img_edit.sh — правка кадра через gpt-image-2 (дешёвая консистентная цепочка сториборда)
# usage: img_edit.sh SRC.png OUT.png "Edit prompt"
KEY=$(python3 /Users/user0/golden-land-new/scripts/read-credential-key.py CHEAPVIBECODE_API_KEY 2>/dev/null)
RESP=$(curl -s --max-time 170 -H "Authorization: Bearer $KEY" \
  -F "image=@$1" -F "model=gpt-image-2" -F "size=1024x1536" -F "quality=low" \
  -F "prompt=$3" https://ru.cheapvibecode.ru/v1/images/edits)
echo "$RESP" | python3 -c "
import json,sys,base64,pathlib
try:
    d=json.load(sys.stdin)['data'][0]
    pathlib.Path(sys.argv[1]).write_bytes(base64.b64decode(d.get('b64_json','')))
    print(sys.argv[1],'ok',pathlib.Path(sys.argv[1]).stat().st_size)
except Exception as e:
    print('EDIT FAIL:', e)"
