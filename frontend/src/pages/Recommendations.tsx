import { useState, useEffect, useMemo } from 'react'
import {
  Sparkles,
  RefreshCw,
  TrendingUp,
  Filter,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
} from 'lucide-react'
import { useContracts } from '../hooks/useContracts'
import { getRecommendations, generateRecommendations } from '../lib/api'
import type { Recommendation } from '../types'
import RecommendationCard from '../components/RecommendationCard'

type StatusFilter = 'all' | 'pending' | 'accepted' | 'dismissed'
type TypeFilter = 'all' | 'cost_reduction' | 'consolidation' | 'risk_alert' | 'renewal_reminder'
type PriorityFilter = 'all' | 'high' | 'medium' | 'low'

export default function Recommendations() {
  const { contracts, loading: contractsLoading } = useContracts()
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Filters
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('pending')
  const [typeFilter, setTypeFilter] = useState<TypeFilter>('all')
  const [priorityFilter, setPriorityFilter] = useState<PriorityFilter>('all')

  useEffect(() => {
    loadRecommendations()
  }, [])

  const loadRecommendations = async () => {
    try {
      setLoading(true)
      setError(null)
      const recs = await getRecommendations()
      setRecommendations(recs)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load recommendations')
    } finally {
      setLoading(false)
    }
  }

  const handleGenerate = async () => {
    try {
      setGenerating(true)
      setError(null)
      const recs = await generateRecommendations()
      setRecommendations(recs)
      setStatusFilter('pending') // Show newly generated recommendations
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate recommendations')
    } finally {
      setGenerating(false)
    }
  }

  const filteredRecommendations = useMemo(() => {
    return recommendations.filter((rec) => {
      if (statusFilter !== 'all') {
        if (statusFilter === 'pending' && rec.status !== 'pending' && rec.status !== 'viewed') {
          return false
        }
        if (statusFilter === 'accepted' && rec.status !== 'accepted') {
          return false
        }
        if (statusFilter === 'dismissed' && rec.status !== 'dismissed') {
          return false
        }
      }
      if (typeFilter !== 'all' && rec.type !== typeFilter) {
        return false
      }
      if (priorityFilter !== 'all' && rec.priority !== priorityFilter) {
        return false
      }
      return true
    })
  }, [recommendations, statusFilter, typeFilter, priorityFilter])

  // Stats
  const stats = useMemo(() => {
    const pending = recommendations.filter(r => r.status === 'pending' || r.status === 'viewed')
    const accepted = recommendations.filter(r => r.status === 'accepted')
    const dismissed = recommendations.filter(r => r.status === 'dismissed')
    const highPriority = pending.filter(r => r.priority === 'high')
    const totalSavings = pending.reduce((sum, r) => sum + (r.estimated_savings || 0), 0)

    return { pending, accepted, dismissed, highPriority, totalSavings }
  }, [recommendations])

  if (loading || contractsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">AI Recommendations</h1>
          <p className="text-gray-600">Smart insights to optimize your contracts</p>
        </div>
        <button
          onClick={handleGenerate}
          disabled={generating || contracts.length === 0}
          className="w-full sm:w-auto inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {generating ? (
            <>
              <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4 mr-2" />
              Generate New
            </>
          )}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
          {error}
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center space-x-3">
            <div className="bg-blue-500 p-2 rounded-lg">
              <Clock className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Pending</p>
              <p className="text-xl font-semibold text-gray-900">{stats.pending.length}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center space-x-3">
            <div className="bg-red-500 p-2 rounded-lg">
              <AlertTriangle className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="text-sm text-gray-600">High Priority</p>
              <p className="text-xl font-semibold text-gray-900">{stats.highPriority.length}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center space-x-3">
            <div className="bg-green-500 p-2 rounded-lg">
              <TrendingUp className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Potential Savings</p>
              <p className="text-xl font-semibold text-gray-900">
                ${stats.totalSavings.toLocaleString()}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center space-x-3">
            <div className="bg-purple-500 p-2 rounded-lg">
              <CheckCircle className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Acted On</p>
              <p className="text-xl font-semibold text-gray-900">
                {stats.accepted.length + stats.dismissed.length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex items-center gap-2 mb-3">
          <Filter className="w-4 h-4 text-gray-500" />
          <span className="text-sm font-medium text-gray-700">Filters</span>
        </div>
        <div className="flex flex-wrap gap-4">
          <div>
            <label className="block text-xs text-gray-500 mb-1">Status</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as StatusFilter)}
              className="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="all">All</option>
              <option value="pending">Pending</option>
              <option value="accepted">Accepted</option>
              <option value="dismissed">Dismissed</option>
            </select>
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Type</label>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value as TypeFilter)}
              className="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="all">All Types</option>
              <option value="cost_reduction">Cost Reduction</option>
              <option value="consolidation">Consolidation</option>
              <option value="risk_alert">Risk Alert</option>
              <option value="renewal_reminder">Renewal Reminder</option>
            </select>
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Priority</label>
            <select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value as PriorityFilter)}
              className="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="all">All Priorities</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
        </div>
      </div>

      {/* Recommendations List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">
            {statusFilter === 'all' ? 'All' : statusFilter.charAt(0).toUpperCase() + statusFilter.slice(1)} Recommendations
          </h2>
          <span className="text-sm text-gray-500">
            {filteredRecommendations.length} {filteredRecommendations.length === 1 ? 'result' : 'results'}
          </span>
        </div>

        {contracts.length === 0 ? (
          <div className="text-center py-12">
            <Sparkles className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No contracts yet</h3>
            <p className="text-gray-500">
              Upload contracts to get AI-powered recommendations.
            </p>
          </div>
        ) : filteredRecommendations.length === 0 ? (
          <div className="text-center py-12">
            {recommendations.length === 0 ? (
              <>
                <Sparkles className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No recommendations yet</h3>
                <p className="text-gray-500 mb-4">
                  Click "Generate New" to analyze your contracts and get smart recommendations.
                </p>
                <button
                  onClick={handleGenerate}
                  disabled={generating}
                  className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50"
                >
                  <Sparkles className="w-4 h-4 mr-2" />
                  Generate Recommendations
                </button>
              </>
            ) : (
              <>
                <Filter className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No matching recommendations</h3>
                <p className="text-gray-500">
                  Try adjusting your filters to see more results.
                </p>
              </>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            {filteredRecommendations.map((rec) => (
              <RecommendationCard
                key={rec.id}
                recommendation={rec}
                contracts={contracts}
                onUpdate={loadRecommendations}
              />
            ))}
          </div>
        )}
      </div>

      {/* History Section */}
      {(stats.accepted.length > 0 || stats.dismissed.length > 0) && statusFilter === 'pending' && (
        <div className="bg-gray-50 rounded-lg border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-600" />
                <span className="text-sm text-gray-600">
                  {stats.accepted.length} accepted
                </span>
              </div>
              <div className="flex items-center gap-2">
                <XCircle className="w-4 h-4 text-red-600" />
                <span className="text-sm text-gray-600">
                  {stats.dismissed.length} dismissed
                </span>
              </div>
            </div>
            <button
              onClick={() => setStatusFilter('all')}
              className="text-sm text-primary-600 hover:text-primary-700"
            >
              View history
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
