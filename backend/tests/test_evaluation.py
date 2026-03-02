import pytest
from unittest.mock import patch, MagicMock
from src.api.v1.evaluation.models import EvaluationRequest
from src.api.v1.evaluation.service import evaluate_ragas

@pytest.mark.asyncio
async def test_evaluate_ragas_success():
    # Mock ragas.evaluate return value
    mock_result = MagicMock()
    mock_result.faithfulness = 0.9
    mock_result.relevance = 0.8
    mock_result.answer_correctness = 0.85
    mock_result.context_precision = 0.7
    mock_result.context_recall = 0.6

    # Patch 'evaluate' where it is imported in service.py
    with patch("src.api.v1.evaluation.service.evaluate", return_value=mock_result) as mock_evaluate:
        request = EvaluationRequest(
            generated=["answer"],
            reference=["reference"]
        )
        result = await evaluate_ragas(request)
        
        assert result.scores["faithfulness"] == 0.9
        assert result.scores["relevance"] == 0.8
        assert result.scores["answer_correctness"] == 0.85
        
        # Verify evaluate was called correctly (via kwargs as used in service)
        mock_evaluate.assert_called_once_with(
            generated_texts=["answer"],
            reference_texts=["reference"]
        )

@pytest.mark.asyncio
async def test_evaluate_ragas_validation_error():
    request = EvaluationRequest(
        generated=["answer"],
        reference=["ref1", "ref2"] # Mismatch
    )
    with pytest.raises(ValueError):
        await evaluate_ragas(request)
