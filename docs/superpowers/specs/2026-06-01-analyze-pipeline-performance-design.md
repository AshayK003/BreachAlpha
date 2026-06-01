# Analyze Pipeline Performance — Design Spec

**Date:** 2026-06-01
**Goal:** Make CSV/XLSX analysis 5-10x faster by parallelizing network I/O and CPU work without breaking existing functionality.

## Current Bottlenecks

| # | Bottleneck | Type | Impact |
|---|---|---|---|
| 1 | `/api/upload/analyze` runs stages 4-8 synchronously in async handler | Blocks event loop | All requests blocked during analysis |
| 2 | `fetch_market_data()` called per-event in sequential loop | Sequential I/O | N events = N sequential network calls |
| 3 | `fetch_stock_batch()` falls back to sequential per-ticker fetch | Sequential I/O | Each ticker ~1-5s |
| 4 | Ticker resolution in `preprocess_dataset()` per-row sequential | Sequential I/O | N rows = N sequential lookups |
| 5 | `compute_features_batch()` uses `ThreadPoolExecutor` for CPU work | GIL limits parallelism | No real parallelism on pandas/numpy |
| 6 | `predict_severity()` called per-row instead of batch | Inefficient | N predict calls vs 1 |

## Design: Approach A+B

### Change 1: Event Loop Fix

**File:** `breachalpha/server.py` — `/api/upload/analyze` endpoint

Wrap stages 4-8 in `asyncio.to_thread()`:

```python
# After preprocessing completes:
result = await asyncio.to_thread(
    _run_analysis_pipeline, tmp_path, result, start_date
)
```

New function `_run_analysis_pipeline()` contains stages 4-8 (ticker resolution, stock fetch, market fetch, feature computation, prediction). This keeps the FastAPI event loop free to handle other requests. Internal flow:

```
_run_analysis_pipeline(tmp_path, preprocess_result, start_date):
    1. Build tickers_needed + row_map from preprocessed data
    2. Parallel stock fetch via fetch_stock_batch() (Change 3)
    3. Build BreachEvent list, resolve tickers for missing data (Change 4)
    4. Parallel market data fetch (Change 2)
    5. Compute features via ProcessPoolExecutor (Change 5)
    6. Batch predict severity (Change 6)
    7. Return BatchResponse
```

### Change 2: Parallel Market Data Fetch

**File:** `breachalpha/server.py` — inside `_run_analysis_pipeline()`

Pre-fetch all unique benchmarks in parallel before feature computation:

```python
unique_benchmarks = set(e.benchmark for e in events)
market_data = {}
with ThreadPoolExecutor(max_workers=8) as pool:
    futures = {
        pool.submit(fetch_market_data, start_date, b): b
        for b in unique_benchmarks
    }
    for future in as_completed(futures):
        b = futures[future]
        market_data[b] = future.result()
```

Each event then uses the pre-fetched market data instead of calling `fetch_market_data()` individually.

### Change 3: Parallel Stock Data Fetch

**File:** `breachalpha/data_sources.py` — `DataFetcher.fetch_batch()`

When batch API fails, parallelize per-ticker fetches instead of sequential:

```python
# Current fallback:
for ticker in tickers:
    result[ticker] = self.fetch(ticker, ...)

# Fixed fallback:
with ThreadPoolExecutor(max_workers=8) as pool:
    results = {
        t: pool.submit(self.fetch, t, ...) for t in tickers
    }
    result = {t: f.result() for t, f in results.items()}
```

### Change 4: Parallel Ticker Resolution

**File:** `breachalpha/preprocessor.py` — `preprocess_dataset()`

Parallelize `resolve_ticker()` calls:

```python
# Current:
for row in df.itertuples():
    ticker = resolve_ticker(row.company)

# Fixed:
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=8) as pool:
    companies = df[company_col].tolist()
    tickers = list(pool.map(resolve_ticker, companies))
```

### Change 5: ProcessPoolExecutor for Feature Computation

**File:** `breachalpha/feature_engine.py` — `compute_features_batch()`

Replace `ThreadPoolExecutor` with `ProcessPoolExecutor` to bypass GIL:

```python
from concurrent.futures import ProcessPoolExecutor
from functools import partial

# Current:
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = {executor.submit(compute_features, e, c): e for e in events}

# Fixed:
worker = partial(compute_features, config=config)
with ProcessPoolExecutor(max_workers=min(4, len(events))) as executor:
    results = list(executor.map(worker, events))
```

**Prerequisite:** `BreachEvent` dataclass and stock DataFrames must be picklable. They are — dataclasses support pickle natively, and pandas DataFrames are designed for it.

**Graceful fallback:** If pickling fails, catch the error and fall back to sequential computation with a warning log.

### Change 6: Batch Prediction

**File:** `breachalpha/server.py` — inside `_run_analysis_pipeline()`

Replace per-row prediction with a single batch call:

```python
# Current:
for _, row in features_df.iterrows():
    prediction = predict_severity(row)

# Fixed:
feature_cols = [...FEATURE_COLS...]
all_features = features_df[feature_cols].fillna(0)
raw_predictions = model.predict(all_features)
# Map numeric predictions to severity labels: 0→low, 1→medium, 2→high, 3→critical
labels = {0: 'low', 1: 'medium', 2: 'high', 3: 'critical'}
predictions = [labels.get(int(p), 'medium') for p in raw_predictions]
```

The prediction probability distribution is also computed in batch via `model.predict_proba(all_features)`, then mapped to `BatchResultItem.probabilities`.

## Files Modified

| File | Changes |
|---|---|
| `breachalpha/server.py` | Wrap pipeline in `to_thread()`, parallel market fetch, batch prediction |
| `breachalpha/data_sources.py` | Parallel fallback in `fetch_batch()` |
| `breachalpha/preprocessor.py` | Parallel ticker resolution |
| `breachalpha/feature_engine.py` | `ProcessPoolExecutor` instead of `ThreadPoolExecutor` |

## Safety Constraints

1. **No breaking changes:** All existing API contracts, request/response schemas, and feature computation logic stay identical
2. **Graceful degradation:** If `ProcessPoolExecutor` fails (e.g., pickling error), fall back to sequential computation with a warning log
3. **Thread safety:** `DataFetcher._default_fetcher` singleton protected by `threading.Lock` (already exists)
4. **Worker limits:** Max 8 I/O threads, max 4 CPU processes — prevents resource exhaustion
5. **Cache behavior unchanged:** Per-source CSV cache in `data/stock_cache/` stays identical
6. **Testing:** All 87 existing backend tests must continue to pass

## Expected Performance

| Dataset size | Current (est.) | After A+B | Speedup |
|---|---|---|---|
| 10 rows, 5 tickers | ~15s | ~4s | ~4x |
| 50 rows, 20 tickers | ~90s | ~12s | ~7x |
| 200 rows, 80 tickers | ~600s | ~60s | ~10x |

Actual speedups depend on network latency and ticker availability.
