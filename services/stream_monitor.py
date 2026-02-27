import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import orm_get_all_channels, orm_update_channel_status
from database.engine import session_maker
from services.twitch_checker import check_channel_status
from aiogram import Bot
import config


async def visit_single_channel(channel, bot: Bot, session: AsyncSession):
    try:
        print(f"\n{'='*60}")
        print(f"🎯 Обработка канала: {channel.channel_name} (ID: {channel.id})")
        print(f"{'='*60}")
        
        previous_status = channel.is_live
        
        print(f"🚀 Проверяю статус канала: {channel.channel_name}")
        success, checked_channel_name, status, viewer_count = check_channel_status(channel.channel_url)
        
        if not success:
            print(f"⚠️ Не удалось проверить канал {channel.channel_name}, статус не изменен")
            return
        
        if success:
            new_status = (status == "online")
            
            channel.last_checked = datetime.now()
            channel.is_live = new_status
            await session.commit()
            print(f"💾 Время проверки и статус обновлены в БД для канала: {checked_channel_name} (is_live={new_status})")
            
            status_changed = (previous_status != new_status)
            
            if status_changed:
                print(f"🔄 Статус изменился! Было: {'ONLINE' if previous_status else 'OFFLINE'}, Стало: {'ONLINE' if new_status else 'OFFLINE'}")
                
                if new_status:
                    status_emoji = "🟢"
                    status_text = "ONLINE"
                    viewer_info = f"\n👥 <b>Зрителей: {viewer_count}</b>" if viewer_count > 0 else ""
                    notification_text = f"🔴 <b>СТРИМ НАЧАЛСЯ!</b>{viewer_info}"
                else:
                    status_emoji = "🔴"
                    status_text = "OFFLINE"
                    notification_text = "📴 <b>СТРИМ ЗАКОНЧИЛСЯ</b>"
                
                if channel.users:
                    try:
                        from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
                        from aiogram.utils.keyboard import InlineKeyboardBuilder
                        from kbrds.reply import menu_reply_markup
                        
                        keyboard = InlineKeyboardBuilder()
                        keyboard.add(InlineKeyboardButton(
                            text="🔗 Открыть канал",
                            url=channel.channel_url
                        ))
                        
                        for user in channel.users:
                            try:
                                await bot.send_message(
                                    chat_id=user.user_id,
                                    text=(
                                        f"{notification_text}\n\n"
                                        f"📺 <b>Канал: {checked_channel_name}</b>\n"
                                        f"{status_emoji} <b>Статус: {status_text}</b>"
                                    ),
                                    reply_markup=keyboard.as_markup(),
                                    parse_mode="HTML",
                                    disable_web_page_preview=True
                                )
                                await bot.send_message(
                                    chat_id=user.user_id,
                                    text="💎 Используйте кнопку ниже для возврата в меню:",
                                    reply_markup=menu_reply_markup
                                )
                                print(f"✅ Уведомление отправлено пользователю {user.user_id} для канала {checked_channel_name} (статус: {status_text})")
                            except Exception as e:
                                print(f"❌ Ошибка при отправке уведомления пользователю {user.user_id}: {e}")
                    except Exception as e:
                        print(f"❌ Ошибка при отправке уведомлений: {e}")
            else:
                print(f"ℹ️ Статус не изменился для канала {checked_channel_name} (статус: {'ONLINE' if new_status else 'OFFLINE'})")
        else:
            print(f"❌ Не удалось открыть канал {channel.channel_name}")
            
    except Exception as e:
        print(f"❌ Ошибка при обработке канала {channel.channel_name}: {e}")
        import traceback
        traceback.print_exc()


async def check_channels_loop(bot: Bot):
    while True:
        try:
            async with session_maker() as session:
                channels = await orm_get_all_channels(session=session)
                
                if not channels:
                    print("Нет каналов для проверки")
                    await asyncio.sleep(60)
                    continue
                
                print(f"📊 Найдено {len(channels)} каналов для проверки")
                print(f"🔄 Начинаю проверку каналов через API...\n")
                
                successful = 0
                skipped = 0
                failed = 0
                
                for channel in channels:
                    try:
                        if channel.last_checked:
                            time_diff = datetime.now() - channel.last_checked
                            seconds_passed = time_diff.total_seconds()
                            if seconds_passed < 120:
                                print(f"⏭️ Пропускаю канал {channel.channel_name} - прошло только {seconds_passed:.0f} секунд")
                                skipped += 1
                                continue
                        
                        try:
                            await visit_single_channel(
                                channel=channel,
                                bot=bot,
                                session=session
                            )
                            successful += 1
                        except Exception as e:
                            print(f"❌ Ошибка при обработке канала {channel.channel_name}: {e}")
                            failed += 1
                            import traceback
                            traceback.print_exc()
                    except Exception as e:
                        print(f"❌ Общая ошибка при обработке канала {channel.channel_name}: {e}")
                        failed += 1
                        import traceback
                        traceback.print_exc()
                
                print(f"\n{'='*60}")
                print(f"✅ Проверка завершена!")
                print(f"📈 Успешно обработано: {successful}, ⏭️ Пропущено: {skipped}, ❌ Ошибок: {failed}")
                print(f"{'='*60}\n")
                
        except Exception as e:
            print(f"❌ Ошибка в цикле проверки каналов: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await asyncio.sleep(10)


async def check_and_notify_streams(bot: Bot):
    print("Запуск мониторинга стримов...")
    await check_channels_loop(bot)


async def start_monitoring(bot: Bot):
    print("Инициализация мониторинга стримов...")
    asyncio.create_task(check_and_notify_streams(bot))
