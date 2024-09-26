/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : https://store.webkul.com/license.html/ */
importScripts('https://www.gstatic.com/firebasejs/3.7.4/firebase-app.js')
importScripts('https://www.gstatic.com/firebasejs/3.7.4/firebase-messaging.js')

/**
 * Push Notification Event Listener
 */
self.addEventListener('push', function(event) {
    var res_data = event.data.json().notification;

    event.waitUntil(
        self.registration.showNotification(res_data.title, {
            body : res_data.body,
            icon : res_data.icon,
            actions : [{
                action : res_data.click_action,
                title : "Explore"
            }],
        })
    );

});

/**
 * Push Notification Click Event Listener
 */
self.addEventListener('notificationclick', function (event) {
    var url = event.notification.actions[0].action;
    if (url) {
        event.notification.close();

        event.waitUntil(
            clients.matchAll({
                type: 'window'
            }).then(function (windowClients) {
                for (var i = 0; i < windowClients.length; i++) {
                  var client = windowClientss[i];
                  if (client.url == url && 'focus' in client)
                    return client.focus();
                }
                if (clients.openWindow) {
                    return clients.openWindow(url);
                }
            })
        );

    }
});
