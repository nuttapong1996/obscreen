import json

from flask import Flask, render_template, redirect, request, url_for, jsonify, flash
from flask_login import login_user, logout_user, current_user
from src.service.ModelStore import ModelStore
from src.model.entity.User import User
from src.interface.ObController import ObController
from typing import Optional

class AuthController(ObController):

    def guard_auth(self, f):
        def decorated_function(*args, **kwargs):
            if not self._model_store.variable().map().get('auth_enabled').as_bool():
                return redirect(url_for('manage'))
            return f(*args, **kwargs)

        return decorated_function

    def register(self):
        self._app.add_url_rule('/login', 'login', self.login, methods=['GET', 'POST'])
        self._app.add_url_rule('/logout', 'logout', self.logout, methods=['GET'])
        self._app.add_url_rule('/auth/user/list', 'auth_user_list', self.guard_auth(self._auth(self.auth_user_list)), methods=['GET'])
        self._app.add_url_rule('/auth/user/add', 'auth_user_add', self.guard_auth(self._auth(self.auth_user_add)), methods=['POST'])
        self._app.add_url_rule('/auth/user/edit', 'auth_user_edit', self.guard_auth(self._auth(self.auth_user_edit)), methods=['POST'])
        self._app.add_url_rule('/auth/user/delete/<user_id>', 'auth_user_delete', self.guard_auth(self._auth(self.auth_user_delete)), methods=['GET'])

    def login(self):
        if current_user.is_authenticated:
            return redirect(url_for('playlist'))

        if not self._model_store.variable().map().get('auth_enabled').as_bool():
            return redirect(url_for('playlist'))

        if len(request.form):
            user = self._model_store.user().get_one_by_username(request.form['username'], enabled=True)
            if user:
                if user.password == self._model_store.user().encode_password(request.form['password']):
                    login_user(user)
                    return redirect(url_for('playlist'))
                else:
                    flash(self.t('login_error_bad_credentials'), 'error')
            else:
                flash(self.t('login_error_not_found'), 'error')

        return render_template(
            'auth/login.jinja.html',
            last_username=request.form['username'] if 'username' in request.form else None
        )

    def logout(self):
        logout_user()

        if request.args.get('restart'):
            return redirect(url_for(
                'sysinfo_restart',
                secret_key=self._model_store.config().map().get('secret_key')
            ))

        return redirect(url_for('login'))

    def auth_user_list(self):
        demo = self._model_store.config().map().get('demo')

        return render_template(
            'auth/list.jinja.html',
            users=self._model_store.user().get_users(exclude=User.DEFAULT_USER if demo else None),
            plugin_core_api_enabled=self._model_store.variable().map().get('plugin_core_api_enabled').as_bool()
        )

    def auth_user_add(self):
        self._model_store.user().add_form(User(
            username=request.form['username'],
            password=request.form['password'],
            enabled=True if 'enabled' in request.form and request.form['enabled'] == '1' else False,
        ))
        return redirect(url_for('auth_user_list'))

    def auth_user_edit(self):
        self._model_store.user().update_form(
            id=request.form['id'],
            enabled=True if 'enabled' in request.form and request.form['enabled'] == '1' else False,
            username=request.form['username'],
            password=request.form['password'] if 'password' in request.form and request.form['password'] else None
        )
        return redirect(url_for('auth_user_list'))

    def auth_user_delete(self, user_id: Optional[int] = 0):
        user = self._model_store.user().get(user_id)

        if not user:
            return redirect(url_for('auth_user_list'))

        if user.id == str(current_user.id):
            flash(self.t('auth_user_delete_cant_delete_yourself'), 'error')
            return redirect(url_for('auth_user_list'))

        if self._model_store.user().count_all_enabled() == 1:
            flash(self.t('auth_user_delete_at_least_one_account'), 'error')
            return redirect(url_for('auth_user_list'))

        self._model_store.user().delete(user_id)
        return redirect(url_for('auth_user_list'))
