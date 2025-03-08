(function(){
    console.log("Loaded");
    const zone = document.getElementById("dropzone");

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

    zone.addEventListener("drop", (event) => {
        // prevent default action (open as link for some elements)
        event.preventDefault();

        // remove class to indicate drop
        if (zone.classList.contains("form__file-dragging")) {
            zone.classList.toggle('form__file-dragging');
        }

        // move dragged element to the selected drop zone
        if (event.target.id === "dropzone") {
            console.log("Item dropped");

            if (event.dataTransfer.items) {
                // Use DataTransferItemList interface to access the file(s)
                [...event.dataTransfer.items].forEach((item, i) => {
                // If dropped items aren't files, reject them
                if (item.kind === "file") {
                    const file = item.getAsFile();
                    console.log(`… file[${i}].name = ${file.name}`);
                }
                });
            }
            else {
                // Use DataTransfer interface to access the file(s)
                [...event.dataTransfer.files].forEach((file, i) => {
                    console.log(`… file[${i}].name = ${file.name}`);
                });
            }
        }
    });
})()