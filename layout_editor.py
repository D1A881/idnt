#!/usr/bin/env python3
"""
Object Browser - Complete IDE-style object inspection tool
Recursive scope enumeration with save/load capabilities
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json
import os
import sys
import inspect
import subprocess
import pickle


class ObjectBrowser:
    """Comprehensive object browser with introspection and persistence"""

    def __init__(self, parent=None, settings=None):
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("Object Browser")
        self.window.geometry("1400x900")

        # Object tracking
        self.current_object = None
        self.current_object_path = ""
        self.loaded_objects = {}  # Store loaded objects by name
        
        # Load settings
        self.settings = settings or self.load_settings()
        self.editor_command = self.settings.get('advanced', {}).get('editor_command', 'notepad {filename}')

        self.create_ui()
        self.populate_full_object_tree()

    def load_settings(self):
        """Load settings from file"""
        if os.path.exists("settings.json"):
            try:
                with open("settings.json", "r") as f:
                    return json.load(f)
            except:
                pass
        return {'advanced': {'editor_command': 'notepad {filename}'}}

    def create_ui(self):
        """Create main UI"""
        # Top toolbar
        self.create_toolbar()
        
        # Main container
        main_paned = ttk.PanedWindow(self.window, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)

        # Left: Object Browser
        left_panel = ttk.Frame(main_paned, width=500)
        main_paned.add(left_panel, weight=2)
        self.create_object_browser(left_panel)
        
        # Right: Details Panel
        right_panel = ttk.Frame(main_paned, width=900)
        main_paned.add(right_panel, weight=3)
        self.create_detail_panel(right_panel)
        
        # Bottom status bar
        self.create_status_bar()

    def create_toolbar(self):
        """Create top toolbar"""
        toolbar = ttk.Frame(self.window)
        toolbar.pack(fill=tk.X, padx=5, pady=2)
        
        # Object operations
        ttk.Button(toolbar, text="🔄 Refresh", command=self.populate_full_object_tree).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="📝 Edit Code", command=self.edit_current_object).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        # Save/Load Python
        ttk.Label(toolbar, text="Python:").pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Save", command=self.save_object_python).pack(side=tk.LEFT, padx=1)
        ttk.Button(toolbar, text="Load", command=self.load_object_python).pack(side=tk.LEFT, padx=1)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        # Save/Load Binary
        ttk.Label(toolbar, text="Binary:").pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Save", command=self.save_object_binary).pack(side=tk.LEFT, padx=1)
        ttk.Button(toolbar, text="Load", command=self.load_object_binary).pack(side=tk.LEFT, padx=1)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        ttk.Button(toolbar, text="⚙️ Settings", command=self.reload_settings).pack(side=tk.LEFT, padx=2)
        
        # Title
        title_label = ttk.Label(toolbar, text="🧠 Object Browser", 
                               font=("Arial", 10, "bold"), foreground="blue")
        title_label.pack(side=tk.RIGHT, padx=10)

    def create_object_browser(self, parent):
        """Create object browser panel"""
        # Title
        ttk.Label(parent, text="Object Hierarchy", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Search bar
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill=tk.X, padx=5, pady=3)
        ttk.Label(search_frame, text="🔍 Search:").pack(side=tk.LEFT)
        self.obj_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.obj_search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=3)
        search_entry.bind("<KeyRelease>", self.filter_object_tree)
        ttk.Button(search_frame, text="Clear", command=lambda: self.obj_search_var.set("")).pack(side=tk.LEFT, padx=2)
        
        # Tree widget
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.object_tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set)
        self.object_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.config(command=self.object_tree.yview)
        self.object_tree.bind("<<TreeviewSelect>>", self.on_object_selected)

    def create_detail_panel(self, parent):
        """Create detail panel with tabs"""
        # Notebook for different views
        self.detail_notebook = ttk.Notebook(parent)
        self.detail_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 1: Members (Properties/Methods)
        members_frame = ttk.Frame(self.detail_notebook)
        self.detail_notebook.add(members_frame, text="📊 Members")
        
        members_scroll = ttk.Scrollbar(members_frame)
        members_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.members_tree = ttk.Treeview(members_frame, yscrollcommand=members_scroll.set,
                                        columns=("type", "value"), show="tree headings")
        self.members_tree.heading("#0", text="Name")
        self.members_tree.heading("type", text="Type")
        self.members_tree.heading("value", text="Value")
        self.members_tree.column("#0", width=250)
        self.members_tree.column("type", width=150)
        self.members_tree.column("value", width=400)
        self.members_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        members_scroll.config(command=self.members_tree.yview)
        
        # Tab 2: Code View
        code_frame = ttk.Frame(self.detail_notebook)
        self.detail_notebook.add(code_frame, text="📝 Code")
        
        self.code_viewer = scrolledtext.ScrolledText(code_frame, font=("Courier", 10), wrap=tk.NONE)
        self.code_viewer.pack(fill=tk.BOTH, expand=True)
        
        # Syntax highlighting tags
        self.code_viewer.tag_config("keyword", foreground="blue", font=("Courier", 10, "bold"))
        self.code_viewer.tag_config("string", foreground="green")
        self.code_viewer.tag_config("comment", foreground="gray", font=("Courier", 10, "italic"))
        self.code_viewer.tag_config("function", foreground="purple", font=("Courier", 10, "bold"))
        
        # Tab 3: Object Info
        info_frame = ttk.Frame(self.detail_notebook)
        self.detail_notebook.add(info_frame, text="ℹ️ Info")
        
        self.info_text = scrolledtext.ScrolledText(info_frame, font=("Courier", 10), wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True)

    def create_status_bar(self):
        """Create bottom status bar"""
        self.status_bar = ttk.Frame(self.window, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_text = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.status_bar, textvariable=self.status_text, 
                                     font=("Courier", 9), anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=2)

    def update_status(self, obj_path="", obj_type="", source_file="", line_num=""):
        """Update status bar with object information"""
        if obj_path:
            status = f"{obj_path} ({obj_type})"
            if source_file:
                status += f" | {source_file}"
                if line_num:
                    status += f":{line_num}"
            self.status_text.set(status)
        else:
            self.status_text.set("Ready")

    def populate_full_object_tree(self):
        """Recursively populate object tree with full program state"""
        # Clear tree
        for item in self.object_tree.get_children():
            self.object_tree.delete(item)
        
        # Root: ObjectBrowser instance
        root_id = self.object_tree.insert("", "end", text="ObjectBrowser (self)", 
                                         values=("ObjectBrowser", "self", __file__, ""))
        
        # Enumerate all attributes recursively
        self._enumerate_object(self, root_id, "self", depth=0, max_depth=6)
        
        # Add loaded objects section
        if self.loaded_objects:
            loaded_id = self.object_tree.insert("", "end", text=f"📦 Loaded Objects ({len(self.loaded_objects)})",
                                                values=("dict", "self.loaded_objects", "", ""))
            for name, obj in self.loaded_objects.items():
                obj_type = type(obj).__name__
                obj_id = self.object_tree.insert(loaded_id, "end", text=f"{name}: {obj_type}",
                                                values=(obj_type, f"self.loaded_objects['{name}']", "", ""))
                self._enumerate_object(obj, obj_id, f"self.loaded_objects['{name}']", depth=0, max_depth=6)
            self.object_tree.item(loaded_id, open=True)
        
        # Expand root
        self.object_tree.item(root_id, open=True)

    def _enumerate_object(self, obj, parent_id, obj_name, depth=0, max_depth=6):
        """Recursively enumerate object attributes"""
        if depth >= max_depth:
            return
        
        try:
            obj_type = type(obj).__name__
            
            # Handle different types
            if isinstance(obj, dict):
                for key, value in obj.items():
                    key_str = str(key)
                    val_type = type(value).__name__
                    node_text = f"🔑 {key_str}: {val_type}"
                    
                    # Value preview
                    try:
                        if isinstance(value, (str, int, float, bool)):
                            preview = repr(value)[:50]
                            node_text += f" = {preview}"
                    except:
                        pass
                    
                    child_id = self.object_tree.insert(parent_id, "end", text=node_text,
                                                      values=(val_type, f"{obj_name}[{repr(key)}]", "", ""))
                    
                    # Recurse into complex values
                    if not isinstance(value, (str, int, float, bool, type(None))):
                        self._enumerate_object(value, child_id, f"{obj_name}[{repr(key)}]", depth + 1, max_depth)
            
            elif isinstance(obj, (list, tuple)):
                for idx, value in enumerate(obj):
                    val_type = type(value).__name__
                    node_text = f"[{idx}]: {val_type}"
                    
                    try:
                        if isinstance(value, (str, int, float, bool)):
                            preview = repr(value)[:50]
                            node_text += f" = {preview}"
                    except:
                        pass
                    
                    child_id = self.object_tree.insert(parent_id, "end", text=node_text,
                                                      values=(val_type, f"{obj_name}[{idx}]", "", ""))
                    
                    if not isinstance(value, (str, int, float, bool, type(None))):
                        self._enumerate_object(value, child_id, f"{obj_name}[{idx}]", depth + 1, max_depth)
            
            else:
                # Enumerate attributes
                for attr_name in dir(obj):
                    # Skip private at deeper levels
                    if depth > 0 and attr_name.startswith('_'):
                        continue
                    
                    try:
                        attr_value = getattr(obj, attr_name)
                        attr_type = type(attr_value).__name__
                        
                        # Icon/prefix
                        if callable(attr_value):
                            prefix = "⚙️"
                        elif isinstance(attr_value, (str, int, float, bool)):
                            prefix = "📊"
                        elif isinstance(attr_value, dict):
                            prefix = "📁"
                        elif isinstance(attr_value, (list, tuple)):
                            prefix = "📋"
                        else:
                            prefix = "●"
                        
                        node_text = f"{prefix} {attr_name}: {attr_type}"
                        
                        # Value preview for simple types
                        if isinstance(attr_value, (str, int, float, bool)):
                            preview = repr(attr_value)[:50]
                            node_text += f" = {preview}"
                        
                        child_id = self.object_tree.insert(parent_id, "end", text=node_text,
                                                          values=(attr_type, f"{obj_name}.{attr_name}", "", ""))
                        
                        # Recurse into complex attributes
                        if not isinstance(attr_value, (str, int, float, bool, type(None))) and not callable(attr_value):
                            if isinstance(attr_value, (dict, list, tuple)) or hasattr(attr_value, '__dict__'):
                                self._enumerate_object(attr_value, child_id, f"{obj_name}.{attr_name}", depth + 1, max_depth)
                    
                    except:
                        pass
        except:
            pass

    def on_object_selected(self, event=None):
        """Handle object tree selection"""
        selection = self.object_tree.selection()
        if not selection:
            return
        
        values = self.object_tree.item(selection[0], "values")
        if not values:
            return
        
        obj_type = values[0]
        obj_path = values[1]
        
        self.current_object_path = obj_path
        
        # Update status bar
        self.update_status(obj_path, obj_type, __file__, "")
        
        # Try to get the actual object
        try:
            obj = eval(obj_path)
            self.current_object = obj
            
            # Update all tabs
            self.populate_members(obj)
            self.show_object_code(obj, obj_type, obj_path)
            self.show_object_info(obj, obj_type, obj_path)
        
        except Exception as e:
            print(f"Error accessing object: {e}")

    def populate_members(self, obj):
        """Populate members tree"""
        for item in self.members_tree.get_children():
            self.members_tree.delete(item)
        
        # Properties section
        props_id = self.members_tree.insert("", "end", text="📊 Properties", values=("", ""))
        
        # Methods section
        methods_id = self.members_tree.insert("", "end", text="⚙️ Methods", values=("", ""))
        
        # Special section
        special_id = self.members_tree.insert("", "end", text="🔮 Special/Magic", values=("", ""))
        
        try:
            for attr_name in dir(obj):
                try:
                    attr_value = getattr(obj, attr_name)
                    attr_type = type(attr_value).__name__
                    
                    if callable(attr_value):
                        # Method
                        sig = ""
                        try:
                            sig = str(inspect.signature(attr_value))
                        except:
                            sig = "()"
                        
                        # Special/magic methods
                        if attr_name.startswith('__') and attr_name.endswith('__'):
                            self.members_tree.insert(special_id, "end", text=f"{attr_name}{sig}",
                                                    values=(attr_type, "magic method"))
                        else:
                            self.members_tree.insert(methods_id, "end", text=f"{attr_name}{sig}",
                                                    values=(attr_type, "method"))
                    else:
                        # Property
                        value_preview = ""
                        try:
                            if isinstance(attr_value, (str, int, float, bool)):
                                value_preview = repr(attr_value)[:100]
                            else:
                                value_preview = f"<{attr_type}>"
                        except:
                            value_preview = "<error>"
                        
                        # Special/magic attributes
                        if attr_name.startswith('__') and attr_name.endswith('__'):
                            self.members_tree.insert(special_id, "end", text=attr_name,
                                                    values=(attr_type, value_preview))
                        else:
                            self.members_tree.insert(props_id, "end", text=attr_name,
                                                    values=(attr_type, value_preview))
                except:
                    pass
        except:
            pass
        
        # Expand sections
        self.members_tree.item(props_id, open=True)
        self.members_tree.item(methods_id, open=True)

    def show_object_code(self, obj, obj_type, obj_path):
        """Show code for object"""
        self.code_viewer.delete("1.0", tk.END)
        
        code = f"# Object: {obj_path}\n"
        code += f"# Type: {obj_type}\n"
        code += f"# ID: {id(obj)}\n\n"
        
        # Try to get source code
        try:
            if inspect.isclass(type(obj)) or inspect.isfunction(obj) or inspect.ismethod(obj):
                source = inspect.getsource(obj if callable(obj) else type(obj))
                code += source
            else:
                # Show repr
                code += f"# Value:\n{repr(obj)}\n"
        except Exception as e:
            code += f"# Could not retrieve source code\n# {str(e)}\n"
        
        self.code_viewer.insert("1.0", code)
        self.apply_syntax_highlighting()

    def show_object_info(self, obj, obj_type, obj_path):
        """Show detailed object information"""
        self.info_text.delete("1.0", tk.END)
        
        info = f"Object Information\n{'='*60}\n\n"
        info += f"Path:     {obj_path}\n"
        info += f"Type:     {obj_type}\n"
        info += f"ID:       {id(obj)}\n"
        info += f"Module:   {type(obj).__module__}\n"
        
        # Size info
        try:
            size = sys.getsizeof(obj)
            info += f"Size:     {size:,} bytes\n"
        except:
            pass
        
        # MRO for classes
        try:
            mro = type(obj).__mro__
            info += f"\nMethod Resolution Order:\n"
            for i, cls in enumerate(mro):
                info += f"  {i}. {cls.__name__}\n"
        except:
            pass
        
        # Doc string
        try:
            doc = inspect.getdoc(obj) or inspect.getdoc(type(obj))
            if doc:
                info += f"\nDocumentation:\n{'-'*60}\n{doc}\n"
        except:
            pass
        
        # Source file
        try:
            source_file = inspect.getsourcefile(type(obj))
            if source_file:
                info += f"\nSource File:\n{source_file}\n"
        except:
            pass
        
        self.info_text.insert("1.0", info)

    def apply_syntax_highlighting(self):
        """Apply basic syntax highlighting"""
        keywords = ['def', 'class', 'import', 'from', 'if', 'else', 'elif', 'for', 'while', 
                   'return', 'try', 'except', 'with', 'as', 'pass', 'break', 'continue', 'lambda']
        
        for keyword in keywords:
            start = "1.0"
            while True:
                pos = self.code_viewer.search(f"\\m{keyword}\\M", start, tk.END, regexp=True)
                if not pos:
                    break
                end = f"{pos}+{len(keyword)}c"
                self.code_viewer.tag_add("keyword", pos, end)
                start = end

    def edit_current_object(self):
        """Open current object's source in external editor"""
        if not self.current_object:
            messagebox.showwarning("No Selection", "Please select an object first")
            return
        
        try:
            source_file = None
            
            try:
                source_file = inspect.getsourcefile(self.current_object)
            except:
                pass
            
            if not source_file:
                try:
                    source_file = inspect.getsourcefile(type(self.current_object))
                except:
                    pass
            
            if not source_file or not os.path.exists(source_file):
                source_file = __file__
            
            if '<' in source_file or '>' in source_file or not os.path.exists(source_file):
                messagebox.showwarning("Cannot Edit", 
                    f"Cannot edit built-in objects.\n\n"
                    f"Selected: {self.current_object_path}\n"
                    f"Type: {type(self.current_object).__name__}")
                return
            
            cmd = self.editor_command.format(filename=source_file)
            subprocess.Popen(cmd, shell=True)
            self.update_status(f"Opened {source_file} in editor", "", "", "")
        
        except Exception as e:
            messagebox.showerror("Error", f"Could not open editor:\n{str(e)}")

    def filter_object_tree(self, event=None):
        """Filter object tree based on search"""
        query = self.obj_search_var.get().lower()
        if not query:
            self.populate_full_object_tree()
            return
        
        def search_tree(item):
            text = self.object_tree.item(item, "text").lower()
            children = self.object_tree.get_children(item)
            
            match = query in text
            child_match = False
            
            for child in children:
                if search_tree(child):
                    child_match = True
            
            if match or child_match:
                self.object_tree.item(item, open=True)
                return True
            return False
        
        for item in self.object_tree.get_children():
            search_tree(item)

    def reload_settings(self):
        """Reload settings from file"""
        self.settings = self.load_settings()
        self.editor_command = self.settings.get('advanced', {}).get('editor_command', 'notepad {filename}')
        messagebox.showinfo("Settings Reloaded", "Settings have been reloaded from file")

    def save_object_python(self):
        """Save current object as Python pickle with comprehensive error checking"""
        if not self.current_object:
            messagebox.showwarning("No Object Selected", 
                "Please select an object from the Object Browser first.\n\n"
                "Click on any item in the tree to select it.")
            return
        
        obj_type = type(self.current_object).__name__
        
        # Check for non-picklable types
        non_picklable_types = (tk.Widget, ttk.Widget, tk.Tk, tk.Toplevel, tk.Canvas, tk.Frame)
        if isinstance(self.current_object, non_picklable_types):
            messagebox.showerror("Cannot Pickle GUI Widget",
                f"Cannot save Tkinter widgets!\n\n"
                f"Selected: {self.current_object_path}\n"
                f"Type: {obj_type}\n\n"
                f"GUI widgets cannot be serialized because they contain:\n"
                f"• Operating system handles\n"
                f"• Event callbacks\n"
                f"• Native window references\n\n"
                f"💡 Try selecting data instead (dicts, lists, strings, etc.)")
            return
        
        # Warn about potentially problematic types
        if hasattr(self.current_object, '__dict__') and any(isinstance(v, (tk.Widget, ttk.Widget)) for v in vars(self.current_object).values()):
            result = messagebox.askyesno("Warning: Contains Widgets",
                f"This object may contain GUI widgets!\n\n"
                f"Type: {obj_type}\n\n"
                f"Pickling may fail. Continue anyway?")
            if not result:
                return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".pkl",
            filetypes=[("Pickle files", "*.pkl"), ("Python objects", "*.pickle"), ("All files", "*.*")],
            title="Save Object as Python Pickle",
            initialfile=f"{obj_type.lower()}.pkl"
        )
        
        if not filename:
            return
        
        try:
            # Test pickle first (don't write file if it fails)
            try:
                test_data = pickle.dumps(self.current_object, protocol=pickle.HIGHEST_PROTOCOL)
            except (pickle.PicklingError, TypeError, AttributeError) as e:
                messagebox.showerror("Object Cannot Be Pickled",
                    f"This object cannot be serialized!\n\n"
                    f"Type: {obj_type}\n"
                    f"Path: {self.current_object_path}\n\n"
                    f"Error: {str(e)}\n\n"
                    f"💡 Common causes:\n"
                    f"• Object contains GUI widgets\n"
                    f"• Object contains file handles or threads\n"
                    f"• Object contains lambda functions\n"
                    f"• Object contains module references")
                return
            
            # Write to file
            with open(filename, 'wb') as f:
                f.write(test_data)
            
            file_size = os.path.getsize(filename)
            
            messagebox.showinfo("✓ Object Saved Successfully", 
                f"Object pickled and saved!\n\n"
                f"Path: {self.current_object_path}\n"
                f"Type: {obj_type}\n"
                f"Size: {file_size:,} bytes\n"
                f"Protocol: {pickle.HIGHEST_PROTOCOL}\n"
                f"File: {os.path.basename(filename)}\n\n"
                f"Full path:\n{filename}")
        
        except IOError as e:
            messagebox.showerror("File Write Error",
                f"Cannot write to file!\n\n"
                f"File: {filename}\n"
                f"Error: {str(e)}\n\n"
                f"💡 Check:\n"
                f"• File is not open in another program\n"
                f"• You have write permissions\n"
                f"• Disk is not full")
        
        except Exception as e:
            messagebox.showerror("Unexpected Error", 
                f"Failed to save object!\n\n"
                f"Type: {obj_type}\n"
                f"Error: {type(e).__name__}\n"
                f"Details: {str(e)}")

    def load_object_python(self):
        """Load object from Python pickle with comprehensive error checking"""
        filename = filedialog.askopenfilename(
            filetypes=[("Pickle files", "*.pkl"), ("Python objects", "*.pickle"), ("All files", "*.*")],
            title="Load Object from Python Pickle"
        )
        
        if not filename:
            return
        
        # Check file exists and is readable
        if not os.path.exists(filename):
            messagebox.showerror("File Not Found",
                f"File does not exist!\n\n{filename}")
            return
        
        if not os.access(filename, os.R_OK):
            messagebox.showerror("Permission Denied",
                f"Cannot read file!\n\n{filename}\n\n"
                f"Check file permissions.")
            return
        
        file_size = os.path.getsize(filename)
        
        # Warn about large files
        if file_size > 100 * 1024 * 1024:  # 100 MB
            result = messagebox.askyesno("Large File Warning",
                f"This is a large file ({file_size:,} bytes).\n\n"
                f"Loading may take time and use significant memory.\n\n"
                f"Continue?")
            if not result:
                return
        
        try:
            with open(filename, 'rb') as f:
                loaded_obj = pickle.load(f)
            
            obj_type = type(loaded_obj).__name__
            
            # Ask for object name
            default_name = os.path.basename(filename).rsplit('.', 1)[0]
            name = self.ask_object_name(default_name)
            
            if not name:
                messagebox.showinfo("Load Cancelled", "Object was not added to browser.")
                return
            
            # Check for duplicate names
            if name in self.loaded_objects:
                result = messagebox.askyesno("Name Already Exists",
                    f"An object named '{name}' already exists.\n\n"
                    f"Overwrite it?")
                if not result:
                    return
            
            # Store loaded object
            self.loaded_objects[name] = loaded_obj
            self.populate_full_object_tree()
            
            # Show success with object info
            obj_info = f"Object loaded successfully!\n\n"
            obj_info += f"Name: {name}\n"
            obj_info += f"Type: {obj_type}\n"
            obj_info += f"File size: {file_size:,} bytes\n"
            
            # Try to get object size in memory
            try:
                mem_size = sys.getsizeof(loaded_obj)
                obj_info += f"Memory size: {mem_size:,} bytes\n"
            except:
                pass
            
            obj_info += f"\n✓ Available as: self.loaded_objects['{name}']"
            
            messagebox.showinfo("✓ Object Loaded", obj_info)
        
        except pickle.UnpicklingError as e:
            messagebox.showerror("Invalid Pickle File",
                f"File is not a valid pickle file!\n\n"
                f"File: {os.path.basename(filename)}\n"
                f"Error: {str(e)}\n\n"
                f"💡 The file may be:\n"
                f"• Corrupted\n"
                f"• Not a pickle file\n"
                f"• Created with incompatible software")
        
        except (EOFError, ValueError) as e:
            messagebox.showerror("Corrupted File",
                f"File appears to be corrupted or incomplete!\n\n"
                f"File: {os.path.basename(filename)}\n"
                f"Error: {str(e)}")
        
        except (ImportError, ModuleNotFoundError) as e:
            messagebox.showerror("Missing Module",
                f"Cannot load object - missing required module!\n\n"
                f"Error: {str(e)}\n\n"
                f"💡 The object was created with a module\n"
                f"that is not installed in your Python environment.")
        
        except AttributeError as e:
            messagebox.showerror("Incompatible Version",
                f"Object structure has changed!\n\n"
                f"Error: {str(e)}\n\n"
                f"💡 The object may have been created with\n"
                f"a different version of the software.")
        
        except MemoryError:
            messagebox.showerror("Out of Memory",
                f"Not enough memory to load this object!\n\n"
                f"File size: {file_size:,} bytes\n\n"
                f"💡 Try closing other applications or\n"
                f"load the object on a system with more RAM.")
        
        except Exception as e:
            messagebox.showerror("Load Failed",
                f"Unexpected error loading object!\n\n"
                f"File: {os.path.basename(filename)}\n"
                f"Error type: {type(e).__name__}\n"
                f"Details: {str(e)}")

    def save_object_binary(self):
        """Save current object as binary with comprehensive error checking"""
        if not self.current_object:
            messagebox.showwarning("No Object Selected", 
                "Please select an object from the Object Browser first.")
            return
        
        obj_type = type(self.current_object).__name__
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".bin",
            filetypes=[("Binary files", "*.bin"), ("Data files", "*.dat"), ("All files", "*.*")],
            title="Save Object as Binary",
            initialfile=f"{obj_type.lower()}.bin"
        )
        
        if not filename:
            return
        
        try:
            # Convert to bytes based on type
            data = None
            conversion_method = ""
            
            if isinstance(self.current_object, bytes):
                data = self.current_object
                conversion_method = "raw bytes"
            
            elif isinstance(self.current_object, str):
                try:
                    data = self.current_object.encode('utf-8')
                    conversion_method = "UTF-8 encoded text"
                except UnicodeEncodeError as e:
                    messagebox.showerror("Encoding Error",
                        f"Cannot encode string to UTF-8!\n\n"
                        f"Error: {str(e)}\n\n"
                        f"String contains invalid characters.")
                    return
            
            elif isinstance(self.current_object, (int, float)):
                data = str(self.current_object).encode('utf-8')
                conversion_method = "number as UTF-8 text"
            
            elif isinstance(self.current_object, (dict, list, tuple)):
                try:
                    json_str = json.dumps(self.current_object, indent=2)
                    data = json_str.encode('utf-8')
                    conversion_method = "JSON encoded"
                except (TypeError, ValueError) as e:
                    # Fall back to pickle
                    try:
                        data = pickle.dumps(self.current_object)
                        conversion_method = "pickle (JSON failed)"
                    except Exception as pickle_error:
                        messagebox.showerror("Conversion Failed",
                            f"Cannot convert to JSON or pickle!\n\n"
                            f"JSON error: {str(e)}\n"
                            f"Pickle error: {str(pickle_error)}")
                        return
            
            else:
                # Try pickle as fallback
                try:
                    data = pickle.dumps(self.current_object)
                    conversion_method = "pickle"
                except Exception as e:
                    messagebox.showerror("Cannot Convert",
                        f"Cannot convert object to binary!\n\n"
                        f"Type: {obj_type}\n"
                        f"Error: {str(e)}")
                    return
            
            if data is None:
                messagebox.showerror("Conversion Failed",
                    f"Could not convert object to binary format!")
                return
            
            # Write to file
            with open(filename, 'wb') as f:
                f.write(data)
            
            messagebox.showinfo("✓ Binary Saved",
                f"Object saved as binary!\n\n"
                f"Type: {obj_type}\n"
                f"Method: {conversion_method}\n"
                f"Size: {len(data):,} bytes\n"
                f"File: {os.path.basename(filename)}\n\n"
                f"Full path:\n{filename}")
        
        except IOError as e:
            messagebox.showerror("File Write Error",
                f"Cannot write to file!\n\n"
                f"Error: {str(e)}")
        
        except Exception as e:
            messagebox.showerror("Save Failed",
                f"Unexpected error!\n\n"
                f"Error: {type(e).__name__}\n"
                f"Details: {str(e)}")

    def load_object_binary(self):
        """Load object from binary file with comprehensive error checking"""
        filename = filedialog.askopenfilename(
            filetypes=[("Binary files", "*.bin"), ("Data files", "*.dat"), ("All files", "*.*")],
            title="Load Object from Binary"
        )
        
        if not filename:
            return
        
        # Check file
        if not os.path.exists(filename):
            messagebox.showerror("File Not Found", f"File does not exist!\n\n{filename}")
            return
        
        if not os.access(filename, os.R_OK):
            messagebox.showerror("Permission Denied", 
                f"Cannot read file!\n\n{filename}")
            return
        
        file_size = os.path.getsize(filename)
        
        if file_size == 0:
            messagebox.showerror("Empty File",
                f"File is empty (0 bytes)!\n\n{filename}")
            return
        
        # Warn about large files
        if file_size > 100 * 1024 * 1024:  # 100 MB
            result = messagebox.askyesno("Large File",
                f"File is {file_size:,} bytes.\n\nContinue?")
            if not result:
                return
        
        try:
            with open(filename, 'rb') as f:
                data = f.read()
            
            # Try multiple interpretations
            loaded_obj = None
            interpretation = "unknown"
            attempts = []
            
            # 1. Try pickle
            try:
                loaded_obj = pickle.loads(data)
                interpretation = "Python pickle"
            except Exception as e:
                attempts.append(f"Pickle: {type(e).__name__}")
            
            # 2. Try JSON
            if loaded_obj is None:
                try:
                    json_str = data.decode('utf-8')
                    loaded_obj = json.loads(json_str)
                    interpretation = "JSON"
                except Exception as e:
                    attempts.append(f"JSON: {type(e).__name__}")
            
            # 3. Try plain text
            if loaded_obj is None:
                try:
                    loaded_obj = data.decode('utf-8')
                    interpretation = "UTF-8 text"
                except Exception as e:
                    attempts.append(f"UTF-8: {type(e).__name__}")
            
            # 4. Keep as raw bytes
            if loaded_obj is None:
                loaded_obj = data
                interpretation = "raw bytes"
            
            obj_type = type(loaded_obj).__name__
            
            # Ask for name
            default_name = os.path.basename(filename).rsplit('.', 1)[0]
            name = self.ask_object_name(default_name)
            
            if not name:
                messagebox.showinfo("Load Cancelled", "Object was not added to browser.")
                return
            
            # Check for duplicates
            if name in self.loaded_objects:
                result = messagebox.askyesno("Duplicate Name",
                    f"'{name}' already exists. Overwrite?")
                if not result:
                    return
            
            # Store object
            self.loaded_objects[name] = loaded_obj
            self.populate_full_object_tree()
            
            # Build info message
            info = f"Binary file loaded!\n\n"
            info += f"Name: {name}\n"
            info += f"Interpretation: {interpretation}\n"
            info += f"Type: {obj_type}\n"
            info += f"File size: {file_size:,} bytes\n"
            
            if attempts:
                info += f"\nAttempted: {', '.join(attempts)}\n"
            
            info += f"\n✓ Available as: self.loaded_objects['{name}']"
            
            messagebox.showinfo("✓ Binary Loaded", info)
        
        except IOError as e:
            messagebox.showerror("Read Error",
                f"Cannot read file!\n\n"
                f"Error: {str(e)}")
        
        except MemoryError:
            messagebox.showerror("Out of Memory",
                f"File is too large!\n\n"
                f"Size: {file_size:,} bytes")
        
        except Exception as e:
            messagebox.showerror("Load Failed",
                f"Unexpected error!\n\n"
                f"Error: {type(e).__name__}\n"
                f"Details: {str(e)}")

    def ask_object_name(self, default="object"):
        """Ask user for a name for loaded object"""
        dialog = tk.Toplevel(self.window)
        dialog.title("Name Loaded Object")
        dialog.geometry("400x150")
        dialog.transient(self.window)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Enter a name for this object:", font=("Arial", 10)).pack(pady=10)
        
        name_var = tk.StringVar(value=default)
        entry = ttk.Entry(dialog, textvariable=name_var, width=40, font=("Arial", 10))
        entry.pack(pady=10, padx=20)
        entry.select_range(0, tk.END)
        entry.focus()
        
        result = [None]
        
        def on_ok():
            result[0] = name_var.get()
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="OK", command=on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT, padx=5)
        
        entry.bind("<Return>", lambda e: on_ok())
        entry.bind("<Escape>", lambda e: on_cancel())
        
        dialog.wait_window()
        return result[0]


def main():
    """Run the Object Browser"""
    app = ObjectBrowser()
    app.window.mainloop()


if __name__ == "__main__":
    main()