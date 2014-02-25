
%def page():

{{!vd['form']}}

%end


%def css():
    <link href="/static/plupload/js/jquery.plupload.queue/css/jquery.plupload.queue.css" rel="stylesheet">
%end

%def js():
    <script type="text/javascript" src="/static/plupload/js/plupload.full.js"></script>
    <script type="text/javascript" src="/static/plupload/js/jquery.plupload.queue/jquery.plupload.queue.js"></script>
    <script type="text/javascript" src="/static/js/uploader.js"></script>
    <script type="text/javascript">

            tinymce.init({
                selector: "textarea",
                plugins: ["link"],
                menubar: false,
                toolbar: 'bold italic | link',
                statusbar: false,
                tabfocus_elements: ":prev,:next",
                force_br_newlines : true,
                force_p_newlines : false,
                forced_root_block : ''

            });

            $('#title').focus();

    </script>
%end

%rebase base vd=vd, page=page, js=js, css=css