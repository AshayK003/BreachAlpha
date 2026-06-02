import { useState, useCallback } from 'react'
import { Button } from '@/components/ui/button'

const MAX_SIZE = 50 * 1024 * 1024

export function FileUpload({ onUpload, onAnalyze, loading }) {
  const [dragActive, setDragActive] = useState(false)
  const [file, setFile] = useState(null)
  const [fileError, setFileError] = useState('')

  const validateAndSet = (f) => {
    setFileError('')
    const allowed = ['.csv', '.xlsx', '.xls', '.tsv']
    const ext = '.' + f.name.split('.').pop().toLowerCase()
    if (!allowed.includes(ext)) {
      setFileError(`Unsupported format. Use: ${allowed.join(', ')}`)
      return
    }
    if (f.size > MAX_SIZE) {
      setFileError(`File too large (max 50 MB). Got ${(f.size / 1024 / 1024).toFixed(1)} MB`)
      return
    }
    setFile(f)
  }

  const handleDrag = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true)
    else if (e.type === 'dragleave') setDragActive(false)
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    const f = e.dataTransfer.files?.[0]
    if (f) validateAndSet(f)
  }, [])

  const handleChange = (e) => {
    const f = e.target.files?.[0]
    if (f) validateAndSet(f)
  }

  return (
    <div className="space-y-3">
      <form
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <label
          className={`flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-xl cursor-pointer transition-all duration-300 ${
            dragActive
              ? 'border-cyan-500 bg-cyan-500/5 shadow-[0_0_20px_rgba(0,240,255,0.1)]'
              : 'border-border bg-card hover:border-border-bright hover:bg-surface'
          }`}
          role="button"
          aria-label="Upload a CSV, XLSX, or TSV file"
        >
          <div className="flex flex-col items-center justify-center pt-2 pb-3">
            <svg className="w-7 h-7 mb-2 text-dim" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <p className="text-xs">
              <span className="font-semibold text-cyan">Click to upload</span>{' '}
              <span className="text-secondary-foreground">or drag and drop</span>
            </p>
            <p className="text-[0.65rem] mt-0.5 text-dim">
              CSV, XLSX, Excel, TSV (max 50 MB)
            </p>
          </div>
          <input
            type="file"
            className="hidden"
            accept=".csv,.xlsx,.xls,.tsv"
            onChange={handleChange}
          />
        </label>
      </form>

      {fileError && (
        <p className="text-xs text-red-400" role="alert">{fileError}</p>
      )}

      {file && (
        <div className="bg-surface border border-border rounded-lg p-3 flex items-center justify-between fade-in">
          <div className="flex items-center gap-2.5 min-w-0">
            <svg className="w-4 h-4 text-emerald-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-sm text-foreground truncate">{file.name}</span>
            <span className="text-xs text-dim shrink-0">
              ({(file.size / 1024).toFixed(1)} KB)
            </span>
          </div>
          <button
            onClick={() => setFile(null)}
            className="text-xs text-dim hover:text-red-400 shrink-0 ml-3 transition-colors"
          >
            Remove
          </button>
        </div>
      )}

      {file && (
        <div className="flex gap-2">
          <Button
            variant="secondary"
            onClick={() => onUpload(file)}
            disabled={loading}
            className="flex-1"
          >
            {loading ? (
              <>
                <div className="animate-spin w-3 h-3 border-2 border-current border-t-transparent rounded-full" />
                Previewing...
              </>
            ) : 'Preview'}
          </Button>
          <Button
            onClick={() => onAnalyze(file)}
            disabled={loading}
            className="flex-1"
          >
            {loading ? (
              <>
                <div className="animate-spin w-3 h-3 border-2 border-white/60 border-t-transparent rounded-full" />
                Analyzing...
              </>
            ) : 'Analyze All'}
          </Button>
        </div>
      )}
    </div>
  )
}
