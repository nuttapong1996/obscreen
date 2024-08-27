import abc

from typing import Optional, List, Dict, Union
from flask import request
from src.service.TemplateRenderer import TemplateRenderer
from src.service.ModelStore import ModelStore
from src.interface.ObPlugin import ObPlugin


class ObController(abc.ABC):

    def __init__(self, kernel, web_server, app, auth_required, model_store: ModelStore, template_renderer: TemplateRenderer, plugin: Optional[ObPlugin] = None):
        self._kernel = kernel
        self._web_server = web_server
        self._app = app
        self._auth = auth_required
        self._model_store = model_store
        self._template_renderer = template_renderer
        self._plugin = plugin
        self.register()

    @abc.abstractmethod
    def register(self) -> None:
        pass

    def plugin(self) -> ObPlugin:
        if not isinstance(self._plugin, ObPlugin):
            raise Error('No plugin for controller {}'.format(self.__class__.__name__))

        return self._plugin

    def get_template_dir(self):
        return self._web_server.get_template_dir()

    def get_web_dir(self):
        return self._web_server.get_web_dir()

    def reload_web_server(self):
        self._web_server.reload()

    def reload_lang(self, lang: str):
        self._kernel.reload_lang(lang)

    def get_application_dir(self):
        return self._kernel.get_application_dir()

    def t(self, token) -> Union[Dict, str]:
        return self._model_store.lang().translate(token)

    def render_view(self, template_file: str, **parameters: dict) -> str:
        return self._template_renderer.render_view(template_file, self.plugin(), **parameters)

    def api(self):
        return self._web_server.api

    def get_referrer_path(self):
        referer_url = request.referrer
        if referer_url:
            return '/' + referer_url.replace(request.host_url, '').split('?')[0]
        return None

    def get_referrer_rule(self):
        referer_path = self.get_referrer_path()

        if referer_path:
            for rule in self._app.url_map.iter_rules():
                if referer_path == rule.rule.split('/<')[0]:
                    return rule.rule

        return None
