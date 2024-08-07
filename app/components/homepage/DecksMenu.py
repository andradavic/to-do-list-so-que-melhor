from flet import *
from app.components.homepage.TaskContainer import TaskContainer
from app.models.Database import Database
from app.models.Deck import Deck

class DecksMenu(Container):
    def __init__(self, page, db, task_container) -> None:
        super().__init__()

        self.deckname: str = 'deck temporário'
        self.menu_items: list = []

        self.db: Database = db
        self.deck: Deck
        self.task_container: TaskContainer = task_container

        self.page: Page = page
        self.padding = padding.only(left=20, bottom=10, right=20)

        self.sub_menu = SubmenuButton(
            content = Text(self.deckname, color='white', size=20),
            controls = self.menu_items
        )

        self.content = MenuBar(
            expand=True,
            style= MenuStyle(
                alignment = alignment.center,
                bgcolor = colors.BLUE,
                mouse_cursor = {
                    MaterialState.HOVERED: MouseCursor.WAIT,
                    MaterialState.DEFAULT: MouseCursor.ZOOM_OUT
                },
            ),
            controls=[self.sub_menu]
        )

        self.dialog_change_deck = AlertDialog(
            bgcolor='black',
            modal=True, 
            title=Text("Atenção!", color=colors.BLUE), 
            open=False,
            content=Text(value="Ao trocar de deck o status atual da atividade em andamento é resetado."), 
            actions=[
                TextButton("Estou de acordo!", on_click=self.accept_change),
                TextButton("Voltar.", on_click=self.decline_change, ),
            ]
        )

        self.dialog_create_deck = AlertDialog(
            bgcolor='black',
            modal=True, 
            title=Text("Atenção!", color=colors.BLUE), 
            open=False,
            content=Text(value="O status atual da atividade em andamento é resetado ao trocar para a página de criação de decks."), 
            actions=[
                TextButton("Estou de acordo!", on_click=lambda _: self.page.go('/createdeck')),
                TextButton("Voltar.", on_click=self.decline_change_to_deckpage),
            ]
        )

        self.update_menu_items()
        
    def updateDeck(self, new_deck_name: str, force=False):
        if not self.sub_menu.content.value == new_deck_name:
            self.active_task = self.task_container.get_active_task(None)
            if not self.active_task or force:
                self.sub_menu.content.value = new_deck_name  # Atualiza o nome do deck

                self.db.deck_name = new_deck_name
                self.deck.name = self.db.deck_name

                self.db.create_deck(self.deck)

                self.deck.name, self.deck.time, self.deck.break_time, self.deck.sound, self.deck.cycles = self.db.find_deck()

                self.sub_menu.update()
                self.task_container.update(force)

            else:
                self.task_container.dialog_change_deck.open = True
                self.db.deck_name = new_deck_name
                self.task_container.content.content.controls[1].update()


    def accept_change(self, e):
        self.task_container.dialog_change_deck.open = False
        self.task_container.content.content.controls[1].update()
        self.updateDeck(self.db.deck_name, True)

    
    def decline_change(self, e):
        self.db.deck_name = self.sub_menu.content.value
        self.task_container.dialog_change_deck.open = False
        self.task_container.content.content.controls[1].update()

    def decline_change_to_deckpage(self, e):
        self.task_container.dialog_create_deck.open = False
        self.task_container.content.content.controls[1].update()

    def delete_deck(self, deck):
        self.db.deck_name = deck
        self.db.delete_deck(deck)
        self.update_menu_items()
        self.update()

        if self.sub_menu.content.value == self.db.deck_name:
            self.db.deck_name = 'deck temporário'
            self.sub_menu.content.value = 'deck temporário'
            self.deck.name = 'deck temporário'
            self.deck.time = 1500
            self.deck.break_time = 300
            self.deck.cycles = 3
            self.update_menu_items()
            self.update()
            self.task_container.update()
            self.db.create_deck(self.deck)


    def route_to_create_deck(self, e):
        self.active_task = self.task_container.get_active_task(None)
        if not self.active_task:
            self.page.go("/createdeck")
        
        else:
            self.task_container.dialog_create_deck.open = True
            self.task_container.content.content.controls[1].update()

    def show_deck_settings(self):
        pass

    def update_menu_items(self):
        self.task_container.dialog_change_deck = self.dialog_change_deck
        self.task_container.dialog_create_deck = self.dialog_create_deck
        self.menu_items.clear()
        decks = self.db.find_decks()
        for deck in decks:
            self.menu_items.append(
                Container(
                    content=Row(
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                        
                        controls=[
                            MenuItemButton(
                                width=200,
                                content=Text(deck, max_lines=1, overflow=TextOverflow.ELLIPSIS, width=150),
                                leading=Icon(icons.FOLDER),
                                style=ButtonStyle(bgcolor={MaterialState.HOVERED: colors.GREEN}),
                                on_click=lambda e, deck=deck: self.updateDeck(deck),
                            ),

                            IconButton(icons.DELETE, width=30, height=30, icon_size=15, icon_color='red', on_click= lambda _, deck=deck: self.delete_deck(deck)), 
                        ]
                    )
                )
                
            )

        self.menu_items.append(
            MenuItemButton(
                content=Text("Criar novo deck."),
                leading=Icon(icons.CREATE_NEW_FOLDER),
                style=ButtonStyle(bgcolor={MaterialState.HOVERED: colors.BLUE}),
                on_click=self.route_to_create_deck
            )
        )