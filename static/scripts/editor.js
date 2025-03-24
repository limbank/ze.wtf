(function(){
    //To-Do: Clean this up
    console.log("Loaded");

    const progress = document.getElementById("progress");
    const progress_inner = document.getElementById("progress-inner");

    const editor_parent = document.getElementById("file-editor");
    const edit_address = document.getElementById("edit-address");

    const edit_save = document.getElementById("save-edit-button");
    const edit_cancel = document.getElementById("cancel-edit-button");

    let editor = new Editor();
    let will_edit;

    // Delete directory and file handler
    document.body.addEventListener("click", async (event) => {
        let button = event.target;
        if (button.classList.contains("browser-edit")) {
            will_edit = button.dataset.target;

            edit_address.innerHTML = will_edit;

            if (will_edit.startsWith("/")) will_edit = will_edit.substring(1);

            var n = will_edit.lastIndexOf('.');
            let file_language = will_edit.substring(n + 1);

            const response = await fetch(window.location.origin + "/dash/spaces/files/download", {
                method: "POST",
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify([will_edit])
            });

            let contentType = response.headers.get("Content-Type");

            if (contentType && contentType.includes("application/json") && !will_edit.endsWith(".json")) {
                // The response is JSON (an error case)
                let result = await response.json();
                if (result.success === false) {
                    console.log(result);
                    return console.log("Error attempting to edit...");
                }
            }
            else {
                // The response is a file (success case)
                let blob = await response.blob();
                let fileContents = await blob.text();  // Convert Blob to string

                // Start editor and load file here...
                editor.runEditor();
                editor_parent.classList.add("open");
                editor.setLanguage(file_language);
                editor.setValue(fileContents);
            }
        }
    });

    function close_editor() {
        editor_parent.classList.remove("open");
        edit_address.innerHTML = "";
        editor.close();
        will_edit = "";
    }

    edit_save.addEventListener("click", async (event) => {
        if (!will_edit || will_edit == "") return console.log("Missing filename");

        let file_contents = editor.getValue();
        let fileBlob = new Blob([file_contents], { type: "text/plain" });

        console.log(will_edit)

        /*
            if includes slash, split at last slash, 0 = directory, 1 = file
        */

        //let new_name;
        //let new_destination = "";

        //if (will_edit.match(/\/.*/)) {
        //    new_destination = will_edit.substring(0, will_edit.lastIndexOf("/"));
        //    new_name = will_edit.substring(will_edit.lastIndexOf("/") + 1, will_edit.length);
        //}
        //else {
        //    new_name = will_edit;
        //}

        //console.log("NEW NAME", new_name)

        const formData = new FormData();
        formData.append("file", fileBlob, will_edit);
        
        try {
            progress.style.display = "block";

            let xhr = new XMLHttpRequest();

            xhr.open("POST", window.location.origin + "/dash/spaces/files/upload", true);
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

                        notify(response.message);

                        if (response.success === false) {
                            notify("Error attempting to save...");
                            return console.log(result);
                        }

                        // Should i rerun this request?
                        get_file_tree();
                        close_editor();

                        progress.style.display = "none";
                    }
                    catch (error) {
                        notify("Error parsing server response...");
                        return console.log(error);
                    }
                }
                else {
                    notify("Save failed: " + xhr.statusText);
                }
            };

            xhr.send(formData);
        } catch (e) {
            console.error(e);
        }
    });

    edit_cancel.addEventListener("click", async (event) => {
        close_editor();
    });
})()