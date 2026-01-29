#!/bin/bash

# MasterBot Platform Test Runner
# Usage: ./run_tests.sh [options]
#
# Options:
#   all         - Run all tests
#   unit        - Run only unit tests
#   integration - Run only integration tests
#   coverage    - Run with coverage report
#   parser      - Run only parser tests
#   service     - Run only service tests
#   api         - Run only API tests
#   fast        - Run quick smoke tests
#   help        - Show this help message

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Ensure virtual environment is activated
if [[ -z "${VIRTUAL_ENV}" ]]; then
    if [[ -f "venv/bin/activate" ]]; then
        echo -e "${YELLOW}Activating virtual environment...${NC}"
        source venv/bin/activate
    else
        echo -e "${YELLOW}Warning: No virtual environment found. Using system Python.${NC}"
    fi
fi

# Install test dependencies if needed
install_deps() {
    echo -e "${YELLOW}Installing test dependencies...${NC}"
    pip install -r requirements-test.txt -q
}

# Run all tests
run_all() {
    echo -e "${GREEN}Running all tests...${NC}"
    python -m pytest tests/ -v --tb=short
}

# Run unit tests only
run_unit() {
    echo -e "${GREEN}Running unit tests...${NC}"
    python -m pytest tests/unit/ -v --tb=short -m unit
}

# Run integration tests only
run_integration() {
    echo -e "${GREEN}Running integration tests...${NC}"
    python -m pytest tests/integration/ -v --tb=short -m integration
}

# Run tests with coverage
run_coverage() {
    echo -e "${GREEN}Running tests with coverage...${NC}"
    python -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing
    echo -e "${GREEN}Coverage report generated in htmlcov/index.html${NC}"
}

# Run parser tests only
run_parser() {
    echo -e "${GREEN}Running parser tests...${NC}"
    python -m pytest tests/unit/*/test_parser.py -v --tb=short
}

# Run service tests only
run_service() {
    echo -e "${GREEN}Running service tests...${NC}"
    python -m pytest tests/unit/*/test_*service*.py -v --tb=short
}

# Run API tests only
run_api() {
    echo -e "${GREEN}Running API tests...${NC}"
    python -m pytest tests/unit/*/test_api.py -v --tb=short
}

# Run fast smoke tests
run_fast() {
    echo -e "${GREEN}Running fast smoke tests...${NC}"
    python -m pytest tests/unit/impulse_service/test_parser.py tests/unit/bablo_service/test_parser.py -v --tb=short -x
}

# Show help
show_help() {
    echo "MasterBot Platform Test Runner"
    echo ""
    echo "Usage: ./run_tests.sh [options]"
    echo ""
    echo "Options:"
    echo "  all         - Run all tests"
    echo "  unit        - Run only unit tests"
    echo "  integration - Run only integration tests"
    echo "  coverage    - Run with coverage report"
    echo "  parser      - Run only parser tests"
    echo "  service     - Run only service tests"
    echo "  api         - Run only API tests"
    echo "  fast        - Run quick smoke tests"
    echo "  install     - Install test dependencies"
    echo "  help        - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run_tests.sh all"
    echo "  ./run_tests.sh unit"
    echo "  ./run_tests.sh coverage"
    echo "  ./run_tests.sh parser"
}

# Main script
case "${1:-all}" in
    all)
        run_all
        ;;
    unit)
        run_unit
        ;;
    integration)
        run_integration
        ;;
    coverage)
        run_coverage
        ;;
    parser)
        run_parser
        ;;
    service)
        run_service
        ;;
    api)
        run_api
        ;;
    fast)
        run_fast
        ;;
    install)
        install_deps
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Unknown option: $1${NC}"
        show_help
        exit 1
        ;;
esac

echo -e "${GREEN}Done!${NC}"
