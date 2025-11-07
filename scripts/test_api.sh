#!/bin/bash
# Script to test the DevAgent API

set -e

API_URL="${API_URL:-http://localhost:8000}"

echo "Testing DevAgent API at $API_URL"
echo "================================"

# Test health endpoint
echo -e "\n1. Testing health endpoint..."
curl -s "$API_URL/health" | jq .

# Submit a test query
echo -e "\n2. Submitting natural language query..."
RESPONSE=$(curl -s -X POST "$API_URL/submit_nl" \
  -H "Content-Type: application/json" \
  -d '{"query": "Create an M/M/1 queue model with exponential arrivals and service"}')

echo "$RESPONSE" | jq .

# Extract job ID
JOB_ID=$(echo "$RESPONSE" | jq -r '.job_id')

if [ "$JOB_ID" = "null" ]; then
    echo "Error: Failed to get job ID"
    exit 1
fi

echo "Job ID: $JOB_ID"

# Check status
echo -e "\n3. Checking job status..."
sleep 2
curl -s "$API_URL/status/$JOB_ID" | jq .

# Wait for completion
echo -e "\n4. Waiting for job completion..."
MAX_ATTEMPTS=10
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    STATUS=$(curl -s "$API_URL/status/$JOB_ID" | jq -r '.status')
    echo "Attempt $((ATTEMPT+1))/$MAX_ATTEMPTS - Status: $STATUS"

    if [ "$STATUS" = "SUCCESS" ] || [ "$STATUS" = "FAILED" ]; then
        break
    fi

    ATTEMPT=$((ATTEMPT+1))
    sleep 2
done

# Get the generated specification
echo -e "\n5. Retrieving generated specification..."
curl -s "$API_URL/spec/$JOB_ID" | jq .

echo -e "\n================================"
echo "API test completed!"
