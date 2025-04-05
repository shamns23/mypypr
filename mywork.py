import customtkinter as ctk
import platform
import os
import subprocess
import distro
import threading
import json
import psutil
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Callable, Optional
from tkinter import messagebox

class SystemToolsGUI:
    def __init__(self):
        # تهيئة مسارات الملفات أولاً
        self.config_dir = Path.home() / ".config" / "system_tools"
        self.config_file = self.config_dir / "config.json"
        self.log_dir = self.config_dir / "logs"
        
        # إنشاء المجلدات اللازمة
        self.setup_directories()
        
        # تهيئة نظام التسجيل
        self.setup_logging()
        
        # تحميل الإعدادات
        self.load_config()
        
        # الترجمات
        self.translations = {
            'en': {
                'window_title': "System Tools Installation Manager",
                'os_info': "Operating System: {}",
                'cpu_info': "CPU: {} ({} cores)",
                'memory_info': "Memory: {:.1f}GB Used / {:.1f}GB Total",
                'disk_info': "Disk Space: {:.1f}GB Free / {:.1f}GB Total",
                'install_nmap': "Install Nmap",
                'install_brave': "Install Brave Browser",
                'install_vscode': "Install VS Code",
                'install_chrome': "Install Chrome",
                'install_firefox': "Install Firefox",
                'install_vlc': "Install VLC",
                'install_gimp': "Install GIMP",
                'install_obs': "Install OBS Studio",
                'install_discord': "Install Discord",
                'install_steam': "Install Steam",
                'install_spotify': "Install Spotify",
                'install_docker': "Install Docker",
                'install_nodejs': "Install Node.js",
                'install_python': "Install Python Tools",
                'installing': "Installing...",
                'error': "Error: {}",
                'executing': "Executing: {}",
                'success': "Installation Complete!",
                'failed': "Installation Failed!",
                'terminal_output': "Terminal Output:",
                'progress': "Progress: {} of {} steps",
                'system_update': "System Update",
                'clear_output': "Clear Output",
                'save_log': "Save Log",
                'settings': "Settings",
                'about': "About",
                'quit': "Quit",
                'confirm_quit': "Are you sure you want to quit?",
                'yes': "Yes",
                'no': "No",
                'theme_light': "Light Theme",
                'theme_dark': "Dark Theme",
                'theme_system': "System Theme",
                'installation_history': "Installation History",
                'last_update': "Last Update: {}",
                'never': "Never",
                'update_available': "Updates Available",
                'system_updated': "System is up to date",
                'loading': "Loading...",
                'ready': "Ready"
            }
        }
        
        # تعريف التطبيقات
        self.apps = {
            'development': {
                'vscode': {
                    'name': 'install_vscode',
                    'description': 'Code Editor',
                    'commands': [
                        "sudo apt install software-properties-common apt-transport-https wget -y",
                        "wget -q https://packages.microsoft.com/keys/microsoft.asc -O- | sudo apt-key add -",
                        "sudo add-apt-repository 'deb [arch=amd64] https://packages.microsoft.com/repos/vscode stable main'",
                        "sudo apt update",
                        "sudo apt install code -y"
                    ]
                },
                'nodejs': {
                    'name': 'install_nodejs',
                    'description': 'JavaScript Runtime',
                    'commands': [
                        "curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -",
                        "sudo apt install nodejs -y"
                    ]
                }
            },
            'browsers': {
                'brave': {
                    'name': 'install_brave',
                    'description': 'Privacy Browser',
                    'commands': [
                        "sudo apt install apt-transport-https curl -y",
                        "sudo curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg",
                        'echo "deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg arch=amd64] https://brave-browser-apt-release.s3.brave.com/ stable main" | sudo tee /etc/apt/sources.list.d/brave-browser-release.list',
                        "sudo apt update",
                        "sudo apt install brave-browser -y"
                    ]
                },
                'chrome': {
                    'name': 'install_chrome',
                    'description': 'Google Chrome',
                    'commands': [
                        "wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb",
                        "sudo apt install ./google-chrome-stable_current_amd64.deb -y",
                        "rm google-chrome-stable_current_amd64.deb"
                    ]
                }
            },
            'multimedia': {
                'vlc': {
                    'name': 'install_vlc',
                    'description': 'Media Player',
                    'commands': ["sudo apt install vlc -y"]
                },
                'obs': {
                    'name': 'install_obs',
                    'description': 'Streaming Software',
                    'commands': ["sudo apt install obs-studio -y"]
                }
            },
            'utilities': {
                'nmap': {
                    'name': 'install_nmap',
                    'description': 'Network Scanner',
                    'commands': ["sudo apt install nmap -y"]
                },
                'docker': {
                    'name': 'install_docker',
                    'description': 'Container Platform',
                    'commands': [
                        "sudo apt update",
                        "sudo apt install apt-transport-https ca-certificates curl software-properties-common -y",
                        "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg",
                        'echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null',
                        "sudo apt update",
                        "sudo apt install docker-ce docker-ce-cli containerd.io -y",
                        "sudo usermod -aG docker $USER"
                    ]
                }
            }
        }
        
        self.current_lang = 'en'
        self.setup_gui()
        self.load_installation_history()

    def setup_directories(self):
        """إنشاء المجلدات الضرورية"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def setup_logging(self):
        """تهيئة نظام التسجيل"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(self.log_dir / f"system_tools_{datetime.now():%Y%m%d}.log")
            ]
        )
        self.logger = logging.getLogger(__name__)

    def load_config(self):
        """تحميل الإعدادات من الملف"""
        try:
            if self.config_file.exists():
                with open(self.config_file) as f:
                    self.config = json.load(f)
            else:
                self.config = {
                    'theme': 'dark',
                    'installation_history': [],
                    'last_update': None
                }
                self.save_config()
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            self.config = {'theme': 'dark', 'installation_history': []}

    def save_config(self):
        """حفظ الإعدادات في الملف"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")

    def setup_gui(self):
        """تهيئة واجهة المستخدم"""
        self.root = ctk.CTk()
        self.root.title(self.get_text('window_title'))
        self.root.geometry("1200x800")
        ctk.set_appearance_mode(self.config.get('theme', 'dark'))
        
        # الإطار الرئيسي
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # إنشاء أقسام الواجهة
        self.create_menu_bar()
        self.create_system_info()
        self.create_notebook()
        self.create_progress_section()
        self.create_status_bar()

    def get_text(self, key: str) -> str:
        """الحصول على النص المترجم"""
        return self.translations[self.current_lang].get(key, f"[{key}]")

    def create_menu_bar(self):
        """إنشاء شريط القوائم"""
        menu_frame = ctk.CTkFrame(self.main_frame)
        menu_frame.pack(fill="x", padx=5, pady=5)
        
        # أزرار القوائم
        buttons = [
            ("System Update", self.system_update),
            ("Settings", self.show_settings),
            ("History", self.show_history),
            ("About", self.show_about)
        ]
        
        for text, command in buttons:
            btn = ctk.CTkButton(
                menu_frame,
                text=self.get_text(text.lower().replace(" ", "_")),
                command=command,
                width=120
            )
            btn.pack(side="left", padx=5)
        
        # اختيار السمة
        self.theme_var = ctk.StringVar(value=self.config.get('theme', 'dark'))
        theme_menu = ctk.CTkOptionMenu(
            menu_frame,
            values=["light", "dark", "system"],
            variable=self.theme_var,
            command=self.change_theme
        )
        theme_menu.pack(side="right", padx=5)

    def create_system_info(self):
        """إنشاء قسم معلومات النظام"""
        info_frame = ctk.CTkFrame(self.main_frame)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        # معلومات النظام
        system_info = self.get_detailed_system_info()
        for key, value in system_info.items():
            label = ctk.CTkLabel(
                info_frame,
                text=f"{key}: {value}",
                font=("Arial", 12)
            )
            label.pack(pady=2)

    def get_detailed_system_info(self) -> Dict[str, str]:
        """الحصول على معلومات مفصلة عن النظام"""
        try:
            # معلومات نظام التشغيل
            os_name = distro.name(pretty=True) if hasattr(distro, 'name') else platform.system()
            os_version = distro.version() if hasattr(distro, 'version') else platform.version()
            
            # معلومات المعالج
            cpu_info = platform.processor()
            cpu_cores = psutil.cpu_count(logical=False)
            cpu_threads = psutil.cpu_count(logical=True)
            
            # معلومات الذاكرة
            mem = psutil.virtual_memory()
            mem_total_gb = mem.total / (1024 ** 3)
            mem_used_gb = mem.used / (1024 ** 3)
            
            # معلومات القرص
            disk = psutil.disk_usage('/')
            disk_total_gb = disk.total / (1024 ** 3)
            disk_free_gb = disk.free / (1024 ** 3)
            
            return {
                "OS": f"{os_name} {os_version}",
                "CPU": f"{cpu_info} ({cpu_cores} cores, {cpu_threads} threads)",
                "Memory": self.get_text('memory_info').format(mem_used_gb, mem_total_gb),
                "Disk": self.get_text('disk_info').format(disk_free_gb, disk_total_gb),
                "Python": platform.python_version()
            }
        except Exception as e:
            self.logger.error(f"Failed to get system info: {e}")
            return {
                "OS": "Unknown",
                "CPU": "Unknown",
                "Memory": "Unknown",
                "Disk": "Unknown",
                "Python": platform.python_version()
            }

    def create_notebook(self):
        """إنشاء دفتر تبويب للتطبيقات"""
        self.notebook = ctk.CTkTabview(self.main_frame)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)
        
        # إنشاء تبويبات لكل فئة
        for category, apps in self.apps.items():
            tab = self.notebook.add(category.title())
            self.create_category_buttons(tab, apps)

    def create_category_buttons(self, tab, apps):
        """إنشاء أزرار للتطبيقات في كل فئة"""
        button_frame = ctk.CTkFrame(tab)
        button_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        row = 0
        col = 0
        max_cols = 3
        
        button_style = {
            "font": ("Arial", 14, "bold"),
            "width": 200,
            "height": 40,
            "corner_radius": 8
        }
        
        for app_id, app_info in apps.items():
            btn = ctk.CTkButton(
                button_frame,
                text=f"{self.get_text(app_info['name'])}\n{app_info['description']}",
                command=lambda a=app_id, i=app_info: self.run_installation(
                    lambda: self.install_app(a, i)
                ),
                **button_style
            )
            btn.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            setattr(self, f"{app_id}_btn", btn)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def create_progress_section(self):
        """إنشاء قسم التقدم والإخراج"""
        progress_frame = ctk.CTkFrame(self.main_frame)
        progress_frame.pack(fill="x", padx=20, pady=10)
        
        # شريط التقدم
        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text=self.get_text('progress').format(0, 0),
            font=("Arial", 12)
        )
        self.progress_label.pack(pady=5)
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", pady=5)
        self.progress_bar.set(0)
        
        # منطقة الإخراج
        output_label = ctk.CTkLabel(
            progress_frame,
            text=self.get_text('terminal_output'),
            font=("Arial", 12, "bold")
        )
        output_label.pack(pady=5)
        
        self.output_text = ctk.CTkTextbox(
            progress_frame,
            height=150,
            font=("Courier", 12)
        )
        self.output_text.pack(fill="x", pady=5)
        
        # أزرار التحكم
        button_frame = ctk.CTkFrame(progress_frame)
        button_frame.pack(fill="x", pady=5)
        
        ctk.CTkButton(
            button_frame,
            text=self.get_text('clear_output'),
            command=self.clear_output,
            width=120
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text=self.get_text('save_log'),
            command=self.save_log,
            width=120
        ).pack(side="left", padx=5)

    def create_status_bar(self):
        """إنشاء شريط الحالة"""
        self.status_bar = ctk.CTkLabel(
            self.main_frame,
            text=self.get_text('ready'),
            font=("Arial", 12)
        )
        self.status_bar.pack(fill="x", padx=20, pady=5)

    def update_status(self, message: str):
        """تحديث شريط الحالة"""
        self.status_bar.configure(text=message)
        self.root.update()

    def update_progress(self, current: int, total: int):
        """تحديث شريط التقدم"""
        self.progress_label.configure(
            text=self.get_text('progress').format(current, total)
        )
        self.progress_bar.set(current / total)
        self.root.update()

    def clear_output(self):
        """مسح منطقة الإخراج"""
        self.output_text.delete(1.0, "end")

    def save_log(self):
        """حفظ السجل في ملف"""
        try:
            log_file = self.log_dir / f"installation_{datetime.now():%Y%m%d_%H%M%S}.log"
            with open(log_file, "w") as f:
                f.write(self.output_text.get(1.0, "end"))
            self.update_status(f"Log saved to {log_file}")
        except Exception as e:
            self.update_status(self.get_text('error').format(str(e)))

    def run_installation(self, installation_func: Callable):
        """تشغيل التثبيت في خيط منفصل"""
        thread = threading.Thread(target=installation_func, daemon=True)
        thread.start()

    def install_app(self, app_id: str, app_info: dict):
        """تثبيت التطبيق"""
        self.logger.info(f"Installing {app_id}")
        self.output_text.delete(1.0, "end")
        commands = app_info['commands']
        
        try:
            total_steps = len(commands)
            for i, cmd in enumerate(commands, 1):
                self.output_text.insert("end", f"{self.get_text('executing').format(cmd)}\n")
                self.update_status(f"Running command {i} of {total_steps}")
                
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True
                )
                
                self.output_text.insert("end", f"Output:\n{result.stdout}\n")
                if result.stderr:
                    self.output_text.insert("end", f"Errors:\n{result.stderr}\n")
                
                self.update_progress(i, total_steps)
                self.output_text.see("end")
            
            success = True
            self.output_text.insert("end", f"\n{self.get_text('success')}\n")
        except Exception as e:
            success = False
            self.logger.error(f"Installation failed: {e}")
            self.output_text.insert("end", self.get_text('error').format(str(e)) + "\n")
        
        self.add_to_history(app_id, success)
        self.update_status(self.get_text('ready'))

    def add_to_history(self, app_id: str, success: bool):
        """إضافة التثبيت إلى السجل"""
        entry = {
            'app': app_id,
            'timestamp': datetime.now().isoformat(),
            'success': success
        }
        self.config['installation_history'].append(entry)
        self.save_config()

    def load_installation_history(self):
        """تحميل سجل التثبيتات"""
        if 'installation_history' not in self.config:
            self.config['installation_history'] = []

    def show_history(self):
        """عرض سجل التثبيتات"""
        history_window = ctk.CTkToplevel(self.root)
        history_window.title(self.get_text('installation_history'))
        history_window.geometry("600x400")
        
        textbox = ctk.CTkTextbox(history_window, font=("Courier", 12))
        textbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        if not self.config['installation_history']:
            textbox.insert("end", "No installation history found\n")
        else:
            for entry in self.config['installation_history']:
                status = "Success" if entry['success'] else "Failed"
                textbox.insert(
                    "end",
                    f"{entry['timestamp']} - {entry['app']} - {status}\n"
                )

    def system_update(self):
        """تحديث النظام"""
        self.run_installation(self._perform_system_update)

    def _perform_system_update(self):
        """تنفيذ تحديث النظام"""
        commands = [
            "sudo apt update",
            "sudo apt upgrade -y",
            "sudo apt autoremove -y"
        ]
        
        self.output_text.delete(1.0, "end")
        self.update_status(self.get_text('system_update'))
        
        try:
            total_steps = len(commands)
            for i, cmd in enumerate(commands, 1):
                self.output_text.insert("end", f"{self.get_text('executing').format(cmd)}\n")
                
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True
                )
                
                self.output_text.insert("end", f"Output:\n{result.stdout}\n")
                if result.stderr:
                    self.output_text.insert("end", f"Errors:\n{result.stderr}\n")
                
                self.update_progress(i, total_steps)
                self.output_text.see("end")
            
            self.config['last_update'] = datetime.now().isoformat()
            self.save_config()
            self.output_text.insert("end", f"\n{self.get_text('system_updated')}\n")
        except Exception as e:
            self.output_text.insert("end", self.get_text('error').format(str(e)) + "\n")
        
        self.update_status(self.get_text('ready'))

    def show_settings(self):
        """عرض الإعدادات"""
        settings_window = ctk.CTkToplevel(self.root)
        settings_window.title(self.get_text('settings'))
        settings_window.geometry("400x300")
        
        label = ctk.CTkLabel(settings_window, text="Settings will be added here")
        label.pack(pady=50)

    def show_about(self):
        """عرض معلومات حول البرنامج"""
        about_window = ctk.CTkToplevel(self.root)
        about_window.title(self.get_text('about'))
        about_window.geometry("400x300")
        
        about_text = (
            "System Tools Installation Manager\n\n"
            "Version: 1.0\n"
            "License: MIT\n\n"
            "A tool to easily install common software on Linux systems"
        )
        
        label = ctk.CTkLabel(about_window, text=about_text)
        label.pack(pady=50)

    def change_theme(self, new_theme: str):
        """تغيير سمة الواجهة"""
        ctk.set_appearance_mode(new_theme)
        self.config['theme'] = new_theme
        self.save_config()

    def on_closing(self):
        """معالجة حدث إغلاق النافذة"""
        if messagebox.askyesno(
            self.get_text('quit'),
            self.get_text('confirm_quit')
        ):
            self.root.destroy()

    def run(self):
        """تشغيل التطبيق"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

if __name__ == "__main__":
    app = SystemToolsGUI()
    app.run()