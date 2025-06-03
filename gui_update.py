import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import subprocess
import threading
import re
import os
import time

class AnimePlayerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Anime Player")
        self.root.geometry("600x400")

        # Playback state
        self.is_playing = False
        self.current_process = None

        # Color palettes (Material 3-inspired)
        self.palettes = {
            "Teal": {
                "primary": "#00695C",  # Deep teal
                "primary_light": "#4DB6AC",
                "surface": "#E0F2F1",
                "surface_card": "#FFFFFF",
                "text": "#212121",
                "text_secondary": "#757575",
                "high_contrast_text": "#000000",
            },
            "Purple": {
                "primary": "#6750A4",  # Deep purple
                "primary_light": "#B39DDB",
                "surface": "#F3E5F5",
                "surface_card": "#FFFFFF",
                "text": "#212121",
                "text_secondary": "#757575",
                "high_contrast_text": "#000000",
            },
            "Amber": {
                "primary": "#FBC02D",  # Amber
                "primary_light": "#FFD95A",
                "surface": "#FFF8E1",
                "surface_card": "#FFFFFF",
                "text": "#212121",
                "text_secondary": "#757575",
                "high_contrast_text": "#000000",
            }
        }

        # Default palette and contrast mode
        self.current_palette = "Teal"
        self.high_contrast = False

        # Apply initial theme
        self.apply_theme()

        # Main container
        self.root.configure(bg=self.palettes[self.current_palette]["surface"])

        # Top bar for app title and theme selection
        top_frame = ttk.Frame(self.root, style="Top.TFrame")
        top_frame.pack(fill=tk.X, padx=16, pady=(8, 0))
        ttk.Label(top_frame, text="Anime Player", font=("Roboto", 20, "bold"), style="Header.TLabel").pack(side=tk.LEFT)
        self.theme_var = tk.StringVar(value=self.current_palette)
        theme_dropdown = ttk.Combobox(top_frame, textvariable=self.theme_var, values=list(self.palettes.keys()) + ["Custom"], state="readonly", width=10, style="Material.TCombobox")
        theme_dropdown.pack(side=tk.RIGHT, padx=(0, 8))
        theme_dropdown.bind("<<ComboboxSelected>>", self.change_theme)
        ttk.Button(top_frame, text="Toggle High Contrast", style="Material.TButton", command=self.toggle_high_contrast).pack(side=tk.RIGHT, padx=(0, 8))

        # Search bar
        self.search_query = tk.StringVar()
        search_frame = ttk.Frame(self.root, style="TFrame")
        search_frame.pack(fill=tk.X, padx=16, pady=8)
        ttk.Label(search_frame, text="Search Anime:", font=("Roboto", 14, "bold"), style="TLabel").pack(side=tk.LEFT, padx=(0, 8))
        search_entry = ttk.Entry(search_frame, textvariable=self.search_query, font=("Roboto", 12), style="Material.TEntry")
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        ttk.Button(search_frame, text="Search", command=self.search_anime, style="Material.TButton").pack(side=tk.LEFT)

        # Quality selector
        quality_frame = ttk.Frame(self.root, style="TFrame")
        quality_frame.pack(fill=tk.X, padx=16, pady=8)
        ttk.Label(quality_frame, text="Quality:", font=("Roboto", 14, "bold"), style="TLabel").pack(side=tk.LEFT, padx=(0, 8))
        self.quality_var = tk.StringVar(value="best")
        quality_entry = ttk.Entry(quality_frame, textvariable=self.quality_var, width=10, font=("Roboto", 12), style="Material.TEntry")
        quality_entry.pack(side=tk.LEFT)

        # Control buttons
        controls_frame = ttk.Frame(self.root, style="TFrame")
        controls_frame.pack(fill=tk.X, padx=16, pady=8)
        self.play_btn = ttk.Button(controls_frame, text="Play", command=self.play_selected, style="Material.TButton")
        self.play_btn.pack(side=tk.LEFT, padx=4)
        self.replay_btn = ttk.Button(controls_frame, text="Replay", command=self.play_replay, style="Material.TButton")
        self.replay_btn.pack(side=tk.LEFT, padx=4)
        self.quality_btn = ttk.Button(controls_frame, text="Change Quality", command=self.change_quality, style="Material.TButton")
        self.quality_btn.pack(side=tk.LEFT, padx=4)
        self.quit_btn = ttk.Button(controls_frame, text="Quit", command=self.quit_playback, style="Material.TButton")
        self.quit_btn.pack(side=tk.LEFT, padx=4)

        # Results list (anime selection)
        self.selected_anime_index = None
        self.results_list = tk.Listbox(
            self.root,
            height=10,
            font=("Roboto", 12),
            bg=self.palettes[self.current_palette]["surface_card"],
            fg=self.palettes[self.current_palette]["text"],
            selectbackground=self.palettes[self.current_palette]["primary_light"],
            selectforeground="#FFFFFF",
            bd=1,
            highlightthickness=0,
            relief="groove"
        )
        self.results_list.pack(fill=tk.BOTH, padx=16, pady=(0, 8), expand=True)
        self.results_list.bind('<<ListboxSelect>>', self.on_anime_select)

        # Progress bar (hidden initially)
        self.progress_frame = ttk.Frame(self.root, style="TFrame")
        self.progress_label = ttk.Label(self.progress_frame, text="Loading Episode: 0%", font=("Roboto", 12), style="TLabel")
        self.progress_label.pack(pady=(0, 4))
        self.progress = ttk.Progressbar(self.progress_frame, length=300, mode="determinate", style="Material.Horizontal.TProgressbar")
        self.progress.pack()

        # Log area
        from tkinter.scrolledtext import ScrolledText
        self.results_text = ScrolledText(
            self.root,
            height=8,
            font=("Roboto", 10),
            bg=self.palettes[self.current_palette]["surface_card"],
            fg=self.palettes[self.current_palette]["text"],
            bd=1,
            highlightthickness=0,
            relief="groove"
        )
        self.results_text.pack(fill=tk.BOTH, padx=16, pady=(0, 8), expand=False)

        # Data store
        self.anime_data = []

        # Paths
        self.git_bash_path = r"C:\\Program Files\\Git\\bin\\bash.exe"
        self.ani_cli_path = r"/c/Users/Victus/scoop/apps/ani-cli/current/ani-cli"

    def apply_theme(self):
        palette = self.palettes[self.current_palette]
        text_color = palette["high_contrast_text"] if self.high_contrast else palette["text"]

        # Configure ttk styles
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.style.configure("TFrame", background=palette["surface"])
        self.style.configure("Top.TFrame", background=palette["surface_card"], borderwidth=1, relief="groove")
        self.style.configure("TLabel", background=palette["surface"], foreground=text_color, font=("Roboto", 12))
        self.style.configure("Header.TLabel", background=palette["surface_card"], foreground=text_color, font=("Roboto", 20, "bold"))
        self.style.configure("Material.TButton", background=palette["primary"], foreground="#FFFFFF", font=("Roboto", 10, "bold"), padding=12, borderwidth=0)
        self.style.map("Material.TButton", background=[("active", palette["primary_light"]), ("pressed", palette["primary"]), ("disabled", "#B0BEC5")], foreground=[("disabled", "#BDBDBD")])
        self.style.configure("Material.TEntry", fieldbackground=palette["surface_card"], foreground=text_color, font=("Roboto", 12))
        self.style.configure("Material.TCombobox", fieldbackground=palette["surface_card"], foreground=text_color, font=("Roboto", 12))
        self.style.configure("Material.Horizontal.TProgressbar", troughcolor=palette["surface"], background=palette["primary"], borderwidth=0)

        # Update Listbox and ScrolledText colors
        if hasattr(self, "results_list"):
            self.results_list.config(
                bg=palette["surface_card"],
                fg=text_color,
                selectbackground=palette["primary_light"],
            )
        if hasattr(self, "results_text"):
            self.results_text.config(
                bg=palette["surface_card"],
                fg=text_color,
            )
        if hasattr(self, "progress_label"):
            self.progress_label.config(background=palette["surface"], foreground=text_color)

        # Update root background
        self.root.configure(bg=palette["surface"])

    def change_theme(self, event=None):
        selected = self.theme_var.get()
        if selected == "Custom":
            color = colorchooser.askcolor(title="Choose a Primary Color", initialcolor=self.palettes[self.current_palette]["primary"])[1]
            if color:
                self.palettes["Custom"] = {
                    "primary": color,
                    "primary_light": self.lighten_color(color, 0.3),
                    "surface": self.lighten_color(color, 0.9),
                    "surface_card": "#FFFFFF",
                    "text": "#212121",
                    "text_secondary": "#757575",
                    "high_contrast_text": "#000000",
                }
                self.current_palette = "Custom"
        else:
            self.current_palette = selected
        self.apply_theme()

    def lighten_color(self, hex_color, factor):
        """Lighten a hex color by a factor (0 to 1)."""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        lightened = tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)
        return f"#{lightened[0]:02x}{lightened[1]:02x}{lightened[2]:02x}"

    def toggle_high_contrast(self):
        self.high_contrast = not self.high_contrast
        self.apply_theme()

    def log_message(self, msg):
        self.results_text.config(state='normal')
        self.results_text.insert(tk.END, msg + '\n')
        self.results_text.see(tk.END)
        self.results_text.config(state='disabled')

    def clear_results_text(self):
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state='disabled')

    def search_anime(self):
        query = self.search_query.get().strip()
        if not query:
            self.log_message("Please enter a search term")
            return
        self.clear_results_text()
        self.log_message(f"Searching for: {query}...")
        self.results_list.delete(0, tk.END)
        self.anime_data = []
        threading.Thread(target=self._do_search, args=(query,), daemon=True).start()

    def _do_search(self, query):
        try:
            cmd = [self.git_bash_path, "-c", f"'{self.ani_cli_path}' --list '{query}'"]
            self.root.after(0, self.log_message, f"[DEBUG] Launching search: {cmd}")
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True,
                env=os.environ.copy()
            )
            self.anime_data = []
            self.results_list.delete(0, tk.END)
            for line in process.stdout:
                clean_line = self.strip_ansi(line.strip())
                self.root.after(0, self.log_message, f"[DEBUG] stdout: {clean_line}")
                if '\t' in clean_line:
                    anime_id, anime_title = clean_line.split('\t', 1)
                    self.anime_data.append((anime_id, anime_title))
                    self.root.after(0, self.results_list.insert, tk.END, anime_title)
            for err_line in process.stderr:
                clean_err = self.strip_ansi(err_line.strip())
                self.root.after(0, self.log_message, f"[DEBUG] stderr: {clean_err}")
            retcode = process.wait()
            self.root.after(0, self.log_message, f"Found {len(self.anime_data)} results")
            if retcode != 0:
                self.root.after(0, self.log_message, f"[ERROR] ani-cli exited with code {retcode}")
            self.root.after(0, self.results_list.update)
        except Exception as e:
            self.root.after(0, self.log_message, f"Search error: {str(e)}")

    def on_anime_select(self, event):
        if self.is_playing:
            self.log_message("Playback in progress, please wait.")
            return
        selection = self.results_list.curselection()
        if not selection:
            return
        self.selected_anime_index = selection[0]
        anime_id, anime_title_full = self.anime_data[self.selected_anime_index]
        anime_title = anime_title_full.split(' (')[0]
        self.clear_results_text()
        self.log_message(f"Fetching episodes for: {anime_title}...")
        threading.Thread(
            target=self._fetch_and_prompt_episode,
            args=(anime_id, anime_title),
            daemon=True
        ).start()

    def _fetch_and_prompt_episode(self, anime_id, anime_title):
        try:
            cmd = [self.git_bash_path, "-c", f"'{self.ani_cli_path}' --episodes {anime_id}"]
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True,
                env=os.environ.copy()
            )
            episodes = []
            for line in process.stdout:
                clean_line = self.strip_ansi(line.strip())
                if clean_line.isdigit():
                    episodes.append(clean_line)
            for err_line in process.stderr:
                clean_err = self.strip_ansi(err_line.strip())
                self.root.after(0, self.log_message, f"[DEBUG] stderr: {clean_err}")
            process.wait()
            if episodes:
                episode_labels = [f"Episode {ep}" for ep in episodes]
                self.root.after(0, self._show_episode_dialog, episode_labels, anime_id, anime_title)
            else:
                self.root.after(0, self.log_message, "No episodes found.")
        except Exception as e:
            self.root.after(0, self.log_message, f"Episode fetch error: {str(e)}")

    def _show_episode_dialog(self, episode_labels, anime_id, anime_title):
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Episode")
        dialog.geometry("300x400")
        dialog.configure(bg=self.palettes[self.current_palette]["surface_card"])
        dialog.transient(self.root)
        dialog.grab_set()

        # Material 3-inspired dialog styling
        text_color = self.palettes[self.current_palette]["high_contrast_text"] if self.high_contrast else self.palettes[self.current_palette]["text"]
        ttk.Label(dialog, text="Select an Episode", font=("Roboto", 16, "bold"), background=self.palettes[self.current_palette]["surface_card"], foreground=text_color).pack(pady=(16, 8))

        # Listbox for episode selection
        listbox = tk.Listbox(
            dialog,
            font=("Roboto", 12),
            bg=self.palettes[self.current_palette]["surface_card"],
            fg=text_color,
            selectbackground=self.palettes[self.current_palette]["primary_light"],
            selectforeground="#FFFFFF",
            bd=0,
            highlightthickness=0
        )
        for label in episode_labels:
            listbox.insert(tk.END, label)
        listbox.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)
        listbox.select_set(0)

        # Buttons
        button_frame = ttk.Frame(dialog, style="TFrame")
        button_frame.pack(fill=tk.X, padx=16, pady=8)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy, style="Material.TButton").pack(side=tk.RIGHT, padx=4)
        ttk.Button(button_frame, text="Select", command=lambda: self._on_episode_select(dialog, listbox, episode_labels, anime_id, anime_title), style="Material.TButton").pack(side=tk.RIGHT, padx=4)

        # Center the dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

    def _on_episode_select(self, dialog, listbox, episode_labels, anime_id, anime_title):
        selection = listbox.curselection()
        if selection:
            idx = selection[0]
            selected_label = episode_labels[idx]
            selected_ep = selected_label.split(" ")[1]  # Extract episode number
            dialog.destroy()
            self._play_episode_with_progress(anime_id, anime_title, selected_ep)
        else:
            self.log_message("Episode selection cancelled.")
            dialog.destroy()

    def _play_episode_with_progress(self, anime_id, anime_title, episode):
        self.clear_results_text()
        self.log_message(f"Preparing: {anime_title} (ep: {episode})...")
        
        # Show progress bar
        self.progress_frame.pack(pady=8)
        self.progress["value"] = 0
        self.progress_label.config(text="Loading Episode: 0%")
        
        # Simulate loading progress (since ani-cli doesn't provide real-time updates)
        def update_progress():
            for i in range(1, 101):
                self.progress["value"] = i
                self.progress_label.config(text=f"Loading Episode: {i}%")
                self.root.update()
                time.sleep(0.03)  # Simulate 3-second loading
            self.progress_frame.pack_forget()
            self._play_episode(anime_id, anime_title, episode)

        # Run progress in a separate thread to avoid blocking UI
        threading.Thread(target=update_progress, daemon=True).start()

    def _play_episode(self, anime_id, anime_title, episode):
        quality = self.quality_var.get().strip() or "best"
        threading.Thread(
            target=self._play_selected_anime,
            args=(anime_id, episode, quality),
            daemon=True
        ).start()

    def _play_selected_anime(self, anime_id, episode, quality):
        try:
            self.is_playing = True
            self.play_btn.config(state='disabled')
            self.replay_btn.config(state='disabled')
            self.quality_btn.config(state='disabled')
            cmd = [self.git_bash_path, "-c", f"'{self.ani_cli_path}' --id '{anime_id}' -e '{episode}' -q '{quality}'"]
            self.root.after(0, self.log_message, f"[DEBUG] Playback CMD: {cmd}")
            env = os.environ.copy()
            env["ANI_CLI_NON_INTERACTIVE"] = "1"
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True,
                env=env
            )
            # Monitor subprocess for completion or termination
            while self.current_process.poll() is None:
                stdout_line = self.current_process.stdout.readline().strip()
                if stdout_line:
                    clean_line = self.strip_ansi(stdout_line)
                    self.root.after(0, self.log_message, clean_line)
                stderr_line = self.current_process.stderr.readline().strip()
                if stderr_line:
                    clean_err = self.strip_ansi(stderr_line)
                    self.root.after(0, self.log_message, f"[DEBUG] stderr: {clean_err}")
            retcode = self.current_process.returncode
            self.root.after(0, self.log_message, f"Playback finished with code {retcode}")
        except Exception as e:
            self.root.after(0, self.log_message, f"Play error: {str(e)}")
        finally:
            self.is_playing = False
            self.current_process = None
            self.play_btn.config(state='normal')
            self.replay_btn.config(state='normal')
            self.quality_btn.config(state='normal')
            # Clear Listbox selection to prevent accidental replay
            self.root.after(0, self.results_list.selection_clear, 0, tk.END)
            self.root.after(0, self.log_message, "[DEBUG] Playback state reset")

    def play_selected(self):
        if self.is_playing:
            self.log_message("Playback in progress, please wait.")
            return
        if self.selected_anime_index is None:
            self.log_message("Please select an anime first.")
            return
        self.on_anime_select(None)

    def play_replay(self):
        if self.is_playing:
            self.log_message("Playback in progress, please wait.")
            return
        self.play_selected()

    def change_quality(self):
        if self.is_playing:
            self.log_message("Playback in progress, please wait.")
            return
        dialog = tk.Toplevel(self.root)
        dialog.title("Change Quality")
        dialog.geometry("300x150")
        dialog.configure(bg=self.palettes[self.current_palette]["surface_card"])
        dialog.transient(self.root)
        dialog.grab_set()

        text_color = self.palettes[self.current_palette]["high_contrast_text"] if self.high_contrast else self.palettes[self.current_palette]["text"]
        ttk.Label(dialog, text="Enter Quality", font=("Roboto", 16, "bold"), background=self.palettes[self.current_palette]["surface_card"], foreground=text_color).pack(pady=(16, 8))
        quality_var = tk.StringVar(value=self.quality_var.get())
        entry = ttk.Entry(dialog, textvariable=quality_var, font=("Roboto", 12), style="Material.TEntry")
        entry.pack(fill=tk.X, padx=16, pady=8)

        button_frame = ttk.Frame(dialog, style="TFrame")
        button_frame.pack(fill=tk.X, padx=16, pady=8)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy, style="Material.TButton").pack(side=tk.RIGHT, padx=4)
        ttk.Button(button_frame, text="Apply", command=lambda: self._apply_quality(dialog, quality_var), style="Material.TButton").pack(side=tk.RIGHT, padx=4)

        # Center the dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

    def _apply_quality(self, dialog, quality_var):
        new_quality = quality_var.get().strip()
        if new_quality:
            self.quality_var.set(new_quality)
            self.play_selected()
        dialog.destroy()

    def quit_playback(self):
        if self.is_playing and self.current_process:
            try:
                self.current_process.terminate()
                self.current_process.wait()
                self.log_message("Playback terminated.")
            except Exception as e:
                self.log_message(f"Error terminating playback: {str(e)}")
            finally:
                self.is_playing = False
                self.current_process = None
                self.play_btn.config(state='normal')
                self.replay_btn.config(state='normal')
                self.quality_btn.config(state='normal')
                self.root.after(0, self.results_list.selection_clear, 0, tk.END)
                self.root.after(0, self.log_message, "[DEBUG] Playback state reset after quit")
        else:
            self.log_message("No playback process running.")

    def strip_ansi(self, line):
        return re.sub(r'\x1b\[([0-?]*[ -/]*[@-~])', '', line)

if __name__ == "__main__":
    root = tk.Tk()
    app = AnimePlayerGUI(root)
    root.mainloop()