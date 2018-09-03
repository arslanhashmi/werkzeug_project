import os
import redis
import urllib.parse
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.utils import redirect

from jinja2 import Environment, FileSystemLoader


def is_valid_input(weight, height):
    return weight.isdigit() and height.isdigit()


def calculate_bmi(weight, height):
    return int(weight) / (int(height) ** 2)


def get_hostname(url):
    return urllib.parse.urlparse(url).netloc


class BMIApp(object):

    def __init__(self, config):
        self.redis = redis.Redis(config['redis_host'], config['redis_port'])
        template_path = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_path),
                                     autoescape=True)
        self.jinja_env.filters['hostname'] = get_hostname

        self.url_map = Map([
            Rule('/', endpoint='index'),
            Rule('/show/<bmi_id>', endpoint='bmi_details')
        ])

    def on_index(self, request):
        error, url = None, ''
        if request.method == 'POST':
            weight = request.form['weight']
            height = request.form['height']
            if not is_valid_input(weight, height):
                error = 'Please enter a valid height and/or weight'
            else:
                bmi_id = self.insert_values(weight, height)
                return redirect(f'/show/{bmi_id}')
        return self.render_template('bmi_calculate.html', error=error, url=url)

    def on_bmi_details(self, request, bmi_id):
        bmi = self.redis.get(f'bmi:{bmi_id}')
        if bmi is None:
            raise NotFound()
        return self.render_template(
            'bmi_details.html', bmi=bmi.decode(),
            bmi_id=bmi_id
        )

    def error_404(self):
        response = self.render_template('404.html')
        response.status_code = 404
        return response

    def insert_values(self, weight, height):
        bmi_id = self.redis.get(f'bmi:{weight}-{height}')
        if bmi_id is not None:
            return bmi_id
        bmi_id = self.redis.incr('last-bmi-id')
        self.redis.set(f'bmi:{bmi_id}', calculate_bmi(weight, height))
        self.redis.set(f'bmi:{weight}-{height}', bmi_id)
        return bmi_id

    def render_template(self, template_name, **context):
        template = self.jinja_env.get_template(template_name)
        return Response(template.render(context), mimetype='text/html')

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, 'on_' + endpoint)(request, **values)
        except NotFound:
            return self.error_404()
        except HTTPException as e:
            return e

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


def create_app(redis_host='localhost', redis_port=6379, with_static=True):
    app = BMIApp({
        'redis_host': redis_host,
        'redis_port': redis_port
    })
    if with_static:
        app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
            '/static': os.path.join(os.path.dirname(__file__), 'static')
        })
    return app


if __name__ == '__main__':
    from werkzeug.serving import run_simple

    app = create_app()
    run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)
