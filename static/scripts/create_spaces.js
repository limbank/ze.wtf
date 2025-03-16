(function(){
    //To-Do: Clean this up
    console.log("Spaces create loaded")

    const create_space = document.getElementById("create-space");
    const create_space_table = document.getElementById("create-space-table");
    const created_space_table = document.getElementById("created-space-table");
    const space_name = document.getElementById("space-name");
    const approve_space = document.getElementById("approve-space");
    const deny_space = document.getElementById("deny-space");

    const notification_area = document.getElementById('notifications');

    create_space.addEventListener("click", (event) => {
        event.preventDefault();

        create_space_table.style.display = "none";
        created_space_table.style.display = "table";
        space_name.focus();
    });

    approve_space.addEventListener("click", async (event) => {
        let new_name = space_name.value;

        if (!new_name || new_name == "") return;

        try {
            const response = await fetch(window.location.origin + "/dash/spaces/create", {
                method: "POST",
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    "name": new_name
                })
            });

            let result = await response.json();

            let new_notif = document.createElement('div');
            new_notif.className = 'notif';
            new_notif.innerHTML = result.message;
            //new_space_delete
            notification_area.appendChild(new_notif);

            if (result.success) location.reload();
        } catch (e) {
            console.error(e);
        }
    });

    deny_space.addEventListener("click", (event) => {
        create_space_table.style.display = "table";
        created_space_table.style.display = "none";
        space_name.value = "";
    });
})()