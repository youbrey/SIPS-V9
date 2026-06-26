"""
ui/sidebar.py
==============
Mixin yang membangun panel SIDEBAR (kiri), terinspirasi gaya sidebar
template "Adminator": background putih, border kanan tipis, menu
dengan submenu dropdown (expand/collapse), indikator item aktif
berupa garis kecil di kiri, dan menyesuaikan diri ke lebar jendela
(collapse otomatis jadi mode ikon saat jendela dipersempit).

Submenu yang tersedia:
    Perjalanan Dinas
        -> DPRD
        -> Setwan
    Surat Undangan
        -> Rapat Paripurna
        -> Rapat AKD
"""

import customtkinter as ctk

from config import (
    APP_VERSION_LABEL, COLOR_SIDEBAR_BG, COLOR_BORDER, COLOR_TEXT,
    COLOR_TEXT_DARK, COLOR_PRIMARY, COLOR_ACTIVE_INDICATOR,
)

# Lebar sidebar saat penuh & saat mode collapsed (mode ikon saja),
# mengikuti nilai asli template ($offscreen-size & $collapsed-size).
SIDEBAR_WIDTH_FULL = 240
SIDEBAR_WIDTH_COLLAPSED = 64
# Di bawah lebar jendela ini, sidebar otomatis collapse ke mode ikon.
COLLAPSE_WINDOW_WIDTH_THRESHOLD = 1300


class SidebarMixin:
    def setup_sidebar(self):
        self.sidebar_collapsed = False
        self._dropdown_open = {"perjalanan_dinas": True, "undangan": False}
        self._sidebar_active_key = "perjalanan_dinas_dprd"
        self._active_indicator_widgets = {}

        self.sidebar_frame = ctk.CTkFrame(self, width=SIDEBAR_WIDTH_FULL, corner_radius=0,
                                           fg_color=COLOR_SIDEBAR_BG,
                                           border_width=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)
        self.sidebar_frame.grid_rowconfigure(99, weight=1)

        # Garis tipis border kanan sidebar (mirip $border-color asli)
        self.sidebar_border = ctk.CTkFrame(self, width=1, fg_color=COLOR_BORDER, corner_radius=0)
        self.sidebar_border.grid(row=0, column=0, sticky="nse")

        # --- Header / Logo --------------------------------------------------
        self.sidebar_logo_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent", height=65)
        self.sidebar_logo_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.logo_label = ctk.CTkLabel(self.sidebar_logo_frame, text="📋 SIPS",
                                        font=("Arial", 17, "bold"), text_color=COLOR_TEXT_DARK)
        self.logo_label.pack(side="left", padx=20, pady=18)

        row = 1

        self.btn_import_db = ctk.CTkButton(self.sidebar_frame, text="📥 Import Database",
                                            fg_color="transparent", text_color=COLOR_TEXT,
                                            hover_color=COLOR_BORDER, anchor="w",
                                            command=self.import_excel_database)
        self.btn_import_db.grid(row=row, column=0, padx=10, pady=(10, 4), sticky="ew")
        row += 1

        # --- Riwayat ------------------------------------------------------
        lbl_history = ctk.CTkLabel(self.sidebar_frame, text="Riwayat Edit Surat", font=("Arial", 10, "bold"),
                                    text_color=COLOR_TEXT, anchor="w")
        lbl_history.grid(row=row, column=0, padx=20, pady=(14, 2), sticky="w")
        row += 1

        history_keys = self.history_db.keys()
        self.combo_history = ctk.CTkComboBox(self.sidebar_frame,
                                              values=history_keys if history_keys else ["Tidak ada riwayat"])
        self.combo_history.grid(row=row, column=0, padx=14, pady=(2, 4), sticky="ew")
        row += 1

        self.btn_load_history = ctk.CTkButton(self.sidebar_frame, text="Load Data Surat",
                                               fg_color="#F59E0B", hover_color="#D97706",
                                               command=self.load_selected_history)
        self.btn_load_history.grid(row=row, column=0, padx=14, pady=(0, 14), sticky="ew")
        row += 1

        self._sidebar_separator(row)
        row += 1

        # --- Menu utama dengan dropdown ------------------------------------
        self.sidebar_menu_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.sidebar_menu_frame.grid(row=row, column=0, sticky="ew", padx=0, pady=(4, 4))
        row += 1
        self._build_sidebar_menu()

        self._sidebar_separator(row)
        row += 1

        self.btn_generate_main = ctk.CTkButton(self.sidebar_frame, text="⚡ CETAK SURAT & SPD",
                                                command=self.generate_documents_action,
                                                fg_color="#37C936", hover_color="#2EA82E",
                                                font=("Arial", 13, "bold"))
        self.btn_generate_main.grid(row=row, column=0, padx=14, pady=14, sticky="ew")
        row += 1

        self.lbl_credit = ctk.CTkLabel(self.sidebar_frame, text=APP_VERSION_LABEL,
                                        font=("Arial", 9), text_color=COLOR_TEXT)
        self.lbl_credit.grid(row=99, column=0, padx=20, pady=15, sticky="s")

        self._update_active_indicator()

    def _sidebar_separator(self, row):
        sep = ctk.CTkFrame(self.sidebar_frame, height=1, fg_color=COLOR_BORDER, corner_radius=0)
        sep.grid(row=row, column=0, padx=0, pady=8, sticky="ew")

    # ------------------------------------------------------------------
    # MENU DROPDOWN
    # ------------------------------------------------------------------
    def _build_sidebar_menu(self):
        for w in self.sidebar_menu_frame.winfo_children():
            w.destroy()

        self._menu_groups = {}

        self._add_dropdown_group(
            key="perjalanan_dinas", icon="🚗", title="Perjalanan Dinas",
            children=[
                ("perjalanan_dinas_dprd", "DPRD", lambda: self._goto_perjalanan_dinas("DPRD")),
                ("perjalanan_dinas_setwan", "Setwan", lambda: self._goto_perjalanan_dinas("Setwan")),
            ]
        )
        self._add_dropdown_group(
            key="undangan", icon="📨", title="Surat Undangan",
            children=[
                ("undangan_paripurna", "Rapat Paripurna", self._goto_undangan_paripurna),
                ("undangan_akd", "Rapat AKD", self._goto_undangan_akd),
            ]
        )

    def _add_dropdown_group(self, key, icon, title, children):
        group_frame = ctk.CTkFrame(self.sidebar_menu_frame, fg_color="transparent")
        group_frame.pack(fill="x", padx=0, pady=0)

        is_open = self._dropdown_open.get(key, False)
        arrow_char = "▾" if is_open else "▸"

        toggle_btn = ctk.CTkButton(
            group_frame, text=f"{icon}  {title}", anchor="w",
            fg_color="transparent", text_color=COLOR_TEXT, hover_color=COLOR_BORDER,
            font=("Arial", 12, "bold"),
            command=lambda k=key: self._toggle_dropdown(k)
        )
        toggle_btn.pack(fill="x", padx=8, pady=2)

        arrow_lbl = ctk.CTkLabel(group_frame, text=arrow_char, font=("Arial", 10), text_color=COLOR_TEXT)
        arrow_lbl.place(in_=toggle_btn, relx=0.92, rely=0.5, anchor="e")

        children_frame = ctk.CTkFrame(group_frame, fg_color="transparent")
        if is_open:
            children_frame.pack(fill="x", padx=0, pady=(0, 4))

        for child_key, child_label, child_cmd in children:
            row_frame = ctk.CTkFrame(children_frame, fg_color="transparent")
            row_frame.pack(fill="x", padx=0, pady=1)

            indicator = ctk.CTkFrame(row_frame, width=3, fg_color="transparent", corner_radius=0)
            indicator.pack(side="left", fill="y", padx=(14, 0))
            self._active_indicator_widgets[child_key] = indicator

            child_btn = ctk.CTkButton(
                row_frame, text=child_label, anchor="w",
                fg_color="transparent", text_color=COLOR_TEXT, hover_color=COLOR_BORDER,
                font=("Arial", 11),
                command=lambda k=child_key, c=child_cmd: self._select_sidebar_item(k, c)
            )
            child_btn.pack(side="left", fill="x", expand=True, padx=(6, 8), pady=1)

        self._menu_groups[key] = {
            "toggle_btn": toggle_btn, "arrow_lbl": arrow_lbl,
            "children_frame": children_frame, "group_frame": group_frame,
        }

    def _toggle_dropdown(self, key):
        self._dropdown_open[key] = not self._dropdown_open.get(key, False)
        self._build_sidebar_menu()
        self._update_active_indicator()

    def _select_sidebar_item(self, key, command):
        self._sidebar_active_key = key
        command()
        self._update_active_indicator()

    def _update_active_indicator(self):
        for key, widget in self._active_indicator_widgets.items():
            try:
                widget.configure(fg_color=COLOR_ACTIVE_INDICATOR if key == self._sidebar_active_key else "transparent")
            except Exception:
                pass

    # ------------------------------------------------------------------
    # NAVIGASI (membungkus method yang sudah ada di mixin lain)
    # ------------------------------------------------------------------
    def _goto_perjalanan_dinas(self, mode_label):
        self.show_perjalanan_dinas()
        self.change_mode(mode_label)

    def _goto_undangan_paripurna(self):
        self.show_undangan_paripurna()

    def _goto_undangan_akd(self):
        self.show_undangan_akd()

    # ------------------------------------------------------------------
    # RESPONSIF: COLLAPSE / EXPAND SIDEBAR SESUAI LEBAR JENDELA
    # ------------------------------------------------------------------
    def on_window_resize(self, event=None):
        try:
            width = self.winfo_width()
        except Exception:
            return
        if width <= 1:
            return
        should_collapse = width < COLLAPSE_WINDOW_WIDTH_THRESHOLD
        if should_collapse != self.sidebar_collapsed:
            self.sidebar_collapsed = should_collapse
            self._apply_sidebar_collapsed_state()

    def _apply_sidebar_collapsed_state(self):
        if self.sidebar_collapsed:
            self.sidebar_frame.configure(width=SIDEBAR_WIDTH_COLLAPSED)
            self.logo_label.configure(text="📋")
            self.btn_import_db.configure(text="📥")
            self.btn_generate_main.configure(text="⚡")
            for grp in self._menu_groups.values():
                grp["children_frame"].pack_forget()
                grp["arrow_lbl"].place_forget()
            self.combo_history.grid_remove()
            self.btn_load_history.grid_remove()
        else:
            self.sidebar_frame.configure(width=SIDEBAR_WIDTH_FULL)
            self.logo_label.configure(text="📋 SIPS")
            self.btn_import_db.configure(text="📥 Import Database")
            self.btn_generate_main.configure(text="⚡ CETAK SURAT & SPD")
            self.combo_history.grid()
            self.btn_load_history.grid()
            self._build_sidebar_menu()
            self._update_active_indicator()
