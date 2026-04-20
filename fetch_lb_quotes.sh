#!/bin/bash
cd /root/.openclaw/workspace
QUOTES_FILE="etf-map-site/lb_quotes.json"
> "$QUOTES_FILE"
echo "{" > "$QUOTES_FILE"
echo '  "quotes": {},' >> "$QUOTES_FILE"
echo '  "updated": "'$(date -Iseconds)'"' >> "$QUOTES_FILE"
echo "}" >> "$QUOTES_FILE"

# Key ETFs to fetch
ETFS="513730.SH 159687.SZ 513130.SH 03190.HK 02800.HK 02828.HK 3033.HK 3037.HK 07226.HK 07552.HK 07200.HK 07500.HK 03033.HK 03037.HK 3441.HK 3442.HK 3174.HK 3167.HK 3432.HK 0941.HK 9988.HK 0700.HK"

for code in $ETFS; do
    result=$(timeout 6 longbridge quote --format json $code 2>/dev/null | grep -v "^New version" | head -1)
    if [ -n "$result" ]; then
        echo "Got $code"
    fi
    sleep 1
done
