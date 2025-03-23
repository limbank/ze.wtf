(function(){
    //To-Do: Clean this up
    console.log("Loaded");

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

        let new_name;
        let new_destination = "";

        if (will_edit.match(/\/.*/)) {
            new_destination = will_edit.substring(0, will_edit.lastIndexOf("/"));
            new_name = will_edit.substring(will_edit.lastIndexOf("/") + 1, will_edit.length);
        }
        else {
            new_name = will_edit;
        }

        const formData = new FormData();
        formData.append("file", fileBlob, new_name);

        formData.append("destination", new_destination);

        try {
            const response = await fetch(window.location.origin + "/dash/spaces/files", {
                method: "POST",
                // Set the FormData instance as the request body
                body: formData,
            });

            let result = await response.json();

            if (result.success === false) {
                console.log(result);
                return console.log("Error attempting to upload...");
            }

            close_editor();
            buildTree(result);
        } catch (e) {
            console.error(e);
        }
    });

    edit_cancel.addEventListener("click", async (event) => {
        close_editor();
    });
})()