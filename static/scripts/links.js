(function(){
    //To-Do: Clean this up
    console.log("Loaded");
    const notification_area = document.getElementById('notifications');
    const delete_buttons = document.querySelectorAll('.delete-item');
    const copy_buttons = document.querySelectorAll('.copy-item');

    const create_link_toggle = document.getElementById("create-link-toggle");
    const create_link_table = document.getElementById("create-link-table");
    const create_link_alias = document.getElementById("create-link-alias");
    const create_link_url = document.getElementById("create-link-url");
    const create_link_confirm = document.getElementById("create-link-confirm");
    const create_link_cancel = document.getElementById("create-link-cancel");

    function reset_create() {
        create_link_table.style.display = "none";
        create_link_alias.value = "";
        create_link_url.value = "";
    }

    create_link_toggle.addEventListener('click', async () => {
        if (create_link_table.style.display  == "none") {
            create_link_table.style.display = "table";
        }
        else {
            create_link_table.style.display = "none";
        }
    });

    create_link_cancel.addEventListener('click', reset_create);

    create_link_confirm.addEventListener("click", async (event) => {
        // To-Do: add input validation
        let alias = create_link_alias.value;
        let url = create_link_url.value;

        if (url == "") return;

        const formData = new FormData();

        formData.append("alias", alias);
        formData.append("url", url);

        try {
            const response = await fetch(window.location.origin + "/dash/links", {
                method: "POST",
                body: formData,
            });

            let result = await response.json();

            if (result.success === false) {
                console.log(result);
                return console.log("Error attempting to upload...");
            }

            reset_create();
            location.reload();
        } catch (e) {
            console.error(e);
        }
    });

    delete_buttons.forEach(button => {
        button.addEventListener('click', async () => {
            let target_url = button.dataset.urlname;

            let confirmation = "Are you sure you want to delete this link?";
            if (confirm(confirmation) == false) {
                return console.log("Deletion cancelled");
            }

            try {
                const response = await fetch(window.location.origin + "/dash/links", {
                    method: "POST",
                    // Set the FormData instance as the request body
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        "delete": target_url
                    }),
                });

                let result = await response.json();

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

    copy_buttons.forEach(button => {
        button.addEventListener('click', async () => {
            let target_file = button.dataset.target;

            try {
                navigator.clipboard.writeText('https://' + target_file).then(() => {
                    console.log("Copied link");
                }, (e) => {
                    console.log(e);
                    console.log("Couldn't copy link");
                });
                document.execCommand("copy");
            } catch (e) {
                console.error(e);
                console.log("Couldn't copy link");
            }
        });
    });
})()