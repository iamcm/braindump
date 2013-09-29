<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Braindump</title>

    <link href="/static/bootstrap/css/bootstrap.min.css" rel="stylesheet">
    <link href="/static/css/generic.css" rel="stylesheet">
    <link href="/static/css/site.css" rel="stylesheet">

</head>

<body>
    <div class="navbar navbar-fixed-top navbar-inverse" role="navigation">
        <div class="container">
            <div class="navbar-header">
                <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                </button>
                <a class="navbar-brand" href="/">Braindump</a>
            </div>
            <div class="collapse navbar-collapse">
                <ul class="nav navbar-nav">
                    <li><a href="/items">Items</a></li>
                    <li><a href="/tags">Tags</a></li>
                    <li><a href="/api-key">Api key</a></li>
                </ul>
            </div>
        </div>
    </div>

    <div class="container">

        %if defined('page'):
            %page()
        %else:
        <div class="row">
            <div class="col-xs-12 col-sm-9">

                <div class="well">
                    <form class="form-inline col-xs-10" action="/search/items">
                        <input type="text" name="name" id="search-input" class="form-control" placeholder="Search">
                    </form>

                    <div class="col-xs-2">
                        <a class="right btn btn-primary" href="/item">Add item</a>
                    </div>

                    <div class="clearfix"></div>
                </div>

                <div id="item-container">
                    %if 'items' in vd:
                        %include items.tpl items=vd['items']
                    %end
                </div>
            </div>

            <div class="col-xs-6 col-sm-3">
                <div class="well">
                    <ul class="nav">
                        % for t in vd['tags']:
                        <li><a href="/tag/{{t.slug}}">{{t.name}}</a></li>
                        % end
                    </ul>
                </div>
            </div>
        </div>
        %end

    </div>

    <script src="/static/js/jquery.js"></script>
    <script src="/static/bootstrap/js/bootstrap.min.js"></script>
    <script src="/static/tinymce/js/tinymce/tinymce.min.js"></script>
    <script src="/static/js/site.js"></script>
    %if defined('js'):
        %js()
    %end

</body>
</html>