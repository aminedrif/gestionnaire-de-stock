# -*- coding: utf-8 -*-
"""
Shared UI style constants — Modern, clean design system.
"""

# ─────────────────────────────────────────────
# PAGE BACKGROUND — Applied to every page container
# ─────────────────────────────────────────────
PAGE_BG = "background-color: #f0f2f5;"

# ─────────────────────────────────────────────
# DIALOG / POPUP STYLING — For QDialog windows
# ─────────────────────────────────────────────
DIALOG_STYLE = """
    QDialog {
        background-color: #f0f2f5;
    }
    QLabel {
        font-size: 13px;
        color: #334155;
    }
    QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox, QDateEdit {
        border: 1.5px solid #d1d5db;
        border-radius: 6px;
        padding: 8px 10px;
        font-size: 13px;
        background-color: white;
        color: #1e293b;
        min-height: 18px;
    }
    QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus, QComboBox:focus, QDateEdit:focus {
        border-color: #6366f1;
        background-color: #fafafe;
    }
    QCheckBox {
        font-size: 13px;
        color: #334155;
        spacing: 6px;
    }
    QGroupBox {
        background-color: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        margin-top: 16px;
        padding: 14px 10px 10px 10px;
        font-weight: 600;
        font-size: 13px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 6px;
        color: #475569;
    }
"""

# ─────────────────────────────────────────────
# TABLE — Clean, modern, soft alternating rows
# ─────────────────────────────────────────────
TABLE_STYLE = """
    QTableWidget {
        border: 1px solid #dfe3e8;
        border-radius: 8px;
        background-color: white;
        gridline-color: transparent;
        font-size: 13px;
        outline: none;
    }
    QHeaderView::section {
        background-color: #f4f6f8;
        padding: 10px 12px;
        border: none;
        border-bottom: 2px solid #dfe3e8;
        font-weight: 600;
        color: #454f5b;
        font-size: 12px;
        text-transform: uppercase;
    }
    QTableWidget::item {
        padding: 8px 10px;
        border-bottom: 1px solid #f0f2f5;
        color: #212b36;
    }
    QTableWidget::item:selected {
        background-color: #eef2ff;
        color: #3730a3;
    }
    QTableWidget::item:alternate {
        background-color: #fafbfc;
    }
    QScrollBar:vertical {
        border: none; background: #f4f6f8; width: 6px; border-radius: 3px;
    }
    QScrollBar::handle:vertical {
        background: #c4cdd5; border-radius: 3px; min-height: 30px;
    }
    QScrollBar::handle:vertical:hover { background: #919eab; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
"""

# ─────────────────────────────────────────────
# SEARCH INPUT
# ─────────────────────────────────────────────
SEARCH_INPUT_STYLE = """
    QLineEdit {
        border: 1.5px solid #dfe3e8;
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 13px;
        background-color: white;
        color: #212b36;
    }
    QLineEdit:focus {
        border-color: #6366f1;
        background-color: #fafafe;
    }
"""

# ─────────────────────────────────────────────
# COMBO BOX
# ─────────────────────────────────────────────
COMBO_STYLE = """
    QComboBox {
        border: 1.5px solid #dfe3e8;
        border-radius: 8px;
        padding: 8px 14px;
        font-size: 13px;
        background-color: white;
        color: #212b36;
    }
    QComboBox::drop-down { border: none; width: 24px; }
    QComboBox:focus { border-color: #6366f1; }
    QComboBox QAbstractItemView {
        border: 1px solid #dfe3e8;
        background-color: white;
        selection-background-color: #eef2ff;
        selection-color: #3730a3;
    }
"""

# ─────────────────────────────────────────────
# DATE EDIT
# ─────────────────────────────────────────────
DATE_INPUT_STYLE = """
    QDateEdit {
        border: 1.5px solid #dfe3e8;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
        background-color: white;
        color: #212b36;
    }
    QDateEdit:focus { border-color: #6366f1; }
"""

# ─────────────────────────────────────────────
# FORM INPUTS (for dialogs)
# ─────────────────────────────────────────────
FORM_INPUT_STYLE = """
    QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox {
        border: 1.5px solid #dfe3e8;
        border-radius: 6px;
        padding: 8px 10px;
        font-size: 13px;
        background-color: white;
    }
    QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus, QComboBox:focus {
        border-color: #6366f1;
    }
"""

# ─────────────────────────────────────────────
# TAB WIDGET
# ─────────────────────────────────────────────
TAB_WIDGET_STYLE = """
    QTabWidget::pane {
        border: 1px solid #dfe3e8;
        background: white;
        border-radius: 8px;
        top: -1px;
    }
    QTabBar::tab {
        background: #f4f6f8;
        border: 1px solid #dfe3e8;
        padding: 10px 22px;
        margin-right: 3px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        color: #637381;
        font-weight: 600;
        font-size: 12px;
    }
    QTabBar::tab:selected {
        background: white;
        border-bottom-color: white;
        color: #212b36;
    }
    QTabBar::tab:hover:!selected {
        background: #ebeef2;
    }
"""

# ─────────────────────────────────────────────
# GROUP BOX
# ─────────────────────────────────────────────
GROUP_BOX_STYLE = """
    QGroupBox {
        background-color: white;
        border: 1px solid #dfe3e8;
        border-radius: 8px;
        padding: 14px 10px 10px 10px;
        font-weight: 600;
        font-size: 13px;
        margin-top: 14px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 6px;
        color: #454f5b;
    }
"""

# ─────────────────────────────────────────────
# BUTTONS — Solid colors, no gradients
# ─────────────────────────────────────────────
def _btn(bg, hover_bg, color="white"):
    return f"""
        QPushButton {{
            background-color: {bg};
            color: {color};
            border: none;
            border-radius: 6px;
            padding: 9px 18px;
            font-size: 13px;
            font-weight: 600;
        }}
        QPushButton:hover {{ background-color: {hover_bg}; }}
        QPushButton:pressed {{ background-color: {hover_bg}; }}
        QPushButton:disabled {{ background-color: #dfe3e8; color: #919eab; }}
    """

PRIMARY_BTN = _btn("#6366f1", "#4f46e5")          # Indigo
GREEN_BTN = _btn("#22c55e", "#16a34a")             # Green
PURPLE_BTN = _btn("#8b5cf6", "#7c3aed")            # Purple
AMBER_BTN = _btn("#f59e0b", "#d97706")             # Amber
DANGER_BTN = _btn("#ef4444", "#dc2626")            # Red
SECONDARY_BTN = _btn("#f4f6f8", "#dfe3e8", color="#454f5b")  # Light gray

# Small inline action button (for table cells)
def action_btn_style(color, hover_bg):
    return f"""
        QPushButton {{
            background-color: transparent;
            color: {color};
            border: 1.5px solid {color};
            border-radius: 5px;
            padding: 4px 10px;
            font-size: 11px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: {hover_bg};
            color: white;
            border-color: {hover_bg};
        }}
    """

# ─────────────────────────────────────────────
# PAGE HEADER — Rounded card with gradient
# ─────────────────────────────────────────────
def header_style(gradient_start, gradient_end):
    return f"""
        QFrame {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {gradient_start}, stop:1 {gradient_end});
            border-radius: 10px;
            padding: 16px 20px;
        }}
    """

HEADER_TITLE_STYLE = "font-size: 20px; font-weight: bold; color: white; background: transparent;"
HEADER_SUBTITLE_STYLE = "font-size: 12px; color: rgba(255,255,255,0.8); background: transparent;"
HEADER_BADGE_STYLE = """
    background-color: rgba(255,255,255,0.18);
    color: white;
    padding: 4px 12px;
    border-radius: 10px;
    font-weight: 600;
    font-size: 12px;
"""

# ─────────────────────────────────────────────
# STAT CARD
# ─────────────────────────────────────────────
def stat_card_style(color, bg_color):
    return f"""
        QFrame {{
            background-color: {bg_color};
            border-radius: 8px;
            border: 1px solid {color}20;
            padding: 10px;
        }}
    """
