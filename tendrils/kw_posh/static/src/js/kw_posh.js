odoo.define('kw_posh.kw_posh', function (require) {
    'use strict';

    var core = require('web.core');
    var AbstractAction = require('web.AbstractAction');
    var NewAction = AbstractAction.extend({
        init: function (parent, context) {
            this._super(parent, context);
            this.renderModal();
        },
        renderModal: function () {
            var $modalContainer = $('<div class="modal fade" role="dialog"></div>');
            var $modalDialog = $('<div class="modal-dialog modal-lg"></div>');
            var $modalContent = $('<div class="modal-content"></div>');
            var $modalHeader = $('<div class="modal-header"></div>');
            var $modalBody = $('<div class="modal-body"></div>');
            var $modalFooter = $('<div class="modal-footer"></div>');

            var $modalTitle = $('<h4 class="modal-title"></h4>').text("POSH GUIDE");
            var $closeButton = $('<button type="button" class="close" data-dismiss="modal">&times;</button>');
            $modalHeader.append($modalTitle, $closeButton);

            var $iframe = $('<iframe src="/kw_posh/static/src/posh_2024.pdf" width="100%" height="600px"></iframe>');
            $modalBody.append($iframe);

            var $closeModalButton = $('<button type="button" class="btn btn-danger" data-dismiss="modal">Close</button>');
            $modalFooter.append($closeModalButton);

            $modalContent.append($modalHeader, $modalBody, $modalFooter);
            $modalDialog.append($modalContent);
            $modalContainer.append($modalDialog);

            $modalContainer.modal('show');
        }
    });

    core.action_registry.add('posh_client_action_tag', NewAction);
});
