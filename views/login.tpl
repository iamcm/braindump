
<div class="container-fluid p10">
    
    %if vd.get('error'):
    <div class="alert alert-error">
        <button class="close" data-dismiss="alert">×</button>
        {{vd['error']}}
    </div>
    %end

    {{!vd['form']}}

    <a href="/auth/forgotten-password">Forgotten password?</a>

</div>

%rebase base_public
