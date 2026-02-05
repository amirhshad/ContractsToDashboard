import { useState } from 'react'
import { Check, X, AlertCircle, Zap } from 'lucide-react'
import type { ExtractionResult } from '../types'
import { CURRENCY_OPTIONS, getCurrencySymbol } from '../types'

interface ExtractionReviewProps {
  extraction: ExtractionResult
  confidence: number
  onConfirm: (data: ExtractionResult) => void
  onCancel: () => void
  saving: boolean
}

export default function ExtractionReview({
  extraction,
  confidence,
  onConfirm,
  onCancel,
  saving,
}: ExtractionReviewProps) {
  const [data, setData] = useState<ExtractionResult>(extraction)

  const confidenceColor =
    confidence >= 0.8
      ? 'text-green-600 bg-green-50'
      : confidence >= 0.5
      ? 'text-yellow-600 bg-yellow-50'
      : 'text-red-600 bg-red-50'

  const contractTypes = [
    'insurance',
    'utility',
    'subscription',
    'rental',
    'saas',
    'service',
    'other',
  ]

  const handleChange = (field: keyof ExtractionResult, value: unknown) => {
    setData((prev) => ({ ...prev, [field]: value }))
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">Review Extracted Data</h2>
        <div className="flex items-center gap-2">
          {extraction.escalated && (
            <span
              className="flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium text-purple-700 bg-purple-50"
              title={`Enhanced with ${extraction.escalation_model || 'advanced model'}`}
            >
              <Zap className="w-3.5 h-3.5" />
              Enhanced
            </span>
          )}
          <span
            className={`px-3 py-1 rounded-full text-sm font-medium ${confidenceColor}`}
          >
            {Math.round(confidence * 100)}% confidence
          </span>
        </div>
      </div>

      {confidence < 0.6 && (
        <div className="flex items-start space-x-2 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
          <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-yellow-700">
            The AI had difficulty extracting some data. Please review and correct the
            fields below.
          </p>
        </div>
      )}

      {extraction.escalated && (
        <div className="flex items-start space-x-2 p-3 bg-purple-50 border border-purple-200 rounded-md">
          <Zap className="w-5 h-5 text-purple-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-purple-700">
            This contract was analyzed with enhanced AI ({extraction.escalation_model === 'claude-sonnet-4' ? 'Claude Sonnet 4' : 'Gemini 2.5 Pro'}) for more thorough extraction of complex terms.
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Provider Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Provider Name *
          </label>
          <input
            type="text"
            value={data.provider_name || ''}
            onChange={(e) => handleChange('provider_name', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            required
          />
        </div>

        {/* Contract Nickname */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Contract Nickname
          </label>
          <input
            type="text"
            value={data.contract_nickname || ''}
            onChange={(e) => handleChange('contract_nickname', e.target.value || null)}
            placeholder="e.g., Car Insurance 2025, Office Lease"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        {/* Contract Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Contract Type
          </label>
          <select
            value={data.contract_type || ''}
            onChange={(e) => handleChange('contract_type', e.target.value || null)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">Select type</option>
            {contractTypes.map((type) => (
              <option key={type} value={type}>
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </option>
            ))}
          </select>
        </div>

        {/* Currency */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Currency
          </label>
          <select
            value={data.currency || 'USD'}
            onChange={(e) => handleChange('currency', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            {CURRENCY_OPTIONS.map((currency) => (
              <option key={currency.value} value={currency.value}>
                {currency.symbol} - {currency.label}
              </option>
            ))}
          </select>
        </div>

        {/* Monthly Cost */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Monthly Cost
          </label>
          <div className="relative">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">
              {getCurrencySymbol(data.currency || 'USD')}
            </span>
            <input
              type="number"
              step="0.01"
              min="0"
              value={data.monthly_cost ?? ''}
              onChange={(e) =>
                handleChange('monthly_cost', e.target.value ? parseFloat(e.target.value) : null)
              }
              className="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>

        {/* Annual Cost */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Annual Cost
          </label>
          <div className="relative">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">
              {getCurrencySymbol(data.currency || 'USD')}
            </span>
            <input
              type="number"
              step="0.01"
              min="0"
              value={data.annual_cost ?? ''}
              onChange={(e) =>
                handleChange('annual_cost', e.target.value ? parseFloat(e.target.value) : null)
              }
              className="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>

        {/* Start Date */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Start Date
          </label>
          <input
            type="date"
            value={data.start_date || ''}
            onChange={(e) => handleChange('start_date', e.target.value || null)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        {/* End Date */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            End Date
          </label>
          <input
            type="date"
            value={data.end_date || ''}
            onChange={(e) => handleChange('end_date', e.target.value || null)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        {/* Auto Renewal */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Auto Renewal
          </label>
          <select
            value={data.auto_renewal === null ? '' : data.auto_renewal ? 'yes' : 'no'}
            onChange={(e) =>
              handleChange(
                'auto_renewal',
                e.target.value === '' ? null : e.target.value === 'yes'
              )
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">Unknown</option>
            <option value="yes">Yes</option>
            <option value="no">No</option>
          </select>
        </div>

        {/* Cancellation Notice */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Cancellation Notice (days)
          </label>
          <input
            type="number"
            min="0"
            value={data.cancellation_notice_days ?? ''}
            onChange={(e) =>
              handleChange(
                'cancellation_notice_days',
                e.target.value ? parseInt(e.target.value) : null
              )
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
      </div>

      {/* Key Terms */}
      {data.key_terms && data.key_terms.length > 0 && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Key Terms
          </label>
          <div className="flex flex-wrap gap-2">
            {data.key_terms.map((term, index) => (
              <span
                key={index}
                className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-gray-100 text-gray-700"
              >
                {term}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-end space-x-3 pt-4 border-t">
        <button
          onClick={onCancel}
          disabled={saving}
          className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
        >
          <X className="w-4 h-4 inline mr-2" />
          Cancel
        </button>
        <button
          onClick={() => onConfirm(data)}
          disabled={saving || !data.provider_name}
          className="px-4 py-2 text-white bg-primary-600 rounded-md hover:bg-primary-700 disabled:opacity-50"
        >
          {saving ? (
            'Saving...'
          ) : (
            <>
              <Check className="w-4 h-4 inline mr-2" />
              Save Contract
            </>
          )}
        </button>
      </div>
    </div>
  )
}
