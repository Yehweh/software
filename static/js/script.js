/**
 * Technical Debt Intelligence - Front-End Interactions
 */

document.addEventListener("DOMContentLoaded", () => {
    // ---------------------------------------------------------
    // 1. File Upload Name Preview
    // ---------------------------------------------------------
    const projectInput = document.getElementById("project_file");
    const selectedFile = document.getElementById("selected-file");

    if (projectInput && selectedFile) {
        projectInput.addEventListener("change", function () {
            if (this.files && this.files.length > 0) {
                selectedFile.textContent = this.files[0].name;
            } else {
                selectedFile.textContent = "No file selected";
            }
        });
    }

    // ---------------------------------------------------------
    // 2. Project File Search (File-Level Debt Assessment Table)
    // ---------------------------------------------------------
    const fileSearchInput = document.getElementById("fileSearchInput");
    const fileResultsTable = document.getElementById("fileResultsTable");

    if (fileSearchInput && fileResultsTable) {
        fileSearchInput.addEventListener("input", function () {
            const searchValue = this.value.toLowerCase().trim();
            const rows = fileResultsTable.querySelectorAll("tbody tr");

            rows.forEach((row) => {
                const rowText = row.textContent.toLowerCase();
                row.style.display = rowText.includes(searchValue) ? "" : "none";
            });
        });
    }

    // ---------------------------------------------------------
    // 3. Dataset Module Search (Baseline Risk Register Table)
    // ---------------------------------------------------------
    const searchInput = document.getElementById("search");
    if (searchInput) {
        searchInput.addEventListener("input", searchTable);
    }

    // ---------------------------------------------------------
    // 4. Password Confirmation Check (Signup Page)
    // ---------------------------------------------------------
    const signupForm = document.querySelector("form.auth-form[action*='signup']");
    const passwordInput = document.getElementById("password");
    const confirmPasswordInput = document.getElementById("confirm_password");

    if (signupForm && passwordInput && confirmPasswordInput) {
        signupForm.addEventListener("submit", function (e) {
            if (passwordInput.value !== confirmPasswordInput.value) {
                e.preventDefault();
                alert("Passwords do not match. Please verify and try again.");
                confirmPasswordInput.focus();
            }
        });
    }

    // ---------------------------------------------------------
    // 5. Flash Message Auto-Dismissal & Close Click
    // ---------------------------------------------------------
    const flashMessages = document.querySelectorAll(".auth-message");
    flashMessages.forEach((msg) => {
        msg.style.cursor = "pointer";
        msg.title = "Click to dismiss";
        msg.addEventListener("click", () => {
            msg.style.transition = "opacity 0.3s, transform 0.3s";
            msg.style.opacity = "0";
            msg.style.transform = "translateY(-10px)";
            setTimeout(() => msg.remove(), 300);
        });

        // Automatically fade out after 6 seconds
        setTimeout(() => {
            if (document.body.contains(msg)) {
                msg.style.transition = "opacity 0.5s, transform 0.5s";
                msg.style.opacity = "0";
                msg.style.transform = "translateY(-10px)";
                setTimeout(() => msg.remove(), 500);
            }
        }, 6000);
    });

    // ---------------------------------------------------------
    // 6. Navigation Tabs (Dashboard / About Metrics / Benchmark)
    // ---------------------------------------------------------
    const navTabs = document.querySelectorAll(".nav-tab");
    navTabs.forEach((tab) => {
        tab.addEventListener("click", function (e) {
            e.preventDefault();
            const tabKey = this.getAttribute("data-tab");
            if (tabKey) {
                switchDashboardTab(tabKey);
            }
        });
    });

    // Initialize active tab from URL hash on load
    const initialHash = window.location.hash.replace("#", "").trim();
    if (["about-metrics", "benchmark", "compare"].includes(initialHash)) {
        switchDashboardTab(initialHash, false);
    } else {
        switchDashboardTab("dashboard", false);
    }

    // Support browser Back/Forward buttons
    window.addEventListener("hashchange", () => {
        const hash = window.location.hash.replace("#", "").trim();
        if (["about-metrics", "benchmark", "compare"].includes(hash)) {
            switchDashboardTab(hash, false);
        } else {
            switchDashboardTab("dashboard", false);
        }
    });

    // ---------------------------------------------------------
    // 7. Compare File Inputs filename preview
    // ---------------------------------------------------------
    const inputA = document.getElementById("file_a");
    const labelA = document.getElementById("label_file_a");
    if (inputA && labelA) {
        inputA.addEventListener("change", function () {
            if (this.files && this.files.length > 0) {
                labelA.textContent = this.files[0].name;
            } else {
                labelA.textContent = "Choose File or ZIP A";
            }
        });
    }

    const inputB = document.getElementById("file_b");
    const labelB = document.getElementById("label_file_b");
    if (inputB && labelB) {
        inputB.addEventListener("change", function () {
            if (this.files && this.files.length > 0) {
                labelB.textContent = this.files[0].name;
            } else {
                labelB.textContent = "Choose File or ZIP B";
            }
        });
    }
});

/**
 * Switches the active view pane between Dashboard, About Metrics, Baseline Benchmark, and Compare.
 */
function switchDashboardTab(targetTab, updateHistory = true) {
    const validTabs = ["dashboard", "about-metrics", "benchmark", "compare"];
    if (!validTabs.includes(targetTab)) {
        targetTab = "dashboard";
    }

    // 1. Update Navigation Tabs Active State
    const navTabs = document.querySelectorAll(".nav-tab");
    navTabs.forEach((tab) => {
        const tabKey = tab.getAttribute("data-tab");
        const isActive = tabKey === targetTab;
        tab.classList.toggle("active", isActive);
        tab.setAttribute("aria-selected", isActive ? "true" : "false");
    });

    // 2. Toggle View Panes
    const viewDashboard = document.getElementById("view-dashboard");
    const viewAbout = document.getElementById("view-about-metrics");
    const viewBenchmark = document.getElementById("view-benchmark");
    const viewCompare = document.getElementById("view-compare");

    if (viewDashboard) {
        viewDashboard.classList.toggle("active-view", targetTab === "dashboard");
    }
    if (viewAbout) {
        viewAbout.classList.toggle("active-view", targetTab === "about-metrics");
    }
    if (viewBenchmark) {
        viewBenchmark.classList.toggle("active-view", targetTab === "benchmark");
    }
    if (viewCompare) {
        viewCompare.classList.toggle("active-view", targetTab === "compare");
    }

    // 3. Update URL Hash
    if (updateHistory) {
        if (window.history && window.history.pushState) {
            window.history.pushState(null, "", "#" + targetTab);
        } else {
            window.location.hash = targetTab;
        }
    }

    // 4. Scroll smoothly to top of main container
    const container = document.querySelector(".dashboard-container");
    if (container) {
        container.scrollIntoView({ behavior: "smooth", block: "start" });
    }
}

/**
 * Searches the baseline dataset table by Module ID or text.
 */
function searchTable() {
    const searchInput = document.getElementById("search");
    const table = document.getElementById("datasetTable") || document.querySelector("table");

    if (!searchInput || !table) {
        return;
    }

    const query = searchInput.value.trim().toLowerCase();
    const rows = table.querySelectorAll("tbody tr");

    rows.forEach((row) => {
        const moduleId = row.cells[0]?.textContent.trim().toLowerCase() || "";
        const rowText = row.textContent.toLowerCase();
        // Exact match on first column or substring match across row
        const match = !query || moduleId === query || rowText.includes(query);
        row.style.display = match ? "" : "none";
    });
}
