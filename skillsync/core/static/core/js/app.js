(() => {
    const root = document.documentElement;
    const storedTheme = localStorage.getItem("skillsync-theme");

    if (storedTheme) {
        root.dataset.theme = storedTheme;
    }

    document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
        button.addEventListener("click", () => {
            const nextTheme = root.dataset.theme === "dark" ? "light" : "dark";
            root.dataset.theme = nextTheme;
            localStorage.setItem("skillsync-theme", nextTheme);
            const icon = button.querySelector("i");
            if (icon) {
                icon.className = nextTheme === "dark" ? "bi bi-sun" : "bi bi-moon-stars";
            }
        });
    });

    document.querySelectorAll("[data-dismiss-toast]").forEach((button) => {
        button.addEventListener("click", () => {
            button.closest(".app-toast")?.remove();
        });
    });

    window.setTimeout(() => {
        document.querySelectorAll(".app-toast").forEach((toast) => {
            toast.style.opacity = "0";
            toast.style.transform = "translateY(8px)";
            window.setTimeout(() => toast.remove(), 200);
        });
    }, 5000);

    document.querySelectorAll("form[data-loading]").forEach((form) => {
        form.addEventListener("submit", (event) => {
            const submitter = event.submitter || form.querySelector("button[type='submit']");
            if (!submitter) {
                return;
            }
            submitter.disabled = true;
            submitter.dataset.originalText = submitter.innerHTML;
            submitter.innerHTML = "<span class='spinner-border spinner-border-sm me-2'></span>Working";
        });
    });
})();
