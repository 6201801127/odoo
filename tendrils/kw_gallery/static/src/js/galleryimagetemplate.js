odoo.define('kw_gallery_image', function (require) {
    "use strict";
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var QWeb = core.qweb;
    var session = require('web.session');
    var imageviewer = AbstractAction.extend({
        template: 'galleryimages',
        events: {
            "click .o_attachment_view": "_onAttachmentView",
            // "click .o_attachment_download": "_onAttachmentDownload",
            // "click .o_attachment_delete_cross": "_onDeleteAttachment",
            // "click .o_upload_attachments_button": "_onUploadAttachments",
            // "change .o_chatter_attachment_form .o_form_binary_form": "_onAddAttachment",
        },
        init :function(){
            this._super.apply(this, arguments);
        },

        _onAttachmentView: function (ev) {
            ev.stopPropagation();
            ev.preventDefault();
            // var activeAttachmentID = $(ev.currentTarget).data('id');
            // if (activeAttachmentID) {
            //     var attachmentViewer = new DocumentViewer(this, this.attachmentIDs, activeAttachmentID);
            //     attachmentViewer.appendTo($('body'));
            // }
            alert("View is called");
        },
    });
    core.action_registry.add('kw_gallery_image.imageviewer', imageviewer);
    });