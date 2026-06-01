import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'

export function TabBar({ active, onChange }) {
  return (
    <Tabs value={active} onValueChange={onChange} className="mb-6">
      <TabsList
        className="w-full bg-surface border border-border rounded-lg p-1 h-auto gap-0.5"
        role="tablist"
        aria-label="Analysis sections"
      >
        <TabsTrigger
          value="single"
          className="flex-1 py-2.5 px-3 text-xs font-semibold font-mono tracking-wide rounded-md data-[state=active]:bg-gradient-to-br data-[state=active]:from-cyan-500/12 data-[state=active]:to-cyan-700/8 data-[state=active]:text-cyan-400 data-[state=active]:border data-[state=active]:border-cyan-500/25 data-[state=active]:shadow-[0_0_15px_rgba(0,240,255,0.08)] data-[state=active]:text-cyan-400 text-muted-foreground border border-transparent transition-all"
        >
          Score
        </TabsTrigger>
        <TabsTrigger
          value="upload"
          className="flex-1 py-2.5 px-3 text-xs font-semibold font-mono tracking-wide rounded-md data-[state=active]:bg-gradient-to-br data-[state=active]:from-cyan-500/12 data-[state=active]:to-cyan-700/8 data-[state=active]:text-cyan-400 data-[state=active]:border data-[state=active]:border-cyan-500/25 data-[state=active]:shadow-[0_0_15px_rgba(0,240,255,0.08)] text-muted-foreground border border-transparent transition-all"
        >
          Upload
        </TabsTrigger>
        <TabsTrigger
          value="explain"
          className="flex-1 py-2.5 px-3 text-xs font-semibold font-mono tracking-wide rounded-md data-[state=active]:bg-gradient-to-br data-[state=active]:from-cyan-500/12 data-[state=active]:to-cyan-700/8 data-[state=active]:text-cyan-400 data-[state=active]:border data-[state=active]:border-cyan-500/25 data-[state=active]:shadow-[0_0_15px_rgba(0,240,255,0.08)] text-muted-foreground border border-transparent transition-all"
        >
          Explain
        </TabsTrigger>
        <TabsTrigger
          value="settings"
          className="flex-1 py-2.5 px-3 text-xs font-semibold font-mono tracking-wide rounded-md data-[state=active]:bg-gradient-to-br data-[state=active]:from-cyan-500/12 data-[state=active]:to-cyan-700/8 data-[state=active]:text-cyan-400 data-[state=active]:border data-[state=active]:border-cyan-500/25 data-[state=active]:shadow-[0_0_15px_rgba(0,240,255,0.08)] text-muted-foreground border border-transparent transition-all"
        >
          Settings
        </TabsTrigger>
      </TabsList>
    </Tabs>
  )
}
