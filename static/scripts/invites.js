(function(){
    //To-Do: Clean this up
    console.log("Loaded");
    const delete_buttons = document.querySelectorAll('.delete-item');
    const copy_buttons = document.querySelectorAll('.copy-item');

    const create_invite = document.getElementById('create-invite');

    create_invite.addEventListener('click', async () => {
        try {
            const response = await fetch(window.location.origin + "/dash/invites/create", {
                method: "POST",
                // Set the FormData instance as the request body
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    "count": 1
                }),
            });

            let result = await response.json();

            if (result.success) location.reload();
            else {
                notify(result.message);
            }
        } catch (e) {
            notify("Unknown error...");
            console.error(e);
        }
    });

    delete_buttons.forEach(button => {
        button.addEventListener('click', async () => {
            let target_invite = button.dataset.invitename;

            let confirmation = "Are you sure you want to delete this invite?";
            if (confirm(confirmation) == false) {
                return console.log("Deletion cancelled");
            }

            try {
                const response = await fetch(window.location.origin + "/dash/invites/delete", {
                    method: "POST",
                    // Set the FormData instance as the request body
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify([target_invite]),
                });

                let result = await response.json();

                if (result.success === true && result.message && result.message != "") {
                    // Delete parent to avoid page reload
                    let closest_tr = button.parentNode.closest('tr');
                    closest_tr.remove();

                    notify(result.message, 3000)
                }
                else if (result.success === false && result.message && result.message != "") {
                    // To-Do: make them autodisappear
                    notify(result.message, 3000)
                }
                else {
                    notify("An unknown error has occurred...", 3000)
                }
            } catch (e) {
                console.error(e);
            }
        });
    });

    copy_buttons.forEach(button => {
        button.addEventListener('click', async () => {
            let target_link = button.dataset.target;

            try {
                navigator.clipboard.writeText('https://' + target_link).then(() => {
                    notify("Copied link!", 3000);
                }, (e) => {
                    console.log(e);
                    notify("Couldn't copy link.", 3000);
                });

                document.execCommand("copy");
            } catch (e) {
                console.error(e);
                notify("Couldn't copy link.", 3000);
            }
        });
    });
})();