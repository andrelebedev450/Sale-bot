from aiogram.fsm.state import State, StatesGroup

class SupportTicketStates(StatesGroup):
    waiting_for_message = State()
