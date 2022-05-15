import enum
import inspect
import sys
from abc import ABC, abstractmethod
from typing import Optional

import data
import intents
from dialog import FALLBACK_TEXT, FALLBACK_TITLE
from request import Request
from response_helpers import button, card, state
from state import STATE_RESPONSE_KEY

DB = data.DB

COMMAND = {
    'ПОМОЩЬ': button('Помощь'),
    'СБРОС': button('Сбросить'),
}

FALLBACK_IMAGE_ID = '213044/b1ceeb99c1d0117d981c'
DEFAULT_IMAGE_ID = '213044/b1ceeb99c1d0117d981c'
OBJ_IMAGE_ID = '1540737/04f370685db18c349968'


class Scene(ABC):

    @classmethod
    def id(cls):
        return cls.__name__

    @abstractmethod
    def reply(self, request):
        raise NotImplementedError()

    def move(self, request: Request):
        next_scene = self.handle_local_intents(request)
        if next_scene is None:
            next_scene = self.handle_global_intents(request)
        return next_scene

    @abstractmethod
    def handle_global_intents(self):
        raise NotImplementedError()

    @abstractmethod
    def handle_local_intents(self, request: Request) -> Optional[str]:
        raise NotImplementedError()

    def fallback(self, request: Request):
        return self.make_response(
            text=FALLBACK_TEXT,
            tts=f"{FALLBACK_TEXT}",
            buttons=[
                COMMAND['ПОМОЩЬ'],
                COMMAND['СБРОС'],
            ],
            state=state(
                secret=request.secret,
                repeat=request.repeat
            ),
            card=card(
                image_id=FALLBACK_IMAGE_ID,
                title=FALLBACK_TITLE,
                desc=FALLBACK_TEXT
            )
        )

    def make_response(self, text, tts=None, card=None, state=None, buttons=None, directives=None):
        response = {
            'text': text,
            'tts': tts if tts is not None else text,
        }
        if card is not None:
            response['card'] = card
        if buttons is not None:
            response['buttons'] = buttons
        if directives is not None:
            response['directives'] = directives
        webhook_response = {
            'response': response,
            'version': '1.0',
            STATE_RESPONSE_KEY: {
                'scene': self.id(),
                'secret': '',
                'repeat': '',
            },
        }
        if state is not None:
            webhook_response[STATE_RESPONSE_KEY].update(state)
        return webhook_response


class Intents(Scene, ABC):
    def handle_global_intents(self, request):
        if intents.START in request.intents:
            return Start()
        elif intents.RESTART in request.intents:
            return Restart()
        elif intents.REPEAT in request.intents:
            return Repeat()
        elif intents.YANDEX_REPEAT in request.intents:
            return Repeat()
        elif intents.YANDEX_HELP in request.intents:
            return Help()
        elif intents.YANDEX_WHAT_CAN_YOU_DO in request.intents:
            return Help()
        elif intents.RESULT in request.intents:
            return Secret()

    def handle_local_intents(self, request: Request):
        return None


class Help(Intents):
    def reply(self, request: Request):
        return self.make_response(
            text='Требуеться помощь',
            buttons=[
                COMMAND['СБРОС'],
            ],
            state=state(
                secret=request.secret,
                repeat=request.repeat
            ),
            card=card(
                image_id=DEFAULT_IMAGE_ID,
                title='Требуеться помощь',
                desc='Требуеться помощь'),
        )


class Repeat(Intents):
    def reply(self, request: Request):
        return self.make_response(
            text=request.repeat,
            buttons=[
                COMMAND['СЛЕДУЮЩИЙ'],
                COMMAND['ПРЕДЫДУЩИЙ'],
                COMMAND['СЛУЧАЙНЫЙ'],
                COMMAND['ВСЕ_НАВЫКИ'],
                COMMAND['ПОМОЩЬ'],
                COMMAND['СБРОС'],
            ],
            state=state(
                secret=request.secret,
                repeat=request.repeat
            ),
        )


class Restart(Intents):
    def reply(self, request: Request):
        return self.make_response(
            text='',
            buttons=[
                COMMAND['НАЧАТЬ'],
                COMMAND['СЛЕДУЮЩИЙ'],
                COMMAND['ПРЕДЫДУЩИЙ'],
                COMMAND['СЛУЧАЙНЫЙ'],
                COMMAND['ПОВТОРИТЬ'],
                COMMAND['ПОМОЩЬ'],
                COMMAND['ВСЕ_НАВЫКИ'],
            ],
            state=state()
        )


class Start(Intents):
    def reply(self, request: Request):
        text, title, image_id, url, market_url = '', '', '', '', ''
        return self.make_response(
            text='Здравствуйте, сообщите свой табельный номер я соберу для Вас информацию по объектам для обслуживания прикрепленные к Вам. Достаточно сказать номер, например 99 или "Получить отчет".',
            buttons=[
                button('Получить отчёт'),
                button('Администратор'),
                button('Подрядчик'),
                button('Сотрудник'),
            ],
            state=state(),
            card=card(
                image_id=DEFAULT_IMAGE_ID,
                title='Введите ID',
                desc=text
            ),
        )


class Secret(Intents):
    def reply(self, request: Request):
        SKILL_ID = request.skill_id
        text, title, image_id, secret, tts, url = '', '', '', '', '', ''
        buttons = []
        answer = request.intents['RESULT']['slots']['answer']['value']
        if answer == 'CLEANER':
            text = 'Специалист по уборки  к вам закреплены 3 объекта. Объект номер 2155 с высокой степенью ' \
                   'загрязнения. Обратите внимание!'
            title = 'Кабинет специалиста'
            image_id = DEFAULT_IMAGE_ID
            buttons = [
                button('Объект 2155 Загрезнение 5'),
                button('Объект 1256, Загрезнение 3'),
                button('Объект 3456, Загрезнение 1'),
                button('Администратор'),
                button('Подрядчик'),
            ]
        elif answer == 'CONT':
            text = 'Представитель подрядной организации ТОО "Ромашка",  у специалиста по уборке  ID 99 обнаружен один объект, номер 2155 с высокой степенью загрязнения.'
            title= 'Кабинет подрядчика'
            image_id = DEFAULT_IMAGE_ID
            buttons = [
                button('Объект 2155 Загрезнение 5'),
                button('Объект 1256 Загрезнение 3'),
                button('Объект 3456 Загрезнение 1'),
                button('Администратор'),
                button('Сотрудник'),
            ]
        elif answer == 'ADMIN':
            text = 'Зафиксировано нарушение у подрядной организации ТОО "Ромашка" один объект с высокой степенью загрязнения, два объекта со средней степенью загрязнения. Факт нарушения внесен в статистику.'
            title = 'Кабинет администратора'
            image_id = DEFAULT_IMAGE_ID
            buttons = [
                button('Объект 2155, Загрезнение 5'),
                button('Объект 1256, Загрезнение 3'),
                button('Объект 3456, Загрезнение 1'),
                button('Подрядчик'),
                button('Сотрудник'),
            ]
        elif answer == 'OBJ':
            text = 'Объект 2155. Текущий статус загрязнения, высокий. Требует особого внимание!'
            title = 'Объект 2155'
            image_id = OBJ_IMAGE_ID
            buttons = [
                button('Построить маршрут', url='https://yandex.ru/maps/1107/anapa/?ll=37.325007%2C44.899082&mode=routes&rtext=44.900511%2C37.321303~44.899153%2C37.328520&rtt=auto&ruri=ymapsbm1%3A%2F%2Forg%3Foid%3D171412346257~ymapsbm1%3A%2F%2Forg%3Foid%3D179668334404&z=17.56'),
                button('Сообщить об ошибки'),
                button('Подрядчик'),
                button('Администратор'),
                button('Сотрудник'),
            ]

        return self.make_response(
            text=text,
            tts=tts,
            buttons=buttons,
            state=state(
                secret=str(secret),
                repeat=text
            ),
            card=card(
                image_id=image_id,
                title=title,
                desc=text
            ),
        )


def _list_scenes():
    current_module = sys.modules[__name__]
    scenes = []
    for name, obj in inspect.getmembers(current_module):
        if inspect.isclass(obj) and issubclass(obj, Scene):
            scenes.append(obj)
    return scenes


SCENES = {
    scene.id(): scene for scene in _list_scenes()
}

DEFAULT_SCENE = Start
