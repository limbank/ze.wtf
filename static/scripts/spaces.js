(function(){
    //To-Do: Clean this up
    console.log("Spaces loaded")

    const create_directory_button = document.getElementById("create-directory-button");
    const upload_file_button = document.getElementById("upload-file-button");
    const create_directory_table = document.getElementById("create-directory");
    const upload_file_table = document.getElementById("upload-file");
    const path_address = document.getElementById("path-address");
    const space_domain = document.getElementById("space-domain");

    const delete_button_template = `
        <svg viewBox="0 0 24 24">
            <g id="icons">
                <path d="M14.8,12l3.6-3.6c0.8-0.8,0.8-2,0-2.8c-0.8-0.8-2-0.8-2.8,0L12,9.2L8.4,5.6c-0.8-0.8-2-0.8-2.8,0   c-0.8,0.8-0.8,2,0,2.8L9.2,12l-3.6,3.6c-0.8,0.8-0.8,2,0,2.8C6,18.8,6.5,19,7,19s1-0.2,1.4-0.6l3.6-3.6l3.6,3.6   C16,18.8,16.5,19,17,19s1-0.2,1.4-0.6c0.8-0.8,0.8-2,0-2.8L14.8,12z" fill="currentColor"/>
            </g>
        </svg>
    `;

    const save_button_template = `
        <svg viewBox="0 0 24 24" >
            <g id="icons">
                <path d="M10,18c-0.5,0-1-0.2-1.4-0.6l-4-4c-0.8-0.8-0.8-2,0-2.8c0.8-0.8,2.1-0.8,2.8,0l2.6,2.6l6.6-6.6   c0.8-0.8,2-0.8,2.8,0c0.8,0.8,0.8,2,0,2.8l-8,8C11,17.8,10.5,18,10,18z" fill="currentColor"/>
            </g>
        </svg>
    `;

    const open_button_template = `
        <svg viewBox="0 0 24 24">
            <g id="icons">
                <path d="M21.7,10.2l-6.6-6C14.6,3.7,14,4.2,14,5v3c-4.7,0-8.7,2.9-10.6,6.8c-0.7,1.3-1.1,2.7-1.4,4.1   c-0.2,1,1.3,1.5,1.9,0.6C6.1,16,9.8,13.7,14,13.7V17c0,0.8,0.6,1.3,1.1,0.8l6.6-6C22.1,11.4,22.1,10.6,21.7,10.2z" fill="currentColor"/>
            </g>
        </svg>
    `;

    let maxDepth = 1;  // Controls depth
    let basePath = ""; // Stores the current directory level
    let backup_data;

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
            addDeleteButton(button_parent, path + "/" + filtered_dirname)
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
            addOpenButton(button_parent, path + "/" + filtered_filename)
            addDeleteButton(button_parent, path + "/" + filtered_filename)
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

    create_directory_button.addEventListener("click", (event) => {
        if (create_directory_table.style.display  == "none") {
            create_directory_table.style.display = "table";
        }
        else {
            create_directory_table.style.display = "none";
        }

        upload_file_table.style.display = "none";
    });

    upload_file_button.addEventListener("click", (event) => {
        if (upload_file_table.style.display == "none") {
            upload_file_table.style.display = "table";
        }
        else {
            upload_file_table.style.display = "none";
        }

        create_directory_table.style.display = "none";
    });

    fetch('/dash/spaces/files')
    .then(response => response.json())
    .then(data => {
            backup_data = data;
            updatePath("");
            renderDirectoryListing(data, basePath);
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
                body: JSON.stringify({
                    "delete": will_delete
                })
            });

            let result = await response.json();
            /*
            let new_notif = document.createElement('div');
            new_notif.className = 'notif';
            new_notif.innerHTML = result.message;
            new_space_delete
            notification_area.appendChild(new_notif);
            
            if (result.success) location.reload();
            */
            console.log(result)

            if (result.success === false) {
                return console.log("Error attempting to delete...");
            }
            
            console.log("ATTEMPTING TO REBUILD");
            backup_data = result;
            updatePath("");
            renderDirectoryListing(result, basePath);
        }
        else if (button.classList.contains("browser-open")) {
            window.open(`${location.protocol}//${space_domain.innerText}${button.dataset.target}`, '_blank');
        }
    });
})();