// Select the form (only one at most per page)
const form = document.getElementsByTagName('form')[0];

// Select the category input
const categoryInput = document.getElementById('category');

// Select the hidden (category-id) input
const hiddenInput = document.getElementById('category-id');

// Only run the code (add an event listener) if a form and hidden input exist
if (form && hiddenInput) {
    /*
    When the form is submitted, assign the value of the category input data-val
    attribute to the value of the hidden input element. As a result, the
    server will receive the category ID, rather than the category name. The
    following sources were helpful in developing this solution:
    
    https://stackoverflow.com/a/9441035
    https://developer.mozilla.org/en-US/docs/Web/API/Element/getAttribute
    */
    form.addEventListener('submit', function() {
        hiddenInput.value = categoryInput.getAttribute('data-val');
    });
}
