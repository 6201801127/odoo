odoo.define('kw_auction.ListControllerButton', function (require) {
    "use strict";

    var core = require('web.core');
    var ListController = require('web.ListController');
    var KanbanRecord = require('web.KanbanRecord');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var ajax = require('web.ajax');
    var _t = core._t;

    ListController.include({
        renderButtons: function ($node) {
            this._super.apply(this, arguments);
            if (this.modelName === 'kw_auction_report' && this.viewType === 'list') {
                this.$buttons.on('click', '.oe_action_download_format', function () {
                    var base_url = window.location.origin || window.location.protocol + '//' + window.location.host;
                    var result_url = base_url + '/download-xls-format/';
                    window.location.href = result_url;
                });
            }
        },
    });

    // Extend KanbanRecord to disable image preview on click
    // KanbanRecord.include({
    //     start: function () {
    //         this._super.apply(this, arguments);
    //         this._disableImagePreview();
    //     },

    //     _disableImagePreview: function () {
    //         this.$el.find('img').off('click').on('click', function (event) {
    //             event.stopPropagation(); // Prevents the event from bubbling up
    //             event.preventDefault(); // Prevents the default action (image preview)
    //         });
    //     },
    // });

    return {
        ListController: ListController,
        // KanbanRecord: KanbanRecord,
    };
});
