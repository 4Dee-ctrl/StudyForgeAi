<script setup>
import { computed, ref } from 'vue'
import DOMPurify from 'dompurify'
import { marked } from 'marked'

const props = defineProps({
  content: {
    type: String,
    required: true,
  },
  type: {
    type: String,
    default: 'summary',
  },
})

const showAnswerKey = ref(false)

marked.use({
  gfm: true,
  breaks: true,
})

const splitQuiz = computed(() => {
  if (props.type !== 'quiz') return null
  const marker = /(^|\n)#\s*Answer Key/i
  const match = props.content.match(marker)
  if (!match || match.index === undefined) return null

  return {
    questions: props.content.slice(0, match.index).trim(),
    answers: props.content.slice(match.index).trim(),
  }
})

function renderMarkdown(markdown) {
  return DOMPurify.sanitize(marked.parse(markdown || ''), {
    ADD_ATTR: ['target', 'rel'],
  })
}

const html = computed(() => renderMarkdown(props.content))
const questionHtml = computed(() => renderMarkdown(splitQuiz.value?.questions || ''))
const answerHtml = computed(() => renderMarkdown(splitQuiz.value?.answers || ''))
</script>

<template>
  <article :class="['markdown-body', `markdown-${type}`]">
    <template v-if="splitQuiz">
      <div v-html="questionHtml"></div>
      <div class="answer-key-toggle">
        <button type="button" class="secondary-button" @click="showAnswerKey = !showAnswerKey">
          {{ showAnswerKey ? 'Hide Answer Key' : 'Show Answer Key' }}
        </button>
      </div>
      <Transition name="fade">
        <div v-if="showAnswerKey" class="answer-key" v-html="answerHtml"></div>
      </Transition>
    </template>
    <div v-else v-html="html"></div>
  </article>
</template>
