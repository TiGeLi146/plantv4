from aiogram.dispatcher.filters.state import State, StatesGroup


class ScheduleForm(StatesGroup):
    AddTasks = State()
    WaitAnswer = State()
    AddTime = State()
