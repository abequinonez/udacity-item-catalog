// Show the message sent by the server as an MDL toast
function showToastMessage() {
    let messageToast = document.querySelector('#message-toast');
    let data = {message: flashMessage};
    messageToast.MaterialSnackbar.showSnackbar(data);
}

/*
If the flashMessage variable contains a value other than null, the
showToastMessage() function will be called to show the message sent
by the server (after the document has finished loading).
*/
if (flashMessage) {
    // Call showToastMessage() when the document is ready
    const toastInterval = setInterval(function() {
        if (document.readyState === 'complete') {
            clearInterval(toastInterval);
            showToastMessage();
        }
    });
}
