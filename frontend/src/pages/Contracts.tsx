import { useState } from 'react'
import { FileText, Trash2, Search, Filter, Download } from 'lucide-react'
import { useContracts } from '../hooks/useContracts'
import { getCurrencySymbol } from '../types'
import type { Contract } from '../types'

export default function Contracts() {
  const { contracts, loading, error, deleteContract } = useContracts()
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState<string>('')
  const [deletingId, setDeletingId] = useState<string | null>(null)

  const filteredContracts = contracts.filter((contract) => {
    const searchLower = search.toLowerCase()
    const matchesSearch =
      contract.provider_name.toLowerCase().includes(searchLower) ||
      (contract.contract_nickname?.toLowerCase().includes(searchLower) ?? false) ||
      (contract.contract_type?.toLowerCase().includes(searchLower) ?? false) ||
      (contract.key_terms?.some(term => term.toLowerCase().includes(searchLower)) ?? false)
    const matchesType = !typeFilter || contract.contract_type === typeFilter
    return matchesSearch && matchesType
  })

  const exportToCSV = () => {
    const headers = [
      'Contract Name',
      'Provider',
      'Type',
      'Monthly Cost',
      'Annual Cost',
      'Currency',
      'Start Date',
      'End Date',
      'Auto Renewal',
      'Cancellation Notice (Days)',
      'Key Terms'
    ]

    const rows = filteredContracts.map((contract: Contract) => [
      contract.contract_nickname || '',
      contract.provider_name,
      contract.contract_type || '',
      contract.monthly_cost?.toString() || '',
      contract.annual_cost?.toString() || '',
      contract.currency || 'USD',
      contract.start_date || '',
      contract.end_date || '',
      contract.auto_renewal ? 'Yes' : 'No',
      contract.cancellation_notice_days?.toString() || '',
      (contract.key_terms || []).join('; ')
    ])

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell.replace(/"/g, '""')}"`).join(','))
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `clausemate-contracts-${new Date().toISOString().split('T')[0]}.csv`
    link.click()
    URL.revokeObjectURL(link.href)
  }

  const contractTypes = [...new Set(contracts.map((c) => c.contract_type).filter(Boolean))]

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this contract?')) return

    setDeletingId(id)
    await deleteContract(id)
    setDeletingId(null)
  }

  const formatDate = (date: string | null) => {
    if (!date) return '-'
    return new Date(date).toLocaleDateString()
  }

  const formatCurrency = (amount: number | null, currency: string = 'USD') => {
    if (amount === null) return '-'
    return `${getCurrencySymbol(currency)}${amount.toLocaleString()}`
  }

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
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Contracts</h1>
          <p className="text-gray-600">{contracts.length} contracts total</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search contracts, providers, key terms..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
        <div className="relative">
          <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="pl-10 pr-8 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent appearance-none bg-white"
          >
            <option value="">All types</option>
            {contractTypes.map((type) => (
              <option key={type} value={type!}>
                {type}
              </option>
            ))}
          </select>
        </div>
        <button
          onClick={exportToCSV}
          disabled={filteredContracts.length === 0}
          className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed text-gray-700"
        >
          <Download className="w-4 h-4" />
          <span className="hidden sm:inline">Export CSV</span>
        </button>
      </div>

      {/* Empty state */}
      {filteredContracts.length === 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
          <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {contracts.length === 0 ? 'No contracts yet' : 'No matching contracts'}
          </h3>
          <p className="text-gray-600">
            {contracts.length === 0
              ? 'Upload your first contract to get started.'
              : 'Try adjusting your search or filters.'}
          </p>
        </div>
      )}

      {/* Contract list */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Contract
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Monthly Cost
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  End Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Auto-Renewal
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredContracts.map((contract) => (
                <tr key={contract.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <FileText className="w-5 h-5 text-gray-400 mr-3" />
                      <div>
                        <div className="font-medium text-gray-900">
                          {contract.contract_nickname || contract.provider_name}
                        </div>
                        <div className="text-sm text-gray-500">
                          {contract.contract_nickname
                            ? contract.provider_name
                            : contract.file_count && contract.file_count > 1
                              ? `${contract.file_count} documents`
                              : contract.file_name || '1 document'}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 capitalize">
                      {contract.contract_type || 'Unknown'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-900">
                    {formatCurrency(contract.monthly_cost, contract.currency)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-500">
                    {formatDate(contract.end_date)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        contract.auto_renewal
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {contract.auto_renewal ? 'Yes' : 'No'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => handleDelete(contract.id)}
                      disabled={deletingId === contract.id}
                      className="text-red-600 hover:text-red-900 disabled:opacity-50"
                    >
                      {deletingId === contract.id ? (
                        <span className="animate-spin">...</span>
                      ) : (
                        <Trash2 className="w-5 h-5" />
                      )}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
