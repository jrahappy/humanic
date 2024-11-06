document.addEventListener("DOMContentLoaded", function() {
    const collapsibleSections = document.querySelectorAll("details");

    // Load saved state from localStorage
    collapsibleSections.forEach(section => {
        const sectionId = section.id;
        if (localStorage.getItem(sectionId) === "open") {
            section.open = true;
        }

        // Add event listener to save state when toggled
        section.addEventListener("toggle", function() {
            localStorage.setItem(sectionId, section.open ? "open" : "closed");
        });
    });
});