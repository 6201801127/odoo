odoo.define('kw_dms_mixin.DigitalSign', function (require) {


    var resellerCode    = 113;
    var file_id         = '';
    var DeskSignObj     = _elk_desksignObj;
    var ajax            = require('web.ajax');   
    
   // window.addEventListener("load", function(){myObj._elk_initialize(mycallback);}, false);
    if(typeof window.addEventListener == "undefined")
        window.onload=function(){DeskSignObj._elk_initialize(mycallback);}
    else
       window.addEventListener("load", function(){DeskSignObj._elk_initialize(mycallback);}, false);

   
    function mycallback(apiName, status, params)
    {
       // console.log("inside call back function")
        
        // This is the API completion callback.
        if(apiName != "SignPDFInMemory")
            return; // No need to show results of other general calls
      
        var retVal = "";        

        if(status != "Success")
        {
            // Give an error message and stay on the same page
            alert("Certificate operation failed: " + status);          
        }
        else {

            if(typeof params.signed_file_content == "undefined")
                retVal = "";
            else if (params.signed_file_content){

                retVal = params.signed_file_content;               

                ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                    model   : 'kw_dms.file',
                    method  : 'save_signed_file',
                    args    : [[file_id]],
                    kwargs  : {
                        content: retVal,
                    },
                }).then(function (url) {
                    //console.log('returned ...')

                    alert("Digital Sign Completed !")
                    location.reload();
                   
                });
                

            }
        }
         
    }

     /**************START : Sample working code of client action****************/
       
        var core = require('web.core');
       
        var QWeb = core.qweb;
       
        var ControlPanelMixin   = require('web.ControlPanelMixin'); 
        var AbstractAction      = require('web.AbstractAction');
     
        var digitalSign = AbstractAction.extend(ControlPanelMixin,{
            
            template:'kw_dms.digi_sign',
            events: {
                "click .btn_digi_sign_proceed": "button_btn_digi_sign_proceed_clicked",
            },
            init: function(parent, params) {
                this._super(parent);              
               
                this.action_manager = parent;
                this.params         = params;

                file_id             = params.context['file_id']                
               
            },
            start: function() {
                //this.sign_status    = 0;
                this.$el.append(QWeb.render("kw_dms.digi_sign", {sign_status: 0}));
            },
            //this is call after Widget.init(parent), Widget.willStart()  and [Rendering]()
            button_btn_digi_sign_proceed_clicked: function() {

                //console.log("inside button_btn_digi_sign_proceed_clicked function")    
                var position = $("[name='radioPosition']:checked").val()
                if(typeof position == "undefined") 
                    position = 0

                this.preInvoke(position)
            },
           
            preInvoke: function (position) {

               // console.log("inside preInvoke function")
                if(!DeskSignObj._elk_initialized)
                {
                   
                    DeskSignObj._elk_initialize(mycallback);
                    window.setTimeout(this.signfile(position), 200);
                }
                else
                    this.signfile(position);

            },
            signfile: function (position) {

               //console.log(this.params.context['file_content'])

                file_content = this.params.context['file_content'] 

                DeskSignObj.SetSigningParametersEx("Digitally Signed", "", "", "SHA1");
                DeskSignObj.SetSigAppearanceParam(2,parseInt(position), ""); // 1- top, 0- buttom

                //elements  width  height  image-position   orientation   sig-text   x-margin   y-margin
                if(position == 1) //if top
                    DeskSignObj.ConfigSigBlock(255,200, 70, 2, 1, "Digitally signed by",20, 20);
                else if(position == 0) //if buttom
                    DeskSignObj.ConfigSigBlock(255,200, 70, 2, 1, "Digitally signed by",20, 600);
        
                DeskSignObj.SignPDFInMemory(file_content, true, 0, "", "", "", "", resellerCode);

                //pdf-data,signing-time,store-type, issued-to, issued-by, pfx-file, pwd , silent-mode, reseller-code
                
              
            },
                        
        });
       
        core.action_registry.add('digisign', digitalSign);


        /**************END : Sample working code of client action****************/


       
});
    