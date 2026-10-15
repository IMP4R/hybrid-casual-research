#!/bin/bash
# img_edit2.sh — правка кадра gpt-image-2 с ретраем и сохранением при успехе
# usage: img_edit2.sh SRC.png OUT.png "Edit prompt"
KEY=$(python3 /Users/user0/golden-land-new/scripts/read-credential-key.py CHEAPVIBECODE_API_KEY 2>/dev/null)
for ATTEMPT in 1 2; do
  RESP=$(curl -s --max-time 170 -H "Authorization: Bearer $KEY" \
    -F "image=@$1" -F "model=gpt-image-2" -F "size=1024x1536" -F "quality=low" \
    -F "prompt=$3" https://ru.cheapvibecode.ru/v1/images/edits)
  OK=$(echo "$RESP" | python3 -c "
import json,sys,base64,pathlib
try:
    d=json.load(sys.stdin)['data'][0]
    pathlib.Path(sys.argv[1]).write_bytes(base64.b64decode(d['b64_json']))
    print('SAVED')
except Exception:
    print('NO')")
  if [ "$OK" = "SAVED" ]; then echo "$2 ok ($(stat -f%z "$2") bytes)"; exit 0; fi
  echo "[$2] попытка $ATTEMPT провалилась, тело: $(echo "$RESP" | head -c 150)"
  [ $ATTEMPT -eq 1 ] && sleep 35
done
exit 1
