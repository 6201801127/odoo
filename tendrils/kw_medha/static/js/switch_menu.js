odoo.define('kw_medha.MedhaKMenu', function(require) {
    "use strict";
     var SystrayMenu = require('web.SystrayMenu');
     var Widget = require('web.Widget');
     var session = require('web.session');
     
    var ActionMenu = Widget.extend({
        template: 'systray_cloud.medha_icon',

         start: function() {
                    session.user_has_group('kw_medha.group_user_module_kw_medha').then(function(result) {
                    if (result) {
                        console.log("User belongs to the group");
                    } else {
                        console.log("User does not belong to the group");
                        var liElement = document.getElementById("medhak_id");
                        if (liElement) {
                            liElement.style.display = "none";
                        }
                    }
                });
            },

        events: {
            'click .medha_icon': 'onclick_myicon',
        },
        onclick_myicon: function () {
            window.open("/go-for-medha/", "_blank");
        }
     
    });
    ActionMenu.prototype.sequence = 100;
    SystrayMenu.Items.push(ActionMenu);//add icon to the SystrayMenu
    return ActionMenu;//return widget
});    