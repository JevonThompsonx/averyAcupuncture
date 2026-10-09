/* Avery Acupuncture — site behaviour: mobile nav, review cards, slider. No dependencies. */
(function () {
  "use strict";

  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("primary-nav");

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });

    // Close the mobile menu after tapping a link (but not a dropdown parent)
    nav.addEventListener("click", function (e) {
      var link = e.target.closest("a");
      if (link && !link.parentElement.classList.contains("has-sub")) {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  // Review cards: expand / collapse the full text
  document.querySelectorAll(".grw__card").forEach(function (card) {
    var btn = card.querySelector(".grw__more");
    var quote = card.querySelector(".grw__text");
    if (!btn || !quote) return;
    // Hide the toggle when the text already fits
    if (quote.scrollHeight <= quote.clientHeight + 4) {
      btn.style.display = "none";
      return;
    }
    btn.addEventListener("click", function () {
      var open = card.classList.toggle("is-open");
      btn.textContent = open ? "show less" : "read more";
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  });

  // Review slider arrows + dots
  var slider = document.querySelector(".grw__slider");
  if (slider) {
    var card = slider.querySelector(".grw__card");
    var stepW = function () {
      var c = slider.querySelector(".grw__card");
      return c ? c.getBoundingClientRect().width + 16 : 320;
    };
    var step = function (dir) {
      slider.scrollBy({ left: dir * stepW(), behavior: "smooth" });
    };
    var prev = document.querySelector(".grw__prev");
    var next = document.querySelector(".grw__next");
    if (prev) prev.addEventListener("click", function () { step(-1); });
    if (next) next.addEventListener("click", function () { step(1); });
    var dots = Array.prototype.slice.call(document.querySelectorAll(".grw__dot"));
    dots.forEach(function (dot) {
      dot.addEventListener("click", function () {
        slider.scrollTo({ left: parseInt(dot.getAttribute("data-page"), 10) * slider.clientWidth, behavior: "smooth" });
      });
    });
    var ticking = false;
    slider.addEventListener("scroll", function () {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(function () {
        var page = Math.min(dots.length - 1, Math.round(slider.scrollLeft / slider.clientWidth));
        dots.forEach(function (d, i) {
          d.classList.toggle("is-active", i === page);
        });
        ticking = false;
      });
    });
  }
})();
