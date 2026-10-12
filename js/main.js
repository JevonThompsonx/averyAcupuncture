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

  // Click-to-load embed facades (YouTube players, Google Maps). The heavy
  // third-party player is fetched only when the visitor asks for it; the
  // preview is the video's YouTube thumbnail or a screenshot of the live
  // embed. On click the facade is swapped for the real iframe, matching the
  // markup the page had before the Lighthouse performance pass.
  document.addEventListener("click", function (e) {
    var btn = e.target.closest ? e.target.closest(".embed-facade__btn") : null;
    if (!btn) return;
    var box = btn.closest(".embed-facade");
    if (!box) return;
    var f = document.createElement("iframe");
    f.src = box.getAttribute("data-src");
    f.title = box.getAttribute("data-title") || "";
    var allow = box.getAttribute("data-allow");
    if (allow) f.setAttribute("allow", allow);
    f.setAttribute("allowfullscreen", "");
    f.setAttribute("frameborder", "0");
    box.replaceWith(f);
  });

  // Defer below-the-fold third-party embeds (Facebook page plugin) until
  // the footer actually scrolls into view: it costs ~390 KB of JS and an
  // autoplaying video, but nothing is lost — it appears the moment the
  // footer is on screen. (The Wellness.com badge is a static screenshot:
  // its script only renders on window load, so it cannot be deferred.)
  function deferUntilVisible(selector, activate) {
    var nodes = Array.prototype.slice.call(document.querySelectorAll(selector));
    if (!nodes.length) return;
    if (!("IntersectionObserver" in window)) {
      nodes.forEach(activate);
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        io.unobserve(entry.target);
        activate(entry.target);
      });
    }, { rootMargin: "300px" });
    nodes.forEach(function (n) { io.observe(n); });
  }
  deferUntilVisible(".fb-slot", function (slot) {
    var f = document.createElement("iframe");
    f.src = slot.getAttribute("data-src");
    f.title = slot.getAttribute("data-title") || "";
    f.width = 275;
    f.height = 370;
    f.setAttribute("style", "border:none;overflow:hidden");
    f.setAttribute("scrolling", "no");
    f.setAttribute("frameborder", "0");
    f.setAttribute("allowtransparency", "true");
    f.setAttribute("loading", "lazy");
    slot.replaceWith(f);
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
