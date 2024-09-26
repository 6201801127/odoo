odoo.define('kw_recruitment.render_Sidebar', function (require) {
"use strict";

var core = require('web.core');
var ListController = require('web.ListController');
var rpc = require('web.rpc');
var session = require('web.session');
var _t = core._t;
var Dialog = require('web.Dialog');
var Sidebar = require('web.Sidebar');

ListController.include({
    renderSidebar: function ($node) {
        var self = this;
        if (this.hasSidebar) {
            var other = [{
                label: _t("Export"),
                callback: this._onExportData.bind(this)
            }];
            // if (this.archiveEnabled) {
            //     other.push({
            //         label: _t("Archive"),
            //         callback: function () {
            //             Dialog.confirm(self, _t("Are you sure that you want to archive all the selected records?"), {
            //                 confirm_callback: self._onToggleArchiveState.bind(self, true),
            //             });
            //         }
            //     });
            //     other.push({
            //         label: _t("Unarchive"),
            //         callback: function () {
            //             Dialog.confirm(self, _t("Are you sure that you want to unarchive all the selected records?"), {
            //                 confirm_callback: self._onToggleArchiveState.bind(self, false),
            //             });
            //         }
            //     });
            // }
            if (this.is_action_enabled('delete')) {
                other.push({
                     label: _t('Delete'),
                    callback: this._onDeleteSelectedRecords.bind(this)
                });
            }
            this.sidebar = new Sidebar(this, {
                editable: this.is_action_enabled('edit'),
                env: {
                    context: this.model.get(this.handle, {raw: true}).getContext(),
                    activeIds: this.getSelectedIds(),
                    model: this.modelName,
                },
                actions: _.extend(this.toolbarActions, {other: other}),
            });
            this.sidebar.appendTo($node);

            this._toggleSidebar();
        }
    },

});

return ListController;

});
