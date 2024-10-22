import sys
import os
import json
import tkinter as tk
from tkinter import messagebox, filedialog, Scrollbar, Canvas, Frame
from PIL import Image, ImageTk

# Generate conflict data

class ImageConflictUI(tk.Tk):
    def __init__(self, path):
        super().__init__()
        self.title("Image Conflict Resolver")
        self.geometry("800x300")  # Set the size of the window here
        self.resizable(True, False)  # Allow resizing width but not height
        self.selected_label = None
        self.conflict_data = self.conflict_Name_Checker(self.parsed_Image_in_Dictionary(path))
        self.initUI()

        if self.conflict_data:
            self.conflictList.selection_set(0)  # Select the first item in the list
            self.loadImages(None)  # Load images for the first conflict

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

    def parsed_Image_in_Dictionary(self, path):
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

        files = os.listdir(path)

        for file in files:
            # Vérifie les fichiers à la racine du dossier
            if file.endswith(extensions_tuple):
                mon_dict['root'].append(file)

            # Vérifie si le fichier est un des dossiers de classement
            elif file in rankFolder_tuple:
                folder_path = os.path.join(path, file)
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
            imagePath = os.path.join(path, imageName)
            if os.path.exists(imagePath):
                return imagePath
            else:
                print('File does not exist')
                return None
        else:
            # Si c'est dans un sous-dossier spécifique
            filepath = os.path.join(path, rank, imageName)
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
                newName = filedialog.asksaveasfilename(initialdir=path, initialfile=imageName, title="Rename Image")
                if newName:
                    newPath = os.path.join(path, rank, os.path.basename(newName))
                    os.rename(imagePath, newPath)
                    messagebox.showinfo("Rename", f"Renamed {imageName} to {os.path.basename(newName)}")
                    locations[locations.index(rank)] = os.path.basename(newName)
                    self.loadImages(None)

    def refreshData(self):
        # Refresh the data by parsing the folder again
        self.conflict_data = self.conflict_Name_Checker(self.parsed_Image_in_Dictionary(path))
        self.conflictList.delete(0, tk.END)
        for item in self.conflict_data.keys():
            self.conflictList.insert(tk.END, item)
        messagebox.showinfo("Refresh", "Data refreshed!")

if __name__ == '__main__':
    path = '/Users/alexandrelaroumet/Dropbox/PERSO/ALEXANDRE/Script/Ai_Image_Classifier/data/TrainingFolder'
    app = ImageConflictUI(path)
    app.mainloop()
