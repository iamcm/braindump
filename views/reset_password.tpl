
<div class="container-fluid p10">
    
    %if vd.get('error'):
    <div class="alert alert-error">
        <button class="close" data-dismiss="alert">×</button>
        {{vd['error']}}
    </div>
    %end

    <form autocomplete="off" class="form-horizontal" method='POST' action="" >
        
		<input type="hidden" name="key" value="{{vd['key']}}" />

        <div class="control-group">
            <label class="control-label" for="password">New password</label>
            <div class="controls">
                <input type="password" class="input-xlarge" name="password" id="password" />
            </div>
        </div>

        <div class="control-group">
            <label class="control-label" for="password2">Confirm password</label>
            <div class="controls">
                <input type="password" class="input-xlarge" name="password2" id="password2" />
            </div>
        </div>
        
        <div class="control-group">
            <div class="controls">
                <button type="submit" class="btn">Reset password</button>
            </div>
        </div>
        
    </form>
</div>

%rebase base_public vd=vd