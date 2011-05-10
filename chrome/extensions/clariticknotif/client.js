var pending_notifications = [];
var django_notifications_url = JSON.parse(localStorage.djangoURL);
var django_notifications_get_url = django_notifications_url + 'get/';
var django_notifications_check_url = django_notifications_url + 'is_authenticated/';
var is_loggedin = false;
var current_username = null;
var n_socket;

const CHECK_LOGIN_TIMEOUT = 60 * 1000; /* Every minute */

/* This will create a timeouting notifications (in seconds) */
function createNotification(image, title, content, timeout)
{
    var n = webkitNotifications.createNotification(image, title, content);
    var notification_timeout_callback = function(notification) 
    {
        return function() 
        {
            notification.cancel();
        };
    };
    setTimeout(notification_timeout_callback(n), timeout * 1000);
    return n;
}

function createHTMLNotification(url, timeout)
{
    var n = webkitNotifications.createHTMLNotification(url);
    var notification_timeout_callback = function(notification) 
    {
        return function() 
        {
            notification.cancel();
        };
    };
    setTimeout(notification_timeout_callback(n), timeout * 1000);
    return n;    
}

function show() 
{
    var notification = webkitNotifications.createHTMLNotification(django_notifications_get_url + '1');
    notification.show();
    var errorCallback = function (notification) 
    {
        return function(e) {
            console.log("Error showing notification: " + e);
            pending_notifications.pop(notification);
        };
    };
    var onDisplayCallback = function (notification) 
    {
        return function() {
            console.log("Shown notification: " + notification);
            pending_notifications.pop(notification);
        };
    };
    var onCloseCallback = function (notification) 
    {
        return function() {
            console.log("Closed notification: " + notification);
            pending_notifications.pop(notification);
        };
    };
    notification.onerror = errorCallback(notification);
    notification.ondisplay = onDisplayCallback(notification);
    notification.onclose = onCloseCallback(notification);
    pending_notifications.push(notification);
}

/* Check if the user is logged in */
function check_auth(first_time)
{
    var xhr = new XMLHttpRequest();
    xhr.open("GET", django_notifications_check_url, true);
    xhr.onreadystatechange = function()
    {
        if (xhr.readyState == 4) 
        {
            // JSON.parse does not evaluate the attacker's scripts.
            var resp = xhr.responseText;
            if (resp != "0")
            {
                /* Login ok */
                current_username = resp;
                is_loggedin = true;
                if (first_time)
                {
                    var notification = createNotification(null, "Sucessfully registered: "+current_username, current_username + ": logged in. You will receive notifications.", 3);
                    setup_websocket();
                    notification.show();
                }
            } else {
                is_loggedin = false;
                current_username = null;
                var notification = createNotification(null, "Not logged in", "You are not loggedin. You will not receive notifications :(", 10);
                notification.show();
            }
        }
    }
    xhr.send();
}

function setup_websocket()
{
    if (! is_loggedin || ! current_username)
    {
        console.error("Not possible to setup websocket: login required.");
        return null;
    }
    var host = JSON.parse(localStorage.wsHost);
    var port = JSON.parse(localStorage.wsPort);
    var isSecure = JSON.parse(localStorage.isSecure);
    
    /* Initialize websocket */
    n_socket = new io.Socket(host, {port: port, secure: isSecure});
    n_socket.connect();
    n_socket.on('connect', function(evt) 
        {
            console.log("Sending register.");
            n_socket.send(JSON.stringify({action: "register", username: current_username}));
        }
    );
    n_socket.on('message', function(evt) 
        {
            /* Ack ? */
            if (! evt || evt == "ack")
            {
                console.log("ack received.");
                return;
            }
            
            console.log("Message received: "+evt);
            try {
                var data = JSON.parse(evt);
            } catch (e) {
                console.error("Unable to decode message");
                return;
            }
            console.log("action:" + data.action);
            if (data.action && data.action == "notification")
            {
                createHTMLNotification(django_notifications_get_url + data.id_notification, 
                    getOption("notificationTimeout")).show();
            }
        }
    );
    n_socket.on('error', function(evt)
        {
            console.error("Error: "+evt);
        }
    );
}

if (!localStorage.isInitialized)
    resetSettings();

if (JSON.parse(localStorage.isActivated))
{
    setInterval("check_auth()", CHECK_LOGIN_TIMEOUT);
    check_auth(true); /* Check just now */
}