from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat.chat_models import GigaChat
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from states.state_make_schedule import ScheduleForm
from  keyboards.productivity import get_productive_time_keyboard
from data.config import GIGACHAT_API

from loader import dp, bot

DATA = ""
PR_TIME = "Утро"

async def set_tasks_ai(message: types.Message, state: FSMContext):
    text = message.text
    async with state.proxy() as data:
        data['text'] = text
    await state.update_data(data)


@dp.message_handler(commands=['make_schedule'], state='*')
async def bot_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("<b>Введите задачи в формате</b>\n"
                         "[Название задачи] с [время начала выполнения задачи] до [конец выполнения] (при наличии) сложность: [сложность от 1 до 5] (при желании)\n"
                         "[Следующая задача в аналогичном формате]\n"
                         "\n"
                         "<b>Например:</b>\n"
                         "Сделать домашку по физике сложность 4\n"
                         "Отправить отчет с 18.05 до 18.10")
    await ScheduleForm.WaitAnswer.set()

@dp.message_handler(state=ScheduleForm.AddTasks)
async def get_text(message: types.Message, state: FSMContext):
    user_message = message.text
    print(user_message)
    await state.update_data(user_message=user_message)
    await message.reply('Выберите наиболее продуктивное время суток:', reply_markup=get_productive_time_keyboard())
    await state.finish()
    await ScheduleForm.AddTime.set()


@dp.callback_query_handler(state=ScheduleForm.AddTime)
async def process_productive_time(callback_query: types.CallbackQuery, state: FSMContext):
    time = callback_query.data
    await state.update_data(time=time)
    await bot.send_message(
        callback_query.from_user.id,
        f'Задачи успешно загружены',
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.finish()
    await ScheduleForm.WaitAnswer.set()


async def generate_schedule(prompt):
    llm = GigaChat(
        credentials=GIGACHAT_API,
        scope="GIGACHAT_API_PERS",
        model="GigaChat",
        # Отключает проверку наличия сертификатов НУЦ Минцифры
        verify_ssl_certs=False,
        streaming=False,
    )

    messages = [
        SystemMessage(
            content="Ты - личный ассистент, который помогает пользователю составлять расписание с учетом приоритетов. Самое важное - сложные задачи ставить в наиболее продуктивное время и старасться оставлять перерывы между задачами для отдыха"
        )
    ]

    user_input = prompt
    messages.append(HumanMessage(content=user_input))
    res = llm.invoke(messages)
    messages.append(res)
    return res.content


@dp.message_handler(state=ScheduleForm.WaitAnswer)
async def make_schedule(message: types.Message, state: FSMContext):
    tasks = await state.get_data()
    print(tasks)
    user_message = tasks.get('user_message', 'Сообщение не найдено.')
    print(user_message)

    prompt = f"Составь расписание на день, учитывая сложность задач от 1 до 5, где 1 - самое простое, 5 - сложное. Задачи: {', '.join(tasks)}. "

    schedule = await generate_schedule(prompt)
    await message.reply(f"Ваше расписание на сегодня:\n{schedule}")
