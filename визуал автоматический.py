import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import random

class VlagomerPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("Влагомер поточный ВМП.0704 - Эмулятор лицевой панели")
        self.root.geometry("1100x700")
        self.root.configure(bg="#2b2b2b")

        # Начальные значения
        self.water_content = 12.45
        self.temperature = 45.2
        self.voltage_out = 3.14
        self.voltage_temp = 1.25
        self.adc_code = 171

        # Флаги для автоматической симуляции
        self.auto_sim = True
        self.target_water = 12.45
        self.target_temp = 45.2

        self.setup_ui()
        self.update_data()
        
        # Запускаем автоматический таймер обновления
        self.auto_update()

    def setup_ui(self):
        # ВЕРХНЯЯ ПАНЕЛЬ
        header = tk.Frame(self.root, bg="#1f1f1f", height=50)
        header.pack(fill=tk.X)
        lbl_title = tk.Label(header, text="МНОГОФАЗНЫЙ ПОТОЧНЫЙ ВЛАГОМЕР «КВАЛИТЕТ» ВМП.0704", 
                             fg="#00ff00", bg="#1f1f1f", font=("Arial", 16, "bold"))
        lbl_title.pack(pady=10)

        main_frame = tk.Frame(self.root, bg="#2b2b2b")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ЛЕВАЯ ПАНЕЛЬ
        left_frame = tk.Frame(main_frame, bg="#2b2b2b")
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        self.create_indicator(left_frame, "ВЛАЖНОСТЬ (Объемная доля воды)", "%", self.water_content, "#00ff00", 0)
        self.create_indicator(left_frame, "ТЕМПЕРАТУРА ПОТОКА", "°C", self.temperature, "#ffaa00", 1)

        raw_frame = tk.LabelFrame(left_frame, text="Аналоговые сигналы", fg="#aaaaaa", bg="#2b2b2b", font=("Arial", 10))
        raw_frame.pack(fill=tk.X, pady=10, ipady=5)
        
        self.lbl_v3 = tk.Label(raw_frame, text=f"Напряжение датчика (U3): {self.voltage_out:.2f} В", fg="#ffffff", bg="#2b2b2b", font=("Consolas", 12))
        self.lbl_v3.pack(anchor="w", padx=10)
        
        self.lbl_v5 = tk.Label(raw_frame, text=f"Напряжение термодатчика (U5): {self.voltage_temp:.2f} В", fg="#ffffff", bg="#2b2b2b", font=("Consolas", 12))
        self.lbl_v5.pack(anchor="w", padx=10)

        adc_frame = tk.LabelFrame(left_frame, text="Выход АЦП (8-бит)", fg="#aaaaaa", bg="#2b2b2b", font=("Arial", 10))
        adc_frame.pack(fill=tk.X, pady=5, ipady=5)
        self.lbl_adc = tk.Label(adc_frame, text=f"Код: {self.adc_code} (10101011)", fg="#00ffff", bg="#2b2b2b", font=("Consolas", 14, "bold"))
        self.lbl_adc.pack()

        # Кнопка переключения режима
        self.btn_sim = tk.Button(left_frame, text="ПАУЗА АВТОМАТИЧЕСКОЙ СИМУЛЯЦИИ", 
                            command=self.toggle_simulation, bg="#444444", fg="#ffffff", font=("Arial", 10, "bold"))
        self.btn_sim.pack(fill=tk.X, pady=20, ipady=10)

        # ПРАВАЯ ПАНЕЛЬ (ОСЦИЛЛОГРАММА)
        right_frame = tk.Frame(main_frame, bg="#1f1f1f", bd=2, relief=tk.SUNKEN)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        lbl_osc = tk.Label(right_frame, text="ОСЦИЛЛОГРАММА СИГНАЛОВ", fg="#aaaaaa", bg="#1f1f1f", font=("Arial", 12))
        lbl_osc.pack(pady=5)

        self.fig, self.ax = plt.subplots(figsize=(7, 5), dpi=100)
        self.fig.patch.set_facecolor('#1f1f1f')
        self.ax.set_facecolor('#000000')
        self.ax.tick_params(colors='white')
        self.ax.grid(True, color='#333333')
        self.ax.set_ylim(-3.5, 3.5)
        self.ax.set_xlim(0, 2)

        self.line_sine, = self.ax.plot([], [], color='#00ff00', label='Вход (U1A)')
        self.line_dc, = self.ax.plot([], [], color='#ff0000', label='Выход (Фильтр)')
        self.ax.legend(loc='upper right', facecolor='#222222', labelcolor='white')

        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.animate_oscilloscope()

    def create_indicator(self, parent, title, unit, value, color, row):
        frame = tk.Frame(parent, bg="#1f1f1f", bd=2, relief=tk.GROOVE)
        frame.pack(fill=tk.X, pady=10, ipady=10)
        
        lbl_title = tk.Label(frame, text=title, fg="#aaaaaa", bg="#1f1f1f", font=("Arial", 10))
        lbl_title.pack()
        
        lbl_val = tk.Label(frame, text=f"{value:.2f} {unit}", fg=color, bg="#1f1f1f", font=("Consolas", 28, "bold"))
        lbl_val.pack()
        
        if row == 0:
            self.lbl_water = lbl_val
        else:
            self.lbl_temp = lbl_val

    def toggle_simulation(self):
        self.auto_sim = not self.auto_sim
        if self.auto_sim:
            self.btn_sim.config(text="ПАУЗА АВТОМАТИЧЕСКОЙ СИМУЛЯЦИИ", bg="#444444")
        else:
            self.btn_sim.config(text="ЗАПУСТИТЬ АВТОМАТИКУ", bg="#aa3333")

    def auto_update(self):
        # Эта функция вызывается каждые 100 мс (10 раз в секунду)
        if self.auto_sim:
            # Раз в секунду (каждые 10 тиков) задаем новую цель для плавного изменения
            if random.random() < 0.1: 
                self.target_water = random.uniform(5.0, 45.0) # Новая случайная влажность
                self.target_temp = random.uniform(30.0, 70.0) # Новая случайная температура

            # Плавно (с шагом 0.2) приближаем текущее значение к цели
            self.water_content += (self.target_water - self.water_content) * 0.05
            self.temperature += (self.target_temp - self.temperature) * 0.05
            
            # Пересчитываем вольтметры
            self.voltage_out = 0.5 + (self.water_content / 100) * 4.5 
            self.voltage_temp = 0.1 + (self.temperature / 100) * 1.0 
            self.adc_code = int((self.voltage_out / 5.0) * 255)

            self.update_data()

        # Зацикливаем таймер
        self.root.after(100, self.auto_update)

    def update_data(self):
        self.lbl_water.config(text=f"{self.water_content:.2f} %")
        self.lbl_temp.config(text=f"{self.temperature:.1f} °C")
        self.lbl_v3.config(text=f"Напряжение датчика (U3): {self.voltage_out:.2f} В")
        self.lbl_v5.config(text=f"Напряжение термодатчика (U5): {self.voltage_temp:.2f} В")
        
        bin_code = format(self.adc_code, '08b')
        self.lbl_adc.config(text=f"Код: {self.adc_code} ({bin_code})")

    def animate_oscilloscope(self):
        t = np.linspace(0, 2, 200)
        sine_wave = 2.0 * np.sin(2 * np.pi * 2 * t) 
        
        # Красная линия теперь отражает реальное (плавно меняющееся) напряжение
        dc_wave = np.full_like(t, self.voltage_out)
        ripple = 0.1 * np.sin(2 * np.pi * 10 * t)
        dc_wave = dc_wave + ripple

        self.line_sine.set_data(t, sine_wave)
        self.line_dc.set_data(t, dc_wave)

        self.canvas.draw()
        self.root.after(50, self.animate_oscilloscope)

if __name__ == "__main__":
    root = tk.Tk()
    app = VlagomerPanel(root)
    root.mainloop()