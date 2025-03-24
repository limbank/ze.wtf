(function(){
    //To-Do: Clean this up
    console.log("Spaces browser script loaded");

    const progress = document.getElementById("progress");
    const progress_inner = document.getElementById("progress-inner");

    const create_directory_button = document.getElementById("create-directory-button");
    const upload_file_button = document.getElementById("upload-file-button");
    const create_directory_table = document.getElementById("create-directory");
    const upload_file_table = document.getElementById("upload-file");
    const path_address = document.getElementById("path-address");
    const space_domain = document.getElementById("space-domain");

    const cancel_file = document.getElementById("cancel-file");
    const cancel_directory = document.getElementById("cancel-directory");
    const save_file = document.getElementById("save-file");
    const save_directory = document.getElementById("save-directory");
    const new_directory_name = document.getElementById("new-directory-name");
    const new_file_name = document.getElementById("new-file-name");
    const new_file_label = document.getElementById("new-file-label");

    const upload_directory_button = document.getElementById("upload-directory-button");
    const upload_directory = document.getElementById("upload-directory");
    const confirm_upload_directory = document.getElementById("confirm-upload-directory");
    const cancel_upload_directory = document.getElementById("cancel-upload-directory");
    const upload_new_directory = document.getElementById("upload-new-directory");
    const upload_new_directory_label = document.getElementById("upload-new-directory-label");

    const create_file_table = document.getElementById("create-file");
    const new_created_file_name = document.getElementById("new-created-file-name");
    const create_new_file = document.getElementById("create-new-file");
    const cancel_new_file = document.getElementById("cancel-new-file");
    const create_new_file_button = document.getElementById("create-new-file-button");

    const delete_button_template = `
        <svg viewBox="0 0 24 24">
            <g>
                <path d="M14.8,12l3.6-3.6c0.8-0.8,0.8-2,0-2.8c-0.8-0.8-2-0.8-2.8,0L12,9.2L8.4,5.6c-0.8-0.8-2-0.8-2.8,0   c-0.8,0.8-0.8,2,0,2.8L9.2,12l-3.6,3.6c-0.8,0.8-0.8,2,0,2.8C6,18.8,6.5,19,7,19s1-0.2,1.4-0.6l3.6-3.6l3.6,3.6   C16,18.8,16.5,19,17,19s1-0.2,1.4-0.6c0.8-0.8,0.8-2,0-2.8L14.8,12z" fill="currentColor"/>
            </g>
        </svg>
    `;

    const save_button_template = `
        <svg viewBox="0 0 24 24" >
            <g>
                <path d="M10,18c-0.5,0-1-0.2-1.4-0.6l-4-4c-0.8-0.8-0.8-2,0-2.8c0.8-0.8,2.1-0.8,2.8,0l2.6,2.6l6.6-6.6   c0.8-0.8,2-0.8,2.8,0c0.8,0.8,0.8,2,0,2.8l-8,8C11,17.8,10.5,18,10,18z" fill="currentColor"/>
            </g>
        </svg>
    `;

    const open_button_template = `
        <svg viewBox="0 0 24 24">
            <g>
                <path d="M21.7,10.2l-6.6-6C14.6,3.7,14,4.2,14,5v3c-4.7,0-8.7,2.9-10.6,6.8c-0.7,1.3-1.1,2.7-1.4,4.1   c-0.2,1,1.3,1.5,1.9,0.6C6.1,16,9.8,13.7,14,13.7V17c0,0.8,0.6,1.3,1.1,0.8l6.6-6C22.1,11.4,22.1,10.6,21.7,10.2z" fill="currentColor"/>
            </g>
        </svg>
    `;

    const edit_button_template = `
        <svg viewBox="0 0 24 24">
            <g id="icons">
                <g>
                    <path d="M2,20c0,1.1,0.9,2,2,2h2.6L2,17.4V20z" fill="currentColor"/>
                    <path d="M21.6,5.6l-3.2-3.2c-0.8-0.8-2-0.8-2.8,0l-0.2,0.2C15,3,15,3.6,15.4,4L20,8.6c0.4,0.4,1,0.4,1.4,0l0.2-0.2    C22.4,7.6,22.4,6.4,21.6,5.6z"/><path d="M14,5.4c-0.4-0.4-1-0.4-1.4,0l-9.1,9.1C3,15,3,15.6,3.4,16L8,20.6c0.4,0.4,1,0.4,1.4,0l9.1-9.1c0.4-0.4,0.4-1,0-1.4    L14,5.4z" fill="currentColor"/>
                </g>
            </g>
        </svg>
    `;

    let maxDepth = 1;  // Controls depth
    let basePath = ""; // Stores the current directory level
    let backup_data;

    let editable_files = [
        'html', 'css', 'js', 'json'
    ];

    function updatePath(newPath) {
        basePath = newPath;
        path_address.innerHTML = "/" + newPath;
    }

    function makeButtonWrapper() {
        const buttons_td = document.createElement('td');
        const buttons_wrapper = document.createElement('div');
        buttons_td.className = "table__button-cell";
        buttons_wrapper.className = "table__buttons";
        buttons_td.appendChild(buttons_wrapper);
        return buttons_td;
    }

    function addOpenButton(parent, target) {
        let button_container = parent.firstChild;
        const current_button = document.createElement('button');
        current_button.className = "action-button browser-open";
        current_button.dataset.target = target;
        current_button.insertAdjacentHTML('afterbegin', open_button_template);
        button_container.appendChild(current_button);
    }

    function addDeleteButton(parent, target) {
        let button_container = parent.firstChild;
        const current_button = document.createElement('button');
        current_button.className = "action-button browser-delete";
        current_button.dataset.target = target;
        current_button.insertAdjacentHTML('afterbegin', delete_button_template);
        button_container.appendChild(current_button);
    }

    function addEditButton(parent, target) {
        let button_container = parent.firstChild;
        const current_button = document.createElement('button');
        current_button.className = "action-button browser-edit";
        current_button.dataset.target = target;
        current_button.insertAdjacentHTML('afterbegin', edit_button_template);
        button_container.appendChild(current_button);
    }

    function renderDirectoryListing(data, path) {
        const container = document.getElementById("file-browser").getElementsByTagName('tbody')[0];
        container.innerHTML = ""; // Clear previous content

        // Ensure directories and files are filtered correctly
        const filteredDirs = data.directories.filter(dir => isDirectChild(dir, path, true));
        const filteredFiles = data.files.filter(file => isDirectChild(file, path, false));

        // Add "../" at the top if we're inside a subdirectory
        if (path) {
            const parent_tr = document.createElement('tr');
            const backElement = document.createElement('td');
            const navLink = document.createElement("a");
            navLink.className = "file-browser__directory";
            navLink.onclick = (e) => {
                e.preventDefault();
                navigateBack(data);
            };
            navLink.textContent = "../";
            backElement.appendChild(navLink);
            parent_tr.appendChild(backElement);
            container.appendChild(parent_tr);
        }

        // Display directories first
        filteredDirs.forEach(dir => {
            const parent_tr = document.createElement('tr');
            const dirElement = document.createElement('td');
            const navLink = document.createElement("a");
            navLink.className = "file-browser__directory";

            let filtered_dirname = path ? dir.replace(path + "/", "") : dir;

            navLink.textContent = `/${filtered_dirname.replace(/\/$/, "")}`;

            if (navLink.textContent == "/") return;

            navLink.onclick = (e) => {
                e.preventDefault();
                navigateTo(dir, data);
            };

            dirElement.appendChild(navLink);
            parent_tr.appendChild(dirElement);
            let button_parent = makeButtonWrapper();
            addDeleteButton(button_parent, path + "/" + filtered_dirname);
            parent_tr.appendChild(button_parent);
            container.appendChild(parent_tr);
        });

        // Display files (remove prefix from file names if inside a subdirectory)
        filteredFiles.forEach(file => {
            const parent_tr = document.createElement('tr');
            const fileElement = document.createElement('td');
            let filtered_filename = path ? file.replace(path + "/", "") : file;
            fileElement.textContent = filtered_filename;
            parent_tr.appendChild(fileElement);
            let button_parent = makeButtonWrapper();
            addOpenButton(button_parent, path + "/" + filtered_filename);

            if (editable_files.some(s => filtered_filename.endsWith(s))) {
                addEditButton(button_parent, path + "/" + filtered_filename);
            }

            addDeleteButton(button_parent, path + "/" + filtered_filename);
            parent_tr.appendChild(button_parent);
            container.appendChild(parent_tr);
        });
    }

    // Function to check if an item is a direct child of the current path
    function isDirectChild(item, currentPath, isDir) {
        if (currentPath) {
            if (!item.startsWith(currentPath)) return false; // Ignore items outside the path
            item = item.substring(currentPath.length); // Remove basePath from the item
        }

        item = item.replace(/^\/+/, ""); // Remove leading slashes

        // Ensure it's a direct child (not deeper nested)
        let depth = item.split('/').length;

        if (isDir) {
            return depth === 1 || (depth === 2 && item.endsWith('/')); // Directories must be one level deep
        } else {
            return depth === 1; // Files must be one level deep
        }
    }

    // Function to navigate into directories
    function navigateTo(dir, data) {
        updatePath(dir.replace(/\/$/, '')); // Remove trailing slash for navigation
        renderDirectoryListing(data, basePath);
    }

    function navigateBack(data) {
        let parts = basePath.split('/');
        parts.pop(); // Remove last directory
        updatePath(parts.join('/'));
        renderDirectoryListing(data, basePath);
    }

    upload_directory_button.addEventListener("click", (event) => {
        if (upload_directory.style.display  == "none") {
            upload_directory.style.display = "table";
        }
        else {
            upload_directory.style.display = "none";
        }

        create_directory_table.style.display = "none";
        upload_file_table.style.display = "none";
        create_file_table.style.display = "none";
    });

    cancel_upload_directory.addEventListener("click", (event) => {
        upload_directory.style.display = "none";
        upload_new_directory.value = "";
        upload_new_directory_label.innerHTML = "Click to select directory";
    });

    create_directory_button.addEventListener("click", (event) => {
        if (create_directory_table.style.display  == "none") {
            create_directory_table.style.display = "table";
            new_directory_name.focus();
        }
        else {
            create_directory_table.style.display = "none";
        }

        upload_directory.style.display = "none";
        upload_file_table.style.display = "none";
        create_file_table.style.display = "none";
    });

    upload_file_button.addEventListener("click", (event) => {
        if (upload_file_table.style.display == "none") {
            upload_file_table.style.display = "table";
        }
        else {
            upload_file_table.style.display = "none";
        }

        upload_directory.style.display = "none";
        create_directory_table.style.display = "none";
        create_file_table.style.display = "none";
    });

    create_new_file_button.addEventListener("click", (event) => {
        if (create_file_table.style.display == "none") {
            create_file_table.style.display = "table";
        }
        else {
            create_file_table.style.display = "none";
        }

        upload_directory.style.display = "none";
        create_directory_table.style.display = "none";
        upload_file_table.style.display = "none";
    });

    window.buildTree = (data, reset = false) => {
        console.log("Building tree...");
        backup_data = data;
        if (reset) updatePath("");
        renderDirectoryListing(data, basePath);
    }

    window.get_file_tree = async (reset) => {
        console.log("Getting file tree...");

        try {
            const response = await fetch(window.location.origin + "/dash/spaces/files/", {
                method: "GET",
                // Set the FormData instance as the request body
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            });

            let result = await response.json();
            
            if (result.success) {
                buildTree(result.files, reset);
            }
            else {
                notify(result.message);
            }
        }
        catch (e) {
            console.error(e);
        }
    }
    get_file_tree(true);

    cancel_file.addEventListener("click", async (event) => {
        new_file_name.value = "";
        upload_file_table.style.display = "none";
        new_file_label.innerHTML = "Click to select file";
    });

    cancel_directory.addEventListener("click", async (event) => {
        new_directory_name.value = "";
        create_directory_table.style.display = "none";
    });

    cancel_new_file.addEventListener("click", async (event) => {
        new_created_file_name.value = "";
        create_file_table.style.display = "none";
    });

    create_new_file.addEventListener("click", async (event) => {
        let created_file_slug = new_created_file_name.value;
        //return to here

        if (created_file_slug == "") return console.log("File name blank");

        if (editable_files.some(s => created_file_slug.endsWith(s)) == false) {
            //file name not allowed
            return console.log("Filetype not allowed", created_file_slug);
        }

        let file_location = basePath;

        if (basePath != "") file_location += '/';

        let target_file = file_location + created_file_slug;

        const response = await fetch(window.location.origin + "/dash/spaces/files/create", {
            method: "POST",
            // Set the FormData instance as the request body
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify([target_file]),
        });

        let result = await response.json();
        
        notify(result.message);

        if (result.success === false) {
            return console.log(result);
        }

        // Should i rerun this request?
        get_file_tree();

        new_created_file_name.value = "";
        create_file_table.style.display = "none";
    });

    save_file.addEventListener("click", async (event) => {
        // Upload files

        let files = new_file_name.files;

        if (files.length) {
            const formData = new FormData();

            [...files].forEach((file, i) => {
                let file_location = basePath;

                if (basePath != "") file_location += '/';

                formData.append("file", file, file_location + file.name);
            });

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
                                notify("Error attempting to upload...");
                                return console.log(result);
                            }

                            // Should i rerun this request?
                            get_file_tree();

                            new_file_name.value = "";
                            upload_file_table.style.display = "none";
                            progress.style.display = "none";
                            new_file_label.innerHTML = "Click to select file";
                        }
                        catch (error) {
                            notify("Error parsing server response...");
                            return console.log(error);
                        }
                    }
                    else {
                        notify("Upload failed: " + xhr.statusText);
                    }
                };

                xhr.send(formData);
            } catch (e) {
                console.error(e);
            }
        }
    });

    save_directory.addEventListener("click", async (event) => {
        // To-Do: add input validation
        let new_name = new_directory_name.value;

        if (new_name == "") return;

        let file_location = basePath;

        if (basePath != "") file_location += '/';

        let target_dir = file_location + new_name;

        const response = await fetch(window.location.origin + "/dash/spaces/files/create", {
            method: "POST",
            // Set the FormData instance as the request body
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify([target_dir]),
        });

        let result = await response.json();
        
        notify(result.message);

        if (result.success === false) {
            return console.log(result);
        }

        // Should i rerun this request?
        get_file_tree();

        new_directory_name.value = "";
        create_directory_table.style.display = "none";
    });

    confirm_upload_directory.addEventListener("click", async (event) => {
        // To-Do: add input validation
        //upload_new_directory
        let files = upload_new_directory.files;

        if (files.length) {
            const formData = new FormData();

            [...files].forEach((file, i) => {
                let file_location = basePath;

                if (basePath != "") file_location += '/';

                formData.append("file", file, file_location + file.webkitRelativePath);
            });

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
                                notify("Error attempting to upload...");
                                return console.log(result);
                            }

                            // Should i rerun this request?
                            get_file_tree();

                            upload_directory.style.display = "none";
                            upload_new_directory.value = "";
                            upload_new_directory_label.innerHTML = "Click to select directory";
                            progress.style.display = "none";
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

    upload_new_directory.addEventListener("change", async (event) => {
        let files = upload_new_directory.files;

        if (files.length) {
            let file_path = files[0].webkitRelativePath;
            let source_dir = file_path.substr(0, file_path.indexOf("/") + 1);

            upload_new_directory_label.innerHTML = source_dir;
        }
    });

    new_file_name.addEventListener("change", async (event) => {
        if (new_file_name.files.length > 0) {
            let new_label_text = "";

            for (let i = 0; i < new_file_name.files.length; i++) {
                new_label_text +=new_file_name.files[i].name;

                if (i < new_file_name.files.length - 1) new_label_text += ", "
            }

            new_file_label.innerHTML = new_label_text;
        }
    });

    // Delete directory and file handler
    document.body.addEventListener("click", async (event) => {
        let button = event.target;
        if (button.classList.contains("browser-delete")) {
            let will_delete = button.dataset.target;

            let text = `You are about to delete '${will_delete}'. Are you sure?`;
            if (confirm(text) != true) return;

            if (will_delete.charAt(0) === '/') {
                will_delete = will_delete.substring(1);
            }

            const response = await fetch(window.location.origin + "/dash/spaces/files/delete", {
                method: "POST",
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify([will_delete])
            });

            let result = await response.json();

            notify(result.message);

            if (result.success === false) {
                return console.log("Error attempting to delete...");
            }

            // just remove the tr instead of rebuilding
            get_file_tree();
        }
        else if (button.classList.contains("browser-open")) {
            let baseURL = `${location.protocol}//${space_domain.innerText}`;

            if (button.dataset.target.startsWith("/")) {
                baseURL += button.dataset.target;
            }
            else {
                baseURL += "/" + button.dataset.target;
            }

            window.open(baseURL, '_blank');
        }
    });
})();