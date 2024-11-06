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

// base model close event
const base_modal = document.getElementById('base_modal');
base_modal.addEventListener('close', () => {
    console.log('Base modal closed');
    base_modal.innerHTML = ""
});