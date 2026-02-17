#!/usr/bin/env python3
"""
Settings Window for Object Browser
Tree-based configuration interface
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import csv
import json
import os


class SettingsWindow:
    """Settings manager for Object Browser"""

    def __init__(self, parent=None, app_instance=None):
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("Object Browser Settings")
        self.window.geometry("900x600")
        self.app_instance = app_instance

        # Settings data structure
        self.settings = self.load_settings()
        
        # Track if settings have changed
        self.settings_modified = False

        self.create_ui()
        self.populate_tree()

    def load_settings(self):
        """Load settings from JSON file"""
        default_settings = {
            "browser": {
                "max_depth": 6,
                "show_private": False,
                "show_magic": True,
                "expand_on_select": True,
                "auto_refresh": False,
                "search_case_sensitive": False
            },
            "display": {
                "theme": "default",
                "font_family": "Courier",
                "font_size": 10,
                "tree_font_size": 9,
                "window_width": 1400,
                "window_height": 900,
                "status_bar_visible": True,
                "line_numbers": False
            },
            "editor": {
                "editor_command": "notepad {filename}",
                "syntax_highlighting": True,
                "word_wrap": False,
                "tab_size": 4,
                "auto_indent": True
            },
            "persistence": {
                "auto_save_loaded_objects": False,
                "loaded_objects_file": "loaded_objects.pkl",
                "remember_window_position": True,
                "max_recent_files": 10,
                "pickle_protocol": 4
            },
            "advanced": {
                "debug_mode": False,
                "log_file": "object_browser.log",
                "enable_logging": False,
                "performance_mode": False,
                "large_file_warning_mb": 100,
                "memory_limit_mb": 500
            },
            "colors": {
                "background": "white",
                "foreground": "black",
                "keyword_color": "blue",
                "string_color": "green",
                "comment_color": "gray",
                "function_color": "purple",
                "selection_bg": "lightblue",
                "error_color": "red"
            }
        }

        settings_file = "settings.json"
        if os.path.exists(settings_file):
            try:
                with open(settings_file, "r") as f:
                    loaded = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    for category, values in default_settings.items():
                        if category not in loaded:
                            loaded[category] = values
                        else:
                            for key, default_val in values.items():
                                if key not in loaded[category]:
                                    loaded[category][key] = default_val
                    return loaded
            except Exception as e:
                messagebox.showerror("Settings Error", f"Failed to load settings: {str(e)}")

        return default_settings

    def save_settings(self):
        """Save settings to JSON file"""
        settings_file = "settings.json"
        try:
            with open(settings_file, "w") as f:
                json.dump(self.settings, f, indent=4)
            messagebox.showinfo("✓ Settings Saved", 
                f"Settings saved successfully!\n\n"
                f"File: {settings_file}\n\n"
                f"Changes will take effect:\n"
                f"• Immediately for some settings\n"
                f"• After restart for others")
            self.settings_modified = False
            return True
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save settings:\n\n{str(e)}")
            return False

    def create_ui(self):
        """Create the settings window UI"""
        # Main container
        main_paned = ttk.PanedWindow(self.window, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)

        # Left panel - Tree navigation
        left_frame = ttk.Frame(main_paned, width=250)
        main_paned.add(left_frame, weight=1)

        # Right panel - Settings detail
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=3)

        self.create_tree_panel(left_frame)
        self.create_detail_panel(right_frame)
        self.create_button_panel()

    def create_tree_panel(self, parent):
        """Create the tree navigation panel"""
        # Title
        title = ttk.Label(parent, text="Settings Categories", font=("Arial", 12, "bold"))
        title.pack(pady=10, padx=10, anchor=tk.W)

        # Search box
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(search_frame, text="🔍").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        search_entry.bind("<KeyRelease>", self.filter_tree)

        # Tree widget
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(tree_frame, yscrollcommand=scrollbar.set, show="tree")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)

        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def populate_tree(self):
        """Populate the tree with settings categories"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add categories with icons
        categories = {
            "browser": "🧠 Browser Settings",
            "display": "🎨 Display & Appearance",
            "editor": "📝 Code Editor",
            "persistence": "💾 Persistence & Files",
            "advanced": "🔧 Advanced Options",
            "colors": "🎨 Color Scheme"
        }

        for category, display_name in categories.items():
            parent_id = self.tree.insert("", "end", text=display_name, values=(category,))
            
            # Add child items for each setting in the category
            if category in self.settings:
                for key in self.settings[category].keys():
                    display_key = key.replace("_", " ").title()
                    self.tree.insert(parent_id, "end", text=f"  {display_key}", values=(category, key))

    def filter_tree(self, event=None):
        """Filter tree items based on search query"""
        query = self.search_var.get().lower()
        
        if not query:
            self.populate_tree()
            return

        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        categories = {
            "browser": "🧠 Browser Settings",
            "display": "🎨 Display & Appearance",
            "editor": "📝 Code Editor",
            "persistence": "💾 Persistence & Files",
            "advanced": "🔧 Advanced Options",
            "colors": "🎨 Color Scheme"
        }

        for category, display_name in categories.items():
            matching_items = []
            
            if category in self.settings:
                for key in self.settings[category].keys():
                    if query in key.lower() or query in str(self.settings[category][key]).lower():
                        matching_items.append(key)
            
            if matching_items or query in display_name.lower():
                parent_id = self.tree.insert("", "end", text=display_name, values=(category,))
                
                for key in matching_items:
                    display_key = key.replace("_", " ").title()
                    self.tree.insert(parent_id, "end", text=f"  {display_key}", values=(category, key))
                
                self.tree.item(parent_id, open=True)

    def create_detail_panel(self, parent):
        """Create the detail panel for editing settings"""
        # Title
        self.detail_title = ttk.Label(parent, text="Select a setting", font=("Arial", 14, "bold"))
        self.detail_title.pack(pady=10, padx=20, anchor=tk.W)

        # Scrollable frame for settings
        canvas = tk.Canvas(parent, bg="white")
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        
        self.detail_frame = ttk.Frame(canvas)
        self.detail_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=self.detail_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)

    def on_tree_select(self, event=None):
        """Handle tree item selection"""
        selection = self.tree.selection()
        if not selection:
            return

        values = self.tree.item(selection[0], "values")
        
        if not values:
            return

        # Clear detail panel
        for widget in self.detail_frame.winfo_children():
            widget.destroy()

        if len(values) == 1:
            # Category selected
            category = values[0]
            self.show_category_settings(category)
        elif len(values) == 2:
            # Individual setting selected
            category, key = values
            self.show_setting_detail(category, key)

    def show_category_settings(self, category):
        """Show all settings in a category"""
        display_names = {
            "browser": "🧠 Browser Settings",
            "display": "🎨 Display & Appearance",
            "editor": "📝 Code Editor",
            "persistence": "💾 Persistence & Files",
            "advanced": "🔧 Advanced Options",
            "colors": "🎨 Color Scheme"
        }

        self.detail_title.config(text=display_names.get(category, category))

        if category not in self.settings:
            return

        row = 0
        for key, value in self.settings[category].items():
            self.create_setting_widget(category, key, value, row)
            row += 1

    def show_setting_detail(self, category, key):
        """Show detail for a single setting"""
        display_key = key.replace("_", " ").title()
        self.detail_title.config(text=display_key)

        if category not in self.settings or key not in self.settings[category]:
            return

        value = self.settings[category][key]
        self.create_setting_widget(category, key, value, 0, detailed=True)

    def create_setting_widget(self, category, key, value, row, detailed=False):
        """Create appropriate widget for a setting based on its type"""
        display_key = key.replace("_", " ").title()
        
        # Label
        label_text = display_key if not detailed else f"{display_key}:"
        label = ttk.Label(self.detail_frame, text=label_text, font=("Arial", 10, "bold" if detailed else "normal"))
        label.grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)

        # Value widget based on type
        if isinstance(value, bool):
            var = tk.BooleanVar(value=value)
            widget = ttk.Checkbutton(self.detail_frame, variable=var, 
                                    command=lambda: self.update_setting(category, key, var.get()))
            widget.grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)

        elif isinstance(value, int):
            var = tk.StringVar(value=str(value))
            widget = ttk.Spinbox(self.detail_frame, from_=0, to=10000, textvariable=var, width=20)
            widget.bind("<KeyRelease>", lambda e: self.update_setting(category, key, int(var.get()) if var.get().isdigit() else 0))
            widget.grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)

        elif isinstance(value, list):
            var = tk.StringVar(value=", ".join(map(str, value)))
            widget = ttk.Entry(self.detail_frame, textvariable=var, width=40)
            widget.bind("<KeyRelease>", lambda e: self.update_setting(category, key, [item.strip() for item in var.get().split(",")]))
            widget.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
            
            hint = ttk.Label(self.detail_frame, text="(comma-separated)", font=("Arial", 8), foreground="gray")
            hint.grid(row=row, column=2, sticky=tk.W, padx=5)

        elif key.endswith("_color") or "color" in key.lower():
            var = tk.StringVar(value=value)
            frame = ttk.Frame(self.detail_frame)
            frame.grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)
            
            entry = ttk.Entry(frame, textvariable=var, width=15)
            entry.pack(side=tk.LEFT, padx=(0, 5))
            entry.bind("<KeyRelease>", lambda e: self.update_setting(category, key, var.get()))
            
            color_btn = ttk.Button(frame, text="Choose", 
                                  command=lambda: self.choose_color(category, key, var))
            color_btn.pack(side=tk.LEFT)

        elif key.endswith("_file") or "filename" in key.lower():
            var = tk.StringVar(value=value)
            frame = ttk.Frame(self.detail_frame)
            frame.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
            
            entry = ttk.Entry(frame, textvariable=var, width=30)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
            entry.bind("<KeyRelease>", lambda e: self.update_setting(category, key, var.get()))
            
            browse_btn = ttk.Button(frame, text="Browse", 
                                   command=lambda: self.browse_file(category, key, var))
            browse_btn.pack(side=tk.LEFT)

        elif key == "editor_command":
            var = tk.StringVar(value=value)
            frame = ttk.Frame(self.detail_frame)
            frame.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
            
            entry = ttk.Entry(frame, textvariable=var, width=40)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            entry.bind("<KeyRelease>", lambda e: self.update_setting(category, key, var.get()))
            
            hint = ttk.Label(self.detail_frame, text="Use {filename} as placeholder", 
                           font=("Arial", 8), foreground="gray")
            hint.grid(row=row+1, column=1, sticky=tk.W, padx=10)

        else:
            var = tk.StringVar(value=str(value))
            widget = ttk.Entry(self.detail_frame, textvariable=var, width=40)
            widget.bind("<KeyRelease>", lambda e: self.update_setting(category, key, var.get()))
            widget.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)

        # Configure column weights
        self.detail_frame.columnconfigure(1, weight=1)

    def update_setting(self, category, key, value):
        """Update a setting value"""
        if category in self.settings and key in self.settings[category]:
            self.settings[category][key] = value
            self.settings_modified = True

    def choose_color(self, category, key, var):
        """Choose a color using color picker"""
        color = colorchooser.askcolor(title=f"Choose {key.replace('_', ' ').title()}")
        if color[1]:
            var.set(color[1])
            self.update_setting(category, key, color[1])

    def browse_file(self, category, key, var):
        """Browse for a file"""
        filename = filedialog.askopenfilename(
            title=f"Select {key.replace('_', ' ').title()}",
            filetypes=[("All files", "*.*")]
        )
        if filename:
            var.set(filename)
            self.update_setting(category, key, filename)

    def create_button_panel(self):
        """Create bottom button panel"""
        button_frame = ttk.Frame(self.window)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=10)

        ttk.Button(button_frame, text="✓ Save", command=self.save_settings, width=15).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="🔄 Reset to Defaults", command=self.reset_defaults, width=20).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="📤 Export", command=self.export_settings, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📥 Import", command=self.import_settings, width=15).pack(side=tk.LEFT, padx=5)
        
        # Modified indicator
        self.modified_label = ttk.Label(button_frame, text="", foreground="orange")
        self.modified_label.pack(side=tk.LEFT, padx=20)

    def reset_defaults(self):
        """Reset all settings to defaults"""
        result = messagebox.askyesno("⚠️ Confirm Reset", 
            "Reset all settings to defaults?\n\n"
            "This cannot be undone!\n\n"
            "Your current settings will be lost.")
        if result:
            # Reload defaults
            self.settings = self.load_settings()
            # Clear the settings file to force defaults
            if os.path.exists("settings.json"):
                os.remove("settings.json")
            self.settings = self.load_settings()
            self.populate_tree()
            self.on_tree_select()
            messagebox.showinfo("✓ Reset Complete", "All settings have been reset to defaults.")

    def export_settings(self):
        """Export settings to a file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Settings",
            initialfile="object_browser_settings.json"
        )
        if filename:
            try:
                with open(filename, "w") as f:
                    json.dump(self.settings, f, indent=4)
                messagebox.showinfo("✓ Export Successful", 
                    f"Settings exported!\n\n{filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export:\n\n{str(e)}")

    def import_settings(self):
        """Import settings from a file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Import Settings"
        )
        if filename:
            try:
                with open(filename, "r") as f:
                    imported = json.load(f)
                
                # Validate structure
                if not isinstance(imported, dict):
                    messagebox.showerror("Invalid Format", 
                        "Settings file must contain a JSON object (dictionary).")
                    return
                
                result = messagebox.askyesno("⚠️ Confirm Import",
                    f"Import settings from:\n{filename}\n\n"
                    "This will overwrite your current settings!\n\n"
                    "Continue?")
                
                if result:
                    self.settings = imported
                    self.populate_tree()
                    messagebox.showinfo("✓ Import Successful", 
                        "Settings imported!\n\n"
                        "Click 'Save' to make them permanent.")
            except json.JSONDecodeError as e:
                messagebox.showerror("Parse Error", 
                    f"Invalid JSON file!\n\n{str(e)}")
            except Exception as e:
                messagebox.showerror("Import Error", 
                    f"Failed to import:\n\n{str(e)}")


def main():
    """Run settings window standalone"""
    app = SettingsWindow()
    app.window.mainloop()


if __name__ == "__main__":
    main()
