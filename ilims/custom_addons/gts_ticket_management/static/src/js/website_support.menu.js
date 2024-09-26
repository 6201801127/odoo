odoo.define("website_support.menu", function (require) {
"use strict";

var publicWidget = require('web.public.widget');

publicWidget.registry.SupportTicketMenu = publicWidget.Widget.extend({
    selector: '.team_menu',
    start: function () {
        var pathname = $(window.location).attr("pathname");
        var $links = this.$('li a');
        if (pathname !== "/support/") {
            $links = $links.filter("[href$='" + pathname + "']");
        }
        $links.first().closest("li").addClass("active");

        return this._super.apply(this, arguments);
    },
});
});
