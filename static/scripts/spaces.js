(function(){
    //To-Do: Clean this up
    console.log("Spaces script loaded");

    const delete_buttons = document.querySelectorAll('.delete-item');
    const copy_buttons = document.querySelectorAll('.copy-item');

    const create_space_toggle = document.getElementById("create-space-toggle");
    const create_space_table = document.getElementById("create-space-table");
    const create_space_name = document.getElementById("create-space-name");
    const create_space_confirm = document.getElementById("create-space-confirm");
    const create_space_cancel = document.getElementById("create-space-cancel");

    function reset_create() {
        create_space_table.style.display = "none";
        create_space_name.value = "";
    }

    create_space_toggle.addEventListener("click", (event) => {
        if (create_space_table.style.display  == "none") {
            create_space_table.style.display = "table";
            create_space_name.focus();
        }
        else {
            create_space_table.style.display = "none";
        }
    });

    create_space_cancel.addEventListener('click', reset_create);

    create_space_confirm.addEventListener("click", async (event) => {
        // To-Do: add input validation
        let name = create_space_name.value;

        if (name == "") return;

        try {
            const response = await fetch(window.location.origin + "/dash/spaces/create", {
                method: "POST",
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify([name]),
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
            let target = button.dataset.target;

            if (target == "space") {
                let space_name = button.dataset.spacename;

                let confirmation = "Are you sure you want to delete this space?";
                if (confirm(confirmation) == false) {
                    return console.log("Deletion cancelled");
                }

                try {
                    const response = await fetch(window.location.origin + "/dash/spaces/delete", {
                        method: "POST",
                        // Set the FormData instance as the request body
                        headers: {
                            'Accept': 'application/json',
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify([space_name]),
                    });

                    let result = await response.json();

                    if (result.success === true && result.message && result.message != "") {
                        // Delete parent to avoid page reload
                        let closest_tr = button.parentNode.closest('tr');
                        closest_tr.remove();

                        notify(result.message);
                    }
                    else if (result.success === false && result.message && result.message != "") {
                        // To-Do: make them autodisappear
                        notify(result.message);
                    }
                    else {
                        notify("An unknown error has occurred.");
                    }
                } catch (e) {
                    console.error(e);
                }
            }
            else if (target == "file") {

            }
        });
    });

    copy_buttons.forEach(button => {
        button.addEventListener('click', async () => {
            let target = button.dataset.target;

            if (target == "space") {
                let space_link = button.dataset.spacelink;

                try {
                    navigator.clipboard.writeText('https://' + space_link).then(() => {
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
            }
        });
    });
})();