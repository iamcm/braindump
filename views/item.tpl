
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
            tabfocus_elements: ":prev,:next"
        });

</script>
%end

%rebase base vd=vd, page=page, js=js