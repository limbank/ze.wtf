(function(){
    //To-Do: Clean this up
    console.log("Loaded");
    const file_input = document.getElementById("file-upload");
    const zone = document.getElementById("dropzone");
    const upload_status = document.getElementById("result");
    const form = document.getElementById("form");

    zone.addEventListener("dragover", (event) => {
        // prevent default to allow drop
        event.preventDefault();
    });

    zone.addEventListener("dragenter", (event) => {
        // prevent default to allow drop
        event.preventDefault();

        // add class to indicate dragging
        if (!zone.classList.contains("form__file-dragging")) {
            zone.classList.toggle('form__file-dragging');
        }
    });

    zone.addEventListener("dragleave", (event) => {
        // prevent default to allow drop
        event.preventDefault();

        // remove class to indicate leave
        if (zone.classList.contains("form__file-dragging")) {
            zone.classList.toggle('form__file-dragging');
        }
    });

    zone.addEventListener("drop", async (event) => {
        // prevent default action (open as link for some elements)
        event.preventDefault();

        // remove class to indicate drop
        if (zone.classList.contains("form__file-dragging")) {
            zone.classList.toggle('form__file-dragging');
        }

        // move dragged element to the selected drop zone
        if (event.target.id === "dropzone") {
            const formData = new FormData();

            if (event.dataTransfer.items) {
                // Use DataTransferItemList interface to access the file(s)
                [...event.dataTransfer.items].forEach((item, i) => {
                    // If dropped items aren't files, reject them
                    if (item.kind === "file") {
                        const file = item.getAsFile();
                        formData.append("file", file, file.name);
                    }
                });
            }
            else {
                // Use DataTransfer interface to access the file(s)
                [...event.dataTransfer.files].forEach((file, i) => {
                    formData.append("file", file, file.name);
                });
            }

            try {
                const response = await fetch(window.location.origin + "/images", {
                    method: "POST",
                    // Set the FormData instance as the request body
                    body: formData,
                });


                let result = await response.json();

                upload_status.innerText = result.message;
                upload_status.style.display = "inline-flex";
                form.style.display = "none";
            } catch (e) {
                console.error(e);
            }
        }
    });

    file_input.addEventListener("change", async function(event) {
        let files = file_input.files;
        if (files.length) {
            const formData = new FormData();

            [...files].forEach((file, i) => {
                formData.append("file", file, file.name);
            });

            try {
                const response = await fetch(window.location.origin + "/images", {
                    method: "POST",
                    // Set the FormData instance as the request body
                    body: formData,
                });

                let result = await response.json();

                upload_status.innerText = result.message;
                upload_status.style.display = "inline-flex";
                form.style.display = "none";
            } catch (e) {
                console.error(e);
            }
        }
    }, false);
})()