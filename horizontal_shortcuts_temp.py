# Horizontal Shortcuts Layout Code
# To be integrated into pos_page.py

def create_shortcuts_grid(self):
    """Créer la rangée horizontale de raccourcis (scrollable)"""
    from PyQt5.QtWidgets import QScrollArea
    
    # Scroll area for horizontal scrolling
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    scroll_area.setMaximumHeight(110)
    scroll_area.setStyleSheet("""
        QScrollArea {
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            background-color: #fafafa;
        }
        QScrollBar:horizontal {
            height: 8px;
            background: #f0f0f0;
        }
        QScrollBar::handle:horizontal {
            background: #8b5cf6;
            border-radius: 4px;
        }
    """)
    
    # Inner container for horizontal layout
    self.shortcuts_inner_container = QWidget()
    self.shortcuts_layout = QHBoxLayout(self.shortcuts_inner_container)
    self.shortcuts_layout.setSpacing(8)
    self.shortcuts_layout.setContentsMargins(10, 10, 10, 10)
    
    # Create 6 initial shortcut slots
    self.shortcut_buttons = {}
    self.max_shortcuts = 20
    
    for i in range(6):
        position = i + 1
        btn = self.create_shortcut_button(position)
        self.shortcuts_layout.addWidget(btn)
        self.shortcut_buttons[position] = btn
    
    self.shortcuts_layout.addStretch()
    
    scroll_area.setWidget(self.shortcuts_inner_container)
    
    # Load shortcuts
    self.load_shortcuts()
    
    return scroll_area

def create_shortcut_button(self, position):
    """Create a single shortcut button"""
    btn = QPushButton()
    btn.setFixedSize(100, 80)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setProperty("position", position)
    btn.setStyleSheet("""
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f0f0f0);
            border: 2px solid #ddd;
            border-radius: 10px;
            padding: 5px;
            font-size: 11px;
            font-weight: bold;
            color: #2c3e50;
            text-align: center;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #e3f2fd, stop:1 #bbdefb);
            border-color: #8b5cf6;
        }
        QPushButton:pressed {
            background: #c5cae9;
        }
    """)
    
    btn.clicked.connect(lambda checked, pos=position: self.on_shortcut_clicked(pos))
    
    # Context menu
    btn.setContextMenuPolicy(Qt.CustomContextMenu)
    btn.customContextMenuRequested.connect(
        lambda point, pos=position: self.show_shortcut_context_menu(pos, btn.mapToGlobal(point))
    )
    
    return btn
