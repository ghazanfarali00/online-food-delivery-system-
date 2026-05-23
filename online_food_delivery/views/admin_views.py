"""Admin views for the Online Food Delivery System."""
import tkinter as tk
from tkinter import ttk, messagebox
from config import COLORS, FONTS, ORDER_STATUSES
from views.base_view import BaseView
from views.components import (StatCard, OrderCard, StatusBadge, EmptyState,
    PrimaryButton, StarRating)
from utils.helpers import format_currency, format_datetime
from utils.exceptions import ValidationError


class AdminView(BaseView):
    """Admin dashboard view."""
    def __init__(self, parent, user, controller, on_logout):
        self.ctrl = controller
        menu = [
            {'icon': '📊', 'label': 'Dashboard', 'command': self.show_dashboard},
            {'icon': '👥', 'label': 'Users', 'command': self.show_users},
            {'icon': '🍽️', 'label': 'Restaurants', 'command': self.show_restaurants},
            {'icon': '📦', 'label': 'Orders', 'command': self.show_orders},
            {'icon': '⭐', 'label': 'Reviews', 'command': self.show_reviews},
            {'icon': '🎫', 'label': 'Support Tickets', 'command': self.show_tickets},
        ]
        super().__init__(parent, user, on_logout, menu)
        self.show_dashboard()

    def show_dashboard(self):
        self.clear_content()
        self.set_header_title("Admin Dashboard")
        self.set_active_menu(0)
        f = self.content_frame
        stats = self.ctrl.get_dashboard_stats()
        # Stats cards
        cards_frame = tk.Frame(f, bg=COLORS['bg_light'])
        cards_frame.pack(fill=tk.X, padx=20, pady=15)
        cards = [
            ("Total Orders", stats['total_orders'], "📦", COLORS['primary']),
            ("Revenue", format_currency(stats['total_revenue']), "💰", COLORS['success']),
            ("Active Orders", stats['active_orders'], "🔄", COLORS['warning']),
            ("Total Users", stats['total_users'], "👥", COLORS['accent']),
        ]
        for i, (title, val, icon, color) in enumerate(cards):
            sc = StatCard(cards_frame, title, val, icon, color)
            sc.grid(row=0, column=i, padx=5, sticky='ew')
            cards_frame.columnconfigure(i, weight=1)
        # Second row
        cards2 = tk.Frame(f, bg=COLORS['bg_light'])
        cards2.pack(fill=tk.X, padx=20, pady=5)
        cards2_data = [
            ("Customers", stats['total_customers'], "🛍️", COLORS['info']),
            ("Vendors", stats['total_vendors'], "🏪", COLORS['warning']),
            ("Delivery Staff", stats['total_delivery'], "🚗", COLORS['success']),
            ("Restaurants", stats['total_restaurants'], "🍽️", COLORS['primary']),
        ]
        for i, (title, val, icon, color) in enumerate(cards2_data):
            sc = StatCard(cards2, title, val, icon, color)
            sc.grid(row=0, column=i, padx=5, sticky='ew')
            cards2.columnconfigure(i, weight=1)
        # Revenue by restaurant
        rev = self.ctrl.get_revenue_by_restaurant()
        if rev:
            rf = tk.Frame(f, bg=COLORS['white'], padx=20, pady=15)
            rf.pack(fill=tk.X, padx=20, pady=10)
            tk.Label(rf, text="Revenue by Restaurant", font=FONTS['heading_sm'],
                fg=COLORS['text_primary'], bg=COLORS['white']).pack(anchor='w', pady=(0,10))
            for r in rev:
                row = tk.Frame(rf, bg=COLORS['bg_light'], padx=10, pady=5)
                row.pack(fill=tk.X, pady=2)
                tk.Label(row, text=r['name'], font=FONTS['body_bold'],
                    fg=COLORS['text_primary'], bg=COLORS['bg_light']).pack(side=tk.LEFT)
                tk.Label(row, text=format_currency(r['revenue']), font=FONTS['body_bold'],
                    fg=COLORS['primary'], bg=COLORS['bg_light']).pack(side=tk.RIGHT)
                tk.Label(row, text=f"({r['order_count']} orders)", font=FONTS['body_sm'],
                    fg=COLORS['text_secondary'], bg=COLORS['bg_light']).pack(side=tk.RIGHT, padx=10)

    def show_users(self):
        self.clear_content()
        self.set_header_title("User Management")
        self.set_active_menu(1)
        f = self.content_frame
        # Filter
        ff = tk.Frame(f, bg=COLORS['white'], padx=15, pady=8)
        ff.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(ff, text="Filter by Role:", font=FONTS['body_bold'],
            bg=COLORS['white']).pack(side=tk.LEFT, padx=(0,10))
        self.user_filter = tk.StringVar(value="All")
        for r in ["All", "customer", "vendor", "delivery", "admin"]:
            tk.Radiobutton(ff, text=r.capitalize(), variable=self.user_filter, value=r,
                font=FONTS['body'], bg=COLORS['white'],
                command=self.show_users).pack(side=tk.LEFT, padx=5)
        role = self.user_filter.get()
        users = self.ctrl.get_all_users(role if role != "All" else None)
        for u in users:
            row = tk.Frame(f, bg=COLORS['white'], padx=15, pady=8,
                highlightbackground=COLORS['border'], highlightthickness=1)
            row.pack(fill=tk.X, padx=20, pady=2)
            status_icon = "🟢" if u['is_active'] else "🔴"
            tk.Label(row, text=f"{status_icon} {u['name']}", font=FONTS['body_bold'],
                fg=COLORS['text_primary'], bg=COLORS['white']).pack(side=tk.LEFT)
            # Toggle button
            if u['role'] != 'admin':
                ttext = "Deactivate" if u['is_active'] else "Activate"
                tcolor = COLORS['danger'] if u['is_active'] else COLORS['success']
                tb = tk.Label(row, text=ttext, font=FONTS['badge'], fg=COLORS['white'],
                    bg=tcolor, padx=8, pady=2, cursor='hand2')
                tb.pack(side=tk.RIGHT, padx=5)
                tb.bind('<Button-1>', lambda e, uid=u['id'], a=u['is_active']:
                    self._toggle_user(uid, not a))
            tk.Label(row, text=u['role'].capitalize(), font=FONTS['badge'],
                fg=COLORS['white'], bg=COLORS['accent'], padx=6, pady=1).pack(side=tk.RIGHT, padx=5)
            tk.Label(row, text=u['email'], font=FONTS['body_sm'],
                fg=COLORS['text_secondary'], bg=COLORS['white']).pack(side=tk.RIGHT, padx=10)

    def _toggle_user(self, uid, active):
        try:
            self.ctrl.toggle_user_status(uid, active)
            self.show_users()
        except ValidationError as e:
            messagebox.showerror("Error", str(e))

    def show_restaurants(self):
        self.clear_content()
        self.set_header_title("Restaurant Management")
        self.set_active_menu(2)
        f = self.content_frame
        restaurants = self.ctrl.get_all_restaurants()
        if not restaurants:
            EmptyState(f, "🍽️", "No restaurants").pack(padx=20, pady=40, fill=tk.X)
            return
        for r in restaurants:
            row = tk.Frame(f, bg=COLORS['white'], padx=15, pady=10,
                highlightbackground=COLORS['border'], highlightthickness=1)
            row.pack(fill=tk.X, padx=20, pady=3)
            status_icon = "🟢" if r['is_active'] else "🔴"
            tk.Label(row, text=f"{status_icon} {r['name']}", font=FONTS['body_bold'],
                fg=COLORS['text_primary'], bg=COLORS['white']).pack(side=tk.LEFT)
            ttext = "Deactivate" if r['is_active'] else "Activate"
            tcolor = COLORS['danger'] if r['is_active'] else COLORS['success']
            tb = tk.Label(row, text=ttext, font=FONTS['badge'], fg=COLORS['white'],
                bg=tcolor, padx=8, pady=2, cursor='hand2')
            tb.pack(side=tk.RIGHT, padx=5)
            tb.bind('<Button-1>', lambda e, rid=r['id'], a=r['is_active']:
                (self.ctrl.toggle_restaurant_status(rid, not a), self.show_restaurants()))
            tk.Label(row, text=f"★ {r.get('avg_rating',0):.1f}", font=FONTS['body_bold'],
                fg=COLORS['star_filled'], bg=COLORS['white']).pack(side=tk.RIGHT, padx=10)
            tk.Label(row, text=f"📍 {r.get('location','')}", font=FONTS['body_sm'],
                fg=COLORS['text_secondary'], bg=COLORS['white']).pack(side=tk.RIGHT, padx=5)

    def show_orders(self):
        self.clear_content()
        self.set_header_title("All Orders")
        self.set_active_menu(3)
        f = self.content_frame
        orders = self.ctrl.get_all_orders()
        if not orders:
            EmptyState(f, "📦", "No orders").pack(padx=20, pady=40, fill=tk.X)
            return
        for o in orders:
            OrderCard(f, dict(o), show_customer=True).pack(fill=tk.X, padx=20, pady=4)

    def show_reviews(self):
        self.clear_content()
        self.set_header_title("Review Moderation")
        self.set_active_menu(4)
        f = self.content_frame
        reviews = self.ctrl.get_all_reviews()
        if not reviews:
            EmptyState(f, "⭐", "No reviews").pack(padx=20, pady=40, fill=tk.X)
            return
        for r in reviews:
            rf = tk.Frame(f, bg=COLORS['white'], padx=15, pady=10,
                highlightbackground=COLORS['border'], highlightthickness=1)
            rf.pack(fill=tk.X, padx=20, pady=3)
            top = tk.Frame(rf, bg=COLORS['white'])
            top.pack(fill=tk.X)
            tk.Label(top, text=f"👤 {r.get('reviewer_name','')} → 🍽️ {r.get('restaurant_name','')}",
                font=FONTS['body_bold'], fg=COLORS['text_primary'], bg=COLORS['white']).pack(side=tk.LEFT)
            db = tk.Label(top, text="Delete", font=FONTS['badge'], fg=COLORS['white'],
                bg=COLORS['danger'], padx=8, pady=2, cursor='hand2')
            db.pack(side=tk.RIGHT)
            db.bind('<Button-1>', lambda e, rid=r['id']: self._del_review(rid))
            StarRating(rf, rating=r['rating']).pack(anchor='w')
            if r.get('comment'):
                tk.Label(rf, text=r['comment'], font=FONTS['body'], fg=COLORS['text_secondary'],
                    bg=COLORS['white'], wraplength=500).pack(anchor='w', pady=3)

    def _del_review(self, rid):
        if messagebox.askyesno("Confirm", "Delete this review?"):
            self.ctrl.delete_review(rid)
            self.show_reviews()

    def show_tickets(self):
        self.clear_content()
        self.set_header_title("Support Tickets")
        self.set_active_menu(5)
        f = self.content_frame
        tickets = self.ctrl.get_all_tickets()
        if not tickets:
            EmptyState(f, "🎫", "No support tickets").pack(padx=20, pady=40, fill=tk.X)
            return
        for t in tickets:
            tf = tk.Frame(f, bg=COLORS['white'], padx=15, pady=10,
                highlightbackground=COLORS['border'], highlightthickness=1)
            tf.pack(fill=tk.X, padx=20, pady=3)
            top = tk.Frame(tf, bg=COLORS['white'])
            top.pack(fill=tk.X)
            tk.Label(top, text=t['subject'], font=FONTS['body_bold'],
                fg=COLORS['text_primary'], bg=COLORS['white']).pack(side=tk.LEFT)
            StatusBadge(top, t['status']).pack(side=tk.RIGHT)
            tk.Label(tf, text=f"By: {t.get('user_name','')} ({t.get('user_email','')})",
                font=FONTS['body_sm'], fg=COLORS['text_secondary'], bg=COLORS['white']).pack(anchor='w')
            tk.Label(tf, text=t['message'], font=FONTS['body'], fg=COLORS['text_secondary'],
                bg=COLORS['white'], wraplength=500).pack(anchor='w', pady=3)
            bf = tk.Frame(tf, bg=COLORS['white'])
            bf.pack(anchor='w', pady=(5,0))
            for s, c in [("In Progress", COLORS['warning']), ("Resolved", COLORS['success']),
                         ("Closed", COLORS['text_secondary'])]:
                b = tk.Label(bf, text=s, font=FONTS['badge'], fg=COLORS['white'],
                    bg=c, padx=8, pady=2, cursor='hand2')
                b.pack(side=tk.LEFT, padx=2)
                b.bind('<Button-1>', lambda e, tid=t['id'], st=s.lower().replace(' ','_'):
                    (self.ctrl.update_ticket_status(tid, st), self.show_tickets()))
