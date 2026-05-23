"""Delivery views for the Online Food Delivery System."""
import tkinter as tk
from tkinter import messagebox
from config import COLORS, FONTS
from views.base_view import BaseView
from views.components import (StatCard, OrderCard, StatusBadge, EmptyState, PrimaryButton)
from utils.helpers import format_currency, format_datetime
from utils.exceptions import OrderError


class DeliveryView(BaseView):
    """Delivery person dashboard view."""
    def __init__(self, parent, user, controller, on_logout):
        self.ctrl = controller
        menu = [
            {'icon': '📊', 'label': 'Dashboard', 'command': self.show_dashboard},
            {'icon': '📋', 'label': 'Available Orders', 'command': self.show_available},
            {'icon': '🚗', 'label': 'My Deliveries', 'command': self.show_deliveries},
            {'icon': '✅', 'label': 'Completed', 'command': self.show_completed},
            {'icon': '🔔', 'label': 'Notifications', 'command': self.show_notifications},
        ]
        super().__init__(parent, user, on_logout, menu)
        self.show_dashboard()

    def show_dashboard(self):
        self.clear_content()
        self.set_header_title("Delivery Dashboard")
        self.set_active_menu(0)
        f = self.content_frame
        stats = self.ctrl.get_delivery_stats()
        cf = tk.Frame(f, bg=COLORS['bg_light'])
        cf.pack(fill=tk.X, padx=20, pady=15)
        cards = [
            ("Total Deliveries", stats['total'], "📦", COLORS['primary']),
            ("Active", stats['active'], "🚗", COLORS['warning']),
            ("Completed", stats['completed'], "✅", COLORS['success']),
        ]
        for i, (t, v, ic, c) in enumerate(cards):
            StatCard(cf, t, v, ic, c).grid(row=0, column=i, padx=8, sticky='ew')
            cf.columnconfigure(i, weight=1)
        # Active deliveries
        active = self.ctrl.get_active_deliveries()
        tk.Label(f, text="Active Deliveries", font=FONTS['heading_sm'],
            fg=COLORS['text_primary'], bg=COLORS['bg_light']).pack(anchor='w', padx=20, pady=(15,5))
        if not active:
            EmptyState(f, "🚗", "No active deliveries").pack(padx=20, fill=tk.X)
        else:
            for o in active:
                self._render_delivery_card(f, dict(o), show_actions=True)

    def show_available(self):
        self.clear_content()
        self.set_header_title("Available Orders")
        self.set_active_menu(1)
        f = self.content_frame
        orders = self.ctrl.get_available_orders()
        if not orders:
            EmptyState(f, "📋", "No orders available", "Check back later!").pack(padx=20, pady=40, fill=tk.X)
            return
        for o in orders:
            card = tk.Frame(f, bg=COLORS['white'], padx=15, pady=12,
                highlightbackground=COLORS['border'], highlightthickness=1)
            card.pack(fill=tk.X, padx=20, pady=4)
            top = tk.Frame(card, bg=COLORS['white'])
            top.pack(fill=tk.X)
            tk.Label(top, text=f"🧾 {o['order_uid']}", font=FONTS['body_bold'],
                fg=COLORS['text_primary'], bg=COLORS['white']).pack(side=tk.LEFT)
            StatusBadge(top, o['status']).pack(side=tk.RIGHT)
            tk.Label(card, text=f"🍽️ {o.get('restaurant_name','')} | 📍 {o.get('restaurant_location','')}",
                font=FONTS['body'], fg=COLORS['text_secondary'], bg=COLORS['white']).pack(anchor='w', pady=2)
            tk.Label(card, text=f"👤 {o.get('customer_name','')} | 💰 {format_currency(o['total_amount'])}",
                font=FONTS['body'], fg=COLORS['text_secondary'], bg=COLORS['white']).pack(anchor='w')
            if o.get('delivery_address'):
                tk.Label(card, text=f"📍 Deliver to: {o['delivery_address']}", font=FONTS['body_sm'],
                    fg=COLORS['text_muted'], bg=COLORS['white']).pack(anchor='w', pady=2)
            ab = tk.Label(card, text="✅ Accept Order", font=FONTS['button'], fg=COLORS['white'],
                bg=COLORS['success'], padx=15, pady=6, cursor='hand2')
            ab.pack(anchor='w', pady=(8,0))
            ab.bind('<Button-1>', lambda e, oid=o['id']: self._accept(oid))

    def _accept(self, oid):
        try:
            self.ctrl.accept_order(oid)
            messagebox.showinfo("Accepted", "Order accepted!")
            self.show_deliveries()
        except OrderError as e:
            messagebox.showerror("Error", str(e))

    def show_deliveries(self):
        self.clear_content()
        self.set_header_title("My Deliveries")
        self.set_active_menu(2)
        f = self.content_frame
        deliveries = self.ctrl.get_active_deliveries()
        if not deliveries:
            EmptyState(f, "🚗", "No active deliveries").pack(padx=20, pady=40, fill=tk.X)
            return
        for o in deliveries:
            self._render_delivery_card(f, dict(o), show_actions=True)

    def _render_delivery_card(self, parent, order, show_actions=False):
        card = tk.Frame(parent, bg=COLORS['white'], padx=15, pady=12,
            highlightbackground=COLORS['border'], highlightthickness=1)
        card.pack(fill=tk.X, padx=20, pady=4)
        top = tk.Frame(card, bg=COLORS['white'])
        top.pack(fill=tk.X)
        tk.Label(top, text=f"🧾 {order['order_uid']}", font=FONTS['body_bold'],
            fg=COLORS['text_primary'], bg=COLORS['white']).pack(side=tk.LEFT)
        StatusBadge(top, order['status']).pack(side=tk.RIGHT)
        tk.Label(card, text=f"🍽️ {order.get('restaurant_name','')}", font=FONTS['body'],
            fg=COLORS['text_secondary'], bg=COLORS['white']).pack(anchor='w', pady=2)
        tk.Label(card, text=f"👤 {order.get('customer_name','')} | 📞 {order.get('customer_phone','')}",
            font=FONTS['body_sm'], fg=COLORS['text_secondary'], bg=COLORS['white']).pack(anchor='w')
        tk.Label(card, text=f"💰 {format_currency(order['total_amount'])}",
            font=FONTS['body_bold'], fg=COLORS['primary'], bg=COLORS['white']).pack(anchor='w', pady=2)
        if order.get('delivery_address'):
            tk.Label(card, text=f"📍 {order['delivery_address']}", font=FONTS['body_sm'],
                fg=COLORS['text_muted'], bg=COLORS['white']).pack(anchor='w')
        if show_actions:
            bf = tk.Frame(card, bg=COLORS['white'])
            bf.pack(anchor='w', pady=(8,0))
            if order['status'] in ('placed', 'preparing'):
                b = tk.Label(bf, text="🚗 Out for Delivery", font=FONTS['button'], fg=COLORS['white'],
                    bg=COLORS['warning'], padx=12, pady=5, cursor='hand2')
                b.pack(side=tk.LEFT, padx=(0,8))
                b.bind('<Button-1>', lambda e, oid=order['id']: self._update(oid, 'out_for_delivery'))
            elif order['status'] == 'out_for_delivery':
                b = tk.Label(bf, text="✅ Mark Delivered", font=FONTS['button'], fg=COLORS['white'],
                    bg=COLORS['success'], padx=12, pady=5, cursor='hand2')
                b.pack(side=tk.LEFT)
                b.bind('<Button-1>', lambda e, oid=order['id']: self._update(oid, 'delivered'))

    def _update(self, oid, status):
        try:
            self.ctrl.update_delivery_status(oid, status)
            if status == 'delivered':
                messagebox.showinfo("Done", "Order delivered!")
            self.show_deliveries()
        except OrderError as e:
            messagebox.showerror("Error", str(e))

    def show_completed(self):
        self.clear_content()
        self.set_header_title("Completed Deliveries")
        self.set_active_menu(3)
        f = self.content_frame
        completed = self.ctrl.get_completed_deliveries()
        if not completed:
            EmptyState(f, "✅", "No completed deliveries yet").pack(padx=20, pady=40, fill=tk.X)
            return
        for o in completed:
            self._render_delivery_card(f, dict(o), show_actions=False)

    def show_notifications(self):
        self.clear_content()
        self.set_header_title("Notifications")
        self.set_active_menu(4)
        f = self.content_frame
        notifs = self.ctrl.get_notifications()
        if not notifs:
            EmptyState(f, "🔔", "No notifications").pack(padx=20, pady=40, fill=tk.X)
            return
        for n in notifs:
            bg = COLORS['white'] if n['is_read'] else COLORS['primary_bg']
            nf = tk.Frame(f, bg=bg, padx=15, pady=10,
                highlightbackground=COLORS['border'], highlightthickness=1)
            nf.pack(fill=tk.X, padx=20, pady=3)
            tk.Label(nf, text=n['title'], font=FONTS['body_bold'],
                fg=COLORS['text_primary'], bg=bg).pack(anchor='w')
            tk.Label(nf, text=n['message'], font=FONTS['body'],
                fg=COLORS['text_secondary'], bg=bg).pack(anchor='w')
            tk.Label(nf, text=format_datetime(n.get('created_at','')),
                font=FONTS['caption'], fg=COLORS['text_muted'], bg=bg).pack(anchor='w')
