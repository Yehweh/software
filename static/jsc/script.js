function searchTable() {
    const searchInput = document.getElementById("search");
    const table = document.querySelector("table");

    if (!searchInput || !table) {
        return;
    }

    const query = searchInput.value.trim().toLowerCase();

    table.querySelectorAll("tbody tr").forEach((row) => {
        const moduleId = row.cells[0]?.textContent.trim().toLowerCase() || "";
        // Module IDs are discrete values: searching for 1 should only show module 1.
        row.style.display = !query || moduleId === query ? "" : "none";
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("search");

    if (searchInput) {
        searchInput.addEventListener("input", searchTable);
    }
});
