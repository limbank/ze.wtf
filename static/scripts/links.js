(function(){
    console.log("Link script loaded");

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
            create_link_alias.focus();
        }
        else {
            create_link_table.style.display = "none";
        }
    });

    create_link_cancel.addEventListener('click', reset_create);

    create_link_confirm.addEventListener("click", async (event) => {
        let alias = create_link_alias.value;
        let url = create_link_url.value;

        if (url == "") return;

        try {
            const response = await fetch(window.location.origin + "/dash/links/create", {
                method: "POST",
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify([
                    {
                        "url": url,
                        "alias": alias
                    }
                ]),
            });

            let result = await response.json();

            if (result.success === false) {
                notify(result.message || "Unknown error...");
                return console.log(result);
            }

            // Instead of reloading, just append the newly created tr

            reset_create();
            location.reload();
        } catch (e) {
            notify("Error attempting to create link...");
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
                const response = await fetch(window.location.origin + "/dash/links/delete", {
                    method: "POST",
                    // Set the FormData instance as the request body
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify([target_url]),
                });

                let result = await response.json();

                if (result.success === true && result.message && result.message != "") {
                    // Delete parent to avoid page reload
                    let closest_tr = button.parentNode.closest('tr');
                    closest_tr.remove();

                    notify(result.message);
                }
                else if (result.success === false && result.message && result.message != "") {
                    notify(result.message);
                }
                else {
                    notify("An unknown error has occurred.");
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
})()