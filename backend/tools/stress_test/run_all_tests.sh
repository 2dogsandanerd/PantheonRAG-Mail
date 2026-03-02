#!/bin/bash

# RAG System - Complete Test Suite Runner
# Runs all tests and generates a comprehensive report

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_DIR="./test_reports"
REPORT_FILE="${REPORT_DIR}/test_report_${TIMESTAMP}.log"
SUMMARY_FILE="${REPORT_DIR}/test_summary_${TIMESTAMP}.txt"

# Create report directory
mkdir -p "$REPORT_DIR"

# Header
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  RAG SYSTEM - TEST SUITE RUNNER${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Timestamp: $(date)"
echo "Report: $REPORT_FILE"
echo ""

# Function to print and log
log() {
    echo -e "$1" | tee -a "$REPORT_FILE"
}

# Function to check if backend is running
check_backend() {
    echo -e "${YELLOW}Checking backend...${NC}"
    if curl -s http://localhost:33800/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is running${NC}"
        return 0
    else
        echo -e "${RED}✗ Backend is NOT running${NC}"
        echo -e "${RED}  Please start the backend first:${NC}"
        echo -e "${RED}  cd frontend && npm start${NC}"
        return 1
    fi
}

# Check backend
if ! check_backend; then
    exit 1
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Starting Test Suite${NC}"
echo -e "${BLUE}========================================${NC}"
echo "" | tee "$REPORT_FILE"

# Test 1: Load Test
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$REPORT_FILE"
echo -e "${YELLOW}TEST 1/4: Load Test (High Concurrency)${NC}" | tee -a "$REPORT_FILE"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

python3 load_test.py 2>&1 | tee -a "$REPORT_FILE"
LOAD_TEST_STATUS=$?

if [ $LOAD_TEST_STATUS -eq 0 ]; then
    echo -e "${GREEN}✓ Load Test PASSED${NC}" | tee -a "$REPORT_FILE"
else
    echo -e "${RED}✗ Load Test FAILED${NC}" | tee -a "$REPORT_FILE"
fi

echo "" | tee -a "$REPORT_FILE"

# Test 2: Endurance Test
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$REPORT_FILE"
echo -e "${YELLOW}TEST 2/4: Endurance Test (Stability)${NC}" | tee -a "$REPORT_FILE"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

python3 endurance_test.py 2>&1 | tee -a "$REPORT_FILE"
ENDURANCE_TEST_STATUS=$?

if [ $ENDURANCE_TEST_STATUS -eq 0 ]; then
    echo -e "${GREEN}✓ Endurance Test PASSED${NC}" | tee -a "$REPORT_FILE"
else
    echo -e "${RED}✗ Endurance Test FAILED${NC}" | tee -a "$REPORT_FILE"
fi

echo "" | tee -a "$REPORT_FILE"

# Test 3: Memory Leak Test (Quick 10-minute version)
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$REPORT_FILE"
echo -e "${YELLOW}TEST 3/4: Memory Leak Test (10 min)${NC}" | tee -a "$REPORT_FILE"
echo -e "${YELLOW}NOTE: For full 60-min test, edit memory_leak_test.py${NC}" | tee -a "$REPORT_FILE"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

python3 memory_leak_test.py 2>&1 | tee -a "$REPORT_FILE"
MEMORY_TEST_STATUS=$?

if [ $MEMORY_TEST_STATUS -eq 0 ]; then
    echo -e "${GREEN}✓ Memory Leak Test PASSED${NC}" | tee -a "$REPORT_FILE"
else
    echo -e "${RED}✗ Memory Leak Test FAILED${NC}" | tee -a "$REPORT_FILE"
fi

echo "" | tee -a "$REPORT_FILE"

# Test 4: Chaos Test (Circuit Breaker only - safe)
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$REPORT_FILE"
echo -e "${YELLOW}TEST 4/4: Chaos Test (Resilience)${NC}" | tee -a "$REPORT_FILE"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

python3 chaos_test.py 2>&1 | tee -a "$REPORT_FILE"
CHAOS_TEST_STATUS=$?

if [ $CHAOS_TEST_STATUS -eq 0 ]; then
    echo -e "${GREEN}✓ Chaos Test PASSED${NC}" | tee -a "$REPORT_FILE"
else
    echo -e "${RED}✗ Chaos Test FAILED${NC}" | tee -a "$REPORT_FILE"
fi

echo "" | tee -a "$REPORT_FILE"

# Generate Summary
echo -e "${BLUE}========================================${NC}" | tee -a "$REPORT_FILE"
echo -e "${BLUE}  TEST SUITE SUMMARY${NC}" | tee -a "$REPORT_FILE"
echo -e "${BLUE}========================================${NC}" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# Count results
TOTAL_TESTS=4
PASSED_TESTS=0

[ $LOAD_TEST_STATUS -eq 0 ] && ((PASSED_TESTS++))
[ $ENDURANCE_TEST_STATUS -eq 0 ] && ((PASSED_TESTS++))
[ $MEMORY_TEST_STATUS -eq 0 ] && ((PASSED_TESTS++))
[ $CHAOS_TEST_STATUS -eq 0 ] && ((PASSED_TESTS++))

echo "Completed: $(date)" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"
echo "Test Results:" | tee -a "$REPORT_FILE"
echo "  Total Tests:  $TOTAL_TESTS" | tee -a "$REPORT_FILE"
echo "  Passed:       $PASSED_TESTS" | tee -a "$REPORT_FILE"
echo "  Failed:       $((TOTAL_TESTS - PASSED_TESTS))" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# Individual results
echo "Individual Test Results:" | tee -a "$REPORT_FILE"
if [ $LOAD_TEST_STATUS -eq 0 ]; then
    echo -e "  ${GREEN}✓${NC} Load Test" | tee -a "$REPORT_FILE"
else
    echo -e "  ${RED}✗${NC} Load Test" | tee -a "$REPORT_FILE"
fi

if [ $ENDURANCE_TEST_STATUS -eq 0 ]; then
    echo -e "  ${GREEN}✓${NC} Endurance Test" | tee -a "$REPORT_FILE"
else
    echo -e "  ${RED}✗${NC} Endurance Test" | tee -a "$REPORT_FILE"
fi

if [ $MEMORY_TEST_STATUS -eq 0 ]; then
    echo -e "  ${GREEN}✓${NC} Memory Leak Test" | tee -a "$REPORT_FILE"
else
    echo -e "  ${RED}✗${NC} Memory Leak Test" | tee -a "$REPORT_FILE"
fi

if [ $CHAOS_TEST_STATUS -eq 0 ]; then
    echo -e "  ${GREEN}✓${NC} Chaos Test" | tee -a "$REPORT_FILE"
else
    echo -e "  ${RED}✗${NC} Chaos Test" | tee -a "$REPORT_FILE"
fi

echo "" | tee -a "$REPORT_FILE"

# Final verdict
if [ $PASSED_TESTS -eq $TOTAL_TESTS ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$REPORT_FILE"
    echo -e "${GREEN}  ✓ ALL TESTS PASSED${NC}" | tee -a "$REPORT_FILE"
    echo -e "${GREEN}  System is PRODUCTION READY${NC}" | tee -a "$REPORT_FILE"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$REPORT_FILE"
    EXIT_CODE=0
elif [ $PASSED_TESTS -ge 3 ]; then
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$REPORT_FILE"
    echo -e "${YELLOW}  ⚠ MOSTLY PASSED ($PASSED_TESTS/$TOTAL_TESTS)${NC}" | tee -a "$REPORT_FILE"
    echo -e "${YELLOW}  Review failed tests before deployment${NC}" | tee -a "$REPORT_FILE"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$REPORT_FILE"
    EXIT_CODE=0
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$REPORT_FILE"
    echo -e "${RED}  ✗ MULTIPLE TESTS FAILED ($PASSED_TESTS/$TOTAL_TESTS)${NC}" | tee -a "$REPORT_FILE"
    echo -e "${RED}  System requires debugging${NC}" | tee -a "$REPORT_FILE"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$REPORT_FILE"
    EXIT_CODE=1
fi

echo "" | tee -a "$REPORT_FILE"
echo "Full report saved to: $REPORT_FILE" | tee -a "$REPORT_FILE"
echo ""

# Create a concise summary file
cat > "$SUMMARY_FILE" << EOF
RAG System Test Suite - Summary Report
========================================
Date: $(date)
Report: $REPORT_FILE

Test Results: $PASSED_TESTS/$TOTAL_TESTS PASSED

Individual Tests:
$([ $LOAD_TEST_STATUS -eq 0 ] && echo "  ✓ Load Test" || echo "  ✗ Load Test")
$([ $ENDURANCE_TEST_STATUS -eq 0 ] && echo "  ✓ Endurance Test" || echo "  ✗ Endurance Test")
$([ $MEMORY_TEST_STATUS -eq 0 ] && echo "  ✓ Memory Leak Test" || echo "  ✗ Memory Leak Test")
$([ $CHAOS_TEST_STATUS -eq 0 ] && echo "  ✓ Chaos Test" || echo "  ✗ Chaos Test")

$(if [ $PASSED_TESTS -eq $TOTAL_TESTS ]; then
    echo "Verdict: ✓ PRODUCTION READY"
elif [ $PASSED_TESTS -ge 3 ]; then
    echo "Verdict: ⚠ MOSTLY READY (review failures)"
else
    echo "Verdict: ✗ NOT READY (debug required)"
fi)
EOF

echo "Summary saved to: $SUMMARY_FILE"
echo ""

exit $EXIT_CODE
