def dark_theme_qss() -> str:
    return """
    QWidget{background:#111827;color:#E5E7EB;font-family:Helvetica Neue,Arial;font-size:12px;}
    QMainWindow,QDialog{background:#0B1120;}
    QToolBar{background:#0F172A;border-bottom:1px solid #1F2937;padding:6px;spacing:8px;}
    QPushButton,QToolButton{background:#1F2937;color:#F9FAFB;border:1px solid #374151;border-radius:7px;padding:7px 10px;}
    QPushButton:hover,QToolButton:hover{background:#263244;border-color:#4B5563;}
    QListWidget,QTextEdit,QLineEdit,QComboBox,QSpinBox,QDoubleSpinBox{background:#0F172A;border:1px solid #1F2937;border-radius:6px;padding:4px;selection-background-color:#2563EB;}
    QGroupBox{border:1px solid #1F2937;border-radius:8px;margin-top:10px;padding:8px;font-weight:600;}
    QStatusBar{background:#0F172A;border-top:1px solid #1F2937;}
    QSplitter::handle{background:#1F2937;}
    """
