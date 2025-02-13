import tkinter as tk
from tkinter import filedialog, messagebox
import binascii
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
        
        self.prev_button = tk.Button(root, text="Previous", command=self.prev_match)
        self.prev_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.next_button = tk.Button(root, text="Next", command=self.next_match)
        self.next_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.file_path = None
        self.matches = []
        self.current_match_index = -1
    
    def extract_strings(self, data, min_length=4):
        """
        Extract readable strings from binary data.
        :param data: Binary data from the file.
        :param min_length: Minimum length of readable strings.
        :return: Extracted strings joined into a readable format.
        """
        text_strings = re.findall(b'[ -~]{%d,}' % min_length, data)  # ASCII printable characters
        return '\n'.join([s.decode('utf-8', errors='ignore') for s in text_strings])
    
    def load_file(self):
        self.file_path = filedialog.askopenfilename()
        if not self.file_path:
            return
        
        try:
            with open(self.file_path, "rb") as file:
                data = file.read()
                extracted_text = self.extract_strings(data)
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, extracted_text)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")
    
    def save_file(self):
        if not self.file_path:
            messagebox.showerror("Error", "No file loaded")
            return
        
        try:
            extracted_text = self.text_area.get(1.0, tk.END).strip()
            binary_data = binascii.unhexlify(extracted_text.replace("\n", ""))
            
            with open(self.file_path, "wb") as file:
                file.write(binary_data)
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

if __name__ == "__main__":
    root = tk.Tk()
    app = HexEditor(root)
    root.mainloop()
