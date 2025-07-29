import '../css/main.css';
import htmx from 'htmx.org';
window.htmx = htmx;

import Alpine from 'alpinejs'
window.Alpine = Alpine
Alpine.start()

import { sayHello } from './hello.js';
console.log('Hello from main.js');
sayHello('World');


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