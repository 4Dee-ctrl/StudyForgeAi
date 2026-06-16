<script setup>
import { ref } from 'vue'
import { useStudyStore } from '../stores/study'

const emit = defineEmits(['extracted'])
const store = useStudyStore()
const fileInput = ref(null)
const isDragging = ref(false)

function chooseFile() {
  fileInput.value?.click()
}

async function handleFile(file) {
  if (!file) return
  await store.extractFile(file)
  emit('extracted')
}

async function onInput(event) {
  const [file] = event.target.files || []
  await handleFile(file)
  event.target.value = ''
}

async function onDrop(event) {
  isDragging.value = false
  const [file] = event.dataTransfer.files || []
  await handleFile(file)
}
</script>

<template>
  <section class="input-panel">
    <div class="section-title-row">
      <div>
        <h2>Upload File</h2>
        <p>PDF and PPTX files up to 10 MB.</p>
      </div>
    </div>

    <button
      type="button"
      :class="['upload-zone', { dragging: isDragging }]"
      :disabled="store.isExtracting"
      @click="chooseFile"
      @dragenter.prevent="isDragging = true"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="onDrop"
    >
      <span class="upload-icon">+</span>
      <strong>{{ store.isExtracting ? 'Extracting text...' : 'Drop a file here or browse' }}</strong>
      <small v-if="store.sourceFile">{{ store.sourceFile.filename }} · {{ store.sourceFile.word_count }} words</small>
      <small v-else>Accepted formats: .pdf, .pptx</small>
    </button>

    <input ref="fileInput" class="sr-only" type="file" accept=".pdf,.pptx" @change="onInput" />
  </section>
</template>
