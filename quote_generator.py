import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
from datetime import datetime

HISTORY_FILE = "quotes_history.json"

# Предопределённый список цитат
DEFAULT_QUOTES = [
    {"text": "Будьте тем изменением, которое хотите видеть в мире.", "author": "Махатма Ганди", "theme": "Мотивация"},
    {"text": "Жизнь — это то, что с тобой происходит, пока ты строишь планы.", "author": "Джон Леннон", "theme": "Жизнь"},
    {"text": "Единственный способ делать великую работу — любить то, что ты делаешь.", "author": "Стив Джобс", "theme": "Работа"},
    {"text": "Не важно, как медленно ты идёшь, главное — не останавливаться.", "author": "Конфуций", "theme": "Мотивация"},
    {"text": "Успех — это способность идти от неудачи к неудаче, не теряя энтузиазма.", "author": "Уинстон Черчилль", "theme": "Успех"},
    {"text": "Лучший способ предсказать будущее — изобрести его.", "author": "Алан Кей", "theme": "Будущее"},
    {"text": "Сложно победить того, кто никогда не сдаётся.", "author": "Бейб Рут", "theme": "Мотивация"},
    {"text": "Знание — сила.", "author": "Фрэнсис Бэкон", "theme": "Знание"},
    {"text": "Кто хочет — ищет возможности, кто не хочет — ищет причины.", "author": "Сократ", "theme": "Мотивация"},
    {"text": "Счастье — это когда то, что ты думаешь, говоришь и делаешь, находится в гармонии.", "author": "Махатма Ганди", "theme": "Счастье"},
    {"text": "Вдохновение приходит только во время работы.", "author": "Габриэль Гарсиа Маркес", "theme": "Творчество"},
    {"text": "Не ошибается только тот, кто ничего не делает.", "author": "Теодор Рузвельт", "theme": "Мотивация"},
    {"text": "Ваше время ограничено, не тратьте его на чужую жизнь.", "author": "Стив Джобс", "theme": "Жизнь"},
    {"text": "Путешествие в тысячу миль начинается с одного шага.", "author": "Лао-цзы", "theme": "Мотивация"},
    {"text": "Тот, кто читает книги, никогда не будет скучать.", "author": "Агата Кристи", "theme": "Книги"},
    {"text": "Программирование — это искусство рассказать компьютеру, что делать.", "author": "Алан Кей", "theme": "Программирование"},
    {"text": "Простота — залог надёжности.", "author": "Никлаус Вирт", "theme": "Программирование"},
    {"text": "Любой дурак может написать код, понятный компьютеру. Хорошие программисты пишут код, понятный людям.", "author": "Мартин Фаулер", "theme": "Программирование"}
]


class QuoteGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Quote Generator - Генератор цитат")
        self.root.geometry("850x620")
        self.root.resizable(True, True)

        self.quotes = DEFAULT_QUOTES.copy()
        self.history = []
        self.load_history()

        self.create_widgets()
        self.update_filter_options()
        self.refresh_history_table()

    def create_widgets(self):
        # === Рамка добавления новой цитаты ===
        add_frame = tk.LabelFrame(self.root, text="📝 Добавить новую цитату", padx=10, pady=10, font=("Arial", 10, "bold"))
        add_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(add_frame, text="Текст цитаты:", font=("Arial", 10)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.quote_text_entry = tk.Entry(add_frame, width=55, font=("Arial", 10))
        self.quote_text_entry.grid(row=0, column=1, padx=5, pady=5, columnspan=3)

        tk.Label(add_frame, text="Автор:", font=("Arial", 10)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.author_entry = tk.Entry(add_frame, width=25, font=("Arial", 10))
        self.author_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(add_frame, text="Тема:", font=("Arial", 10)).grid(row=1, column=2, sticky="e", padx=5, pady=5)
        self.theme_entry = tk.Entry(add_frame, width=20, font=("Arial", 10))
        self.theme_entry.grid(row=1, column=3, padx=5, pady=5)

        tk.Button(add_frame, text="➕ Добавить цитату в библиотеку", command=self.add_quote,
                  bg="lightgreen", font=("Arial", 10)).grid(row=1, column=4, padx=10, pady=5)

        # === Рамка генерации ===
        gen_frame = tk.LabelFrame(self.root, text="🎲 Генерация цитаты", padx=10, pady=10, font=("Arial", 10, "bold"))
        gen_frame.pack(fill="x", padx=10, pady=5)

        tk.Button(gen_frame, text="🎲 Сгенерировать случайную цитату", command=self.generate_quote,
                  bg="lightblue", font=("Arial", 12, "bold")).pack(pady=10)

        # === Отображение текущей цитаты ===
        current_frame = tk.LabelFrame(self.root, text="✨ Текущая цитата", padx=10, pady=10, font=("Arial", 10, "bold"))
        current_frame.pack(fill="x", padx=10, pady=5)

        self.current_quote_text = tk.Label(current_frame, text="", wraplength=750, font=("Georgia", 12, "italic"),
                                           justify="center", fg="darkblue")
        self.current_quote_text.pack(pady=5)

        self.current_author_label = tk.Label(current_frame, text="", font=("Arial", 10, "bold"),
                                             justify="center", fg="gray")
        self.current_author_label.pack(pady=2)

        self.current_theme_label = tk.Label(current_frame, text="", font=("Arial", 9), justify="center", fg="green")
        self.current_theme_label.pack(pady=2)

        # === Рамка фильтрации ===
        filter_frame = tk.LabelFrame(self.root, text="🔍 Фильтрация истории", padx=10, pady=10, font=("Arial", 10, "bold"))
        filter_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(filter_frame, text="Фильтр по автору:", font=("Arial", 10)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.filter_author_combo = ttk.Combobox(filter_frame, width=20, font=("Arial", 10))
        self.filter_author_combo.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(filter_frame, text="Фильтр по теме:", font=("Arial", 10)).grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.filter_theme_combo = ttk.Combobox(filter_frame, width=20, font=("Arial", 10))
        self.filter_theme_combo.grid(row=0, column=3, padx=5, pady=5)

        tk.Button(filter_frame, text="🔍 Применить фильтр", command=self.apply_filter,
                  bg="lightyellow", font=("Arial", 9)).grid(row=0, column=4, padx=10, pady=5)
        tk.Button(filter_frame, text="❌ Сбросить фильтр", command=self.reset_filter,
                  bg="lightgray", font=("Arial", 9)).grid(row=0, column=5, padx=5, pady=5)

        # === Таблица истории ===
        history_frame = tk.LabelFrame(self.root, text="📜 История сгенерированных цитат", padx=10, pady=10, font=("Arial", 10, "bold"))
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("Дата и время", "Цитата", "Автор", "Тема")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=10)

        self.tree.heading("Дата и время", text="Дата и время")
        self.tree.heading("Цитата", text="Цитата")
        self.tree.heading("Автор", text="Автор")
        self.tree.heading("Тема", text="Тема")

        self.tree.column("Дата и время", width=130)
        self.tree.column("Цитата", width=370)
        self.tree.column("Автор", width=130)
        self.tree.column("Тема", width=100)

        scrollbar_y = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(history_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        self.tree.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill="y")
        scrollbar_x.pack(side=tk.BOTTOM, fill="x")

        # === Кнопки управления ===
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=10)

        tk.Button(btn_frame, text="💾 Сохранить историю", command=self.save_history,
                  bg="lightyellow", font=("Arial", 10), width=15).pack(side="left", padx=5)
        tk.Button(btn_frame, text="📂 Загрузить историю", command=self.load_history_interactive,
                  bg="lightyellow", font=("Arial", 10), width=15).pack(side="left", padx=5)
        tk.Button(btn_frame, text="🗑 Очистить историю", command=self.clear_history,
                  bg="salmon", font=("Arial", 10), width=15).pack(side="left", padx=5)

        # Статистика
        self.stats_label = tk.Label(btn_frame, text="", font=("Arial", 9), fg="blue")
        self.stats_label.pack(side="right", padx=10)
        self.update_stats()

    def update_filter_options(self):
        # Получаем уникальных авторов и темы
        authors = sorted(set(q["author"] for q in self.quotes))
        themes = sorted(set(q["theme"] for q in self.quotes))

        self.filter_author_combo["values"] = ["Все"] + authors
        self.filter_theme_combo["values"] = ["Все"] + themes
        self.filter_author_combo.set("Все")
        self.filter_theme_combo.set("Все")

    def add_quote(self):
        text = self.quote_text_entry.get().strip()
        author = self.author_entry.get().strip()
        theme = self.theme_entry.get().strip()

        # Проверка на пустые строки
        if not text:
            messagebox.showerror("Ошибка", "Текст цитаты не может быть пустым")
            return
        if not author:
            messagebox.showerror("Ошибка", "Автор не может быть пустым")
            return
        if not theme:
            messagebox.showerror("Ошибка", "Тема не может быть пустой")
            return

        new_quote = {"text": text, "author": author, "theme": theme}
        self.quotes.append(new_quote)
        self.update_filter_options()

        # Очищаем поля
        self.quote_text_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.theme_entry.delete(0, tk.END)

        messagebox.showinfo("Успех", f"Цитата добавлена в библиотеку! Теперь доступно {len(self.quotes)} цитат")

    def generate_quote(self):
        if not self.quotes:
            messagebox.showerror("Ошибка", "Нет доступных цитат. Добавьте хотя бы одну цитату.")
            return

        quote = random.choice(self.quotes)

        # Обновляем отображение
        self.current_quote_text.config(text=f"«{quote['text']}»")
        self.current_author_label.config(text=f"— {quote['author']} —")
        self.current_theme_label.config(text=f"Тема: {quote['theme']}")

        # Добавляем в историю
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.insert(0, {
            "timestamp": timestamp,
            "text": quote["text"],
            "author": quote["author"],
            "theme": quote["theme"]
        })

        # Ограничиваем историю 100 записями
        if len(self.history) > 100:
            self.history = self.history[:100]

        self.refresh_history_table()
        self.update_stats()
        messagebox.showinfo("Генерация", f"Цитата от {quote['author']} добавлена в историю")

    def refresh_history_table(self, history_to_show=None):
        for row in self.tree.get_children():
            self.tree.delete(row)

        data = history_to_show if history_to_show is not None else self.history
        for record in data:
            # Обрезаем слишком длинные цитаты для отображения
            display_text = record["text"][:70] + "..." if len(record["text"]) > 70 else record["text"]
            self.tree.insert("", tk.END, values=(
                record["timestamp"],
                display_text,
                record["author"],
                record["theme"]
            ))

    def apply_filter(self):
        filtered = self.history[:]

        author_filter = self.filter_author_combo.get()
        theme_filter = self.filter_theme_combo.get()

        if author_filter != "Все":
            filtered = [h for h in filtered if h["author"] == author_filter]

        if theme_filter != "Все":
            filtered = [h for h in filtered if h["theme"] == theme_filter]

        self.refresh_history_table(filtered)
        messagebox.showinfo("Фильтр", f"Показано записей в истории: {len(filtered)}")

    def reset_filter(self):
        self.filter_author_combo.set("Все")
        self.filter_theme_combo.set("Все")
        self.refresh_history_table()
        messagebox.showinfo("Фильтр", "Фильтр сброшен")

    def update_stats(self):
        total_quotes = len(self.quotes)
        history_count = len(self.history)
        self.stats_label.config(text=f"📚 Цитат в библиотеке: {total_quotes} | 📜 Записей в истории: {history_count}")

    def save_history(self):
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Сохранение", f"История сохранена в {HISTORY_FILE}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.history = []

    def load_history_interactive(self):
        self.load_history()
        self.refresh_history_table()
        self.update_stats()
        messagebox.showinfo("Загрузка", f"Загружено записей в истории: {len(self.history)}")

    def clear_history(self):
        if messagebox.askyesno("Очистка", "Вы уверены, что хотите очистить всю историю цитат?"):
            self.history = []
            self.refresh_history_table()
            self.update_stats()
            messagebox.showinfo("Очистка", "История очищена")


if __name__ == "__main__":
    root = tk.Tk()
    app = QuoteGenerator(root)
    root.mainloop()
  
