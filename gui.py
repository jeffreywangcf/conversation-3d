import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import time
import subprocess
import audio_split
import scanner
from generator import generate_playbook


class AudioSplitApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Splitter")
        self.file_path = None
        self.animation_running = False

        # UI
        title_label = tk.Label(root, text="Conversation 3D", font=("Helvetica", 20))
        title_label.pack(pady=10)
        self.tree = ttk.Treeview(root, columns=("Hostname", "IP"), show="headings", selectmode="extended")
        self.tree.heading("Hostname", text="Device Name")
        self.tree.heading("IP", text="IP Address")
        self.tree.pack(pady=10)
        refresh_button = tk.Button(root, text="Refresh Devices", command=self.load_devices)
        refresh_button.pack(pady=10)
        select_button = tk.Button(root, text="Select Audio File", command=self.select_file)
        select_button.pack(pady=10)
        self.file_label = tk.Label(root, text="", font=("Helvetica", 14))
        self.file_label.pack(pady=5)
        analyze_button = tk.Button(root, text="Analyze", command=self.start_analysis)
        analyze_button.pack(pady=10)
        self.status_label = tk.Label(root, text="", font=("Helvetica", 14))
        self.status_label.pack(pady=5)

        # init
        self.load_devices()

    def load_devices(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            devices = scanner.scan_network()
            if not devices:
                self.status_label.config(text="No Devices Found.")
                return
            for device in devices:
                self.tree.insert("", "end", values=(device["hostname"], device["ip"]))
        except Exception as e:
            self.status_label.config(text=f"Error loading devices: {e}")

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav")])
        if file_path:
            self.file_path = file_path
            # Display the selected file name in the label
            file_name = os.path.basename(file_path)
            self.file_label.config(text=f"Selected file: {file_name}")

    def get_selected_devices(self):
        selected_devices = []
        for item in self.tree.selection():
            device = self.tree.item(item)["values"]
            selected_devices.append({
                "hostname": device[0],
                "ip": device[1]
            })
        return selected_devices

    def start_analysis(self):
        self.animation_running = True
        self.status_label.config(text="Analyzing...")
        threading.Thread(target=self.analyze_audio).start()
        self.animate_status()

    def animate_status(self):
        def animate():
            while self.animation_running:
                for i in range(4):
                    if not self.animation_running:
                        break
                    dots = "." * i
                    self.status_label.config(text=f"Analyzing{dots}")
                    time.sleep(0.5)

        threading.Thread(target=animate).start()

    def analyze_audio(self):
        if not self.file_path:
            self.animation_running = False
            self.status_label.config(text="No file selected.")
            return

        selected_devices = [device["ip"] for device in self.get_selected_devices()]
        if not selected_devices:
            self.animation_running = False
            self.status_label.config(text="No devices selected.")
            return

        try:
            api_token = os.getenv("API_TOKEN")
            pipeline = audio_split.Pipeline.from_pretrained("pyannote/speaker-diarization@2.1", use_auth_token=api_token)
            audio_split.separate_speakers(pipeline, self.file_path)
            self.animation_running = False
            self.status_label.config(text="Analysis completed.")
            self.generate_playbook(selected_devices)
        except Exception as e:
            self.animation_running = False
            self.status_label.config(text="Error during analysis.")
            print(f"An error occurred: {e}")

    def generate_playbook(self, selected_devices):
        output_dir = "output"
        if not os.path.exists(output_dir):
            self.status_label.config(text="Output directory not found.")
            return

        audio_files = sorted([f for f in os.listdir(output_dir) if f.startswith("part") and f.endswith(".wav")])
        if len(selected_devices) != len(audio_files):
            self.status_label.config(text="Number of devices does not match number of audio files.")
            return

        try:
            generate_playbook(selected_devices, audio_files)
            self.alert_playbook_generated()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate playbook: {e}")

    def alert_playbook_generated(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Playbook Generated")
        tk.Label(dialog, text="Playbook has been generated.", font=("Helvetica", 12)).pack(pady=10)
        tk.Button(
            dialog, text="Execute",
            command=lambda: self.execute_playbook(dialog)
        ).pack(side=tk.LEFT, padx=20, pady=10)
        tk.Button(
            dialog, text="Cancel",
            command=dialog.destroy
        ).pack(side=tk.RIGHT, padx=20, pady=10)

    def execute_playbook(self, dialog):
        try:
            subprocess.run(["ansible-playbook", "-i", "hosts.ini", "playbook.yml"], check=True)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to execute playbook: {e}")
        finally:
            dialog.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = AudioSplitApp(root)
    root.mainloop()
