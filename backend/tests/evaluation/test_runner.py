"""
RAG Test Runner for automated evaluation.

This module provides infrastructure for running automated RAG evaluation tests
using the golden test dataset and RAGAS metrics.
"""

import asyncio
from typing import List, Dict, Any, Optional
from src.core.services.query_service import QueryService
from src.core.evaluation.rag_evaluator import RAGEvaluator
from .test_datasets import ALL_TESTS, RAGTestCase
import time
import logging

logger = logging.getLogger(__name__)


class RAGTestRunner:
    """Runs evaluation test suite against the RAG system."""

    def __init__(self, query_service: QueryService):
        """
        Initialize test runner.

        Args:
            query_service: QueryService instance to test
        """
        self.query_service = query_service
        self.evaluator = RAGEvaluator()

    async def run_test(self, test_case: RAGTestCase) -> Dict[str, Any]:
        """
        Run a single test case.

        Args:
            test_case: Test case to execute

        Returns:
            Test result with scores and metadata
        """
        logger.info(f"Running test: {test_case.id} - {test_case.query}")
        start_time = time.time()

        try:
            # Execute query
            result = await self.query_service.answer_query(
                query_text=test_case.query,
                collection_names=test_case.collections,
                final_k=10
            )

            # Evaluate response
            scores = await self.evaluator.evaluate_response(
                query=test_case.query,
                response=result["response"],
                context=[c["content"] for c in result["context"]],
                ground_truth=test_case.ground_truth
            )

            # Check required keywords
            response_lower = result["response"].lower()
            keywords_found = [
                kw for kw in test_case.required_context_keywords
                if kw.lower() in response_lower
            ]

            # Check domain detection
            detected_domain = result.get("metadata", {}).get("detected_domain")
            domain_correct = (detected_domain == test_case.expected_domain)

            # Calculate overall score
            overall_score = self.evaluator.get_overall_score(scores)

            # Determine pass/fail
            passed = (
                scores["faithfulness"] >= (1 - test_case.max_hallucination_score) and
                scores["answer_relevancy"] >= test_case.min_relevancy_score and
                len(keywords_found) >= len(test_case.required_context_keywords) * 0.7 and
                domain_correct
            )

            duration = time.time() - start_time

            # Get failure reasons if failed
            failure_reasons = []
            if not passed:
                failure_reasons = self.evaluator.get_failure_reasons(scores)
                if not domain_correct:
                    failure_reasons.append(
                        f"domain_mismatch: expected={test_case.expected_domain}, got={detected_domain}"
                    )
                if len(keywords_found) < len(test_case.required_context_keywords) * 0.7:
                    missing = list(set(test_case.required_context_keywords) - set(keywords_found))
                    failure_reasons.append(f"missing_keywords: {missing}")

            return {
                "test_id": test_case.id,
                "query": test_case.query,
                "response": result["response"],
                "expected_domain": test_case.expected_domain,
                "detected_domain": detected_domain,
                "domain_correct": domain_correct,
                "scores": scores,
                "overall_score": overall_score,
                "keywords_found": keywords_found,
                "keywords_missing": list(
                    set(test_case.required_context_keywords) - set(keywords_found)
                ),
                "passed": passed,
                "failure_reasons": failure_reasons,
                "duration": duration,
                "metadata": test_case.metadata,
                "context_count": len(result["context"])
            }

        except Exception as e:
            logger.error(f"Test {test_case.id} failed with error: {e}", exc_info=True)
            return {
                "test_id": test_case.id,
                "query": test_case.query,
                "passed": False,
                "error": str(e),
                "failure_reasons": [f"exception: {str(e)}"],
                "duration": time.time() - start_time,
                "metadata": test_case.metadata
            }

    async def run_suite(
        self,
        test_cases: Optional[List[RAGTestCase]] = None,
        parallel: bool = False,
        max_parallel: int = 5
    ) -> Dict[str, Any]:
        """
        Run full test suite.

        Args:
            test_cases: Optional list of test cases (defaults to ALL_TESTS)
            parallel: Whether to run tests in parallel
            max_parallel: Maximum number of parallel tests

        Returns:
            Test suite results with summary statistics
        """
        if test_cases is None:
            test_cases = ALL_TESTS

        logger.info(f"Running {len(test_cases)} tests (parallel={parallel})...")
        start_time = time.time()

        if parallel:
            # Run tests in parallel with semaphore to limit concurrency
            semaphore = asyncio.Semaphore(max_parallel)
            
            async def run_with_semaphore(test):
                async with semaphore:
                    return await self.run_test(test)
            
            tasks = [run_with_semaphore(test) for test in test_cases]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            results = [
                r if not isinstance(r, Exception) else {
                    "test_id": "unknown",
                    "passed": False,
                    "error": str(r),
                    "failure_reasons": [f"exception: {str(r)}"]
                }
                for r in results
            ]
        else:
            # Run tests sequentially
            results = []
            for i, test in enumerate(test_cases, 1):
                logger.info(f"Progress: {i}/{len(test_cases)}")
                result = await self.run_test(test)
                results.append(result)

        # Calculate summary statistics
        total = len(results)
        passed = sum(1 for r in results if r.get("passed", False))
        failed = total - passed

        # Group failures by reason
        failures_by_metric = {}
        for r in results:
            if not r.get("passed", False):
                for reason in r.get("failure_reasons", []):
                    metric = reason.split(":")[0]
                    failures_by_metric[metric] = failures_by_metric.get(metric, 0) + 1

        # Category breakdown
        category_stats = {}
        for r in results:
            category = r.get("metadata", {}).get("category", "unknown")
            if category not in category_stats:
                category_stats[category] = {"total": 0, "passed": 0, "failed": 0}
            category_stats[category]["total"] += 1
            if r.get("passed", False):
                category_stats[category]["passed"] += 1
            else:
                category_stats[category]["failed"] += 1

        # Domain breakdown
        domain_stats = {}
        for r in results:
            domain = r.get("expected_domain", "unknown")
            if domain not in domain_stats:
                domain_stats[domain] = {"total": 0, "passed": 0, "failed": 0}
            domain_stats[domain]["total"] += 1
            if r.get("passed", False):
                domain_stats[domain]["passed"] += 1
            else:
                domain_stats[domain]["failed"] += 1

        # Difficulty breakdown
        difficulty_stats = {}
        for r in results:
            difficulty = r.get("metadata", {}).get("difficulty", "unknown")
            if difficulty not in difficulty_stats:
                difficulty_stats[difficulty] = {"total": 0, "passed": 0, "failed": 0}
            difficulty_stats[difficulty]["total"] += 1
            if r.get("passed", False):
                difficulty_stats[difficulty]["passed"] += 1
            else:
                difficulty_stats[difficulty]["failed"] += 1

        # Average scores
        avg_scores = {}
        score_metrics = ["faithfulness", "answer_relevancy", "context_precision", 
                        "context_recall", "context_relevancy", "overall_score"]
        for metric in score_metrics:
            scores = [r.get("scores", {}).get(metric, r.get(metric, 0)) 
                     for r in results if "scores" in r or metric in r]
            avg_scores[metric] = sum(scores) / len(scores) if scores else 0.0

        duration = time.time() - start_time

        summary = {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / total if total > 0 else 0,
            "duration": duration,
            "avg_duration_per_test": duration / total if total > 0 else 0,
            "failures_by_metric": failures_by_metric,
            "category_stats": category_stats,
            "domain_stats": domain_stats,
            "difficulty_stats": difficulty_stats,
            "average_scores": avg_scores,
            "results": results
        }

        logger.info(
            f"Test suite completed: {passed}/{total} passed "
            f"({summary['pass_rate']*100:.1f}%) in {duration:.2f}s"
        )
        
        return summary

    def print_summary(self, summary: Dict[str, Any]) -> None:
        """
        Print formatted test summary to console.

        Args:
            summary: Test suite summary from run_suite()
        """
        print("\n" + "="*80)
        print("RAG EVALUATION TEST RESULTS")
        print("="*80)
        
        # Overall results
        print(f"\n📊 OVERALL RESULTS:")
        print(f"  Total Tests: {summary['total_tests']}")
        print(f"  ✅ Passed: {summary['passed']} ({summary['pass_rate']*100:.1f}%)")
        print(f"  ❌ Failed: {summary['failed']}")
        print(f"  ⏱️  Duration: {summary['duration']:.2f}s")
        print(f"  ⚡ Avg per test: {summary['avg_duration_per_test']:.2f}s")
        
        # Average scores
        print(f"\n📈 AVERAGE SCORES:")
        for metric, score in summary['average_scores'].items():
            emoji = "✅" if score >= 0.7 else "⚠️" if score >= 0.5 else "❌"
            print(f"  {emoji} {metric}: {score:.3f}")
        
        # Domain breakdown
        print(f"\n🏷️  DOMAIN BREAKDOWN:")
        for domain, stats in summary['domain_stats'].items():
            pass_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"  {domain}: {stats['passed']}/{stats['total']} ({pass_rate:.1f}%)")
        
        # Category breakdown
        print(f"\n📁 CATEGORY BREAKDOWN:")
        for category, stats in summary['category_stats'].items():
            pass_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"  {category}: {stats['passed']}/{stats['total']} ({pass_rate:.1f}%)")
        
        # Difficulty breakdown
        print(f"\n⚙️  DIFFICULTY BREAKDOWN:")
        for difficulty, stats in summary['difficulty_stats'].items():
            pass_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"  {difficulty}: {stats['passed']}/{stats['total']} ({pass_rate:.1f}%)")
        
        # Failure analysis
        if summary['failures_by_metric']:
            print(f"\n❌ FAILURE ANALYSIS:")
            for metric, count in sorted(summary['failures_by_metric'].items(), 
                                       key=lambda x: x[1], reverse=True):
                print(f"  {metric}: {count} failures")
        
        # Failed tests detail
        failed_tests = [r for r in summary['results'] if not r.get('passed', False)]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for r in failed_tests[:10]:  # Show first 10
                print(f"\n  Test ID: {r['test_id']}")
                print(f"  Query: {r['query']}")
                if 'error' in r:
                    print(f"  Error: {r['error']}")
                else:
                    print(f"  Reasons: {', '.join(r.get('failure_reasons', []))}")
            
            if len(failed_tests) > 10:
                print(f"\n  ... and {len(failed_tests) - 10} more failed tests")
        
        print("\n" + "="*80 + "\n")
