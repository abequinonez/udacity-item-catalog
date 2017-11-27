/*
Google Sign-In code below. Developed with extensive help from the Google
Sign-In docs: https://developers.google.com/identity/sign-in/web
*/
let auth2;
gapi.load('auth2', function() {
    auth2 = gapi.auth2.init();
});

$('#signinButton').click(function() {
    /*
    In case of promise failure, call signInFailure(). The following
    MDN page was used as a reference:
    https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/then
    */
    auth2.grantOfflineAccess().then(signInCallback, signInFailure);
});

function signInCallback(authResult) {
    console.log(authResult);
}

function signInFailure(error) {
    console.log('Failed to sign in with Google: ' + error.error);
}
