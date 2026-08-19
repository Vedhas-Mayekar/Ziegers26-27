/* ============================================================
   ZIEGERS 2026-27 | Preloader Controller
   Sequence: ZIEGERS logo reveals + glows (≈2s) → fade out
   ============================================================ */

(function () {
    'use strict';

    var PRELOADER_DELAY = 2000; // total visible time (ms) before fade out
    var FADE_MS = 650;          // must match the CSS #preloader transition

    function hidePreloader() {
        var preloader = document.getElementById('preloader');
        if (!preloader) return;

        var unlock = function () {
            document.documentElement.classList.remove('preload-lock');
            // Fully detach so it never sits in the DOM / blocks anything
            if (preloader.parentNode) {
                preloader.parentNode.removeChild(preloader);
            }
        };

        preloader.classList.add('preloader-done');
        window.setTimeout(unlock, FADE_MS + 50);
    }

    // Lock scrolling for the whole sequence, then release.
    document.documentElement.classList.add('preload-lock');

    // End the sequence after the logo reveal + hold.
    window.setTimeout(hidePreloader, PRELOADER_DELAY);
})();