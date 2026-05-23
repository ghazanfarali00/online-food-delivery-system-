"""Customer views for the Online Food Delivery System."""
import tkinter as tk
from tkinter import ttk, messagebox
from config import COLORS, FONTS, CUISINE_TYPES, PAYMENT_METHODS
from views.base_view import BaseView
from views.components import (RestaurantCard, MenuItemCard, OrderCard,
    StatusBadge, StarRating, FormField, PrimaryButton, EmptyState, StatCard)
from utils.helpers import format_currency, format_datetime, get_star_display
from utils.exceptions import OrderError, ValidationError


class CustomerView(BaseView):
    """Main customer dashboard view."""
    def __init__(self, parent, user, controller, on_logout):
        self.ctrl = controller
        menu = [
            {'icon': '🍽️', 'label': 'Restaurants', 'command': self.show_restaurants},
            {'icon': '🛒', 'label': 'My Cart', 'command': self.show_cart},
            {'icon': '📦', 'label': 'My Orders', 'command': self.show_orders},
            {'icon': '🔔', 'label': 'Notifications', 'command': self.show_notifications},
            {'icon': '👤', 'label': 'Profile', 'command': self.show_profile},
            {'icon': '❓', 'label': 'Help & Support', 'command': self.show_support},
        ]
        super().__init__(parent, user, on_logout, menu)
        self.show_restaurants()

    def show_restaurants(self):
        self.clear_content()
        self.set_header_title("Browse Restaurants")
        self.set_active_menu(0)
        f = self.content_frame
        # Search bar
        sf = tk.Frame(f, bg=COLORS['white'], padx=15, pady=10)
        sf.pack(fill=tk.X, padx=20, pady=(15,5))
        tk.Label(sf, text="🔍", font=FONTS['icon'], bg=COLORS['white']).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        se = tk.Entry(sf, textvariable=self.search_var, font=FONTS['body'],
            bg=COLORS['bg_light'], relief='flat', width=30,
            highlightbackground=COLORS['border'], highlightthickness=1)
        se.pack(side=tk.LEFT, padx=10, ipady=6, ipadx=5)
        sb = tk.Label(sf, text="Search", font=FONTS['button'], fg=COLORS['white'],
            bg=COLORS['primary'], padx=15, pady=6, cursor='hand2')
        sb.pack(side=tk.LEFT)
        sb.bind('<Button-1>', lambda e: self._do_search())
        # Filter
        tk.Label(sf, text="  Cuisine:", font=FONTS['body'], bg=COLORS['white']).pack(side=tk.LEFT, padx=(15,5))
        self.cuisine_var = tk.StringVar(value="All")
        cb = ttk.Combobox(sf, textvariable=self.cuisine_var, values=["All"]+CUISINE_TYPES, state='readonly', width=12)
        cb.pack(side=tk.LEFT)
        cb.bind('<<ComboboxSelected>>', lambda e: self._do_search())
        # Restaurant list
        restaurants = self.ctrl.get_all_restaurants()
        self._show_restaurant_list(restaurants)

    def _do_search(self):
        q = self.search_var.get()
        c = self.cuisine_var.get()
        if c and c != "All":
            results = self.ctrl.filter_restaurants(cuisine_type=c)
        elif q:
            results = self.ctrl.search_restaurants(q)
        else:
            results = self.ctrl.get_all_restaurants()
        # Clear old list
        for w in self.content_frame.winfo_children()[1:]:
            w.destroy()
        self._show_restaurant_list(results)

    def _show_restaurant_list(self, restaurants):
        f = self.content_frame
        if not restaurants:
            EmptyState(f, "🍽️", "No restaurants found").pack(padx=20, pady=20, fill=tk.X)
            return
        for r in restaurants:
            card = RestaurantCard(f, dict(r), on_click=lambda rest: self.show_menu(rest))
            card.pack(fill=tk.X, padx=20, pady=5)

    def show_menu(self, restaurant):
        self.clear_content()
        self.set_header_title(f"Menu — {restaurant['name']}")
        f = self.content_frame
        rid = restaurant['id']
        # Back button
        back = tk.Label(f, text="← Back to Restaurants", font=FONTS['body_bold'],
            fg=COLORS['primary'], bg=COLORS['bg_light'], cursor='hand2')
        back.pack(anchor='w', padx=20, pady=10)
        back.bind('<Button-1>', lambda e: self.show_restaurants())
        # Restaurant header
        hdr = tk.Frame(f, bg=COLORS['white'], padx=20, pady=15)
        hdr.pack(fill=tk.X, padx=20, pady=(0,10))
        tk.Label(hdr, text=f"🍽️ {restaurant['name']}", font=FONTS['heading_lg'],
            fg=COLORS['text_primary'], bg=COLORS['white']).pack(anchor='w')
        tk.Label(hdr, text=restaurant.get('description',''), font=FONTS['body'],
            fg=COLORS['text_secondary'], bg=COLORS['white'], wraplength=600).pack(anchor='w', pady=5)
        info = tk.Frame(hdr, bg=COLORS['white'])
        info.pack(anchor='w')
        tk.Label(info, text=f"★ {restaurant.get('avg_rating',0):.1f}", font=FONTS['body_bold'],
            fg=COLORS['star_filled'], bg=COLORS['white']).pack(side=tk.LEFT, padx=(0,15))
        tk.Label(info, text=f"📍 {restaurant.get('location','')}", font=FONTS['body'],
            fg=COLORS['text_secondary'], bg=COLORS['white']).pack(side=tk.LEFT)
        # Menu items
        items = self.ctrl.get_restaurant_menu(rid)
        if not items:
            EmptyState(f, "📋", "No menu items available").pack(padx=20, pady=20, fill=tk.X)
            return
        for item in items:
            MenuItemCard(f, dict(item), on_add=lambda it, r=rid: self._add_to_cart(r, it)).pack(
                fill=tk.X, padx=20, pady=3)

    def _add_to_cart(self, rid, item):
        try:
            self.ctrl.add_to_cart(rid, item, 1)
            messagebox.showinfo("Added", f"{item['name']} added to cart!")
        except (OrderError, ValidationError) as e:
            messagebox.showerror("Error", str(e))

    def show_cart(self):
        self.clear_content()
        self.set_header_title("My Cart")
        self.set_active_menu(1)
        f = self.content_frame
        items = self.ctrl.get_cart_items()
        if not items:
            EmptyState(f, "🛒", "Your cart is empty", "Browse restaurants to add items").pack(padx=20, pady=40, fill=tk.X)
            return
        for ci in items:
            row = tk.Frame(f, bg=COLORS['white'], padx=15, pady=10,
                highlightbackground=COLORS['border'], highlightthickness=1)
            row.pack(fill=tk.X, padx=20, pady=3)
            tk.Label(row, text=ci['item']['name'], font=FONTS['body_bold'],
                fg=COLORS['text_primary'], bg=COLORS['white']).pack(side=tk.LEFT)
            # Remove btn
            rb = tk.Label(row, text="✕", font=FONTS['body_bold'], fg=COLORS['danger'],
                bg=COLORS['white'], cursor='hand2', padx=5)
            rb.pack(side=tk.RIGHT)
            rb.bind('<Button-1>', lambda e, r=ci['restaurant_id'], i=ci['item']['id']: self._remove_item(r,i))
            tk.Label(row, text=format_currency(ci['subtotal']), font=FONTS['body_bold'],
                fg=COLORS['primary'], bg=COLORS['white']).pack(side=tk.RIGHT, padx=15)
            tk.Label(row, text=f"Qty: {ci['quantity']}", font=FONTS['body'],
                fg=COLORS['text_secondary'], bg=COLORS['white']).pack(side=tk.RIGHT, padx=10)
            tk.Label(row, text=f"× {format_currency(ci['item']['price'])}", font=FONTS['body'],
                fg=COLORS['text_secondary'], bg=COLORS['white']).pack(side=tk.RIGHT)
        # Total + checkout
        tf = tk.Frame(f, bg=COLORS['white'], padx=20, pady=15)
        tf.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(tf, text="Total:", font=FONTS['heading_md'], fg=COLORS['text_primary'],
            bg=COLORS['white']).pack(side=tk.LEFT)
        tk.Label(tf, text=format_currency(self.ctrl.get_cart_total()), font=FONTS['heading_md'],
            fg=COLORS['primary'], bg=COLORS['white']).pack(side=tk.LEFT, padx=10)
        bf = tk.Frame(f, bg=COLORS['bg_light'])
        bf.pack(fill=tk.X, padx=20, pady=5)
        cb = tk.Label(bf, text="🗑 Clear Cart", font=FONTS['button'], fg=COLORS['white'],
            bg=COLORS['danger'], padx=15, pady=8, cursor='hand2')
        cb.pack(side=tk.LEFT, padx=(0,10))
        cb.bind('<Button-1>', lambda e: (self.ctrl.clear_cart(), self.show_cart()))
        PrimaryButton(bf, "🛵 Checkout", self._show_checkout).pack(side=tk.LEFT)

    def _remove_item(self, rid, iid):
        self.ctrl.remove_from_cart(rid, iid)
        self.show_cart()

    def _show_checkout(self):
        self.clear_content()
        self.set_header_title("Checkout")
        f = self.content_frame
        cf = tk.Frame(f, bg=COLORS['white'], padx=30, pady=20)
        cf.pack(fill=tk.X, padx=20, pady=15)
        tk.Label(cf, text="Delivery Address", font=FONTS['heading_sm'],
            fg=COLORS['text_primary'], bg=COLORS['white']).pack(anchor='w', pady=(0,5))
        # Load saved addresses
        addrs = self.ctrl.get_addresses()
        self.addr_var = tk.StringVar()
        if addrs:
            addr_list = [f"{a['label']}: {a['address_line']}, {a['city']}" for a in addrs]
            self.addr_var.set(addr_list[0])
            ttk.Combobox(cf, textvariable=self.addr_var, values=addr_list,
                state='readonly', font=FONTS['body'], width=50).pack(fill=tk.X, pady=5)
        tk.Label(cf, text="Or enter new address:", font=FONTS['body'],
            fg=COLORS['text_secondary'], bg=COLORS['white']).pack(anchor='w', pady=(10,3))
        self.new_addr = FormField(cf, "Address", field_type="text")
        self.new_addr.pack(fill=tk.X, pady=5)
        tk.Label(cf, text="Payment Method", font=FONTS['heading_sm'],
            fg=COLORS['text_primary'], bg=COLORS['white']).pack(anchor='w', pady=(15,5))
        self.pay_var = tk.StringVar(value="cod")
        for k, v in PAYMENT_METHODS.items():
            tk.Radiobutton(cf, text=v, variable=self.pay_var, value=k,
                font=FONTS['body'], bg=COLORS['white'], activebackground=COLORS['white']).pack(anchor='w')
        tk.Label(cf, text=f"Total: {format_currency(self.ctrl.get_cart_total())}",
            font=FONTS['heading_md'], fg=COLORS['primary'], bg=COLORS['white']).pack(anchor='w', pady=15)
        PrimaryButton(cf, "Place Order", self._place_order).pack(anchor='w')

    def _place_order(self):
        addr = self.new_addr.get() if self.new_addr.get() else self.addr_var.get()
        try:
            uid = self.ctrl.place_order(self.pay_var.get(), addr)
            messagebox.showinfo("Order Placed!", f"Order {uid} placed successfully!")
            self.show_orders()
        except (OrderError, ValidationError) as e:
            messagebox.showerror("Error", str(e))

    def show_orders(self):
        self.clear_content()
        self.set_header_title("My Orders")
        self.set_active_menu(2)
        f = self.content_frame
        orders = self.ctrl.get_my_orders()
        if not orders:
            EmptyState(f, "📦", "No orders yet").pack(padx=20, pady=40, fill=tk.X)
            return
        for o in orders:
            OrderCard(f, dict(o), on_click=lambda od: self._show_order_detail(od)).pack(
                fill=tk.X, padx=20, pady=4)

    def _show_order_detail(self, order):
        self.clear_content()
        self.set_header_title(f"Order {order['order_uid']}")
        f = self.content_frame
        back = tk.Label(f, text="← Back to Orders", font=FONTS['body_bold'],
            fg=COLORS['primary'], bg=COLORS['bg_light'], cursor='hand2')
        back.pack(anchor='w', padx=20, pady=10)
        back.bind('<Button-1>', lambda e: self.show_orders())
        d = tk.Frame(f, bg=COLORS['white'], padx=20, pady=15)
        d.pack(fill=tk.X, padx=20, pady=5)
        top = tk.Frame(d, bg=COLORS['white'])
        top.pack(fill=tk.X)
        tk.Label(top, text=order['order_uid'], font=FONTS['heading_md'],
            fg=COLORS['text_primary'], bg=COLORS['white']).pack(side=tk.LEFT)
        StatusBadge(top, order['status']).pack(side=tk.RIGHT)
        tk.Label(d, text=f"🍽️ {order.get('restaurant_name','')}", font=FONTS['body'],
            fg=COLORS['text_secondary'], bg=COLORS['white']).pack(anchor='w', pady=3)
        tk.Label(d, text=f"💰 {format_currency(order['total_amount'])}", font=FONTS['heading_sm'],
            fg=COLORS['primary'], bg=COLORS['white']).pack(anchor='w', pady=3)
        tk.Label(d, text=f"📅 {format_datetime(order.get('created_at',''))}", font=FONTS['body_sm'],
            fg=COLORS['text_muted'], bg=COLORS['white']).pack(anchor='w')
        tk.Label(d, text=f"Payment: {PAYMENT_METHODS.get(order.get('payment_method',''), order.get('payment_method',''))}",
            font=FONTS['body'], fg=COLORS['text_secondary'], bg=COLORS['white']).pack(anchor='w', pady=3)
        # Items
        try:
            _, items = self.ctrl.get_order_details(order['order_uid'])
            if items:
                tk.Label(d, text="Order Items:", font=FONTS['body_bold'],
                    fg=COLORS['text_primary'], bg=COLORS['white']).pack(anchor='w', pady=(10,5))
                for it in items:
                    tk.Label(d, text=f"  • {it['item_name']} × {it['quantity']} = {format_currency(it['subtotal'])}",
                        font=FONTS['body'], fg=COLORS['text_secondary'], bg=COLORS['white']).pack(anchor='w')
        except Exception:
            pass
        # Cancel / Review buttons
        bf = tk.Frame(d, bg=COLORS['white'])
        bf.pack(anchor='w', pady=(15,0))
        if order['status'] == 'placed':
            cb = tk.Label(bf, text="Cancel Order", font=FONTS['button'], fg=COLORS['white'],
                bg=COLORS['danger'], padx=15, pady=6, cursor='hand2')
            cb.pack(side=tk.LEFT, padx=(0,10))
            cb.bind('<Button-1>', lambda e, oid=order['id']: self._cancel(oid))
        if order['status'] == 'delivered':
            rb = tk.Label(bf, text="⭐ Leave Review", font=FONTS['button'], fg=COLORS['white'],
                bg=COLORS['primary'], padx=15, pady=6, cursor='hand2')
            rb.pack(side=tk.LEFT)
            rb.bind('<Button-1>', lambda e, o=order: self._show_review(o))

    def _cancel(self, oid):
        if messagebox.askyesno("Confirm", "Cancel this order?"):
            try:
                self.ctrl.cancel_order(oid)
                messagebox.showinfo("Cancelled", "Order cancelled.")
                self.show_orders()
            except OrderError as e:
                messagebox.showerror("Error", str(e))

    def _show_review(self, order):
        self.clear_content()
        self.set_header_title("Leave a Review")
        f = self.content_frame
        rf = tk.Frame(f, bg=COLORS['white'], padx=30, pady=20)
        rf.pack(fill=tk.X, padx=20, pady=15)
        tk.Label(rf, text=f"Review for {order.get('restaurant_name','')}", font=FONTS['heading_sm'],
            fg=COLORS['text_primary'], bg=COLORS['white']).pack(anchor='w', pady=(0,10))
        tk.Label(rf, text="Rating:", font=FONTS['body_bold'], bg=COLORS['white']).pack(anchor='w')
        self.review_rating = StarRating(rf, interactive=True)
        self.review_rating.pack(anchor='w', pady=5)
        self.review_comment = FormField(rf, "Comment (optional)", field_type="text")
        self.review_comment.pack(fill=tk.X, pady=10)
        PrimaryButton(rf, "Submit Review",
            lambda: self._submit_review(order)).pack(anchor='w')

    def _submit_review(self, order):
        try:
            r = self.review_rating.get_rating()
            if r == 0:
                messagebox.showwarning("Warning", "Please select a rating")
                return
            self.ctrl.add_review(order['restaurant_id'], r, self.review_comment.get(), order['id'])
            messagebox.showinfo("Thanks!", "Review submitted!")
            self.show_orders()
        except (ValidationError, Exception) as e:
            messagebox.showerror("Error", str(e))

    def show_notifications(self):
        self.clear_content()
        self.set_header_title("Notifications")
        self.set_active_menu(3)
        f = self.content_frame
        notifs = self.ctrl.get_notifications()
        if notifs:
            mb = tk.Label(f, text="Mark All Read", font=FONTS['body_bold'], fg=COLORS['primary'],
                bg=COLORS['bg_light'], cursor='hand2')
            mb.pack(anchor='e', padx=20, pady=10)
            mb.bind('<Button-1>', lambda e: (self.ctrl.mark_all_notifications_read(), self.show_notifications()))
        if not notifs:
            EmptyState(f, "🔔", "No notifications").pack(padx=20, pady=40, fill=tk.X)
            return
        for n in notifs:
            bg = COLORS['white'] if n['is_read'] else COLORS['primary_bg']
            nf = tk.Frame(f, bg=bg, padx=15, pady=10, highlightbackground=COLORS['border'], highlightthickness=1)
            nf.pack(fill=tk.X, padx=20, pady=3)
            tk.Label(nf, text=n['title'], font=FONTS['body_bold'], fg=COLORS['text_primary'], bg=bg).pack(anchor='w')
            tk.Label(nf, text=n['message'], font=FONTS['body'], fg=COLORS['text_secondary'], bg=bg, wraplength=500).pack(anchor='w')
            tk.Label(nf, text=format_datetime(n.get('created_at','')), font=FONTS['caption'], fg=COLORS['text_muted'], bg=bg).pack(anchor='w')
            if not n['is_read']:
                nf.bind('<Button-1>', lambda e, nid=n['id']: (self.ctrl.mark_notification_read(nid), self.show_notifications()))

    def show_profile(self):
        self.clear_content()
        self.set_header_title("My Profile")
        self.set_active_menu(4)
        f = self.content_frame
        pf = tk.Frame(f, bg=COLORS['white'], padx=30, pady=20)
        pf.pack(fill=tk.X, padx=20, pady=15)
        tk.Label(pf, text="Profile Details", font=FONTS['heading_sm'],
            fg=COLORS['text_primary'], bg=COLORS['white']).pack(anchor='w', pady=(0,10))
        self.profile_name = FormField(pf, "Name")
        self.profile_name.pack(fill=tk.X, pady=5)
        self.profile_name.set(self.user.get('name',''))
        self.profile_phone = FormField(pf, "Phone")
        self.profile_phone.pack(fill=tk.X, pady=5)
        self.profile_phone.set(self.user.get('phone',''))
        tk.Label(pf, text=f"Email: {self.user.get('email','')}", font=FONTS['body'],
            fg=COLORS['text_secondary'], bg=COLORS['white']).pack(anchor='w', pady=5)
        PrimaryButton(pf, "Update Profile", self._update_profile).pack(anchor='w', pady=10)
        # Addresses section
        af = tk.Frame(f, bg=COLORS['white'], padx=30, pady=20)
        af.pack(fill=tk.X, padx=20, pady=10)
        tk.Label(af, text="Delivery Addresses", font=FONTS['heading_sm'],
            fg=COLORS['text_primary'], bg=COLORS['white']).pack(anchor='w', pady=(0,10))
        addrs = self.ctrl.get_addresses()
        for a in addrs:
            row = tk.Frame(af, bg=COLORS['bg_light'], padx=10, pady=5)
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=f"📍 {a['label']}: {a['address_line']}, {a['city']}",
                font=FONTS['body'], fg=COLORS['text_primary'], bg=COLORS['bg_light']).pack(side=tk.LEFT)
            db = tk.Label(row, text="✕", font=FONTS['body_bold'], fg=COLORS['danger'],
                bg=COLORS['bg_light'], cursor='hand2')
            db.pack(side=tk.RIGHT)
            db.bind('<Button-1>', lambda e, aid=a['id']: (self.ctrl.delete_address(aid), self.show_profile()))
        # Add address
        tk.Label(af, text="Add New Address", font=FONTS['body_bold'],
            fg=COLORS['text_primary'], bg=COLORS['white']).pack(anchor='w', pady=(15,5))
        self.addr_label = FormField(af, "Label (e.g. Home)")
        self.addr_label.pack(fill=tk.X, pady=3)
        self.addr_line = FormField(af, "Address")
        self.addr_line.pack(fill=tk.X, pady=3)
        self.addr_city = FormField(af, "City")
        self.addr_city.pack(fill=tk.X, pady=3)
        PrimaryButton(af, "Add Address", self._add_address).pack(anchor='w', pady=10)

    def _update_profile(self):
        try:
            self.ctrl.update_profile(self.profile_name.get(), self.profile_phone.get())
            self.user['name'] = self.profile_name.get()
            messagebox.showinfo("Success", "Profile updated!")
        except ValidationError as e:
            messagebox.showerror("Error", str(e))

    def _add_address(self):
        try:
            self.ctrl.add_address(self.addr_label.get(), self.addr_line.get(), self.addr_city.get())
            messagebox.showinfo("Success", "Address added!")
            self.show_profile()
        except ValidationError as e:
            messagebox.showerror("Error", str(e))

    def show_support(self):
        self.clear_content()
        self.set_header_title("Help & Support")
        self.set_active_menu(5)
        f = self.content_frame
        # FAQ
        faq_f = tk.Frame(f, bg=COLORS['white'], padx=20, pady=15)
        faq_f.pack(fill=tk.X, padx=20, pady=15)
        tk.Label(faq_f, text="Frequently Asked Questions", font=FONTS['heading_sm'],
            fg=COLORS['text_primary'], bg=COLORS['white']).pack(anchor='w', pady=(0,10))
        faqs = [("How to place an order?", "Browse restaurants, add items to cart, and checkout."),
                ("How to track my order?", "Go to My Orders and click on any order."),
                ("How to cancel an order?", "Orders can be cancelled if status is 'Placed'."),
                ("Payment methods?", "We support Cash on Delivery, Card, and Digital Wallet.")]
        for q, a in faqs:
            tk.Label(faq_f, text=f"Q: {q}", font=FONTS['body_bold'], fg=COLORS['text_primary'],
                bg=COLORS['white'], anchor='w').pack(fill=tk.X, pady=(5,0))
            tk.Label(faq_f, text=f"A: {a}", font=FONTS['body'], fg=COLORS['text_secondary'],
                bg=COLORS['white'], anchor='w').pack(fill=tk.X, pady=(0,5))
        # Submit ticket
        tf = tk.Frame(f, bg=COLORS['white'], padx=20, pady=15)
        tf.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(tf, text="Submit a Support Ticket", font=FONTS['heading_sm'],
            fg=COLORS['text_primary'], bg=COLORS['white']).pack(anchor='w', pady=(0,10))
        self.ticket_subject = FormField(tf, "Subject")
        self.ticket_subject.pack(fill=tk.X, pady=3)
        self.ticket_message = FormField(tf, "Message", field_type="text")
        self.ticket_message.pack(fill=tk.X, pady=3)
        PrimaryButton(tf, "Submit Ticket", self._submit_ticket).pack(anchor='w', pady=10)
        # My tickets
        tickets = self.ctrl.get_my_tickets()
        if tickets:
            tk.Label(tf, text="Your Tickets:", font=FONTS['body_bold'],
                fg=COLORS['text_primary'], bg=COLORS['white']).pack(anchor='w', pady=(10,5))
            for t in tickets:
                row = tk.Frame(tf, bg=COLORS['bg_light'], padx=10, pady=5)
                row.pack(fill=tk.X, pady=2)
                tk.Label(row, text=t['subject'], font=FONTS['body_bold'],
                    fg=COLORS['text_primary'], bg=COLORS['bg_light']).pack(side=tk.LEFT)
                StatusBadge(row, t['status']).pack(side=tk.RIGHT)

    def _submit_ticket(self):
        try:
            self.ctrl.submit_ticket(self.ticket_subject.get(), self.ticket_message.get())
            messagebox.showinfo("Submitted", "Support ticket created!")
            self.show_support()
        except ValidationError as e:
            messagebox.showerror("Error", str(e))
