from kivymd.app import MDApp
from kivymd.uix.screen import Screen 
from kivymd.uix.screenmanager import ScreenManager
from kivymd.uix.list import ThreeLineIconListItem, IconLeftWidget
from kivy.factory import Factory
from kivy.properties import ObjectProperty, NumericProperty
from datetime import datetime
from kivy.uix.popup import Popup
import sqlite3

#RECICYCLE VIEW SERA IMPLEMENTADO NO FUTURO

conn = sqlite3.connect('.\\tasks.db')
conn.close()

class PopupDetalhes(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id_task = NumericProperty(None)
        self.widget_task = ObjectProperty(None)

class TaskIco(IconLeftWidget):
    id_task = ObjectProperty(None)

class MenuInicial(Screen):
    pass

class TasksList(Screen):
    def build(self):
        conn = sqlite3.connect('.\\tasks.db')
        cur = conn.cursor()
        cur.execute("""Select * from Tarefas;
        """)
        for linha in cur.fetchall():
            if linha[4] == 0:
                bg = 'black'
                ico = 'clock-outline'
            else:
                bg = 'green'
                ico = 'check'
            ico_widget= IconLeftWidget(icon=ico,on_release=self.change_status_task)
            widget = ThreeLineIconListItem(ico_widget,text=linha[1],secondary_text=str('Criado em '+linha[3]),tertiary_text=str('ID #'+str(linha[0])),on_release=self.detalhes,bg_color=bg)
            ico_widget.id_task = widget
            self.ids.list_view.add_widget(widget)
        conn.close()

    def destroy(self):
        rows = [i for i in self.ids.list_view.children]
        for row in rows:
            self.ids.list_view.remove_widget(row)

    def detalhes(self, widget):
        int_widget = widget.tertiary_text[4:]
        conn = sqlite3.connect('.\\tasks.db')
        cur = conn.cursor()
        cur.execute("""SELECT id_tarefa, nome_tarefa, subtitulo_tarefa FROM Tarefas WHERE id_tarefa = ?;
        """, [int_widget])
        detalhes = cur.fetchone()
        pop = PopupDetalhes()
        pop.id_task = int(detalhes[0])
        pop.title = str(detalhes[1])
        pop.title_size = 18
        pop.ids.label_detalhes.text = str(detalhes[2])
        if widget.bg_color == [0.0, 0.5019607843137255, 0.0, 1.0]:
            pop.title_color = (0, 1, 0, 1)
            pop.separator_color = (0, 1, 0, 1)
        pop.widget_task = widget
        pop.open()
        conn.close()

    def change_status_task(self, widget):
        int_id_task = widget.id_task.tertiary_text[4:]
        conn = sqlite3.connect('.\\tasks.db')
        cur = conn.cursor()
        if widget.icon == 'clock-outline':
            widget.icon = 'check'
            widget.id_task.bg_color = 'green'
            new_status = 1

        else:
            widget.icon = 'clock-outline'
            widget.id_task.bg_color = 'black'
            new_status = 0

        cur.execute("""UPDATE Tarefas
                    SET status_tarefa = ?
                    WHERE id_tarefa = ?""",(new_status,int_id_task))
        conn.commit()
        conn.close()

    def delete_task(self, id, widget):
        conn = sqlite3.connect('.\\tasks.db')
        cur = conn.cursor()
        cur.execute("""DELETE FROM Tarefas WHERE id_tarefa = ?""", [int(id)])
        conn.commit()
        conn.close()
        self.ids.list_view.remove_widget(widget)


class CreateTask(Screen):
    def insert_task(self):
        nome_task = self.ids.nome_tarefa.text
        desc_task = self.ids.descricao_tarefa.text

        if nome_task == "" or nome_task.isspace():
            Factory.PopupError().open()
        else:
            conn = sqlite3.connect('.\\tasks.db')
            cur = conn.cursor()
            data_hoje = datetime.now()
            cur.execute("""INSERT INTO Tarefas (nome_tarefa, subtitulo_tarefa, criado_em_tarefa, status_tarefa)
                        VALUES (?, ?, ?, 0);
                        """, (nome_task, desc_task, data_hoje))
            conn.commit()
            conn.close()
            self.ids.nome_tarefa.text = 'Nome da tarefa'
            self.ids.descricao_tarefa.text='Descricao da tarefa'
            Factory.PopupTarefaCriada().open()


class TaskOrganizerApp(MDApp):
    title = 'Task Organizer'
    def build(self):
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'BlueGray'
        sm = ScreenManager()
        sm.add_widget(MenuInicial(name='MenuInicial'))
        sm.add_widget(TasksList(name='TasksList'))
        sm.add_widget(CreateTask(name='CreateTask'))
        conn = sqlite3.connect('.\\tasks.db')
        cur = conn.cursor()
        cur.execute(
        """CREATE TABLE IF NOT EXISTS Tarefas (id_tarefa INTEGER PRIMARY KEY,
        nome_tarefa VARCHAR(20) NOT NULL,
        subtitulo_tarefa TEXT,
        criado_em_tarefa DATE NOT NULL,
        status_tarefa INTEGER NOT NULL);""").fetchall()
        conn.commit()
        conn.close()
        return sm

if __name__ == '__main__':
    TaskOrganizerApp().run()