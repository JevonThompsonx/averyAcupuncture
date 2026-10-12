/* Avery Acupuncture — site behaviour: mobile nav, review cards, slider,
   FAQ accordion, scroll-fade entrances. No dependencies. */
(function () {
  "use strict";

  var root = document.documentElement;
  root.classList.add("js");

  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("primary-nav");

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });

    // Escape closes the mobile menu (WCAG 2.1.2 keyboard operability)
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("is-open")) {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.focus();
      }
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

  // FAQ accordion (contact page): first item starts open, one at a time
  document.querySelectorAll(".cp-faq__item").forEach(function (item) {
    var btn = item.querySelector(".cp-faq__q");
    var a = item.querySelector(".cp-faq__a");
    var icon = item.querySelector(".cp-faq__icon");
    if (!btn || !a) return;
    if (item.classList.contains("is-open")) {
      a.style.maxHeight = a.scrollHeight + "px";
    }
    btn.addEventListener("click", function () {
      var wasOpen = item.classList.contains("is-open");
      // close siblings (the live accordion keeps one panel open at a time)
      document.querySelectorAll(".cp-faq__item").forEach(function (other) {
        if (other === item) return;
        other.classList.remove("is-open");
        var oa = other.querySelector(".cp-faq__a");
        var ob = other.querySelector(".cp-faq__q");
        var oi = other.querySelector(".cp-faq__icon");
        if (oa) oa.style.maxHeight = "0px";
        if (ob) ob.setAttribute("aria-expanded", "false");
        if (oi) oi.innerHTML = "+";
      });
      item.classList.toggle("is-open", !wasOpen);
      btn.setAttribute("aria-expanded", !wasOpen ? "true" : "false");
      if (icon) icon.innerHTML = !wasOpen ? "&times;" : "+";
      a.style.maxHeight = !wasOpen ? a.scrollHeight + "px" : "0px";
    });
  });

  // Scroll-fade entrances (live theme: fade + 45px slide over 750ms)
  var fades = Array.prototype.slice.call(document.querySelectorAll(".fx"));
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-in");
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
    fades.forEach(function (el) { io.observe(el); });
    // Anything already in view on load (or if the observer never fires)
    window.addEventListener("load", function () {
      fades.forEach(function (el) {
        var r = el.getBoundingClientRect();
        if (r.top < window.innerHeight && r.bottom > 0) el.classList.add("is-in");
      });
    });
  } else {
    fades.forEach(function (el) { el.classList.add("is-in"); });
  }

  // The Wellness.com badge script injects its own <iframe> with no title
  // attribute (Lighthouse frame-title audit). Label it for screen readers.
  function titleBadgeFrames() {
    var frames = document.querySelectorAll('.wellness-badge iframe[id^="iframe_badge_"]');
    frames.forEach(function (f) {
      if (!f.getAttribute("title")) {
        f.setAttribute("title", "Wellness.com profile badge for Avery Acupuncture");
      }
    });
  }
  var badgeScript = document.getElementById("script_badge_160_200_3245076");
  if (badgeScript) {
    badgeScript.addEventListener("load", titleBadgeFrames);
    badgeScript.addEventListener("error", titleBadgeFrames);
  }
  window.addEventListener("load", function () {
    titleBadgeFrames();
    // the badge script can finish after window load — retry briefly
    setTimeout(titleBadgeFrames, 1500);
    setTimeout(titleBadgeFrames, 4000);
  });

  // Hero photo parallax, ported from the live site's X theme: the hero's
  // background drifted at 0.1x the scroll speed (their background-position
  // formula, rect.top * 0.1). Reproduced with object-position on the same
  // <img> (keeping the LCP-discovery win of the real image) — the cover-fit
  // overflow absorbs the drift, so no edge is ever exposed and the crop at
  // rest is pixel-unchanged. rAF-gated, and completely inert once the hero
  // has scrolled past, on touch input, or under prefers-reduced-motion —
  // exactly the cases where the old site also dropped the effect.
  var heroImg = document.querySelector(".hero__img");
  if (heroImg) {
    var finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
    var calmMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (finePointer && !calmMotion) {
      var hero = heroImg.closest(".hero");
      var restTop = hero.getBoundingClientRect().top + window.scrollY;
      var ticking = false;
      var drift = function () {
        ticking = false;
        var r = hero.getBoundingClientRect();
        if (r.bottom < 0 || r.top > window.innerHeight) return;
        var y = (r.top - restTop) * 0.1;
        if (y < -46) y = -46;
        if (y > 0) y = 0;
        heroImg.style.objectPosition = "50% calc(50% + " + y.toFixed(1) + "px)";
      };
      var onScroll = function () {
        if (!ticking) { ticking = true; requestAnimationFrame(drift); }
      };
      window.addEventListener("scroll", onScroll, { passive: true });
      window.addEventListener("resize", onScroll, { passive: true });
      drift();
    }
  }
})();
