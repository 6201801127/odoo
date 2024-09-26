odoo.define('kw_vocalize.VocalizeMenu', function(require) {
    "use strict";
     var SystrayMenu = require('web.SystrayMenu');
     var Widget = require('web.Widget');
     
    var ActionMenu = Widget.extend({
        template: 'systray_cloud.myicon',//provide the template name
        events: {
            'click .my_icon': 'onclick_myicon',
        },
        onclick_myicon : function(){
            window.location.href = "/vocalize-voting/"
        }
     
    });
    ActionMenu.prototype.sequence = 100;
    SystrayMenu.Items.push(ActionMenu);//add icon to the SystrayMenu
    return ActionMenu;//return widget
});    