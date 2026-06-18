<template>
  <section class="landing-view">
    <div class="landing-hero">
      <div class="landing-copy">
        <p class="eyebrow">StudyForge AI</p>
        <h1>Build better study materials from the notes you already have.</h1>
        <video class="hero-video" autoplay muted loop playsinline>
        <source src="/hero-video.mp4" type="video/mp4" />
        </video>
        <p class="hero-copy">
          StudyForge helps students turn class content into summaries, key terms, quizzes, and study guides without making the AI workspace the first stop.
        </p>
        <div class="hero-actions">
          <RouterLink class="primary-button" to="/ai">Try the AI</RouterLink>
          <RouterLink class="ghost-button" to="/about">About StudyForge</RouterLink>
        </div>
      </div>
      <div class="hero-product-panel" aria-label="StudyForge feature preview">
        <div>
          <span>01</span>
          <strong>Add your material</strong>
          <small>Paste notes or upload a supported file.</small>
        </div>
        <div>
          <span>02</span>
          <strong>Choose study aids</strong>
          <small>Summaries, key terms, quizzes, and guides.</small>
        </div>
        <div>
          <span>03</span>
          <strong>Export results</strong>
          <small>Copy, print, or download polished outputs.</small>
        </div>
      </div>
    </div>

    <section class="feature-band">
      <article>
        <h2>Fast Prep</h2>
        <p>Move from raw source material to organized review content in minutes.</p>
      </article>
      <article>
        <h2>Flexible Inputs</h2>
        <p>Start with pasted text or extract text from documents when available.</p>
      </article>
      <article>
        <h2>Study Focused</h2>
        <p>Outputs are shaped for revision, recall practice, and quick review.</p>
      </article>
    </section>
  </section>
</template>
