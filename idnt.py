#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
import webbrowser


class DeviceNamingTool:
    """IT Device Naming Tool - Generates standardized device names from organizational codes."""

    def __init__(self, root):
        self.root = root
        self.root.appname = "IDNT"
        self.root.appver = "0.001"
        self.root.appdate = "012426"
        self.root.author = "Billy Watts"
        self.root.authoremail = "billy@slack.net"
        self.root.title(self.root.appname + " " + self.root.appver + self.root.appdate)
        self.root.resizable(False, False)

        # Load data from CSV files
        self.entities = self.load_csv("entity.csv")
        self.departments = self.load_csv("department.csv")
        self.divisions = self.load_csv("division.csv")
        self.types = self.load_csv("type.csv")

        self.active_column = 0
        self.create_widgets()

    def load_csv(self, filename):
        """Load dropdown data from CSV file. Expected format: Label,Code"""
        if not os.path.exists(filename):
            # Return sample data if file doesn't exist
            samples = {
                "entity.csv": [("County", "L"), ("City", "C"), ("State", "S")],
                "department.csv": [
                    ("Keebler Cemetery", "KBC"),
                    ("Public Works", "PW"),
                    ("Finance", "FIN"),
                ],
                "division.csv": [
                    ("Administration", "ADM"),
                    ("Operations", "OPS"),
                    ("Support", "SUP"),
                ],
                "type.csv": [
                    ("Workstation", "WK"),
                    ("Laptop", "LT"),
                    ("Server", "SV"),
                    ("Printer", "PR"),
                ],
            }
            return samples.get(filename, [("Unknown", "UNK")])

        try:
            with open(filename, "r") as f:
                reader = csv.reader(f)
                next(reader, None)  # Skip header if present
                return [(row[0], row[1]) for row in reader if len(row) >= 2]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load {filename}: {str(e)}")
            return [("Error", "ERR")]

    def _create_combobox(self, parent, variable, data, column):
        """Helper method to create a combobox with standard bindings"""
        combo = ttk.Combobox(parent, textvariable=variable, width=15, state="readonly")
        combo["values"] = [f"{label} - {code}" for label, code in data]
        combo.current(0)
        combo.grid(row=2, column=column, padx=5)
        combo.bind("<<ComboboxSelected>>", lambda e: self.update_display())
        combo.bind("<FocusIn>", lambda e: self.set_active_column(column))
        return combo

    def _create_entry(self, parent, variable, column, default_value, width=10):
        """Helper method to create an entry with standard bindings"""
        entry = ttk.Entry(parent, textvariable=variable, width=width)
        variable.set(default_value)
        entry.grid(row=2, column=column, padx=5)
        entry.bind("<KeyRelease>", lambda e: self.update_display())
        entry.bind("<FocusIn>", lambda e: self.set_active_column(column))
        return entry

    def create_widgets(self):
        """Create and layout all GUI widgets"""
        # Configure style for button colors
        style = ttk.Style()
        #style.configure("GreenTButton", foreground="green")

        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        # Title
        ttk.Label(main_frame, text="IT Device Naming Tool", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=6, sticky=tk.W, pady=(0, 10))
        # Field labels
        labels = ["Entity", "Department", "Division", "Type", "Deployed", "TechID"]
        for i, label in enumerate(labels):
            ttk.Label(main_frame, text=label).grid(row=1, column=i, padx=5, pady=5)

        # Create dropdowns
        self.entity_var = tk.StringVar()
        self.entity_combo = self._create_combobox(
            main_frame, self.entity_var, self.entities, 0
        )

        self.dept_var = tk.StringVar()
        self.dept_combo = self._create_combobox(
            main_frame, self.dept_var, self.departments, 1
        )

        self.div_var = tk.StringVar()
        self.div_combo = self._create_combobox(
            main_frame, self.div_var, self.divisions, 2
        )

        self.type_var = tk.StringVar()
        self.type_combo = self._create_combobox(
            main_frame, self.type_var, self.types, 3
        )

        # Create entry fields
        self.deployed_var = tk.StringVar()
        self.deployed_entry = self._create_entry(
            main_frame, self.deployed_var, 4, "2026"
        )

        self.techid_var = tk.StringVar()
        self.techid_entry = self._create_entry(main_frame, self.techid_var, 5, "00A7")
        self.techid_entry.bind("<Return>", lambda e: self.on_techid_enter())
        # Code display labels (large text showing extracted codes)
        self.code_labels = []
        self.active_column = 0
        for i in range(6):
            label = ttk.Label(main_frame, text="", font=("Arial", 18, "bold"))
            label.grid(row=3, column=i, padx=5, pady=10)
            self.code_labels.append(label)
        # Device name display
        self.device_name_var = tk.StringVar()
        device_frame = ttk.Frame(main_frame, relief="solid", borderwidth=2)
        device_frame.grid(row=4, column=0, columnspan=6, sticky=(tk.W, tk.E), pady=5)
        device_label = ttk.Label(
            device_frame, textvariable=self.device_name_var, font=("Arial", 24, "bold")
        )
        device_label.pack(side=tk.LEFT, expand=True)
        # Copy button
        
        # unicode string for clipboard icon
        #icon_copy = str("\UF0" + "\U9F" + "\U93" + "\U8B")
        #icon_copy = str("\0001F4CB")
        self.copy_btn = ttk.Button(
            device_frame, text="Copy", command=self.copy_to_clipboard
        )
        self.copy_btn.pack(side=tk.RIGHT, padx=10)
        self.copy_btn.bind("<FocusIn>", lambda e: self.on_copy_button_focus())
        self.copy_btn.bind("<FocusOut>", lambda e: self.on_copy_button_unfocus())
        # Footer
        footer_frame = ttk.Frame(main_frame)
        footer_frame.grid(row=5, column=2, columnspan=6, pady=10, sticky=(tk.W, tk.E))
        ttk.Label(footer_frame, text="©2026 by", foreground="Black").pack(side=tk.LEFT)
        # Clickable email link
        email_label = ttk.Label(
            footer_frame, text=self.root.authoremail, foreground="blue", cursor="hand2"
        )
        email_label.pack(side=tk.LEFT)
        #email_label.bind("<Button-1>", lambda e: self.open_email())
        email_label.bind("<Button-1>", lambda e: self.open_web())
        # Set initial focus to entity combobox
        self.entity_combo.focus_set()
        # Initial display update
        self.update_display()

    def extract_code(self, combo_value):
        """Extract the code from 'Label - CODE' format"""
        if " - " in combo_value:
            return combo_value.split(" - ")[-1].strip()
        return ""

    def set_active_column(self, column):
        """Set the active column and update code label colors"""
        self.active_column = column
        self.update_code_colors()

    def on_copy_button_focus(self):
        """Handle copy button gaining focus"""
        self.set_active_column(None)

    def on_copy_button_unfocus(self):
        """Handle copy button losing focus"""
        self.copy_btn.config(style="")

    def on_techid_enter(self):
        """Handle Enter key press in TechID field"""
        self.copy_to_clipboard()
        self.copy_btn.focus_set()

    def update_code_colors(self):
        """Update the colors of code labels based on active column"""
        for i, label in enumerate(self.code_labels):
            if self.active_column is None:
                label.config(foreground="black")
                #self.copy_btn.config(foreground="green")
            elif i == self.active_column:
                label.config(foreground="red")
            else:
                label.config(foreground="black")

    def update_display(self):
        """Update the code labels and device name"""
        entity_code = self.extract_code(self.entity_var.get())
        dept_code = self.extract_code(self.dept_var.get())
        div_code = self.extract_code(self.div_var.get())
        type_code = self.extract_code(self.type_var.get())
        deployed_year = self.deployed_var.get()
        deployed_digit = deployed_year[-1] if deployed_year else ""
        techid = self.techid_var.get()

        # Update code display labels
        codes = [entity_code, dept_code, div_code, type_code, deployed_digit, techid]
        for i, (label, code) in enumerate(zip(self.code_labels, codes)):
            label.config(text=code)

        self.update_code_colors()

        # Generate and display device name
        device_name = (
            f"{entity_code}{dept_code}{div_code}{type_code}{deployed_digit}{techid}"
        )
        self.device_name_var.set(device_name)
        self.root.title(self.root.appname + " " + self.root.appver + " -> " + device_name)

    def copy_to_clipboard(self):
        """Copy device name to clipboard"""
        device_name = self.device_name_var.get()
        self.root.clipboard_clear()
        self.root.clipboard_append(device_name)
        messagebox.showinfo("Success", f"Copied '{device_name}' to clipboard!")

    def open_email(self):
        """Open default email client with mailto link"""
        webbrowser.open("mailto:billy@slack.net?subject=re%3Aidnt")

    def open_web(self):
        """Open default browser with website link"""
        webbrowser.open("https://github.com/D1A881/idnt")


def main():
    root = tk.Tk()
    app = DeviceNamingTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()
