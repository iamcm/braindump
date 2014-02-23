
%def page():

{{!vd['form']}}



%end


%def js():
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

%rebase base vd=vd, page=page, js=js