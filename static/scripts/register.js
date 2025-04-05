(function(){
    console.log("Register script loaded");

    const invite_input = document.getElementById("invite");

    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const invite_code = urlParams.get('invite');

    if (invite_code != "") {
        invite_input.value = invite_code;
    }
})();