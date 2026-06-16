<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import MarkdownRenderer from '../components/MarkdownRenderer.vue'
import { STUDY_AID_TYPES, useStudyStore } from '../stores/study'

const store = useStudyStore()
const router = useRouter()
const copied = ref(false)
const showSource = ref(false)

const availableTabs = computed(() => STUDY_AID_TYPES.filter((type) => store.selectedTypes.includes(type.id)))
const activeLabel = computed(() => STUDY_AID_TYPES.find((type) => type.id === store.activeTab)?.label || 'Study Aid')

async function copyActive() {
  if (!store.activeResult) return
  await navigator.clipboard.writeText(store.activeResult)
  copied.value = true
  window.setTimeout(() => {
    copied.value = false
  }, 1600)
}

function startOver() {
  store.clearAll()
  router.push('/')
}
</script>

<template>
  <section class="results-view">
    <div class="results-toolbar">
      <button class="ghost-button" type="button" @click="router.push('/')">Back to Input</button>
      <button class="ghost-button" type="button" @click="showSource = !showSource">
        {{ showSource ? 'Hide Source' : 'Show Source' }}
      </button>
      <button class="ghost-button" type="button" @click="startOver">Start Over</button>
    </div>

    <section v-if="showSource" class="source-preview">
      <h2>Source Preview</h2>
      <p>{{ store.sourceText.slice(0, 1200) }}{{ store.sourceText.length > 1200 ? '...' : '' }}</p>
    </section>

    <section v-if="!store.hasResults && !store.isGenerating" class="empty-state">
      <h1>No study aids yet</h1>
      <p>Paste or upload source material first, then generate results.</p>
      <button class="primary-button" type="button" @click="router.push('/')">Go to Input</button>
    </section>

    <template v-else>
      <div class="result-tabs" role="tablist" aria-label="Study aid results">
        <button
          v-for="type in availableTabs"
          :key="type.id"
          type="button"
          :class="['result-tab', { active: store.activeTab === type.id, error: store.typeErrors[type.id] }]"
          @click="store.setActiveTab(type.id)"
        >
          <span>{{ type.label }}</span>
          <small>{{ store.generationProgress[type.id] || 'ready' }}</small>
        </button>
      </div>

      <section class="result-card">
        <div class="result-card-header">
          <div>
            <p class="eyebrow">{{ activeLabel }}</p>
            <h1>{{ activeLabel }}</h1>
          </div>
          <div class="result-actions">
            <button class="ghost-button" type="button" :disabled="!store.activeResult" @click="copyActive">
              {{ copied ? 'Copied' : 'Copy' }}
            </button>
            <button
              class="ghost-button"
              type="button"
              :disabled="!store.activeResult || store.exporting[`${store.activeTab}:pdf`]"
              @click="store.exportResult(store.activeTab, 'pdf')"
            >
              PDF
            </button>
            <button
              class="ghost-button"
              type="button"
              :disabled="!store.activeResult || store.exporting[`${store.activeTab}:docx`]"
              @click="store.exportResult(store.activeTab, 'docx')"
            >
              Word
            </button>
          </div>
        </div>

        <div v-if="store.typeErrors[store.activeTab]" class="error-state">
          <h2>Could not generate this study aid</h2>
          <p>{{ store.typeErrors[store.activeTab] }}</p>
          <button class="secondary-button" type="button" @click="store.retryType(store.activeTab)">Retry</button>
        </div>

        <div v-else-if="!store.activeResult" class="loading-state">
          <span class="spinner"></span>
          <p>Generating {{ activeLabel.toLowerCase() }}...</p>
        </div>

        <Transition name="fade" mode="out-in">
          <MarkdownRenderer
            v-if="store.activeResult"
            :key="store.activeTab"
            :content="store.activeResult"
            :type="store.activeTab"
          />
        </Transition>
      </section>
    </template>
  </section>
</template>
