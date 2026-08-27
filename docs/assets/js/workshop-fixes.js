// Reset stuck theme overlays and scope lightbox to workshop diagrams only.

function scopeLightbox() {
  document.querySelectorAll(".figure__inner img, .figure img").forEach((img) => {
    if (img.closest("figure.workshop-diagram")) return;
    img.dataset.nozoom = "";
  });
}

function resetOverlays() {
  document.querySelectorAll(".lightbox.is-open, .site-search.is-open").forEach((el) => {
    el.classList.remove("is-open");
  });

  document.body.style.position = "";
  document.body.style.top = "";
  document.body.style.left = "";
  document.body.style.right = "";
}

// Before theme initLightbox runs on DOMContentLoaded.
scopeLightbox();

function init() {
  resetOverlays();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}

window.addEventListener("pageshow", (event) => {
  if (event.persisted) init();
});
