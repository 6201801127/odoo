odoo.define('kw_onboarding_process.kwonboard_indentification_validation', function (require) {
    'use strict';
    $.validator.setDefaults({ ignore: '' });
    var Identity = {
        dateFormat: 'dd-mm-yyyy',
        // 'yyyy-mm-dd'
        init: function(){
            this.validation();
            this.dateRestrict('0');
            this.dateRestrictdl('0');
            $('select').select2();
            $('[data-rel="tooltip"]').tooltip();

            $('#idtable').on('click', ".clear", function() {
                $(this).parents('tr').find("input[type=text],input[type=file],input[type=hidden]").val("");
                $(this).parents('tr').find("select").val("");
                $(this).parents('tr').find("span").text("");
                $(this).parents('tr').find("label").text("");
            });
            function disableBack() { window.history.forward() }

            window.onload = disableBack();
            window.onpageshow = function(evt) { if (evt.persisted) disableBack() }
            $(document).on("keydown keyup", "input[type=text]", function() {
                var $el = $(this);
                var val = $.trim( $el.val() ) || "";
                if (this["name"] === "txtpassport") {//PASSPORT
                    val = val.replace(/[^A-Z0-9\s]/gi, '');
                } else if (this["name"] === "txtpan") {//PAN
                    val = val.replace(/[^A-Z0-9\s]/gi, '');
                } else if (this["name"] === "txtaadhaar") {//AADHAAR
                    val = val.replace(/[^0-9\s]/gi, '');
                } else if (this["name"] === "txtdl") {//DL
                    val = val.replace(/[^A-Z0-9\s]/gi, '');
                } else if (this["name"] === "txtvoterid") {//Voter ID
                    val = val.replace(/[^A-Z0-9\s]/gi, '');
                }
                $el.val( val );
            });
            
            // on change of file
            $(document).on('change', ".clsfrmfile", function(){     
                var _el         = $(this);
                var filename    = _el.val();
                var $file       = _el.closest('td').find(".file-upload");
                var $noFile     = _el.closest('td').find(".file-select-name");
                var ddlFileName = _el.closest('td').find(".txt-filename");

               
                var ddlHdnFileName = _el.closest('td').find('input[type=hidden]')

                if (/^\s*$/.test(filename)) {

                    $file.removeClass('active');
                    $noFile.text("No file chosen...");
                    ddlFileName.html("");
                    ddlHdnFileName.val('');

                } else {

                    $file.addClass('active');
                    $noFile.text(filename.replace("C:\\fakepath\\", ""));
                    ddlFileName.html(filename.replace("C:\\fakepath\\", ""));
                    
                    ddlHdnFileName.val(filename.replace("C:\\fakepath\\", ""));
                }
            })


        },
        dateRestrict: function(cnt){
            var from = $("#passdtdoi").datepicker({
                minDate: new Date(1954, 1 - 1, 1), 
                maxDate: '0d', 
                dateFormat: 'dd-M-yy',
                changeMonth: true,
                changeYear: true,
                yearRange: "-18: + new Date().getFullYear()"
            })
            .on("change", function() {
                to.datepicker('option', 'minDate', Identity.getDate(this));
            }),
            to = $("#passdtdoe").datepicker({
                minDate: '0d', 
                dateFormat: 'dd-M-yy',
                changeMonth: true,
                changeYear: true,
                yearRange: "new Date().getFullYear() : +18"
            })
            .on("change", function() {
                from.datepicker('option', 'maxDate', Identity.getDate(this));
            });
        },
        dateRestrictdl: function(cnt){
            var from = $( "#dldtdoi" ).datepicker({
                minDate: new Date(1954, 1 - 1, 1), 
                maxDate: '0d', 
                dateFormat: 'dd-M-yy',
                changeMonth: true,
                changeYear: true,
                yearRange: "-18: + new Date().getFullYear()"
            })
            .on( "change", function() {
                to.datepicker("setStartDate", Identity.getDate(this));
            }),
            to = $( "#dldtdoe" ).datepicker({
                dateFormat: 'dd-M-yy',
                changeMonth: true,
                changeYear: true,
                yearRange: "new Date().getFullYear() : +18"
            })
            .on( "change", function() {
                from.datepicker("setEndDate", Identity.getDate(this));
            });
            $("#dldtdoi").datepicker("option", "showAnim", "slideDown");
            $("#dldtdoe").datepicker("option", "showAnim", "slideDown");

        },
        getDate: function( element ) {
            var date;
            try {
                date = $(element).datepicker('getDate');
            } catch( error ) {
                date = null;
            }
            return date;
        },
        validation: function(){
            $.validator.messages.accept     = 'File must be .jpeg,.png, .pdf format';
            $.validator.messages.filesize   = 'File size must be less than 4 MB';          
            
            $.validator.addClassRules({               
                clsfrmfile: {
                   /* required    : function(element) {
                            var hdnfile = $(element).closest('td').find('input[type=hidden]')
                            var otherelms = $(element).closest('tr').find('.likert-field')
                            var blankfield = 0;

                            $(element).closest('tr').find('.likert-field').each(function(){
                                if($(this).val()!='')
                                    blankfield++
                            });
                            return $(hdnfile).val()=='' && blankfield>0;
                      },*/
                    accept      : "image/png,image/jpeg,image/jpg,application/pdf",
                    filesize    : 4194304
                },                 
              });


            $("form#frm_identification").validate({
                // Specify validation rules
                rules: {
                    txtaadhaar:{
                        required: true,
                    },
                    txtpan: {
                        required: true,
                    },
                },
                // Specify validation error messages
                messages: {
                    txtaadhaar: "Please enter Aadhar No",
                    txtpan: "Please enter PAN No",
                },

                // Make sure the form is submitted to the destination defined
                // in the "action" attribute of the form when valid
                submitHandler: function (form4) {
                    form4.submit();
                },
                errorElement: "div",
                highlight: function (element) {
                    $(element).css('background', '#ffdddd');
                },
                // Called when the element is valid:
                unhighlight: function (element) {
                    $(element).css('background', '#ffffff');
                },
            });
        },
    };
    $(function(){
        Identity.init();
    }); //end of ready function
});

$('.clsfrmfile').bind('change', function () {
    var _el = $(this);
    var filename = _el.val();
    var $file = _el.closest('td').find(".file-upload");
    var $noFile = _el.closest('td').find("#noFile");
    var ddlFileName = _el.closest('td').find("span[id^='ddlFileName']");
    if (/^\s*$/.test(filename)) {
        $file.removeClass('active');
        $noFile.text("No file chosen...");
        ddlFileName.html("");
    } else {
        $file.addClass('active');
        $noFile.text(filename.replace("C:\\fakepath\\", ""));
        ddlFileName.html(filename.replace("C:\\fakepath\\", ""));
    }
  });