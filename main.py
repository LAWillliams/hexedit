import tkinter as tk
from tkinter import filedialog, messagebox
import binascii
import struct
import re

class HexEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Hex Editor")
        
        self.text_area = tk.Text(root, wrap=tk.NONE, font=("Courier", 10))
        self.text_area.pack(expand=True, fill=tk.BOTH)
        
        self.load_button = tk.Button(root, text="Load File", command=self.load_file)
        self.load_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.save_button = tk.Button(root, text="Save File", command=self.save_file)
        self.save_button.pack(side=tk.RIGHT, padx=5, pady=5)
        
        self.search_entry = tk.Entry(root)
        self.search_entry.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.search_button = tk.Button(root, text="Search", command=self.search_text)
        self.search_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.edit_float_button = tk.Button(root, text="Edit Float", command=self.edit_float)
        self.edit_float_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.file_path = None
        self.file_data = None
    
    def extract_strings(self, data, min_length=4):
        text_strings = re.findall(b'[ -~]{%d,}' % min_length, data)  # ASCII printable characters
        return '\n'.join([s.decode('utf-8', errors='ignore') for s in text_strings])
    
    def load_file(self):
        self.file_path = filedialog.askopenfilename()
        if not self.file_path:
            return
        
        try:
            with open(self.file_path, "rb") as file:
                self.file_data = bytearray(file.read())
                extracted_text = self.extract_strings(self.file_data)
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, extracted_text)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")
    
    def save_file(self):
        if not self.file_path:
            messagebox.showerror("Error", "No file loaded")
            return
        
        try:
            with open(self.file_path, "wb") as file:
                file.write(self.file_data)
            messagebox.showinfo("Success", "File saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")
    
    def search_text(self):
        search_term = self.search_entry.get()
        if not search_term:
            messagebox.showerror("Error", "Please enter text to search")
            return
        
        self.text_area.tag_remove("highlight", "1.0", tk.END)
        start_pos = "1.0"
        while True:
            start_pos = self.text_area.search(search_term, start_pos, stopindex=tk.END)
            if not start_pos:
                break
            end_pos = f"{start_pos}+{len(search_term)}c"
            self.text_area.tag_add("highlight", start_pos, end_pos)
            start_pos = end_pos
        
        self.text_area.tag_config("highlight", background="yellow")
    
    def edit_float(self):
        if not self.file_data:
            messagebox.showerror("Error", "No file loaded")
            return
        
        try:
            float_value = float(self.search_entry.get())
            float_bytes = struct.pack('<f', float_value)  # Convert float to IEEE-754 format
            
            for i in range(len(self.file_data) - 4):
                chunk = self.file_data[i:i+4]
                if len(chunk) == 4:
                    try:
                        extracted_float = struct.unpack('<f', chunk)[0]
                        if abs(extracted_float - float_value) < 0.001:  # Tolerance check
                            self.file_data[i:i+4] = float_bytes
                            messagebox.showinfo("Success", f"Modified float at offset {i}")
                            return
                    except struct.error:
                        continue
            
            messagebox.showerror("Error", "Float value not found in file")
        except ValueError:
            messagebox.showerror("Error", "Invalid float input")

if __name__ == "__main__":
    root = tk.Tk()
    app = HexEditor(root)
    root.mainloop()
