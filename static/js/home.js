/* ============================================================
   RapidVenta Home Page — Probid-style JS
   Handles: slider nav, countdown timers (DD:HH:MM:SS),
            stat counters, filter auto-submit, active category
   ============================================================ */

(function () {
  'use strict';

  /* ── Simple slider factory ────────────────────────────────── */
  function makeSlider(trackId, prevId, nextId, slideSelector) {
    var track = document.getElementById(trackId);
    var prevBtn = document.getElementById(prevId);
    var nextBtn = document.getElementById(nextId);
    if (!track || !prevBtn || !nextBtn) return;

    var slides = track.querySelectorAll(slideSelector || '.swiper-slide');
    if (!slides.length) return;

    var idx = 0;

    function getVisible() {
      var w = track.parentElement.offsetWidth;
      var gap = 24;
      var slideW = slides[0].offsetWidth + gap;
      return Math.max(1, Math.round((w + gap) / slideW));
    }

    function maxIdx() {
      return Math.max(0, slides.length - getVisible());
    }

    function go(n) {
      idx = Math.max(0, Math.min(n, maxIdx()));
      var gap = 24;
      var slideW = slides[0].offsetWidth + gap;
      track.style.transform = 'translateX(-' + (idx * slideW) + 'px)';
    }

    prevBtn.addEventListener('click', function () { go(idx - 1); });
    nextBtn.addEventListener('click', function () { go(idx + 1); });

    window.addEventListener('resize', function () { go(Math.min(idx, maxIdx())); });
  }

  /* ── Probid-style countdown (DD:HH:MM:SS) ────────────────── */
  function updateCountdown(ul) {
    var end = new Date(ul.dataset.end);
    var now = new Date();
    var diff = end - now;

    var dayEl  = ul.querySelector('[data-unit="days"]');
    var hrEl   = ul.querySelector('[data-unit="hours"]');
    var minEl  = ul.querySelector('[data-unit="minutes"]');
    var secEl  = ul.querySelector('[data-unit="seconds"]');

    if (!dayEl) return;

    if (diff <= 0) {
      dayEl.textContent = hrEl.textContent = minEl.textContent = secEl.textContent = '00';
      return;
    }

    var days    = Math.floor(diff / 86400000);
    var hours   = Math.floor((diff % 86400000) / 3600000);
    var minutes = Math.floor((diff % 3600000) / 60000);
    var seconds = Math.floor((diff % 60000) / 1000);

    dayEl.textContent  = pad(days);
    hrEl.textContent   = pad(hours);
    minEl.textContent  = pad(minutes);
    secEl.textContent  = pad(seconds);

    /* urgency styling if < 1 hour */
    if (diff < 3600000) {
      var card = ul.closest('.auction-card');
      if (card) card.style.borderColor = 'rgba(185,1,1,.4)';
    }
  }

  function pad(n) { return n < 10 ? '0' + n : String(n); }

  function initCountdowns() {
    var timers = document.querySelectorAll('.countdown-timer ul[data-end]');
    if (!timers.length) return;

    timers.forEach(function (ul) { updateCountdown(ul); });

    setInterval(function () {
      timers.forEach(function (ul) { updateCountdown(ul); });
    }, 1000);
  }

  /* ── Also drive the existing main.js countdown-display spans ─ */
  /* (for the hero featured card which uses data-end on a div) */
  function initHeroCountdown() {
    var wrappers = document.querySelectorAll('[data-end]:not(.countdown-timer ul)');
    wrappers.forEach(function (el) {
      var span = el.querySelector('.countdown-display');
      if (!span) return;

      function tick() {
        var end  = new Date(el.dataset.end);
        var diff = end - Date.now();
        if (diff <= 0) { span.textContent = 'Ended'; return; }
        var d = Math.floor(diff / 86400000);
        var h = Math.floor((diff % 86400000) / 3600000);
        var m = Math.floor((diff % 3600000)  / 60000);
        var s = Math.floor((diff % 60000)    / 1000);
        span.textContent = (d ? d + 'd ' : '') + pad(h) + ':' + pad(m) + ':' + pad(s);
      }

      tick();
      setInterval(tick, 1000);
    });
  }

  /* ── Stat counter animation ───────────────────────────────── */
  function animateCounter(el) {
    var target = parseInt(el.dataset.target, 10) || 0;
    if (!target) { el.textContent = '0'; return; }
    var duration = 1600;
    var start = performance.now();

    function step(now) {
      var progress = Math.min((now - start) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.round(eased * target);
      if (progress < 1) requestAnimationFrame(step);
    }

    requestAnimationFrame(step);
  }

  function initCounters() {
    var els = document.querySelectorAll('.js-counter[data-target]');
    if (!els.length) return;

    if ('IntersectionObserver' in window) {
      var obs = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) {
            animateCounter(e.target);
            obs.unobserve(e.target);
          }
        });
      }, { threshold: 0.5 });
      els.forEach(function (el) { obs.observe(el); });
    } else {
      els.forEach(animateCounter);
    }
  }

  /* ── Filter select auto-submit ────────────────────────────── */
  function initFilterAutoSubmit() {
    var form = document.getElementById('filterForm');
    if (!form) return;
    form.querySelectorAll('select').forEach(function (sel) {
      sel.addEventListener('change', function () { form.submit(); });
    });
  }

  /* ── Active category card from URL ────────────────────────── */
  function initActiveCategoryCard() {
    var params  = new URLSearchParams(window.location.search);
    var active  = params.get('category');
    if (!active) return;
    document.querySelectorAll('.category-card').forEach(function (card) {
      var href = card.getAttribute('href') || '';
      if (href.includes('category=' + active)) {
        card.style.borderColor = '#01AA85';
        card.style.background  = 'rgba(1,170,133,.07)';
      }
    });
  }

  /* ── Init ─────────────────────────────────────────────────── */
  document.addEventListener('DOMContentLoaded', function () {
    /* Sliders */
    makeSlider('liveSliderTrack',  'liveSliderPrev',  'liveSliderNext');
    makeSlider('catSliderTrack',   'catSliderPrev',   'catSliderNext');

    /* Timers & counters */
    initCountdowns();
    initHeroCountdown();
    initCounters();

    /* UX helpers */
    initFilterAutoSubmit();
    initActiveCategoryCard();
  });

}());
