#!/usr/bin/env bash

set -euo pipefail

# ============================================================
# Usage:
#   ./run_dataset_pipeline.sh <DATASET_DIR> <RESULTS_DIR> [S_NAME]
#
# ============================================================

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <DATASET_DIR> <RESULTS_DIR> [S_NAME]"
    exit 1
fi

PROJECT_DIR="/home/cohent59/pattern_finder/subgraph_filter_suit"

PATTERN_FINDER="$PROJECT_DIR/build/sgf-pattern-finder"
GRAPH_SEARCHER="$PROJECT_DIR/build/sgf-graph-searcher"

DATASET_DIR="$1"
RESULTS_DIR="$2"
ONLY_S_NAME="${3:-}"

shopt -s nullglob

if [[ -d "$DATASET_DIR/S_graphs" ]]; then
    G_PATH="$DATASET_DIR/G.json"
    S_DIR="$DATASET_DIR/S_graphs"
elif [[ -f "$DATASET_DIR/G.json" ]]; then
    G_PATH="$DATASET_DIR/G.json"
    S_DIR="$DATASET_DIR"
else
    echo "Error: expected a dataset directory containing G.json and S_graphs/, or a directory containing G.json and S_*.json" >&2
    exit 1
fi

if [[ ! -f "$G_PATH" ]]; then
    echo "Error: missing G.json at $G_PATH" >&2
    exit 1
fi

if [[ ! -d "$S_DIR" ]]; then
    echo "Error: missing graph directory at $S_DIR" >&2
    exit 1
fi

S_FILES=("$S_DIR"/S_*.json)
if [[ ${#S_FILES[@]} -eq 0 ]]; then
    echo "Error: no S_*.json files found in $S_DIR" >&2
    exit 1
fi

TMP_LIBRARY="$PROJECT_DIR/local_tests/figure1_toy_models/tmp_single_graph_library"

READER_TYPE="json"
PATTERN_OUTPUT_TYPE="json"
SCORE_THRESHOLD="-3"
PRIOR_POLICY="combined"

mkdir -p "$RESULTS_DIR"
mkdir -p "$TMP_LIBRARY"

SUMMARY_CSV="$RESULTS_DIR/summary.csv"
TMP_SUMMARY="$RESULTS_DIR/summary.tmp"

# Keep a count of how many S graphs are not found in G.
NOT_FOUND_COUNT=0

count=0

mapfile -t S_FILES < <(
    for path in "$S_DIR"/S_*.json; do
        [[ -f "$path" ]] || continue
        base=$(basename "$path" .json)
        num=${base#S_}
        printf '%05d\t%s\n' "$num" "$path"
    done | sort -k1,1n | cut -f2-
)
for S_PATH in "${S_FILES[@]}"
do
    if [[ ! -f "$S_PATH" ]]; then
        continue
    fi

    S_NAME=$(basename "$S_PATH" .json)
    if [[ -n "$ONLY_S_NAME" && "$S_NAME" != "$ONLY_S_NAME" ]]; then
        continue
    fi
    OUT_DIR="$RESULTS_DIR/$S_NAME"

    echo "========================================"
    echo "Processing $S_NAME"
    echo "========================================"

    rm -rf "$OUT_DIR"
    mkdir -p "$OUT_DIR"

    rm -f "$TMP_LIBRARY"/*.json
    cp "$S_PATH" "$TMP_LIBRARY/"

    # --------------------------------------------------------
    # Step 1: pattern finder
    # --------------------------------------------------------
    set +e
    "$PATTERN_FINDER" \
        --preprocess \
        --reader-type "$READER_TYPE" \
        --library-input-folder "$TMP_LIBRARY" \
        --output-folder "$OUT_DIR" \
        --pattern-output-type "$PATTERN_OUTPUT_TYPE" \
        --preprocess-single-graph 0 \
        --background-graph-path "$G_PATH" \
        --score-threshold "$SCORE_THRESHOLD" \
        > "$OUT_DIR/pattern_finder.log" 2>&1
    FINDER_EXIT=$?
    set -e

    S_MATCHED=0
    BEST_MATCHES=""
    BEST_PATTERN=""

    if [[ $FINDER_EXIT -eq 0 ]]; then
        PATTERN_FILES=("$OUT_DIR"/pattern_*.json)

        if [[ ${#PATTERN_FILES[@]} -gt 0 ]]; then
            for PATTERN_FILE in "${PATTERN_FILES[@]}"; do
                if [[ ! -f "$PATTERN_FILE" ]]; then
                    continue
                fi

                PATTERN_INDEX=$(basename "$PATTERN_FILE" .json)
                PATTERN_INDEX=${PATTERN_INDEX#pattern_}

                set +e
                SEARCH_OUTPUT=$("$GRAPH_SEARCHER" \
                    --subgraph-path "$PATTERN_FILE" \
                    --background-path "$G_PATH" \
                    --reader-type "$READER_TYPE" \
                    --prior-policy "$PRIOR_POLICY" \
                    --stop-on-first-match 2>&1)
                SEARCH_EXIT=$?
                set -e
                if [[ $SEARCH_EXIT -eq 0 && "$SEARCH_OUTPUT" =~ Matches[[:space:]]found:[[:space:]]*([0-9]+) ]]; then
                    MATCHES_FOUND="${BASH_REMATCH[1]}"
                    S_MATCHED=1
                    if [[ -z "$BEST_MATCHES" || "$MATCHES_FOUND" -lt "$BEST_MATCHES" ]]; then
                        BEST_MATCHES="$MATCHES_FOUND"
                        BEST_PATTERN="$PATTERN_FILE"
                    fi
                fi
            done
        fi
    fi

    if [[ -n "$BEST_PATTERN" ]]; then
        cp "$BEST_PATTERN" "$OUT_DIR/smallest_pattern.json"
        echo "$BEST_MATCHES" > "$OUT_DIR/smallest_match_count.txt"
    fi

    # Keep only the selected pattern; the finder may also create an index CSV.
    rm -f "$OUT_DIR"/pattern_*.json "$OUT_DIR"/pattern_index_*.csv

    if [[ $S_MATCHED -eq 0 ]]; then
        NOT_FOUND_COUNT=$((NOT_FOUND_COUNT + 1))
    fi

    count=$((count + 1))

    if (( count % 50 == 0 )); then
        echo "Completed $count graphs"
    fi
done

echo
printf 'Not found in G: %d\n' "$NOT_FOUND_COUNT"
echo "Finished."
echo "Graphs with no match in G: $NOT_FOUND_COUNT"
