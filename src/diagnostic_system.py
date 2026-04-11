import json
import customtkinter as ctk
import os
import re
from datetime import datetime
from neo4j import GraphDatabase
import math
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox


class MedicalDiagnosticSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Medical Diagnostic System")
        self.root.geometry("1400x800")
        self.root.configure(bg="#E6F0FA")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 1400) // 2
        y = (screen_height - 800) // 2
        self.root.geometry(f"1400x800+{x}+{y}")

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.current_screen = None
        self.current_user = None
        self.warning_label = None
        self.bayesian_network = None
        self.page_container = None
        self.footer = None

        # --- NEW: Load the trash icon ---
        self.trash_icon = None
        try:
            # Assumes a 24x24 pixel trash_icon.png is in the same folder as the script
            trash_image = Image.open("trash_icon.png")
            self.trash_icon = ctk.CTkImage(trash_image, size=(20, 20))
        except FileNotFoundError:
            print("Warning: 'trash_icon.png' not found. Delete buttons will be text-based.")

        self.show_sign_in_screen()

    def _get_or_create_bayesian_network(self):
        if self.bayesian_network is None:
            print("Connecting to database and initializing Bayesian Network for the first time...")
            neo4j_driver = GraphDatabase.driver("neo4j+ssc://5830d6bf.databases.neo4j.io",
                                                auth=("5830d6bf", "GPrI0zK7MaGw0uczDSPTjxCtef4LgMUJ4BM_6BUq4Ko"))
            self.bayesian_network = BayesianNetwork(neo4j_driver)
            print("Bayesian Network is ready.")
        return self.bayesian_network

    def _create_persistent_layout(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.page_container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.page_container.pack(fill="both", expand=True, padx=50, pady=(50, 0))
        self.footer = ctk.CTkFrame(self.root, fg_color="transparent")
        self.footer.pack(side="bottom", fill="x", pady=(10, 20))
        back_button = ctk.CTkButton(self.footer, text="Back to Main Menu", width=200, height=45,
                                    fg_color="#6D8299", hover_color="#5A6B7D",
                                    command=self.show_main_screen)
        back_button.pack()

    def show_sign_in_screen(self, message=None, message_color="#2ECC71"):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.page_container = None
        self.footer = None
        self.current_screen = ctk.CTkFrame(self.root, fg_color="#FFFFFF", corner_radius=15, border_width=2,
                                           border_color="#D3E0EA")
        self.current_screen.pack(expand=True, padx=50, pady=50)
        title_label = ctk.CTkLabel(self.current_screen, text="Medical Diagnostic System", font=("Arial", 48, "bold"),
                                   text_color="#2C3E50", wraplength=600)
        title_label.pack(pady=40)
        sign_in_frame = ctk.CTkFrame(self.current_screen, fg_color="#F9FBFD", corner_radius=10)
        sign_in_frame.pack(pady=20, padx=30, fill="x")
        sign_in_frame.grid_columnconfigure(0, weight=1)
        sign_in_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(sign_in_frame, text="Username:", font=("Arial", 16), text_color="#2C3E50").grid(row=0, column=0,
                                                                                                     padx=20, pady=20,
                                                                                                     sticky="e")
        self.sign_in_username = ctk.CTkEntry(sign_in_frame, width=300, height=45, corner_radius=10,
                                             border_color="#A3BFFA")
        self.sign_in_username.grid(row=0, column=1, padx=20, pady=20, sticky="w")
        ctk.CTkLabel(sign_in_frame, text="Password:", font=("Arial", 16), text_color="#2C3E50").grid(row=1, column=0,
                                                                                                     padx=20, pady=20,
                                                                                                     sticky="e")
        self.sign_in_password = ctk.CTkEntry(sign_in_frame, width=300, height=45, corner_radius=10, show="*",
                                             border_color="#A3BFFA")
        self.sign_in_password.grid(row=1, column=1, padx=20, pady=20, sticky="w")
        sign_in_button = ctk.CTkButton(sign_in_frame, text="Sign In", width=180, height=45, fg_color="#4A90E2",
                                       hover_color="#357ABD", command=self.sign_in)
        sign_in_button.grid(row=2, column=0, columnspan=2, pady=25)
        sign_up_button = ctk.CTkButton(sign_in_frame, text="Sign Up", width=180, height=45, fg_color="#6D8299",
                                       hover_color="#5A6B7D", command=self.show_sign_up_screen)
        sign_up_button.grid(row=3, column=0, columnspan=2, pady=15)
        self.warning_label = ctk.CTkLabel(self.current_screen, text="", font=("Arial", 16, "bold"))
        self.warning_label.pack(pady=(5, 10), fill="x")
        if message:
            self.warning_label.configure(text=message, text_color=message_color)

    def show_sign_up_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.current_screen = ctk.CTkFrame(self.root, fg_color="#FFFFFF", corner_radius=15, border_width=2,
                                           border_color="#D3E0EA")
        self.current_screen.pack(expand=True, padx=50, pady=50)
        title_label = ctk.CTkLabel(self.current_screen, text="Create Account", font=("Arial", 40, "bold"),
                                   text_color="#2C3E50")
        title_label.pack(pady=(40, 20))
        sign_up_frame = ctk.CTkFrame(self.current_screen, fg_color="#F9FBFD", corner_radius=10)
        sign_up_frame.pack(pady=10, padx=30, fill="x")
        sign_up_frame.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkLabel(sign_up_frame, text="Username:", font=("Arial", 16), text_color="#2C3E50").grid(row=0, column=0,
                                                                                                     padx=(20, 5),
                                                                                                     pady=10,
                                                                                                     sticky="e")
        self.sign_up_username = ctk.CTkEntry(sign_up_frame, width=300, height=45, corner_radius=10,
                                             border_color="#A3BFFA", placeholder_text="e.g., john_doe123")
        self.sign_up_username.grid(row=0, column=1, padx=(5, 20), pady=10, sticky="w")
        ctk.CTkLabel(sign_up_frame, text="Password:", font=("Arial", 16), text_color="#2C3E50").grid(row=1, column=0,
                                                                                                     padx=(20, 5),
                                                                                                     pady=10,
                                                                                                     sticky="e")
        self.sign_up_password = ctk.CTkEntry(sign_up_frame, width=300, height=45, corner_radius=10, show="*",
                                             border_color="#A3BFFA")
        self.sign_up_password.grid(row=1, column=1, padx=(5, 20), pady=10, sticky="w")
        ctk.CTkLabel(sign_up_frame, text="Full Name:", font=("Arial", 16), text_color="#2C3E50").grid(row=2, column=0,
                                                                                                      padx=(20, 5),
                                                                                                      pady=10,
                                                                                                      sticky="e")
        self.sign_up_full_name = ctk.CTkEntry(sign_up_frame, width=300, height=45, corner_radius=10,
                                              border_color="#A3BFFA", placeholder_text="e.g., John Doe")
        self.sign_up_full_name.grid(row=2, column=1, padx=(5, 20), pady=10, sticky="w")
        ctk.CTkLabel(sign_up_frame, text="Date of Birth:", font=("Arial", 16), text_color="#2C3E50").grid(row=3,
                                                                                                          column=0,
                                                                                                          padx=(20, 5),
                                                                                                          pady=10,
                                                                                                          sticky="e")
        self.sign_up_dob = ctk.CTkEntry(sign_up_frame, width=300, height=45, corner_radius=10, border_color="#A3BFFA",
                                        placeholder_text="YYYY-MM-DD")
        self.sign_up_dob.grid(row=3, column=1, padx=(5, 20), pady=10, sticky="w")
        ctk.CTkLabel(sign_up_frame, text="Contact:", font=("Arial", 16), text_color="#2C3E50").grid(row=4, column=0,
                                                                                                    padx=(20, 5),
                                                                                                    pady=10, sticky="e")
        self.sign_up_contact = ctk.CTkEntry(sign_up_frame, width=300, height=45, corner_radius=10,
                                            border_color="#A3BFFA", placeholder_text="11 digits")
        self.sign_up_contact.grid(row=4, column=1, padx=(5, 20), pady=10, sticky="w")
        sign_up_button = ctk.CTkButton(sign_up_frame, text="Sign Up", width=180, height=45, fg_color="#4A90E2",
                                       hover_color="#357ABD", command=self.sign_up)
        sign_up_button.grid(row=5, column=0, columnspan=2, pady=(20, 10))
        back_button = ctk.CTkButton(sign_up_frame, text="Back to Sign In", width=180, height=45, fg_color="#6D8299",
                                    hover_color="#5A6B7D", command=self.show_sign_in_screen)
        back_button.grid(row=6, column=0, columnspan=2, pady=(0, 20))
        self.warning_label = ctk.CTkLabel(self.current_screen, text="", font=("Arial", 16, "bold"),
                                          text_color="#E74C3C")
        self.warning_label.pack(pady=(5, 10), fill="x")

    def show_main_screen(self):
        if self.page_container is None: return
        if self.footer: self.footer.pack_forget()
        for widget in self.page_container.winfo_children():
            widget.destroy()
        self.current_screen = ctk.CTkFrame(self.page_container, fg_color="#FFFFFF", corner_radius=15, border_width=2,
                                           border_color="#D3E0EA")
        self.current_screen.pack(expand=True, fill="both")
        content_frame = ctk.CTkFrame(self.current_screen, fg_color="#F9FBFD", corner_radius=10)
        content_frame.pack(pady=30, padx=30, fill="both", expand=True)
        title_label = ctk.CTkLabel(content_frame, text="Medical Diagnostic System", font=("Arial", 48, "bold"),
                                   text_color="#2C3E50")
        title_label.pack(pady=(40, 20), padx=20)
        start_button = ctk.CTkButton(content_frame, text="Start Diagnosing", width=300, height=60,
                                     font=("Arial", 20, "bold"), fg_color="#4A90E2", hover_color="#357ABD",
                                     command=self.show_diagnosing_screen)
        start_button.pack(pady=10)
        treatments_button = ctk.CTkButton(content_frame, text="Current Treatments", width=300, height=60,
                                          font=("Arial", 20, "bold"), fg_color="#4A90E2", hover_color="#357ABD",
                                          command=self.show_treatments_screen)
        treatments_button.pack(pady=10)
        # <<< NEW BUTTON FOR TESTS >>>
        tests_button = ctk.CTkButton(content_frame, text="Recommended Tests", width=300, height=60,
                                     font=("Arial", 20, "bold"), fg_color="#4A90E2", hover_color="#357ABD",
                                     command=self.show_tests_screen)
        tests_button.pack(pady=10)
        profile_button = ctk.CTkButton(content_frame, text="My Profile", width=300, height=60,
                                       font=("Arial", 20, "bold"), fg_color="#4A90E2", hover_color="#357ABD",
                                       command=self.show_profile_screen)
        profile_button.pack(pady=10)
        exit_button = ctk.CTkButton(content_frame, text="Exit", width=300, height=60, font=("Arial", 20, "bold"),
                                    fg_color="#E74C3C", hover_color="#C0392B", command=self.root.quit)
        exit_button.pack(pady=(10, 20))

    def show_profile_screen(self):
        if self.page_container is None: return
        if self.footer: self.footer.pack(side="bottom", fill="x", pady=(10, 20))
        for widget in self.page_container.winfo_children(): widget.destroy()

        self.current_screen = ctk.CTkScrollableFrame(self.page_container, fg_color="#FFFFFF", corner_radius=15,
                                                     border_width=2, border_color="#D3E0EA")
        self.current_screen.pack(expand=True, fill="both")

        profile_data = self._read_profile_data()

        # --- HEADER ---
        header_frame = ctk.CTkFrame(self.current_screen, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 0))
        full_name = profile_data.get("Full Name", "N/A")
        username = profile_data.get("Username", "N/A")
        ctk.CTkLabel(header_frame, text=full_name, font=("Arial", 32, "bold"), text_color="#2C3E50").pack()
        ctk.CTkLabel(header_frame, text=f"@{username}", font=("Arial", 16), text_color="#85929E").pack()

        separator = ctk.CTkFrame(self.current_screen, height=2, fg_color="#EAECEE")
        separator.pack(fill="x", padx=50, pady=20)

        # --- NEW 2-COLUMN LAYOUT FRAME ---
        main_content_frame = ctk.CTkFrame(self.current_screen, fg_color="transparent")
        main_content_frame.pack(fill="both", expand=True, padx=20)
        main_content_frame.grid_columnconfigure(0, weight=1)  # Left column for details
        main_content_frame.grid_columnconfigure(1, weight=1)  # Right column for graph

        # --- LEFT COLUMN ---
        left_column = ctk.CTkFrame(main_content_frame, fg_color="transparent")
        left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        personal_card = ctk.CTkFrame(left_column, fg_color="#FDFEFE", corner_radius=10, border_width=1,
                                     border_color="#EAECEE")
        personal_card.pack(fill="x", padx=10, pady=10)
        personal_title = ctk.CTkLabel(personal_card, text="Personal Details", font=("Arial", 22, "bold"),
                                      text_color="#2C3E50")
        personal_title.pack(anchor="w", padx=20, pady=(15, 10))
        details_frame = ctk.CTkFrame(personal_card, fg_color="transparent")
        details_frame.pack(fill="x", padx=20, pady=(0, 15))
        details_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(details_frame, text="🎂", font=("Arial", 20)).grid(row=0, column=0, sticky="w", padx=(0, 10))
        ctk.CTkLabel(details_frame, text="Date of Birth", font=("Arial", 16, "bold"), text_color="#566573").grid(row=0,
                                                                                                                 column=1,
                                                                                                                 sticky="w")
        ctk.CTkLabel(details_frame, text=profile_data.get("Date of Birth", "N/A"), font=("Arial", 16),
                     text_color="#34495E").grid(row=0, column=2, sticky="e")
        ctk.CTkLabel(details_frame, text="⏳", font=("Arial", 20)).grid(row=1, column=0, sticky="w", padx=(0, 10),
                                                                       pady=5)
        ctk.CTkLabel(details_frame, text="Age", font=("Arial", 16, "bold"), text_color="#566573").grid(row=1, column=1,
                                                                                                       sticky="w",
                                                                                                       pady=5)
        ctk.CTkLabel(details_frame, text=profile_data.get("Age", "N/A"), font=("Arial", 16), text_color="#34495E").grid(
            row=1, column=2, sticky="e", pady=5)
        ctk.CTkLabel(details_frame, text="📞", font=("Arial", 20)).grid(row=2, column=0, sticky="w", padx=(0, 10))
        ctk.CTkLabel(details_frame, text="Contact", font=("Arial", 16, "bold"), text_color="#566573").grid(row=2,
                                                                                                           column=1,
                                                                                                           sticky="w")
        ctk.CTkLabel(details_frame, text=profile_data.get("Contact", "N/A"), font=("Arial", 16),
                     text_color="#34495E").grid(row=2, column=2, sticky="e")

        # --- RIGHT COLUMN (FOR THE GRAPH) ---
        right_column = ctk.CTkFrame(main_content_frame, fg_color="#FDFEFE", corner_radius=10, border_width=1,
                                    border_color="#EAECEE")
        right_column.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)
        self._create_and_display_pie_chart(right_column, profile_data)

        # --- HEALTH RECORD (now full width below the columns) ---
        self.health_card = ctk.CTkFrame(self.current_screen, fg_color="#FDFEFE", corner_radius=10, border_width=1,
                                        border_color="#EAECEE")
        self.health_card.pack(fill="x", expand=True, padx=30, pady=(20, 10))
        self._populate_health_card(profile_data)

    def show_treatments_screen(self):
        if self.page_container is None: return
        if self.footer: self.footer.pack(side="bottom", fill="x", pady=(10, 20))
        for widget in self.page_container.winfo_children(): widget.destroy()
        self.current_screen = ctk.CTkScrollableFrame(self.page_container, fg_color="#FFFFFF", corner_radius=15,
                                                     border_width=2, border_color="#D3E0EA")
        self.current_screen.pack(expand=True, fill="both")
        header_frame = ctk.CTkFrame(self.current_screen, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 10))
        ctk.CTkLabel(header_frame, text="Current Treatments", font=("Arial", 32, "bold"), text_color="#2C3E50").pack()
        ctk.CTkLabel(header_frame, text="Recommended treatments for your ongoing health issues.", font=("Arial", 16),
                     text_color="#566573").pack()
        separator = ctk.CTkFrame(self.current_screen, height=2, fg_color="#EAECEE")
        separator.pack(fill="x", padx=50, pady=20)
        self.treatments_container = ctk.CTkFrame(self.current_screen, fg_color="transparent")
        self.treatments_container.pack(fill="both", expand=True, padx=30)
        loading_label = ctk.CTkLabel(self.treatments_container, text="Loading treatments, please wait...",
                                     font=("Arial", 18, "italic"), text_color="#85929E")
        loading_label.pack(pady=50)
        self.root.after(50, self._load_and_display_treatments)

    def _load_and_display_treatments(self):
        for widget in self.treatments_container.winfo_children():
            widget.destroy()
        try:
            bayesian_network = self._get_or_create_bayesian_network()
            profile_data = self._read_profile_data()
            all_diseases = profile_data.get("Diseases", [])
            ongoing_diseases = [d for d in all_diseases if isinstance(d, dict) and not d.get("cured", False)]

            try:
                age = int(profile_data.get("Age", 30))
            except (ValueError, TypeError):
                age = 30

            if age < 18:
                patient_category, dosage_key = ("Child", "child_dosage")
            elif age > 60:
                patient_category, dosage_key = ("Elderly", "elderly_dosage")
            else:
                patient_category, dosage_key = ("Adult", "adult_dosage")

            if not ongoing_diseases:
                no_issues_card = ctk.CTkFrame(self.treatments_container, fg_color="#F9FBFD", corner_radius=10,
                                              border_width=1, border_color="#D3E0EA")
                no_issues_card.pack(fill="x", pady=20)
                ctk.CTkLabel(no_issues_card, text="You have no ongoing treatments. Keep up the good health! ✨",
                             font=("Arial", 18, "italic"), text_color="#27AE60").pack(pady=30, padx=20)
            else:
                for disease_info in ongoing_diseases:
                    disease_name = disease_info.get("name")
                    if not disease_name: continue
                    disease_data = bayesian_network.probability_tables.get(disease_name, {})
                    medicines_data = disease_data.get("medicines", [])
                    disease_card = ctk.CTkFrame(self.treatments_container, fg_color="#FDFEFE", corner_radius=10,
                                                border_width=1, border_color="#EAECEE")
                    disease_card.pack(fill="x", pady=15, padx=10)
                    ctk.CTkLabel(disease_card, text=f"Treatment for: {disease_name}", font=("Arial", 22, "bold"),
                                 text_color="#2C3E50").pack(anchor="w", padx=20, pady=(15, 5))
                    ctk.CTkLabel(disease_card, text=f"Showing dosage for a {patient_category} (Age {age})",
                                 font=("Arial", 14, "italic"), text_color="#566573").pack(anchor="w", padx=20,
                                                                                          pady=(0, 15))
                    if not medicines_data:
                        ctk.CTkLabel(disease_card, text="No specific medication found. Please consult a doctor.",
                                     font=("Arial", 16), text_color="#85929E").pack(padx=20, pady=(0, 20))
                    else:
                        # --- MODIFICATION STARTS HERE: Applying the dosage parsing logic ---
                        for med_data in medicines_data:
                            med_frame = ctk.CTkFrame(disease_card, fg_color="transparent")
                            med_frame.pack(fill="x", padx=20, pady=5)

                            med_name = med_data['name']
                            ctk.CTkLabel(med_frame, text=f"• Medicine: {med_name}", font=("Arial", 16, "bold"),
                                         text_color="#34495E").pack(anchor="w", pady=(5, 0))

                            # --- THIS IS THE COPIED LOGIC THAT FIXES THE BUG ---
                            full_dosage_string = med_data.get(dosage_key, "N/A")
                            specific_dosage = "Not specified for this medicine."
                            possible_dosages = re.split(r'[;,]\s*', full_dosage_string)
                            for dose_part in possible_dosages:
                                if dose_part.strip().lower().startswith(med_name.lower()):
                                    specific_dosage = dose_part.strip()
                                    break
                            if specific_dosage == "Not specified for this medicine." and len(possible_dosages) == 1:
                                specific_dosage = full_dosage_string

                            # Display the CORRECT, parsed dosage
                            ctk.CTkLabel(med_frame, text=f"  Recommended Dosage: {specific_dosage}",
                                         font=("Arial", 14, "bold"), text_color="#27AE60", wraplength=800,
                                         justify="left").pack(anchor="w", padx=15)

                            note = med_data.get('note', 'No specific notes.')
                            ctk.CTkLabel(med_frame, text=f"  Note: {note}", font=("Arial", 14, "italic"),
                                         text_color="#566573", wraplength=800, justify="left").pack(anchor="w", padx=15,
                                                                                                    pady=(0, 10))
                        # --- MODIFICATION ENDS HERE ---

            ctk.CTkLabel(self.treatments_container,
                         text="Disclaimer: This is an AI-generated recommendation. Always consult a qualified doctor.",
                         font=("Arial", 12, "italic"), text_color="#85929E").pack(pady=(20, 0), side="bottom")
        except Exception as e:
            error_label = ctk.CTkLabel(self.treatments_container, text=f"Error loading treatments:\n{e}",
                                       font=("Arial", 16), text_color="red", wraplength=800)
            error_label.pack(pady=20)

    # <<< START: NEW METHODS FOR THE TESTS PAGE >>>
    def show_tests_screen(self):
        if self.page_container is None: return
        if self.footer: self.footer.pack(side="bottom", fill="x", pady=(10, 20))
        for widget in self.page_container.winfo_children(): widget.destroy()

        self.current_screen = ctk.CTkScrollableFrame(self.page_container, fg_color="#FFFFFF", corner_radius=15,
                                                     border_width=2, border_color="#D3E0EA")
        self.current_screen.pack(expand=True, fill="both")

        header_frame = ctk.CTkFrame(self.current_screen, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 10))
        ctk.CTkLabel(header_frame, text="Recommended Tests", font=("Arial", 32, "bold"), text_color="#2C3E50").pack()
        ctk.CTkLabel(header_frame, text="Track the status of tests for your ongoing health issues.", font=("Arial", 16),
                     text_color="#566573").pack()
        separator = ctk.CTkFrame(self.current_screen, height=2, fg_color="#EAECEE")
        separator.pack(fill="x", padx=50, pady=20)

        self.tests_container = ctk.CTkFrame(self.current_screen, fg_color="transparent")
        self.tests_container.pack(fill="both", expand=True, padx=30)
        loading_label = ctk.CTkLabel(self.tests_container, text="Loading recommended tests, please wait...",
                                     font=("Arial", 18, "italic"), text_color="#85929E")
        loading_label.pack(pady=50)

        self.root.after(50, self._load_and_display_tests)

    def _load_and_display_tests(self):
        """
        Loads and displays all tests for ongoing diseases, sorted into
        'Pending' and 'Completed' sections with a single toggle button.
        """
        for widget in self.tests_container.winfo_children():
            widget.destroy()

        profile_data = self._read_profile_data()
        all_diseases = profile_data.get("Diseases", [])

        # --- STEP 1: Flatten the list of all tests from ongoing diseases ---
        all_ongoing_tests = []
        for disease in all_diseases:
            if not disease.get("cured") and disease.get("tests"):
                disease_name = disease.get("name", "Unknown Disease")
                for test in disease.get("tests"):
                    all_ongoing_tests.append({
                        "test_name": test.get("name"),
                        "status": test.get("status", "pending"),
                        "disease_name": disease_name
                    })

        # --- STEP 2: Build the new UI structure ---
        pending_frame = ctk.CTkFrame(self.tests_container, fg_color="transparent")
        pending_frame.pack(fill="x", padx=10, pady=(10, 20))
        ctk.CTkLabel(pending_frame, text="Pending Tests", font=("Arial", 22, "bold"), text_color="#2C3E50").pack(
            anchor="w", pady=(5, 10))

        completed_frame = ctk.CTkFrame(self.tests_container, fg_color="transparent")
        completed_frame.pack(fill="x", padx=10, pady=(10, 20))
        ctk.CTkLabel(completed_frame, text="Completed Tests", font=("Arial", 22, "bold"), text_color="#2C3E50").pack(
            anchor="w", pady=(5, 10))

        # --- STEP 3: Populate the sections with tests ---
        has_pending = False
        has_completed = False

        if not all_ongoing_tests:
            has_pending = False
            has_completed = False
        else:
            for test_item in all_ongoing_tests:
                test_name = test_item["test_name"]
                test_status = test_item["status"]
                disease_name = test_item["disease_name"]

                target_frame = pending_frame if test_status == "pending" else completed_frame

                if test_status == "pending":
                    has_pending = True
                else:
                    has_completed = True

                test_row = ctk.CTkFrame(target_frame, fg_color="transparent")
                test_row.pack(fill="x", padx=10, pady=5)

                # Label showing the test name and its associated disease
                label_text = f"• {test_name} (for {disease_name})"
                ctk.CTkLabel(test_row, text=label_text, font=("Arial", 16), wraplength=700, justify="left").pack(
                    side="left", padx=(10, 0))

                # --- NEW SINGLE TOGGLE BUTTON LOGIC ---
                if test_status == "done":
                    button_text = "Mark as Pending"
                    button_fg_color = "#F5CBA7"
                    button_text_color = "#E67E22"
                    button_hover_color = "#FAD7A0"
                    new_status_to_set = "pending"
                else:  # 'pending'
                    button_text = "Mark as Done"
                    button_fg_color = "#E8F8F5"
                    button_text_color = "#1ABC9C"
                    button_hover_color = "#D1F2EB"
                    new_status_to_set = "done"

                toggle_button = ctk.CTkButton(test_row, text=button_text, height=28,
                                              font=("Arial", 12, "bold"),
                                              fg_color=button_fg_color,
                                              text_color=button_text_color,
                                              hover_color=button_hover_color,
                                              command=lambda dn=disease_name, tn=test_name,
                                                             ns=new_status_to_set: self._update_test_status(dn, tn, ns))
                toggle_button.pack(side="right", padx=(0, 10))

        # --- STEP 4: Add placeholder messages if sections are empty ---
        if not has_pending:
            no_pending_label = ctk.CTkLabel(pending_frame, text="No pending tests. ✅", font=("Arial", 16, "italic"),
                                            text_color="#85929E")
            no_pending_label.pack(pady=15, padx=20)

        if not has_completed:
            no_completed_label = ctk.CTkLabel(completed_frame, text="No completed tests found.",
                                              font=("Arial", 16, "italic"), text_color="#85929E")
            no_completed_label.pack(pady=15, padx=20)

    def _update_test_status(self, disease_name, test_name, new_status):
        profile_data = self._read_profile_data()
        all_diseases = profile_data.get("Diseases", [])

        for disease in all_diseases:
            if disease.get("name") == disease_name:
                for test in disease.get("tests", []):
                    if test.get("name") == test_name:
                        test["status"] = new_status
                        break
                break

        self._write_profile_data(profile_data)
        self.show_tests_screen()

    # <<< END: NEW METHODS FOR THE TESTS PAGE >>>

    def show_diagnosing_screen(self):
        if self.page_container is None: return
        if self.footer: self.footer.pack(side="bottom", fill="x", pady=(10, 20))
        for widget in self.page_container.winfo_children(): widget.destroy()
        self.current_screen = ctk.CTkFrame(self.page_container, fg_color="#E6F0FA")
        self.current_screen.pack(expand=True, fill="both")
        loading_label = ctk.CTkLabel(self.current_screen, text="Loading Diagnosis Engine, please wait...",
                                     font=("Arial", 22, "italic"), text_color="#566573")
        loading_label.pack(expand=True)
        self.root.after(50, self._start_diagnosis)

    def _start_diagnosis(self):
        try:
            bayesian_network = self._get_or_create_bayesian_network()
            for widget in self.current_screen.winfo_children():
                widget.destroy()
            DiagnosingScreen(self.current_screen, bayesian_network, self, self.show_main_screen)
        except Exception as e:
            for widget in self.current_screen.winfo_children():
                widget.destroy()
            error_label = ctk.CTkLabel(self.current_screen, text=f"Failed to load diagnosis engine:\n{e}",
                                       font=("Arial", 16), text_color="red")
            error_label.pack(expand=True, padx=20)

    def _create_and_display_pie_chart(self, parent_frame, profile_data):
        """Creates and embeds a pie chart of health status into the parent frame."""
        ctk.CTkLabel(parent_frame, text="Health Status Overview", font=("Arial", 22, "bold"),
                     text_color="#2C3E50").pack(pady=(15, 10))

        diseases = profile_data.get("Diseases", [])

        ongoing_count = 0
        cured_count = 0
        for disease in diseases:
            if disease.get("cured", False):
                cured_count += 1
            else:
                ongoing_count += 1

        # --- Create the Pie Chart ---
        if ongoing_count == 0 and cured_count == 0:
            # If there's no data, show a message instead of an empty chart
            ctk.CTkLabel(parent_frame, text="No health records to display.\nStart a diagnosis to see your status here.",
                         font=("Arial", 16, "italic"), text_color="#85929E").pack(expand=True)
            return

        # Data and labels for the chart
        labels = []
        sizes = []
        colors = []

        if ongoing_count > 0:
            labels.append(f'Ongoing ({ongoing_count})')
            sizes.append(ongoing_count)
            colors.append('#E74C3CB3')  # Red for ongoing

        if cured_count > 0:
            labels.append(f'Cured ({cured_count})')
            sizes.append(cured_count)
            colors.append('#2ECC71B3')  # Green for cured

        # Use Matplotlib to create the figure
        # The facecolor matches the CustomTkinter frame for a seamless look
        fig, ax = plt.subplots(figsize=(5, 4), dpi=100, facecolor='#FDFEFE')

        # Customize the pie chart
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90,
               colors=colors, textprops={'color': 'black', 'fontsize': 12, 'weight': 'bold'})

        # Ensure the pie is a circle
        ax.axis('equal')
        fig.tight_layout()

        # --- Embed the chart into the CustomTkinter window ---
        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def sign_in(self):
        self.warning_label.configure(text="")
        username = self.sign_in_username.get()
        password = self.sign_in_password.get()
        if not username or not password:
            self.warning_label.configure(text="Please enter both username and password.", text_color="#E74C3C")
            return
        file_path = os.path.join("Profiles", f"{username}.txt")
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                lines = file.readlines()
                stored_password = next((line.split(": ")[1].strip() for line in lines if line.startswith("Password:")),
                                       None)
                if stored_password == password:
                    self.current_user = username
                    self._create_persistent_layout()
                    self.show_main_screen()
                else:
                    self.warning_label.configure(text="Invalid username or password.", text_color="#E74C3C")
        else:
            self.warning_label.configure(text="Invalid username or password.", text_color="#E74C3C")

    def sign_up(self):
        self.warning_label.configure(text="")
        username = self.sign_up_username.get()
        password = self.sign_up_password.get()
        full_name = self.sign_up_full_name.get()
        dob = self.sign_up_dob.get()
        contact = self.sign_up_contact.get()
        if not all([username, password, full_name, dob, contact]):
            self.warning_label.configure(text="All fields are required!")
            return
        file_path = os.path.join("Profiles", f"{username}.txt")
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            self.warning_label.configure(text="Username must contain only letters, numbers, and underscores.")
            return
        if os.path.exists(file_path):
            self.warning_label.configure(text="Username already exists!")
            return
        if not re.match(r'^[a-zA-Z\s]+$', full_name):
            self.warning_label.configure(text="Full Name must contain only letters and spaces.")
            return
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', dob):
            self.warning_label.configure(text="Date of Birth must be in YYYY-MM-DD format.")
            return
        try:
            datetime.strptime(dob, '%Y-%m-%d')
        except ValueError:
            self.warning_label.configure(text="Invalid date! Please check the day, month, and year.")
            return
        if not re.match(r'^\d{11}$', contact):
            self.warning_label.configure(text="Contact must be exactly 11 digits.")
            return
        self.save_user_profile(username, password, full_name, dob, contact)
        self.show_sign_in_screen(message="Account created successfully! Please sign in.")

    def save_user_profile(self, username, password, full_name, dob, contact):
        if not os.path.exists("Profiles"):
            os.makedirs("Profiles")
        file_path = os.path.join("Profiles", f"{username}.txt")
        with open(file_path, 'w') as file:
            file.write(f"Username: {username}\n")
            file.write(f"Password: {password}\n")
            file.write(f"Full Name: {full_name}\n")
            file.write(f"Date of Birth: {dob}\n")
            file.write(f"Contact: {contact}\n")
            try:
                birth_date = datetime.strptime(dob, '%Y-%m-%d')
                today = datetime.today()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                file.write(f"Age: {age}\n")
            except:
                file.write("Age: Calculation Failed\n")
            file.write(f"Diseases: []\n")

    def _read_profile_data(self):
        profile_data = {}
        file_path = os.path.join("Profiles", f"{self.current_user}.txt")
        if not os.path.exists(file_path): return profile_data
        with open(file_path, 'r') as file:
            for line in file:
                parts = line.strip().split(": ", 1)
                if len(parts) == 2:
                    key, value = parts
                    if key == "Diseases":
                        if value == "None" or not value:
                            profile_data[key] = []
                        elif value.startswith("["):
                            try:
                                profile_data[key] = json.loads(value)
                            except json.JSONDecodeError:
                                profile_data[key] = []
                        else:
                            diseases = [d.strip() for d in value.split(',') if d.strip()]
                            profile_data[key] = [{"name": d, "cured": False} for d in diseases]
                    else:
                        profile_data[key] = value
        return profile_data

    def _write_profile_data(self, profile_data):
        file_path = os.path.join("Profiles", f"{self.current_user}.txt")
        with open(file_path, 'w') as file:
            for key, value in profile_data.items():
                if key == "Diseases":
                    value_to_write = json.dumps(value) if value else "[]"
                else:
                    value_to_write = value
                file.write(f"{key}: {value_to_write}\n")

    def _populate_health_card(self, profile_data):
        for widget in self.health_card.winfo_children():
            widget.destroy()

        health_title = ctk.CTkLabel(self.health_card, text="Health Record", font=("Arial", 22, "bold"),
                                    text_color="#2C3E50")
        health_title.pack(anchor="w", padx=20, pady=(15, 10))

        diseases = profile_data.get("Diseases", [])

        ongoing_frame = ctk.CTkFrame(self.health_card, fg_color="transparent")
        ongoing_frame.pack(fill="x", padx=20, pady=(10, 5))
        ongoing_title = ctk.CTkLabel(ongoing_frame, text="Treatment Ongoing", font=("Arial", 18, "bold"),
                                     text_color="#2C3E50")
        ongoing_title.pack(anchor="w", pady=(5, 5))

        treated_frame = ctk.CTkFrame(self.health_card, fg_color="transparent")
        treated_frame.pack(fill="x", padx=20, pady=(10, 5))
        treated_title = ctk.CTkLabel(treated_frame, text="Treated", font=("Arial", 18, "bold"), text_color="#2C3E50")
        treated_title.pack(anchor="w", pady=(5, 5))

        has_ongoing = False
        has_treated = False

        if not diseases:
            ctk.CTkLabel(ongoing_frame, text="No recorded health issues. ✨", font=("Arial", 16, "italic"),
                         text_color="#85929E").pack(pady=10)
            ctk.CTkLabel(treated_frame, text="No treated health issues.", font=("Arial", 14, "italic"),
                         text_color="#85929E").pack(pady=5)
        else:
            for disease in diseases:
                if not isinstance(disease, dict): continue
                disease_name = disease.get("name", "Unknown")
                cured = disease.get("cured", False)

                target_frame = treated_frame if cured else ongoing_frame
                if cured:
                    has_treated = True
                else:
                    has_ongoing = True

                disease_row_frame = ctk.CTkFrame(target_frame, fg_color="transparent")
                disease_row_frame.pack(fill="x", pady=5)

                disease_label = ctk.CTkLabel(disease_row_frame, text=f"• {disease_name}", font=("Arial", 16),
                                             text_color="#34495E")
                disease_label.pack(side="left", padx=10, pady=5)

                # --- NEW BUTTONS FRAME ---
                # A frame on the right to hold the action buttons
                buttons_frame = ctk.CTkFrame(disease_row_frame, fg_color="transparent")
                buttons_frame.pack(side="right", padx=10)

                # --- NEW DELETE ICON BUTTON ---
                delete_button = ctk.CTkButton(
                    buttons_frame,
                    text="",  # No text
                    image=self.trash_icon,
                    width=28,
                    height=28,
                    fg_color="transparent",
                    hover_color="#FADBD8",
                    command=lambda d=disease_name: self._prompt_delete_disease(d)
                )
                delete_button.pack(side="right", padx=(5, 0))
                # If icon didn't load, show text as a fallback
                if self.trash_icon is None:
                    delete_button.configure(text="🗑️", text_color="red")

                # --- CURE/UNCURE BUTTON ---
                button_text = "Mark as Not Cured" if cured else "Mark as Cured"
                button_fg_color = "#F5CBA7" if cured else "#E8F8F5"
                button_text_color = "#E67E22" if cured else "#1ABC9C"
                button_hover_color = "#FAD7A0" if cured else "#D1F2EB"

                cure_button = ctk.CTkButton(buttons_frame, text=button_text, height=28,
                                            font=("Arial", 12, "bold"), text_color_disabled="D3D3D3",
                                            fg_color=button_fg_color, text_color=button_text_color,
                                            hover_color=button_hover_color,
                                            command=lambda d=disease_name: self._mark_disease_as_cured(d))
                cure_button.pack(side="right")

            if not has_ongoing:
                ctk.CTkLabel(ongoing_frame, text="No ongoing health issues.", font=("Arial", 14, "italic"),
                             text_color="#85929E").pack(pady=5)
            if not has_treated:
                ctk.CTkLabel(treated_frame, text="No treated health issues.", font=("Arial", 14, "italic"),
                             text_color="#85929E").pack(pady=5)

    def _mark_disease_as_cured(self, disease_name):
        """Toggles the 'cured' status of a disease and refreshes the entire profile screen."""
        profile_data = self._read_profile_data()
        diseases = profile_data.get("Diseases", [])

        # Find the specific disease and toggle its 'cured' status
        for disease in diseases:
            if isinstance(disease, dict) and disease.get("name") == disease_name:
                disease["cured"] = not disease.get("cured", False)
                break

        # Save the updated data back to the file
        profile_data["Diseases"] = diseases
        self._write_profile_data(profile_data)

        # --- THE CRUCIAL FIX ---
        # Re-render the entire profile screen to reflect the changes in the chart and lists.
        self.show_profile_screen()

    def _prompt_delete_disease(self, disease_name):
        """Shows a confirmation dialog before deleting a disease record."""
        is_sure = messagebox.askyesno(
            title="Confirm Deletion",
            message=f"Are you sure you want to permanently delete the record for '{disease_name}'?\n\nThis action cannot be undone."
        )
        if is_sure:
            self._delete_disease_record(disease_name)

    def _delete_disease_record(self, disease_name_to_delete):
        """Removes a disease from the user's profile and refreshes the UI."""
        profile_data = self._read_profile_data()

        # Filter out the disease to be deleted
        diseases = profile_data.get("Diseases", [])
        updated_diseases = [d for d in diseases if d.get("name") != disease_name_to_delete]

        profile_data["Diseases"] = updated_diseases
        self._write_profile_data(profile_data)

        # Refresh the profile screen to show the change
        self.show_profile_screen()

class BayesianNetwork:
    def __init__(self, neo4j_driver):
        self.driver = neo4j_driver
        self.probability_tables = self._load_probabilities()
        self.disease_priors = self._calculate_priors()
        self.background_symptom_prob = 0.01

    def _load_probabilities(self):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (d:Disease) WHERE (d)-[:HAS_SYMPTOM]->()
                WITH d,
                     [(d)-[r:HAS_SYMPTOM]->(s:Symptom) | {name: s.name, severity: r.weight, probability: r.probability}] AS symptoms,
                     [(d)-[:TREATED_BY]->(m:Medicine) | {name: m.name, adult_dosage: m.adult_dosage, child_dosage: m.child_dosage, elderly_dosage: m.elderly_dosage, note: m.note}] AS medicines,
                     [(d)-[:DIAGNOSED_BY]->(t:Test) | t.name] AS tests
                RETURN d.name AS disease, symptoms, medicines, tests
            """)
            tables = {}
            for record in result:
                disease_name = record["disease"]
                if not disease_name: continue
                tables[disease_name] = {"symptoms": {}, "medicines": [], "tests": []}
                for symptom_info in record["symptoms"]:
                    tables[disease_name]["symptoms"][symptom_info["name"]] = {"severity": int(symptom_info["severity"]),
                                                                              "probability": symptom_info[
                                                                                                 "probability"] or 0.1}
                for med_info in record["medicines"]:
                    medicine_data = {"name": med_info["name"], "adult_dosage": med_info["adult_dosage"] or "N/A",
                                     "child_dosage": med_info["child_dosage"] or "N/A",
                                     "elderly_dosage": med_info["elderly_dosage"] or "N/A",
                                     "note": med_info["note"] or "No specific notes."}
                    if medicine_data not in tables[disease_name]["medicines"]:
                        tables[disease_name]["medicines"].append(medicine_data)
                tables[disease_name]["tests"] = record["tests"]
        return tables

    def _calculate_priors(self):
        num_diseases = len(self.probability_tables)
        if num_diseases == 0: return {}
        prior = 1.0 / num_diseases
        return {disease: prior for disease in self.probability_tables.keys()}

    def infer_diseases(self, symptoms_with_severities):
        log_probabilities = {}
        for disease, data in self.probability_tables.items():
            prior = self.disease_priors.get(disease, 1e-9)
            log_probabilities[disease] = math.log(prior)
            for symptom, severity in symptoms_with_severities:
                if symptom in data["symptoms"]:
                    symptom_data = data["symptoms"][symptom]
                    prob = symptom_data["probability"]
                    if abs(symptom_data["severity"] - severity) == 1:
                        prob *= 0.75
                    elif abs(symptom_data["severity"] - severity) > 1:
                        prob *= 0.25
                    log_probabilities[disease] += math.log(prob + 1e-9)
                else:
                    log_probabilities[disease] += math.log(self.background_symptom_prob)
        sorted_diseases = sorted(log_probabilities.items(), key=lambda item: item[1], reverse=True)
        return [disease for disease, score in sorted_diseases[:4]]


class DiagnosingScreen:
    def __init__(self, parent, bayesian_network, app, main_menu_callback):
        self.parent = parent
        self.bayesian_network = bayesian_network
        self.app = app
        self.main_menu_callback = main_menu_callback
        self.symptoms = self.fetch_symptoms()
        self.additional_symptom_checkboxes = []
        self.container = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.container.pack(expand=True, fill="both", padx=20, pady=20)
        self.build_step1_ui()

    def fetch_symptoms(self):
        symptom_set = set()
        for disease_data in self.bayesian_network.probability_tables.values():
            for symptom in disease_data["symptoms"]:
                symptom_set.add(symptom)
        return sorted(list(symptom_set))

    def clear_container(self):
        for widget in self.container.winfo_children(): widget.destroy()

    def create_live_search_widget(self, parent, excluded_symptoms=[]):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        entry_var = ctk.StringVar()
        entry = ctk.CTkEntry(frame, textvariable=entry_var, placeholder_text="Type to search for a symptom...",
                             height=40)
        entry.pack(fill="x")
        suggestions_frame = ctk.CTkScrollableFrame(frame, fg_color="#FDFEFE", border_color="#D3E0EA", border_width=1)

        def update_suggestions(*args):
            search_term = entry_var.get().lower()
            for widget in suggestions_frame.winfo_children(): widget.destroy()
            if not search_term: suggestions_frame.pack_forget(); return
            available = [s for s in self.symptoms if s not in excluded_symptoms]
            matches = [s for s in available if search_term in s.lower()][:5]
            if matches:
                suggestions_frame.pack(fill="x", pady=(2, 0), expand=False)
                for match in matches:
                    btn = ctk.CTkButton(suggestions_frame, text=match, anchor="w", fg_color="transparent",
                                        text_color="#2C3E50", hover_color="#E6F0FA",
                                        command=lambda m=match: on_suggestion_click(m))
                    btn.pack(fill="x", padx=5, pady=2)
            else:
                suggestions_frame.pack_forget()

        def on_suggestion_click(symptom_name):
            entry_var.set(symptom_name)
            suggestions_frame.pack_forget()

        def on_focus_out(event):
            suggestions_frame.after(200, suggestions_frame.pack_forget)

        entry_var.trace_add("write", update_suggestions)
        entry.bind("<FocusOut>", on_focus_out)
        return frame, entry

    def build_step1_ui(self):
        self.clear_container()
        frame = ctk.CTkFrame(self.container, fg_color="#FFFFFF", corner_radius=15)
        frame.pack(expand=True, padx=20, pady=20)
        ctk.CTkLabel(frame, text="Symptom-Based Diagnosis", font=("Arial", 32, "bold"), text_color="#2C3E50").pack(
            pady=(30, 20))
        ctk.CTkLabel(frame,
                     text="Please select your two primary symptoms and their severity (1: Mild, 2: Moderate, 3: Severe).",
                     font=("Arial", 16), text_color="#566573").pack(pady=(0, 25))
        s1_card = ctk.CTkFrame(frame, fg_color="#F9FBFD", corner_radius=10)
        s1_card.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(s1_card, text="Primary Symptom:", font=("Arial", 16, "bold"), text_color="#2C3E50").pack(
            anchor="w", padx=20, pady=(10, 5))
        search_frame1, self.symptom_entry1 = self.create_live_search_widget(s1_card)
        search_frame1.pack(fill="x", padx=20)
        self.severity_var1 = ctk.IntVar(value=2)
        ctk.CTkSlider(s1_card, from_=1, to=3, number_of_steps=2, variable=self.severity_var1).pack(pady=(10, 15),
                                                                                                   padx=20)
        s2_card = ctk.CTkFrame(frame, fg_color="#F9FBFD", corner_radius=10)
        s2_card.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(s2_card, text="Secondary Symptom:", font=("Arial", 16, "bold"), text_color="#2C3E50").pack(
            anchor="w", padx=20, pady=(10, 5))
        search_frame2, self.symptom_entry2 = self.create_live_search_widget(s2_card)
        search_frame2.pack(fill="x", padx=20)
        self.severity_var2 = ctk.IntVar(value=2)
        ctk.CTkSlider(s2_card, from_=1, to=3, number_of_steps=2, variable=self.severity_var2).pack(pady=(10, 15),
                                                                                                   padx=20)
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(pady=(30, 30))
        ctk.CTkButton(button_frame, text="Proceed", command=self.proceed_to_step2, height=45,
                      font=("Arial", 16, "bold")).pack(side="left", padx=10)

    def proceed_to_step2(self):
        s1, sev1 = self.symptom_entry1.get(), self.severity_var1.get()
        s2, sev2 = self.symptom_entry2.get(), self.severity_var2.get()
        if not s1 or not s2 or s1 == s2 or s1 not in self.symptoms or s2 not in self.symptoms:
            self.symptom_entry1.configure(border_color="red" if not s1 or s1 not in self.symptoms else "#979DA2")
            self.symptom_entry2.configure(
                border_color="red" if not s2 or s2 not in self.symptoms or s1 == s2 else "#979DA2")
            return
        initial_symptoms = [(s1, sev1), (s2, sev2)]
        initial_diseases = self.bayesian_network.infer_diseases(initial_symptoms)
        if not initial_diseases:
            self.display_results("No matching diseases found.", [], [])
            return
        self.build_step2_ui(initial_diseases, initial_symptoms)

    def get_relevant_additional_symptoms(self, diseases, excluded_symptoms):
        relevant_symptoms = set()
        for disease in diseases:
            disease_data = self.bayesian_network.probability_tables.get(disease, {})
            for symptom in disease_data.get("symptoms", {}):
                if symptom not in excluded_symptoms:
                    relevant_symptoms.add(symptom)
        return sorted(list(relevant_symptoms))

    def build_step2_ui(self, initial_diseases, initial_symptoms):
        self.clear_container()
        self.additional_symptom_checkboxes = []
        excluded = [s[0] for s in initial_symptoms]
        relevant_symptoms = self.get_relevant_additional_symptoms(initial_diseases, excluded)
        frame = ctk.CTkFrame(self.container, fg_color="#FFFFFF", corner_radius=15, width=1100)
        frame.pack(expand=True, pady=20)
        ctk.CTkLabel(frame, text="Refine Diagnosis", font=("Arial", 32, "bold"), text_color="#2C3E50").pack(
            pady=(30, 20))
        ctk.CTkLabel(frame,
                     text="To help improve the accuracy of your diagnosis,\nplease check any of the following symptoms you are also experiencing.",
                     font=("Arial", 16), text_color="#566573").pack(pady=(0, 25))
        if not relevant_symptoms:
            ctk.CTkLabel(frame, text="No further differentiating symptoms found in the database.",
                         font=("Arial", 14, "italic"), text_color="#85929E").pack(pady=20)
        else:
            checkbox_frame = ctk.CTkScrollableFrame(frame, fg_color="#F9FBFD")
            checkbox_frame.pack(fill="both", expand=True, padx=20, pady=10)
            for i, symptom in enumerate(relevant_symptoms):
                cb = ctk.CTkCheckBox(checkbox_frame, text=symptom, onvalue=symptom, offvalue="", font=("Arial", 14))
                cb.grid(row=i // 2, column=i % 2, padx=15, pady=10, sticky="w")
                self.additional_symptom_checkboxes.append(cb)
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(pady=(20, 30))
        ctk.CTkButton(button_frame, text="Finalize Diagnosis",
                      command=lambda: self.finalize_diagnosis(initial_symptoms), height=45,
                      font=("Arial", 16, "bold")).pack()

    def finalize_diagnosis(self, initial_symptoms):
        additional_symptoms = [(cb.get(), 2) for cb in self.additional_symptom_checkboxes if cb.get()]
        final_symptoms = initial_symptoms + additional_symptoms
        final_diseases = self.bayesian_network.infer_diseases(final_symptoms)
        final_disease = final_diseases[0] if final_diseases else "Undetermined"

        medicines_data = self.get_medicines_for_disease(final_disease)
        tests_data = self.get_tests_for_disease(final_disease)

        # <<< THE CRUCIAL FIX IS HERE: We must pass 'tests_data' to the save function.
        self.save_diagnosis_to_profile(final_disease, tests_data)

        self.display_results(final_disease, medicines_data, tests_data)

    def get_medicines_for_disease(self, disease_name):
        if disease_name in self.bayesian_network.probability_tables:
            return self.bayesian_network.probability_tables[disease_name].get("medicines", [])
        return []

    def get_tests_for_disease(self, disease_name):
        if disease_name in self.bayesian_network.probability_tables:
            return self.bayesian_network.probability_tables[disease_name].get("tests", [])
        return []

    def save_diagnosis_to_profile(self, disease_name, tests_data):
        """
        Saves/updates the diagnosis and its tests to the user's profile.
        If the disease exists, it's marked as uncured and its test list is updated.
        If not, a new entry is created.
        """
        if disease_name == "Undetermined":
            return

        profile_data = self.app._read_profile_data()

        if 'Diseases' not in profile_data or not isinstance(profile_data['Diseases'], list):
            profile_data['Diseases'] = []

        # Find if the disease already exists in the profile
        existing_disease_entry = None
        for disease in profile_data['Diseases']:
            if isinstance(disease, dict) and disease.get("name") == disease_name:
                existing_disease_entry = disease
                break

        if existing_disease_entry:
            # --- UPDATE THE EXISTING ENTRY ---
            # A new diagnosis means the disease is no longer considered 'cured'.
            existing_disease_entry['cured'] = False

            # Ensure the 'tests' key exists
            if 'tests' not in existing_disease_entry:
                existing_disease_entry['tests'] = []

            # Create a dictionary of existing tests for fast lookup {test_name: test_dict}
            existing_tests_map = {t['name']: t for t in existing_disease_entry['tests']}

            # Add new tests or reset status of existing ones to 'pending'
            for test_name in tests_data:
                if test_name in existing_tests_map:
                    # If test already exists, it must be reset to pending for the new diagnosis
                    existing_tests_map[test_name]['status'] = 'pending'
                else:
                    # If this is a new test for this disease, add it
                    new_test = {'name': test_name, 'status': 'pending'}
                    existing_disease_entry['tests'].append(new_test)
        else:
            # --- CREATE A COMPLETELY NEW ENTRY ---
            new_disease_entry = {
                "name": disease_name,
                "cured": False,
                "tests": [{"name": test_name, "status": "pending"} for test_name in tests_data]
            }
            profile_data['Diseases'].append(new_disease_entry)

        self.app._write_profile_data(profile_data)

    def display_results(self, final_disease, medicines_data, tests_data):
        self.clear_container()

        # --- NEW LAYOUT STRUCTURE ---
        # Main container for the entire report page
        report_container = ctk.CTkFrame(self.container, fg_color="#FFFFFF", corner_radius=15)
        report_container.pack(expand=True, padx=20, pady=20, fill="both")

        ctk.CTkLabel(report_container, text="Diagnosis Report", font=("Arial", 32, "bold"), text_color="#2C3E50").pack(
            pady=(20, 10))

        # --- SCROLLABLE FRAME for all the dynamic content ---
        scrollable_frame = ctk.CTkScrollableFrame(report_container, fg_color="transparent")
        scrollable_frame.pack(fill="both", expand=True, padx=15, pady=5)

        # --- All content now goes inside the SCROLLABLE FRAME ---
        result_card = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        result_card.pack(pady=10, padx=25, fill="x")
        ctk.CTkLabel(result_card, text="Possible Disease:", font=("Arial", 18, "bold"), text_color="#2C3E50").pack(
            anchor="w")
        ctk.CTkLabel(result_card, text=final_disease, font=("Arial", 24, "bold"), text_color="#4A90E2").pack(anchor="w",
                                                                                                             pady=(
                                                                                                             0, 10))

        if tests_data:
            tests_card = ctk.CTkFrame(scrollable_frame, fg_color="#F9FBFD", corner_radius=10, border_width=1,
                                      border_color="#EAECEE")
            tests_card.pack(fill="x", padx=25, pady=(0, 20))
            ctk.CTkLabel(tests_card, text="Recommended Test(s) to Confirm:", font=("Arial", 18, "bold"),
                         text_color="#2C3E50").pack(anchor="w", padx=20, pady=(15, 5))
            tests_list_text = "\n".join([f"• {test_name}" for test_name in tests_data])
            ctk.CTkLabel(tests_card, text=tests_list_text, font=("Arial", 16), text_color="#34495E", justify="left",
                         wraplength=900).pack(anchor="w", padx=30, pady=(0, 15))

        profile = self.app._read_profile_data()
        try:
            age = int(profile.get("Age", 30))
        except (ValueError, TypeError):
            age = 30
        if age < 18:
            patient_category, dosage_key = ("Child", "child_dosage")
        elif age > 60:
            patient_category, dosage_key = ("Elderly", "elderly_dosage")
        else:
            patient_category, dosage_key = ("Adult", "adult_dosage")

        ctk.CTkLabel(scrollable_frame, text=f"Recommended Treatment for a {patient_category} (Age {age}):",
                     font=("Arial", 18, "bold"), text_color="#2C3E50").pack(anchor="w", padx=25, pady=(10, 5))

        if not medicines_data:
            ctk.CTkLabel(scrollable_frame, text="No specific medication found. Please consult a doctor.",
                         font=("Arial", 16, "italic"), text_color="#85929E").pack(pady=20, padx=25)
        else:
            for i, med_data in enumerate(medicines_data):
                med_card = ctk.CTkFrame(scrollable_frame, fg_color="#F9FBFD", corner_radius=10, border_width=1,
                                        border_color="#D3E0EA")
                med_card.pack(fill="x", pady=10, padx=25)
                med_name = med_data['name']
                ctk.CTkLabel(med_card, text=f"Medicine: {med_name}", font=("Arial", 16, "bold"),
                             text_color="#34495E").pack(anchor="w", padx=15, pady=(10, 5))
                full_dosage_string = med_data.get(dosage_key, "N/A")
                specific_dosage = "Not specified for this medicine."
                possible_dosages = re.split(r'[;,]\s*', full_dosage_string)
                for dose_part in possible_dosages:
                    if dose_part.strip().lower().startswith(med_name.lower()):
                        specific_dosage = dose_part.strip()
                        break
                if specific_dosage == "Not specified for this medicine." and len(possible_dosages) == 1:
                    specific_dosage = full_dosage_string
                ctk.CTkLabel(med_card, text=f"Recommended Dosage: {specific_dosage}", font=("Arial", 14, "bold"),
                             text_color="#27AE60", wraplength=850, justify="left").pack(anchor="w", padx=15)
                note = med_data.get('note', 'No specific notes.')
                ctk.CTkLabel(med_card, text=f"Note: {note}", font=("Arial", 14, "italic"), text_color="#566573",
                             wraplength=900, justify="left").pack(anchor="w", padx=15, pady=(5, 10))

        # --- FOOTER SECTION inside the main container, but OUTSIDE the scrollable part ---
        footer_frame = ctk.CTkFrame(report_container, fg_color="transparent")
        footer_frame.pack(side="bottom", fill="x", pady=10)

        ctk.CTkLabel(footer_frame,
                     text="Disclaimer: This is an AI-generated diagnosis. Always consult a qualified doctor.",
                     font=("Arial", 12, "italic"), text_color="#85929E").pack(pady=(5, 10))

        button_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
        button_frame.pack(pady=(5, 10))
        ctk.CTkButton(button_frame, text="Start New Diagnosis", command=self.build_step1_ui, height=45,
                      font=("Arial", 16, "bold")).pack(side="left", padx=10)



if __name__ == "__main__":
    root = ctk.CTk()
    app = MedicalDiagnosticSystem(root)
    root.mainloop()