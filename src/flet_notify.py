import logging
from typing import Callable, Optional, List
from enum import Enum
from dataclasses import dataclass, field
from flet import Page, PagePlatform


logging.basicConfig(level=logging.DEBUG, format="[%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("FletNotify")


class NotificationImportance(Enum):
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class NotificationStyle(Enum):
    SIMPLE = "simple"
    PROGRESS = "progress"
    INBOX = "inbox"
    BIG_TEXT = "big_text"
    LARGE_ICON = "large_icon"
    BIG_PICTURE = "big_picture"
    BOTH_IMAGES = "both_imgs"


@dataclass
class NotificationButton:
    text: str
    callback: Callable[[], None]


@dataclass
class NotificationConfig:
    title: str
    message: str
    channel_id: str = "default"
    channel_name: str = "Padrão"
    importance: NotificationImportance = NotificationImportance.URGENT
    style: NotificationStyle = NotificationStyle.SIMPLE
    notification_id: Optional[str] = None
    app_icon: Optional[str] = None
    buttons: List[NotificationButton] = field(default_factory=list)
    progress_current: int = 0
    progress_max: int = 100
    large_icon_path: Optional[str] = None
    big_picture_path: Optional[str] = None
    big_text_body: Optional[str] = None
    inbox_lines: List[str] = field(default_factory=list)


class FletNotifyException(Exception):
    pass


class PermissionDeniedException(FletNotifyException):
    pass


class PlatformNotSupportedException(FletNotifyException):
    pass


class AndroidNotifyNotAvailableException(FletNotifyException):
    pass


def _check_android_notify_available():
    try:
        import android_notify

        logger.debug("android-notify está disponível")
        return True
    except ImportError:
        logger.error("android-notify não está disponível")
        return False


def _get_android_notification_class():
    try:
        from android_notify import Notification

        return Notification
    except ImportError as e:
        logger.error(f"Falha ao importar Notification: {e}")
        raise AndroidNotifyNotAvailableException(
            "android-notify não está instalado ou configurado. "
            "Verifique se está em [tool.flet.android] dependencies"
        )


def _get_notification_handler_class():
    try:
        from android_notify import NotificationHandler

        return NotificationHandler
    except ImportError as e:
        logger.error(f"Falha ao importar NotificationHandler: {e}")
        raise AndroidNotifyNotAvailableException(
            "android-notify não está instalado ou configurado"
        )


class FletNotification:

    def __init__(self, page: Page, config: NotificationConfig):
        if not page:
            raise ValueError("Page não pode ser None")

        self.page = page
        self.config = config
        self._notification = None
        self._sent = False

        logger.debug(f"FletNotification criada: {config.title}")

        if self.page.platform != PagePlatform.ANDROID:
            logger.warning(f"Plataforma não suportada: {self.page.platform}")
            raise PlatformNotSupportedException(
                f"FletNotify suporta apenas Android (atual: {self.page.platform})"
            )

    def send(
        self,
        silent: bool = False,
        persistent: bool = False,
        close_on_click: bool = True,
    ) -> "FletNotification":
        try:
            logger.info(f"Tentando enviar notificação: {self.config.title}")

            Notification = _get_android_notification_class()

            kwargs = {
                "title": self.config.title,
                "message": self.config.message,
                "channel_id": self.config.channel_id,
                "channel_name": self.config.channel_name,
                "style": self.config.style.value,
            }

            if self.config.notification_id:
                kwargs["name"] = self.config.notification_id

            if self.config.app_icon:
                kwargs["app_icon"] = self.config.app_icon

            if self.config.style == NotificationStyle.PROGRESS:
                kwargs["progress_current_value"] = self.config.progress_current
                kwargs["progress_max_value"] = self.config.progress_max

            elif self.config.style == NotificationStyle.LARGE_ICON:
                kwargs["large_icon_path"] = self.config.large_icon_path

            elif self.config.style == NotificationStyle.BIG_PICTURE:
                kwargs["big_picture_path"] = self.config.big_picture_path

            elif self.config.style == NotificationStyle.BOTH_IMAGES:
                kwargs["large_icon_path"] = self.config.large_icon_path
                kwargs["big_picture_path"] = self.config.big_picture_path

            elif self.config.style == NotificationStyle.BIG_TEXT:
                kwargs["body"] = self.config.big_text_body

            elif self.config.style == NotificationStyle.INBOX:
                kwargs["lines_txt"] = "\n".join(self.config.inbox_lines)

            logger.debug(f"Criando notificação com kwargs: {kwargs}")
            self._notification = Notification(**kwargs)

            for btn in self.config.buttons:
                logger.debug(f"Adicionando botão: {btn.text}")
                self._notification.addButton(btn.text, btn.callback)

            logger.debug(
                f"Enviando notificação (silent={silent}, persistent={persistent})"
            )
            self._notification.send(
                silent=silent, persistent=persistent, close_on_click=close_on_click
            )

            self._sent = True
            logger.info(f"✅ Notificação enviada com sucesso: {self.config.title}")

            return self

        except AndroidNotifyNotAvailableException:
            raise
        except Exception as e:
            logger.error(
                f"❌ Erro ao enviar notificação: {type(e).__name__}: {e}", exc_info=True
            )
            raise FletNotifyException(f"Falha ao enviar notificação: {e}")

    def update_title(self, new_title: str) -> "FletNotification":
        if not self._sent or not self._notification:
            raise FletNotifyException("Notificação ainda não foi enviada")

        self.config.title = new_title
        self._notification.updateTitle(new_title)
        logger.debug(f"Título atualizado: {new_title}")
        return self

    def update_message(self, new_message: str) -> "FletNotification":
        if not self._sent or not self._notification:
            raise FletNotifyException("Notificação ainda não foi enviada")

        self.config.message = new_message
        self._notification.updateMessage(new_message)
        logger.debug(f"Mensagem atualizada: {new_message}")
        return self

    def update_progress(
        self, current: int, title: Optional[str] = None, message: Optional[str] = None
    ) -> "FletNotification":
        if not self._sent or not self._notification:
            raise FletNotifyException("Notificação ainda não foi enviada")

        if self.config.style != NotificationStyle.PROGRESS:
            raise FletNotifyException(
                "update_progress requer NotificationStyle.PROGRESS"
            )

        self.config.progress_current = current

        kwargs = {"current_value": current}
        if title:
            kwargs["title"] = title
            self.config.title = title
        if message:
            kwargs["message"] = message
            self.config.message = message

        self._notification.updateProgressBar(**kwargs)
        logger.debug(f"Progresso atualizado: {current}/{self.config.progress_max}")
        return self

    def show_infinite_progress(self) -> "FletNotification":
        if not self._sent or not self._notification:
            raise FletNotifyException("Notificação ainda não foi enviada")

        self._notification.showInfiniteProgressBar()
        logger.debug("Barra de progresso infinita ativada")
        return self

    def remove_progress(
        self, message: Optional[str] = None, show_briefly: bool = True
    ) -> "FletNotification":
        if not self._sent or not self._notification:
            raise FletNotifyException("Notificação ainda não foi enviada")

        self._notification.removeProgressBar(
            message=message, show_on_update=show_briefly
        )
        logger.debug("Barra de progresso removida")
        return self

    def cancel(self) -> None:
        if not self._sent or not self._notification:
            raise FletNotifyException("Notificação ainda não foi enviada")

        self._notification.cancel()
        logger.info(f"Notificação cancelada: {self.config.title}")

    def refresh(self) -> "FletNotification":
        if not self._sent or not self._notification:
            raise FletNotifyException("Notificação ainda não foi enviada")

        self._notification.refresh()
        logger.debug("Notificação atualizada")
        return self


class FletNotify:

    _instances = {}

    def __new__(cls, page: Page):
        page_id = id(page)
        if page_id not in cls._instances:
            logger.debug(f"Criando nova instância FletNotify para page {page_id}")
            instance = super().__new__(cls)
            cls._instances[page_id] = instance
        else:
            logger.debug(
                f"Reutilizando instância FletNotify existente para page {page_id}"
            )
        return cls._instances[page_id]

    def __init__(self, page: Page):
        if not page:
            raise ValueError("Page não pode ser None")

        page_id = id(page)

        if (
            not hasattr(self, "_initialized")
            or getattr(self, "_page_id", None) != page_id
        ):
            logger.info(f"Inicializando FletNotify para plataforma: {page.platform}")

            self.page = page
            self._page_id = page_id
            self._initialized = True

            if self.page.platform != PagePlatform.ANDROID:
                logger.error(f"Plataforma não suportada: {self.page.platform}")
                raise PlatformNotSupportedException(
                    f"FletNotify suporta apenas Android (atual: {self.page.platform})"
                )

            if not _check_android_notify_available():
                logger.error(
                    "android-notify não disponível - notificações não funcionarão"
                )

            logger.info("✅ FletNotify inicializado com sucesso")

    def check_permission(self) -> bool:
        logger.debug("Verificando permissão de notificação")

        try:
            import os
            from jnius import autoclass

            activity_host_class = os.getenv("MAIN_ACTIVITY_HOST_CLASS_NAME")
            if not activity_host_class:
                logger.error("MAIN_ACTIVITY_HOST_CLASS_NAME não definida")
                return False

            logger.debug(f"Activity host class: {activity_host_class}")

            activity = autoclass(activity_host_class).mActivity
            BuildVersion = autoclass("android.os.Build$VERSION")
            ManifestPermission = autoclass("android.Manifest$permission")
            ContextCompat = autoclass("androidx.core.content.ContextCompat")
            PackageManager = autoclass("android.content.pm.PackageManager")

            sdk_int = BuildVersion.SDK_INT
            logger.debug(f"Android SDK: {sdk_int}")

            if sdk_int >= 33:
                permission = ManifestPermission.POST_NOTIFICATIONS
                check = ContextCompat.checkSelfPermission(activity, permission)
                granted = check == PackageManager.PERMISSION_GRANTED
            else:
                granted = True

            logger.info(
                f"Permissão de notificação: {'✅ concedida' if granted else '❌ negada'}"
            )
            return granted

        except Exception as e:
            logger.error(
                f"❌ Erro ao verificar permissão: {type(e).__name__}: {e}",
                exc_info=True,
            )
            return False

    def request_permission(self) -> bool:
        logger.info("Solicitando permissão de notificação")

        try:
            import os
            from jnius import autoclass

            activity_host_class = os.getenv("MAIN_ACTIVITY_HOST_CLASS_NAME")
            if not activity_host_class:
                logger.error("MAIN_ACTIVITY_HOST_CLASS_NAME não definida")
                raise PermissionDeniedException("Activity host class não encontrada")

            activity = autoclass(activity_host_class).mActivity
            BuildVersion = autoclass("android.os.Build$VERSION")
            ManifestPermission = autoclass("android.Manifest$permission")
            ActivityCompat = autoclass("androidx.core.app.ActivityCompat")

            sdk_int = BuildVersion.SDK_INT
            logger.debug(f"Android SDK: {sdk_int}")

            if sdk_int >= 33:
                permission = ManifestPermission.POST_NOTIFICATIONS
                ActivityCompat.requestPermissions(activity, [permission], 101)
                logger.info("✅ Diálogo de permissão exibido")
                return True

            logger.info("✅ Permissão não necessária (SDK < 33)")
            return True

        except Exception as e:
            logger.error(
                f"❌ Erro ao solicitar permissão: {type(e).__name__}: {e}",
                exc_info=True,
            )
            raise PermissionDeniedException(f"Falha ao solicitar permissão: {e}")

    def create(
        self,
        title: str,
        message: str,
        channel_id: str = "default",
        channel_name: str = "Padrão",
        importance: NotificationImportance = NotificationImportance.URGENT,
        notification_id: Optional[str] = None,
    ) -> "NotificationBuilder":
        logger.debug(f"Criando builder para: {title}")
        return NotificationBuilder(
            page=self.page,
            config=NotificationConfig(
                title=title,
                message=message,
                channel_id=channel_id,
                channel_name=channel_name,
                importance=importance,
                notification_id=notification_id,
            ),
        )

    def send(
        self,
        title: str,
        message: str,
        channel_id: str = "default",
        silent: bool = False,
        persistent: bool = False,
    ) -> FletNotification:
        logger.info(f"Enviando notificação simples: {title}")
        return self.create(title=title, message=message, channel_id=channel_id).send(
            silent=silent, persistent=persistent
        )

    @staticmethod
    def create_channel(
        channel_id: str,
        channel_name: str,
        description: str = "",
        importance: NotificationImportance = NotificationImportance.URGENT,
    ) -> None:
        logger.info(f"Criando canal: {channel_name} ({channel_id})")

        try:
            Notification = _get_android_notification_class()

            Notification.createChannel(
                id=channel_id,
                name=channel_name,
                description=description,
                importance=importance.value,
            )
            logger.info(f"✅ Canal criado: {channel_name}")

        except AndroidNotifyNotAvailableException:
            raise
        except Exception as e:
            logger.error(
                f"❌ Erro ao criar canal: {type(e).__name__}: {e}", exc_info=True
            )
            raise FletNotifyException(f"Falha ao criar canal: {e}")

    @staticmethod
    def delete_channel(channel_id: str) -> None:
        logger.info(f"Deletando canal: {channel_id}")

        try:
            Notification = _get_android_notification_class()
            Notification.deleteChannel(channel_id)
            logger.info(f"✅ Canal deletado: {channel_id}")

        except AndroidNotifyNotAvailableException:
            raise

    @staticmethod
    def delete_all_channels() -> None:
        logger.info("Deletando todos os canais")

        try:
            Notification = _get_android_notification_class()
            Notification.deleteAllChannel()
            logger.info("✅ Todos os canais deletados")

        except AndroidNotifyNotAvailableException:
            raise

    @staticmethod
    def cancel_all() -> None:
        logger.info("Cancelando todas as notificações")

        try:
            Notification = _get_android_notification_class()
            Notification.cancelAll()
            logger.info("✅ Todas as notificações canceladas")

        except AndroidNotifyNotAvailableException:
            raise

    @staticmethod
    def get_opened_notification() -> Optional[str]:
        logger.debug("Verificando qual notificação abriu o app")

        try:
            NotificationHandler = _get_notification_handler_class()
            name = NotificationHandler.get_name()

            if name:
                logger.info(f"✅ App aberto pela notificação: {name}")
            else:
                logger.debug("App não foi aberto por notificação")

            return name

        except AndroidNotifyNotAvailableException:
            raise


class NotificationBuilder:

    def __init__(self, page: Page, config: NotificationConfig):
        self.page = page
        self.config = config
        logger.debug(f"NotificationBuilder criado: {config.title}")

    def set_icon(self, path: str) -> "NotificationBuilder":
        self.config.app_icon = path
        logger.debug(f"Ícone definido: {path}")
        return self

    def add_button(
        self, text: str, callback: Callable[[], None]
    ) -> "NotificationBuilder":
        if len(self.config.buttons) >= 3:
            raise FletNotifyException("Máximo de 3 botões por notificação")

        self.config.buttons.append(NotificationButton(text, callback))
        logger.debug(f"Botão adicionado: {text}")
        return self

    def with_progress(
        self, current: int = 0, max_value: int = 100
    ) -> "NotificationBuilder":
        self.config.style = NotificationStyle.PROGRESS
        self.config.progress_current = current
        self.config.progress_max = max_value
        logger.debug(f"Progress bar configurado: {current}/{max_value}")
        return self

    def set_large_icon(self, path: str) -> "NotificationBuilder":
        if self.config.big_picture_path:
            self.config.style = NotificationStyle.BOTH_IMAGES
        else:
            self.config.style = NotificationStyle.LARGE_ICON
        self.config.large_icon_path = path
        logger.debug(f"Large icon definido: {path}")
        return self

    def set_big_picture(self, path: str) -> "NotificationBuilder":
        if self.config.large_icon_path:
            self.config.style = NotificationStyle.BOTH_IMAGES
        else:
            self.config.style = NotificationStyle.BIG_PICTURE
        self.config.big_picture_path = path
        logger.debug(f"Big picture definido: {path}")
        return self

    def set_big_text(self, body: str) -> "NotificationBuilder":
        self.config.style = NotificationStyle.BIG_TEXT
        self.config.big_text_body = body
        logger.debug(f"Big text definido ({len(body)} chars)")
        return self

    def add_line(self, text: str) -> "NotificationBuilder":
        self.config.style = NotificationStyle.INBOX
        self.config.inbox_lines.append(text)
        logger.debug(f"Linha adicionada: {text}")
        return self

    def set_lines(self, lines: List[str]) -> "NotificationBuilder":
        self.config.style = NotificationStyle.INBOX
        self.config.inbox_lines = lines
        logger.debug(f"{len(lines)} linhas definidas")
        return self

    def send(
        self,
        silent: bool = False,
        persistent: bool = False,
        close_on_click: bool = True,
    ) -> FletNotification:
        notification = FletNotification(self.page, self.config)
        return notification.send(silent, persistent, close_on_click)
