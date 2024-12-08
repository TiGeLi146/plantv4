from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat.chat_models import GigaChat

API_TOKEN = '7613378641:AAFMk4fG-PPZGyTmlzmzbyDgcIrA2PGvTnI'
GIGACHAT_API = "MThmYmU2NzEtNWY0Zi00ODBmLThjMDgtNmFjYmUzMWE5MmU0OmViYWQ2ZjJkLTFhOGYtNDkwZC1iNmMwLTgyNTFlNDI1YjM2ZQ=="


# Создаем объекты бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Определяем состояния
class Form(StatesGroup):
    waiting_for_message = State()

# @dp.message_handler(commands=['start'])
# async def cmd_start(message: types.Message):
#     await message.answer(f"Привет, {message.from_user.full_name}!\n"
#                          "Чтобы составить расписание,\n"
#                          "введи задачи и первой строкой наиболее продуктивное время (утро, день, вечер)"
#                          "Формат задач:"
#                          "[Название задачи] с [время начала выполнения задачи] до [конец выполнения] (при наличии) сложность: [сложность от 1 до 5] (при желании)\n"
#                          "[Следующая задача в аналогичном формате]\n"
#                          "\n"
#                          "<b>Например:</b>\n"
#                          "Сделать домашку по физике сложность 4\n"
#                          "Отправить отчет с 18.05 до 18.10\n"
#                          "\n"
#                          "Для получения расписания введите /get_schedule"
#                          )
#     await Form.waiting_for_message.set()  # Переход в состояние ожидания сообщения

# @dp.message_handler(state=Form.waiting_for_message)
# async def process_message(message: types.Message, state: FSMContext):
#     user_message = message.text  # Сохраняем сообщение пользователя в переменную
#     await state.update_data(user_message=user_message)  # Сохраняем в контексте состояния
#     await state.finish()  # Завершаем состояние
#     await message.answer(f"Задачи и продуктивное время введены")  # Отправляем ответ пользователю

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


# @dp.message_handler(commands=['get_schedule'])
# async def get_message(message: types.Message, state: FSMContext):
#     data = await state.get_data()  # Получаем данные из состояния
#     user_message = data.get('user_message', 'Сообщение не найдено.')  # Извлекаем сообщение
#     print(user_message)
#     await message.answer(f"Ваше предыдущее сообщение: {user_message}")  # Отправляем ответ пользователю
#     await state.finish()
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer(f"Привет, {message.from_user.full_name}!\n"
                         "Чтобы составить расписание,\n"
                         "введи задачи и первой строкой наиболее продуктивное время (утро, день, вечер)"
                         "Формат задач:"
                         "[Название задачи] с [время начала выполнения задачи] до [конец выполнения] (при наличии) сложность: [сложность от 1 до 5] (при желании)\n"
                         "[Следующая задача в аналогичном формате]\n"
                         "\n"
                         "<b>Например:</b>\n"
                         "Сделать домашку по физике сложность 4\n"
                         "Отправить отчет с 18.05 до 18.10\n")
    await Form.waiting_for_message.set()  # Переход в состояние ожидания сообщения

@dp.message_handler(state=Form.waiting_for_message)
async def process_message(message: types.Message, state: FSMContext):
    user_message = message.text  # Сохраняем сообщение пользователя в переменную
    await state.finish()  # Завершаем состояние
    print(user_message)
    await message.answer(f"Вы написали: {user_message}")
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
