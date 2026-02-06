import { useMemo } from 'react'
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from 'recharts'
import { TrendingUp, PieChart as PieChartIcon } from 'lucide-react'
import type { Contract } from '../types'
import { getCurrencySymbol } from '../types'

interface SpendingChartsProps {
  contracts: Contract[]
}

// Colors for the pie chart categories
const CATEGORY_COLORS: Record<string, string> = {
  insurance: '#3B82F6',   // blue
  utility: '#10B981',     // green
  subscription: '#8B5CF6', // purple
  rental: '#F59E0B',      // amber
  saas: '#EC4899',        // pink
  service: '#06B6D4',     // cyan
  other: '#6B7280',       // gray
}

const DEFAULT_COLOR = '#94A3B8'

export default function SpendingCharts({ contracts }: SpendingChartsProps) {
  // Calculate spending by category
  const categoryData = useMemo(() => {
    const byCategory: Record<string, number> = {}

    contracts.forEach((contract) => {
      const category = contract.contract_type || 'other'
      const monthlyCost = contract.monthly_cost || 0
      byCategory[category] = (byCategory[category] || 0) + monthlyCost
    })

    return Object.entries(byCategory)
      .map(([name, value]) => ({
        name: name.charAt(0).toUpperCase() + name.slice(1),
        value: Math.round(value * 100) / 100,
        color: CATEGORY_COLORS[name] || DEFAULT_COLOR,
      }))
      .filter((d) => d.value > 0)
      .sort((a, b) => b.value - a.value)
  }, [contracts])

  // Calculate monthly spending projection for next 12 months
  const monthlyTrendData = useMemo(() => {
    const today = new Date()
    const months: { month: string; spending: number; projected: number }[] = []

    for (let i = 0; i < 12; i++) {
      const date = new Date(today.getFullYear(), today.getMonth() + i, 1)
      const monthName = date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' })

      let monthlyTotal = 0
      let projectedTotal = 0

      contracts.forEach((contract) => {
        const monthlyCost = contract.monthly_cost || 0
        if (monthlyCost === 0) return

        const startDate = contract.start_date ? new Date(contract.start_date) : null
        const endDate = contract.end_date ? new Date(contract.end_date) : null

        // Check if contract is active in this month
        const monthStart = new Date(date.getFullYear(), date.getMonth(), 1)
        const monthEnd = new Date(date.getFullYear(), date.getMonth() + 1, 0)

        const hasStarted = !startDate || startDate <= monthEnd
        const hasEnded = endDate && endDate < monthStart

        if (hasStarted && !hasEnded) {
          // Contract is active
          if (i === 0) {
            monthlyTotal += monthlyCost
          }
          projectedTotal += monthlyCost
        } else if (hasEnded && contract.auto_renewal) {
          // Contract ended but has auto-renewal
          projectedTotal += monthlyCost
        }
      })

      months.push({
        month: monthName,
        spending: i === 0 ? monthlyTotal : 0, // Only current month has actual spending
        projected: projectedTotal,
      })
    }

    return months
  }, [contracts])

  // Calculate totals
  const totalMonthly = useMemo(() => {
    return contracts.reduce((sum, c) => sum + (c.monthly_cost || 0), 0)
  }, [contracts])

  const totalAnnual = useMemo(() => {
    return contracts.reduce((sum, c) => {
      if (c.annual_cost) return sum + c.annual_cost
      if (c.monthly_cost) return sum + c.monthly_cost * 12
      return sum
    }, 0)
  }, [contracts])

  // Get dominant currency (most used)
  const dominantCurrency = useMemo(() => {
    const currencyCounts: Record<string, number> = {}
    contracts.forEach((c) => {
      const curr = c.currency || 'USD'
      currencyCounts[curr] = (currencyCounts[curr] || 0) + 1
    })
    return Object.entries(currencyCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || 'USD'
  }, [contracts])

  const currencySymbol = getCurrencySymbol(dominantCurrency)

  if (contracts.length === 0) {
    return null
  }

  const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: Array<{ name: string; value: number; color: string }> }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white px-3 py-2 shadow-lg rounded-lg border border-gray-200">
          {payload.map((entry, index) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {currencySymbol}{entry.value.toLocaleString()}
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Spending by Category */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center space-x-2 mb-4">
          <PieChartIcon className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">Spending by Category</h3>
        </div>

        {categoryData.length > 0 ? (
          <div className="flex flex-col md:flex-row items-center">
            <div className="w-full md:w-1/2 h-48">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={categoryData}
                    cx="50%"
                    cy="50%"
                    innerRadius={40}
                    outerRadius={70}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {categoryData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value) => [`${currencySymbol}${(value as number).toLocaleString()}/mo`, '']}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="w-full md:w-1/2 mt-4 md:mt-0">
              <div className="space-y-2">
                {categoryData.map((entry) => (
                  <div key={entry.name} className="flex items-center justify-between text-sm">
                    <div className="flex items-center">
                      <div
                        className="w-3 h-3 rounded-full mr-2"
                        style={{ backgroundColor: entry.color }}
                      />
                      <span className="text-gray-700">{entry.name}</span>
                    </div>
                    <span className="font-medium text-gray-900">
                      {currencySymbol}{entry.value.toLocaleString()}/mo
                    </span>
                  </div>
                ))}
              </div>
              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="flex justify-between text-sm font-semibold">
                  <span className="text-gray-700">Total Monthly</span>
                  <span className="text-gray-900">{currencySymbol}{totalMonthly.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-sm mt-1">
                  <span className="text-gray-500">Projected Annual</span>
                  <span className="text-gray-700">{currencySymbol}{totalAnnual.toLocaleString()}</span>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="h-48 flex items-center justify-center text-gray-500">
            No spending data available
          </div>
        )}
      </div>

      {/* Monthly Spending Trend */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center space-x-2 mb-4">
          <TrendingUp className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">12-Month Projection</h3>
        </div>

        {monthlyTrendData.some((d) => d.projected > 0) ? (
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={monthlyTrendData}>
                <defs>
                  <linearGradient id="colorProjected" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis
                  dataKey="month"
                  tick={{ fontSize: 11 }}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  tick={{ fontSize: 11 }}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(value) => `${currencySymbol}${value >= 1000 ? `${(value / 1000).toFixed(0)}k` : value}`}
                />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="projected"
                  name="Projected"
                  stroke="#8B5CF6"
                  fillOpacity={1}
                  fill="url(#colorProjected)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="h-48 flex items-center justify-center text-gray-500">
            No projection data available
          </div>
        )}

        {/* Summary below chart */}
        <div className="mt-4 pt-4 border-t border-gray-200 grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-gray-500">Contracts with Costs</p>
            <p className="font-semibold text-gray-900">
              {contracts.filter((c) => c.monthly_cost || c.annual_cost).length} of {contracts.length}
            </p>
          </div>
          <div>
            <p className="text-gray-500">Auto-Renewing</p>
            <p className="font-semibold text-gray-900">
              {contracts.filter((c) => c.auto_renewal).length} contracts
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
