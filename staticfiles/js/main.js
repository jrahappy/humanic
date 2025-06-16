import '../css/main.css';
import { sayHello } from './hello.js';
import htmx from 'htmx.org';
window.htmx = htmx;

import Alpine from 'alpinejs'
window.Alpine = Alpine
Alpine.start()

console.log('Hello from main.js');
sayHello('World');