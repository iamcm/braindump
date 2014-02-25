% for i in items:
<div class="item well">
    <div class="right">
        <a class="px10" href="/item/{{i._id}}/edit">edit</a>
        <a class="px10 deleteLink" entity="item" href="/item/{{i._id}}/delete">delete</a>
    </div>
    <div class="title bold">{{i.title}}</div>
    <span style="display:none">
        <hr />
        <div class="content">{{!i.content}}</div>
	    % if i.files:
	        <div class="py10">
			    % for f in i.files:
			    	<div>
			    		<a href="/userfiles/{{f.sysname}}">{{f.nicename}}</a>
			    	</div>
				% end
			</div>
		% end
    </span>
	
</div>
% end
