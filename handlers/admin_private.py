from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from database.models import User
from database.orm_query import (
    orm_add_object, 
    orm_get_user,
    orm_get_all_users,
    orm_get_statistics,
    orm_get_subscription_settings,
    orm_update_subscription_price,
    orm_ban_user,
    orm_unban_user,
    orm_create_subscription,
    orm_check_subscription_active,
    orm_get_user_subscription
)
from filters.chat_types import IsAdmin
from sqlalchemy.ext.asyncio import AsyncSession
from handlers.states import AdminGiveSubscription, AdminBanUser, AdminUnbanUser, AdminBroadcast
from kbrds.inline import get_main_inline_kb
import config
import re
import asyncio


admin_router = Router()
admin_router.message.filter(IsAdmin())
admin_router.callback_query.filter(IsAdmin())


@admin_router.message(F.text == "/admin")
async def admin_start(message: types.Message, session: AsyncSession):
    user_id = message.from_user.id
    user = await orm_get_user(user_id=user_id, session=session)
    if not user:
        user = User(user_id=user_id)
        await orm_add_object(obj=user, session=session)

    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"))
    keyboard.add(InlineKeyboardButton(text="💰 Управление ценой", callback_data="admin_price"))
    keyboard.add(InlineKeyboardButton(text="👥 Управление пользователями", callback_data="admin_users"))
    keyboard.add(InlineKeyboardButton(text="💎 Выдать подписку", callback_data="admin_give_sub"))
    keyboard.add(InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast"))
    keyboard.adjust(1)
    
    await message.answer(
        f"🔐 <b>Админ-панель</b>\n\n"
        f"Выберите действие:",
        reply_markup=keyboard.as_markup()
    )


@admin_router.callback_query(F.data == "admin_stats")
async def admin_statistics(callback: types.CallbackQuery, session: AsyncSession):
    stats = await orm_get_statistics(session)
    
    text = (
        f"📊 <b>Статистика бота</b>\n\n"
        f"👥 Всего пользователей: <b>{stats['total_users']}</b>\n"
        f"💎 Активных подписок: <b>{stats['active_subscriptions']}</b>\n"
        f"📺 Всего каналов: <b>{stats['total_channels']}</b>\n"
        f"🚫 Заблокированных: <b>{stats['banned_users']}</b>"
    )
    
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back"))
    
    try:
        await callback.message.edit_text(
            text,
            reply_markup=keyboard.as_markup()
        )
    except:
        await callback.message.answer(
            text,
            reply_markup=keyboard.as_markup()
        )
    
    await callback.answer()


@admin_router.callback_query(F.data == "admin_price")
async def admin_price_menu(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    # Очищаем состояние, если оно было
    await state.clear()
    
    settings = await orm_get_subscription_settings(session)
    
    text = (
        f"💰 <b>Управление ценой подписки</b>\n\n"
        f"Текущая цена: <b>{settings.price:.0f}₽/месяц</b>\n\n"
        f"Отправьте новую цену в рублях:"
    )
    
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back"))
    
    try:
        await callback.message.edit_text(
            text,
            reply_markup=keyboard.as_markup()
        )
    except:
        await callback.message.answer(
            text,
            reply_markup=keyboard.as_markup()
        )
    
    await callback.answer()


# Обновленная функция для обработки цифр (только в состоянии None)
@admin_router.message(StateFilter(None), F.text.regexp(r'^\d+(\.\d+)?$'))
async def admin_set_price(message: types.Message, session: AsyncSession):
    try:
        price = float(message.text)
        if price < 0:
            await message.answer("❌ Цена не может быть отрицательной")
            return
        
        await orm_update_subscription_price(session, price)
        await message.answer(f"✅ Цена подписки обновлена: <b>{price:.0f}₽/месяц</b>")
    except ValueError:
        await message.answer("❌ Неверный формат цены. Используйте число (например: 50 или 99.99)")


@admin_router.callback_query(F.data == "admin_users")
async def admin_users_menu(callback: types.CallbackQuery, state: FSMContext):
    # Очищаем состояние
    await state.clear()
    
    text = (
        f"👥 <b>Управление пользователями</b>\n\n"
        f"Выберите действие:"
    )
    
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="🚫 Забанить пользователя", callback_data="admin_ban"))
    keyboard.add(InlineKeyboardButton(text="✅ Разбанить пользователя", callback_data="admin_unban"))
    keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back"))
    
    try:
        await callback.message.edit_text(
            text,
            reply_markup=keyboard.as_markup()
        )
    except:
        await callback.message.answer(
            text,
            reply_markup=keyboard.as_markup()
        )
    
    await callback.answer()


@admin_router.callback_query(F.data == "admin_ban")
async def admin_ban_start(callback: types.CallbackQuery, state: FSMContext):
    text = (
        f"🚫 <b>Забанить пользователя</b>\n\n"
        f"Отправьте ID пользователя в формате:\n"
        f"<code>USER_ID</code>\n\n"
        f"Пример: <code>123456789</code>"
    )
    
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="admin_users"))
    
    try:
        await callback.message.edit_text(
            text,
            reply_markup=keyboard.as_markup()
        )
    except:
        await callback.message.answer(
            text,
            reply_markup=keyboard.as_markup()
        )
    
    await state.set_state(AdminBanUser.waiting_for_user_id)
    await callback.answer()


@admin_router.message(StateFilter(AdminBanUser.waiting_for_user_id))
async def admin_ban_user_id(message: types.Message, state: FSMContext, session: AsyncSession):
    try:
        user_id = int(message.text.strip())
        user = await orm_get_user(user_id=user_id, session=session)
        
        if not user:
            await message.answer(f"❌ Пользователь <code>{user_id}</code> не найден")
            await state.clear()
            return
        
        if user.is_banned:
            await message.answer(f"⚠️ Пользователь <code>{user_id}</code> уже заблокирован")
            await state.clear()
            return
        
        await state.update_data(user_id=user_id)
        await state.set_state(AdminBanUser.waiting_for_reason)
        
        await message.answer(
            f"👤 Пользователь найден: <code>{user_id}</code>\n\n"
            f"Отправьте причину бана:"
        )
    except ValueError:
        await message.answer("❌ Неверный формат. Отправьте только ID пользователя (число)")


@admin_router.message(StateFilter(AdminBanUser.waiting_for_reason))
async def admin_ban_reason(message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot):
    reason = message.text.strip()
    data = await state.get_data()
    user_id = data.get("user_id")
    
    if not user_id:
        await message.answer("❌ Ошибка: не найден ID пользователя")
        await state.clear()
        return
    
    user = await orm_ban_user(session, user_id, reason)
    
    if user:
        await message.answer(
            f"✅ Пользователь <code>{user_id}</code> заблокирован\n\n"
            f"📝 Причина: {reason}"
        )
        
        try:
            await bot.send_message(
                chat_id=user_id,
                text=(
                    f"🚫 <b>Вы были заблокированы</b>\n\n"
                    f"📝 <b>Причина:</b> {reason}\n\n"
                    f"Если вы считаете, что это ошибка, обратитесь в поддержку."
                )
            )
        except Exception as e:
            print(f"⚠️ Не удалось отправить уведомление пользователю {user_id}: {e}")
    else:
        await message.answer(f"❌ Пользователь <code>{user_id}</code> не найден")
    
    await state.clear()


@admin_router.callback_query(F.data == "admin_unban")
async def admin_unban_start(callback: types.CallbackQuery, state: FSMContext):
    text = (
        f"✅ <b>Разбанить пользователя</b>\n\n"
        f"Отправьте ID пользователя в формате:\n"
        f"<code>USER_ID</code>\n\n"
        f"Пример: <code>123456789</code>"
    )
    
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="admin_users"))
    
    try:
        await callback.message.edit_text(
            text,
            reply_markup=keyboard.as_markup()
        )
    except:
        await callback.message.answer(
            text,
            reply_markup=keyboard.as_markup()
        )
    
    await state.set_state(AdminUnbanUser.waiting_for_user_id)
    await callback.answer()


@admin_router.message(StateFilter(AdminUnbanUser.waiting_for_user_id))
async def admin_unban_user_id(message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot):
    try:
        user_id = int(message.text.strip())
        user = await orm_unban_user(session, user_id)
        
        if user:
            await message.answer(f"✅ Пользователь <code>{user_id}</code> разблокирован")
            
            try:
                await bot.send_message(
                    chat_id=user_id,
                    text=(
                        f"✅ <b>Вы были разблокированы</b>\n\n"
                        f"Добро пожаловать обратно! Теперь вы можете использовать бота."
                    )
                )
            except Exception as e:
                print(f"⚠️ Не удалось отправить уведомление пользователю {user_id}: {e}")
        else:
            await message.answer(f"❌ Пользователь <code>{user_id}</code> не найден")
    except ValueError:
        await message.answer("❌ Неверный формат. Отправьте только ID пользователя (число)")
    
    await state.clear()


@admin_router.callback_query(F.data == "admin_give_sub")
async def admin_give_subscription(callback: types.CallbackQuery, state: FSMContext):
    text = (
        f"💎 <b>Выдача подписки</b>\n\n"
        f"Отправьте данные в формате:\n"
        f"<code>USER_ID КОЛИЧЕСТВО_ДНЕЙ</code>\n\n"
        f"Пример: <code>123456789 30</code>\n"
        f"Пример: <code>123456789 7</code>\n"
    )
    
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back"))
    
    try:
        await callback.message.edit_text(
            text,
            reply_markup=keyboard.as_markup()
        )
    except:
        await callback.message.answer(
            text,
            reply_markup=keyboard.as_markup()
        )
    
    await state.set_state(AdminGiveSubscription.waiting_for_user_id_and_days)
    await callback.answer()

@admin_router.message(StateFilter(AdminGiveSubscription.waiting_for_user_id_and_days))
async def admin_give_subscription_process(message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot):
    try:
        parts = message.text.strip().split()
        if len(parts) != 2:
            await message.answer(
                "❌ Неверный формат.\n\n"
                "Используйте: <code>USER_ID КОЛИЧЕСТВО_ДНЕЙ</code>\n"
                "Пример: <code>123456789 30</code>\n"
                "Пример: <code>123456789 999</code>"
            )
            return
        
        user_id = int(parts[0])
        days = int(parts[1])
        
        if days <= 0:
            await message.answer("❌ Количество дней должно быть больше 0")
            return
        
        
        user = await orm_get_user(user_id=user_id, session=session)
        if not user:
            await message.answer(f"❌ Пользователь <code>{user_id}</code> не найден")
            await state.clear()
            return
        
        subscription = await orm_create_subscription(session, user_id, days=days)
        
        if subscription:
            end_date = subscription.end_date.strftime('%d.%m.%Y %H:%M')
            
            await message.answer(
                f"✅ Подписка выдана пользователю <code>{user_id}</code>\n\n"
                f"📅 Срок: <b>{days} дней</b>\n"
                f"📆 Действует до: <b>{end_date}</b>"
            )
            
            try:
                await bot.send_message(
                    chat_id=user_id,
                    text=(
                        f"💎 <b>Вам выдана подписка!</b>\n\n"
                        f"📅 Срок: <b>{days} дней</b>\n"
                        f"📆 Действует до: <b>{end_date}</b>\n\n"
                        f"✅ Теперь вы можете отслеживать неограниченное количество каналов!"
                    )
                )
            except Exception as e:
                print(f"⚠️ Не удалось отправить уведомление пользователю {user_id}: {e}")
        else:
            await message.answer(f"❌ Ошибка при выдаче подписки")
    except ValueError:
        await message.answer(
            "❌ Неверный формат.\n\n"
            "Используйте: <code>USER_ID КОЛИЧЕСТВО_ДНЕЙ</code>\n"
            "Пример: <code>123456789 30</code>"
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
    
    await state.clear()

@admin_router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_start(callback: types.CallbackQuery, state: FSMContext):
    text = (
        f"📢 <b>Рассылка сообщений</b>\n\n"
        f"Отправьте любое сообщение:\n"
        f"• Текст (можно с HTML-разметкой)\n"
        f"• Фото/Видео/Документ\n"
        f"• Голосовое сообщение\n\n"
        f"Сообщение будет отправлено всем активным пользователям бота."
    )
    
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back"))
    
    try:
        await callback.message.edit_text(
            text,
            reply_markup=keyboard.as_markup()
        )
    except:
        await callback.message.answer(
            text,
            reply_markup=keyboard.as_markup()
        )
    
    await state.set_state(AdminBroadcast.waiting_for_message)
    await callback.answer()


@admin_router.message(StateFilter(AdminBroadcast.waiting_for_message))
async def admin_broadcast_process(message: types.Message, state: FSMContext, session: AsyncSession):
    users = await orm_get_all_users(session)
    
    active_users = [user for user in users if not user.is_banned]
    
    if not active_users:
        await message.answer("❌ Нет активных пользователей для рассылки")
        await state.clear()
        return
    
    await state.update_data(
        message=message,
        active_users_count=len(active_users),
        active_users=[user.user_id for user in active_users]
    )
    
    await state.set_state(AdminBroadcast.confirm_message)
    
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="✅ Да, разослать", callback_data="confirm_broadcast"))
    keyboard.add(InlineKeyboardButton(text="❌ Нет, отменить", callback_data="cancel_broadcast"))
    keyboard.adjust(1)
    
    # В зависимости от типа сообщения, показываем разный предпросмотр
    if message.text:
        preview_text = message.text[:500] + "..." if len(message.text) > 500 else message.text
        preview = f"📢 <b>Предпросмотр рассылки</b>\n\n<b>Сообщение:</b>\n{preview_text}\n\n"
    elif message.photo:
        preview = f"📢 <b>Предпросмотр рассылки</b>\n\n<b>Тип:</b> Фото\n"
        if message.caption:
            preview += f"<b>Подпись:</b> {message.caption[:300]}\n\n"
        else:
            preview += "\n"
    elif message.video:
        preview = f"📢 <b>Предпросмотр рассылки</b>\n\n<b>Тип:</b> Видео\n"
        if message.caption:
            preview += f"<b>Подпись:</b> {message.caption[:300]}\n\n"
        else:
            preview += "\n"
    elif message.document:
        preview = f"📢 <b>Предпросмотр рассылки</b>\n\n<b>Тип:</b> Документ\n"
        if message.caption:
            preview += f"<b>Подпись:</b> {message.caption[:300]}\n\n"
        else:
            preview += "\n"
    elif message.voice:
        preview = f"📢 <b>Предпросмотр рассылки</b>\n\n<b>Тип:</b> Голосовое сообщение\n\n"
    else:
        preview = f"📢 <b>Предпросмотр рассылки</b>\n\n<b>Тип:</b> Другое\n\n"
    
    preview += f"<b>Получатели:</b> {len(active_users)} пользователей\n"
    preview += f"<b>Заблокированные:</b> {len(users) - len(active_users)} пользователей\n\n"
    preview += f"<b>Разослать сообщение?</b>"
    
    await message.answer(
        preview,
        reply_markup=keyboard.as_markup()
    )


@admin_router.callback_query(F.data == "confirm_broadcast", StateFilter(AdminBroadcast.confirm_message))
async def admin_broadcast_confirm(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession, bot: Bot):
    try:
        data = await state.get_data()
        broadcast_message = data.get("message")
        active_users = data.get("active_users", [])
        
        if not broadcast_message or not active_users:
            await callback.answer("❌ Данные для рассылки не найдены", show_alert=True)
            await state.clear()
            return
        
        await callback.message.edit_text(
            f"📢 <b>Начинаю рассылку...</b>\n\n"
            f"<b>Получателей:</b> {len(active_users)}\n"
            f"<b>Статус:</b> Ожидание..."
        )
        
        success_count = 0
        failed_count = 0

        for i, user_id in enumerate(active_users, 1):
            try:
                if broadcast_message.text:
                    await bot.send_message(
                        chat_id=user_id,
                        text=broadcast_message.text,
                        parse_mode="HTML",
                        disable_web_page_preview=True
                    )
                elif broadcast_message.photo:
                    photo = broadcast_message.photo[-1] 
                    await bot.send_photo(
                        chat_id=user_id,
                        photo=photo.file_id,
                        caption=broadcast_message.caption,
                        parse_mode="HTML"
                    )
                elif broadcast_message.video:
                    await bot.send_video(
                        chat_id=user_id,
                        video=broadcast_message.video.file_id,
                        caption=broadcast_message.caption,
                        parse_mode="HTML"
                    )
                elif broadcast_message.document:
                    await bot.send_document(
                        chat_id=user_id,
                        document=broadcast_message.document.file_id,
                        caption=broadcast_message.caption,
                        parse_mode="HTML"
                    )
                elif broadcast_message.voice:
                    await bot.send_voice(
                        chat_id=user_id,
                        voice=broadcast_message.voice.file_id,
                        caption=broadcast_message.caption,
                        parse_mode="HTML"
                    )
                
                success_count += 1
                
                if i % 10 == 0 or i == len(active_users):
                    try:
                        await callback.message.edit_text(
                            f"📢 <b>Рассылка в процессе...</b>\n\n"
                            f"<b>Отправлено:</b> {i}/{len(active_users)}\n"
                            f"<b>Успешно:</b> {success_count}\n"
                            f"<b>Ошибок:</b> {failed_count}\n"
                            f"<b>Осталось:</b> {len(active_users) - i}"
                        )
                    except:
                        pass
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                failed_count += 1
                print(f"❌ Ошибка при отправке пользователю {user_id}: {e}")
        
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="🔙 Назад в админку", callback_data="admin_back"))
        
        success_rate = (success_count/len(active_users)*100) if active_users else 0
        
        await callback.message.edit_text(
            f"✅ <b>Рассылка завершена!</b>\n\n"
            f"<b>Всего получателей:</b> {len(active_users)}\n"
            f"<b>✅ Успешно отправлено:</b> {success_count}\n"
            f"<b>❌ Ошибок:</b> {failed_count}\n"
            f"<b>📊 Процент успеха:</b> {success_rate:.1f}%",
            reply_markup=keyboard.as_markup()
        )
        
    except Exception as e:
        await callback.answer(f"❌ Ошибка при рассылке: {e}", show_alert=True)
        print(f"❌ Ошибка при рассылке: {e}")
    
    await state.clear()


@admin_router.callback_query(F.data == "cancel_broadcast", StateFilter(AdminBroadcast.confirm_message))
async def admin_broadcast_cancel(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"))
    keyboard.add(InlineKeyboardButton(text="💰 Управление ценой", callback_data="admin_price"))
    keyboard.add(InlineKeyboardButton(text="👥 Управление пользователями", callback_data="admin_users"))
    keyboard.add(InlineKeyboardButton(text="💎 Выдать подписку", callback_data="admin_give_sub"))
    keyboard.add(InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast"))
    keyboard.adjust(1)
    
    try:
        await callback.message.edit_text(
            f"🔐 <b>Админ-панель</b>\n\n"
            f"Выберите действие:",
            reply_markup=keyboard.as_markup()
        )
    except:
        await callback.message.answer(
            f"🔐 <b>Админ-панель</b>\n\n"
            f"Выберите действие:",
            reply_markup=keyboard.as_markup()
        )
    
    await callback.answer("❌ Рассылка отменена")


@admin_router.callback_query(F.data == "admin_back")
async def admin_back(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"))
    keyboard.add(InlineKeyboardButton(text="💰 Управление ценой", callback_data="admin_price"))
    keyboard.add(InlineKeyboardButton(text="👥 Управление пользователями", callback_data="admin_users"))
    keyboard.add(InlineKeyboardButton(text="💎 Выдать подписку", callback_data="admin_give_sub"))
    keyboard.add(InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast"))
    keyboard.adjust(1)
    
    try:
        await callback.message.edit_text(
            f"🔐 <b>Админ-панель</b>\n\n"
            f"Выберите действие:",
            reply_markup=keyboard.as_markup()
        )
    except:
        await callback.message.answer(
            f"🔐 <b>Админ-панель</b>\n\n"
            f"Выберите действие:",
            reply_markup=keyboard.as_markup()
        )
    
    await callback.answer()