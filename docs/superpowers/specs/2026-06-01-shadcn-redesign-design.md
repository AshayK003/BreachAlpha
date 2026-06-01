# BreachAlpha Frontend Redesign — shadcn/ui + Tailwind CSS

## Overview

Full frontend rewrite of BreachAlpha using shadcn/ui components, Tailwind CSS, and Recharts. The current 1564-line single-file App.jsx is split into ~25-30 feature-based component files. The cyber terminal aesthetic is preserved on data/analysis views while settings/forms use clean shadcn styling.

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Scope | Full rewrite | Clean slate, no incremental migration debt |
| UI library | shadcn/ui | Unstyled primitives, full design control, zero runtime cost |
| Design direction | Hybrid: terminal + polish | Terminal for data views, clean shadcn for forms/settings |
| Component split | Feature-based | `components/score/`, `components/upload/`, etc. |
| State management | useState (keep) | 12 pieces of state is manageable without a library |
| Charting | Recharts (replace Chart.js) | React-native API, works with Tailwind, shadcn-compatible |
| TypeScript | No | Matches current codebase, faster iteration |

## Project Structure

```
frontend/
├── index.html                    # JetBrains Mono + Outfit fonts (keep)
├── vite.config.js                # Vite + React plugin + API proxy (keep)
├── tailwind.config.js            # Custom BreachAlpha theme
├── postcss.config.js             # tailwindcss + autoprefixer (keep)
├── src/
│   ├── main.jsx                  # React entry (keep)
│   ├── App.jsx                   # Shell: header, tabs, routing (~100 lines)
│   ├── index.css                 # Tailwind directives + CSS variables + terminal effects
│   ├── lib/
│   │   └── utils.js              # cn() = clsx + tailwind-merge
│   ├── components/
│   │   ├── ui/                   # shadcn primitives (Button, Card, Input, etc.)
│   │   ├── layout/               # Header.jsx, TabBar.jsx, Footer.jsx
│   │   ├── score/                # ScoreForm.jsx, RiskGauge.jsx, ProbabilityBar.jsx, FeatureCard.jsx, FeaturesChart.jsx
│   │   ├── upload/               # FileUpload.jsx, DatasetPreview.jsx, BatchResults.jsx
│   │   ├── explain/              # ExplainabilityPanel.jsx
│   │   ├── settings/             # SettingsPanel.jsx
│   │   ├── demos/                # DemoCard.jsx
│   │   └── llm/                  # LLMAnalysisPanel.jsx
│   └── hooks/
│       └── useDebounce.js        # Reusable debounce hook (extracted from ScoreForm)
```

## Dependencies

### Add
- `@radix-ui/react-*` (via shadcn — Dialog, Tabs, Select, Switch, etc.)
- `class-variance-authority` (shadcn component variants)
- `clsx` (conditional class joining)
- `tailwind-merge` (Tailwind class deduplication)
- `lucide-react` (icon library)
- `recharts` (charting)

### Remove
- `chart.js`
- `react-chartjs-2`

### Keep
- `react`, `react-dom`
- `vite`, `@vitejs/plugin-react`
- `tailwindcss`, `postcss`, `autoprefixer`
- `eslint`, `eslint-plugin-react`, `eslint-plugin-react-hooks`, `eslint-plugin-react-refresh`

## Design System

### Tailwind Theme Mapping

Our terminal palette maps to shadcn's CSS variable names:

```
Colors:
  background:     #050810    (void — page background)
  foreground:     #e0e6f0    (primary text)
  card:           #0a0f1a    (card backgrounds)
  card-foreground: #e0e6f0
  primary:        #00f0ff    (cyan — main accent)
  primary-foreground: #050810
  secondary:      #0d1320    (surface-raised)
  secondary-foreground: #7a8ba8
  muted:          #111827    (surface-overlay)
  muted-foreground: #4a5568
  accent:         #ff9500    (amber — warning)
  destructive:    #ff3366    (red — error/critical)
  border:         #151d2e    (default borders)
  input:          #1e293b    (input borders)
  ring:           #00f0ff    (focus ring)
  severity-low:   #00ff88
  severity-medium: #ff9500
  severity-high:  #ff6633
  severity-critical: #ff3366
  llm-accent:     #b366ff    (purple — AI)

Typography:
  font-sans:  'Outfit', system-ui, sans-serif      (display/headings)
  font-mono:  'JetBrains Mono', monospace           (data/terminal)

Border Radius:
  lg: 12px
  md: 8px
  sm: 4px
```

### Global Effects (Preserved)

- **Ambient gradient mesh**: Three radial gradients on `body::before` (cyan top-left, amber bottom-right, purple center)
- **Scanline overlay**: Repeating horizontal lines on `body::after` (z-9999)
- **Custom scrollbar**: 4px thin, border-bright thumb, cyan-dim on hover
- **Selection**: Cyan background (rgba(0,240,255,0.25))
- **Focus**: Cyan outline with 2px offset
- **Reduced motion**: Full `prefers-reduced-motion` support

### Hybrid Approach

**Terminal mode** (score views, batch results, explainability):
- Custom `.terminal-card` class: gradient background, border glow on hover, corner accents
- Scanline overlay visible
- JetBrains Mono for data
- Glow effects on interactive elements

**Clean mode** (settings, forms, LLM panel):
- Standard shadcn Card, Input, Button — no glow, no scanlines
- Outfit for headings
- Subtle, professional look

**Switching mechanism**: CSS class on view container:
```jsx
<div className={activeTab === 'settings' ? '' : 'terminal-view'}>
  {/* terminal-view enables glow/scanline effects */}
</div>
```

## Component Design

### Layout Components

**Header.jsx**
- Logo: "BreachAlpha" in JetBrains Mono with cyan gradient text
- Health status: green/amber/red dot with pulse animation
- Clean shadcn styling

**TabBar.jsx**
- shadcn Tabs component with custom active state (cyan glow, JetBrains Mono labels)
- Tabs: Score, Upload, Explain, Settings

**Footer.jsx**
- Muted text, version info, links
- Clean shadcn styling

### Score Components

**ScoreForm.jsx**
- shadcn Input for company/ticker search with Command autocomplete
- shadcn Select for breach type
- shadcn Input for records and date
- shadcn Button for "Analyze Risk" (primary cyan)
- Ticker search: debounced with AbortController (extracted useDebounce hook)
- Breach search: "Find from Internet" button with results dropdown

**RiskGauge.jsx**
- Custom SVG circular gauge (no shadcn equivalent)
- Animated stroke-dashoffset for score
- Glow filter on SVG
- Color mapped from severity prediction

**ProbabilityBar.jsx**
- Custom horizontal bar with glow shadow
- Animated width transition
- Color from severity palette

**FeatureCard.jsx**
- Terminal-style card with corner accent
- Label in uppercase mono, value in large mono
- Negative values in red

**FeaturesChart.jsx**
- Recharts BarChart replacing Chart.js
- Custom theme: JetBrains Mono font, dark grid, severity colors
- Bars colored red (negative) / green (positive)

### Upload Components

**FileUpload.jsx**
- shadcn Card with dashed border dropzone
- Drag-and-drop with visual feedback
- File validation (extension, size)
- Preview + Analyze buttons

**DatasetPreview.jsx**
- shadcn Table for data preview
- shadcn Badge for stats (rows, resolution rate)
- Warnings list

**BatchResults.jsx**
- Sortable table with column headers
- Severity badges with color coding
- Mini probability bars inline
- Expandable rows for details
- CSV export button

### Explainability Components

**ExplainabilityPanel.jsx**
- Numbered calculation steps (1-12)
- Formula rendering in monospace
- Feature contribution diverging bar chart (Recharts)
- Methodology section
- Limitations list

### Settings Components

**SettingsPanel.jsx**
- shadcn Card for analysis config (presets, thresholds, windows)
- shadcn Switch for advanced toggle
- shadcn Select for data sources
- shadcn Input for Alpha Vantage key
- Source status list with availability indicators
- Data source test button

### Demo Components

**DemoCard.jsx**
- Terminal-style card with glow border
- Company info, severity tag, risk score
- "Explain" button
- Scale-down on click

### LLM Components

**LLMAnalysisPanel.jsx**
- shadcn Card with purple accent
- "Generate AI Analysis" button
- Analysis text output
- Q&A interface with shadcn Input
- LM Studio connection status

## API Integration

**Endpoints** (unchanged — all 15):
- `GET /api/health`
- `POST /api/score`
- `POST /api/score/auto`
- `POST /api/explain/auto`
- `GET /api/demo`
- `POST /api/upload`
- `POST /api/upload/analyze`
- `GET /api/search`
- `GET /api/breach-search`
- `GET /api/config/presets`
- `GET /api/data-sources`
- `GET /api/data-sources/test/{name}`
- `POST /api/data-sources/configure`
- `GET /api/llm/status`
- `POST /api/llm/analyze-dataset`
- `POST /api/llm/ask`

**Proxy**: Vite dev server proxies `/api/*` to `http://localhost:8000`

**Error handling**: shadcn Toast component for API errors instead of inline error banners

**Loading states**: shadcn Skeleton components replacing custom `.skeleton` class

## Data Flow

```
App.jsx (~100 lines)
├── State: activeTab, score, demos, loading, error, health, uploadData, batchData, explainData, analysisConfig, presets
├── API handlers: handleScore, handleUpload, handleAnalyze, handleAutoExplain, loadDemos, loadPresets
├── Render: Header → TabBar → tab content switch
│   ├── 'single' → ScoreForm + RiskGauge + ProbabilityBar + FeatureCard + FeaturesChart + DemoCard[]
│   ├── 'upload' → FileUpload + DatasetPreview + BatchResults + LLMAnalysisPanel
│   ├── 'explain' → ExplainabilityPanel
│   └── 'settings' → SettingsPanel
```

**App.jsx shrinks from 1564 lines to ~80-120 lines** — just state, handlers, and layout.

## Implementation Order

1. **Setup**: Install shadcn/ui, configure tailwind.config.js, set up CSS variables theme
2. **Lib/Utils**: Create `lib/utils.js` with `cn()` helper
3. **UI primitives**: Install shadcn components (Button, Card, Input, Select, Badge, Table, Tabs, Switch, Skeleton)
4. **Layout**: Header, TabBar, Footer
5. **Score view**: ScoreForm, RiskGauge, ProbabilityBar, FeatureCard, FeaturesChart (Recharts migration)
6. **Upload view**: FileUpload, DatasetPreview, BatchResults
7. **Explain view**: ExplainabilityPanel
8. **Settings view**: SettingsPanel
9. **Demos**: DemoCard
10. **LLM**: LLMAnalysisPanel
11. **App.jsx**: Rewrite shell, wire everything together
12. **Polish**: Terminal effects, animations, reduced motion, responsive
13. **Cleanup**: Remove App.css, old chart.js deps, verify build

## Success Criteria

- [ ] All 15 components render correctly
- [ ] All 15 API endpoints functional
- [ ] Terminal aesthetic preserved on data views
- [ ] Clean shadcn look on settings/forms
- [ ] Responsive design (mobile-friendly)
- [ ] Reduced motion support
- [ ] Build succeeds (`npm run build`)
- [ ] No console errors
- [ ] Bundle size comparable or smaller than current
