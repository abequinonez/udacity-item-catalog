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
$('#g-sign-in-button').click(function() {
    /*
    In case of promise failure, call gSignInFailure(). The following
    MDN page was used as a reference:
    https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/then
    */
    auth2.grantOfflineAccess().then(gSignInCallback, gSignInFailure);
});

/*
Callback function that receives a one-time authorization code from Google
after signing in. Calls a function that sends the authorization code, along
with the state token received from the server, to the server as an AJAX POST
request.
*/
function gSignInCallback(authResult) {
    if (authResult['code']) {
        /*
        Hide sign-in buttons after the user receives authorization from Google
        */
        hideSignInButtons();

        // Send the authorization code to the server
        loginPostRequest(authResult['code'], '/gconnect', 'google');
    } else {
        console.log('Failed to receive an authorization code.')
    }
}

function gSignInFailure(error) {
    console.log('Failed to sign in with Google: ' + error.error);
}

/*
Sign out the current Google user from the application (without the inconvenience
of signing out of Google). Then send a POST request to the server to fully
sign them out of the application (clear the login_session).
*/
function gSignOut() {
    auth2.signOut().then(function () {
        // Send the POST request to the server
        logoutPostRequest();
    });
}
// End of Google Sign-In code

/*
Facebook Login code below. Developed with extensive help from the Facebook
Login docs: https://developers.facebook.com/docs/facebook-login/web
*/
window.fbAsyncInit = function() {
    FB.init({
        appId      : '301685340342326',
        cookie     : true,
        xfbml      : true,
        version    : 'v2.11'
    });
};

(function(d, s, id){
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) {return;}
    js = d.createElement(s); js.id = id;
    js.src = "https://connect.facebook.net/en_US/sdk.js";
    fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));

/*
Callback function called after the user is finished interacting with the
Facebook login dialog window. Calls FB.getLoginStatus() to get the login state
of the user (returned as a response object). If the user successfully logs in
to Facebook and connects to the application, Facebook will send a response
object with a status of 'connected'. A function is then called that sends an
AJAX POST request to the server (to complete the login process).
*/
function fbCheckLoginState() {
    FB.getLoginStatus(function(response) {
        if (response.status === 'connected') {
            fbSendTokenToServer(response);
        }
    });
}

/*
Completes the login process by calling a function that sends an access token
received from Facebook to the server as an AJAX POST request.
*/
function fbSendTokenToServer(response) {
    // Hide sign-in buttons after the user connects with Facebook
    hideSignInButtons();

    // Store the access token received from Facebook
    let accessToken = response.authResponse.accessToken;

    // Send the access token to the server
    loginPostRequest(accessToken, '/fbconnect', 'facebook');
}

/*
Log out the current Facebook user from the application (may also log the user
out of Facebook). Then send a POST request to the server to fully
log them out of the application (clear the login_session).
*/
function fbLogout() {
    // First get the user's status
    FB.getLoginStatus(function(response) {
        // If the user is connected, call FB.logout()
        if (response.status === 'connected') {
            FB.logout(function () {
                // Then send the POST request to the server
                logoutPostRequest();
            });
        }

        // Otherwise just send the POST request to the server
        else {
            logoutPostRequest();
        }
    });
}
// End of Facebook Login code

/*
Completes the login process by sending the necessary code or access token
received from the authentication provider to the server as an AJAX POST
request. Also sends the state token received from the server.
*/
function loginPostRequest(data, route, provider) {
    $.ajax({
        type: 'POST',

        // Send the request to this route (along with the state token)
        url: `${route}?state=${state}`,

        // Include an X-Requested-With header in case of a CSRF attack
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        },
        contentType: 'application/octet-stream; charset=utf-8',

        // On success, send the user to the home page
        success: function() {
            window.location.href = '/';
        },

        // In case the request fails
        error: function() {
            console.log('POST request failed.');
            resetSignInButtons(provider);
        },
        processData: false,
        data: data
    });
}

/*
If there's an error or problem contacting the server (login process could not
be completed), sign the user out of the appropriate provider and show the
sign-in buttons again after a delay.
*/
function resetSignInButtons(provider) {
    setTimeout(function() {
        if (provider === 'google') {
            auth2.signOut().then(function() {
                showSignInButtons();
            });
        } else if (provider === 'facebook') {
            FB.logout(function () {
                showSignInButtons();
            });
        }
    }, 1000);
}

// Hide the sign-in buttons and show the MDL loading spinner
function hideSignInButtons() {
    $('#g-sign-in-button').attr('style', 'display: none');
    $('.fb-login-button').attr('style', 'display: none');
    $('#login-spinner').attr('style', 'display: inline-block');
}

// Show the sign-in buttons and hide the MDL loading spinner
function showSignInButtons() {
    $('#login-spinner').attr('style', 'display: none');
    $('#g-sign-in-button').attr('style', 'display: block');
    $('.fb-login-button').attr('style', 'display: inline-block');
}

// Click handler that calls provider-specific logout function
$('.logout-link').click(function(event) {
    // Prevent the default anchor tag behavior
    event.preventDefault();

    if (authProvider === 'google') {
        gSignOut();
    } else if (authProvider === 'facebook') {
        fbLogout();
    }
});

/*
Send a POST request to the server to fully log the user out of the
application. Upon receiving the request, the server will clear the
login_session. The user will then be redirected to the home page.
*/
function logoutPostRequest() {
    $.ajax({
        type: 'POST',
        url: '/logout',
        success: function() {
            // On success, send the user to the home page
            window.location.href = '/';
        },
        error: function(jqXHR, status, error) {
            console.log('Error logging out: ' + error);
        }
    });
}
