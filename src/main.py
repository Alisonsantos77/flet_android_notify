import asyncio
import flet as ft
from flet_notify import FletNotify, NotificationImportance, FletNotifyException


class NotificationDemo:

    def __init__(self, page: ft.Page):
        self.page = page
        self.notifier = None
        self.notification_count = 0
        self.has_permission = False
        self.dev_mode = page.platform != ft.PagePlatform.ANDROID

        self.counter_text_ref = ft.Ref[ft.Text]()
        self.snackbar_ref = ft.Ref[ft.SnackBar]()

    async def initialize(self):
        self.page.title = "Notificações"
        self.page.scroll = ft.ScrollMode.AUTO
        self.page.padding = 0

        self.page.overlay.append(
            ft.SnackBar(
                ref=self.snackbar_ref,
                content=ft.Text(""),
                duration=2000,
                behavior=ft.SnackBarBehavior.FLOATING,
                margin=ft.margin.all(10),
            )
        )

        if self.dev_mode:
            self.has_permission = True
        else:
            try:
                self.notifier = FletNotify(self.page)
                self.has_permission = self.notifier.check_permission()
            except Exception as e:
                pass

        self.page.floating_action_button = ft.FloatingActionButton(
            icon=ft.Icons.DELETE_SWEEP,
            on_click=self._cancel_all_notifications,
            tooltip="Limpar todas as notificações",
        )

        self.page.add(self.build())

        if self.dev_mode:
            self._show_snack(
                f"⚠️ Modo desenvolvimento: executando em {self.page.platform.value}",
                error=False,
            )

        self.page.update()

    def build(self):
        return ft.Column(
            [
                self._build_app_bar(),
                ft.Container(
                    content=ft.Column(
                        [
                            self._build_simple_section(),
                            self._build_progress_section(),
                            self._build_buttons_section(),
                            self._build_images_section(),
                            self._build_text_section(),
                            self._build_advanced_section(),
                            ft.Container(height=80),
                        ]
                    ),
                    padding=20,
                ),
            ]
        )

    def _build_app_bar(self):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, size=28),
                    ft.Text("Notificações", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.SEND, size=20),
                            ft.Text(
                                ref=self.counter_text_ref,
                                value="0",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        spacing=5,
                    ),
                ],
                spacing=10,
            ),
            padding=ft.padding.symmetric(horizontal=20, vertical=15),
        )

    def _build_simple_section(self):
        return ft.ExpansionTile(
            title=ft.Text("📨 Notificações Simples"),
            subtitle=ft.Text("Básicas, silenciosas e persistentes"),
            initially_expanded=True,
            controls=[
                ft.Container(
                    content=ft.ResponsiveRow(
                        [
                            ft.Column(
                                col={"xs": 12, "sm": 6, "md": 4},
                                controls=[
                                    ft.OutlinedButton(
                                        "Normal",
                                        icon=ft.Icons.NOTIFICATIONS,
                                        on_click=self._send_simple_normal,
                                        expand=True,
                                    )
                                ],
                            ),
                            ft.Column(
                                col={"xs": 12, "sm": 6, "md": 4},
                                controls=[
                                    ft.OutlinedButton(
                                        "Silenciosa",
                                        icon=ft.Icons.NOTIFICATIONS_OFF,
                                        on_click=self._send_simple_silent,
                                        expand=True,
                                    )
                                ],
                            ),
                            ft.Column(
                                col={"xs": 12, "sm": 6, "md": 4},
                                controls=[
                                    ft.OutlinedButton(
                                        "Persistente",
                                        icon=ft.Icons.PUSH_PIN,
                                        on_click=self._send_simple_persistent,
                                        expand=True,
                                    )
                                ],
                            ),
                        ]
                    ),
                    padding=10,
                )
            ],
        )

    def _build_progress_section(self):
        return ft.ExpansionTile(
            title=ft.Text("📊 Progress Bar"),
            subtitle=ft.Text("Determinado e indeterminado"),
            controls=[
                ft.Container(
                    content=ft.ResponsiveRow(
                        [
                            ft.Column(
                                col={"xs": 12, "sm": 6},
                                controls=[
                                    ft.OutlinedButton(
                                        "Determinado (0-100%)",
                                        icon=ft.Icons.DOWNLOADING,
                                        on_click=self._send_progress_determinate,
                                        expand=True,
                                    )
                                ],
                            ),
                            ft.Column(
                                col={"xs": 12, "sm": 6},
                                controls=[
                                    ft.OutlinedButton(
                                        "Indeterminado",
                                        icon=ft.Icons.AUTORENEW,
                                        on_click=self._send_progress_indeterminate,
                                        expand=True,
                                    )
                                ],
                            ),
                        ]
                    ),
                    padding=10,
                )
            ],
        )

    def _build_buttons_section(self):
        return ft.ExpansionTile(
            title=ft.Text("🎮 Com Botões de Ação"),
            subtitle=ft.Text("Interatividade com callbacks"),
            controls=[
                ft.Container(
                    content=ft.ResponsiveRow(
                        [
                            ft.Column(
                                col={"xs": 12, "sm": 6, "md": 4},
                                controls=[
                                    ft.OutlinedButton(
                                        "1 Botão",
                                        icon=ft.Icons.TOUCH_APP,
                                        on_click=self._send_with_one_button,
                                        expand=True,
                                    )
                                ],
                            ),
                            ft.Column(
                                col={"xs": 12, "sm": 6, "md": 4},
                                controls=[
                                    ft.OutlinedButton(
                                        "2 Botões",
                                        icon=ft.Icons.SWIPE,
                                        on_click=self._send_with_two_buttons,
                                        expand=True,
                                    )
                                ],
                            ),
                            ft.Column(
                                col={"xs": 12, "sm": 6, "md": 4},
                                controls=[
                                    ft.OutlinedButton(
                                        "3 Botões",
                                        icon=ft.Icons.GRID_VIEW,
                                        on_click=self._send_with_three_buttons,
                                        expand=True,
                                    )
                                ],
                            ),
                        ]
                    ),
                    padding=10,
                )
            ],
        )

    def _build_images_section(self):
        return ft.ExpansionTile(
            title=ft.Text("🖼️ Com Imagens"),
            subtitle=ft.Text("Large icon, big picture e ambos"),
            controls=[
                ft.Container(
                    content=ft.ResponsiveRow(
                        [
                            ft.Column(
                                col={"xs": 12, "sm": 6, "md": 4},
                                controls=[
                                    ft.OutlinedButton(
                                        "Large Icon",
                                        icon=ft.Icons.ACCOUNT_CIRCLE,
                                        on_click=self._send_with_large_icon,
                                        expand=True,
                                    )
                                ],
                            ),
                            ft.Column(
                                col={"xs": 12, "sm": 6, "md": 4},
                                controls=[
                                    ft.OutlinedButton(
                                        "Big Picture",
                                        icon=ft.Icons.IMAGE,
                                        on_click=self._send_with_big_picture,
                                        expand=True,
                                    )
                                ],
                            ),
                            ft.Column(
                                col={"xs": 12, "sm": 6, "md": 4},
                                controls=[
                                    ft.OutlinedButton(
                                        "Ambas Imagens",
                                        icon=ft.Icons.COLLECTIONS,
                                        on_click=self._send_with_both_images,
                                        expand=True,
                                    )
                                ],
                            ),
                        ]
                    ),
                    padding=10,
                )
            ],
        )

    def _build_text_section(self):
        return ft.ExpansionTile(
            title=ft.Text("📝 Estilos de Texto"),
            subtitle=ft.Text("Inbox e big text"),
            controls=[
                ft.Container(
                    content=ft.ResponsiveRow(
                        [
                            ft.Column(
                                col={"xs": 12, "sm": 6},
                                controls=[
                                    ft.OutlinedButton(
                                        "Inbox Style",
                                        icon=ft.Icons.INBOX,
                                        on_click=self._send_inbox_style,
                                        expand=True,
                                    )
                                ],
                            ),
                            ft.Column(
                                col={"xs": 12, "sm": 6},
                                controls=[
                                    ft.OutlinedButton(
                                        "Big Text",
                                        icon=ft.Icons.SUBJECT,
                                        on_click=self._send_big_text,
                                        expand=True,
                                    )
                                ],
                            ),
                        ]
                    ),
                    padding=10,
                )
            ],
        )

    def _build_advanced_section(self):
        return ft.ExpansionTile(
            title=ft.Text("⚡ Recursos Avançados"),
            subtitle=ft.Text("Updates em tempo real e configurações"),
            controls=[
                ft.Container(
                    content=ft.ResponsiveRow(
                        [
                            ft.Column(
                                col={"xs": 12, "sm": 6, "md": 4},
                                controls=[
                                    ft.OutlinedButton(
                                        "Update em Tempo Real",
                                        icon=ft.Icons.REFRESH,
                                        on_click=self._send_realtime_update,
                                        expand=True,
                                    )
                                ],
                            ),
                            ft.Column(
                                col={"xs": 12, "sm": 6, "md": 4},
                                controls=[
                                    ft.OutlinedButton(
                                        "Canal Customizado",
                                        icon=ft.Icons.SETTINGS_INPUT_ANTENNA,
                                        on_click=self._create_custom_channel,
                                        expand=True,
                                    )
                                ],
                            ),
                            ft.Column(
                                col={"xs": 12, "sm": 6, "md": 4},
                                controls=[
                                    ft.OutlinedButton(
                                        "Sequência Completa",
                                        icon=ft.Icons.SCIENCE,
                                        on_click=self._run_complete_test,
                                        expand=True,
                                    )
                                ],
                            ),
                        ]
                    ),
                    padding=10,
                )
            ],
        )

    def _increment_counter(self):
        self.notification_count += 1
        self.counter_text_ref.current.value = str(self.notification_count)
        self.page.update()

    def _show_snack(self, message: str, error: bool = False, action=None):
        snack = self.snackbar_ref.current
        snack.content.value = message
        snack.bgcolor = ft.Colors.RED_900 if error else None
        snack.action = action
        snack.open = True
        self.page.update()

    def _dev_simulate(self, action_name: str):
        if self.dev_mode:
            self._increment_counter()
            self._show_snack(f"🔧 DEV: Simulando '{action_name}'")
            return True
        return False

    async def _send_simple_normal(self, e):
        if self._dev_simulate("Notificação normal"):
            return

        try:
            self.notifier.send(
                title="Nova notificação", message="Esta é uma notificação normal"
            )
            self._increment_counter()
            self._show_snack("✅ Notificação enviada")

        except Exception as ex:
            self._show_snack(f"Erro: {ex}", error=True)

    async def _send_simple_silent(self, e):
        if self._dev_simulate("Notificação silenciosa"):
            return

        try:
            self.notifier.send(
                title="Notificação Silenciosa",
                message="Sem som ou vibração",
                silent=True,
            )
            self._increment_counter()
            self._show_snack("🔇 Notificação silenciosa enviada")

        except Exception as ex:
            self._show_snack(f"Erro: {ex}", error=True)

    async def _send_simple_persistent(self, e):
        if self._dev_simulate("Notificação persistente"):
            return

        try:
            self.notifier.send(
                title="Notificação Persistente",
                message="Não pode ser deslizada para fechar",
                persistent=True,
            )
            self._increment_counter()
            self._show_snack("📌 Notificação persistente enviada")

        except Exception as ex:
            self._show_snack(f"Erro: {ex}", error=True)

    async def _send_progress_determinate(self, e):
        if self.dev_mode:
            e.control.disabled = True
            self.page.update()
            self._increment_counter()
            self._show_snack("🔧 DEV: Simulando progress bar")
            await asyncio.sleep(2)
            e.control.disabled = False
            self.page.update()
            return

        try:
            e.control.disabled = True
            self.page.update()

            progress = (
                self.notifier.create(
                    title="Download em andamento", message="Baixando arquivo..."
                )
                .with_progress(0, 100)
                .send()
            )

            self._increment_counter()
            self._show_snack("⬇️ Download iniciado")

            for i in range(0, 101, 10):
                await asyncio.sleep(0.3)
                progress.update_progress(i)

            progress.remove_progress("Download concluído!", show_briefly=True)
            self._show_snack("✅ Download concluído!")

        except Exception as ex:
            self._show_snack(f"Erro: {ex}", error=True)
        finally:
            e.control.disabled = False
            self.page.update()

    async def _send_progress_indeterminate(self, e):
        if self.dev_mode:
            e.control.disabled = True
            self.page.update()
            self._increment_counter()
            self._show_snack("🔧 DEV: Simulando processamento")
            await asyncio.sleep(2)
            e.control.disabled = False
            self.page.update()
            return

        try:
            e.control.disabled = True
            self.page.update()

            progress = (
                self.notifier.create(
                    title="Processando", message="Aguarde enquanto processamos..."
                )
                .with_progress()
                .send()
            )

            self._increment_counter()
            self._show_snack("⚙️ Processamento iniciado")

            await asyncio.sleep(3)

            progress.remove_progress("Processamento concluído!", show_briefly=True)
            self._show_snack("✅ Processamento concluído!")

        except Exception as ex:
            self._show_snack(f"Erro: {ex}", error=True)
        finally:
            e.control.disabled = False
            self.page.update()

    async def _send_with_one_button(self, e):
        if self._dev_simulate("Notificação com 1 botão"):
            return

        try:

            def on_action():
                self._show_snack("👆 Botão 'Abrir' clicado!")

            self.notifier.create(
                title="Novo E-mail", message="Você tem 1 mensagem não lida"
            ).add_button("Abrir", on_action).send(persistent=True)

            self._increment_counter()
            self._show_snack("✅ Notificação com botão enviada")

        except Exception as ex:
            self._show_snack(f"Erro: {ex}", error=True)

    async def _send_with_two_buttons(self, e):
        if self._dev_simulate("Notificação com 2 botões"):
            return

        try:

            def on_accept():
                self._show_snack("✅ Convite aceito!")

            def on_decline():
                self._show_snack("❌ Convite recusado!")

            self.notifier.create(
                title="Convite de Reunião", message="Reunião de equipe às 15h"
            ).add_button("Aceitar", on_accept).add_button("Recusar", on_decline).send(
                persistent=True
            )

            self._increment_counter()
            self._show_snack("✅ Notificação com botões enviada")

        except Exception as ex:
            self._show_snack(f"Erro: {ex}", error=True)

    async def _send_with_three_buttons(self, e):
        if self._dev_simulate("Notificação com 3 botões"):
            return

        try:

            def on_play():
                self._show_snack("▶️ Play pressionado")

            def on_pause():
                self._show_snack("⏸️ Pause pressionado")

            def on_skip():
                self._show_snack("⏭️ Skip pressionado")

            self.notifier.create(
                title="🎵 Tocando Agora", message="Artist - Song Name"
            ).add_button("Play", on_play).add_button("Pause", on_pause).add_button(
                "Skip", on_skip
            ).send(
                persistent=True
            )

            self._increment_counter()
            self._show_snack("✅ Notificação com controles enviada")

        except Exception as ex:
            self._show_snack(f"Erro: {ex}", error=True)

    async def _send_with_large_icon(self, e):
        if self._dev_simulate("Notificação com large icon"):
            return

        try:
            self.notifier.create(
                title="Nova Mensagem", message="@usuario enviou uma mensagem"
            ).set_large_icon("assets/profile.jpg").send()

            self._increment_counter()
            self._show_snack("✅ Notificação com ícone enviada")

        except Exception as ex:
            self._show_snack(f"Erro: {ex}", error=True)

    async def _send_with_big_picture(self, e):
        if self._dev_simulate("Notificação com big picture"):
            return

        try:
            self.notifier.create(
                title="Nova Foto", message="Você foi marcado em uma foto"
            ).set_big_picture("assets/photo.jpg").send()

            self._increment_counter()
            self._show_snack("✅ Notificação com imagem enviada")

        except Exception as ex:
            self._show_snack(f"Erro: {ex}", error=True)

    async def _send_with_both_images(self, e):
        if self._dev_simulate("Notificação com ambas imagens"):
            return

        try:
            self.notifier.create(
                title="@usuario comentou",
                message="Que foto incrível! Adorei os detalhes.",
            ).set_large_icon("assets/profile.jpg").set_big_picture(
                "assets/post.jpg"
            ).send()

            self._increment_counter()
            self._show_snack("✅ Notificação completa enviada")

        except Exception as ex:
            self._show_snack(f"Erro: {ex}", error=True)

    async def _send_inbox_style(self, e):
        if self._dev_simulate("Notificação inbox style"):
            return

        try:
            self.notifier.create(
                title="5 novas mensagens", message="WhatsApp"
            ).add_line("João: E aí, bora codar hoje?").add_line(
                "Maria: Reunião às 15h, não esqueça!"
            ).add_line(
                "Pedro: PR aprovado! 🎉"
            ).add_line(
                "Ana: Parabéns pelo projeto!"
            ).add_line(
                "Carlos: Pizza depois do trabalho?"
            ).send()

            self._increment_counter()
            self._show_snack("✅ Notificação inbox enviada")

        except Exception as ex:
            self._show_snack(f"Erro: {ex}", error=True)

    async def _send_big_text(self, e):
        if self._dev_simulate("Notificação big text"):
            return

        try:
            long_text = (
                "O Python 3.13 traz melhorias significativas em performance, "
                "incluindo um novo GIL opcional que permite verdadeiro paralelismo "
                "em threads. Além disso, o interpretador agora é até 20% mais rápido "
                "em benchmarks comuns, e a gestão de memória foi otimizada para "
                "aplicações de longa duração. O suporte a type hints foi expandido "
                "com novos recursos do PEP 692, tornando o código mais seguro e "
                "expressivo. Experimente hoje mesmo e veja a diferença!"
            )

            self.notifier.create(
                title="Python 3.13 Lançado!",
                message="Confira as novidades desta versão",
            ).set_big_text(long_text).send()

            self._increment_counter()
            self._show_snack("✅ Notificação com texto expandido enviada")

        except Exception as ex:
            self._show_snack(f"Erro: {ex}", error=True)

    async def _send_realtime_update(self, e):
        if self.dev_mode:
            e.control.disabled = True
            self.page.update()
            self._increment_counter()
            self._show_snack("🔧 DEV: Simulando updates em tempo real")
            await asyncio.sleep(3)
            e.control.disabled = False
            self.page.update()
            return

        try:
            e.control.disabled = True
            self.page.update()

            status = self.notifier.create(
                title="Processando tarefa", message="Iniciando processamento..."
            ).send()

            self._increment_counter()
            self._show_snack("⚙️ Iniciando updates em tempo real")

            await asyncio.sleep(1.5)
            status.update_message("Fase 1/3: Carregando dados...")

            await asyncio.sleep(1.5)
            status.update_message("Fase 2/3: Processando informações...")

            await asyncio.sleep(1.5)
            status.update_message("Fase 3/3: Finalizando...")

            await asyncio.sleep(1)
            status.update_title("Concluído!")
            status.update_message("Todas as fases completadas com sucesso")

            self._show_snack("✅ Updates concluídos")

        except Exception as ex:
            self._show_snack(f"Erro: {ex}", error=True)
        finally:
            e.control.disabled = False
            self.page.update()

    async def _create_custom_channel(self, e):
        if self._dev_simulate("Criação de canal customizado"):
            return

        try:
            FletNotify.create_channel(
                channel_id="app_custom",
                channel_name="Notificações Personalizadas",
                description="Canal com configurações customizadas",
                importance=NotificationImportance.HIGH,
            )

            await asyncio.sleep(0.5)

            self.notifier.send(
                title="Canal Customizado",
                message="Esta notificação usa um canal personalizado!",
                channel_id="app_custom",
            )

            self._increment_counter()
            self._show_snack("✅ Canal criado e notificação enviada")

        except Exception as ex:
            self._show_snack(f"Erro: {ex}", error=True)

    async def _run_complete_test(self, e):
        if self.dev_mode:
            e.control.disabled = True
            self.page.update()
            self._show_snack("🔧 DEV: Simulando sequência completa")
            for i in range(5):
                self._increment_counter()
                await asyncio.sleep(0.5)
            e.control.disabled = False
            self.page.update()
            return

        try:
            e.control.disabled = True
            self.page.update()

            self._show_snack("🧪 Iniciando sequência completa...")

            self.notifier.send("Passo 1/5", "Notificação simples")
            self._increment_counter()
            await asyncio.sleep(1)

            self.notifier.send("Passo 2/5", "Silenciosa", silent=True)
            self._increment_counter()
            await asyncio.sleep(1)

            self.notifier.create("Passo 3/5", "Com botão").add_button(
                "OK", lambda: None
            ).send()
            self._increment_counter()
            await asyncio.sleep(1)

            self.notifier.create("Passo 4/5", "Inbox").add_line("Linha 1").add_line(
                "Linha 2"
            ).add_line("Linha 3").send()
            self._increment_counter()
            await asyncio.sleep(1)

            progress = (
                self.notifier.create("Passo 5/5", "Progress").with_progress().send()
            )
            self._increment_counter()

            for i in range(0, 101, 25):
                await asyncio.sleep(0.5)
                progress.update_progress(i, message=f"{i}%")

            progress.remove_progress("Sequência completa!", show_briefly=True)

            self._show_snack("✅ Sequência finalizada!")

        except Exception as ex:
            self._show_snack(f"Erro: {ex}", error=True)
        finally:
            e.control.disabled = False
            self.page.update()

    async def _cancel_all_notifications(self, e):
        if self._dev_simulate("Cancelamento de todas as notificações"):
            return

        try:
            FletNotify.cancel_all()
            self._show_snack("🗑️ Todas as notificações foram canceladas")
        except Exception as ex:
            self._show_snack(f"Erro: {ex}", error=True)


async def main(page: ft.Page):
    app = NotificationDemo(page)
    await app.initialize()


ft.app(target=main, assets_dir="assets")
