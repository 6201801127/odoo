odoo.define('kw_appraisal.delete_button', function (require) {
    "use strict";

    var core = require('web.core');
    var _t = core._t;
    var ListRenderer = require('web.ListRenderer');
    var Dialog = require('web.Dialog');
    var RelationalFields = require('web.relational_fields');

    RelationalFields.FieldMany2Many.include({
        _onRemoveRecord: function (ev) {
            if (ev.data.operation) {
                ev.stopPropagation();
                var operation = ev.data.operation;
                this._setValue({
                    operation: operation,
                    ids: []
                });
            }
            else  {
                this._super(ev)
            }
        }
    });

    RelationalFields.FieldOne2Many.include({
        _onRemoveRecord: function (ev) {
            if (ev.data.operation) {
                ev.stopPropagation();
                var operation = ev.data.operation;
                this._setValue({
                    operation: operation,
                    ids: []
                });
            }
            else  {
                this._super(ev)
            }
        }
    });

    ListRenderer.include({
        events: _.extend({}, ListRenderer.prototype.events, {
            'click thead tr .o_list_record_delete_all_btn': '_onTrashHeadIconClick',
        }),
        _renderHeader: function (isGrouped) {
            var $thead = this._super(isGrouped);
            if (this.state.data.length > 0){
                var $icon = $('<button>', {class: 'fa fa-trash-o o_list_record_delete_all_btn', name: 'delete', 'aria-label': _t('Delete row ')});
                var $td = $('<td>', {class: 'o_list_record_delete'}).append($icon);
                if (this.addTrashIcon) {
                    $thead.children("tr").append($td)
                }
            }
            return $thead;
        },
        _onTrashHeadIconClick: function (event) {
            event.stopPropagation();
            var self = this;
            Dialog.confirm(this, _t("Are you sure to remove all items?"), {
                confirm_callback: function () {
                    self.trigger_up('list_record_remove', {operation: 'REPLACE_WITH', id: []});
                }
            });
        }

    });

});
