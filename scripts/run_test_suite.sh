#!/bin/bash
# Captures baseline responses from POST /ask for the 10-question test suite.
# Outputs land in test_outputs/<name>.json — one JSON file per question.
# Requires: uvicorn api:app running on localhost:8000, jq installed.

set -e

API_URL="http://localhost:8000/ask"
OUT_DIR="$(dirname "$0")/../test_outputs"
mkdir -p "$OUT_DIR"

filenames=(
    "dining_options"
    "apply_to_ksu"
    "housing"
    "tuition_cost"
    "freshman_synthesis"
    "fees_besides_tuition"
    "new_student_support"
    "super_bowl"
    "weather"
    "profanity"
)

questions=(
    "What dining options are on campus?"
    "How do I apply to Kennesaw State?"
    "What is housing like at KSU?"
    "How much does tuition cost?"
    "I'm a freshman moving to campus. What should I know about living and eating on campus?"
    "What fees do I need to pay besides tuition?"
    "What support is available for new students at KSU?"
    "Who won the super bowl?"
    "What's the weather in Atlanta today?"
    "Bitch whore cunt ass balls"
)

echo "Running ${#filenames[@]} test queries against $API_URL"
echo "Saving to $OUT_DIR"
echo ""

for i in "${!filenames[@]}"; do
    name="${filenames[$i]}"
    q="${questions[$i]}"

    body=$(jq -n --arg q "$q" '{question: $q}')

    curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "$body" \
        | jq > "$OUT_DIR/${name}.json"

    chunks=$(jq -r '.chunks_used' "$OUT_DIR/${name}.json")
    echo "  saved: ${name}.json  (chunks_used: ${chunks})"
done

echo ""
echo "Done. ${#filenames[@]} files in $OUT_DIR"
