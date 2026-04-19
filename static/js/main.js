/**
 * RapidVenta – Main JavaScript
 * Countdown timers, bid form enhancements, and UI utilities.
 * No inline JS anywhere in templates – all logic lives here.
 */

"use strict";

/* ── 1. Countdown Timer Engine ──────────────────────────────────────────── */

/**
 * Format seconds into a human-readable string.
 * @param {number} totalSeconds
 * @returns {string}
 */
function formatCountdown(totalSeconds) {
  if (totalSeconds <= 0) return "Ended";

  const days    = Math.floor(totalSeconds / 86400);
  const hours   = Math.floor((totalSeconds % 86400) / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = Math.floor(totalSeconds % 60);

  if (days > 0)  return `${days}d ${hours}h ${minutes}m`;
  if (hours > 0) return `${hours}h ${minutes}m ${seconds}s`;
  return `${minutes}m ${seconds}s`;
}

/**
 * Attach a live countdown to a single element.
 * The element must have a `data-end` attribute with an ISO 8601 datetime.
 * @param {HTMLElement} el   – Container element.
 * @param {HTMLElement} display – Element to update with the countdown string.
 */
function startCountdown(el, display) {
  const endTime = new Date(el.dataset.end).getTime();

  function tick() {
    const remaining = Math.floor((endTime - Date.now()) / 1000);

    if (remaining <= 0) {
      display.textContent = "Ended";
      display.classList.add("countdown--ended");
      return; // stop ticking
    }

    // Urgent styling when < 1 hour remains
    if (remaining < 3600) {
      display.classList.add("countdown--urgent");
    }

    display.textContent = formatCountdown(remaining);
    setTimeout(tick, 1000);
  }

  tick();
}

/**
 * Initialise all countdown timers on the page.
 * Card timers:   [data-end] elements with a .countdown-display child span.
 * Detail timer:  #detailTimer with #timerDisplay child.
 */
function initCountdowns() {
  // ── Listing cards (list page) ──────────────────────────────────────────
  document.querySelectorAll("[data-end]").forEach((el) => {
    // Skip the detail page timer – handled separately below
    if (el.id === "detailTimer") return;

    const display = el.querySelector(".countdown-display");
    if (display) startCountdown(el, display);
  });

  // ── Detail page timer ──────────────────────────────────────────────────
  const detailTimer = document.getElementById("detailTimer");
  const timerDisplay = document.getElementById("timerDisplay");
  if (detailTimer && timerDisplay) {
    startCountdown(detailTimer, timerDisplay);
  }
}

/* ── 2. Bid Form Enhancements ───────────────────────────────────────────── */

/**
 * Enhance the bid input on the detail page:
 * - Auto-populate with minimum required bid on focus
 * - Show a running "your total" preview
 */
function initBidForm() {
  const bidInput = document.getElementById("id_amount");
  const bidHint  = document.querySelector(".rv-bid-hint strong");

  if (!bidInput) return;

  // Parse minimum bid from the hint element's text content
  const hintText = bidHint ? bidHint.textContent : "";
  const minMatch = hintText.match(/[\d,.]+/);
  const minBid   = minMatch ? parseFloat(minMatch[0].replace(/,/g, "")) : 0;

  // Pre-fill on focus if empty
  bidInput.addEventListener("focus", () => {
    if (!bidInput.value && minBid > 0) {
      bidInput.value = minBid.toFixed(2);
    }
  });

  // Validate on blur
  bidInput.addEventListener("blur", () => {
    const val = parseFloat(bidInput.value);
    if (!isNaN(val) && val < minBid && minBid > 0) {
      bidInput.classList.add("is-invalid");
    } else {
      bidInput.classList.remove("is-invalid");
    }
  });

  // Prevent form submit with invalid amount
  const bidForm = bidInput.closest("form");
  if (bidForm) {
    bidForm.addEventListener("submit", (e) => {
      const val = parseFloat(bidInput.value);
      if (isNaN(val) || val <= 0) {
        e.preventDefault();
        bidInput.classList.add("is-invalid");
        bidInput.focus();
      }
    });
  }
}

/* ── 3. Auto-dismiss Alerts ─────────────────────────────────────────────── */

/**
 * Automatically dismiss success/info alerts after a delay.
 */
function initAutoDismissAlerts() {
  const alerts = document.querySelectorAll(".rv-alert--success, .rv-alert--info");

  alerts.forEach((alert) => {
    setTimeout(() => {
      // Bootstrap 5 dismiss API
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });
}

/* ── 4. Filter Form Auto-submit ─────────────────────────────────────────── */

/**
 * Automatically submit the filter form when a select changes.
 */
function initFilterAutoSubmit() {
  const filterForm = document.getElementById("filterForm");
  if (!filterForm) return;

  filterForm.querySelectorAll("select").forEach((select) => {
    select.addEventListener("change", () => filterForm.submit());
  });
}

/* ── 5. Confirm Dangerous Actions ───────────────────────────────────────── */

/**
 * Add a confirmation dialog to any button with data-confirm attribute.
 * Usage: <button data-confirm="Are you sure?">Delete</button>
 */
function initConfirmActions() {
  document.querySelectorAll("[data-confirm]").forEach((el) => {
    el.addEventListener("click", (e) => {
      if (!window.confirm(el.dataset.confirm)) {
        e.preventDefault();
        e.stopPropagation();
      }
    });
  });
}

/* ── 6. Image Preview for File Inputs ───────────────────────────────────── */

/**
 * Show an inline preview when a user selects an image file.
 */
function initImagePreviews() {
  document.querySelectorAll('input[type="file"][accept*="image"]').forEach((input) => {
    input.addEventListener("change", () => {
      const file = input.files[0];
      if (!file) return;

      // Find or create a preview element
      let preview = input.parentElement.querySelector(".rv-img-preview");
      if (!preview) {
        preview = document.createElement("img");
        preview.className = "rv-img-preview mt-2";
        preview.style.cssText =
          "max-height:160px;border-radius:8px;border:1px solid #e2e8f0;display:block;";
        input.parentElement.appendChild(preview);
      }

      const reader = new FileReader();
      reader.onload = (ev) => { preview.src = ev.target.result; };
      reader.readAsDataURL(file);
    });
  });
}

/* ── 7. CSV Upload Feedback ─────────────────────────────────────────────── */

/**
 * Show a loading state when the CSV upload form is submitted.
 */
function initCSVUpload() {
  const uploadForm = document.querySelector('form[enctype="multipart/form-data"]');
  if (!uploadForm) return;

  const fileInput = uploadForm.querySelector('input[type="file"]');
  if (!fileInput) return;

  uploadForm.addEventListener("submit", () => {
    const btn = uploadForm.querySelector('button[type="submit"]');
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing…';
    }
  });
}

/* ── 8. Sticky Bid Panel Shadow on Scroll ───────────────────────────────── */

/**
 * Enhance the sticky bid panel with an elevated shadow when the user scrolls.
 */
function initBidPanelScroll() {
  const panel = document.querySelector(".rv-bid-panel");
  if (!panel) return;

  let lastScroll = 0;
  window.addEventListener(
    "scroll",
    () => {
      const current = window.scrollY;
      if (current > 200) {
        panel.style.boxShadow = "0 20px 60px rgba(14,165,233,.22)";
      } else {
        panel.style.boxShadow = "";
      }
      lastScroll = current;
    },
    { passive: true }
  );
}

/* ── 9. Tooltip Initialisation (Bootstrap 5) ────────────────────────────── */

function initTooltips() {
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach((el) => {
    new bootstrap.Tooltip(el, { trigger: "hover focus" });
  });
}

/* ── 10. Status Badge Urgency Colouring ─────────────────────────────────── */

/**
 * Add a pulsing animation to ACTIVE status pills that are close to expiry.
 * Relies on data-end being present on the listing card.
 */
function initUrgencyBadges() {
  document.querySelectorAll("[data-end]").forEach((el) => {
    const endTime   = new Date(el.dataset.end).getTime();
    const remaining = Math.floor((endTime - Date.now()) / 1000);

    if (remaining > 0 && remaining < 3600) {
      // Less than 1 hour – add urgency class to the card
      const card = el.closest(".rv-card");
      if (card) card.classList.add("rv-card--urgent");
    }
  });
}

/* ── Bootstrap 5 CSS injection for countdown urgency ────────────────────── */
(function injectDynamicStyles() {
  const style = document.createElement("style");
  style.textContent = `
    .countdown--urgent  { color: #dc2626 !important; font-weight: 700; }
    .countdown--ended   { color: #94a3b8 !important; }
    .rv-card--urgent    { border-color: #fca5a5 !important; }
    .rv-card--urgent .rv-card__countdown { color: #dc2626 !important; }
  `;
  document.head.appendChild(style);
})();

/* ── Entry Point ────────────────────────────────────────────────────────── */

document.addEventListener("DOMContentLoaded", () => {
  initCountdowns();
  initBidForm();
  initAutoDismissAlerts();
  initFilterAutoSubmit();
  initConfirmActions();
  initImagePreviews();
  initCSVUpload();
  initBidPanelScroll();
  initTooltips();
  initUrgencyBadges();
});
