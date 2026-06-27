#!/bin/sh
printf '\033[2J\033[H'
printf '\033[1;38;5;87mTrace Mono Console\033[0m  terminal log specimen\n'
printf '\033[38;5;244mfont=Trace Mono Console  goal=logs, shells, tracebacks\033[0m\n\n'
printf '\033[38;5;79mINFO \033[0m 2026-06-27T10:42:01.932Z api.gateway request_id=8f14e45f-ea5d-4c12-9281-7a8f67\n'
printf '\033[38;5;221mWARN \033[0m 2026-06-27T10:42:02.104Z cache.miss key=user:1042 ttl=0ms path=/v1/users/1042\n'
printf '\033[38;5;203mERROR\033[0m 2026-06-27T10:42:02.337Z db.pool timeout after 2500ms host=10.42.0.17 port=5432\n'
printf '      at connect(pool.py:184) -> acquire(pool.py:92) -> handle_request(app.py:61)\n'
printf '      payload={"status":503,"retry":true,"trace":"0O1lI|5S2Z8B"}\n\n'
printf 'Ambiguity check: 0 O o   1 l I |   5 S s   2 Z z   8 B b   rn m nn\n'
printf 'JSON/path check:  {} [] () <>  /var/log/app.json  status=503  retry=true\n'
printf 'Box drawing:     ├─ parser.decode_json -> storage.write_batch -> notifier.enqueue\n'
sleep "${TRACE_MONO_DEMO_HOLD:-30}"
