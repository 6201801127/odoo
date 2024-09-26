odoo.define('base_exception_and_approval.approvals_list_kanban', function(require) {
    'use strict';

    var core = require('web.core');
    var session = require('web.session');
    var KanbanController = require("web.KanbanController");
    var KanbanColumn = require("web.KanbanColumn");
    var KanbanRecord = require("web.KanbanRecord");
    var ListController = require("web.ListController");

    var _t = core._t;


    KanbanColumn.include({
        /**
         * @override
         */
        init: function () {
            this._super.apply(this, arguments);
            if (this.modelName === "approvals.list") {
                this.draggable = false;
            }
        },
    });
 });