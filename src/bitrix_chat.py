import os

import requests
from dotenv import load_dotenv
from requests.exceptions import ConnectTimeout

from loggers import logger


class BitrixChat:
    """Класс для работы с чатами в системе Bitrix24"""

    def __init__(self) -> None:
        """
        Инициализирует объект BitrixChat, загружая конфигурационные переменные из окружения.
        """
        load_dotenv()
        self.count = 0
        self.admin_id = int(os.getenv("ADMIN_ID"))
        self.__bot_id = int(os.getenv("BOT_ID"))
        self.__hook = os.getenv("HOOK")
        self._portal_name = os.getenv("PORTAL_NAME")

    async def get_all_chat(self) -> list | list[dict]:
        """
        Получает список всех новых сообщений обрабатываемого нами пользователя.

        :return: Список словарей, представляющих информацию о сообщениях.
        """
        data = []
        params = {
            "SKIP_OPENLINES": "Y",
            "SKIP_DIALOG": "N",
            "SKIP_CHAT": "Y",
        }
        url = f"https://{self._portal_name}/rest/{self.__bot_id}/{self.__hook}/im.recent.get.json"
        try:
            response = requests.get(url=url, params=params)
            if response.status_code == 200:
                for chat in response.json()["result"]:
                    chat_id = chat["id"]
                    author_id = chat["message"]["author_id"]
                    text = chat["message"]["text"]
                    if text and author_id != self.__bot_id and chat_id == author_id:
                        chat_dict = {
                            "id": chat_id,
                            "title": chat["title"],
                            "author_id": author_id,
                            "text": text,
                            "date": chat["message"]["date"],
                        }
                        data.append(chat_dict)
        except ConnectTimeout as ex_ct:
            logger.warning(f"{ex_ct.__class__.__name__}: {ex_ct}")
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
        finally:
            return data

    async def send_message(self, author_id: int, message: str) -> bool:
        """
        Отправляет сообщение в чат в системе Bitrix24.

        :params author_id: Идентификатор пользователя, кому мы отправим сообщение.
        :params message: Текст сообщения.

        :return: True, если сообщение успешно отправлено, False в противном случае.
        """
        status = False
        try:
            url = f"https://{self._portal_name}/rest/{self.__bot_id}/{self.__hook}/im.message.add.json"
            params = {"DIALOG_ID": author_id, "MESSAGE": message}
            response = requests.get(url=url, params=params)
            if response.status_code == 200:
                status = True
        except ConnectTimeout as ex_ct:
            logger.warning(f"{ex_ct.__class__.__name__}: {ex_ct}")
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
        finally:
            return status
