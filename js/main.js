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

  // Review slider arrows + dots. Layout reads (card width, viewport
  // width) are cached and refreshed on resize only: reading clientWidth
  // inside the scroll handler forced a reflow on every scroll frame
  // (Lighthouse flagged ~163 ms of forced reflow here on mobile).
  var slider = document.querySelector(".grw__slider");
  if (slider) {
    var cardW = 320, viewW = 1;
    var measureSlider = function () {
      var c = slider.querySelector(".grw__card");
      cardW = c ? c.getBoundingClientRect().width + 16 : 320;
      viewW = slider.clientWidth || 1;
    };
    measureSlider();
    var step = function (dir) {
      slider.scrollBy({ left: dir * cardW, behavior: "smooth" });
    };
    var prev = document.querySelector(".grw__prev");
    var next = document.querySelector(".grw__next");
    if (prev) prev.addEventListener("click", function () { step(-1); });
    if (next) next.addEventListener("click", function () { step(1); });
    var dots = Array.prototype.slice.call(document.querySelectorAll(".grw__dot"));
    dots.forEach(function (dot) {
      dot.addEventListener("click", function () {
        slider.scrollTo({ left: parseInt(dot.getAttribute("data-page"), 10) * viewW, behavior: "smooth" });
      });
    });
    var ticking = false;
    slider.addEventListener("scroll", function () {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(function () {
        var page = Math.min(dots.length - 1, Math.round(slider.scrollLeft / viewW));
        dots.forEach(function (d, i) {
          d.classList.toggle("is-active", i === page);
        });
        ticking = false;
      });
    }, { passive: true });
    var rzT = false;
    window.addEventListener("resize", function () {
      if (rzT) return;
      rzT = true;
      window.requestAnimationFrame(function () { measureSlider(); rzT = false; });
    }, { passive: true });
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
    // No load-time getBoundingClientRect sweep: the observer fires
    // immediately for elements already in view, and sweeping every .fx
    // element forced a full-page layout during load for no benefit.
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
  // the footer is actually visible AND the browser is idle after load: the
  // plugin costs ~390 KB of JS, and a full-page screenshot pass (or a fast
  // scroll) used to pull it into the load window via the 300px rootMargin.
  // (The Wellness.com badge is a static screenshot: its script only renders
  // on window load, so it cannot be deferred.)
  function deferUntilVisible(selector, activate) {
    var nodes = Array.prototype.slice.call(document.querySelectorAll(selector));
    if (!nodes.length) return;
    var start = function () {
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
      }, { rootMargin: "0px" });
      nodes.forEach(function (n) { io.observe(n); });
    };
    var idle = function () {
      if ("requestIdleCallback" in window) requestIdleCallback(start, { timeout: 4000 });
      else setTimeout(start, 3000);
    };
    if (document.readyState === "complete") idle();
    else window.addEventListener("load", idle);
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
  // rest is pixel-unchanged. The ported formula (live top minus the top at
  // load) simplifies to -scrollY * 0.1, so scroll frames use scrollY math
  // only and force no layout; geometry is measured once (plus on resize)
  // just for the off-screen guard. Inert once the hero has scrolled past,
  // on touch input, or under prefers-reduced-motion — exactly the cases
  // where the old site also dropped the effect.
  var heroImg = document.querySelector(".hero__img");
  if (heroImg) {
    var finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
    var calmMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (finePointer && !calmMotion) {
      var hero = heroImg.closest(".hero");
      var heroTop = 0, heroBottom = 0;
      var measureHero = function () {
        var r = hero.getBoundingClientRect();
        heroTop = r.top + window.scrollY;
        heroBottom = heroTop + r.height;
      };
      measureHero();
      var ticking = false;
      var drift = function () {
        ticking = false;
        if (window.scrollY > heroBottom || heroTop > window.scrollY + window.innerHeight) return;
        var y = window.scrollY * -0.1;
        if (y < -46) y = -46;
        if (y > 0) y = 0;
        heroImg.style.objectPosition = "50% calc(50% + " + y.toFixed(1) + "px)";
      };
      var onScroll = function () {
        if (!ticking) { ticking = true; requestAnimationFrame(drift); }
      };
      window.addEventListener("scroll", onScroll, { passive: true });
      window.addEventListener("resize", function () { measureHero(); onScroll(); }, { passive: true });
      drift();
    }
  }
})();
