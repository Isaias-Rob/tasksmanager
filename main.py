from kivymd.app import MDApp
from kivymd.uix.screen import Screen 
from kivymd.uix.screenmanager import ScreenManager
from kivymd.uix.list import ThreeLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivy.factory import Factory
from kivy.properties import ObjectProperty, NumericProperty, StringProperty
from datetime import datetime
from kivy.uix.popup import Popup
import sqlite3

#RECICYCLE VIEW SERA IMPLEMENTADO NO FUTURO

conn = sqlite3.connect('.\\tasks.db')
conn.close()

class PopupDetalhes(Popup):
    detalhes_task = StringProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id_task = NumericProperty(None)
        self.widget_task = ObjectProperty(None)

class PopupEditarTask(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id_task = NumericProperty(None)
        self.widget_task = ObjectProperty(None)

class PopupConfirmaExclusao(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id_task = NumericProperty(None)
        self.widget_task = ObjectProperty(None)

class PopupConfirmaExclusaoMassa(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
class TaskIco(IconRightWidget):
    id_mark = NumericProperty(None)

class TaskIconList(ThreeLineAvatarIconListItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.marked = NumericProperty(None)
        self.id_mark = NumericProperty(None)

class MenuInicial(Screen):
    pass

class TasksList(Screen):
    def build(self):
        self.destroy()
        conn = sqlite3.connect('.\\tasks.db')
        cur = conn.cursor()
        if not str(self.ids.search_input.text) == '':
            cur.execute("""Select * from Tarefas
            WHERE nome_tarefa LIKE ?;
            """, [str('%'+str(self.ids.search_input.text)+'%')])
        else:
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
            ico_widget_select = TaskIco(icon='checkbox-blank-outline',on_release=self.marked_task)
            ico_widget_select.id_mark = linha[0]
            widget = TaskIconList(ico_widget,ico_widget_select,text=linha[1],secondary_text=str('Criado em '+linha[3]),tertiary_text=str('ID #'+str(linha[0])),on_release=self.detalhes,bg_color=bg)
            widget.marked = 0
            widget.id_mark = linha[0]
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

    def confirm_delete_task(self, id, widget):
        conn = sqlite3.connect('.\\tasks.db')
        cur = conn.cursor()
        cur.execute("""DELETE FROM Tarefas WHERE id_tarefa = ?""", [int(id)])
        conn.commit()
        conn.close()
        self.ids.list_view.remove_widget(widget)

    def delete_task(self, id, widget):
        pop = PopupConfirmaExclusao()
        pop.id_task = id
        pop.widget_task = widget
        pop.open()
    
    def edit_task(self, id, widget):
        conn = sqlite3.connect('.\\tasks.db')
        cur = conn.cursor()
        cur.execute("""SELECT nome_tarefa, subtitulo_tarefa from Tarefas
                    WHERE id_tarefa = ?""",[int(id)])
        task_info = cur.fetchone()
        pop = PopupEditarTask()
        pop.ids.input_title_edit.text = task_info[0]
        pop.ids.input_detalhes_edit.text = task_info[1]
        pop.id_task = id
        pop.widget_task = widget
        conn.close()
        pop.open()
    
    def commit_edit_task(self, id, widget, new_title, new_description):
        if str(new_title) == "" or str(new_title).isspace():
            Factory.PopupError().open()
        else:
            conn = sqlite3.connect('.\\tasks.db')
            cur = conn.cursor()
            cur.execute("""UPDATE Tarefas 
                        set nome_tarefa= ?, subtitulo_tarefa = ?
                        WHERE id_tarefa = ?""",(str(new_title), str(new_description), int(id)))
            conn.commit()
            widget.text = str(new_title)
            self.detalhes(widget)
            conn.close()

    def marked_task(self, widget):
        task = self.return_row(widget)
        if widget.icon == 'checkbox-marked':
            widget.icon = 'checkbox-blank-outline'
            task.marked = 0
        else:
            widget.icon = 'checkbox-marked'
            task.marked = 1
    
    def return_row(self, widget):
        rows = [i for i in self.ids.list_view.children]
        for row in rows:
            if row.id_mark == widget.id_mark:
                return row
    
    def delete_mass_task(self):
        pop = PopupConfirmaExclusaoMassa()
        pop.open()
    
    def confirm_delete_mass_task(self):
        lista_exclusao = []
        rows = [i for i in self.ids.list_view.children]
        for row in rows:
            if row.marked == 1:
                self.ids.list_view.remove_widget(row)
                lista_exclusao.append(row.id_mark)

        conn = sqlite3.connect('.\\tasks.db')
        cur = conn.cursor()

        for elemento_exclusao in lista_exclusao:
            cur.execute("""DELETE FROM Tarefas 
                        WHERE id_tarefa = ?""", 
                        [int(elemento_exclusao)])
            conn.commit()
        conn.close()

        
        
        
class CreateTask(Screen):
    def insert_task(self, id_task = None, widget_task = None):

        if id_task == None and widget_task == None:
            nome_task = self.ids.nome_tarefa.text
            desc_task = self.ids.descricao_tarefa.text
        else:
            conn = sqlite3.connect('.\\tasks.db')
            cur = conn.cursor()
            cur.execute("""SELECT nome_tarefa, subtitulo_tarefa from Tarefas
            WHERE id_tarefa = ?""",[int(id_task)])
            task = cur.fetchone()
            nome_task = task[0]
            desc_task = task[1]

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
            self.ids.nome_tarefa.text = ''
            self.ids.descricao_tarefa.text=''
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