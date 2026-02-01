export type ContractType =
  | 'insurance'
  | 'utility'
  | 'subscription'
  | 'rental'
  | 'saas'
  | 'service'
  | 'other'

export type PaymentFrequency =
  | 'monthly'
  | 'annual'
  | 'quarterly'
  | 'one-time'
  | 'other'

export interface Contract {
  id: string
  user_id: string
  provider_name: string
  contract_type: ContractType | null
  monthly_cost: number | null
  annual_cost: number | null
  currency: string
  payment_frequency: PaymentFrequency | null
  start_date: string | null
  end_date: string | null
  auto_renewal: boolean
  cancellation_notice_days: number | null
  key_terms: string[]
  file_path: string | null
  file_name: string | null
  extraction_confidence: number | null
  user_verified: boolean
  created_at: string
  updated_at: string
}

export interface ContractSummary {
  total_contracts: number
  total_monthly_spend: number
  total_annual_spend: number
  contracts_by_type: Record<string, number>
  expiring_soon: number
  auto_renewal_count: number
}

export interface ExtractionResult {
  provider_name: string | null
  contract_type: string | null
  monthly_cost: number | null
  annual_cost: number | null
  payment_frequency: string | null
  start_date: string | null
  end_date: string | null
  auto_renewal: boolean | null
  cancellation_notice_days: number | null
  key_terms: string[]
  confidence: number
}

export type RecommendationType =
  | 'cost_reduction'
  | 'consolidation'
  | 'risk_alert'
  | 'renewal_reminder'

export type Priority = 'high' | 'medium' | 'low'

export type RecommendationStatus = 'pending' | 'viewed' | 'accepted' | 'dismissed'

export interface Recommendation {
  id: string
  user_id: string
  contract_id: string | null
  type: RecommendationType
  title: string
  description: string
  estimated_savings: number | null
  priority: Priority
  status: RecommendationStatus
  reasoning: string | null
  confidence: number | null
  created_at: string
  acted_on_at: string | null
}
