"use client"

import { useEffect, useState } from "react"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { fetchCounts, CountItem } from "@/lib/api"

export function SentimentBarChart() {
  const [data, setData] = useState<{ label: string; count: number }[]>([])

  useEffect(() => {
    let mounted = true
    const load = async () => {
      try {
        const counts = await fetchCounts(5)
        if (!mounted) return
        // ensure order positive, neutral, negative
        const ordered = ["positive", "neutral", "negative"].map(lbl => ({
          label: lbl,
          count: counts.find(c => c.label === (lbl as any))?.count ?? 0,
        }))
        setData(ordered)
      } catch {
        if (mounted) setData([])
      }
    }
    load()
    const t = setInterval(load, 2000)
    return () => { mounted = false; clearInterval(t) }
  }, [])

  return (
    <ChartContainer config={{}}>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="label" />
          <YAxis allowDecimals={false} />
          <ChartTooltip content={<ChartTooltipContent />} />
          <Bar dataKey="count" />
        </BarChart>
      </ResponsiveContainer>
    </ChartContainer>
  )
}
