import { defineStore } from 'pinia'
import { extractFile, exportStudyAid, generateStudyAid } from '../services/api'

const STORAGE_KEY = 'studyforge-study-session-v1'

export const STUDY_AID_TYPES = [
  { id: 'summary', label: 'Summary' },
  { id: 'key_terms', label: 'Key Terms' },
  { id: 'quiz', label: 'Quiz' },
  { id: 'study_guide', label: 'Study Guide' },
]

function initialResults() {
  return {
    summary: null,
    key_terms: null,
    quiz: null,
    study_guide: null,
  }
}

function defaultSelectedTypes() {
  return STUDY_AID_TYPES.map((type) => type.id)
}

function loadPersistedSession() {
  if (typeof window === 'undefined') return null

  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (!raw) return null

    const parsed = JSON.parse(raw)
    const selectedTypes = Array.isArray(parsed.selectedTypes) && parsed.selectedTypes.length
      ? parsed.selectedTypes.filter((type) => STUDY_AID_TYPES.some((item) => item.id === type))
      : defaultSelectedTypes()
    const results = { ...initialResults(), ...(parsed.results || {}) }
    const activeTab = STUDY_AID_TYPES.some((type) => type.id === parsed.activeTab)
      ? parsed.activeTab
      : selectedTypes[0] || 'summary'

    return {
      sourceText: parsed.sourceText || '',
      sourceFile: parsed.sourceFile || null,
      selectedTypes,
      results,
      resultMeta: parsed.resultMeta || {},
      typeErrors: parsed.typeErrors || {},
      activeTab,
      generationProgress: parsed.generationProgress || Object.fromEntries(
        selectedTypes.map((type) => [type, results[type] ? 'done' : 'ready']),
      ),
    }
  } catch {
    window.localStorage.removeItem(STORAGE_KEY)
    return null
  }
}

function hasStoredResults(results) {
  return Object.values(results || {}).some(Boolean)
}

export const useStudyStore = defineStore('study', {
  state: () => {
    const persisted = loadPersistedSession()

    return {
      sourceText: persisted?.sourceText || '',
      sourceFile: persisted?.sourceFile || null,
      selectedTypes: persisted?.selectedTypes || defaultSelectedTypes(),
      isExtracting: false,
      isGenerating: false,
      generationProgress: persisted?.generationProgress || {},
      results: persisted?.results || initialResults(),
      resultMeta: persisted?.resultMeta || {},
      error: null,
      typeErrors: persisted?.typeErrors || {},
      activeTab: persisted?.activeTab || 'summary',
      exporting: {},
    }
  },

  getters: {
    charCount: (state) => state.sourceText.length,
    hasSourceText: (state) => state.sourceText.trim().length >= 50,
    isOverLimit: (state) => state.sourceText.length > 50000,
    hasResults: (state) => Object.values(state.results).some(Boolean),
    canGenerate() {
      return this.hasSourceText && this.selectedTypes.length > 0 && !this.isGenerating && !this.isOverLimit
    },
    activeResult: (state) => state.results[state.activeTab],
  },

  actions: {
    persistSession() {
      if (typeof window === 'undefined') return

      if (!hasStoredResults(this.results)) {
        window.localStorage.removeItem(STORAGE_KEY)
        return
      }

      window.localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          sourceText: this.sourceText,
          sourceFile: this.sourceFile,
          selectedTypes: this.selectedTypes,
          generationProgress: this.generationProgress,
          results: this.results,
          resultMeta: this.resultMeta,
          typeErrors: this.typeErrors,
          activeTab: this.activeTab,
        }),
      )
    },

    setSourceText(text) {
      this.sourceText = text
      this.error = null
    },

    toggleType(type) {
      if (this.selectedTypes.includes(type)) {
        this.selectedTypes = this.selectedTypes.filter((item) => item !== type)
      } else {
        this.selectedTypes = [...this.selectedTypes, type]
      }
    },

    setActiveTab(type) {
      this.activeTab = type
      this.persistSession()
    },

    async extractFile(file) {
      this.error = null
      this.isExtracting = true

      try {
        const response = await extractFile(file)
        this.sourceText = response.text
        this.sourceFile = response.metadata
        if (response.warning) {
          this.error = response.warning
        }
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.isExtracting = false
      }
    },

    async generateAll() {
      if (!this.canGenerate) return false

      this.error = null
      this.typeErrors = {}
      this.resultMeta = {}
      this.results = initialResults()
      this.isGenerating = true
      this.generationProgress = Object.fromEntries(this.selectedTypes.map((type) => [type, 'waiting']))
      this.activeTab = this.selectedTypes[0]
      this.persistSession()

      await Promise.all(
        this.selectedTypes.map(async (type) => {
          this.generationProgress[type] = 'loading'
          try {
            const response = await generateStudyAid(this.sourceText.trim(), type)
            this.results[type] = response.content
            this.resultMeta[type] = response.meta
            this.generationProgress[type] = 'done'
          } catch (error) {
            this.typeErrors[type] = error.message
            this.generationProgress[type] = 'error'
          }
        }),
      )

      this.isGenerating = false

      const generated = this.selectedTypes.some((type) => this.results[type])
      if (!generated) {
        this.error = 'Study aid generation failed. Please try again.'
      }

      this.persistSession()
      return generated
    },

    async retryType(type) {
      this.typeErrors[type] = null
      this.generationProgress[type] = 'loading'

      try {
        const response = await generateStudyAid(this.sourceText.trim(), type)
        this.results[type] = response.content
        this.resultMeta[type] = response.meta
        this.generationProgress[type] = 'done'
      } catch (error) {
        this.typeErrors[type] = error.message
        this.generationProgress[type] = 'error'
      } finally {
        this.persistSession()
      }
    },

    async exportResult(type, format) {
      const content = this.results[type]
      if (!content) return

      const key = `${type}:${format}`
      this.exporting[key] = true
      this.error = null

      try {
        const response = await exportStudyAid(content, format, STUDY_AID_TYPES.find((item) => item.id === type)?.label || 'Study Aid')
        const blob = response.data instanceof Blob ? response.data : new Blob([response.data])
        const blobUrl = URL.createObjectURL(blob)
        const filename = `${type}.${format}`

        if (format === 'pdf') {
          window.location.href = blobUrl
          window.setTimeout(() => URL.revokeObjectURL(blobUrl), 300000)
          return
        }

        const link = document.createElement('a')
        link.href = blobUrl
        link.download = filename
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.setTimeout(() => URL.revokeObjectURL(blobUrl), 60000)
      } catch (error) {
        this.error = error.message || 'Export failed. Please try again.'
        throw error
      } finally {
        this.exporting[key] = false
      }
    },

    clearAll() {
      this.sourceText = ''
      this.sourceFile = null
      this.selectedTypes = defaultSelectedTypes()
      this.isExtracting = false
      this.isGenerating = false
      this.generationProgress = {}
      this.results = initialResults()
      this.resultMeta = {}
      this.error = null
      this.typeErrors = {}
      this.activeTab = 'summary'
      this.exporting = {}
      if (typeof window !== 'undefined') {
        window.localStorage.removeItem(STORAGE_KEY)
      }
    },
  },
})
