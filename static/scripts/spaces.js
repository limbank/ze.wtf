(function(){
    //To-Do: Clean this up
    console.log("Spaces loaded")

    const create_directory_button = document.getElementById("create-directory-button");
    const upload_file_button = document.getElementById("upload-file-button");
    const create_directory_table = document.getElementById("create-directory");
    const upload_file_table = document.getElementById("upload-file");

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
})()