"""Vendor views for the Online Food Delivery System."""
import tkinter as tk
from tkinter import ttk, messagebox
from config import COLORS, FONTS, CUISINE_TYPES, MENU_CATEGORIES
from views.base_view import BaseView
from views.components import (FormField, PrimaryButton, OrderCard, StatusBadge,
    EmptyState, StarRating, MenuItemCard)
from utils.helpers import format_currency, format_datetime
from utils.exceptions import ValidationError


class VendorView(BaseView):
    """Vendor dashboard view."""
    def __init__(self, parent, user, controller, on_logout):
        self.ctrl = controller
        menu = [
            {'icon': '🏪', 'label': 'My Restaurant', 'command': self.show_restaurant},
            {'icon': '📋', 'label': 'Menu Items', 'command': self.show_menu},
            {'icon': '📦', 'label': 'Orders', 'command': self.show_orders},
            {'icon': '⭐', 'label': 'Reviews', 'command': self.show_reviews},
        ]
        super().__init__(parent, user, on_logout, menu)
        self.show_restaurant()

    def show_restaurant(self):
        self.clear_content()
        self.set_header_title("My Restaurant")
        self.set_active_menu(0)
        f = self.content_frame
        rest = self.ctrl.get_my_restaurant()
        if not rest:
            cf = tk.Frame(f, bg=COLORS['white'], padx=30, pady=20)
            cf.pack(fill=tk.X, padx=20, pady=15)
            tk.Label(cf, text="Create Your Restaurant", font=FONTS['heading_md'],
                fg=COLORS['text_primary'], bg=COLORS['white']).pack(anchor='w', pady=(0,10))
            self.r_name = FormField(cf, "Restaurant Name")
            self.r_name.pack(fill=tk.X, pady=5)
            self.r_desc = FormField(cf, "Description", field_type="text")
            self.r_desc.pack(fill=tk.X, pady=5)
            self.r_cuisine = FormField(cf, "Cuisine Type", field_type="combo", options=CUISINE_TYPES)
            self.r_cuisine.pack(fill=tk.X, pady=5)
            self.r_location = FormField(cf, "Location")
            self.r_location.pack(fill=tk.X, pady=5)
            PrimaryButton(cf, "Create Restaurant", self._create_restaurant).pack(anchor='w', pady=10)
            return
        # Show restaurant details
        df = tk.Frame(f, bg=COLORS['white'], padx=25, pady=20)
        df.pack(fill=tk.X, padx=20, pady=15)
        tk.Label(df, text=f"🍽️ {rest['name']}", font=FONTS['heading_lg'],
            fg=COLORS['text_primary'], bg=COLORS['white']).pack(anchor='w')
        tk.Label(df, text=rest.get('description',''), font=FONTS['body'],
            fg=COLORS['text_secondary'], bg=COLORS['white'], wraplength=500).pack(anchor='w', pady=5)
        info = tk.Frame(df, bg=COLORS['white'])
        info.pack(anchor='w', pady=5)
        tk.Label(info, text=f"🍕 {rest.get('cuisine_type','')}", font=FONTS['body'],
            fg=COLORS['accent'], bg=COLORS['white']).pack(side=tk.LEFT, padx=(0,20))
        tk.Label(info, text=f"📍 {rest.get('location','')}", font=FONTS['body'],
            fg=COLORS['text_secondary'], bg=COLORS['white']).pack(side=tk.LEFT, padx=(0,20))
        tk.Label(info, text=f"★ {rest.get('avg_rating',0):.1f}", font=FONTS['body_bold'],
            fg=COLORS['star_filled'], bg=COLORS['white']).pack(side=tk.LEFT)
        status = "Active ✅" if rest.get('is_active') else "Inactive ❌"
        tk.Label(df, text=f"Status: {status}", font=FONTS['body_bold'],
            fg=COLORS['success'] if rest.get('is_active') else COLORS['danger'],
            bg=COLORS['white']).pack(anchor='w', pady=5)
        # Edit form
        ef = tk.Frame(f, bg=COLORS['white'], padx=25, pady=20)
        ef.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(ef, text="Edit Restaurant", font=FONTS['heading_sm'],
            fg=COLORS['text_primary'], bg=COLORS['white']).pack(anchor='w', pady=(0,10))
        self.e_name = FormField(ef, "Name")
        self.e_name.pack(fill=tk.X, pady=3)
        self.e_name.set(rest['name'])
        self.e_desc = FormField(ef, "Description", field_type="text")
        self.e_desc.pack(fill=tk.X, pady=3)
        self.e_desc.set(rest.get('description',''))
        self.e_loc = FormField(ef, "Location")
        self.e_loc.pack(fill=tk.X, pady=3)
        self.e_loc.set(rest.get('location',''))
        self._edit_rest_id = rest['id']
        PrimaryButton(ef, "Save Changes", self._update_restaurant).pack(anchor='w', pady=10)

    def _create_restaurant(self):
        try:
            self.ctrl.create_restaurant(self.r_name.get(), self.r_desc.get(),
                self.r_cuisine.get(), self.r_location.get())
            messagebox.showinfo("Success", "Restaurant created!")
            self.show_restaurant()
        except ValidationError as e:
            messagebox.showerror("Error", str(e))

    def _update_restaurant(self):
        try:
            self.ctrl.update_restaurant(self._edit_rest_id,
                name=self.e_name.get(), description=self.e_desc.get(), location=self.e_loc.get())
            messagebox.showinfo("Success", "Restaurant updated!")
            self.show_restaurant()
        except ValidationError as e:
            messagebox.showerror("Error", str(e))

    def show_menu(self):
        self.clear_content()
        self.set_header_title("Menu Management")
        self.set_active_menu(1)
        f = self.content_frame
        rest = self.ctrl.get_my_restaurant()
        if not rest:
            EmptyState(f, "🏪", "Create a restaurant first").pack(padx=20, pady=40, fill=tk.X)
            return
        rid = rest['id']
        # Add item form
        af = tk.Frame(f, bg=COLORS['white'], padx=25, pady=15)
        af.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(af, text="Add Menu Item", font=FONTS['heading_sm'],
            fg=COLORS['text_primary'], bg=COLORS['white']).pack(anchor='w', pady=(0,10))
        row1 = tk.Frame(af, bg=COLORS['white'])
        row1.pack(fill=tk.X)
        self.m_name = FormField(row1, "Item Name")
        self.m_name.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,10))
        self.m_price = FormField(row1, "Price (Rs)")
        self.m_price.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.m_cat = FormField(af, "Category", field_type="combo", options=MENU_CATEGORIES)
        self.m_cat.pack(fill=tk.X, pady=5)
        self.m_desc = FormField(af, "Description")
        self.m_desc.pack(fill=tk.X, pady=5)
        PrimaryButton(af, "Add Item", lambda: self._add_item(rid)).pack(anchor='w', pady=5)
        # Current items
        items = self.ctrl.get_menu_items(rid)
        tk.Label(f, text=f"Menu Items ({len(items)})", font=FONTS['heading_sm'],
            fg=COLORS['text_primary'], bg=COLORS['bg_light']).pack(anchor='w', padx=20, pady=(15,5))
        if not items:
            EmptyState(f, "📋", "No menu items yet").pack(padx=20, fill=tk.X)
            return
        for item in items:
            row = tk.Frame(f, bg=COLORS['white'], padx=15, pady=8,
                highlightbackground=COLORS['border'], highlightthickness=1)
            row.pack(fill=tk.X, padx=20, pady=2)
            avail = "✅" if item['is_available'] else "❌"
            tk.Label(row, text=f"{avail} {item['name']}", font=FONTS['body_bold'],
                fg=COLORS['text_primary'], bg=COLORS['white']).pack(side=tk.LEFT)
            # Delete
            db = tk.Label(row, text="Delete", font=FONTS['badge'], fg=COLORS['white'],
                bg=COLORS['danger'], padx=8, pady=2, cursor='hand2')
            db.pack(side=tk.RIGHT, padx=2)
            db.bind('<Button-1>', lambda e, iid=item['id'], r=rid: self._del_item(iid, r))
            # Toggle
            ttext = "Disable" if item['is_available'] else "Enable"
            tcolor = COLORS['warning'] if item['is_available'] else COLORS['success']
            tb = tk.Label(row, text=ttext, font=FONTS['badge'], fg=COLORS['white'],
                bg=tcolor, padx=8, pady=2, cursor='hand2')
            tb.pack(side=tk.RIGHT, padx=2)
            tb.bind('<Button-1>', lambda e, iid=item['id'], a=item['is_available'], r=rid:
                self._toggle_item(iid, not a, r))
            tk.Label(row, text=format_currency(item['price']), font=FONTS['body_bold'],
                fg=COLORS['primary'], bg=COLORS['white']).pack(side=tk.RIGHT, padx=10)
            tk.Label(row, text=item.get('category',''), font=FONTS['body_sm'],
                fg=COLORS['text_secondary'], bg=COLORS['white']).pack(side=tk.RIGHT, padx=5)

    def _add_item(self, rid):
        try:
            self.ctrl.add_menu_item(rid, self.m_name.get(), self.m_desc.get(),
                self.m_cat.get(), self.m_price.get())
            messagebox.showinfo("Success", "Item added!")
            self.show_menu()
        except (ValidationError, Exception) as e:
            messagebox.showerror("Error", str(e))

    def _del_item(self, iid, rid):
        if messagebox.askyesno("Confirm", "Delete this item?"):
            self.ctrl.delete_menu_item(iid)
            self.show_menu()

    def _toggle_item(self, iid, avail, rid):
        self.ctrl.toggle_item_availability(iid, avail)
        self.show_menu()

    def show_orders(self):
        self.clear_content()
        self.set_header_title("Orders")
        self.set_active_menu(2)
        f = self.content_frame
        rest = self.ctrl.get_my_restaurant()
        if not rest:
            EmptyState(f, "🏪", "Create a restaurant first").pack(padx=20, pady=40, fill=tk.X)
            return
        orders = self.ctrl.get_orders(rest['id'])
        if not orders:
            EmptyState(f, "📦", "No orders yet").pack(padx=20, pady=40, fill=tk.X)
            return
        for o in orders:
            card = tk.Frame(f, bg=COLORS['white'], padx=15, pady=10,
                highlightbackground=COLORS['border'], highlightthickness=1)
            card.pack(fill=tk.X, padx=20, pady=4)
            top = tk.Frame(card, bg=COLORS['white'])
            top.pack(fill=tk.X)
            tk.Label(top, text=f"🧾 {o['order_uid']}", font=FONTS['body_bold'],
                fg=COLORS['text_primary'], bg=COLORS['white']).pack(side=tk.LEFT)
            StatusBadge(top, o['status']).pack(side=tk.RIGHT)
            tk.Label(card, text=f"👤 {o.get('customer_name','')} | 📞 {o.get('customer_phone','')}",
                font=FONTS['body_sm'], fg=COLORS['text_secondary'], bg=COLORS['white']).pack(anchor='w', pady=2)
            tk.Label(card, text=f"💰 {format_currency(o['total_amount'])} | 📅 {format_datetime(o.get('created_at',''))}",
                font=FONTS['body_sm'], fg=COLORS['text_muted'], bg=COLORS['white']).pack(anchor='w')
            # Status buttons
            bf = tk.Frame(card, bg=COLORS['white'])
            bf.pack(anchor='w', pady=(5,0))
            if o['status'] == 'placed':
                b = tk.Label(bf, text="Start Preparing", font=FONTS['badge'], fg=COLORS['white'],
                    bg=COLORS['warning'], padx=10, pady=3, cursor='hand2')
                b.pack(side=tk.LEFT, padx=2)
                b.bind('<Button-1>', lambda e, oid=o['id']: self._update_status(oid, 'preparing'))
            elif o['status'] == 'preparing':
                b = tk.Label(bf, text="Ready for Delivery", font=FONTS['badge'], fg=COLORS['white'],
                    bg=COLORS['success'], padx=10, pady=3, cursor='hand2')
                b.pack(side=tk.LEFT, padx=2)
                b.bind('<Button-1>', lambda e, oid=o['id']: self._update_status(oid, 'out_for_delivery'))

    def _update_status(self, oid, status):
        self.ctrl.update_order_status(oid, status)
        self.show_orders()

    def show_reviews(self):
        self.clear_content()
        self.set_header_title("Customer Reviews")
        self.set_active_menu(3)
        f = self.content_frame
        rest = self.ctrl.get_my_restaurant()
        if not rest:
            EmptyState(f, "🏪", "Create a restaurant first").pack(padx=20, pady=40, fill=tk.X)
            return
        reviews = self.ctrl.get_restaurant_reviews(rest['id'])
        if not reviews:
            EmptyState(f, "⭐", "No reviews yet").pack(padx=20, pady=40, fill=tk.X)
            return
        for r in reviews:
            rf = tk.Frame(f, bg=COLORS['white'], padx=15, pady=10,
                highlightbackground=COLORS['border'], highlightthickness=1)
            rf.pack(fill=tk.X, padx=20, pady=3)
            top = tk.Frame(rf, bg=COLORS['white'])
            top.pack(fill=tk.X)
            tk.Label(top, text=f"👤 {r.get('reviewer_name','')}", font=FONTS['body_bold'],
                fg=COLORS['text_primary'], bg=COLORS['white']).pack(side=tk.LEFT)
            StarRating(top, rating=r['rating']).pack(side=tk.RIGHT)
            if r.get('comment'):
                tk.Label(rf, text=r['comment'], font=FONTS['body'], fg=COLORS['text_secondary'],
                    bg=COLORS['white'], wraplength=500, anchor='w').pack(anchor='w', pady=(5,0))
            tk.Label(rf, text=format_datetime(r.get('created_at','')), font=FONTS['caption'],
                fg=COLORS['text_muted'], bg=COLORS['white']).pack(anchor='w', pady=(3,0))
