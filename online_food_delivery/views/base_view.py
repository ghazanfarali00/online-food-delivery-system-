"""
Base view module for the Online Food Delivery System.
Provides the main application shell with sidebar navigation.
"""

import tkinter as tk
from tkinter import ttk
from config import COLORS, FONTS


class BaseView(tk.Frame):
    """
    Base application shell with sidebar navigation and content area.
    All role-specific views inherit from this base.
    """

    def __init__(self, parent, user, on_logout, menu_items=None):
        """
        Initialize the base view.

        Args:
            parent: Parent Tkinter widget.
            user (dict): Current user data.
            on_logout (callable): Callback when user logs out.
            menu_items (list): List of dicts with 'label', 'icon', 'command'.
        """
        super().__init__(parent, bg=COLORS['bg_light'])
        self.parent = parent
        self.user = user
        self.on_logout = on_logout
        self.menu_items = menu_items or []
        self.active_menu_index = 0
        self.menu_buttons = []

        self._build_layout()

    def _build_layout(self):
        """Build the main layout with sidebar and content area."""
        # Main container
        self.pack(fill=tk.BOTH, expand=True)

        # ─── Sidebar ────────────────────────────────────────────────────
        self.sidebar = tk.Frame(self, bg=COLORS['sidebar_bg'], width=240)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # App Logo / Brand
        brand_frame = tk.Frame(self.sidebar, bg=COLORS['primary'], height=70)
        brand_frame.pack(fill=tk.X)
        brand_frame.pack_propagate(False)

        tk.Label(
            brand_frame, text="🍔 FoodExpress",
            font=FONTS['heading_md'], fg=COLORS['white'],
            bg=COLORS['primary']
        ).pack(pady=18)

        # User info section
        user_frame = tk.Frame(self.sidebar, bg=COLORS['sidebar_bg'], pady=15)
        user_frame.pack(fill=tk.X)

        tk.Label(
            user_frame, text=f"👤  {self.user['name']}",
            font=FONTS['body_bold'], fg=COLORS['white'],
            bg=COLORS['sidebar_bg'], anchor='w'
        ).pack(padx=20, anchor='w')

        role_label = self.user.get('role', 'user').capitalize()
        tk.Label(
            user_frame, text=role_label,
            font=FONTS['caption'], fg=COLORS['sidebar_text'],
            bg=COLORS['sidebar_bg'], anchor='w'
        ).pack(padx=20, anchor='w')

        # Separator
        sep = tk.Frame(self.sidebar, bg=COLORS['sidebar_hover'], height=1)
        sep.pack(fill=tk.X, padx=15, pady=5)

        # Menu Label
        tk.Label(
            self.sidebar, text="MENU",
            font=FONTS['sidebar_heading'], fg=COLORS['sidebar_text'],
            bg=COLORS['sidebar_bg'], anchor='w'
        ).pack(padx=20, pady=(10, 5), anchor='w')

        # Navigation menu items
        self.menu_buttons = []
        for i, item in enumerate(self.menu_items):
            btn = self._create_menu_button(item['icon'], item['label'],
                                           item['command'], i)
            self.menu_buttons.append(btn)

        # Spacer
        spacer = tk.Frame(self.sidebar, bg=COLORS['sidebar_bg'])
        spacer.pack(fill=tk.BOTH, expand=True)

        # Logout button at bottom
        logout_frame = tk.Frame(self.sidebar, bg=COLORS['sidebar_bg'])
        logout_frame.pack(fill=tk.X, pady=10)

        sep2 = tk.Frame(logout_frame, bg=COLORS['sidebar_hover'], height=1)
        sep2.pack(fill=tk.X, padx=15, pady=(0, 10))

        logout_btn = tk.Label(
            logout_frame, text="🚪  Logout",
            font=FONTS['sidebar'], fg=COLORS['danger'],
            bg=COLORS['sidebar_bg'], cursor='hand2',
            padx=20, pady=8
        )
        logout_btn.pack(fill=tk.X)
        logout_btn.bind('<Button-1>', lambda e: self.on_logout())
        logout_btn.bind('<Enter>', lambda e: e.widget.config(
            bg=COLORS['sidebar_hover']))
        logout_btn.bind('<Leave>', lambda e: e.widget.config(
            bg=COLORS['sidebar_bg']))

        # ─── Content Area ───────────────────────────────────────────────
        self.content_wrapper = tk.Frame(self, bg=COLORS['bg_light'])
        self.content_wrapper.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Header bar
        self.header = tk.Frame(
            self.content_wrapper, bg=COLORS['white'], height=60
        )
        self.header.pack(fill=tk.X)
        self.header.pack_propagate(False)

        # Header shadow
        tk.Frame(
            self.content_wrapper, bg=COLORS['border'], height=1
        ).pack(fill=tk.X)

        self.header_title = tk.Label(
            self.header, text="Dashboard",
            font=FONTS['heading_md'], fg=COLORS['text_primary'],
            bg=COLORS['white']
        )
        self.header_title.pack(side=tk.LEFT, padx=25, pady=15)

        # Content frame (scrollable)
        self.content_container = tk.Frame(
            self.content_wrapper, bg=COLORS['bg_light']
        )
        self.content_container.pack(fill=tk.BOTH, expand=True)

        # Canvas + Scrollbar for scrollable content
        self.content_canvas = tk.Canvas(
            self.content_container, bg=COLORS['bg_light'],
            highlightthickness=0
        )
        self.scrollbar = ttk.Scrollbar(
            self.content_container, orient=tk.VERTICAL,
            command=self.content_canvas.yview
        )

        self.content_frame = tk.Frame(
            self.content_canvas, bg=COLORS['bg_light']
        )
        self.content_frame.bind(
            '<Configure>',
            lambda e: self.content_canvas.configure(
                scrollregion=self.content_canvas.bbox('all')
            )
        )

        self.content_canvas.create_window(
            (0, 0), window=self.content_frame, anchor='nw'
        )
        self.content_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.content_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Mouse wheel scrolling
        self.content_canvas.bind_all(
            '<MouseWheel>',
            lambda e: self.content_canvas.yview_scroll(
                int(-1 * (e.delta / 120)), 'units'
            )
        )

        # Bind canvas resize to adjust content frame width
        self.content_canvas.bind('<Configure>', self._on_canvas_configure)

        # Set first menu item as active
        if self.menu_items:
            self.set_active_menu(0)

    def _on_canvas_configure(self, event):
        """Resize the inner frame to match canvas width."""
        self.content_canvas.itemconfig(
            self.content_canvas.find_all()[0] if self.content_canvas.find_all() else None,
            width=event.width
        )

    def _create_menu_button(self, icon, label, command, index):
        """
        Create a sidebar menu button.

        Args:
            icon (str): Unicode icon.
            label (str): Menu label.
            command (callable): Click callback.
            index (int): Menu item index.

        Returns:
            tk.Label: The created menu button widget.
        """
        btn = tk.Label(
            self.sidebar, text=f"{icon}   {label}",
            font=FONTS['sidebar'], fg=COLORS['sidebar_text'],
            bg=COLORS['sidebar_bg'], cursor='hand2',
            padx=20, pady=10, anchor='w'
        )
        btn.pack(fill=tk.X)

        def on_click(e):
            self.set_active_menu(index)
            command()

        btn.bind('<Button-1>', on_click)
        btn.bind('<Enter>', lambda e: self._on_menu_hover(e, index))
        btn.bind('<Leave>', lambda e: self._on_menu_leave(e, index))

        return btn

    def set_active_menu(self, index):
        """
        Set a menu item as active (highlighted).

        Args:
            index (int): Index of the menu item to activate.
        """
        # Deactivate all
        for i, btn in enumerate(self.menu_buttons):
            btn.config(
                bg=COLORS['sidebar_bg'],
                fg=COLORS['sidebar_text']
            )
        # Activate selected
        if 0 <= index < len(self.menu_buttons):
            self.active_menu_index = index
            self.menu_buttons[index].config(
                bg=COLORS['sidebar_active'],
                fg=COLORS['sidebar_text_active']
            )

    def _on_menu_hover(self, event, index):
        """Handle menu button hover effect."""
        if index != self.active_menu_index:
            event.widget.config(bg=COLORS['sidebar_hover'])

    def _on_menu_leave(self, event, index):
        """Handle menu button leave effect."""
        if index != self.active_menu_index:
            event.widget.config(bg=COLORS['sidebar_bg'])

    def set_header_title(self, title):
        """Update the header title text."""
        self.header_title.config(text=title)

    def clear_content(self):
        """Clear all widgets from the content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        # Reset scroll position
        self.content_canvas.yview_moveto(0)
