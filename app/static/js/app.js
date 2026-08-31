(function () {
    const key = "o3cloud.darkMode";

    function applyDarkMode(enabled) {
        document.body.classList.toggle("dark-mode", enabled);
        document.querySelectorAll("#darkModeSwitch").forEach(function (input) {
            input.checked = enabled;
        });
    }

    function darkModeEnabled() {
        return localStorage.getItem(key) === "1";
    }

    applyDarkMode(darkModeEnabled());

    document.addEventListener("click", function (event) {
        const button = event.target.closest("#darkModeToggle");
        if (!button) {
            return;
        }
        event.preventDefault();
        event.stopPropagation();
        const enabled = !darkModeEnabled();
        localStorage.setItem(key, enabled ? "1" : "0");
        applyDarkMode(enabled);
    });
})();
(function () {
    if (window.bootstrap && window.bootstrap.Dropdown) {
        return;
    }
    document.addEventListener("click", function (event) {
        const toggle = event.target.closest(".user-menu-toggle");
        const menu = document.querySelector(".user-dropdown");
        if (!menu) {
            return;
        }
        if (toggle) {
            event.preventDefault();
            menu.classList.toggle("show");
            toggle.setAttribute("aria-expanded", menu.classList.contains("show") ? "true" : "false");
            return;
        }
        if (!event.target.closest(".user-dropdown")) {
            menu.classList.remove("show");
            const openToggle = document.querySelector(".user-menu-toggle");
            if (openToggle) {
                openToggle.setAttribute("aria-expanded", "false");
            }
        }
    });
})();

(function () {
    const storageKey = "o3cloud.sidebarScrollTop";

    function getSidebarMenu() {
        return document.querySelector(".sidebar-menu");
    }

    function saveScrollPosition() {
        const menu = getSidebarMenu();
        if (!menu) {
            return;
        }

        try {
            sessionStorage.setItem(storageKey, String(menu.scrollTop));
        } catch (error) {
            // A navegacao continua funcionando mesmo se o armazenamento estiver indisponivel.
        }
    }

    function restoreScrollPosition() {
        const menu = getSidebarMenu();
        if (!menu) {
            return;
        }

        try {
            const savedPosition = sessionStorage.getItem(storageKey);
            if (savedPosition !== null) {
                menu.scrollTop = Number(savedPosition) || 0;
            }
        } catch (error) {
            // A posicao inicial permanece como fallback.
        }
    }

    restoreScrollPosition();

    const menu = getSidebarMenu();
    if (menu) {
        menu.addEventListener("scroll", saveScrollPosition, { passive: true });
    }

    document.addEventListener("click", function (event) {
        if (event.target.closest(".sidebar-menu a, .global-back-button, [data-smart-back]")) {
            saveScrollPosition();
        }
    }, true);

    window.addEventListener("pagehide", saveScrollPosition);
})();

(function () {
    const prefix = "o3cloud.pageScrollTop:";

    function storageKey() {
        return prefix + window.location.pathname + window.location.search;
    }

    function savePageScrollPosition() {
        try {
            sessionStorage.setItem(storageKey(), String(window.scrollY || document.documentElement.scrollTop || 0));
        } catch (error) {
            // A navegacao segue normalmente mesmo sem armazenamento local.
        }
    }

    function restorePageScrollPosition() {
        if (window.location.hash) {
            return;
        }
        try {
            const savedPosition = sessionStorage.getItem(storageKey());
            if (savedPosition === null) {
                return;
            }
            const top = Number(savedPosition) || 0;
            if (top > 0) {
                window.scrollTo({ top: top, left: 0, behavior: "auto" });
            }
        } catch (error) {
            // A tela permanece no topo como fallback.
        }
    }

    if ("scrollRestoration" in window.history) {
        window.history.scrollRestoration = "manual";
    }

    window.addEventListener("load", restorePageScrollPosition);
    window.addEventListener("pagehide", savePageScrollPosition);
    document.addEventListener("submit", savePageScrollPosition, true);
    document.addEventListener("click", function (event) {
        if (event.target.closest("a[href], button[type='submit'], input[type='submit']")) {
            savePageScrollPosition();
        }
    }, true);
    document.addEventListener("change", function (event) {
        const field = event.target.closest("select, input[type='checkbox'], input[type='radio']");
        if (field && field.form) {
            savePageScrollPosition();
        }
    }, true);
})();


(function () {
    const globalKey = "o3cloud.lastReturnUrl";
    const scopedPrefix = "o3cloud.lastReturnUrl:";
    const fallbackUrl = "/";
    const transientSegments = new Set(["novo", "editar", "importar"]);

    function currentUrl() {
        return window.location.pathname + window.location.search;
    }

    function isSafeInternalUrl(url) {
        return typeof url === "string" && url.charAt(0) === "/" && url.substring(0, 2) !== "//";
    }

    function isNumericSegment(value) {
        return /^\d+$/.test(value || "");
    }

    function pathSegments(path) {
        return String(path || "").split("/").filter(Boolean);
    }

    function isTransientPath(path) {
        const segments = pathSegments(path);
        if (!segments.length) {
            return false;
        }
        if (isNumericSegment(segments[segments.length - 1])) {
            return true;
        }
        return segments.some(function (segment) {
            return transientSegments.has(segment);
        });
    }

    function scopeFromPath(path) {
        const segments = pathSegments(path);
        if (!segments.length) {
            return fallbackUrl;
        }
        if (segments[0] === "implantacao" && segments[1] === "cofre-senhas") {
            return "/implantacao/cofre-senhas";
        }
        if (segments[1] && !isNumericSegment(segments[1]) && !transientSegments.has(segments[1])) {
            return "/" + segments[0] + "/" + segments[1];
        }
        return "/" + segments[0];
    }

    function readStoredReturnUrl(scope, fallback) {
        try {
            const scoped = sessionStorage.getItem(scopedPrefix + scope);
            if (isSafeInternalUrl(scoped) && scoped !== currentUrl()) {
                return scoped;
            }
            const global = sessionStorage.getItem(globalKey);
            if (isSafeInternalUrl(global) && global !== currentUrl()) {
                return global;
            }
        } catch (error) {
            // Keep the normal link fallback when sessionStorage is unavailable.
        }
        return isSafeInternalUrl(fallback) ? fallback : fallbackUrl;
    }

    function rememberCurrentPage() {
        const path = window.location.pathname;
        if (path === fallbackUrl || isTransientPath(path)) {
            return;
        }
        const url = currentUrl();
        const scope = scopeFromPath(path);
        try {
            sessionStorage.setItem(globalKey, url);
            sessionStorage.setItem(scopedPrefix + scope, url);
        } catch (error) {
            // Navigation remains available through link hrefs.
        }
    }

    rememberCurrentPage();

    document.addEventListener("click", function (event) {
        const button = event.target.closest("[data-smart-back]");
        if (!button) {
            return;
        }
        const target = readStoredReturnUrl(scopeFromPath(window.location.pathname), button.getAttribute("href"));
        if (!isSafeInternalUrl(target)) {
            return;
        }
        event.preventDefault();
        window.location.assign(target);
    });
})();
