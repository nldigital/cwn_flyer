from flask_assets import Bundle

common_css = Bundle(
        Bundle(
            'css/vendor/bootstrap.min.css',
            'css/vendor/font-awesome.min.css',
            'css/vendor/Raleway.css',
            'css/main.css',
            filters='cssmin'),
        output='public/css/common.css')

common_js = Bundle(
        'js/vendor/bootstrap.min.js',
        'js/vendor/jquery-3.1.1.slim.min.js',
        'js/vendor/tether.min.js',
        Bundle(
            'js/main.js',
            filters='jsmin'
            ),
        output='public/js/common.js'
        )

