import { useMemo } from 'react'
import { Link } from 'react-router-dom'
import {
  Calendar,
  AlertTriangle,
  RefreshCw,
  ArrowRight,
  Bell,
} from 'lucide-react'
import { useContracts } from '../hooks/useContracts'
import EmptyState from '../components/EmptyState'

interface TimelineEvent {
  id: string
  contractId: string
  provider: string
  nickname: string | null
  type: 'end_date' | 'cancellation_deadline' | 'renewal'
  date: Date
  label: string
  daysUntil: number
  autoRenewal: boolean
  cancellationNoticeDays: number | null
}

export default function Timeline() {
  const { contracts, loading, error } = useContracts()

  const { timelineEvents, contractBars } = useMemo(() => {
    const events: TimelineEvent[] = []
    const today = new Date()
    today.setHours(0, 0, 0, 0)

    const bars: {
      id: string
      provider: string
      nickname: string | null
      type: string | null
      startDate: Date | null
      endDate: Date | null
      autoRenewal: boolean
      monthlyCost: number | null
    }[] = []

    contracts.forEach((contract) => {
      const startDate = contract.start_date ? new Date(contract.start_date) : null
      const endDate = contract.end_date ? new Date(contract.end_date) : null

      bars.push({
        id: contract.id,
        provider: contract.provider_name,
        nickname: contract.contract_nickname,
        type: contract.contract_type,
        startDate,
        endDate,
        autoRenewal: contract.auto_renewal,
        monthlyCost: contract.monthly_cost,
      })

      if (endDate) {
        const daysUntilEnd = Math.ceil((endDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))

        // Add end date event
        events.push({
          id: `${contract.id}-end`,
          contractId: contract.id,
          provider: contract.provider_name,
          nickname: contract.contract_nickname,
          type: 'end_date',
          date: endDate,
          label: contract.auto_renewal ? 'Auto-renews' : 'Expires',
          daysUntil: daysUntilEnd,
          autoRenewal: contract.auto_renewal,
          cancellationNoticeDays: contract.cancellation_notice_days,
        })

        // Add cancellation deadline if applicable
        if (contract.cancellation_notice_days && contract.auto_renewal) {
          const cancellationDeadline = new Date(endDate)
          cancellationDeadline.setDate(cancellationDeadline.getDate() - contract.cancellation_notice_days)
          const daysUntilCancellation = Math.ceil((cancellationDeadline.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))

          events.push({
            id: `${contract.id}-cancel`,
            contractId: contract.id,
            provider: contract.provider_name,
            nickname: contract.contract_nickname,
            type: 'cancellation_deadline',
            date: cancellationDeadline,
            label: `Cancel by (${contract.cancellation_notice_days} days notice)`,
            daysUntil: daysUntilCancellation,
            autoRenewal: contract.auto_renewal,
            cancellationNoticeDays: contract.cancellation_notice_days,
          })
        }
      }
    })

    // Sort events by date
    events.sort((a, b) => a.date.getTime() - b.date.getTime())

    // Sort bars by end date
    bars.sort((a, b) => {
      if (!a.endDate) return 1
      if (!b.endDate) return -1
      return a.endDate.getTime() - b.endDate.getTime()
    })

    return { timelineEvents: events, contractBars: bars }
  }, [contracts])

  const getEventColor = (event: TimelineEvent) => {
    if (event.daysUntil < 0) return 'bg-gray-100 text-gray-600 border-gray-200'
    if (event.type === 'cancellation_deadline') {
      if (event.daysUntil <= 7) return 'bg-red-100 text-red-800 border-red-200'
      if (event.daysUntil <= 30) return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      return 'bg-blue-100 text-blue-800 border-blue-200'
    }
    if (event.daysUntil <= 30) return 'bg-orange-100 text-orange-800 border-orange-200'
    if (event.daysUntil <= 90) return 'bg-yellow-100 text-yellow-800 border-yellow-200'
    return 'bg-green-100 text-green-800 border-green-200'
  }

  const getEventIcon = (event: TimelineEvent) => {
    if (event.type === 'cancellation_deadline') return Bell
    if (event.autoRenewal) return RefreshCw
    return Calendar
  }

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  }

  const formatDaysUntil = (days: number) => {
    if (days < 0) return `${Math.abs(days)} days ago`
    if (days === 0) return 'Today'
    if (days === 1) return 'Tomorrow'
    if (days < 7) return `${days} days`
    if (days < 30) return `${Math.ceil(days / 7)} weeks`
    if (days < 365) return `${Math.ceil(days / 30)} months`
    return `${Math.ceil(days / 365)} years`
  }

  // Calculate timeline range for visualization
  const timelineRange = useMemo(() => {
    const today = new Date()
    const minDate = new Date(today)
    minDate.setMonth(minDate.getMonth() - 3) // 3 months ago

    const maxDate = new Date(today)
    maxDate.setMonth(maxDate.getMonth() + 18) // 18 months ahead

    return { minDate, maxDate, today }
  }, [])

  const getBarPosition = (startDate: Date | null, endDate: Date | null) => {
    const { minDate, maxDate } = timelineRange
    const totalRange = maxDate.getTime() - minDate.getTime()

    const start = startDate ? Math.max(startDate.getTime(), minDate.getTime()) : minDate.getTime()
    const end = endDate ? Math.min(endDate.getTime(), maxDate.getTime()) : maxDate.getTime()

    const leftPercent = ((start - minDate.getTime()) / totalRange) * 100
    const widthPercent = ((end - start) / totalRange) * 100

    return { left: `${Math.max(0, leftPercent)}%`, width: `${Math.max(2, widthPercent)}%` }
  }

  const getTodayPosition = () => {
    const { minDate, maxDate, today } = timelineRange
    const totalRange = maxDate.getTime() - minDate.getTime()
    const percent = ((today.getTime() - minDate.getTime()) / totalRange) * 100
    return `${percent}%`
  }

  // Filter upcoming events (next 6 months)
  const upcomingEvents = timelineEvents.filter(e => e.daysUntil >= 0 && e.daysUntil <= 180)
  const urgentEvents = upcomingEvents.filter(e => e.daysUntil <= 30)

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
        {error}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Contract Timeline</h1>
        <p className="text-gray-600">Visual overview of contract periods and important dates</p>
      </div>

      {/* Urgent Alerts */}
      {urgentEvents.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <h2 className="font-semibold text-red-800">Requires Attention ({urgentEvents.length})</h2>
          </div>
          <div className="space-y-2">
            {urgentEvents.map((event) => {
              const Icon = getEventIcon(event)
              return (
                <Link
                  key={event.id}
                  to={`/contracts/${event.contractId}/analysis`}
                  className="flex items-center justify-between p-2 bg-white rounded border border-red-100 hover:border-red-300 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <Icon className="w-4 h-4 text-red-600" />
                    <div>
                      <p className="font-medium text-gray-900">{event.nickname || event.provider}</p>
                      <p className="text-sm text-red-600">{event.label}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-red-600">{formatDaysUntil(event.daysUntil)}</p>
                    <p className="text-xs text-gray-500">{formatDate(event.date)}</p>
                  </div>
                </Link>
              )
            })}
          </div>
        </div>
      )}

      {/* Timeline Visualization - Desktop */}
      <div className="hidden md:block bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="font-semibold text-gray-900 mb-4">Contract Periods</h2>

        {/* Month labels */}
        <div className="relative h-8 mb-2 border-b border-gray-200">
          {[0, 3, 6, 9, 12, 15, 18].map((monthOffset) => {
            const date = new Date()
            date.setMonth(date.getMonth() + monthOffset - 3)
            const { minDate, maxDate } = timelineRange
            const totalRange = maxDate.getTime() - minDate.getTime()
            const percent = ((date.getTime() - minDate.getTime()) / totalRange) * 100
            if (percent < 0 || percent > 100) return null
            return (
              <div
                key={monthOffset}
                className="absolute text-xs text-gray-500"
                style={{ left: `${percent}%`, transform: 'translateX(-50%)' }}
              >
                {date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' })}
              </div>
            )
          })}
        </div>

        {/* Timeline bars */}
        <div className="relative space-y-3">
          {/* Today marker */}
          <div
            className="absolute top-0 bottom-0 w-0.5 bg-primary-500 z-10"
            style={{ left: getTodayPosition() }}
          >
            <div className="absolute -top-6 left-1/2 -translate-x-1/2 text-xs font-medium text-primary-600 whitespace-nowrap">
              Today
            </div>
          </div>

          {contractBars.length === 0 ? (
            contracts.length === 0 ? (
              <div className="py-8">
                <EmptyState type="timeline" />
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                No contracts with dates to display
              </div>
            )
          ) : (
            contractBars.map((bar) => {
              const position = getBarPosition(bar.startDate, bar.endDate)
              const isPast = bar.endDate && bar.endDate < new Date()
              return (
                <Link
                  key={bar.id}
                  to={`/contracts/${bar.id}/analysis`}
                  className="relative h-12 flex items-center group"
                >
                  {/* Provider label */}
                  <div className="w-48 pr-4 truncate text-sm font-medium text-gray-700 group-hover:text-primary-600">
                    {bar.nickname || bar.provider}
                  </div>

                  {/* Bar container */}
                  <div className="flex-1 relative h-8">
                    {/* Background track */}
                    <div className="absolute inset-0 bg-gray-100 rounded" />

                    {/* Contract bar */}
                    <div
                      className={`absolute top-1 bottom-1 rounded flex items-center px-2 text-xs font-medium ${
                        isPast
                          ? 'bg-gray-300 text-gray-600'
                          : bar.autoRenewal
                          ? 'bg-yellow-400 text-yellow-900'
                          : 'bg-primary-400 text-white'
                      }`}
                      style={{ left: position.left, width: position.width, minWidth: '60px' }}
                    >
                      <span className="truncate">
                        {bar.autoRenewal && <RefreshCw className="w-3 h-3 inline mr-1" />}
                        {bar.monthlyCost ? `$${bar.monthlyCost}/mo` : bar.type || ''}
                      </span>
                    </div>
                  </div>
                </Link>
              )
            })
          )}
        </div>

        {/* Legend */}
        <div className="flex items-center gap-6 mt-6 pt-4 border-t text-sm">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-primary-400" />
            <span className="text-gray-600">Fixed term</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-yellow-400" />
            <span className="text-gray-600">Auto-renewal</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-gray-300" />
            <span className="text-gray-600">Expired</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-0.5 h-4 bg-primary-500" />
            <span className="text-gray-600">Today</span>
          </div>
        </div>
      </div>

      {/* Timeline Visualization - Mobile (Card-based) */}
      <div className="md:hidden bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <h2 className="font-semibold text-gray-900 mb-4">Contract Periods</h2>

        {contractBars.length === 0 ? (
          contracts.length === 0 ? (
            <EmptyState type="timeline" />
          ) : (
            <div className="text-center py-8 text-gray-500">
              No contracts with dates to display
            </div>
          )
        ) : (
          <div className="space-y-3">
            {contractBars.map((bar) => {
              const isPast = bar.endDate && bar.endDate < new Date()
              const today = new Date()
              const daysUntilEnd = bar.endDate
                ? Math.ceil((bar.endDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
                : null

              return (
                <Link
                  key={bar.id}
                  to={`/contracts/${bar.id}/analysis`}
                  className={`block p-4 rounded-lg border-l-4 ${
                    isPast
                      ? 'bg-gray-50 border-gray-300'
                      : bar.autoRenewal
                      ? 'bg-yellow-50 border-yellow-400'
                      : 'bg-primary-50 border-primary-400'
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 truncate">
                        {bar.nickname || bar.provider}
                      </p>
                      <p className="text-sm text-gray-500">
                        {bar.type || 'Contract'}
                        {bar.monthlyCost && ` • $${bar.monthlyCost}/mo`}
                      </p>
                    </div>
                    {bar.autoRenewal && (
                      <span className="flex items-center text-xs text-yellow-700 bg-yellow-100 px-2 py-1 rounded-full">
                        <RefreshCw className="w-3 h-3 mr-1" />
                        Auto
                      </span>
                    )}
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <div className="text-gray-600">
                      <span className="font-medium">
                        {bar.startDate?.toLocaleDateString('en-US', { month: 'short', year: '2-digit' }) || '?'}
                      </span>
                      <span className="mx-2">→</span>
                      <span className="font-medium">
                        {bar.endDate?.toLocaleDateString('en-US', { month: 'short', year: '2-digit' }) || 'Ongoing'}
                      </span>
                    </div>

                    {daysUntilEnd !== null && (
                      <span className={`text-xs font-medium ${
                        isPast
                          ? 'text-gray-500'
                          : daysUntilEnd <= 30
                          ? 'text-red-600'
                          : daysUntilEnd <= 90
                          ? 'text-yellow-600'
                          : 'text-green-600'
                      }`}>
                        {isPast
                          ? 'Expired'
                          : daysUntilEnd === 0
                          ? 'Today'
                          : `${daysUntilEnd}d left`}
                      </span>
                    )}
                  </div>
                </Link>
              )
            })}
          </div>
        )}

        {/* Mobile Legend */}
        <div className="flex flex-wrap items-center gap-4 mt-4 pt-4 border-t text-xs">
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded bg-primary-400" />
            <span className="text-gray-600">Fixed</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded bg-yellow-400" />
            <span className="text-gray-600">Auto-renew</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded bg-gray-300" />
            <span className="text-gray-600">Expired</span>
          </div>
        </div>
      </div>

      {/* Upcoming Events List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="font-semibold text-gray-900 mb-4">Upcoming Events</h2>

        {upcomingEvents.length === 0 ? (
          <p className="text-gray-500 text-center py-4">No upcoming events in the next 6 months</p>
        ) : (
          <div className="space-y-3">
            {upcomingEvents.slice(0, 10).map((event) => {
              const Icon = getEventIcon(event)
              return (
                <Link
                  key={event.id}
                  to={`/contracts/${event.contractId}/analysis`}
                  className={`flex items-center justify-between p-3 rounded-lg border transition-colors hover:shadow-sm ${getEventColor(event)}`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className="w-5 h-5" />
                    <div>
                      <p className="font-medium">{event.nickname || event.provider}</p>
                      <p className="text-sm opacity-80">{event.label}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className="font-semibold">{formatDaysUntil(event.daysUntil)}</p>
                      <p className="text-xs opacity-70">{formatDate(event.date)}</p>
                    </div>
                    <ArrowRight className="w-4 h-4 opacity-50" />
                  </div>
                </Link>
              )
            })}
            {upcomingEvents.length > 10 && (
              <p className="text-sm text-gray-500 text-center">
                +{upcomingEvents.length - 10} more events
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
