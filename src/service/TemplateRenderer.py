import os
import json

from flask import Flask, send_from_directory, Markup, url_for, request
from flask_login import current_user
from typing import List, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
from src.service.ModelStore import ModelStore
from src.model.enum.HookType import HookType
from src.model.hook.HookRegistration import HookRegistration
from src.model.hook.StaticHookRegistration import StaticHookRegistration
from src.model.hook.FunctionalHookRegistration import FunctionalHookRegistration
from src.constant.WebDirConstant import WebDirConstant
from src.service.AliasFileSystemLoader import AliasFileSystemLoader
from src.util.utils import get_safe_cron_descriptor, \
    is_cron_in_datetime_moment, \
    is_cron_in_week_moment, \
    seconds_to_hhmmss, am_i_in_docker, \
    truncate, merge_dicts, dictsort


class TemplateRenderer:

    def __init__(self, kernel, model_store: ModelStore, render_hook):
        self._kernel = kernel
        self._model_store = model_store
        self._render_hook = render_hook
        self._rendering_env = self.init_rendering_env()

    def cron_descriptor(self, expression: str, use_24hour_time_format=True) -> str:
        return get_safe_cron_descriptor(expression, use_24hour_time_format, self._model_store.lang().get_lang(local_with_country=True))

    def get_view_globals(self) -> dict:
        globals = dict(
            STATIC_PREFIX="/{}/{}/".format(WebDirConstant.FOLDER_STATIC, WebDirConstant.FOLDER_STATIC_WEB_ASSETS),
            SECRET_KEY=self._model_store.config().map().get('secret_key'),
            FLEET_PLAYER_ENABLED=self._model_store.variable().map().get('fleet_player_enabled').as_bool(),
            DARK_MODE=self._model_store.variable().map().get('dark_mode').as_bool(),
            AUTH_ENABLED=self._model_store.variable().map().get('auth_enabled').as_bool(),
            last_pillmenu_slideshow=self._model_store.variable().map().get('last_pillmenu_slideshow').as_string(),
            last_pillmenu_configuration=self._model_store.variable().map().get('last_pillmenu_configuration').as_string(),
            external_url=self._model_store.variable().map().get('external_url').as_string().strip('/'),
            last_pillmenu_fleet=self._model_store.variable().map().get('last_pillmenu_fleet').as_string(),
            last_pillmenu_security=self._model_store.variable().map().get('last_pillmenu_security').as_string(),
            track_created=self._model_store.user().track_user_created,
            track_updated=self._model_store.user().track_user_updated,
            PORT=self._model_store.config().map().get('port'),
            VERSION=self._model_store.config().map().get('version'),
            LANG=self._model_store.variable().map().get('lang').as_string(),
            HOOK=self._render_hook,
            cron_descriptor=self.cron_descriptor,
            str=str,
            seconds_to_hhmmss=seconds_to_hhmmss,
            is_cron_in_datetime_moment=is_cron_in_datetime_moment,
            is_cron_in_week_moment=is_cron_in_week_moment,
            json_dumps=json.dumps,
            json_loads=json.loads,
            merge_dicts=merge_dicts,
            dictsort=dictsort,
            truncate=truncate,
            l=self._model_store.lang().map(),
            t=self._model_store.lang().translate,
        )

        for hook in HookType:
            globals[hook.name] = hook

        return globals

    def render_hooks(self, hooks_registrations: List[HookRegistration]) -> str:
        content = []

        for hook_registration in hooks_registrations:
            if isinstance(hook_registration, StaticHookRegistration):
                template = hook_registration.plugin.get_rendering_env().get_template("@{}/{}".format(
                    WebDirConstant.FOLDER_PLUGIN_HOOK,
                    os.path.basename(hook_registration.template)
                ))
                content.append(template.render(
                    **self.get_view_globals(),
                    url_for=url_for
                ))
            elif isinstance(hook_registration, FunctionalHookRegistration):
                content.append(hook_registration.function())

        return Markup("".join(content))

    def init_rendering_env(self, base_folder: Optional[str] = None) -> Environment:
        base_folder = "{}/".format(base_folder.replace(self._kernel.get_application_dir(), '')) if base_folder else ''

        alias_paths = {
            "::": "{}/".format(WebDirConstant.FOLDER_TEMPLATES),
            "@": "{}{}/".format(base_folder, WebDirConstant.FOLDER_TEMPLATES)
        }

        env = Environment(
            loader=AliasFileSystemLoader(
                searchpath=self._kernel.get_application_dir(),
                alias_paths=alias_paths
            ),
            autoescape=select_autoescape(['html', 'xml'])
        )

        return env

    def get_rendering_env(self) -> Environment:
        return self._rendering_env

    def render_view(self, template_file: str, plugin: Optional = None, **parameters: dict) -> str:
        base_rendering_env = plugin.get_rendering_env() if plugin else self.get_rendering_env()
        template = base_rendering_env.get_template(template_file)

        if plugin:
            parameters['STATIC_PLUGIN_PREFIX'] = "/{}/{}/{}/{}/".format(
                WebDirConstant.FOLDER_STATIC,
                WebDirConstant.FOLDER_STATIC_WEB_ASSETS,
                WebDirConstant.FOLDER_PLUGIN_STATIC_DST,
                plugin.use_id()
            )

        return template.render(
            request=request,
            url_for=url_for,
            current_user=current_user,
            **parameters,
            **self.get_view_globals(),
        )
