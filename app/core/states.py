from aiogram.fsm.state import State, StatesGroup

class CreateUserState(StatesGroup):
    ask_name = State()
    get_name = State()
    ask_number = State()
    finish = State()

class AdminState(StatesGroup):
    get_id = State()
    get_name = State()

class CatalogSetState(StatesGroup):
    get_name = State()
    get_price = State()
    create = State()

class Requests(StatesGroup):
    choose_ct = State()
    ask_date = State()
    get_date = State()
    get_hour = State()
    get_comment = State()
    create_request = State()

#===============================================================

class AiUserState(StatesGroup):
    chatting = State()

class AiAdminState(StatesGroup):
    chatting = State()