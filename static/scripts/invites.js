(function(){
    //To-Do: Clean this up
    console.log("Loaded");
    const notification_area = document.getElementById('notifications');
    const delete_buttons = document.querySelectorAll('.delete-item');

    const create_invite = document.getElementById('create-invite');
    const invite_alias = document.getElementById('invite-alias');
    const create_invite_table = document.getElementById('create-invite-table');
    const approve_invite = document.getElementById('approve-invite');
    const deny_invite = document.getElementById('deny-invite');

    delete_buttons.forEach(button => {
        button.addEventListener('click', async () => {
            let target_invite = button.dataset.invitename;

            let confirmation = "Are you sure you want to delete this invite?";
            if (confirm(confirmation) == false) {
                return console.log("Deletion cancelled");
            }

            try {
                const response = await fetch(window.location.origin + "/dash/invites", {
                    method: "POST",
                    // Set the FormData instance as the request body
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        "delete": target_invite
                    }),
                });

                let result = await response.json();
                console.log(result)

                let new_notif = document.createElement('div');
                new_notif.className = 'notif';

                if (result.success === true && result.message && result.message != "") {
                    // Delete parent to avoid page reload
                    let closest_tr = button.parentNode.closest('tr');
                    closest_tr.remove();

                    new_notif.innerHTML = result.message;
                    notification_area.appendChild(new_notif);
                }
                else if (result.success === false && result.message && result.message != "") {
                    // To-Do: make them autodisappear
                    new_notif.innerHTML = result.message;
                    notification_area.appendChild(new_notif);
                }
                else {
                    new_notif.innerHTML = "An unknown error has occurred.";
                    notification_area.appendChild(new_notif);
                }
            } catch (e) {
                console.error(e);
            }
        });
    });

    create_invite.addEventListener('click', () => {
        if (create_invite_table.style.display  == "none") {
            create_invite_table.style.display = "table";
            invite_alias.focus();
        }
        else {
            create_invite_table.style.display = "none";
        }
    });

    deny_invite.addEventListener('click', () => {
        create_invite_table.style.display = "none";
        invite_alias.value = "";
    });

    approve_invite.addEventListener('click', async () => {
        try {
            const response = await fetch(window.location.origin + "/dash/invites", {
                method: "POST",
                // Set the FormData instance as the request body
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    "create": invite_alias.value
                }),
            });

            let result = await response.json();

            create_invite_table.style.display = "none";
            invite_alias.value = "";

            if (result.success) location.reload();
        } catch (e) {
            console.error(e);
        }
    });
})()