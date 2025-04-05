(function(){
    console.log("Key script loaded");

    const delete_buttons = document.querySelectorAll('.delete-item');

    const create_key_toggle = document.getElementById("create-key-toggle");
    const create_key_table = document.getElementById("create-key-table");
    const create_key_name = document.getElementById("create-key-name");
    const create_key_expiry = document.getElementById("create-key-expiry");
    const create_key_confirm = document.getElementById("create-key-confirm");
    const create_key_cancel = document.getElementById("create-key-cancel");

    function reset_create() {
        create_key_table.style.display = "none";
        create_key_expiry.value = "";
    }

    create_key_toggle.addEventListener('click', async () => {
        if (create_key_table.style.display  == "none") {
            create_key_table.style.display = "table";
        }
        else {
            create_key_table.style.display = "none";
        }
    });

    create_key_cancel.addEventListener('click', reset_create);

    create_key_confirm.addEventListener("click", async (event) => {
        let expiry = create_key_expiry.value;
        let name = create_key_name.value;

        try {
            const response = await fetch(window.location.origin + "/dash/keys/create", {
                method: "POST",
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify([{
                    "name": name,
                    "expires": expiry
                }]),
            });

            let result = await response.json();

            notify(result.message);

            if (result.success === false) {
                console.log(result);
            }

            if (result.keys) {
                let notify_string = "Here are your created keys. Please remember to write them down as you will not be able to see them again: <br><br>";

                for (let i = 0; i < result.keys.length; i++) {
                    notify_string += result.keys[i].name + ": " + result.keys[i].key

                    if (i < result.keys.length - 1) notify_string += "<br>";
                }

                notify(notify_string, -1);
            }

            // Instead of reloading, just append the newly created tr
            reset_create();
            //location.reload();
        } catch (e) {
            notify("Error attempting to create key...");
            console.error(e);
        }
    });

    delete_buttons.forEach(button => {
        button.addEventListener('click', async () => {
            let key_name = button.dataset.keyname;

            let confirmation = "Are you sure you want to delete this key?";
            if (confirm(confirmation) == false) {
                return console.log("Deletion cancelled");
            }

            try {
                const response = await fetch(window.location.origin + "/dash/keys/delete", {
                    method: "POST",
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify([key_name]),
                });

                let result = await response.json();

                notify(result.message);

                if (result.success === false) {
                    console.log(result);
                }

                // Instead of reloading, just append the newly created tr
                reset_create();
                //location.reload();
            } catch (e) {
                notify("Error attempting to delete key...");
                console.error(e);
            }
        });
    });
})()