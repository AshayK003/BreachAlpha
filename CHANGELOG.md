# Changelog

## [0.4.0] — 2026-07-18

### Added
- **tests**: 13 unit tests for `_extract_records_from_text()` and `_detect_breach_type()` covering multiple record count formats and breach type classification
- **tests**: 17 unit tests for `_sanitize_formula_injection()` and `normalize_column_name()` covering formula prefixes, edge cases, and column name normalization patterns

### Fixed
- **preprocessor**: `_sanitize_formula_injection()` now handles pandas 3.x Arrow StringDtype — replaced `dtype == object` check with `pd.api.types.is_string_dtype()`
- **breach_loader**: `== False` comparison replaced with safe `~df[col].fillna(False).astype(bool)` filter that handles nullable boolean columns
- **feature_engine**: `ar_days: list` typehint tightened to `list[int]`

### Changed
- Test suite expanded from 144 to 188 tests across 14 modules

## [0.3.3] — 2026-06-02

### Fixed
- **crash**: `/api/cache` endpoint crashed with `NameError: CACHE_DIR` (missing import in `stock_loader.py`)
- **crash**: `/api/cache` endpoint crashed with `TypeError` — response dict used `count` but `CacheInfoResponse` expected `cached_files`
- **crash**: File upload date parsing crashed on pandas 3.0 — `infer_datetime_format` parameter removed in pandas 2.0
- **crash**: LLM analysis panel crashed on successful response — `res.json()` called twice on same response body stream
- **crash**: LLM ask panel crashed on successful response — same double `.json()` pattern
- **crash**: ExplainabilityPanel crashed when `feature_contributions`, `steps`, or `limitations` was null/missing
- **crash**: DemoCard crashed when `pwn_count` was null/undefined — division on null
- **logic**: LLM `temperature=0.0` silently used default (0.3) — Python `or` treats `0.0` as falsy
- **logic**: Demo endpoint blocked the entire event loop — `fetch_market_data()` and `fetch_stock_data()` called synchronously in async handler
- **logic**: Data sources endpoint always reported `primary_source="yfinance"` regardless of actual configuration
- **logic**: NSE India source claimed to support any 2-10 letter uppercase ticker (e.g., MSFT, AAPL), wasting time on invalid requests
- **data**: CSV export broke on company names containing commas — no RFC 4180 escaping

### Changed
- Demo endpoint uses `asyncio.gather()` to fetch market data and model in parallel, then stock data per-case via `asyncio.to_thread()`
- NSE India `supports_ticker()` now only matches `.NS` and `.BO` suffixes
- Data sources endpoint reads actual active source from fetcher status

## [0.3.2] — 2026-06-02

### Fixed
- **accessibility**: `text-dim` contrast raised from `#4a5568` to `#708096` (WCAG AA compliance)
- **accessibility**: Scanline overlay z-index lowered from 9999 to 1 (no longer blocks dropdown/select interactions)
- **accessibility**: DemoCard nested `<button>` fixed — outer element converted to `<div role="button">` with `aria-label`
- **accessibility**: ScoreForm labels now have `htmlFor` associations
- **accessibility**: RiskGauge score has `aria-live="polite"` for screen reader updates
- **accessibility**: BatchResults table rows respond to Space key (Enter + Space)
- **responsive**: SettingsPanel CAR Windows grid now `grid-cols-2 sm:grid-cols-4` (mobile-friendly)
- **UX**: FileUpload buttons show loading spinners during Preview/Analyze
- **UX**: Footer font size increased from `text-[0.6rem]` to `text-xs`
- **UX**: SettingsPanel shows empty state when no presets available

## [0.3.1] — 2026-06-01

### Fixed
- **security**: Admin endpoints (`/api/train`, `/api/data-sources/configure`, `DELETE /api/cache`) now return 503 when `BREACHALPHA_ADMIN_KEY` is not set (previously bypassed auth entirely)
- **security**: Admin key comparison uses `hmac.compare_digest()` for timing-safe comparison
- **frontend**: Settings config (benchmark, windows, thresholds) now sent to `/api/score/config` (was silently ignored)
- **frontend**: Removed unused `chart.js` + `react-chartjs-2` (~200KB)
- **frontend**: Removed unused Radix UI packages (dialog, dropdown-menu, scroll-area, tooltip)
- **frontend**: Removed `lucide-react`, replaced 2 icons with inline SVGs

## [0.3.0] — 2026-06-01

### Added
- **server**: `_run_analysis_pipeline()` — stages 4-8 wrapped in `asyncio.to_thread()` to avoid blocking the event loop
- **server**: Parallel market data fetch via `ThreadPoolExecutor(8)` — all unique benchmarks fetched concurrently
- **server**: Batch prediction — single `model.predict()` + `predict_proba()` call instead of per-row loop
- **data_sources**: Parallel fallback in `DataFetcher.fetch_batch()` — `ThreadPoolExecutor(8)` replaces sequential loop
- **preprocessor**: Parallel ticker resolution — `ThreadPoolExecutor(8)` for datasets > 5 rows
- **feature_engine**: `ProcessPoolExecutor` replaces `ThreadPoolExecutor` — true parallelism on CPU-bound work (bypasses GIL)
- **docs**: Design spec for pipeline performance optimization

### Changed
- Analysis pipeline runs in a dedicated thread, keeping the FastAPI event loop free
- Feature batch computation falls back to sequential on pickling errors
- Batch prediction falls back to per-row prediction on failure
- Ticker resolution uses sequential path for small datasets (≤5 rows) to avoid thread overhead

## [0.2.0] — 2026-06-01

### Added
- **breach_search**: Internet breach search via Yahoo Finance News + DuckDuckGo web crawl
  - Ticker-to-company name resolution (TATAPOWER.NS → "Tata Power")
  - Extracts breach type, date, records affected from search snippets
  - Multiple query variations for better coverage
- **ticker_search**: Real-time ticker search (Yahoo Finance + NSE India + fallback chain)
  - Debounced frontend search with client-side cache
  - Live price verification
- **llm_integration**: LM Studio LLM client for optional enrichment
  - Dataset analysis, risk summaries, Q&A, record enrichment
  - Graceful fallback when LM Studio is offline
- **data_sources**: Multi-source stock data fetcher with fallback chain
  - YFinance (via curl_cffi Chrome impersonation)
  - Alpha Vantage, NSE India, Yahoo Finance HTML scrape
  - Batch multi-ticker download via Yahoo Finance chart API
- **server endpoints**: 12 new REST endpoints
  - `/api/search` — ticker search
  - `/api/breach-search` — breach incident search
  - `/api/llm/*` — LLM analysis, risk summary, Q&A, enrichment
  - `/api/data-sources/*` — data source config, test, status
  - `/api/cache` — stock cache info, clear
  - `/api/config/presets` — analysis configuration presets
  - `/api/score/auto` — auto-search breach data and score company
  - `/api/explain/auto` — auto-search breach data and explain score
- **frontend features**:
  - Settings tab with analysis presets and data source configuration
  - LLM analysis panel in upload results
  - Breach search with auto-fill date/type/records
  - Ticker search with debounce and live price display
  - Sortable batch results table with aria-sort
  - Chart error states and tooltips
  - Reduced motion support (prefers-reduced-motion)
  - Scale press feedback on buttons and cards

### Fixed
- **preprocessor**: Ticker validation in CSV uploads
  - `resolve_tickers` now validates ticker column values via `is_likely_ticker()`
  - Falls back to company name resolution for fake tickers (e.g., "XXXXX", "N/A")
- **data_sources**: YFinanceSource.fetch_batch chart result iteration
  - Removed non-existent `_write_cache` call
  - Added `chart.get("result")` guard for NoneType iteration
- **server**: upload/analyze endpoint returns results for valid companies
  - Added company-name fallback when stock data fetch returns empty
- **feature_engine**: Cross-exchange timestamp normalization
  - Stock and market indices normalized to date-only before intersection
  - Fixes "Insufficient data around breach date" for Indian stocks (TATAPOWER.NS)
  - Common dates: 0 → 2728 (TATAPOWER.NS vs ^GSPC)
- **server**: Path traversal protection in SPA catch-all and training endpoint
- **server**: CORS restricted to localhost:3000
- **server**: Thread-safe config via app.state (replaced global env mutation)
- **server**: Temp file cleanup across all upload endpoints

### Changed
- YFinance fetcher uses curl_cffi with Chrome impersonation by default
- Batch stock download replaces sequential per-ticker fetching
- Preprocessor validates dataset presence before batch analysis

## [0.1.0] — 2026-05-31

### Added
- **breach_loader**: Parse HIBP breach CSVs, filter by record count, deduplicate
- **ticker_resolver**: Map company names to stock tickers (200+ mappings)
- **stock_loader**: Fetch and cache historical stock prices via yfinance
- **feature_engine**: Compute abnormal returns, CAR, volatility spikes, recovery time
- **model**: XGBoost classifier for impact severity (Low/Medium/High/Critical)
- **preprocessor**: Dataset preprocessing pipeline for CSV, XLSX, Excel, TSV files
- **explainability**: Step-by-step calculation breakdown with formulas, inputs, outputs
- **server**: FastAPI REST API with 9 endpoints
- **frontend**: React + Vite + Tailwind CSS dashboard with 4 tabs
- **cli**: `demo`, `train`, `score` commands
- Test suite: 87 tests across 7 modules
- Documentation: README, ARCHITECTURE, API, TESTING, CONTRIBUTING, DECISIONS
