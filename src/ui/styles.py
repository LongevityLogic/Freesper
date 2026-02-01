class Styles:
    # Colors
    BACKGROUND_DARK = "#1e1e1e"
    TEXT_WHITE = "#ffffff"
    TEXT_GRAY = "#a0a0a0"
    ACCENT_RED = "#ff453a"  # Mac-like red for recording
    ACCENT_BLUE = "#0a84ff" # Mac-like blue for buttons
    BORDER_COLOR = "#3a3a3a"

    # Fonts
    FONT_FAMILY = "Segoe UI, San Francisco, Helvetica Neue, Arial, sans-serif"

    MAIN_WINDOW = f"""
        QMainWindow {{
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2c2c2c, stop:1 #1e1e1e);
            border-radius: 12px;
            border: 1px solid {BORDER_COLOR};
        }}
        QLabel {{
            font-family: "{FONT_FAMILY}";
            color: {TEXT_WHITE};
            font-size: 14px;
            background: transparent;
        }}
        QPushButton {{
            background: transparent;
        }}
    """

    RECORD_BUTTON_IDLE = f"""
        QPushButton {{
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3a3a3a, stop:1 #2c2c2c);
            border: 1px solid #4a4a4a;
            border-radius: 40px; 
            font-size: 32px;
        }}
        QPushButton:hover {{
            background-color: #4a4a4a;
        }}
    """

    RECORD_BUTTON_ACTIVE = f"""
        QPushButton {{
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff5f55, stop:1 {ACCENT_RED});
            border: none;
            border-radius: 40px;
            font-size: 32px;
        }}
        QPushButton:hover {{
            background-color: #ff7066;
        }}
    """

    SETTINGS_WINDOW = f"""
        QDialog {{
            background-color: {BACKGROUND_DARK};
        }}
        QLabel {{
            font-family: "{FONT_FAMILY}";
            color: {TEXT_WHITE};
            font-size: 13px;
        }}
        QLineEdit {{
            background-color: #2c2c2c;
            color: {TEXT_WHITE};
            border: 1px solid {BORDER_COLOR};
            border-radius: 6px;
            padding: 6px;
            selection-background-color: {ACCENT_BLUE};
        }}
        QComboBox {{
            background-color: #2c2c2c;
            color: {TEXT_WHITE};
            border: 1px solid {BORDER_COLOR};
            border-radius: 6px;
            padding: 4px;
        }}
        QCheckBox {{
            color: {TEXT_WHITE};
            font-family: "{FONT_FAMILY}";
            spacing: 8px;
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 1px solid {BORDER_COLOR};
            background-color: #2c2c2c;
        }}
        QCheckBox::indicator:checked {{
            background-color: {ACCENT_BLUE};
            border: 1px solid {ACCENT_BLUE};
        }}
        QPushButton {{
            background-color: {ACCENT_BLUE};
            color: white;
            border-radius: 6px;
            padding: 6px 12px;
            font-weight: 600;
            border: none;
        }}
        QPushButton:hover {{
            background-color: #409cff;
        }}
        QPushButton:pressed {{
            background-color: #0060df;
        }}
    """
