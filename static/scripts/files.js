(function(){
    //To-Do: Clean this up
    console.log("Loaded");
    const notification_area = document.getElementById('notifications');
    const delete_buttons = document.querySelectorAll('.delete-item');
    const copy_buttons = document.querySelectorAll('.copy-item');

    const upload_file_toggle = document.getElementById("upload-file-toggle");
    const upload_file_table = document.getElementById("upload-file-table");
    const upload_file_input = document.getElementById("upload-file-input");
    const upload_file_label = document.getElementById("upload-file-label");
    const upload_file_confirm = document.getElementById("upload-file-confirm");
    const upload_file_cancel = document.getElementById("upload-file-cancel");

    function reset_upload() {
        upload_file_table.style.display = "none";
        upload_file_input.value = "";
        upload_file_label.innerHTML = "Click to select file";
    }

    upload_file_toggle.addEventListener('click', async () => {
        if (upload_file_table.style.display  == "none") {
            upload_file_table.style.display = "table";
        }
        else {
            upload_file_table.style.display = "none";
        }
    });

    upload_file_cancel.addEventListener('click', reset_upload);

    upload_file_input.addEventListener("change", async (event) => {
        let files = upload_file_input.files;

        let filename_string = "";

        if (files.length) {
            for (let i = 0; i < files.length; i++) {
                filename_string += files[i].name;
                if (i < files.length - 1) filename_string += ", ";
            }
        }

        upload_file_label.innerHTML = filename_string;
    });

    upload_file_confirm.addEventListener("click", async (event) => {
        // To-Do: add input validation
        let files = upload_file_input.files;

        if (files.length) {
            const formData = new FormData();

            [...files].forEach((file, i) => {
                formData.append("file", file, file.path);
            });

            try {
                const response = await fetch(window.location.origin + "/dash/files", {
                    method: "POST",
                    body: formData,
                });

                let result = await response.json();

                if (result.success === false) {
                    console.log(result);
                    return console.log("Error attempting to upload...");
                }

                reset_upload();
                location.reload();
            } catch (e) {
                console.error(e);
            }
        }
    });

    delete_buttons.forEach(button => {
        button.addEventListener('click', async () => {
            let target_file = button.dataset.filename;

            let confirmation = "Are you sure you want to delete this file?";
            if (confirm(confirmation) == false) {
                return console.log("Deletion cancelled");
            }

            try {
                const response = await fetch(window.location.origin + "/dash/files", {
                    method: "POST",
                    // Set the FormData instance as the request body
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        "delete": target_file
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