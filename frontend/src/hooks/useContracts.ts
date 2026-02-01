import { useEffect, useState, useCallback } from 'react'
import { getContracts, getContractSummary, deleteContract as apiDeleteContract } from '../lib/api'
import type { Contract, ContractSummary } from '../types'

export function useContracts() {
  const [contracts, setContracts] = useState<Contract[]>([])
  const [summary, setSummary] = useState<ContractSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchContracts = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const [contractsData, summaryData] = await Promise.all([
        getContracts(),
        getContractSummary(),
      ])
      setContracts(contractsData)
      setSummary(summaryData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch contracts')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchContracts()
  }, [fetchContracts])

  const deleteContract = async (id: string) => {
    try {
      await apiDeleteContract(id)
      setContracts(prev => prev.filter(c => c.id !== id))
      // Refresh summary
      const summaryData = await getContractSummary()
      setSummary(summaryData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete contract')
    }
  }

  return { contracts, summary, loading, error, refetch: fetchContracts, deleteContract }
}
