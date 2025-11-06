import tkinter as tk
from tkinter import ttk, messagebox
import socket
import json

class SystemInfoClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Системная информация")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        self.setup_ui()
        self.refresh_data()  # Автоматическое обновление при запуске
        
    def setup_ui(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        title_label = ttk.Label(main_frame, 
                               text="Информация об операционной системе", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Фрейм с кнопками
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(0, 15))
        
        # Кнопки управления
        refresh_btn = ttk.Button(button_frame, text="🔄 Обновить", 
                                command=self.refresh_data)
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        exit_btn = ttk.Button(button_frame, text="🚪 Выход", 
                             command=self.root.quit)
        exit_btn.pack(side=tk.LEFT)
        
        # Таблица с информацией
        self.create_info_table(main_frame)
        
        # Статус бар
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W, padding=(5, 2))
        status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Настройка расширения
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
    def create_info_table(self, parent):
        # Создаем фрейм для таблицы
        table_frame = ttk.Frame(parent)
        table_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Создаем Treeview для отображения данных
        columns = ('parameter', 'value')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='tree', height=12)
        
        # Настраиваем колонки
        self.tree.column('#0', width=0, stretch=tk.NO)
        self.tree.column('parameter', width=250, anchor=tk.W, minwidth=200)
        self.tree.column('value', width=400, anchor=tk.W, minwidth=300)
        
        # Заголовки
        self.tree.heading('parameter', text='Параметр системы')
        self.tree.heading('value', text='Значение')
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Полосы прокрутки
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Настройка расширения таблицы
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
    def refresh_data(self):
        """Получение данных от сервера"""
        self.status_var.set("Подключение к серверу...")
        self.root.update()
        
        try:
            # Подключаемся к серверу
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.settimeout(10)
                client_socket.connect(('localhost', 12345))
                
                # Получаем данные
                data = b""
                while True:
                    chunk = client_socket.recv(1024)
                    if not chunk:
                        break
                    data += chunk
                
                system_info = json.loads(data.decode('utf-8'))
                
                # Обработка ошибок
                if system_info.get('error'):
                    messagebox.showerror("Ошибка", system_info['error'])
                    self.status_var.set("Ошибка получения данных")
                    return
                
                # Обновляем интерфейс
                self.update_display(system_info)
                self.status_var.set("Данные успешно обновлены")
                
        except ConnectionRefusedError:
            messagebox.showerror("Ошибка", 
                               "Не удалось подключиться к серверу.\n"
                               "Убедитесь, что server.py запущен.")
            self.status_var.set("Ошибка подключения")
        except socket.timeout:
            messagebox.showerror("Ошибка", "Таймаут подключения к серверу")
            self.status_var.set("Таймаут подключения")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
            self.status_var.set("Ошибка")
    
    def update_display(self, system_info):
        """Обновление отображения данных"""
        # Очищаем предыдущие данные
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Добавляем новые данные
        data_mapping = [
            ("💻 Операционная система", system_info['os_name']),
            ("🔧 Номер сервис-пака", system_info['service_pack']),
            ("🏗️ Архитектура", system_info['architecture']),
            ("⚙️ Процессор", system_info['processor']),
            ("🖥️ Тип системы", system_info['machine']),
            ("🧮 Общий объем памяти", f"{system_info['total_memory_gb']} ГБ"),
            ("✅ Доступно памяти", f"{system_info['available_memory_gb']} ГБ"),
            ("📊 Используется памяти", 
             f"{system_info['total_memory_gb'] - system_info['available_memory_gb']:.2f} ГБ")
        ]
        
        for param, value in data_mapping:
            item_id = self.tree.insert('', tk.END, values=(param, value))
            # Добавляем тег для чередования цветов
            if len(self.tree.get_children()) % 2 == 0:
                self.tree.item(item_id, tags=('evenrow',))
        
        # Настраиваем теги для цветов
        self.tree.tag_configure('evenrow', background='#f0f0f0')

def main():
    root = tk.Tk()
    app = SystemInfoClient(root)
    root.mainloop()

if __name__ == "__main__":
    main()
