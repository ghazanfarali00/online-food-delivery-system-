"""
Authentication views for the Online Food Delivery System.
Provides login, registration, and password reset screens.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from config import COLORS, FONTS, ROLES, SECURITY_QUESTIONS
from views.components import FormField, PrimaryButton
from utils.exceptions import AuthenticationError, ValidationError


class AuthView(tk.Frame):
    """Container for authentication screens (Login/Register/Reset)."""

    def __init__(self, parent, auth_controller, on_login_success):
        """
        Initialize auth view.

        Args:
            parent: Parent widget.
            auth_controller: Authentication controller instance.
            on_login_success (callable): Called with user data on successful login.
        """
        super().__init__(parent, bg=COLORS['bg_light'])
        self.parent = parent
        self.auth = auth_controller
        self.on_login_success = on_login_success
        self.pack(fill=tk.BOTH, expand=True)
        self.show_login()

    def _clear(self):
        """Clear all widgets."""
        for w in self.winfo_children():
            w.destroy()

    def show_login(self):
        """Display the login screen."""
        self._clear()

        # Split layout: left branding, right form
        left = tk.Frame(self, bg=COLORS['primary'], width=450)
        left.pack(side=tk.LEFT, fill=tk.Y)
        left.pack_propagate(False)

        # Branding
        brand_container = tk.Frame(left, bg=COLORS['primary'])
        brand_container.place(relx=0.5, rely=0.5, anchor='center')

        tk.Label(
            brand_container, text="🍔",
            font=("Segoe UI", 60), bg=COLORS['primary']
        ).pack()

        tk.Label(
            brand_container, text="FoodExpress",
            font=("Segoe UI", 32, "bold"), fg=COLORS['white'],
            bg=COLORS['primary']
        ).pack(pady=(10, 5))

        tk.Label(
            brand_container, text="Delivering happiness to your doorstep",
            font=FONTS['body_lg'], fg=COLORS['primary_light'],
            bg=COLORS['primary']
        ).pack()

        tk.Label(
            brand_container, text="━━━━━━━━━━━━━",
            font=FONTS['body'], fg=COLORS['primary_light'],
            bg=COLORS['primary']
        ).pack(pady=15)

        features = ["🚀 Fast Delivery", "🍕 Best Restaurants", "💰 Great Deals"]
        for feat in features:
            tk.Label(
                brand_container, text=feat,
                font=FONTS['body_lg'], fg=COLORS['white'],
                bg=COLORS['primary']
            ).pack(pady=3)

        # Right: Login form
        right = tk.Frame(self, bg=COLORS['white'])
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        form_container = tk.Frame(right, bg=COLORS['white'])
        form_container.place(relx=0.5, rely=0.5, anchor='center')

        tk.Label(
            form_container, text="Welcome Back",
            font=FONTS['heading_xl'], fg=COLORS['text_primary'],
            bg=COLORS['white']
        ).pack(anchor='w')

        tk.Label(
            form_container, text="Sign in to your account",
            font=FONTS['body_lg'], fg=COLORS['text_secondary'],
            bg=COLORS['white']
        ).pack(anchor='w', pady=(5, 25))

        # Email
        self.login_email = FormField(form_container, "Email Address")
        self.login_email.pack(fill=tk.X, pady=(0, 12))
        self.login_email.input.config(width=35)

        # Password
        self.login_password = FormField(form_container, "Password",
                                         field_type="password")
        self.login_password.pack(fill=tk.X, pady=(0, 5))

        # Forgot password link
        forgot = tk.Label(
            form_container, text="Forgot Password?",
            font=FONTS['body_sm'], fg=COLORS['primary'],
            bg=COLORS['white'], cursor='hand2'
        )
        forgot.pack(anchor='e', pady=(0, 20))
        forgot.bind('<Button-1>', lambda e: self.show_forgot_password())

        # Login button
        PrimaryButton(
            form_container, "Sign In", self._handle_login
        ).pack(fill=tk.X, pady=(0, 15))

        # Register link
        reg_frame = tk.Frame(form_container, bg=COLORS['white'])
        reg_frame.pack()

        tk.Label(
            reg_frame, text="Don't have an account? ",
            font=FONTS['body'], fg=COLORS['text_secondary'],
            bg=COLORS['white']
        ).pack(side=tk.LEFT)

        reg_link = tk.Label(
            reg_frame, text="Sign Up",
            font=FONTS['body_bold'], fg=COLORS['primary'],
            bg=COLORS['white'], cursor='hand2'
        )
        reg_link.pack(side=tk.LEFT)
        reg_link.bind('<Button-1>', lambda e: self.show_register())

        # Demo credentials
        demo_frame = tk.Frame(form_container, bg=COLORS['bg_light'],
                              padx=15, pady=10)
        demo_frame.pack(fill=tk.X, pady=(20, 0))

        tk.Label(
            demo_frame, text="Demo Accounts:",
            font=FONTS['body_bold'], fg=COLORS['text_primary'],
            bg=COLORS['bg_light']
        ).pack(anchor='w')

        demos = [
            ("Admin", "admin@foodexpress.com", "admin123"),
            ("Customer", "sara@gmail.com", "customer123"),
            ("Vendor", "ali@kitchen.com", "vendor123"),
            ("Delivery", "ahmed@rider.com", "delivery123"),
        ]
        for role, email, pwd in demos:
            row = tk.Frame(demo_frame, bg=COLORS['bg_light'])
            row.pack(fill=tk.X, pady=1)
            tk.Label(
                row, text=f"{role}: {email} / {pwd}",
                font=FONTS['caption'], fg=COLORS['text_secondary'],
                bg=COLORS['bg_light'], anchor='w'
            ).pack(side=tk.LEFT)

    def _handle_login(self):
        """Handle login button click."""
        email = self.login_email.get()
        password = self.login_password.get()
        try:
            user = self.auth.login(email, password)
            self.on_login_success(user)
        except (AuthenticationError, ValidationError) as e:
            messagebox.showerror("Login Failed", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def show_register(self):
        """Display the registration screen."""
        self._clear()

        # Left branding (smaller)
        left = tk.Frame(self, bg=COLORS['primary'], width=350)
        left.pack(side=tk.LEFT, fill=tk.Y)
        left.pack_propagate(False)

        brand_container = tk.Frame(left, bg=COLORS['primary'])
        brand_container.place(relx=0.5, rely=0.5, anchor='center')

        tk.Label(
            brand_container, text="🍔",
            font=("Segoe UI", 50), bg=COLORS['primary']
        ).pack()

        tk.Label(
            brand_container, text="FoodExpress",
            font=("Segoe UI", 28, "bold"), fg=COLORS['white'],
            bg=COLORS['primary']
        ).pack(pady=(10, 5))

        tk.Label(
            brand_container, text="Join thousands of\nhappy food lovers!",
            font=FONTS['body_lg'], fg=COLORS['primary_light'],
            bg=COLORS['primary'], justify='center'
        ).pack(pady=10)

        # Right: Registration form (scrollable)
        right = tk.Frame(self, bg=COLORS['white'])
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(right, bg=COLORS['white'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(right, orient=tk.VERTICAL, command=canvas.yview)
        form_outer = tk.Frame(canvas, bg=COLORS['white'])
        form_outer.bind('<Configure>', lambda e: canvas.configure(
            scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=form_outer, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(fill=tk.BOTH, expand=True)
        canvas.bind('<Configure>',
                    lambda e: canvas.itemconfig(canvas.find_all()[0], width=e.width))

        form_container = tk.Frame(form_outer, bg=COLORS['white'], padx=50, pady=30)
        form_container.pack(fill=tk.X)

        tk.Label(
            form_container, text="Create Account",
            font=FONTS['heading_xl'], fg=COLORS['text_primary'],
            bg=COLORS['white']
        ).pack(anchor='w')

        tk.Label(
            form_container, text="Fill in your details to get started",
            font=FONTS['body_lg'], fg=COLORS['text_secondary'],
            bg=COLORS['white']
        ).pack(anchor='w', pady=(5, 20))

        # Form fields
        self.reg_name = FormField(form_container, "Full Name")
        self.reg_name.pack(fill=tk.X, pady=(0, 10))

        self.reg_email = FormField(form_container, "Email Address")
        self.reg_email.pack(fill=tk.X, pady=(0, 10))

        self.reg_phone = FormField(form_container, "Phone Number")
        self.reg_phone.pack(fill=tk.X, pady=(0, 10))

        self.reg_role = FormField(
            form_container, "Register As", field_type="combo",
            options=["Customer", "Vendor", "Delivery Person"]
        )
        self.reg_role.pack(fill=tk.X, pady=(0, 10))

        self.reg_password = FormField(form_container, "Password",
                                       field_type="password")
        self.reg_password.pack(fill=tk.X, pady=(0, 10))

        self.reg_confirm = FormField(form_container, "Confirm Password",
                                      field_type="password")
        self.reg_confirm.pack(fill=tk.X, pady=(0, 10))

        self.reg_question = FormField(
            form_container, "Security Question", field_type="combo",
            options=SECURITY_QUESTIONS
        )
        self.reg_question.pack(fill=tk.X, pady=(0, 10))

        self.reg_answer = FormField(form_container, "Security Answer")
        self.reg_answer.pack(fill=tk.X, pady=(0, 20))

        PrimaryButton(
            form_container, "Create Account", self._handle_register
        ).pack(fill=tk.X, pady=(0, 15))

        # Back to login
        back_frame = tk.Frame(form_container, bg=COLORS['white'])
        back_frame.pack()
        tk.Label(
            back_frame, text="Already have an account? ",
            font=FONTS['body'], fg=COLORS['text_secondary'],
            bg=COLORS['white']
        ).pack(side=tk.LEFT)
        login_link = tk.Label(
            back_frame, text="Sign In",
            font=FONTS['body_bold'], fg=COLORS['primary'],
            bg=COLORS['white'], cursor='hand2'
        )
        login_link.pack(side=tk.LEFT)
        login_link.bind('<Button-1>', lambda e: self.show_login())

    def _handle_register(self):
        """Handle registration."""
        role_map = {
            "Customer": "customer",
            "Vendor": "vendor",
            "Delivery Person": "delivery"
        }
        try:
            role = role_map.get(self.reg_role.get(), "customer")
            user_id = self.auth.register(
                name=self.reg_name.get(),
                email=self.reg_email.get(),
                phone=self.reg_phone.get(),
                password=self.reg_password.get(),
                confirm_password=self.reg_confirm.get(),
                role=role,
                security_question=self.reg_question.get(),
                security_answer=self.reg_answer.get()
            )
            messagebox.showinfo(
                "Registration Successful",
                "Your account has been created! Please login."
            )
            self.show_login()
        except (AuthenticationError, ValidationError) as e:
            messagebox.showerror("Registration Failed", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def show_forgot_password(self):
        """Display the password reset screen."""
        self._clear()

        container = tk.Frame(self, bg=COLORS['white'])
        container.place(relx=0.5, rely=0.5, anchor='center')

        tk.Label(
            container, text="🔑",
            font=("Segoe UI", 50), bg=COLORS['white']
        ).pack()

        tk.Label(
            container, text="Reset Password",
            font=FONTS['heading_xl'], fg=COLORS['text_primary'],
            bg=COLORS['white']
        ).pack(pady=(10, 5))

        tk.Label(
            container, text="Enter your email to get started",
            font=FONTS['body_lg'], fg=COLORS['text_secondary'],
            bg=COLORS['white']
        ).pack(pady=(0, 20))

        self.reset_email = FormField(container, "Email Address")
        self.reset_email.pack(fill=tk.X, pady=(0, 10))
        self.reset_email.input.config(width=35)

        self.question_label = tk.Label(
            container, text="",
            font=FONTS['body_bold'], fg=COLORS['accent'],
            bg=COLORS['white'], wraplength=350
        )
        self.question_label.pack(anchor='w', pady=(5, 5))

        self.reset_answer = FormField(container, "Security Answer")
        self.reset_answer.pack(fill=tk.X, pady=(0, 10))

        self.reset_new_pw = FormField(container, "New Password",
                                       field_type="password")
        self.reset_new_pw.pack(fill=tk.X, pady=(0, 10))

        self.reset_confirm_pw = FormField(container, "Confirm New Password",
                                           field_type="password")
        self.reset_confirm_pw.pack(fill=tk.X, pady=(0, 10))

        btn_frame = tk.Frame(container, bg=COLORS['white'])
        btn_frame.pack(fill=tk.X, pady=(5, 10))

        fetch_btn = tk.Label(
            btn_frame, text="Get Question",
            font=FONTS['button'], fg=COLORS['white'],
            bg=COLORS['accent'], padx=15, pady=8, cursor='hand2'
        )
        fetch_btn.pack(side=tk.LEFT, padx=(0, 10))
        fetch_btn.bind('<Button-1>', lambda e: self._fetch_question())

        PrimaryButton(
            btn_frame, "Reset Password", self._handle_reset
        ).pack(side=tk.LEFT)

        # Back to login
        back = tk.Label(
            container, text="← Back to Login",
            font=FONTS['body_bold'], fg=COLORS['primary'],
            bg=COLORS['white'], cursor='hand2'
        )
        back.pack(pady=(15, 0))
        back.bind('<Button-1>', lambda e: self.show_login())

    def _fetch_question(self):
        """Fetch security question for the entered email."""
        try:
            question = self.auth.get_security_question(self.reset_email.get())
            self.question_label.config(text=f"Question: {question}")
        except AuthenticationError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def _handle_reset(self):
        """Handle password reset."""
        try:
            self.auth.reset_password(
                email=self.reset_email.get(),
                security_answer=self.reset_answer.get(),
                new_password=self.reset_new_pw.get(),
                confirm_password=self.reset_confirm_pw.get()
            )
            messagebox.showinfo("Success", "Password reset successfully! Please login.")
            self.show_login()
        except (AuthenticationError, ValidationError) as e:
            messagebox.showerror("Reset Failed", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
