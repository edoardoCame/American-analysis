#!/usr/bin/env bash

# Launch one background scraper per populated SAM.gov table.
# Each job writes its own log/pid under webscraping/download_logs
# so we can monitor or stop them independently.

set -euo pipefail

DB_PATH="db/sam_archived_opportunities_filtered.sqlite"
PAGE_SIZE=25
THROTTLE_MIN=0.5
THROTTLE_MAX=1.0
LOG_DIR="webscraping/download_logs"

mkdir -p "$LOG_DIR"

sqlite3 "$DB_PATH" "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'fy%' ORDER BY name;" | \
while read -r table_name; do
    [[ -z "$table_name" ]] && continue
    row_count=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM $table_name;")
    if [[ "$row_count" -eq 0 ]]; then
        echo "Skipping $table_name (0 rows)"
        continue
    fi

    pages=$(( (row_count + PAGE_SIZE - 1) / PAGE_SIZE ))
    output_dir="webscraping/downloads/$table_name"
    log_file="$LOG_DIR/${table_name}.log"
    pid_file="$LOG_DIR/${table_name}.pid"

    mkdir -p "$output_dir"

    if [[ -f "$pid_file" ]]; then
        existing_pid=$(<"$pid_file")
        if ps -p "$existing_pid" > /dev/null 2>&1; then
            echo "Already running $table_name (pid $existing_pid); skipping."
            continue
        else
            rm -f "$pid_file"
        fi
    fi

    echo "Launching $table_name ($row_count rows, $pages pages)..."
    nohup python webscraping/sam_attachment_scraper.py \
        --tables "$table_name" \
        --pages "$pages" \
        --page-size "$PAGE_SIZE" \
        --output-dir "$output_dir" \
        --headless \
        --throttle-min "$THROTTLE_MIN" \
        --throttle-max "$THROTTLE_MAX" \
        > "$log_file" 2>&1 &

    echo $! > "$pid_file"
done
