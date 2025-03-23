(function(){
    //To-Do: Clean this up
    console.log("Notifications loaded");

    //Create notification div
    const me = document.currentScript;
    me.insertAdjacentHTML('beforebegin', `<div class="notifications" id="notifications"></div>`);

    const close_button_template = `
        <svg viewBox="0 0 24 24">
            <g>
                <path d="M14.8,12l3.6-3.6c0.8-0.8,0.8-2,0-2.8c-0.8-0.8-2-0.8-2.8,0L12,9.2L8.4,5.6c-0.8-0.8-2-0.8-2.8,0   c-0.8,0.8-0.8,2,0,2.8L9.2,12l-3.6,3.6c-0.8,0.8-0.8,2,0,2.8C6,18.8,6.5,19,7,19s1-0.2,1.4-0.6l3.6-3.6l3.6,3.6   C16,18.8,16.5,19,17,19s1-0.2,1.4-0.6c0.8-0.8,0.8-2,0-2.8L14.8,12z" fill="currentColor"/>
            </g>
        </svg>
    `;

    const notifications_parent = document.getElementById('notifications');

    function createNotification(text, time) {
        let general_timeout;

        const notification = document.createElement("div");
        notification.classList.add("notification");

        const notification_inner = document.createElement("div");
        notification_inner.classList.add("notification__inner");
        notification_inner.innerHTML = text;

        const notification_close = document.createElement("button");
        notification_close.classList.add("notification__close");
        notification_close.insertAdjacentHTML('afterbegin', close_button_template);
        notification_close.onclick = function (e) {
            let current_nofitication = e.target.parentNode;
            current_nofitication.style.opacity = 0;

            setTimeout(() => {
                clearTimeout(general_timeout);
                current_nofitication.remove();
            }, 500);
        }

        notification.append(notification_close);
        notification.append(notification_inner);

        if (time > -1) {
            general_timeout = setTimeout(() => {
                notification.style.opacity = 0;

                setTimeout(() => {
                    notification.remove();
                }, 500);
            }, time);
        }

        return notification;
    }

    window.notify = (message, time = 5000) => {
        let new_notification = createNotification(message, time);

        notifications_parent.append(new_notification);
    };
})();