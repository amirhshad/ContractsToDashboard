import { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  TrendingDown,
  Layers,
  AlertTriangle,
  Clock,
  Check,
  X,
  DollarSign,
  ExternalLink,
} from 'lucide-react'
import { updateRecommendation } from '../lib/api'
import type { Recommendation, Contract } from '../types'

interface RecommendationCardProps {
  recommendation: Recommendation
  contracts: Contract[]
  onUpdate: () => void
}

const typeConfig = {
  cost_reduction: {
    icon: TrendingDown,
    color: 'text-green-600',
    bg: 'bg-green-50',
    label: 'Cost Reduction',
  },
  consolidation: {
    icon: Layers,
    color: 'text-blue-600',
    bg: 'bg-blue-50',
    label: 'Consolidation',
  },
  risk_alert: {
    icon: AlertTriangle,
    color: 'text-red-600',
    bg: 'bg-red-50',
    label: 'Risk Alert',
  },
  renewal_reminder: {
    icon: Clock,
    color: 'text-yellow-600',
    bg: 'bg-yellow-50',
    label: 'Renewal Reminder',
  },
}

const priorityStyles = {
  high: 'border-l-red-500',
  medium: 'border-l-yellow-500',
  low: 'border-l-gray-400',
}

export default function RecommendationCard({
  recommendation,
  contracts,
  onUpdate,
}: RecommendationCardProps) {
  const [updating, setUpdating] = useState(false)

  const config = typeConfig[recommendation.type]
  const Icon = config.icon

  // Find the contract this recommendation refers to
  const relatedContract = recommendation.contract_id
    ? contracts.find(c => c.id === recommendation.contract_id)
    : null

  const handleAction = async (action: 'accepted' | 'dismissed') => {
    try {
      setUpdating(true)
      await updateRecommendation(recommendation.id, action)
      onUpdate()
    } catch (err) {
      console.error('Failed to update recommendation:', err)
    } finally {
      setUpdating(false)
    }
  }

  return (
    <div
      className={`bg-white border border-gray-200 rounded-lg p-4 border-l-4 ${
        priorityStyles[recommendation.priority]
      }`}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3">
          <div className={`p-2 rounded-lg ${config.bg}`}>
            <Icon className={`w-5 h-5 ${config.color}`} />
          </div>
          <div className="flex-1">
            <div className="flex items-center space-x-2">
              <h3 className="font-medium text-gray-900">{recommendation.title}</h3>
              <span
                className={`text-xs px-2 py-0.5 rounded-full ${config.bg} ${config.color}`}
              >
                {config.label}
              </span>
            </div>
            <p className="text-sm text-gray-600 mt-1">{recommendation.description}</p>

            <div className="flex flex-wrap items-center gap-3 mt-2">
              {relatedContract && (
                <Link
                  to={`/contracts/${relatedContract.id}/analysis`}
                  className="inline-flex items-center text-sm text-primary-600 hover:text-primary-700"
                >
                  <ExternalLink className="w-3 h-3 mr-1" />
                  {relatedContract.provider_name}
                </Link>
              )}
              {!relatedContract && recommendation.contract_id === null && (
                <span className="text-sm text-gray-500 italic">Portfolio-wide</span>
              )}
              {recommendation.estimated_savings && (
                <div className="flex items-center space-x-1 text-green-600">
                  <DollarSign className="w-4 h-4" />
                  <span className="text-sm font-medium">
                    Est. savings: ${recommendation.estimated_savings.toLocaleString()}/year
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2 ml-4">
          <button
            onClick={() => handleAction('accepted')}
            disabled={updating}
            className="p-2 text-green-600 hover:bg-green-50 rounded-md transition-colors disabled:opacity-50"
            title="Accept"
          >
            <Check className="w-5 h-5" />
          </button>
          <button
            onClick={() => handleAction('dismissed')}
            disabled={updating}
            className="p-2 text-gray-400 hover:bg-gray-50 rounded-md transition-colors disabled:opacity-50"
            title="Dismiss"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  )
}
