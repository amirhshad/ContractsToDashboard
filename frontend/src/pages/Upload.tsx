import { useState, useCallback, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload as UploadIcon, FileText, AlertCircle, X, Plus } from 'lucide-react'
import { extractContracts, confirmContracts } from '../lib/api'
import type { ExtractionResult, UploadFile, DocumentType } from '../types'
import { DOCUMENT_TYPE_OPTIONS } from '../types'
import ExtractionReview from '../components/ExtractionReview'

// Multi-document upload support (v2)
const MAX_FILES = 5
const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB

export default function Upload() {
  const navigate = useNavigate()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [files, setFiles] = useState<UploadFile[]>([])
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

    if (e.dataTransfer.files) {
      handleFiles(Array.from(e.dataTransfer.files))
    }
  }, [files])

  const validateFile = (file: File): string | null => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      return `${file.name}: Only PDF files are allowed`
    }
    if (file.size > MAX_FILE_SIZE) {
      return `${file.name}: File size must be less than 10MB`
    }
    return null
  }

  const handleFiles = (newFiles: File[]) => {
    // Check total file count
    if (files.length + newFiles.length > MAX_FILES) {
      setError(`Maximum ${MAX_FILES} documents allowed per contract`)
      return
    }

    // Validate each file
    const errors: string[] = []
    const validFiles: UploadFile[] = []

    for (const file of newFiles) {
      const validationError = validateFile(file)
      if (validationError) {
        errors.push(validationError)
      } else {
        // Check for duplicates
        if (files.some(f => f.file.name === file.name)) {
          errors.push(`${file.name}: File already added`)
        } else {
          // Determine default document type based on file name or position
          let defaultType: DocumentType = 'other'
          const lowerName = file.name.toLowerCase()
          if (lowerName.includes('sow') || lowerName.includes('statement of work')) {
            defaultType = 'sow'
          } else if (lowerName.includes('terms') || lowerName.includes('conditions') || lowerName.includes('t&c')) {
            defaultType = 'terms_conditions'
          } else if (lowerName.includes('amendment')) {
            defaultType = 'amendment'
          } else if (lowerName.includes('addendum')) {
            defaultType = 'addendum'
          } else if (files.length === 0) {
            defaultType = 'main_agreement'
          }

          validFiles.push({
            file,
            document_type: defaultType,
            label: file.name.replace('.pdf', '').replace(/_/g, ' ')
          })
        }
      }
    }

    if (errors.length > 0) {
      setError(errors.join('\n'))
    } else {
      setError(null)
    }

    if (validFiles.length > 0) {
      setFiles(prev => [...prev, ...validFiles])
    }
  }

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
    setError(null)
  }

  const updateFileType = (index: number, docType: DocumentType) => {
    setFiles(prev => prev.map((f, i) =>
      i === index ? { ...f, document_type: docType } : f
    ))
  }

  const updateFileLabel = (index: number, label: string) => {
    setFiles(prev => prev.map((f, i) =>
      i === index ? { ...f, label } : f
    ))
  }

  const handleExtract = async () => {
    if (files.length === 0) return

    try {
      setExtracting(true)
      setError(null)
      const result = await extractContracts(files)
      setExtraction(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to extract contract data')
    } finally {
      setExtracting(false)
    }
  }

  const handleConfirm = async (data: ExtractionResult) => {
    if (files.length === 0) return

    try {
      setSaving(true)
      await confirmContracts(files, data)
      navigate('/contracts')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save contract')
    } finally {
      setSaving(false)
    }
  }

  const handleReset = () => {
    setFiles([])
    setExtraction(null)
    setError(null)
  }

  const triggerFileInput = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Upload Contract</h1>
        <p className="text-gray-600">
          Upload PDF contracts and our AI will extract the key information.
          You can upload multiple related documents (up to {MAX_FILES}).
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md flex items-start space-x-2">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <span className="whitespace-pre-line">{error}</span>
        </div>
      )}

      {!extraction ? (
        <div className="space-y-6">
          {/* Drop zone */}
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              dragActive
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            {extracting ? (
              <div className="space-y-4">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
                <p className="text-gray-600">Analyzing {files.length} document{files.length > 1 ? 's' : ''}...</p>
                <p className="text-sm text-gray-500">This may take a moment</p>
              </div>
            ) : (
              <>
                <UploadIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 mb-2">
                  Drag and drop your PDFs here, or{' '}
                  <button
                    onClick={triggerFileInput}
                    className="text-primary-600 hover:text-primary-700 cursor-pointer font-medium"
                  >
                    browse
                  </button>
                </p>
                <p className="text-sm text-gray-500">
                  PDF files up to 10MB each • Max {MAX_FILES} documents
                </p>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf"
                  multiple
                  className="hidden"
                  onChange={(e) => e.target.files && handleFiles(Array.from(e.target.files))}
                />
              </>
            )}
          </div>

          {/* File list */}
          {files.length > 0 && !extracting && (
            <div className="space-y-4">
              <h3 className="font-medium text-gray-900">
                Documents ({files.length}/{MAX_FILES})
              </h3>

              <div className="space-y-3">
                {files.map((uploadFile, index) => (
                  <div
                    key={index}
                    className="border border-gray-200 rounded-lg p-4 bg-white"
                  >
                    <div className="flex items-start gap-4">
                      <FileText className="w-8 h-8 text-primary-600 flex-shrink-0 mt-1" />

                      <div className="flex-1 min-w-0 space-y-3">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-medium text-gray-900 truncate">
                              {uploadFile.file.name}
                            </p>
                            <p className="text-sm text-gray-500">
                              {(uploadFile.file.size / 1024 / 1024).toFixed(2)} MB
                            </p>
                          </div>
                          <button
                            onClick={() => removeFile(index)}
                            className="text-gray-400 hover:text-red-500 p-1"
                          >
                            <X className="w-5 h-5" />
                          </button>
                        </div>

                        <div className="grid grid-cols-2 gap-3">
                          <div>
                            <label className="block text-sm text-gray-600 mb-1">
                              Document Type
                            </label>
                            <select
                              value={uploadFile.document_type}
                              onChange={(e) => updateFileType(index, e.target.value as DocumentType)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-primary-500 focus:border-primary-500"
                            >
                              {DOCUMENT_TYPE_OPTIONS.map(opt => (
                                <option key={opt.value} value={opt.value}>
                                  {opt.label}
                                </option>
                              ))}
                            </select>
                          </div>

                          <div>
                            <label className="block text-sm text-gray-600 mb-1">
                              Label (optional)
                            </label>
                            <input
                              type="text"
                              value={uploadFile.label}
                              onChange={(e) => updateFileLabel(index, e.target.value)}
                              placeholder="e.g., 2024 SOW"
                              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-primary-500 focus:border-primary-500"
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Add more button */}
              {files.length < MAX_FILES && (
                <button
                  onClick={triggerFileInput}
                  className="flex items-center gap-2 text-primary-600 hover:text-primary-700 font-medium"
                >
                  <Plus className="w-4 h-4" />
                  Add More Documents
                </button>
              )}

              {/* Action buttons */}
              <div className="flex gap-3 pt-4 border-t">
                <button
                  onClick={handleReset}
                  className="px-4 py-2 text-gray-700 hover:text-gray-900"
                >
                  Clear All
                </button>
                <button
                  onClick={handleExtract}
                  disabled={files.length === 0}
                  className="flex-1 bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Analyze {files.length} Document{files.length > 1 ? 's' : ''}
                </button>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-6">
          {/* Documents analyzed summary */}
          {extraction.documents_analyzed && extraction.documents_analyzed.length > 1 && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="text-sm font-medium text-blue-800 mb-3">
                Documents Analyzed ({extraction.documents_analyzed.length})
              </h3>
              <ul className="space-y-2">
                {extraction.documents_analyzed.map((doc, i) => (
                  <li key={i} className="text-sm text-blue-700">
                    <span className="font-medium">{doc.filename}</span>
                    <span className="text-blue-600"> ({doc.document_type})</span>
                    {doc.summary && (
                      <p className="text-blue-600 mt-0.5">{doc.summary}</p>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <ExtractionReview
            extraction={extraction}
            confidence={extraction.confidence}
            onConfirm={handleConfirm}
            onCancel={handleReset}
            saving={saving}
          />
        </div>
      )}
    </div>
  )
}
