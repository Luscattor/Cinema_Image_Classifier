import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, Scrollbar, Canvas, Frame
from tkinter import ttk
from PIL import Image, ImageTk

class ImageConflictUI(tk.Toplevel):
    def __init__(self, parent, path):
        super().__init__(parent)
        self.title("Image Conflict Resolver")
        self.geometry("800x300")  # Set the size of the window here
        self.resizable(True, False)  # Allow resizing width but not height
        self.selected_label = None
        self.path = path
        self.conflict_data = self.conflict_Name_Checker(self.parsed_Image_in_Dictionary())

        self.initUI()
        
        # Additional UI elements can be added here

    def initUI(self):
        # Main Frame
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left Column: List of Conflicts
        self.conflictList = tk.Listbox(main_frame, selectmode=tk.SINGLE)
        self.conflictList.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        if hasattr(self, 'conflict_data') and self.conflict_data:
            for item in self.conflict_data.keys():
                self.conflictList.insert(tk.END, item)
        self.conflictList.bind('<<ListboxSelect>>', self.loadImages)

        # Right Side: Divided in multiple frames
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 1. Top Left: Number of Images in Conflict
        self.conflictCountLabel = tk.Label(right_frame, text="#", font=('Helvetica', 12, 'bold'))
        self.conflictCountLabel.pack(anchor='nw', pady=0)

        # 2. Center: Scroll Area for Images with Conflicts
        self.imageFrame = tk.Frame(right_frame)
        self.imageFrame.pack(fill=tk.BOTH, expand=True, pady=0)

        self.imageCanvas = Canvas(self.imageFrame, height=150)  # Fix the height to 150
        self.imageCanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.scrollbar = Scrollbar(self.imageFrame, orient="horizontal", command=self.imageCanvas.xview)
        self.scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.imageCanvas.config(xscrollcommand=self.scrollbar.set, scrollregion=self.imageCanvas.bbox("all"))
        self.imageHolder = Frame(self.imageCanvas)
        self.imageCanvas.create_window((0, 0), window=self.imageHolder, anchor='nw')

        # 3. Bottom Left: Control Buttons (Delete and Rename)
        buttonFrameBottomLeft = tk.Frame(right_frame)
        buttonFrameBottomLeft.pack(side=tk.TOP, fill=tk.X, padx=0, pady=0)

        self.deleteButton = tk.Button(buttonFrameBottomLeft, text="Delete", command=self.deleteImage)
        self.deleteButton.pack(side=tk.LEFT, padx=0)

        self.renameButton = tk.Button(buttonFrameBottomLeft, text="Rename", command=self.renameImage)
        self.renameButton.pack(side=tk.LEFT, padx=0)

        # 4. Bottom Right: Refresh and Close Buttons
        buttonFrameBottomRight = tk.Frame(right_frame)
        buttonFrameBottomRight.pack(side=tk.BOTTOM, fill=tk.X, anchor='se', padx=0, pady=0)

        self.closeButton = tk.Button(buttonFrameBottomRight, text="Close", command=self.destroy)
        self.closeButton.pack(side=tk.RIGHT, padx=0)

        self.refreshButton = tk.Button(buttonFrameBottomRight, text="Refresh", command=self.refreshData)
        self.refreshButton.pack(side=tk.RIGHT, padx=0)

    def parsed_Image_in_Dictionary(self):
        extensions = ['jpg', 'png', 'gif', 'tiff']
        extensions_tuple = tuple(extensions)

        rankFolder = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
        rankFolder_tuple = tuple(rankFolder)

        mon_dict = {
            'root': [],
            '01': [],
            '02': [],
            '03': [],
            '04': [],
            '05': [],
            '06': [],
            '07': [],
            '08': [],
            '09': [],
            '10': []
        }

        files = os.listdir(self.path)

        for file in files:
            # Vérifie les fichiers à la racine du dossier
            if file.endswith(extensions_tuple):
                mon_dict['root'].append(file)

            # Vérifie si le fichier est un des dossiers de classement
            elif file in rankFolder_tuple:
                folder_path = os.path.join(self.path, file)
                if os.path.isdir(folder_path):
                    filesRank = os.listdir(folder_path)
                    for fileRank in filesRank:
                        if fileRank.endswith(extensions_tuple):
                            mon_dict[file].append(fileRank)
        return mon_dict

    def conflict_Name_Checker(self, mon_dict):
        occurrences = {}

        # Parcourir chaque catégorie du dictionnaire
        for key, files in mon_dict.items():
            for file in files:
                # Enregistrer le nombre de fois que chaque fichier est rencontré
                if file in occurrences:
                    occurrences[file].append(key)
                else:
                    occurrences[file] = [key]

        # Filtrer pour trouver les fichiers qui apparaissent dans plusieurs catégories
        doublons = {file: locations for file, locations in occurrences.items() if len(locations) > 1}

        return doublons

    def get_Image_Path(self, rank, imageName):
        if rank == 'root':
            # Si c'est à la racine
            imagePath = os.path.join(self.path, imageName)
            if os.path.exists(imagePath):
                return imagePath
            else:
                print('File does not exist')
                return None
        else:
            # Si c'est dans un sous-dossier spécifique
            filepath = os.path.join(self.path, rank, imageName)
            if os.path.exists(filepath):
                return filepath
            else:
                print('File does not exist')
                return None

    def loadImages(self, event):
        # Clear previous images
        self.selected_label = None  # Reset the selected label before clearing
        for widget in self.imageHolder.winfo_children():
            widget.destroy()

        # Get selected conflict
        selected_index = self.conflictList.curselection()
        if selected_index:
            imageName = self.conflictList.get(selected_index)
            locations = self.conflict_data[imageName]

            # Update conflict count label
            self.conflictCountLabel.config(text=f"# {len(locations)}")

            total_width = 0  # Variable pour calculer la largeur totale de toutes les images

            # Load images from different locations
            for location in locations:
                imagePath = self.get_Image_Path(location, imageName)
                if imagePath:
                    img = Image.open(imagePath)
                    img.thumbnail((img.width, 150), Image.LANCZOS)  # Fixe la hauteur à 150 pixels

                    imgTk = ImageTk.PhotoImage(img)
                    total_width += imgTk.width() + 10  # Ajouter la largeur de chaque image plus padding entre les images

                    # Crée un frame pour chaque image
                    image_frame = tk.Frame(self.imageHolder, highlightbackground="black", highlightthickness=1)
                    label = tk.Label(image_frame, image=imgTk, text=location, compound='top', fg='yellow', font=('Helvetica', 10, 'bold'))
                    label.image = imgTk  # Keep a reference
                    label.bind('<Button-1>', lambda e, lbl=label, fr=image_frame: self.selectImage(lbl, fr))
                    label.pack()
                    image_frame.pack(side=tk.LEFT, padx=5, pady=5)

            # Mettre à jour la largeur de la zone de défilement
            self.imageCanvas.update_idletasks()  # Mise à jour de la zone de défilement
            self.imageCanvas.config(scrollregion=(0, 0, total_width, 150))  # Hauteur de la région fixe à 150

    def selectImage(self, label, frame):
        # Clear previous selection
        if self.selected_label is not None:
            if self.selected_label[1].winfo_exists():  # Vérifier si le frame existe toujours
                self.selected_label[1].config(highlightbackground="black", highlightthickness=1)
        # Update current selection
        self.selected_label = (label, frame)
        frame.config(highlightbackground="yellow", highlightthickness=2)

    def deleteImage(self):
        if self.selected_label is not None:
            label, frame = self.selected_label
            imageName = self.conflictList.get(self.conflictList.curselection())
            locations = self.conflict_data[imageName]
            rank = label.cget("text")
            imagePath = self.get_Image_Path(rank, imageName)
            if imagePath and os.path.exists(imagePath):
                os.remove(imagePath)
                messagebox.showinfo("Delete", f"Deleted {imageName} from {rank}")
                locations.remove(rank)
                if not locations:
                    del self.conflict_data[imageName]
                    self.conflictList.delete(self.conflictList.curselection())
                self.loadImages(None)

    def renameImage(self):
        if self.selected_label is not None:
            label, frame = self.selected_label
            imageName = self.conflictList.get(self.conflictList.curselection())
            locations = self.conflict_data[imageName]
            rank = label.cget("text")
            imagePath = self.get_Image_Path(rank, imageName)
            if imagePath:
                newName = filedialog.asksaveasfilename(initialdir=self.path, initialfile=imageName, title="Rename Image")
                if newName:
                    newPath = os.path.join(self.path, rank, os.path.basename(newName))
                    os.rename(imagePath, newPath)
                    messagebox.showinfo("Rename", f"Renamed {imageName} to {os.path.basename(newName)}")
                    locations[locations.index(rank)] = os.path.basename(newName)
                    self.loadImages(None)

    def refreshData(self):
        # Refresh the data by parsing the folder again
        self.conflict_data = self.conflict_Name_Checker(self.parsed_Image_in_Dictionary(self.path))
        self.conflictList.delete(0, tk.END)
        for item in self.conflict_data.keys():
            self.conflictList.insert(tk.END, item)
        messagebox.showinfo("Refresh", "Data refreshed!")

class ImageClassifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Classifier")
        
        
        
        # Default root path
        self.root_path = tk.StringVar()
        self.root_path.set(os.getcwd())
        
        # Main Frame to hold all elements
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Main Paned Window to make interface responsive
        self.main_pane = tk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.main_pane.pack(fill=tk.BOTH, expand=True)
        
        # Image List Frame (Left side)
        self.image_list_frame = tk.Frame(self.main_pane)
        self.image_listbox = tk.Listbox(self.image_list_frame, width=30)
        self.image_listbox.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        
        self.scrollbar = tk.Scrollbar(self.image_list_frame, orient=tk.VERTICAL)
        self.scrollbar.config(command=self.image_listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.image_listbox.config(yscrollcommand=self.scrollbar.set)
        
        self.main_pane.add(self.image_list_frame)
        
        # Viewer Frame (Right side)
        self.viewer_frame = tk.Frame(self.main_pane)
        self.rank_number = tk.Label(self.viewer_frame, text="#")
        self.rank_number.pack(anchor="nw", padx=10, pady=5)
        
        self.canvas = tk.Label(self.viewer_frame)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.main_pane.add(self.viewer_frame)
        
        # Rank Buttons Frame (Below Viewer)
        self.button_frame = tk.Frame(self.viewer_frame)
        self.button_frame.pack(fill=tk.X, pady=5)
        
        for i in range(1, 11):
            btn_text = str(i) if i < 10 else "0"
            btn = tk.Button(self.button_frame, text=btn_text, command=lambda i=i: self.classify_image(i))
            btn.pack(side=tk.LEFT, expand=True, padx=2)
        
        # Navigation and Conflict Buttons Frame (Below Rank Buttons)
        self.nav_frame = tk.Frame(self.viewer_frame)
        self.nav_frame.pack(fill=tk.X, pady=5)
        
        self.conflict_button = tk.Button(self.nav_frame, text="Image Rank Conflict", command=self.resolve_conflict_button)
        self.conflict_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.prev_button = tk.Button(self.nav_frame, text="<-", command=self.prev_image)
        self.prev_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.next_button = tk.Button(self.nav_frame, text="->", command=self.next_image)
        self.next_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Bottom Frame for Path Input
        self.lower_frame = tk.Frame(self.main_frame)
        self.lower_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
        
        # Path Entry
        self.browse_path()
        
        self.path_label = tk.Label(self.lower_frame, text="Path image root:")
        self.path_label.pack(side=tk.LEFT, padx=5)
        
        self.root_entry = tk.Entry(self.lower_frame, textvariable=self.root_path, width=70)
        self.root_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.change_dir_button = tk.Button(self.lower_frame, text="Change Dir", command=self.browse_folder)
        self.change_dir_button.pack(side=tk.LEFT, padx=5)
        
        # Load the first image
        self.image_list = []
        self.conflict_list = []
        self.load_images()
        self.current_image_index = 0
        self.current_image = None
        self.display_next_image()
        
        # Bind configure event to update image display on resize
        self.root.bind('<Configure>', lambda event: self.update_image_display())
        
        

    def browse_path(self):
            path = filedialog.askdirectory()
            if path:
                self.root_path.set(path)
                
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
        # Parse for conflicts

    def update_conflict_list(self):
        """
        Update the listbox on the left to show conflicts with appropriate indicators.
        """
        self.image_listbox.delete(0, tk.END)
        for image_name in self.conflict_list:
            conflict_rank = any("/" in path for path in image_name)  # Checking if image is in a rank folder
            conflict_name = len([path for path in image_name if "/" in path]) > 1  # Checking if there are multiple locations
            entry_text = image_name
            if conflict_rank:
                entry_text += " [RANK CONFLICT]"
            if conflict_name:
                entry_text += " [NAME CONFLICT]"
            self.image_listbox.insert(tk.END, entry_text)

    def resolve_conflict_button(self):
        # Open the ImageConflictUI window with the selected path
        conflict_window = ImageConflictUI(self.root, self.root_path.get())
        conflict_window.grab_set()  # Make the conflict window modal

    def display_next_image(self):
        if self.current_image_index < len(self.image_list):
            image_path = os.path.join(self.root_path.get(), self.image_list[self.current_image_index])
            self.display_image(image_path)
            self.update_rank_number()
        else:
            self.rank_number.config(text="#")

    def display_image(self, image_path):
        self.current_image = Image.open(image_path)
        self.update_image_display()

    def update_image_display(self):
        if self.current_image:
            # Obtenir la taille actuelle du viewer
            viewer_width = self.viewer_frame.winfo_width()
            viewer_height = self.viewer_frame.winfo_height()

            # Redimensionner l'image tout en conservant les proportions
            image = self.current_image.copy()
            image.thumbnail((viewer_width, viewer_height))

            # Mettre à jour l'image affichée sur le canvas
            self.photo = ImageTk.PhotoImage(image)
            self.canvas.config(image=self.photo)

    def classify_image(self, class_number):
        if self.current_image_index < len(self.image_list):
            image_name = self.image_list[self.current_image_index]
            src_path = os.path.join(self.root_path.get(), image_name)
            dest_folder = os.path.join(self.root_path.get(), f"{class_number:02}")
            dest_path = os.path.join(dest_folder, image_name)
            os.makedirs(dest_folder, exist_ok=True)
            shutil.move(src_path, dest_path)
            self.image_listbox.delete(self.current_image_index)
            self.image_list.pop(self.current_image_index)
            self.display_next_image()

    def update_rank_number(self):
        # Update the rank number display
        image_name = self.image_list[self.current_image_index]
        rank_found = False
        for i in range(1, 11):
            rank_folder = os.path.join(self.root_path.get(), f"{i:02}")
            if os.path.exists(os.path.join(rank_folder, image_name)):
                self.rank_number.config(text=f"{i:02}")
                rank_found = True
                break
        if not rank_found:
            self.rank_number.config(text="#")

    def prev_image(self):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.display_next_image()

    def next_image(self):
        if self.current_image_index < len(self.image_list) - 1:
            self.current_image_index += 1
            self.display_next_image()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageClassifierApp(root)
    root.geometry("1000x500")
    root.mainloop()