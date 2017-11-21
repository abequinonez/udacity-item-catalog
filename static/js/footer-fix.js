// Select the mdl-layout div
const mdlLayout = document.getElementsByClassName('mdl-layout')[0];

// Select the main element
const main = document.getElementsByTagName('main')[0];

// Select the footer element
const footer = document.getElementsByTagName('footer')[0];

// Declare a boolean variable for checking the footer's visibility
let isFooterHidden = true;

// Adjust the footer's position (and visibility) based on scroll status
function adjustFooter() {
    /*
    Check if the main element's scrollHeight is greater than clientHeight.
    If so, then the page has a vertical scrollbar. This solution was developed
    with help from the following Stack Overflow post:
    https://stackoverflow.com/a/5038256
    */
    const hasScroll = main.scrollHeight > main.clientHeight;

    /*
    If the page has scroll, append (move) the footer to the main element
    (if it's not already appended to main).
    */
    if (hasScroll) {
        /*
        The following MDN page was used as a resource:
        https://developer.mozilla.org/en-US/docs/Web/API/Node/contains
        */
        if (!main.contains(footer)) {
            main.appendChild(footer);
        }
    }

    /*
    Otherwise append the footer to the mdl-layout div (if it's not already
    appended to the mdl-layout div).
    */
    else {
        if (!mdlLayout.contains(footer) || main.contains(footer)) {
            mdlLayout.appendChild(footer);
        }
    }

    // If the footer is hidden, make it visible
    if (isFooterHidden) {
        /*
        The following MDN page was used as a resource:
        https://developer.mozilla.org/en-US/docs/Web/API/Element/classList
        */
        footer.classList.remove('hidden');
        isFooterHidden = false;
    }
}

/*
Continually check if the footer needs to be readjusted, until the document's
readyState is either interactive or complete. Cancel the interval thereafter.
Developed with help from the following resources:

https://davidwalsh.name/document-readystate
https://developer.mozilla.org/en-US/docs/Web/API/Document/readyState
*/
const interval = setInterval(function() {
    if (document.readyState === 'interactive' || document.readyState === 'complete') {
        clearInterval(interval);
        adjustFooter();
    }
});

// Check for readjustment when the page finishes loading
window.addEventListener('load', function() {
    adjustFooter();
});

// Check for readjustment on resize
window.addEventListener('resize', function() {
    adjustFooter();
});

// Adjust the footer as soon as possible
adjustFooter();
