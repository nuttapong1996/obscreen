import json
import os
import time

from flask import Flask, render_template, redirect, request, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from src.model.Slide import Slide
from src.model.SlideType import SlideType
from src.utils import str_to_enum


class SlideshowController:

    def __init__(self, app, lang_dict, slide_manager, variable_manager):
        self._app = app
        self._lang_dict = lang_dict
        self._slide_manager = slide_manager
        self._variable_manager = variable_manager
        self.register()

    def register(self):
        self._app.add_url_rule('/manage', 'manage', self.manage, methods=['GET'])
        self._app.add_url_rule('/slideshow', 'slideshow_slide_list', self.slideshow, methods=['GET'])
        self._app.add_url_rule('/slideshow/slide/add', 'slideshow_slide_add', self.slideshow_slide_add, methods=['POST'])
        self._app.add_url_rule('/slideshow/slide/edit', 'slideshow_slide_edit', self.slideshow_slide_edit, methods=['POST'])
        self._app.add_url_rule('/slideshow/slide/toggle', 'slideshow_slide_toggle', self.slideshow_slide_toggle, methods=['POST'])
        self._app.add_url_rule('/slideshow/slide/delete', 'slideshow_slide_delete', self.slideshow_slide_delete, methods=['DELETE'])
        self._app.add_url_rule('/slideshow/slide/position', 'slideshow_slide_position', self.slideshow_slide_position, methods=['POST'])

    def manage(self):
        return redirect(url_for('slideshow_slide_list'))

    def slideshow(self):
        return render_template(
            'slideshow/list.jinja.html',
            l=self._lang_dict,
            enabled_slides=self._slide_manager.get_enabled_slides(),
            disabled_slides=self._slide_manager.get_disabled_slides(),
            var_last_restart=self._variable_manager.get_one_by_name('last_restart'),
            var_external_url=self._variable_manager.get_one_by_name('external_url')
        )

    def slideshow_slide_add(self):
        slide = Slide(
            name=request.form['name'],
            type=str_to_enum(request.form['type'], SlideType),
            duration=request.form['duration'],
        )

        if slide.has_file():
            if 'object' not in request.files:
                return redirect(request.url)

            object = request.files['object']

            if object.filename == '':
                return redirect(request.url)

            if object:
                object_name = secure_filename(object.filename)
                object_path = os.path.join(self._app.config['UPLOAD_FOLDER'], object_name)
                object.save(object_path)
                slide.location = object_path
        else:
            slide.location = request.form['object']

        self._slide_manager.add_form(slide)
        self._post_update()

        return redirect(url_for('slideshow_slide_list'))

    def slideshow_slide_edit(self):
        self._slide_manager.update_form(request.form['id'], request.form['name'], request.form['duration'])
        self._post_update()
        return redirect(url_for('slideshow_slide_list'))

    def slideshow_slide_toggle(self):
        data = request.get_json()
        self._slide_manager.update_enabled(data.get('id'), data.get('enabled'))
        self._post_update()
        return jsonify({'status': 'ok'})

    def slideshow_slide_delete(self):
        data = request.get_json()
        self._slide_manager.delete(data.get('id'))
        self._post_update()
        return jsonify({'status': 'ok'})

    def slideshow_slide_position(self):
        data = request.get_json()
        self._slide_manager.update_positions(data)
        self._post_update()
        return jsonify({'status': 'ok'})

    def _post_update(self):
        self._variable_manager.update_by_name("last_slide_update", time.time())

