(function(){
    //To-Do: Clean this up
    console.log("File script loaded");

    const delete_buttons = document.querySelectorAll('.delete-item');
    const copy_buttons = document.querySelectorAll('.copy-item');

    const upload_file_toggle = document.getElementById("upload-file-toggle");
    const upload_file_table = document.getElementById("upload-file-table");
    const upload_file_input = document.getElementById("upload-file-input");
    const upload_file_label = document.getElementById("upload-file-label");
    const upload_file_confirm = document.getElementById("upload-file-confirm");
    const upload_file_cancel = document.getElementById("upload-file-cancel");

    const progress = document.getElementById("progress");
    const progress_inner = document.getElementById("progress-inner");

    function reset_upload() {
        progress.style.display = "none";
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
                progress.style.display = "block";

                let xhr = new XMLHttpRequest();

                xhr.open("POST", window.location.origin + "/dash/files/upload", true);
                xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");

                xhr.upload.onprogress = function (event) {
                    if (event.lengthComputable) {
                        let percentComplete = (event.loaded / event.total) * 100;
                        progress_inner.style.width = percentComplete + "%";
                        console.log(Math.round(percentComplete) + "%")
                    }
                };

                // When the upload is complete
                xhr.onload = function () {
                    if (xhr.status === 200) {
                        try {
                            let response = JSON.parse(xhr.responseText);

                            if (response.success === false) {
                                notify("Error attempting to upload...");
                                return console.log(result);
                            }

                            reset_upload();
                            location.reload();
                        }
                        catch (error) {
                            notify("Error parsing server response...");
                            return console.log(error);
                        }
                    }
                    else {
                        notify("Upload Failed: " + xhr.statusText);
                    }
                };

                xhr.send(formData);
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
                const response = await fetch(window.location.origin + "/dash/files/delete", {
                    method: "POST",
                    // Set the FormData instance as the request body
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify([target_file]),
                });

                let result = await response.json();
                console.log(result)

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
                    notify("An unknown error has occurred...");
                }
            }
            catch (e) {
                console.error(e);
            }
        });
    });

    copy_buttons.forEach(button => {
        button.addEventListener('click', async () => {
            let target_file = button.dataset.target;

            try {
                navigator.clipboard.writeText('https://' + target_file).then(() => {
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