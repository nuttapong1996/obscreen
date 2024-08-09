import time

from flask import request, abort, jsonify
from flask_restx import Resource, Namespace, fields
from src.model.entity.Slide import Slide
from src.interface.ObController import ObController
from src.util.utils import str_datetime_to_cron, str_weekdaytime_to_cron, str_to_bool
from src.service.WebServer import create_require_api_key_decorator

# Namespace for slide operations
slide_ns = Namespace('slides', description='Operations on slides')

# Output model for a slide
slide_output_model = slide_ns.model('SlideOutput', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a slide'),
    'content_id': fields.Integer(description='The content ID for the slide'),
    'playlist_id': fields.Integer(description='The playlist ID to which the slide belongs'),
    'enabled': fields.Boolean(description='Is the slide enabled?'),
    'delegate_duration': fields.Boolean(description='Should the duration be delegated?'),
    'duration': fields.Integer(description='Duration of the slide'),
    'position': fields.Integer(description='Position of the slide'),
    'is_notification': fields.Boolean(description='Is the slide a notification?'),
    'cron_schedule': fields.String(description='Cron expression for scheduling start'),
    'cron_schedule_end': fields.String(description='Cron expression for scheduling end'),
})

# Input model for updating slide positions
positions_model = slide_ns.model('SlidePositions', {
    'positions': fields.Raw(required=True, description='A dictionary where keys are slide IDs and values are their new positions')
})

# Parser for basic slide attributes
slide_base_parser = slide_ns.parser()
slide_base_parser.add_argument('content_id', type=int, required=True, help='The content ID for the slide')
slide_base_parser.add_argument('playlist_id', type=int, required=True, help='The playlist ID to which the slide belongs')
slide_base_parser.add_argument('enabled', type=str_to_bool, default=None, help='Is the slide enabled?')
slide_base_parser.add_argument('duration', type=int, default=3, help='Duration of the slide')
slide_base_parser.add_argument('position', type=int, default=999, help='Position of the slide')

# Parser for slide attributes (add)
slide_parser = slide_base_parser.copy()
slide_parser.add_argument('scheduling', type=str, required=True, help='Scheduling type: loop, datetime or inweek')
slide_parser.add_argument('delegate_duration', type=str_to_bool, default=None, help='Should the duration be delegated to video\'s duration?')
slide_parser.add_argument('datetime_start', type=str, required=False, help='Start datetime for scheduling (format: Y-m-d H:M)')
slide_parser.add_argument('datetime_end', type=str, required=False, help='End datetime for scheduling (format: Y-m-d H:M)')
slide_parser.add_argument('day_start', type=int, required=False, help='Start day for inweek scheduling (format: 1 for Monday to 7 for Sunday)')
slide_parser.add_argument('time_start', type=str, required=False, help='Start time for inweek scheduling (format: H:M)')
slide_parser.add_argument('day_end', type=int, required=False, help='End day for inweek scheduling (format: 1 for Monday to 7 for Sunday)')
slide_parser.add_argument('time_end', type=str, required=False, help='End time for inweek scheduling (format: H:M)')

# Parser for slide notification attributes (add)
slide_notification_parser = slide_base_parser.copy()
slide_notification_parser.add_argument('scheduling', type=str, required=True, help='Scheduling type: datetime or cron')
slide_notification_parser.add_argument('datetime_start', type=str, required=False, help='Start datetime for notification scheduling (format: Y-m-d H:M)')
slide_notification_parser.add_argument('datetime_end', type=str, required=False, help='End datetime for notification scheduling (format: Y-m-d H:M)')
slide_notification_parser.add_argument('cron_start', type=str, required=False, help='Cron expression for notification scheduling start (format: * * * * * * *)')
slide_notification_parser.add_argument('cron_end', type=str, required=False, help='Cron expression for notification scheduling end (format: * * * * * * *)')

# Parser for slide attributes (update)
slide_edit_parser = slide_parser.copy()
slide_edit_parser.replace_argument('scheduling', type=str, required=False, help='Scheduling type: loop, datetime, or inweek')
slide_edit_parser.replace_argument('content_id', type=int, required=False, help='The content ID for the slide')
slide_edit_parser.replace_argument('playlist_id', type=int, required=False, help='The playlist ID to which the slide belongs')

# Parser for slide notification attributes (update)
slide_notification_edit_parser = slide_notification_parser.copy()
slide_notification_edit_parser.replace_argument('scheduling', type=str, required=False, help='Scheduling type: datetime or cron')
slide_notification_edit_parser.replace_argument('content_id', type=int, required=False, help='The content ID for the slide')
slide_notification_edit_parser.replace_argument('playlist_id', type=int, required=False, help='The playlist ID to which the slide belongs')


class SlideApiController(ObController):

    def register(self):
        self.api().add_namespace(slide_ns, path='/api/slides')
        slide_ns.add_resource(self.create_resource(SlideNotificationResource), '/notifications/<int:slide_id>')
        slide_ns.add_resource(self.create_resource(SlideResource), '/<int:slide_id>')
        slide_ns.add_resource(self.create_resource(SlideAddResource), '/')
        slide_ns.add_resource(self.create_resource(SlideAddNotificationResource), '/notifications')
        slide_ns.add_resource(self.create_resource(SlidePositionResource), '/positions')

    def create_resource(self, resource_class):
        # Function to inject dependencies into resources
        return type(f'{resource_class.__name__}WithDependencies', (resource_class,), {
            '_model_store': self._model_store,
            '_controller': self,
            'require_api_key': create_require_api_key_decorator(self._web_server)
        })

    def _add_slide_or_notification(self, data, is_notification=False):
        if not data or 'content_id' not in data:
            abort(400, description="Valid Content ID is required")

        if not self._model_store.content().get(data.get('content_id')):
            abort(404, description="Content not found")

        if not data or 'playlist_id' not in data:
            abort(400, description="Valid Playlist ID is required")

        if not self._model_store.playlist().get(data.get('playlist_id')):
            abort(404, description="Playlist not found")

        cron_schedule_start, cron_schedule_end = self._resolve_scheduling(data, is_notification=is_notification)

        slide = Slide(
            content_id=data.get('content_id'),
            enabled=data.get('enabled') if data.get('enabled') is not None else True,
            delegate_duration=data.get('delegate_duration') if data.get('delegate_duration') is not None else False,
            duration=data.get('duration', 3),
            position=data.get('position', 999),
            is_notification=is_notification,
            playlist_id=data.get('playlist_id', None),
            cron_schedule=cron_schedule_start,
            cron_schedule_end=cron_schedule_end
        )

        slide = self._model_store.slide().add_form(slide)
        self._post_update()

        return slide.to_dict(), 201

    def _resolve_scheduling(self, data, is_notification=False):
        try:
            return self._resolve_scheduling_for_notification(data) if is_notification else self._resolve_scheduling_for_slide(data)
        except ValueError as ve:
            abort(400, description=str(ve))

    def _resolve_scheduling_for_slide(self, data):
        scheduling = data.get('scheduling', 'loop')
        cron_schedule_start = None
        cron_schedule_end = None

        if scheduling == 'loop':
            pass
        elif scheduling == 'datetime':
            datetime_start = data.get('datetime_start')
            datetime_end = data.get('datetime_end')

            if not datetime_start:
                abort(400, description="Field datetime_start is required for scheduling='datetime'")

            cron_schedule_start = str_datetime_to_cron(datetime_str=datetime_start)

            if datetime_end:
                cron_schedule_end = str_datetime_to_cron(datetime_str=datetime_end)
        elif scheduling == 'inweek':
            day_start = data.get('day_start')
            time_start = data.get('time_start')
            day_end = data.get('day_end')
            time_end = data.get('time_end')

            if not (day_start and time_start and day_end and time_end):
                abort(400, description="day_start, time_start, day_end, and time_end are required for scheduling='inweek'")
            cron_schedule_start = str_weekdaytime_to_cron(weekday=int(day_start), time_str=time_start)
            cron_schedule_end = str_weekdaytime_to_cron(weekday=int(day_end), time_str=time_end)
        else:
            abort(400, description="Invalid value for slide scheduling. Expected 'loop', 'datetime', or 'inweek'.")

        return cron_schedule_start, cron_schedule_end

    def _resolve_scheduling_for_notification(self, data):
        scheduling = data.get('scheduling', 'datetime')
        cron_schedule_start = None
        cron_schedule_end = None

        if scheduling == 'datetime':
            datetime_start = data.get('datetime_start')
            datetime_end = data.get('datetime_end')

            if not datetime_start:
                abort(400, description="Field datetime_start is required for scheduling='datetime'")

            cron_schedule_start = str_datetime_to_cron(datetime_str=datetime_start)

            if datetime_end:
                cron_schedule_end = str_datetime_to_cron(datetime_str=datetime_end)
        elif scheduling == 'cron':
            cron_schedule_start = data.get('cron_start')

            if not cron_schedule_start:
                abort(400, description="Field cron_start is required for scheduling='cron'")
        else:
            abort(400, description="Invalid value for notification scheduling. Expected 'datetime' or 'cron'.")

        return cron_schedule_start, cron_schedule_end

    def _post_update(self):
        self._model_store.variable().update_by_name("last_slide_update", time.time())


class SlideAddResource(Resource):

    @slide_ns.expect(slide_parser)
    @slide_ns.marshal_with(slide_output_model, code=201)
    def post(self):
        """Add a new slide"""
        self.require_api_key()
        data = slide_parser.parse_args()
        return self._controller._add_slide_or_notification(data, is_notification=False)


class SlideAddNotificationResource(Resource):

    @slide_ns.expect(slide_notification_parser)
    @slide_ns.marshal_with(slide_output_model, code=201)
    def post(self):
        """Add a new slide notification"""
        self.require_api_key()
        data = slide_notification_parser.parse_args()
        return self._controller._add_slide_or_notification(data, is_notification=True)


class SlideResource(Resource):

    @slide_ns.marshal_with(slide_output_model)
    def get(self, slide_id):
        """Get a slide by its ID"""
        self.require_api_key()
        slide = self._model_store.slide().get(slide_id)
        if not slide:
            abort(404, description="Slide not found")
        return slide.to_dict()

    @slide_ns.expect(slide_edit_parser)
    @slide_ns.marshal_with(slide_output_model)
    def put(self, slide_id):
        """Edit an existing slide"""
        self.require_api_key()
        data = slide_edit_parser.parse_args()

        slide = self._model_store.slide().get(slide_id)
        if not slide:
            abort(404, description="Slide not found")

        cron_schedule_start = slide.cron_schedule
        cron_schedule_end = slide.cron_schedule_end

        if data.get('scheduling'):
            cron_schedule_start, cron_schedule_end = self._controller._resolve_scheduling(data, is_notification=slide.is_notification)

        self._model_store.slide().update_form(
            id=slide_id,
            content_id=data.get('content_id', slide.content_id),
            enabled=data.get('enabled', slide.enabled),
            position=data.get('position', slide.position),
            duration=data.get('duration', slide.duration),
            cron_schedule=cron_schedule_start,
            cron_schedule_end=cron_schedule_end
        )
        self._controller._post_update()

        updated_slide = self._model_store.slide().get(slide_id)
        return updated_slide.to_dict()

    def delete(self, slide_id):
        """Delete a slide"""
        self.require_api_key()
        slide = self._model_store.slide().get(slide_id)

        if not slide:
            abort(404, description="Slide not found")

        self._model_store.slide().delete(slide_id)
        self._controller._post_update()

        return '', 204


class SlideNotificationResource(Resource):

    @slide_ns.expect(slide_notification_edit_parser)
    @slide_ns.marshal_with(slide_output_model)
    def put(self, slide_id):
        """Edit an existing slide notification"""
        self.require_api_key()
        data = slide_notification_edit_parser.parse_args()

        slide = self._model_store.slide().get(slide_id)
        if not slide:
            abort(404, description="Slide not found")

        cron_schedule_start = slide.cron_schedule
        cron_schedule_end = slide.cron_schedule_end

        if data.get('scheduling'):
            cron_schedule_start, cron_schedule_end = self._controller._resolve_scheduling(data, is_notification=slide.is_notification)

        self._model_store.slide().update_form(
            id=slide_id,
            content_id=data.get('content_id', slide.content_id),
            enabled=data.get('enabled', slide.enabled),
            position=data.get('position', slide.position),
            delegate_duration=data.get('delegate_duration', slide.delegate_duration),
            duration=data.get('duration', slide.duration),
            cron_schedule=cron_schedule_start,
            cron_schedule_end=cron_schedule_end
        )
        self._controller._post_update()

        updated_slide = self._model_store.slide().get(slide_id)
        return updated_slide.to_dict()


class SlidePositionResource(Resource):

    @slide_ns.expect(positions_model)
    def post(self):
        """Update positions of multiple slides"""
        self.require_api_key()
        data = request.get_json()
        positions = data.get('positions', None) if data else None

        if not positions:
            abort(400, description="Positions data are required")

        # Ensure the input is a dictionary with integer keys and values
        if not isinstance(data, dict) or not all(isinstance(k, str) and isinstance(v, int) for k, v in positions.items()):
            abort(400, description="Input must be a dictionary with string keys as slide IDs and integer values as positions")

        self._model_store.slide().update_positions(positions)
        self._controller._post_update()
        return jsonify({'status': 'ok'})
