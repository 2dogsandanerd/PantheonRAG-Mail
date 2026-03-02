"""
Prometheus Metrics for RAG System.

This module defines all Prometheus metrics for monitoring the RAG pipeline:
- Query metrics (success/failure, latency, context chunks)
- Reranker metrics (usage, latency, score improvement)
- LLM metrics (tokens, cost, latency)
- System metrics (collections, documents)
"""

from prometheus_client import Counter, Histogram, Gauge


# ============================================================================
# QUERY METRICS
# ============================================================================

query_total = Counter(
    'rag_query_total',
    'Total RAG queries',
    ['status', 'domain', 'collections_count']
)

query_latency = Histogram(
    'rag_query_latency_seconds',
    'Query latency in seconds',
    ['stage'],  # retrieval, reranking, llm, total
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

query_context_chunks = Histogram(
    'rag_context_chunks',
    'Number of context chunks retrieved',
    buckets=[1, 5, 10, 20, 50, 100]
)


# ============================================================================
# RERANKER METRICS
# ============================================================================

reranker_enabled = Counter(
    'rag_reranker_usage_total',
    'Reranker usage count',
    ['enabled']
)

reranker_latency = Histogram(
    'rag_reranker_latency_seconds',
    'Reranker processing time',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

reranker_score_improvement = Histogram(
    'rag_reranker_score_delta',
    'Score improvement from reranking',
    buckets=[-0.5, -0.1, 0.0, 0.1, 0.2, 0.5, 1.0]
)


# ============================================================================
# LLM METRICS
# ============================================================================

llm_tokens_total = Counter(
    'rag_llm_tokens_total',
    'Total tokens used',
    ['provider', 'model', 'type']  # type: prompt, completion
)

llm_cost_usd = Counter(
    'rag_llm_cost_usd_total',
    'Estimated LLM cost in USD',
    ['provider', 'model']
)

llm_latency = Histogram(
    'rag_llm_latency_seconds',
    'LLM generation latency',
    ['provider', 'model'],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)


# ============================================================================
# SYSTEM METRICS
# ============================================================================

active_collections = Gauge(
    'rag_active_collections',
    'Number of active collections'
)

total_documents = Gauge(
    'rag_total_documents',
    'Total documents in all collections'
)


# ============================================================================
# EVALUATION METRICS (for future use)
# ============================================================================

evaluation_faithfulness = Histogram(
    'rag_evaluation_faithfulness',
    'Faithfulness score (hallucination detection)',
    buckets=[0.0, 0.5, 0.7, 0.8, 0.9, 0.95, 1.0]
)

evaluation_answer_relevancy = Histogram(
    'rag_evaluation_answer_relevancy',
    'Answer relevancy score',
    buckets=[0.0, 0.5, 0.7, 0.8, 0.9, 0.95, 1.0]
)

evaluation_failures = Counter(
    'rag_evaluation_failures_total',
    'Failed quality checks',
    ['metric']
)

evaluation_requests_total = Counter(
    'rag_evaluation_requests_total',
    'Total evaluation requests processed'
)

evaluation_latency_seconds = Histogram(
    'rag_evaluation_latency_seconds',
    'Latency of evaluation requests',
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0]
)


# ============================================================================
# CACHE METRICS (for future use)
# ============================================================================

cache_hits = Counter(
    'rag_cache_hits_total',
    'Cache hit count',
    ['cache_type']  # query, embedding
)

cache_misses = Counter(
    'rag_cache_misses_total',
    'Cache miss count',
    ['cache_type']
)
