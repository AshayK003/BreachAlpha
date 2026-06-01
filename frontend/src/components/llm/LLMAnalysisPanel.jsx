import { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

const API = '/api'

export function LLMAnalysisPanel({ batchData }) {
  const [llmStatus, setLlmStatus] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(false)
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [askLoading, setAskLoading] = useState(false)
  const questionRef = useRef(null)

  useEffect(() => {
    fetch(`${API}/llm/status`)
      .then((r) => r.json())
      .then(setLlmStatus)
      .catch(() => {})
  }, [])

  const generateAnalysis = async () => {
    setLoading(true)
    try {
      const summary =
        `Dataset: ${batchData.total} companies, ${batchData.analyzed} analyzed, ${batchData.failed} failed. ` +
        `Results: ${batchData.results
          .map((r) => `${r.company}(${r.ticker}): score=${r.risk_score}, ${r.prediction}`)
          .join('; ')}`
      const res = await fetch(`${API}/llm/analyze-dataset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          dataset_summary: summary,
          analysis_results: JSON.stringify(batchData.results),
        }),
      })
      if (!res.ok) throw new Error((await res.json()).detail)
      setAnalysis((await res.json()).analysis)
    } catch (e) {
      setAnalysis('Error: ' + e.message)
    }
    setLoading(false)
  }

  const askQuestion = async () => {
    if (!question.trim()) return
    setAskLoading(true)
    try {
      const context = `Dataset has ${batchData.analyzed} analyzed companies. Top: ${
        batchData.results
          .filter((r) => r.status === 'ok')
          .slice(0, 5)
          .map((r) => `${r.company}: risk=${r.risk_score}, severity=${r.prediction}`)
          .join('; ')
      }`
      const res = await fetch(`${API}/llm/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, context }),
      })
      if (!res.ok) throw new Error((await res.json()).detail)
      setAnswer((await res.json()).answer)
    } catch (e) {
      setAnswer('Error: ' + e.message)
    }
    setAskLoading(false)
  }

  if (!llmStatus?.available) {
    return (
      <Card className="terminal-card mt-6">
        <CardContent className="p-5">
          <h3 className="text-xs font-semibold tracking-wider uppercase mb-2 flex items-center gap-2 font-mono text-dim">
            <svg className="w-4 h-4 text-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            LLM Analysis
          </h3>
          <p className="text-xs leading-relaxed text-secondary-foreground">
            Connect <strong className="text-foreground">LM Studio</strong> with Qwen 3.5 9B at{' '}
            <code className="px-1.5 py-0.5 rounded bg-surface text-cyan font-mono text-[0.65rem]">
              192.168.56.1:1234
            </code>{' '}
            for AI insights.
          </p>
          <p className="text-xs mt-1 text-secondary-foreground">
            Start LM Studio and load a model to enable this feature.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="terminal-card mt-6 fade-in">
      <CardContent className="p-5">
        <h3 className="text-xs font-semibold tracking-wider uppercase mb-4 flex items-center gap-2 font-mono text-dim">
          <svg className="w-4 h-4 text-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          LLM Analysis
          <span className="text-[0.6rem] font-normal tracking-wide text-emerald-400">
            ({llmStatus.default_model || 'connected'})
          </span>
        </h3>

        <Button
          variant="secondary"
          onClick={generateAnalysis}
          disabled={loading}
          className="w-full justify-center mb-4"
        >
          {loading ? (
            <>
              <div className="animate-spin w-3 h-3 border-2 border-purple-400 border-t-transparent rounded-full" />
              Analyzing...
            </>
          ) : (
            'Generate AI Risk Analysis'
          )}
        </Button>

        {analysis && (
          <div className="rounded-lg p-4 mb-4 bg-background border border-border fade-in">
            <h4 className="text-xs font-semibold tracking-wider uppercase mb-2 text-dim">
              AI Analysis
            </h4>
            <div className="text-xs whitespace-pre-wrap leading-relaxed text-secondary-foreground">
              {analysis}
            </div>
          </div>
        )}

        <div className="pt-4 border-t border-border">
          <h4 className="text-xs font-semibold tracking-wider uppercase mb-2 text-dim">
            Ask about this data
          </h4>
          <div className="flex gap-2">
            <Input
              ref={questionRef}
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="e.g., Which breach type causes the most damage?"
              className="flex-1"
              onKeyDown={(e) => e.key === 'Enter' && askQuestion()}
            />
            <Button onClick={askQuestion} disabled={askLoading || !question.trim()}>
              {askLoading ? '...' : 'Ask'}
            </Button>
          </div>
          {answer && (
            <div className="mt-3 rounded-lg p-3 bg-background border border-border fade-in">
              <div className="text-xs whitespace-pre-wrap text-secondary-foreground">{answer}</div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
