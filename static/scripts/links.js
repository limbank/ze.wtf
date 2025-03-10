(function(){
    //To-Do: Clean this up
    console.log("Loaded");
    const notification_area = document.getElementById('notifications');
    const delete_buttons = document.querySelectorAll('.delete-link');

    delete_buttons.forEach(button => {
        button.addEventListener('click', async () => {
            let target_url = button.dataset.urlname;

            try {
                const response = await fetch(window.location.origin + "/links", {
                    method: "POST",
                    // Set the FormData instance as the request body
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        "delete": target_url
                    }),
                });

                let result = await response.json();

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

})()