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
        if (event.target.closest(".sidebar-menu a, .global-back-button, a[onclick*=\"history.back\"]")) {
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
