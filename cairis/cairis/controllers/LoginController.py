import cherrypy
import cherrypy.lib.cptools

__author__ = 'Robin Quetin'


class LoginController(object):
    exposed = True

    def GET(self):
        cherrypy.response.headers['Content-Type'] = 'text/html'
        return '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title>Login</title>
</head>
<body>
    <p>
        <form action="." method="post" enctype="text/plain">
            <input type="submit" value="Log in" />
        </form>
    </p>
</body>
</html>'''

    def POST(self):
        cherrypy.session['IsLoggedIn'] = 1
        return 'It works! You should be logged in now!'