<template>
  <div class="app-shell">
    <header class="app-header">
      <RouterLink class="brand" to="/" aria-label="StudyForge home">
        <span class="brand-mark">SF</span>
        <span>
          <strong>StudyForge</strong>
          <small>AI study companion</small>
        </span>
      </RouterLink>
      <nav class="top-nav" aria-label="Main navigation">
        <RouterLink to="/">Input</RouterLink>
        <RouterLink to="/results">Results</RouterLink>
      </nav>
    </header>

    <main>
      <RouterView />
    </main>

    <footer class="app-footer">
      <span>StudyForge MVP</span>
      <span>Verify AI-generated study material against your source.</span>
    </footer>
  </div>
</template>
