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
        /*
        Hide sign-in buttons after the user receives authorization from Google
        */
        $('#signinButton').attr('style', 'display: none');
        $('.fb-login-button').attr('style', 'display: none');

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

            // On success, send the user to the home page
            success: function() {
                window.location.href = '/';
            },

            // In case the request fails
            error: function() {
                console.log('POST request failed.');
                resetSignInButton();
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
If signing in fails for any reason, sign out the Google user (only from the
application) and show the sign-in buttons again after a delay.
*/
function resetSignInButton() {
    setTimeout(function() {
        auth2.signOut().then(function() {
            $('#login-spinner').attr('style', 'display: none');
            $('#signinButton').attr('style', 'display: block');
            $('.fb-login-button').attr('style', 'display: inline-block');
        });
    }, 1000);
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
        // Send the POST request to the server
        logOutPostRequest();
    });
});

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
Completes the login process by sending an access token received from Facebook
to the server as an AJAX POST request. Also sends the state token received
from the server.
*/
function fbSendTokenToServer(response) {
    // Hide sign-in buttons after the user connects with Facebook
    $('#signinButton').attr('style', 'display: none');
    $('.fb-login-button').attr('style', 'display: none');

    // Show the MDL loading spinner
    $('#login-spinner').attr('style', 'display: inline-block');

    // Store the access token received from Facebook
    let accessToken = response.authResponse.accessToken;

    // Send the access token to the server
    $.ajax({
        type: 'POST',

        // Send the request to this route (along with the state token)
        url: `/fbconnect?state=${state}`,

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
            fbResetSignInButtons();
        },
        processData: false,
        data: accessToken
    });
}

/*
If the server returns an error response (login process could not be
completed) show the sign-in buttons again after a delay.
*/
function fbResetSignInButtons() {
    setTimeout(function() {
        $('#login-spinner').attr('style', 'display: none');
        $('#signinButton').attr('style', 'display: block');
        $('.fb-login-button').attr('style', 'display: inline-block');
    }, 1000);
}

/*
Log out the current Facebook user from the application (may also log the user
out of Facebook). Then send a POST request to the server to fully
log them out of the application (clear the login_session).
*/
$('#fbLogOut').click(function(event) {
    // Prevent the default anchor tag behavior
    event.preventDefault();

    // First get the user's status
    FB.getLoginStatus(function(response) {
        // If the user is connected, call FB.logout()
        if (response.status === 'connected') {
            FB.logout(function () {
                // Then send the POST request to the server
                logOutPostRequest();
            });
        }

        // Otherwise just send the POST request to the server
        else {
            logOutPostRequest();
        }
    });
});

/*
Send a POST request to the server to fully log the user out of the
application. Upon receiving the request, the server will clear the
login_session. The user will then be redirected to the home page.
*/
function logOutPostRequest() {
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
