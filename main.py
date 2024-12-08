import tkinter
import zipfile
import json
import requests
from tkinter import filedialog
from tkinter import ttk
import os
from tkinter import messagebox

selectedMods = []

messagebox.showerror("WARNING: THIS SOFTWARE IS ONLY FOR FABRIC MODS. OTHER LOADERS WONT BE RECOGNIZED!")

def CheckForUpdates():
    for mod_info in selectedMods:
        try:
            mod_path = mod_info["path"]
            row_id = mod_info["row_id"]

            with zipfile.ZipFile(mod_path, 'r') as jar:
                if "fabric.mod.json" in jar.namelist():
                    with jar.open("fabric.mod.json") as f:
                        data = json.load(f)
                        current_version = data.get("version")
                        mod_id = data.get("id")
                        print(f"Processing {mod_id} with version {current_version}")
                        print("")

                        url = f"https://api.modrinth.com/v2/project/{mod_id}/version"
                        response = requests.get(url)
                        
                        if response.status_code == 200:
                            versions_data = response.json()
                            fabric_versions = [
                                v for v in versions_data if "fabric" in v["loaders"]
                            ]
                            if fabric_versions:
                                fabric_versions.sort(
                                    key=lambda x: x["date_published"], reverse=True
                                )
                                latest_version = fabric_versions[0]["version_number"]
                                status = "Available" if latest_version != current_version else "Up-to-date"
                                modTree.item(row_id, values=(os.path.basename(mod_path), current_version, status))
                            else:
                                messagebox.showerror(f"No fabric versions found for {mod_id}")
                        else:
                            modTree.item(row_id, values=(os.path.basename(mod_path), current_version, response.status_code))

        except Exception as e:
            messagebox.showerror(f"Error processing {mod_path}: {e}")
    messagebox.showinfo("Update check finished!")
    

window = tkinter.Tk()
window.title("Modup")
window.geometry("600x300")
window.resizable(False, False)

default_font = ("Consolas", 12)
window.option_add("*Font", default_font)

modTree = ttk.Treeview(window, columns=("Mod Name", "Current Version", "Update"), show='headings')
modTree.place(x=10, y=10, width=580, height=280)

modTree.heading("Mod Name", text="Mod Name")
modTree.heading("Current Version", text="Current Version")
modTree.heading("Update", text="Update")

modTree.column("Mod Name", width=300)
modTree.column("Current Version", width=170)
modTree.column("Update", width=100)

def clearList(tree):
    for item in tree.get_children():
        tree.delete(item)

def SelectIndividualMods():
    userMods = filedialog.askopenfilenames(title="Select mods", filetypes=(("Java Files", "*.jar"),))
    for path in userMods:
        if path not in selectedMods:
            selectedMods.append(path)
            mod_name = os.path.basename(path)
            row_id = modTree.insert("", "end", values=(mod_name, "Unknown", "Pending"))
            selectedMods[-1] = {"path": path, "row_id": row_id}

menuBar = tkinter.Menu(window)

selectMenu = tkinter.Menu(menuBar, tearoff=0)
selectMenu.add_command(label="Select mods from Launcher")
selectMenu.add_command(label="Select individual mods", command=SelectIndividualMods)

listMenu = tkinter.Menu(menuBar, tearoff=0)
listMenu.add_command(label="Clear List", command=clearList(modTree))

menuBar.add_cascade(label="Select", menu=selectMenu)
menuBar.add_cascade(label="List", menu=listMenu)
menuBar.add_command(label="Check for Updates", command=CheckForUpdates)

window.config(menu=menuBar)

window.mainloop()
