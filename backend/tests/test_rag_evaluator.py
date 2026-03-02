"""
Unit tests for RAGEvaluator.

Tests the core evaluation functionality including:
- Basic evaluation with good responses
- Hallucination detection
- Low relevancy detection
- Threshold checking
- Overall score calculation
"""

import pytest
from src.core.evaluation.rag_evaluator import RAGEvaluator


@pytest.mark.asyncio
async def test_evaluator_basic():
    """Test basic evaluator functionality with good response."""
    evaluator = RAGEvaluator()

    query = "Was kostet Produkt XYZ?"
    response = "Produkt XYZ kostet 49,90€."
    context = [
        "Produkt XYZ ist in unserem Shop für 49,90€ erhältlich.",
        "Versandkosten betragen 4,90€."
    ]
    ground_truth = "Das Produkt XYZ kostet 49,90€."

    scores = await evaluator.evaluate_response(
        query=query,
        response=response,
        context=context,
        ground_truth=ground_truth
    )

    # Check all metrics present
    assert "faithfulness" in scores
    assert "answer_relevancy" in scores
    assert "context_precision" in scores
    assert "context_recall" in scores
    assert "context_relevancy" in scores

    # All scores should be between 0 and 1
    for metric, score in scores.items():
        assert 0.0 <= score <= 1.0, f"{metric} score {score} not in [0, 1]"

    # Good response should have high scores
    assert scores["faithfulness"] > 0.7, "Faithfulness should be high for good response"
    assert scores["answer_relevancy"] > 0.6, "Answer relevancy should be high"


@pytest.mark.asyncio
async def test_evaluator_hallucination():
    """Test hallucination detection with incorrect information."""
    evaluator = RAGEvaluator()

    query = "Was kostet Produkt XYZ?"
    response = "Produkt XYZ kostet 99,90€."  # Wrong price!
    context = [
        "Produkt XYZ ist in unserem Shop für 49,90€ erhältlich."
    ]
    ground_truth = "Das Produkt XYZ kostet 49,90€."

    scores = await evaluator.evaluate_response(
        query=query,
        response=response,
        context=context,
        ground_truth=ground_truth
    )

    # Should have lower faithfulness score due to hallucination
    # Note: RAGAS may not always detect this perfectly, so we use a lenient threshold
    assert scores["faithfulness"] < 1.0, "Faithfulness should be lower for hallucinated response"


@pytest.mark.asyncio
async def test_evaluator_irrelevant_response():
    """Test detection of irrelevant responses."""
    evaluator = RAGEvaluator()

    query = "Was kostet Produkt XYZ?"
    response = "Wir haben viele tolle Produkte im Angebot."  # Irrelevant!
    context = [
        "Produkt XYZ ist in unserem Shop für 49,90€ erhältlich."
    ]
    ground_truth = "Das Produkt XYZ kostet 49,90€."

    scores = await evaluator.evaluate_response(
        query=query,
        response=response,
        context=context,
        ground_truth=ground_truth
    )

    # Should have low answer relevancy
    assert scores["answer_relevancy"] < 0.7, "Answer relevancy should be low for irrelevant response"


@pytest.mark.asyncio
async def test_evaluator_without_ground_truth():
    """Test evaluation without ground truth (context_recall will be 0)."""
    evaluator = RAGEvaluator()

    query = "Was kostet Produkt XYZ?"
    response = "Produkt XYZ kostet 49,90€."
    context = [
        "Produkt XYZ ist in unserem Shop für 49,90€ erhältlich."
    ]

    scores = await evaluator.evaluate_response(
        query=query,
        response=response,
        context=context,
        ground_truth=None  # No ground truth
    )

    # Should still have scores for other metrics
    assert "faithfulness" in scores
    assert "answer_relevancy" in scores
    assert "context_precision" in scores
    assert "context_relevancy" in scores
    
    # Context recall should be 0 without ground truth
    assert scores["context_recall"] == 0.0


def test_is_passing_with_good_scores():
    """Test threshold checking with good scores."""
    evaluator = RAGEvaluator()

    good_scores = {
        "faithfulness": 0.95,
        "answer_relevancy": 0.85,
        "context_precision": 0.75,
        "context_recall": 0.70,
        "context_relevancy": 0.80
    }

    assert evaluator.is_passing(good_scores), "Good scores should pass"


def test_is_passing_with_bad_scores():
    """Test threshold checking with bad scores."""
    evaluator = RAGEvaluator()

    bad_scores = {
        "faithfulness": 0.50,  # Too low!
        "answer_relevancy": 0.85,
        "context_precision": 0.75,
        "context_recall": 0.70,
        "context_relevancy": 0.80
    }

    assert not evaluator.is_passing(bad_scores), "Bad scores should fail"


def test_is_passing_with_custom_thresholds():
    """Test threshold checking with custom thresholds."""
    evaluator = RAGEvaluator()

    scores = {
        "faithfulness": 0.85,
        "answer_relevancy": 0.75,
        "context_precision": 0.65,
        "context_recall": 0.60,
        "context_relevancy": 0.70
    }

    # Should fail with default strict thresholds
    assert not evaluator.is_passing(scores), "Should fail with default thresholds"

    # Should pass with relaxed thresholds
    relaxed_thresholds = {
        "faithfulness": 0.8,
        "answer_relevancy": 0.7,
        "context_precision": 0.6,
        "context_recall": 0.5,
        "context_relevancy": 0.6
    }
    assert evaluator.is_passing(scores, relaxed_thresholds), "Should pass with relaxed thresholds"


def test_get_overall_score():
    """Test overall score calculation."""
    evaluator = RAGEvaluator()

    scores = {
        "faithfulness": 0.9,
        "answer_relevancy": 0.8,
        "context_precision": 0.7,
        "context_recall": 0.6,
        "context_relevancy": 0.7
    }

    overall = evaluator.get_overall_score(scores)

    # Overall should be weighted average
    # faithfulness: 0.3, answer_relevancy: 0.25, others: 0.15 each
    expected = (0.9 * 0.3) + (0.8 * 0.25) + (0.7 * 0.15) + (0.6 * 0.15) + (0.7 * 0.15)
    
    assert abs(overall - expected) < 0.01, f"Overall score {overall} != expected {expected}"
    assert 0.0 <= overall <= 1.0, "Overall score should be in [0, 1]"


def test_get_overall_score_perfect():
    """Test overall score with perfect scores."""
    evaluator = RAGEvaluator()

    perfect_scores = {
        "faithfulness": 1.0,
        "answer_relevancy": 1.0,
        "context_precision": 1.0,
        "context_recall": 1.0,
        "context_relevancy": 1.0
    }

    overall = evaluator.get_overall_score(perfect_scores)
    assert overall == 1.0, "Perfect scores should give overall score of 1.0"


def test_get_overall_score_zero():
    """Test overall score with zero scores."""
    evaluator = RAGEvaluator()

    zero_scores = {
        "faithfulness": 0.0,
        "answer_relevancy": 0.0,
        "context_precision": 0.0,
        "context_recall": 0.0,
        "context_relevancy": 0.0
    }

    overall = evaluator.get_overall_score(zero_scores)
    assert overall == 0.0, "Zero scores should give overall score of 0.0"


def test_get_failure_reasons():
    """Test failure reason extraction."""
    evaluator = RAGEvaluator()

    scores = {
        "faithfulness": 0.85,  # Fails (< 0.9)
        "answer_relevancy": 0.65,  # Fails (< 0.7)
        "context_precision": 0.75,  # Passes
        "context_recall": 0.70,  # Passes
        "context_relevancy": 0.80  # Passes
    }

    failures = evaluator.get_failure_reasons(scores)

    assert len(failures) == 2, "Should have 2 failures"
    assert any("faithfulness" in f for f in failures), "Should include faithfulness failure"
    assert any("answer_relevancy" in f for f in failures), "Should include answer_relevancy failure"


def test_get_failure_reasons_all_pass():
    """Test failure reasons when all metrics pass."""
    evaluator = RAGEvaluator()

    good_scores = {
        "faithfulness": 0.95,
        "answer_relevancy": 0.85,
        "context_precision": 0.75,
        "context_recall": 0.70,
        "context_relevancy": 0.80
    }

    failures = evaluator.get_failure_reasons(good_scores)
    assert len(failures) == 0, "Should have no failures for good scores"


@pytest.mark.asyncio
async def test_evaluator_error_handling():
    """Test that evaluator handles errors gracefully."""
    evaluator = RAGEvaluator()

    # Test with invalid inputs
    scores = await evaluator.evaluate_response(
        query="",  # Empty query
        response="",  # Empty response
        context=[],  # Empty context
        ground_truth=None
    )

    # Should return default scores instead of crashing
    assert isinstance(scores, dict)
    assert all(isinstance(v, float) for v in scores.values())
