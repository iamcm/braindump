// Convert divs to queue widgets when the DOM is ready
    $("#file").after('<div id="uploader"></div>');
    $("#file").remove();

    var files = 0;

    var uploader = $("#uploader").pluploadQueue({
        // General settings
        runtimes : 'html5,flash',
        url : '/upload',
        max_file_size : '10mb',
        //chunk_size : '1mb',
        unique_names : true,
        multipart_params : {},
        // Resize images on clientside if we can
        //resize : {width : 320, height : 240, quality : 90},

        // Flash settings
        flash_swf_url : '/static/plupload/js/plupload.flash.swf',

        // PreInit events, bound before any internal events
        /*preinit : {
            UploadFile: function(up, file) {
                up.settings.multipart_params = {"catId":$('#id_category option:selected').val()};
            }
        },*/

        init : {
            FilesAdded: function(){
                files += 1;
            },

            FilesRemoved: function(){
                files -= 1;
            },

            UploadComplete: function(up) {
                files = 0;
                $('form').submit();
            }
        }
    });

    $('form').on('submit', function(ev){
        if(files > 0){
            ev.preventDefault();
            uploader.pluploadQueue().start();
        }
    });