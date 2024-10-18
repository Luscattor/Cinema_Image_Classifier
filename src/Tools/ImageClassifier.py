import os
import shutil
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from PIL import Image, ImageTk

class ImageClassifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Classifier")
        
        # Default root path
        self.root_path = tk.StringVar()
        self.root_path.set(os.getcwd())
        
        # Frame to display image and list
        self.main_frame = tk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Listbox to display all images in the root folder, placed on the left
        self.listbox_frame = tk.Frame(self.main_frame)
        self.image_listbox = tk.Listbox(self.listbox_frame, width=10)
        self.image_listbox.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        
        # Scrollbar for the listbox
        self.scrollbar = tk.Scrollbar(self.listbox_frame, orient=tk.VERTICAL)
        self.scrollbar.config(command=self.image_listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.image_listbox.config(yscrollcommand=self.scrollbar.set)
        
        self.main_frame.add(self.listbox_frame)
        
        # Frame to display image
        self.image_frame = tk.Frame(self.main_frame)
        self.canvas = tk.Label(self.image_frame)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.main_frame.add(self.image_frame)
        
        # Bind resizing event to update image size
        self.root.bind('<Configure>', self.resize_image)
        
        # Bind key events for classification shortcuts
        self.root.bind('<Key>', self.key_classify_image)
        
        # Bind selection event for the listbox
        self.image_listbox.bind('<<ListboxSelect>>', self.on_image_select)
        
        # Frame for buttons
        self.button_frame = tk.Frame(root)
        self.button_frame.pack()
        
        # Creating 10 buttons
        for i in range(1, 11):
            btn_text = str(i) if i < 10 else "0"
            btn = tk.Button(self.button_frame, text=btn_text, command=lambda i=i: self.classify_image(i))
            btn.grid(row=0, column=i-1)
        
        # Entry for the root directory
        self.entry_frame = tk.Frame(root)
        self.entry_frame.pack()
        
        tk.Label(self.entry_frame, text="Root Folder:").pack(side=tk.LEFT)
        self.root_entry = tk.Entry(self.entry_frame, textvariable=self.root_path, width=50)
        self.root_entry.pack(side=tk.LEFT)
        tk.Button(self.entry_frame, text="Browse", command=self.browse_folder).pack(side=tk.LEFT)
        
        # Load the first image
        self.image_list = []
        self.load_images()
        self.current_image_index = 0
        self.current_image = None
        self.display_next_image()
    
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.root_path.set(folder)
            self.load_images()
            self.current_image_index = 0
            self.display_next_image()
    
    def load_images(self):
        root_folder = self.root_path.get()
        self.image_list = [f for f in os.listdir(root_folder) if os.path.isfile(os.path.join(root_folder, f)) and f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        self.image_listbox.delete(0, tk.END)
        for image_name in self.image_list:
            self.image_listbox.insert(tk.END, image_name)
    
    def display_next_image(self):
        if self.current_image_index < len(self.image_list):
            image_path = os.path.join(self.root_path.get(), self.image_list[self.current_image_index])
            self.display_image(image_path)
        else:
            # No more images to classify, close the app
            self.root.quit()
    
    def display_image(self, image_path):
        self.current_image = Image.open(image_path)
        self.update_image_display()
    
    def update_image_display(self):
        if self.current_image:
            # Resize image to fit the current canvas size
            image = self.current_image.copy()
            image.thumbnail((self.image_frame.winfo_width(), self.image_frame.winfo_height()))
            self.photo = ImageTk.PhotoImage(image)
            self.canvas.config(image=self.photo)
    
    def resize_image(self, event):
        self.update_image_display()
    
    def classify_image(self, class_number):
        if self.current_image_index < len(self.image_list):
            image_name = self.image_list[self.current_image_index]
            src_path = os.path.join(self.root_path.get(), image_name)
            dest_folder = os.path.join(self.root_path.get(), f"{class_number:02}")
            dest_path = os.path.join(dest_folder, image_name)
            os.makedirs(dest_folder, exist_ok=True)
            
            existing_rank_path, existing_rank = self.check_existing_rank(image_name)
            if existing_rank_path:
                self.resolve_rank_conflict(src_path, existing_rank_path, dest_path, existing_rank, class_number)
            elif os.path.exists(dest_path):
                self.resolve_conflict(src_path, dest_path)
            else:
                shutil.move(src_path, dest_folder)  # Move instead of copy to remove from root folder

        # Remove the image from listbox and list
        self.image_listbox.delete(self.current_image_index)
        self.image_list.pop(self.current_image_index)
                
        # Move to the next image
        if self.current_image_index < len(self.image_list):
            self.display_next_image()
        else:
            self.root.quit()
    
    def key_classify_image(self, event):
        if event.char.isdigit():
            key_number = int(event.char)
            if key_number == 0:
                key_number = 10
            if 1 <= key_number <= 10:
                self.classify_image(key_number)
    
    def check_existing_rank(self, image_name):
        root_folder = self.root_path.get()
        for i in range(1, 11):
            rank_folder = os.path.join(root_folder, f"{i:02}")
            image_path = os.path.join(rank_folder, image_name)
            if os.path.exists(image_path):
                return image_path, i
        return None, None
    
    def resolve_rank_conflict(self, src_path, existing_path, dest_path, existing_rank, new_rank):
        conflict_window = tk.Toplevel(self.root)
        conflict_window.title("Rank Conflict Resolution")
        
        # Load both images
        src_image = Image.open(src_path)
        existing_image = Image.open(existing_path)
        
        src_image.thumbnail((200, 200))
        existing_image.thumbnail((200, 200))
        
        src_photo = ImageTk.PhotoImage(src_image)
        existing_photo = ImageTk.PhotoImage(existing_image)
        
        # Create frames for side-by-side layout
        image_frame = tk.Frame(conflict_window)
        image_frame.pack()
        
        # Display source image on the left
        src_image_frame = tk.Frame(image_frame)
        src_image_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(src_image_frame, text=f"Image from Root Folder (Trying to move to Rank {new_rank:02}):").pack()
        src_label = tk.Label(src_image_frame, image=src_photo)
        src_label.image = src_photo
        src_label.pack()
        
        # Display existing ranked image on the right
        existing_image_frame = tk.Frame(image_frame)
        existing_image_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(existing_image_frame, text=f"Existing Image in Rank {existing_rank:02}:").pack()
        existing_label = tk.Label(existing_image_frame, image=existing_photo)
        existing_label.image = existing_photo
        existing_label.pack()
        
        # Buttons to decide which rank to keep
        button_frame = tk.Frame(conflict_window)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Keep Existing Rank", command=lambda: self.keep_rank(existing_path, src_path, conflict_window)).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Move to New Rank", command=lambda: self.keep_new_rank(existing_path, src_path, dest_path, conflict_window)).pack(side=tk.LEFT, padx=5)
        
        # Prevent moving to the next image until conflict is resolved
        self.conflict_window_open = True
        conflict_window.protocol("WM_DELETE_WINDOW", lambda: self.on_conflict_window_close(conflict_window))
    
    def on_conflict_window_close(self, conflict_window):
        conflict_window.destroy()
        self.conflict_window_open = False
        self.move_to_next_image()
    
    def keep_rank(self, existing_path, src_path, conflict_window):
        os.remove(src_path)  # Remove the source image
        conflict_window.destroy()
        self.conflict_window_open = False
        self.move_to_next_image()
    
    def keep_new_rank(self, existing_path, src_path, dest_path, conflict_window):
        os.remove(existing_path)  # Remove the existing image from its current rank
        shutil.move(src_path, dest_path)  # Move the source image to the new rank
        conflict_window.destroy()
        self.conflict_window_open = False
        self.move_to_next_image()
    
    def resolve_conflict(self, src_path, dest_path):
        conflict_window = tk.Toplevel(self.root)
        conflict_window.title("Conflict Resolution")
        
        # Load both images
        src_image = Image.open(src_path)
        dest_image = Image.open(dest_path)
        
        src_image.thumbnail((200, 200))
        dest_image.thumbnail((200, 200))
        
        src_photo = ImageTk.PhotoImage(src_image)
        dest_photo = ImageTk.PhotoImage(dest_image)
        
        # Create frames for side-by-side layout
        image_frame = tk.Frame(conflict_window)
        image_frame.pack()
        
        # Display source image on the left
        src_image_frame = tk.Frame(image_frame)
        src_image_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(src_image_frame, text="Image from Root Folder:").pack()
        src_label = tk.Label(src_image_frame, image=src_photo)
        src_label.image = src_photo
        src_label.pack()
        
        # Display destination image on the right
        dest_image_frame = tk.Frame(image_frame)
        dest_image_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(dest_image_frame, text="Image from Destination Folder:").pack()
        dest_label = tk.Label(dest_image_frame, image=dest_photo)
        dest_label.image = dest_photo
        dest_label.pack()
        
        # Buttons to decide which image to keep
        button_frame = tk.Frame(conflict_window)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Keep Image from Root Folder", command=lambda: self.keep_image(src_path, dest_path, conflict_window, keep_src=True)).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Keep Image from Destination Folder", command=lambda: self.keep_image(src_path, dest_path, conflict_window, keep_src=False)).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Keep Both Images", command=lambda: self.keep_both_images(src_path, os.path.dirname(dest_path), conflict_window)).pack(side=tk.LEFT, padx=5)
        
        # Prevent moving to the next image until conflict is resolved
        self.conflict_window_open = True
        conflict_window.protocol("WM_DELETE_WINDOW", lambda: self.on_conflict_window_close(conflict_window))
    
    def keep_image(self, src_path, dest_path, conflict_window, keep_src):
        if keep_src:
            shutil.move(src_path, dest_path)  # Overwrite the destination image with the source image
        else:
            os.remove(src_path)  # Remove the source image if keeping the destination
        conflict_window.destroy()
        self.conflict_window_open = False
        self.move_to_next_image()
    
    def keep_both_images(self, src_path, dest_folder, conflict_window):
        base, ext = os.path.splitext(os.path.basename(src_path))
        new_name = f"{base}_copy{ext}"
        new_dest_path = os.path.join(dest_folder, new_name)
        shutil.move(src_path, new_dest_path)
        conflict_window.destroy()
        self.conflict_window_open = False
        self.move_to_next_image()
    
    def move_to_next_image(self):
        if not hasattr(self, 'conflict_window_open') or not self.conflict_window_open:
            if self.current_image_index < len(self.image_list):
                self.display_next_image()
            else:
                self.root.quit()
    
    def on_image_select(self, event):
        try:
            selection = event.widget.curselection()
            if selection:
                self.current_image_index = selection[0]
                image_name = self.image_list[self.current_image_index]
                image_path = os.path.join(self.root_path.get(), image_name)
                self.display_image(image_path)
        except IndexError:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageClassifierApp(root)
    root.mainloop()
