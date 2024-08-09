import os
import time
from waitress import serve
from functools import wraps

from flask import Flask, send_from_directory, redirect, url_for, request, jsonify, make_response, abort
from flask_login import LoginManager, current_user, login_user
from flask_restx import Api

from src.manager.UserManager import UserManager
from src.service.ModelStore import ModelStore
from src.service.TemplateRenderer import TemplateRenderer
from src.controller.PlayerController import PlayerController
from src.controller.SlideController import SlideController
from src.controller.ContentController import ContentController
from src.controller.FleetNodePlayerController import FleetNodePlayerController
from src.controller.FleetNodePlayerGroupController import FleetNodePlayerGroupController
from src.controller.PlaylistController import PlaylistController
from src.controller.AuthController import AuthController
from src.controller.SysinfoController import SysinfoController
from src.controller.SettingsController import SettingsController
from src.controller.CoreController import CoreController
from src.constant.WebDirConstant import WebDirConstant
from src.exceptions.HttpClientException import HttpClientException
from plugins.system.CoreApi.exception.ContentPathMissingException import ContentPathMissingException


class WebServer:

    def __init__(self, kernel, model_store: ModelStore, template_renderer: TemplateRenderer):
        self._app = None
        self._api = None
        self._login_manager = None
        self._kernel = kernel
        self._model_store = model_store
        self._template_renderer = template_renderer
        self._debug = self._model_store.config().map().get('debug')
        self.setup()

    @property
    def api(self) -> Api:
        return self._api

    def get_max_upload_size(self):
        return self._model_store.variable().map().get('slide_upload_limit').as_int() * 1024 * 1024

    def run(self) -> None:
        serve(
            self._app,
            host=self._model_store.config().map().get('bind'),
            port=self._model_store.config().map().get('port'),
            threads=100,
            max_request_body_size=self.get_max_upload_size(),
        )

    def reload(self) -> None:
        self.setup()

    def setup(self) -> None:
        self._setup_flask_app()
        self._setup_web_globals()
        self._setup_web_errors()
        self._setup_web_controllers()
        self._setup_api()

    def get_app(self):
        return self._app

    def get_template_dir(self) -> str:
        return "{}/{}".format(self._kernel.get_application_dir(), WebDirConstant.FOLDER_TEMPLATES)

    def get_static_dir(self) -> str:
        return "{}/{}".format(self._kernel.get_application_dir(), WebDirConstant.FOLDER_STATIC)

    def get_web_dir(self) -> str:
        return "{}/{}/{}".format(self._kernel.get_application_dir(), WebDirConstant.FOLDER_STATIC, WebDirConstant.FOLDER_STATIC_WEB_ASSETS)

    def get_plugin_static_dst_dir(self, plugin_id: str) -> str:
        return "{}/{}/{}".format(self.get_web_dir(), WebDirConstant.FOLDER_PLUGIN_STATIC_DST, plugin_id)

    def _setup_flask_app(self) -> None:
        self._app = Flask(
            __name__,
            template_folder=self.get_template_dir(),
            static_folder=self.get_static_dir(),
        )

        self._app.config['UPLOAD_FOLDER'] = "{}/{}".format(WebDirConstant.FOLDER_STATIC, WebDirConstant.FOLDER_STATIC_WEB_UPLOADS)
        self._app.config['MAX_CONTENT_LENGTH'] = self.get_max_upload_size()
        self._app.config['ERROR_404_HELP'] = False

        self._setup_flask_login()

        if self._debug:
            self._app.config['TEMPLATES_AUTO_RELOAD'] = True

    def _setup_flask_login(self):
        self._app.config['SECRET_KEY'] = self._model_store.config().map().get('secret_key')
        self._login_manager = LoginManager()
        self._login_manager.init_app(self._app)
        self._login_manager.login_view = 'login'

        @self._login_manager.user_loader
        def load_user(user_id):
            return self._model_store.user().get(user_id)

    def is_auth_enabled(self) -> bool:
        return self._model_store.variable().map().get('auth_enabled').as_bool()

    def auth_required(self, f):
        def decorated_function(*args, **kwargs):
            if not self.is_auth_enabled():
                return f(*args, **kwargs)

            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            return f(*args, **kwargs)

        return decorated_function

    def _setup_web_controllers(self) -> None:
        CoreController(self._kernel, self, self._app, self.auth_required, self._model_store, self._template_renderer)
        PlayerController(self._kernel, self, self._app, self.auth_required, self._model_store, self._template_renderer)
        SlideController(self._kernel, self, self._app, self.auth_required, self._model_store, self._template_renderer)
        ContentController(self._kernel, self, self._app, self.auth_required, self._model_store, self._template_renderer)
        SettingsController(self._kernel, self, self._app, self.auth_required, self._model_store, self._template_renderer)
        SysinfoController(self._kernel, self, self._app, self.auth_required, self._model_store, self._template_renderer)
        FleetNodePlayerController(self._kernel, self, self._app, self.auth_required, self._model_store, self._template_renderer)
        FleetNodePlayerGroupController(self._kernel, self, self._app, self.auth_required, self._model_store, self._template_renderer)
        PlaylistController(self._kernel, self, self._app, self.auth_required, self._model_store, self._template_renderer)
        AuthController(self._kernel, self, self._app, self.auth_required, self._model_store, self._template_renderer)

    def _setup_api(self) -> None:
        security = None
        authorizations = None

        if self.is_auth_enabled():
            security = 'apikey'
            authorizations = {
                'apikey': {
                    'type': 'apiKey',
                    'in': 'header',
                    'name': 'Authorization'
                }
            }

        self._api = Api(
            self._app,
            version=self._model_store.config().map().get('version'),
            title="{} {}".format(self._model_store.config().map().get('application_name'), "API"),
            description='API Documentation with Swagger',
            endpoint='api',
            doc='/api',
            security=security,
            authorizations=authorizations
        )

    def _setup_web_globals(self) -> None:
        @self._app.context_processor
        def inject_global_vars() -> dict:
            return self._template_renderer.get_view_globals()

    def _setup_web_errors(self) -> None:
        def handle_error(error):
            if request.headers.get('Content-Type') == 'application/json' or request.headers.get('Accept') == 'application/json':
                response = jsonify({
                    'error': {
                        'code': error.code,
                        'message': error.description
                    }
                })
                return make_response(response, error.code)

            if error.code == 404:
                return send_from_directory(self.get_template_dir(), 'core/error404.html'), 404

            return error

        self._app.register_error_handler(400, handle_error)
        self._app.register_error_handler(404, handle_error)
        self._app.register_error_handler(409, handle_error)
        self._app.register_error_handler(HttpClientException, handle_error)


def create_require_api_key_decorator(web_server: WebServer):
    def require_api_key(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not web_server.is_auth_enabled():
                return

            auth_header = request.headers.get('Authorization')

            if auth_header:
                apikey = auth_header
                parts = auth_header.split()
                if parts[0].lower() == 'bearer':
                    apikey = parts[1]

                user = web_server._model_store.user().get_one_by_apikey(apikey)

                if user:
                    login_user(user)
                    return user

                return abort(403, 'Forbidden: You do not have access to this resource.')

            return abort(401, 'Invalid or missing API key.')

        return decorated_function()

    return require_api_key
