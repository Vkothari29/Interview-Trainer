/**
 * main.js — Shared utilities loaded on all pages
 */

// ── Auto-apply stored theme on load (before Bootstrap kicks in) ──
(function () {
  const stored = localStorage.getItem('theme') || 'auto';
  document.documentElement.setAttribute('data-bs-theme', stored);
})();

// ── Dismiss alerts after 5 s ──
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.alert-dismissible').forEach(el => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
      bsAlert && bsAlert.close();
    }, 5000);
  });
});
