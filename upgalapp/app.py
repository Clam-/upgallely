from starlette.config import Config
from starlette.applications import Starlette
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from starlette.datastructures import CommaSeparatedStrings, Secret, URL
import uvicorn
import json
from authlib.integrations.starlette_client import OAuth

config = Config('.env')
DEBUG = config('DEBUG', cast=bool, default=False)
DATABASE_URL = config('DATABASE_URL', cast=URL)
SECRET_KEY = config('SECRET_KEY', cast=Secret)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=CommaSeparatedStrings)
TEMPLATE_DIR = config('TEMPLATES')
STATIC_DIR = config('STATIC')

templates = Jinja2Templates(directory=TEMPLATE_DIR)

app = Starlette(debug=DEBUG)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.mount('/static', StaticFiles(directory=STATIC_DIR), name='static')

##
## Main logic?
##
@app.route('/admin')
async def homepage(request):
    user = request.session.get('user')
    data = json.dumps(user)
    return templates.TemplateResponse("index.jinja2", {"request": request, "user": data})
@app.route('/')
async def homepage(request):
    user = request.session.get('user')
    data = json.dumps(user)
    return templates.TemplateResponse("no.jinja2", {"request": request, "user": data})

##
## Auth
##
oauth = OAuth(config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)
@app.route('/login')
async def login(request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)
@app.route('/auth')
async def auth(request):
    token = await oauth.google.authorize_access_token(request)
    user = await oauth.google.parse_id_token(request, token)
    request.session['user'] = dict(user)
    return RedirectResponse(url='/admin')
@app.route('/logout')
async def logout(request):
    request.session.pop('user', None)
    return RedirectResponse(url='/admin')

##
## Error handling
##
@app.route('/error')
async def error(request):
    """
    An example error. Switch the `debug` setting to see either tracebacks or 500 pages.
    """
    raise RuntimeError("Oh no")
@app.exception_handler(404)
async def not_found(request, exc):
    """
    Return an HTTP 404 page.
    """
    return templates.TemplateResponse("404.jinja2", {"request": request}, status_code=404)
@app.exception_handler(500)
async def server_error(request, exc):
    """
    Return an HTTP 500 page.
    """
    return templates.TemplateResponse("500.jinja2", {"request": request}, status_code=500)


if __name__ == "__main__":
    uvicorn.run("app:app", host='0.0.0.0', port=8000, reload=DEBUG)
