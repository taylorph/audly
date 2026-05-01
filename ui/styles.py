APP_STYLESHEET = """
    QWidget {
        background-color: #08110D;
        color: #F3F1E8;
        font-family: "Helvetica Neue";
    }

    QScrollArea#scrollArea {
        background: transparent;
        border: none;
    }

    QLabel {
        background: transparent;
    }

    QLabel#brandLabel {
        color: #F7F4EA;
        font-size: 14px;
        font-weight: 900;
        font-family: Helvetica, Arial, sans-serif;
    }

    QLabel#title {
        color: #F7F4EA;
        font-size: 46px;
        font-weight: 900;
    }

    QLabel#subtitle {
        color: #B7BFAF;
        font-size: 15px;
        font-weight: 700;
    }

    QLabel#sites {
        color: #7F8A78;
        font-size: 12px;
        font-weight: 600;
    }

    QFrame#card, QFrame#panel {
        background-color: #121B16;
        border: 1px solid #2A372F;
        border-radius: 18px;
    }

    QLabel#fieldLabel {
        color: #E8E4D5;
        font-size: 13px;
        font-weight: 900;
        padding-left: 4px;
        padding-bottom: 1px;
    }

    QLabel#timeHelp {
        color: #8F9A87;
        font-size: 11px;
        font-weight: 700;
    }

    QLineEdit#urlInput, QLineEdit#timeInput, QLineEdit#titleInput {
        background-color: #07100C;
        color: #F7F4EA;
        border: 1px solid #405044;
        border-radius: 20px;
        padding-left: 18px;
        padding-right: 18px;
        font-size: 14px;
        font-weight: 700;
        selection-background-color: #8AA66E;
    }

    QLineEdit#urlInput:focus, QLineEdit#timeInput:focus, QLineEdit#titleInput:focus {
        border: 2px solid #9DBB7D;
    }

    QCheckBox#clipCheckbox, QCheckBox#playlistCheckbox {
        color: #D8D5C7;
        font-size: 12px;
        font-weight: 800;
        spacing: 7px;
    }

    QCheckBox#clipCheckbox::indicator, QCheckBox#playlistCheckbox::indicator {
        width: 16px;
        height: 16px;
        border-radius: 5px;
        border: 1px solid #405044;
        background-color: #07100C;
    }

    QCheckBox#clipCheckbox::indicator:checked, QCheckBox#playlistCheckbox::indicator:checked {
        background-color: #8AA66E;
        border: 1px solid #A8C98A;
    }

    QPushButton#pillButton {
        background-color: #07100C;
        color: #D8D5C7;
        border: 1px solid #405044;
        border-radius: 21px;
        font-size: 13px;
        font-weight: 900;
    }

    QPushButton#pillButton:hover {
        background-color: #1B2A20;
        color: #F7F4EA;
    }

    QPushButton#pillButton:checked {
        background-color: #8AA66E;
        border: 1px solid #A8C98A;
        color: #08110D;
    }

    QLabel#folderDisplay {
        background-color: #07100C;
        color: #B7BFAF;
        border: 1px solid #405044;
        border-radius: 20px;
        padding-left: 18px;
        padding-right: 18px;
        font-size: 13px;
        font-weight: 700;
    }

    QPushButton#secondaryButton {
        background-color: #233122;
        color: #F7F4EA;
        border: 1px solid #4C6047;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 900;
    }

    QPushButton#secondaryButton:hover {
        background-color: #2C3C2A;
    }

    QPushButton#secondaryButton:disabled {
        background-color: #1B241F;
        color: #7A8374;
    }

    QProgressBar#progressBar {
        background: #07100C;
        border: 1px solid #5F6F63;
        border-radius: 9px;
        padding: 2px;
    }

    QProgressBar#progressBar::chunk {
        border-radius: 7px;
        background-color: #A8D5BA;
    }

    QPushButton#primaryButton {
        background-color: #D7E8BF;
        color: #08110D;
        border: none;
        border-radius: 25px;
        font-size: 19px;
        font-weight: 900;
    }

    QPushButton#primaryButton:hover {
        background-color: #E4F0D4;
    }

    QPushButton#primaryButton:disabled {
        background-color: #4D5948;
        color: #9EA693;
    }

    QLabel#status {
        color: #A9B2A0;
        font-size: 13px;
        font-weight: 800;
    }

    QLabel#previewTitle {
        color: #F7F4EA;
        font-size: 16px;
        font-weight: 900;
    }

    QLabel#previewMeta {
        color: #B7BFAF;
        font-size: 12px;
        font-weight: 700;
    }

    QLabel#thumbnailPlaceholder {
        background-color: #07100C;
        color: #8F9A87;
        border: 1px solid #405044;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 800;
    }

    QPlainTextEdit#debugLog {
        background-color: #07100C;
        color: #D8D5C7;
        border: 1px solid #405044;
        border-radius: 12px;
        padding: 10px;
        font-family: Consolas, "Courier New";
        font-size: 11px;
    }

    QFrame#resultPanel {
        background-color: #121B16;
        border: 1px solid #2A372F;
        border-radius: 18px;
    }

    QFrame#resultPanel[state="pending"] {
        border-color: #62715F;
    }

    QFrame#resultPanel[state="success"] {
        border-color: #A8D5BA;
        background-color: #102119;
    }

    QFrame#resultPanel[state="error"] {
        border-color: #D08A7A;
        background-color: #241411;
    }

    QLabel#resultHeading {
        color: #F7F4EA;
        font-size: 15px;
        font-weight: 900;
    }

    QLabel#resultDetails {
        color: #B7BFAF;
        font-size: 12px;
        font-weight: 700;
    }
"""
