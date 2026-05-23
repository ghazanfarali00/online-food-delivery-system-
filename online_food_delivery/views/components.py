"""
Reusable UI components for the Online Food Delivery System.
Provides cards, badges, tables, star ratings, and other common widgets.
"""

import tkinter as tk
from tkinter import ttk
from config import COLORS, FONTS
from utils.helpers import format_currency, get_star_display, format_datetime


class StatCard(tk.Frame):
    """A statistics card showing a value with label and icon."""

    def __init__(self, parent, title, value, icon="📊", color=None, **kwargs):
        """
        Create a stat card.

        Args:
            parent: Parent widget.
            title (str): Card title/label.
            value (str): Display value.
            icon (str): Unicode icon.
            color (str): Accent color.
        """
        color = color or COLORS['primary']
        super().__init__(parent, bg=COLORS['white'], padx=20, pady=15,
                         highlightbackground=COLORS['border'],
                         highlightthickness=1, **kwargs)

        # Color accent bar
        accent = tk.Frame(self, bg=color, width=4, height=60)
        accent.pack(side=tk.LEFT, padx=(0, 15))

        # Content
        content = tk.Frame(self, bg=COLORS['white'])
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(
            content, text=title,
            font=FONTS['body_sm'], fg=COLORS['text_secondary'],
            bg=COLORS['white'], anchor='w'
        ).pack(anchor='w')

        tk.Label(
            content, text=str(value),
            font=FONTS['heading_lg'], fg=COLORS['text_primary'],
            bg=COLORS['white'], anchor='w'
        ).pack(anchor='w')

        # Icon
        tk.Label(
            self, text=icon,
            font=FONTS['icon_lg'], fg=color,
            bg=COLORS['white']
        ).pack(side=tk.RIGHT, padx=5)


class RestaurantCard(tk.Frame):
    """A card displaying restaurant information."""

    def __init__(self, parent, restaurant, on_click=None, **kwargs):
        """
        Create a restaurant card.

        Args:
            parent: Parent widget.
            restaurant (dict): Restaurant data.
            on_click (callable): Click callback.
        """
        super().__init__(parent, bg=COLORS['white'], padx=15, pady=12,
                         highlightbackground=COLORS['border'],
                         highlightthickness=1, cursor='hand2', **kwargs)

        # Top row: name + rating
        top = tk.Frame(self, bg=COLORS['white'])
        top.pack(fill=tk.X)

        tk.Label(
            top, text=f"🍽️  {restaurant['name']}",
            font=FONTS['heading_sm'], fg=COLORS['text_primary'],
            bg=COLORS['white'], anchor='w'
        ).pack(side=tk.LEFT)

        rating = restaurant.get('avg_rating', 0)
        rating_text = f"★ {rating:.1f}" if rating else "No ratings"
        rating_color = COLORS['star_filled'] if rating >= 4.0 else (
            COLORS['warning'] if rating >= 3.0 else COLORS['text_secondary']
        )
        tk.Label(
            top, text=rating_text,
            font=FONTS['body_bold'], fg=rating_color,
            bg=COLORS['white']
        ).pack(side=tk.RIGHT)

        # Description
        desc = restaurant.get('description', '')
        if desc and len(desc) > 80:
            desc = desc[:77] + "..."
        tk.Label(
            self, text=desc,
            font=FONTS['body'], fg=COLORS['text_secondary'],
            bg=COLORS['white'], anchor='w', wraplength=400
        ).pack(fill=tk.X, pady=(5, 0))

        # Bottom: cuisine + location
        bottom = tk.Frame(self, bg=COLORS['white'])
        bottom.pack(fill=tk.X, pady=(8, 0))

        cuisine = restaurant.get('cuisine_type', '')
        if cuisine:
            badge = tk.Label(
                bottom, text=f" {cuisine} ",
                font=FONTS['badge'], fg=COLORS['white'],
                bg=COLORS['primary'], padx=8, pady=2
            )
            badge.pack(side=tk.LEFT, padx=(0, 8))

        location = restaurant.get('location', '')
        if location:
            tk.Label(
                bottom, text=f"📍 {location}",
                font=FONTS['body_sm'], fg=COLORS['text_secondary'],
                bg=COLORS['white']
            ).pack(side=tk.LEFT)

        # Bind click
        if on_click:
            self.bind('<Button-1>', lambda e: on_click(restaurant))
            for child in self.winfo_children():
                child.bind('<Button-1>', lambda e: on_click(restaurant))
                for sub_child in child.winfo_children():
                    sub_child.bind('<Button-1>', lambda e: on_click(restaurant))

        # Hover effect
        self.bind('<Enter>', lambda e: self.config(
            highlightbackground=COLORS['primary']))
        self.bind('<Leave>', lambda e: self.config(
            highlightbackground=COLORS['border']))


class MenuItemCard(tk.Frame):
    """A card displaying a menu item with add-to-cart button."""

    def __init__(self, parent, item, on_add=None, **kwargs):
        """
        Create a menu item card.

        Args:
            parent: Parent widget.
            item (dict): Menu item data.
            on_add (callable): Add-to-cart callback.
        """
        super().__init__(parent, bg=COLORS['white'], padx=15, pady=10,
                         highlightbackground=COLORS['border'],
                         highlightthickness=1, **kwargs)

        # Left content
        left = tk.Frame(self, bg=COLORS['white'])
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Item name
        tk.Label(
            left, text=item['name'],
            font=FONTS['body_bold'], fg=COLORS['text_primary'],
            bg=COLORS['white'], anchor='w'
        ).pack(anchor='w')

        # Description
        desc = item.get('description', '')
        if desc:
            tk.Label(
                left, text=desc,
                font=FONTS['body_sm'], fg=COLORS['text_secondary'],
                bg=COLORS['white'], anchor='w', wraplength=350
            ).pack(anchor='w', pady=(2, 0))

        # Category badge
        category = item.get('category', '')
        if category:
            cat_label = tk.Label(
                left, text=f" {category} ",
                font=FONTS['badge'], fg=COLORS['accent'],
                bg=COLORS['bg_medium'], padx=6, pady=1
            )
            cat_label.pack(anchor='w', pady=(4, 0))

        # Right: price + add button
        right = tk.Frame(self, bg=COLORS['white'])
        right.pack(side=tk.RIGHT, padx=(10, 0))

        tk.Label(
            right, text=format_currency(item['price']),
            font=FONTS['price'], fg=COLORS['primary'],
            bg=COLORS['white']
        ).pack()

        if on_add:
            add_btn = tk.Label(
                right, text="+ Add",
                font=FONTS['badge'], fg=COLORS['white'],
                bg=COLORS['primary'], padx=12, pady=4,
                cursor='hand2'
            )
            add_btn.pack(pady=(5, 0))
            add_btn.bind('<Button-1>', lambda e: on_add(item))
            add_btn.bind('<Enter>', lambda e: e.widget.config(
                bg=COLORS['primary_dark']))
            add_btn.bind('<Leave>', lambda e: e.widget.config(
                bg=COLORS['primary']))


class OrderCard(tk.Frame):
    """A card displaying order summary information."""

    def __init__(self, parent, order, on_click=None, show_customer=False,
                 **kwargs):
        """
        Create an order card.

        Args:
            parent: Parent widget.
            order (dict): Order data.
            on_click (callable): Click callback.
            show_customer (bool): Whether to show customer name.
        """
        super().__init__(parent, bg=COLORS['white'], padx=15, pady=12,
                         highlightbackground=COLORS['border'],
                         highlightthickness=1, **kwargs)

        # Top row: order ID + status
        top = tk.Frame(self, bg=COLORS['white'])
        top.pack(fill=tk.X)

        tk.Label(
            top, text=f"🧾 {order['order_uid']}",
            font=FONTS['body_bold'], fg=COLORS['text_primary'],
            bg=COLORS['white']
        ).pack(side=tk.LEFT)

        StatusBadge(top, order['status']).pack(side=tk.RIGHT)

        # Restaurant name
        restaurant_name = order.get('restaurant_name', '')
        if restaurant_name:
            tk.Label(
                self, text=f"🍽️ {restaurant_name}",
                font=FONTS['body'], fg=COLORS['text_secondary'],
                bg=COLORS['white'], anchor='w'
            ).pack(fill=tk.X, pady=(4, 0))

        # Customer name (for vendor/admin views)
        if show_customer and order.get('customer_name'):
            tk.Label(
                self, text=f"👤 {order['customer_name']}",
                font=FONTS['body_sm'], fg=COLORS['text_secondary'],
                bg=COLORS['white'], anchor='w'
            ).pack(fill=tk.X, pady=(2, 0))

        # Bottom: total + date
        bottom = tk.Frame(self, bg=COLORS['white'])
        bottom.pack(fill=tk.X, pady=(6, 0))

        tk.Label(
            bottom, text=format_currency(order['total_amount']),
            font=FONTS['body_bold'], fg=COLORS['primary'],
            bg=COLORS['white']
        ).pack(side=tk.LEFT)

        tk.Label(
            bottom, text=format_datetime(order.get('created_at', '')),
            font=FONTS['caption'], fg=COLORS['text_muted'],
            bg=COLORS['white']
        ).pack(side=tk.RIGHT)

        # Click binding
        if on_click:
            self.config(cursor='hand2')
            self.bind('<Button-1>', lambda e: on_click(order))
            for child in self.winfo_children():
                child.bind('<Button-1>', lambda e: on_click(order))
                for sc in child.winfo_children():
                    sc.bind('<Button-1>', lambda e: on_click(order))

            self.bind('<Enter>', lambda e: self.config(
                highlightbackground=COLORS['primary']))
            self.bind('<Leave>', lambda e: self.config(
                highlightbackground=COLORS['border']))


class StatusBadge(tk.Label):
    """A colored badge showing order status."""

    STATUS_COLORS = {
        'placed': ('status_placed', 'white'),
        'preparing': ('status_preparing', 'white'),
        'out_for_delivery': ('status_out', 'white'),
        'delivered': ('status_delivered', 'white'),
        'cancelled': ('status_cancelled', 'white'),
        'open': ('info', 'white'),
        'in_progress': ('warning', 'white'),
        'resolved': ('success', 'white'),
        'closed': ('text_secondary', 'white'),
        'active': ('success', 'white'),
        'inactive': ('danger', 'white'),
        'pending': ('warning', 'white'),
        'paid': ('success', 'white'),
        'failed': ('danger', 'white'),
    }

    STATUS_LABELS = {
        'placed': 'Placed',
        'preparing': 'Preparing',
        'out_for_delivery': 'Out for Delivery',
        'delivered': 'Delivered',
        'cancelled': 'Cancelled',
        'open': 'Open',
        'in_progress': 'In Progress',
        'resolved': 'Resolved',
        'closed': 'Closed',
        'pending': 'Pending',
        'paid': 'Paid',
        'failed': 'Failed',
    }

    def __init__(self, parent, status, **kwargs):
        bg_key, fg_key = self.STATUS_COLORS.get(
            status, ('text_secondary', 'white')
        )
        label = self.STATUS_LABELS.get(status, status.replace('_', ' ').title())
        super().__init__(
            parent, text=f" {label} ",
            font=FONTS['badge'], fg=COLORS[fg_key],
            bg=COLORS[bg_key], padx=8, pady=2, **kwargs
        )


class StarRating(tk.Frame):
    """Interactive or display-only star rating widget."""

    def __init__(self, parent, rating=0, max_stars=5, interactive=False,
                 on_rate=None, size='body_lg', **kwargs):
        """
        Create a star rating widget.

        Args:
            parent: Parent widget.
            rating (int): Current rating (0-5).
            max_stars (int): Maximum number of stars.
            interactive (bool): Allow clicking to set rating.
            on_rate (callable): Callback when rating is set.
            size (str): Font size key.
        """
        super().__init__(parent, bg=COLORS['white'], **kwargs)
        self.rating = rating
        self.max_stars = max_stars
        self.on_rate = on_rate
        self.stars = []

        for i in range(max_stars):
            star = tk.Label(
                self, text="★" if i < rating else "☆",
                font=FONTS[size],
                fg=COLORS['star_filled'] if i < rating else COLORS['star_empty'],
                bg=COLORS['white'],
                cursor='hand2' if interactive else ''
            )
            star.pack(side=tk.LEFT)
            self.stars.append(star)

            if interactive:
                star.bind('<Button-1>', lambda e, idx=i: self._set_rating(idx + 1))
                star.bind('<Enter>', lambda e, idx=i: self._hover(idx + 1))
                star.bind('<Leave>', lambda e: self._show_rating())

    def _set_rating(self, rating):
        """Set the rating and trigger callback."""
        self.rating = rating
        self._show_rating()
        if self.on_rate:
            self.on_rate(rating)

    def _hover(self, stars):
        """Show hover effect."""
        for i, star in enumerate(self.stars):
            if i < stars:
                star.config(text="★", fg=COLORS['star_filled'])
            else:
                star.config(text="☆", fg=COLORS['star_empty'])

    def _show_rating(self):
        """Show current rating."""
        for i, star in enumerate(self.stars):
            if i < self.rating:
                star.config(text="★", fg=COLORS['star_filled'])
            else:
                star.config(text="☆", fg=COLORS['star_empty'])

    def get_rating(self):
        """Get current rating value."""
        return self.rating


class DataTable(tk.Frame):
    """A styled data table with headers and rows."""

    def __init__(self, parent, columns, data, actions=None, **kwargs):
        """
        Create a data table.

        Args:
            parent: Parent widget.
            columns (list): List of dicts with 'key', 'label', 'width'.
            data (list): List of row data dicts.
            actions (list): List of dicts with 'label', 'command', 'color'.
        """
        super().__init__(parent, bg=COLORS['white'],
                         highlightbackground=COLORS['border'],
                         highlightthickness=1, **kwargs)

        self.columns = columns
        self.actions = actions or []

        # Header
        header = tk.Frame(self, bg=COLORS['bg_medium'])
        header.pack(fill=tk.X)

        for col in columns:
            tk.Label(
                header, text=col['label'],
                font=FONTS['body_bold'], fg=COLORS['text_primary'],
                bg=COLORS['bg_medium'], width=col.get('width', 15),
                anchor='w', padx=10, pady=8
            ).pack(side=tk.LEFT)

        if actions:
            tk.Label(
                header, text="Actions",
                font=FONTS['body_bold'], fg=COLORS['text_primary'],
                bg=COLORS['bg_medium'], width=20, anchor='w',
                padx=10, pady=8
            ).pack(side=tk.LEFT)

        # Rows
        for i, row_data in enumerate(data):
            row_bg = COLORS['white'] if i % 2 == 0 else COLORS['bg_light']
            row = tk.Frame(self, bg=row_bg)
            row.pack(fill=tk.X)

            for col in columns:
                value = row_data.get(col['key'], '')
                if col.get('format') == 'currency':
                    value = format_currency(value)
                elif col.get('format') == 'status':
                    StatusBadge(row, str(value)).pack(
                        side=tk.LEFT, padx=10, pady=6)
                    continue

                tk.Label(
                    row, text=str(value),
                    font=FONTS['body'], fg=COLORS['text_primary'],
                    bg=row_bg, width=col.get('width', 15),
                    anchor='w', padx=10, pady=6
                ).pack(side=tk.LEFT)

            if actions:
                action_frame = tk.Frame(row, bg=row_bg)
                action_frame.pack(side=tk.LEFT, padx=10, pady=4)
                for action in actions:
                    btn = tk.Label(
                        action_frame, text=action['label'],
                        font=FONTS['badge'],
                        fg=COLORS['white'],
                        bg=COLORS.get(action.get('color', 'primary'), COLORS['primary']),
                        padx=8, pady=2, cursor='hand2'
                    )
                    btn.pack(side=tk.LEFT, padx=2)
                    btn.bind('<Button-1>',
                             lambda e, d=row_data, a=action: a['command'](d))


class FormField(tk.Frame):
    """A labeled form input field."""

    def __init__(self, parent, label, placeholder="", field_type="entry",
                 options=None, **kwargs):
        """
        Create a form field.

        Args:
            parent: Parent widget.
            label (str): Field label.
            placeholder (str): Placeholder text.
            field_type (str): 'entry', 'password', 'text', 'combo'.
            options (list): Options for combo box.
        """
        super().__init__(parent, bg=COLORS['white'], **kwargs)

        tk.Label(
            self, text=label,
            font=FONTS['body_bold'], fg=COLORS['text_primary'],
            bg=COLORS['white'], anchor='w'
        ).pack(anchor='w', pady=(0, 4))

        if field_type == 'entry':
            self.input = tk.Entry(
                self, font=FONTS['body'], fg=COLORS['text_primary'],
                bg=COLORS['bg_light'], relief='flat', bd=0,
                highlightbackground=COLORS['border'],
                highlightthickness=1, insertbackground=COLORS['text_primary']
            )
            self.input.pack(fill=tk.X, ipady=8, ipadx=8)
            if placeholder:
                self.input.insert(0, placeholder)

        elif field_type == 'password':
            self.input = tk.Entry(
                self, font=FONTS['body'], fg=COLORS['text_primary'],
                bg=COLORS['bg_light'], relief='flat', bd=0,
                show='●', highlightbackground=COLORS['border'],
                highlightthickness=1, insertbackground=COLORS['text_primary']
            )
            self.input.pack(fill=tk.X, ipady=8, ipadx=8)

        elif field_type == 'text':
            self.input = tk.Text(
                self, font=FONTS['body'], fg=COLORS['text_primary'],
                bg=COLORS['bg_light'], relief='flat', bd=0,
                height=4, highlightbackground=COLORS['border'],
                highlightthickness=1, insertbackground=COLORS['text_primary']
            )
            self.input.pack(fill=tk.X, ipady=4, ipadx=8)

        elif field_type == 'combo':
            self.input = ttk.Combobox(
                self, font=FONTS['body'], values=options or [],
                state='readonly'
            )
            self.input.pack(fill=tk.X, ipady=4)
            if options:
                self.input.current(0)

    def get(self):
        """Get the field value."""
        if isinstance(self.input, tk.Text):
            return self.input.get('1.0', tk.END).strip()
        return self.input.get()

    def set(self, value):
        """Set the field value."""
        if isinstance(self.input, tk.Text):
            self.input.delete('1.0', tk.END)
            self.input.insert('1.0', value)
        elif isinstance(self.input, ttk.Combobox):
            self.input.set(value)
        else:
            self.input.delete(0, tk.END)
            self.input.insert(0, value)

    def clear(self):
        """Clear the field."""
        if isinstance(self.input, tk.Text):
            self.input.delete('1.0', tk.END)
        else:
            self.input.delete(0, tk.END)


class PrimaryButton(tk.Label):
    """A styled primary button."""

    def __init__(self, parent, text, command, color=None, **kwargs):
        color = color or COLORS['primary']
        dark_color = COLORS.get('primary_dark', color)
        super().__init__(
            parent, text=text,
            font=FONTS['button'], fg=COLORS['white'],
            bg=color, padx=20, pady=10, cursor='hand2', **kwargs
        )
        self.bind('<Button-1>', lambda e: command())
        self.bind('<Enter>', lambda e: self.config(bg=dark_color))
        self.bind('<Leave>', lambda e: self.config(bg=color))


class SecondaryButton(tk.Label):
    """A styled secondary button (outlined)."""

    def __init__(self, parent, text, command, **kwargs):
        super().__init__(
            parent, text=text,
            font=FONTS['button'], fg=COLORS['primary'],
            bg=COLORS['white'], padx=20, pady=10, cursor='hand2',
            highlightbackground=COLORS['primary'], highlightthickness=1,
            **kwargs
        )
        self.bind('<Button-1>', lambda e: command())
        self.bind('<Enter>', lambda e: self.config(
            bg=COLORS['primary_bg']))
        self.bind('<Leave>', lambda e: self.config(bg=COLORS['white']))


class EmptyState(tk.Frame):
    """A placeholder for empty lists/views."""

    def __init__(self, parent, icon="📭", message="Nothing to show",
                 sub_message="", **kwargs):
        super().__init__(parent, bg=COLORS['white'], padx=30, pady=40,
                         **kwargs)
        tk.Label(
            self, text=icon,
            font=("Segoe UI", 40), bg=COLORS['white']
        ).pack()
        tk.Label(
            self, text=message,
            font=FONTS['heading_sm'], fg=COLORS['text_secondary'],
            bg=COLORS['white']
        ).pack(pady=(10, 0))
        if sub_message:
            tk.Label(
                self, text=sub_message,
                font=FONTS['body'], fg=COLORS['text_muted'],
                bg=COLORS['white']
            ).pack(pady=(5, 0))
