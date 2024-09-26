odoo.define('kw_employee_social_image.imagecrop', function (require) {
    'use strict';
    var ajax = require('web.ajax');

    var _URL = window.URL;
    $("#socialPhoto").change(function (e) {
        var file, img;
        if ((file = this.files[0])) {
            img = new Image();
            img.onload = function () {
                if (this.width > 96 || this.height > 63){
                    console.log("Width:" + this.width + "   Height: " + this.height);
                }
            };
            img.src = _URL.createObjectURL(file);
        }
    });
    var image_crop = {
        init: function (){
            image_crop.imageCropWeb();
        },

        imageCropWeb: function(){
            var $modal = $('#modal');
            var image = document.getElementById('image');

            // var cropper;
            // $("body").on("change", ".social_image", function(e) {
            //     var files = e.target.files;
            //     console.log(files)
            //     var done = function(url) {
            //         image.src = url;
            //         $modal.modal('show');
            //     };
            //     var reader;
            //     var file;
            //     // var url;
            //     if (files && files.length > 0) {
            //         file = files[0];
            //         if (URL) {
            //             done(URL.createObjectURL(file));
            //         } else if (FileReader) {
            //             reader = new FileReader();
            //             reader.onload = function(e) {
            //                 done(reader.result);
            //             };
            //             reader.readAsDataURL(file);
            //         }
            //     }
            // });
            // $modal.on('shown.bs.modal', function() {
            //     image_crop.cropper = new Cropper(image, {
            //         aspectRatio: 32 / 21,
            //         viewMode: 2,
            //         preview: '.preview',
            //         dragCrop: false,
            //         cropBoxMovable: true,
            //         cropBoxResizable: true,
            //         minCropBoxWidth: 96,
            //         minCropBoxHeight: 63,
            //         dragMode: 'move',
            //     });
            // }).on('hidden.bs.modal', function() {
            //     image_crop.cropper.destroy();
            //     image_crop.cropper = null;
            // });
            $("#btn_submit").click(function(event) {
                var fileUpload = document.getElementById("socialPhoto");
                console.log(fileUpload.files[0]);
                if(typeof fileUpload.files[0] === 'undefined'){
                    swal({ title:"Error !", text: "Please select an image to upload.", type: "error", confirmButtonText:'Okay' });
                    return false;
                }
                var reader = new FileReader();
                reader.readAsDataURL(fileUpload.files[0]);
                reader.onload = function (e) {
                    var image = new Image();
                    image.src = e.target.result;
                    image.onload = function () {
                        var height = this.height;
                        var width = this.width;
//                        console.log("Width:" + width + " Height: " + height);
//                        if (height > 63 || width > 96) {
//                            swal({ title:"Error !", text: "Please upload image with Width: 96px and Height: 63px only.", type: "error", confirmButtonText:'Okay' });
//                            return false;
//                        }else{
                            var base64data = reader.result;
                            ajax.jsonRpc("/candid-image/submit-image", 'call', {'socialPhoto' :base64data})
                                .then(function (response) {
                                    console.log(response);
                                    window.location.href = response.url
                                });
//                        }
                        return false;
                    };
                // var reader = new FileReader();
                // reader.readAsDataURL(fileUpload.files[0]);
                // reader.onloadend = function() {
                //     var base64data = reader.result;

                //     ajax.jsonRpc("/candid-image/submit-image", 'call', {'socialPhoto' :base64data})
                //         .then(function (response) {
                //             console.log(response);
                //             window.location.href = response.url
                //             //alert("Crop image successfully uploaded");
                //         });
                    // console.log(base64data);
                    // $('.final-preview').html("<img scr='"+base64data+"'/>");

                }
                // image_crop.canvas = image_crop.cropper.getCroppedCanvas({
                //     width: 96,
                //     height: 63,
                //     imageSmoothingQuality : "high",
                //     imageSmoothingEnabled : true,
                // });
                // image_crop.canvas.toBlob(function(blob) {
                //     image_crop.url = URL.createObjectURL(blob);
                //     var fileUpload = document.getElementById("fileUpload");
                //     var reader = new FileReader();
                //     reader.readAsDataURL(fileUpload.files[0]);
                //     reader.onloadend = function() {
                //         var base64data = reader.result;

                //         ajax.jsonRpc("/candid-image/submit-image", 'call', {'socialPhoto' :base64data})
                //             .then(function (response) {
                //                 console.log(response);
                //                 window.location.href = response.url
                //                 //alert("Crop image successfully uploaded");
                //             });
                //         // console.log(base64data);
                //         // $('.final-preview').html("<img scr='"+base64data+"'/>");

                //     }

                // });
            });
            
        },
    };
   

    $(function(){
        image_crop.init();
    });
});


