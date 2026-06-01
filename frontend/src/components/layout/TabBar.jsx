import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'

const TABS = [
  { value: 'single', label: 'Score' },
  { value: 'upload', label: 'Upload' },
  { value: 'explain', label: 'Explain' },
  { value: 'settings', label: 'Settings' },
]

export function TabBar({ active, onChange }) {
  return (
    <Tabs value={active} onValueChange={onChange} className="mb-6 fade-in stagger-1">
      <TabsList
        className="w-full bg-surface border border-border rounded-lg p-1 h-auto gap-0.5"
        role="tablist"
        aria-label="Analysis sections"
      >
        {TABS.map((tab) => (
          <TabsTrigger
            key={tab.value}
            value={tab.value}
            className="flex-1 py-2.5 px-3 text-xs font-semibold font-mono tracking-wide rounded-md text-dim border border-transparent transition-all duration-300 ease-out data-[state=active]:bg-gradient-to-br data-[state=active]:from-cyan-500/15 data-[state=active]:to-cyan-700/8 data-[state=active]:text-cyan data-[state=active]:border data-[state=active]:border-cyan-500/30 data-[state=active]:shadow-[0_0_20px_rgba(0,240,255,0.1)] data-[state=active]:text-cyan hover:text-secondary"
          >
            {tab.label}
          </TabsTrigger>
        ))}
      </TabsList>
    </Tabs>
  )
}
