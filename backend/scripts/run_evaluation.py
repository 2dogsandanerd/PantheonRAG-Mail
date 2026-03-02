#!/usr/bin/env python3
"""
RAG Evaluation CLI Tool.

This script runs automated RAG evaluation tests using the golden test dataset.
Results are printed to console and optionally saved to JSON.

Usage:
    # Run all tests
    python scripts/run_evaluation.py

    # Run only product tests
    python scripts/run_evaluation.py --domain PRODUKTE

    # Run only pricing category tests
    python scripts/run_evaluation.py --category pricing

    # Run only easy tests
    python scripts/run_evaluation.py --difficulty easy

    # Run tests in parallel (faster)
    python scripts/run_evaluation.py --parallel --max-parallel 10

    # Save results to custom file
    python scripts/run_evaluation.py --output my_results.json

    # Run specific test by ID
    python scripts/run_evaluation.py --test-id PROD-001
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.services.query_service import QueryService
from src.core.config import Config
from tests.evaluation.test_runner import RAGTestRunner
from tests.evaluation.test_datasets import (
    ALL_TESTS, 
    get_tests_by_category, 
    get_tests_by_domain, 
    get_tests_by_difficulty,
    get_test_by_id,
    get_test_statistics
)
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run RAG evaluation tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Test selection
    parser.add_argument(
        "--category", 
        help="Filter by category (e.g., pricing, shipping, troubleshooting)"
    )
    parser.add_argument(
        "--domain", 
        help="Filter by domain (e.g., PRODUKTE, KUNDE_SERVICE, SUPPORT)"
    )
    parser.add_argument(
        "--difficulty", 
        choices=["easy", "medium", "hard"],
        help="Filter by difficulty level"
    )
    parser.add_argument(
        "--test-id",
        help="Run a specific test by ID (e.g., PROD-001)"
    )
    
    # Execution options
    parser.add_argument(
        "--parallel", 
        action="store_true",
        help="Run tests in parallel (faster but more resource-intensive)"
    )
    parser.add_argument(
        "--max-parallel",
        type=int,
        default=5,
        help="Maximum number of parallel tests (default: 5)"
    )
    
    # Output options
    parser.add_argument(
        "--output", 
        default="evaluation_results.json",
        help="Output JSON file (default: evaluation_results.json)"
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save results to file"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    # Quality gate
    parser.add_argument(
        "--min-pass-rate",
        type=float,
        default=0.9,
        help="Minimum pass rate for success exit code (default: 0.9)"
    )
    
    # Statistics
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show test dataset statistics and exit"
    )
    
    return parser.parse_args()


def print_test_statistics():
    """Print statistics about the test dataset."""
    stats = get_test_statistics()
    
    print("\n" + "="*80)
    print("RAG TEST DATASET STATISTICS")
    print("="*80)
    
    print(f"\n📊 Total Tests: {stats['total_tests']}")
    
    print(f"\n🏷️  By Domain:")
    for domain, count in sorted(stats['by_domain'].items()):
        print(f"  {domain}: {count} tests")
    
    print(f"\n📁 By Category:")
    for category, count in sorted(stats['by_category'].items()):
        print(f"  {category}: {count} tests")
    
    print(f"\n⚙️  By Difficulty:")
    for difficulty, count in sorted(stats['by_difficulty'].items()):
        print(f"  {difficulty}: {count} tests")
    
    print("\n" + "="*80 + "\n")


async def main():
    """Main execution function."""
    args = parse_args()
    
    # Setup verbose logging if requested
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Show statistics and exit if requested
    if args.stats:
        print_test_statistics()
        return 0
    
    # Filter tests based on arguments
    if args.test_id:
        test = get_test_by_id(args.test_id)
        if not test:
            print(f"❌ Error: Test ID '{args.test_id}' not found")
            return 1
        tests = [test]
        print(f"Running single test: {args.test_id}")
    elif args.category:
        tests = get_tests_by_category(args.category)
        if not tests:
            print(f"❌ Error: No tests found for category '{args.category}'")
            return 1
        print(f"Running {len(tests)} tests for category: {args.category}")
    elif args.domain:
        tests = get_tests_by_domain(args.domain)
        if not tests:
            print(f"❌ Error: No tests found for domain '{args.domain}'")
            return 1
        print(f"Running {len(tests)} tests for domain: {args.domain}")
    elif args.difficulty:
        tests = get_tests_by_difficulty(args.difficulty)
        if not tests:
            print(f"❌ Error: No tests found for difficulty '{args.difficulty}'")
            return 1
        print(f"Running {len(tests)} tests for difficulty: {args.difficulty}")
    else:
        tests = ALL_TESTS
        print(f"Running all {len(tests)} tests")
    
    print(f"Parallel execution: {args.parallel}")
    if args.parallel:
        print(f"Max parallel tests: {args.max_parallel}")
    print("="*80 + "\n")
    
    # Initialize services
    try:
        config = Config()
        query_service = QueryService(config=config)
        runner = RAGTestRunner(query_service)
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}", exc_info=True)
        print(f"❌ Error: Failed to initialize services: {e}")
        return 1
    
    # Run tests
    try:
        results = await runner.run_suite(
            tests, 
            parallel=args.parallel,
            max_parallel=args.max_parallel
        )
    except Exception as e:
        logger.error(f"Test suite failed: {e}", exc_info=True)
        print(f"❌ Error: Test suite failed: {e}")
        return 1
    
    # Print summary
    runner.print_summary(results)
    
    # Save results to file
    if not args.no_save:
        try:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Results saved to: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}", exc_info=True)
            print(f"⚠️  Warning: Failed to save results: {e}")
    
    # Determine exit code based on pass rate
    pass_rate = results['pass_rate']
    if pass_rate >= args.min_pass_rate:
        print(f"\n✅ SUCCESS: Pass rate {pass_rate*100:.1f}% >= {args.min_pass_rate*100:.1f}%")
        return 0
    else:
        print(f"\n❌ FAILURE: Pass rate {pass_rate*100:.1f}% < {args.min_pass_rate*100:.1f}%")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
