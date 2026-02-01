import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload as UploadIcon, FileText, X, Check, AlertCircle } from 'lucide-react'
import { extractContract, confirmContract } from '../lib/api'
import type { ExtractionResult } from '../types'
import ExtractionReview from '../components/ExtractionReview'

export default function Upload() {
  const navigate = useNavigate()
  const [file, setFile] = useState<File | null>(null)
  const [dragActive, setDragActive] = useState(false)
  const [extracting, setExtracting] = useState(false)
  const [extraction, setExtraction] = useState<ExtractionResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }, [])

  const handleFile = async (selectedFile: File) => {
    if (!selectedFile.name.toLowerCase().endsWith('.pdf')) {
      setError('Please upload a PDF file')
      return
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB')
      return
    }

    setFile(selectedFile)
    setError(null)
    setExtraction(null)

    // Start extraction
    try {
      setExtracting(true)
      const result = await extractContract(selectedFile)
      setExtraction(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to extract contract data')
    } finally {
      setExtracting(false)
    }
  }

  const handleConfirm = async (data: ExtractionResult) => {
    if (!file) return

    try {
      setSaving(true)
      await confirmContract(file, data)
      navigate('/contracts')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save contract')
    } finally {
      setSaving(false)
    }
  }

  const handleReset = () => {
    setFile(null)
    setExtraction(null)
    setError(null)
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Upload Contract</h1>
        <p className="text-gray-600">
          Upload a PDF contract and our AI will extract the key information.
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md flex items-center space-x-2">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {!extraction ? (
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
            dragActive
              ? 'border-primary-500 bg-primary-50'
              : 'border-gray-300 hover:border-gray-400'
          }`}
        >
          {extracting ? (
            <div className="space-y-4">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
              <p className="text-gray-600">Extracting contract data...</p>
              <p className="text-sm text-gray-500">This may take a moment</p>
            </div>
          ) : file ? (
            <div className="space-y-4">
              <FileText className="w-12 h-12 text-primary-600 mx-auto" />
              <div>
                <p className="font-medium text-gray-900">{file.name}</p>
                <p className="text-sm text-gray-500">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
              <button
                onClick={handleReset}
                className="text-sm text-red-600 hover:text-red-700"
              >
                Remove
              </button>
            </div>
          ) : (
            <>
              <UploadIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-2">
                Drag and drop your PDF here, or{' '}
                <label className="text-primary-600 hover:text-primary-700 cursor-pointer">
                  browse
                  <input
                    type="file"
                    accept=".pdf"
                    className="hidden"
                    onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
                  />
                </label>
              </p>
              <p className="text-sm text-gray-500">PDF files up to 10MB</p>
            </>
          )}
        </div>
      ) : (
        <ExtractionReview
          extraction={extraction}
          confidence={extraction.confidence}
          onConfirm={handleConfirm}
          onCancel={handleReset}
          saving={saving}
        />
      )}
    </div>
  )
}
