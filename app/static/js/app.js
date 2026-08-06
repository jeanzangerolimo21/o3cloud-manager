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
