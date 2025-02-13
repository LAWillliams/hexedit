import tkinter as tk
from tkinter import filedialog, messagebox
import struct
import re

class HexEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Hex Editor")
        
        # Text area to display extracted strings
        self.text_area = tk.Text(root, wrap=tk.NONE, font=("Courier", 10))
        self.text_area.pack(expand=True, fill=tk.BOTH)
        
        # Top frame for controls
        top_frame = tk.Frame(root)
        top_frame.pack(fill=tk.X)
        
        self.load_button = tk.Button(top_frame, text="Load File", command=self.load_file)
        self.load_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.save_button = tk.Button(top_frame, text="Save File", command=self.save_file)
        self.save_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Entry field that now serves double-duty:
        # 1. For searching text in the extracted printable strings.
        # 2. For entering the numeric value to search for/edit.
        self.search_entry = tk.Entry(top_frame)
        self.search_entry.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.search_button = tk.Button(top_frame, text="Search", command=self.search_text)
        self.search_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.prev_button = tk.Button(top_frame, text="Previous", command=self.prev_match)
        self.prev_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.next_button = tk.Button(top_frame, text="Next", command=self.next_match)
        self.next_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Dropdown menu for selecting the data type to experiment with.
        self.data_type_var = tk.StringVar(root)
        self.data_type_var.set("float")  # default value
        data_types = ["float", "int", "unsigned int", "short", "unsigned short"]
        self.data_type_menu = tk.OptionMenu(top_frame, self.data_type_var, *data_types)
        self.data_type_menu.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Button to trigger the value editing function.
        self.edit_value_button = tk.Button(top_frame, text="Edit Value", command=self.edit_value)
        self.edit_value_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.file_path = None
        self.file_data = None
        self.matches = []
        self.current_match_index = -1
    
    def extract_strings(self, data, min_length=4):
        # Extract sequences of ASCII printable characters for display.
        text_strings = re.findall(b'[ -~]{%d,}' % min_length, data)
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
        self.matches = []
        start_pos = "1.0"
        while True:
            start_pos = self.text_area.search(search_term, start_pos, stopindex=tk.END)
            if not start_pos:
                break
            end_pos = f"{start_pos}+{len(search_term)}c"
            self.text_area.tag_add("highlight", start_pos, end_pos)
            self.matches.append(start_pos)
            start_pos = end_pos
        
        self.text_area.tag_config("highlight", background="yellow")
        self.current_match_index = 0 if self.matches else -1
        self.jump_to_match()
    
    def jump_to_match(self):
        if self.matches and 0 <= self.current_match_index < len(self.matches):
            self.text_area.mark_set("insert", self.matches[self.current_match_index])
            self.text_area.see(self.matches[self.current_match_index])
    
    def prev_match(self):
        if self.matches and self.current_match_index > 0:
            self.current_match_index -= 1
            self.jump_to_match()
    
    def next_match(self):
        if self.matches and self.current_match_index < len(self.matches) - 1:
            self.current_match_index += 1
            self.jump_to_match()
    
    def edit_value(self):
        if not self.file_data:
            messagebox.showerror("Error", "No file loaded")
            return
        
        data_type = self.data_type_var.get()
        input_val = self.search_entry.get()
        
        try:
            # Determine the struct format string and size based on the selected data type.
            if data_type == "float":
                format_str = "<f"
                size = 4
                target_val = float(input_val)
            elif data_type == "int":
                format_str = "<i"
                size = 4
                target_val = int(input_val)
            elif data_type == "unsigned int":
                format_str = "<I"
                size = 4
                target_val = int(input_val)
            elif data_type == "short":
                format_str = "<h"
                size = 2
                target_val = int(input_val)
            elif data_type == "unsigned short":
                format_str = "<H"
                size = 2
                target_val = int(input_val)
            else:
                messagebox.showerror("Error", "Unsupported data type")
                return
            
            # Pack the new value into bytes.
            new_bytes = struct.pack(format_str, target_val)
            found = False
            
            # Loop through the file data searching for the target value.
            for i in range(len(self.file_data) - size + 1):
                chunk = self.file_data[i:i+size]
                if len(chunk) == size:
                    current_val = struct.unpack(format_str, chunk)[0]
                    # Use a tolerance check for floats; exact match for other types.
                    if data_type == "float":
                        if abs(current_val - target_val) < 0.001:
                            self.file_data[i:i+size] = new_bytes
                            messagebox.showinfo("Success", f"Modified float at offset {i}")
                            found = True
                            break
                    else:
                        if current_val == target_val:
                            self.file_data[i:i+size] = new_bytes
                            messagebox.showinfo("Success", f"Modified {data_type} at offset {i}")
                            found = True
                            break
            
            if not found:
                messagebox.showerror("Error", f"{data_type} value not found in file")
        except ValueError:
            messagebox.showerror("Error", "Invalid input for the selected data type")
        except struct.error as se:
            messagebox.showerror("Error", f"Struct error: {se}")

if __name__ == "__main__":
    root = tk.Tk()
    app = HexEditor(root)
    root.mainloop()
