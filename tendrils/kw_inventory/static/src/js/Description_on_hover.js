// odoo.define('kw_inventory.Description_on_hover', function (require) {
//     "use strict";
//     var ListRenderer = require('web.ListRenderer');
//     ListRenderer.include({
//         events: _.extend({}, ListRenderer.prototype.events, {
//             'mouseover tbody tr td .o_field_widget': '_onHoverRecord_details',
//         }),
//         _onHoverRecord_details: function (event) {
//             var record_details =
//             $(event.currentTarget).tooltip({
//                 title: "Show Description on Hover",
//                 delay: 0,
//             }).tooltip('show');
//         }
//     });
// })
