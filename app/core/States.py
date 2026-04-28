from aiogram.fsm.state import State, StatesGroup

class RecordState(StatesGroup):
    check_authorization = State()
    service = State()

class AdminState(StatesGroup):
    get_id = State()