(function () {
    "use strict";

    /* ---------------------------------------------------------------------
     * Theme toggle
     * ------------------------------------------------------------------- */
    var themeToggle = document.querySelector("[data-theme-toggle]");
    if (themeToggle) {
        themeToggle.addEventListener("click", function () {
            var current = document.documentElement.getAttribute("data-theme") || "dark";
            var next = current === "dark" ? "light" : "dark";
            document.documentElement.setAttribute("data-theme", next);
            try {
                localStorage.setItem("theme", next);
            } catch (e) {
                /* localStorage unavailable — theme just won't persist */
            }
            themeToggle.setAttribute(
                "aria-label",
                next === "dark" ? "Switch to light theme" : "Switch to dark theme"
            );
        });
    }

    /* ---------------------------------------------------------------------
     * Mobile navigation
     * ------------------------------------------------------------------- */
    var navToggle = document.querySelector("[data-nav-toggle]");
    var mobileNav = document.querySelector("[data-mobile-nav]");
    if (navToggle && mobileNav) {
        var closeMobileNav = function () {
            navToggle.setAttribute("aria-expanded", "false");
            mobileNav.classList.remove("is-open");
        };
        navToggle.addEventListener("click", function () {
            var isOpen = mobileNav.classList.toggle("is-open");
            navToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
        });
        mobileNav.querySelectorAll("[data-nav-close]").forEach(function (link) {
            link.addEventListener("click", closeMobileNav);
        });
        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape") closeMobileNav();
        });
    }

    /* ---------------------------------------------------------------------
     * Sticky header shadow once the page has scrolled
     * ------------------------------------------------------------------- */
    var header = document.querySelector("[data-site-header]");
    if (header) {
        var updateHeaderState = function () {
            header.classList.toggle("is-scrolled", window.scrollY > 4);
        };
        updateHeaderState();
        window.addEventListener("scroll", updateHeaderState, { passive: true });
    }

    /* ---------------------------------------------------------------------
     * Reveal-on-scroll + stat count-up
     * ------------------------------------------------------------------- */
    var revealTargets = document.querySelectorAll("[data-reveal]");
    var animateCounter = function (el) {
        var target = parseFloat(el.dataset.countTo);
        if (isNaN(target)) return;
        var duration = 1200;
        var start = null;
        var from = 0;
        var step = function (timestamp) {
            if (start === null) start = timestamp;
            var progress = Math.min((timestamp - start) / duration, 1);
            var eased = 1 - Math.pow(1 - progress, 3);
            var value = Math.round(from + (target - from) * eased);
            el.textContent = value;
            if (progress < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
    };

    if ("IntersectionObserver" in window && revealTargets.length) {
        var revealObserver = new IntersectionObserver(
            function (entries, observer) {
                entries.forEach(function (entry) {
                    if (!entry.isIntersecting) return;
                    entry.target.classList.add("is-visible");
                    if (entry.target.hasAttribute("data-count-up")) {
                        entry.target.querySelectorAll("[data-count-to]").forEach(animateCounter);
                    }
                    observer.unobserve(entry.target);
                });
            },
            { threshold: 0.15, rootMargin: "0px 0px -60px 0px" }
        );
        revealTargets.forEach(function (el) {
            revealObserver.observe(el);
        });
    } else {
        revealTargets.forEach(function (el) {
            el.classList.add("is-visible");
        });
    }

    /* ---------------------------------------------------------------------
     * On-page navigation scroll-spy
     * ------------------------------------------------------------------- */
    var pageNavLinks = document.querySelectorAll("[data-page-nav] a[href^='#']");
    if ("IntersectionObserver" in window && pageNavLinks.length) {
        var sections = [];
        pageNavLinks.forEach(function (link) {
            var section = document.getElementById(link.getAttribute("href").slice(1));
            if (section) sections.push({ link: link, section: section });
        });

        var setActive = function (link) {
            pageNavLinks.forEach(function (l) {
                l.classList.toggle("is-active", l === link);
            });
        };

        var spyObserver = new IntersectionObserver(
            function (entries) {
                entries.forEach(function (entry) {
                    if (!entry.isIntersecting) return;
                    var match = sections.find(function (s) {
                        return s.section === entry.target;
                    });
                    if (match) setActive(match.link);
                });
            },
            { rootMargin: "-45% 0px -50% 0px", threshold: 0 }
        );
        sections.forEach(function (s) {
            spyObserver.observe(s.section);
        });
    }

    /* ---------------------------------------------------------------------
     * Copy-to-clipboard for code blocks
     * ------------------------------------------------------------------- */
    document.querySelectorAll("[data-copy-code]").forEach(function (button) {
        button.addEventListener("click", function () {
            var codeEl = button.closest(".code-block").querySelector("code");
            if (!codeEl || !navigator.clipboard) return;
            navigator.clipboard.writeText(codeEl.textContent).then(function () {
                var original = button.textContent;
                button.textContent = "Copied!";
                setTimeout(function () {
                    button.textContent = original;
                }, 1500);
            });
        });
    });
})();
