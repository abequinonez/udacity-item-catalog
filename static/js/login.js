/*
Google Sign-In code below. Developed with extensive help from the Google
Sign-In docs: https://developers.google.com/identity/sign-in/web
*/
let auth2;
gapi.load('auth2', function() {
    auth2 = gapi.auth2.init();
});

/*
Add a click listener to the Google Sign-In button. If signing in with Google
is successful, a callback function is called that sends an AJAX POST request
to the server.
*/
$('#signinButton').click(function() {
    /*
    In case of promise failure, call signInFailure(). The following
    MDN page was used as a reference:
    https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/then
    */
    auth2.grantOfflineAccess().then(signInCallback, signInFailure);
});

/*
Callback function that receives a one-time authorization code from Google
after signing in. Sends the authorization code, along with the state token
received from the server, to the server as an AJAX POST request.
*/
function signInCallback(authResult) {
    if (authResult['code']) {
        // Hide the sign-in button after the user receives authorization
        $('#signinButton').attr('style', 'display: none');

        // Show the MDL loading spinner
        $('#login-spinner').attr('style', 'display: inline-block');

        // Send the authorization code to the server
        $.ajax({
            type: 'POST',

            // Send the request to this route (along with the state token)
            url: `/gconnect?state=${state}`,

            // Include an X-Requested-With header in case of a CSRF attack
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            contentType: 'application/octet-stream; charset=utf-8',
            success: function(result) {
                if (result) {
                    // On success, send the user to the home page
                    window.location.href = '/';
                } else if (authResult['error']) {
                    console.log('An error occurred: ' + authResult['error']);
                } else {
                    console.log('Failed to log in.');
                }
            },
            error: function() {
                // In case the request fails
                console.log('POST request failed.');
            },
            processData: false,
            data: authResult['code']
        });
    } else {
        console.log('Failed to receive an authorization code.')
    }
}

function signInFailure(error) {
    console.log('Failed to sign in with Google: ' + error.error);
}

/*
Sign out the current Google user from the application (without the inconvenience
of signing out of Google). Then send a POST request to the server to fully
sign them out of the application (clear the login_session).
*/
$('#signOut').click(function(event) {
    // Prevent the default anchor tag behavior
    event.preventDefault();
    let auth2 = gapi.auth2.getAuthInstance();
    auth2.signOut().then(function () {
        $.ajax({
            type: 'POST',
            url: '/logout',
            success: function() {
                // On success, send the user to the home page
                window.location.href = '/';
            },
            error: function(jqXHR, status, error) {
                console.log('Error signing out: ' + error);
            }
        });
    });
});
