"""
DeskButler - persoonlijke desktop-assistent voor Windows.

Eén bestand met alle functionaliteit en assets ingebed:
  - Animerende butler (rechtsonder, met lipsync en muis-volgende ogen)
  - Systeemvak met menu
  - Zoekvenster (Shift+V)
  - Browser, e-mail, agenda, snelgids, instellingen

Run met: python deskbutler.py
Bouw met PyInstaller: pyinstaller --onefile --windowed deskbutler.py
"""

# ---------- Stdlib ----------
import sys
import os
import signal
import threading
import time
import random
import math
import json
import re
import sqlite3
import base64
import tempfile
import atexit
import shutil
import subprocess
import stat
import wave
import struct
import locale
import ctypes
import imaplib
import smtplib
import ssl
import poplib
import email
import zipfile
import urllib.request
from email import policy
from email.header import decode_header
from email.message import EmailMessage as _EmailMessage  # alias om botsing met onze class te voorkomen
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from urllib.parse import quote_plus, unquote, quote
from html import escape as html_escape, unescape

# ---------- 3rd-party ----------
import numpy as np
import requests
import feedparser

# ---------- Qt / PySide6 ----------
from PySide6.QtCore import (
    Qt, QTimer, QPoint, QPointF, QRect, QRectF, QSize, QUrl, QThread,
    QPropertyAnimation, QEasingCurve, Property, Signal, QObject, QDate, QTime,
    QByteArray,
)
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QFontMetrics, QPainterPath,
    QCursor, QGuiApplication, QPixmap, QTransform, QIcon, QAction,
    QKeySequence, QShortcut, QTextCharFormat, QDesktopServices,
    QSyntaxHighlighter,
)
from PySide6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QDialog, QDialogButtonBox, QSplitter,
    QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QPlainTextEdit, QLineEdit,
    QPushButton, QTimeEdit, QComboBox, QFileDialog, QMessageBox, QListWidget,
    QListWidgetItem, QSystemTrayIcon, QMenu, QToolBar, QTabWidget, QFrame,
    QCalendarWidget, QTextBrowser, QTextEdit, QSizePolicy, QGraphicsOpacityEffect, QCheckBox,
    QProgressBar, QStatusBar, QAbstractItemView,
    QTreeWidget, QTreeWidgetItem, QInputDialog,
    QScrollArea,
)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineUrlRequestInterceptor, QWebEnginePage

# ---------- Auto-detected extra imports ----------
import ast
import operator
import uuid

# ========================================================================
# Embedded assets (uitgepakt naar tempdir bij opstart)
# ========================================================================

_BUTLER_SVG = r"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 1000" width="100%" height="100%">
  <!--
    DeskButler - butler SVG
    Eyes (370,295) and mouth (400,345) are drawn dynamically by butler_widget.py
    for mouse-following, blinking, and lipsync animation.
    Left arm (with tray) and right arm (with umbrella) are in separate groups
    so they can be transformed for gestures.
  -->

  <!-- KAAL HOOFD & OREN -->
  <g id="head_base">
    <path d="M 330 300 C 330 200, 470 200, 470 300 C 470 370, 330 370, 330 300 Z" fill="#fddcb4" />
    <circle cx="325" cy="310" r="15" fill="#fca484" />
    <circle cx="327" cy="310" r="8" fill="#fddcb4" />
    <circle cx="475" cy="310" r="15" fill="#fca484" />
    <circle cx="473" cy="310" r="8" fill="#fddcb4" />

    <!-- GRIJS HAAR -->
    <path d="M 323 290 C 320 270, 335 250, 340 260 C 335 280, 330 300, 328 320 C 322 315, 322 300, 323 290 Z" fill="#dcdde1" />
    <path d="M 477 290 C 480 270, 465 250, 460 260 C 465 280, 470 300, 472 320 C 478 315, 478 300, 477 290 Z" fill="#dcdde1" />

    <!-- Wenkbrauwen -->
    <path d="M 350 275 Q 370 270 385 280" stroke="#7f8c8d" stroke-width="4" stroke-linecap="round" fill="none" />
    <path d="M 450 275 Q 430 270 415 280" stroke="#7f8c8d" stroke-width="4" stroke-linecap="round" fill="none" />

    <!-- Monocle (blijft op rechteroog) -->
    <circle cx="430" cy="295" r="16" stroke="#f1c40f" stroke-width="3" fill="rgba(255,255,255,0.3)" />
    <path d="M 446 295 Q 465 310 465 330" stroke="#f1c40f" stroke-width="2" fill="none" />

    <!-- Neus -->
    <path d="M 400 280 L 395 320 L 405 320" stroke="#fca484" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" fill="none" />

    <!-- Wang rimpels -->
    <path d="M 345 320 Q 340 330 345 340" stroke="#fca484" stroke-width="2" fill="none" />
    <path d="M 455 320 Q 460 330 455 340" stroke="#fca484" stroke-width="2" fill="none" />
  </g>

  <!-- BODY / KLEDING -->
  <g id="body">
    <!-- Nek -->
    <rect x="380" y="350" width="40" height="50" fill="#fddcb4" />

    <!-- Wit Overhemd & Boord -->
    <polygon points="350,400 450,400 400,460" fill="#ffffff" />
    <polygon points="360,400 385,400 400,430" fill="#ffffff" stroke="#dcdde1" stroke-width="1" />
    <polygon points="440,400 415,400 400,430" fill="#ffffff" stroke="#dcdde1" stroke-width="1" />

    <!-- Zwarte Vlinderdas -->
    <polygon points="380,410 400,420 380,430" fill="#111111" />
    <polygon points="420,410 400,420 420,430" fill="#111111" />
    <circle cx="400" cy="420" r="6" fill="#222222" />

    <!-- Gilet -->
    <polygon points="350,430 450,430 430,600 370,600" fill="#7f8c8d" />
    <circle cx="400" cy="470" r="4" fill="#2c3e50" />
    <circle cx="400" cy="500" r="4" fill="#2c3e50" />
    <circle cx="400" cy="530" r="4" fill="#2c3e50" />
    <circle cx="400" cy="560" r="4" fill="#2c3e50" />

    <!-- Smoking jas -->
    <path d="M 350 400 C 300 420, 260 480, 260 580 L 320 580 L 340 800 L 370 800 L 370 600 Z" fill="#1e272e" />
    <path d="M 450 400 C 500 420, 540 480, 540 580 L 480 580 L 460 800 L 430 800 L 430 600 Z" fill="#1e272e" />
    <polygon points="350,400 380,460 355,520 330,450" fill="#0f1418" />
    <polygon points="450,400 420,460 445,520 470,450" fill="#0f1418" />
  </g>

  <!-- LINKERARM met dienblad -->
  <g id="left_arm">
    <path d="M 275 430 Q 220 480, 190 530" stroke="#1e272e" stroke-width="38" stroke-linecap="round" fill="none" />
    <path d="M 190 530 Q 180 500, 210 470" stroke="#1e272e" stroke-width="34" stroke-linecap="round" fill="none" />
    <path d="M 210 470 L 220 460" stroke="#ffffff" stroke-width="36" stroke-linecap="round" fill="none" />
    <circle cx="225" cy="450" r="16" fill="#ffffff" />
    <ellipse cx="210" cy="430" rx="70" ry="12" fill="#b2bec3" stroke="#dfe6e9" stroke-width="3" />
    <path d="M 190 510 C 185 550, 175 620, 175 660 L 200 660 C 200 620, 205 550, 210 510 Z" fill="#ffffff" opacity="0.9" />
    <path d="M 175 660 L 200 660" stroke="#b2bec3" stroke-width="2" />
  </g>

  <!-- RECHTERARM met paraplu -->
  <g id="right_arm">
    <!-- Paraplu stok -->
    <rect x="545" y="420" width="10" height="480" fill="#4a3728" rx="5" />
    <path d="M 530 425 C 530 390, 570 390, 570 420" stroke="#4a3728" stroke-width="12" stroke-linecap="round" fill="none" />
    <path d="M 542 900 L 558 900 L 550 915 Z" fill="#7f8c8d" />
    <!-- Arm -->
    <path d="M 525 430 Q 560 480, 560 540" stroke="#1e272e" stroke-width="38" stroke-linecap="round" fill="none" />
    <path d="M 560 540 Q 560 520, 550 470" stroke="#1e272e" stroke-width="34" stroke-linecap="round" fill="none" />
    <path d="M 550 470 L 550 460" stroke="#ffffff" stroke-width="36" stroke-linecap="round" fill="none" />
    <circle cx="550" cy="450" r="16" fill="#ffffff" />
  </g>

  <!-- BROEK & SCHOENEN -->
  <g id="legs">
    <rect x="370" y="600" width="30" height="260" fill="#2c3e50" />
    <rect x="400" y="600" width="30" height="260" fill="#2c3e50" />
    <line x1="375" y1="600" x2="375" y2="860" stroke="#34495e" stroke-width="2" />
    <line x1="385" y1="600" x2="385" y2="860" stroke="#34495e" stroke-width="2" />
    <line x1="395" y1="600" x2="395" y2="860" stroke="#34495e" stroke-width="2" />
    <line x1="405" y1="600" x2="405" y2="860" stroke="#34495e" stroke-width="2" />
    <line x1="415" y1="600" x2="415" y2="860" stroke="#34495e" stroke-width="2" />
    <line x1="425" y1="600" x2="425" y2="860" stroke="#34495e" stroke-width="2" />

    <path d="M 370 850 C 350 850, 330 870, 330 880 C 330 890, 360 890, 385 890 C 385 870, 380 850, 370 850 Z" fill="#0f1418" />
    <ellipse cx="350" cy="885" rx="15" ry="5" fill="#57606f" opacity="0.3" />
    <path d="M 430 850 C 450 850, 470 870, 470 880 C 470 890, 440 890, 415 890 C 415 870, 420 850, 430 850 Z" fill="#0f1418" />
    <ellipse cx="450" cy="885" rx="15" ry="5" fill="#57606f" opacity="0.3" />
  </g>
</svg>
"""

_ICO_B64 = (
    "AAABAAEAICAYAAAAAACoDAAAFgAAACgAAAAgAAAAQAAAAAEAGAAAAAAAAAwAAAAAAAAAAAAAAAAA"
    "AAAAAAArLCwrLCwrLCwrLCwrLCwrLCwrLCwrLCwrLCwrLCwrLCwrLCwrLCwrLCwrLCwrLCwrLCwr"
    "LCwrLCwrLCwrLCwrLCwrLCwrLCwrLCwrLCwrLCwrLCwrLCwrLCwrLCwrLCwfISEfISEfISEfISEf"
    "ISEfISEfISEfISEfISEfISEfISEfISEfISEfISEfISEfISEfISEfISEfISEfISEgISEfICAfICAg"
    "ISEfISEfISEfISEfISEfISEfISEfISEfISEdHh4dHh4dHh4dHh4dHh4dHh4dHh4dHh4dHh4dHh4d"
    "Hh4dHh4dHh4dHh4dHh4dHx8dHh4dHh8dHh8dHh4aGhooKSkpKyoaGhodHh4dHh4dHh4dHh4dHh4d"
    "Hh4dHh4dHh4eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8dHh8dHh4cHh4gHx0dGxkY"
    "GhsZGRghHhsdHh0cHBsgIycgJCgcHBseHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8e"
    "Hx8eHx8eHx8eHx8eHx8eHx8dHh4dHh4dHh4fHx8hISEdGxkZFA8zKyUlHxkYFREhIB8fHx0gIycf"
    "IyccHBseHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8dHh4d"
    "Hh4fHx8iISAjIiEjIiEeHx8vKiRdRjNKOi0eHyAiISAiIB8kJikiJSkdHRwdHh4dHh4eHx8eHx8e"
    "Hx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8dHh4dHh4hICAjIiEjIiEjIiEiISEgHx41"
    "LSVYQzJKOi0kIh8hIB8iHx8kJikkJioiIB4fHx8cHh4dHh4eHx8eHx8eHx8eHx8eHx8eHx8eHx8e"
    "Hx8eHx8eHx8eHx8dHh4dHh4iISAjIiEjIiEjIiEjIiEgICEkIh06LyNWQjJLOysrJR0iISAiIB8k"
    "JikkJSoiIB8jIiEgIB8cHR0dHh4eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8dHh4dHh4iISAj"
    "IiEjIiEjIiEjIiEjIiEgISElIR46LyRXQzJLOywrJB4jIiAiIB8kJikkJiohHx8jIiEjIiEfHx8c"
    "HR0dHh4eHx8eHx8eHx8eHx8eHx8eHx8eHx8dHh4dHh4hICAjIiEjIiEjIiEjIiEjIiEjIiEhISEm"
    "Ih46LyRXQzJLOy0sJB4jISAiIB8kJikkJioiIB8jIiEjIiEjISAeHx8cHR0eHx8eHx8eHx8eHx8e"
    "Hx8eHx8dHh4cHR0fHx8jIiEjIiEgHx4dHBsjIiEjIiEjIiEiISEnIx46LyRXQzJLOy0rJR4kIiAh"
    "IB8kJikkJioiIB8jIiEjIiEjIiEiISAdHh4dHh4eHx8eHx8eHx8eHx8eHx8dHh4dHh4iISAjIiEh"
    "IB8nJiUtLCwhIB8jIiEiISEhICEoIx05LiRXQzJLOy0sJh4lIiAhIB8kJikkJioiIB8jIiEjIiEj"
    "IiEjIiEfHx8cHR0dHh4eHx8eHx8eHx8eHx8cHR0fHx8jIiEjIiEWFRRTU1KxsbAWFRQjIiEhICEh"
    "ICAoIxw4LiRXQzJLOy0tJh4mIiAgIB8kJikkJioiIB8jIiEjIiEjIiEjIiEiISAdHh4dHh4eHx8e"
    "Hx8eHx8dHh4dHh4hIB8jIiEjIiEXFhVLS0q7uroZGBciISEhICEiISApJB03KyFSPCtHNigtJh4n"
    "Ix8gHx8jJSkkJSoiIB8jIiEjIiEjIiEjIiEjIiEfHx8cHR0eHx8eHx8eHx8cHR0eHh8iISAjIiEj"
    "IiEaGRg7Ojm2tbUeHRwhIB8iISAjIh8mHxhHQDeHgXRtZ1wrIxsnIx4hIB4kJigjJSohHx8jIiEj"
    "IiEjIiEjIiEjIiEgIB8cHR0eHx8eHx8eHx8dHh4fHx4jIiEjIiEjIiEdHBstLCuysrIlJSQhHx0s"
    "Jh4tJh4kHBRWUkmcnJGEg3ktJh4qJBwsJRwqKCcjJikhIB4iISEjIiEjIiEjIiEjIiEhISAdHh4d"
    "Hh4eHx8eHx8dHh4fIB8jIiEjIiEjIiEgIB8iIB62tLIzMjIeHBouJh4uJx0lHRVfW1KUk4eHhXo0"
    "LSUqIhouJhsrKSYrKSgjIB4iISEjIiEjIiEjIiEjIiEiIB8eHx8cHR0eHx8eHx8dHh4gICAjIiEj"
    "IiEjIiEiISEhHhp/enMuKiYdHBwsJh8uJx4jHBRnZFqUkoeNjIE3MSkoIRkuJhwjIR8kIh8kIR4h"
    "ICEjIiEjIiEjIiEjIiEiISAeHx8dHh4eHx8eHx8dHh4hICAjIiEjIiEjIiEhICEcGhhTTUZdV1Aa"
    "GBUqJR8wKB8eGBFGQz2Ylop6eW8eGhQsJR0qIhlCQkFFRUUfHRsiISEjIiEjIiEjIiEjIiEjIiEe"
    "Hx8dHh4eHx8eHx8dHh4gICAjIiEjIiEkIyIdHBwAAACQj5D///8qJB0ZFRAxKSEbFhEcGBSTkYVX"
    "VEwKBgMsJR0jGxKZmpygo6gZFxUjIiEjIiEjIiEjIiEjIiEiISAeHx8dHh4eHx8eHx8dHh4fIB8j"
    "IiEjIiEbGhk/PjySj4mopJ3r6OGtqJ9MRj8kHxgXEQs1My6VlIlvbmYQDAgqIxwmIBlYV1dUV1sc"
    "GxkiISAjIiEjIiEjIiEjIiEiIB8eHx8cHR0eHx8eHx8dHh4fHx4jIiEjIiEfHh0wLi1eXFhmY19Y"
    "VVFcWlY5NjIeHRwcFxKXlZO2ubu9vb5KRkEbGBQkIyEfJSwbIywjIyIiIR8jIiEjIiEjIiEjIiEh"
    "ISAdHh4dHh4eHx8eHx8cHR0eHh8iISAjIiEjIiEfHh0WFRUUFBMUFBMWFRUeHR0jIiEdGxgmIB2A"
    "lKVOU1kcFhEfHRwiISAiJCYjJSgiIR8iISEjIiEjIiEjIiEjIiEgIB8cHR0eHx8eHx8eHx8dHh4d"
    "Hh4hIB8jIiEjIiEjIiEjIiEjIiEjIiEjIiEjIiEbGRYrLjKCnbCUttiWtc5ZZ3MXFhUiIR8iIR8i"
    "IR8jIiEjIiEjIiEjIiEjIiEjIiEfHx8cHR0eHx8eHx8eHx8eHx8cHR0fHx8jIiEjIiEjIiEjIiEj"
    "IiEjIiEjIiEZFhBCSFupyvLC7v+23v+26f+v6P95kLceGxshIB4jIiEjIiEjIiEjIiEjIiEjIiEi"
    "ISAdHh4dHh4eHx8eHx8eHx8eHx8dHh4dHh4iISAjIiEjIiEjIiEjIiEjIiEjIiEaGRc3NDbJ4vio"
    "yd6ozeyZyuG46v2MkZwSEA4iISAjIiEjIiEjIiEjIiEjIiEjIiEfHx8cHR0dHh4eHx8eHx8eHx8e"
    "Hx8dHh4cHR0fHx8jIiEjIiEjIiEjIiEjIiEjIiEhICAbFhGIlJzE7v+85P+65/+31+tFQT4YFhUj"
    "IiEjIiEjIiEjIiEjIiEjIiEiISAdHh4dHh4eHx8eHx8eHx8eHx8eHx8eHx8dHh4dHh4hICAjIiEj"
    "IiEjIiEjIiEjIiEjIiEfHRwXFRN0ipmt0+afv9E8QkgUEQ4kIyIjIiEjIiEjIiEjIiEjIiEjISAe"
    "Hx8cHR0eHx8eHx8eHx8dHh4dHh4dHh4dHh4eHh8cHh4dHh4iISAjIiEjIiEjIiEjIiEjIiEjIiEg"
    "Hx0XExAlJCMdGhkaFxQkIyIjIiEjIiEjIiEjIiEjIiEjISAfHx8cHR0dHh4dHh4dHh4dHh4dHh4d"
    "Hh4dHh4dHh4dHh4dHh4cHR0dHh4fHx8fIB8gIB8gIB8gIB8gIB8gIB8fIB8cGxoeHh0gIB8gIB8g"
    "IB8gIB8gIB8fIB8gIB8eHx4cHR0dHh4dHh4dHh4dHh4dHh4dHh4dHh4dHh4dHh4dHh4dHh4dHx4d"
    "Hh4dHh4dHh4dHh4dHh4dHh4dHh4dHh4dHh4dHh4dHh4dHh4dHh4dHh4dHh4dHh4dHh4dHh4dHh4d"
    "Hh4dHx4dHh4dHh4dHh4dHh4eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8e"
    "Hx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8eHx8A"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAA=="
)

_ASSETS_TEMPDIR = None

def _extract_assets() -> Path:
    """Pak de embedded assets uit naar een tijdelijke map en geef het pad terug."""
    global _ASSETS_TEMPDIR
    if _ASSETS_TEMPDIR is not None and _ASSETS_TEMPDIR.exists():
        return _ASSETS_TEMPDIR
    _ASSETS_TEMPDIR = Path(tempfile.mkdtemp(prefix="deskbutler_assets_"))
    (_ASSETS_TEMPDIR / "butler.svg").write_text(_BUTLER_SVG, encoding="utf-8")
    (_ASSETS_TEMPDIR / "deskbutler.ico").write_bytes(base64.b64decode(_ICO_B64))
    atexit.register(_cleanup_assets)
    return _ASSETS_TEMPDIR


def _cleanup_assets():
    if _ASSETS_TEMPDIR and _ASSETS_TEMPDIR.exists():
        shutil.rmtree(_ASSETS_TEMPDIR, ignore_errors=True)


# Maak ASSETS_DIR globaal beschikbaar (vervangt de oude Path-resolution)
ASSETS_DIR = _extract_assets()
SVG_PATH = ASSETS_DIR / "butler.svg"
ICON_PATH = ASSETS_DIR / "deskbutler.ico"


# ========================================================================
# CONFIG  (was: config.py)
# ========================================================================

def get_app_dir() -> Path:
    """Map waar het programma staat (werkt voor zowel .py als PyInstaller .exe)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def get_config_dir() -> Path:
    """Map voor instellingen en data. Standaard: <app>/data."""
    cfg = get_app_dir() / "data"
    try:
        cfg.mkdir(parents=True, exist_ok=True)
        # Schrijftest
        test = cfg / ".write_test"
        test.write_text("x")
        test.unlink()
    except OSError:
        # Geen schrijfrechten in app-map (bv. Program Files): val terug op tempdir
        print(f"[config] Geen schrijfrechten in {cfg}, val terug op tempdir.")
        cfg = Path(tempfile.gettempdir()) / "DeskButler_data"
        cfg.mkdir(parents=True, exist_ok=True)
    return cfg


def _migrate_from_appdata():
    """Eenmalige migratie van oude %APPDATA%\\DeskButler locatie."""
    if os.name != "nt":
        return
    appdata = os.environ.get("APPDATA")
    if not appdata:
        return
    old_dir = Path(appdata) / "DeskButler"
    if not old_dir.exists():
        return
    new_dir = get_config_dir()
    # Als nieuwe map al actief in gebruik is: niet migreren
    if (new_dir / "config.json").exists():
        return
    # Kopieer alle bestanden uit oude map
    print(f"[migrate] Verplaats data van {old_dir} naar {new_dir}")
    for item in old_dir.iterdir():
        try:
            target = new_dir / item.name
            if item.is_file() and not target.exists():
                shutil.copy2(item, target)
            elif item.is_dir() and not target.exists():
                shutil.copytree(item, target)
        except Exception as e:
            print(f"[migrate] kon {item.name} niet kopiëren: {e}")
    print("[migrate] klaar - de oude map blijft staan en kunt u handmatig verwijderen.")


# Voer migratie uit voordat verdere setup gebeurt
_migrate_from_appdata()

CONFIG_FILE = get_config_dir() / "config.json"
DATA_DIR = get_config_dir() / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DEFAULTS = {
    "language": "auto",
    "voice_name": "Linda",
    "voice_speed": 0.9,
    "voice_pitch": -1.0,
    "voice_volume": 0.85,
    "use_neuvoice": True,
    "butler_position": "bottom-right",
    "butler_scale": 1.0,
    "high_contrast": True,
    "font_size": 16,
    "hotkey_search": "shift+v",
    "hotkey_read_clipboard": "ctrl+shift+l",
    "news_country": "nl",
    "default_search_engine": "duckduckgo",  # duckduckgo, bing, google, startpage, qwant, brave
    "use_ollama": False,
    "ollama_url": "http://localhost:11434",
    "ollama_model": "",
    "ollama_decision": "",  # "", "yes", "later", "no" — gebruikerskeuze voor de intro
    "ollama_last_seen_available": False,  # was Ollama bij vorige start beschikbaar?
    "character_id": "alfred",
    "character_custom_image": "",  # pad naar eigen PNG/JPG (optioneel)
    "email_accounts": [],
    "mail_check_interval_min": 5,
    "adblock_enabled": True,
    "auto_accept_cookies": True,
    "last_briefing_date": "",
    "first_run": True,
    "user_name": "",
    "ollama_auto_start": False,
    "ollama_preload_at_startup": False,
    "voice_input_enabled": False,  # microfoon-luisteraar aan/uit
    # Per-karakter stem-overrides. Sleutel = character_id, waarde = dict met
    # voice_name/voice_pitch/voice_speed/voice_volume. Lege dict = globaal.
    "character_voices": {},
}


class Config:
    """Centrale instellingen-manager."""

    def __init__(self):
        self._data = dict(DEFAULTS)
        self.load()

    def load(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                for k, v in DEFAULTS.items():
                    if k not in saved:
                        saved[k] = v
                self._data = saved
            except (json.JSONDecodeError, OSError):
                self._data = dict(DEFAULTS)

    def save(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except OSError as e:
            print(f"[config] Kon niet opslaan: {e}")

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value
        self.save()

    def update(self, **kwargs):
        self._data.update(kwargs)
        self.save()


config = Config()


# ========================================================================
# LOGGING (persistent log naar bestand + console)  (was: core/logging_setup.py)
# ========================================================================

def get_log_dir() -> Path:
    """
    Geef de map terug waarin logs worden geschreven.

    Strategie:
      1. Eerste keus: de map waarin de app staat (naast start.bat /
         deskbutler.py). Intuïtief voor de gebruiker — kan hij gewoon
         in de map openen waar hij ook het programma vandaan opstart.
      2. Fallback: %APPDATA%\\DeskButler (Windows) of ~/.deskbutler
         als de app-map niet schrijfbaar is (bv. C:\\Program Files
         vereist administrator-rechten).
    """
    # ----- Probeer eerst de app-map -----
    try:
        if getattr(sys, "frozen", False):
            # PyInstaller / Nuitka bundle
            app_dir = Path(sys.executable).resolve().parent
        else:
            # Python script — argv[0] is het scriptpad
            app_dir = Path(sys.argv[0]).resolve().parent
        # Test of we ernaar mogen schrijven (zonder rotzooi achter te laten)
        test_file = app_dir / ".deskbutler_write_test"
        try:
            test_file.write_text("ok")
            test_file.unlink()
            return app_dir
        except Exception:
            # Geen schrijfrechten — val terug op APPDATA
            pass
    except Exception:
        pass

    # ----- Fallback: APPDATA -----
    if os.name == "nt":
        appdata = os.environ.get("APPDATA")
        if appdata:
            fallback = Path(appdata) / "DeskButler"
            try:
                fallback.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass
            return fallback
    return Path.home() / ".deskbutler"


def get_log_path() -> Path:
    """Pad naar het huidige log-bestand."""
    return get_log_dir() / "deskbutler.log"


class _TeeStream:
    """Schrijft naar twee streams tegelijk (console + log-bestand)."""

    def __init__(self, original, file):
        # original kan None zijn (bij pythonw.exe is sys.stdout None)
        self.original = original
        self.file = file

    def write(self, text):
        if self.original is not None:
            try:
                self.original.write(text)
            except Exception:
                pass
        try:
            self.file.write(text)
            self.file.flush()  # belangrijk: direct doorschrijven
        except Exception:
            pass

    def flush(self):
        if self.original is not None:
            try:
                self.original.flush()
            except Exception:
                pass
        try:
            self.file.flush()
        except Exception:
            pass

    def isatty(self):
        # Sommige libs vragen dit; doen alsof we geen terminal zijn
        return False


def _rotate_logs(log_path: Path):
    """Verschuif log -> log.1 -> log.2, bewaar laatste 3 sessies."""
    try:
        log_dir = log_path.parent
        log2 = log_dir / "deskbutler.log.2"
        log1 = log_dir / "deskbutler.log.1"
        # Oudste weg
        if log2.exists():
            try:
                log2.unlink()
            except Exception:
                pass
        # log.1 -> log.2
        if log1.exists():
            try:
                log1.rename(log2)
            except Exception:
                pass
        # log -> log.1
        if log_path.exists():
            try:
                log_path.rename(log1)
            except Exception:
                pass
    except Exception as e:
        # Logging mag NOOIT de opstart breken
        try:
            print(f"[logging] Log-rotatie faalde: {e}")
        except Exception:
            pass


_log_file = None  # globale referentie zodat het bestand open blijft


def setup_logging() -> Path | None:
    """
    Zet logging op: alle print() en errors gaan vanaf nu ook naar bestand.
    Returns: pad naar log-bestand, of None bij fout.
    """
    global _log_file
    try:
        log_dir = get_log_dir()
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "deskbutler.log"

        # Roteer oude logs
        _rotate_logs(log_path)

        # Open nieuw log-bestand
        # line-buffered (buffering=1) zodat regels meteen worden weggeschreven
        _log_file = open(log_path, "w", encoding="utf-8", buffering=1)

        # Header met basis-info
        _log_file.write(f"=== DeskButler log gestart {datetime.now().isoformat()} ===\n")
        try:
            _log_file.write(f"Log-locatie: {log_path}\n")
        except Exception:
            pass
        try:
            _log_file.write(f"Python: {sys.version.splitlines()[0]}\n")
        except Exception:
            pass
        try:
            _log_file.write(f"Platform: {sys.platform}\n")
        except Exception:
            pass
        try:
            _log_file.write(f"Werkmap: {os.getcwd()}\n")
        except Exception:
            pass
        _log_file.write("=" * 60 + "\n")
        _log_file.flush()

        # Vervang stdout/stderr met Tee versies
        # Belangrijk: bij pythonw.exe zijn deze None — dan schrijven we
        # alleen naar bestand, wat ook prima is.
        sys.stdout = _TeeStream(sys.stdout, _log_file)
        sys.stderr = _TeeStream(sys.stderr, _log_file)

        return log_path
    except Exception as e:
        # Logging mag NOOIT de app stuk maken
        try:
            print(f"[logging] Setup faalde: {e}")
        except Exception:
            pass
        return None


def close_logging():
    """Sluit het log-bestand netjes af bij quit."""
    global _log_file
    try:
        if _log_file is not None:
            _log_file.write(f"=== DeskButler log afgesloten {datetime.now().isoformat()} ===\n")
            _log_file.flush()
            _log_file.close()
            _log_file = None
    except Exception:
        pass


def open_log_in_editor():
    """
    Open het log-bestand in de standaard tekst-editor van het OS.
    Returns True bij succes.
    """
    try:
        log_path = get_log_path()
        if not log_path.exists():
            return False
        if os.name == "nt":
            os.startfile(str(log_path))
        elif sys.platform == "darwin":
            import subprocess
            subprocess.Popen(["open", str(log_path)])
        else:
            import subprocess
            subprocess.Popen(["xdg-open", str(log_path)])
        return True
    except Exception as e:
        print(f"[logging] Open in editor faalde: {e}")
        return False


def open_log_folder():
    """Open de map waar de logs staan (Verkenner / Finder / etc)."""
    try:
        log_dir = get_log_dir()
        if os.name == "nt":
            os.startfile(str(log_dir))
        elif sys.platform == "darwin":
            import subprocess
            subprocess.Popen(["open", str(log_dir)])
        else:
            import subprocess
            subprocess.Popen(["xdg-open", str(log_dir)])
        return True
    except Exception as e:
        print(f"[logging] Open map faalde: {e}")
        return False


# ========================================================================
# LANGUAGE  (was: core/language.py)
# ========================================================================

# Neuvoice ondersteunde talen (ISO 639-1 codes)
NEUVOICE_LANGS = {
    "en", "ko", "ja", "ar", "bg", "cs", "da", "de", "el", "es",
    "et", "fi", "fr", "hi", "hr", "hu", "id", "it", "lt", "lv",
    "nl", "pl", "pt", "ro", "ru", "sk", "sl", "sv", "tr", "uk", "vi",
}

# Fallback naar 'en' als taal niet ondersteund wordt
FALLBACK_LANG = "en"


def _windows_locale() -> str:
    """Vraag Windows direct om de gebruikersvoorkeurstaal."""
    try:
        windll = ctypes.windll.kernel32
        lcid = windll.GetUserDefaultUILanguage()
        # Tabel met meest voorkomende LCID -> taalcode
        lcid_map = {
            0x0413: "nl", 0x0813: "nl",   # Nederlands (NL, BE)
            0x0409: "en", 0x0809: "en",   # English (US, UK)
            0x0407: "de", 0x0807: "de",   # Duits
            0x040C: "fr", 0x080C: "fr",   # Frans
            0x0410: "it",                  # Italiaans
            0x040A: "es", 0x080A: "es",   # Spaans
            0x0416: "pt", 0x0816: "pt",   # Portugees
            0x0419: "ru",                  # Russisch
            0x0415: "pl",                  # Pools
            0x0411: "ja",                  # Japans
            0x0412: "ko",                  # Koreaans
            0x0401: "ar",                  # Arabisch
            0x041D: "sv",                  # Zweeds
            0x0406: "da",                  # Deens
            0x040B: "fi",                  # Fins
            0x0414: "no",                  # Noors (niet in Neuvoice -> fallback)
            0x041F: "tr",                  # Turks
        }
        if lcid in lcid_map:
            return lcid_map[lcid]
        # primary language id (laatste 10 bits)
        primary = lcid & 0x3FF
        primary_map = {
            0x13: "nl", 0x09: "en", 0x07: "de", 0x0C: "fr",
            0x10: "it", 0x0A: "es", 0x16: "pt", 0x19: "ru",
            0x15: "pl", 0x11: "ja", 0x12: "ko", 0x01: "ar",
            0x1D: "sv", 0x06: "da", 0x0B: "fi", 0x1F: "tr",
        }
        return primary_map.get(primary, FALLBACK_LANG)
    except Exception:
        return ""


def detect_language() -> str:
    """
    Geeft de taalcode terug die we moeten gebruiken.
    Als config 'language' op 'auto' staat, detecteer Windows-taal.
    """
    forced = config.get("language", "auto")
    if forced and forced != "auto":
        return forced if forced in NEUVOICE_LANGS else FALLBACK_LANG

    # Probeer eerst Windows API
    lang = _windows_locale()

    # Fallback: Python locale module
    if not lang:
        try:
            loc = locale.getdefaultlocale()[0]  # bv. 'nl_NL'
            if loc:
                lang = loc.split("_")[0].lower()
        except Exception:
            lang = ""

    if not lang or lang not in NEUVOICE_LANGS:
        lang = FALLBACK_LANG

    return lang


def language_name(code: str) -> str:
    """Geeft de naam van een taal in het Nederlands."""
    names = {
        "nl": "Nederlands", "en": "Engels", "de": "Duits",
        "fr": "Frans", "es": "Spaans", "it": "Italiaans",
        "pt": "Portugees", "ru": "Russisch", "pl": "Pools",
        "ja": "Japans", "ko": "Koreaans", "ar": "Arabisch",
        "sv": "Zweeds", "da": "Deens", "fi": "Fins", "tr": "Turks",
    }
    return names.get(code, code.upper())


if __name__ == "__main__":
    print(f"Gedetecteerde taal: {detect_language()}")


# ========================================================================
# I18N  (was: core/i18n.py)
# ========================================================================

# Alle UI-teksten per taal. Voor talen die hier niet staan valt het systeem
# automatisch terug op Engels.
TRANSLATIONS = {
    "nl": {
        # App
        "app_name": "DeskButler",
        "greeting_morning": "Goedemorgen, meneer. Waarmee mag ik u helpen?",
        "greeting_afternoon": "Goedemiddag. Wat kan ik voor u doen?",
        "greeting_evening": "Goedenavond. Tot uw dienst.",
        "ready": "Tot uw dienst.",
        "butler_name": "Alfred",
        "first_run_intro": (
            "Goedendag. Mijn naam is Alfred, uw nieuwe butler. "
            "Het is mij een genoegen u van dienst te zijn. "
            "Druk op shift plus V om mij iets te vragen, of klik op mij wanneer u mij nodig heeft. "
            "Rechtsonder bij de klok vindt u mijn menu met alle opties. "
            "Voor een korte rondleiding kunt u de snelgids openen."
        ),
        "about_text": (
            "DeskButler 1.2\n\n"
            "Uw persoonlijke butler Alfred staat tot uw dienst.\n"
            "Een sprekende karakter-assistent gecombineerd met "
            "e-mail, browser, agenda en zoekfunctionaliteit.\n\n"
            "Stem: Neuvoice (CPU-vriendelijk)."
        ),
        # Tray menu
        "menu_search": "Zoeken (Shift+V)",
        "menu_email": "E-mail openen",
        "menu_browser": "Browser openen",
        "menu_calendar": "Agenda openen",
        "menu_todo": "Te-doen lijst",
        "menu_quickguide": "Snelgids",
        "menu_settings": "Instellingen",
        "menu_about": "Over DeskButler",
        "menu_quit": "Afsluiten",
        # Search window
        "search_title": "Wat kan ik voor u opzoeken?",
        "search_placeholder": "Stel een vraag, type een programma-naam, of zeg \"weer\" of \"nieuws\"...",
        "btn_ask": "Vraag",
        "btn_cancel": "Annuleren",
        "btn_yes": "Ja",
        "btn_no": "Nee",
        "show_in_browser": "Wilt u dit in de browser zien?",
        "no_results": "Helaas heb ik daar niets over kunnen vinden.",
        "searching": "Ik ben aan het zoeken...",
        "opening_app": "Ik open {name} voor u.",
        "app_not_found": "Het programma {name} kon ik niet vinden.",
        # Weather
        "weather_for": "Het weer voor {city}",
        "weather_now": "Het is nu {temp} graden. {desc}.",
        "weather_unavailable": "Het weer is op dit moment niet beschikbaar.",
        # News
        "news_today": "Het nieuws van vandaag",
        "news_unavailable": "Ik kan op dit moment geen nieuws ophalen.",
        # Browser
        "browser_title": "Browser",
        "browser_url_placeholder": "Voer een webadres in...",
        "btn_back": "Terug",
        "btn_forward": "Vooruit",
        "btn_refresh": "Vernieuwen",
        "btn_home": "Begin",
        # Email
        "email_title": "E-mail",
        "email_add_account": "Account toevoegen",
        "email_compose": "Nieuw bericht",
        "email_reply": "Beantwoorden",
        "email_forward": "Doorsturen",
        "email_delete": "Verwijderen",
        "email_refresh": "Vernieuwen",
        "email_inbox": "Postvak in",
        "email_sent": "Verzonden",
        "email_drafts": "Concepten",
        "email_no_account": "U heeft nog geen e-mailaccount ingesteld. Klik op 'Account toevoegen' om te beginnen.",
        "email_from": "Van",
        "email_to": "Aan",
        "email_subject": "Onderwerp",
        "email_send": "Verzenden",
        "email_sent_ok": "Uw bericht is verzonden.",
        "email_send_error": "Er ging iets mis bij het verzenden.",
        # Calendar / reminders
        "calendar_title": "Agenda",
        "calendar_add": "Herinnering toevoegen",
        "calendar_time": "Tijd",
        "calendar_text": "Wat moet ik onthouden?",
        "calendar_save": "Opslaan",
        "calendar_no_reminders": "U heeft geen herinneringen staan.",
        "reminder_title": "Herinnering",
        # Quick guide
        "guide_title": "Snelgids",
        "guide_intro": "Welkom bij DeskButler. Hier zijn de belangrijkste functies:",
        # Errors
        "error_generic": "Er ging iets mis: {error}",
        "no_network": "Ik heb geen internetverbinding.",
        # Mail checker
        "new_mail_one": "U heeft een nieuw bericht in {account}.",
        "new_mail_many": "U heeft {count} nieuwe berichten in {account}.",
        # Settings tabs
        "settings_voice": "Stem",
        "settings_mail": "E-mail check",
        "settings_mail_intro": "Hoe vaak moet ik kijken of er nieuwe e-mail is?",
        "settings_mail_off": "Uit (geen automatische check)",
        "settings_mail_every": "Elke {n} minuten",
        "settings_mail_every_one": "Elke minuut",
        # Browser settings
        "settings_browser": "Browser",
        "settings_browser_intro": "Extra functies voor de ingebouwde browser:",
        "settings_adblock": "Reclames blokkeren",
        "settings_cookies": "Cookie-meldingen automatisch accepteren",
        "settings_toggle_on": "AAN",
        "settings_toggle_off": "UIT",
    },
    "en": {
        "app_name": "DeskButler",
        "greeting_morning": "Good morning, sir. How may I assist you?",
        "greeting_afternoon": "Good afternoon. What can I do for you?",
        "greeting_evening": "Good evening. At your service.",
        "ready": "At your service.",
        "butler_name": "Alfred",
        "first_run_intro": (
            "Good day. My name is Alfred, your new butler. "
            "It is my pleasure to be of service. "
            "Press shift plus V to ask me something, or click on me whenever you need me. "
            "You will find my menu near the clock on the right. "
            "For a short introduction, please open the quick guide."
        ),
        "about_text": (
            "DeskButler 1.2\n\n"
            "Your personal butler Alfred is at your service.\n"
            "A speaking character assistant combined with "
            "email, browser, calendar and search.\n\n"
            "Voice: Neuvoice (CPU-friendly)."
        ),
        "menu_search": "Search (Shift+V)",
        "menu_email": "Open email",
        "menu_browser": "Open browser",
        "menu_calendar": "Open calendar",
        "menu_todo": "To-do list",
        "menu_quickguide": "Quick guide",
        "menu_settings": "Settings",
        "menu_about": "About DeskButler",
        "menu_quit": "Quit",
        "search_title": "What may I look up for you?",
        "search_placeholder": "Ask a question, type a program name, or say \"weather\" or \"news\"...",
        "btn_ask": "Ask",
        "btn_cancel": "Cancel",
        "btn_yes": "Yes",
        "btn_no": "No",
        "show_in_browser": "Would you like to see this in the browser?",
        "no_results": "I'm afraid I couldn't find anything.",
        "searching": "Searching...",
        "opening_app": "Opening {name} for you.",
        "app_not_found": "I couldn't find the program {name}.",
        "weather_for": "Weather for {city}",
        "weather_now": "It's currently {temp} degrees. {desc}.",
        "weather_unavailable": "Weather is not available at the moment.",
        "news_today": "Today's news",
        "news_unavailable": "I can't fetch news right now.",
        "browser_title": "Browser",
        "browser_url_placeholder": "Enter a web address...",
        "btn_back": "Back",
        "btn_forward": "Forward",
        "btn_refresh": "Refresh",
        "btn_home": "Home",
        "email_title": "Email",
        "email_add_account": "Add account",
        "email_compose": "New message",
        "email_reply": "Reply",
        "email_forward": "Forward",
        "email_delete": "Delete",
        "email_refresh": "Refresh",
        "email_inbox": "Inbox",
        "email_sent": "Sent",
        "email_drafts": "Drafts",
        "email_no_account": "You have no email account configured yet. Click 'Add account' to begin.",
        "email_from": "From",
        "email_to": "To",
        "email_subject": "Subject",
        "email_send": "Send",
        "email_sent_ok": "Your message has been sent.",
        "email_send_error": "Something went wrong while sending.",
        "calendar_title": "Calendar",
        "calendar_add": "Add reminder",
        "calendar_time": "Time",
        "calendar_text": "What should I remember?",
        "calendar_save": "Save",
        "calendar_no_reminders": "You have no reminders.",
        "reminder_title": "Reminder",
        "guide_title": "Quick guide",
        "guide_intro": "Welcome to DeskButler. Here are the main features:",
        "error_generic": "Something went wrong: {error}",
        "no_network": "I have no internet connection.",
        "new_mail_one": "You have one new message in {account}.",
        "new_mail_many": "You have {count} new messages in {account}.",
        "settings_voice": "Voice",
        "settings_mail": "Mail check",
        "settings_mail_intro": "How often should I check for new email?",
        "settings_mail_off": "Off (no automatic check)",
        "settings_mail_every": "Every {n} minutes",
        "settings_mail_every_one": "Every minute",
        "settings_browser": "Browser",
        "settings_browser_intro": "Extra features for the built-in browser:",
        "settings_adblock": "Block advertisements",
        "settings_cookies": "Automatically accept cookie banners",
        "settings_toggle_on": "ON",
        "settings_toggle_off": "OFF",
    },
    "de": {
        "app_name": "DeskButler",
        "greeting_morning": "Guten Morgen. Womit darf ich Ihnen behilflich sein?",
        "greeting_afternoon": "Guten Tag. Was kann ich für Sie tun?",
        "greeting_evening": "Guten Abend. Zu Ihren Diensten.",
        "ready": "Zu Ihren Diensten.",
        "butler_name": "Alfred",
        "first_run_intro": (
            "Guten Tag. Mein Name ist Alfred, Ihr neuer Butler. "
            "Es ist mir ein Vergnügen, Ihnen zu dienen. "
            "Drücken Sie shift plus V, um mich etwas zu fragen, oder klicken Sie auf mich. "
            "Mein Menü finden Sie unten rechts an der Uhr. "
            "Für eine kurze Einführung öffnen Sie bitte die Kurzanleitung."
        ),
        "about_text": (
            "DeskButler 1.2\n\n"
            "Ihr persönlicher Butler Alfred steht zu Ihren Diensten.\n"
            "Ein sprechender Assistent mit E-Mail, Browser, Kalender und Suche.\n\n"
            "Stimme: Neuvoice (CPU-freundlich)."
        ),
        "menu_search": "Suchen (Shift+V)",
        "menu_email": "E-Mail öffnen",
        "menu_browser": "Browser öffnen",
        "menu_calendar": "Kalender öffnen",
        "menu_todo": "Aufgabenliste",
        "menu_quickguide": "Kurzanleitung",
        "menu_settings": "Einstellungen",
        "menu_about": "Über DeskButler",
        "menu_quit": "Beenden",
        "search_title": "Wonach soll ich suchen?",
        "search_placeholder": "Stellen Sie eine Frage oder geben Sie einen Programmnamen ein...",
        "btn_ask": "Fragen",
        "btn_cancel": "Abbrechen",
        "btn_yes": "Ja",
        "btn_no": "Nein",
        "show_in_browser": "Möchten Sie das im Browser sehen?",
        "no_results": "Leider konnte ich nichts finden.",
        "searching": "Ich suche...",
        "opening_app": "Ich öffne {name} für Sie.",
        "app_not_found": "Das Programm {name} habe ich nicht gefunden.",
        "weather_for": "Das Wetter in {city}",
        "weather_now": "Es sind aktuell {temp} Grad. {desc}.",
        "weather_unavailable": "Wetter ist gerade nicht verfügbar.",
        "news_today": "Die heutigen Nachrichten",
        "news_unavailable": "Nachrichten sind nicht abrufbar.",
        "browser_title": "Browser",
        "browser_url_placeholder": "Webadresse eingeben...",
        "btn_back": "Zurück",
        "btn_forward": "Vorwärts",
        "btn_refresh": "Aktualisieren",
        "btn_home": "Start",
        "email_title": "E-Mail",
        "email_add_account": "Konto hinzufügen",
        "email_compose": "Neue Nachricht",
        "email_reply": "Antworten",
        "email_forward": "Weiterleiten",
        "email_delete": "Löschen",
        "email_refresh": "Aktualisieren",
        "email_inbox": "Posteingang",
        "email_sent": "Gesendet",
        "email_drafts": "Entwürfe",
        "email_no_account": "Noch kein E-Mail-Konto eingerichtet.",
        "email_from": "Von",
        "email_to": "An",
        "email_subject": "Betreff",
        "email_send": "Senden",
        "email_sent_ok": "Ihre Nachricht wurde gesendet.",
        "email_send_error": "Beim Senden ist ein Fehler aufgetreten.",
        "calendar_title": "Kalender",
        "calendar_add": "Erinnerung hinzufügen",
        "calendar_time": "Zeit",
        "calendar_text": "Was soll ich mir merken?",
        "calendar_save": "Speichern",
        "calendar_no_reminders": "Keine Erinnerungen.",
        "reminder_title": "Erinnerung",
        "guide_title": "Kurzanleitung",
        "guide_intro": "Willkommen bei DeskButler. Die wichtigsten Funktionen:",
        "error_generic": "Etwas ist schiefgegangen: {error}",
        "no_network": "Keine Internetverbindung.",
        "new_mail_one": "Sie haben eine neue Nachricht in {account}.",
        "new_mail_many": "Sie haben {count} neue Nachrichten in {account}.",
        "settings_voice": "Stimme",
        "settings_mail": "E-Mail-Prüfung",
        "settings_mail_intro": "Wie oft soll ich nach neuen E-Mails sehen?",
        "settings_mail_off": "Aus",
        "settings_mail_every": "Alle {n} Minuten",
        "settings_mail_every_one": "Jede Minute",
        "settings_browser": "Browser",
        "settings_browser_intro": "Zusatzfunktionen für den eingebauten Browser:",
        "settings_adblock": "Werbung blockieren",
        "settings_cookies": "Cookie-Hinweise automatisch akzeptieren",
        "settings_toggle_on": "EIN",
        "settings_toggle_off": "AUS",
    },
    "fr": {
        "app_name": "DeskButler",
        "greeting_morning": "Bonjour, monsieur. En quoi puis-je vous aider ?",
        "greeting_afternoon": "Bon après-midi. Que puis-je faire pour vous ?",
        "greeting_evening": "Bonsoir. À votre service.",
        "ready": "À votre service.",
        "butler_name": "Alfred",
        "first_run_intro": (
            "Bonjour. Je m'appelle Alfred, votre nouveau majordome. "
            "C'est un plaisir d'être à votre service. "
            "Appuyez sur shift plus V pour me poser une question, ou cliquez sur moi. "
            "Mon menu se trouve près de l'horloge en bas à droite. "
            "Pour une courte introduction, ouvrez le guide rapide."
        ),
        "about_text": (
            "DeskButler 1.2\n\n"
            "Votre majordome personnel Alfred est à votre service.\n"
            "Un assistant parlant avec courriel, navigateur, agenda et recherche.\n\n"
            "Voix : Neuvoice (sans GPU)."
        ),
        "menu_search": "Rechercher (Shift+V)",
        "menu_email": "Ouvrir le courriel",
        "menu_browser": "Ouvrir le navigateur",
        "menu_calendar": "Ouvrir l'agenda",
        "menu_todo": "Liste de tâches",
        "menu_quickguide": "Guide rapide",
        "menu_settings": "Paramètres",
        "menu_about": "À propos",
        "menu_quit": "Quitter",
        "search_title": "Que voulez-vous chercher ?",
        "search_placeholder": "Posez une question ou tapez un nom de programme...",
        "btn_ask": "Demander",
        "btn_cancel": "Annuler",
        "btn_yes": "Oui",
        "btn_no": "Non",
        "show_in_browser": "Voulez-vous voir cela dans le navigateur ?",
        "no_results": "Désolé, je n'ai rien trouvé.",
        "searching": "Recherche en cours...",
        "opening_app": "J'ouvre {name} pour vous.",
        "app_not_found": "Je n'ai pas trouvé le programme {name}.",
        "weather_for": "Météo à {city}",
        "weather_now": "Il fait actuellement {temp} degrés. {desc}.",
        "weather_unavailable": "Météo indisponible.",
        "news_today": "Les nouvelles d'aujourd'hui",
        "news_unavailable": "Impossible de récupérer les nouvelles.",
        "browser_title": "Navigateur",
        "browser_url_placeholder": "Entrez une adresse web...",
        "btn_back": "Précédent",
        "btn_forward": "Suivant",
        "btn_refresh": "Actualiser",
        "btn_home": "Accueil",
        "email_title": "Courriel",
        "email_add_account": "Ajouter un compte",
        "email_compose": "Nouveau message",
        "email_reply": "Répondre",
        "email_forward": "Transférer",
        "email_delete": "Supprimer",
        "email_refresh": "Actualiser",
        "email_inbox": "Boîte de réception",
        "email_sent": "Envoyés",
        "email_drafts": "Brouillons",
        "email_no_account": "Aucun compte configuré.",
        "email_from": "De",
        "email_to": "À",
        "email_subject": "Objet",
        "email_send": "Envoyer",
        "email_sent_ok": "Votre message a été envoyé.",
        "email_send_error": "Erreur lors de l'envoi.",
        "calendar_title": "Agenda",
        "calendar_add": "Ajouter un rappel",
        "calendar_time": "Heure",
        "calendar_text": "De quoi se souvenir ?",
        "calendar_save": "Enregistrer",
        "calendar_no_reminders": "Aucun rappel.",
        "reminder_title": "Rappel",
        "guide_title": "Guide rapide",
        "guide_intro": "Bienvenue dans DeskButler. Fonctions principales :",
        "error_generic": "Une erreur est survenue : {error}",
        "no_network": "Pas de connexion internet.",
        "new_mail_one": "Vous avez un nouveau message dans {account}.",
        "new_mail_many": "Vous avez {count} nouveaux messages dans {account}.",
        "settings_voice": "Voix",
        "settings_mail": "Vérif. e-mail",
        "settings_mail_intro": "À quelle fréquence dois-je vérifier les nouveaux messages ?",
        "settings_mail_off": "Désactivé",
        "settings_mail_every": "Toutes les {n} minutes",
        "settings_mail_every_one": "Chaque minute",
        "settings_browser": "Navigateur",
        "settings_browser_intro": "Fonctions supplémentaires du navigateur intégré :",
        "settings_adblock": "Bloquer les publicités",
        "settings_cookies": "Accepter automatiquement les cookies",
        "settings_toggle_on": "ACTIVÉ",
        "settings_toggle_off": "DÉSACTIVÉ",
    },
}


class I18n:
    """Vertaal-helper. Lazy laadt de huidige taal."""

    def __init__(self):
        self._lang = None
        self._strings = None

    def _load(self):
        if self._lang is None:
            code = detect_language()
            self._lang = code
            self._strings = TRANSLATIONS.get(code, TRANSLATIONS["en"])

    def t(self, key: str, **kwargs) -> str:
        """Geef een vertaalde string. Met format-vars indien aanwezig."""
        self._load()
        text = self._strings.get(key)
        if text is None:
            # Fallback naar Engels
            text = TRANSLATIONS["en"].get(key, key)
        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, IndexError):
                pass
        return text

    @property
    def lang(self) -> str:
        self._load()
        return self._lang

    def reload(self):
        """Forceer herladen (na taalwijziging in settings)."""
        self._lang = None
        self._strings = None
        self._load()


# Singleton + handige shortcut
i18n = I18n()
def _(key, **kwargs):
    return i18n.t(key, **kwargs)


# ========================================================================
# STYLING (centrale stijl + lettergrootte)  (was: core/styling.py)
# ========================================================================

def base_font_size() -> int:
    """Lees de gewenste lettergrootte uit config (default 16pt)."""
    return int(config.get("font_size", 16))


def base_font() -> QFont:
    """Standaard lettertype gebaseerd op gebruikersvoorkeur."""
    return QFont("Segoe UI", base_font_size())


def title_font() -> QFont:
    """Voor titels en headers."""
    f = QFont("Segoe UI", base_font_size() + 4)
    f.setBold(True)
    return f


def DIALOG_STYLE() -> str:
    """
    Globale stijl voor dialogen, gegenereerd op basis van de huidige
    font_size. Toepassen via self.setStyleSheet(DIALOG_STYLE()).
    Gebruikt grote, toegankelijke maten voor alle invoervelden.
    """
    fs = base_font_size()
    fs_label = fs           # labels
    fs_input = fs           # invoervelden
    pad_input = max(10, fs - 4)  # padding schaalt mee
    return f"""
        QDialog {{
            background-color: #1a1a1a;
            color: #f5f5f5;
        }}
        QWidget {{
            color: #f5f5f5;
        }}
        QLabel {{
            color: #f5f5f5;
            font-size: {fs_label}pt;
            padding: 4px 2px;
        }}
        QLineEdit, QPlainTextEdit, QTextEdit {{
            background-color: #2a2a2a;
            color: #f5f5f5;
            border: 2px solid #707070;
            border-radius: 6px;
            padding: {pad_input}px;
            font-size: {fs_input}pt;
            min-height: {fs_input + 12}px;
        }}
        QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus {{
            border-color: #909090;
        }}
        QComboBox {{
            background-color: #2a2a2a;
            color: #f5f5f5;
            border: 2px solid #707070;
            border-radius: 6px;
            padding: {pad_input}px;
            font-size: {fs_input}pt;
            min-height: {fs_input + 12}px;
        }}
        QComboBox:hover {{
            border-color: #909090;
        }}
        QComboBox QAbstractItemView {{
            background-color: #2a2a2a;
            color: #f5f5f5;
            selection-background-color: #707070;
            font-size: {fs_input}pt;
            padding: 4px;
        }}
        QPushButton {{
            background-color: #2a2a2a;
            color: #c0c0c0;
            border: 2px solid #707070;
            border-radius: 6px;
            padding: {max(8, fs - 6)}px {max(14, fs)}px;
            font-size: {fs}pt;
            min-height: {fs + 12}px;
        }}
        QPushButton:hover {{
            background-color: #3a3a3a;
            color: #ffffff;
        }}
        QPushButton:pressed {{
            background-color: #4a4a4a;
        }}
        QPushButton#primary {{
            background-color: #707070;
            color: #ffffff;
            border: 2px solid #909090;
            font-weight: bold;
        }}
        QPushButton#primary:hover {{
            background-color: #909090;
        }}
        QListWidget {{
            background-color: #2a2a2a;
            color: #f5f5f5;
            border: 2px solid #707070;
            border-radius: 6px;
            padding: 4px;
            font-size: {fs}pt;
        }}
        QListWidget::item {{
            padding: {max(8, fs - 6)}px;
            min-height: {fs + 10}px;
        }}
        QListWidget::item:selected {{
            background-color: #707070;
            color: #ffffff;
            font-weight: bold;
        }}
        QCheckBox, QRadioButton {{
            color: #f5f5f5;
            font-size: {fs}pt;
            spacing: 8px;
            min-height: {fs + 8}px;
        }}
        QCheckBox::indicator, QRadioButton::indicator {{
            width: {fs + 4}px;
            height: {fs + 4}px;
        }}
        QGroupBox {{
            font-size: {fs}pt;
            padding-top: {fs + 8}px;
            margin-top: {fs}px;
        }}
        QTabBar::tab {{
            font-size: {fs}pt;
            padding: {max(8, fs - 4)}px {max(16, fs + 2)}px;
            min-height: {fs + 10}px;
        }}
        /* Scrollbar - groot en duidelijk */
        QScrollBar:vertical {{
            background: #2a2a2a;
            width: 18px;
            border-radius: 9px;
            margin: 2px;
        }}
        QScrollBar::handle:vertical {{
            background: #707070;
            border-radius: 7px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: #909090;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar:horizontal {{
            background: #2a2a2a;
            height: 18px;
            border-radius: 9px;
            margin: 2px;
        }}
        QScrollBar::handle:horizontal {{
            background: #707070;
            border-radius: 7px;
            min-width: 30px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: #909090;
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        QFormLayout > QLabel {{
            font-size: {fs}pt;
        }}
        QMessageBox QLabel {{
            font-size: {fs}pt;
            min-width: 400px;
        }}
        QMessageBox QPushButton {{
            min-width: 100px;
            font-size: {fs}pt;
        }}
    """


def apply_dialog_style(dialog: QWidget):
    """
    Pas de toegankelijke stijl toe op een dialoog of widget.
    Werkt zowel voor QDialog als andere QWidgets.
    """
    dialog.setStyleSheet(DIALOG_STYLE())
    dialog.setFont(base_font())
    # EU-toegankelijkheidsregels: hand-cursor + tooltips op interactieve elementen
    apply_accessibility(dialog)


def apply_accessibility(root: QWidget):
    """
    Loop door alle child-widgets en pas toegankelijkheidsregels toe:
      - Handje-cursor (PointingHandCursor) op alle klikbare widgets
      - Tooltip toevoegen waar nog niet aanwezig (gebruikt de tekst van de widget)
    Conform de European Accessibility Act (EAA) — sinds 28 juni 2025 verplicht.
    """
    from PySide6.QtWidgets import (
        QPushButton, QCheckBox, QRadioButton, QComboBox, QToolButton,
        QListWidget, QLineEdit, QTabBar,
    )
    # Klikbare widgets krijgen pointing-hand cursor
    clickable_types = (QPushButton, QCheckBox, QRadioButton, QComboBox, QToolButton)
    for w in root.findChildren(QWidget):
        try:
            if isinstance(w, clickable_types):
                w.setCursor(Qt.PointingHandCursor)
                # Tooltip: als er nog geen is, gebruik de tekst van de knop
                if not w.toolTip():
                    text = ""
                    if hasattr(w, "text"):
                        text = w.text() or ""
                    if text:
                        # Strip emoji/iconen voor schone tooltip
                        clean = text.strip()
                        for marker in [":", "✓", "✕", "▶️", "🛑", "🔄", "📋", "🔊",
                                       "✉️", "🌐", "💝", "📁", "🎙️", "⌨️", "🎤"]:
                            clean = clean.replace(marker, "").strip()
                        if clean:
                            w.setToolTip(clean)
            elif isinstance(w, QListWidget):
                # Lijsten zelf krijgen geen handje, items wel
                w.setCursor(Qt.PointingHandCursor)
                if not w.toolTip():
                    w.setToolTip("Kies een optie uit de lijst")
            elif isinstance(w, QLineEdit):
                if not w.toolTip() and w.placeholderText():
                    w.setToolTip(w.placeholderText())
            elif isinstance(w, QTabBar):
                w.setCursor(Qt.PointingHandCursor)
        except Exception:
            pass


# ========================================================================
# VERSION (versie + update checker)  (was: core/version.py)
# ========================================================================

# Centrale versie-info
APP_NAME = "DeskButler"
APP_VERSION = "6.7"
AUTHOR_NAME = "Dravenlock"
WEBSITE_URL = "https://dravenlock.nl/"
UPDATE_CHECK_URL = "https://dravenlock.nl/downloads/Deskbutler.txt"
DOWNLOAD_PAGE_URL = "https://dravenlock.nl/"


def parse_version(s: str) -> tuple:
    """
    Geef een tuple van getallen terug voor vergelijking.
    'v2.3.1' -> (2, 3, 1).  'invalid' -> (0,).
    """
    if not s:
        return (0,)
    s = s.strip().lstrip("vV")
    parts = re.findall(r"\d+", s)
    if not parts:
        return (0,)
    return tuple(int(p) for p in parts)


def is_newer(remote: str, local: str = APP_VERSION) -> bool:
    """True als remote-versie nieuwer is dan locale."""
    return parse_version(remote) > parse_version(local)


def fetch_latest_version() -> dict | None:
    """
    Haal de laatste versie-info op van de remote URL.
    Returnt dict {'version': str, 'notes': str} of None bij fout.
    """
    try:
        r = requests.get(
            UPDATE_CHECK_URL,
            timeout=6,
            headers={"User-Agent": f"DeskButler/{APP_VERSION}"},
        )
        if r.status_code != 200:
            return None
        text = r.text.strip()
        if not text:
            return None
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        if not lines:
            return None
        return {
            "version": lines[0],
            "notes": "\n".join(lines[1:]) if len(lines) > 1 else "",
        }
    except requests.RequestException as e:
        print(f"[update] check faalde: {e}")
        return None


def check_for_update() -> dict | None:
    """
    Controleer of er een nieuwere versie is.
    Returnt dict met {'version', 'notes', 'is_newer'} of None bij fout.
    """
    latest = fetch_latest_version()
    if latest is None:
        return None
    latest["is_newer"] = is_newer(latest["version"])
    latest["current"] = APP_VERSION
    return latest


# ========================================================================
# GREETINGS (begroeting + afscheid + naam)  (was: core/greetings.py)
# ========================================================================

def user_name() -> str:
    """Geef de voornaam van de gebruiker, of lege string."""
    return str(config.get("user_name", "")).strip()


def addressed(name_first: bool = True) -> str:
    """
    Geef een aanspreekvorm. Met naam: 'Anna, ' of ', Anna'.
    Zonder naam: lege string.
    """
    n = user_name()
    if not n:
        return ""
    return f"{n}, " if name_first else f", {n}"


def part_of_day() -> str:
    """morning / afternoon / evening / night."""
    h = datetime.now().hour
    if 5 <= h < 12:
        return "morning"
    if 12 <= h < 17:
        return "afternoon"
    if 17 <= h < 22:
        return "evening"
    return "night"


def greeting(short: bool = False) -> str:
    """Tijdsafhankelijke groet, met naam als bekend."""
    n = user_name()
    pod = part_of_day()
    nm = f", {n}" if n else ""

    if short:
        if pod == "morning":
            return f"Goedemorgen{nm}!"
        if pod == "afternoon":
            return f"Goedemiddag{nm}!"
        if pod == "evening":
            return f"Goedenavond{nm}!"
        return f"Goedenacht{nm}!"

    options = {
        "morning": [
            f"Goedemorgen{nm}! Heeft u goed geslapen?",
            f"Goedemorgen{nm}. Een mooie nieuwe dag.",
            f"Goedemorgen{nm}! Wat kan ik vandaag voor u betekenen?",
        ],
        "afternoon": [
            f"Goedemiddag{nm}! Fijn u te zien.",
            f"Goedemiddag{nm}. Hopelijk verloopt uw dag voorspoedig.",
            f"Goedemiddag{nm}!",
        ],
        "evening": [
            f"Goedenavond{nm}. Een prettige avond gewenst.",
            f"Goedenavond{nm}! Komt u nog wat doen?",
            f"Goedenavond{nm}.",
        ],
        "night": [
            f"Nog laat aan het werk{nm}?",
            f"Goedenacht{nm}. Vergeet niet ook eens te rusten.",
            f"Een late avond{nm}?",
        ],
    }
    return random.choice(options[pod])


def farewell() -> str:
    """Tijdsafhankelijk afscheid bij app-sluiten."""
    n = user_name()
    pod = part_of_day()
    nm = f", {n}" if n else ""

    options = {
        "morning": [
            f"Tot straks{nm}! Een fijne dag verder.",
            f"Tot ziens{nm}. Veel succes vandaag!",
            f"Tot horens{nm}.",
        ],
        "afternoon": [
            f"Tot later{nm}! Geniet van uw middag.",
            f"Tot ziens{nm}. Een prettige middag.",
            f"Tot horens{nm}.",
        ],
        "evening": [
            f"Een fijne avond{nm}. Tot horens.",
            f"Welterusten alvast{nm}.",
            f"Een prettige avond{nm}!",
        ],
        "night": [
            f"Welterusten{nm}. Slaap zacht.",
            f"Een goede nachtrust{nm}!",
            f"Tot morgen{nm}.",
        ],
    }
    return random.choice(options[pod])


def status_back() -> str:
    """Kort 'ik ben er weer' zinnetje."""
    n = user_name()
    nm = f", {n}" if n else ""
    return random.choice([
        f"Daar ben ik weer{nm}.",
        f"Tot uw dienst{nm}.",
        f"Wat kan ik voor u doen{nm}?",
    ])


# ========================================================================
# VOICE  (was: core/voice.py)
# ========================================================================

class VoiceEngine(QObject):
    """
    Spreekt teksten uit. Stuurt signalen voor lipsync:
      started, finished, amplitude(float 0..1)
    """
    started = Signal(str)            # tekst die wordt uitgesproken
    finished = Signal()
    amplitude = Signal(float)        # 0..1, voor mond-animatie
    error = Signal(str)

    def __init__(self):
        super().__init__()
        self._engine = None
        self._engine_type = None     # "neuvoice" of "sapi"
        self._lock = threading.Lock()
        self._stop_flag = threading.Event()
        self._current_thread = None
        self._init_engine()

    # ------------------------------------------------------------------
    # Engine initialisatie
    # ------------------------------------------------------------------
    def _init_engine(self):
        """Probeer Neuvoice te laden. Lukt het niet, gebruik dan SAPI."""
        if config.get("use_neuvoice", True):
            try:
                from neuvoice import TTS
                print("[voice] Neuvoice laden (kan even duren bij eerste keer)...")
                self._engine = TTS(auto_download=True)
                self._engine_type = "neuvoice"
                print("[voice] Neuvoice geladen.")
                return
            except Exception as e:
                print(f"[voice] Neuvoice kon niet worden geladen: {e}")
                print("[voice] Val terug op Windows SAPI.")

        # Fallback: Windows SAPI via pyttsx3
        try:
            import pyttsx3
            self._engine = pyttsx3.init()
            self._engine_type = "sapi"
            print("[voice] Windows SAPI (pyttsx3) geladen.")
        except Exception as e:
            print(f"[voice] Ook SAPI faalde: {e}")
            self._engine_type = None

    # ------------------------------------------------------------------
    # Publieke API
    # ------------------------------------------------------------------
    @property
    def available(self) -> bool:
        return self._engine is not None

    @property
    def engine_type(self) -> str:
        return self._engine_type or "none"

    def speak(self, text: str, lang: str = None, voice_name: str = None):
        """
        Spreek tekst uit op de achtergrond. Vorige spraak wordt afgebroken.
        voice_name: overschrijf eenmalig de stem (bv. voor het testen van een stem
        in het instellingen-venster zonder de config te wijzigen).
        """
        if not text or not self._engine:
            return
        self.stop()

        if lang is None:
            lang = detect_language()

        # Als geen expliciete voice_name: gebruik de actieve karakter-override
        # uit character_voices als die bestaat, anders globale voice_name.
        if voice_name is None:
            voice_name = get_effective_voice_name()

        self._stop_flag.clear()
        self._current_thread = threading.Thread(
            target=self._speak_worker, args=(text, lang, voice_name), daemon=True
        )
        self._current_thread.start()

    def list_voice_names(self) -> list:
        """Geef de beschikbare stemnamen terug (alleen Neuvoice)."""
        if self._engine_type == "neuvoice" and self._engine is not None:
            try:
                return list(self._engine.voice_style_names)
            except Exception as e:
                print(f"[voice] kon stem-lijst niet ophalen: {e}")
        return []

    def stop(self):
        """Stop huidige spraak."""
        self._stop_flag.set()
        if self._engine_type == "sapi" and self._engine is not None:
            try:
                self._engine.stop()
            except Exception:
                pass

    def is_speaking(self) -> bool:
        """True als er momenteel spraak afgespeeld wordt."""
        if self._current_thread is None:
            return False
        return self._current_thread.is_alive()

    # ------------------------------------------------------------------
    # Worker thread - daadwerkelijke synthese + afspelen
    # ------------------------------------------------------------------
    def _speak_worker(self, text: str, lang: str, voice_name: str = None):
        with self._lock:
            try:
                self.started.emit(text)
                if self._engine_type == "neuvoice":
                    self._speak_neuvoice(text, lang, voice_name)
                elif self._engine_type == "sapi":
                    self._speak_sapi(text)
            except Exception as e:
                self.error.emit(str(e))
            finally:
                self.amplitude.emit(0.0)
                self.finished.emit()

    def _speak_neuvoice(self, text: str, lang: str, voice_name: str = None):
        """Synthetiseer met Neuvoice en speel af + emit amplitude voor lipsync."""
        try:
            if voice_name is None:
                voice_name = config.get("voice_name", "Linda")
            style = self._engine.get_voice_style(voice_name)
        except Exception:
            # Stem bestaat niet meer: pak de eerste beschikbare
            names = self._engine.voice_style_names
            style = self._engine.get_voice_style(names[0])

        speed = get_effective_voice_speed()
        wav, duration = self._engine.synthesize(
            text, voice_style=style, lang=lang if lang != "no" else "na", speed=speed
        )
        if self._stop_flag.is_set():
            return

        # wav is (1, samples) numpy array, sample rate 24000 normaal
        sample_rate = getattr(self._engine, "sample_rate", 24000)
        self._play_with_amplitude(wav.flatten(), sample_rate)

    def _speak_sapi(self, text: str):
        """SAPI heeft geen amplitude-callback. Simuleer beweging."""
        # Schat duur op ongeveer 15 chars/seconde
        est_duration = max(0.5, len(text) / 15.0)
        start = time.time()

        # Mond-pulse simulatie in aparte thread
        def pulse():
            while not self._stop_flag.is_set():
                t = time.time() - start
                if t >= est_duration:
                    break
                # Pseudo-random mondbeweging
                amp = 0.3 + 0.5 * abs(np.sin(t * 8.0 + np.cos(t * 3.7)))
                self.amplitude.emit(float(amp))
                time.sleep(0.05)
            self.amplitude.emit(0.0)

        t = threading.Thread(target=pulse, daemon=True)
        t.start()

        try:
            self._engine.say(text)
            self._engine.runAndWait()
        except Exception:
            pass

    def _play_with_amplitude(self, samples: np.ndarray, sample_rate: int):
        """
        Speel de audio af en emit amplitude-signalen elke ~50ms voor lipsync.
        Past volume en pitch toe. Speed is al door synthesize() verwerkt
        in de natuurlijke spraak — NIET ook nog sample-rate scaling toepassen,
        anders krijg je een 'chipmunk'-effect (te hoog + te snel).
        """
        samples = samples.astype(np.float32)
        # Normaliseer
        peak = max(np.max(np.abs(samples)), 1e-6)
        norm = samples / peak


        # ---- Pitch shift via resampling (in halve tonen) ----
        pitch_semis = get_effective_voice_pitch()
        if abs(pitch_semis) > 0.05:
            pitch_factor = 2 ** (pitch_semis / 12)
            new_len = max(1, int(len(norm) / pitch_factor))
            indices = np.linspace(0, len(norm) - 1, new_len)
            norm = np.interp(indices, np.arange(len(norm)), norm).astype(np.float32)
            peak2 = max(np.max(np.abs(norm)), 1e-6)
            norm = norm / peak2

        # ---- Native sample-rate (geen speed-multiplicatie meer!) ----
        # Speed is al toegepast in synthesize(); hier afspelen op natuurlijke rate.
        playback_rate = sample_rate

        chunk_ms = 50
        chunk_samples = int(playback_rate * chunk_ms / 1000)

        # Volume (0.0 - 0.99 om clipping te voorkomen)
        volume = get_effective_voice_volume()
        volume = max(0.0, min(0.99, volume))

        played_via = None

        # Probeer sounddevice (best)
        try:
            import sounddevice as sd
            sd.play(norm * volume, playback_rate)
            played_via = "sounddevice"

            total_chunks = len(norm) // chunk_samples + 1
            for i in range(total_chunks):
                if self._stop_flag.is_set():
                    sd.stop()
                    return
                chunk = norm[i*chunk_samples:(i+1)*chunk_samples]
                if len(chunk) == 0:
                    break
                # RMS amplitude van dit chunkje
                rms = float(np.sqrt(np.mean(chunk ** 2)))
                # Schaal naar 0..1 met soft knee
                amp = min(1.0, rms * 4.0)
                self.amplitude.emit(amp)
                time.sleep(chunk_ms / 1000.0)
            sd.wait()
            return
        except Exception as e:
            print(f"[voice] sounddevice faalde: {e}")

        # Fallback: schrijf naar tijdelijk wav en speel via winsound
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = tmp.name
            # Schrijf 16-bit PCM met aangepaste playback_rate
            with wave.open(tmp_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(playback_rate)
                int_samples = (norm * volume * 32767).astype(np.int16)
                wf.writeframes(int_samples.tobytes())

            # Op Windows: winsound; elders: probeer playsound
            if os.name == "nt":
                import winsound
                def play():
                    winsound.PlaySound(tmp_path, winsound.SND_FILENAME)
                pt = threading.Thread(target=play, daemon=True)
                pt.start()
            else:
                try:
                    from playsound import playsound
                    pt = threading.Thread(target=playsound, args=(tmp_path,), daemon=True)
                    pt.start()
                except Exception:
                    pt = None

            # Emit amplitude chunks parallel
            duration = len(norm) / playback_rate
            chunks_total = int(duration * 1000 / chunk_ms)
            for i in range(chunks_total):
                if self._stop_flag.is_set():
                    return
                start_idx = i * chunk_samples
                end_idx = start_idx + chunk_samples
                chunk = norm[start_idx:end_idx]
                if len(chunk) == 0:
                    break
                rms = float(np.sqrt(np.mean(chunk ** 2)))
                amp = min(1.0, rms * 4.0)
                self.amplitude.emit(amp)
                time.sleep(chunk_ms / 1000.0)

            if pt is not None:
                pt.join(timeout=duration + 1)

            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        except Exception as e:
            print(f"[voice] Audio afspelen faalde: {e}")


# Singleton
_voice_instance = None
def get_voice() -> VoiceEngine:
    global _voice_instance
    if _voice_instance is None:
        _voice_instance = VoiceEngine()
    return _voice_instance


# ----------------------------------------------------------------------
# Per-karakter stem-instellingen
# ----------------------------------------------------------------------
def _character_override(key: str):
    """Geef de override voor het huidige karakter, of None."""
    cv = config.get("character_voices", {}) or {}
    char_id = config.get("character_id", "alfred")
    char_settings = cv.get(char_id, {}) if isinstance(cv, dict) else {}
    if isinstance(char_settings, dict) and key in char_settings:
        return char_settings[key]
    return None


def get_effective_voice_name() -> str:
    """Stem voor huidig karakter, of globale stem."""
    ov = _character_override("voice_name")
    if ov:
        return str(ov)
    return str(config.get("voice_name", "Linda"))


def get_effective_voice_pitch() -> float:
    ov = _character_override("voice_pitch")
    if ov is not None:
        return float(ov)
    return float(config.get("voice_pitch", 0.0))


def get_effective_voice_speed() -> float:
    ov = _character_override("voice_speed")
    if ov is not None:
        return float(ov)
    return float(config.get("voice_speed", 1.0))


def get_effective_voice_volume() -> float:
    ov = _character_override("voice_volume")
    if ov is not None:
        return float(ov)
    return float(config.get("voice_volume", 0.95))


# ========================================================================
# VOICE INPUT (microfoon wake-word)  (was: core/voice_input.py)
# ========================================================================

try:
    import speech_recognition as sr
    _SR_AVAILABLE = True
except ImportError:
    sr = None
    _SR_AVAILABLE = False


# Wake-woorden per karakter (lowercase, met varianten)
WAKE_WORDS = {
    "alfred": ["alfred", "hee alfred", "hé alfred", "hey alfred"],
    "sophie": ["sophie", "hee sophie", "hé sophie"],
    "robo":   ["robo", "hee robo", "hé robo"],
    "sage":   ["sage", "hee sage", "hé sage"],
    "pip":    ["pip", "hee pip", "hé pip"],
    "drake":  ["drake", "hee drake", "hé drake", "draak"],
}

# Generieke wake-woorden die voor elk karakter werken
GENERIC_WAKES = ["assistent", "butler", "computer"]


def is_voice_input_available() -> bool:
    """True als de benodigde libraries zijn geïnstalleerd."""
    return _SR_AVAILABLE


def get_install_instructions() -> str:
    """Tekst voor de gebruiker hoe spraakherkenning aan te zetten."""
    return (
        "Voor spraakherkenning zijn enkele extra pakketten nodig:\n\n"
        "  1. Open Opdrachtprompt\n"
        "  2. Typ:  pip install SpeechRecognition pyaudio\n"
        "  3. Sluit en herstart DeskButler\n\n"
        "Werkt PyAudio niet? Probeer dan via een wheel-bestand:\n"
        "  pip install pipwin\n"
        "  pipwin install pyaudio"
    )


class VoiceInput:
    """
    Microfoon-luisteraar met wake-word detectie.

    Lifecyle:
        vi = VoiceInput(on_wake=fn1, on_command=fn2)
        vi.start()    # begint te luisteren in achtergrond
        ...
        vi.stop()     # stopt de thread netjes

    Callbacks krijgen geen argumenten (on_wake) of een string (on_command).
    """

    def __init__(self, on_wake=None, on_command=None, on_status=None):
        self._on_wake = on_wake
        self._on_command = on_command
        self._on_status = on_status
        self._running = False
        self._thread = None
        self._listening_for_command = False
        # We staan toe dat er meerdere wake-woorden vergeleken worden;
        # de actieve set wordt bepaald door de huidige character_id.
        self._recognizer = None
        self._mic = None

    def _status(self, msg: str):
        print(f"[voice_input] {msg}")
        if self._on_status:
            try:
                self._on_status(msg)
            except Exception:
                pass

    def _build_recognizer(self):
        if not _SR_AVAILABLE:
            return False
        try:
            self._recognizer = sr.Recognizer()
            # Vermijd te streng gedrag: pas dynamic energy threshold aan
            self._recognizer.energy_threshold = 300
            self._recognizer.dynamic_energy_threshold = True
            self._recognizer.pause_threshold = 0.8
            self._mic = sr.Microphone()
            # Initieel aanpassen aan omgevingsgeluid
            with self._mic as source:
                self._recognizer.adjust_for_ambient_noise(source, duration=0.5)
            return True
        except Exception as e:
            self._status(f"Microfoon-init faalde: {e}")
            return False

    def _current_wake_words(self) -> list:
        char_id = config.get("character_id", "alfred")
        words = list(WAKE_WORDS.get(char_id, ["alfred"]))
        words.extend(GENERIC_WAKES)
        return [w.lower() for w in words]

    def _matches_wake(self, text: str) -> bool:
        """Check of de tekst een wake-woord bevat."""
        if not text:
            return False
        low = text.lower().strip()
        for w in self._current_wake_words():
            # Hele woord-grens matching
            if re.search(rf"\b{re.escape(w)}\b", low):
                return True
        return False

    def _strip_wake_word(self, text: str) -> str:
        """Verwijder het wake-woord uit het begin van de tekst."""
        low = text.lower().strip()
        for w in self._current_wake_words():
            pattern = rf"^(?:hee\s+|hé\s+|hey\s+)?{re.escape(w)}[,.\s]+"
            m = re.match(pattern, low)
            if m:
                return text[m.end():].strip()
        return text

    def _recognize(self, audio) -> str:
        """Probeer audio te herkennen. Returnt lege string bij mislukking."""
        if self._recognizer is None:
            return ""
        # Probeer Google (online, gratis, geen key)
        try:
            return self._recognizer.recognize_google(audio, language="nl-NL")
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            self._status(f"Online herkenning faalt: {e}")
            return ""
        except Exception as e:
            self._status(f"Herkenning-fout: {e}")
            return ""

    def _loop(self):
        if not self._build_recognizer():
            self._status("Spraakherkenning niet beschikbaar")
            return

        self._status("Microfoon actief — luistert naar wake-woord")
        while self._running:
            try:
                with self._mic as source:
                    # Korte luister-periode voor wake-detectie
                    audio = self._recognizer.listen(
                        source, timeout=2, phrase_time_limit=4
                    )
            except sr.WaitTimeoutError:
                continue
            except Exception as e:
                self._status(f"Microfoon-fout: {e}")
                time.sleep(1)
                continue

            text = self._recognize(audio)
            if not text:
                continue

            self._status(f"Gehoord: {text!r}")

            if self._matches_wake(text):
                # Wake-woord gedetecteerd
                command_part = self._strip_wake_word(text)
                if self._on_wake:
                    try:
                        self._on_wake()
                    except Exception as e:
                        self._status(f"on_wake callback faalde: {e}")

                # Als er al een commando direct na het wake-woord stond,
                # gebruik dat. Anders nog even luisteren naar het commando.
                if command_part:
                    self._fire_command(command_part)
                else:
                    self._listen_for_command()

    def _listen_for_command(self):
        """Na wake-detectie: nog 5 seconden actief luisteren naar het commando."""
        self._status("Luistert naar uw vraag...")
        try:
            with self._mic as source:
                audio = self._recognizer.listen(
                    source, timeout=4, phrase_time_limit=8
                )
        except sr.WaitTimeoutError:
            self._status("Geen commando gehoord.")
            return
        except Exception as e:
            self._status(f"Commando-luister faalde: {e}")
            return

        text = self._recognize(audio)
        if text:
            self._fire_command(text)
        else:
            self._status("Kon de vraag niet verstaan.")

    def _fire_command(self, command: str):
        self._status(f"Commando: {command!r}")
        if self._on_command:
            try:
                self._on_command(command)
            except Exception as e:
                self._status(f"on_command callback faalde: {e}")

    def start(self):
        if not _SR_AVAILABLE:
            self._status("speech_recognition niet geinstalleerd")
            return False
        if self._running:
            return True
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        return True

    def stop(self):
        self._running = False
        # Thread is daemon, stopt vanzelf wanneer Python afsluit


# ========================================================================
# NOTIFICATIONS  (was: core/notifications.py)
# ========================================================================

# (ICON_PATH komt uit globale assets-sectie)


def notify(title: str, message: str, speak: bool = True, urgent: bool = False):
    """
    Toon een Windows toast en (optioneel) spreek de melding uit.
    De butler is een spreekgrage assistent: standaard wordt alles uitgesproken.
    """
    # Probeer toast via plyer
    try:
        from plyer import notification
        notification.notify(
            title=title,
            message=message,
            app_name=_("app_name"),
            app_icon=str(ICON_PATH) if ICON_PATH.exists() else None,
            timeout=10 if not urgent else 30,
        )
    except Exception as e:
        print(f"[notify] plyer faalde: {e}")
        # Fallback: simpele console output
        print(f"[NOTIFY] {title}: {message}")

    # Spreek de melding ook uit
    if speak:
        try:
            voice = get_voice()
            voice.speak(f"{title}. {message}")
        except Exception as e:
            print(f"[notify] spreken faalde: {e}")


# ========================================================================
# QUICK ANSWERS (tijd/datum/rekenen/eenheden)  (was: core/quick_answers.py)
# ========================================================================

# ----------------------------------------------------------------------
# Tijd / datum
# ----------------------------------------------------------------------
_TIME_PATTERNS = [
    r"\bhoe\s+laat\s+is\s+het\b",
    r"\bwat\s+is\s+de\s+tijd\b",
    r"\bwhat\s+time\s+is\s+it\b",
    r"\bwhat'?s\s+the\s+time\b",
    r"\bwie\s+sp[äa]t\s+ist\s+es\b",
    r"\bquelle\s+heure\s+est[- ]il\b",
]
_DATE_PATTERNS = [
    r"\bwelke\s+(?:datum|dag)\b",
    r"\bwat\s+is\s+(?:de\s+datum|het\s+vandaag|vandaag\s+voor\s+(?:een\s+)?dag)\b",
    r"\bwelke\s+dag\s+is\s+het\b",
    r"\bwhat\s+(?:date|day)\s+is\s+(?:it|today)\b",
    r"\bwelches\s+datum\b",
]

_DAYS_NL = ["maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag", "zondag"]
_MONTHS_NL = ["januari", "februari", "maart", "april", "mei", "juni",
              "juli", "augustus", "september", "oktober", "november", "december"]


def _format_time_nl() -> str:
    now = datetime.now()
    hh, mm = now.hour, now.minute
    return f"Het is {hh} uur {mm:02d}."


def _format_date_nl() -> str:
    now = datetime.now()
    return (
        f"Vandaag is {_DAYS_NL[now.weekday()]}, "
        f"{now.day} {_MONTHS_NL[now.month - 1]} {now.year}."
    )


# ----------------------------------------------------------------------
# Veilige rekenmachine
# ----------------------------------------------------------------------
_ALLOWED_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_ALLOWED_UNOPS = {ast.USub: operator.neg, ast.UAdd: operator.pos}


def _safe_eval_math(expr: str):
    """Evalueer een rekensom veilig (zonder eval())."""
    try:
        node = ast.parse(expr, mode="eval")
        return _walk(node.body)
    except (SyntaxError, ValueError, ZeroDivisionError, KeyError, TypeError):
        return None


def _walk(n):
    if isinstance(n, ast.Constant):
        if isinstance(n.value, (int, float)):
            return n.value
        raise ValueError("only numbers")
    if isinstance(n, ast.BinOp):
        return _ALLOWED_BINOPS[type(n.op)](_walk(n.left), _walk(n.right))
    if isinstance(n, ast.UnaryOp):
        return _ALLOWED_UNOPS[type(n.op)](_walk(n.operand))
    raise ValueError("not allowed")


def _try_math(query: str):
    """Zoek of de query een rekensom bevat. Returnt antwoord-tekst of None."""
    # Sta ook 'maal'/'gedeeld door' toe via vervangen
    expr = (
        query.lower()
        .replace("keer", "*").replace("maal", "*").replace("vermenigvuldig met", "*")
        .replace("gedeeld door", "/").replace("plus", "+").replace("min", "-")
        .replace("tot de macht", "**").replace("^", "**")
        .replace("times", "*").replace("divided by", "/")
        .replace(",", ".")
    )
    # Pak alleen het stukje dat eruit ziet als rekensom (cijfers + operatoren)
    m = re.search(r"[-+]?\d+(?:\.\d+)?(?:\s*[+\-*/%]+\s*[-+]?\d+(?:\.\d+)?)+", expr)
    if not m:
        return None
    sub = m.group(0)
    # Bevatte de query ook andere woorden? Filter daarvoor: alleen accepteren
    # als de query KORT is OF expliciet begint met "bereken X"
    starts_with_calc = re.match(
        r"^\s*(?:bereken|calculate|rechne|wat\s+is|hoeveel\s+is|how\s+much\s+is)\b",
        query.lower(),
    )
    other_words = re.sub(r"[\d.\s+\-*/%^,()]", "", expr).strip()
    if other_words and not starts_with_calc:
        return None

    result = _safe_eval_math(sub.replace("**", "**"))
    if result is None:
        return None
    # Mooi formatteren
    if isinstance(result, float):
        if result.is_integer():
            result_str = str(int(result))
        else:
            result_str = f"{result:.6g}".replace(".", ",")
    else:
        result_str = str(result)
    return f"{sub.replace('**', ' tot de macht ')} is {result_str}."


# ----------------------------------------------------------------------
# Eenhedenconversie (klein maar handig)
# ----------------------------------------------------------------------
# Lengte
_LENGTH = {
    "km": 1000.0, "kilometer": 1000.0, "kilometers": 1000.0,
    "m": 1.0, "meter": 1.0, "meters": 1.0,
    "cm": 0.01, "centimeter": 0.01,
    "mm": 0.001, "millimeter": 0.001,
    "mile": 1609.344, "mijl": 1609.344, "mijlen": 1609.344, "miles": 1609.344, "mi": 1609.344,
    "yard": 0.9144, "yards": 0.9144, "yd": 0.9144,
    "ft": 0.3048, "feet": 0.3048, "foot": 0.3048, "voet": 0.3048,
    "inch": 0.0254, "inches": 0.0254, "in": 0.0254, "duim": 0.0254,
}
# Massa
_MASS = {
    "kg": 1000.0, "kilogram": 1000.0,
    "g": 1.0, "gram": 1.0, "grammen": 1.0,
    "mg": 0.001,
    "ton": 1_000_000.0,
    "pound": 453.59237, "pounds": 453.59237, "lb": 453.59237, "lbs": 453.59237, "pond": 453.59237,
    "ounce": 28.349523125, "ounces": 28.349523125, "oz": 28.349523125, "ons": 100.0,
}
# Snelheid
_SPEED = {
    "kmh": 1.0, "kmu": 1.0, "km/h": 1.0, "kph": 1.0,
    "mph": 1.609344, "mi/h": 1.609344,
    "mps": 3.6, "m/s": 3.6,
}

_UNIT_GROUPS = [("lengte", _LENGTH), ("massa", _MASS), ("snelheid", _SPEED)]


def _try_unit_conversion(query: str):
    """Herken patronen als '5 km in mijlen' of '20 c naar f'."""
    q = query.lower().replace(",", ".")
    # Eerst lange namen naar korte symbolen normaliseren
    q = re.sub(r"\bcelsius\b", "c", q)
    q = re.sub(r"\bfahrenheit\b", "f", q)

    # Temperatuur apart (eigen formule)
    m = re.search(
        r"(-?\d+(?:\.\d+)?)\s*°?\s*([cf])\s+(?:in|naar|to)\s*°?\s*([cf])",
        q,
    )
    if m:
        val = float(m.group(1))
        src, dst = m.group(2), m.group(3)
        if src == "c" and dst == "f":
            res = val * 9 / 5 + 32
            return f"{val:g} graden Celsius is {res:.1f} graden Fahrenheit."
        if src == "f" and dst == "c":
            res = (val - 32) * 5 / 9
            return f"{val:g} graden Fahrenheit is {res:.1f} graden Celsius."

    # Algemene unit conversie
    m = re.search(
        r"(-?\d+(?:\.\d+)?)\s*([a-z/]+)\s+(?:in|naar|to)\s+([a-z/]+)",
        q,
    )
    if not m:
        return None
    val = float(m.group(1))
    src_unit = m.group(2)
    dst_unit = m.group(3)

    for group_name, group in _UNIT_GROUPS:
        if src_unit in group and dst_unit in group:
            # Convert via base
            in_base = val * group[src_unit]
            out = in_base / group[dst_unit]
            # Mooi formatteren
            if abs(out - round(out)) < 1e-9:
                out_str = str(int(round(out)))
            else:
                out_str = f"{out:.4g}".replace(".", ",")
            return f"{val:g} {src_unit} is {out_str} {dst_unit}."
    return None


# ----------------------------------------------------------------------
# Hoofd-dispatcher
# ----------------------------------------------------------------------
def try_quick_answer(query: str) -> str | None:
    """
    Probeer een direct antwoord te geven op simpele vragen.
    Geeft None terug als de vraag niet matched.
    """
    if not query:
        return None
    q = query.lower().strip()

    # 1) Tijd
    for pat in _TIME_PATTERNS:
        if re.search(pat, q):
            return _format_time_nl()

    # 2) Datum
    for pat in _DATE_PATTERNS:
        if re.search(pat, q):
            return _format_date_nl()

    # 3) Eenheidsconversie (eerst, want bevat ook getallen)
    res = _try_unit_conversion(query)
    if res:
        return res

    # 4) Rekensom
    res = _try_math(query)
    if res:
        return res

    return None


# ========================================================================
# NOTES (notitie-opslag)  (was: core/notes.py)
# ========================================================================

DB_PATH = DATA_DIR / "notes.db"


def _notes_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(DB_PATH))
    con.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            text TEXT NOT NULL
        )
    """)
    return con


def add_note(text: str) -> int:
    """Sla een nieuwe notitie op, geef het ID terug."""
    con = _notes_conn()
    cur = con.execute(
        "INSERT INTO notes (ts, text) VALUES (?, ?)",
        (datetime.now().isoformat(), text.strip()),
    )
    new_id = cur.lastrowid
    con.commit()
    con.close()
    return new_id


def list_notes() -> list:
    """Geef alle notities terug als (id, datetime, text) tuples, nieuwste eerst."""
    con = _notes_conn()
    cur = con.execute("SELECT id, ts, text FROM notes ORDER BY id DESC")
    rows = cur.fetchall()
    con.close()
    out = []
    for r_id, ts, text in rows:
        try:
            dt = datetime.fromisoformat(ts)
        except ValueError:
            dt = datetime.now()
        out.append((r_id, dt, text))
    return out


def delete_note_by_id(note_id: int) -> bool:
    con = _notes_conn()
    cur = con.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    deleted = cur.rowcount > 0
    con.commit()
    con.close()
    return deleted


def delete_notes_containing(keyword: str) -> int:
    """Verwijder alle notities die het keyword bevatten. Geeft aantal verwijderd."""
    con = _notes_conn()
    cur = con.execute(
        "DELETE FROM notes WHERE LOWER(text) LIKE ?",
        (f"%{keyword.lower()}%",),
    )
    n = cur.rowcount
    con.commit()
    con.close()
    return n


def clear_all() -> int:
    con = _notes_conn()
    cur = con.execute("DELETE FROM notes")
    n = cur.rowcount
    con.commit()
    con.close()
    return n


# ========================================================================
# TODO (te-doen lijst opslag)  (was: core/todo.py)
# ========================================================================

DB_PATH = DATA_DIR / "todo.db"


def _todo_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(DB_PATH))
    con.execute("""
        CREATE TABLE IF NOT EXISTS todo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts_created TEXT NOT NULL,
            ts_done TEXT,
            text TEXT NOT NULL,
            done INTEGER DEFAULT 0
        )
    """)
    return con


def add_todo(text: str) -> int:
    con = _todo_conn()
    cur = con.execute(
        "INSERT INTO todo (ts_created, text) VALUES (?, ?)",
        (datetime.now().isoformat(), text.strip()),
    )
    new_id = cur.lastrowid
    con.commit()
    con.close()
    return new_id


def list_todos(include_done: bool = True) -> list:
    """Geef (id, ts_created, text, done) tuples."""
    con = _todo_conn()
    if include_done:
        cur = con.execute(
            "SELECT id, ts_created, text, done FROM todo "
            "ORDER BY done ASC, id DESC"
        )
    else:
        cur = con.execute(
            "SELECT id, ts_created, text, done FROM todo "
            "WHERE done = 0 ORDER BY id DESC"
        )
    rows = cur.fetchall()
    con.close()
    out = []
    for r_id, ts, text, done in rows:
        try:
            dt = datetime.fromisoformat(ts)
        except ValueError:
            dt = datetime.now()
        out.append((r_id, dt, text, bool(done)))
    return out


def list_open_todos() -> list:
    return list_todos(include_done=False)


def set_done(todo_id: int, done: bool = True) -> bool:
    con = _todo_conn()
    cur = con.execute(
        "UPDATE todo SET done = ?, ts_done = ? WHERE id = ?",
        (1 if done else 0,
         datetime.now().isoformat() if done else None,
         todo_id),
    )
    ok = cur.rowcount > 0
    con.commit()
    con.close()
    return ok


def set_done_by_keyword(keyword: str) -> int:
    """Vink alle (open) todos af die het keyword in de tekst hebben."""
    con = _todo_conn()
    cur = con.execute(
        "UPDATE todo SET done = 1, ts_done = ? "
        "WHERE done = 0 AND LOWER(text) LIKE ?",
        (datetime.now().isoformat(), f"%{keyword.lower()}%"),
    )
    n = cur.rowcount
    con.commit()
    con.close()
    return n


def delete_todo(todo_id: int) -> bool:
    con = _todo_conn()
    cur = con.execute("DELETE FROM todo WHERE id = ?", (todo_id,))
    ok = cur.rowcount > 0
    con.commit()
    con.close()
    return ok


def delete_todos_containing(keyword: str) -> int:
    con = _todo_conn()
    cur = con.execute(
        "DELETE FROM todo WHERE LOWER(text) LIKE ?",
        (f"%{keyword.lower()}%",),
    )
    n = cur.rowcount
    con.commit()
    con.close()
    return n


def count_open() -> int:
    con = _todo_conn()
    cur = con.execute("SELECT COUNT(*) FROM todo WHERE done = 0")
    n = cur.fetchone()[0]
    con.close()
    return int(n or 0)


# ========================================================================
# CHARACTERS (6 karakters + SVG-data)  (was: core/characters.py)
# ========================================================================

# ----------------------------------------------------------------------
# Alfred — de chique butler (origineel)
# ----------------------------------------------------------------------
_ALFRED_SVG = r"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 1000">
  <!-- Hoofd / huid -->
  <g id="head_base">
    <ellipse cx="400" cy="280" rx="140" ry="160" fill="#f4d6b4" stroke="#3a2818" stroke-width="3"/>
    <!-- Grijs haar aan zijkanten -->
    <path d="M 270 240 Q 250 290 270 340 L 280 320 Q 285 280 295 250 Z" fill="#888"/>
    <path d="M 530 240 Q 550 290 530 340 L 520 320 Q 515 280 505 250 Z" fill="#888"/>
    <!-- Wenkbrauwen -->
    <path d="M 350 250 Q 370 240 395 252" stroke="#3a2818" stroke-width="4" fill="none" stroke-linecap="round"/>
    <path d="M 405 252 Q 430 240 450 250" stroke="#3a2818" stroke-width="4" fill="none" stroke-linecap="round"/>
    <!-- Monocle rond rechteroog -->
    <circle cx="430" cy="295" r="42" fill="none" stroke="#888" stroke-width="3"/>
    <line x1="455" y1="320" x2="475" y2="380" stroke="#888" stroke-width="2"/>
  </g>
  <!-- Lichaam / tuxedo -->
  <g id="body">
    <path d="M 280 440 Q 280 600 290 800 L 510 800 Q 520 600 520 440 Z" fill="#1a1a1a" stroke="#000" stroke-width="2"/>
    <!-- Wit overhemd -->
    <path d="M 360 440 L 360 700 L 440 700 L 440 440 Z" fill="#ffffff"/>
    <!-- Grijs vest -->
    <path d="M 340 460 L 340 680 L 460 680 L 460 460 Q 400 470 340 460 Z" fill="#555" opacity="0.85"/>
    <!-- Vlinderdas -->
    <path d="M 370 455 L 400 440 L 430 455 L 430 475 L 400 460 L 370 475 Z" fill="#1a1a1a"/>
    <circle cx="400" cy="465" r="4" fill="#333"/>
    <!-- Knoopjes -->
    <circle cx="400" cy="540" r="4" fill="#999"/>
    <circle cx="400" cy="600" r="4" fill="#999"/>
    <circle cx="400" cy="660" r="4" fill="#999"/>
  </g>
  <!-- Linkerarm met dienblad + handdoek -->
  <g id="left_arm">
    <path d="M 285 470 Q 240 540 230 650 L 250 650 Q 270 540 305 470 Z" fill="#1a1a1a"/>
    <!-- Hand -->
    <ellipse cx="230" cy="660" rx="22" ry="18" fill="#f4d6b4" stroke="#3a2818" stroke-width="2"/>
    <!-- Dienblad -->
    <ellipse cx="170" cy="650" rx="80" ry="14" fill="#c0c0c0" stroke="#888" stroke-width="2"/>
    <ellipse cx="170" cy="646" rx="76" ry="10" fill="#e0e0e0"/>
    <!-- Handdoek over de arm -->
    <path d="M 215 645 Q 200 700 205 760 L 245 760 Q 240 700 255 645 Z" fill="#ffffff" stroke="#ccc" stroke-width="1.5"/>
  </g>
  <!-- Rechterarm met paraplu -->
  <g id="right_arm">
    <path d="M 515 470 Q 560 540 570 650 L 550 650 Q 530 540 495 470 Z" fill="#1a1a1a"/>
    <ellipse cx="570" cy="660" rx="22" ry="18" fill="#f4d6b4" stroke="#3a2818" stroke-width="2"/>
    <!-- Paraplu - steel -->
    <line x1="600" y1="500" x2="600" y2="780" stroke="#222" stroke-width="6"/>
    <!-- Paraplu - bovenkant -->
    <path d="M 540 510 Q 600 480 660 510 L 660 520 Q 600 495 540 520 Z" fill="#1a1a1a" stroke="#444" stroke-width="2"/>
    <!-- Handvat -->
    <path d="M 600 780 Q 610 795 615 780" stroke="#222" stroke-width="6" fill="none" stroke-linecap="round"/>
  </g>
  <!-- Broek + schoenen -->
  <g id="legs">
    <path d="M 320 800 L 320 940 L 380 940 L 390 800 Z" fill="#1a1a1a"/>
    <path d="M 410 800 L 420 940 L 480 940 L 480 800 Z" fill="#1a1a1a"/>
    <!-- Streepjes op de broek -->
    <line x1="350" y1="810" x2="355" y2="930" stroke="#333" stroke-width="1.5"/>
    <line x1="440" y1="810" x2="445" y2="930" stroke="#333" stroke-width="1.5"/>
    <!-- Schoenen -->
    <ellipse cx="350" cy="945" rx="42" ry="14" fill="#000" stroke="#333" stroke-width="1.5"/>
    <ellipse cx="450" cy="945" rx="42" ry="14" fill="#000" stroke="#333" stroke-width="1.5"/>
  </g>
</svg>"""


# ----------------------------------------------------------------------
# Sophie — vrouwelijke huishoudster (eenvoudige variatie op Alfred)
# ----------------------------------------------------------------------
_SOPHIE_SVG = r"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 1000">
  <g id="head_base">
    <ellipse cx="400" cy="280" rx="140" ry="160" fill="#f4d6b4" stroke="#3a2818" stroke-width="3"/>
    <!-- Bruin haar - blijft boven de wenkbrauwen -->
    <path d="M 265 245 Q 245 180 320 145 Q 400 120 480 145 Q 555 180 535 245 Q 540 232 525 222 L 400 218 L 275 222 Q 260 232 265 245 Z" fill="#5a3018"/>
    <!-- Korte zijhaar-strookjes -->
    <path d="M 265 240 Q 252 285 258 345 Q 263 365 278 360 Q 278 308 273 250 Z" fill="#5a3018"/>
    <path d="M 535 240 Q 548 285 542 345 Q 537 365 522 360 Q 522 308 527 250 Z" fill="#5a3018"/>
    <!-- WIT HUISHOUDSTER-KAPJE (mobcap) bovenop het hoofd -->
    <ellipse cx="400" cy="160" rx="115" ry="48" fill="#ffffff" stroke="#ccc" stroke-width="2"/>
    <!-- Kapje-rand met kleine plooien -->
    <path d="M 290 165 Q 320 175 350 170 Q 380 175 410 170 Q 440 175 470 170 Q 500 175 510 165" stroke="#ddd" stroke-width="2" fill="none"/>
    <!-- Rood lintje op het kapje voor vrolijke noot -->
    <ellipse cx="350" cy="150" rx="12" ry="6" fill="#dc143c"/>
    <path d="M 338 150 L 332 158 M 362 150 L 368 158" stroke="#dc143c" stroke-width="3"/>
    <!-- Wenkbrauwen -->
    <path d="M 350 260 Q 370 250 395 262" stroke="#3a2818" stroke-width="4" fill="none" stroke-linecap="round"/>
    <path d="M 405 262 Q 430 250 450 260" stroke="#3a2818" stroke-width="4" fill="none" stroke-linecap="round"/>
    <!-- Wangen-blos -->
    <ellipse cx="320" cy="330" rx="22" ry="14" fill="#f4a8a8" opacity="0.7"/>
    <ellipse cx="480" cy="330" rx="22" ry="14" fill="#f4a8a8" opacity="0.7"/>
    <!-- Oorbellen -->
    <circle cx="265" cy="320" r="5" fill="#d4af37"/>
    <circle cx="535" cy="320" r="5" fill="#d4af37"/>
  </g>
  <g id="body">
    <!-- Zwarte jurk (achtergrond) -->
    <path d="M 280 440 Q 280 600 290 800 L 510 800 Q 520 600 520 440 Z" fill="#202020"/>
    <!-- VOL WIT SCHORT — over de hele jurk, prominente huishoudster-look -->
    <path d="M 305 450 Q 295 600 305 800 L 495 800 Q 505 600 495 450 Q 400 460 305 450 Z" fill="#ffffff" stroke="#ccc" stroke-width="2"/>
    <!-- Schort-band om het middel (rood, opvallend) -->
    <rect x="305" y="555" width="190" height="22" fill="#dc143c"/>
    <!-- Schortband-strik aan de zijkant -->
    <ellipse cx="510" cy="565" rx="14" ry="10" fill="#dc143c"/>
    <ellipse cx="495" cy="565" rx="14" ry="10" fill="#dc143c"/>
    <!-- Schouder-bandjes van het schort -->
    <path d="M 320 445 L 330 470 L 345 460 L 340 440 Z" fill="#ffffff" stroke="#ccc" stroke-width="1"/>
    <path d="M 480 445 L 470 470 L 455 460 L 460 440 Z" fill="#ffffff" stroke="#ccc" stroke-width="1"/>
    <!-- Klassieke 'borst-zak' op het schort -->
    <rect x="370" y="490" width="60" height="40" fill="none" stroke="#ddd" stroke-width="1.5"/>
    <!-- Kraag van de jurk (zichtbaar boven het schort) -->
    <path d="M 365 445 L 400 460 L 435 445 Q 420 475 400 475 Q 380 475 365 445 Z" fill="#202020"/>
    <!-- Witte kraag-rand -->
    <path d="M 365 445 L 400 458 L 435 445" stroke="#ffffff" stroke-width="3" fill="none"/>
  </g>
  <g id="left_arm">
    <!-- Linker arm in zwarte mouw -->
    <path d="M 285 470 Q 240 540 230 650 L 250 650 Q 270 540 305 470 Z" fill="#202020"/>
    <!-- Witte manchet -->
    <ellipse cx="240" cy="650" rx="22" ry="6" fill="#ffffff"/>
    <ellipse cx="230" cy="660" rx="22" ry="18" fill="#f4d6b4" stroke="#3a2818" stroke-width="2"/>
    <!-- PLUMEAU (stofdoek) in haar hand — duidelijk huishoudster-attribuut -->
    <line x1="225" y1="660" x2="195" y2="715" stroke="#8a5a30" stroke-width="6" stroke-linecap="round"/>
    <!-- Pluimen van de plumeau -->
    <ellipse cx="175" cy="745" rx="22" ry="35" fill="#f4d860" opacity="0.85"/>
    <ellipse cx="165" cy="735" rx="14" ry="28" fill="#ffe680" opacity="0.7" transform="rotate(-15 165 735)"/>
    <ellipse cx="185" cy="735" rx="14" ry="28" fill="#ffe680" opacity="0.7" transform="rotate(15 185 735)"/>
    <ellipse cx="160" cy="755" rx="10" ry="22" fill="#e0c040" opacity="0.6" transform="rotate(-25 160 755)"/>
    <ellipse cx="190" cy="755" rx="10" ry="22" fill="#e0c040" opacity="0.6" transform="rotate(25 190 755)"/>
  </g>
  <g id="right_arm">
    <!-- Rechter arm in zwarte mouw -->
    <path d="M 515 470 Q 560 540 570 650 L 550 650 Q 530 540 495 470 Z" fill="#202020"/>
    <!-- Witte manchet -->
    <ellipse cx="560" cy="650" rx="22" ry="6" fill="#ffffff"/>
    <ellipse cx="570" cy="660" rx="22" ry="18" fill="#f4d6b4" stroke="#3a2818" stroke-width="2"/>
  </g>
  <g id="legs">
    <!-- Onderkant van de jurk komt over de bovenkant van de benen -->
    <path d="M 320 800 L 320 940 L 380 940 L 390 800 Z" fill="#202020"/>
    <path d="M 410 800 L 420 940 L 480 940 L 480 800 Z" fill="#202020"/>
    <!-- Zwarte schoenen met klein hak -->
    <ellipse cx="350" cy="945" rx="42" ry="14" fill="#000"/>
    <ellipse cx="450" cy="945" rx="42" ry="14" fill="#000"/>
  </g>
</svg>"""


# ----------------------------------------------------------------------
# Robo — vriendelijke retro robot
# ----------------------------------------------------------------------
_ROBO_SVG = r"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 1000">
  <g id="head_base">
    <!-- Antenne -->
    <line x1="400" y1="100" x2="400" y2="140" stroke="#888" stroke-width="6"/>
    <circle cx="400" cy="95" r="14" fill="#ff4040" stroke="#a02020" stroke-width="2"/>
    <!-- Vierkant hoofd -->
    <rect x="270" y="140" width="260" height="280" rx="20" ry="20" fill="#b8c5d6" stroke="#3a4858" stroke-width="3"/>
    <!-- Schroefjes -->
    <circle cx="290" cy="160" r="6" fill="#666"/>
    <circle cx="510" cy="160" r="6" fill="#666"/>
    <circle cx="290" cy="400" r="6" fill="#666"/>
    <circle cx="510" cy="400" r="6" fill="#666"/>
    <!-- Display met visor -->
    <rect x="305" y="230" width="190" height="90" rx="8" ry="8" fill="#1a1a1a"/>
    <rect x="310" y="235" width="180" height="80" rx="5" ry="5" fill="#0a0a1a"/>
  </g>
  <g id="body">
    <!-- Romp -->
    <rect x="290" y="440" width="220" height="360" rx="20" ry="20" fill="#b8c5d6" stroke="#3a4858" stroke-width="3"/>
    <!-- Borst-paneel -->
    <rect x="340" y="500" width="120" height="160" rx="6" ry="6" fill="#2a3848" stroke="#1a2838" stroke-width="2"/>
    <!-- Knoppen / LEDs -->
    <circle cx="370" cy="540" r="10" fill="#00ff00"/>
    <circle cx="400" cy="540" r="10" fill="#ffeb3b"/>
    <circle cx="430" cy="540" r="10" fill="#ff4040"/>
    <!-- Indicator-strepen -->
    <rect x="360" y="580" width="80" height="6" fill="#00ddff"/>
    <rect x="360" y="600" width="60" height="6" fill="#00ddff" opacity="0.6"/>
    <rect x="360" y="620" width="40" height="6" fill="#00ddff" opacity="0.3"/>
  </g>
  <g id="left_arm">
    <rect x="240" y="450" width="50" height="200" rx="6" ry="6" fill="#9aa8b8" stroke="#3a4858" stroke-width="2"/>
    <!-- Gewricht -->
    <circle cx="265" cy="650" r="20" fill="#444" stroke="#222" stroke-width="2"/>
    <!-- Onderarm + 'klauw' -->
    <rect x="245" y="660" width="40" height="80" rx="4" ry="4" fill="#9aa8b8" stroke="#3a4858" stroke-width="2"/>
    <rect x="240" y="740" width="50" height="18" rx="4" ry="4" fill="#666"/>
  </g>
  <g id="right_arm">
    <rect x="510" y="450" width="50" height="200" rx="6" ry="6" fill="#9aa8b8" stroke="#3a4858" stroke-width="2"/>
    <circle cx="535" cy="650" r="20" fill="#444" stroke="#222" stroke-width="2"/>
    <rect x="515" y="660" width="40" height="80" rx="4" ry="4" fill="#9aa8b8" stroke="#3a4858" stroke-width="2"/>
    <rect x="510" y="740" width="50" height="18" rx="4" ry="4" fill="#666"/>
  </g>
  <g id="legs">
    <rect x="320" y="800" width="60" height="140" rx="6" ry="6" fill="#9aa8b8" stroke="#3a4858" stroke-width="2"/>
    <rect x="420" y="800" width="60" height="140" rx="6" ry="6" fill="#9aa8b8" stroke="#3a4858" stroke-width="2"/>
    <!-- Voet-platforms -->
    <rect x="305" y="940" width="90" height="20" rx="4" ry="4" fill="#444"/>
    <rect x="405" y="940" width="90" height="20" rx="4" ry="4" fill="#444"/>
  </g>
</svg>"""


# ----------------------------------------------------------------------
# Sage — een tovenaar/wijze
# ----------------------------------------------------------------------
_SAGE_SVG = r"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 1000">
  <g id="head_base">
    <!-- Tovenaarshoed -->
    <path d="M 250 220 Q 300 80 400 60 Q 500 80 550 220 Z" fill="#3a2c5c" stroke="#1a1024" stroke-width="3"/>
    <!-- Ster op hoed -->
    <path d="M 400 130 L 408 150 L 430 150 L 412 165 L 420 188 L 400 175 L 380 188 L 388 165 L 370 150 L 392 150 Z" fill="#ffeb3b" stroke="#d4a008" stroke-width="1"/>
    <!-- Hoofd -->
    <ellipse cx="400" cy="290" rx="120" ry="140" fill="#f4d6b4" stroke="#3a2818" stroke-width="3"/>
    <!-- Lange witte baard -->
    <path d="M 320 320 Q 320 480 400 530 Q 480 480 480 320 Q 460 360 440 380 Q 400 410 360 380 Q 340 360 320 320 Z" fill="#f0f0f0" stroke="#bbb" stroke-width="2"/>
    <!-- Snor -->
    <path d="M 360 340 Q 380 350 400 345 Q 420 350 440 340 Q 420 360 400 355 Q 380 360 360 340 Z" fill="#f0f0f0"/>
    <!-- Wenkbrauwen (dik en wit) -->
    <path d="M 345 260 Q 370 245 400 262" stroke="#bbb" stroke-width="6" fill="none" stroke-linecap="round"/>
    <path d="M 400 262 Q 430 245 455 260" stroke="#bbb" stroke-width="6" fill="none" stroke-linecap="round"/>
  </g>
  <g id="body">
    <!-- Mantel -->
    <path d="M 280 440 Q 250 600 270 800 L 530 800 Q 550 600 520 440 Z" fill="#3a2c5c" stroke="#1a1024" stroke-width="3"/>
    <!-- Sterren op de mantel -->
    <path d="M 340 560 L 344 568 L 352 568 L 346 574 L 348 582 L 340 577 L 332 582 L 334 574 L 328 568 L 336 568 Z" fill="#ffeb3b"/>
    <path d="M 460 600 L 464 608 L 472 608 L 466 614 L 468 622 L 460 617 L 452 622 L 454 614 L 448 608 L 456 608 Z" fill="#ffeb3b"/>
    <path d="M 400 700 L 404 708 L 412 708 L 406 714 L 408 722 L 400 717 L 392 722 L 394 714 L 388 708 L 396 708 Z" fill="#ffeb3b"/>
    <!-- Riem -->
    <rect x="290" y="640" width="220" height="20" fill="#8b6f1f" stroke="#5a4810" stroke-width="2"/>
    <rect x="385" y="640" width="30" height="20" fill="#d4a008" stroke="#5a4810" stroke-width="2"/>
  </g>
  <g id="left_arm">
    <path d="M 280 460 Q 240 540 220 660 L 250 660 Q 270 540 305 470 Z" fill="#3a2c5c"/>
    <!-- Hand met boek -->
    <ellipse cx="230" cy="670" rx="20" ry="16" fill="#f4d6b4" stroke="#3a2818" stroke-width="2"/>
    <!-- Boek -->
    <rect x="170" y="660" width="70" height="50" fill="#8b1818" stroke="#5a0808" stroke-width="2"/>
    <line x1="205" y1="660" x2="205" y2="710" stroke="#5a0808" stroke-width="2"/>
  </g>
  <g id="right_arm">
    <path d="M 520 460 Q 560 540 580 660 L 550 660 Q 530 540 495 470 Z" fill="#3a2c5c"/>
    <ellipse cx="570" cy="670" rx="20" ry="16" fill="#f4d6b4" stroke="#3a2818" stroke-width="2"/>
    <!-- Staf -->
    <line x1="595" y1="500" x2="600" y2="820" stroke="#5a3818" stroke-width="6"/>
    <!-- Kristal -->
    <circle cx="595" cy="495" r="14" fill="#88e8ff" stroke="#4080a0" stroke-width="2" opacity="0.9"/>
    <circle cx="591" cy="491" r="4" fill="#ffffff" opacity="0.8"/>
  </g>
  <g id="legs">
    <!-- Geen losse benen, de mantel reikt tot de grond -->
    <ellipse cx="350" cy="945" rx="42" ry="12" fill="#3a2818"/>
    <ellipse cx="450" cy="945" rx="42" ry="12" fill="#3a2818"/>
  </g>
</svg>"""


# ----------------------------------------------------------------------
# Pip — een vriendelijke mascotte (klein wezen)
# ----------------------------------------------------------------------
_PIP_SVG = r"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 1000">
  <g id="head_base">
    <!-- Rond hoofd -->
    <circle cx="400" cy="350" r="220" fill="#88c8e8" stroke="#3a6890" stroke-width="4"/>
    <!-- Lichte vlek op buik / borst -->
    <ellipse cx="400" cy="500" rx="140" ry="180" fill="#c8e8f8" opacity="0.8"/>
    <!-- Wangetjes -->
    <circle cx="270" cy="380" r="20" fill="#ff9090" opacity="0.6"/>
    <circle cx="530" cy="380" r="20" fill="#ff9090" opacity="0.6"/>
  </g>
  <g id="body">
    <!-- Lichaam zit verbonden aan hoofd, geen aparte vorm nodig -->
  </g>
  <g id="left_arm">
    <!-- Kleine zijvinnen/handen -->
    <ellipse cx="200" cy="500" rx="40" ry="60" fill="#88c8e8" stroke="#3a6890" stroke-width="3"/>
  </g>
  <g id="right_arm">
    <ellipse cx="600" cy="500" rx="40" ry="60" fill="#88c8e8" stroke="#3a6890" stroke-width="3"/>
  </g>
  <g id="legs">
    <!-- Kleine voetjes onderaan -->
    <ellipse cx="350" cy="600" rx="40" ry="20" fill="#88c8e8" stroke="#3a6890" stroke-width="3"/>
    <ellipse cx="450" cy="600" rx="40" ry="20" fill="#88c8e8" stroke="#3a6890" stroke-width="3"/>
  </g>
</svg>"""


# ----------------------------------------------------------------------
# Karakter-registratie
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# Drake — vuurspuwende rode draak
# ----------------------------------------------------------------------
_DRAKE_SVG = r"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 1000">
  <defs>
    <linearGradient id="drake_body" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#cc2020"/>
      <stop offset="50%" style="stop-color:#8b0000"/>
      <stop offset="100%" style="stop-color:#4a0000"/>
    </linearGradient>
    <linearGradient id="drake_belly" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#ffa030"/>
      <stop offset="100%" style="stop-color:#cc6010"/>
    </linearGradient>
  </defs>

  <!-- Vleugels achter het lichaam -->
  <g id="wings">
    <!-- Linker vleugel -->
    <path d="M 230 380 Q 100 320 80 480 Q 130 470 200 470 Q 220 450 230 420 Z"
          fill="#5a0000" stroke="#2a0000" stroke-width="3"/>
    <path d="M 230 420 L 200 470 M 230 405 L 175 460 M 230 390 L 150 450"
          stroke="#2a0000" stroke-width="2" fill="none"/>
    <!-- Rechter vleugel -->
    <path d="M 570 380 Q 700 320 720 480 Q 670 470 600 470 Q 580 450 570 420 Z"
          fill="#5a0000" stroke="#2a0000" stroke-width="3"/>
    <path d="M 570 420 L 600 470 M 570 405 L 625 460 M 570 390 L 650 450"
          stroke="#2a0000" stroke-width="2" fill="none"/>
  </g>

  <!-- Hoofd -->
  <g id="head_base">
    <!-- Hoorns -->
    <path d="M 320 180 Q 305 130 290 100 L 310 95 Q 330 130 345 175 Z"
          fill="#8b0000" stroke="#3a0000" stroke-width="2"/>
    <path d="M 480 180 Q 495 130 510 100 L 490 95 Q 470 130 455 175 Z"
          fill="#8b0000" stroke="#3a0000" stroke-width="2"/>
    <!-- Hoofdvorm: gestrekte snuit -->
    <ellipse cx="400" cy="290" rx="135" ry="155" fill="url(#drake_body)" stroke="#2a0000" stroke-width="3"/>
    <!-- Snuit -->
    <ellipse cx="400" cy="365" rx="80" ry="55" fill="#a01010" stroke="#2a0000" stroke-width="2"/>
    <!-- Neusgaten -->
    <ellipse cx="380" cy="350" rx="6" ry="9" fill="#1a0000"/>
    <ellipse cx="420" cy="350" rx="6" ry="9" fill="#1a0000"/>
    <!-- Wenkbrauw-richels -->
    <path d="M 320 250 Q 360 230 395 252" stroke="#3a0000" stroke-width="5" fill="none" stroke-linecap="round"/>
    <path d="M 405 252 Q 440 230 480 250" stroke="#3a0000" stroke-width="5" fill="none" stroke-linecap="round"/>
    <!-- Vurige gloed onder kaak -->
    <ellipse cx="400" cy="400" rx="40" ry="12" fill="#ff6010" opacity="0.5"/>
    <!-- Schub-stippen op voorhoofd -->
    <circle cx="345" cy="220" r="4" fill="#3a0000"/>
    <circle cx="400" cy="200" r="4" fill="#3a0000"/>
    <circle cx="455" cy="220" r="4" fill="#3a0000"/>
    <!-- Kaaklijn-stippen -->
    <circle cx="350" cy="330" r="3" fill="#3a0000"/>
    <circle cx="450" cy="330" r="3" fill="#3a0000"/>
  </g>

  <!-- Lichaam -->
  <g id="body">
    <!-- Borst en buik -->
    <path d="M 280 440 Q 270 600 290 800 L 510 800 Q 530 600 520 440 Z"
          fill="url(#drake_body)" stroke="#2a0000" stroke-width="3"/>
    <!-- Lichtere buikplaten -->
    <path d="M 340 480 L 340 740 L 460 740 L 460 480 Z" fill="url(#drake_belly)" opacity="0.85"/>
    <!-- Buikplaat-strepen -->
    <line x1="340" y1="540" x2="460" y2="540" stroke="#a04010" stroke-width="2"/>
    <line x1="340" y1="600" x2="460" y2="600" stroke="#a04010" stroke-width="2"/>
    <line x1="340" y1="660" x2="460" y2="660" stroke="#a04010" stroke-width="2"/>
    <line x1="340" y1="720" x2="460" y2="720" stroke="#a04010" stroke-width="2"/>
  </g>

  <!-- Armen / klauwen -->
  <g id="left_arm">
    <path d="M 280 470 Q 230 550 230 660 L 260 660 Q 260 550 305 480 Z"
          fill="url(#drake_body)" stroke="#2a0000" stroke-width="2"/>
    <!-- Klauw -->
    <ellipse cx="240" cy="670" rx="25" ry="18" fill="#8b0000" stroke="#2a0000" stroke-width="2"/>
    <!-- 3 klauwnagels -->
    <path d="M 220 685 L 215 700 M 240 685 L 240 705 M 260 685 L 265 700"
          stroke="#1a0000" stroke-width="3" stroke-linecap="round"/>
  </g>
  <g id="right_arm">
    <path d="M 520 470 Q 570 550 570 660 L 540 660 Q 540 550 495 480 Z"
          fill="url(#drake_body)" stroke="#2a0000" stroke-width="2"/>
    <ellipse cx="560" cy="670" rx="25" ry="18" fill="#8b0000" stroke="#2a0000" stroke-width="2"/>
    <path d="M 540 685 L 535 700 M 560 685 L 560 705 M 580 685 L 585 700"
          stroke="#1a0000" stroke-width="3" stroke-linecap="round"/>
  </g>

  <!-- Benen + voeten -->
  <g id="legs">
    <path d="M 320 800 L 320 930 L 380 930 L 390 800 Z" fill="url(#drake_body)" stroke="#2a0000" stroke-width="2"/>
    <path d="M 410 800 L 420 930 L 480 930 L 480 800 Z" fill="url(#drake_body)" stroke="#2a0000" stroke-width="2"/>
    <!-- Klauwen-voeten -->
    <ellipse cx="350" cy="945" rx="45" ry="16" fill="#5a0000" stroke="#1a0000" stroke-width="2"/>
    <ellipse cx="450" cy="945" rx="45" ry="16" fill="#5a0000" stroke="#1a0000" stroke-width="2"/>
    <!-- Voetnagels -->
    <path d="M 320 955 L 315 970 M 350 960 L 350 978 M 380 955 L 385 970"
          stroke="#1a0000" stroke-width="3" stroke-linecap="round"/>
    <path d="M 420 955 L 415 970 M 450 960 L 450 978 M 480 955 L 485 970"
          stroke="#1a0000" stroke-width="3" stroke-linecap="round"/>
  </g>

  <!-- Staart aan de zijkant -->
  <g id="tail">
    <path d="M 520 800 Q 600 770 650 720 Q 700 680 700 620"
          stroke="#8b0000" stroke-width="20" fill="none" stroke-linecap="round"/>
    <path d="M 690 600 L 720 580 L 710 615 Z" fill="#8b0000" stroke="#2a0000" stroke-width="2"/>
  </g>
</svg>"""


# ----------------------------------------------------------------------
# Karakter-registratie
# ----------------------------------------------------------------------
CHARACTERS = {
    "alfred": {
        "name": "Alfred",
        "description": "Chique butler met dienblad en paraplu (standaard)",
        "svg": _ALFRED_SVG,
        "eye_left": (370, 295),
        "eye_right": (430, 295),
        "mouth": (400, 345),
        "eye_radius": 12,
        "pupil_radius": 5,
        "svg_width": 800,
        "svg_height": 1000,
    },
    "sophie": {
        "name": "Sophie",
        "description": "Vriendelijke huishoudster met wit kapje, schort en plumeau",
        "svg": _SOPHIE_SVG,
        "eye_left": (370, 295),
        "eye_right": (430, 295),
        "mouth": (400, 345),
        "eye_radius": 12,
        "pupil_radius": 5,
        "svg_width": 800,
        "svg_height": 1000,
    },
    "robo": {
        "name": "Robo",
        "description": "Vriendelijke retro-robot met visor en knipperlichten",
        "svg": _ROBO_SVG,
        "eye_left": (355, 280),
        "eye_right": (445, 280),
        "mouth": (400, 380),
        "eye_radius": 16,
        "pupil_radius": 7,
        "svg_width": 800,
        "svg_height": 1000,
    },
    "sage": {
        "name": "Sage",
        "description": "Wijze tovenaar met staf, boek en sterrenmantel",
        "svg": _SAGE_SVG,
        "eye_left": (370, 300),
        "eye_right": (430, 300),
        "mouth": (400, 345),
        "eye_radius": 11,
        "pupil_radius": 5,
        "svg_width": 800,
        "svg_height": 1000,
    },
    "pip": {
        "name": "Pip",
        "description": "Klein, schattig wezentje — strak en minimalistisch",
        "svg": _PIP_SVG,
        "eye_left": (320, 320),
        "eye_right": (480, 320),
        "mouth": (400, 410),
        "eye_radius": 22,
        "pupil_radius": 10,
        "svg_width": 800,
        "svg_height": 1000,
    },
    "drake": {
        "name": "Drake",
        "description": "Vurige rode draak met vleugels, hoorns en klauwen",
        "svg": _DRAKE_SVG,
        "eye_left": (360, 285),
        "eye_right": (440, 285),
        "mouth": (400, 365),
        "eye_radius": 14,
        "pupil_radius": 6,
        "svg_width": 800,
        "svg_height": 1000,
    },
}


def get_character(char_id: str = None) -> dict:
    """Geef het karakter-dict voor een ID; valt terug op Alfred bij onbekend ID."""
    if char_id is None:
        char_id = config.get("character_id", "alfred")
    return CHARACTERS.get(char_id, CHARACTERS["alfred"])


def list_characters() -> list:
    """Lijst (id, name, description) voor in een UI-selector."""
    return [(cid, c["name"], c["description"]) for cid, c in CHARACTERS.items()]


# ========================================================================
# BROWSER EXTENSIES (Dark Reader, adblock, etc.)  (was: core/browser_extensions.py)
# ========================================================================

# ----------------------------------------------------------------------
# Locatie van eigen extensies (in de app-map, naast deskbutler.py)
# ----------------------------------------------------------------------
def get_extensions_dir() -> Path:
    """Map waarin eigen extensies van de gebruiker staan."""
    try:
        if getattr(sys, "frozen", False):
            app_dir = Path(sys.executable).resolve().parent
        else:
            app_dir = Path(sys.argv[0]).resolve().parent
        ext_dir = app_dir / "extensions"
        # Test schrijfbaar
        try:
            ext_dir.mkdir(parents=True, exist_ok=True)
            test = ext_dir / ".write_test"
            test.write_text("ok")
            test.unlink()
            return ext_dir
        except Exception:
            pass
    except Exception:
        pass
    # Fallback (Program Files): %APPDATA%
    import os
    if os.name == "nt":
        appdata = os.environ.get("APPDATA")
        if appdata:
            d = Path(appdata) / "DeskButler" / "extensions"
            try:
                d.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass
            return d
    fallback = Path.home() / ".deskbutler" / "extensions"
    try:
        fallback.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    return fallback


# ----------------------------------------------------------------------
# INGEBOUWDE EXTENSIES
# ----------------------------------------------------------------------

# --- Dark Reader: alle websites donker maken ---
DARK_READER_CSS = """
/*
  Eenvoudige Dark Reader: inverteer de hele pagina en draai de kleur 180°.
  Daarna afbeeldingen, video's en iframes terugzetten zodat die normaal blijven.
*/
html {
    filter: invert(0.92) hue-rotate(180deg) !important;
    background: #1e1e1e !important;
}
/* Afbeeldingen, video's en iframes weer 'normaal' tonen */
img, video, iframe, embed, object, picture,
[style*="background-image"], [class*="logo"], svg {
    filter: invert(1) hue-rotate(180deg) !important;
}
/* Code-blokken een leesbare kleur geven (anders worden ze rood) */
pre, code {
    filter: invert(0) hue-rotate(0deg) !important;
    background: #2a2a2a !important;
    color: #e0e0e0 !important;
}
"""

# --- Advertenties verbergen: veel gebruikte ad-selectors ---
ADBLOCK_CSS = """
/* Verberg veelvoorkomende advertentie-elementen. Niet 100% volledig
   (echte ad-blockers gebruiken EasyList) maar het haalt het meeste weg. */
[id*="advertisement"]:not(body),
[id*="banner-ad"],
[id*="google_ads"],
[id*="googlead"],
[id*="ad-container"],
[id*="ad-wrapper"],
[id*="adsense"],
[class*="advertisement"]:not(body),
[class*="ad-banner"],
[class*="ad-container"],
[class*="ad-wrapper"],
[class*="adsense"],
[class*="adsbygoogle"],
[class*="sponsor"],
[class*="promotion"],
[data-ad-slot],
[data-ad-client],
ins.adsbygoogle,
iframe[src*="doubleclick"],
iframe[src*="googleadservices"],
iframe[src*="googlesyndication"],
iframe[src*="amazon-adsystem"],
iframe[id*="google_ads"],
div[aria-label*="advertisement" i],
div[aria-label*="sponsored" i] {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    width: 0 !important;
}
"""

# --- Cookie-bannerverberger ---
COOKIE_HIDE_CSS = """
/* Verberg veelvoorkomende cookie-popups (auto-accept doet de aanvaarding) */
[id*="cookie-banner"],
[id*="cookieBanner"],
[id*="cookie-notice"],
[id*="cookieNotice"],
[id*="cookie-consent"],
[id*="cookieConsent"],
[class*="cookie-banner"],
[class*="cookieBanner"],
[class*="cookie-consent"],
[class*="cookieConsent"],
[class*="cookie-notice"],
[aria-label*="cookie" i] {
    display: none !important;
}
body { overflow: auto !important; }
"""

# --- Voorlezen-knop op elke pagina ---
READER_JS = r"""
(function() {
    if (document.getElementById('__deskbutler_reader_btn')) return;
    var btn = document.createElement('button');
    btn.id = '__deskbutler_reader_btn';
    btn.textContent = '🔊';
    btn.title = 'Voorlezen (selecteer eerst tekst)';
    btn.style.cssText = [
        'position:fixed','bottom:20px','right:20px',
        'width:60px','height:60px','border-radius:50%',
        'background:#707070','color:#fff','border:3px solid #909090',
        'font-size:28px','cursor:pointer','z-index:2147483647',
        'box-shadow:0 4px 12px rgba(0,0,0,0.4)'
    ].join(';');
    btn.onclick = function() {
        var sel = window.getSelection().toString();
        var text = sel || document.body.innerText.substring(0, 2000);
        // Stuur naar Python via een speciale URL
        window.location.href = 'deskbutler://speak?' + encodeURIComponent(text);
    };
    document.body.appendChild(btn);
})();
"""

# --- Tekst-vergroten: extra grote teksten + ruime regelafstand ---
LARGE_TEXT_CSS = """
/* Voor leesgemak bij slechtziendheid: vergroot tekst + ruimte */
body, p, span, div, a, li, td, th, label {
    font-size: 1.15em !important;
    line-height: 1.7 !important;
}
h1 { font-size: 2.4em !important; }
h2 { font-size: 1.9em !important; }
h3 { font-size: 1.5em !important; }
"""


# ----------------------------------------------------------------------
# Greasemonkey / Tampermonkey API shim
# ----------------------------------------------------------------------
# Veel userscripts van greasyfork.org gebruiken GM_* functies die alleen
# in de Greasemonkey/Tampermonkey omgeving bestaan. Zonder deze functies
# crashen die scripts stil bij het laden. Onderstaande shim voegt
# fallback-implementaties toe die de meeste scripts laten werken.
#
# Beperkingen:
#  - GM_xmlhttpRequest gebruikt fetch() — onderhevig aan CORS-regels van
#    de QWebEngineView. Sommige scripts werken hierdoor alsnog niet.
#  - GM_download opent gewoon de URL in een nieuw venster (downloads gaan
#    via de browser-download-handler die we niet hebben aangesloten).
#  - Geen sandboxing tussen scripts en pagina — `unsafeWindow` is identiek
#    aan `window`.
GM_API_SHIM = r"""
// === DeskButler GM API shim ===
// Stelt populaire Greasemonkey-functies beschikbaar zodat userscripts
// van greasyfork.org/tampermonkey gemakkelijk(er) werken.
(function() {
    if (window.__deskbutler_gm_installed) return;
    window.__deskbutler_gm_installed = true;

    // localStorage onder DeskButler-namespace
    function _key(k) { return '__db_gm__' + k; }

    // GM_setValue / GM_getValue / GM_deleteValue / GM_listValues
    window.GM_setValue = function(k, v) {
        try { localStorage.setItem(_key(k), JSON.stringify(v)); } catch(e) {}
    };
    window.GM_getValue = function(k, def) {
        try {
            var raw = localStorage.getItem(_key(k));
            return raw === null ? def : JSON.parse(raw);
        } catch(e) { return def; }
    };
    window.GM_deleteValue = function(k) {
        try { localStorage.removeItem(_key(k)); } catch(e) {}
    };
    window.GM_listValues = function() {
        var out = [];
        for (var i = 0; i < localStorage.length; i++) {
            var k = localStorage.key(i);
            if (k && k.indexOf('__db_gm__') === 0) out.push(k.substring(9));
        }
        return out;
    };

    // GM_addStyle: voeg een <style>-blok toe
    window.GM_addStyle = function(css) {
        var style = document.createElement('style');
        style.textContent = css;
        (document.head || document.documentElement).appendChild(style);
        return style;
    };

    // GM_xmlhttpRequest: wrap fetch() naar oud-stijl XHR callback
    window.GM_xmlhttpRequest = function(opts) {
        var headers = opts.headers || {};
        var init = {
            method: opts.method || 'GET',
            headers: headers,
            body: opts.data,
            credentials: 'include',
            mode: 'cors',
        };
        fetch(opts.url, init).then(function(resp) {
            return resp.text().then(function(text) {
                var event = {
                    status: resp.status,
                    statusText: resp.statusText,
                    responseText: text,
                    response: text,
                    responseURL: resp.url,
                    readyState: 4,
                    finalUrl: resp.url,
                };
                if (opts.onload) opts.onload(event);
            });
        }).catch(function(err) {
            if (opts.onerror) opts.onerror({error: err, statusText: String(err)});
        });
    };

    // GM_openInTab: open URL in nieuw venster
    window.GM_openInTab = function(url, opts) {
        return window.open(url, '_blank');
    };

    // GM_download: probeert te downloaden (fallback: open in nieuw venster)
    window.GM_download = function(arg, name) {
        var url = (typeof arg === 'string') ? arg : (arg && arg.url);
        var fname = name || (arg && arg.name);
        if (!url) return;
        try {
            var a = document.createElement('a');
            a.href = url;
            if (fname) a.download = fname;
            a.target = '_blank';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        } catch(e) {
            window.open(url, '_blank');
        }
    };

    // GM_notification: gebruik browser Notification API als beschikbaar
    window.GM_notification = function(opts) {
        var text = (typeof opts === 'string') ? opts : (opts.text || opts.title || '');
        try {
            if (window.Notification && Notification.permission === 'granted') {
                new Notification(opts.title || 'Mededeling', {body: text});
            } else {
                console.log('[GM_notification]', text);
            }
        } catch(e) { console.log('[GM_notification]', text); }
    };

    // GM_setClipboard: kopieer naar klembord
    window.GM_setClipboard = function(text) {
        try {
            if (navigator.clipboard) navigator.clipboard.writeText(text);
        } catch(e) {}
    };

    // GM_info: minimale meta-informatie
    window.GM_info = {
        script: {name: 'DeskButler userscript', version: '1.0'},
        scriptHandler: 'DeskButler',
        version: '1.0',
    };

    // unsafeWindow: in DeskButler is alles in dezelfde context
    if (typeof window.unsafeWindow === 'undefined') {
        window.unsafeWindow = window;
    }

    // GM convenience: alleen log naar console (handig voor debug)
    if (typeof window.GM_log === 'undefined') {
        window.GM_log = function(msg) { console.log('[GM_log]', msg); };
    }
})();
"""


# --- YouTube Ads-Bypass: skip YouTube video-advertenties ---
# Gebaseerd op het greasyfork userscript "YouTube Ads-Bypass" door WakeUpNeo,
# MIT licentie. Aangepast voor DeskButler: verwijderd de inter-language
# strings (alleen NL/EN) en de console.log opmerkingen voor onze logger.
YOUTUBE_ADS_BYPASS_JS = r"""
(function() {
    if (window.__deskbutler_yt_ads_bypass) return;
    window.__deskbutler_yt_ads_bypass = true;
    if (!/youtube\.com/.test(location.host)) return;

    'use strict';

    var SELECTORS = {
        toHide: [
            '.ytp-ad-message-container',
            'ytd-player-legacy-desktop-watch-ads-renderer',
            'ytd-ad-slot-renderer',
            '#masthead-ad',
            'tp-yt-paper-dialog:has(#feedback.ytd-enforcement-message-view-model)',
            '.yt-mealbar-promo-renderer',
            '.ytp-ad-player-overlay-layout__player-card-container',
            '.ytp-ad-player-overlay-layout__ad-info-container',
            '.ytp-ad-player-overlay-layout__ad-disclosure-banner-container',
            '.ytp-ad-player-overlay',
            '.ad-showing > video',
            '.ad-interrupting > video',
            'div:has(> div#banner)',
            'ytd-engagement-panel-section-list-renderer[target-id="engagement-panel-ads"]',
            'ytd-rich-item-renderer:has(ytd-ad-slot-renderer)',
            'ytmusic-mealbar-promo-renderer',
            'ytd-in-feed-ad-layout-renderer',
            '#player-ads',
            '.ytd-video-masthead-ad-v3-renderer',
            'ytd-ad-selection-preview-renderer',
            '.ytp-ad-image-overlay',
            '#root.yt-chips-search-renderer-header-v2',
            '.ytp-cued-thumbnail-overlay',
            '.ytp-ad-avatar',
            '.ytp-ad-button-vm'
        ],
        player: ['#movie_player', '.html5-video-player'],
        skipButtons: [
            '.ytp-ad-skip-button-modern',
            '.ytp-skip-ad-button',
            '.ytp-ad-skip-button',
            '.ytp-ad-skip-button-slot',
            '.ytp-ad-skip-button-container'
        ]
    };
    var selectors = {
        toHide: SELECTORS.toHide.join(', '),
        player: SELECTORS.player.join(', '),
        skipButtons: SELECTORS.skipButtons.join(', ')
    };

    var player = null, playerObs = null, video = null;
    var spinner = null, cuedThumb = null;
    var lastSkip = 0, adActive = false;

    function injectStyles() {
        var s = document.createElement('style');
        s.setAttribute('data-deskbutler', '1');
        s.textContent =
            '@keyframes dbAnimSkip { 0%{transform:translate(-8px,0);opacity:0} 25%{opacity:1} 75%{opacity:1} 100%{transform:translate(30px,0);opacity:0} } ' +
            selectors.toHide + ' { display:flex !important; visibility:hidden !important; opacity:0 !important; pointer-events:none !important; height:1px !important; width:1px !important; overflow:hidden !important; } ' +
            selectors.skipButtons + ' { display:flex !important; border:1px solid yellow !important; background-color:rgba(247,241,40,0.6) !important; box-shadow:0 0 20px #DD3 !important; overflow:hidden !important; } ' +
            '.ytp-skip-ad { display:flex !important; } ' +
            '.ytp-prev-button, .ytp-next-button { display:flex !important; } ' +
            '.ad-simple-attributed-string { visibility:hidden; } ' +
            '.ad-simple-attributed-string::before { content:"Wacht of druk op Overslaan"; display:flex !important; visibility:visible; color:white; width:100% !important; justify-content:center !important; white-space:nowrap !important; } ' +
            '.ytp-skip-ad-button__icon { transform:translate(-8px,0); animation:1s linear 0s infinite dbAnimSkip; }';
        (document.head || document.documentElement).appendChild(s);
    }

    function isAdActive() {
        return player && (
            player.classList.contains('ad-showing') ||
            player.classList.contains('ad-interrupting') ||
            player.classList.contains('ytp-ad-player-overlay')
        );
    }

    function skipAction() {
        if (!video) return;
        if (!video.muted) { video.muted = true; video.volume = 0; }
        if (video.playbackRate !== 2.0) { video.playbackRate = 2.0; }
        if (isFinite(video.duration) && video.duration > 0) {
            video.currentTime = video.duration - 0.1;
        }
        if (video.paused) { try { video.play(); } catch(e){} }
    }

    function checkAndSkip() {
        if (!video || !video.isConnected) video = document.querySelector('video');
        if (!video) return;
        var now = Date.now();
        if (now - lastSkip < 500) return;
        lastSkip = now;
        if (isAdActive()) {
            adActive = true;
            skipAction();
        } else if (adActive) {
            adActive = false;
            if (video.muted) { video.muted = false; }
            if (video.playbackRate > 1) { video.playbackRate = 1; }
        }
    }

    function setupObserver() {
        player = document.querySelector(selectors.player);
        if (player && !playerObs) {
            playerObs = new MutationObserver(checkAndSkip);
            playerObs.observe(player, {attributes: true, attributeFilter: ['class']});
            checkAndSkip();
        }
    }

    window.addEventListener('yt-navigate-finish', setupObserver);
    window.addEventListener('yt-page-data-updated', setupObserver);
    window.addEventListener('load', setupObserver);
    if (document.readyState === 'loading') {
        window.addEventListener('DOMContentLoaded', injectStyles);
    } else {
        injectStyles();
    }

    // Fallback voor het geval load-events al gevallen zijn
    var tries = 0;
    var retry = setInterval(function() {
        setupObserver();
        if (playerObs || tries > 10) clearInterval(retry);
        tries++;
    }, 1000);

    console.log('[DeskButler] YouTube Ads-Bypass actief');
})();
"""


# ----------------------------------------------------------------------
# Extensie-class
# ----------------------------------------------------------------------
class BrowserExtension:
    """
    Eén extensie die CSS en/of JS in webpagina's injecteert.

    type='builtin': ingebouwd in DeskButler (gebruiker kan alleen aan/uit)
    type='user'   : door gebruiker zelf gemaakt (kan worden bewerkt)
    """

    def __init__(self, ext_id: str, name: str, description: str,
                 css: str = "", js: str = "",
                 type_: str = "builtin",
                 file_path: Optional[Path] = None,
                 url_pattern: str = "*",
                 enabled: bool = False):
        self.id = ext_id
        self.name = name
        self.description = description
        self.css = css
        self.js = js
        self.type = type_  # 'builtin' of 'user'
        self.file_path = file_path
        self.url_pattern = url_pattern  # bv. "*", "*google.com*"
        self.enabled = enabled

    def matches_url(self, url: str) -> bool:
        """Past deze extensie op deze URL?"""
        if not self.url_pattern or self.url_pattern == "*":
            return True
        # Eenvoudige wildcard-match: * matched alles ertussen
        pat = self.url_pattern.replace(".", r"\.").replace("*", ".*")
        try:
            return bool(re.match(f"^{pat}$", url))
        except re.error:
            return True

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "description": self.description,
            "type": self.type, "url_pattern": self.url_pattern,
            "enabled": self.enabled,
        }


# ----------------------------------------------------------------------
# ExtensionsManager
# ----------------------------------------------------------------------
class ExtensionsManager:
    """Centraal punt voor alle extensies (laad, sla op, toggle)."""

    def __init__(self):
        self._extensions: Dict[str, BrowserExtension] = {}
        self._load_builtin()
        self._load_user()

    def _load_builtin(self):
        """Registreer de ingebouwde extensies."""
        builtins = [
            BrowserExtension(
                ext_id="dark_reader",
                name="🌙 Dark Reader",
                description=(
                    "Toon alle websites in een donker thema. Rustig voor de "
                    "ogen, vooral 's avonds. Afbeeldingen blijven normaal."
                ),
                css=DARK_READER_CSS,
                type_="builtin",
            ),
            BrowserExtension(
                ext_id="adblock_css",
                name="🚫 Advertenties verbergen",
                description=(
                    "Verberg de meest voorkomende advertentie-blokken op "
                    "websites. Werkt aanvullend op de DNS-adblock van DeskButler."
                ),
                css=ADBLOCK_CSS,
                type_="builtin",
            ),
            BrowserExtension(
                ext_id="cookie_hide",
                name="🍪 Cookie-banners verbergen",
                description=(
                    "Verberg cookie-toestemming-popups (auto-accept blijft "
                    "wel werken op de achtergrond)."
                ),
                css=COOKIE_HIDE_CSS,
                type_="builtin",
            ),
            BrowserExtension(
                ext_id="large_text",
                name="🔍 Grote tekst",
                description=(
                    "Vergroot tekst en regelafstand op alle websites voor "
                    "betere leesbaarheid."
                ),
                css=LARGE_TEXT_CSS,
                type_="builtin",
            ),
            BrowserExtension(
                ext_id="reader_button",
                name="🔊 Voorlees-knop",
                description=(
                    "Toon een ronde 🔊-knop rechtsonder op elke webpagina. "
                    "Klik om de geselecteerde tekst (of pagina-inleiding) "
                    "voor te laten lezen door de butler."
                ),
                js=READER_JS,
                type_="builtin",
            ),
            BrowserExtension(
                ext_id="youtube_ads_bypass",
                name="🎬 YouTube zonder ads",
                description=(
                    "Slaat video-advertenties op YouTube automatisch over "
                    "door ze te dempen, op 2× snelheid te zetten, en naar "
                    "het einde te springen. Verbergt ook reclame-banners "
                    "en overlay-promoties.\n\n"
                    "Werkt op youtube.com en music.youtube.com. "
                    "Gebaseerd op het MIT-licensed greasyfork-script "
                    "'YouTube Ads-Bypass' door WakeUpNeo."
                ),
                js=YOUTUBE_ADS_BYPASS_JS,
                type_="builtin",
                url_pattern="*youtube.com*",
            ),
        ]
        # Haal opgeslagen aan/uit-status op
        enabled_ids = set(config.get("enabled_extensions", []))
        for ext in builtins:
            ext.enabled = ext.id in enabled_ids
            self._extensions[ext.id] = ext

    def _load_user(self):
        """Lees user-extensies uit de extensions/ map."""
        enabled_ids = set(config.get("enabled_extensions", []))
        ext_dir = get_extensions_dir()
        if not ext_dir.exists():
            return
        for path in sorted(ext_dir.glob("*.user.js")):
            try:
                content = path.read_text(encoding="utf-8", errors="replace")
                meta = self._parse_meta(content)
                ext_id = f"user_{path.stem.replace('.user', '')}"
                ext = BrowserExtension(
                    ext_id=ext_id,
                    name=meta.get("name", path.stem),
                    description=meta.get("description", "(eigen extensie)"),
                    js=content,
                    type_="user",
                    file_path=path,
                    url_pattern=meta.get("match", "*"),
                    enabled=ext_id in enabled_ids,
                )
                self._extensions[ext_id] = ext
            except Exception as e:
                print(f"[extensions] kon {path.name} niet laden: {e}")
        for path in sorted(ext_dir.glob("*.user.css")):
            try:
                content = path.read_text(encoding="utf-8", errors="replace")
                meta = self._parse_meta(content)
                ext_id = f"user_{path.stem.replace('.user', '')}_css"
                ext = BrowserExtension(
                    ext_id=ext_id,
                    name=meta.get("name", path.stem),
                    description=meta.get("description", "(eigen stijl-extensie)"),
                    css=content,
                    type_="user",
                    file_path=path,
                    url_pattern=meta.get("match", "*"),
                    enabled=ext_id in enabled_ids,
                )
                self._extensions[ext_id] = ext
            except Exception as e:
                print(f"[extensions] kon {path.name} niet laden: {e}")

    def _parse_meta(self, content: str) -> dict:
        """
        Parse Greasemonkey-stijl meta-block uit een script:
            // ==UserScript==
            // @name        Naam
            // @description Wat het doet
            // @match       *://*.example.com/*
            // ==/UserScript==
        Of de CSS-variant met /* ==UserStyle== */ ... /* ==/UserStyle== */
        """
        meta = {}
        m = re.search(
            r"==(?:UserScript|UserStyle)==(.*?)==/(?:UserScript|UserStyle)==",
            content, re.DOTALL,
        )
        if not m:
            return meta
        for line in m.group(1).splitlines():
            mm = re.match(r"^[\s/*]*@(\w+)\s+(.+?)[\s*]*$", line)
            if mm:
                key, val = mm.group(1).strip(), mm.group(2).strip()
                meta[key] = val
        return meta

    def all(self) -> List[BrowserExtension]:
        return list(self._extensions.values())

    def get(self, ext_id: str) -> Optional[BrowserExtension]:
        return self._extensions.get(ext_id)

    def enabled_for_url(self, url: str) -> List[BrowserExtension]:
        return [e for e in self._extensions.values()
                if e.enabled and e.matches_url(url)]

    def set_enabled(self, ext_id: str, enabled: bool):
        ext = self._extensions.get(ext_id)
        if not ext:
            return
        ext.enabled = enabled
        ids = [e.id for e in self._extensions.values() if e.enabled]
        config.set("enabled_extensions", ids)

    def save_user_extension(self, name: str, content: str, kind: str = "js") -> Path:
        """
        Sla een nieuwe of bijgewerkte user-extensie op naar disk.
        kind: 'js' of 'css'
        """
        ext_dir = get_extensions_dir()
        ext_dir.mkdir(parents=True, exist_ok=True)
        safe = re.sub(r"[^a-zA-Z0-9_-]", "_", name)
        path = ext_dir / f"{safe}.user.{kind}"
        path.write_text(content, encoding="utf-8")
        # Herlaad om de nieuwe in de manager te krijgen
        self._load_user()
        return path

    def delete_user_extension(self, ext_id: str) -> bool:
        ext = self._extensions.get(ext_id)
        if not ext or ext.type != "user" or not ext.file_path:
            return False
        try:
            ext.file_path.unlink()
        except Exception as e:
            print(f"[extensions] verwijderen faalde: {e}")
            return False
        del self._extensions[ext_id]
        # Update config
        ids = [e.id for e in self._extensions.values() if e.enabled]
        config.set("enabled_extensions", ids)
        return True


# Singleton — eenmalig geladen
# Singleton — eigen naam om collision met andere modules in single-file
# build te voorkomen
_extensions_manager: Optional[ExtensionsManager] = None


def get_extensions_manager() -> ExtensionsManager:
    global _extensions_manager
    if _extensions_manager is None:
        _extensions_manager = ExtensionsManager()
    return _extensions_manager


# ----------------------------------------------------------------------
# JavaScript-helpers voor injectie
# ----------------------------------------------------------------------
def make_css_inject_js(css: str) -> str:
    """
    Maak een JS-snippet dat een <style>-tag injecteert met de gegeven CSS.
    Voor permanente toepassing (CSS-extensies).
    """
    # Escape backticks en backslashes voor template literal
    escaped = css.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
    return f"""
(function() {{
    var style = document.createElement('style');
    style.setAttribute('data-deskbutler', '1');
    style.textContent = `{escaped}`;
    (document.head || document.documentElement).appendChild(style);
}})();
"""


# ----------------------------------------------------------------------
# Voorbeeld-templates voor de gebruiker bij 'Nieuwe extensie'
# ----------------------------------------------------------------------
USERSCRIPT_TEMPLATE = """// ==UserScript==
// @name        Mijn nieuwe script
// @description Wat dit script doet
// @match       *
// @run-at      document-end
// ==/UserScript==

// Schrijf hier uw JavaScript code. Voorbeeld:
// Verberg alle <h1> elementen:
//
// document.querySelectorAll('h1').forEach(function(el) {
//     el.style.display = 'none';
// });

console.log('Mijn nieuwe script is geladen!');
"""

USERSTYLE_TEMPLATE = """/* ==UserStyle==
@name        Mijn nieuwe stijl
@description Wat deze stijl doet
@match       *
==/UserStyle== */

/* Schrijf hier uw CSS. Voorbeeld:
   alle teksten geel maken op een bepaalde site:

body {
    color: yellow !important;
}
*/
"""


# ========================================================================
# FAVORIETEN (met mappen, JSON-opslag)  (was: core/favorites.py)
# ========================================================================

def get_favorites_file() -> Path:
    """Geef het pad naar favorites.json terug (en zorg dat de map bestaat)."""
    try:
        if getattr(sys, "frozen", False):
            app_dir = Path(sys.executable).resolve().parent
        else:
            app_dir = Path(sys.argv[0]).resolve().parent
        # Test schrijfbaarheid
        test = app_dir / ".favorites_write_test"
        try:
            test.write_text("ok")
            test.unlink()
            return app_dir / "favorites.json"
        except Exception:
            pass
    except Exception:
        pass
    # Fallback: APPDATA
    if os.name == "nt":
        appdata = os.environ.get("APPDATA")
        if appdata:
            d = Path(appdata) / "DeskButler"
            d.mkdir(parents=True, exist_ok=True)
            return d / "favorites.json"
    fallback = Path.home() / ".deskbutler"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback / "favorites.json"


class FavoritesManager:
    """
    Centraal beheer van favorieten met mappen.

    API:
      mgr = FavoritesManager()
      mgr.add(title, url, folder_id=None)
      mgr.remove(fav_id)
      mgr.add_folder(name)
      mgr.remove_folder(folder_id)
      mgr.rename_folder(folder_id, new_name)
      mgr.move_to_folder(fav_id, folder_id)
      mgr.all_folders()
      mgr.root_favorites()
      mgr.find(fav_id)
    """

    def __init__(self):
        self._file = get_favorites_file()
        self._data = {"folders": [], "root_favorites": []}
        self._load()

    def _load(self):
        if not self._file.exists():
            return
        try:
            with open(self._file, "r", encoding="utf-8") as f:
                self._data = json.load(f)
            # Zorg dat de keys bestaan (oude bestanden)
            if "folders" not in self._data:
                self._data["folders"] = []
            if "root_favorites" not in self._data:
                self._data["root_favorites"] = []
        except Exception as e:
            print(f"[favorites] laden faalde: {e}")
            self._data = {"folders": [], "root_favorites": []}

    def _save(self):
        try:
            with open(self._file, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[favorites] opslaan faalde: {e}")

    # ------------------------------------------------------------------
    # Favorieten
    # ------------------------------------------------------------------
    def add(self, title: str, url: str,
            folder_id: Optional[str] = None) -> Optional[str]:
        """
        Voeg een favoriet toe. Retourneer het ID, of None bij duplicaat.

        Als de URL al bestaat (waar dan ook), wordt geen nieuwe toegevoegd.
        """
        if self._url_exists(url):
            print(f"[favorites] URL bestaat al: {url}")
            return None
        fav_id = f"b_{uuid.uuid4().hex[:10]}"
        item = {
            "id": fav_id,
            "title": (title or url)[:200],
            "url": url,
            "added": int(time.time()),
        }
        if folder_id:
            folder = self._find_folder(folder_id)
            if folder is not None:
                folder["favorites"].append(item)
            else:
                # Onbekende folder → naar root
                self._data["root_favorites"].append(item)
        else:
            self._data["root_favorites"].append(item)
        self._save()
        return fav_id

    def remove(self, fav_id: str) -> bool:
        """Verwijder een favoriet ongeacht waar hij staat."""
        # Probeer in root
        before = len(self._data["root_favorites"])
        self._data["root_favorites"] = [
            f for f in self._data["root_favorites"] if f["id"] != fav_id
        ]
        if len(self._data["root_favorites"]) < before:
            self._save()
            return True
        # Anders in mappen
        for folder in self._data["folders"]:
            before = len(folder["favorites"])
            folder["favorites"] = [
                f for f in folder["favorites"] if f["id"] != fav_id
            ]
            if len(folder["favorites"]) < before:
                self._save()
                return True
        return False

    def update(self, fav_id: str, title: str = None, url: str = None) -> bool:
        """Wijzig een bestaande favoriet (titel en/of URL)."""
        fav = self.find(fav_id)
        if not fav:
            return False
        if title is not None:
            fav["title"] = title[:200]
        if url is not None:
            fav["url"] = url
        self._save()
        return True

    def move_to_folder(self, fav_id: str, folder_id: Optional[str]) -> bool:
        """
        Verplaats een favoriet naar een map (of root als folder_id=None).
        """
        fav = self.find(fav_id)
        if not fav:
            return False
        # Verwijder uit huidige plek
        self._data["root_favorites"] = [
            f for f in self._data["root_favorites"] if f["id"] != fav_id
        ]
        for folder in self._data["folders"]:
            folder["favorites"] = [
                f for f in folder["favorites"] if f["id"] != fav_id
            ]
        # Plaats op nieuwe plek
        if folder_id:
            target = self._find_folder(folder_id)
            if target:
                target["favorites"].append(fav)
            else:
                self._data["root_favorites"].append(fav)
        else:
            self._data["root_favorites"].append(fav)
        self._save()
        return True

    def find(self, fav_id: str) -> Optional[Dict]:
        """Zoek een favoriet op ID."""
        for f in self._data["root_favorites"]:
            if f["id"] == fav_id:
                return f
        for folder in self._data["folders"]:
            for f in folder["favorites"]:
                if f["id"] == fav_id:
                    return f
        return None

    def find_by_url(self, url: str) -> Optional[Dict]:
        """Zoek een favoriet op URL."""
        for f in self._data["root_favorites"]:
            if f["url"] == url:
                return f
        for folder in self._data["folders"]:
            for f in folder["favorites"]:
                if f["url"] == url:
                    return f
        return None

    def _url_exists(self, url: str) -> bool:
        return self.find_by_url(url) is not None

    def is_favorited(self, url: str) -> bool:
        """Snelle check of een URL al een favoriet is."""
        return self._url_exists(url)

    # ------------------------------------------------------------------
    # Mappen
    # ------------------------------------------------------------------
    def add_folder(self, name: str) -> str:
        """Maak een nieuwe map aan, retourneer het ID."""
        folder_id = f"f_{uuid.uuid4().hex[:10]}"
        self._data["folders"].append({
            "id": folder_id,
            "name": name[:80],
            "favorites": [],
        })
        self._save()
        return folder_id

    def remove_folder(self, folder_id: str, move_to_root: bool = True) -> bool:
        """
        Verwijder een map. Als move_to_root=True, gaan de favorieten in die
        map naar root (anders worden ze ook verwijderd).
        """
        target = self._find_folder(folder_id)
        if not target:
            return False
        if move_to_root and target["favorites"]:
            self._data["root_favorites"].extend(target["favorites"])
        self._data["folders"] = [
            f for f in self._data["folders"] if f["id"] != folder_id
        ]
        self._save()
        return True

    def rename_folder(self, folder_id: str, new_name: str) -> bool:
        folder = self._find_folder(folder_id)
        if not folder:
            return False
        folder["name"] = new_name[:80]
        self._save()
        return True

    def _find_folder(self, folder_id: str) -> Optional[Dict]:
        for f in self._data["folders"]:
            if f["id"] == folder_id:
                return f
        return None

    # ------------------------------------------------------------------
    # Lezen
    # ------------------------------------------------------------------
    def all_folders(self) -> List[Dict]:
        """Geef alle mappen terug, met hun favorieten."""
        return list(self._data["folders"])

    def root_favorites(self) -> List[Dict]:
        """Geef favorieten die niet in een map staan terug."""
        return list(self._data["root_favorites"])

    def total_count(self) -> int:
        """Totaal aantal favorieten over alle mappen + root."""
        n = len(self._data["root_favorites"])
        for f in self._data["folders"]:
            n += len(f["favorites"])
        return n


# Singleton — eigen naam om collision met andere modules in single-file
# build te voorkomen
_favorites_manager: Optional[FavoritesManager] = None


def get_favorites_manager() -> FavoritesManager:
    global _favorites_manager
    if _favorites_manager is None:
        _favorites_manager = FavoritesManager()
    return _favorites_manager


# ========================================================================
# AFBEELDINGSPIKKER (thumbnail loader thread)  (was: core/image_picker.py)
# ========================================================================

# JavaScript die in elke pagina draait om afbeeldings-info te verzamelen.
# Geeft een lijst van {src, width, height, alt, source} objecten terug.
#
# Verzamelt:
#  1. <img> tags (met srcset → hoogste resolutie)
#  2. <picture><source srcset> elementen
#  3. <image> elementen in inline SVG
#  4. Background-images uit inline style attribuut
#  5. Background-images uit computed styles (alleen voor zichtbare elementen)
COLLECT_IMAGES_JS = r"""
(function() {
    // De HELE functie in try/catch zodat we altijd een list teruggeven,
    // ook als er iets in de pagina onverwacht gedrag heeft (sommige
    // sites overschrijven globals of breken DOM-APIs).
    try {
        function bestFromSrcset(srcset) {
            if (!srcset) return null;
            try {
                var candidates = srcset.split(',').map(function(s) {
                    var parts = s.trim().split(/\s+/);
                    var w = 0;
                    if (parts[1]) {
                        var m = parts[1].match(/(\d+)/);
                        if (m) w = parseInt(m[1]);
                    }
                    return { url: parts[0], w: w };
                });
                candidates.sort(function(a, b) { return b.w - a.w; });
                return candidates[0] && candidates[0].url;
            } catch(e) { return null; }
        }

        function extractUrlsFromCss(value) {
            if (!value || value === 'none') return [];
            var out = [];
            try {
                var re = /url\(\s*['"]?([^'")]+)['"]?\s*\)/gi;
                var m;
                while ((m = re.exec(value)) !== null) {
                    out.push(m[1]);
                }
            } catch(e) {}
            return out;
        }

        function absolutize(url) {
            try { return new URL(url, document.baseURI).href; }
            catch(e) { return url; }
        }

        var seen = {};
        var out = [];

        function add(src, width, height, alt, source) {
            try {
                if (!src) return;
                src = absolutize(src);
                if (!/^(https?:|data:image\/)/.test(src)) return;
                if (seen[src]) return;
                seen[src] = true;
                out.push({
                    src: src,
                    width: width || 0,
                    height: height || 0,
                    alt: (alt || '').substring(0, 80),
                    source: source || '?',
                });
            } catch(e) {}
        }

        // 1. <img> tags
        try {
            var imgs = document.querySelectorAll('img');
            for (var i = 0; i < imgs.length; i++) {
                var img = imgs[i];
                var best = bestFromSrcset(img.srcset) || img.currentSrc || img.src;
                add(best, img.naturalWidth || img.width,
                    img.naturalHeight || img.height, img.alt, 'img');
            }
        } catch(e) {}

        // 2. <picture><source srcset>
        try {
            var sources = document.querySelectorAll('picture source[srcset]');
            for (var i = 0; i < sources.length; i++) {
                add(bestFromSrcset(sources[i].srcset), 0, 0, '', 'picture');
            }
        } catch(e) {}

        // 3. SVG <image>
        try {
            var svgImgs = document.querySelectorAll('image');
            for (var i = 0; i < svgImgs.length; i++) {
                var s = svgImgs[i];
                var href = s.getAttribute('href') || s.getAttribute('xlink:href');
                add(href, 0, 0, '', 'svg');
            }
        } catch(e) {}

        // 4. Inline style background-image
        try {
            var styled = document.querySelectorAll('[style*="background"]');
            for (var i = 0; i < styled.length && i < 200; i++) {
                var el = styled[i];
                var urls = extractUrlsFromCss(el.style.backgroundImage);
                if (urls.length === 0) continue;
                var rect = el.getBoundingClientRect();
                for (var j = 0; j < urls.length; j++) {
                    add(urls[j], rect.width, rect.height, '', 'bg-inline');
                }
            }
        } catch(e) {}

        // 5. Computed background-image — minder agressief (max 200, simpelere
        //    selector) om traagheid op grote pagina's te voorkomen
        try {
            var candidates = document.querySelectorAll('div, section, figure, a');
            var checked = 0;
            for (var i = 0; i < candidates.length && checked < 200; i++) {
                var el = candidates[i];
                var rect = el.getBoundingClientRect();
                if (rect.width < 100 || rect.height < 100) continue;
                checked++;
                var cs = window.getComputedStyle(el);
                if (!cs || cs.display === 'none' || cs.visibility === 'hidden') continue;
                var urls = extractUrlsFromCss(cs.backgroundImage);
                for (var j = 0; j < urls.length; j++) {
                    add(urls[j], rect.width, rect.height, '', 'bg-css');
                }
            }
        } catch(e) {}

        return JSON.stringify(out);
    } catch(fatalError) {
        // Laatste vangnet — geef ALTIJD een geldige JSON string terug
        return JSON.stringify([{
            src: '_error_', width: 0, height: 0, alt: '',
            source: 'fatal:' + String(fatalError),
        }]);
    }
})();
"""


def get_downloads_dir() -> Path:
    """Geef de downloads-map terug (gedeeld met video downloader)."""
    try:
        return _gdd()
    except Exception:
        # Fallback: zelf bepalen
        if getattr(sys, "frozen", False):
            app_dir = Path(sys.executable).resolve().parent
        else:
            app_dir = Path(sys.argv[0]).resolve().parent
        d = app_dir / "downloads"
        d.mkdir(parents=True, exist_ok=True)
        return d


def get_img_extension(url: str, content_type: str = "") -> str:
    """
    Bepaal de juiste bestandsextensie op basis van Content-Type en URL.
    Gebaseerd op Roger's _get_img_ext_from_url_and_ct.
    """
    ct_map = {
        "image/jpeg": ".jpg", "image/jpg": ".jpg",
        "image/png": ".png", "image/gif": ".gif",
        "image/webp": ".webp", "image/svg+xml": ".svg",
        "image/bmp": ".bmp", "image/avif": ".avif",
    }
    ct = content_type.split(";")[0].strip().lower()
    if ct in ct_map:
        return ct_map[ct]
    clean = url.split("?")[0].split("#")[0]
    ext = os.path.splitext(clean)[1].lower()
    if ext in (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".avif"):
        return ".jpg" if ext == ".jpeg" else ext
    return ".jpg"


def safe_image_filename(url: str, ext: str) -> str:
    """Verzin een veilige bestandsnaam op basis van de URL."""
    clean = url.split("?")[0].split("#")[0]
    base = os.path.splitext(os.path.basename(clean))[0] or "afbeelding"
    # Verboden tekens vervangen
    base = re.sub(r'[\\/*?:"<>|]', "_", base)[:80]
    return f"{base}{ext}"


# ----------------------------------------------------------------------
# Async thumbnail-loader
# ----------------------------------------------------------------------
class ThumbnailLoaderThread(QThread):
    """
    Download alle afbeeldings-thumbnails in achtergrond. Per geladen
    thumbnail wordt een signal geëmit zodat de UI direct kan updaten.

    images: list of dicts met {src, width, height, alt}
    """
    thumbnail_ready = Signal(int, bytes)         # index, image data
    thumbnail_failed = Signal(int, str)          # index, error
    progress = Signal(int, int)                  # current, total
    finished_loading = Signal()

    def __init__(self, images: list, parent=None):
        super().__init__(parent)
        self.images = images
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        }
        total = len(self.images)
        for idx, img in enumerate(self.images):
            if self._cancelled:
                return
            url = img.get("src")
            if not url:
                self.thumbnail_failed.emit(idx, "geen URL")
                self.progress.emit(idx + 1, total)
                continue
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=5) as r:
                    data = r.read(5 * 1024 * 1024)  # max 5 MB per thumbnail
                self.thumbnail_ready.emit(idx, data)
            except Exception as e:
                self.thumbnail_failed.emit(idx, str(e))
            self.progress.emit(idx + 1, total)
        self.finished_loading.emit()


# ----------------------------------------------------------------------
# Synchrone download van één afbeelding op volledige resolutie
# ----------------------------------------------------------------------
def download_image_to_file(url: str, target_path: str) -> tuple:
    """
    Download een afbeelding naar disk. Returnt (success, message_or_path).

    Belangrijk: lees ALLE data IN voordat de QFileDialog opent
    (anders raakt de verbinding time-out). Wordt gebruikt door
    'opslaan als'-flow.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        ),
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as r:
            data = r.read(30 * 1024 * 1024)  # max 30 MB
        with open(target_path, "wb") as f:
            f.write(data)
        return True, target_path
    except Exception as e:
        return False, str(e)


def fetch_image_data(url: str) -> Optional[bytes]:
    """
    Download een afbeelding en geef de data terug (zonder schrijven).
    Voor de 'opslaan als'-flow waar we eerst de data willen, dan pas
    een QFileDialog tonen (anders timeout).
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        ),
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read(30 * 1024 * 1024)
    except Exception as e:
        print(f"[picker] fetch_image_data faalde: {e}")
        return None


# ========================================================================
# TOOLS INSTALLER (auto-download yt-dlp + ffmpeg)  (was: core/tools_installer.py)
# ========================================================================

# URLs — officiële bronnen
YT_DLP_URL = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"


def get_tools_dir() -> Path:
    """Geef de submap 'tools' naast de app terug (en maak hem aan)."""
    try:
        if getattr(sys, "frozen", False):
            app_dir = Path(sys.executable).resolve().parent
        else:
            app_dir = Path(sys.argv[0]).resolve().parent
        tools = app_dir / "tools"
        tools.mkdir(parents=True, exist_ok=True)
        # Test schrijfbaar
        test = tools / ".write_test"
        test.write_text("ok")
        test.unlink()
        return tools
    except Exception:
        pass
    # Fallback: APPDATA
    if os.name == "nt":
        appdata = os.environ.get("APPDATA")
        if appdata:
            d = Path(appdata) / "DeskButler" / "tools"
            d.mkdir(parents=True, exist_ok=True)
            return d
    fallback = Path.home() / ".deskbutler" / "tools"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


def _find_in_path(name: str) -> Optional[Path]:
    """Zoek een uitvoerbaar bestand in systeem-PATH."""
    for p in os.environ.get("PATH", "").split(os.pathsep):
        if not p:
            continue
        candidate = Path(p) / name
        if candidate.exists():
            return candidate
        # Windows: probeer ook .exe variant
        if os.name == "nt" and not name.lower().endswith(".exe"):
            candidate_exe = Path(p) / f"{name}.exe"
            if candidate_exe.exists():
                return candidate_exe
    return None


def get_yt_dlp_path() -> Optional[Path]:
    """
    Geef pad naar yt-dlp.exe (of yt-dlp op Linux/Mac). Volgorde:
      1. tools/yt-dlp.exe in app-map
      2. yt-dlp in systeem-PATH
      3. None (moet nog geïnstalleerd worden)
    """
    name = "yt-dlp.exe" if os.name == "nt" else "yt-dlp"
    tools_path = get_tools_dir() / name
    if tools_path.exists():
        return tools_path
    return _find_in_path(name)


def get_ffmpeg_dir() -> Optional[Path]:
    """
    Geef de map terug waarin ffmpeg.exe staat. yt-dlp gebruikt
    --ffmpeg-location met DE MAP, niet het pad naar de exe.
    """
    name = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
    tools_path = get_tools_dir() / name
    if tools_path.exists():
        return tools_path.parent
    found = _find_in_path(name)
    if found:
        return found.parent
    return None


def tools_are_installed() -> bool:
    """True als zowel yt-dlp als ffmpeg gevonden kunnen worden."""
    return get_yt_dlp_path() is not None and get_ffmpeg_dir() is not None


# ----------------------------------------------------------------------
# Versie-detectie + update-check
# ----------------------------------------------------------------------
def get_yt_dlp_version() -> Optional[str]:
    """Haal de huidige yt-dlp versie op (bv. '2026.04.15')."""
    yt = get_yt_dlp_path()
    if not yt:
        return None
    try:
        flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        res = subprocess.run(
            [str(yt), "--version"],
            capture_output=True, text=True, timeout=10,
            creationflags=flags,
        )
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception as e:
        print(f"[tools] yt-dlp version-check faalde: {e}")
    return None


def get_ffmpeg_version() -> Optional[str]:
    """Haal de huidige ffmpeg versie op (bv. '7.1' uit eerste regel output)."""
    ff_dir = get_ffmpeg_dir()
    if not ff_dir:
        return None
    ff_exe = ff_dir / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
    if not ff_exe.exists():
        return None
    try:
        flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        res = subprocess.run(
            [str(ff_exe), "-version"],
            capture_output=True, text=True, timeout=10,
            creationflags=flags,
        )
        if res.returncode == 0:
            # Eerste regel: "ffmpeg version 7.1-essentials_build-www.gyan.dev ..."
            first = res.stdout.split("\n", 1)[0]
            m = re.search(r"version\s+([\w\.\-]+)", first)
            if m:
                return m.group(1)
            return first.strip()
    except Exception as e:
        print(f"[tools] ffmpeg version-check faalde: {e}")
    return None


def get_latest_yt_dlp_version() -> Optional[str]:
    """Haal de nieuwste yt-dlp versie van GitHub releases."""
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(
            "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest",
            headers={"User-Agent": "DeskButler"},
        )
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("tag_name", "").strip()
    except Exception as e:
        print(f"[tools] latest yt-dlp ophalen faalde: {e}")
        return None


def yt_dlp_is_in_tools_dir() -> bool:
    """True als yt-dlp.exe in onze eigen tools/ map staat (niet PATH)."""
    name = "yt-dlp.exe" if os.name == "nt" else "yt-dlp"
    return (get_tools_dir() / name).exists()


# ----------------------------------------------------------------------
# Update-thread voor yt-dlp
# ----------------------------------------------------------------------
class YtDlpUpdateThread(QThread):
    """Download nieuwste yt-dlp.exe en overschrijf de versie in tools/."""
    progress = Signal(str, int)
    finished_update = Signal(bool, str)

    def run(self):
        try:
            tools = get_tools_dir()
            target = tools / ("yt-dlp.exe" if os.name == "nt" else "yt-dlp")
            ctx = ssl.create_default_context()

            self.progress.emit("Nieuwste versie downloaden...", 0)
            # Download eerst naar tijdelijk bestand, dan vervangen
            tmp = tools / ("yt-dlp.new" if os.name == "nt" else "yt-dlp.new")
            try:
                with urllib.request.urlopen(YT_DLP_URL, context=ctx, timeout=30) as resp:
                    total = int(resp.headers.get("Content-Length", 0)) or 1
                    downloaded = 0
                    with open(tmp, "wb") as f:
                        while True:
                            chunk = resp.read(64 * 1024)
                            if not chunk:
                                break
                            f.write(chunk)
                            downloaded += len(chunk)
                            pct = int((downloaded / total) * 100)
                            mb = downloaded / (1024 * 1024)
                            mb_total = total / (1024 * 1024)
                            self.progress.emit(
                                f"yt-dlp downloaden: {mb:.1f} MB van {mb_total:.1f} MB",
                                pct,
                            )
            except Exception as e:
                self.finished_update.emit(False, f"Download mislukt: {e}")
                try:
                    tmp.unlink()
                except Exception:
                    pass
                return

            # Vervang oude met nieuwe
            try:
                if target.exists():
                    target.unlink()
                tmp.rename(target)
            except Exception as e:
                self.finished_update.emit(False, f"Bestand vervangen mislukt: {e}")
                return

            self.progress.emit("Klaar!", 100)
            self.finished_update.emit(True, "")
        except Exception as e:
            self.finished_update.emit(False, f"Onverwachte fout: {e}")


# ----------------------------------------------------------------------
# Download-thread
# ----------------------------------------------------------------------
class ToolsInstallThread(QThread):
    """
    Downloadt yt-dlp.exe en ffmpeg-essentials.zip in achtergrond.
    Extraheert alleen ffmpeg.exe en ffprobe.exe uit de zip — de rest
    (lib, doc, presets) gooien we weg om schijfruimte te besparen.
    """
    progress = Signal(str, int)   # status-tekst, percentage (0-100)
    finished_install = Signal(bool, str)  # success, error-msg

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            tools = get_tools_dir()
            ctx = ssl.create_default_context()

            # ---- yt-dlp ----
            # Check eerst of yt-dlp al ergens bereikbaar is (in tools/ of PATH).
            # Zo ja, sla deze download over.
            if get_yt_dlp_path():
                self.progress.emit("yt-dlp is al beschikbaar op uw systeem", 25)
            else:
                self.progress.emit("yt-dlp downloaden...", 0)
                try:
                    self._download(YT_DLP_URL, tools / "yt-dlp.exe", ctx,
                                   "yt-dlp downloaden", 0, 25)
                except Exception as e:
                    self.finished_install.emit(False, f"yt-dlp download mislukt: {e}")
                    return

            if self._cancelled:
                self.finished_install.emit(False, "Geannuleerd door gebruiker")
                return

            # ---- ffmpeg ----
            if get_ffmpeg_dir():
                self.progress.emit("ffmpeg is al beschikbaar op uw systeem", 90)
            else:
                self.progress.emit(
                    "ffmpeg downloaden (groot bestand, ongeveer 80 MB)...", 25)
                zip_path = tools / "ffmpeg-temp.zip"
                try:
                    self._download(FFMPEG_URL, zip_path, ctx,
                                   "ffmpeg downloaden", 25, 85)
                except Exception as e:
                    self.finished_install.emit(False, f"ffmpeg download mislukt: {e}")
                    return

                if self._cancelled:
                    self.finished_install.emit(False, "Geannuleerd door gebruiker")
                    try:
                        zip_path.unlink()
                    except Exception:
                        pass
                    return

                # Extract alleen ffmpeg.exe en ffprobe.exe
                self.progress.emit("ffmpeg uitpakken...", 90)
                try:
                    self._extract_ffmpeg(zip_path, tools)
                except Exception as e:
                    self.finished_install.emit(False, f"ffmpeg uitpakken mislukt: {e}")
                    return
                finally:
                    try:
                        zip_path.unlink()
                    except Exception:
                        pass

            self.progress.emit("Installatie voltooid!", 100)
            self.finished_install.emit(True, "")
        except Exception as e:
            self.finished_install.emit(False, f"Onverwachte fout: {e}")

    def _download(self, url: str, dest: Path, ctx, label: str,
                  pct_start: int, pct_end: int):
        """Download een URL naar dest met voortgang-rapportage."""
        with urllib.request.urlopen(url, context=ctx, timeout=30) as resp:
            total = int(resp.headers.get("Content-Length", 0)) or 1
            downloaded = 0
            chunk_size = 64 * 1024
            with open(dest, "wb") as f:
                while True:
                    if self._cancelled:
                        return
                    chunk = resp.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    pct = pct_start + int((downloaded / total) * (pct_end - pct_start))
                    mb_done = downloaded / (1024 * 1024)
                    mb_total = total / (1024 * 1024)
                    self.progress.emit(
                        f"{label}: {mb_done:.1f} MB van {mb_total:.1f} MB",
                        min(pct, pct_end)
                    )

    def _extract_ffmpeg(self, zip_path: Path, dest_dir: Path):
        """
        Pak ALLEEN ffmpeg.exe en ffprobe.exe uit de ZIP naar dest_dir.
        Negeer de map-structuur in de zip (alles plat).
        """
        with zipfile.ZipFile(zip_path, "r") as zf:
            for name in zf.namelist():
                base = os.path.basename(name).lower()
                if base in ("ffmpeg.exe", "ffprobe.exe"):
                    target = dest_dir / os.path.basename(name)
                    with zf.open(name) as src, open(target, "wb") as out:
                        shutil.copyfileobj(src, out)


# ========================================================================
# VIDEO DOWNLOADER (yt-dlp worker voor video/audio)  (was: core/video_downloader.py)
# ========================================================================

def get_downloads_dir() -> Path:
    """Geef de map waar downloads worden opgeslagen (en maak hem aan)."""
    try:
        if getattr(sys, "frozen", False):
            app_dir = Path(sys.executable).resolve().parent
        else:
            app_dir = Path(sys.argv[0]).resolve().parent
        d = app_dir / "downloads"
        d.mkdir(parents=True, exist_ok=True)
        return d
    except Exception:
        pass
    fallback = Path.home() / "Downloads" / "DeskButler"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


def safe_filename(name: str, max_len: int = 80) -> str:
    """
    Maak een veilige bestandsnaam: vervang Windows-verboden tekens,
    knip op max_len, val terug op timestamp als naam leeg is.
    """
    clean = re.sub(r'[\\/*?:"<>|]', "_", (name or "").strip())
    clean = clean[:max_len].strip()
    return clean or f"download_{int(time.time())}"


def get_video_title(url: str) -> str:
    """
    Probeer de titel van de video op te halen via yt-dlp (--get-title).
    Snel en lichtgewicht. Val terug op timestamp bij fout.
    """
    yt = get_yt_dlp_path()
    if not yt:
        return f"download_{int(time.time())}"
    try:
        flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        res = subprocess.run(
            [str(yt), "--get-title", "--no-playlist", url],
            capture_output=True, text=True, timeout=10,
            creationflags=flags,
        )
        if res.returncode == 0:
            return safe_filename(res.stdout)
    except Exception as e:
        print(f"[video_dl] get_title faalde: {e}")
    return f"download_{int(time.time())}"


class VideoDownloadWorker(QThread):
    """
    QThread die een download uitvoert via yt-dlp.

    mode: 'mp4' of 'mp3'
    """
    status_update = Signal(str)              # tekstuele status voor UI
    progress_percent = Signal(int)           # 0-100 voor voortgangsbalk
    finished_dl = Signal(bool, str)          # success, error-message

    def __init__(self, url: str, output_path: str, mode: str = "mp4",
                 parent=None):
        super().__init__(parent)
        self.url = url
        self.output_path = output_path
        self.mode = mode  # 'mp4' of 'mp3'
        self.proc = None
        self._cancelled = False

    def cancel(self):
        """Stop de download netjes en ruim onvolledig bestand op."""
        self._cancelled = True
        if self.proc:
            try:
                if sys.platform == "win32":
                    subprocess.call(
                        ["taskkill", "/F", "/T", "/PID", str(self.proc.pid)],
                        creationflags=subprocess.CREATE_NO_WINDOW,
                    )
                else:
                    self.proc.terminate()
            except Exception as e:
                print(f"[video_dl] cancel faalde: {e}")
        time.sleep(0.4)
        # Verwijder onvolledig bestand
        try:
            if os.path.exists(self.output_path):
                os.remove(self.output_path)
        except Exception:
            pass

    def run(self):
        yt_path = get_yt_dlp_path()
        ffmpeg_dir = get_ffmpeg_dir()
        if not yt_path or not ffmpeg_dir:
            self.finished_dl.emit(
                False, "yt-dlp of ffmpeg ontbreekt. Installeer ze via Settings."
            )
            return

        try:
            base = os.path.splitext(self.output_path)[0]
            base_name = os.path.basename(base)
            search_dir = os.path.dirname(base) or "."

            if self.mode == "mp3":
                output_path = base + ".mp3"
                output_template = base + ".%(ext)s"
                cmd = [
                    str(yt_path),
                    "--ffmpeg-location", str(ffmpeg_dir),
                    "--no-playlist", "--newline", "--progress", "--no-cache-dir",
                    "-f", "bestaudio/best",
                    "-x", "--audio-format", "mp3", "--audio-quality", "0",
                    "-o", output_template,
                    self.url,
                ]
            else:
                output_path = base + ".mp4"
                cmd = [
                    str(yt_path),
                    "--ffmpeg-location", str(ffmpeg_dir),
                    "--no-playlist", "--newline", "--progress", "--no-cache-dir",
                    "-f", "bestvideo+bestaudio/best",
                    "--merge-output-format", "mp4",
                    "-o", output_path,
                    self.url,
                ]

            log_path = os.path.join(search_dir, "deskbutler_dl.log")
            log_lines = []
            print(f"[video_dl] start: {self.mode} → {output_path}")

            flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            self.proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, creationflags=flags,
            )

            for line in self.proc.stdout:
                if self._cancelled:
                    break
                line = line.strip()
                if not line:
                    continue
                log_lines.append(line)

                # Detectie van conversie-fase
                if any(x in line for x in (
                    "[ExtractAudio]", "[ffmpeg]", "[VideoConvertor]",
                    "Merging", "Deleting", "post-process", "Destination",
                )):
                    self.status_update.emit("⚙️ Converteren naar definitief formaat...")
                    self.progress_percent.emit(95)
                    continue

                if "[download] 100%" in line:
                    self.status_update.emit("✅ Download klaar, even afronden...")
                    self.progress_percent.emit(95)
                    continue

                # Voortgang-parsing
                m = re.search(
                    r"\[download\].*?(\d+\.?\d*)%(?:.*?of\s+([\d.]+\w+))?",
                    line,
                )
                if m:
                    try:
                        pct = float(m.group(1))
                    except ValueError:
                        pct = 0.0
                    of = f" van {m.group(2)}" if m.group(2) else ""
                    self.status_update.emit(f"⬇️ Downloaden... {pct:.0f}%{of}")
                    # We mappen de yt-dlp 0-100% naar 5-90% (laat ruimte voor merge)
                    self.progress_percent.emit(5 + int(pct * 0.85))

            self.proc.communicate()

            # Log naar bestand voor diagnose
            try:
                with open(log_path, "w", encoding="utf-8") as lf:
                    lf.write(" ".join(cmd) + "\n\n")
                    lf.write("\n".join(log_lines))
            except Exception:
                pass

            if self._cancelled:
                return  # cancel() heeft al opgeruimd

            # Ruim achterblijvende tussen-bestanden op (yt-dlp merge laat soms
            # .webm/.m4a/.part files staan als die niet automatisch worden gewist)
            junk_extensions = (".webm", ".m4a", ".opus", ".part", ".ytdl", ".tmp")
            for f in os.listdir(search_dir):
                fp = os.path.join(search_dir, f)
                if os.path.abspath(fp) == os.path.abspath(output_path):
                    continue
                if f.startswith(base_name) and f.endswith(junk_extensions):
                    try:
                        os.remove(fp)
                        print(f"[video_dl] tussenbestand gewist: {f}")
                    except Exception:
                        pass

            success = (
                os.path.exists(output_path)
                and os.path.getsize(output_path) > 0
            )
            self.progress_percent.emit(100)
            if success:
                self.finished_dl.emit(True, output_path)
            else:
                self.finished_dl.emit(
                    False,
                    "Het bestand kon niet worden gemaakt. "
                    f"Zie {log_path} voor details."
                )
        except Exception as e:
            print(f"[video_dl] onverwachte fout: {e}")
            if not self._cancelled:
                self.finished_dl.emit(False, f"Fout: {e}")


# ========================================================================
# OLLAMA CLIENT (lokale AI met auto-start/preload)  (was: core/ollama_client.py)
# ========================================================================

DEFAULT_URL = "http://localhost:11434"
SYSTEM_PROMPT = (
    "Je bent een beleefde, kundige persoonlijke assistent. "
    "Antwoord altijd in dezelfde taal als de vraag (meestal Nederlands). "
    "Wees beknopt en duidelijk: maximaal 3-4 zinnen, geschikt om hardop "
    "voorgelezen te worden. Geen markdown, geen lijstjes — gewoon vloeiende "
    "tekst die natuurlijk klinkt. Als je iets niet zeker weet, zeg dat eerlijk."
)

# Houd bij of WIJ Ollama gestart hebben (dan mogen we hem afsluiten)
_started_by_us = False
_ollama_process = None


def _base_url() -> str:
    return str(config.get("ollama_url", DEFAULT_URL)).rstrip("/")


def ollama_is_available(timeout: float = 2.0) -> bool:
    """Snelle check of de Ollama-server bereikbaar is."""
    try:
        r = requests.get(f"{_base_url()}/api/tags", timeout=timeout)
        return r.status_code == 200
    except requests.RequestException:
        return False


def ollama_is_available_with_retries(total_seconds: float = 10.0) -> bool:
    """
    Doe meerdere checks gedurende `total_seconds` seconden. Handig bij
    opstart wanneer Ollama nog moet warmlopen. Returnt zodra hij wel
    beschikbaar is, of False na het tijdsbestek.
    """
    # 5 checks verdeeld over de tijd: 0, 2, 4, 6, 8 seconden (bij 10s totaal)
    check_interval = max(1.0, total_seconds / 5)
    elapsed = 0.0
    while elapsed < total_seconds:
        if ollama_is_available(timeout=2.0):
            return True
        time.sleep(check_interval)
        elapsed += check_interval + 2.0  # 2s timeout + interval
    return False


def _ollama_process_running_on_system() -> bool:
    """
    Check of er al een Ollama proces draait via Windows tasklist.
    Belangrijk: er zijn TWEE proces-namen:
      - 'ollama.exe'      = de eigenlijke server (door `ollama serve`)
      - 'ollama app.exe'  = de tray-app die Ollama bij Windows-start opent
    Beide moeten gedetecteerd worden om dubbel-starten te voorkomen.
    """
    if os.name != "nt":
        return False
    # Eerst: directe socket-check op poort 11434 — meest betrouwbaar
    import socket
    try:
        s = socket.create_connection(("127.0.0.1", 11434), timeout=1.5)
        s.close()
        print("[ollama] poort 11434 is bezet → server draait al ergens")
        return True
    except Exception:
        pass

    # Daarna: tasklist check op beide namen
    for proc_name in ["ollama.exe", "ollama app.exe"]:
        try:
            result = subprocess.run(
                ["tasklist", "/FI", f"IMAGENAME eq {proc_name}", "/NH", "/FO", "CSV"],
                capture_output=True, text=True, timeout=3,
                creationflags=0x08000000,
            )
            stdout = (result.stdout or "").lower()
            if proc_name.lower() in stdout:
                print(f"[ollama] gevonden in proceslijst: {proc_name}")
                return True
        except Exception as e:
            print(f"[ollama] tasklist {proc_name} faalde: {e}")
    return False


def ollama_list_models() -> list:
    """Geef een lijst van geïnstalleerde modellen."""
    try:
        r = requests.get(f"{_base_url()}/api/tags", timeout=3)
        if r.status_code != 200:
            return []
        data = r.json()
        return [m.get("name", "") for m in data.get("models", []) if m.get("name")]
    except (requests.RequestException, ValueError):
        return []


def is_ollama_installed() -> bool:
    """Check of het 'ollama' commando bestaat op het systeem (Windows: PATH)."""
    import shutil
    return shutil.which("ollama") is not None


def ollama_try_start() -> bool:
    """
    Start de Ollama-server als die wel geïnstalleerd is maar niet draait.
    Returnt True als hij na de poging beschikbaar is.

    BELANGRIJK: checkt eerst of er al een ollama.exe draait in Windows —
    zo voorkomen we dat we een tweede starten dat alleen maar zombie wordt
    (de poort is al bezet door de eerste).
    """
    global _started_by_us, _ollama_process

    # Stap 1: misschien draait hij al en is alleen de eerste check te streng
    if ollama_is_available_with_retries(total_seconds=8.0):
        print("[ollama] al beschikbaar (geen start nodig)")
        return True

    # Stap 2: er draait al een ollama.exe proces maar API antwoordt niet —
    # niet een tweede starten! Wacht nog wat langer.
    if _ollama_process_running_on_system():
        print("[ollama] proces draait al in Windows, wacht extra...")
        if ollama_is_available_with_retries(total_seconds=15.0):
            print("[ollama] na extra wachttijd toch beschikbaar")
            return True
        print("[ollama] proces draait maar API antwoordt niet — niet nog een starten")
        return False

    if not is_ollama_installed():
        return False

    print("[ollama] niet bereikbaar - probeer auto-start")
    try:
        # Start zonder console venster op Windows (CREATE_NO_WINDOW = 0x08000000)
        kwargs = {}
        if os.name == "nt":
            kwargs["creationflags"] = 0x08000000
        _ollama_process = subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            **kwargs,
        )
        _started_by_us = True
        print("[ollama] server proces gestart (PID:", _ollama_process.pid, ")")
    except Exception as e:
        print(f"[ollama] auto-start faalde: {e}")
        return False

    # Wacht tot de server bereikbaar is (max 12 seconden — koude start kan duren)
    for _ in range(60):
        time.sleep(0.2)
        if ollama_is_available(timeout=1.5):
            print("[ollama] server is nu bereikbaar")
            return True
    print("[ollama] server start lukt niet binnen 12s")
    return False


def ollama_shutdown_if_we_started():
    """Stop de Ollama-server alleen als WIJ hem gestart hebben."""
    global _started_by_us, _ollama_process
    if not _started_by_us or _ollama_process is None:
        return
    try:
        print("[ollama] netjes afsluiten (we startten hem zelf)")
        _ollama_process.terminate()
        try:
            _ollama_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            print("[ollama] terminate werkte niet, kill...")
            _ollama_process.kill()
            try:
                _ollama_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                pass
    except Exception as e:
        print(f"[ollama] shutdown fout: {e}")
    finally:
        _started_by_us = False
        _ollama_process = None
    # Als ollama.exe nog draait (kan, want 'ollama serve' is een wrapper):
    # probeer ze allemaal te killen via Windows taskkill.
    _force_kill_ollama_processes()


def ollama_force_shutdown() -> tuple[bool, str]:
    """
    Stop ALLE Ollama processen, ongeacht wie ze startte.
    Voor gebruikers-knop in Settings. Returnt (success, message).
    """
    global _started_by_us, _ollama_process

    # Eerst onze eigen subprocess (als we die hebben)
    if _ollama_process is not None:
        try:
            _ollama_process.terminate()
            try:
                _ollama_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                _ollama_process.kill()
        except Exception as e:
            print(f"[ollama] eigen proces stoppen faalde: {e}")
        finally:
            _started_by_us = False
            _ollama_process = None

    # Dan alle andere ollama-processen via systeem
    killed_count = _force_kill_ollama_processes()

    # Verifieer
    import time
    time.sleep(0.5)
    still_up = ollama_is_available()

    if still_up:
        return (False, "Ollama draait nog steeds — mogelijk geen rechten om af te sluiten.")
    elif killed_count > 0:
        return (True, f"Ollama is afgesloten ({killed_count} proces(sen) gestopt).")
    else:
        return (True, "Ollama is gestopt.")


def _force_kill_ollama_processes() -> int:
    """
    Kill alle ollama.exe processen op Windows via taskkill.
    Returnt aantal gestopte processen (best-effort).
    """
    if os.name != "nt":
        return 0
    killed = 0
    for proc_name in ["ollama.exe", "ollama app.exe"]:
        try:
            # /F = force, /IM = image name, /T = ook child processes
            result = subprocess.run(
                ["taskkill", "/F", "/IM", proc_name, "/T"],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=0x08000000,  # CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                # Output zegt hoeveel processen zijn gestopt
                output = result.stdout or ""
                # Tel "SUCCESS" lijntjes
                killed += output.count("SUCCESS:")
                if killed == 0 and "succes" in output.lower():
                    killed += 1
        except Exception as e:
            print(f"[ollama] taskkill {proc_name} faalde: {e}")
    return killed


def ollama_preload(model: str = None, on_status=None) -> bool:
    """
    Laad een model alvast in het geheugen door er een mini-vraag aan te stellen.
    De eerste echte vraag is dan veel sneller (model is al warm).
    on_status is optioneel callback(message) voor voortgang.
    """
    use_model = model or config.get("ollama_model", "")
    if not use_model:
        models = ollama_list_models()
        if not models:
            return False
        use_model = models[0]

    def emit(msg):
        if on_status:
            try:
                on_status(msg)
            except Exception:
                pass
        print(f"[ollama preload] {msg}")

    emit(f"Model '{use_model}' wordt voorbereid...")
    try:
        # Lege prompt = alleen model laden, geen generatie
        r = requests.post(
            f"{_base_url()}/api/generate",
            json={"model": use_model, "prompt": "", "keep_alive": "30m"},
            timeout=120,
        )
        if r.status_code == 200:
            emit(f"Model '{use_model}' is geladen en klaar.")
            return True
        emit(f"Preload faalde: HTTP {r.status_code}")
    except requests.Timeout:
        emit("Preload duurt te lang — model zal later geladen worden.")
    except requests.RequestException as e:
        emit(f"Preload fout: {e}")
    return False


def ollama_preload_async(model: str = None, on_status=None, on_done=None):
    """Preload in een achtergrond-thread (UI bevriest niet)."""
    def runner():
        ok = ollama_preload(model=model, on_status=on_status)
        if on_done:
            try:
                on_done(ok)
            except Exception:
                pass
    t = threading.Thread(target=runner, daemon=True)
    t.start()
    return t


def ollama_chat(prompt: str, model: str = None, timeout: int = 90) -> str | None:
    """Stuur een vraag naar Ollama en geef het antwoord terug."""
    if not prompt or not prompt.strip():
        return None
    use_model = model or config.get("ollama_model", "")
    if not use_model:
        avail = ollama_list_models()
        if not avail:
            return None
        use_model = avail[0]

    try:
        r = requests.post(
            f"{_base_url()}/api/chat",
            json={
                "model": use_model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "stream": False,
                "options": {"temperature": 0.4, "num_predict": 250},
                "keep_alive": "30m",  # houd het model 30 min warm
            },
            timeout=timeout,
        )
        if r.status_code != 200:
            print(f"[ollama] HTTP {r.status_code}: {r.text[:200]}")
            return None
        data = r.json()
        msg = data.get("message", {}).get("content", "")
        return msg.strip() or None
    except requests.Timeout:
        print(f"[ollama] timeout na {timeout}s (model {use_model})")
        return None
    except (requests.RequestException, ValueError) as e:
        print(f"[ollama] fout: {e}")
        return None


def ollama_diagnostics() -> dict:
    info = {
        "url": _base_url(),
        "available": ollama_is_available(),
        "models": [],
        "selected_model": str(config.get("ollama_model", "")),
        "enabled": bool(config.get("use_ollama", False)),
        "installed": is_ollama_installed(),
        "started_by_us": _started_by_us,
    }
    if info["available"]:
        info["models"] = ollama_list_models()
    return info


# ========================================================================
# MAIL: IMAP  (was: mail/imap_client.py)
# ========================================================================

@dataclass
class EmailMessage:
    uid: str
    folder: str
    from_addr: str
    to_addr: str
    subject: str
    date: str
    body_text: str = ""
    body_html: str = ""
    is_read: bool = False
    has_attachments: bool = False
    attachments: list = field(default_factory=list)


def _decode(value: str | bytes) -> str:
    """Decodeer een mail-header (gecodeerde UTF-8 / quoted-printable)."""
    if value is None:
        return ""
    if isinstance(value, bytes):
        try:
            return value.decode("utf-8", errors="replace")
        except Exception:
            return str(value)
    parts = decode_header(value)
    out = []
    for text, charset in parts:
        if isinstance(text, bytes):
            try:
                out.append(text.decode(charset or "utf-8", errors="replace"))
            except Exception:
                out.append(text.decode("utf-8", errors="replace"))
        else:
            out.append(text)
    return "".join(out)


class IMAPClient:
    """Wrapper rond imaplib.IMAP4_SSL met een eenvoudige API."""

    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self._conn: imaplib.IMAP4_SSL | None = None

    # ------------------------------------------------------------------
    def connect(self):
        # Belangrijk: timeout zodat de hele app niet vastloopt als de
        # mailserver niet antwoordt. 15 seconden is voor IMAP-login ruim.
        import socket
        old_timeout = socket.getdefaulttimeout()
        try:
            socket.setdefaulttimeout(15)
            self._conn = imaplib.IMAP4_SSL(self.host, self.port)
            self._conn.login(self.username, self.password)
        finally:
            socket.setdefaulttimeout(old_timeout)

    def disconnect(self):
        if self._conn is not None:
            try:
                self._conn.logout()
            except Exception:
                pass
            self._conn = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.disconnect()

    # ------------------------------------------------------------------
    def list_folders(self) -> List[str]:
        if not self._conn:
            return []
        typ, data = self._conn.list()
        if typ != "OK":
            return []
        folders = []
        for line in data:
            if not line:
                continue
            line_str = line.decode(errors="replace") if isinstance(line, bytes) else line
            # Format: (flags) "delimiter" "naam"
            parts = line_str.rsplit(" ", 1)
            if len(parts) == 2:
                name = parts[1].strip().strip('"')
                folders.append(name)
        return folders

    def fetch_recent(self, folder: str = "INBOX", limit: int = 30) -> List[EmailMessage]:
        if not self._conn:
            return []
        try:
            typ, _ = self._conn.select(folder)
            if typ != "OK":
                return []
        except imaplib.IMAP4.error:
            return []

        typ, data = self._conn.uid("search", None, "ALL")
        if typ != "OK":
            return []
        uids = data[0].split()
        # Pak de laatste `limit` items (nieuwste laatst)
        uids = uids[-limit:]
        messages = []
        for uid in reversed(uids):  # nieuwste eerst
            msg = self._fetch_message(folder, uid.decode())
            if msg:
                messages.append(msg)
        return messages

    def _fetch_message(self, folder: str, uid: str) -> EmailMessage | None:
        typ, data = self._conn.uid("fetch", uid, "(RFC822 FLAGS)")
        if typ != "OK" or not data:
            return None
        # Parse de raw email
        raw = None
        flags = b""
        for part in data:
            if isinstance(part, tuple) and len(part) >= 2:
                raw = part[1]
            elif isinstance(part, bytes):
                flags += part

        if not raw:
            return None
        msg = email.message_from_bytes(raw, policy=policy.default)

        text, html, attachments = "", "", []
        for part in msg.walk():
            ctype = part.get_content_type()
            disp = (part.get("Content-Disposition") or "").lower()
            if "attachment" in disp:
                fname = part.get_filename()
                if fname:
                    attachments.append(fname)
                continue
            if ctype == "text/plain" and not text:
                try:
                    text = part.get_content()
                except Exception:
                    text = ""
            elif ctype == "text/html" and not html:
                try:
                    html = part.get_content()
                except Exception:
                    html = ""

        is_read = b"\\Seen" in flags

        return EmailMessage(
            uid=uid,
            folder=folder,
            from_addr=_decode(msg.get("From", "")),
            to_addr=_decode(msg.get("To", "")),
            subject=_decode(msg.get("Subject", "")),
            date=msg.get("Date", ""),
            body_text=text,
            body_html=html,
            is_read=is_read,
            has_attachments=bool(attachments),
            attachments=attachments,
        )

    def mark_read(self, folder: str, uid: str, read: bool = True):
        if not self._conn:
            return
        self._conn.select(folder)
        flag = "+FLAGS" if read else "-FLAGS"
        self._conn.uid("store", uid, flag, "\\Seen")

    def fetch_unread_uids(self, folder: str = "INBOX") -> list:
        """Geef de UIDs van ongelezen berichten in deze folder."""
        if not self._conn:
            return []
        try:
            typ, _ = self._conn.select(folder)
            if typ != "OK":
                return []
        except imaplib.IMAP4.error:
            return []
        typ, data = self._conn.uid("search", None, "UNSEEN")
        if typ != "OK" or not data or not data[0]:
            return []
        return [uid.decode() for uid in data[0].split()]

    def fetch_attachment(self, folder: str, uid: str, filename: str):
        """Download een specifieke bijlage uit een bericht. Returns bytes of None."""
        if not self._conn:
            return None
        try:
            typ, _ = self._conn.select(folder)
            if typ != "OK":
                return None
        except imaplib.IMAP4.error:
            return None
        typ, data = self._conn.uid("fetch", uid, "(RFC822)")
        if typ != "OK" or not data or not data[0]:
            return None
        raw = data[0][1] if isinstance(data[0], tuple) else None
        if not raw:
            return None
        msg = email.message_from_bytes(raw, policy=policy.default)
        for part in msg.walk():
            disp = (part.get("Content-Disposition") or "").lower()
            if "attachment" not in disp:
                continue
            fname = part.get_filename() or ""
            # Decode RFC2047 (=?utf-8?...?=)
            try:
                from email.header import decode_header
                decoded = decode_header(fname)
                fname = "".join(
                    (p.decode(enc or "utf-8", errors="replace") if isinstance(p, bytes) else p)
                    for p, enc in decoded
                )
            except Exception:
                pass
            if fname == filename:
                try:
                    return part.get_content() if hasattr(part, "get_content") \
                        else part.get_payload(decode=True)
                except Exception:
                    return part.get_payload(decode=True)
        return None

    def delete(self, folder: str, uid: str):
        if not self._conn:
            return
        self._conn.select(folder)
        self._conn.uid("store", uid, "+FLAGS", "\\Deleted")
        self._conn.expunge()


# ========================================================================
# MAIL: SMTP  (was: mail/smtp_client.py)
# ========================================================================

class SMTPClient:
    def __init__(self, host: str, port: int, username: str, password: str,
                 use_starttls: bool = False):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_starttls = use_starttls

    def send(self, from_addr: str, to_addrs: list, subject: str, body: str,
             html: str = None, attachments: list = None) -> bool:
        msg = _EmailMessage()
        msg["From"] = from_addr
        msg["To"] = ", ".join(to_addrs)
        msg["Subject"] = subject
        msg.set_content(body or "")

        if html:
            msg.add_alternative(html, subtype="html")

        for path in attachments or []:
            p = Path(path)
            if not p.exists():
                continue
            data = p.read_bytes()
            # Simpele detection
            ctype, subtype = "application", "octet-stream"
            if p.suffix.lower() in [".jpg", ".jpeg"]:
                ctype, subtype = "image", "jpeg"
            elif p.suffix.lower() == ".png":
                ctype, subtype = "image", "png"
            elif p.suffix.lower() == ".pdf":
                ctype, subtype = "application", "pdf"
            elif p.suffix.lower() in [".txt", ".log"]:
                ctype, subtype = "text", "plain"
            msg.add_attachment(data, maintype=ctype, subtype=subtype, filename=p.name)

        context = ssl.create_default_context()
        try:
            if self.use_starttls:
                with smtplib.SMTP(self.host, self.port, timeout=30) as s:
                    s.starttls(context=context)
                    s.login(self.username, self.password)
                    s.send_message(msg)
            else:
                with smtplib.SMTP_SSL(self.host, self.port, context=context, timeout=30) as s:
                    s.login(self.username, self.password)
                    s.send_message(msg)
            return True
        except Exception as e:
            print(f"[smtp] verzenden faalde: {e}")
            return False


# ========================================================================
# MAIL: POP3  (was: mail/pop3_client.py)
# ========================================================================

class POP3Client:
    def __init__(self, host: str, port: int, username: str, password: str,
                 use_ssl: bool = True):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self._conn = None

    def connect(self):
        if self.use_ssl:
            self._conn = poplib.POP3_SSL(self.host, self.port, timeout=30)
        else:
            self._conn = poplib.POP3(self.host, self.port, timeout=30)
        self._conn.user(self.username)
        self._conn.pass_(self.password)

    def disconnect(self):
        if self._conn:
            try:
                self._conn.quit()
            except Exception:
                pass
            self._conn = None

    def fetch_recent(self, limit: int = 30):
        if not self._conn:
            return []
        try:
            count = len(self._conn.list()[1])
        except Exception:
            return []
        first = max(1, count - limit + 1)
        messages = []
        for i in range(count, first - 1, -1):
            try:
                resp, lines, octets = self._conn.retr(i)
            except poplib.error_proto:
                continue
            raw = b"\n".join(lines)
            msg = email.message_from_bytes(raw, policy=policy.default)

            text, html = "", ""
            for part in msg.walk():
                ctype = part.get_content_type()
                disp = (part.get("Content-Disposition") or "").lower()
                if "attachment" in disp:
                    continue
                if ctype == "text/plain" and not text:
                    try: text = part.get_content()
                    except Exception: pass
                elif ctype == "text/html" and not html:
                    try: html = part.get_content()
                    except Exception: pass

            messages.append(EmailMessage(
                uid=str(i),
                folder="POP3",
                from_addr=_decode(msg.get("From", "")),
                to_addr=_decode(msg.get("To", "")),
                subject=_decode(msg.get("Subject", "")),
                date=msg.get("Date", ""),
                body_text=text,
                body_html=html,
                is_read=True,  # POP3 heeft geen flags
            ))
        return messages

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.disconnect()


# ========================================================================
# MAIL: OAuth Gmail  (was: mail/oauth_gmail.py)
# ========================================================================

_GMAIL_SCOPES = [
    "https://mail.google.com/",
]
_GMAIL_TOKEN_FILE = get_config_dir() / "gmail_token.json"
_GMAIL_SECRET_FILE = get_config_dir() / "oauth_gmail.json"


def _gmail_get_access_token() -> str | None:
    """Haal of vernieuw het Gmail OAuth-token."""
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
    except ImportError:
        print("[oauth_gmail] google-auth libraries niet geïnstalleerd")
        return None

    creds = None
    if _GMAIL_TOKEN_FILE.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(_GMAIL_TOKEN_FILE), _GMAIL_SCOPES)
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"[oauth_gmail] refresh faalde: {e}")
                creds = None
        if not creds:
            if not _GMAIL_SECRET_FILE.exists():
                print(f"[oauth_gmail] Geen client secret op: {_GMAIL_SECRET_FILE}")
                print("Maak een OAuth-client op https://console.cloud.google.com en sla het bestand op.")
                return None
            try:
                flow = InstalledAppFlow.from_client_secrets_file(str(_GMAIL_SECRET_FILE), _GMAIL_SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                print(f"[oauth_gmail] flow faalde: {e}")
                return None
        # Opslaan
        try:
            with open(_GMAIL_TOKEN_FILE, "w") as f:
                f.write(creds.to_json())
        except OSError:
            pass

    return creds.token if creds else None


def _gmail_build_xoauth2(username: str, access_token: str) -> str:
    """Bouw de XOAUTH2 string voor IMAP/SMTP authenticatie."""
    import base64
    auth_string = f"user={username}\x01auth=Bearer {access_token}\x01\x01"
    return base64.b64encode(auth_string.encode()).decode()


# ========================================================================
# MAIL: OAuth Outlook  (was: mail/oauth_outlook.py)
# ========================================================================

_OUTLOOK_SCOPES = [
    "https://outlook.office.com/IMAP.AccessAsUser.All",
    "https://outlook.office.com/SMTP.Send",
    "offline_access",
]
_OUTLOOK_CONFIG_FILE = get_config_dir() / "oauth_outlook.json"
_OUTLOOK_CACHE_FILE = get_config_dir() / "outlook_token_cache.bin"


def _outlook_get_access_token(username: str) -> str | None:
    try:
        import msal
    except ImportError:
        print("[oauth_outlook] msal library niet geïnstalleerd")
        return None

    if not _OUTLOOK_CONFIG_FILE.exists():
        print(f"[oauth_outlook] Geen config op {_OUTLOOK_CONFIG_FILE}")
        print("Maak een app-registratie aan: https://portal.azure.com -> App Registrations")
        return None

    try:
        cfg = json.loads(_OUTLOOK_CONFIG_FILE.read_text())
        client_id = cfg["client_id"]
        tenant = cfg.get("tenant_id", "consumers")
    except (KeyError, json.JSONDecodeError):
        print("[oauth_outlook] Config-bestand ongeldig.")
        return None

    cache = msal.SerializableTokenCache()
    if _OUTLOOK_CACHE_FILE.exists():
        try:
            cache.deserialize(_OUTLOOK_CACHE_FILE.read_text())
        except Exception:
            pass

    app = msal.PublicClientApplication(
        client_id,
        authority=f"https://login.microsoftonline.com/{tenant}",
        token_cache=cache,
    )

    accounts = app.get_accounts(username=username)
    result = None
    if accounts:
        result = app.acquire_token_silent(_OUTLOOK_SCOPES, account=accounts[0])

    if not result:
        # Interactieve flow (opent browser)
        try:
            result = app.acquire_token_interactive(_OUTLOOK_SCOPES, login_hint=username)
        except Exception as e:
            print(f"[oauth_outlook] interactieve flow faalde: {e}")
            return None

    if cache.has_state_changed:
        try:
            _OUTLOOK_CACHE_FILE.write_text(cache.serialize())
        except OSError:
            pass

    if result and "access_token" in result:
        return result["access_token"]
    return None


def _outlook_build_xoauth2(username: str, access_token: str) -> str:
    """Bouw XOAUTH2 string (zelfde formaat als Gmail)."""
    import base64
    auth_string = f"user={username}\x01auth=Bearer {access_token}\x01\x01"
    return base64.b64encode(auth_string.encode()).decode()


# ========================================================================
# MAIL: accounts storage  (was: mail/accounts.py)
# ========================================================================

KEY_FILE = get_config_dir() / ".key"
ACCOUNTS_FILE = get_config_dir() / "accounts.enc"


def _get_or_create_key() -> bytes:
    """Maak een Fernet-sleutel of laad de bestaande."""
    from cryptography.fernet import Fernet
    if KEY_FILE.exists():
        return KEY_FILE.read_bytes()
    key = Fernet.generate_key()
    KEY_FILE.write_bytes(key)
    try:
        os.chmod(KEY_FILE, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass
    return key


def load_accounts() -> list:
    """Geef de lijst geconfigureerde accounts terug (ontsleuteld)."""
    if not ACCOUNTS_FILE.exists():
        return []
    try:
        from cryptography.fernet import Fernet
        key = _get_or_create_key()
        f = Fernet(key)
        decrypted = f.decrypt(ACCOUNTS_FILE.read_bytes())
        return json.loads(decrypted)
    except Exception as e:
        print(f"[accounts] laden faalde: {e}")
        return []


def save_accounts(accounts: list):
    """Sla de lijst accounts versleuteld op."""
    try:
        from cryptography.fernet import Fernet
        key = _get_or_create_key()
        f = Fernet(key)
        data = json.dumps(accounts).encode()
        encrypted = f.encrypt(data)
        ACCOUNTS_FILE.write_bytes(encrypted)
    except Exception as e:
        print(f"[accounts] opslaan faalde: {e}")


def add_account(account: dict):
    """Voeg een account toe."""
    accounts = load_accounts()
    accounts.append(account)
    save_accounts(accounts)


def remove_account(index: int):
    accounts = load_accounts()
    if 0 <= index < len(accounts):
        del accounts[index]
        save_accounts(accounts)


def update_account(index: int, account: dict):
    """Vervang het account op index met de nieuwe gegevens."""
    accounts = load_accounts()
    if 0 <= index < len(accounts):
        accounts[index] = account
        save_accounts(accounts)
        return True
    return False


# Voorbeeld account-dict:
# {
#   "name": "Mijn Gmail",
#   "protocol": "imap",      # imap, pop3
#   "auth": "password",      # password, oauth_gmail, oauth_outlook
#   "email": "naam@gmail.com",
#   "password": "<plaintext, alleen bij protocol=password>",
#   "imap_host": "imap.gmail.com",
#   "imap_port": 993,
#   "smtp_host": "smtp.gmail.com",
#   "smtp_port": 465,
#   "smtp_starttls": false,
# }


# ========================================================================
# MAIL CHECKER (auto)  (was: core/mail_checker.py)
# ========================================================================

class MailChecker(QObject):
    """Houdt op de achtergrond ongelezen-mail in de gaten."""

    new_mail = Signal(str, int, bool)
    check_error = Signal(str, str)
    check_status = Signal(str)

    def __init__(self):
        super().__init__()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._last_uids: dict = {}
        self._is_checking = False

    # ------------------------------------------------------------------
    def start(self):
        """Start de periodieke check (interval uit config)."""
        self._log(f"start() aangeroepen")
        try:
            interval = int(config.get("mail_check_interval_min", 5))
        except Exception as e:
            self._log(f"FOUT bij lezen interval-config: {e}")
            return
        self._log(f"interval geconfigureerd: {interval} minuten")

        if interval <= 0:
            self._log("uitgeschakeld (interval = 0 minuten)")
            return

        try:
            accounts = load_accounts()
        except Exception as e:
            self._log(f"FOUT bij laden accounts: {e}")
            return
        self._log(f"accounts geladen: {len(accounts)} totaal")

        if not accounts:
            self._log("geen mail-accounts geconfigureerd")
            return
        usable = [a for a in accounts
                  if a.get("protocol") == "imap" and a.get("password")]
        self._log(f"bruikbaar (IMAP + wachtwoord): {len(usable)}")
        if not usable:
            self._log(
                f"geen bruikbare IMAP+wachtwoord-accounts gevonden "
                f"(totaal {len(accounts)}; OAuth wordt nog niet ondersteund)"
            )
            # Toch starten — een nieuw account kan later worden toegevoegd

        self._timer.stop()
        self._timer.setInterval(interval * 60 * 1000)
        # Eerste check na 8 sec
        QTimer.singleShot(8000, self._tick)
        self._timer.start()
        self._log(f"actief — eerste check over 8 sec, daarna elke {interval} minuten")

    def stop(self):
        self._timer.stop()

    def reload_interval(self):
        """Aan te roepen na wijziging van het interval in de settings."""
        self.stop()
        self.start()

    def check_now(self):
        """Forceer een onmiddellijke check (bv. vanuit een UI-knop)."""
        self._tick()

    def reset_baseline(self):
        """Vergeet de baseline; volgende check telt alles als initial."""
        self._last_uids.clear()

    # ------------------------------------------------------------------
    def _log(self, msg: str):
        text = f"[mail_check {datetime.now().strftime('%H:%M:%S')}] {msg}"
        print(text)
        try:
            self.check_status.emit(text)
        except Exception:
            pass

    def _tick(self):
        if self._is_checking:
            self._log("overgeslagen — vorige check loopt nog")
            return
        threading.Thread(target=self._check_all_accounts, daemon=True).start()

    def _check_all_accounts(self):
        self._is_checking = True
        try:
            accounts = load_accounts()
            self._log(f"start check, {len(accounts)} account(s) ingesteld")
            for acc in accounts:
                self._check_one(acc)
            self._log("check voltooid")
        except Exception as e:
            self._log(f"onverwachte fout: {e}")
        finally:
            self._is_checking = False

    def _check_one(self, acc: dict):
        name = acc.get("name", acc.get("email", "?"))

        if acc.get("protocol") != "imap":
            self._log(f"  - {name}: overgeslagen (niet IMAP)")
            return
        if not acc.get("password"):
            self._log(f"  - {name}: overgeslagen (geen wachtwoord — OAuth?)")
            return

        try:
            with IMAPClient(acc["imap_host"], acc["imap_port"],
                            acc["email"], acc["password"]) as c:
                unread = set(c.fetch_unread_uids("INBOX"))
        except Exception as e:
            self._log(f"  - {name}: FOUT {e}")
            self.check_error.emit(name, str(e))
            return

        key = acc["email"]
        previous = self._last_uids.get(key)

        if previous is None:
            # Eerste check sinds opstart: meld huidige unread count
            self._last_uids[key] = unread
            self._log(f"  - {name}: {len(unread)} ongelezen (eerste check)")
            if len(unread) > 0:
                self.new_mail.emit(name, len(unread), True)
            return

        new_uids = unread - previous
        if new_uids:
            self._log(f"  - {name}: {len(new_uids)} nieuwe sinds laatste check")
            self.new_mail.emit(name, len(new_uids), False)
        else:
            self._log(f"  - {name}: geen nieuwe ({len(unread)} ongelezen totaal)")

        # Update baseline naar huidige set
        self._last_uids[key] = unread


# ========================================================================
# SEARCH: web  (was: search/web.py)
# ========================================================================

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


# URL-mappings per zoekmachine
ENGINE_HOMEPAGES = {
    "duckduckgo": "https://duckduckgo.com",
    "bing":       "https://www.bing.com",
    "startpage":  "https://www.startpage.com",
    "qwant":      "https://www.qwant.com",
    "brave":      "https://search.brave.com",
    "google":     "https://www.google.com",
}

ENGINE_SEARCH_URLS = {
    "duckduckgo": "https://duckduckgo.com/?q={q}",
    "bing":       "https://www.bing.com/search?q={q}",
    "startpage":  "https://www.startpage.com/do/search?query={q}",
    "qwant":      "https://www.qwant.com/?q={q}",
    "brave":      "https://search.brave.com/search?q={q}",
    "google":     "https://www.google.com/search?q={q}",
}


def get_engine_homepage(engine: str = None) -> str:
    """Geef de homepage-URL voor de huidige (of opgegeven) zoekmachine."""
    eng = engine or str(config.get("default_search_engine", "duckduckgo"))
    return ENGINE_HOMEPAGES.get(eng, ENGINE_HOMEPAGES["duckduckgo"])


def get_engine_search_url(query: str, engine: str = None) -> str:
    """Geef een complete search-URL voor de huidige (of opgegeven) engine."""
    eng = engine or str(config.get("default_search_engine", "duckduckgo"))
    template = ENGINE_SEARCH_URLS.get(eng, ENGINE_SEARCH_URLS["duckduckgo"])
    return template.format(q=quote_plus(query))


# Engine functies — elk geeft (titel, url, snippet) tuples of [] terug
def web_search(query: str, max_results: int = 5):
    """
    Doe een zoekopdracht. Probeert eerst de gekozen engine uit config,
    daarna alle overige als fallback.
    """
    if not query or not query.strip():
        return []

    preferred = config.get("default_search_engine", "duckduckgo")
    ENGINES = {
        "duckduckgo": _ddg_html,
        "duckduckgo_lite": _ddg_lite,
        "bing": _bing,
        "startpage": _startpage,
        "qwant": _qwant,
        "brave": _brave,
        "google": _google,
    }

    # Volgorde: eerst preferred, dan DDG Lite (gratis fallback), dan rest
    order = [preferred]
    for name in ["duckduckgo", "duckduckgo_lite", "bing", "startpage", "qwant", "brave"]:
        if name not in order:
            order.append(name)

    for engine_name in order:
        fn = ENGINES.get(engine_name)
        if not fn:
            continue
        try:
            results = fn(query, max_results)
        except Exception as e:
            print(f"[web] {engine_name} faalde: {e}")
            continue
        if results:
            return results
    return []


# ----------------------------------------------------------------------
# DuckDuckGo HTML
# ----------------------------------------------------------------------
def _ddg_html(query: str, max_results: int):
    url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
        if r.status_code != 200:
            return []
        html = r.text
    except requests.RequestException as e:
        print(f"[web] DuckDuckGo HTML faalde: {e}")
        return []

    link_pattern = re.compile(
        r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
        re.DOTALL,
    )
    snippet_pattern = re.compile(
        r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>',
        re.DOTALL,
    )
    links = link_pattern.findall(html)
    snippets = snippet_pattern.findall(html)

    results = []
    for i, (href, title_html) in enumerate(links):
        if i >= max_results:
            break
        title = _strip_html(title_html)
        snippet = _strip_html(snippets[i]) if i < len(snippets) else ""
        results.append((title, _unwrap_duckduckgo_url(href), snippet))
    return results


# ----------------------------------------------------------------------
# DuckDuckGo Lite
# ----------------------------------------------------------------------
def _ddg_lite(query: str, max_results: int):
    url = f"https://lite.duckduckgo.com/lite/?q={quote_plus(query)}"
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
        if r.status_code != 200:
            return []
        html = r.text
    except requests.RequestException as e:
        print(f"[web] DuckDuckGo Lite faalde: {e}")
        return []

    # Lite-resultaat: per rij een <a rel="nofollow" href="URL">TITLE</a> gevolgd door
    # een snippet td.
    link_pattern = re.compile(
        r'<a[^>]+class="result-link"[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
        re.DOTALL,
    )
    snippet_pattern = re.compile(
        r'<td[^>]+class="result-snippet"[^>]*>(.*?)</td>',
        re.DOTALL,
    )
    # Lite is simpel; oude structuur fallback ook proberen
    if not link_pattern.findall(html):
        link_pattern = re.compile(
            r'<a[^>]+rel="nofollow"[^>]+href="(http[^"]+)"[^>]*>(.*?)</a>',
            re.DOTALL,
        )
    links = link_pattern.findall(html)
    snippets = snippet_pattern.findall(html)

    results = []
    for i, (href, title_html) in enumerate(links):
        if i >= max_results:
            break
        title = _strip_html(title_html)
        snippet = _strip_html(snippets[i]) if i < len(snippets) else ""
        results.append((title, _unwrap_duckduckgo_url(href), snippet))
    return results


# ----------------------------------------------------------------------
# Bing
# ----------------------------------------------------------------------
def _bing(query: str, max_results: int):
    url = f"https://www.bing.com/search?q={quote_plus(query)}"
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
        if r.status_code != 200:
            return []
        html = r.text
    except requests.RequestException as e:
        print(f"[web] Bing faalde: {e}")
        return []

    li_pattern = re.compile(r'<li[^>]+class="b_algo"[^>]*>([\s\S]*?)</li>')
    h2a_pattern = re.compile(r'<h2[^>]*>\s*<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', re.DOTALL)
    snippet_pattern = re.compile(r'<p[^>]*>(.*?)</p>', re.DOTALL)

    results = []
    for item_html in li_pattern.findall(html):
        m = h2a_pattern.search(item_html)
        if not m:
            continue
        url_, title_html = m.group(1), m.group(2)
        title = _strip_html(title_html)
        sm = snippet_pattern.search(item_html)
        snippet = _strip_html(sm.group(1)) if sm else ""
        results.append((title, url_, snippet))
        if len(results) >= max_results:
            break
    return results


# ----------------------------------------------------------------------
# Startpage (privacy-vriendelijk, gebruikt Google index)
# ----------------------------------------------------------------------
def _startpage(query: str, max_results: int):
    url = f"https://www.startpage.com/do/search?q={quote_plus(query)}"
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
        if r.status_code != 200:
            return []
        html = r.text
    except requests.RequestException as e:
        print(f"[web] Startpage faalde: {e}")
        return []

    # Startpage gebruikt class="w-gl__result-title" of vergelijkbaar
    link_pattern = re.compile(
        r'<a[^>]+class="w-gl__result-title[^"]*"[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
        re.DOTALL,
    )
    snippet_pattern = re.compile(
        r'<p[^>]+class="w-gl__description[^"]*"[^>]*>(.*?)</p>',
        re.DOTALL,
    )
    links = link_pattern.findall(html)
    snippets = snippet_pattern.findall(html)

    results = []
    for i, (href, title_html) in enumerate(links):
        if i >= max_results:
            break
        results.append((_strip_html(title_html), href,
                        _strip_html(snippets[i]) if i < len(snippets) else ""))
    return results


# ----------------------------------------------------------------------
# Qwant (privacy, Europees)
# ----------------------------------------------------------------------
def _qwant(query: str, max_results: int):
    url = f"https://www.qwant.com/?q={quote_plus(query)}"
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
        if r.status_code != 200:
            return []
        html = r.text
    except requests.RequestException as e:
        print(f"[web] Qwant faalde: {e}")
        return []

    # Qwant is grotendeels JS-rendered; lukt vaak niet zonder JS-engine
    # Best-effort: zoek <a href> met title-achtige inhoud
    link_pattern = re.compile(
        r'<a[^>]+href="(https?://[^"]+)"[^>]*>([^<]{10,160})</a>',
        re.DOTALL,
    )
    results = []
    seen = set()
    for href, title in link_pattern.findall(html):
        if "qwant.com" in href or "javascript:" in href:
            continue
        if href in seen:
            continue
        seen.add(href)
        results.append((_strip_html(title), href, ""))
        if len(results) >= max_results:
            break
    return results


# ----------------------------------------------------------------------
# Brave Search
# ----------------------------------------------------------------------
def _brave(query: str, max_results: int):
    url = f"https://search.brave.com/search?q={quote_plus(query)}"
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
        if r.status_code != 200:
            return []
        html = r.text
    except requests.RequestException as e:
        print(f"[web] Brave faalde: {e}")
        return []

    # Brave: class="result-header" / "snippet-description"
    link_pattern = re.compile(
        r'<a[^>]+class="[^"]*result-header[^"]*"[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
        re.DOTALL,
    )
    snippet_pattern = re.compile(
        r'<div[^>]+class="[^"]*snippet[- ]?description[^"]*"[^>]*>(.*?)</div>',
        re.DOTALL,
    )
    links = link_pattern.findall(html)
    snippets = snippet_pattern.findall(html)

    results = []
    for i, (href, title_html) in enumerate(links):
        if i >= max_results:
            break
        results.append((_strip_html(title_html), href,
                        _strip_html(snippets[i]) if i < len(snippets) else ""))
    return results


# ----------------------------------------------------------------------
# Google (werkt vaak moeilijk i.v.m. captchas, alleen als laatste keuze)
# ----------------------------------------------------------------------
def _google(query: str, max_results: int):
    url = f"https://www.google.com/search?q={quote_plus(query)}&hl=nl"
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
        if r.status_code != 200:
            return []
        html = r.text
    except requests.RequestException as e:
        print(f"[web] Google faalde: {e}")
        return []

    # Google: h3 in een <a href>, snippet vaak in span met datatag
    h3a = re.compile(
        r'<a[^>]+href="(/url\?q=[^"&]+|https?://[^"]+)"[^>]*>\s*<h3[^>]*>(.*?)</h3>',
        re.DOTALL,
    )
    results = []
    for href, title_html in h3a.findall(html):
        # Strip Google redirect
        if href.startswith("/url?q="):
            href = href[7:].split("&")[0]
        results.append((_strip_html(title_html), href, ""))
        if len(results) >= max_results:
            break
    return results


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def _strip_html(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    s = unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def _unwrap_duckduckgo_url(url: str) -> str:
    m = re.search(r"uddg=([^&]+)", url)
    if m:
        return unquote(m.group(1))
    if url.startswith("//"):
        return "https:" + url
    return url


def first_snippet(query: str) -> str | None:
    """Eerste resultaat als spreekbare tekst, of None."""
    results = web_search(query, max_results=1)
    if not results:
        return None
    title, url, snippet = results[0]
    if snippet:
        return f"{title}. {snippet}"
    return title


# ========================================================================
# SEARCH: smart APIs (Wikipedia/TheMealDB/DDG IA)  (was: search/smart_apis.py)
# ========================================================================

# ----------------------------------------------------------------------
# Wikipedia
# ----------------------------------------------------------------------
def wikipedia_summary(query: str, lang: str = "nl") -> dict | None:
    """
    Haal een korte samenvatting op van een Wikipedia-artikel.
    Probeert eerst de opgegeven taal, dan Engels als fallback.

    Returnt dict: {title, summary, url} of None.
    """
    # Strip vraag-prefixen
    clean = re.sub(
        r"^(?:wat\s+is\s+(?:een\s+|de\s+|het\s+)?|"
        r"wie\s+is\s+|"
        r"what\s+is\s+(?:a\s+|the\s+)?|"
        r"who\s+is\s+|"
        r"wer\s+ist\s+|"
        r"was\s+ist\s+(?:ein|der|die|das)?\s*)",
        "",
        query.strip(),
        flags=re.IGNORECASE,
    ).strip(" ?.!")
    if not clean:
        return None

    for try_lang in (lang, "en"):
        url = f"https://{try_lang}.wikipedia.org/api/rest_v1/page/summary/{quote(clean)}"
        try:
            r = requests.get(
                url,
                headers={"User-Agent": "DeskButler/1.0 (https://example.local)"},
                timeout=8,
            )
            if r.status_code != 200:
                continue
            data = r.json()
            # Skip disambiguatie- en redirect-pagina's zonder echte inhoud
            if data.get("type") in ("disambiguation",):
                continue
            summary = data.get("extract") or ""
            if not summary or len(summary) < 30:
                continue
            return {
                "title": data.get("title", clean),
                "summary": summary,
                "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                "lang": try_lang,
            }
        except (requests.RequestException, ValueError):
            continue
    return None


# ----------------------------------------------------------------------
# TheMealDB - recepten
# ----------------------------------------------------------------------
def search_recipe(query: str) -> dict | None:
    """
    Zoek een recept via TheMealDB (gratis, geen API key).
    Returnt dict: {name, area, category, instructions, ingredients, url} of None.
    """
    # Probeer de zoekterm te isoleren: strip "recept voor", "suikervrij", etc.
    clean = re.sub(
        r"^(?:zoek\s+(?:voor\s+(?:mij\s+)?)?(?:een\s+)?(?:lekker\s+)?|"
        r"geef\s+(?:mij\s+)?(?:een\s+)?(?:lekker\s+)?|"
        r"ik\s+wil\s+(?:een\s+)?|"
        r"find\s+(?:a\s+|me\s+a\s+)?)",
        "",
        query.strip(),
        flags=re.IGNORECASE,
    )
    # Verwijder "recept(en) voor"
    clean = re.sub(
        r"\b(?:recept(?:en)?\s+voor|recipe\s+for)\s+",
        "",
        clean,
        flags=re.IGNORECASE,
    )
    # Verwijder bijvoeglijke filters die we niet kunnen matchen ("suikervrij", "veganistisch")
    clean = re.sub(
        r"\b(?:suikervrij(?:e)?|sugar[- ]free|glutenvrij(?:e)?|gluten[- ]free|"
        r"veganistisch(?:e)?|vegan|vegetarisch(?:e)?|vegetarian|lactosevrij(?:e)?|"
        r"gezond(?:e)?|healthy|snel|easy|simpel|eenvoudig)\b",
        "",
        clean,
        flags=re.IGNORECASE,
    ).strip()
    clean = re.sub(r"\s+", " ", clean).strip(" ?.!")

    if not clean:
        return None

    url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={quote(clean)}"
    try:
        r = requests.get(url, timeout=8)
        if r.status_code != 200:
            return None
        data = r.json()
    except (requests.RequestException, ValueError):
        return None

    meals = data.get("meals") or []
    if not meals:
        return None

    meal = meals[0]

    # Ingrediënten verzamelen (TheMealDB heeft strIngredient1..20)
    ingredients = []
    for i in range(1, 21):
        ing = meal.get(f"strIngredient{i}", "")
        measure = meal.get(f"strMeasure{i}", "")
        if ing and ing.strip():
            txt = f"{measure.strip()} {ing.strip()}".strip()
            ingredients.append(txt)

    return {
        "name": meal.get("strMeal", clean),
        "area": meal.get("strArea", ""),
        "category": meal.get("strCategory", ""),
        "instructions": meal.get("strInstructions", ""),
        "ingredients": ingredients,
        "url": meal.get("strSource") or meal.get("strYoutube") or "",
        "image": meal.get("strMealThumb", ""),
    }


# ----------------------------------------------------------------------
# DuckDuckGo Instant Answer API (JSON, geen scraping)
# ----------------------------------------------------------------------
def ddg_instant_answer(query: str) -> dict | None:
    """
    Probeer DuckDuckGo's Instant Answer API. Geeft soms direct een
    samenvatting (uit Wikipedia of andere bronnen). Returnt None als
    er geen bruikbaar antwoord is.
    """
    url = f"https://api.duckduckgo.com/?q={quote(query)}&format=json&no_html=1&skip_disambig=1"
    try:
        r = requests.get(
            url,
            headers={"User-Agent": "DeskButler/1.0"},
            timeout=8,
        )
        if r.status_code != 200:
            return None
        data = r.json()
    except (requests.RequestException, ValueError):
        return None

    abstract = data.get("AbstractText") or data.get("Abstract") or ""
    if not abstract or len(abstract) < 30:
        # Probeer Definition als alternatief
        abstract = data.get("Definition") or ""
        if not abstract or len(abstract) < 20:
            return None

    return {
        "title": data.get("Heading") or query,
        "summary": abstract,
        "url": data.get("AbstractURL") or data.get("DefinitionURL") or "",
        "source": data.get("AbstractSource") or data.get("DefinitionSource") or "",
    }


# ----------------------------------------------------------------------
# Detecteer welke smart-API past bij de query
# ----------------------------------------------------------------------
def try_smart_search(query: str, lang: str = "nl") -> dict | None:
    """
    Probeer in volgorde: TheMealDB voor recepten, Wikipedia voor 'wat is/wie is',
    DuckDuckGo Instant Answer als algemene fallback.

    Returnt dict met velden:
      - kind: "recipe" | "wikipedia" | "instant_answer"
      - title, summary, url
      - extra velden afhankelijk van kind
    """
    if not query:
        return None
    q_low = query.lower()

    # 1) Recept-patroon
    if re.search(r"\brecept(?:en)?\b|\brecipe(?:s)?\b", q_low):
        recipe = search_recipe(query)
        if recipe:
            return {"kind": "recipe", **recipe}

    # 2) Wat-is / Wie-is patroon -> Wikipedia
    if re.search(
        r"^(?:wat\s+is|wie\s+is|wat\s+zijn|what\s+is|who\s+is|wer\s+ist|was\s+ist)\b",
        q_low,
    ):
        wiki = wikipedia_summary(query, lang=lang)
        if wiki:
            return {"kind": "wikipedia", **wiki}

    # 3) Algemeen -> DDG Instant Answer (best-effort, vaak leeg)
    ia = ddg_instant_answer(query)
    if ia:
        return {"kind": "instant_answer", **ia}

    return None


# ========================================================================
# SEARCH: weather  (was: search/weather.py)
# ========================================================================

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

WMO_CODES = {
    0: "helder", 1: "vrijwel helder", 2: "deels bewolkt", 3: "bewolkt",
    45: "mistig", 48: "mist met rijp",
    51: "lichte motregen", 53: "motregen", 55: "dichte motregen",
    61: "lichte regen", 63: "regen", 65: "zware regen",
    66: "ijzel", 67: "zware ijzel",
    71: "lichte sneeuwval", 73: "sneeuwval", 75: "zware sneeuwval",
    77: "sneeuwkorrels",
    80: "lichte regenbui", 81: "regenbui", 82: "hevige regenbui",
    85: "sneeuwbui", 86: "zware sneeuwbui",
    95: "onweer", 96: "onweer met hagel", 99: "zwaar onweer met hagel",
}


# Woorden die in een 'weer'-query staan maar GEEN stadsnaam zijn.
_STOPWORDS = {
    "weer", "het", "wat", "is", "in", "voor", "vandaag", "morgen", "nu",
    "zie", "doe", "geef", "me", "u", "mij", "graag", "alstublieft",
    "weather", "the", "what", "today", "tomorrow", "now",
    "wetter", "was", "ist", "das", "heute", "jetzt",
    "meteo", "météo", "le", "la", "quel",
}


def extract_city(query: str) -> str | None:
    """Trek een stadsnaam uit een weer-query. None = huidige locatie."""
    if not query:
        return None
    clean = re.sub(r"[?!.,;:]", " ", query)
    words = clean.split()
    if not words:
        return None
    keep = [w for w in words if w.lower() not in _STOPWORDS]
    if not keep:
        return None
    candidate = " ".join(keep).strip()
    if len(candidate) < 2:
        return None
    return candidate


def get_weather(city: str = None, lang: str = "nl") -> dict | None:
    """
    Huidige weer voor een stad. Geeft dict met data OF dict met 'error' veld.
    """
    if not city:
        loc = _ip_location()
        if not loc:
            return {"error": "no_location",
                    "message": "Ik kon uw locatie niet bepalen. Vraag mij bijvoorbeeld het weer in een stad."}
        lat, lon, name = loc
    else:
        coords = _geocode(city)
        if not coords:
            return {"error": "city_not_found",
                    "message": f"Ik kon de stad '{city}' niet vinden."}
        lat, lon, name = coords

    try:
        r = requests.get(
            WEATHER_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,weather_code,wind_speed_10m",
                "timezone": "auto",
            },
            timeout=8,
        )
        r.raise_for_status()
        data = r.json()
        cur = data.get("current", {})
        temp = cur.get("temperature_2m")
        code = cur.get("weather_code", 0)
        wind = cur.get("wind_speed_10m")
        return {
            "city": name,
            "temp": round(temp) if temp is not None else None,
            "description": WMO_CODES.get(code, "onbekend"),
            "wind_kmh": round(wind) if wind is not None else None,
        }
    except requests.RequestException as e:
        return {"error": "api_failed",
                "message": f"De weer-service is niet bereikbaar ({e.__class__.__name__})."}


def _geocode(city: str):
    try:
        r = requests.get(
            GEOCODE_URL,
            params={"name": city, "count": 1, "language": "nl"},
            timeout=8,
        )
        r.raise_for_status()
        data = r.json()
        results = data.get("results")
        if not results:
            return None
        top = results[0]
        return top["latitude"], top["longitude"], top.get("name", city)
    except requests.RequestException:
        return None


def _ip_location():
    """Locatie via IP, met twee providers als fallback."""
    for url in ("https://ipapi.co/json/", "http://ip-api.com/json/"):
        try:
            r = requests.get(url, timeout=6)
            if r.status_code != 200:
                continue
            data = r.json()
            lat = data.get("latitude") or data.get("lat")
            lon = data.get("longitude") or data.get("lon")
            name = data.get("city") or "uw locatie"
            if lat is not None and lon is not None:
                return lat, lon, name
        except (requests.RequestException, ValueError):
            continue
    return None


def _weather_speak_text(weather: dict | None) -> str:
    """Uitspreekbare zin van een weer-dict."""
    if not weather:
        return _("weather_unavailable")
    if "error" in weather:
        return weather.get("message", _("weather_unavailable"))
    parts = [_("weather_for", city=weather["city"]) + "."]
    if weather.get("temp") is not None:
        parts.append(
            _("weather_now", temp=weather["temp"], desc=weather["description"])
        )
    if weather.get("wind_kmh") is not None:
        parts.append(f"De wind is {weather['wind_kmh']} kilometer per uur.")
    return " ".join(parts)


# ========================================================================
# SEARCH: news  (was: search/news.py)
# ========================================================================

# Standaard feed per taal (gebruikt voor "nieuws" zonder bron)
DEFAULT_FEEDS = {
    "nl": "https://feeds.nos.nl/nosnieuwsalgemeen",
    "en": "http://feeds.bbci.co.uk/news/rss.xml",
    "de": "https://www.tagesschau.de/xml/rss2",
    "fr": "https://www.lemonde.fr/rss/une.xml",
    "es": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada",
    "it": "https://www.ansa.it/sito/ansait_rss.xml",
    "pt": "https://feeds.folha.uol.com.br/folha/topo/rss091.xml",
    "ru": "https://lenta.ru/rss/news",
    "ja": "https://www3.nhk.or.jp/rss/news/cat0.xml",
    "sv": "https://www.svt.se/nyheter/rss.xml",
    "pl": "https://www.tvn24.pl/najnowsze.xml",
    "tr": "https://www.hurriyet.com.tr/rss/anasayfa",
}

# Backwards compat (oudere code refereert hier nog naar)
FEEDS = DEFAULT_FEEDS

# Specifieke nieuwssites die de gebruiker bij naam kan vragen.
# Sleutels zijn lowercase / spelling-tolerant.
NAMED_SOURCES = {
    # Nederland
    "nos":       "https://feeds.nos.nl/nosnieuwsalgemeen",
    "nu":        "https://www.nu.nl/rss/Algemeen",
    "nu.nl":     "https://www.nu.nl/rss/Algemeen",
    "rtl":       "https://www.rtlnieuws.nl/rss.xml",
    "rtlnieuws": "https://www.rtlnieuws.nl/rss.xml",
    "telegraaf": "https://www.telegraaf.nl/rss",
    "ad":        "https://www.ad.nl/home/rss.xml",
    "volkskrant": "https://www.volkskrant.nl/voorpagina/rss.xml",
    "nrc":       "https://www.nrc.nl/rss/",
    "trouw":     "https://www.trouw.nl/voorpagina/rss.xml",
    "parool":    "https://www.parool.nl/voorpagina/rss.xml",
    "fd":        "https://fd.nl/?widget=rssfeed&view=feed&contentId=1129931",
    # Internationaal
    "bbc":       "http://feeds.bbci.co.uk/news/rss.xml",
    "cnn":       "http://rss.cnn.com/rss/edition.rss",
    "reuters":   "https://www.reutersagency.com/feed/?best-topics=top-news&post_type=best",
    "guardian":  "https://www.theguardian.com/world/rss",
    "nytimes":   "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "tagesschau": "https://www.tagesschau.de/xml/rss2",
    "spiegel":   "https://www.spiegel.de/schlagzeilen/index.rss",
    "lemonde":   "https://www.lemonde.fr/rss/une.xml",
}


def _source_from_query(query: str) -> str | None:
    """Zoek een bekende nieuwsbron in de query. None = standaard feed."""
    if not query:
        return None
    q = query.lower()
    # Sorteer op lengte (langste eerst) zodat 'rtlnieuws' niet als 'rtl' wordt herkend
    for name in sorted(NAMED_SOURCES.keys(), key=len, reverse=True):
        # Match op woordgrens om bv 'fd' niet in 'fdaling' te matchen
        if re.search(r"\b" + re.escape(name) + r"\b", q):
            return name
    return None


def get_headlines(max_items: int = 5, query: str = None):
    """
    Geef een lijst (titel, samenvatting, url, bronnaam) van het laatste nieuws.
    Als 'query' een bekende bron noemt, gebruik die. Anders default per taal.
    """
    source_name = _source_from_query(query) if query else None
    if source_name:
        feed_url = NAMED_SOURCES[source_name]
        display_name = source_name.upper()
    else:
        lang = detect_language()
        feed_url = DEFAULT_FEEDS.get(lang, DEFAULT_FEEDS["en"])
        display_name = None  # generiek

    try:
        feed = feedparser.parse(feed_url)
    except Exception as e:
        print(f"[news] parsing faalde ({feed_url}): {e}")
        return []

    if not feed.entries:
        return []

    items = []
    for entry in feed.entries[:max_items]:
        title = entry.get("title", "").strip()
        summary = entry.get("summary", "").strip()
        # Strip eventuele HTML tags uit summary
        summary = re.sub(r"<[^>]+>", "", summary)
        link = entry.get("link", "")
        items.append((title, summary, link, display_name))
    return items


def _news_speak_text(max_items: int = 3, query: str = None) -> str:
    """Maak een uitspreekbare tekst van het belangrijkste nieuws."""
    items = get_headlines(max_items, query)
    if not items:
        return _("news_unavailable")

    # Eerste item heeft de bronnaam (of None)
    first_source = items[0][3] if items[0][3] else None
    if first_source:
        parts = [f"Het nieuws van {first_source}:"]
    else:
        parts = [_("news_today") + ":"]

    for i, (title, _summary, _link, _src) in enumerate(items, 1):
        parts.append(f"{i}. {title}.")
    return " ".join(parts)


# ========================================================================
# SEARCH: Windows apps  (was: search/apps.py)
# ========================================================================

# Bekende programma's met directe executable mapping (case-insensitive)
KNOWN_APPS = {
    "notepad": "notepad.exe",
    "kladblok": "notepad.exe",
    "calculator": "calc.exe",
    "rekenmachine": "calc.exe",
    "paint": "mspaint.exe",
    "wordpad": "write.exe",
    "explorer": "explorer.exe",
    "verkenner": "explorer.exe",
    "cmd": "cmd.exe",
    "command prompt": "cmd.exe",
    "opdrachtprompt": "cmd.exe",
    "powershell": "powershell.exe",
    "terminal": "wt.exe",
    "task manager": "taskmgr.exe",
    "taakbeheer": "taskmgr.exe",
    "control panel": "control.exe",
    "configuratiescherm": "control.exe",
    "settings": "ms-settings:",
    "instellingen": "ms-settings:",
    "edge": "msedge.exe",
    "microsoft edge": "msedge.exe",
}


def _start_menu_paths():
    """Locaties waar Windows snelkoppelingen plaatst."""
    candidates = []
    appdata = os.environ.get("APPDATA")
    program_data = os.environ.get("ProgramData")
    if appdata:
        candidates.append(Path(appdata) / "Microsoft/Windows/Start Menu/Programs")
    if program_data:
        candidates.append(Path(program_data) / "Microsoft/Windows/Start Menu/Programs")
    return [p for p in candidates if p.exists()]


def find_shortcut(name: str) -> Path | None:
    """Zoek een .lnk file in het Start menu waarvan de naam matched."""
    name_low = name.lower()
    best_match = None
    best_len_diff = 9999
    for root in _start_menu_paths():
        for lnk in root.rglob("*.lnk"):
            stem = lnk.stem.lower()
            if name_low == stem:
                return lnk
            if name_low in stem:
                # Voorkeur voor kortere match (preciezere overeenkomst)
                ld = len(stem) - len(name_low)
                if ld < best_len_diff:
                    best_match = lnk
                    best_len_diff = ld
    return best_match


def open_app(name: str) -> bool:
    """
    Probeer een Windows-programma te openen.
    Returnt True bij succes, False als niets gevonden.
    """
    if not name:
        return False
    key = name.strip().lower()

    # 1. Bekende namen
    if key in KNOWN_APPS:
        exe = KNOWN_APPS[key]
        try:
            if exe.endswith(":"):  # ms-settings: e.d.
                if os.name == "nt":
                    os.startfile(exe)
                return True
            subprocess.Popen(exe, shell=True)
            return True
        except Exception as e:
            print(f"[apps] kon {exe} niet starten: {e}")

    # 2. Start-menu snelkoppeling
    lnk = find_shortcut(key)
    if lnk is not None:
        try:
            if os.name == "nt":
                os.startfile(str(lnk))
                return True
        except Exception as e:
            print(f"[apps] os.startfile faalde: {e}")

    # 3. Probeer 'start' via cmd (laatste redmiddel)
    try:
        if os.name == "nt":
            subprocess.Popen(["cmd", "/c", "start", "", name], shell=False)
            return True
    except Exception:
        pass

    return False


# ========================================================================
# SEARCH: lokale bestanden  (was: search/files.py)
# ========================================================================

def _user_search_dirs() -> list:
    """Standaard mappen om in te zoeken."""
    home = Path.home()
    candidates = [
        home / "Documents", home / "Documenten",
        home / "Desktop", home / "Bureaublad",
        home / "Downloads",
        home / "Pictures", home / "Afbeeldingen",
        home / "Music", home / "Muziek",
        home / "Videos", home / "Video's",
        home / "OneDrive",
    ]
    return [p for p in candidates if p.exists() and p.is_dir()]


def find_files(query: str, max_results: int = 20, max_depth: int = 6) -> list:
    """
    Zoek bestanden die de zoekterm in hun naam bevatten.
    Returnt een lijst Path-objecten, sorted by mtime (nieuwste eerst).
    """
    if not query or len(query.strip()) < 2:
        return []
    needle = query.strip().lower()
    matches = []

    for root in _user_search_dirs():
        for match in _walk_files(root, needle, max_results - len(matches), max_depth):
            matches.append(match)
            if len(matches) >= max_results:
                break
        if len(matches) >= max_results:
            break

    # Nieuwste eerst
    try:
        matches.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    except OSError:
        pass
    return matches


def _walk_files(root: Path, needle: str, limit: int, max_depth: int):
    """Generator: lopen door root en submappen tot max_depth, yield matches."""
    if limit <= 0:
        return
    try:
        for dirpath, dirnames, filenames in os.walk(root):
            # Diepte beperken
            rel = Path(dirpath).relative_to(root)
            depth = len(rel.parts)
            if depth > max_depth:
                dirnames[:] = []
                continue
            # Skip verborgen / systeem mappen
            dirnames[:] = [
                d for d in dirnames
                if not d.startswith(".") and not d.startswith("$") and d.lower() != "node_modules"
            ]
            for fname in filenames:
                if needle in fname.lower():
                    yield Path(dirpath) / fname
                    limit -= 1
                    if limit <= 0:
                        return
    except (PermissionError, OSError):
        return


# ========================================================================
# HOTKEYS  (was: hotkeys.py)
# ========================================================================

class HotkeyManager(QObject):
    """Luistert naar globale sneltoetsen en stuurt Qt-signalen."""

    search_triggered = Signal()
    read_clipboard_triggered = Signal()

    def __init__(self):
        super().__init__()
        self._thread = None
        self._handles = []

    def start(self):
        """Start de hotkey-luisteraar in een aparte thread."""
        try:
            import keyboard
        except ImportError:
            print("[hotkeys] 'keyboard' library niet geïnstalleerd. Hotkeys uitgeschakeld.")
            return

        hotkey_search = config.get("hotkey_search", "shift+v")
        hotkey_clipboard = config.get("hotkey_read_clipboard", "ctrl+shift+l")

        def listen():
            try:
                h1 = keyboard.add_hotkey(
                    hotkey_search, lambda: self.search_triggered.emit()
                )
                h2 = keyboard.add_hotkey(
                    hotkey_clipboard, lambda: self.read_clipboard_triggered.emit()
                )
                self._handles = [h1, h2]
                print(f"[hotkeys] Geregistreerd: {hotkey_search} -> zoek, "
                      f"{hotkey_clipboard} -> klembord-voorlezen")
                keyboard.wait()
            except Exception as e:
                print(f"[hotkeys] Hotkey-registratie faalde: {e}")
                print("[hotkeys] Op sommige systemen vereist 'keyboard' admin-rechten.")

        self._thread = threading.Thread(target=listen, daemon=True)
        self._thread.start()

    def stop(self):
        try:
            import keyboard
            for h in self._handles:
                try:
                    keyboard.remove_hotkey(h)
                except Exception:
                    pass
        except Exception:
            pass


# ========================================================================
# UI: volledige tekst venster (scrollbaar)  (was: ui/full_text_dialog.py)
# ========================================================================

class FullTextDialog(QDialog):
    """Modaal venster met de volledige tekst en een scrollbar."""

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Volledige tekst")
        self.setMinimumSize(720, 480)

        apply_dialog_style(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Titel
        title = QLabel("📝  Volledige tekst")
        title.setFont(title_font())
        layout.addWidget(title)

        # Hulpzin
        hint = QLabel("Hieronder de complete inhoud. Scroll om alles te lezen.")
        hint.setFont(base_font())
        hint.setStyleSheet("color: #a0a0a0; padding-bottom: 8px;")
        layout.addWidget(hint)

        # Tekstvak met scrollbar
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        self.text.setPlainText(text)
        self.text.setFont(base_font())
        # Verticale scrollbar altijd zichtbaar als nodig (Qt regelt automatisch)
        layout.addWidget(self.text, 1)

        # Knoppen onder: kopiëren + sluiten
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        btn_copy = QPushButton("📋  Kopiëren naar klembord")
        btn_copy.setFont(base_font())
        btn_copy.setMinimumHeight(48)
        btn_copy.clicked.connect(self._copy_to_clipboard)
        btn_row.addWidget(btn_copy)

        btn_row.addStretch()

        btn_close = QPushButton("Sluiten")
        btn_close.setFont(base_font())
        btn_close.setMinimumHeight(48)
        btn_close.setMinimumWidth(120)
        btn_close.setObjectName("primary")
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)

        layout.addLayout(btn_row)


    def showEvent(self, event):
        super().showEvent(event)
        # EU-toegankelijkheid: handje + tooltips op alle interactieve widgets
        try:
            apply_accessibility(self)
        except Exception:
            pass

    def _copy_to_clipboard(self):
        QApplication.clipboard().setText(self.text.toPlainText())
        # Korte status
        self.setWindowTitle("Volledige tekst — Gekopieerd!")


# ========================================================================
# UI: ja/nee dialoog (herbruikbaar)  (was: ui/yes_no_dialog.py)
# ========================================================================

class YesNoDialog(QDialog):
    """
    Eenvoudige ja/nee-dialoog met grote, gekleurde knoppen.
    Groene Ja-knop, rode Nee-knop (consistent met de rest van de app).
    """

    def __init__(self, question: str, parent=None,
                 yes_text: str = "Ja",
                 no_text: str = "Nee",
                 title: str = "Even bevestigen"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(520, 280)

        apply_dialog_style(self)
        big = base_font()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(18)

        # Titel
        title_lbl = QLabel(title)
        title_lbl.setFont(title_font())
        layout.addWidget(title_lbl)

        # Vraag
        q_label = QLabel(question)
        q_label.setFont(QFont("Segoe UI", big.pointSize() + 1))
        q_label.setWordWrap(True)
        q_label.setMinimumHeight(70)
        q_label.setStyleSheet(
            "background:#2a2a2a; padding:14px; border-radius:6px; color:#e0e0e0;"
        )
        layout.addWidget(q_label, 1)

        # Knoppen
        btn_row = QHBoxLayout()
        btn_row.setSpacing(14)

        self.btn_yes = QPushButton(f"✓  {yes_text}")
        self.btn_yes.setFont(QFont("Segoe UI", big.pointSize(), QFont.Bold))
        self.btn_yes.setMinimumHeight(64)
        self.btn_yes.setStyleSheet(
            "QPushButton { background:#2a8a2a; color:#fff; "
            "border:3px solid #4aaa4a; border-radius:6px; padding:8px 20px; }"
            "QPushButton:hover { background:#3a9a3a; }"
        )
        self.btn_yes.clicked.connect(self.accept)
        btn_row.addWidget(self.btn_yes)

        self.btn_no = QPushButton(f"✕  {no_text}")
        self.btn_no.setFont(QFont("Segoe UI", big.pointSize(), QFont.Bold))
        self.btn_no.setMinimumHeight(64)
        self.btn_no.setStyleSheet(
            "QPushButton { background:#8a2a2a; color:#fff; "
            "border:3px solid #aa4a4a; border-radius:6px; padding:8px 20px; }"
            "QPushButton:hover { background:#9a3a3a; }"
        )
        self.btn_no.clicked.connect(self.reject)
        btn_row.addWidget(self.btn_no)

        layout.addLayout(btn_row)

        # Toegankelijkheid: na opbouw alle widgets
        apply_accessibility(self)

        # Focus standaard op Nee, zodat Enter niet meteen Ja activeert
        # (veiliger default — gebruiker moet bewust kiezen)
        self.btn_no.setDefault(True)
        self.btn_no.setFocus()

    def keyPressEvent(self, event):
        """Snelkoppelingen: J = Ja, N = Nee, Esc = Nee."""
        key = event.key()
        text = event.text().lower()
        if text == "j" or key == Qt.Key_Y:
            self.accept()
        elif text == "n" or key == Qt.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)


# ========================================================================
# UI: browser-extensies beheer-venster + editor  (was: ui/extensions_window.py)
# ========================================================================

# ----------------------------------------------------------------------
# Eenvoudige JS/CSS syntax highlighter voor de editor
# ----------------------------------------------------------------------
class _SimpleSyntaxHighlighter(QSyntaxHighlighter):
    """Geeft sleutelwoorden, strings en commentaar een kleur."""

    def __init__(self, parent, language: str = "js"):
        super().__init__(parent)
        self.language = language

        # Kleuren
        self.fmt_keyword = QTextCharFormat()
        self.fmt_keyword.setForeground(QColor("#569cd6"))
        self.fmt_keyword.setFontWeight(QFont.Bold)

        self.fmt_string = QTextCharFormat()
        self.fmt_string.setForeground(QColor("#ce9178"))

        self.fmt_comment = QTextCharFormat()
        self.fmt_comment.setForeground(QColor("#6a9955"))
        self.fmt_comment.setFontItalic(True)

        self.fmt_number = QTextCharFormat()
        self.fmt_number.setForeground(QColor("#b5cea8"))

        self.fmt_property = QTextCharFormat()
        self.fmt_property.setForeground(QColor("#9cdcfe"))

    def highlightBlock(self, text):
        import re
        # Commentaren: // ... en /* ... */
        for m in re.finditer(r"//[^\n]*|/\*.*?\*/", text):
            self.setFormat(m.start(), m.end() - m.start(), self.fmt_comment)
        # Strings
        for m in re.finditer(r"'[^'\n]*'|\"[^\"\n]*\"|`[^`]*`", text):
            self.setFormat(m.start(), m.end() - m.start(), self.fmt_string)
        # Getallen
        for m in re.finditer(r"\b\d+(\.\d+)?\b", text):
            self.setFormat(m.start(), m.end() - m.start(), self.fmt_number)
        # Sleutelwoorden
        if self.language == "js":
            kws = (r"\b(function|var|let|const|if|else|for|while|return|"
                   r"document|window|true|false|null|undefined|new|this)\b")
        else:  # css
            kws = (r"\b(important|inherit|initial|none|auto|absolute|"
                   r"relative|fixed|block|inline|flex|grid)\b")
        for m in re.finditer(kws, text):
            self.setFormat(m.start(), m.end() - m.start(), self.fmt_keyword)


# ----------------------------------------------------------------------
# Editor-dialoog voor een nieuwe of bestaande extensie
# ----------------------------------------------------------------------
class _ExtensionEditorDialog(QDialog):
    """Een eenvoudige editor om eigen extensies te schrijven/bewerken."""

    def __init__(self, ext: BrowserExtension = None, parent=None):
        super().__init__(parent)
        self.ext = ext
        self.saved = False
        self.setWindowTitle("Extensie bewerken" if ext else "Nieuwe extensie")
        self.resize(900, 720)
        apply_dialog_style(self)

        big = base_font()

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(12)

        title_lbl = QLabel("Extensie bewerken" if ext else "Nieuwe extensie")
        title_lbl.setFont(title_font())
        root.addWidget(title_lbl)

        # Uitleg
        info = QLabel(
            "Een extensie injecteert CSS of JavaScript in webpagina's. "
            "Schrijf hieronder zelf code, of begin met een voorbeeld-sjabloon."
        )
        info.setFont(big)
        info.setWordWrap(True)
        info.setStyleSheet("color:#c0c0c0; padding:4px;")
        root.addWidget(info)

        # Vorm: naam + type + url-pattern
        form = QFormLayout()
        form.setSpacing(8)

        self.txt_name = QLineEdit()
        self.txt_name.setFont(big)
        self.txt_name.setMinimumHeight(36)
        self.txt_name.setPlaceholderText("Bijvoorbeeld: Wikipedia-zoom-vergroten")
        form.addRow(self._label("Naam:"), self.txt_name)

        self.cmb_type = QComboBox()
        self.cmb_type.setFont(big)
        self.cmb_type.setMinimumHeight(36)
        self.cmb_type.addItem("🎨 CSS-extensie (kleuren/lay-out aanpassen)", "css")
        self.cmb_type.addItem("⚙ JavaScript-extensie (gedrag aanpassen)", "js")
        self.cmb_type.currentIndexChanged.connect(self._on_type_changed)
        form.addRow(self._label("Type:"), self.cmb_type)

        self.txt_pattern = QLineEdit()
        self.txt_pattern.setFont(big)
        self.txt_pattern.setMinimumHeight(36)
        self.txt_pattern.setText("*")
        self.txt_pattern.setPlaceholderText("* = overal, of bv. *wikipedia.org*")
        form.addRow(self._label("URL-patroon:"), self.txt_pattern)

        root.addLayout(form)

        # Editor — monospace + syntax highlighting
        editor_lbl = QLabel("Code:")
        editor_lbl.setFont(big)
        root.addWidget(editor_lbl)

        self.editor = QTextEdit()
        self.editor.setFont(QFont("Consolas", base_font().pointSize() + 1))
        self.editor.setStyleSheet(
            "QTextEdit { background:#1e1e1e; color:#d4d4d4; "
            "border:1px solid #3a3a3a; border-radius:6px; padding:8px; }"
        )
        self.editor.setMinimumHeight(280)
        root.addWidget(self.editor, 1)

        self.highlighter = _SimpleSyntaxHighlighter(self.editor.document(), "js")

        # Help-tekst
        help_lbl = QLabel(
            "💡 Tip: zoek voor inspiratie op sites zoals greasyfork.org of "
            "userstyles.world (heel veel kant-en-klare scripts en stijlen "
            "die u kunt overnemen)."
        )
        help_lbl.setFont(big)
        help_lbl.setWordWrap(True)
        help_lbl.setStyleSheet("color:#909090; padding:4px;")
        root.addWidget(help_lbl)

        # Knoppen
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.btn_save = QPushButton("✓  Opslaan")
        self.btn_save.setFont(QFont("Segoe UI", big.pointSize(), QFont.Bold))
        self.btn_save.setMinimumHeight(48)
        self.btn_save.setMinimumWidth(140)
        self.btn_save.setStyleSheet(
            "QPushButton { background:#2a8a2a; color:#fff; "
            "border:3px solid #4aaa4a; border-radius:6px; padding:6px 16px; }"
            "QPushButton:hover { background:#3a9a3a; }"
        )
        self.btn_save.clicked.connect(self._on_save)
        btn_row.addWidget(self.btn_save)

        btn_cancel = QPushButton("✕  Annuleren")
        btn_cancel.setFont(QFont("Segoe UI", big.pointSize(), QFont.Bold))
        btn_cancel.setMinimumHeight(48)
        btn_cancel.setMinimumWidth(140)
        btn_cancel.setStyleSheet(
            "QPushButton { background:#8a2a2a; color:#fff; "
            "border:3px solid #aa4a4a; border-radius:6px; padding:6px 16px; }"
            "QPushButton:hover { background:#9a3a3a; }"
        )
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)

        btn_row.addStretch()
        root.addLayout(btn_row)

        # Vul vooraf in als bewerken-modus
        if ext:
            self.txt_name.setText(ext.name)
            self.txt_pattern.setText(ext.url_pattern)
            if ext.css and not ext.js:
                self.cmb_type.setCurrentIndex(0)
                self.editor.setPlainText(ext.css)
            else:
                self.cmb_type.setCurrentIndex(1)
                self.editor.setPlainText(ext.js)
        else:
            # Begin met een sjabloon
            self.cmb_type.setCurrentIndex(0)
            self.editor.setPlainText(USERSTYLE_TEMPLATE)

        apply_accessibility(self)

    def _label(self, t: str) -> QLabel:
        lbl = QLabel(t)
        lbl.setFont(base_font())
        return lbl

    def _on_type_changed(self, idx: int):
        kind = self.cmb_type.itemData(idx)
        # Wissel syntax highlighter
        self.highlighter = _SimpleSyntaxHighlighter(
            self.editor.document(), kind
        )
        # Als veld leeg / sjabloon: vervang met passend sjabloon
        cur = self.editor.toPlainText().strip()
        if not cur or cur in (USERSCRIPT_TEMPLATE.strip(), USERSTYLE_TEMPLATE.strip()):
            self.editor.setPlainText(
                USERSCRIPT_TEMPLATE if kind == "js" else USERSTYLE_TEMPLATE
            )

    def _on_save(self):
        name = self.txt_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Naam ontbreekt",
                                "Geef de extensie een naam.")
            return
        content = self.editor.toPlainText()
        if not content.strip():
            QMessageBox.warning(self, "Inhoud ontbreekt",
                                "Schrijf wat code voor de extensie.")
            return
        kind = self.cmb_type.currentData()  # 'css' of 'js'

        # Sla op
        try:
            mgr = get_extensions_manager()
            mgr.save_user_extension(name, content, kind)
            self.saved = True
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Opslaan mislukt", f"Kon niet opslaan: {e}")


# ----------------------------------------------------------------------
# Hoofdvenster: lijst van extensies + acties
# ----------------------------------------------------------------------
class ExtensionsWindow(QMainWindow):
    """Beheer venster voor browser-extensies."""

    extensions_changed = Signal()  # voor de browser om opnieuw te injecteren

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Browser-extensies")
        self.resize(960, 700)
        apply_dialog_style(self)

        self._setup_ui()
        self._populate()

    def _setup_ui(self):
        big = base_font()
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # Titel + uitleg
        title_lbl = QLabel("🧩 Browser-extensies")
        title_lbl.setFont(title_font())
        root.addWidget(title_lbl)

        info = QLabel(
            "Extensies maken websites aangenamer: donkere kleuren, "
            "reclame verbergen, tekst voorlezen, en meer. "
            "Klik op een extensie in de lijst om hem aan of uit te zetten. "
            "U kunt ook eigen extensies maken — gebruik de groene knop onderaan."
        )
        info.setFont(big)
        info.setWordWrap(True)
        info.setStyleSheet("color:#c0c0c0; padding:8px; background:#2a2a2a; border-radius:6px;")
        root.addWidget(info)

        # Splitter: lijst (links) + details (rechts)
        splitter = QSplitter(Qt.Horizontal)
        root.addWidget(splitter, 1)

        # Links: lijst
        self.lst = QListWidget()
        self.lst.setFont(big)
        self.lst.setMinimumWidth(360)
        self.lst.itemClicked.connect(self._on_item_clicked)
        self.lst.currentItemChanged.connect(self._on_item_selected)
        splitter.addWidget(self.lst)

        # Rechts: details + knoppen
        right = QWidget()
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(8, 0, 0, 0)

        self.lbl_detail_name = QLabel("Kies een extensie...")
        self.lbl_detail_name.setFont(QFont("Segoe UI", big.pointSize() + 2, QFont.Bold))
        self.lbl_detail_name.setWordWrap(True)
        right_lay.addWidget(self.lbl_detail_name)

        self.lbl_detail_status = QLabel("")
        self.lbl_detail_status.setFont(big)
        right_lay.addWidget(self.lbl_detail_status)

        self.lbl_detail_desc = QLabel("")
        self.lbl_detail_desc.setFont(big)
        self.lbl_detail_desc.setWordWrap(True)
        self.lbl_detail_desc.setStyleSheet(
            "background:#2a2a2a; padding:14px; border-radius:6px; color:#d0d0d0;"
        )
        self.lbl_detail_desc.setMinimumHeight(140)
        right_lay.addWidget(self.lbl_detail_desc, 1)

        # Detail-knoppen (toggle / bewerken / verwijderen)
        btn_detail = QHBoxLayout()
        btn_detail.setSpacing(8)

        self.btn_toggle = QPushButton("✓  Inschakelen")
        self.btn_toggle.setFont(QFont("Segoe UI", big.pointSize(), QFont.Bold))
        self.btn_toggle.setMinimumHeight(48)
        self.btn_toggle.clicked.connect(self._on_toggle)
        btn_detail.addWidget(self.btn_toggle)

        self.btn_edit = QPushButton("✏️  Bewerken")
        self.btn_edit.setFont(big)
        self.btn_edit.setMinimumHeight(48)
        self.btn_edit.clicked.connect(self._on_edit)
        self.btn_edit.setEnabled(False)
        btn_detail.addWidget(self.btn_edit)

        self.btn_delete = QPushButton("🗑️  Verwijderen")
        self.btn_delete.setFont(big)
        self.btn_delete.setMinimumHeight(48)
        self.btn_delete.clicked.connect(self._on_delete)
        self.btn_delete.setEnabled(False)
        btn_detail.addWidget(self.btn_delete)

        right_lay.addLayout(btn_detail)
        splitter.addWidget(right)
        splitter.setSizes([400, 540])

        # Onder: knop om nieuwe te maken + openen folder
        bottom = QHBoxLayout()
        bottom.setSpacing(10)

        btn_new = QPushButton("➕  Nieuwe extensie maken")
        btn_new.setFont(QFont("Segoe UI", big.pointSize(), QFont.Bold))
        btn_new.setMinimumHeight(52)
        btn_new.setMinimumWidth(220)
        btn_new.setStyleSheet(
            "QPushButton { background:#2a8a2a; color:#fff; "
            "border:3px solid #4aaa4a; border-radius:6px; padding:6px 16px; }"
            "QPushButton:hover { background:#3a9a3a; }"
        )
        btn_new.setToolTip("Maak een nieuwe eigen extensie met een editor")
        btn_new.clicked.connect(self._on_new)
        bottom.addWidget(btn_new)

        btn_folder = QPushButton("📁  Open extensies-map")
        btn_folder.setFont(big)
        btn_folder.setMinimumHeight(52)
        btn_folder.setMinimumWidth(200)
        btn_folder.setToolTip("Open de map waar uw eigen extensies staan")
        btn_folder.clicked.connect(self._on_open_folder)
        bottom.addWidget(btn_folder)

        btn_help = QPushButton("❓  Hulp / voorbeelden")
        btn_help.setFont(big)
        btn_help.setMinimumHeight(52)
        btn_help.setMinimumWidth(200)
        btn_help.setToolTip("Lees hoe u zelf extensies kunt maken")
        btn_help.clicked.connect(self._on_help)
        bottom.addWidget(btn_help)

        bottom.addStretch()

        btn_close = QPushButton("Sluiten")
        btn_close.setFont(big)
        btn_close.setMinimumHeight(52)
        btn_close.setMinimumWidth(140)
        btn_close.clicked.connect(self.close)
        bottom.addWidget(btn_close)

        root.addLayout(bottom)

        apply_accessibility(self)

    def _populate(self):
        """Laad alle extensies in de lijst."""
        self.lst.clear()
        mgr = get_extensions_manager()
        for ext in mgr.all():
            label = f"{'✓ ' if ext.enabled else '○ '}{ext.name}"
            if ext.type == "user":
                label += "  (eigen)"
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, ext.id)
            self.lst.addItem(item)
        if self.lst.count() > 0:
            self.lst.setCurrentRow(0)

    def _selected_extension(self) -> BrowserExtension:
        item = self.lst.currentItem()
        if not item:
            return None
        ext_id = item.data(Qt.UserRole)
        return get_extensions_manager().get(ext_id)

    def _on_item_selected(self, current, _previous):
        ext = self._selected_extension()
        if not ext:
            self.lbl_detail_name.setText("Kies een extensie...")
            self.lbl_detail_status.setText("")
            self.lbl_detail_desc.setText("")
            self.btn_edit.setEnabled(False)
            self.btn_delete.setEnabled(False)
            return
        self.lbl_detail_name.setText(ext.name)
        status = "✓ Ingeschakeld" if ext.enabled else "○ Uitgeschakeld"
        type_label = "(ingebouwd)" if ext.type == "builtin" else "(door u gemaakt)"
        self.lbl_detail_status.setText(
            f"{status}    •    {type_label}    •    Werkt op: {ext.url_pattern}"
        )
        self.lbl_detail_status.setStyleSheet(
            "color:#90c090;" if ext.enabled else "color:#909090;"
        )
        self.lbl_detail_desc.setText(ext.description)
        # Knoppen
        self.btn_toggle.setText("✕  Uitschakelen" if ext.enabled else "✓  Inschakelen")
        if ext.enabled:
            self.btn_toggle.setStyleSheet(
                "QPushButton { background:#8a2a2a; color:#fff; "
                "border:3px solid #aa4a4a; border-radius:6px; padding:6px 16px; }"
                "QPushButton:hover { background:#9a3a3a; }"
            )
        else:
            self.btn_toggle.setStyleSheet(
                "QPushButton { background:#2a8a2a; color:#fff; "
                "border:3px solid #4aaa4a; border-radius:6px; padding:6px 16px; }"
                "QPushButton:hover { background:#3a9a3a; }"
            )
        self.btn_edit.setEnabled(ext.type == "user")
        self.btn_delete.setEnabled(ext.type == "user")

    def _on_item_clicked(self, item):
        # Niets bijzonders, _on_item_selected doet het werk
        pass

    def _on_toggle(self):
        ext = self._selected_extension()
        if not ext:
            return
        mgr = get_extensions_manager()
        mgr.set_enabled(ext.id, not ext.enabled)
        self.extensions_changed.emit()
        # Update lijst-label
        cur_idx = self.lst.currentRow()
        self._populate()
        if 0 <= cur_idx < self.lst.count():
            self.lst.setCurrentRow(cur_idx)

    def _on_new(self):
        dlg = _ExtensionEditorDialog(parent=self)
        if dlg.exec() == QDialog.Accepted and dlg.saved:
            self.extensions_changed.emit()
            cur_idx = self.lst.currentRow()
            self._populate()
            if 0 <= cur_idx < self.lst.count():
                self.lst.setCurrentRow(cur_idx)

    def _on_edit(self):
        ext = self._selected_extension()
        if not ext or ext.type != "user":
            return
        dlg = _ExtensionEditorDialog(ext=ext, parent=self)
        if dlg.exec() == QDialog.Accepted and dlg.saved:
            self.extensions_changed.emit()
            self._populate()

    def _on_delete(self):
        ext = self._selected_extension()
        if not ext or ext.type != "user":
            return
        dlg = YesNoDialog(
            question=f'Weet u zeker dat u "{ext.name}" wilt verwijderen?',
            title="Extensie verwijderen?",
            yes_text="Ja, verwijderen",
            no_text="Nee, behouden",
            parent=self,
        )
        if dlg.exec() != QDialog.Accepted:
            return
        mgr = get_extensions_manager()
        if mgr.delete_user_extension(ext.id):
            self.extensions_changed.emit()
            self._populate()

    def _on_open_folder(self):
        import os, subprocess, sys
        path = get_extensions_dir()
        try:
            if os.name == "nt":
                os.startfile(str(path))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(path)])
            else:
                subprocess.Popen(["xdg-open", str(path)])
        except Exception as e:
            QMessageBox.warning(self, "Kon map niet openen",
                                f"De map staat hier:\n{path}")

    def _on_help(self):
        help_text = """
<h2>Hoe maak ik mijn eigen extensie?</h2>

<p><b>Wat is een extensie?</b><br>
Een klein stukje code (CSS of JavaScript) dat in elke webpagina wordt
gevoegd om hem aan te passen.</p>

<p><b>Twee soorten:</b></p>
<ul>
  <li><b>CSS-extensie</b> — kleuren, lay-out, lettergrootte aanpassen.
      Eenvoudiger te beginnen.</li>
  <li><b>JavaScript-extensie</b> — gedrag aanpassen, knoppen toevoegen,
      elementen verbergen of veranderen.</li>
</ul>

<p><b>URL-patroon:</b><br>
Met <code>*</code> werkt de extensie overal. Met bijvoorbeeld
<code>*wikipedia.org*</code> alleen op Wikipedia-pagina's.</p>

<p><b>Voorbeeld 1 — Maak alle Wikipedia-tekst groot (CSS):</b></p>
<pre style="background:#2a2a2a;padding:8px;">
/* ==UserStyle==
@name Wikipedia groot
@match *wikipedia.org*
==/UserStyle== */

body, p, li { font-size: 1.3em !important; }
</pre>

<p><b>Voorbeeld 2 — Verberg de zijbalk op nu.nl (JavaScript):</b></p>
<pre style="background:#2a2a2a;padding:8px;">
// ==UserScript==
// @name Geen zijbalk op nu.nl
// @match *nu.nl*
// ==/UserScript==

document.querySelectorAll('aside').forEach(function(el) {
    el.style.display = 'none';
});
</pre>

<p><b>Sites met kant-en-klare scripts (klik om te openen in DeskButler):</b></p>
<ul>
  <li><a href="https://greasyfork.org" style="color:#90c0ff;">
        <b>greasyfork.org</b></a> — duizenden JavaScript-extensies</li>
  <li><a href="https://userstyles.world" style="color:#90c0ff;">
        <b>userstyles.world</b></a> — duizenden CSS-extensies (donkere thema's
      voor specifieke sites, lay-out-tweaks)</li>
</ul>

<p>Kopieer een script vanaf zo'n site, plak het in de editor (groene knop
"Nieuwe extensie maken"), en geef het een naam.</p>
"""
        dlg = QDialog(self)
        dlg.setWindowTitle("Hulp bij extensies")
        dlg.resize(760, 640)
        apply_dialog_style(dlg)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 16, 20, 16)
        from PySide6.QtWidgets import QTextBrowser
        tb = QTextBrowser()
        tb.setFont(base_font())
        tb.setHtml(help_text)
        tb.setStyleSheet(
            "QTextBrowser { background:#1e1e1e; color:#e0e0e0; "
            "border:1px solid #3a3a3a; border-radius:6px; padding:8px; }"
        )
        # BELANGRIJK: laat anchors klikbaar zijn, open in DeskButler-browser
        tb.setOpenLinks(False)  # we handelen zelf af
        tb.setOpenExternalLinks(False)
        tb.anchorClicked.connect(self._open_link_in_deskbutler)
        layout.addWidget(tb, 1)

        btn = QPushButton("Sluiten")
        btn.setFont(base_font())
        btn.setMinimumHeight(48)
        btn.clicked.connect(dlg.accept)
        layout.addWidget(btn)

        apply_accessibility(dlg)
        dlg.exec()

    def _open_link_in_deskbutler(self, url):
        """
        Open een klikbare link uit de Hulp-dialoog in DeskButler's eigen
        browser. We zoeken de parent BrowserWindow (door de boom omhoog)
        en roepen open_url() aan. Als die niet wordt gevonden vallen we
        terug op de OS-standaardbrowser.
        """
        url_str = url.toString() if hasattr(url, "toString") else str(url)
        # Zoek BrowserWindow als parent
        parent = self.parent()
        while parent is not None:
            if hasattr(parent, "open_url"):
                try:
                    parent.open_url(url_str)
                    parent.show()
                    parent.raise_()
                    parent.activateWindow()
                    return
                except Exception as e:
                    print(f"[ext] open_url faalde: {e}")
                    break
            parent = parent.parent() if hasattr(parent, "parent") else None
        # Fallback: standaardbrowser van het OS
        try:
            from PySide6.QtGui import QDesktopServices
            QDesktopServices.openUrl(url if hasattr(url, "toString") else QUrl(url_str))
        except Exception as e:
            print(f"[ext] QDesktopServices faalde: {e}")


# ========================================================================
# UI: favorieten beheer-venster met mappen  (was: ui/favorites_window.py)
# ========================================================================

class _EditFavoriteDialog(QDialog):
    """Dialog om een favoriet (titel, URL, map) te bewerken."""

    def __init__(self, fav: dict, current_folder_id: str = None, parent=None):
        super().__init__(parent)
        self.fav = fav
        self.current_folder_id = current_folder_id
        self.new_folder_id = current_folder_id
        self.setWindowTitle("Favoriet bewerken")
        self.setMinimumSize(560, 320)
        apply_dialog_style(self)

        big = base_font()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title_lbl = QLabel("⭐ Favoriet bewerken")
        title_lbl.setFont(title_font())
        layout.addWidget(title_lbl)

        form = QFormLayout()
        form.setSpacing(10)

        self.txt_title = QLineEdit(fav.get("title", ""))
        self.txt_title.setFont(big)
        self.txt_title.setMinimumHeight(36)
        form.addRow(self._lbl("Titel:"), self.txt_title)

        self.txt_url = QLineEdit(fav.get("url", ""))
        self.txt_url.setFont(big)
        self.txt_url.setMinimumHeight(36)
        form.addRow(self._lbl("URL:"), self.txt_url)

        self.cmb_folder = QComboBox()
        self.cmb_folder.setFont(big)
        self.cmb_folder.setMinimumHeight(36)
        self.cmb_folder.addItem("(geen map)", None)
        mgr = get_favorites_manager()
        for folder in mgr.all_folders():
            self.cmb_folder.addItem(f"📁  {folder['name']}", folder["id"])
        # Selecteer huidige map
        for i in range(self.cmb_folder.count()):
            if self.cmb_folder.itemData(i) == current_folder_id:
                self.cmb_folder.setCurrentIndex(i)
                break
        form.addRow(self._lbl("Map:"), self.cmb_folder)

        layout.addLayout(form)

        btn_row = QHBoxLayout()
        btn_save = QPushButton("✓  Opslaan")
        btn_save.setFont(QFont("Segoe UI", big.pointSize(), QFont.Bold))
        btn_save.setMinimumHeight(48)
        btn_save.setMinimumWidth(140)
        btn_save.setStyleSheet(
            "QPushButton { background:#2a8a2a; color:#fff; "
            "border:3px solid #4aaa4a; border-radius:6px; padding:6px 16px; }"
            "QPushButton:hover { background:#3a9a3a; }"
        )
        btn_save.clicked.connect(self._on_save)
        btn_row.addWidget(btn_save)

        btn_cancel = QPushButton("✕  Annuleren")
        btn_cancel.setFont(big)
        btn_cancel.setMinimumHeight(48)
        btn_cancel.setMinimumWidth(140)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)
        btn_row.addStretch()

        layout.addLayout(btn_row)
        apply_accessibility(self)

    def _lbl(self, t):
        l = QLabel(t)
        l.setFont(base_font())
        return l

    def _on_save(self):
        title = self.txt_title.text().strip()
        url = self.txt_url.text().strip()
        if not title or not url:
            QMessageBox.warning(self, "Velden ontbreken",
                                "Titel en URL zijn beide verplicht.")
            return
        self.fav["title"] = title
        self.fav["url"] = url
        self.new_folder_id = self.cmb_folder.currentData()
        self.accept()


class FavoritesWindow(QMainWindow):
    """Beheer-venster voor favorieten."""

    favorite_opened = Signal(str)   # URL → open in browser

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Window)
        self.setWindowTitle("⭐ Favorieten")
        self.resize(900, 700)
        apply_dialog_style(self)
        self._setup_ui()
        self._populate()

    def _setup_ui(self):
        big = base_font()
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)

        title_lbl = QLabel("⭐ Favorieten")
        title_lbl.setFont(title_font())
        root.addWidget(title_lbl)

        info = QLabel(
            "Dubbelklik op een favoriet om hem te openen in een nieuwe tab. "
            "Rechter-muisklik op een map of favoriet voor meer opties."
        )
        info.setFont(big)
        info.setWordWrap(True)
        info.setStyleSheet("color:#c0c0c0; padding:4px;")
        root.addWidget(info)

        # Tree widget met mappen + favorieten
        self.tree = QTreeWidget()
        self.tree.setFont(big)
        self.tree.setHeaderLabels(["Naam", "URL"])
        self.tree.setColumnWidth(0, 360)
        self.tree.setRootIsDecorated(True)
        self.tree.setAlternatingRowColors(True)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._on_context_menu)
        self.tree.itemDoubleClicked.connect(self._on_double_click)
        self.tree.setStyleSheet(
            "QTreeWidget { background:#1e1e1e; border:1px solid #3a3a3a; "
            "border-radius:6px; padding:4px; }"
            "QTreeWidget::item { padding:6px; }"
            "QTreeWidget::item:selected { background:#2a8a2a; }"
            "QHeaderView::section { background:#2a2a2a; color:#fff; "
            "padding:6px; border:1px solid #3a3a3a; }"
        )
        root.addWidget(self.tree, 1)

        # Knoppen onderaan
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        btn_new_folder = QPushButton("📁  Nieuwe map")
        btn_new_folder.setFont(QFont("Segoe UI", big.pointSize(), QFont.Bold))
        btn_new_folder.setMinimumHeight(48)
        btn_new_folder.setMinimumWidth(180)
        btn_new_folder.setStyleSheet(
            "QPushButton { background:#2a8a2a; color:#fff; "
            "border:3px solid #4aaa4a; border-radius:6px; padding:6px 16px; }"
            "QPushButton:hover { background:#3a9a3a; }"
        )
        btn_new_folder.clicked.connect(self._on_new_folder)
        btn_row.addWidget(btn_new_folder)

        self.btn_open = QPushButton("🌐  Openen")
        self.btn_open.setFont(big)
        self.btn_open.setMinimumHeight(48)
        self.btn_open.setMinimumWidth(140)
        self.btn_open.clicked.connect(self._on_open_selected)
        btn_row.addWidget(self.btn_open)

        self.btn_edit = QPushButton("✏️  Bewerken")
        self.btn_edit.setFont(big)
        self.btn_edit.setMinimumHeight(48)
        self.btn_edit.setMinimumWidth(140)
        self.btn_edit.clicked.connect(self._on_edit_selected)
        btn_row.addWidget(self.btn_edit)

        self.btn_delete = QPushButton("🗑️  Verwijderen")
        self.btn_delete.setFont(big)
        self.btn_delete.setMinimumHeight(48)
        self.btn_delete.setMinimumWidth(160)
        self.btn_delete.clicked.connect(self._on_delete_selected)
        btn_row.addWidget(self.btn_delete)

        btn_row.addStretch()

        btn_close = QPushButton("Sluiten")
        btn_close.setFont(big)
        btn_close.setMinimumHeight(48)
        btn_close.setMinimumWidth(140)
        btn_close.clicked.connect(self.close)
        btn_row.addWidget(btn_close)

        root.addLayout(btn_row)
        apply_accessibility(self)

    def _populate(self):
        """Vul de tree opnieuw met alle mappen en favorieten."""
        self.tree.clear()
        mgr = get_favorites_manager()

        # Mappen eerst
        for folder in mgr.all_folders():
            folder_item = QTreeWidgetItem(self.tree)
            count = len(folder["favorites"])
            folder_item.setText(0, f"📁  {folder['name']}  ({count})")
            folder_item.setText(1, "")
            folder_item.setData(0, Qt.UserRole, {
                "type": "folder", "id": folder["id"],
            })
            # Maak vetgedrukt
            f = folder_item.font(0)
            f.setBold(True)
            folder_item.setFont(0, f)
            # Favorieten in deze map
            for fav in folder["favorites"]:
                fav_item = QTreeWidgetItem(folder_item)
                fav_item.setText(0, f"⭐ {fav['title']}")
                fav_item.setText(1, fav["url"])
                fav_item.setToolTip(1, fav["url"])
                fav_item.setData(0, Qt.UserRole, {
                    "type": "favorite", "id": fav["id"],
                    "folder_id": folder["id"],
                })
            folder_item.setExpanded(True)

        # Root-favorieten daarna
        for fav in mgr.root_favorites():
            fav_item = QTreeWidgetItem(self.tree)
            fav_item.setText(0, f"⭐ {fav['title']}")
            fav_item.setText(1, fav["url"])
            fav_item.setToolTip(1, fav["url"])
            fav_item.setData(0, Qt.UserRole, {
                "type": "favorite", "id": fav["id"], "folder_id": None,
            })

        # Update knoppen-status
        self._update_buttons()
        self.tree.currentItemChanged.connect(lambda *_: self._update_buttons())

    def _update_buttons(self):
        item = self.tree.currentItem()
        is_fav = (item is not None and
                  item.data(0, Qt.UserRole) and
                  item.data(0, Qt.UserRole).get("type") == "favorite")
        self.btn_open.setEnabled(is_fav)
        self.btn_edit.setEnabled(is_fav)
        self.btn_delete.setEnabled(item is not None)

    # ------------------------------------------------------------------
    # Acties
    # ------------------------------------------------------------------
    def _selected_data(self) -> dict:
        item = self.tree.currentItem()
        if not item:
            return {}
        return item.data(0, Qt.UserRole) or {}

    def _on_double_click(self, item, _col):
        data = item.data(0, Qt.UserRole) or {}
        if data.get("type") == "favorite":
            fav = get_favorites_manager().find(data["id"])
            if fav:
                self.favorite_opened.emit(fav["url"])

    def _on_open_selected(self):
        data = self._selected_data()
        if data.get("type") != "favorite":
            return
        fav = get_favorites_manager().find(data["id"])
        if fav:
            self.favorite_opened.emit(fav["url"])

    def _on_edit_selected(self):
        data = self._selected_data()
        if data.get("type") != "favorite":
            return
        mgr = get_favorites_manager()
        fav = mgr.find(data["id"])
        if not fav:
            return
        dlg = _EditFavoriteDialog(
            fav=dict(fav),  # kopie zodat we niet inplace muteren
            current_folder_id=data.get("folder_id"),
            parent=self,
        )
        if dlg.exec() != QDialog.Accepted:
            return
        # Bijwerken
        mgr.update(data["id"], title=dlg.fav["title"], url=dlg.fav["url"])
        # Map verplaatsen indien gewijzigd
        if dlg.new_folder_id != data.get("folder_id"):
            mgr.move_to_folder(data["id"], dlg.new_folder_id)
        self._populate()

    def _on_delete_selected(self):
        data = self._selected_data()
        if not data:
            return
        if data.get("type") == "folder":
            ask = YesNoDialog(
                question=(
                    "Wilt u deze map verwijderen?\n\n"
                    "De favorieten in deze map worden niet verwijderd — "
                    "ze gaan naar het hoofdniveau (zonder map)."
                ),
                title="Map verwijderen?",
                yes_text="Ja, verwijderen",
                no_text="Nee, behouden",
                parent=self,
            )
            if ask.exec() != QDialog.Accepted:
                return
            get_favorites_manager().remove_folder(data["id"], move_to_root=True)
        else:
            ask = YesNoDialog(
                question="Wilt u deze favoriet verwijderen?",
                title="Favoriet verwijderen?",
                yes_text="Ja, verwijderen",
                no_text="Nee, behouden",
                parent=self,
            )
            if ask.exec() != QDialog.Accepted:
                return
            get_favorites_manager().remove(data["id"])
        self._populate()

    def _on_new_folder(self):
        name, ok = QInputDialog.getText(
            self, "Nieuwe map", "Naam voor de nieuwe map:",
        )
        if not ok or not name.strip():
            return
        get_favorites_manager().add_folder(name.strip())
        self._populate()

    def _on_context_menu(self, pos):
        item = self.tree.itemAt(pos)
        if not item:
            return
        self.tree.setCurrentItem(item)
        data = item.data(0, Qt.UserRole) or {}
        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu { background:#2a2a2a; color:#fff; "
            "border:1px solid #555; padding:6px; }"
            "QMenu::item { padding:8px 20px; }"
            "QMenu::item:selected { background:#444; }"
        )
        if data.get("type") == "favorite":
            menu.addAction("🌐  Openen", self._on_open_selected)
            menu.addAction("✏️  Bewerken", self._on_edit_selected)
            menu.addSeparator()
            menu.addAction("🗑️  Verwijderen", self._on_delete_selected)
        elif data.get("type") == "folder":
            menu.addAction("📝  Naam wijzigen", self._on_rename_folder)
            menu.addSeparator()
            menu.addAction("🗑️  Map verwijderen", self._on_delete_selected)
        menu.exec(self.tree.mapToGlobal(pos))

    def _on_rename_folder(self):
        data = self._selected_data()
        if data.get("type") != "folder":
            return
        mgr = get_favorites_manager()
        # Zoek huidige naam
        current_name = ""
        for folder in mgr.all_folders():
            if folder["id"] == data["id"]:
                current_name = folder["name"]
                break
        new_name, ok = QInputDialog.getText(
            self, "Naam wijzigen", "Nieuwe naam:", text=current_name,
        )
        if not ok or not new_name.strip():
            return
        mgr.rename_folder(data["id"], new_name.strip())
        self._populate()


# ========================================================================
# UI: afbeeldingspikker venster  (was: ui/image_picker_window.py)
# ========================================================================

# Min. afmeting om favicons/tracking-pixels te negeren
MIN_IMG_SIZE = 80   # pixels


def _make_placeholder_pixmap(size: int = 200, text: str = "...") -> QPixmap:
    """Maak een grijze placeholder met '...' tekst voor nog-niet-geladen afbeeldingen."""
    pm = QPixmap(size, size)
    pm.fill(QColor("#2a2a2a"))
    painter = QPainter(pm)
    painter.setPen(QPen(QColor("#666"), 2))
    painter.drawRect(2, 2, size - 4, size - 4)
    painter.setPen(QColor("#888"))
    f = QFont("Segoe UI", 20)
    painter.setFont(f)
    painter.drawText(pm.rect(), Qt.AlignCenter, text)
    painter.end()
    return pm


class ImagePickerWindow(QMainWindow):
    """Hoofdvenster voor de afbeeldingspikker."""

    def __init__(self, images: list, parent=None):
        """
        images: lijst van dicts {src, width, height, alt} van de browser
        """
        # Maak het een echt los venster (Qt.Window) zodat het niet
        # als kind onzichtbaar blijft achter de browser
        super().__init__(parent, Qt.Window)
        self.setWindowTitle("🖼️ Afbeeldingspikker")
        self.resize(1000, 760)
        apply_dialog_style(self)

        # Filter te kleine afbeeldingen weg (favicons, tracking-pixels)
        # Behoud afbeeldingen waarvan de afmetingen onbekend zijn
        self.images = [
            img for img in images
            if (img.get("width", 0) == 0 and img.get("height", 0) == 0)
            or (img.get("width", 0) >= MIN_IMG_SIZE
                and img.get("height", 0) >= MIN_IMG_SIZE)
        ]
        print(f"[picker] na filter: {len(self.images)} van {len(images)} "
              f"afbeeldingen overgebleven (min size {MIN_IMG_SIZE}px)")

        self._setup_ui()
        if self.images:
            self._start_loading()
        else:
            self.lbl_status.setText(
                f"⚠ {len(images)} afbeeldingen gevonden, maar alle waren te klein "
                f"(< {MIN_IMG_SIZE}×{MIN_IMG_SIZE} pixels). "
                "Het zijn vermoedelijk icoontjes of tracking-pixels."
            )
            self.lbl_status.setStyleSheet("color:#cc9966; padding:4px;")

    def _setup_ui(self):
        big = base_font()
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)

        # Titel
        title_lbl = QLabel(
            f"🖼️ Afbeeldingen op deze pagina  ({len(self.images)} gevonden)"
        )
        title_lbl.setFont(title_font())
        root.addWidget(title_lbl)

        # Uitleg
        info = QLabel(
            "Dubbelklik op een afbeelding om hem direct op te slaan in de "
            "downloads-map. Of selecteer een afbeelding en klik op "
            "'Opslaan als...' om hem een eigen plek te geven."
        )
        info.setFont(big)
        info.setWordWrap(True)
        info.setStyleSheet("color:#c0c0c0; padding:4px;")
        root.addWidget(info)

        # Status-tekst boven de lijst
        self.lbl_status = QLabel("Thumbnails laden...")
        self.lbl_status.setFont(big)
        self.lbl_status.setStyleSheet("color:#90c0ff; padding:4px;")
        root.addWidget(self.lbl_status)

        # Voortgangsbalk
        self.bar = QProgressBar()
        self.bar.setMinimum(0)
        self.bar.setMaximum(max(1, len(self.images)))
        self.bar.setValue(0)
        self.bar.setMinimumHeight(22)
        self.bar.setStyleSheet(
            "QProgressBar { background:#1e1e1e; border:1px solid #555; "
            "border-radius:4px; text-align:center; color:#fff; }"
            "QProgressBar::chunk { background:#2a8a2a; border-radius:3px; }"
        )
        root.addWidget(self.bar)

        # Grid van thumbnails
        self.lst = QListWidget()
        self.lst.setViewMode(QListWidget.IconMode)
        self.lst.setIconSize(QSize(200, 200))
        self.lst.setResizeMode(QListWidget.Adjust)
        self.lst.setSpacing(10)
        self.lst.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.lst.setSelectionMode(QAbstractItemView.SingleSelection)
        self.lst.setStyleSheet(
            "QListWidget { background:#1e1e1e; border:1px solid #3a3a3a; "
            "border-radius:6px; padding:6px; }"
            "QListWidget::item { background:#2a2a2a; border:2px solid #3a3a3a; "
            "border-radius:6px; padding:4px; }"
            "QListWidget::item:selected { border:3px solid #2a8a2a; }"
        )
        self.lst.itemDoubleClicked.connect(self._save_direct)
        root.addWidget(self.lst, 1)

        # Vul de lijst eerst met placeholders, één per gevonden afbeelding
        ph = _make_placeholder_pixmap(200)
        for img in self.images:
            label_txt = ""
            if img.get("width") and img.get("height"):
                label_txt = f"{img['width']}×{img['height']}"
            item = QListWidgetItem(QIcon(ph), label_txt)
            item.setData(Qt.UserRole, img.get("src"))
            item.setData(Qt.UserRole + 1, False)  # loaded-flag
            item.setSizeHint(QSize(220, 240))
            self.lst.addItem(item)

        # Knoppen onderaan
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.btn_save_as = QPushButton("💾  Opslaan als...")
        self.btn_save_as.setFont(QFont("Segoe UI", big.pointSize(), QFont.Bold))
        self.btn_save_as.setMinimumHeight(48)
        self.btn_save_as.setMinimumWidth(200)
        self.btn_save_as.setStyleSheet(
            "QPushButton { background:#2a8a2a; color:#fff; "
            "border:3px solid #4aaa4a; border-radius:6px; padding:6px 16px; }"
            "QPushButton:hover { background:#3a9a3a; }"
            "QPushButton:disabled { background:#444; color:#888; border-color:#555; }"
        )
        self.btn_save_as.clicked.connect(self._save_as)
        btn_row.addWidget(self.btn_save_as)

        self.btn_save_direct = QPushButton("⚡  Snel opslaan in downloads")
        self.btn_save_direct.setFont(big)
        self.btn_save_direct.setMinimumHeight(48)
        self.btn_save_direct.setMinimumWidth(240)
        self.btn_save_direct.clicked.connect(self._save_direct_from_button)
        btn_row.addWidget(self.btn_save_direct)

        btn_row.addStretch()

        btn_close = QPushButton("Sluiten")
        btn_close.setFont(big)
        btn_close.setMinimumHeight(48)
        btn_close.setMinimumWidth(140)
        btn_close.clicked.connect(self.close)
        btn_row.addWidget(btn_close)

        root.addLayout(btn_row)

        apply_accessibility(self)

    def _start_loading(self):
        """Start de async thumbnail-loader thread."""
        self._loader = ThumbnailLoaderThread(self.images, parent=self)
        self._loader.thumbnail_ready.connect(self._on_thumbnail_ready)
        self._loader.thumbnail_failed.connect(self._on_thumbnail_failed)
        self._loader.progress.connect(self._on_progress)
        self._loader.finished_loading.connect(self._on_finished)
        self._loader.start()

    def _on_thumbnail_ready(self, idx: int, data: bytes):
        """Vervang de placeholder voor afbeelding idx met de echte thumbnail."""
        if idx < 0 or idx >= self.lst.count():
            return
        pm = QPixmap()
        if not pm.loadFromData(data) or pm.isNull():
            self._on_thumbnail_failed(idx, "kan niet decoderen")
            return
        # Schaal naar passend formaat voor het rooster
        if pm.width() > 400 or pm.height() > 400:
            pm = pm.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        item = self.lst.item(idx)
        item.setIcon(QIcon(pm))
        item.setData(Qt.UserRole + 1, True)  # loaded
        # Update label met afmetingen als die nog niet bekend waren
        if not item.text():
            item.setText(f"{pm.width()}×{pm.height()}")

    def _on_thumbnail_failed(self, idx: int, error: str):
        """Markeer een afbeelding als niet-laadbaar (rood placeholder)."""
        if idx < 0 or idx >= self.lst.count():
            return
        pm = QPixmap(200, 200)
        pm.fill(QColor("#3a1a1a"))
        painter = QPainter(pm)
        painter.setPen(QPen(QColor("#aa4444"), 2))
        painter.drawRect(2, 2, 196, 196)
        painter.setPen(QColor("#cc8888"))
        painter.setFont(QFont("Segoe UI", 14))
        painter.drawText(pm.rect(), Qt.AlignCenter, "✕")
        painter.end()
        item = self.lst.item(idx)
        item.setIcon(QIcon(pm))
        item.setText("(niet laadbaar)")

    def _on_progress(self, current: int, total: int):
        self.bar.setValue(current)
        self.lbl_status.setText(f"Thumbnails laden: {current} van {total}...")

    def _on_finished(self):
        loaded = sum(
            1 for i in range(self.lst.count())
            if self.lst.item(i).data(Qt.UserRole + 1)
        )
        self.lbl_status.setText(
            f"✅ Klaar — {loaded} afbeeldingen ingeladen. "
            "Dubbelklik om op te slaan."
        )
        self.lbl_status.setStyleSheet("color:#90c090; padding:4px;")

    # ------------------------------------------------------------------
    # Opslaan
    # ------------------------------------------------------------------
    def _selected_item(self) -> QListWidgetItem:
        return self.lst.currentItem()

    def _save_direct_from_button(self):
        item = self._selected_item()
        if item:
            self._save_direct(item)
        else:
            QMessageBox.information(
                self, "Geen selectie",
                "Klik eerst op een afbeelding om hem te selecteren."
            )

    def _save_direct(self, item: QListWidgetItem):
        """Sla de afbeelding direct op in de downloads-map (geen dialog)."""
        url = item.data(Qt.UserRole)
        if not url:
            return
        self.lbl_status.setText("⏳ Bezig met opslaan...")
        self.lbl_status.setStyleSheet("color:#90c0ff; padding:4px;")
        QApplication.processEvents()

        import urllib.request
        # Eerst extensie bepalen op basis van Content-Type
        ext = ".jpg"
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0",
            })
            with urllib.request.urlopen(req, timeout=10) as r:
                ct = r.headers.get("Content-Type", "")
                ext = get_img_extension(url, ct)
                data = r.read(30 * 1024 * 1024)
        except Exception as e:
            self.lbl_status.setText(f"❌ Opslaan mislukt: {e}")
            self.lbl_status.setStyleSheet("color:#cc7777; padding:4px;")
            return

        # Zoek unieke naam
        dl_dir = get_downloads_dir()
        base = safe_image_filename(url, ext)
        target = dl_dir / base
        counter = 1
        while target.exists():
            stem = Path(base).stem
            target = dl_dir / f"{stem}_{counter}{ext}"
            counter += 1

        try:
            with open(target, "wb") as f:
                f.write(data)
        except Exception as e:
            self.lbl_status.setText(f"❌ Schrijven mislukt: {e}")
            self.lbl_status.setStyleSheet("color:#cc7777; padding:4px;")
            return

        self.lbl_status.setText(f"✅ Opgeslagen: {target.name}")
        self.lbl_status.setStyleSheet("color:#90c090; padding:4px;")

    def _save_as(self):
        """Opslaan-als via QFileDialog."""
        item = self._selected_item()
        if not item:
            QMessageBox.information(
                self, "Geen selectie",
                "Klik eerst op een afbeelding om hem te selecteren."
            )
            return
        url = item.data(Qt.UserRole)
        if not url:
            return

        # BELANGRIJK (Roger's truc): eerst data ophalen voordat we de
        # QFileDialog openen — anders blokkeert de dialoog de event-loop
        # en raakt de HTTP-verbinding time-out.
        self.lbl_status.setText("⏳ Downloaden...")
        QApplication.processEvents()
        data = fetch_image_data(url)
        if not data:
            self.lbl_status.setText("❌ Download mislukt")
            return

        # Bepaal extensie
        ext = get_img_extension(url, "")
        default_name = safe_image_filename(url, ext)
        default_path = str(get_downloads_dir() / default_name)

        path, _ = QFileDialog.getSaveFileName(
            self, "Afbeelding opslaan als...", default_path,
            f"Afbeeldingen (*{ext});;Alle bestanden (*)"
        )
        if not path:
            self.lbl_status.setText("Opslaan geannuleerd")
            return

        try:
            with open(path, "wb") as f:
                f.write(data)
            self.lbl_status.setText(f"✅ Opgeslagen als: {os.path.basename(path)}")
            self.lbl_status.setStyleSheet("color:#90c090; padding:4px;")
        except Exception as e:
            self.lbl_status.setText(f"❌ Schrijven mislukt: {e}")
            self.lbl_status.setStyleSheet("color:#cc7777; padding:4px;")

    def closeEvent(self, event):
        """Stop de thread netjes bij sluiten."""
        if hasattr(self, "_loader") and self._loader.isRunning():
            self._loader.cancel()
            self._loader.wait(2000)
        super().closeEvent(event)


# ========================================================================
# UI: video/audio download voortgang + tools-installer  (was: ui/download_dialog.py)
# ========================================================================

class ToolsInstallDialog(QDialog):
    """
    Toont voortgang van auto-install van yt-dlp + ffmpeg bij eerste
    gebruik van de download-functie.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hulpprogramma's downloaden")
        self.setMinimumSize(560, 280)
        self.setModal(True)
        apply_dialog_style(self)

        big = base_font()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title = QLabel("⬇️  Hulpprogramma's installeren")
        title.setFont(title_font())
        layout.addWidget(title)

        info = QLabel(
            "Om video's en muziek te kunnen downloaden, heb ik twee kleine "
            "hulpprogramma's nodig: yt-dlp en ffmpeg. Ze worden in een "
            "submap 'tools' bij DeskButler gezet.\n\n"
            "Eenmalige download van ongeveer 95 MB (yt-dlp 15 MB + ffmpeg 80 MB)."
        )
        info.setFont(big)
        info.setWordWrap(True)
        info.setStyleSheet(
            "background:#2a2a2a; padding:14px; border-radius:6px; color:#d0d0d0;"
        )
        layout.addWidget(info)

        self.lbl_status = QLabel("Bezig met voorbereiden...")
        self.lbl_status.setFont(big)
        self.lbl_status.setStyleSheet("color:#90c0ff; padding:4px;")
        self.lbl_status.setWordWrap(True)
        layout.addWidget(self.lbl_status)

        self.bar = QProgressBar()
        self.bar.setMinimum(0)
        self.bar.setMaximum(100)
        self.bar.setValue(0)
        self.bar.setMinimumHeight(28)
        self.bar.setFont(big)
        self.bar.setStyleSheet(
            "QProgressBar { background:#1e1e1e; border:1px solid #444; "
            "border-radius:6px; text-align:center; color:#fff; }"
            "QProgressBar::chunk { background:#2a8a2a; border-radius:5px; }"
        )
        layout.addWidget(self.bar)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_cancel = QPushButton("✕  Annuleren")
        self.btn_cancel.setFont(QFont("Segoe UI", big.pointSize(), QFont.Bold))
        self.btn_cancel.setMinimumHeight(48)
        self.btn_cancel.setMinimumWidth(160)
        self.btn_cancel.setStyleSheet(
            "QPushButton { background:#8a2a2a; color:#fff; "
            "border:3px solid #aa4a4a; border-radius:6px; padding:6px 16px; }"
            "QPushButton:hover { background:#9a3a3a; }"
        )
        self.btn_cancel.clicked.connect(self._on_cancel)
        btn_row.addWidget(self.btn_cancel)
        layout.addLayout(btn_row)

        self._thread = None
        self.success = False
        apply_accessibility(self)

    def start_install(self):
        """Start de install-thread (parent moet self zijn voor cleanup)."""
        print("[install_dlg] start_install aangeroepen")
        self._thread = ToolsInstallThread(parent=self)
        self._thread.progress.connect(self._on_progress)
        self._thread.finished_install.connect(self._on_finished)
        self._thread.start()

    def _on_progress(self, status: str, pct: int):
        print(f"[install_dlg] progress: {pct}% — {status}")
        self.lbl_status.setText(status)
        self.bar.setValue(pct)

    def _on_finished(self, ok: bool, error: str):
        print(f"[install_dlg] finished: ok={ok} error={error!r}")
        if ok:
            self.success = True
            self.lbl_status.setText("✅ Klaar! De hulpprogramma's zijn geïnstalleerd.")
            self.bar.setValue(100)
            self.btn_cancel.setText("Sluiten")
            self.btn_cancel.setStyleSheet(
                "QPushButton { background:#2a8a2a; color:#fff; "
                "border:3px solid #4aaa4a; border-radius:6px; padding:6px 16px; }"
                "QPushButton:hover { background:#3a9a3a; }"
            )
            try:
                self.btn_cancel.clicked.disconnect()
            except (RuntimeError, TypeError):
                pass
            self.btn_cancel.clicked.connect(self.accept)
        else:
            QMessageBox.warning(
                self, "Installatie mislukt",
                f"De installatie is mislukt:\n\n{error}\n\n"
                "Controleer uw internetverbinding en probeer het opnieuw."
            )
            self.reject()

    def _on_cancel(self):
        if self._thread and self._thread.isRunning():
            self._thread.cancel()
            self._thread.wait(2000)
        self.reject()


class VideoDownloadDialog(QDialog):
    """
    Toont voortgang van een video/audio download.
    """

    def __init__(self, url: str, output_path: str, mode: str = "mp4",
                 parent=None):
        super().__init__(parent)
        self.url = url
        self.output_path = output_path
        self.mode = mode
        self.setWindowTitle(
            "Video downloaden" if mode == "mp4" else "Audio downloaden"
        )
        self.setMinimumSize(560, 240)
        self.setModal(False)
        apply_dialog_style(self)

        big = base_font()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        icon_emoji = "🎬" if mode == "mp4" else "🎵"
        title = QLabel(
            f"{icon_emoji}  {'Video' if mode == 'mp4' else 'Audio'} downloaden"
        )
        title.setFont(title_font())
        layout.addWidget(title)

        # Bestandsnaam tonen
        from pathlib import Path
        name_label = QLabel(f"Doel: {Path(output_path).name}")
        name_label.setFont(big)
        name_label.setStyleSheet("color:#c0c0c0; padding:4px;")
        name_label.setWordWrap(True)
        layout.addWidget(name_label)

        self.lbl_status = QLabel("Verbinding maken...")
        self.lbl_status.setFont(big)
        self.lbl_status.setStyleSheet("color:#90c0ff; padding:4px;")
        self.lbl_status.setWordWrap(True)
        layout.addWidget(self.lbl_status)

        self.bar = QProgressBar()
        self.bar.setMinimum(0)
        self.bar.setMaximum(100)
        self.bar.setValue(0)
        self.bar.setMinimumHeight(28)
        self.bar.setFont(big)
        self.bar.setStyleSheet(
            "QProgressBar { background:#1e1e1e; border:1px solid #444; "
            "border-radius:6px; text-align:center; color:#fff; }"
            "QProgressBar::chunk { background:#2a8a2a; border-radius:5px; }"
        )
        layout.addWidget(self.bar)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_cancel = QPushButton("✕  Annuleren")
        self.btn_cancel.setFont(QFont("Segoe UI", big.pointSize(), QFont.Bold))
        self.btn_cancel.setMinimumHeight(48)
        self.btn_cancel.setMinimumWidth(160)
        self.btn_cancel.setStyleSheet(
            "QPushButton { background:#8a2a2a; color:#fff; "
            "border:3px solid #aa4a4a; border-radius:6px; padding:6px 16px; }"
            "QPushButton:hover { background:#9a3a3a; }"
        )
        self.btn_cancel.clicked.connect(self._on_cancel)
        btn_row.addWidget(self.btn_cancel)
        layout.addLayout(btn_row)

        self._worker = None
        self.success_path = None
        apply_accessibility(self)

    def start_download(self):
        """Start de download-worker."""
        self._worker = VideoDownloadWorker(
            self.url, self.output_path, self.mode, parent=self,
        )
        self._worker.status_update.connect(self.lbl_status.setText)
        self._worker.progress_percent.connect(self.bar.setValue)
        self._worker.finished_dl.connect(self._on_finished)
        self._worker.start()

    def _on_finished(self, ok: bool, msg: str):
        if ok:
            self.success_path = msg
            self.lbl_status.setText(f"✅ Klaar! Opgeslagen als {msg}")
            self.bar.setValue(100)
            self.btn_cancel.setText("Sluiten")
            self.btn_cancel.setStyleSheet(
                "QPushButton { background:#2a8a2a; color:#fff; "
                "border:3px solid #4aaa4a; border-radius:6px; padding:6px 16px; }"
                "QPushButton:hover { background:#3a9a3a; }"
            )
            self.btn_cancel.clicked.disconnect()
            self.btn_cancel.clicked.connect(self.accept)
        else:
            QMessageBox.warning(
                self, "Download mislukt",
                f"De download is mislukt:\n\n{msg}\n\n"
                "Controleer of de pagina een video bevat en probeer opnieuw."
            )
            self.reject()

    def _on_cancel(self):
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait(3000)
        self.reject()


# ========================================================================
# UI: donatie venster  (was: ui/donation_dialog.py)
# ========================================================================

PAYPAL_URL = "https://paypal.me/roger076"


class DonationDialog(QDialog):
    """Vriendelijk donatie-venster."""

    # Signaal voor in-app browser opening (verbinden in main.py)
    open_in_browser = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Steun DeskButler")
        self.setMinimumSize(560, 420)

        apply_dialog_style(self)
        big = base_font()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title = QLabel("☕  Een kop koffie waard?")
        title.setFont(title_font())
        layout.addWidget(title)

        body = QLabel(
            "DeskButler is helemaal gratis en blijft dat ook.\n\n"
            "Vindt u de app nuttig? Een kleine bijdrage helpt mij om door te "
            "blijven ontwikkelen en nieuwe functies toe te voegen. Elke gift "
            "wordt enorm gewaardeerd — maar er is geen verplichting.\n\n"
            "Doneren kan veilig en eenvoudig via PayPal. U kunt zelf het bedrag "
            "kiezen, helemaal aan u."
        )
        body.setFont(big)
        body.setWordWrap(True)
        body.setStyleSheet(
            "background:#2a2a2a; padding:18px; border-radius:8px; color:#e0e0e0;"
        )
        layout.addWidget(body)

        # Grote, prominente donatie-knop
        btn_donate = QPushButton("💝  Doneer via PayPal")
        btn_donate.setFont(QFont("Segoe UI", base_font().pointSize() + 2, QFont.Bold))
        btn_donate.setMinimumHeight(64)
        btn_donate.setObjectName("primary")
        btn_donate.setStyleSheet(
            "QPushButton#primary { background:#0070ba; color:#fff; "
            "border:3px solid #003087; border-radius:8px; padding:12px 24px; "
            "font-weight: bold; }"
            "QPushButton#primary:hover { background:#005ea6; }"
        )
        btn_donate.clicked.connect(self._open_paypal)
        layout.addWidget(btn_donate)

        # Kopieer link
        copy_row = QHBoxLayout()
        lbl_link = QLabel(f"Of kopieer de link:  {PAYPAL_URL}")
        lbl_link.setFont(big)
        lbl_link.setStyleSheet("color: #a0a0a0;")
        copy_row.addWidget(lbl_link, 1)

        btn_copy = QPushButton("📋  Kopiëren")
        btn_copy.setFont(big)
        btn_copy.setMinimumHeight(40)
        btn_copy.clicked.connect(self._copy_link)
        copy_row.addWidget(btn_copy)
        layout.addLayout(copy_row)

        # Sluiten
        btn_close = QPushButton("Sluiten")
        btn_close.setFont(big)
        btn_close.setMinimumHeight(48)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

        apply_accessibility(self)

    def _open_paypal(self):
        # Emit signal — main.py opent dit in de in-app browser
        self.open_in_browser.emit(PAYPAL_URL)
        self.accept()

    def _copy_link(self):
        QApplication.clipboard().setText(PAYPAL_URL)
        self.setWindowTitle("Steun DeskButler — Link gekopieerd!")


# ========================================================================
# UI: contact-formulier (service e-mail)  (was: ui/contact_dialog.py)
# ========================================================================

SERVICE_EMAIL = "service@dravenlock.nl"


SUBJECTS = [
    ("Vraag",       "Vraag over DeskButler"),
    ("Klacht",      "Klacht over DeskButler"),
    ("Idee",        "Idee voor DeskButler"),
    ("Bug / fout",  "Foutmelding in DeskButler"),
    ("Anders",      "Bericht over DeskButler"),
]


class _SmtpSendWorker(QThread):
    """
    Verzendt in achtergrond-thread zodat UI responsive blijft.
    Emit finished_result(ok: bool, error_msg: str).
    """
    finished_result = Signal(bool, str)

    def __init__(self, subject: str, body: str):
        super().__init__()
        self.subject = subject
        self.body = body

    def run(self):
        # 'pass' regels staan er zodat het try-blok niet leeg wordt
        # nadat de single-file build de interne imports verwijdert.
        try:
            pass
        except Exception as e:
            self.finished_result.emit(False, f"Kon mail-modules niet laden: {e}")
            return

        try:
            accounts = load_accounts()
        except Exception as e:
            self.finished_result.emit(False, f"Kon accounts niet ophalen: {e}")
            return

        if not accounts:
            self.finished_result.emit(False, "Geen e-mailaccount ingesteld")
            return

        last_error = "Geen werkend account gevonden"
        for acc in accounts:
            host = acc.get("smtp_host", "")
            port = int(acc.get("smtp_port", 0))
            email = acc.get("email", "")
            password = acc.get("password", "")
            if not host or not port or not email:
                last_error = f"Account {email} mist SMTP-instellingen"
                continue
            try:
                use_starttls = (port == 587)
                client = SMTPClient(
                    host=host, port=port,
                    username=email, password=password,
                    use_starttls=use_starttls,
                )
                client.send(
                    from_addr=email,
                    to_addrs=[SERVICE_EMAIL],
                    subject=self.subject,
                    body=self.body,
                )
                self.finished_result.emit(True, email)
                return
            except Exception as e:
                last_error = f"{email}: {type(e).__name__}: {e}"
                print(f"[contact] SMTP via {email} faalde: {e}")
                continue

        self.finished_result.emit(False, last_error)


class ContactDialog(QDialog):
    """
    Contact-formulier waarmee een gebruiker direct service kan mailen.

    Probeert het bericht te verzenden via een eerder geconfigureerd
    e-mailaccount. Als die er niet is, opent het de systeem-mailclient.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Contact opnemen")
        self.setMinimumSize(680, 620)

        apply_dialog_style(self)
        big = base_font()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(12)

        # ----- Titel -----
        title = QLabel("✉️  Contact opnemen met de maker")
        title.setFont(title_font())
        layout.addWidget(title)

        intro = QLabel(
            f"Vragen, klachten, ideeën of een fout gevonden? Laat het weten "
            f"via dit formulier. Uw bericht gaat naar {SERVICE_EMAIL}."
        )
        intro.setFont(big)
        intro.setWordWrap(True)
        intro.setStyleSheet(
            "background:#2a2a2a; padding:12px; border-radius:6px; color:#e0e0e0;"
        )
        layout.addWidget(intro)

        # ----- Formulier -----
        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Onderwerp
        self.combo_subject = QComboBox()
        self.combo_subject.setFont(big)
        self.combo_subject.setMinimumHeight(40)
        for label, _internal in SUBJECTS:
            self.combo_subject.addItem(label)
        lbl_subj = QLabel("Soort bericht:")
        lbl_subj.setFont(QFont("Segoe UI", big.pointSize(), QFont.Bold))
        form.addRow(lbl_subj, self.combo_subject)

        # Naam (optioneel)
        self.txt_name = QLineEdit()
        self.txt_name.setFont(big)
        self.txt_name.setMinimumHeight(40)
        self.txt_name.setPlaceholderText("Bijvoorbeeld: Anna")
        # Voorinvullen met opgeslagen voornaam als bekend
        self.txt_name.setText(str(config.get("user_name", "")))
        lbl_name = QLabel("Uw naam:")
        lbl_name.setFont(QFont("Segoe UI", big.pointSize(), QFont.Bold))
        form.addRow(lbl_name, self.txt_name)

        # E-mail van afzender (zodat antwoord mogelijk is)
        self.txt_email = QLineEdit()
        self.txt_email.setFont(big)
        self.txt_email.setMinimumHeight(40)
        self.txt_email.setPlaceholderText("naam@voorbeeld.nl  (zodat ik kan antwoorden)")
        # Voorinvullen met eerste e-mailaccount als bekend
        try:
            accs = load_accounts()
            if accs:
                self.txt_email.setText(accs[0].get("email", ""))
        except Exception:
            pass
        lbl_email = QLabel("Uw e-mail:")
        lbl_email.setFont(QFont("Segoe UI", big.pointSize(), QFont.Bold))
        form.addRow(lbl_email, self.txt_email)

        layout.addLayout(form)

        # Bericht (groot tekstvak)
        msg_label = QLabel("Uw bericht:")
        msg_label.setFont(QFont("Segoe UI", big.pointSize(), QFont.Bold))
        layout.addWidget(msg_label)

        self.txt_message = QPlainTextEdit()
        self.txt_message.setFont(big)
        self.txt_message.setMinimumHeight(180)
        self.txt_message.setPlaceholderText(
            "Schrijf hier uw vraag, klacht of idee. Wees zo duidelijk mogelijk — "
            "als het om een fout gaat, beschrijf wat u deed en wat er gebeurde."
        )
        layout.addWidget(self.txt_message, 1)

        # Status-tekst
        self.lbl_status = QLabel("")
        self.lbl_status.setFont(big)
        self.lbl_status.setWordWrap(True)
        self.lbl_status.setMinimumHeight(50)
        layout.addWidget(self.lbl_status)

        # ----- Knoppen onderaan -----
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.btn_send = QPushButton("✉️  Verzenden")
        self.btn_send.setFont(QFont("Segoe UI", big.pointSize(), QFont.Bold))
        self.btn_send.setMinimumHeight(54)
        self.btn_send.setObjectName("primary")
        self.btn_send.setStyleSheet(
            "QPushButton#primary { background:#2a5a2a; color:#fff; "
            "border:2px solid #4a8a4a; border-radius:6px; padding:10px 20px; }"
            "QPushButton#primary:hover { background:#3a6a3a; }"
        )
        self.btn_send.clicked.connect(self._send)
        btn_row.addWidget(self.btn_send, 1)

        btn_close = QPushButton("Sluiten")
        btn_close.setFont(big)
        btn_close.setMinimumHeight(54)
        btn_close.setMinimumWidth(140)
        btn_close.clicked.connect(self.reject)
        btn_row.addWidget(btn_close)

        layout.addLayout(btn_row)

        # EU-toegankelijkheid: handje + tooltips na opbouw van alle widgets
        apply_accessibility(self)

    # ------------------------------------------------------------------
    def _validate(self) -> str | None:
        """Returnt foutboodschap of None als alles oké is."""
        message = self.txt_message.toPlainText().strip()
        email = self.txt_email.text().strip()

        if len(message) < 10:
            return "Schrijf alstublieft een wat uitgebreidere boodschap (minimaal 10 tekens)."
        if email and "@" not in email:
            return "Het ingevulde e-mailadres lijkt niet geldig (geen @ erin)."
        return None

    def _build_email_body(self) -> tuple[str, str]:
        """Geef (subject, body) terug, met handige meta-info."""
        subject_label = self.combo_subject.currentText()
        # Vind de bijbehorende email-subject
        subject_internal = subject_label
        for label, internal in SUBJECTS:
            if label == subject_label:
                subject_internal = internal
                break

        name = self.txt_name.text().strip() or "(geen naam opgegeven)"
        reply_to = self.txt_email.text().strip() or "(geen e-mailadres opgegeven)"
        message = self.txt_message.toPlainText().strip()

        body = (
            f"Bericht via DeskButler v{APP_VERSION} contact-formulier\n"
            f"───────────────────────────────────────\n\n"
            f"Van:        {name}\n"
            f"E-mail:     {reply_to}\n"
            f"Soort:      {subject_label}\n\n"
            f"Bericht:\n"
            f"{message}\n\n"
            f"───────────────────────────────────────\n"
            f"DeskButler v{APP_VERSION}\n"
        )
        return subject_internal, body

    def _send(self):
        """Probeer via SMTP (in achtergrond), val anders terug op mailto:."""
        err = self._validate()
        if err:
            self.lbl_status.setText(f"⚠️  {err}")
            return

        self.btn_send.setEnabled(False)
        self.lbl_status.setText("⏳  Bezig met verzenden... (kan tot 30 seconden duren)")
        QApplication.processEvents()

        subject, body = self._build_email_body()
        self._last_subject = subject
        self._last_body = body

        # Snel-check: zijn er überhaupt accounts? Zo niet, direct mailto:
        try:
            has_accounts = bool(load_accounts())
        except Exception:
            has_accounts = False

        if not has_accounts:
            self.lbl_status.setText(
                "ℹ️  Geen mail-account ingesteld — ik open uw mail-programma..."
            )
            QApplication.processEvents()
            self._open_mailto(subject, body)
            return

        # Verzenden via SMTP in achtergrond-thread
        self._worker = _SmtpSendWorker(subject, body)
        self._worker.finished_result.connect(self._on_send_done)
        self._worker.start()

    def _on_send_done(self, ok: bool, info: str):
        """Callback wanneer SMTP-thread klaar is."""
        if ok:
            self.lbl_status.setText(
                f"✓  Bericht verzonden naar {SERVICE_EMAIL} via {info}! "
                f"U krijgt antwoord op {self.txt_email.text().strip() or 'uw mail'}."
            )
            self.btn_send.setText("✓ Verzonden")
            return

        # SMTP faalde — vertel waarom en val terug op mailto:
        self.lbl_status.setText(
            f"⚠️  SMTP-verzending faalde: {info}\n"
            f"Ik open nu uw mail-programma in plaats daarvan..."
        )
        QApplication.processEvents()
        self._open_mailto(self._last_subject, self._last_body)

    def _open_mailto(self, subject: str, body: str):
        """
        Probeer in volgorde:
          1. os.startfile (Windows native, werkt vrijwel altijd)
          2. QDesktopServices.openUrl (cross-platform)
          3. subprocess met explorer.exe (Windows last resort)
        Als niets werkt: kopieer alles naar klembord en geef instructie.
        """
        # Beperk body-lengte; sommige mail-apps falen bij grote mailto: URLs
        # (typisch limiet 2000 tekens voor de hele URL).
        short_body = body
        if len(body) > 1500:
            short_body = body[:1500] + "\n\n[...bericht ingekort voor mailto:]"

        mailto_url = (
            f"mailto:{SERVICE_EMAIL}"
            f"?subject={quote(subject)}"
            f"&body={quote(short_body)}"
        )

        opened = False
        last_error = ""

        # Route 1: os.startfile op Windows (native shell open)
        import os
        if os.name == "nt":
            try:
                os.startfile(mailto_url)
                opened = True
            except Exception as e:
                last_error = f"os.startfile: {e}"
                print(f"[contact] os.startfile faalde: {e}")

        # Route 2: QDesktopServices (cross-platform)
        if not opened:
            try:
                if QDesktopServices.openUrl(QUrl(mailto_url)):
                    opened = True
            except Exception as e:
                last_error = f"QDesktopServices: {e}"

        # Route 3: explorer.exe als allerlaatste
        if not opened and os.name == "nt":
            try:
                import subprocess
                subprocess.Popen(["explorer.exe", mailto_url])
                opened = True
            except Exception as e:
                last_error = f"explorer: {e}"

        if opened:
            self.lbl_status.setText(
                f"✉️  Uw mail-programma is geopend met het bericht klaar. "
                f"Klik daar op 'Verzenden' om het te versturen naar {SERVICE_EMAIL}."
            )
            self.btn_send.setText("✓ Mailclient geopend")
        else:
            # Allerlaatste redmiddel: kopieer naar klembord met instructie
            clipboard_text = (
                f"Aan: {SERVICE_EMAIL}\n"
                f"Onderwerp: {subject}\n\n"
                f"{body}"
            )
            QApplication.clipboard().setText(clipboard_text)
            self.lbl_status.setText(
                f"⚠️  Geen mail-programma gevonden op uw pc.\n"
                f"Uw bericht is wel automatisch gekopieerd naar het klembord. "
                f"Open uw browser (bv. Gmail.com of Outlook.com), klik op "
                f"'Nieuwe mail', en plak met Ctrl+V. Stuur naar {SERVICE_EMAIL}.\n"
                f"(Foutdetail: {last_error or 'onbekend'})"
            )
            self.btn_send.setEnabled(True)
            self.btn_send.setText("📋 Gekopieerd — probeer opnieuw")


# ========================================================================
# UI: Over + update venster  (was: ui/about_dialog.py)
# ========================================================================

class UpdateCheckWorker(QThread):
    """Achtergrond-thread die de update-check uitvoert (geen UI-blokkering)."""
    finished_result = Signal(dict)  # leeg dict bij fout

    def run(self):
        info = check_for_update()
        self.finished_result.emit(info or {})


class AboutDialog(QDialog):
    """Info over de app + handmatige update-knop."""

    # Signaal voor in-app browser opening
    open_in_browser = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Over {APP_NAME}")
        self.setMinimumSize(560, 480)

        apply_dialog_style(self)
        big = base_font()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 20)
        layout.setSpacing(12)

        # Titel
        title = QLabel(f"🎩  {APP_NAME}")
        title.setFont(QFont("Segoe UI", base_font().pointSize() + 8, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Versie
        ver = QLabel(f"Versie {APP_VERSION}")
        ver.setFont(QFont("Segoe UI", base_font().pointSize() + 2))
        ver.setAlignment(Qt.AlignCenter)
        ver.setStyleSheet("color: #c0c0c0;")
        layout.addWidget(ver)

        # Maker
        author = QLabel(f"Gemaakt door <b>{AUTHOR_NAME}</b>")
        author.setFont(big)
        author.setAlignment(Qt.AlignCenter)
        layout.addWidget(author)

        # Website link knop
        btn_site = QPushButton(f"🌐  Bezoek {WEBSITE_URL}")
        btn_site.setFont(big)
        btn_site.setMinimumHeight(50)
        btn_site.clicked.connect(self._open_website)
        layout.addWidget(btn_site)

        # Contact knop
        btn_contact = QPushButton("✉️  Contact opnemen met de maker")
        btn_contact.setFont(big)
        btn_contact.setMinimumHeight(50)
        btn_contact.clicked.connect(self._open_contact)
        layout.addWidget(btn_contact)

        # Beschrijving
        desc = QLabel(
            "Uw persoonlijke desktop-assistent: helpt met zoeken, e-mail, "
            "agenda, herinneringen, notities, te-doen lijst en meer. "
            "Volledig toegankelijk voor slechtziende gebruikers met grote "
            "tekst, hoog contrast en spraakfeedback."
        )
        desc.setFont(big)
        desc.setWordWrap(True)
        desc.setStyleSheet("background:#2a2a2a; padding:14px; border-radius:6px; color:#e0e0e0;")
        layout.addWidget(desc)

        # Update sectie
        self.lbl_update_status = QLabel("Klik hieronder om te controleren op updates...")
        self.lbl_update_status.setFont(big)
        self.lbl_update_status.setWordWrap(True)
        self.lbl_update_status.setStyleSheet("color: #909090; padding: 6px;")
        layout.addWidget(self.lbl_update_status)

        btn_check = QPushButton("🔄  Controleer op updates")
        btn_check.setFont(big)
        btn_check.setMinimumHeight(48)
        btn_check.clicked.connect(self._check_updates)
        layout.addWidget(btn_check)

        # ---- Log-bestand sectie ----
        # Toon ook de exacte locatie zodat gebruiker weet waar het staat
        try:
            log_loc = str(get_log_path())
        except Exception:
            log_loc = "(onbekend)"
        log_label = QLabel(
            "📋 Log-bestand voor probleemoplossing:\n"
            "Als u problemen ondervindt kunt u het log-bestand bekijken of "
            "meesturen naar service@dravenlock.nl.\n"
            f"Locatie: {log_loc}"
        )
        log_label.setFont(big)
        log_label.setWordWrap(True)
        log_label.setStyleSheet("color: #c0c0c0; padding: 6px;")
        layout.addWidget(log_label)

        log_row = QHBoxLayout()
        log_row.setSpacing(10)

        btn_open_log = QPushButton("📄  Open log-bestand")
        btn_open_log.setFont(big)
        btn_open_log.setMinimumHeight(44)
        btn_open_log.setToolTip("Open het log-bestand in uw tekst-editor")
        btn_open_log.clicked.connect(self._open_log)
        log_row.addWidget(btn_open_log)

        btn_open_folder = QPushButton("📁  Open log-map")
        btn_open_folder.setFont(big)
        btn_open_folder.setMinimumHeight(44)
        btn_open_folder.setToolTip(
            "Open de map waar de log-bestanden staan (de laatste 3 sessies)"
        )
        btn_open_folder.clicked.connect(self._open_log_folder)
        log_row.addWidget(btn_open_folder)

        layout.addLayout(log_row)

        layout.addStretch()

        # Sluiten
        btn_close = QPushButton("Sluiten")
        btn_close.setFont(big)
        btn_close.setMinimumHeight(48)
        btn_close.setObjectName("primary")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

        self._update_worker = None

        # EU-toegankelijkheid: handje + tooltips na opbouw alle widgets
        apply_accessibility(self)

    def _open_website(self):
        self.open_in_browser.emit(WEBSITE_URL)

    def _open_log(self):
        """Open het log-bestand in de standaard tekst-editor."""
        try:
            log_path = get_log_path()
            if not log_path.exists():
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(
                    self, "Geen log",
                    "Er is nog geen log-bestand. Dat komt zodra de app even draait."
                )
                return
            ok = open_log_in_editor()
            if not ok:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self, "Kon niet openen",
                    f"Het log-bestand staat hier:\n{log_path}"
                )
        except Exception as e:
            print(f"[about] open log faalde: {e}")

    def _open_log_folder(self):
        """Open de map waar de logs staan."""
        try:
            open_log_folder()
        except Exception as e:
            print(f"[about] open log-map faalde: {e}")

    def _open_contact(self):
        dlg = ContactDialog(parent=self)
        dlg.exec()

    def _check_updates(self):
        self.lbl_update_status.setText("⏳  Bezig met controleren...")
        QApplication.processEvents()

        # Async via QThread (geen UI-bevriezing)
        self._update_worker = UpdateCheckWorker()
        self._update_worker.finished_result.connect(self._on_update_result)
        self._update_worker.start()

    def _on_update_result(self, info: dict):
        if not info:
            self.lbl_update_status.setText(
                "⚠️  Kon de update-server niet bereiken. "
                "Probeer het later opnieuw of bezoek de website handmatig."
            )
            return
        if info.get("is_newer"):
            self.lbl_update_status.setText(
                f"✨  Nieuwe versie {info['version']} beschikbaar!"
            )
            # Direct popup
            dlg = UpdateAvailableDialog(info, parent=self)
            # Forward signal van geneste dialog naar buiten
            dlg.open_in_browser.connect(self.open_in_browser.emit)
            dlg.exec()
        else:
            self.lbl_update_status.setText(
                f"✓  U gebruikt de laatste versie ({APP_VERSION})."
            )


class UpdateAvailableDialog(QDialog):
    """Popup wanneer een update beschikbaar is."""

    open_in_browser = Signal(str)

    def __init__(self, update_info: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Update beschikbaar")
        self.setMinimumSize(620, 420)

        apply_dialog_style(self)
        big = base_font()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Header
        title = QLabel(f"✨  Update beschikbaar!")
        title.setFont(title_font())
        layout.addWidget(title)

        ver_info = QLabel(
            f"<b>Huidige versie:</b> {update_info.get('current', APP_VERSION)}<br>"
            f"<b>Nieuwste versie:</b> {update_info.get('version', '?')}"
        )
        ver_info.setFont(big)
        ver_info.setStyleSheet("background:#2a2a2a; padding:12px; border-radius:6px;")
        layout.addWidget(ver_info)

        # Release notes (als beschikbaar)
        notes = update_info.get("notes", "").strip()
        if notes:
            notes_label = QLabel("Wat is er nieuw:")
            notes_label.setFont(QFont("Segoe UI", base_font().pointSize(), QFont.Bold))
            layout.addWidget(notes_label)

            notes_view = QPlainTextEdit()
            notes_view.setPlainText(notes)
            notes_view.setReadOnly(True)
            notes_view.setFont(big)
            notes_view.setMaximumHeight(180)
            layout.addWidget(notes_view)
        else:
            extra = QLabel(
                f"Bezoek {DOWNLOAD_PAGE_URL} voor de nieuwste versie en details."
            )
            extra.setFont(big)
            extra.setWordWrap(True)
            extra.setStyleSheet("color: #c0c0c0;")
            layout.addWidget(extra)

        # Knoppen
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        btn_download = QPushButton("⬇️  Ja, naar download-pagina")
        btn_download.setFont(QFont("Segoe UI", base_font().pointSize(), QFont.Bold))
        btn_download.setMinimumHeight(56)
        btn_download.setStyleSheet(
            "QPushButton { background:#2a8a2a; color:#fff; "
            "border:3px solid #4aaa4a; border-radius:6px; padding:8px 20px; }"
            "QPushButton:hover { background:#3a9a3a; }"
        )
        btn_download.setToolTip("Open de download-pagina in de browser")
        btn_download.clicked.connect(self._download)
        btn_row.addWidget(btn_download)

        btn_later = QPushButton("✕  Nee, later")
        btn_later.setFont(QFont("Segoe UI", big.pointSize(), QFont.Bold))
        btn_later.setMinimumHeight(56)
        btn_later.setStyleSheet(
            "QPushButton { background:#8a2a2a; color:#fff; "
            "border:3px solid #aa4a4a; border-radius:6px; padding:8px 20px; }"
            "QPushButton:hover { background:#9a3a3a; }"
        )
        btn_later.setToolTip("Doe later, ik herinner u eraan bij de volgende update-check")
        btn_later.clicked.connect(self.reject)
        btn_row.addWidget(btn_later)

        layout.addLayout(btn_row)

        apply_accessibility(self)

    def _download(self):
        self.open_in_browser.emit(DOWNLOAD_PAGE_URL)
        self.accept()


def check_update_on_startup_async(butler_widget=None, on_open_url=None):
    """
    Voert update-check uit in achtergrond. Toont popup als nieuwer beschikbaar.
    Niet-blokkerend; faalt stil bij netwerkproblemen.

    on_open_url: callback(url: str) voor in-app browser opening.
    """
    from PySide6.QtCore import QObject

    class StartupWorker(QObject):
        def __init__(self):
            super().__init__()
            self.thread = UpdateCheckWorker()
            self.thread.finished_result.connect(self._on_result)
            # Houd referentie zodat thread niet vrijgeven wordt
            self._self_ref = self

        def start(self):
            self.thread.start()

        def _on_result(self, info: dict):
            try:
                if info and info.get("is_newer"):
                    # Toon korte ballon-notificatie
                    if butler_widget is not None:
                        try:
                            butler_widget.show_bubble(
                                f"✨ Update {info['version']} beschikbaar!",
                                duration_ms=5000,
                            )
                        except Exception:
                            pass
                    # Open de update-popup
                    dlg = UpdateAvailableDialog(info, parent=None)
                    if on_open_url is not None:
                        dlg.open_in_browser.connect(on_open_url)
                    dlg.exec()
            finally:
                self._self_ref = None

    worker = StartupWorker()
    worker.start()
    return worker


# ========================================================================
# UI: butler widget  (was: ui/butler_widget.py)
# ========================================================================

# (ASSETS_DIR komt uit globale assets-sectie)
# (SVG_PATH komt uit globale assets-sectie)

# Default-coördinaten (worden bij init overschreven door het gekozen karakter)
SVG_W, SVG_H = 800, 1000
EYE_LEFT_CENTER = (370, 295)
EYE_RIGHT_CENTER = (430, 295)
EYE_RADIUS = 9
PUPIL_RADIUS = 4
EYE_MAX_OFFSET = 4
MOUTH_CENTER = (400, 345)
MOUTH_WIDTH = 40


class ButlerWidget(QWidget):
    """De zwevende butler rechtsonder."""

    clicked = Signal()
    right_clicked = Signal(QPoint)  # geeft globale positie door

    def __init__(self, tray_menu_provider=None):
        super().__init__()
        self._tray_menu_provider = tray_menu_provider

        # Frameless, transparant, always-on-top, niet in taakbalk
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
            | Qt.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        # EU-toegankelijkheid: handje-cursor + tooltip
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(
            "Dubbelklik = vraag stellen.\n"
            "Eén keer klikken = mij stil maken (tijdens spraak) of mij verplaatsen.\n"
            "Rechtsklik = menu openen."
        )

        # Grootte van de butler op het scherm
        scale = float(config.get("butler_scale", 1.0))
        self._display_w = int(220 * scale)
        self._display_h = int(275 * scale)
        # Ballon staat LINKS naast de butler (niet meer erboven, want dan
        # zakte de tekst uit beeld bij lange voorlezingen)
        self._bubble_w = 340
        self._bubble_h = 0  # wordt dynamisch berekend
        # Widget: bubble + gap + butler breed, butler-hoogte hoog
        self._gap = 10
        total_w = self._bubble_w + self._gap + self._display_w
        total_h = self._display_h + 20  # 20 marge onder voor speling
        self.setMinimumSize(total_w, total_h)
        self.resize(total_w, total_h)

        # Vasthouden waar de ballon getekend staat (voor klik-detectie)
        self._bubble_rect_cached = QRect()

        # Laad het gekozen karakter (default: Alfred)
        self._svg = QSvgRenderer()
        self._custom_pixmap = None
        self._load_character()

        # State
        self._breath_phase = 0.0
        self._blink_state = 1.0          # 1.0 = open, 0.0 = dicht
        self._blink_target = 1.0
        self._mouth_open = 0.0           # 0..1, voor lipsync
        self._mouth_target = 0.0
        self._pupil_offset = QPointF(0, 0)
        self._pupil_target = QPointF(0, 0)
        self._gesture_offset = QPointF(0, 0)
        self._gesture_rotation = 0.0
        self._gesture_active = None
        self._gesture_progress = 0.0

        # Spraakballon
        self._bubble_text = ""
        self._bubble_visible = False
        self._bubble_full_text = ""  # ongekorte versie voor klik-opening
        self._has_more_text = False
        self._bubble_timer = QTimer(self)
        self._bubble_timer.setSingleShot(True)
        self._bubble_timer.timeout.connect(self._on_bubble_timeout)

        # Wachtrij van ballonnen: zo verdringen ze elkaar niet
        # Elke item is een tuple: (text, duration_ms)
        self._bubble_queue = []

        # Animatie-timer (60 fps voor vloeiende beweging)
        self._anim_timer = QTimer(self)
        self._anim_timer.setInterval(16)
        self._anim_timer.timeout.connect(self._tick)
        self._anim_timer.start()

        # Knipper-timer (sturen random momenten)
        self._blink_timer = QTimer(self)
        self._blink_timer.timeout.connect(self._do_blink)
        self._schedule_next_blink()

        # Voice koppelen
        self._voice = get_voice()
        self._voice.amplitude.connect(self._on_voice_amplitude)
        self._voice.started.connect(self._on_voice_started)
        self._voice.finished.connect(self._on_voice_finished)

        # Position rechtsonder boven taakbalk
        self._position_bottom_right()

        # Voor drag&drop op de butler (optioneel)
        self._drag_pos = None

        # Boek-animatie tijdens zoeken
        self._searching = False
        self._search_book_phase = 0.0  # 0..1 voor in-/uit-fade
        self._search_book_target = 0.0  # waar we naartoe animeren

        # Walk away/back animatie
        self._walk_anim = None  # actieve QPropertyAnimation
        self._home_pos = None   # natuurlijke positie (wordt na _position_bottom_right gevuld)
        QTimer.singleShot(100, self._remember_home_pos)

    def _remember_home_pos(self):
        from PySide6.QtCore import QPoint
        self._home_pos = QPoint(self.x(), self.y())

    # ------------------------------------------------------------------
    # Positionering
    # ------------------------------------------------------------------
    def _position_bottom_right(self):
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return
        # availableGeometry sluit de taakbalk uit -> butler komt erboven
        geo = screen.availableGeometry()
        margin = 10
        x = geo.right() - self.width() + margin
        y = geo.bottom() - self.height() + margin
        self.move(x, y)

    # ------------------------------------------------------------------
    # Animatie tick (60fps)
    # ------------------------------------------------------------------
    def _tick(self):
        # Ademhaling
        self._breath_phase += 0.016 * 1.4  # ~1.4 rad/sec -> trage ademhaling
        if self._breath_phase > math.tau:
            self._breath_phase -= math.tau

        # Knipperen
        d = self._blink_target - self._blink_state
        self._blink_state += d * 0.35

        # Mond
        d = self._mouth_target - self._mouth_open
        self._mouth_open += d * 0.4

        # Pupillen volgen muis
        self._update_pupil_target()
        dx = self._pupil_target.x() - self._pupil_offset.x()
        dy = self._pupil_target.y() - self._pupil_offset.y()
        self._pupil_offset.setX(self._pupil_offset.x() + dx * 0.15)
        self._pupil_offset.setY(self._pupil_offset.y() + dy * 0.15)

        # Gebaren voortgang
        if self._gesture_active:
            self._gesture_progress += 0.025
            if self._gesture_progress >= 1.0:
                self._gesture_active = None
                self._gesture_progress = 0.0
                self._gesture_offset = QPointF(0, 0)
                self._gesture_rotation = 0.0
            else:
                self._apply_gesture()

        # Boek fade-in/uit
        d = self._search_book_target - self._search_book_phase
        self._search_book_phase += d * 0.12  # zachte fade
        # Clamp
        if abs(self._search_book_phase - self._search_book_target) < 0.005:
            self._search_book_phase = self._search_book_target

        self.update()

    def _apply_gesture(self):
        """Bereken offset/rotatie voor het huidige gebaar."""
        p = self._gesture_progress
        if self._gesture_active == "nod":
            # Knik: kleine op-neer beweging
            self._gesture_offset = QPointF(0, math.sin(p * math.tau) * 5)
        elif self._gesture_active == "point":
            # Wijzen: hele butler iets naar voren leunen
            self._gesture_offset = QPointF(math.sin(p * math.pi) * 8, 0)
        elif self._gesture_active == "tap_umbrella":
            # Paraplu-tikje: kleine schok
            if p < 0.5:
                self._gesture_offset = QPointF(0, math.sin(p * 2 * math.pi) * 3)
            else:
                self._gesture_offset = QPointF(0, 0)

    def _update_pupil_target(self):
        """Bereken waar de pupillen heen moeten."""
        # Tijdens lezen: scan-patroon, ogen omlaag richting het boek
        if self._searching and self._search_book_phase > 0.5:
            import time
            t = time.time()
            # Snelheid: ~1.6 sec per regel-passage
            line_speed = 1.6
            phase = (t / line_speed) % 2.0  # 0..2
            # Bepaalde regel-index voor lichte verticale variatie
            line_idx = int(t / line_speed) % 4
            # Horizontaal: heen (0..1) of terug (1..0) afhankelijk van pariteit
            if int(t / line_speed) % 2 == 0:
                scan_x = phase if phase < 1 else 2 - phase
            else:
                scan_x = (1 - phase) if phase < 1 else phase - 1
            # Map naar pupil offset
            # Horizontaal: van -0.7 tot +0.7 van max (niet helemaal in de hoek)
            target_x = (scan_x - 0.5) * 2 * EYE_MAX_OFFSET * 0.7
            # Verticaal: stevig omlaag (~70% van max) met kleine variatie per regel
            target_y = EYE_MAX_OFFSET * 0.55 + (line_idx - 1.5) * EYE_MAX_OFFSET * 0.08
            self._pupil_target = QPointF(target_x, target_y)
            return

        # Normale modus: muis volgen
        cursor = QCursor.pos()
        widget_pos = self.mapToGlobal(QPoint(self._display_w // 2, int(self._display_h * 0.3)))
        dx = cursor.x() - widget_pos.x()
        dy = cursor.y() - widget_pos.y()

        dist = math.hypot(dx, dy)
        if dist < 1:
            self._pupil_target = QPointF(0, 0)
            return
        max_dist = 600
        factor = min(1.0, dist / max_dist)
        nx = (dx / dist) * factor * EYE_MAX_OFFSET
        ny = (dy / dist) * factor * EYE_MAX_OFFSET
        self._pupil_target = QPointF(nx, ny)

    # ------------------------------------------------------------------
    # Knipperen
    # ------------------------------------------------------------------
    def _schedule_next_blink(self):
        # Tussen 2 en 6 seconden
        interval = random.randint(2000, 6000)
        self._blink_timer.start(interval)

    def _do_blink(self):
        self._blink_target = 0.0
        QTimer.singleShot(120, self._open_eyes_after_blink)
        self._schedule_next_blink()

    def _open_eyes_after_blink(self):
        self._blink_target = 1.0

    # ------------------------------------------------------------------
    # Voice koppeling
    # ------------------------------------------------------------------
    def _on_voice_amplitude(self, amp: float):
        self._mouth_target = max(0.0, min(1.0, amp))

    def _on_voice_started(self, text: str):
        self.show_bubble(text)

    def _on_voice_finished(self):
        self._mouth_target = 0.0
        # Verberg ballon na korte vertraging
        self._bubble_timer.start(2500)

    # ------------------------------------------------------------------
    # Spraakballon
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # Karakter laden
    # ------------------------------------------------------------------
    def _load_character(self):
        """Laad het karakter uit config + zijn animatie-coördinaten."""
        global SVG_W, SVG_H, EYE_LEFT_CENTER, EYE_RIGHT_CENTER
        global EYE_RADIUS, PUPIL_RADIUS, MOUTH_CENTER

        char = get_character()
        SVG_W = char["svg_width"]
        SVG_H = char["svg_height"]
        EYE_LEFT_CENTER = char["eye_left"]
        EYE_RIGHT_CENTER = char["eye_right"]
        EYE_RADIUS = char["eye_radius"]
        PUPIL_RADIUS = char["pupil_radius"]
        MOUTH_CENTER = char["mouth"]

        # Check of de gebruiker een eigen afbeelding heeft opgegeven
        custom_path = str(config.get("character_custom_image", "")).strip()
        if config.get("character_id") == "custom" and custom_path:
            from pathlib import Path
            p = Path(custom_path)
            if p.exists():
                self._custom_pixmap = QPixmap(str(p))
                if self._custom_pixmap.isNull():
                    self._custom_pixmap = None
                else:
                    print(f"[butler] custom afbeelding geladen: {custom_path}")
                    return  # geen SVG nodig
        self._custom_pixmap = None

        # SVG laden uit het karakter-dict
        svg_data = char.get("svg")
        if svg_data:
            ok = self._svg.load(bytes(svg_data, "utf-8"))
            if not ok:
                print(f"[butler] SVG laden faalde voor {char['name']}")
        elif SVG_PATH.exists():
            # Fallback voor losse versie met bestand op disk
            self._svg.load(str(SVG_PATH))

    def reload_character(self):
        """Hot-reload: aan te roepen na karakterwijziging in settings."""
        self._load_character()
        self.update()

    # ------------------------------------------------------------------
    def show_bubble(self, text: str, duration_ms: int = None):
        """
        Toon een ballon. Als er al één zichtbaar is met een timer, wordt
        deze in een wachtrij geplaatst zodat ze elkaar niet overschrijven.
        Ballonnen zonder duration_ms (bij voorlezen) krijgen voorrang.
        """
        # Belangrijke ballonnen zonder duration_ms (lopende spraak) krijgen direct voorrang
        if duration_ms is None:
            self._bubble_queue.clear()
            self._show_bubble_now(text, None)
            return

        # Als er nu geen ballon zichtbaar is: meteen tonen
        if not self._bubble_visible:
            self._show_bubble_now(text, duration_ms)
            return

        # Anders: in de queue plaatsen (max 5, om te voorkomen dat de
        # gebruiker minutenlang oude meldingen krijgt te zien)
        if len(self._bubble_queue) < 5:
            self._bubble_queue.append((text, duration_ms))

    def _show_bubble_now(self, text: str, duration_ms):
        """Vervang de huidige ballon-inhoud direct."""
        self._bubble_text = text
        self._bubble_full_text = text  # volledige versie voor klik-popup
        self._bubble_visible = True
        if duration_ms is not None:
            self._bubble_timer.start(duration_ms)
        else:
            self._bubble_timer.stop()
        self.update()

    def _on_bubble_timeout(self):
        """Wanneer de timer afloopt: volgende ballon uit queue, of verbergen."""
        if self._bubble_queue:
            text, duration = self._bubble_queue.pop(0)
            self._show_bubble_now(text, duration)
        else:
            self._hide_bubble()

    def open_full_text_dialog(self):
        """Open een gescroll-baar venster met de volledige tekstinhoud."""
        if not self._bubble_full_text:
            return
        try:
            dlg = FullTextDialog(self._bubble_full_text, parent=self)
            dlg.exec()
        except Exception as e:
            print(f"[butler] full text dialog faalde: {e}")

    def _hide_bubble(self):
        self._bubble_visible = False
        self.update()

    # ------------------------------------------------------------------
    # Publieke gebaar-API
    # ------------------------------------------------------------------
    def gesture_nod(self):
        self._gesture_active = "nod"
        self._gesture_progress = 0.0

    def gesture_point(self):
        self._gesture_active = "point"
        self._gesture_progress = 0.0

    def gesture_tap_umbrella(self):
        self._gesture_active = "tap_umbrella"
        self._gesture_progress = 0.0

    def speak(self, text: str):
        """Laat de butler praten + ballon tonen + knikken voor accent."""
        self._voice.speak(text)
        # Subtiele knik bij start
        QTimer.singleShot(150, self.gesture_nod)

    # ------------------------------------------------------------------
    # Zoek-boek animatie
    # ------------------------------------------------------------------
    def start_searching(self):
        """Toon een boek voor de butler tijdens een zoekactie."""
        self._searching = True
        self._search_book_target = 1.0  # fade in

    def stop_searching(self):
        """Verberg het boek wanneer het zoeken klaar is."""
        self._searching = False
        self._search_book_target = 0.0  # fade out

    # ------------------------------------------------------------------
    # Walk away / walk back
    # ------------------------------------------------------------------
    def walk_away(self):
        """Animeer de butler naar buiten beeld (rechts)."""
        from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QPoint
        if not self.isVisible():
            return
        if self._home_pos is None:
            self._home_pos = QPoint(self.x(), self.y())
        # Doel: helemaal naar rechts buiten beeld
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return
        screen_w = screen.availableGeometry().right()
        end = QPoint(screen_w + 50, self.y())
        if self._walk_anim is not None:
            self._walk_anim.stop()
        anim = QPropertyAnimation(self, b"pos")
        anim.setDuration(900)
        anim.setStartValue(self.pos())
        anim.setEndValue(end)
        anim.setEasingCurve(QEasingCurve.InCubic)
        anim.finished.connect(self.hide)
        anim.start()
        self._walk_anim = anim

    def walk_back(self):
        """Animeer de butler vanuit rechts buiten beeld terug naar zijn plek."""
        from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QPoint
        if self._home_pos is None:
            self._position_bottom_right()
            self._home_pos = QPoint(self.x(), self.y())
            self.show()
            return
        # Begin buiten beeld
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            self.show()
            return
        screen_w = screen.availableGeometry().right()
        start = QPoint(screen_w + 50, self._home_pos.y())
        self.move(start)
        self.show()
        if self._walk_anim is not None:
            self._walk_anim.stop()
        anim = QPropertyAnimation(self, b"pos")
        anim.setDuration(900)
        anim.setStartValue(start)
        anim.setEndValue(self._home_pos)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()
        self._walk_anim = anim

    # ------------------------------------------------------------------
    # Paint
    # ------------------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # Bereken positie van de butler in het widget.
        # Butler staat RECHTS in het widget; ballon komt LINKS daarvan.
        butler_x = (self._bubble_w + self._gap) + self._gesture_offset.x()
        butler_y = self.height() - self._display_h + self._gesture_offset.y()

        # Ademhaling: heel subtiele schaal
        breath_scale = 1.0 + 0.008 * math.sin(self._breath_phase)

        # Schaal-factor van SVG-coords naar widget-pixels
        sx = self._display_w / SVG_W * breath_scale
        sy = self._display_h / SVG_H * breath_scale

        # Teken het karakter
        target = QRectF(
            butler_x + (self._display_w * (1 - breath_scale)) / 2,
            butler_y + self._display_h * (1 - breath_scale),
            self._display_w * breath_scale,
            self._display_h * breath_scale,
        )

        if self._custom_pixmap is not None:
            # Custom afbeelding (statisch, geen ogen/mond animatie)
            painter.drawPixmap(target, self._custom_pixmap, QRectF(self._custom_pixmap.rect()))
            # Spraakballon nog steeds tonen
            if self._bubble_visible and self._bubble_text:
                self._draw_bubble(painter, butler_x, butler_y)
            return

        self._svg.render(painter, target)

        # Bereken waar de ogen en mond op het scherm tekenen
        def svg_to_widget(x, y):
            wx = butler_x + (x / SVG_W) * self._display_w * breath_scale + (self._display_w * (1 - breath_scale)) / 2
            wy = butler_y + (y / SVG_H) * self._display_h * breath_scale + self._display_h * (1 - breath_scale)
            return QPointF(wx, wy)

        # ---- Ogen tekenen ----
        self._draw_eye(painter, svg_to_widget(*EYE_LEFT_CENTER), sx, sy)
        self._draw_eye(painter, svg_to_widget(*EYE_RIGHT_CENTER), sx, sy)

        # ---- Mond tekenen ----
        self._draw_mouth(painter, svg_to_widget(*MOUTH_CENTER), sx, sy)

        # ---- Zoek-boek ----
        if self._search_book_phase > 0.01:
            self._draw_search_book(painter, butler_x, butler_y, breath_scale)

        # ---- Spraakballon ----
        if self._bubble_visible and self._bubble_text:
            self._draw_bubble(painter, butler_x, butler_y)

    def _draw_search_book(self, painter: QPainter, butler_x: float, butler_y: float, scale: float):
        """
        Teken een boek dat Alfred VOOR ZICHZELF houdt - we zien de buitenkant
        van de kaft (rug naar de kijker, pagina-randen aan de zijkanten).
        """
        alpha = self._search_book_phase  # 0..1
        # Positie: voor het lichaam, op handhoogte
        cx = butler_x + self._display_w * 0.50
        cy = butler_y + self._display_h * 0.62
        book_w = self._display_w * 0.28 * scale
        book_h = self._display_h * 0.18 * scale

        # Schaduw onder boek
        shadow_color = QColor(0, 0, 0, int(80 * alpha))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(shadow_color))
        painter.drawEllipse(
            QPointF(cx, cy + book_h * 0.55),
            book_w * 0.50, book_h * 0.08,
        )

        # ----------------------------------------------------------
        # Buitenkant kaft (rugzijde naar ons, het boek leunt iets achterover)
        # We tekenen een licht trapezium: bovenkant iets smaller dan onderkant
        # (perspective alsof het boek iets naar Alfred toe gekanteld is).
        # ----------------------------------------------------------
        from PySide6.QtGui import QPolygonF
        kaft_donker = QColor(110, 25, 25, int(255 * alpha))
        kaft_licht = QColor(155, 40, 40, int(255 * alpha))
        kaft_rand = QColor(60, 10, 10, int(255 * alpha))

        # Hoofdvlak van de rugzijde
        kaft = QPolygonF([
            QPointF(cx - book_w * 0.42, cy - book_h * 0.48),  # links boven
            QPointF(cx + book_w * 0.42, cy - book_h * 0.48),  # rechts boven
            QPointF(cx + book_w * 0.48, cy + book_h * 0.45),  # rechts onder
            QPointF(cx - book_w * 0.48, cy + book_h * 0.45),  # links onder
        ])
        painter.setBrush(QBrush(kaft_donker))
        painter.setPen(QPen(kaft_rand, 1.5))
        painter.drawPolygon(kaft)

        # Hooglicht op de rugzijde (verticale streep)
        painter.setBrush(QBrush(kaft_licht))
        painter.setPen(Qt.NoPen)
        hooglicht = QPolygonF([
            QPointF(cx - book_w * 0.10, cy - book_h * 0.46),
            QPointF(cx + book_w * 0.05, cy - book_h * 0.46),
            QPointF(cx + book_w * 0.06, cy + book_h * 0.42),
            QPointF(cx - book_w * 0.11, cy + book_h * 0.42),
        ])
        painter.drawPolygon(hooglicht)

        # Goud-getinte titel op de rug
        goud = QColor(212, 175, 55, int(255 * alpha))
        painter.setPen(QPen(goud, 1.5))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(
            QRectF(cx - book_w * 0.20, cy - book_h * 0.22,
                   book_w * 0.40, book_h * 0.10)
        )
        # Streepje als 'titel' onder het kader
        painter.drawLine(
            QPointF(cx - book_w * 0.16, cy - book_h * 0.05),
            QPointF(cx + book_w * 0.16, cy - book_h * 0.05),
        )
        painter.drawLine(
            QPointF(cx - book_w * 0.10, cy + book_h * 0.05),
            QPointF(cx + book_w * 0.10, cy + book_h * 0.05),
        )

        # Pagina-randen aan de zijkanten (cremekleur, fijne streepjes)
        creme = QColor(240, 230, 200, int(255 * alpha))
        creme_rand = QColor(180, 165, 130, int(255 * alpha))
        painter.setBrush(QBrush(creme))
        painter.setPen(QPen(creme_rand, 1))
        # Linker pagina-strookje
        left_strip = QPolygonF([
            QPointF(cx - book_w * 0.48, cy - book_h * 0.46),
            QPointF(cx - book_w * 0.42, cy - book_h * 0.48),
            QPointF(cx - book_w * 0.42, cy + book_h * 0.45),
            QPointF(cx - book_w * 0.50, cy + book_h * 0.43),
        ])
        painter.drawPolygon(left_strip)
        # Rechter pagina-strookje
        right_strip = QPolygonF([
            QPointF(cx + book_w * 0.42, cy - book_h * 0.48),
            QPointF(cx + book_w * 0.48, cy - book_h * 0.46),
            QPointF(cx + book_w * 0.50, cy + book_h * 0.43),
            QPointF(cx + book_w * 0.42, cy + book_h * 0.45),
        ])
        painter.drawPolygon(right_strip)

        # Fijne horizontale streepjes om papier-lagen te suggereren
        painter.setPen(QPen(creme_rand, 0.6))
        for i in range(5):
            y_off = -book_h * 0.32 + i * (book_h * 0.16)
            painter.drawLine(
                QPointF(cx - book_w * 0.50, cy + y_off),
                QPointF(cx - book_w * 0.42, cy + y_off),
            )
            painter.drawLine(
                QPointF(cx + book_w * 0.42, cy + y_off),
                QPointF(cx + book_w * 0.50, cy + y_off),
            )

        # Bladwijzer (gele lint) hangt aan de onderkant
        if alpha > 0.5:
            bw_color = QColor(220, 180, 30, int(255 * alpha))
            painter.setBrush(QBrush(bw_color))
            painter.setPen(QPen(QColor(150, 120, 15, int(255 * alpha)), 1))
            bookmark = QPolygonF([
                QPointF(cx + book_w * 0.20, cy + book_h * 0.42),
                QPointF(cx + book_w * 0.30, cy + book_h * 0.42),
                QPointF(cx + book_w * 0.27, cy + book_h * 0.68),
                QPointF(cx + book_w * 0.25, cy + book_h * 0.62),
                QPointF(cx + book_w * 0.23, cy + book_h * 0.68),
            ])
            painter.drawPolygon(bookmark)

    def _draw_eye(self, painter: QPainter, center: QPointF, sx: float, sy: float):
        """Teken een oog: wit met pupil, met knipper-effect."""
        eye_r_x = EYE_RADIUS * sx
        eye_r_y = EYE_RADIUS * sy * max(0.05, self._blink_state)

        # Sclera (oogwit)
        painter.setPen(QPen(QColor("#2c3e50"), max(1.0, 1.5 * sx)))
        painter.setBrush(QBrush(QColor("#ffffff")))
        painter.drawEllipse(center, eye_r_x, eye_r_y)

        # Pupil alleen tekenen als oog open genoeg is
        if self._blink_state > 0.25:
            pupil_x = center.x() + self._pupil_offset.x() * sx
            pupil_y = center.y() + self._pupil_offset.y() * sy
            pupil_r_x = PUPIL_RADIUS * sx
            pupil_r_y = PUPIL_RADIUS * sy * max(0.1, self._blink_state)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor("#1a1a1a")))
            painter.drawEllipse(QPointF(pupil_x, pupil_y), pupil_r_x, pupil_r_y)
            # Klein highlight
            painter.setBrush(QBrush(QColor("#ffffff")))
            painter.drawEllipse(
                QPointF(pupil_x - pupil_r_x * 0.3, pupil_y - pupil_r_y * 0.3),
                pupil_r_x * 0.25, pupil_r_y * 0.25
            )

    def _draw_mouth(self, painter: QPainter, center: QPointF, sx: float, sy: float):
        """
        Teken de mond. Bij open=0 een subtiele glimlach,
        bij open=1 een open mond voor lipsync.
        """
        w = MOUTH_WIDTH * sx
        # Hoogte schaalt met mouth_open
        h = (2 + 14 * self._mouth_open) * sy

        if self._mouth_open < 0.05:
            # Subtiele glimlach (curve)
            path = QPainterPath()
            path.moveTo(center.x() - w/2, center.y())
            path.quadTo(center.x(), center.y() + 5 * sy, center.x() + w/2, center.y())
            painter.setPen(QPen(QColor("#c0392b"), 3 * sx, Qt.SolidLine, Qt.RoundCap))
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(path)
        else:
            # Open mond (donker ovaal)
            painter.setPen(QPen(QColor("#7a1f17"), max(1.0, 1.5 * sx)))
            painter.setBrush(QBrush(QColor("#3d0e0a")))
            painter.drawEllipse(center, w/2 * 0.8, h/2)
            # Tong-hint onderin
            if self._mouth_open > 0.4:
                painter.setBrush(QBrush(QColor("#c0392b")))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(
                    QPointF(center.x(), center.y() + h * 0.2),
                    w/2 * 0.5, h/2 * 0.4
                )

    def _draw_bubble(self, painter: QPainter, butler_x: float, butler_y: float):
        """Spraakballon LINKS van de butler met pijl rechts naar butler toe."""
        font_size = config.get("font_size", 16)
        font = QFont("Segoe UI", font_size)
        painter.setFont(font)
        fm = QFontMetrics(font)

        # Tekst breken op woord-niveau
        max_text_w = self._bubble_w - 50
        words = self._bubble_text.split()
        lines = []
        cur = ""
        for w in words:
            test = (cur + " " + w).strip()
            if fm.horizontalAdvance(test) <= max_text_w:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        if not lines:
            lines = [self._bubble_text]

        line_h = fm.height()
        max_lines = max(3, self._display_h // line_h - 1)
        was_truncated = False
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            was_truncated = True
            if len(lines[-1]) > 3:
                lines[-1] = lines[-1].rstrip() + "..."

        text_h = line_h * len(lines) + 28
        bubble_h = text_h
        bubble_x = 5
        head_center_y = butler_y + self._display_h * 0.18
        bubble_y = head_center_y - bubble_h / 2
        if bubble_y < 5:
            bubble_y = 5
        if bubble_y + bubble_h > self.height() - 5:
            bubble_y = self.height() - 5 - bubble_h

        self._bubble_rect_cached = QRect(
            int(bubble_x), int(bubble_y),
            int(self._bubble_w - 20), int(bubble_h)
        )

        bubble_rect = QRectF(bubble_x, bubble_y, self._bubble_w - 20, bubble_h)

        if config.get("high_contrast", True):
            bg = QColor(28, 28, 32, 245)
            fg = QColor(255, 255, 255)
            border = QColor(150, 150, 160)
            shadow = QColor(0, 0, 0, 90)
            highlight = QColor(255, 255, 255, 25)
        else:
            bg = QColor(252, 252, 248, 245)
            fg = QColor(20, 20, 20)
            border = QColor(80, 80, 90)
            shadow = QColor(0, 0, 0, 60)
            highlight = QColor(255, 255, 255, 100)

        # Schaduw onder ballon
        shadow_rect = QRectF(bubble_rect)
        shadow_rect.translate(3, 4)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(shadow))
        painter.drawRoundedRect(shadow_rect, 16, 16)

        # Ballon-vorm: zachte ronding + pijl als cloud-tail (3 cirkels)
        arrow_tip_y = head_center_y
        arrow_right_x = bubble_x + self._bubble_w - 20

        # Hoofd-ballon
        painter.setPen(QPen(border, 2))
        painter.setBrush(QBrush(bg))
        painter.drawRoundedRect(bubble_rect, 16, 16)

        # Cloud-tail: 3 kleine ovaaltjes die de ballon met de butler verbinden
        # (in plaats van een scherpe driehoek)
        tail_y = arrow_tip_y
        # Grote tail-bel net aan de rand
        painter.drawEllipse(QPointF(arrow_right_x + 4, tail_y - 2),
                           10, 8)
        # Middel
        painter.drawEllipse(QPointF(arrow_right_x + 14, tail_y + 4),
                           7, 5.5)
        # Klein laatste
        painter.drawEllipse(QPointF(arrow_right_x + 22, tail_y + 10),
                           4, 3.5)

        # Subtiele hooglicht-streep aan bovenkant
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(highlight))
        hl_rect = QRectF(bubble_rect.x() + 8, bubble_rect.y() + 4,
                        bubble_rect.width() - 16, 8)
        painter.drawRoundedRect(hl_rect, 4, 4)

        # Tekst
        painter.setPen(QPen(fg))
        y = bubble_y + 16 + fm.ascent()
        for line in lines:
            painter.drawText(QPointF(bubble_x + 18, y), line)
            y += line_h

        # Hint dat er meer is: klein "..." rechtsonder + klikbaar-aanwijzer
        if was_truncated:
            hint_color = QColor(160, 160, 170, 200)
            painter.setPen(QPen(hint_color))
            hint_font = QFont("Segoe UI", max(10, font_size - 4))
            painter.setFont(hint_font)
            painter.drawText(
                QPointF(bubble_x + self._bubble_w - 100,
                        bubble_y + bubble_h - 6),
                "klik voor volledig"
            )
            # Onthoud dat er extra tekst is, voor klik-event
            self._has_more_text = True
        else:
            self._has_more_text = False

    # ------------------------------------------------------------------
    # Muis-events
    # ------------------------------------------------------------------
    def _butler_rect(self) -> QRect:
        """Rechthoek waar de butler getekend wordt (voor klik-detectie)."""
        butler_x = self._bubble_w + self._gap
        return QRect(butler_x, self.height() - self._display_h,
                     self._display_w, self._display_h)

    def _bubble_rect(self) -> QRect:
        """Rechthoek van de ballon (alleen geldig als ballon zichtbaar is)."""
        if self._bubble_visible:
            return self._bubble_rect_cached
        return QRect()

    def _is_speaking(self) -> bool:
        """Is de butler op dit moment aan het praten?"""
        # Mond niet helemaal dicht? Dan praat hij
        return self._mouth_target > 0.05 or self._mouth_open > 0.05

    def mousePressEvent(self, event):
        in_butler = self._butler_rect().contains(event.pos())
        in_bubble = self._bubble_rect().contains(event.pos())

        if not in_butler and not in_bubble:
            event.ignore()
            return

        if event.button() == Qt.LeftButton:
            # Klik op bubble met "klik voor volledig" hint -> open dialog
            if in_bubble and self._has_more_text and not self._is_speaking():
                self.open_full_text_dialog()
                event.accept()
                return

            # Praat de butler? Klik = stop spreken (zowel op butler als op ballon)
            if self._is_speaking():
                self._voice.stop()
                self._mouth_target = 0.0
                self._bubble_visible = False
                self.update()
                event.accept()
                return
            # Enkelklik: alleen drag voorbereiden. GEEN zoek-venster openen
            # (dat doen we nu via dubbelklik).
            if in_butler:
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        elif event.button() == Qt.RightButton:
            if in_butler:
                self.right_clicked.emit(event.globalPosition().toPoint())
            event.accept()

    def mouseDoubleClickEvent(self, event):
        """Dubbelklik op de butler opent het zoek-venster."""
        in_butler = self._butler_rect().contains(event.pos())
        if event.button() == Qt.LeftButton and in_butler and not self._is_speaking():
            self.clicked.emit()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() & Qt.LeftButton:
            new_pos = event.globalPosition().toPoint() - self._drag_pos
            self.move(new_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def keyPressEvent(self, event):
        # ESC stopt spraak
        if event.key() == Qt.Key_Escape and self._is_speaking():
            self._voice.stop()
            self._mouth_target = 0.0
            self._bubble_visible = False
            self.update()
            event.accept()
            return
        super().keyPressEvent(event)


# ========================================================================
# UI: system tray  (was: ui/tray.py)
# ========================================================================

# (ASSETS_DIR komt uit globale assets-sectie)
# (ICON_PATH komt uit globale assets-sectie)


class TrayManager(QObject):
    """Beheert het systeemvak-icoon en het rechtermuisknop-menu."""

    open_search = Signal()
    open_email = Signal()
    open_browser = Signal()
    open_calendar = Signal()
    open_todo = Signal()
    open_quickguide = Signal()
    open_settings = Signal()
    open_donation = Signal()
    open_contact = Signal()
    show_about = Signal()
    quit_requested = Signal()

    def __init__(self, parent_app: QApplication):
        super().__init__()
        self._app = parent_app

        icon = QIcon(str(ICON_PATH)) if ICON_PATH.exists() else QIcon()
        self.tray = QSystemTrayIcon(icon, parent_app)
        self.tray.setToolTip(f"{_('app_name')} — {_('butler_name')}")

        self.menu = self._build_menu()
        self.tray.setContextMenu(self.menu)

        # Dubbelklik = zoekvenster openen (snel toegankelijk voor slechtzienden)
        self.tray.activated.connect(self._on_activated)

        self.tray.show()

    def _build_menu(self) -> QMenu:
        menu = QMenu()
        # Grote tekst voor toegankelijkheid
        font = menu.font()
        font.setPointSize(max(11, font.pointSize() + 2))
        menu.setFont(font)

        act_search = QAction(_("menu_search"), menu)
        act_search.setStatusTip("Stel een vraag of zoek iets op (Shift+V)")
        act_search.setToolTip("Stel een vraag of zoek iets op (Shift+V)")
        act_search.triggered.connect(self.open_search.emit)
        menu.addAction(act_search)

        menu.addSeparator()

        act_email = QAction(_("menu_email"), menu)
        act_email.setStatusTip("Open uw e-mailaccounts om te lezen of versturen")
        act_email.setToolTip("Open uw e-mailaccounts om te lezen of versturen")
        act_email.triggered.connect(self.open_email.emit)
        menu.addAction(act_email)

        act_browser = QAction(_("menu_browser"), menu)
        act_browser.setStatusTip("Open de ingebouwde webbrowser")
        act_browser.setToolTip("Open de ingebouwde webbrowser")
        act_browser.triggered.connect(self.open_browser.emit)
        menu.addAction(act_browser)

        act_calendar = QAction(_("menu_calendar"), menu)
        act_calendar.setStatusTip("Bekijk uw agenda en herinneringen")
        act_calendar.setToolTip("Bekijk uw agenda en herinneringen")
        act_calendar.triggered.connect(self.open_calendar.emit)
        menu.addAction(act_calendar)

        act_todo = QAction(_("menu_todo"), menu)
        act_todo.setStatusTip("Open uw te-doen lijst")
        act_todo.setToolTip("Open uw te-doen lijst")
        act_todo.triggered.connect(self.open_todo.emit)
        menu.addAction(act_todo)

        menu.addSeparator()

        act_guide = QAction(_("menu_quickguide"), menu)
        act_guide.setStatusTip("Korte handleiding van alle functies")
        act_guide.setToolTip("Korte handleiding van alle functies")
        act_guide.triggered.connect(self.open_quickguide.emit)
        menu.addAction(act_guide)

        act_settings = QAction(_("menu_settings"), menu)
        act_settings.setStatusTip("Pas stem, karakter, e-mail en meer aan")
        act_settings.setToolTip("Pas stem, karakter, e-mail en meer aan")
        act_settings.triggered.connect(self.open_settings.emit)
        menu.addAction(act_settings)

        act_about = QAction(_("menu_about"), menu)
        act_about.setStatusTip("Versie-info en controle op updates")
        act_about.setToolTip("Versie-info en controle op updates")
        act_about.triggered.connect(self.show_about.emit)
        menu.addAction(act_about)

        act_contact = QAction("✉️  Contact opnemen...", menu)
        act_contact.setStatusTip("Stuur een bericht naar de maker (vragen, klachten, ideeën)")
        act_contact.setToolTip("Stuur een bericht naar de maker (vragen, klachten, ideeën)")
        act_contact.triggered.connect(self.open_contact.emit)
        menu.addAction(act_contact)

        act_donate = QAction("💝  Steun DeskButler...", menu)
        act_donate.setStatusTip("Een kleine donatie helpt de ontwikkeling")
        act_donate.setToolTip("Een kleine donatie helpt de ontwikkeling")
        act_donate.triggered.connect(self.open_donation.emit)
        menu.addAction(act_donate)

        menu.addSeparator()

        act_quit = QAction(_("menu_quit"), menu)
        act_quit.setStatusTip("Sluit DeskButler volledig af")
        act_quit.setToolTip("Sluit DeskButler volledig af")
        act_quit.triggered.connect(self.quit_requested.emit)
        menu.addAction(act_quit)

        # Toon ook de tooltips in het menu (Qt doet dit niet standaard)
        menu.setToolTipsVisible(True)

        return menu

    def _on_activated(self, reason):
        # Dubbelklik op tray-icoon opent zoekvenster
        if reason == QSystemTrayIcon.DoubleClick:
            self.open_search.emit()
        elif reason == QSystemTrayIcon.Trigger:
            # Enkele klik: ook zoekvenster openen (handig voor slechtzienden)
            self.open_search.emit()

    def show_message(self, title: str, message: str, ms: int = 5000):
        """Toon een balloon-tip vanuit het systeemvak."""
        self.tray.showMessage(title, message, QSystemTrayIcon.Information, ms)

    def show_context_menu_at(self, global_pos):
        """Toon het menu op een specifieke positie (bv. bij klik op butler)."""
        self.menu.exec(global_pos)


# ========================================================================
# UI: calendar (eerder, want main.py imports list_reminders_for_date)  (was: ui/calendar_window.py)
# ========================================================================

DB_PATH = DATA_DIR / "reminders.db"


def _init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(DB_PATH))
    con.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            text TEXT NOT NULL,
            notified INTEGER DEFAULT 0,
            recur_yearly INTEGER DEFAULT 0
        )
    """)
    # Migratie: voeg recur_yearly toe als de kolom nog niet bestaat
    cur = con.execute("PRAGMA table_info(reminders)")
    cols = [row[1] for row in cur.fetchall()]
    if "recur_yearly" not in cols:
        con.execute("ALTER TABLE reminders ADD COLUMN recur_yearly INTEGER DEFAULT 0")
    con.commit()
    return con


def get_reminders():
    """Lijst van (id, datetime, text, notified, recur_yearly) tuples."""
    con = _init_db()
    cur = con.execute(
        "SELECT id, ts, text, notified, recur_yearly FROM reminders ORDER BY ts ASC"
    )
    rows = cur.fetchall()
    con.close()
    out = []
    for r_id, ts, text, notified, recur in rows:
        try:
            dt = datetime.fromisoformat(ts)
        except ValueError:
            continue
        out.append((r_id, dt, text, bool(notified), bool(recur)))
    return out


def add_reminder(dt: datetime, text: str, recur_yearly: bool = False):
    con = _init_db()
    con.execute(
        "INSERT INTO reminders (ts, text, recur_yearly) VALUES (?, ?, ?)",
        (dt.isoformat(), text, 1 if recur_yearly else 0),
    )
    con.commit()
    con.close()


def remove_reminder(r_id: int):
    con = _init_db()
    con.execute("DELETE FROM reminders WHERE id = ?", (r_id,))
    con.commit()
    con.close()


def mark_notified(r_id: int):
    con = _init_db()
    con.execute("UPDATE reminders SET notified = 1 WHERE id = ?", (r_id,))
    con.commit()
    con.close()


def reschedule_yearly(r_id: int, new_dt: datetime):
    """Voor jaarlijks herhalende herinneringen: zet datum een jaar vooruit."""
    con = _init_db()
    con.execute(
        "UPDATE reminders SET ts = ?, notified = 0 WHERE id = ?",
        (new_dt.isoformat(), r_id),
    )
    con.commit()
    con.close()


def list_reminders_for_date(date) -> list:
    """Lijst van herinneringen voor een specifieke datum (voor ochtendbriefing)."""
    out = []
    for r in get_reminders():
        r_id, dt, text, notified, recur = r
        if dt.date() == date:
            out.append({
                "id": r_id,
                "time": dt.strftime("%H:%M"),
                "text": text,
                "notified": notified,
                "recur_yearly": recur,
            })
    return out


# ----------------------------------------------------------------------
# Scheduler runt op de achtergrond en triggert notificaties
# ----------------------------------------------------------------------
class ReminderScheduler:
    """Controleert elke 30 seconden of er herinneringen getriggerd moeten worden."""

    def __init__(self):
        self._timer = QTimer()
        self._timer.setInterval(30 * 1000)  # 30 seconden
        self._timer.timeout.connect(self._check)


    def showEvent(self, event):
        super().showEvent(event)
        # EU-toegankelijkheid: handje + tooltips op alle interactieve widgets
        try:
            apply_accessibility(self)
        except Exception:
            pass

    def start(self):
        # Direct check + dan elke 30s
        self._check()
        self._timer.start()

    def stop(self):
        self._timer.stop()

    def _check(self):
        now = datetime.now()
        for r in get_reminders():
            r_id, dt, text, notified, recur_yearly = r
            if notified:
                continue
            if dt <= now:
                notify(_("reminder_title"), text, speak=True)
                if recur_yearly:
                    # Herhaal volgend jaar (zelfde tijd/datum)
                    try:
                        new_dt = dt.replace(year=dt.year + 1)
                    except ValueError:
                        # 29 feb in een niet-schrikkeljaar -> 28 feb
                        new_dt = dt.replace(year=dt.year + 1, day=28)
                    reschedule_yearly(r_id, new_dt)
                else:
                    mark_notified(r_id)


# ----------------------------------------------------------------------
# Add Reminder dialog
# ----------------------------------------------------------------------
class ReminderDialog(QDialog):
    def __init__(self, date: QDate, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("calendar_add"))
        self.setMinimumWidth(450)

        font_size = config.get("font_size", 16)
        self.setFont(QFont("Segoe UI", font_size))

        layout = QFormLayout(self)

        self.date_label = QLabel(date.toString("dddd d MMMM yyyy"))
        self.date_label.setFont(QFont("Segoe UI", font_size, QFont.Bold))
        layout.addRow(self.date_label)

        self.time = QTimeEdit()
        self.time.setDisplayFormat("HH:mm")
        self.time.setTime(QTime.currentTime().addSecs(60 * 60))
        layout.addRow(QLabel(_("calendar_time") + ":"), self.time)

        self.text = QPlainTextEdit()
        self.text.setPlaceholderText(_("calendar_text"))
        self.text.setFixedHeight(120)
        layout.addRow(QLabel(_("calendar_text") + ":"), self.text)

        # Jaarlijks herhalen (voor verjaardagen, jubileums e.d.)
        from PySide6.QtWidgets import QCheckBox
        self.chk_yearly = QCheckBox("Jaarlijks herhalen (verjaardag, jubileum, ...)")
        self.chk_yearly.setFont(QFont("Segoe UI", font_size))
        layout.addRow(self.chk_yearly)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self._date = date

    def get_datetime(self) -> datetime:
        qd = self._date
        qt = self.time.time()
        return datetime(qd.year(), qd.month(), qd.day(), qt.hour(), qt.minute())

    def get_text(self) -> str:
        return self.text.toPlainText().strip()

    def is_yearly(self) -> bool:
        return self.chk_yearly.isChecked()


# ----------------------------------------------------------------------
# Calendar window
# ----------------------------------------------------------------------
class CalendarWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(_("calendar_title"))
        self.resize(1100, 700)
        self._setup_ui()
        self._apply_theme()
        self._refresh_reminders()

    def _setup_ui(self):
        font_size = config.get("font_size", 16)
        big_font = QFont("Segoe UI", font_size)

        central = QWidget()
        self.setCentralWidget(central)
        h = QHBoxLayout(central)

        # Linker: kalender
        left = QVBoxLayout()
        self.calendar = QCalendarWidget()
        self.calendar.setFont(big_font)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendar.activated.connect(self._on_date_activated)  # dubbelklik
        left.addWidget(self.calendar, 1)

        btn_row = QHBoxLayout()
        self.btn_add = QPushButton(_("calendar_add"))
        self.btn_add.setMinimumHeight(50)
        self.btn_add.setFont(big_font)
        self.btn_add.clicked.connect(self._add_for_selected_date)
        btn_row.addWidget(self.btn_add)
        left.addLayout(btn_row)

        # Rechter: lijst met herinneringen
        right = QVBoxLayout()
        self.lbl_upcoming = QLabel("Aankomende herinneringen:")
        self.lbl_upcoming.setFont(QFont("Segoe UI", font_size, QFont.Bold))
        right.addWidget(self.lbl_upcoming)
        self.lst = QListWidget()
        self.lst.setFont(big_font)
        right.addWidget(self.lst, 1)

        self.btn_remove = QPushButton("Verwijder geselecteerde")
        self.btn_remove.setMinimumHeight(40)
        self.btn_remove.setFont(big_font)
        self.btn_remove.clicked.connect(self._remove_selected)
        right.addWidget(self.btn_remove)

        h.addLayout(left, 2)
        h.addLayout(right, 1)

    def _apply_theme(self):
        apply_dialog_style(self)


    # ------------------------------------------------------------------
    def _on_date_activated(self, qdate: QDate):
        self._open_add_dialog(qdate)

    def _add_for_selected_date(self):
        self._open_add_dialog(self.calendar.selectedDate())

    def _open_add_dialog(self, qdate: QDate):
        dlg = ReminderDialog(qdate, self)
        if dlg.exec() == QDialog.Accepted:
            text = dlg.get_text()
            if not text:
                return
            dt = dlg.get_datetime()
            yearly = dlg.is_yearly()
            add_reminder(dt, text, recur_yearly=yearly)
            extra = " (jaarlijks)" if yearly else ""
            get_voice().speak(
                f"Herinnering opgeslagen voor {dt.strftime('%H:%M op %d %B')}{extra}."
            )
            self._refresh_reminders()

    def _refresh_reminders(self):
        self.lst.clear()
        rems = get_reminders()
        if not rems:
            item = QListWidgetItem(_("calendar_no_reminders"))
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
            self.lst.addItem(item)
            return
        for r_id, dt, text, notified, recur in rems:
            prefix = "✓ " if notified else ("🔁 " if recur else "● ")
            text_short = text[:80] + "..." if len(text) > 80 else text
            label = f"{prefix}{dt.strftime('%a %d %b %H:%M')} - {text_short}"
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, r_id)
            if notified:
                font = item.font()
                font.setItalic(True)
                item.setFont(font)
            self.lst.addItem(item)

        # Markeer dagen met herinneringen in de kalender
        fmt = QTextCharFormat()
        fmt.setBackground(QColor("#707070"))
        fmt.setForeground(QColor("#ffffff"))
        for r_id, dt, text, notified, recur in rems:
            qd = QDate(dt.year, dt.month, dt.day)
            self.calendar.setDateTextFormat(qd, fmt)

    def _remove_selected(self):
        item = self.lst.currentItem()
        if not item:
            return
        r_id = item.data(Qt.UserRole)
        if r_id is None:
            return
        ans = QMessageBox.question(self, "Bevestig", "Deze herinnering verwijderen?")
        if ans == QMessageBox.Yes:
            remove_reminder(int(r_id))
            self._refresh_reminders()


# ========================================================================
# UI: search window  (was: ui/search_window.py)
# ========================================================================

class SearchWorker(QThread):
    """
    Voert de zoek-pipeline uit op een achtergrond-thread zodat de UI niet
    bevriest. Emit progress-signalen en uiteindelijk een finished_result.
    """
    progress = Signal(str)
    finished_result = Signal(dict)

    def __init__(self, query: str):
        super().__init__()
        self.query = query

    def run(self):

        tried = []  # houd bij wat geprobeerd is voor diagnostiek

        # 1) Smart APIs
        self.progress.emit("📚  Ik zoek in mijn naslagwerken (Wikipedia, recepten)...")
        try:
            smart = try_smart_search(self.query)
            if smart:
                self.finished_result.emit({"kind": "smart", "data": smart, "tried": tried})
                return
            tried.append("naslagwerken: geen treffer")
        except Exception as e:
            print(f"[search_worker] smart_apis fout: {e}")
            tried.append(f"naslagwerken: fout ({type(e).__name__})")

        # 2) Ollama
        if config.get("use_ollama", False):
            model = config.get("ollama_model", "")
            # Vereenvoudig "llama3.2:latest" → "llama3.2"
            model_display = model.split(":")[0] if model else "lokaal model"
            self.progress.emit(f"🧠  {model_display} denkt na over uw vraag...")
            try:
                answer = ollama_chat(self.query, timeout=90)
                if answer:
                    self.finished_result.emit({"kind": "ollama", "data": answer, "tried": tried})
                    return
                tried.append(f"AI ({model_display}): leeg antwoord")
            except Exception as e:
                print(f"[search_worker] ollama fout: {e}")
                tried.append(f"AI ({model_display}): fout ({type(e).__name__})")
        else:
            tried.append("AI: staat uit")

        # 3) Zoekmachines
        engine = config.get("default_search_engine", "duckduckgo")
        self.progress.emit(f"🌐  Ik raadpleeg de zoekmachines ({engine} eerst)...")
        try:
            results = web_search(self.query, max_results=3)
            if results:
                self.finished_result.emit({"kind": "web", "data": results, "tried": tried})
                return
            tried.append("zoekmachines: geen resultaten (mogelijk geblokkeerd)")
        except Exception as e:
            print(f"[search_worker] web_search fout: {e}")
            tried.append(f"zoekmachines: fout ({type(e).__name__})")

        self.finished_result.emit({"kind": "none", "data": None, "tried": tried})


class _SearchInputEdit(QPlainTextEdit):
    """
    Subclass van QPlainTextEdit zodat Enter een zoekopdracht stuurt
    in plaats van een nieuwe regel. Shift+Enter blijft een newline geven.
    """

    def __init__(self, parent_window):
        super().__init__()
        self._parent_window = parent_window

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if event.modifiers() & Qt.ShiftModifier:
                # Shift+Enter = gewone newline
                super().keyPressEvent(event)
                return
            # Enter = vraag stellen
            if self._parent_window is not None:
                self._parent_window._on_ask()
            return
        super().keyPressEvent(event)


class SearchWindow(QWidget):
    """Zoekvenster dat verschijnt bij Shift+V of vanuit het tray-menu."""

    open_in_browser = Signal(str)  # url om in browser te openen

    def __init__(self):
        super().__init__()
        self.setWindowTitle(_("search_title"))
        self.setMinimumSize(700, 320)
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)

        self._last_url = None
        self._last_url_is_file = False
        self._last_query = ""
        self._butler_ref = None
        self._search_worker = None
        self._voice = get_voice()
        self._setup_ui()
        self._apply_theme()

    def set_butler_ref(self, butler):
        """Verbind de butler-widget zodat we boek-animaties kunnen triggeren."""
        self._butler_ref = butler

    # ------------------------------------------------------------------
    def _setup_ui(self):
        font_size = config.get("font_size", 16)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel(_("search_title"))
        title_font = QFont("Segoe UI", font_size + 4, QFont.Bold)
        title.setFont(title_font)
        title.setObjectName("title")
        layout.addWidget(title)

        # Tekstveld - groot voor goede zichtbaarheid
        # Enter = vraag stellen, Shift+Enter = nieuwe regel
        self.text_input = _SearchInputEdit(self)
        self.text_input.setPlaceholderText(_("search_placeholder"))
        input_font = QFont("Segoe UI", font_size + 2)
        self.text_input.setFont(input_font)
        self.text_input.setFixedHeight(110)
        layout.addWidget(self.text_input)

        # Status/antwoord-label
        self.status = QLabel("")
        self.status.setFont(QFont("Segoe UI", font_size))
        self.status.setWordWrap(True)
        self.status.setObjectName("status")
        layout.addWidget(self.status)

        # Knoppen
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.btn_ask = QPushButton(_("btn_ask"))
        self.btn_ask.setFont(QFont("Segoe UI", font_size, QFont.Bold))
        self.btn_ask.setMinimumHeight(48)
        self.btn_ask.setMinimumWidth(160)
        self.btn_ask.clicked.connect(self._on_ask)

        self.btn_cancel = QPushButton(_("btn_cancel"))
        self.btn_cancel.setFont(QFont("Segoe UI", font_size))
        self.btn_cancel.setMinimumHeight(48)
        self.btn_cancel.setMinimumWidth(160)
        self.btn_cancel.clicked.connect(self.close)

        # Browser-vraag knoppen (verborgen tot er een resultaat is)
        self.btn_yes = QPushButton("✓  " + _("btn_yes"))
        self.btn_no = QPushButton("✕  " + _("btn_no"))
        self.btn_yes.setMinimumHeight(48)
        self.btn_no.setMinimumHeight(48)
        self.btn_yes.setMinimumWidth(120)
        self.btn_no.setMinimumWidth(120)
        self.btn_yes.setFont(QFont("Segoe UI", font_size, QFont.Bold))
        self.btn_no.setFont(QFont("Segoe UI", font_size, QFont.Bold))
        self.btn_yes.setStyleSheet(
            "QPushButton { background:#2a8a2a; color:#fff; "
            "border:3px solid #4aaa4a; border-radius:6px; padding:6px 16px; }"
            "QPushButton:hover { background:#3a9a3a; }"
        )
        self.btn_no.setStyleSheet(
            "QPushButton { background:#8a2a2a; color:#fff; "
            "border:3px solid #aa4a4a; border-radius:6px; padding:6px 16px; }"
            "QPushButton:hover { background:#9a3a3a; }"
        )
        self.btn_yes.setToolTip("Ja, open dit resultaat in de browser")
        self.btn_no.setToolTip("Nee, geen browser openen")
        self.btn_yes.hide()
        self.btn_no.hide()
        self.btn_yes.clicked.connect(self._on_yes_browser)
        self.btn_no.clicked.connect(self._on_no_browser)

        btn_row.addWidget(self.btn_ask)
        btn_row.addWidget(self.btn_yes)
        btn_row.addWidget(self.btn_no)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_cancel)

        layout.addLayout(btn_row)

        # Toetsenbord shortcuts
        QShortcut(QKeySequence("Ctrl+Return"), self, activated=self._on_ask)
        QShortcut(QKeySequence("Escape"), self, activated=self.close)

    def _apply_theme(self):
        apply_dialog_style(self)


    # ------------------------------------------------------------------
    def showEvent(self, event):
        super().showEvent(event)
        # EU-toegankelijkheid: handje + tooltips
        try:
            apply_accessibility(self)
        except Exception:
            pass
        self.text_input.clear()
        self.status.clear()
        self.btn_yes.hide()
        self.btn_no.hide()
        self.btn_ask.show()
        self._last_url = None
        self._last_url_is_file = False
        # Centreer op scherm
        screen = self.screen() or QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.move(
                geo.center().x() - self.width() // 2,
                geo.center().y() - self.height() // 2,
            )
        # Forceer focus op tekstveld na show + window-activatie. Een korte
        # QTimer is nodig omdat Qt op Windows soms focus pas geeft NA showEvent.
        QTimer.singleShot(50, self._focus_input)

    def _focus_input(self):
        """Focus + cursor in tekstveld zetten."""
        self.activateWindow()
        self.raise_()
        self.text_input.setFocus(Qt.ActiveWindowFocusReason)
        # Cursor naar het einde zetten (in geval er voorbije inhoud was)
        cursor = self.text_input.textCursor()
        cursor.movePosition(cursor.End)
        self.text_input.setTextCursor(cursor)

    # ------------------------------------------------------------------
    # Routing
    # ------------------------------------------------------------------
    def _on_ask(self):
        query = self.text_input.toPlainText().strip()
        if not query:
            return
        self.status.setText(_("searching"))
        self.btn_ask.setEnabled(False)
        QApplication.processEvents()

        try:
            self._route(query)
        finally:
            self.btn_ask.setEnabled(True)

    def _route(self, query: str):
        q_low = query.lower()

        # 1. Quick answers (tijd, datum, rekenen, eenheden)
        quick = try_quick_answer(query)
        if quick:
            self._handle_quick(quick)
            return

        # 2. Te-doen lijst tonen (FIRST, zodat "todo lijst" niet als add geclassificeerd wordt)
        if re.search(r"\b(?:mijn|de)\s+(?:te[- ]?doen[- ]?)?lijst\b", q_low) \
                or re.search(r"\bwat\s+(?:staat\s+er\s+op|moet\s+ik\s+nog\s+doen)\b", q_low) \
                or re.search(r"\btodo\s+lijst\b", q_low) \
                or re.search(r"\bshow\s+(?:my\s+)?(?:todo\s+)?list\b", q_low):
            self._handle_todo_list()
            return

        # 3. Te-doen lijst toevoegen
        todo_add = re.match(
            r"^(?:voeg\s+(?:toe\s+)?aan\s+(?:mijn\s+)?(?:te[- ]doen[- ]?)?lijst[:\s]+|"
            r"te[- ]doen[:\s]+|todo[:\s]+|doe\s+nog[:\s]+|"
            r"add\s+to\s+(?:my\s+)?(?:todo\s+)?list[:\s]+)(.+)$",
            q_low,
        )
        if todo_add:
            real = re.match(
                r"^(?:voeg\s+(?:toe\s+)?aan\s+(?:mijn\s+)?(?:te[- ]doen[- ]?)?lijst[:\s]+|"
                r"te[- ]doen[:\s]+|todo[:\s]+|doe\s+nog[:\s]+|"
                r"add\s+to\s+(?:my\s+)?(?:todo\s+)?list[:\s]+)(.+)$",
                query, re.I,
            )
            self._handle_todo_add(real.group(1) if real else todo_add.group(1))
            return

        # 4. Taak afvinken
        check_match = re.match(
            r"^(?:vink\s+af|afvinken|klaar\s+met|check\s+off|done\s+with)\s+(.+)$",
            q_low,
        )
        if check_match:
            self._handle_todo_check(check_match.group(1))
            return

        # 5. Notitie toevoegen
        note_match = re.match(
            r"^(?:onthoud(?:\s+dat)?|noteer|remember(?:\s+that)?)\s+(.+)$",
            q_low,
        )
        if note_match:
            real = re.match(
                r"^(?:onthoud(?:\s+dat)?|noteer|remember(?:\s+that)?)\s+(.+)$",
                query, re.I,
            )
            self._handle_note_add(real.group(1) if real else note_match.group(1))
            return

        # 6. Notities tonen
        if re.search(r"\b(lees|toon|laat\s+zien|show|list)\b.*\bnotities?\b", q_low) \
                or re.search(r"\bmijn\s+notities?\b", q_low):
            self._handle_notes_list()
            return

        # 7. Notitie vergeten
        forget_match = re.match(
            r"^(?:vergeet|delete|verwijder)\s+(?:de\s+)?notitie\s+(?:over\s+|about\s+)?(.+)$",
            q_low,
        )
        if forget_match:
            self._handle_note_delete(forget_match.group(1))
            return

        # 8. Bestand zoeken
        file_match = re.match(
            r"^(?:zoek|vind|find)\s+(?:het\s+|the\s+)?bestand(?:en)?\s+(.+)$",
            q_low,
        )
        if not file_match:
            file_match = re.match(r"^find\s+files?\s+(.+)$", q_low)
        if file_match:
            self._handle_file_search(file_match.group(1))
            return

        # 9. Expliciete "zoek..." prefix
        search_match = re.match(
            r"^(?:zoek(?:en)?|search|find|suche|cherche)\s+"
            r"(?:voor\s+(?:mij|me)\s+)?"
            r"(?:online\s+)?"
            r"(?:naar\s+|for\s+|nach\s+|op\s+)?"
            r"(?:een\s+|the\s+|de\s+|het\s+|a\s+|an\s+)?"
            r"(.+)$",
            q_low,
        )
        if search_match:
            stripped = re.match(
                r"^(?:zoek(?:en)?|search|find|suche|cherche)\s+"
                r"(?:voor\s+(?:mij|me)\s+)?"
                r"(?:online\s+)?"
                r"(?:naar\s+|for\s+|nach\s+|op\s+)?"
                r"(?:een\s+|the\s+|de\s+|het\s+|a\s+|an\s+)?"
                r"(.+)$",
                query, flags=re.IGNORECASE,
            )
            real_q = stripped.group(1) if stripped else query
            self._handle_web(real_q)
            return

        # 10. "Open <app>" patroon
        open_match = re.match(r"^(?:open|start|launch|begin)\s+(.+)$", q_low)
        if open_match:
            self._handle_app(open_match.group(1))
            return

        # 11. Weer
        if re.search(r"\b(weer|weather|wetter|météo|tiempo|tempo)\b", q_low):
            self._handle_weather(query)
            return

        # 12. Nieuws
        if re.search(r"\b(nieuws|news|nachrichten|actualités|noticias|notizie)\b", q_low):
            self._handle_news(query)
            return

        # 13. Korte input mogelijk een app-naam
        if len(query.split()) <= 2 and "?" not in query and len(query) <= 30:
            if q_low in KNOWN_APPS or find_shortcut(q_low):
                self._handle_app(query)
                return

        # 14. Default: web search
        self._handle_web(query)

    # ------------------------------------------------------------------
    def _handle_quick(self, text: str):
        """Direct antwoord van quick_answers — laat zien en spreek uit."""
        self.status.setText(text)
        self._voice.speak(text)
        # Klein moment laten staan zodat gebruiker het kan lezen, dan dicht
        QTimer.singleShot(3500, self.close)

    def _handle_note_add(self, text: str):
        add_note(text)
        msg = f"Genoteerd: \"{text}\""
        self.status.setText(msg)
        self._voice.speak("Genoteerd.")
        QTimer.singleShot(2000, self.close)

    def _handle_todo_add(self, text: str):
        add_todo(text)
        n = count_open()
        msg = f"Toegevoegd aan uw lijst: \"{text}\"  ({n} openstaand)"
        self.status.setText(msg)
        self._voice.speak(f"Op de lijst gezet. U heeft nu {n} taken openstaan.")
        QTimer.singleShot(2200, self.close)

    def _handle_todo_list(self):
        todos = list_open_todos()
        if not todos:
            msg = "Uw te-doen lijst is leeg. Dat is mooi werk."
            self.status.setText(msg)
            self._voice.speak(msg)
            return
        lines = [f"U heeft {len(todos)} openstaande taken:"]
        spoken_parts = [f"U heeft {len(todos)} openstaande taken."]
        for i, (t_id, dt, text, done) in enumerate(todos[:20], 1):
            lines.append(f"  {i}. {text}")
            if i <= 5:
                spoken_parts.append(f"Taak {i}: {text}.")
        self.status.setText("\n".join(lines))
        self._voice.speak(" ".join(spoken_parts))

    def _handle_todo_check(self, keyword: str):
        n = set_done_by_keyword(keyword)
        if n == 0:
            msg = f"Ik kon geen openstaande taak vinden met '{keyword}'."
        elif n == 1:
            remaining = count_open()
            msg = f"Taak met '{keyword}' afgevinkt. Nog {remaining} openstaand."
        else:
            remaining = count_open()
            msg = f"{n} taken met '{keyword}' afgevinkt. Nog {remaining} openstaand."
        self.status.setText(msg)
        self._voice.speak(msg)
        QTimer.singleShot(2500, self.close)

    def _handle_notes_list(self):
        notes = list_notes()
        if not notes:
            msg = "U heeft geen notities."
            self.status.setText(msg)
            self._voice.speak(msg)
            return
        # Toon ze in de status, spreek max 5 uit
        lines = []
        spoken_parts = [f"U heeft {len(notes)} notities."]
        for i, (note_id, dt, text) in enumerate(notes[:20], 1):
            date_str = dt.strftime("%d %b")
            lines.append(f"{i}. ({date_str}) {text}")
            if i <= 5:
                spoken_parts.append(f"Notitie {i}: {text}.")
        self.status.setText("\n".join(lines))
        self._voice.speak(" ".join(spoken_parts))

    def _handle_note_delete(self, keyword: str):
        n = delete_notes_containing(keyword)
        if n == 0:
            msg = f"Ik vond geen notitie over '{keyword}'."
        elif n == 1:
            msg = f"Notitie over '{keyword}' verwijderd."
        else:
            msg = f"{n} notities over '{keyword}' verwijderd."
        self.status.setText(msg)
        self._voice.speak(msg)
        QTimer.singleShot(2200, self.close)

    def _handle_file_search(self, needle: str):
        self.status.setText(f"Bestanden zoeken: '{needle}'...")
        self._voice.speak(f"Ik zoek bestanden met '{needle}' in de naam.")
        QApplication.processEvents()

        matches = find_files(needle, max_results=15)
        if not matches:
            msg = f"Ik heb geen bestanden met '{needle}' kunnen vinden."
            self.status.setText(msg)
            self._voice.speak(msg)
            return

        # Toon resultaten in status + spreek aantal uit
        lines = [f"Ik vond {len(matches)} bestand(en):"]
        for i, p in enumerate(matches, 1):
            lines.append(f"{i}. {p.name}\n     {p.parent}")
        self.status.setText("\n".join(lines))
        if len(matches) == 1:
            self._voice.speak(f"Ik vond één bestand: {matches[0].name}.")
            # Bied aan om het te openen
            self._last_url = str(matches[0])
            self._last_url_is_file = True
            self._offer_open_file()
        else:
            self._voice.speak(f"Ik vond {len(matches)} bestanden. "
                              f"Het eerste is {matches[0].name}.")
            self._last_url = str(matches[0])
            self._last_url_is_file = True
            self._offer_open_file()

    def _offer_open_file(self):
        """Vraag of het eerste gevonden bestand geopend moet worden."""
        if not self._last_url:
            return
        prompt = "Wilt u het eerste bestand openen?"
        self.status.setText(self.status.text() + "\n\n" + prompt)
        QTimer.singleShot(1800, lambda: self._voice.speak(prompt))
        self.btn_ask.hide()
        self.btn_yes.show()
        self.btn_no.show()

    # ------------------------------------------------------------------
    def _handle_app(self, name: str):
        ok = open_app(name)
        if ok:
            msg = _("opening_app", name=name)
            self.status.setText(msg)
            self._voice.speak(msg)
            QTimer.singleShot(1500, self.close)
        else:
            msg = _("app_not_found", name=name)
            self.status.setText(msg)
            self._voice.speak(msg)

    def _handle_weather(self, query: str):
        city = extract_city(query)
        w = get_weather(city)
        text = _weather_speak_text(w)
        self.status.setText(text)
        self._voice.speak(text)
        # Bied browser-link aan voor succesvolle queries
        if w and "error" not in w:
            self._last_url = f"https://www.google.com/search?q=weer+{w['city']}"
            self._offer_browser()

    def _handle_news(self, query: str = ""):
        text = _news_speak_text(max_items=3, query=query)
        self.status.setText(text)
        self._voice.speak(text)
        # Open eerste nieuwsitem URL als gebruiker dat wil
        items = get_headlines(1, query=query)
        if items:
            self._last_url = items[0][2]
            self._offer_browser()

    def _handle_web(self, query: str):
        """Start een asynchrone zoekactie zodat de UI niet bevriest."""
        from urllib.parse import quote_plus
        self._last_query = query
        self.status.setText(f"🔍  Ik ben aan het zoeken naar: '{query}'  (een ogenblik...)")
        QApplication.processEvents()

        # Laat de butler een boek pakken tijdens het zoeken
        if self._butler_ref is not None:
            try:
                self._butler_ref.start_searching()
            except Exception:
                pass

        # Voorkom dubbele zoekopdrachten
        if hasattr(self, "_search_worker") and self._search_worker is not None \
                and self._search_worker.isRunning():
            return

        self._search_worker = SearchWorker(query)
        self._search_worker.progress.connect(self._on_search_progress)
        self._search_worker.finished_result.connect(self._on_search_done)
        self._search_worker.start()

    def _on_search_progress(self, message: str):
        """Tussenstatus tijdens het zoeken."""
        self.status.setText(message)
        QApplication.processEvents()

    def _on_search_done(self, payload: dict):
        """Wordt aangeroepen wanneer de zoek-thread klaar is."""
        # Boek weer wegstoppen
        if self._butler_ref is not None:
            try:
                self._butler_ref.stop_searching()
            except Exception:
                pass

        kind = payload.get("kind")
        data = payload.get("data")

        if kind == "smart":
            self._handle_smart_result(data)
            return

        if kind == "ollama":
            answer = data
            self.status.setText(answer)
            self._voice.speak(answer)
            self._last_url = get_engine_search_url(self._last_query)
            self._offer_browser()
            return

        if kind == "web":
            results = data
            title, url, snippet = results[0]
            spoken = f"{title}. {snippet}" if snippet else title
            self.status.setText(spoken)
            self._voice.speak(spoken)
            self._last_url = url
            self._offer_browser()
            return

        # Geen resultaten — toon wat geprobeerd is en bied hulp aan
        tried = payload.get("tried", [])
        lines = ["Ik kon helaas niets bruikbaars vinden voor uw vraag."]
        if tried:
            lines.append("")
            lines.append("Wat ik probeerde:")
            for t in tried:
                lines.append(f"  • {t}")
        lines.append("")
        lines.append("Suggesties:")
        lines.append("  • Probeer het over een paar minuten opnieuw")
        lines.append("  • Kies een andere zoekmachine in Instellingen → Browser")
        lines.append("  • Of klik op 'Open in browser' om handmatig te zoeken")
        text = "\n".join(lines)
        self.status.setText(text)
        self._voice.speak(
            "Ik kon niets bruikbaars vinden. U kunt het opnieuw proberen "
            "of de browser openen om zelf te zoeken."
        )
        self._last_url = get_engine_search_url(self._last_query)
        self._offer_browser()

    def _handle_smart_result(self, smart: dict):
        """Toon en spreek een resultaat uit smart APIs (recept/wiki/instant)."""
        kind = smart.get("kind")
        if kind == "recipe":
            self._handle_recipe(smart)
        elif kind in ("wikipedia", "instant_answer"):
            title = smart.get("title", "")
            summary = smart.get("summary", "")
            url = smart.get("url", "")
            source_lbl = "Wikipedia" if kind == "wikipedia" else (smart.get("source") or "")
            tag = f"[{source_lbl}]" if source_lbl else ""
            self.status.setText(f"{tag}  {title}\n\n{summary}")
            # Voor spraak: korter knippen als heel lang
            spoken = summary if len(summary) < 700 else summary[:700].rsplit(". ", 1)[0] + "..."
            self._voice.speak(f"{title}. {spoken}")
            if url:
                self._last_url = url
                self._offer_browser()

    def _handle_recipe(self, recipe: dict):
        """Toon recept met ingrediënten + bereiding."""
        name = recipe.get("name", "")
        ingredients = recipe.get("ingredients", [])
        instructions = recipe.get("instructions", "")
        area = recipe.get("area", "")
        category = recipe.get("category", "")

        lines = [f"Recept: {name}"]
        if area or category:
            lines.append(f"  ({category} — {area})".replace("( — )", "").replace(" — )", ")"))
        lines.append("")
        lines.append("INGREDIËNTEN:")
        for ing in ingredients[:20]:
            lines.append(f"  • {ing}")
        lines.append("")
        lines.append("BEREIDING:")
        # Wrap instructies op ~80 chars per regel
        lines.append(instructions[:2000])
        self.status.setText("\n".join(lines))

        # Voor spraak: korter
        ing_count = len(ingredients)
        spoken_ings = ", ".join(ingredients[:5])
        if ing_count > 5:
            spoken_ings += f", en nog {ing_count - 5} andere ingrediënten"
        # Eerste 2-3 zinnen van de bereiding
        first_instr = re.split(r"\.\s+", instructions)[:2]
        instr_short = ". ".join(first_instr) + ("..." if instructions else "")
        spoken = (
            f"Ik heb een recept gevonden: {name}. "
            f"U heeft nodig: {spoken_ings}. "
            f"Bereiding, kort: {instr_short}. "
            f"De volledige instructie staat in het venster."
        )
        self._voice.speak(spoken)
        if recipe.get("url"):
            self._last_url = recipe["url"]
            self._offer_browser()

    # ------------------------------------------------------------------
    def _offer_browser(self):
        """Vraag of het in de browser getoond moet worden."""
        if not self._last_url:
            return
        prompt = _("show_in_browser")
        # Voeg vraag toe aan status
        self.status.setText(self.status.text() + "\n\n" + prompt)
        # Wacht een kort moment om audio niet over elkaar te laten praten
        QTimer.singleShot(2200, lambda: self._voice.speak(prompt))
        self.btn_ask.hide()
        self.btn_yes.show()
        self.btn_no.show()

    def _on_yes_browser(self):
        if not self._last_url:
            self.close()
            return
        if getattr(self, "_last_url_is_file", False):
            # Open een lokaal bestand met de standaard-applicatie
            try:
                import os
                if hasattr(os, "startfile"):
                    os.startfile(self._last_url)
                else:
                    import subprocess
                    subprocess.Popen(["xdg-open", self._last_url])
            except Exception as e:
                print(f"[search] bestand openen faalde: {e}")
        else:
            self.open_in_browser.emit(self._last_url)
        self.close()

    def _on_no_browser(self):
        self.btn_yes.hide()
        self.btn_no.hide()
        self.btn_ask.show()
        # Status resetten zodat een nieuwe vraag gesteld kan worden
        self.status.clear()
        self.text_input.clear()
        self.text_input.setFocus()


# ========================================================================
# UI: browser extras (adblock + cookies)  (was: ui/browser_extras.py)
# ========================================================================

# ----------------------------------------------------------------------
# Lijst met bekende reclame- en tracker-domeinen.
# Subdomeinen worden automatisch ook geblokkeerd.
# ----------------------------------------------------------------------
AD_DOMAINS = {
    # Google Ads / Analytics
    "doubleclick.net", "googleadservices.com", "googlesyndication.com",
    "google-analytics.com", "googletagmanager.com", "googletagservices.com",
    "adservice.google.com", "adservice.google.nl", "adservice.google.de",
    "adservice.google.be", "adservice.google.fr",

    # Facebook / Meta tracking
    "connect.facebook.net", "facebook.net",

    # Amazon Ads
    "amazon-adsystem.com",

    # Demand-side platforms / ad exchanges
    "adnxs.com", "appnexus.com",
    "criteo.com", "criteo.net",
    "rubiconproject.com", "pubmatic.com", "openx.net", "openx.com",
    "yieldlab.net", "adform.net", "bidswitch.net", "33across.com",
    "indexexchange.com", "spotxchange.com", "rfihub.com",
    "improvedigital.com", "smartadserver.com", "stickyadstv.com",
    "casalemedia.com", "betweendigital.com", "lijit.com", "yieldmo.com",
    "media.net",

    # Content-recommendation / clickbait
    "taboola.com", "outbrain.com", "revcontent.com", "mgid.com",

    # Analytics & session replay / heatmap
    "scorecardresearch.com", "quantserve.com", "hotjar.com", "hotjar.io",
    "mouseflow.com", "mixpanel.com", "segment.com", "segment.io",
    "fullstory.com", "lucky-orange.com", "crazyegg.com", "smartlook.com",
    "amplitude.com", "heap.io",
    "yandex.ru", "mc.yandex.ru",
    "newrelic.com", "nr-data.net",
    "clarity.ms",

    # Push-notification spam
    "onesignal.com", "pushwoosh.com", "pushpushgo.com",

    # Diverse low-quality ad networks
    "adsterra.com", "propellerads.com", "popads.net", "popcash.net",
    "exoclick.com", "adcash.com",
    "trafficjunky.com", "trafficfactory.biz",
    "smaato.com", "ad-stir.com",

    # Microsoft Ads
    "msads.net", "bingads.microsoft.com",

    # Mobile-attribution / SDK trackers
    "branch.io", "adjust.com", "appsflyer.com", "kochava.com",
}


# ----------------------------------------------------------------------
# JavaScript dat cookie-banners herkent en de "accepteer alles"-knop klikt.
# ----------------------------------------------------------------------
JS_AUTO_COOKIE_ACCEPT = r"""
(function() {
    if (window.__deskbutlerCookieDone) return;

    // Zinnen die we als "match" beschouwen (kleine letters, deelmatching).
    var ACCEPT_PHRASES = [
        // English
        'accept all', 'accept cookies', 'agree to all', 'i agree',
        'allow all', 'got it', 'i accept', 'continue',
        // Dutch
        'accepteer alles', 'alles accepteren', 'accepteren', 'akkoord',
        'ja, ik ga akkoord', 'aanvaarden', 'sta toe', 'cookies toestaan',
        // German
        'alle akzeptieren', 'akzeptieren', 'einverstanden', 'zustimmen',
        'alle annehmen',
        // French
        'tout accepter', "j'accepte", 'accepter',
        // Spanish / Portuguese / Italian
        'aceptar todo', 'aceptar', 'aceitar tudo', 'accetta tutto'
    ];

    // Exact-match korte woorden (anders risico op false positives in lopende tekst).
    var ACCEPT_EXACT = ['ok', 'oke', 'okay', 'accept', 'accepteer', 'agree'];

    // Specifieke ID's / classes van populaire cookie-banner-frameworks.
    var KNOWN_IDS = [
        'onetrust-accept-btn-handler',
        'CybotCookiebotDialogBodyButtonAccept',
        'CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll',
        'CookieBoxSaveButton',
        'didomi-notice-agree-button',
        'tc-accept-all',
        'cookieAccept', 'cookie-accept', 'btn-cookie-accept',
        'acceptCookies', 'accept-cookies'
    ];

    function tryClick() {
        // 1) Bekende ID's
        for (var i = 0; i < KNOWN_IDS.length; i++) {
            var el = document.getElementById(KNOWN_IDS[i]);
            if (el) { el.click(); window.__deskbutlerCookieDone = true; return true; }
        }

        // 2) Tekstmatching op alle klikbare elementen
        var els = document.querySelectorAll(
            'button, a, input[type="button"], input[type="submit"], [role="button"]'
        );
        for (var j = 0; j < els.length; j++) {
            var el2 = els[j];
            if (!el2 || el2.offsetParent === null) continue;
            var text = (el2.innerText || el2.value || el2.textContent || '');
            text = text.trim().toLowerCase();
            if (!text || text.length > 80) continue;

            for (var k = 0; k < ACCEPT_PHRASES.length; k++) {
                if (text.indexOf(ACCEPT_PHRASES[k]) !== -1) {
                    el2.click();
                    window.__deskbutlerCookieDone = true;
                    return true;
                }
            }
            for (var m = 0; m < ACCEPT_EXACT.length; m++) {
                if (text === ACCEPT_EXACT[m]) {
                    el2.click();
                    window.__deskbutlerCookieDone = true;
                    return true;
                }
            }
        }
        return false;
    }

    // Probeer direct en daarna nog enkele keren -
    // sommige banners laden vertraagd in.
    if (tryClick()) return;
    setTimeout(tryClick, 500);
    setTimeout(tryClick, 1500);
    setTimeout(tryClick, 3500);
})();
"""


class AdBlockInterceptor(QWebEngineUrlRequestInterceptor):
    """Onderschept browser-requests en blokkeert bekende ad/tracker-hosts."""

    def __init__(self):
        super().__init__()
        self._blocked = AD_DOMAINS

    def interceptRequest(self, info):
        # Live check op de config — toggle in settings werkt zonder herstart.
        if not config.get("adblock_enabled", True):
            return
        try:
            host = info.requestUrl().host().lower()
        except Exception:
            return
        if not host:
            return
        # Exact-match
        if host in self._blocked:
            info.block(True)
            return
        # Subdomein-match (".doubleclick.net" → "ad.doubleclick.net" wordt geblokkeerd)
        for blocked in self._blocked:
            if host.endswith("." + blocked):
                info.block(True)
                return


# ========================================================================
# UI: browser  (was: ui/browser_window.py)
# ========================================================================

def _get_engine_home() -> str:
    """Geef de homepage van de huidig geselecteerde zoekmachine."""
    try:
        return get_engine_homepage()
    except Exception:
        return "https://duckduckgo.com"


class BrowserTab(QWidget):
    """Eén tabblad met een QWebEngineView."""

    def __init__(self, url: str = "", browser_window=None):
        super().__init__()
        # Referentie naar het hoofdvenster zodat we nieuwe tabs kunnen
        # maken bij links met target="_blank" (zie _LoggingPage.createWindow).
        self._browser_window = browser_window

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.view = QWebEngineView()

        # Custom page-subclass die:
        #   1. console.log/warn/error opvangt → deskbutler.log
        #   2. target="_blank" links opent in nieuwe tab
        #      (zonder dit blijven die kliks zonder effect — een veelvoorkomende
        #       valkuil bij QWebEngineView die zelf geen tab-management heeft)
        from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile

        # Belangrijk: gebruik expliciet het default-profile zodat onze
        # AdBlocker-interceptor en cookies blijven werken
        profile = QWebEngineProfile.defaultProfile()
        outer_browser_window = self._browser_window

        class _LoggingPage(QWebEnginePage):
            def __init__(self, profile_, parent):
                super().__init__(profile_, parent)
                self._browser_window = outer_browser_window

            def javaScriptConsoleMessage(self, level, msg, line, src):
                # level is een JavaScriptConsoleMessageLevel enum — in PySide6
                # is int() er niet direct op toepasbaar. Probeer .value, val
                # terug op 0 (info) als dat ook niet lukt.
                try:
                    lvl = int(level.value) if hasattr(level, "value") else int(level)
                except Exception:
                    lvl = 0
                tags = {0: "INFO", 1: "WARN", 2: "ERR"}
                tag = tags.get(lvl, "?")
                # Beperk lengte zodat log niet ontploft
                m = msg if len(msg) < 400 else msg[:400] + "..."
                try:
                    print(f"[JS {tag}] {m}    ({src}:{line})")
                except Exception:
                    pass

            def createWindow(self, _type):
                """
                Wordt aangeroepen voor target="_blank" links, window.open()
                aanroepen, en midden-klikken. Maak een nieuwe tab en geef
                de page daarvan terug — Qt navigeert de nieuwe URL daar dan
                automatisch heen.
                """
                if self._browser_window is None:
                    print("[browser] createWindow: geen browser-venster bekend, "
                          "link wordt genegeerd")
                    return None
                try:
                    print("[browser] createWindow: nieuwe tab voor link")
                    # Maak nieuwe tab maar zonder URL — Qt zet hem zelf
                    new_tab = BrowserTab(
                        url="", browser_window=self._browser_window
                    )
                    idx = self._browser_window.tabs.addTab(new_tab, "...")
                    self._browser_window.tabs.setCurrentIndex(idx)
                    # Hang signals op zoals open_url dat ook doet
                    new_tab.view.urlChanged.connect(
                        lambda u, t=new_tab: self._browser_window._sync_url(t, u)
                    )
                    new_tab.view.titleChanged.connect(
                        lambda txt, t=new_tab: self._browser_window._sync_title(t, txt)
                    )
                    return new_tab.view.page()
                except Exception as e:
                    print(f"[browser] createWindow faalde: {e}")
                    return None

        self._page = _LoggingPage(profile, self.view)
        self.view.setPage(self._page)

        layout.addWidget(self.view)
        # Bij elke succesvolle pagelaad: cookie-accept JS injecteren als toggle aan staat
        self.view.loadFinished.connect(self._on_load_finished)
        if url:
            self.load(url)


    def showEvent(self, event):
        super().showEvent(event)
        # EU-toegankelijkheid: handje + tooltips op alle interactieve widgets
        try:
            apply_accessibility(self)
        except Exception:
            pass

    def _on_load_finished(self, ok: bool):
        if not ok:
            return
        if config.get("auto_accept_cookies", True):
            try:
                self.view.page().runJavaScript(JS_AUTO_COOKIE_ACCEPT)
            except Exception as e:
                print(f"[browser] cookie-script faalde: {e}")

        # Pas alle ingeschakelde extensies toe op deze URL
        try:
            self._apply_extensions()
        except Exception as e:
            print(f"[browser] extensies toepassen faalde: {e}")

    def _apply_extensions(self):
        """
        Injecteer CSS + JS van alle ingeschakelde extensies die op de
        huidige URL van toepassing zijn.

        Volgorde:
          1) GM API shim (zodat userscripts GM_xmlhttpRequest etc. hebben)
          2) Per extensie: CSS via <style>-tag, JS in pagina-context
        """
        current_url = self.view.url().toString()
        mgr = get_extensions_manager()
        enabled = mgr.enabled_for_url(current_url)
        if not enabled:
            return

        # Stap 1: GM-shim installeren (eenmalig per pagelaad)
        # Doet niets als al geïnstalleerd.
        try:
            self.view.page().runJavaScript(GM_API_SHIM)
        except Exception as e:
            print(f"[browser] GM shim faalde: {e}")

        # Stap 2: extensies injecteren
        for ext in enabled:
            try:
                if ext.css:
                    js = make_css_inject_js(ext.css)
                    self.view.page().runJavaScript(js)
                if ext.js:
                    self.view.page().runJavaScript(ext.js)
                print(f"[browser] extensie geladen: {ext.name}")
            except Exception as e:
                print(f"[browser] extensie '{ext.name}' faalde: {e}")

    def load(self, url: str):
        if not url.startswith(("http://", "https://", "file://", "about:")):
            # Behandel als zoekopdracht — gebruik gekozen zoekmachine
            url = get_engine_search_url(url)
        self.view.setUrl(QUrl(url))


class BrowserWindow(QMainWindow):
    """Hoofd browser-venster met tabs en navigatiebalk."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(_("browser_title"))
        self.resize(1200, 800)

        # Installeer de adblock-interceptor op het standaard profile
        # (alle tabs gebruiken dit profile).
        self._adblock = AdBlockInterceptor()
        try:
            profile = QWebEngineProfile.defaultProfile()
            profile.setUrlRequestInterceptor(self._adblock)
        except Exception as e:
            print(f"[browser] adblock kon niet installeren: {e}")

        self._setup_ui()
        self._apply_theme()
        self._update_status_indicator()

    def _setup_ui(self):
        font_size = config.get("font_size", 16)

        # Tab widget centraal
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self._close_tab)
        self.tabs.currentChanged.connect(self._on_tab_changed)
        self.setCentralWidget(self.tabs)

        # ---- Status-balk onder in het browser-venster ----
        # Grote, duidelijk zichtbare balk voor downloads en andere
        # achtergrondactiviteiten. Verbergt zichzelf als er niets te zeggen is.
        from PySide6.QtWidgets import QStatusBar, QProgressBar, QLabel as _QLabel
        self._statusbar = QStatusBar()
        self._statusbar.setSizeGripEnabled(False)
        self._statusbar.setStyleSheet(
            "QStatusBar { background:#1e1e1e; border-top:1px solid #3a3a3a; }"
            "QStatusBar::item { border:none; }"
        )
        self.setStatusBar(self._statusbar)

        self._status_label = _QLabel("")
        self._status_label.setFont(QFont("Segoe UI", font_size, QFont.Bold))
        self._status_label.setMinimumHeight(34)
        self._status_label.setStyleSheet(
            "padding:4px 12px; color:#fff; background:transparent;"
        )
        self._statusbar.addWidget(self._status_label, 1)

        self._status_progress = QProgressBar()
        self._status_progress.setMinimum(0)
        self._status_progress.setMaximum(100)
        self._status_progress.setValue(0)
        self._status_progress.setFixedWidth(280)
        self._status_progress.setFixedHeight(22)
        self._status_progress.setFont(QFont("Segoe UI", max(10, font_size - 4)))
        self._status_progress.setStyleSheet(
            "QProgressBar { background:#1e1e1e; border:1px solid #555; "
            "border-radius:4px; text-align:center; color:#fff; }"
            "QProgressBar::chunk { background:#2a8a2a; border-radius:3px; }"
        )
        self._statusbar.addPermanentWidget(self._status_progress)

        # Begin verborgen
        self._status_label.hide()
        self._status_progress.hide()
        self._statusbar.hide()

        # Toolbar
        tb = QToolBar()
        tb.setMovable(False)
        tb.setIconSize(tb.iconSize() * 1.5)
        self.addToolBar(tb)

        big_font = QFont("Segoe UI", font_size, QFont.Bold)

        self.btn_back = QPushButton("◀ " + _("btn_back"))
        self.btn_back.setFont(big_font)
        self.btn_back.setMinimumHeight(40)
        self.btn_back.clicked.connect(lambda: self.current_view() and self.current_view().back())
        tb.addWidget(self.btn_back)

        self.btn_fwd = QPushButton(_("btn_forward") + " ▶")
        self.btn_fwd.setFont(big_font)
        self.btn_fwd.setMinimumHeight(40)
        self.btn_fwd.clicked.connect(lambda: self.current_view() and self.current_view().forward())
        tb.addWidget(self.btn_fwd)

        self.btn_refresh = QPushButton("⟳")
        self.btn_refresh.setFont(big_font)
        self.btn_refresh.setMinimumHeight(40)
        self.btn_refresh.setToolTip(_("btn_refresh"))
        self.btn_refresh.clicked.connect(lambda: self.current_view() and self.current_view().reload())
        tb.addWidget(self.btn_refresh)

        self.btn_home = QPushButton("⌂")
        self.btn_home.setFont(big_font)
        self.btn_home.setMinimumHeight(40)
        self.btn_home.setToolTip(_("btn_home"))
        self.btn_home.clicked.connect(self._go_home)
        tb.addWidget(self.btn_home)

        self.url_bar = QLineEdit()
        self.url_bar.setFont(QFont("Segoe UI", font_size))
        self.url_bar.setMinimumHeight(40)
        self.url_bar.setPlaceholderText(_("browser_url_placeholder"))
        self.url_bar.returnPressed.connect(self._navigate)
        tb.addWidget(self.url_bar)

        self.btn_new_tab = QPushButton("+")
        self.btn_new_tab.setFont(big_font)
        self.btn_new_tab.setMinimumHeight(40)
        self.btn_new_tab.setMinimumWidth(40)
        self.btn_new_tab.setToolTip("Nieuwe tab openen")
        self.btn_new_tab.clicked.connect(lambda: self.open_url(_get_engine_home()))
        tb.addWidget(self.btn_new_tab)

        # Visuele scheidslijn tussen navigatie-knoppen (+) en functie-knoppen
        # (🧩 ☆ ⭐ 🖼️ ⬇️). Maakt de groepering duidelijker — zo zie je in
        # één oogopslag wat bij "tab beheren" en wat bij "extra functies" hoort.
        from PySide6.QtWidgets import QFrame as _QFrame
        separator = _QFrame()
        separator.setFrameShape(_QFrame.VLine)
        separator.setFrameShadow(_QFrame.Sunken)
        separator.setStyleSheet("color:#555; margin:4px 8px;")
        separator.setMinimumHeight(32)
        tb.addWidget(separator)

        # Knop voor extensies-beheer
        self.btn_extensions = QPushButton("🧩")
        self.btn_extensions.setFont(big_font)
        self.btn_extensions.setMinimumHeight(40)
        self.btn_extensions.setMinimumWidth(48)
        self.btn_extensions.setToolTip(
            "Browser-extensies — Dark Reader, advertenties verbergen, "
            "tekst voorlezen, eigen scripts, en meer"
        )
        self.btn_extensions.clicked.connect(self._open_extensions)
        tb.addWidget(self.btn_extensions)

        # Knop voor snel toevoegen van de huidige pagina aan favorieten
        # (komt eerst — eerst toevoegen, dan beheer)
        self.btn_add_fav = QPushButton("☆")
        self.btn_add_fav.setFont(big_font)
        self.btn_add_fav.setMinimumHeight(40)
        self.btn_add_fav.setMinimumWidth(48)
        self.btn_add_fav.setToolTip(
            "Huidige pagina toevoegen aan favorieten"
        )
        self.btn_add_fav.clicked.connect(self._add_current_to_favorites)
        tb.addWidget(self.btn_add_fav)

        # Knop voor favorieten-overzicht / beheer (gevuld sterretje)
        self.btn_favorites = QPushButton("⭐")
        self.btn_favorites.setFont(big_font)
        self.btn_favorites.setMinimumHeight(40)
        self.btn_favorites.setMinimumWidth(48)
        self.btn_favorites.setToolTip(
            "Favorieten — bekijk en beheer al je opgeslagen pagina's"
        )
        self.btn_favorites.clicked.connect(self._show_favorites_menu)
        tb.addWidget(self.btn_favorites)

        # Knop voor afbeeldingspikker
        self.btn_picker = QPushButton("🖼️")
        self.btn_picker.setFont(big_font)
        self.btn_picker.setMinimumHeight(40)
        self.btn_picker.setMinimumWidth(48)
        self.btn_picker.setToolTip(
            "Afbeeldingspikker — bekijk en download alle afbeeldingen "
            "van de huidige pagina"
        )
        self.btn_picker.clicked.connect(self._open_image_picker)
        tb.addWidget(self.btn_picker)

        # Knop voor video/audio downloaden
        self.btn_download = QPushButton("⬇️")
        self.btn_download.setFont(big_font)
        self.btn_download.setMinimumHeight(40)
        self.btn_download.setMinimumWidth(48)
        self.btn_download.setToolTip(
            "Video of audio downloaden van de huidige pagina "
            "(YouTube, TikTok, Vimeo, en honderden andere sites)"
        )
        self.btn_download.clicked.connect(self._show_download_menu)
        tb.addWidget(self.btn_download)

        # Status-indicator voor adblock + cookies (klein label rechtsbovenin)
        self.lbl_status = QLabel("")
        self.lbl_status.setFont(QFont("Segoe UI", max(10, font_size - 4)))
        self.lbl_status.setStyleSheet("color: #909090; padding: 0 8px;")
        self.lbl_status.setToolTip(
            "Adblock en cookie-accept zijn instelbaar via Instellingen → Browser"
        )
        tb.addWidget(self.lbl_status)

        # Shortcuts
        QShortcut(QKeySequence.Refresh, self, activated=lambda: self.current_view() and self.current_view().reload())
        QShortcut(QKeySequence("Ctrl+T"), self, activated=lambda: self.open_url(_get_engine_home()))
        QShortcut(QKeySequence("Ctrl+W"), self, activated=lambda: self._close_tab(self.tabs.currentIndex()))
        QShortcut(QKeySequence("Alt+Left"), self, activated=lambda: self.current_view() and self.current_view().back())
        QShortcut(QKeySequence("Alt+Right"), self, activated=lambda: self.current_view() and self.current_view().forward())

    def _apply_theme(self):
        apply_dialog_style(self)


    # ------------------------------------------------------------------
    def _update_status_indicator(self):
        """Werk de adblock+cookie indicator in de toolbar bij."""
        if not hasattr(self, "lbl_status"):
            return
        parts = []
        if config.get("adblock_enabled", True):
            parts.append("🛡 Adblock")
        if config.get("auto_accept_cookies", True):
            parts.append("🍪 Auto")
        self.lbl_status.setText("  ".join(parts) if parts else "")

    def refresh_extras(self):
        """Aan te roepen door de settings na een toggle-wijziging."""
        self._update_status_indicator()

    # ------------------------------------------------------------------
    def open_url(self, url: str):
        """Open een URL in een nieuwe tab (of als geen tabs: maak er één)."""
        tab = BrowserTab(url, browser_window=self)
        title = "..."
        idx = self.tabs.addTab(tab, title)
        self.tabs.setCurrentIndex(idx)
        tab.view.urlChanged.connect(lambda u, t=tab: self._sync_url(t, u))
        tab.view.titleChanged.connect(lambda t_text, t=tab: self._sync_title(t, t_text))
        self.show()
        self.raise_()
        self.activateWindow()

    def current_view(self):
        widget = self.tabs.currentWidget()
        if isinstance(widget, BrowserTab):
            return widget.view
        return None

    def _navigate(self):
        url = self.url_bar.text().strip()
        if not url:
            return
        if not url.startswith(("http://", "https://", "about:")):
            # Geen . of geen spaties? Dan zoekopdracht; anders prefix met https://
            if "." in url and " " not in url:
                url = "https://" + url
            else:
                url = get_engine_search_url(url)
        view = self.current_view()
        if view is None:
            self.open_url(url)
        else:
            view.setUrl(QUrl(url))

    def _go_home(self):
        view = self.current_view()
        if view:
            view.setUrl(QUrl(_get_engine_home()))
        else:
            self.open_url(_get_engine_home())

    def _open_extensions(self):
        """Open het extensies-beheer-venster."""
        if not hasattr(self, "_ext_win") or self._ext_win is None:
            self._ext_win = ExtensionsWindow(parent=self)
            # Als extensies wijzigen: pas direct toe op alle open tabs
            self._ext_win.extensions_changed.connect(self._reapply_extensions_all_tabs)
        self._ext_win.show()
        self._ext_win.raise_()
        self._ext_win.activateWindow()

    # ------------------------------------------------------------------
    # Favorieten — sterretje (toevoegen) + ⭐ (menu/overzicht)
    # ------------------------------------------------------------------
    def _show_favorites_menu(self):
        """
        Klik op ⭐: toon een dropdown-menu met de favorieten + mappen.
        Optie onderaan: 'Alle favorieten beheren' opent het beheer-venster.
        """
        print("[favorites] ⭐ knop geklikt")
        try:
            from PySide6.QtWidgets import QMenu
            from PySide6.QtCore import QPoint
            mgr = get_favorites_manager()
            print(f"[favorites] manager geladen, totaal: {mgr.total_count()}")

            menu = QMenu(self)
            menu.setStyleSheet(
                "QMenu { background:#2a2a2a; color:#fff; "
                "border:1px solid #555; padding:6px; }"
                "QMenu::item { padding:8px 20px; }"
                "QMenu::item:selected { background:#444; }"
                "QMenu::separator { height:1px; background:#3a3a3a; margin:4px 0; }"
            )

            # Mappen eerst (elk als submenu)
            for folder in mgr.all_folders():
                if not folder["favorites"]:
                    continue
                sub = menu.addMenu(f"📁  {folder['name']}")
                sub.setStyleSheet(menu.styleSheet())
                for fav in folder["favorites"]:
                    label = fav["title"][:60] + ("..." if len(fav["title"]) > 60 else "")
                    act = sub.addAction(f"⭐ {label}")
                    act.triggered.connect(
                        lambda checked=False, url=fav["url"]: self.open_url(url)
                    )

            # Root-favorieten direct
            root = mgr.root_favorites()
            if root:
                if any(f["favorites"] for f in mgr.all_folders()):
                    menu.addSeparator()
                for fav in root[:20]:
                    label = fav["title"][:60] + ("..." if len(fav["title"]) > 60 else "")
                    act = menu.addAction(f"⭐ {label}")
                    act.triggered.connect(
                        lambda checked=False, url=fav["url"]: self.open_url(url)
                    )

            if mgr.total_count() == 0:
                empty = menu.addAction("(nog geen favorieten)")
                empty.setEnabled(False)

            menu.addSeparator()
            act_manage = menu.addAction("📋  Alle favorieten beheren...")
            act_manage.triggered.connect(self._open_favorites_window)

            # Toon onder de knop
            pos = self.btn_favorites.mapToGlobal(
                QPoint(0, self.btn_favorites.height())
            )
            print(f"[favorites] menu tonen op {pos.x()},{pos.y()}")
            menu.exec(pos)
            print("[favorites] menu gesloten")
        except Exception as e:
            import traceback
            print(f"[favorites] FOUT in _show_favorites_menu: {e}")
            traceback.print_exc()
            self._popup_info(
                "Fout bij favorieten",
                f"Er ging iets mis bij het tonen van het menu:\n\n{e}"
            )

    def _add_current_to_favorites(self):
        """Snel toevoegen van de huidige pagina (uses pagina-titel automatisch)."""
        print("[favorites] ☆ knop geklikt")
        try:
            view = self.current_view()
            if not view:
                print("[favorites] geen actieve view")
                self.show_browser_status("Open eerst een pagina",
                                         color="#8a2a2a")
                self.hide_browser_status()
                return
            url = view.url().toString()
            print(f"[favorites] url={url}")
            if not url or url == "about:blank":
                self.show_browser_status("Geen pagina om op te slaan",
                                         color="#8a2a2a")
                self.hide_browser_status()
                return
            title = ""
            try:
                title = view.page().title() or ""
            except Exception as e:
                print(f"[favorites] kon titel niet ophalen: {e}")
            if not title:
                title = url
            print(f"[favorites] titel: {title!r}")

            mgr = get_favorites_manager()

            # Check of het al een favoriet is
            if mgr.is_favorited(url):
                print("[favorites] is al favoriet")
                self.show_browser_status(
                    "⭐ Deze pagina staat al in je favorieten",
                    color="#cc9966"
                )
                self.hide_browser_status()
                return

            # Voeg toe aan root (gebruiker kan later naar map verplaatsen)
            fav_id = mgr.add(title, url)
            print(f"[favorites] add resultaat: {fav_id}")
            if fav_id:
                self.show_browser_status(
                    f"⭐ Toegevoegd: {title[:60]}",
                    color="#2a8a2a"
                )
                self.hide_browser_status()
                print(f"[favorites] toegevoegd: {title} → {url}")
            else:
                self.show_browser_status(
                    "Kon niet toevoegen",
                    color="#8a2a2a"
                )
                self.hide_browser_status()
        except Exception as e:
            import traceback
            print(f"[favorites] FOUT in _add_current_to_favorites: {e}")
            traceback.print_exc()
            self._popup_info(
                "Fout bij toevoegen",
                f"Er ging iets mis bij het toevoegen:\n\n{e}"
            )

    def _open_favorites_window(self):
        """Open het beheer-venster voor favorieten."""
        print("[favorites] beheer-venster openen...")
        try:
            if not hasattr(self, "_fav_win") or self._fav_win is None:
                self._fav_win = FavoritesWindow(parent=self)
                self._fav_win.favorite_opened.connect(self.open_url)
            else:
                # Herlaad de lijst (kan gewijzigd zijn intussen)
                self._fav_win._populate()
            self._fav_win.show()
            self._fav_win.raise_()
            self._fav_win.activateWindow()
            print("[favorites] beheer-venster getoond")
        except Exception as e:
            import traceback
            print(f"[favorites] FOUT in _open_favorites_window: {e}")
            traceback.print_exc()
            self._popup_info(
                "Fout bij openen",
                f"Het favorieten-venster kon niet worden geopend:\n\n{e}"
            )

    # ------------------------------------------------------------------
    # Afbeeldingspikker — alle afbeeldingen van de huidige pagina
    # ------------------------------------------------------------------
    def _open_image_picker(self):
        """Verzamel alle afbeeldingen van de huidige pagina en toon de picker."""
        from PySide6.QtWidgets import QMessageBox, QApplication
        from PySide6.QtCore import QTimer

        view = self.current_view()
        if not view:
            self._popup_info("Geen pagina",
                             "Open eerst een pagina in een tab.")
            return

        url = view.url().toString()
        if not url or url == "about:blank":
            self._popup_info("Geen pagina",
                             "Deze tab heeft geen pagina geladen.")
            return

        print(f"[picker] afbeeldingen ophalen van pagina: {url}")
        self.show_browser_status("🔍 Afbeeldingen op pagina verzamelen...",
                                 color="#0a6dc2")


        # Een safety-net: als de callback NIET binnen 8 seconden komt,
        # meld dat aan de gebruiker (in plaats van eeuwig te wachten).
        self._picker_callback_received = False

        def on_result(images):
            """JS-callback: ontvangt de lijst van afbeeldingen.
            
            Belangrijk: Qt's PySide6 marshaling kan het JS-resultaat als 
            JSON-string OF als list teruggeven, afhankelijk van versie. 
            Onze JavaScript geeft tegenwoordig JSON.stringify() terug, dus
            de callback moet beide formats accepteren.
            """
            import json as _json
            self._picker_callback_received = True
            print(f"[picker] callback aangeroepen, type={type(images).__name__}")
            self.hide_browser_status(delay_ms=200)

            if images is None:
                print("[picker] callback kreeg None terug (JS-fout?)")
                self._popup_info(
                    "JavaScript-fout",
                    "Het verzamelen van afbeeldingen mislukte. "
                    "Probeer de pagina te verversen en het opnieuw."
                )
                return

            # Parse JSON-string indien nodig
            if isinstance(images, str):
                print(f"[picker] resultaat is string ({len(images)} chars), JSON parsen...")
                try:
                    images = _json.loads(images)
                    print(f"[picker] JSON parse OK, type nu: {type(images).__name__}")
                except Exception as e:
                    print(f"[picker] JSON parse faalde: {e}")
                    print(f"[picker] eerste 200 chars: {images[:200]!r}")
                    self._popup_info(
                        "JavaScript-fout",
                        f"De pagina gaf een onleesbaar resultaat terug.\n\n"
                        f"Foutmelding: {e}"
                    )
                    return

            if not isinstance(images, list):
                print(f"[picker] onverwacht type: {images!r}")
                self._popup_info(
                    "Onverwacht resultaat",
                    f"De pagina gaf een onverwacht resultaat terug. "
                    f"Type: {type(images).__name__}"
                )
                return

            # Check op fatale JS-fout vlag
            if images and isinstance(images[0], dict) and \
                    images[0].get("src") == "_error_":
                err = images[0].get("source", "onbekend")
                print(f"[picker] JS-fatal: {err}")
                self._popup_info(
                    "JavaScript-fout op pagina",
                    f"De pagina blokkeert het uitlezen van afbeeldingen:\n\n{err}"
                )
                return

            print(f"[picker] {len(images)} afbeeldingen gevonden")
            for i, img in enumerate(images[:5]):
                print(f"  {i}: {img.get('source', '?')} "
                      f"{img.get('width', 0)}x{img.get('height', 0)} "
                      f"{img.get('src', '?')[:80]}")
            if len(images) > 5:
                print(f"  ... en {len(images) - 5} meer")

            if not images:
                self._popup_info(
                    "Geen afbeeldingen gevonden",
                    "Op deze pagina kon ik geen afbeeldingen vinden.\n\n"
                    "Mogelijke redenen:\n"
                    "  • De pagina is nog niet volledig geladen\n"
                    "  • De afbeeldingen worden dynamisch geladen "
                    "(scroll eerst naar beneden)\n"
                    "  • De website gebruikt een ongebruikelijke techniek"
                )
                return

            # Open picker venster
            print("[picker] ImagePickerWindow openen...")
            try:
                self._picker_win = ImagePickerWindow(images, parent=self)
                self._picker_win.show()
                self._picker_win.raise_()
                self._picker_win.activateWindow()
                QApplication.processEvents()
                print("[picker] venster getoond")
            except Exception as e:
                import traceback
                print(f"[picker] picker openen faalde: {e}")
                traceback.print_exc()
                self._popup_info(
                    "Fout bij openen",
                    f"Het afbeeldingen-venster kon niet worden geopend:\n\n{e}"
                )

        # Safety-net timer: als callback niet binnen 8s komt
        def safety_check():
            if not self._picker_callback_received:
                print("[picker] !!! Callback kwam NIET binnen 8 seconden")
                self.hide_browser_status(delay_ms=0)
                self._popup_info(
                    "Geen reactie van pagina",
                    "De pagina reageert niet binnen 8 seconden. "
                    "Mogelijk blokkeert de site JavaScript-uitvoering. "
                    "Probeer de pagina te verversen."
                )

        QTimer.singleShot(8000, safety_check)

        try:
            view.page().runJavaScript(COLLECT_IMAGES_JS, on_result)
            print("[picker] JS geïnjecteerd, wacht op callback...")
        except Exception as e:
            print(f"[picker] JS-injectie faalde: {e}")
            self.hide_browser_status(delay_ms=0)
            self._popup_info("Fout", f"JavaScript starten mislukt: {e}")

    def _popup_info(self, title: str, message: str):
        """
        Toon een eenvoudige info-dialoog die GEGARANDEERD bovenop komt.
        QMessageBox kan soms achter andere vensters verdwijnen — dit
        is een eigen QDialog met expliciete WindowStaysOnTopHint flag.
        """
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import (
            QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        )
        from PySide6.QtGui import QFont

        dlg = QDialog(self, Qt.Dialog | Qt.WindowStaysOnTopHint)
        dlg.setWindowTitle(title)
        dlg.setMinimumSize(520, 220)
        apply_dialog_style(dlg)

        big = base_font()
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title_lbl = QLabel(title)
        title_lbl.setFont(title_font())
        layout.addWidget(title_lbl)

        msg_lbl = QLabel(message)
        msg_lbl.setFont(big)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet(
            "background:#2a2a2a; padding:14px; border-radius:6px; color:#d0d0d0;"
        )
        layout.addWidget(msg_lbl, 1)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_ok = QPushButton("✓  OK")
        btn_ok.setFont(QFont("Segoe UI", big.pointSize(), QFont.Bold))
        btn_ok.setMinimumHeight(48)
        btn_ok.setMinimumWidth(140)
        btn_ok.setStyleSheet(
            "QPushButton { background:#2a8a2a; color:#fff; "
            "border:3px solid #4aaa4a; border-radius:6px; padding:6px 16px; }"
            "QPushButton:hover { background:#3a9a3a; }"
        )
        btn_ok.clicked.connect(dlg.accept)
        btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)

        apply_accessibility(dlg)
        # Forceer top-level zichtbaarheid
        dlg.show()
        dlg.raise_()
        dlg.activateWindow()
        dlg.exec()

    # ------------------------------------------------------------------
    # Video / audio downloaden (yt-dlp)
    # ------------------------------------------------------------------
    def _show_download_menu(self):
        """Toon een popup-menu met download-opties bij klik op ⬇️."""
        from PySide6.QtWidgets import QMenu
        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu { background:#2a2a2a; color:#fff; "
            "border:1px solid #555; padding:6px; }"
            "QMenu::item { padding:10px 24px; }"
            "QMenu::item:selected { background:#444; }"
        )
        act_video = menu.addAction("🎬  Video downloaden (MP4)")
        act_audio = menu.addAction("🎵  Audio downloaden (MP3)")
        menu.addSeparator()
        act_check = menu.addAction("🔄  Controleer op updates van hulpprogramma's")
        act_open_folder = menu.addAction("📂  Open downloads-map")

        # Toon onder de knop
        from PySide6.QtCore import QPoint
        pos = self.btn_download.mapToGlobal(QPoint(0, self.btn_download.height()))
        chosen = menu.exec(pos)
        if chosen == act_video:
            self._start_download("mp4")
        elif chosen == act_audio:
            self._start_download("mp3")
        elif chosen == act_check:
            self._check_tools_updates()
        elif chosen == act_open_folder:
            self._open_downloads_folder()

    def _start_download(self, mode: str):
        """Start een download van de huidige tab (mode: 'mp4' of 'mp3')."""
        from PySide6.QtWidgets import QMessageBox, QDialog
        from PySide6.QtCore import QTimer
        print(f"[download] knop geklikt, mode={mode}")

        view = self.current_view()
        if not view:
            print("[download] geen actieve view")
            QMessageBox.information(self, "Geen pagina",
                                    "Open eerst een video-pagina in een tab.")
            return
        url = view.url().toString()
        print(f"[download] url={url}")
        if not url or url == "about:blank":
            QMessageBox.information(self, "Geen URL",
                                    "Deze tab heeft geen pagina geladen.")
            return

        # Stap 1: zijn yt-dlp + ffmpeg geïnstalleerd?
        installed = tools_are_installed()
        print(f"[download] tools_are_installed: {installed}")
        print(f"[download] yt-dlp pad: {get_yt_dlp_path()}")
        print(f"[download] ffmpeg map: {get_ffmpeg_dir()}")

        if not installed:
            ask = YesNoDialog(
                question=(
                    "Om video's en muziek te downloaden heb ik eenmalig "
                    "twee hulpprogramma's nodig: yt-dlp en ffmpeg. "
                    "Ze worden gedownload naar de map 'tools' bij DeskButler "
                    "(in totaal ongeveer 95 MB).\n\n"
                    "Wilt u dat ik ze nu installeer?"
                ),
                title="Hulpprogramma's installeren?",
                yes_text="Ja, installeren",
                no_text="Nee, later",
                parent=self,
            )
            print("[download] vraag-dialoog openen...")
            res = ask.exec()
            print(f"[download] vraag-dialoog resultaat: {res} (Accepted={QDialog.Accepted})")
            if res != QDialog.Accepted:
                print("[download] gebruiker zei nee, stoppen")
                return

            # Eerst dialoog tonen, dan pas thread starten
            install_dlg = ToolsInstallDialog(parent=self)
            install_dlg.show()
            # Laat Qt de dialoog daadwerkelijk schilderen voordat we
            # de thread starten — anders kan een hele snelle download
            # klaar zijn voordat de UI op het scherm staat.
            from PySide6.QtWidgets import QApplication
            QApplication.processEvents()
            print("[download] install-dialoog getoond, thread starten...")

            # Verbind ook met onze statusbalk onderaan zodat zichtbaar
            # blijft als de gebruiker dialoog wegklikt
            self.show_browser_status("⬇️ Hulpprogramma's downloaden...",
                                     percent=0, color="#0a6dc2")

            def _install_status(text, pct):
                self.show_browser_status(f"⬇️ {text}", percent=pct,
                                         color="#0a6dc2")

            install_dlg._thread_status_callback = _install_status
            install_dlg.start_install()
            # Hook de signal-emit zodat we ook de browser-status updaten
            try:
                install_dlg._thread.progress.connect(_install_status)
            except Exception as e:
                print(f"[download] kon status-signal niet koppelen: {e}")

            res2 = install_dlg.exec()
            print(f"[download] install-dialoog resultaat: {res2}")
            if res2 != QDialog.Accepted:
                print("[download] installatie geannuleerd/mislukt")
                self.show_browser_status("❌ Installatie geannuleerd",
                                         color="#8a2a2a")
                self.hide_browser_status()
                return
            self.show_browser_status("✅ Hulpprogramma's klaar voor gebruik",
                                     color="#2a8a2a")
            self.hide_browser_status()

        # Stap 2: vraag bestandsnaam
        from PySide6.QtWidgets import QFileDialog
        import os

        page_title = ""
        try:
            page_title = view.page().title() or ""
        except Exception:
            pass
        default_name = safe_filename(page_title) if page_title else "video"
        ext = "mp3" if mode == "mp3" else "mp4"

        # Zorg dat downloads-map BESTAAT (anders faalt getSaveFileName)
        dl_dir = get_downloads_dir()
        os.makedirs(str(dl_dir), exist_ok=True)
        default_path = os.path.join(str(dl_dir), f"{default_name}.{ext}")
        print(f"[download] default opslag: {default_path}")

        kind_label = "MP3 (audio)" if mode == "mp3" else "MP4 (video)"
        path, _ = QFileDialog.getSaveFileName(
            self, f"{kind_label} opslaan als...",
            default_path,
            f"{kind_label} bestanden (*.{ext})",
        )
        print(f"[download] gebruiker koos pad: {path!r}")
        if not path:
            return

        # Stap 3: open voortgangs-dialoog EERST, daarna thread
        dl_dialog = VideoDownloadDialog(url, path, mode, parent=self)
        dl_dialog.show()
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()
        print("[download] voortgang-dialoog getoond, download starten...")

        # Status onderaan browser ook bijhouden
        kind_icon = "🎬" if mode == "mp4" else "🎵"
        self.show_browser_status(f"{kind_icon} Download voorbereiden...",
                                 percent=0, color="#0a6dc2")

        def _on_status(text):
            self.show_browser_status(f"{kind_icon} {text}",
                                     percent=self._status_progress.value(),
                                     color="#0a6dc2")

        def _on_pct(pct):
            self.show_browser_status(
                self._status_label.text() or f"{kind_icon} Downloaden...",
                percent=pct, color="#0a6dc2"
            )

        def _on_done(ok, msg):
            if ok:
                import os as _os
                self.show_browser_status(
                    f"✅ Klaar! {_os.path.basename(msg)} opgeslagen",
                    color="#2a8a2a"
                )
            else:
                self.show_browser_status(f"❌ {msg}", color="#8a2a2a")
            self.hide_browser_status()

        dl_dialog.start_download()
        # Hook in op de worker-signals (via de dialog)
        try:
            dl_dialog._worker.status_update.connect(_on_status)
            dl_dialog._worker.progress_percent.connect(_on_pct)
            dl_dialog._worker.finished_dl.connect(_on_done)
        except Exception as e:
            print(f"[download] kon worker-signals niet koppelen: {e}")

    def _open_downloads_folder(self):
        """Open de downloads-map in de OS-bestandsbeheerder."""
        import os, sys, subprocess
        path = get_downloads_dir()
        try:
            if os.name == "nt":
                os.startfile(str(path))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(path)])
            else:
                subprocess.Popen(["xdg-open", str(path)])
        except Exception as e:
            print(f"[browser] open downloads-map faalde: {e}")

    def _check_tools_updates(self):
        """
        Controleer of yt-dlp (en ffmpeg-info) bijgewerkt kunnen worden.
        Toont een dialoog met de huidige en nieuwste versie.
        """
        from PySide6.QtWidgets import QMessageBox, QApplication, QDialog

        if not get_yt_dlp_path():
            QMessageBox.information(
                self, "Niet geïnstalleerd",
                "yt-dlp en ffmpeg zijn nog niet geïnstalleerd. "
                "Klik op een download-optie om ze te installeren."
            )
            return

        self.show_browser_status("🔍 Controleren op updates...",
                                 color="#0a6dc2")
        QApplication.processEvents()

        # Huidige versies ophalen
        cur_ytdlp = get_yt_dlp_version() or "?"
        cur_ffmpeg = get_ffmpeg_version() or "?"
        # Nieuwste yt-dlp van GitHub
        latest_ytdlp = get_latest_yt_dlp_version()

        self.hide_browser_status(delay_ms=100)

        # Bepaal of er een update nodig is
        ytdlp_in_tools = yt_dlp_is_in_tools_dir()
        update_available = (
            latest_ytdlp
            and latest_ytdlp != cur_ytdlp
            and cur_ytdlp != "?"
        )

        # Bouw bericht
        lines = ["**Hulpprogramma's status**", ""]
        lines.append(f"📺 yt-dlp")
        lines.append(f"   Huidige versie: {cur_ytdlp}")
        if latest_ytdlp:
            lines.append(f"   Nieuwste versie op GitHub: {latest_ytdlp}")
        else:
            lines.append("   Kon nieuwste versie niet ophalen (geen internet?)")
        lines.append("")
        lines.append(f"🎞️ ffmpeg")
        lines.append(f"   Huidige versie: {cur_ffmpeg}")
        lines.append("   (Updates voor ffmpeg worden niet automatisch gecheckt — "
                     "alleen handmatig via 'opnieuw installeren')")
        msg = "\n".join(lines)

        if update_available:
            if ytdlp_in_tools:
                # We kunnen het vervangen
                ask = YesNoDialog(
                    question=(
                        f"{msg}\n\nEr is een nieuwere yt-dlp beschikbaar "
                        f"({latest_ytdlp}). Wilt u nu updaten?"
                    ),
                    title="Update beschikbaar",
                    yes_text="Ja, updaten",
                    no_text="Nu niet",
                    parent=self,
                )
                if ask.exec() != QDialog.Accepted:
                    return
                self._start_ytdlp_update()
            else:
                # yt-dlp is via PATH gevonden (bv. via pip) — wij kunnen het
                # niet automatisch updaten zonder pip-install te doen
                QMessageBox.information(
                    self, "Update beschikbaar",
                    f"{msg}\n\n"
                    f"Er is een nieuwere yt-dlp beschikbaar ({latest_ytdlp}).\n\n"
                    "Uw yt-dlp is via uw systeem (PATH) gevonden, niet via "
                    "DeskButler's eigen tools-map. Voor updates:\n\n"
                    "  • Via pip: open een terminal en typ "
                    "'pip install -U yt-dlp'\n"
                    "  • Of: verwijder de systeem-versie en gebruik de "
                    "ingebouwde install van DeskButler."
                )
        else:
            QMessageBox.information(
                self, "Up-to-date" if latest_ytdlp else "Status",
                f"{msg}\n\n"
                + ("✅ yt-dlp is up-to-date." if latest_ytdlp == cur_ytdlp
                   else "")
            )

    def _start_ytdlp_update(self):
        """Start de update-thread en toon voortgang in de statusbar."""
        from PySide6.QtWidgets import QMessageBox

        self.show_browser_status("⬇️ yt-dlp updaten...", percent=0,
                                 color="#0a6dc2")
        self._ytdlp_update_thread = YtDlpUpdateThread(parent=self)

        def on_progress(text, pct):
            self.show_browser_status(f"⬇️ {text}", percent=pct,
                                     color="#0a6dc2")

        def on_done(ok, error):
            if ok:
                self.show_browser_status(
                    "✅ yt-dlp bijgewerkt naar nieuwste versie",
                    color="#2a8a2a"
                )
            else:
                self.show_browser_status(f"❌ Update mislukt: {error}",
                                         color="#8a2a2a")
                QMessageBox.warning(self, "Update mislukt", error)
            self.hide_browser_status()

        self._ytdlp_update_thread.progress.connect(on_progress)
        self._ytdlp_update_thread.finished_update.connect(on_done)
        self._ytdlp_update_thread.start()

    # ------------------------------------------------------------------
    # Statusbalk onder in browser (voor downloads en andere acties)
    # ------------------------------------------------------------------
    def show_browser_status(self, text: str, percent: int = None,
                            color: str = "#2a8a2a"):
        """
        Toon een statusbericht onderaan de browser. Optioneel met
        voortgangsbalk-percentage en accentkleur.

        Voorbeeld:
          self.show_browser_status("⬇️ Downloaden 45%", percent=45)
        """
        self._statusbar.show()
        self._status_label.setText(text)
        self._status_label.setStyleSheet(
            f"padding:4px 12px; color:#fff; background:{color};"
        )
        self._status_label.show()
        if percent is not None:
            self._status_progress.setValue(max(0, min(100, percent)))
            self._status_progress.setStyleSheet(
                "QProgressBar { background:#1e1e1e; border:1px solid #555; "
                "border-radius:4px; text-align:center; color:#fff; }"
                f"QProgressBar::chunk {{ background:{color}; border-radius:3px; }}"
            )
            self._status_progress.show()
        else:
            self._status_progress.hide()

    def hide_browser_status(self, delay_ms: int = 4000):
        """Verberg de statusbalk na een korte vertraging."""
        from PySide6.QtCore import QTimer
        QTimer.singleShot(delay_ms, self._status_label.hide)
        QTimer.singleShot(delay_ms, self._status_progress.hide)
        QTimer.singleShot(delay_ms, self._statusbar.hide)

    def _reapply_extensions_all_tabs(self):
        """Herlaad alle tabs zodat nieuwe extensie-instellingen meteen effect hebben."""
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if w and hasattr(w, "view"):
                try:
                    w.view.reload()
                except Exception:
                    pass

    def _close_tab(self, index: int):
        # Stop EERST de inhoud van deze tab (anders blijft media spelen!)
        try:
            w = self.tabs.widget(index)
            if w and hasattr(w, "view"):
                # Naar leeg laden: stopt video/audio
                w.view.setUrl(QUrl("about:blank"))
        except Exception as e:
            print(f"[browser] tab stoppen faalde: {e}")

        if self.tabs.count() <= 1:
            # Laatste tab dicht: alles netjes opruimen en venster verbergen
            self._stop_all_tabs()
            self.hide()
            return
        self.tabs.removeTab(index)

    def _stop_all_tabs(self):
        """Stop alle tabs (laad about:blank om media te stoppen)."""
        for i in range(self.tabs.count()):
            try:
                w = self.tabs.widget(i)
                if w and hasattr(w, "view"):
                    w.view.setUrl(QUrl("about:blank"))
            except Exception as e:
                print(f"[browser] stop tab {i} faalde: {e}")

    def closeEvent(self, event):
        """
        Wanneer het browser-venster wordt gesloten (X-knop): stop ALLE
        actieve tabs zodat geen video of muziek op de achtergrond blijft
        spelen. We sluiten alleen de tabs, het venster zelf wordt verborgen
        (zodat heropenen snel gaat).
        """
        try:
            self._stop_all_tabs()
        except Exception as e:
            print(f"[browser] closeEvent stop tabs faalde: {e}")
        # Verberg in plaats van echt sluiten, zodat heropenen direct werkt
        # (DeskButler app blijft draaien op de achtergrond)
        event.ignore()
        self.hide()

    def _on_tab_changed(self, index: int):
        view = self.current_view()
        if view:
            self.url_bar.setText(view.url().toString())

    def _sync_url(self, tab: BrowserTab, url: QUrl):
        if self.tabs.currentWidget() is tab:
            self.url_bar.setText(url.toString())

    def _sync_title(self, tab: BrowserTab, title: str):
        idx = self.tabs.indexOf(tab)
        if idx >= 0:
            short = title[:30] + "..." if len(title) > 30 else title
            self.tabs.setTabText(idx, short or "...")


# ========================================================================
# UI: email  (was: ui/email_window.py)
# ========================================================================

# ----------------------------------------------------------------------
# Account dialog
# ----------------------------------------------------------------------
class AccountDialog(QDialog):
    """Wizard voor het toevoegen van een nieuw mail-account."""

    PRESETS = {
        "Gmail (wachtwoord)": dict(
            imap_host="imap.gmail.com", imap_port=993,
            smtp_host="smtp.gmail.com", smtp_port=465, smtp_starttls=False,
            protocol="imap", auth="password",
        ),
        "Outlook.com (wachtwoord)": dict(
            imap_host="outlook.office365.com", imap_port=993,
            smtp_host="smtp-mail.outlook.com", smtp_port=587, smtp_starttls=True,
            protocol="imap", auth="password",
        ),
        "Yahoo (wachtwoord)": dict(
            imap_host="imap.mail.yahoo.com", imap_port=993,
            smtp_host="smtp.mail.yahoo.com", smtp_port=465, smtp_starttls=False,
            protocol="imap", auth="password",
        ),
        "Gmail (OAuth)": dict(
            imap_host="imap.gmail.com", imap_port=993,
            smtp_host="smtp.gmail.com", smtp_port=465, smtp_starttls=False,
            protocol="imap", auth="oauth_gmail",
        ),
        "Outlook (OAuth)": dict(
            imap_host="outlook.office365.com", imap_port=993,
            smtp_host="smtp.office365.com", smtp_port=587, smtp_starttls=True,
            protocol="imap", auth="oauth_outlook",
        ),
        "POP3 (handmatig)": dict(protocol="pop3", auth="password"),
        "Handmatig IMAP": dict(protocol="imap", auth="password"),
    }

    def __init__(self, parent=None, existing: dict = None):
        super().__init__(parent)
        title = "Account bewerken" if existing else _("email_add_account")
        self.setWindowTitle(title)
        self.setMinimumWidth(640)
        self.setMinimumHeight(560)

        apply_dialog_style(self)
        big_font = base_font()

        layout = QFormLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.preset = QComboBox()
        self.preset.setFont(big_font)
        self.preset.addItems(list(self.PRESETS.keys()))
        self.preset.currentTextChanged.connect(self._apply_preset)
        lbl_type = QLabel("Type:")
        lbl_type.setFont(big_font)
        layout.addRow(lbl_type, self.preset)

        self.name = QLineEdit()
        self.name.setFont(big_font)
        self.name.setPlaceholderText("bv. Mijn werkmail")
        lbl_name = QLabel("Naam:")
        lbl_name.setFont(big_font)
        layout.addRow(lbl_name, self.name)

        self.email = QLineEdit()
        self.email.setFont(big_font)
        self.email.setPlaceholderText("naam@voorbeeld.nl")
        lbl_email = QLabel("E-mailadres:")
        lbl_email.setFont(big_font)
        layout.addRow(lbl_email, self.email)

        self.password = QLineEdit()
        self.password.setFont(big_font)
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("Wachtwoord (bij OAuth: laat leeg)")
        lbl_pwd = QLabel("Wachtwoord:")
        lbl_pwd.setFont(big_font)
        layout.addRow(lbl_pwd, self.password)

        self.imap_host = QLineEdit()
        self.imap_host.setFont(big_font)
        lbl_imap = QLabel("IMAP server:")
        lbl_imap.setFont(big_font)
        layout.addRow(lbl_imap, self.imap_host)
        self.imap_port = QLineEdit("993")
        self.imap_port.setFont(big_font)
        lbl_imap_p = QLabel("IMAP poort:")
        lbl_imap_p.setFont(big_font)
        layout.addRow(lbl_imap_p, self.imap_port)

        self.smtp_host = QLineEdit()
        self.smtp_host.setFont(big_font)
        lbl_smtp = QLabel("SMTP server:")
        lbl_smtp.setFont(big_font)
        layout.addRow(lbl_smtp, self.smtp_host)
        self.smtp_port = QLineEdit("465")
        self.smtp_port.setFont(big_font)
        lbl_smtp_p = QLabel("SMTP poort:")
        lbl_smtp_p.setFont(big_font)
        layout.addRow(lbl_smtp_p, self.smtp_port)

        info = QLabel(
            "Tip: voor Gmail/Outlook met wachtwoord heb je een 'app-wachtwoord' nodig.\n"
            "Voor OAuth: zie README voor het opzetten van client_id."
        )
        info.setFont(big_font)
        info.setWordWrap(True)
        info.setStyleSheet("color: #a0a0a0; padding: 12px;")
        layout.addRow(info)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.setFont(big_font)
        # Maak knoppen groter
        for btn in buttons.buttons():
            btn.setFont(big_font)
            btn.setMinimumHeight(50)
            btn.setMinimumWidth(120)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        if existing:
            self._load_existing(existing)
        else:
            self._apply_preset(self.preset.currentText())

    def _load_existing(self, acc: dict):
        # Match preset op auth + protocol
        target_auth = acc.get("auth", "password")
        target_proto = acc.get("protocol", "imap")
        chosen_key = None
        for key, p in self.PRESETS.items():
            if p.get("auth") == target_auth and p.get("protocol") == target_proto \
                    and p.get("imap_host") == acc.get("imap_host"):
                chosen_key = key
                break
        if not chosen_key:
            chosen_key = "Handmatig IMAP" if target_proto == "imap" else "POP3 (handmatig)"

        # Blokkeer signaal tijdens setText om _apply_preset niet te triggeren
        self.preset.blockSignals(True)
        self.preset.setCurrentText(chosen_key)
        self.preset.blockSignals(False)

        self.name.setText(acc.get("name", ""))
        self.email.setText(acc.get("email", ""))
        self.password.setText(acc.get("password", ""))
        self.imap_host.setText(acc.get("imap_host", ""))
        self.imap_port.setText(str(acc.get("imap_port", 993)))
        self.smtp_host.setText(acc.get("smtp_host", ""))
        self.smtp_port.setText(str(acc.get("smtp_port", 465)))

    def _apply_preset(self, key: str):
        preset = self.PRESETS.get(key, {})
        if "imap_host" in preset:
            self.imap_host.setText(preset["imap_host"])
            self.imap_port.setText(str(preset["imap_port"]))
        if "smtp_host" in preset:
            self.smtp_host.setText(preset["smtp_host"])
            self.smtp_port.setText(str(preset["smtp_port"]))

    def get_account(self) -> dict:
        key = self.preset.currentText()
        preset = self.PRESETS.get(key, {})
        return {
            "name": self.name.text().strip() or self.email.text().strip(),
            "email": self.email.text().strip(),
            "password": self.password.text(),
            "imap_host": self.imap_host.text().strip(),
            "imap_port": int(self.imap_port.text().strip() or "993"),
            "smtp_host": self.smtp_host.text().strip(),
            "smtp_port": int(self.smtp_port.text().strip() or "465"),
            "smtp_starttls": preset.get("smtp_starttls", False),
            "protocol": preset.get("protocol", "imap"),
            "auth": preset.get("auth", "password"),
        }


# ----------------------------------------------------------------------
# Compose dialog
# ----------------------------------------------------------------------
class ComposeDialog(QDialog):
    """Nieuwe e-mail opstellen."""

    def __init__(self, account: dict, parent=None,
                 to: str = "", subject: str = "", body: str = ""):
        super().__init__(parent)
        self.account = account
        self.setWindowTitle(_("email_compose"))
        self.resize(700, 500)

        font_size = config.get("font_size", 16)
        big_font = QFont("Segoe UI", font_size)
        self.setFont(big_font)

        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.to = QLineEdit(to)
        form.addRow(QLabel(_("email_to") + ":"), self.to)
        self.subject = QLineEdit(subject)
        form.addRow(QLabel(_("email_subject") + ":"), self.subject)
        layout.addLayout(form)

        self.body = QPlainTextEdit(body)
        self.body.setFont(QFont("Segoe UI", font_size))
        layout.addWidget(self.body, 1)

        # ---- Bijlagen ----
        self._attachments: list = []
        self.lbl_attachments_header = QLabel("📎 Bijlagen (0):")
        self.lbl_attachments_header.setFont(QFont("Segoe UI", font_size, QFont.Bold))
        self.lbl_attachments_header.setStyleSheet("color: #c0c0c0; padding: 6px 0 2px 0;")
        layout.addWidget(self.lbl_attachments_header)

        self.lst_attachments = QListWidget()
        self.lst_attachments.setFont(QFont("Segoe UI", font_size))
        self.lst_attachments.setMaximumHeight(110)
        self.lst_attachments.setStyleSheet(
            "QListWidget { background:#2a2a2a; color:#f5f5f5; border:1px solid #555; }"
            "QListWidget::item { padding: 6px; }"
            "QListWidget::item:selected { background-color: #707070; color: #ffffff; }"
        )
        self.lst_attachments.itemDoubleClicked.connect(self._remove_attachment)
        layout.addWidget(self.lst_attachments)

        btn_row = QHBoxLayout()
        btn_attach = QPushButton("📎 Bijlage toevoegen")
        btn_attach.setMinimumHeight(40)
        btn_attach.clicked.connect(self._add_attachment)
        btn_row.addWidget(btn_attach)

        btn_remove = QPushButton("✕ Geselecteerde bijlage verwijderen")
        btn_remove.setMinimumHeight(40)
        btn_remove.clicked.connect(self._remove_selected_attachment)
        btn_row.addWidget(btn_remove)
        btn_row.addStretch()

        btn_send = QPushButton(_("email_send"))
        btn_send.setMinimumHeight(40)
        btn_send.setStyleSheet("background-color: #707070; color: #ffffff; font-weight: bold; padding: 6px 24px;")
        btn_send.clicked.connect(self._send)
        btn_row.addWidget(btn_send)

        btn_cancel = QPushButton(_("btn_cancel"))
        btn_cancel.setMinimumHeight(40)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)

        layout.addLayout(btn_row)

    def _add_attachment(self):
        files, _ok = QFileDialog.getOpenFileNames(self, "Kies bijlage(s)")
        if not files:
            return
        from pathlib import Path
        for f in files:
            self._attachments.append(f)
            size = ""
            try:
                kb = Path(f).stat().st_size / 1024
                size = f"  ({kb:.1f} KB)" if kb < 1024 else f"  ({kb/1024:.1f} MB)"
            except OSError:
                pass
            name = f.split("/")[-1].split("\\")[-1]
            self.lst_attachments.addItem(f"📎 {name}{size}")
        self.lbl_attachments_header.setText(f"📎 Bijlagen ({len(self._attachments)}):")

    def _remove_attachment(self, item):
        """Dubbelklik op een bijlage verwijdert hem."""
        row = self.lst_attachments.row(item)
        if 0 <= row < len(self._attachments):
            self._attachments.pop(row)
            self.lst_attachments.takeItem(row)
            self.lbl_attachments_header.setText(f"📎 Bijlagen ({len(self._attachments)}):")

    def _remove_selected_attachment(self):
        row = self.lst_attachments.currentRow()
        if row >= 0:
            self._remove_attachment(self.lst_attachments.currentItem())

    def _send(self):
        to_addrs = [a.strip() for a in self.to.text().split(",") if a.strip()]
        if not to_addrs:
            QMessageBox.warning(self, "Fout", "Geen ontvanger ingevuld.")
            return
        if not self.account.get("smtp_host"):
            QMessageBox.warning(self, "Fout", "Dit account heeft geen SMTP-configuratie.")
            return
        client = SMTPClient(
            self.account["smtp_host"],
            self.account["smtp_port"],
            self.account["email"],
            self.account.get("password", ""),
            use_starttls=self.account.get("smtp_starttls", False),
        )
        ok = client.send(
            from_addr=self.account["email"],
            to_addrs=to_addrs,
            subject=self.subject.text(),
            body=self.body.toPlainText(),
            attachments=self._attachments,
        )
        if ok:
            QMessageBox.information(self, "OK", _("email_sent_ok"))
            get_voice().speak(_("email_sent_ok"))
            self.accept()
        else:
            QMessageBox.warning(self, "Fout", _("email_send_error"))
            get_voice().speak(_("email_send_error"))


# ----------------------------------------------------------------------
# Background fetcher (om UI niet te bevriezen)
# ----------------------------------------------------------------------
class FetchWorker(QObject):
    finished = Signal(list)   # lijst EmailMessage
    error = Signal(str)

    def __init__(self, account: dict, folder: str = "INBOX", limit: int = 30):
        super().__init__()
        self.account = account
        self.folder = folder
        self.limit = limit
        self.cancel = False  # gezet door GUI bij sluiten — voorkomt hang

    def run(self):
        try:
            if self.cancel:
                return
            acc = self.account
            if acc.get("protocol") == "pop3":
                with POP3Client(acc["imap_host"], acc["imap_port"],
                                acc["email"], acc["password"]) as c:
                    msgs = c.fetch_recent(self.limit)
            else:
                with IMAPClient(acc["imap_host"], acc["imap_port"],
                                acc["email"], acc["password"]) as c:
                    msgs = c.fetch_recent(self.folder, self.limit)
            if self.cancel:
                return
            self.finished.emit(msgs)
        except Exception as e:
            if not self.cancel:
                self.error.emit(str(e))


# ----------------------------------------------------------------------
# Email window
# ----------------------------------------------------------------------
class EmailWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(_("email_title"))
        # Adaptieve grootte: max 1300x800 maar nooit groter dan 90% van scherm
        from PySide6.QtWidgets import QApplication as _QApp
        screen = _QApp.primaryScreen()
        if screen:
            avail = screen.availableGeometry()
            target_w = min(1300, int(avail.width() * 0.9))
            target_h = min(800, int(avail.height() * 0.9))
        else:
            target_w, target_h = 1100, 700
        self.resize(target_w, target_h)
        self.setMinimumSize(720, 500)

        self._accounts = load_accounts()
        self._current_account = None
        self._current_folder = "INBOX"
        self._messages: list = []
        self._current_message: EmailMessage | None = None
        self._fetch_thread: QThread | None = None

        self._setup_ui()
        self._apply_theme()
        self._populate_accounts()

    def showEvent(self, event):
        super().showEvent(event)
        # EU-toegankelijkheid: zorg dat alle knoppen handje + tooltips hebben
        # (gedaan bij showEvent omdat sommige sub-widgets pas later worden gemaakt)
        try:
            apply_accessibility(self)
        except Exception:
            pass
        # Centreer op het scherm zodat hij nooit half buiten beeld zit
        try:
            from PySide6.QtWidgets import QApplication as _QApp
            screen = self.screen() or _QApp.primaryScreen()
            if screen:
                geo = screen.availableGeometry()
                self.move(
                    geo.center().x() - self.width() // 2,
                    geo.center().y() - self.height() // 2,
                )
        except Exception as e:
            print(f"[email] centreren faalde: {e}")
        # Auto-refresh bij heropenen: ververs de berichten als er al een
        # account/folder geselecteerd is (gebruiker hoeft niet te klikken)
        try:
            if self._current_account is not None:
                self._fetch_messages()
            elif self._accounts and self.lst_accounts.count() >= 2:
                # Geen huidige selectie maar wel accounts: selecteer eerste inbox
                inbox_item = self.lst_accounts.item(1)
                if inbox_item:
                    self.lst_accounts.setCurrentItem(inbox_item)
                    self._on_account_or_folder(inbox_item)
        except Exception as e:
            print(f"[email] auto-refresh faalde: {e}")

    def closeEvent(self, event):
        """
        Stop netjes de achtergrond-IMAP-thread voordat het venster sluit.
        Voorkomt dat de app bevriest terwijl Qt wacht tot de thread klaar is
        (kan minuten duren bij een trage of niet-responsief antwoordende
        mailserver).
        """
        try:
            if self._fetch_thread is not None:
                if self._fetch_thread.isRunning():
                    print("[email] fetch-thread is nog bezig, vragen te stoppen...")
                    # Signaal aan de worker dat hij moet stoppen
                    if hasattr(self, "_worker") and self._worker is not None:
                        try:
                            self._worker.cancel = True
                        except Exception:
                            pass
                    # Vraag de thread netjes te quitten
                    self._fetch_thread.quit()
                    # Wacht maximaal 1 seconde — anders gewoon doorgaan
                    if not self._fetch_thread.wait(1000):
                        print("[email] thread reageert niet, force-terminate")
                        self._fetch_thread.terminate()
                        self._fetch_thread.wait(500)
                self._fetch_thread = None
                self._worker = None
        except Exception as e:
            print(f"[email] close cleanup faalde: {e}")
        super().closeEvent(event)

    # ------------------------------------------------------------------
    def _setup_ui(self):
        font_size = config.get("font_size", 16)
        big_font = QFont("Segoe UI", font_size)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(8, 8, 8, 8)

        # Toolbar: in TWEE rijen, anders zijn knoppen te smal voor de tekst.
        # Rij 1 = accountbeheer, Rij 2 = mail-acties.
        tb_row1 = QHBoxLayout()
        tb_row1.setSpacing(8)
        tb_row2 = QHBoxLayout()
        tb_row2.setSpacing(8)

        # --- Rij 1: account-beheer ---
        self.btn_add_account = QPushButton("➕  " + _("email_add_account"))
        self.btn_add_account.setMinimumHeight(44)
        self.btn_add_account.setMinimumWidth(180)
        self.btn_add_account.setFont(big_font)
        self.btn_add_account.clicked.connect(self._add_account_clicked)
        tb_row1.addWidget(self.btn_add_account)

        self.btn_edit_account = QPushButton("✏️  Account bewerken")
        self.btn_edit_account.setMinimumHeight(44)
        self.btn_edit_account.setMinimumWidth(180)
        self.btn_edit_account.setFont(big_font)
        self.btn_edit_account.clicked.connect(self._edit_account_clicked)
        tb_row1.addWidget(self.btn_edit_account)

        self.btn_remove_account = QPushButton("✕  Account verwijderen")
        self.btn_remove_account.setMinimumHeight(44)
        self.btn_remove_account.setMinimumWidth(200)
        self.btn_remove_account.setFont(big_font)
        self.btn_remove_account.clicked.connect(self._remove_account_clicked)
        tb_row1.addWidget(self.btn_remove_account)

        tb_row1.addStretch()

        # --- Rij 2: mail-acties ---
        self.btn_refresh = QPushButton("⟳  " + _("email_refresh"))
        self.btn_refresh.setMinimumHeight(44)
        self.btn_refresh.setMinimumWidth(140)
        self.btn_refresh.setFont(big_font)
        self.btn_refresh.clicked.connect(self._refresh)
        tb_row2.addWidget(self.btn_refresh)

        self.btn_compose = QPushButton("✉  " + _("email_compose"))
        self.btn_compose.setMinimumHeight(44)
        self.btn_compose.setMinimumWidth(160)
        self.btn_compose.setFont(big_font)
        self.btn_compose.clicked.connect(self._compose)
        tb_row2.addWidget(self.btn_compose)

        self.btn_reply = QPushButton("↩  " + _("email_reply"))
        self.btn_reply.setMinimumHeight(44)
        self.btn_reply.setMinimumWidth(160)
        self.btn_reply.setFont(big_font)
        self.btn_reply.clicked.connect(self._reply)
        tb_row2.addWidget(self.btn_reply)

        self.btn_forward = QPushButton("↪  " + _("email_forward"))
        self.btn_forward.setMinimumHeight(44)
        self.btn_forward.setMinimumWidth(140)
        self.btn_forward.setFont(big_font)
        self.btn_forward.clicked.connect(self._forward)
        tb_row2.addWidget(self.btn_forward)

        self.btn_delete = QPushButton("✕  " + _("email_delete"))
        self.btn_delete.setMinimumHeight(44)
        self.btn_delete.setMinimumWidth(140)
        self.btn_delete.setFont(big_font)
        self.btn_delete.clicked.connect(self._delete)
        tb_row2.addWidget(self.btn_delete)

        self.btn_speak = QPushButton("🔊  Voorlezen")
        self.btn_speak.setMinimumHeight(44)
        self.btn_speak.setMinimumWidth(140)
        self.btn_speak.setFont(big_font)
        self.btn_speak.clicked.connect(self._speak_message)
        tb_row2.addWidget(self.btn_speak)

        tb_row2.addStretch()

        root.addLayout(tb_row1)
        root.addLayout(tb_row2)

        # Splitter met 3 panelen
        splitter = QSplitter(Qt.Horizontal)
        root.addWidget(splitter, 1)

        # Linker paneel: accounts/folders
        left = QWidget()
        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(0, 0, 0, 0)
        left_lay.addWidget(QLabel("Accounts & mappen:"))
        self.lst_accounts = QListWidget()
        self.lst_accounts.setFont(big_font)
        self.lst_accounts.itemClicked.connect(self._on_account_or_folder)
        left_lay.addWidget(self.lst_accounts)
        splitter.addWidget(left)

        # Midden paneel: berichtenlijst
        mid = QWidget()
        mid_lay = QVBoxLayout(mid)
        mid_lay.setContentsMargins(0, 0, 0, 0)
        self.lbl_messages = QLabel("Berichten:")
        mid_lay.addWidget(self.lbl_messages)
        self.lst_messages = QListWidget()
        self.lst_messages.setFont(big_font)
        self.lst_messages.currentRowChanged.connect(self._on_message_selected)
        mid_lay.addWidget(self.lst_messages)
        splitter.addWidget(mid)

        # Rechter paneel: berichtweergave
        right = QWidget()
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(0, 0, 0, 0)
        self.lbl_header = QLabel("")
        self.lbl_header.setFont(QFont("Segoe UI", font_size, QFont.Bold))
        self.lbl_header.setWordWrap(True)
        self.lbl_header.setStyleSheet("padding: 8px; background: #2a2a2a; color: #707070;")
        right_lay.addWidget(self.lbl_header)

        # Bijlagen-paneel (verschijnt alleen als er bijlagen zijn)
        self.attachments_panel = QWidget()
        self.attachments_layout = QHBoxLayout(self.attachments_panel)
        self.attachments_layout.setContentsMargins(8, 4, 8, 4)
        self.attachments_layout.setSpacing(6)
        self.attachments_panel.setStyleSheet(
            "background: #2a2a2a; border-top: 1px solid #444; border-bottom: 1px solid #444;"
        )
        right_lay.addWidget(self.attachments_panel)
        self.attachments_panel.hide()

        self.view = QWebEngineView()
        # Donkere placeholder zodat het witte vlak niet pijn aan de ogen doet
        # voordat een bericht wordt geselecteerd
        self.view.setHtml(self._placeholder_html())
        right_lay.addWidget(self.view, 1)
        splitter.addWidget(right)

        splitter.setSizes([280, 380, 640])

        # Shortcuts
        QShortcut(QKeySequence("Ctrl+N"), self, activated=self._compose)
        QShortcut(QKeySequence("F5"), self, activated=self._refresh)
        QShortcut(QKeySequence("Delete"), self, activated=self._delete)
        QShortcut(QKeySequence("Ctrl+R"), self, activated=self._reply)

    def _apply_theme(self):
        apply_dialog_style(self)


    # ------------------------------------------------------------------
    def _populate_accounts(self):
        self.lst_accounts.clear()
        if not self._accounts:
            item = QListWidgetItem(_("email_no_account"))
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
            self.lst_accounts.addItem(item)
            return
        for i, acc in enumerate(self._accounts):
            item = QListWidgetItem(f"📧 {acc.get('name', acc.get('email'))}")
            item.setData(Qt.UserRole, ("account", i))
            self.lst_accounts.addItem(item)
            # Folders (standaard alleen INBOX direct, andere bij selectie laden)
            inbox = QListWidgetItem(f"   📥 {_('email_inbox')}")
            inbox.setData(Qt.UserRole, ("folder", i, "INBOX"))
            self.lst_accounts.addItem(inbox)

        # AUTO-SELECT: kies de eerste INBOX zodat mail meteen wordt opgehaald
        # bij het openen van het venster (gebruiker hoeft niet handmatig te klikken)
        if self.lst_accounts.count() >= 2:
            inbox_item = self.lst_accounts.item(1)  # eerste inbox-item
            if inbox_item:
                self.lst_accounts.setCurrentItem(inbox_item)
                # itemClicked vuurt niet op programmatic select; direct aanroepen:
                self._on_account_or_folder(inbox_item)

    def _on_account_or_folder(self, item: QListWidgetItem):
        data = item.data(Qt.UserRole)
        if not data:
            return
        if data[0] == "account":
            self._current_account = self._accounts[data[1]]
            self._current_folder = "INBOX"
            self._load_folders_for_current()
        elif data[0] == "folder":
            self._current_account = self._accounts[data[1]]
            self._current_folder = data[2]
            self._fetch_messages()

    def _load_folders_for_current(self):
        """Bij selectie van account: haal de echte folder-lijst op."""
        if not self._current_account:
            return
        acc = self._current_account
        if acc.get("protocol") != "imap":
            self._fetch_messages()
            return

        # Doe IMAP-list op de achtergrond
        def work():
            try:
                with IMAPClient(acc["imap_host"], acc["imap_port"],
                                acc["email"], acc["password"]) as c:
                    folders = c.list_folders()
                # Update UI in mainthread via signal:
                # eenvoudshalve via QTimer.singleShot
                from PySide6.QtCore import QTimer
                QTimer.singleShot(0, lambda: self._show_folders(folders))
            except Exception as e:
                print(f"[email] folders ophalen faalde: {e}")
                from PySide6.QtCore import QTimer
                QTimer.singleShot(0, self._fetch_messages)

        threading.Thread(target=work, daemon=True).start()
        # Direct alvast INBOX laden:
        self._fetch_messages()

    def _show_folders(self, folders: list):
        if not self._current_account:
            return
        idx = self._accounts.index(self._current_account)
        # Zoek de account-rij en vervang de folder-items
        # Verwijder bestaande folder-items van dit account
        i = 0
        rows_to_remove = []
        found_account = False
        while i < self.lst_accounts.count():
            it = self.lst_accounts.item(i)
            data = it.data(Qt.UserRole)
            if not data:
                i += 1
                continue
            if data[0] == "account" and data[1] == idx:
                found_account = True
                i += 1
                continue
            if found_account and data[0] == "folder" and data[1] == idx:
                rows_to_remove.append(i)
                i += 1
                continue
            if found_account and data[0] == "account":
                break
            i += 1
        for r in reversed(rows_to_remove):
            self.lst_accounts.takeItem(r)

        # Voeg folders in op de juiste plek
        insert_pos = idx_of_account = None
        for r in range(self.lst_accounts.count()):
            it = self.lst_accounts.item(r)
            data = it.data(Qt.UserRole)
            if data and data[0] == "account" and data[1] == idx:
                insert_pos = r + 1
                break
        if insert_pos is None:
            return
        for folder in folders:
            if folder.upper() == "INBOX":
                continue  # al ingevoegd
            it = QListWidgetItem(f"   📁 {folder}")
            it.setData(Qt.UserRole, ("folder", idx, folder))
            self.lst_accounts.insertItem(insert_pos, it)
            insert_pos += 1

    def _fetch_messages(self):
        if not self._current_account:
            return
        self.lst_messages.clear()
        self.lbl_messages.setText(f"Berichten in {self._current_folder} (laden...)")
        # Start worker in QThread
        if self._fetch_thread and self._fetch_thread.isRunning():
            return
        self._fetch_thread = QThread()
        self._worker = FetchWorker(self._current_account, self._current_folder, 30)
        self._worker.moveToThread(self._fetch_thread)
        self._fetch_thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_messages_loaded)
        self._worker.error.connect(self._on_fetch_error)
        self._worker.finished.connect(self._fetch_thread.quit)
        self._worker.error.connect(self._fetch_thread.quit)
        self._fetch_thread.start()

    def _on_messages_loaded(self, msgs: list):
        self._messages = msgs
        self.lst_messages.clear()
        self.lbl_messages.setText(f"Berichten in {self._current_folder} ({len(msgs)})")
        for m in msgs:
            prefix = "● " if not m.is_read else "  "
            sender_short = m.from_addr[:40] + "..." if len(m.from_addr) > 40 else m.from_addr
            subject_short = (m.subject[:60] + "...") if len(m.subject) > 60 else m.subject
            item = QListWidgetItem(f"{prefix}{sender_short}\n   {subject_short}")
            font = item.font()
            if not m.is_read:
                font.setBold(True)
            item.setFont(font)
            self.lst_messages.addItem(item)

    def _on_fetch_error(self, err: str):
        QMessageBox.warning(self, "Fout", f"Kon mail niet ophalen:\n{err}")
        self.lbl_messages.setText("Fout bij ophalen.")
        get_voice().speak("Ik kon uw e-mail niet ophalen.")

    def _placeholder_html(self) -> str:
        """
        HTML voor de leeg-state van de mail-viewer. Donker thema in plaats
        van een wit vlak — dat is rustiger voor de ogen (de gebruiker wachtte
        anders op het laden of na het sluiten van een bericht in een fel
        wit veld).
        """
        return """
        <!DOCTYPE html>
        <html><head><meta charset="utf-8"><style>
        html, body {
            background: #1e1e1e;
            color: #c0c0c0;
            font-family: 'Segoe UI', sans-serif;
            margin: 0; padding: 0;
            height: 100%;
        }
        .container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            text-align: center;
            padding: 40px;
        }
        .icon { font-size: 72px; margin-bottom: 16px; opacity: 0.75; }
        h1 {
            font-size: 28px;
            font-weight: 600;
            margin: 0 0 12px 0;
            color: #e0e0e0;
        }
        p {
            font-size: 17px;
            margin: 4px 0;
            color: #909090;
            line-height: 1.5;
        }
        .accent { color: #b0b0b0; }
        </style></head>
        <body>
          <div class="container">
            <div class="icon">📬</div>
            <h1>DeskButler Mail</h1>
            <p>Selecteer een bericht uit de lijst om het hier te lezen.</p>
            <p class="accent">Tip: klik op een mail-account links om de berichten op te halen.</p>
          </div>
        </body></html>
        """

    def _on_message_selected(self, row: int):
        if row < 0 or row >= len(self._messages):
            self._current_message = None
            self.lbl_header.setText("")
            self.view.setHtml(self._placeholder_html())
            self.attachments_panel.hide()
            return
        msg = self._messages[row]
        self._current_message = msg
        header = (
            f"<b>{_('email_from')}:</b> {html_escape(msg.from_addr)}<br>"
            f"<b>{_('email_to')}:</b> {html_escape(msg.to_addr)}<br>"
            f"<b>{_('email_subject')}:</b> {html_escape(msg.subject)}<br>"
            f"<b>Datum:</b> {html_escape(msg.date)}"
        )
        self.lbl_header.setText(header)

        # Bijlagen-paneel
        self._update_attachments_panel(msg)

        # Toon HTML als beschikbaar, anders text
        if msg.body_html:
            self.view.setHtml(self._sanitize_html(msg.body_html))
        else:
            text = html_escape(msg.body_text or "(geen tekst)")
            self.view.setHtml(
                f"<body style='font-family:Segoe UI; font-size:{config.get('font_size',16)}pt; "
                f"background:#1a1a1a; color:#f5f5f5; padding:16px;'>"
                f"<pre style='white-space: pre-wrap'>{text}</pre></body>"
            )
        # Markeer als gelezen
        if not msg.is_read and self._current_account.get("protocol") == "imap":
            try:
                acc = self._current_account
                with IMAPClient(acc["imap_host"], acc["imap_port"],
                                acc["email"], acc["password"]) as c:
                    c.mark_read(msg.folder, msg.uid, True)
                msg.is_read = True
            except Exception:
                pass

    def _sanitize_html(self, html: str) -> str:
        """Wrap HTML met donker thema voor leesbaarheid bij hoog contrast."""
        if not config.get("high_contrast", True):
            return html
        wrapper = (
            f"<style>body{{background:#1a1a1a;color:#f5f5f5;"
            f"font-family:Segoe UI;font-size:{config.get('font_size',16)}pt;padding:16px;}}"
            f"a{{color:#707070;}}</style>"
        )
        if "<body" in html.lower():
            return re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + wrapper, html, count=1, flags=re.I)
        return wrapper + html

    # ------------------------------------------------------------------
    # Bijlagen in lees-modus
    # ------------------------------------------------------------------
    def _update_attachments_panel(self, msg):
        """Toon klikbare knoppen voor elke bijlage in het ontvangen bericht."""
        # Clear oude knoppen
        while self.attachments_layout.count():
            item = self.attachments_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        attachments = getattr(msg, "attachments", None) or []
        if not attachments:
            self.attachments_panel.hide()
            return

        # Titel-label
        lbl = QLabel(f"📎 {len(attachments)} bijlage{'n' if len(attachments) != 1 else ''}:")
        lbl.setStyleSheet("color: #c0c0c0; padding-right: 8px;")
        font_size = config.get("font_size", 16)
        lbl.setFont(QFont("Segoe UI", font_size, QFont.Bold))
        self.attachments_layout.addWidget(lbl)

        # Per bijlage een knop
        for fname in attachments:
            btn = QPushButton(f"💾 {fname}")
            btn.setFont(QFont("Segoe UI", font_size))
            btn.setMinimumHeight(36)
            btn.setStyleSheet(
                "QPushButton { background:#3a3a3a; color:#f5f5f5; "
                "border:1px solid #707070; border-radius:4px; padding: 4px 12px; }"
                "QPushButton:hover { background:#4a4a4a; }"
            )
            btn.setToolTip(f"Klik om '{fname}' te openen of op te slaan")
            btn.clicked.connect(lambda checked, m=msg, f=fname: self._download_attachment(m, f))
            self.attachments_layout.addWidget(btn)

        self.attachments_layout.addStretch()
        self.attachments_panel.show()

    def _download_attachment(self, msg, filename: str):
        """Download een bijlage uit IMAP en open hem met de standaard-applicatie."""
        if not self._current_account:
            return
        acc = self._current_account
        if acc.get("protocol") != "imap":
            QMessageBox.information(
                self, "Bijlagen",
                "Bijlagen downloaden werkt alleen voor IMAP-accounts."
            )
            return

        # Toon spinner-status
        old_text = self.lbl_header.text()
        self.lbl_header.setText(old_text + f"<br><i>Bijlage '{filename}' ophalen...</i>")
        QApplication.processEvents()

        try:
            with IMAPClient(acc["imap_host"], acc["imap_port"],
                            acc["email"], acc["password"]) as c:
                data = c.fetch_attachment(msg.folder, msg.uid, filename)
        except Exception as e:
            self.lbl_header.setText(old_text)
            QMessageBox.warning(self, "Fout", f"Bijlage ophalen faalde:\n{e}")
            return

        self.lbl_header.setText(old_text)

        if data is None:
            QMessageBox.warning(self, "Niet gevonden",
                                f"Kon bijlage '{filename}' niet vinden in het bericht.")
            return

        # Vraag waar opslaan, default naar gebruiker Downloads
        from pathlib import Path
        default_dir = Path.home() / "Downloads"
        if not default_dir.exists():
            default_dir = Path.home()
        save_path, _ok = QFileDialog.getSaveFileName(
            self, "Bijlage opslaan",
            str(default_dir / filename),
        )
        if not save_path:
            return
        try:
            content = data if isinstance(data, (bytes, bytearray)) else str(data).encode("utf-8")
            Path(save_path).write_bytes(content)
        except OSError as e:
            QMessageBox.warning(self, "Opslagfout", f"Kon niet opslaan:\n{e}")
            return

        # Vraag of openen
        ret = QMessageBox.question(
            self, "Geopend",
            f"Bijlage opgeslagen als:\n{save_path}\n\nNu openen?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if ret == QMessageBox.Yes:
            try:
                import os
                if hasattr(os, "startfile"):
                    os.startfile(save_path)
                else:
                    import subprocess
                    subprocess.Popen(["xdg-open", save_path])
            except Exception as e:
                QMessageBox.warning(self, "Open-fout", f"Kon bijlage niet openen:\n{e}")

    # ------------------------------------------------------------------
    # Acties
    # ------------------------------------------------------------------
    def _add_account_clicked(self):
        dlg = AccountDialog(self)
        if dlg.exec() == QDialog.Accepted:
            acc = dlg.get_account()
            add_account(acc)
            self._accounts = load_accounts()
            self._populate_accounts()
            get_voice().speak("Account toegevoegd.")

    def _edit_account_clicked(self):
        """Open AccountDialog voor het huidige geselecteerde account."""
        if not self._current_account:
            QMessageBox.information(
                self, "Geen account",
                "Selecteer eerst een account in de lijst links."
            )
            return
        idx = self._accounts.index(self._current_account)
        dlg = AccountDialog(self, existing=self._current_account)
        if dlg.exec() == QDialog.Accepted:
            new_acc = dlg.get_account()
            update_account(idx, new_acc)
            self._accounts = load_accounts()
            self._current_account = self._accounts[idx]
            self._populate_accounts()
            get_voice().speak("Account bijgewerkt.")

    def _remove_account_clicked(self):
        """Verwijder het huidige geselecteerde account na bevestiging."""
        if not self._current_account:
            QMessageBox.information(
                self, "Geen account",
                "Selecteer eerst een account in de lijst links."
            )
            return
        name = self._current_account.get("name", self._current_account.get("email", "?"))
        ret = QMessageBox.question(
            self, "Bevestiging",
            f"Weet u zeker dat u het account '{name}' wilt verwijderen?\n\n"
            "Dit verwijdert het account uit de lokale opslag. "
            "Uw e-mails bij de provider blijven uiteraard staan.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if ret != QMessageBox.Yes:
            return
        idx = self._accounts.index(self._current_account)
        remove_account(idx)
        self._accounts = load_accounts()
        self._current_account = self._accounts[0] if self._accounts else None
        self._populate_accounts()
        # Clear de berichten-view
        self.lst_messages.clear()
        self._messages = []
        self.lbl_header.setText("")
        self.view.setHtml(self._placeholder_html())
        try:
            self.attachments_panel.hide()
        except Exception:
            pass
        get_voice().speak(f"Account {name} verwijderd.")

    def _refresh(self):
        self._fetch_messages()

    def _compose(self):
        if not self._current_account:
            QMessageBox.information(self, "Info", _("email_no_account"))
            return
        dlg = ComposeDialog(self._current_account, self)
        dlg.exec()

    def _reply(self):
        if not self._current_message or not self._current_account:
            return
        msg = self._current_message
        # Trek het eerste e-mailadres uit "From"
        m = re.search(r"<([^>]+)>", msg.from_addr)
        to = m.group(1) if m else msg.from_addr
        body = f"\n\n--- Origineel bericht ---\n{msg.body_text or ''}"
        dlg = ComposeDialog(self._current_account, self,
                            to=to, subject=f"Re: {msg.subject}", body=body)
        dlg.exec()

    def _forward(self):
        if not self._current_message or not self._current_account:
            return
        msg = self._current_message
        body = f"\n\n--- Doorgestuurd bericht ---\nVan: {msg.from_addr}\nOnderwerp: {msg.subject}\n\n{msg.body_text or ''}"
        dlg = ComposeDialog(self._current_account, self,
                            subject=f"Fwd: {msg.subject}", body=body)
        dlg.exec()

    def _delete(self):
        if not self._current_message or not self._current_account:
            return
        if self._current_account.get("protocol") != "imap":
            QMessageBox.information(self, "Info", "Verwijderen werkt alleen bij IMAP-accounts.")
            return
        ans = QMessageBox.question(self, "Bevestig", "Dit bericht verwijderen?")
        if ans != QMessageBox.Yes:
            return
        try:
            acc = self._current_account
            with IMAPClient(acc["imap_host"], acc["imap_port"],
                            acc["email"], acc["password"]) as c:
                c.delete(self._current_message.folder, self._current_message.uid)
            get_voice().speak("Verwijderd.")
            self._fetch_messages()
        except Exception as e:
            QMessageBox.warning(self, "Fout", f"Verwijderen faalde: {e}")

    def _speak_message(self):
        """Lees het huidige bericht voor."""
        if not self._current_message:
            return
        msg = self._current_message
        text = (
            f"Bericht van {msg.from_addr}. "
            f"Onderwerp: {msg.subject}. "
            f"{(msg.body_text or '')[:600]}"
        )
        get_voice().speak(text)


# ========================================================================
# UI: quick guide  (was: ui/quickguide_window.py)
# ========================================================================

SECTIONS = [
    ("Welkom", """
Mijn naam is Alfred, uw persoonlijke desktop-butler. Ik verschijn rechtsonder op uw scherm
en help u graag met dagelijkse taken.

Klik op mij wanneer u mij nodig heeft, of druk op Shift+V om mij iets te vragen.

In deze gids leg ik u alle functies kort uit. Selecteer een onderwerp links en klik op
"Sectie voorlezen" als u de tekst liever wilt horen dan lezen.

NIEUW IN DEZE VERSIE (v2.3)
  - Update-check bij opstart: als er een nieuwe versie is, ziet u dat direct
  - Info-venster met versie, maker (Dravenlock), website link
  - Cursor staat automatisch in tekstveld bij Shift+V (typ direct!)
  - Stem-bug opgelost: spraak werkt nu betrouwbaar (oneindige recursie fix)
  - Instellingen-venster groter + scrollbaar: opslaan-knop altijd zichtbaar
  - Verbeterde thread-veiligheid van AI-statusballonnen

v2.2 (eerder)
  - Persoonlijke begroeting met uw voornaam
  - 6 karakters (incl. Drake de vuurdraak)
  - Spraakherkenning ('Hé Alfred...')
  - Donatie-knop, tekstballonnen met cloud-vorm + scrollbaar
  - Tijdsafhankelijk afscheid bij afsluiten
"""),
    ("Sneltoetsen", """
- Shift + V                : open het zoekvenster
- Ctrl + Shift + L         : ik lees de inhoud van uw klembord voor
- Escape                   : stop mijn spraak of sluit het huidige venster
- Enter                    : verstuur uw vraag in het zoekvenster
- Shift + Enter            : nieuwe regel in tekstveld (zonder versturen)
- Ctrl + N                 : nieuw e-mailbericht (in het e-mailvenster)
- F5                       : ververs (in e-mail of browser)
- Ctrl + R                 : beantwoord een e-mail
- Delete                   : verwijder geselecteerde e-mail
- Alt + Links / Rechts     : terug / vooruit in browser
- Ctrl + T                 : nieuwe browsertab
- Ctrl + W                 : browsertab sluiten

Dubbelklik op mijn systeemvak-icoon opent direct het zoekvenster.
"""),
    ("Persoonlijke begroeting", """
Ik kan u bij uw voornaam aanspreken. Open Instellingen -> tab "Persoonlijk"
en vul uw voornaam in. Vanaf dan groet ik u bijvoorbeeld met:

  's Morgens:  "Goedemorgen, [uw voornaam]! Heeft u goed geslapen?"
  's Middags:  "Goedemiddag, [uw voornaam]. Fijn u te zien."
  's Avonds:   "Goedenavond, [uw voornaam]. Een prettige avond gewenst."
  Bij sluiten: "Welterusten, [uw voornaam]. Slaap zacht."

Mijn begroeting past zich aan aan het tijdstip van de dag. Bij het afsluiten
van de app neem ik ook netjes afscheid voordat alles weggaat.

De voornaam wordt alleen op uw eigen pc opgeslagen — niemand anders krijgt
dit te zien. U kunt het veld leeggooien om weer anoniem te worden.

In het Instellingen-venster staat een knop "Beluister groet (voorbeeld)"
zodat u direct kunt horen hoe het klinkt.
"""),
    ("Spraakherkenning (microfoon)", """
Sinds v2.2 kan ik luisteren naar uw microfoon en reageren op gesproken
opdrachten. Open Instellingen -> Persoonlijk en zet "Spraakherkenning" aan.

ACTIVEREN MET WAKE-WOORD
  Begin uw vraag met mijn naam (verandert mee met het gekozen karakter):
    'Hé Alfred, zoek voor mij een recept voor lasagne'
    'Hé Sophie, hoe laat is het'
    'Hé Drake, open de mail'
  Werkt voor alle 6 karakters. Daarnaast werken altijd ook 'computer',
  'assistent' en 'butler'.

WAT KUNT U VRAGEN?
  Alles wat u in het zoekvenster ook zou kunnen typen:
    'Hé Alfred, wat is het weer'
    'Hé Alfred, zoek nieuws van NOS'
    'Hé Alfred, voeg toe aan mijn lijst: melk kopen'
    'Hé Alfred, lees mijn notities'

VEREISTEN
  Voor spraakherkenning zijn extra pakketten nodig. Als die niet
  aanwezig zijn, toont de Instellingen-tab een uitleg met het commando
  om ze te installeren. Werkt uw microfoon, dan herkent een online
  recognizer (gratis, Google) uw stem.

PRIVACY
  Audio wordt alleen verzonden ZODRA u een wake-woord gebruikt — daarvoor
  blijft alles lokaal. Het wake-woord-onderdeel zelf werkt lokaal via
  energie-detectie en speech-to-text van korte fragmenten.
"""),
    ("Klembord voorlezen", """
Selecteer ergens tekst (in een PDF, document, webpagina, e-mail) en kopieer die met
Ctrl+C. Druk daarna op Ctrl+Shift+L en ik lees voor wat u zojuist gekopieerd heeft.

Dit werkt OVERAL, niet alleen in mijn eigen vensters. Voor lange teksten lees ik
maximaal 1200 tekens; de rest kapt af.

Stop me op elk moment met een klik of met Escape.
"""),
    ("Snelle antwoorden", """
In het zoekvenster (Shift+V) krijgt u direct antwoord op deze soorten vragen:

TIJD
  'hoe laat is het'    'wat is de tijd'
  'what time is it'    'wie spät ist es'

DATUM
  'welke datum'        'welke dag is het'
  'wat is het vandaag voor een dag'

REKENSOMMEN
  '25 * 32'            'bereken 100 / 7'
  '2 tot de macht 10'  'wat is 250 plus 175'

EENHEDEN CONVERTEREN
  '5 km in mijlen'        '60 mph in kmh'
  '32 fahrenheit naar celsius'  '500 gram in pond'
  '20 celsius naar fahrenheit'

Voor temperatuur, lengte, massa en snelheid heb ik de meest gebruikte eenheden ingebouwd.
"""),
    ("Notities", """
Ik kan dingen voor u onthouden.

EEN NOTITIE TOEVOEGEN
  'onthoud dat de belasting voor 1 mei betaald moet worden'
  'noteer: kapper bellen volgende week'
  'remember to buy bread' (Engels werkt ook)

UW NOTITIES OPVRAGEN
  'lees mijn notities'    'toon notities'
  'show my notes'

EEN NOTITIE VERWIJDEREN
  'vergeet notitie over belasting'
  'verwijder notitie over kapper'

Uw notities staan in <DeskButler-map>/data/notes.db en blijven dus bewaard tussen
sessies. Bij 'lees mijn notities' spreek ik de eerste vijf uit en toon ik alle 20
meest recente in het venster.

Het verschil met de te-doen lijst: notities zijn permanent (totdat u ze verwijdert);
te-doen items zijn afvinkbaar.
"""),
    ("Te-doen lijst", """
Een af te vinken takenlijst voor wat u nog moet doen. Open via mijn menu
(rechtsklik op mij of klik op het systeemvak-icoon) -> "Te-doen lijst".

VIA HET VENSTER
  - Typ een nieuwe taak in het tekstvak en druk op Enter
  - Dubbelklik op een taak om die af te vinken (of weer aan)
  - Knoppen onderaan: (af)vinken, verwijderen, of "Afgevinkte opruimen"

VIA SPRAAK / ZOEKVENSTER
  Toevoegen:
    'voeg toe aan mijn lijst: belasting indienen'
    'te doen: kapper bellen volgende week'
    'todo: boodschappen doen'

  Bekijken:
    'wat moet ik nog doen'    'mijn lijst'    'todo lijst'
    'wat staat er op mijn lijst'

  Afvinken:
    'vink af kapper'    'klaar met belasting'
    'afvinken boodschappen'

Opslag in <DeskButler-map>/data/todo.db.
"""),
    ("Bestanden zoeken op uw pc", """
'zoek bestand <naam>' (of 'vind bestand', 'find file')

Voorbeelden:
  'zoek bestand belasting'      'find file invoice'
  'zoek bestand foto'           'vind bestand recept'

Ik zoek in uw Documenten, Bureaublad, Downloads, Afbeeldingen, Muziek en Video's
(en hun submappen tot 6 lagen diep). De gevonden bestanden komen in een lijst met
hun pad. Het eerste resultaat kan ik direct voor u openen met de standaard-applicatie
(Word voor .docx, een browser voor .html, enzovoort).
"""),
    ("Slim zoeken: Wikipedia & recepten", """
Voordat ik een gewone zoekmachine raadpleeg, probeer ik eerst een paar
gespecialiseerde bronnen. Die geven vaak betere en stabielere antwoorden.

WAT IS X? / WIE IS X?
  Vragen die beginnen met 'wat is...', 'wie is...', 'wat zijn...' worden eerst
  geprobeerd op Wikipedia. Voorbeelden:
    'wat is een quasar'
    'wie is Vincent van Gogh'
    'wat zijn antioxidanten'
    'wat is fotosynthese'
  Ik lees de samenvatting uit het Wikipedia-artikel voor.

RECEPTEN ZOEKEN
  Bij vragen die het woord 'recept' bevatten, doorzoek ik TheMealDB. Voorbeelden:
    'zoek een recept voor lasagne'
    'recept voor appeltaart'
    'geef me een recept voor curry'
  Ik toon de naam, de ingrediënten en de bereidingswijze. Ook bij filterwoorden
  als 'suikervrij' of 'glutenvrij' werk ik — ik filter die woorden weg en zoek
  op het hoofdgerecht.

DIRECTE ANTWOORDEN
  Andere algemene vragen probeer ik via de DuckDuckGo Instant Answer API,
  die soms direct een samenvatting geeft uit hun encyclopedische bronnen.

Pas als deze gespecialiseerde bronnen geen antwoord geven, val ik terug op
de gekozen zoekmachine (DuckDuckGo, Bing, Startpage, etc.).
"""),
    ("Favorieten beheren", """
De browser heeft een ingebouwd favorieten-systeem met mappen. Vind ze
in de werkbalk:

  ⭐  Knop links: toont menu met je favorieten en mappen
  ☆  Knop rechts: voegt de HUIDIGE pagina toe aan favorieten

SNEL TOEVOEGEN

Klik op ☆ terwijl je op een pagina bent — DeskButler:
  - Pakt automatisch de pagina-titel als naam
  - Slaat de URL op in het hoofdniveau (zonder map)
  - Toont kort een bevestiging in de statusbalk onderaan

Klik nogmaals op ☆: krijgt melding "staat al in favorieten".

OPENEN VANUIT MENU

Klik op ⭐ in de werkbalk:
  - Mappen verschijnen als submenu's met hun favorieten erin
  - Losse favorieten (zonder map) staan direct in het menu
  - Klik op een favoriet om hem te openen in een nieuwe tab
  - Onderaan: "📋 Alle favorieten beheren..." voor het volledige
    beheer-venster

BEHEER-VENSTER

In het venster zie je een boom-structuur met alle mappen + favorieten:
  - 📁 Nieuwe map: maak een nieuwe map aan (bv. "Werk", "Nieuws")
  - Dubbelklik op een favoriet: openen in browser
  - Selecteer + ✏️ Bewerken: wijzig titel, URL, of verplaats naar
    andere map
  - Selecteer + 🗑️ Verwijderen: verwijder favoriet of map
    (favorieten in een verwijderde map gaan naar hoofdniveau)
  - Rechter-muisklik: snelmenu met meer opties (bv. naam wijzigen
    voor mappen)

WAAR STAAT DE OPSLAG?

Favorieten worden opgeslagen in:
  <DeskButler-map>/favorites.json

Je kunt dit bestand kopiëren naar een andere computer om je
favorieten mee te nemen.
"""),
    ("Browser-extensies", """
De ingebouwde browser ondersteunt extensies: stukjes code (CSS of JavaScript)
die in elke webpagina worden gevoegd om hem aan te passen. Open de browser
en klik op de 🧩-knop in de werkbalk om het beheer-venster te openen.

INGEBOUWDE EXTENSIES (klik om aan of uit te zetten):

🌙 Dark Reader
   Toont alle websites in een donker thema. Rustig voor de ogen, vooral
   's avonds. Afbeeldingen blijven normaal weergegeven.

🚫 Advertenties verbergen
   Verbergt veelvoorkomende advertentie-blokken. Werkt aanvullend op de
   DNS-adblock van DeskButler zelf.

🍪 Cookie-banners verbergen
   Verstopt cookie-toestemming-popups op websites. De auto-accept (in
   Instellingen → Browser) blijft op de achtergrond gewoon werken.

🔍 Grote tekst
   Vergroot tekst en regelafstand op alle websites voor extra leesbaarheid.

🔊 Voorlees-knop
   Plaatst een ronde 🔊-knop rechtsonder op elke webpagina. Klik er op om
   geselecteerde tekst (of het begin van de pagina) hardop voor te laten
   lezen door de butler.

🎬 YouTube zonder ads
   Slaat video-advertenties op YouTube automatisch over door ze te dempen,
   op 2× snelheid te zetten, en naar het einde te springen. Verbergt ook
   reclame-banners. Werkt op youtube.com en music.youtube.com.

EIGEN EXTENSIES MAKEN

In het beheer-venster (groene knop "Nieuwe extensie maken") staat een
editor waarmee u zelf CSS of JavaScript kunt schrijven. Met een URL-patroon
bepaalt u op welke sites de extensie werkt:
  *                  → overal
  *wikipedia.org*    → alleen op Wikipedia-pagina's
  *nu.nl*            → alleen op nu.nl

EXTENSIES VAN INTERNET OVERNEMEN

Sites met duizenden kant-en-klare extensies:
  greasyfork.org     — voor JavaScript-extensies (.user.js)
  userstyles.world   — voor CSS-stijlen (.user.css)

Kopieer een script vanaf zo'n site, plak het in de editor (knop "Nieuwe
extensie maken"), geef het een naam en klik Opslaan. De extensie verschijnt
direct in de lijst.

EXTENSIES-MAP

Eigen extensies worden opgeslagen als bestanden in de map "extensions/"
naast deskbutler.py. U kunt daar handmatig bestanden plaatsen of bewerken
met Kladblok. De knop "📁 Open extensies-map" opent deze map direct in
Verkenner.
"""),
    ("Video / muziek downloaden", """
De browser kan video's en muziek downloaden van YouTube, TikTok, Vimeo,
Facebook, en honderden andere sites. Klik op de ⬇️-knop in de werkbalk
van de browser om een keuzemenu te krijgen:

  🎬  Video downloaden (MP4)     — beste kwaliteit, beeld + geluid
  🎵  Audio downloaden (MP3)     — alleen geluid (handig voor muziek)
  📂  Open downloads-map         — toon waar bestanden zijn opgeslagen

EERSTE KEER: HULPPROGRAMMA'S INSTALLEREN

De eerste keer dat u een video downloadt, vraag ik toestemming om twee
kleine hulpprogramma's te downloaden:

  yt-dlp.exe  (ongeveer 15 MB)  — haalt video op van de site
  ffmpeg.exe  (ongeveer 80 MB)  — voegt beeld en geluid samen

Ze komen in een submap "tools/" naast DeskButler. Dit is eenmalig —
daarna werken downloads direct. De tools blijven up-to-date door af
en toe opnieuw te installeren (yt-dlp wijzigt regelmatig omdat YouTube
zijn formaten aanpast).

WERKWIJZE

1. Ga in de browser naar een video-pagina (YouTube, etc.)
2. Klik op ⬇️ in de werkbalk
3. Kies "Video downloaden" of "Audio downloaden"
4. Eerste keer: bevestig de installatie van de hulpprogramma's
5. Kies een bestandsnaam en map (standaard: "downloads/" bij DeskButler)
6. Voortgang verschijnt in een venster met annuleer-knop
7. Bij voltooid: bestand staat in de gekozen map

DOWNLOADS-MAP

Standaard worden bestanden opgeslagen in:
  <DeskButler-map>/downloads/

U kunt elke download een eigen plek geven via het "Opslaan als..." venster.
Een log-bestand "deskbutler_dl.log" wordt naast elke download geschreven
voor diagnose als er iets mis ging.

ANNULEREN

Tijdens het downloaden kunt u op "✕ Annuleren" klikken. Onvolledige
bestanden worden automatisch weggegooid.
"""),
    ("Afbeeldingen downloaden", """
De browser heeft een 🖼️-knop in de werkbalk waarmee u alle afbeeldingen
van de huidige pagina kunt bekijken en downloaden — handig bij webshops,
fotosites, of artikelen met veel illustraties.

WERKWIJZE

1. Open een pagina met afbeeldingen
2. Klik op 🖼️ in de werkbalk
3. Een venster opent met een rooster van alle afbeeldingen
4. Per afbeelding wordt getoond:
     - De afbeelding zelf als thumbnail
     - De afmetingen (bv. 1920×1080)
5. Selecteer een afbeelding en klik op een knop:
     - 💾 Opslaan als... — geeft een vrije plek en naam
     - ⚡ Snel opslaan — direct in downloads-map (met unieke naam)
     - Of dubbelklik op de afbeelding voor snelle opslag

INTELLIGENTE FILTERS

DeskButler filtert automatisch:
  - Te kleine afbeeldingen (< 80 pixels) worden verborgen
    Dit haalt favicons en tracking-pixels uit de lijst
  - Duplicaten worden samengevoegd
  - Voor websites met meerdere resoluties (srcset) wordt automatisch
    de hoogste resolutie gekozen

THUMBNAILS LADEN IN ACHTERGROND

De thumbnails worden in een aparte achtergrond-thread geladen, dus de
browser blijft tijdens het laden gewoon reageren. U ziet een
voortgangsbalk bovenaan.

Mocht een afbeelding niet laadbaar zijn (bv. door anti-bot bescherming),
verschijnt er een rood kruisje. De rest van het venster blijft werken.
"""),
    ("Karakter & AI", """
KARAKTER KIEZEN
  Open Instellingen → tab "Karakter & AI". Bovenaan kunt u uit vijf karakters
  kiezen:
    - Alfred   : chique butler met dienblad en paraplu (standaard)
    - Sophie   : huishoudster met schort en bloemenschaal
    - Robo     : retro robot met visor en knipperende LEDs
    - Sage     : tovenaar met staf, boek en sterrenmantel
    - Pip      : klein, vriendelijk wezentje (minimalistisch)
  Alle vijf karakters knipperen met hun ogen, hun blik volgt de muis, en hun
  mond beweegt mee terwijl ze praten.

EIGEN AFBEELDING
  Liever uw eigen foto, een AI-gegenereerd plaatje of iets gedownload van
  internet? Klik op "📁 Kies eigen afbeelding..." en selecteer een PNG of JPG.
  Let op: een eigen afbeelding wordt STATISCH getoond — geen knipperende ogen
  of bewegende mond, alleen het beeld plus de spraakballon. Voor de animaties
  zijn de ingebouwde karakters nodig.

  Wis uw eigen afbeelding met "✕ Eigen afbeelding wissen" — ik val dan terug
  op het laatst gekozen ingebouwde karakter.

LOKALE AI VIA OLLAMA (geavanceerd, optioneel)
  Ollama is een gratis tool waarmee u een Large Language Model lokaal kunt
  draaien — dus zonder dat uw vragen het internet op gaan. Als u Ollama
  installeert kan ik die als slimme antwoord-engine gebruiken voor algemene
  vragen.

  Installatie in 3 stappen:
    1. Download en installeer Ollama van https://ollama.com (eenmalige stap)
    2. Open Opdrachtprompt en typ: ollama pull llama3.2
       (dit downloadt het model, ongeveer 2 GB)
    3. Zet in Instellingen → tab "Karakter & AI" de schakelaar AAN
       en kies het model uit de lijst

  Daarna probeer ik bij algemene vragen eerst de lokale AI, voordat ik een
  zoekmachine raadpleeg. Dat geeft vaak directere antwoorden, werkt zonder
  internetverbinding, en uw vragen blijven volledig op uw eigen pc.

  Werkt Ollama niet of staat hij uit? Dan gebruik ik gewoon de zoekmachines.

AUTO-DETECTIE
  Ik controleer bij elke opstart of Ollama op uw pc draait. Drie scenario's:

   • Bij uw eerste opstart van DeskButler vraag ik één keer of u Ollama
     wilt gaan gebruiken. U heeft drie keuzes:
       - "Ja, ik wil het installeren"  -> ik open de begeleide installatie
       - "Misschien later"              -> u kunt het altijd later opzetten
       - "Nee, niet voor mij"           -> ik zal hier nooit meer over vragen

   • Heeft u "Misschien later" gekozen en installeert u Ollama achteraf?
     Dan merk ik dat bij de volgende opstart en vraag ik eenmalig of ik
     het mag aanzetten — met een keuze uit uw geïnstalleerde modellen.

   • Heeft u "Nee" gekozen? Dan vraag ik nooit meer iets. Wilt u dat
     ongedaan maken: Instellingen -> Karakter & AI -> "🔄 Reset
     Ollama-keuze".

BEGELEIDE INSTALLATIE
  In de tab "Karakter & AI" staat een knop "📖 Open begeleide installatie"
  die u door de drie stappen heen leidt en daarna automatisch controleert
  of alles werkt. Geen handmatige configuratie nodig.
"""),
    ("Zoeken en algemene vragen", """
Voor alles wat ik niet als specifiek commando herken, zoek ik op het internet via
de gekozen zoekmachine (DuckDuckGo standaard, met andere als reserve). Voorbeelden:

  'zoek een suikervrij recept voor appeltaart'
  'hoofdstad van Australië'
  'wisselkoers euro dollar'
  'wat is het verschil tussen ssd en hdd'
  'beste python tutorials voor beginners'

Ik lees het eerste resultaat voor en vraag of u het in mijn browser wilt zien.

PROGRAMMAS OPENEN
  'open kladblok'   'open paint'   'open rekenmachine'   'start opdrachtprompt'

WEER
  'weer'  'weer in Amsterdam'  'wat is het weer in Den Haag'  'Amsterdam weer'

NIEUWS
  'nieuws'  'nieuws van NOS'  'BBC nieuws'  'Volkskrant'  'AD'  'NU.nl nieuws'
"""),
    ("E-mail", """
Open het e-mailvenster via mijn menu.

EERSTE KEER
  - Klik op 'Account toevoegen' en kies uw provider (Gmail, Outlook, Yahoo of handmatig).
  - Voor Gmail/Outlook met wachtwoord heeft u een 'app-wachtwoord' nodig.

ACCOUNTS BEHEREN
  Bovenin het e-mailvenster staan drie knoppen voor account-beheer:
    [+ Account toevoegen]        nieuwe account
    [✏️ Account bewerken]         pas naam, wachtwoord of servers van
                                  het geselecteerde account aan
    [✕ Account verwijderen]      verwijder het geselecteerde account
                                  (met bevestiging — uw mails bij de
                                  provider blijven natuurlijk staan)
  Selecteer eerst een account in de lijst links voordat u bewerkt of verwijdert.

DAGELIJKS GEBRUIK
  - Klik op een account links om e-mails te zien.
  - Selecteer een bericht om het te lezen.
  - Knop '🔊 Voorlezen' laat mij het bericht voorlezen.

BIJLAGEN ONTVANGEN
  Als een bericht bijlagen heeft, verschijnt er onder de header een rij met knoppen:
  '💾 bestand.pdf'  '💾 foto.jpg'. Klik op zo'n knop om de bijlage te downloaden.
  U kunt kiezen waar u hem opslaat (standaard uw Downloads-map) en daarna openen.

BIJLAGEN VERSTUREN
  Bij het opstellen van een nieuw bericht (Ctrl+N) ziet u een sectie
  "📎 Bijlagen (0):" boven de verstuur-knoppen. Klik op "📎 Bijlage toevoegen"
  om bestanden te kiezen. Ze verschijnen in de lijst met bestandsgrootte.
  Dubbelklik op een bijlage in de lijst (of selecteer + klik "✕ Geselecteerde
  bijlage verwijderen") om hem weer weg te halen.

AUTOMATISCHE CONTROLE
  Ik controleer continu — niet één keer per dag, maar elke X minuten gedurende de
  hele tijd dat ik draai.

  Standaard staat dit op elke 5 minuten. Bij de eerste check na opstart meld ik
  hoeveel ongelezen berichten u nog heeft. Daarna meld ik alleen NIEUWE
  binnenkomers.

  Het interval is in te stellen via Instellingen → tab "E-mail check":
    - Uit (geen automatische check)
    - Elke minuut, 2 of 5 minuten (intensief)
    - Elke 10 of 15 minuten (rustiger; 15 = kwartier)
    - Elke 30 of 60 minuten (heel rustig; 60 = elk uur)

  In start_debug.bat ziet u per check een logregel ('[mail_check 14:35:00] ...')
  zodat u kunt verifiëren dat hij werkt.
"""),
    ("Browser", """
Mijn ingebouwde browser heeft tabs en standaard navigatieknoppen.

GEBRUIK
  - Adresbalk: webadres of zoekopdracht.
  - Plus-knop (+) voor een nieuwe tab.
  - Alt+Links / Alt+Rechts voor terug/vooruit.

ADBLOKKER (🛡)
  Standaard blokkeer ik ~75 bekende reclame- en tracker-domeinen.

COOKIE-BANNERS (🍪)
  Bij elke pagina probeer ik automatisch de "accepteer alles" knop weg te klikken.

STANDAARD ZOEKMACHINE
  In Instellingen → tab "Browser" kunt u kiezen welke zoekmachine als eerste wordt
  gebruikt voor algemene vragen via Shift+V. Opties:
    - DuckDuckGo (privacy, standaard)
    - Bing
    - Startpage (privacy, gebruikt Google-index)
    - Qwant (Europees, privacy)
    - Brave Search
    - Google (werkt soms moeilijk i.v.m. captchas)
  Als de gekozen machine geen resultaten geeft, worden de andere automatisch als
  reserve geprobeerd.

Alle browser-instellingen kunt u aan/uit zetten of kiezen in Instellingen → tab "Browser".
"""),
    ("Agenda en herinneringen", """
Open de agenda via mijn menu. Dubbelklik op een datum om een herinnering toe te voegen.

JAARLIJKS HERHALEN
  In het herinnering-venster kunt u 'Jaarlijks herhalen' aanvinken. Handig voor
  verjaardagen, jubileums en jaarlijkse afspraken. Na de melding zet ik de datum
  automatisch een jaar vooruit. In het lijstje ziet u zulke herinneringen met
  een 🔁 icoon.

OCHTENDBRIEFING
  Bij de eerste opstart van een nieuwe dag krijgt u van mij een briefing: groet,
  huidig weer en uw herinneringen van vandaag. Verschijnt dus maar één keer per dag.
"""),
    ("Mijn stem", """
Standaard gebruik ik de Neuvoice "Linda"-stem. Open Instellingen → tab "Stem" om:

  - Een andere stem te kiezen uit de Neuvoice-lijst (met testknop)
  - Het VOLUME in te stellen (Stil / Zacht / Normaal / Wat luider / Hard)
  - De SNELHEID in te stellen (Heel langzaam → Heel snel, 5 niveaus)
  - De TOONHOOGTE in te stellen (Heel laag → Heel hoog, 5 niveaus halve tonen)

De drie audio-controls staan naast elkaar als compacte lijsten. Klik op
'🔊 Test stem' bovenaan om uw selectie te horen met de huidige instellingen.

Alle wijzigingen werken direct nadat u opslaat — geen herstart nodig.

TIP
  - Snelheid 'Snel' of 'Heel snel' is handig als u een lange e-mail laat voorlezen.
  - Toonhoogte 'Laag' geeft een meer baritone karakter, 'Hoog' een lichtere stem.
  - Snelheid en toon werken onafhankelijk van elkaar.
"""),
    ("Instellingen en data-locatie", """
Mijn instellingen-venster heeft VIJF tabs:

  Tab 'Persoonlijk'   : uw voornaam + spraakherkenning aan/uit
  Tab 'Stem'          : welke stem, volume, snelheid en toonhoogte
  Tab 'E-mail check'  : hoe vaak ik moet kijken naar nieuwe mail
  Tab 'Browser'       : adblock, cookie-banner auto-accept, standaard zoekmachine
  Tab 'Karakter & AI' : welke karakter + eigen afbeelding + lokale AI (Ollama)

DATA-LOCATIE
  Alles staat in een 'data/' submap NAAST mij (niet in %APPDATA%):

    data/config.json     - alle instellingen
    data/accounts.enc    - versleutelde mail-accounts
    data/.key            - encryptiesleutel (NIET verwijderen)
    data/notes.db        - uw notities
    data/todo.db         - uw te-doen lijst
    data/data/reminders.db - uw herinneringen

  Bij upgrade vanaf eerdere versies migreer ik automatisch uit %APPDATA%\\DeskButler.
"""),
    ("DeskButler steunen", """
DeskButler is gratis en blijft dat ook. Vindt u de app nuttig? Dan kunt u
de ontwikkelaar steunen met een vrijwillige bijdrage.

Open mijn menu (rechts-klik op mij of klik op het systeemvak-icoon) en kies
"💝 Steun DeskButler...". Er verschijnt een venster met een blauwe PayPal-knop
die direct uw browser opent naar de donatiepagina. U kiest zelf het bedrag.

Er is geen verplichting — gewoon gebruiken is ook prima. Mocht u willen
bijdragen: alle gulle gevers worden enorm gewaardeerd!
"""),
    ("Contact opnemen", """
Heeft u een vraag, klacht, idee, of bug gevonden? Neem rechtstreeks contact
op met de maker via het contact-formulier in mijn menu:

  Mijn menu → "✉️ Contact opnemen..."

Er verschijnt een formulier waar u kunt invullen:
  • Soort bericht (vraag, klacht, idee, bug, anders)
  • Uw naam (uw voornaam wordt voorgevuld als die bekend is)
  • Uw e-mailadres (zodat de maker u kan antwoorden)
  • Uw bericht

Het bericht gaat naar service@dravenlock.nl. Werkt op twee manieren:

1. Heeft u een e-mailaccount toegevoegd in DeskButler? Dan stuur ik het
   bericht direct via uw account.
2. Heeft u nog geen account toegevoegd? Dan open ik uw standaard
   mail-programma (Outlook, Thunderbird, Mail) met het bericht alvast
   ingevuld; u klikt daar nog op 'Verzenden'.

Reageren doe ik (de maker, Dravenlock) zo snel mogelijk."""),
    ("Updates en versie", """
DeskButler is gemaakt door Dravenlock — bezoek https://dravenlock.nl/ voor
de nieuwste versie en informatie.

INFO-VENSTER
  Mijn menu → "Over DeskButler" toont:
    - Het versienummer dat u nu gebruikt
    - De naam van de maker (Dravenlock)
    - Een link naar de website
    - Een knop "🔄 Controleer op updates"

AUTOMATISCHE CONTROLE
  Bij het opstarten kijk ik kort of er een nieuwere versie beschikbaar is.
  Als dat zo is, krijgt u eenmalig een melding:

    ✨ Update beschikbaar!
    Huidige versie: 2.3
    Nieuwste versie: 2.4
    [⬇️ Naar download-pagina]   [Annuleren]

  Klikt u op de download-knop, dan opent uw browser direct de
  download-pagina. U kunt ook annuleren — er gebeurt niets ongewenst.

  De controle gebeurt achtergrondisch en faalt stil als er geen
  internetverbinding is. U merkt het dus alleen als er écht een update is.

HANDMATIG CONTROLEREN
  Menu → "Over DeskButler" → "🔄 Controleer op updates" doet het direct.
"""),
]


class QuickGuideWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(_("guide_title"))
        self.resize(1100, 760)
        self._setup_ui()
        self._apply_theme()


    def showEvent(self, event):
        super().showEvent(event)
        # EU-toegankelijkheid: handje + tooltips op alle interactieve widgets
        try:
            apply_accessibility(self)
        except Exception:
            pass

    def _setup_ui(self):
        font_size = config.get("font_size", 16)
        big_font = QFont("Segoe UI", font_size)

        central = QWidget()
        self.setCentralWidget(central)
        h = QHBoxLayout(central)

        left = QVBoxLayout()
        lbl = QLabel(_("guide_intro"))
        lbl.setFont(QFont("Segoe UI", font_size, QFont.Bold))
        lbl.setWordWrap(True)
        left.addWidget(lbl)

        self.lst = QListWidget()
        self.lst.setFont(big_font)
        for title, _content in SECTIONS:
            self.lst.addItem(QListWidgetItem(title))
        self.lst.currentRowChanged.connect(self._show_section)
        left.addWidget(self.lst, 1)

        right = QVBoxLayout()
        self.browser = QTextBrowser()
        self.browser.setFont(QFont("Segoe UI", font_size))
        right.addWidget(self.browser, 1)

        btn_speak = QPushButton("🔊 Sectie voorlezen")
        btn_speak.setMinimumHeight(48)
        btn_speak.setFont(QFont("Segoe UI", font_size, QFont.Bold))
        btn_speak.setToolTip("Laat mij deze sectie hardop voorlezen")
        btn_speak.setStyleSheet(
            "QPushButton { background:#3a3a3a; color:#fff; "
            "border:2px solid #707070; border-radius:6px; padding:8px 16px; }"
            "QPushButton:hover { background:#4a4a4a; border-color:#909090; }"
        )
        btn_speak.clicked.connect(self._speak_current)
        right.addWidget(btn_speak)

        h.addLayout(left, 1)
        h.addLayout(right, 2)

        self.lst.setCurrentRow(0)

    def _apply_theme(self):
        apply_dialog_style(self)


    def _show_section(self, row: int):
        if row < 0 or row >= len(SECTIONS):
            return
        title, content = SECTIONS[row]
        font_size = config.get("font_size", 16)
        html = (
            f"<style>body{{font-family:Segoe UI;font-size:{font_size}pt;"
            f"background:#2a2a2a;color:#f5f5f5;}}"
            f"h1{{color:#c0c0c0;}}</style>"
            f"<h1>{title}</h1>"
            f"<pre style='white-space:pre-wrap;font-family:Segoe UI;font-size:{font_size}pt;'>"
            f"{content.strip()}</pre>"
        )
        self.browser.setHtml(html)

    def _speak_current(self):
        row = self.lst.currentRow()
        if 0 <= row < len(SECTIONS):
            title, content = SECTIONS[row]
            get_voice().speak(f"{title}. {content}")


# ========================================================================
# UI: te-doen lijst venster  (was: ui/todo_window.py)
# ========================================================================

class TodoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Te-doen lijst")
        self.resize(820, 640)
        self._setup_ui()
        self._apply_theme()
        self.refresh()


    def showEvent(self, event):
        super().showEvent(event)
        # EU-toegankelijkheid: handje + tooltips op alle interactieve widgets
        try:
            apply_accessibility(self)
        except Exception:
            pass

    def _setup_ui(self):
        font_size = config.get("font_size", 16)
        big_font = QFont("Segoe UI", font_size)
        head_font = QFont("Segoe UI", font_size + 2, QFont.Bold)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        title = QLabel("📋 Te-doen lijst")
        title.setFont(head_font)
        root.addWidget(title)

        self.lbl_count = QLabel("")
        self.lbl_count.setFont(big_font)
        self.lbl_count.setStyleSheet("color: #c0c0c0;")
        root.addWidget(self.lbl_count)

        # Lijst van todos
        self.lst = QListWidget()
        self.lst.setFont(big_font)
        self.lst.setAlternatingRowColors(False)
        self.lst.itemDoubleClicked.connect(self._on_toggle)
        root.addWidget(self.lst, 1)

        # Hint
        hint = QLabel("Tip: dubbelklik op een taak om die af te vinken (of weer aan).")
        hint.setFont(big_font)
        hint.setStyleSheet("color: #909090;")
        root.addWidget(hint)

        # Invoer voor nieuwe taak
        input_row = QHBoxLayout()
        input_row.setSpacing(8)
        self.txt_new = QLineEdit()
        self.txt_new.setFont(big_font)
        self.txt_new.setMinimumHeight(40)
        self.txt_new.setPlaceholderText("Nieuwe taak...")
        self.txt_new.returnPressed.connect(self._add_clicked)
        input_row.addWidget(self.txt_new, 1)

        btn_add = QPushButton("+ Toevoegen")
        btn_add.setMinimumHeight(40)
        btn_add.setFont(big_font)
        btn_add.setObjectName("primary")
        btn_add.clicked.connect(self._add_clicked)
        input_row.addWidget(btn_add)

        root.addLayout(input_row)

        # Actieknoppen onderaan
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        btn_toggle = QPushButton("✓ Geselecteerde (af)vinken")
        btn_toggle.setMinimumHeight(48)
        btn_toggle.setFont(big_font)
        btn_toggle.clicked.connect(self._toggle_selected)
        btn_row.addWidget(btn_toggle)

        btn_delete = QPushButton("✕ Geselecteerde verwijderen")
        btn_delete.setMinimumHeight(48)
        btn_delete.setFont(big_font)
        btn_delete.clicked.connect(self._delete_selected)
        btn_row.addWidget(btn_delete)

        btn_clear_done = QPushButton("🧹 Afgevinkte opruimen")
        btn_clear_done.setMinimumHeight(48)
        btn_clear_done.setFont(big_font)
        btn_clear_done.clicked.connect(self._clear_done)
        btn_row.addWidget(btn_clear_done)

        root.addLayout(btn_row)

    def _apply_theme(self):
        apply_dialog_style(self)


    # ------------------------------------------------------------------
    def refresh(self):
        self.lst.clear()
        items = list_todos(include_done=True)
        open_n = sum(1 for _id, _ts, _t, done in items if not done)
        done_n = len(items) - open_n
        self.lbl_count.setText(f"{open_n} openstaand, {done_n} afgevinkt")

        if not items:
            placeholder = QListWidgetItem(
                "(Nog geen taken — voeg er een toe met het tekstvak hieronder)"
            )
            placeholder.setFlags(placeholder.flags() & ~Qt.ItemIsSelectable)
            self.lst.addItem(placeholder)
            return

        for r_id, ts, text, done in items:
            mark = "✓" if done else "○"
            label = f"{mark}  {text}"
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, r_id)
            if done:
                font = item.font()
                font.setItalic(True)
                font.setStrikeOut(True)
                item.setFont(font)
                item.setForeground(Qt.gray)
            self.lst.addItem(item)

    # ------------------------------------------------------------------
    def _add_clicked(self):
        text = self.txt_new.text().strip()
        if not text:
            return
        add_todo(text)
        self.txt_new.clear()
        self.refresh()

    def _on_toggle(self, item: QListWidgetItem):
        todo_id = item.data(Qt.UserRole)
        if todo_id is None:
            return
        # Zoek de huidige status
        items = list_todos(include_done=True)
        cur_done = next((d for r, _ts, _t, d in items if r == todo_id), False)
        set_done(todo_id, not cur_done)
        self.refresh()

    def _toggle_selected(self):
        item = self.lst.currentItem()
        if item is not None and item.flags() & Qt.ItemIsSelectable:
            self._on_toggle(item)

    def _delete_selected(self):
        item = self.lst.currentItem()
        if not item or not (item.flags() & Qt.ItemIsSelectable):
            return
        todo_id = item.data(Qt.UserRole)
        if todo_id is None:
            return
        ret = QMessageBox.question(
            self, "Bevestiging",
            "Wilt u deze taak permanent verwijderen?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if ret == QMessageBox.Yes:
            delete_todo(todo_id)
            self.refresh()

    def _clear_done(self):
        items = list_todos(include_done=True)
        done_ids = [r for r, _ts, _t, d in items if d]
        if not done_ids:
            QMessageBox.information(self, "Niets", "Geen afgevinkte taken om op te ruimen.")
            return
        ret = QMessageBox.question(
            self, "Bevestiging",
            f"Wilt u {len(done_ids)} afgevinkte taak/taken permanent verwijderen?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if ret == QMessageBox.Yes:
            for r_id in done_ids:
                delete_todo(r_id)
            self.refresh()


# ========================================================================
# UI: Ollama dialogen (intro/detect/install)  (was: ui/ollama_dialogs.py)
# ========================================================================

# ----------------------------------------------------------------------
# Dialog 1: Kennismaking (eerste opstart, nog geen keuze gemaakt)
# ----------------------------------------------------------------------
class OllamaIntroDialog(QDialog):
    """Eenmalige kennismaking met de Ollama-optie. Drie keuzes."""

    CHOICE_YES = "yes"
    CHOICE_LATER = "later"
    CHOICE_NO = "no"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Slimme antwoorden via lokale AI?")
        self.setMinimumWidth(640)
        self._choice = None

        font_size = config.get("font_size", 16)
        big = QFont("Segoe UI", font_size)
        title_font = QFont("Segoe UI", font_size + 4, QFont.Bold)
        self.setFont(big)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title = QLabel("🧠 Slimmere antwoorden mogelijk maken?")
        title.setFont(title_font)
        title.setWordWrap(True)
        layout.addWidget(title)

        body = QLabel(
            "Ik kan optioneel gebruikmaken van 'Ollama' — een gratis programma dat\n"
            "een AI-model volledig lokaal op uw pc laat draaien. Daarmee kan ik\n"
            "antwoorden geven in eigen woorden, ook op vragen die niet in mijn\n"
            "standaard lijstje staan.\n\n"
            "VOORDELEN:\n"
            "   • Geen account, geen abonnement, geen kosten\n"
            "   • Volledig privé — vragen blijven op uw eigen pc\n"
            "   • Werkt zonder internetverbinding\n\n"
            "WAT HET KOST:\n"
            "   • Eenmalige installatie van ongeveer 5 minuten\n"
            "   • Circa 2 GB schijfruimte voor het AI-model\n"
            "   • Tijdens gebruik wat extra rekenkracht en geheugen\n\n"
            "Wilt u dit nu opzetten? U kunt ook later via Instellingen → 'Karakter & AI'.\n"
            "Zonder Ollama werk ik ook prima — dan gebruik ik gewone zoekmachines."
        )
        body.setFont(big)
        body.setWordWrap(True)
        body.setStyleSheet(
            "background:#2a2a2a; padding:14px; border-radius:6px; color:#e0e0e0;"
        )
        layout.addWidget(body)

        # Drie knoppen — duidelijk en groot
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        btn_yes = QPushButton("✓  Ja, ik wil het installeren")
        btn_yes.setMinimumHeight(56)
        btn_yes.setFont(QFont("Segoe UI", font_size, QFont.Bold))
        btn_yes.setStyleSheet(
            "QPushButton { background:#2a8a2a; color:#fff; "
            "border:3px solid #4aaa4a; border-radius:6px; padding:8px 18px; }"
            "QPushButton:hover { background:#3a9a3a; }"
        )
        btn_yes.clicked.connect(self._choose_yes)
        btn_row.addWidget(btn_yes)

        btn_later = QPushButton("⏳  Misschien later")
        btn_later.setMinimumHeight(56)
        btn_later.setFont(QFont("Segoe UI", font_size, QFont.Bold))
        btn_later.setStyleSheet(
            "QPushButton { background:#7a6a2a; color:#fff; "
            "border:3px solid #aa9a4a; border-radius:6px; padding:8px 18px; }"
            "QPushButton:hover { background:#8a7a3a; }"
        )
        btn_later.clicked.connect(self._choose_later)
        btn_row.addWidget(btn_later)

        btn_no = QPushButton("✕  Nee, niet voor mij")
        btn_no.setMinimumHeight(56)
        btn_no.setFont(QFont("Segoe UI", font_size, QFont.Bold))
        btn_no.setStyleSheet(
            "QPushButton { background:#8a2a2a; color:#fff; "
            "border:3px solid #aa4a4a; border-radius:6px; padding:8px 18px; }"
            "QPushButton:hover { background:#9a3a3a; }"
        )
        btn_no.clicked.connect(self._choose_no)
        btn_row.addWidget(btn_no)

        layout.addLayout(btn_row)

        # Footer-tip
        footer = QLabel(
            "Tip: u kunt deze keuze altijd wijzigen via Instellingen → Karakter & AI."
        )
        footer.setFont(big)
        footer.setWordWrap(True)
        footer.setStyleSheet("color:#909090; padding-top: 6px;")
        layout.addWidget(footer)

        self._apply_theme()

    def _apply_theme(self):
        apply_dialog_style(self)


    def _choose_yes(self):
        self._choice = self.CHOICE_YES
        config.set("ollama_decision", self.CHOICE_YES)
        self.accept()

    def _choose_later(self):
        self._choice = self.CHOICE_LATER
        config.set("ollama_decision", self.CHOICE_LATER)
        self.accept()

    def _choose_no(self):
        self._choice = self.CHOICE_NO
        config.set("ollama_decision", self.CHOICE_NO)
        self.accept()

    def chosen(self) -> str:
        return self._choice or ""


# ----------------------------------------------------------------------
# Dialog 2: Detectie (Ollama is nét beschikbaar geworden)
# ----------------------------------------------------------------------
class OllamaDetectedDialog(QDialog):
    """Wanneer Ollama tussen twee opstarts beschikbaar is geworden."""

    def __init__(self, models: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ollama gedetecteerd!")
        self.setMinimumWidth(560)
        self._enable = False
        self._selected_model = models[0] if models else ""

        font_size = config.get("font_size", 16)
        big = QFont("Segoe UI", font_size)
        title_font = QFont("Segoe UI", font_size + 4, QFont.Bold)
        self.setFont(big)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title = QLabel("🟢 Ollama gedetecteerd!")
        title.setFont(title_font)
        layout.addWidget(title)

        body = QLabel(
            f"Goed nieuws — ik zie dat u Ollama op uw pc draaiend heeft met "
            f"{len(models)} model(len) geïnstalleerd.\n\n"
            "Wilt u dat ik dit ga gebruiken voor slimmere antwoorden?\n"
            "Vanaf dan probeer ik bij algemene vragen eerst uw lokale AI, "
            "voordat ik een zoekmachine gebruik."
        )
        body.setFont(big)
        body.setWordWrap(True)
        body.setStyleSheet(
            "background:#2a2a2a; padding:14px; border-radius:6px; color:#e0e0e0;"
        )
        layout.addWidget(body)

        if len(models) > 1:
            model_label = QLabel("Welk model wilt u gebruiken?")
            model_label.setFont(big)
            layout.addWidget(model_label)

            self.lst_models = QListWidget()
            self.lst_models.setFont(big)
            self.lst_models.setMaximumHeight(150)
            for m in models:
                item = QListWidgetItem(m)
                self.lst_models.addItem(item)
            self.lst_models.setCurrentRow(0)
            self.lst_models.currentItemChanged.connect(self._on_model_changed)
            layout.addWidget(self.lst_models)
        else:
            info = QLabel(f"Model: {self._selected_model}")
            info.setFont(big)
            info.setStyleSheet("color:#c0c0c0;")
            layout.addWidget(info)

        # Knoppen
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        btn_yes = QPushButton("✓  Ja, gebruiken")
        btn_yes.setMinimumHeight(56)
        btn_yes.setFont(QFont("Segoe UI", font_size, QFont.Bold))
        btn_yes.setStyleSheet(
            "QPushButton { background:#707070; color:#fff; "
            "border:2px solid #909090; border-radius:6px; padding:8px 18px; }"
            "QPushButton:hover { background:#909090; }"
        )
        btn_yes.clicked.connect(self._accept_yes)
        btn_row.addWidget(btn_yes)

        btn_no = QPushButton("Nu niet")
        btn_no.setMinimumHeight(56)
        btn_no.setFont(big)
        btn_no.clicked.connect(self.reject)
        btn_row.addWidget(btn_no)

        layout.addLayout(btn_row)

        footer = QLabel("U kunt deze keuze altijd wijzigen via Instellingen.")
        footer.setFont(big)
        footer.setStyleSheet("color:#909090; padding-top: 6px;")
        layout.addWidget(footer)

        self._apply_theme()

    def _apply_theme(self):
        apply_dialog_style(self)


    def _on_model_changed(self, current, _previous):
        if current is not None:
            self._selected_model = current.text()

    def _accept_yes(self):
        self._enable = True
        config.set("use_ollama", True)
        config.set("ollama_model", self._selected_model)
        config.set("ollama_decision", "yes")
        self.accept()

    def did_enable(self) -> bool:
        return self._enable

    def chosen_model(self) -> str:
        return self._selected_model


# ----------------------------------------------------------------------
# Dialog 3: Installatie-uitleg in 3 stappen
# ----------------------------------------------------------------------
class OllamaInstallGuideDialog(QDialog):
    """Begeleidt de gebruiker door de installatie. Verifieert achteraf."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ollama installeren — 3 stappen")
        self.setMinimumWidth(640)

        font_size = config.get("font_size", 16)
        big = QFont("Segoe UI", font_size)
        title_font = QFont("Segoe UI", font_size + 4, QFont.Bold)
        self.setFont(big)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title = QLabel("Ollama installeren in 3 stappen")
        title.setFont(title_font)
        layout.addWidget(title)

        step1 = QLabel(
            "<b>Stap 1.</b> Download het installatieprogramma van Ollama.<br>"
            "Klik op de knop hieronder — de website opent in uw browser.<br>"
            "Daar klikt u op 'Download for Windows' en draait het installatieprogramma."
        )
        step1.setFont(big)
        step1.setWordWrap(True)
        step1.setStyleSheet("background:#2a2a2a; padding:12px; border-radius:6px;")
        layout.addWidget(step1)

        btn_open = QPushButton("🌐  Open ollama.com in de browser")
        btn_open.setMinimumHeight(48)
        btn_open.setFont(big)
        btn_open.clicked.connect(self._open_website)
        layout.addWidget(btn_open)

        step2 = QLabel(
            "<b>Stap 2.</b> Open een Opdrachtprompt (typ 'cmd' in het Start-menu).<br>"
            "Typ daar precies dit en druk op Enter:<br><br>"
            "&nbsp;&nbsp;&nbsp;&nbsp;<code style='background:#000;color:#9f9;"
            "padding:4px 8px;font-size:14pt;'>ollama pull llama3.2</code><br><br>"
            "Het downloadt nu het AI-model (ongeveer 2 GB). Dat duurt een paar minuten."
        )
        step2.setFont(big)
        step2.setWordWrap(True)
        step2.setStyleSheet("background:#2a2a2a; padding:12px; border-radius:6px;")
        layout.addWidget(step2)

        step3 = QLabel(
            "<b>Stap 3.</b> Klik op 'Controleer installatie' hieronder.<br>"
            "Als alles goed staat zet ik het automatisch voor u aan."
        )
        step3.setFont(big)
        step3.setWordWrap(True)
        step3.setStyleSheet("background:#2a2a2a; padding:12px; border-radius:6px;")
        layout.addWidget(step3)

        # Knoppen onderaan
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        btn_check = QPushButton("🔍  Controleer installatie")
        btn_check.setMinimumHeight(56)
        btn_check.setFont(QFont("Segoe UI", font_size, QFont.Bold))
        btn_check.setStyleSheet(
            "QPushButton { background:#707070; color:#fff; "
            "border:2px solid #909090; border-radius:6px; padding:8px 18px; }"
            "QPushButton:hover { background:#909090; }"
        )
        btn_check.clicked.connect(self._check_installation)
        btn_row.addWidget(btn_check)

        btn_close = QPushButton("Sluiten")
        btn_close.setMinimumHeight(56)
        btn_close.setFont(big)
        btn_close.clicked.connect(self.reject)
        btn_row.addWidget(btn_close)

        layout.addLayout(btn_row)

        self._apply_theme()

    def _apply_theme(self):
        apply_dialog_style(self)


    def _open_website(self):
        QDesktopServices.openUrl(QUrl("https://ollama.com"))

    def _check_installation(self):
        info = ollama_diagnostics()
        if not info["available"]:
            QMessageBox.information(
                self, "Nog niet gevonden",
                "Ik kan Ollama nog niet bereiken op " + info["url"] + ".\n\n"
                "Mogelijke oorzaken:\n"
                "  • De installatie is nog niet klaar (afronden, herstart pc)\n"
                "  • Ollama draait nog niet — open Ollama vanuit het Start-menu\n"
                "  • Het draait op een andere poort (zie Instellingen)\n\n"
                "Probeer het over een paar minuten opnieuw."
            )
            return
        if not info["models"]:
            QMessageBox.information(
                self, "Geen modellen gevonden",
                "Ollama draait, maar er zijn nog geen AI-modellen geïnstalleerd.\n\n"
                "Open een Opdrachtprompt en typ:\n"
                "    ollama pull llama3.2\n\n"
                "Wacht tot het klaar is en probeer het dan opnieuw."
            )
            return

        # Alles in orde — zet het aan
        first_model = info["models"][0]
        config.set("use_ollama", True)
        config.set("ollama_model", first_model)
        config.set("ollama_decision", "yes")
        QMessageBox.information(
            self, "Ollama is klaar!",
            f"Uitstekend — Ollama draait en model '{first_model}' is gekozen.\n\n"
            "Vanaf nu probeer ik bij algemene vragen eerst uw lokale AI. "
            "U kunt deze instelling altijd wijzigen via Instellingen → 'Karakter & AI'."
        )
        self.accept()


# ----------------------------------------------------------------------
# Startup-coördinator
# ----------------------------------------------------------------------
def check_ollama_on_startup(parent=None):
    """
    Wordt aangeroepen na het opstarten van de app. Beslist of er een dialoog
    getoond moet worden op basis van:
      - of Ollama momenteel beschikbaar is
      - of dat een verandering is sinds vorige start
      - of de gebruiker al een keuze had gemaakt

    Geen herhalend zeuren: als de gebruiker 'Nee' heeft gekozen,
    wordt nooit meer iets getoond. 'Later' triggert opnieuw als er
    iets verandert.
    """

    is_avail = ollama_is_available()
    was_avail = bool(config.get("ollama_last_seen_available", False))
    decision = str(config.get("ollama_decision", ""))

    # Onthoud huidige status voor volgende keer
    config.set("ollama_last_seen_available", is_avail)

    # Gebruiker heeft definitief Nee gezegd
    if decision == "no":
        return

    # Ollama is net beschikbaar gekomen sinds vorige start.
    # Dit overrulet 'later' (omdat de toestand is gewijzigd) maar niet 'no'.
    if is_avail and not was_avail:
        # Behalve als al gebruikt — dan niet opnieuw vragen
        if decision == "yes" and config.get("use_ollama", False):
            return
        models = ollama_list_models()
        if models:
            dlg = OllamaDetectedDialog(models, parent=parent)
            dlg.exec()
            return

    # Eerste keer ooit (nog niet gevraagd)
    if decision == "":
        dlg = OllamaIntroDialog(parent=parent)
        if dlg.exec() == QDialog.Accepted and dlg.chosen() == "yes":
            # Open installatiegids
            guide = OllamaInstallGuideDialog(parent=parent)
            guide.exec()


def show_install_guide(parent=None):
    """Open de installatie-gids direct (vanuit Instellingen-knop)."""
    dlg = OllamaInstallGuideDialog(parent=parent)
    dlg.exec()


def reset_ollama_choice():
    """Reset de gebruikerskeuze zodat de intro-dialog weer kan verschijnen."""
    config.set("ollama_decision", "")
    config.set("ollama_last_seen_available", False)


# ========================================================================
# UI: settings  (was: ui/settings_window.py)
# ========================================================================

# Test-tekst per taal
TEST_PHRASES = {
    "nl": "Goedemiddag. Ik ben uw butler. Hoe kan ik u van dienst zijn?",
    "en": "Good afternoon. I am your butler. How may I be of service?",
    "de": "Guten Tag. Ich bin Ihr Butler. Wie kann ich Ihnen helfen?",
    "fr": "Bonjour. Je suis votre majordome. Comment puis-je vous aider ?",
    "es": "Buenas tardes. Soy su mayordomo. ¿En qué puedo servirle?",
    "it": "Buon pomeriggio. Sono il suo maggiordomo. Come posso aiutarla?",
    "pt": "Boa tarde. Eu sou o seu mordomo. Como posso ajudar?",
}

# Beschikbare intervallen voor de mail check
MAIL_INTERVALS = [0, 1, 2, 5, 10, 15, 30, 60]


class _OllamaDiagThread(QThread):
    """
    Voert ollama_diagnostics() uit in achtergrond zodat de Qt-hoofdthread
    vrij blijft. Belangrijk omdat de HTTP-check tot 2 seconden kan duren,
    en gedurende die tijd zou anders de butler-mondanimatie stilstaan.
    """
    result = Signal(dict)

    def __init__(self, parent=None):
        # Parent is BELANGRIJK: Qt garandeert dat een thread met een
        # parent niet vroegtijdig wordt opgeruimd terwijl hij nog draait.
        # Zonder parent krijg je "QThread: Destroyed while thread is
        # still running" -> mogelijke crash.
        super().__init__(parent)

    def run(self):
        try:
            info = ollama_diagnostics()
        except Exception as e:
            info = {
                "available": False, "url": "?", "models": [],
                "installed": False, "selected_model": "",
                "enabled": False, "started_by_us": False,
                "error": str(e),
            }
        self.result.emit(info)


class _OllamaActionThread(QThread):
    """
    Voert een Ollama-actie (start/stop) uit in achtergrond zodat de UI
    niet bevriest. De Ollama-server kan tot 15 seconden nodig hebben
    om op te starten, en 'taskkill' kan een paar seconden duren.
    """
    finished_result = Signal(bool, str)  # success, info-string

    def __init__(self, action: str, parent=None):
        # Parent voorkomt vroegtijdige opruiming (zie _OllamaDiagThread)
        super().__init__(parent)
        self.action = action  # 'start' of 'stop'

    def run(self):
        try:
            if self.action == "start":
                ok = ollama_try_start()
                self.finished_result.emit(ok, "" if ok else "start_failed")
            elif self.action == "stop":
                ok, msg = ollama_force_shutdown()
                self.finished_result.emit(ok, msg)
            else:
                self.finished_result.emit(False, f"onbekende actie: {self.action}")
        except Exception as e:
            self.finished_result.emit(False, f"fout: {e}")


class SettingsWindow(QMainWindow):
    """Instellingenvenster met tabs."""

    # Signalen voor live updates in de hoofdapp
    character_changed = Signal()
    engine_changed = Signal(str)        # nieuwe engine-key
    ollama_changed = Signal(bool)       # use_ollama nieuwe waarde
    request_ollama_stop = Signal()      # gebruiker klikt 'Stop Ollama'

    def __init__(self, mail_checker=None, browser_window=None):
        super().__init__()
        self.setWindowTitle("Instellingen")
        # Grotere standaard zodat alle inhoud + opslaan-knop in beeld passen
        self.resize(960, 880)
        self.setMinimumSize(720, 600)

        self._voice = get_voice()
        self._mail_checker = mail_checker
        self._browser_window = browser_window

        # State
        self._saved_voice = config.get("voice_name", "Linda")
        self._selected_voice = self._saved_voice
        self._saved_interval = int(config.get("mail_check_interval_min", 5))
        self._selected_interval = self._saved_interval
        self._adblock_state = bool(config.get("adblock_enabled", True))
        self._cookies_state = bool(config.get("auto_accept_cookies", True))
        self._saved_volume = float(config.get("voice_volume", 0.95))
        self._selected_volume = self._saved_volume
        self._saved_speed = float(config.get("voice_speed", 1.0))
        self._selected_speed = self._saved_speed
        self._saved_pitch = float(config.get("voice_pitch", 0.0))
        self._selected_pitch = self._saved_pitch
        self._saved_engine = str(config.get("default_search_engine", "duckduckgo"))
        self._selected_engine = self._saved_engine
        self._saved_character = str(config.get("character_id", "alfred"))
        self._selected_character = self._saved_character
        self._ollama_state = bool(config.get("use_ollama", False))
        self._saved_model = str(config.get("ollama_model", ""))
        self._selected_model = self._saved_model
        self._saved_user_name = str(config.get("user_name", ""))

        self._build_ui()
        self._apply_theme()
        self._populate_personal()
        self._populate_voices()
        self._populate_intervals()
        self._populate_volumes()
        self._populate_speeds()
        self._populate_pitches()
        self._populate_engines()
        self._populate_characters()
        self._populate_ollama()

    # ------------------------------------------------------------------
    def _build_ui(self):
        font_size = config.get("font_size", 16)
        big_font = QFont("Segoe UI", font_size)
        tab_font = QFont("Segoe UI", font_size + 2, QFont.Bold)
        button_font = QFont("Segoe UI", font_size, QFont.Bold)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(12)

        self.tabs = QTabWidget()
        self.tabs.setFont(tab_font)
        # Wrap elke tab in een scroll-area zodat lange inhoud bereikbaar is
        self.tabs.addTab(self._wrap_scroll(self._build_personal_tab(big_font)), "👤 Persoonlijk")
        self.tabs.addTab(self._wrap_scroll(self._build_voice_tab(big_font)), _("settings_voice"))
        self.tabs.addTab(self._wrap_scroll(self._build_mail_tab(big_font)), _("settings_mail"))
        self.tabs.addTab(self._wrap_scroll(self._build_browser_tab(big_font)), _("settings_browser"))
        self.tabs.addTab(self._wrap_scroll(self._build_character_tab(big_font)), "Karakter & AI")
        # Reset scrollpositie naar bovenaan bij elke tab-wissel
        self.tabs.currentChanged.connect(self._reset_tab_scroll)
        root.addWidget(self.tabs, 1)

        # Globale status + knoppen onderaan
        self.lbl_status = QLabel("")
        self.lbl_status.setFont(big_font)
        self.lbl_status.setWordWrap(True)
        self.lbl_status.setObjectName("status")
        self.lbl_status.setMinimumHeight(64)
        root.addWidget(self.lbl_status)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.btn_save = QPushButton("✓ Opslaan")
        self.btn_save.setMinimumHeight(60)
        self.btn_save.setFont(button_font)
        self.btn_save.setObjectName("save")
        self.btn_save.clicked.connect(self._save_all)
        btn_row.addWidget(self.btn_save)

        self.btn_cancel = QPushButton("✕ Sluiten")
        self.btn_cancel.setMinimumHeight(60)
        self.btn_cancel.setFont(button_font)
        self.btn_cancel.clicked.connect(self.close)
        btn_row.addWidget(self.btn_cancel)

        root.addLayout(btn_row)

    # ------------------------------------------------------------------
    def _wrap_scroll(self, inner: QWidget) -> QScrollArea:
        """Verpakt een tab in een scroll-area, zodat lange inhoud bereikbaar blijft."""
        sa = QScrollArea()
        sa.setWidgetResizable(True)
        sa.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        sa.setFrameShape(QScrollArea.NoFrame)
        sa.setWidget(inner)
        return sa

    def _reset_tab_scroll(self, index: int):
        """Bij tabwissel: scroll naar bovenaan, zodat de titel zichtbaar is."""
        widget = self.tabs.widget(index)
        if isinstance(widget, QScrollArea):
            widget.verticalScrollBar().setValue(0)

    # ------------------------------------------------------------------
    def _build_personal_tab(self, big_font: QFont) -> QWidget:
        from PySide6.QtWidgets import QLineEdit, QFormLayout
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 20, 16, 16)
        layout.setSpacing(14)

        # Titel
        title = QLabel("Uw persoonlijke gegevens")
        title.setFont(QFont("Segoe UI", big_font.pointSize() + 2, QFont.Bold))
        layout.addWidget(title)

        intro = QLabel(
            "Met uw voornaam kan ik u persoonlijk groeten en aanspreken. "
            "Dit blijft volledig op uw eigen pc. U kunt het veld leeg laten "
            "als u dat liever heeft."
        )
        intro.setFont(big_font)
        intro.setWordWrap(True)
        intro.setStyleSheet("color: #c0c0c0; padding: 4px;")
        layout.addWidget(intro)

        # Naam veld
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        form.setSpacing(12)

        self.txt_user_name = QLineEdit()
        self.txt_user_name.setFont(big_font)
        self.txt_user_name.setPlaceholderText("Bijvoorbeeld: Anna")
        self.txt_user_name.setMinimumHeight(44)
        lbl_name = QLabel("Voornaam:")
        lbl_name.setFont(QFont("Segoe UI", big_font.pointSize(), QFont.Bold))
        form.addRow(lbl_name, self.txt_user_name)

        layout.addLayout(form)

        # Preview-knop
        btn_preview = QPushButton("🔊  Beluister groet (voorbeeld)")
        btn_preview.setMinimumHeight(50)
        btn_preview.setFont(big_font)
        btn_preview.clicked.connect(self._preview_greeting)
        layout.addWidget(btn_preview)

        # --- Spraakherkenning sectie ---
        sep = QLabel("")
        sep.setFixedHeight(8)
        layout.addWidget(sep)

        mic_title = QLabel("🎤  Spraakherkenning")
        mic_title.setFont(QFont("Segoe UI", big_font.pointSize() + 2, QFont.Bold))
        layout.addWidget(mic_title)

        if is_voice_input_available():
            mic_intro = QLabel(
                "Als spraakherkenning aan staat luister ik continu naar uw microfoon. "
                "U kunt mij activeren door te zeggen:\n\n"
                "    'Hé Alfred, zoek voor mij...' \n"
                "    'Hé Alfred, open de mail'\n\n"
                "Het wake-woord verandert mee met het gekozen karakter "
                "('Hé Sophie', 'Hé Drake', enz.). 'Computer', 'assistent' "
                "en 'butler' werken altijd."
            )
            mic_intro.setFont(big_font)
            mic_intro.setWordWrap(True)
            mic_intro.setStyleSheet("background:#2a2a2a; padding:14px; border-radius:6px; color:#e0e0e0;")
            layout.addWidget(mic_intro)

            self._voice_input_state = bool(config.get("voice_input_enabled", False))
            self.btn_voice_input = QPushButton(
                self._toggle_label("Spraakherkenning", self._voice_input_state))
            self.btn_voice_input.setMinimumHeight(58)
            self.btn_voice_input.setFont(QFont("Segoe UI", big_font.pointSize(), QFont.Bold))
            self.btn_voice_input.setStyleSheet(self._toggle_style(self._voice_input_state))
            self.btn_voice_input.clicked.connect(self._toggle_voice_input)
            layout.addWidget(self.btn_voice_input)
        else:
            # Vriendelijke uitleg voor gebruikers zonder technische kennis
            self._build_voice_install_guide(layout, big_font)
            self._voice_input_state = False

        layout.addStretch()
        return tab

    def _build_voice_install_guide(self, parent_layout, big_font: QFont):
        """Bouw een vriendelijke installatie-gids voor de spraakherkenning."""
        from PySide6.QtWidgets import QFrame
        from PySide6.QtGui import QClipboard

        # Hoofdtitel + uitleg
        explainer = QLabel(
            "Spraakherkenning is een extra onderdeel dat eenmalig moet worden "
            "geïnstalleerd. Het is gratis en hoeft maar één keer."
        )
        explainer.setFont(big_font)
        explainer.setWordWrap(True)
        explainer.setStyleSheet(
            "background:#2a2a2a; padding:14px; border-radius:6px; color:#e0e0e0;"
        )
        parent_layout.addWidget(explainer)

        # ----- Begeleidings-knoppen bovenaan -----
        helper_row = QHBoxLayout()
        helper_row.setSpacing(10)

        btn_guide_me = QPushButton("🎙️ Begeleid mij stap voor stap")
        btn_guide_me.setFont(QFont("Segoe UI", big_font.pointSize(), QFont.Bold))
        btn_guide_me.setMinimumHeight(48)
        btn_guide_me.setStyleSheet(
            "QPushButton { background:#2a5a8a; color:#ffffff; "
            "border:2px solid #4a8aca; border-radius:6px; padding:8px 16px; }"
            "QPushButton:hover { background:#3a6a9a; }"
        )
        btn_guide_me.setToolTip("Ik begeleid u met spraak door alle stappen")
        btn_guide_me.clicked.connect(self._guide_voice_install)
        helper_row.addWidget(btn_guide_me, 1)

        btn_open_cmd = QPushButton("⌨️ Open Opdrachtprompt nu")
        btn_open_cmd.setFont(QFont("Segoe UI", big_font.pointSize(), QFont.Bold))
        btn_open_cmd.setMinimumHeight(48)
        btn_open_cmd.setStyleSheet(
            "QPushButton { background:#2a5a2a; color:#ffffff; "
            "border:2px solid #4a8a4a; border-radius:6px; padding:8px 16px; }"
            "QPushButton:hover { background:#3a6a3a; }"
        )
        btn_open_cmd.setToolTip("Opent direct een Opdrachtprompt-venster voor u")
        btn_open_cmd.clicked.connect(self._open_cmd_prompt)
        helper_row.addWidget(btn_open_cmd, 1)

        parent_layout.addLayout(helper_row)

        # Stappen-titel
        steps_title = QLabel("📋 Of doe het zelf in 3 stappen:")
        steps_title.setFont(QFont("Segoe UI", big_font.pointSize() + 1, QFont.Bold))
        steps_title.setStyleSheet("padding-top: 8px; color: #f5f5f5;")
        parent_layout.addWidget(steps_title)

        # ----- Stap 1: Opdrachtprompt + illustratie -----
        step1 = self._make_install_step(
            step_num="1",
            title="Open de Opdrachtprompt",
            explanation=(
                "De Opdrachtprompt is een venster waarin u commando's kunt typen. "
                "Klik op '⌨️ Open Opdrachtprompt nu' hierboven, OF doe het zelf:\n"
                "  • Druk op de Windows-toets\n"
                "  • Typ:  cmd\n"
                "  • Druk op Enter\n"
                "  Er verschijnt een zwart venster — dat is de Opdrachtprompt."
            ),
            command=None,
            big_font=big_font,
            illustration_kind="cmd_window",
        )
        parent_layout.addWidget(step1)

        # ----- Stap 2: commando voor de installatie -----
        step2 = self._make_install_step(
            step_num="2",
            title="Kopieer en plak dit commando",
            explanation=(
                "Klik op '📋 Kopieer' hieronder. Daarna terug naar de "
                "Opdrachtprompt, klik er met de rechtermuisknop in (dat plakt "
                "het commando), en druk op Enter. Het installeren begint en "
                "duurt 1 à 2 minuten."
            ),
            command="pip install SpeechRecognition pyaudio",
            big_font=big_font,
            illustration_kind="cmd_pasted",
        )
        parent_layout.addWidget(step2)

        # ----- Stap 3: herstart -----
        step3 = self._make_install_step(
            step_num="3",
            title="Sluit en herstart DeskButler",
            explanation=(
                "Wanneer u de app de volgende keer opent, is spraakherkenning "
                "beschikbaar en kunt u hem hier aan zetten."
            ),
            command=None,
            big_font=big_font,
            illustration_kind="restart",
        )
        parent_layout.addWidget(step3)

        # ----- Probleem-oplosser -----
        trouble_title = QLabel("⚠️ Krijgt u een fout bij stap 2?")
        trouble_title.setFont(QFont("Segoe UI", big_font.pointSize(), QFont.Bold))
        trouble_title.setStyleSheet("padding-top: 8px; color: #ffcc88;")
        parent_layout.addWidget(trouble_title)

        trouble_text = QLabel(
            "Soms lukt PyAudio niet in één keer. Probeer dan eerst dit "
            "(werkt vaak wel, ook op nieuwe Python-versies):"
        )
        trouble_text.setFont(big_font)
        trouble_text.setWordWrap(True)
        trouble_text.setStyleSheet("color: #e0e0e0; padding: 4px 0;")
        parent_layout.addWidget(trouble_text)

        # Route A: pip-upgrade + opnieuw proberen (werkt op Python 3.13)
        route_a = QLabel("Route A — pip bijwerken en opnieuw proberen:")
        route_a.setFont(QFont("Segoe UI", big_font.pointSize(), QFont.Bold))
        route_a.setStyleSheet("color: #b0e0b0; padding: 4px 0;")
        parent_layout.addWidget(route_a)

        parent_layout.addWidget(self._make_command_box(
            "python -m pip install --upgrade pip", big_font))
        parent_layout.addWidget(self._make_command_box(
            "pip install pyaudio", big_font))
        parent_layout.addWidget(self._make_command_box(
            "pip install SpeechRecognition", big_font))

        # Route B: oude pipwin-methode, met expliciete waarschuwing
        route_b = QLabel("Route B — alleen voor oudere Python (3.10 of lager):")
        route_b.setFont(QFont("Segoe UI", big_font.pointSize(), QFont.Bold))
        route_b.setStyleSheet("color: #e0c080; padding: 8px 0 4px 0;")
        parent_layout.addWidget(route_b)

        route_b_warn = QLabel(
            "Let op: 'pipwin' werkt NIET meer op Python 3.13 of nieuwer. "
            "Als u Python 3.13 heeft, gebruik Route A hierboven."
        )
        route_b_warn.setFont(big_font)
        route_b_warn.setWordWrap(True)
        route_b_warn.setStyleSheet(
            "background:#3a2a1a; color:#ffcc88; padding:8px 12px; border-radius:6px;"
        )
        parent_layout.addWidget(route_b_warn)

        parent_layout.addWidget(self._make_command_box(
            "pip install pipwin", big_font))
        parent_layout.addWidget(self._make_command_box(
            "pipwin install pyaudio", big_font))

        # Route C: handmatige wheel als alles faalt
        route_c = QLabel("Route C — handmatig pyaudio-wheel downloaden:")
        route_c.setFont(QFont("Segoe UI", big_font.pointSize(), QFont.Bold))
        route_c.setStyleSheet("color: #b0c0e0; padding: 8px 0 4px 0;")
        parent_layout.addWidget(route_c)

        route_c_text = QLabel(
            "Werkt niets? Download dan handmatig een pyaudio 'wheel' "
            "(een .whl bestand) van een vertrouwde bron en installeer hem:\n"
            "  1. Ga naar https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio\n"
            "  2. Download het bestand dat past bij uw Python-versie\n"
            "     (bv. 'PyAudio-0.2.14-cp313-cp313-win_amd64.whl' voor Python 3.13)\n"
            "  3. Open Opdrachtprompt op de Downloads-map en typ:\n"
            "     pip install <bestandsnaam.whl>"
        )
        route_c_text.setFont(big_font)
        route_c_text.setWordWrap(True)
        route_c_text.setStyleSheet(
            "background:#2a2a2a; color:#d0d0d0; padding:12px; border-radius:6px;"
        )
        parent_layout.addWidget(route_c_text)

    def _make_install_step(self, step_num: str, title: str, explanation: str,
                            command: str | None, big_font: QFont,
                            illustration_kind: str | None = None) -> QWidget:
        """Bouw een visueel duidelijke 'stap'-box met optionele illustratie."""
        from PySide6.QtWidgets import QFrame
        box = QFrame()
        box.setStyleSheet(
            "QFrame { background:#2a2a2a; border-radius:8px; border:1px solid #444; }"
        )
        bl = QVBoxLayout(box)
        bl.setContentsMargins(14, 12, 14, 12)
        bl.setSpacing(8)

        # Kop: stapnummer + titel
        header_row = QHBoxLayout()
        num_label = QLabel(f"  {step_num}  ")
        num_label.setFont(QFont("Segoe UI", big_font.pointSize() + 2, QFont.Bold))
        num_label.setStyleSheet(
            "background:#707070; color:#fff; border-radius:18px; "
            "padding:4px 8px; min-width:36px; max-width:36px;"
        )
        num_label.setAlignment(Qt.AlignCenter)
        header_row.addWidget(num_label, 0)

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", big_font.pointSize(), QFont.Bold))
        title_label.setStyleSheet("color: #ffffff; border: none;")
        header_row.addWidget(title_label, 1)
        bl.addLayout(header_row)

        # Uitleg
        exp = QLabel(explanation)
        exp.setFont(big_font)
        exp.setWordWrap(True)
        exp.setStyleSheet("color: #d0d0d0; padding-left: 44px; border: none;")
        bl.addWidget(exp)

        # Commando-box (optioneel)
        if command:
            cmd_box = self._make_command_box(command, big_font)
            from PySide6.QtWidgets import QHBoxLayout as _HL
            cmd_row = _HL()
            cmd_row.addSpacing(44)
            cmd_row.addWidget(cmd_box, 1)
            bl.addLayout(cmd_row)

        # Illustratie (optioneel)
        if illustration_kind:
            illus = self._make_step_illustration(illustration_kind, big_font)
            if illus is not None:
                from PySide6.QtWidgets import QHBoxLayout as _HL
                il_row = _HL()
                il_row.addSpacing(44)
                il_row.addWidget(illus, 1)
                bl.addLayout(il_row)

        return box

    def _make_step_illustration(self, kind: str, big_font: QFont) -> QWidget | None:
        """
        Maak een visuele illustratie voor een stap. Toont een 'mini-screenshot'
        zodat de gebruiker weet waar hij naar uitkijkt.
        """
        from PySide6.QtWidgets import QFrame
        wrap = QFrame()
        wrap.setStyleSheet(
            "QFrame { background:transparent; border:none; }"
        )
        v = QVBoxLayout(wrap)
        v.setContentsMargins(0, 6, 0, 0)
        v.setSpacing(4)

        caption = QLabel()
        cap_font = QFont("Segoe UI", max(10, big_font.pointSize() - 2))
        cap_font.setItalic(True)
        caption.setFont(cap_font)
        caption.setStyleSheet("color:#909090; border:none; padding:2px;")

        if kind == "cmd_window":
            # Lege opdrachtprompt — zwart venster met prompt
            illu = QLabel(
                "<pre style='background:#000; color:#bbb; padding:8px 12px; "
                "border:1px solid #555; font-family:Consolas, monospace; "
                "font-size:11pt; margin:0;'>"
                "Microsoft Windows [Version 10.0.22631.4391]<br>"
                "(c) Microsoft Corporation. Alle rechten voorbehouden.<br><br>"
                "C:\\Users\\u&gt; <span style='background:#bbb; color:#000;'>&nbsp;</span>"
                "</pre>"
            )
            caption.setText("↑ Zo ziet de Opdrachtprompt eruit als hij open is")

        elif kind == "cmd_pasted":
            # Hetzelfde venster met het commando er net in geplakt
            illu = QLabel(
                "<pre style='background:#000; color:#bbb; padding:8px 12px; "
                "border:1px solid #555; font-family:Consolas, monospace; "
                "font-size:11pt; margin:0;'>"
                "C:\\Users\\u&gt; <span style='color:#9fff9f;'>"
                "pip install SpeechRecognition pyaudio</span>"
                "<span style='background:#bbb; color:#000;'>&nbsp;</span><br>"
                "<span style='color:#888;'>Collecting SpeechRecognition...</span><br>"
                "<span style='color:#888;'>Collecting pyaudio...</span>"
                "</pre>"
            )
            caption.setText("↑ Zo ziet het eruit als het commando geplakt en gestart is")

        elif kind == "restart":
            # Symbolisch: pijl van app naar app
            illu = QLabel(
                "<div style='background:#1a1a1a; padding:12px; border:1px solid #555; "
                "color:#d0d0d0; font-size:14pt; text-align:center;'>"
                "🎩&nbsp;&nbsp;✕&nbsp;&nbsp;→&nbsp;&nbsp;⏳&nbsp;&nbsp;→&nbsp;&nbsp;🎩&nbsp;&nbsp;✓"
                "</div>"
            )
            caption.setText("↑ Sluit de butler, wacht een momentje, en open hem opnieuw")

        else:
            return None

        illu.setTextFormat(Qt.RichText)
        illu.setWordWrap(True)
        v.addWidget(illu)
        v.addWidget(caption)
        return wrap

    def _open_cmd_prompt(self):
        """Open een nieuwe Opdrachtprompt-venster voor de gebruiker."""
        import subprocess
        import os
        try:
            if os.name == "nt":
                # 'start' opent een nieuw cmd-venster, niet als child-proces
                subprocess.Popen(
                    'start cmd',
                    shell=True,
                    creationflags=0x08000000 if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
                )
                self.lbl_status.setText(
                    "⌨️ Opdrachtprompt is geopend! Ga er nu heen en klik op 'Kopieer' bij stap 2."
                )
                # Spraak-begeleiding
                try:
                    self._voice.speak(
                        "De opdrachtprompt is geopend. Klik nu op kopieer "
                        "bij stap twee, en plak het daarna in het zwarte venster."
                    )
                except Exception:
                    pass
            else:
                self.lbl_status.setText(
                    "⚠️ Deze functie werkt alleen op Windows. Open zelf een terminal."
                )
        except Exception as e:
            self.lbl_status.setText(f"⚠️ Kon Opdrachtprompt niet openen: {e}")

    def _guide_voice_install(self):
        """Begeleid de gebruiker stap voor stap met spraak."""
        steps = [
            "Welkom! Ik begeleid u door de installatie van spraakherkenning.",
            "Stap één. Klik op de groene knop, open opdrachtprompt nu. "
            "Er verschijnt dan een zwart venster met witte tekst.",
            "Stap twee. Kom terug naar dit venster. Bij stap twee staat een commando "
            "met een groene kopieer knop ernaast. Klik op die kopieer knop.",
            "Ga nu naar het zwarte venster. Klik er met uw rechter muisknop in. "
            "Het commando wordt geplakt. Druk dan op enter om te installeren.",
            "Het installeren duurt ongeveer twee minuten. "
            "Sluit daarna deze app en open hem opnieuw. Klaar!",
            "Krijgt u een foutmelding? Scroll naar beneden, naar 'route A', "
            "en gebruik de drie commando's daar. Die werken op alle Python versies, "
            "ook op de nieuwste. Negeer pipwin als u Python drie punt dertien heeft.",
        ]
        full_text = " ".join(steps)
        self.lbl_status.setText(
            "🎙️ Begeleiding gestart — luister naar mij. Klik op 'Test stem' om mij te onderbreken."
        )
        try:
            self._voice.speak(full_text)
        except Exception as e:
            self.lbl_status.setText(f"⚠️ Spraak-begeleiding faalde: {e}")

    def _make_command_box(self, command: str, big_font: QFont) -> QWidget:
        """
        Toon een commando in een selecteerbaar tekstveld met kopieer-knop.
        Hierdoor kan elke gebruiker (technisch of niet) het commando makkelijk
        meenemen naar de Opdrachtprompt.
        """
        from PySide6.QtWidgets import QLineEdit, QFrame, QApplication
        wrapper = QFrame()
        wrapper.setStyleSheet(
            "QFrame { background:#000000; border:2px solid #707070; border-radius:6px; }"
        )
        row = QHBoxLayout(wrapper)
        row.setContentsMargins(8, 6, 8, 6)
        row.setSpacing(8)

        # Selecteerbaar (read-only) tekstveld met het commando
        cmd_edit = QLineEdit(command)
        cmd_edit.setReadOnly(True)
        mono = QFont("Consolas", big_font.pointSize())
        if not mono.exactMatch():
            mono = QFont("Courier New", big_font.pointSize())
        cmd_edit.setFont(mono)
        cmd_edit.setStyleSheet(
            "QLineEdit { background:#000000; color:#9fff9f; border:none; "
            "padding:6px 4px; }"
        )
        cmd_edit.setCursorPosition(0)
        row.addWidget(cmd_edit, 1)

        # Kopieer-knop
        btn_copy = QPushButton("📋 Kopieer")
        btn_copy.setFont(big_font)
        btn_copy.setMinimumHeight(38)
        btn_copy.setStyleSheet(
            "QPushButton { background:#2a2a2a; color:#ffffff; "
            "border:1px solid #707070; border-radius:4px; padding:6px 12px; }"
            "QPushButton:hover { background:#3a3a3a; }"
            "QPushButton:pressed { background:#4a4a4a; }"
        )

        def do_copy():
            QApplication.clipboard().setText(command)
            # Visuele feedback: knoptekst even wijzigen
            btn_copy.setText("✓ Gekopieerd!")
            btn_copy.setStyleSheet(
                "QPushButton { background:#2a5a2a; color:#ffffff; "
                "border:1px solid #4a8a4a; border-radius:4px; padding:6px 12px; }"
            )
            QTimer.singleShot(1500, lambda: (
                btn_copy.setText("📋 Kopieer"),
                btn_copy.setStyleSheet(
                    "QPushButton { background:#2a2a2a; color:#ffffff; "
                    "border:1px solid #707070; border-radius:4px; padding:6px 12px; }"
                    "QPushButton:hover { background:#3a3a3a; }"
                )
            ))

        btn_copy.clicked.connect(do_copy)
        row.addWidget(btn_copy, 0)

        return wrapper

    def _populate_personal(self):
        if hasattr(self, "txt_user_name"):
            self.txt_user_name.setText(str(config.get("user_name", "")))

    def _preview_greeting(self):
        """Sla tijdelijk de naam op, spreek begroeting, herstel."""
        new_name = self.txt_user_name.text().strip()
        old_name = config.get("user_name", "")
        config.set("user_name", new_name)
        try:
            get_voice().speak(greeting(short=False))
        finally:
            # Herstel als het nog niet opgeslagen is via _save_all
            # (laat de naam staan; gebruiker hoeft niet eerst Save te klikken)
            pass

    def _toggle_voice_input(self):
        self._voice_input_state = not self._voice_input_state
        self.btn_voice_input.setText(
            self._toggle_label("Spraakherkenning", self._voice_input_state))
        self.btn_voice_input.setStyleSheet(self._toggle_style(self._voice_input_state))

    def _build_voice_tab(self, big_font: QFont) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 16, 8, 8)
        layout.setSpacing(12)

        info = QLabel(
            "Kies een stem uit de lijst en klik op 'Test stem' om hem te horen. "
            "Klik daarna op 'Opslaan' onderaan."
        )
        info.setFont(big_font)
        info.setWordWrap(True)
        layout.addWidget(info)

        self.lst_voices = QListWidget()
        self.lst_voices.setFont(big_font)
        self.lst_voices.setMinimumHeight(260)
        self.lst_voices.currentItemChanged.connect(self._on_voice_selected)
        layout.addWidget(self.lst_voices, 1)

        btn_test = QPushButton("🔊 Test stem")
        btn_test.setMinimumHeight(54)
        btn_test.setFont(QFont("Segoe UI", big_font.pointSize(), QFont.Bold))
        btn_test.clicked.connect(self._test_voice)
        layout.addWidget(btn_test)

        # Drie audio-instellingen naast elkaar
        audio_row = QHBoxLayout()
        audio_row.setSpacing(10)

        # ---- Volume ----
        vol_col = QVBoxLayout()
        vol_label = QLabel("🔉 Volume:")
        vol_label.setFont(QFont("Segoe UI", big_font.pointSize(), QFont.Bold))
        vol_col.addWidget(vol_label)
        self.lst_volumes = QListWidget()
        self.lst_volumes.setFont(big_font)
        self.lst_volumes.setMaximumHeight(190)
        self.lst_volumes.currentItemChanged.connect(self._on_volume_selected)
        vol_col.addWidget(self.lst_volumes)
        audio_row.addLayout(vol_col)

        # ---- Spreeksnelheid ----
        spd_col = QVBoxLayout()
        spd_label = QLabel("⏩ Snelheid:")
        spd_label.setFont(QFont("Segoe UI", big_font.pointSize(), QFont.Bold))
        spd_col.addWidget(spd_label)
        self.lst_speeds = QListWidget()
        self.lst_speeds.setFont(big_font)
        self.lst_speeds.setMaximumHeight(190)
        self.lst_speeds.currentItemChanged.connect(self._on_speed_selected)
        spd_col.addWidget(self.lst_speeds)
        audio_row.addLayout(spd_col)

        # ---- Toonhoogte (pitch) ----
        pit_col = QVBoxLayout()
        pit_label = QLabel("🎵 Toonhoogte:")
        pit_label.setFont(QFont("Segoe UI", big_font.pointSize(), QFont.Bold))
        pit_col.addWidget(pit_label)
        self.lst_pitches = QListWidget()
        self.lst_pitches.setFont(big_font)
        self.lst_pitches.setMaximumHeight(190)
        self.lst_pitches.currentItemChanged.connect(self._on_pitch_selected)
        pit_col.addWidget(self.lst_pitches)
        audio_row.addLayout(pit_col)

        layout.addLayout(audio_row)

        return tab

    # ---- Volume opties ----
    _VOLUME_OPTIONS = [
        ("Stil",        0.30),
        ("Zacht",       0.55),
        ("Normaal",     0.75),
        ("Wat luider",  0.85),
        ("Hard (max)",  0.95),
    ]
    # ---- Spreeksnelheid opties ----
    _SPEED_OPTIONS = [
        ("Heel langzaam", 0.70),
        ("Langzaam",      0.85),
        ("Normaal",       1.00),
        ("Snel",          1.15),
        ("Heel snel",     1.35),
    ]
    # ---- Toonhoogte opties (halve tonen) ----
    _PITCH_OPTIONS = [
        ("Heel laag",     -3.0),
        ("Laag",          -1.5),
        ("Normaal",        0.0),
        ("Hoog",           1.5),
        ("Heel hoog",      3.0),
    ]

    def _populate_audio_list(self, widget, options, current_value):
        widget.clear()
        best_i = min(
            range(len(options)),
            key=lambda i: abs(options[i][1] - current_value),
        )
        for i, (label, val) in enumerate(options):
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, val)
            widget.addItem(item)
            if i == best_i:
                widget.setCurrentItem(item)
        return options[best_i][1]

    def _populate_volumes(self):
        if not hasattr(self, "lst_volumes"):
            return
        cur = float(config.get("voice_volume", 0.95))
        sel = self._populate_audio_list(self.lst_volumes, self._VOLUME_OPTIONS, cur)
        self._selected_volume = sel
        self._saved_volume = sel

    def _populate_speeds(self):
        if not hasattr(self, "lst_speeds"):
            return
        cur = float(config.get("voice_speed", 1.0))
        sel = self._populate_audio_list(self.lst_speeds, self._SPEED_OPTIONS, cur)
        self._selected_speed = sel
        self._saved_speed = sel

    def _populate_pitches(self):
        if not hasattr(self, "lst_pitches"):
            return
        cur = float(config.get("voice_pitch", 0.0))
        sel = self._populate_audio_list(self.lst_pitches, self._PITCH_OPTIONS, cur)
        self._selected_pitch = sel
        self._saved_pitch = sel

    def _on_volume_selected(self, current, _previous):
        if current is None:
            return
        self._selected_volume = float(current.data(Qt.UserRole) or 0.95)

    def _on_speed_selected(self, current, _previous):
        if current is None:
            return
        self._selected_speed = float(current.data(Qt.UserRole) or 1.0)

    def _on_pitch_selected(self, current, _previous):
        if current is None:
            return
        self._selected_pitch = float(current.data(Qt.UserRole) or 0.0)

    def _build_mail_tab(self, big_font: QFont) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 16, 8, 8)
        layout.setSpacing(12)

        info = QLabel(_("settings_mail_intro"))
        info.setFont(big_font)
        info.setWordWrap(True)
        layout.addWidget(info)

        self.lst_intervals = QListWidget()
        self.lst_intervals.setFont(big_font)
        self.lst_intervals.setMinimumHeight(260)
        self.lst_intervals.currentItemChanged.connect(self._on_interval_selected)
        layout.addWidget(self.lst_intervals, 1)

        hint = QLabel(
            "De butler kondigt nieuwe e-mail aan met een notificatie en spraak."
        )
        hint.setFont(big_font)
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #b0b0b0; padding: 4px;")
        layout.addWidget(hint)

        return tab

    # ------------------------------------------------------------------
    def _build_browser_tab(self, big_font: QFont) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 16, 8, 8)
        layout.setSpacing(16)

        intro = QLabel(_("settings_browser_intro"))
        intro.setFont(big_font)
        intro.setWordWrap(True)
        layout.addWidget(intro)

        # Adblock toggle
        self.btn_adblock = QPushButton(self._toggle_label(
            _("settings_adblock"), self._adblock_state))
        self.btn_adblock.setMinimumHeight(70)
        self.btn_adblock.setFont(QFont("Segoe UI", big_font.pointSize(), QFont.Bold))
        self.btn_adblock.setStyleSheet(self._toggle_style(self._adblock_state))
        self.btn_adblock.clicked.connect(self._toggle_adblock)
        layout.addWidget(self.btn_adblock)

        # Cookies toggle
        self.btn_cookies = QPushButton(self._toggle_label(
            _("settings_cookies"), self._cookies_state))
        self.btn_cookies.setMinimumHeight(70)
        self.btn_cookies.setFont(QFont("Segoe UI", big_font.pointSize(), QFont.Bold))
        self.btn_cookies.setStyleSheet(self._toggle_style(self._cookies_state))
        self.btn_cookies.clicked.connect(self._toggle_cookies)
        layout.addWidget(self.btn_cookies)

        hint = QLabel(
            "Adblock werkt direct. Cookie-acceptatie wordt op elke geladen pagina "
            "geprobeerd; werkt niet altijd 100% omdat cookie-banners verschillen."
        )
        hint.setFont(big_font)
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #b0b0b0; padding: 4px;")
        layout.addWidget(hint)

        # ---- Zoekmachine keuze ----
        engine_label = QLabel("🔍 Standaard zoekmachine:")
        engine_label.setFont(QFont("Segoe UI", big_font.pointSize(), QFont.Bold))
        engine_label.setStyleSheet("padding-top: 12px;")
        layout.addWidget(engine_label)

        self.lst_engines = QListWidget()
        self.lst_engines.setFont(big_font)
        self.lst_engines.setMaximumHeight(220)
        self.lst_engines.currentItemChanged.connect(self._on_engine_selected)
        layout.addWidget(self.lst_engines)

        engine_hint = QLabel(
            "Deze wordt eerst geprobeerd voor algemene zoekopdrachten. "
            "Als hij geen resultaten geeft worden de andere automatisch als reserve gebruikt."
        )
        engine_hint.setFont(big_font)
        engine_hint.setWordWrap(True)
        engine_hint.setStyleSheet("color: #b0b0b0; padding: 4px;")
        layout.addWidget(engine_hint)

        layout.addStretch()
        return tab

    _ENGINE_OPTIONS = [
        ("DuckDuckGo (privacy, standaard)", "duckduckgo"),
        ("Bing",                            "bing"),
        ("Startpage (privacy, Google-index)", "startpage"),
        ("Qwant (privacy, Europees)",       "qwant"),
        ("Brave Search",                    "brave"),
        ("Google (kan captchas geven)",     "google"),
    ]

    def _populate_engines(self):
        if not hasattr(self, "lst_engines"):
            return
        # Onthoud huidige gebruikers-keuze (kan afwijken van saved)
        # en herstel als die nog in de lijst voorkomt na clear+vul
        prev_selection = getattr(self, "_selected_engine", None)
        self.lst_engines.clear()
        cur = config.get("default_search_engine", "duckduckgo")
        # Eerste keer: _saved_engine bestaat nog niet, anders houden we het
        if not hasattr(self, "_saved_engine"):
            self._saved_engine = cur
        # Bepaal welke we visueel selecteren: de niet-opgeslagen keuze als die er is
        select_key = prev_selection if prev_selection else self._saved_engine
        for label, key in self._ENGINE_OPTIONS:
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, key)
            self.lst_engines.addItem(item)
            if key == select_key:
                self.lst_engines.setCurrentItem(item)
        if self.lst_engines.currentItem() is None:
            self.lst_engines.setCurrentRow(0)

    def _on_engine_selected(self, current, _previous):
        if current is None:
            return
        self._selected_engine = str(current.data(Qt.UserRole) or "duckduckgo")

    def _build_character_tab(self, big_font: QFont) -> QWidget:

        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 16, 8, 8)
        layout.setSpacing(10)

        # ---- Karakter-keuze ----
        char_label = QLabel("👤 Karakter (wie verschijnt er rechtsonder?)")
        char_label.setFont(QFont("Segoe UI", big_font.pointSize(), QFont.Bold))
        layout.addWidget(char_label)

        # Lijst + preview naast elkaar
        char_row = QHBoxLayout()
        char_row.setSpacing(12)

        self.lst_characters = QListWidget()
        self.lst_characters.setFont(big_font)
        self.lst_characters.setMaximumHeight(220)
        self.lst_characters.currentItemChanged.connect(self._on_character_selected)
        char_row.addWidget(self.lst_characters, 2)

        # Preview-paneel rechts: toont het gekozen karakter
        # We gebruiken QLabel + QPixmap (zelf gerenderd met QSvgRenderer)
        # in plaats van QSvgWidget, omdat die laatste in PySide6 niet
        # consistent de aspect-ratio bewaart.
        preview_box = QWidget()
        preview_box.setMinimumWidth(200)
        preview_box.setMaximumWidth(230)
        preview_layout = QVBoxLayout(preview_box)
        preview_layout.setContentsMargins(8, 8, 8, 8)
        preview_layout.setSpacing(6)

        preview_title = QLabel("Voorbeeld:")
        preview_title.setFont(big_font)
        preview_title.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(preview_title)

        # SVG viewBox is 800x1000 = ratio 4:5
        # Render-doel: 176×220 = exact 4:5 verhouding
        self.character_preview = QLabel()
        self.character_preview.setFixedSize(176, 220)
        self.character_preview.setAlignment(Qt.AlignCenter)
        self.character_preview.setStyleSheet(
            "background: #1a1a1a; border: 1px solid #444; border-radius: 6px;"
        )
        # Centreer in het vak
        preview_center = QHBoxLayout()
        preview_center.addStretch()
        preview_center.addWidget(self.character_preview)
        preview_center.addStretch()
        preview_layout.addLayout(preview_center)
        preview_layout.addStretch()

        char_row.addWidget(preview_box, 1)

        layout.addLayout(char_row)

        # Knoppen voor eigen afbeelding
        img_row = QHBoxLayout()
        btn_pick = QPushButton("📁 Kies eigen afbeelding...")
        btn_pick.setMinimumHeight(40)
        btn_pick.setFont(big_font)
        btn_pick.clicked.connect(self._pick_custom_image)
        img_row.addWidget(btn_pick)

        btn_clear = QPushButton("✕ Eigen afbeelding wissen")
        btn_clear.setMinimumHeight(40)
        btn_clear.setFont(big_font)
        btn_clear.clicked.connect(self._clear_custom_image)
        img_row.addWidget(btn_clear)
        layout.addLayout(img_row)

        self.lbl_custom_image = QLabel("")
        self.lbl_custom_image.setFont(big_font)
        self.lbl_custom_image.setWordWrap(True)
        self.lbl_custom_image.setStyleSheet("color: #b0b0b0; padding: 4px;")
        layout.addWidget(self.lbl_custom_image)

        char_hint = QLabel(
            "Bij een ingebed karakter knipperen de ogen en beweegt de mond mee. "
            "Bij een eigen afbeelding worden geen animaties getoond — uw afbeelding "
            "staat statisch op het scherm, met spraakballon erbij."
        )
        char_hint.setFont(big_font)
        char_hint.setWordWrap(True)
        char_hint.setStyleSheet("color: #b0b0b0; padding: 4px;")
        layout.addWidget(char_hint)

        # ---- Ollama / lokale AI ----
        ai_label = QLabel("🧠 Lokale AI (Ollama) — voor slimme antwoorden")
        ai_label.setFont(QFont("Segoe UI", big_font.pointSize(), QFont.Bold))
        ai_label.setStyleSheet("padding-top: 12px;")
        layout.addWidget(ai_label)

        # GROOT statusveld bovenaan: vertelt direct of de server draait
        self.lbl_server_state = QLabel()
        self.lbl_server_state.setFont(QFont("Segoe UI", big_font.pointSize() + 2, QFont.Bold))
        self.lbl_server_state.setWordWrap(True)
        self.lbl_server_state.setMinimumHeight(60)
        self.lbl_server_state.setAlignment(Qt.AlignCenter)
        self.lbl_server_state.setStyleSheet(
            "background:#1a1a1a; border:2px solid #444; border-radius:8px; padding:12px;"
        )
        layout.addWidget(self.lbl_server_state)

        # Server-knoppen (Start/Stop/Detecteer) — direct onder status
        server_btn_row = QHBoxLayout()
        server_btn_row.setSpacing(10)

        self.btn_detect = QPushButton("🔄  Opnieuw detecteren")
        self.btn_detect.setMinimumHeight(52)
        self.btn_detect.setFont(big_font)
        self.btn_detect.setToolTip("Controleer of Ollama-server nu draait en welke modellen aanwezig zijn.")
        self.btn_detect.setStyleSheet(
            "QPushButton { background:#3a3a3a; color:#fff; "
            "border:2px solid #5a5a5a; border-radius:6px; padding:8px 12px; }"
            "QPushButton:hover { background:#4a4a4a; }"
        )
        self.btn_detect.clicked.connect(self._detect_ollama_with_voice)
        server_btn_row.addWidget(self.btn_detect)

        self.btn_start_ollama = QPushButton("▶️  Start Ollama")
        self.btn_start_ollama.setMinimumHeight(52)
        self.btn_start_ollama.setFont(QFont("Segoe UI", big_font.pointSize(), QFont.Bold))
        self.btn_start_ollama.setToolTip("Start de Ollama-server (vereist dat Ollama is geïnstalleerd).")
        self.btn_start_ollama.clicked.connect(self._start_ollama_now)
        server_btn_row.addWidget(self.btn_start_ollama)

        self.btn_stop_ollama = QPushButton("🛑  Stop Ollama")
        self.btn_stop_ollama.setMinimumHeight(52)
        self.btn_stop_ollama.setFont(QFont("Segoe UI", big_font.pointSize(), QFont.Bold))
        self.btn_stop_ollama.setToolTip("Stop de Ollama-server (kill alle ollama-processen).")
        self.btn_stop_ollama.clicked.connect(lambda: self.request_ollama_stop.emit())
        server_btn_row.addWidget(self.btn_stop_ollama)

        layout.addLayout(server_btn_row)

        # AAN/UIT-toggle: maakt nu DUIDELIJK dat het gaat om gebruik in zoekresultaten
        toggle_label = QLabel("\n💡 Wilt u AI-antwoorden in zoekresultaten?")
        toggle_label.setFont(QFont("Segoe UI", big_font.pointSize(), QFont.Bold))
        layout.addWidget(toggle_label)

        self.btn_ollama = QPushButton(self._toggle_label(
            "Slimme AI-antwoorden gebruiken", self._ollama_state))
        self.btn_ollama.setObjectName("toggle_ollama")
        self.btn_ollama.setMinimumHeight(56)
        self.btn_ollama.setFont(QFont("Segoe UI", big_font.pointSize(), QFont.Bold))
        self.btn_ollama.setStyleSheet(self._toggle_style(self._ollama_state))
        self.btn_ollama.setToolTip(
            "Schakelt AI-antwoorden in of uit. Werkt alleen als de "
            "Ollama-server draait (zie hierboven)."
        )
        self.btn_ollama.clicked.connect(self._toggle_ollama)
        layout.addWidget(self.btn_ollama)

        # Apart status-label
        self.lbl_ollama_toggle_state = QLabel()
        self.lbl_ollama_toggle_state.setFont(big_font)
        self._update_ollama_toggle_state_label()
        layout.addWidget(self.lbl_ollama_toggle_state)

        # Model-keuze
        model_label = QLabel("\nModel om te gebruiken:")
        model_label.setFont(QFont("Segoe UI", big_font.pointSize(), QFont.Bold))
        layout.addWidget(model_label)

        self.lst_models = QListWidget()
        self.lst_models.setFont(big_font)
        self.lst_models.setMaximumHeight(130)
        self.lst_models.currentItemChanged.connect(self._on_model_selected)
        layout.addWidget(self.lst_models)

        # Diagnose / hulptekst
        self.lbl_ollama_status = QLabel("")
        self.lbl_ollama_status.setFont(big_font)
        self.lbl_ollama_status.setWordWrap(True)
        self.lbl_ollama_status.setStyleSheet(
            "background:#2a2a2a; border:1px solid #555; padding:8px; color:#c0c0c0;"
        )
        layout.addWidget(self.lbl_ollama_status)

        ai_hint = QLabel(
            "Ollama (https://ollama.com) is gratis en draait volledig lokaal op uw pc. "
            "Installatiestappen: 1) Download en installeer Ollama. 2) Open Opdrachtprompt "
            "en typ 'ollama pull llama3.2' (~2 GB download). 3) Zet hier de schakelaar AAN "
            "en kies het model. Werkt zonder internetverbinding en zonder dat uw vragen "
            "naar buiten gaan."
        )
        ai_hint.setFont(big_font)
        ai_hint.setWordWrap(True)
        ai_hint.setStyleSheet("color: #b0b0b0; padding: 4px;")
        layout.addWidget(ai_hint)

        # Begeleide installatie + reset knoppen
        guide_row = QHBoxLayout()
        btn_guide = QPushButton("📖  Open begeleide installatie")
        btn_guide.setMinimumHeight(44)
        btn_guide.setFont(big_font)
        btn_guide.clicked.connect(self._open_install_guide)
        guide_row.addWidget(btn_guide)

        btn_reset = QPushButton("🔄  Reset Ollama-keuze")
        btn_reset.setMinimumHeight(44)
        btn_reset.setFont(big_font)
        btn_reset.setToolTip(
            "Reset de eerder gemaakte keuze ('Nee' of 'Later'), zodat de "
            "kennismakingsdialoog bij de volgende opstart weer verschijnt."
        )
        btn_reset.clicked.connect(self._reset_ollama_choice)
        guide_row.addWidget(btn_reset)

        layout.addLayout(guide_row)

        return tab

    def _detect_ollama_with_voice(self):
        """
        Opnieuw detecteren met spraak-feedback. Doet de check async zodat
        de butler-mondanimatie niet stilstaat tijdens het wachten op de
        HTTP-check (kan 1-2 seconden duren).
        """
        try:
            self._voice.speak("Een moment, ik controleer of Ollama draait.")
        except Exception:
            pass
        # Markeer dat we het resultaat willen uitspreken
        self._speak_detect_result = True
        self._populate_ollama()
        # Resultaat wordt uitgesproken via _on_ollama_diag_done (zie hieronder)

    def _start_ollama_now(self):
        """
        Start Ollama-server in een achtergrond-thread zodat de UI niet
        bevriest. Geeft spraak- + visuele feedback tijdens de wachttijd.
        """
        if ollama_is_available(timeout=1.5):
            msg = "✓ Ollama draait al, er hoeft niets gestart te worden."
            self.lbl_status.setText(msg)
            try:
                self._voice.speak("Ollama draait al.")
            except Exception:
                pass
            self._populate_ollama()
            return

        # Spraak + ballon: dit kan even duren
        wait_msg = "Een moment, ik start Ollama op. Dit kan tot 15 seconden duren."
        self.lbl_status.setText("⏳ " + wait_msg)
        try:
            self._voice.speak(wait_msg)
        except Exception:
            pass

        # Disable de knop tijdens het wachten
        sender = self.sender()
        if sender:
            sender.setEnabled(False)
            sender.setText("⏳  Bezig met starten...")

        # Run in achtergrond — parent=self voor veilige thread-cleanup
        # Bewaar vorige nog-lopende thread in lijst om premature GC te voorkomen
        if not hasattr(self, "_old_threads"):
            self._old_threads = []
        self._old_threads = [t for t in self._old_threads if t.isRunning()]
        if hasattr(self, "_ollama_start_thread") and self._ollama_start_thread is not None:
            if self._ollama_start_thread.isRunning():
                self._old_threads.append(self._ollama_start_thread)
        self._ollama_start_thread = _OllamaActionThread("start", parent=self)
        self._ollama_start_thread.finished_result.connect(
            lambda ok, info: self._on_ollama_start_done(ok, info, sender)
        )
        self._ollama_start_thread.start()

    def _on_ollama_start_done(self, ok: bool, info: str, sender_btn):
        """Callback wanneer Ollama-start-thread klaar is."""
        if sender_btn:
            sender_btn.setEnabled(True)
            sender_btn.setText("▶️  Start Ollama")
        if ok:
            msg = "Ollama is opgestart en klaar voor gebruik."
            self.lbl_status.setText("✓ " + msg)
            try:
                self._voice.speak(msg)
            except Exception:
                pass
            self._populate_ollama()
        else:
            msg = (
                "Het is niet gelukt Ollama te starten. "
                "Mogelijk is Ollama niet geïnstalleerd op uw pc. "
                "Download van ollama punt com."
            )
            self.lbl_status.setText("⚠️ " + msg)
            try:
                self._voice.speak(msg)
            except Exception:
                pass

    def _open_install_guide(self):
        show_install_guide(parent=self)
        # Refresh diagnostics na de gids
        self._populate_ollama()

    def _reset_ollama_choice(self):
        from PySide6.QtWidgets import QMessageBox
        ret = QMessageBox.question(
            self, "Bevestiging",
            "Wilt u de eerder gemaakte Ollama-keuze resetten?\n\n"
            "Bij de volgende opstart vraag ik dan weer of u Ollama wilt gebruiken. "
            "Uw huidige aan/uit-instelling blijft staan.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if ret != QMessageBox.Yes:
            return
        reset_ollama_choice()
        QMessageBox.information(
            self, "Gereset",
            "Keuze gereset. Bij de volgende opstart vraag ik het opnieuw."
        )

    def _populate_characters(self):
        if not hasattr(self, "lst_characters"):
            return
        prev_selection = getattr(self, "_selected_character", None)
        self.lst_characters.clear()
        cur = config.get("character_id", "alfred")
        if not hasattr(self, "_saved_character"):
            self._saved_character = cur
        select_key = prev_selection if prev_selection else self._saved_character
        for cid, name, desc in list_characters():
            item = QListWidgetItem(f"  {name}\n     {desc}")
            item.setData(Qt.UserRole, cid)
            self.lst_characters.addItem(item)
            if cid == select_key:
                self.lst_characters.setCurrentItem(item)
        if self.lst_characters.currentItem() is None:
            self.lst_characters.setCurrentRow(0)
        # Custom-image label updaten
        cur_img = str(config.get("character_custom_image", "")).strip()
        if cur_img:
            from pathlib import Path
            self.lbl_custom_image.setText(f"📁 Eigen afbeelding: {Path(cur_img).name}")
        else:
            self.lbl_custom_image.setText("(geen eigen afbeelding gekozen)")

    def _on_character_selected(self, current, _previous):
        if current is None:
            return
        char_id = str(current.data(Qt.UserRole) or "alfred")
        self._selected_character = char_id
        # Toon preview van het gekozen karakter direct (niet pas bij Opslaan)
        self._update_character_preview(char_id)

    def _update_character_preview(self, char_id: str):
        """
        Render het karakter naar een QPixmap met gegarandeerd aspect-ratio
        behoud, en toon die in het preview-label. We doen dit zelf met
        QSvgRenderer + QPainter omdat QSvgWidget de aspect-ratio niet
        consistent bewaart.
        """
        if not hasattr(self, "character_preview"):
            return
        try:
            from PySide6.QtSvg import QSvgRenderer
            from PySide6.QtGui import QPixmap, QPainter
            from PySide6.QtCore import QSize, QRectF, QByteArray

            char = get_character(char_id)
            svg_data = char.get("svg")
            if not svg_data:
                self.character_preview.clear()
                return

            # Maak een renderer met de SVG. We bewaren expliciet de aspect-ratio
            # door zelf te rekenen op basis van de viewBox (800x1000 voor onze
            # karakters).
            renderer = QSvgRenderer(QByteArray(bytes(svg_data, "utf-8")))

            # Doelgrootte: exact zoals de label
            target_w = self.character_preview.width()
            target_h = self.character_preview.height()
            # SVG-verhouding ophalen
            svg_size = renderer.defaultSize()
            if svg_size.width() <= 0 or svg_size.height() <= 0:
                svg_size = QSize(800, 1000)
            svg_ratio = svg_size.width() / svg_size.height()
            target_ratio = target_w / target_h if target_h > 0 else 1.0

            # Pas grootte aan zodat het past binnen target en aspect bewaard blijft
            if svg_ratio > target_ratio:
                # Breder dan target: paste op breedte
                draw_w = target_w
                draw_h = int(target_w / svg_ratio)
            else:
                # Smaller dan target: paste op hoogte
                draw_h = target_h
                draw_w = int(target_h * svg_ratio)

            # Maak pixmap met label-formaat, met de SVG gecentreerd erbinnen
            pixmap = QPixmap(target_w, target_h)
            pixmap.fill(Qt.transparent)

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
            # Centreer de teken-rechthoek
            x = (target_w - draw_w) // 2
            y = (target_h - draw_h) // 2
            renderer.render(painter, QRectF(x, y, draw_w, draw_h))
            painter.end()

            self.character_preview.setPixmap(pixmap)
        except Exception as e:
            print(f"[settings] preview laden faalde: {e}")

    def _pick_custom_image(self):
        from PySide6.QtWidgets import QFileDialog
        path, _ok = QFileDialog.getOpenFileName(
            self, "Kies een afbeelding voor het karakter",
            "", "Afbeeldingen (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if not path:
            return
        config.set("character_custom_image", path)
        config.set("character_id", "custom")
        from pathlib import Path
        self.lbl_custom_image.setText(f"📁 Eigen afbeelding: {Path(path).name}")
        self._selected_character = "custom"
        self._saved_character = "custom"
        # Live update via signaal
        self.character_changed.emit()

    def _clear_custom_image(self):
        config.set("character_custom_image", "")
        self.lbl_custom_image.setText("(geen eigen afbeelding gekozen)")
        # Reset naar Alfred
        config.set("character_id", "alfred")
        self._selected_character = "alfred"
        self._saved_character = "alfred"
        self._populate_characters()
        self.character_changed.emit()

    def _populate_ollama(self):
        """
        Start een achtergrond-thread om Ollama te detecteren. We blokkeren
        de Qt-hoofdthread NIET — anders staat de mond-animatie van de butler
        stil terwijl hij praat (de HTTP-check kan tot 2 seconden duren).
        De UI wordt geüpdatet via _on_ollama_diag_done als de thread klaar is.
        """
        if not hasattr(self, "lst_models"):
            return
        # Toon "controleren..." status direct (snel, niet blokkerend)
        if hasattr(self, "lbl_server_state"):
            self.lbl_server_state.setText("⏳  Controleren of Ollama draait...")
            self.lbl_server_state.setStyleSheet(
                "background:#2a2a2a; border:2px solid #555; "
                "border-radius:8px; padding:12px; color:#c0c0c0;"
            )
        if hasattr(self, "lbl_ollama_status"):
            self.lbl_ollama_status.setText("⏳ Status wordt gecontroleerd...")
        # Disable knoppen tijdens controle om dubbele klikken te voorkomen
        for btn_name in ["btn_detect", "btn_start_ollama", "btn_stop_ollama"]:
            if hasattr(self, btn_name):
                getattr(self, btn_name).setEnabled(False)

        # Run de diagnose in een achtergrond-thread.
        # CRITICAL: Geef self mee als parent zodat Qt de thread niet
        # vroegtijdig opruimt terwijl hij nog draait. Anders crash.
        # Als er nog een vorige diag-thread loopt: bewaar referentie zodat
        # de garbage collector hem niet vroegtijdig opruimt.
        if not hasattr(self, "_old_threads"):
            self._old_threads = []
        # Schuif voltooide threads uit de bewaar-lijst
        self._old_threads = [t for t in self._old_threads if t.isRunning()]
        # Als de vorige diag-thread nog loopt: hou hem in de lijst
        if hasattr(self, "_ollama_diag_thread") and self._ollama_diag_thread is not None:
            if self._ollama_diag_thread.isRunning():
                self._old_threads.append(self._ollama_diag_thread)

        self._ollama_diag_thread = _OllamaDiagThread(parent=self)
        self._ollama_diag_thread.result.connect(self._on_ollama_diag_done)
        self._ollama_diag_thread.start()

    def _on_ollama_diag_done(self, info: dict):
        """Callback wanneer de achtergrond-Ollama-diagnose klaar is."""
        if not hasattr(self, "lst_models"):
            return
        self.lst_models.clear()

        # Update server-state label + knop-stijlen
        self._update_server_state_ui(info)

        # Als _detect_ollama_with_voice ons heeft aangeroepen: spreek resultaat uit
        if getattr(self, "_speak_detect_result", False):
            self._speak_detect_result = False  # eenmalig
            try:
                if info.get("available"):
                    n = len(info.get("models", []))
                    self._voice.speak(
                        f"Ollama draait, met {n} model{'len' if n != 1 else ''} beschikbaar."
                    )
                else:
                    self._voice.speak("Ollama draait nu niet.")
            except Exception:
                pass

        if not info["available"]:
            extra = ""
            if info.get("installed"):
                extra = (
                    "  Ollama IS geïnstalleerd op uw pc, maar de server (op "
                    f"{info['url']}) draait niet. Probeer:\n"
                    "  • Klik op de groene knop '▶️ Start Ollama' hierboven\n"
                    "  • Of open Opdrachtprompt en typ: ollama serve"
                )
            else:
                extra = (
                    "  Ollama lijkt niet geïnstalleerd. Download het van "
                    "https://ollama.com en herstart DeskButler."
                )
            self.lbl_ollama_status.setText(
                "🔴 Ollama is niet bereikbaar.\n" + extra
            )
            return
        if not info["models"]:
            self.lbl_ollama_status.setText(
                "🟡 Ollama draait, maar er zijn nog geen modellen geïnstalleerd. "
                "Open Opdrachtprompt en typ:  ollama pull llama3.2"
            )
            return
        self.lbl_ollama_status.setText(
            f"🟢 Ollama draait op {info['url']}. {len(info['models'])} model(len) gevonden."
        )
        cur_model = config.get("ollama_model", "") or info["models"][0]
        for m in info["models"]:
            item = QListWidgetItem(m)
            item.setData(Qt.UserRole, m)
            self.lst_models.addItem(item)
            if m == cur_model:
                self.lst_models.setCurrentItem(item)
        if self.lst_models.currentItem() is None:
            self.lst_models.setCurrentRow(0)
        self._selected_model = self.lst_models.currentItem().text() if self.lst_models.currentItem() else ""
        self._saved_model = self._selected_model

    def _update_server_state_ui(self, info: dict):
        """
        Update het server-state label en de Start/Stop knop-stijlen op basis
        van de huidige Ollama-toestand. Slimme enable/disable + kleur:
          - Server draait      -> Start grijs/disabled, Stop fel rood/enabled
          - Server uit (install) -> Start fel groen/enabled, Stop grijs/disabled
          - Niet geïnstalleerd -> Start + Stop allebei grijs/disabled
        """
        if not hasattr(self, "lbl_server_state"):
            return

        available = info.get("available", False)
        installed = info.get("installed", False)

        # Server-state label bovenaan
        if available:
            n = len(info.get("models", []))
            self.lbl_server_state.setText(
                f"🟢  Ollama-server: DRAAIT   ({n} model{'len' if n != 1 else ''} klaar)"
            )
            self.lbl_server_state.setStyleSheet(
                "background:#1a3a1a; border:2px solid #4a8a4a; "
                "border-radius:8px; padding:12px; color:#a0e0a0;"
            )
        elif installed:
            self.lbl_server_state.setText(
                "🔴  Ollama-server: UIT   (geïnstalleerd, maar niet gestart)"
            )
            self.lbl_server_state.setStyleSheet(
                "background:#3a1a1a; border:2px solid #8a4a4a; "
                "border-radius:8px; padding:12px; color:#e0a0a0;"
            )
        else:
            self.lbl_server_state.setText(
                "⚪  Ollama: NIET GEÏNSTALLEERD op deze pc"
            )
            self.lbl_server_state.setStyleSheet(
                "background:#2a2a2a; border:2px solid #555; "
                "border-radius:8px; padding:12px; color:#c0c0c0;"
            )

        # Start-knop: fel groen als nodig, grijs/disabled anders
        if available:
            # Server draait -> Start niet nodig
            self.btn_start_ollama.setEnabled(False)
            self.btn_start_ollama.setStyleSheet(
                "QPushButton { background:#2a2a2a; color:#666; "
                "border:2px solid #444; border-radius:6px; padding:8px 12px; }"
            )
        elif installed:
            # Server uit + Ollama geïnstalleerd -> Start fel groen
            self.btn_start_ollama.setEnabled(True)
            self.btn_start_ollama.setStyleSheet(
                "QPushButton { background:#2a8a2a; color:#fff; "
                "border:2px solid #4aaa4a; border-radius:6px; padding:8px 12px; }"
                "QPushButton:hover { background:#3a9a3a; }"
            )
        else:
            # Niet geïnstalleerd -> Start uit
            self.btn_start_ollama.setEnabled(False)
            self.btn_start_ollama.setStyleSheet(
                "QPushButton { background:#2a2a2a; color:#666; "
                "border:2px solid #444; border-radius:6px; padding:8px 12px; }"
            )

        # Stop-knop: fel rood als server draait, grijs anders
        if available:
            self.btn_stop_ollama.setEnabled(True)
            self.btn_stop_ollama.setStyleSheet(
                "QPushButton { background:#8a2a2a; color:#fff; "
                "border:2px solid #aa4a4a; border-radius:6px; padding:8px 12px; }"
                "QPushButton:hover { background:#9a3a3a; }"
            )
        else:
            self.btn_stop_ollama.setEnabled(False)
            self.btn_stop_ollama.setStyleSheet(
                "QPushButton { background:#2a2a2a; color:#666; "
                "border:2px solid #444; border-radius:6px; padding:8px 12px; }"
            )

        # Detect-knop: altijd actief (gebruikt async, blokkeert niet meer)
        if hasattr(self, "btn_detect"):
            self.btn_detect.setEnabled(True)

    def _on_model_selected(self, current, _previous):
        if current is None:
            return
        self._selected_model = str(current.data(Qt.UserRole) or "")

    def _toggle_ollama(self):
        self._ollama_state = not self._ollama_state
        self.btn_ollama.setText(self._toggle_label(
            "Slimme AI-antwoorden gebruiken", self._ollama_state))
        self.btn_ollama.setStyleSheet(self._toggle_style(self._ollama_state))
        self.btn_ollama.style().unpolish(self.btn_ollama)
        self.btn_ollama.style().polish(self.btn_ollama)
        self.btn_ollama.update()
        self._update_ollama_toggle_state_label()
        # Audio-feedback zodat de gebruiker weet dat de klik geregistreerd is
        try:
            msg = "AI staat aan" if self._ollama_state else "AI staat uit"
            self.lbl_status.setText(
                f"{'🟢' if self._ollama_state else '⚪'} {msg} — klik 'Opslaan' om te bevestigen."
            )
        except Exception:
            pass

    def _update_ollama_toggle_state_label(self):
        if not hasattr(self, "lbl_ollama_toggle_state"):
            return
        if self._ollama_state:
            self.lbl_ollama_toggle_state.setText("    ➜ Status: 🟢 AAN (klik knop om uit te zetten)")
            self.lbl_ollama_toggle_state.setStyleSheet("color: #80c080; padding: 4px;")
        else:
            self.lbl_ollama_toggle_state.setText("    ➜ Status: ⚪ UIT (klik knop om aan te zetten)")
            self.lbl_ollama_toggle_state.setStyleSheet("color: #a0a0a0; padding: 4px;")

    def _toggle_label(self, name: str, state: bool) -> str:
        suffix = _("settings_toggle_on") if state else _("settings_toggle_off")
        icon = "✓" if state else "✕"
        return f"{icon}  {name}:  {suffix}"

    def _toggle_style(self, on: bool) -> str:
        """
        Stijl voor alle aan/uit-toggles in de app. Groen voor 'aan',
        rood voor 'uit'. Belangrijk voor toegankelijkheid: gebruikers
        met zichtbeperkingen zien meteen aan de kleur in welke stand
        de schakelaar staat.
        """
        if on:
            # Groen: AAN / actief
            return (
                "QPushButton { background-color: #2a8a2a; color: #ffffff; "
                "border: 3px solid #4aaa4a; border-radius: 6px; "
                "padding: 8px 20px; font-weight: bold; }"
                "QPushButton:hover { background-color: #3a9a3a; }"
                "QPushButton:disabled { background-color: #2a2a2a; "
                "color: #666; border-color: #444; }"
            )
        # Rood: UIT / inactief
        return (
            "QPushButton { background-color: #8a2a2a; color: #ffffff; "
            "border: 3px solid #aa4a4a; border-radius: 6px; "
            "padding: 8px 20px; font-weight: bold; }"
            "QPushButton:hover { background-color: #9a3a3a; }"
            "QPushButton:disabled { background-color: #2a2a2a; "
            "color: #666; border-color: #444; }"
        )

    def _toggle_adblock(self):
        self._adblock_state = not self._adblock_state
        self.btn_adblock.setText(self._toggle_label(_("settings_adblock"), self._adblock_state))
        self.btn_adblock.setStyleSheet(self._toggle_style(self._adblock_state))

    def _toggle_cookies(self):
        self._cookies_state = not self._cookies_state
        self.btn_cookies.setText(self._toggle_label(_("settings_cookies"), self._cookies_state))
        self.btn_cookies.setStyleSheet(self._toggle_style(self._cookies_state))

    # ------------------------------------------------------------------
    def _apply_theme(self):
        apply_dialog_style(self)


    # ------------------------------------------------------------------
    # Stem
    # ------------------------------------------------------------------
    def _populate_voices(self):
        self.lst_voices.clear()
        engine_type = self._voice.engine_type

        if engine_type != "neuvoice":
            self.lbl_status.setText(
                "Neuvoice is niet beschikbaar. Mogelijk nog aan het laden; "
                "sluit dit venster en probeer het later opnieuw."
            )
            return

        names = self._voice.list_voice_names()
        if not names:
            self.lbl_status.setText(
                "Geen stemmen gevonden in Neuvoice. Herstart DeskButler."
            )
            return

        for name in names:
            item = QListWidgetItem(name)
            self.lst_voices.addItem(item)
            if name == self._saved_voice:
                self.lst_voices.setCurrentItem(item)

        if self.lst_voices.currentItem() is None:
            self.lst_voices.setCurrentRow(0)

        self.lbl_status.setText(
            f"Huidige stem: {self._saved_voice}.  "
            f"Mail-check: {self._format_interval(self._saved_interval)}."
        )

    def _on_voice_selected(self, current, _previous):
        if current is None:
            return
        self._selected_voice = current.text()

    def _test_voice(self):
        if not self._selected_voice:
            return
        lang = detect_language()
        phrase = TEST_PHRASES.get(lang, TEST_PHRASES["en"])
        self.lbl_status.setText(
            f"🔊 Testen met stem '{self._selected_voice}'... "
            f"(klik op Opslaan om deze stem ook elders te gebruiken)"
        )
        self._voice.speak(phrase, voice_name=self._selected_voice)

    # ------------------------------------------------------------------
    # Mail interval
    # ------------------------------------------------------------------
    def _format_interval(self, mins: int) -> str:
        if mins == 0:
            return _("settings_mail_off")
        if mins == 1:
            return _("settings_mail_every_one")
        return _("settings_mail_every", n=mins)

    def _populate_intervals(self):
        self.lst_intervals.clear()
        for mins in MAIL_INTERVALS:
            item = QListWidgetItem(self._format_interval(mins))
            item.setData(Qt.UserRole, mins)
            self.lst_intervals.addItem(item)
            if mins == self._saved_interval:
                self.lst_intervals.setCurrentItem(item)

        if self.lst_intervals.currentItem() is None:
            # Selecteer de eerste die niet 0 is
            for i in range(self.lst_intervals.count()):
                it = self.lst_intervals.item(i)
                if it.data(Qt.UserRole) == 5:
                    self.lst_intervals.setCurrentItem(it)
                    break

    def _on_interval_selected(self, current, _previous):
        if current is None:
            return
        self._selected_interval = int(current.data(Qt.UserRole) or 0)

    # ------------------------------------------------------------------
    def _save_all(self):
        voice_changed = self._selected_voice and self._selected_voice != self._saved_voice
        new_user_name = self.txt_user_name.text().strip() if hasattr(self, "txt_user_name") else self._saved_user_name
        user_name_changed = new_user_name != self._saved_user_name
        interval_changed = self._selected_interval != self._saved_interval
        adblock_changed = self._adblock_state != bool(config.get("adblock_enabled", True))
        cookies_changed = self._cookies_state != bool(config.get("auto_accept_cookies", True))
        volume_changed = abs(self._selected_volume - self._saved_volume) > 0.01
        speed_changed = abs(self._selected_speed - self._saved_speed) > 0.01
        pitch_changed = abs(self._selected_pitch - self._saved_pitch) > 0.05
        engine_changed = self._selected_engine != self._saved_engine
        char_changed = self._selected_character != self._saved_character
        ollama_changed = self._ollama_state != bool(config.get("use_ollama", False))
        model_changed = self._selected_model != self._saved_model

        if voice_changed:
            config.set("voice_name", self._selected_voice)
            self._saved_voice = self._selected_voice

        if user_name_changed:
            config.set("user_name", new_user_name)
            self._saved_user_name = new_user_name

        # Voice input toggle
        if hasattr(self, "_voice_input_state"):
            new_vi = bool(self._voice_input_state)
            if new_vi != bool(config.get("voice_input_enabled", False)):
                config.set("voice_input_enabled", new_vi)
                # Hot-reload bij main app
                try:
                    from PySide6.QtWidgets import QApplication
                    for w in QApplication.topLevelWidgets():
                        app = getattr(w, "_deskbutler_main", None)
                        if app:
                            if new_vi:
                                app.start_voice_input()
                            else:
                                app.stop_voice_input()
                            break
                except Exception:
                    pass

        if volume_changed:
            config.set("voice_volume", self._selected_volume)
            self._saved_volume = self._selected_volume

        if speed_changed:
            config.set("voice_speed", self._selected_speed)
            self._saved_speed = self._selected_speed

        if pitch_changed:
            config.set("voice_pitch", self._selected_pitch)
            self._saved_pitch = self._selected_pitch

        if engine_changed:
            config.set("default_search_engine", self._selected_engine)
            self._saved_engine = self._selected_engine
            # Signal naar main app
            self.engine_changed.emit(self._selected_engine)

        if char_changed:
            config.set("character_id", self._selected_character)
            self._saved_character = self._selected_character
            # Signal naar main app voor hot-reload van butler
            self.character_changed.emit()

        if ollama_changed:
            config.set("use_ollama", self._ollama_state)
            self.ollama_changed.emit(self._ollama_state)
        if model_changed:
            config.set("ollama_model", self._selected_model)
            self._saved_model = self._selected_model

        if interval_changed:
            config.set("mail_check_interval_min", self._selected_interval)
            self._saved_interval = self._selected_interval
            if self._mail_checker is not None:
                self._mail_checker.reload_interval()

        if adblock_changed:
            config.set("adblock_enabled", self._adblock_state)
        if cookies_changed:
            config.set("auto_accept_cookies", self._cookies_state)
        if (adblock_changed or cookies_changed) and self._browser_window is not None:
            try:
                self._browser_window.refresh_extras()
            except Exception:
                pass

        # Statusupdate
        changes = []
        if voice_changed:
            changes.append(f"stem: {self._saved_voice}")
        if user_name_changed:
            changes.append(f"naam: {self._saved_user_name or '(leeg)'}")
        if volume_changed:
            changes.append(f"volume: {int(self._saved_volume * 100)}%")
        if speed_changed:
            changes.append(f"snelheid: {self._saved_speed:.2f}x")
        if pitch_changed:
            sign = "+" if self._saved_pitch >= 0 else ""
            changes.append(f"toon: {sign}{self._saved_pitch:.1f} ht")
        if engine_changed:
            changes.append(f"zoekmachine: {self._saved_engine}")
        if char_changed:
            changes.append(f"karakter: {self._saved_character}")
        if ollama_changed:
            changes.append(f"AI: {'aan' if self._ollama_state else 'uit'}")
        if model_changed:
            changes.append(f"model: {self._saved_model}")
        if interval_changed:
            changes.append(f"mail-check: {self._format_interval(self._saved_interval)}")
        if adblock_changed:
            changes.append(f"adblock: {'aan' if self._adblock_state else 'uit'}")
        if cookies_changed:
            changes.append(f"cookies: {'aan' if self._cookies_state else 'uit'}")
        if changes:
            self.lbl_status.setText("Opgeslagen — " + ", ".join(changes))
            lang = detect_language()
            confirm = {
                "nl": "De instellingen zijn opgeslagen.",
                "en": "Settings saved.",
                "de": "Einstellungen gespeichert.",
                "fr": "Réglages enregistrés.",
            }
            self._voice.speak(confirm.get(lang, confirm["en"]))
            # NIET meer automatisch sluiten — gebruiker kan blijven testen.
            # Status-tekst toont al dat het is opgeslagen.
        else:
            self.lbl_status.setText("Niets gewijzigd.")
            # Ook hier niet automatisch sluiten

    def closeEvent(self, event):
        try:
            self._voice.stop()
        except Exception:
            pass
        super().closeEvent(event)


# ========================================================================
# MAIN entry point  (was: main.py)
# ========================================================================

# Voeg het project root toe aan sys.path zodat 'config' etc. importeerbaar zijn
# (sys.path manipulatie niet nodig in single-file versie)

# *** ALS EERSTE: log-setup activeren ***
# Dit MOET vóór alle andere imports/code zodat ook eventuele import-fouten
# in de log terechtkomen.
try:
    _log_path = setup_logging()
    if _log_path:
        print(f"[logging] Logs worden geschreven naar: {_log_path}")
except Exception as e:
    print(f"[logging] Kon logging niet opzetten: {e}")
    _log_path = None


# Voeg het project root toe aan sys.path zodat 'config' etc. importeerbaar zijn
# (ROOT niet nodig in single-file versie)
# (geen sys.path manipulatie nodig in single-file versie)





class DeskButlerApp:
    """Hoofdklasse die alles bij elkaar houdt."""

    def __init__(self, qapp: QApplication):
        self.app = qapp
        self.app.setQuitOnLastWindowClosed(False)  # tray blijft draaien
        self.app.setApplicationName("DeskButler")
        self.app.setWindowIcon(QIcon(str(ICON_PATH)))

        # ---- Core components ----
        print(f"[main] Taal: {detect_language()}")
        print("[main] Stem initialiseren...")
        self.voice = get_voice()
        print(f"[main] Stem-engine: {self.voice.engine_type}")

        # ---- UI components ----
        self.butler = ButlerWidget()
        self.tray = TrayManager(self.app)
        self.hotkeys = HotkeyManager()
        self.scheduler = ReminderScheduler()
        self.mail_checker = MailChecker()
        self._voice_input = None  # microfoon-luisteraar, lazy init

        # Lazy windows
        self._search_win: SearchWindow | None = None
        self._browser_win: BrowserWindow | None = None
        self._email_win: EmailWindow | None = None
        self._calendar_win: CalendarWindow | None = None
        self._todo_win: TodoWindow | None = None
        self._guide_win: QuickGuideWindow | None = None
        self._settings_win: SettingsWindow | None = None

        self._wire_signals()
        self._show_initial()
        self._first_time_greeting()

    # ------------------------------------------------------------------
    def _wire_signals(self):
        """Verbind alle signalen tussen tray, butler, hotkey en vensters."""

        # Tray menu
        self.tray.open_search.connect(self.show_search)
        self.tray.open_email.connect(self.show_email)
        self.tray.open_browser.connect(self.show_browser)
        self.tray.open_calendar.connect(self.show_calendar)
        self.tray.open_todo.connect(self.show_todo)
        self.tray.open_quickguide.connect(self.show_quickguide)
        self.tray.open_settings.connect(self.show_settings)
        self.tray.show_about.connect(self.show_about)
        self.tray.open_donation.connect(self.show_donation)
        self.tray.open_contact.connect(self.show_contact)
        self.tray.quit_requested.connect(self.quit)

        # Butler clicks
        self.butler.clicked.connect(self.show_search)
        self.butler.right_clicked.connect(self.tray.show_context_menu_at)

        # Hotkeys
        self.hotkeys.search_triggered.connect(self.show_search)
        self.hotkeys.read_clipboard_triggered.connect(self._read_clipboard)

        # Mail checker -> nieuwe mail melding
        self.mail_checker.new_mail.connect(self._on_new_mail)
        self.mail_checker.check_error.connect(self._on_mail_check_error)

    def _show_initial(self):
        """Toon de butler en start alle achtergrond-diensten.

        We wrappen elke start in zijn eigen try/except zodat een
        crash van bijvoorbeeld de hotkey-luisteraar niet voorkomt
        dat de mail-check start.
        """
        print("[main] _show_initial: butler tonen...")
        try:
            self.butler.show()
        except Exception as e:
            print(f"[main] butler.show faalde: {e}")

        print("[main] _show_initial: hotkeys starten...")
        try:
            self.hotkeys.start()
        except Exception as e:
            print(f"[main] hotkeys.start faalde: {e}")

        print("[main] _show_initial: scheduler starten...")
        try:
            self.scheduler.start()
        except Exception as e:
            print(f"[main] scheduler.start faalde: {e}")

        print("[main] _show_initial: mail_checker starten...")
        try:
            self.mail_checker.start()
        except Exception as e:
            print(f"[main] mail_checker.start faalde: {e}")
        print("[main] _show_initial: voltooid")

    def _read_clipboard(self):
        """Lees de huidige klembord-inhoud voor."""
        try:
            text = QGuiApplication.clipboard().text()
        except Exception as e:
            print(f"[clipboard] kon niet lezen: {e}")
            self.butler.speak("Het klembord kon ik niet uitlezen.")
            return
        text = (text or "").strip()
        if not text:
            self.butler.speak("Het klembord is leeg.")
            return
        # Te lange teksten: spreek alleen het begin uit
        if len(text) > 1200:
            text = text[:1200] + "..."
        print(f"[clipboard] {len(text)} tekens voorgelezen")
        self.butler.speak(text)

    def _on_mail_check_error(self, account_name: str, error: str):
        """
        Achtergrond mail-check leverde een fout. Eerste keer NEGEREN
        (kan tijdelijke netwerkstoring zijn). Bij herhaling: éénmalig
        kort melden zodat de gebruiker weet wat er speelt.
        """
        # Initialiseer teller als nodig
        if not hasattr(self, "_mail_error_count"):
            self._mail_error_count = {}
        c = self._mail_error_count.get(account_name, 0) + 1
        self._mail_error_count[account_name] = c

        print(f"[main] mail-check fout #{c} voor {account_name}: {error}")

        # Bij eerste fout: stil negeren (vaak tijdelijk)
        # Bij DERDE achtereenvolgende fout: één keer melden
        if c == 3:
            try:
                self.butler.show_bubble(
                    f"⚠️ Mail-check geeft herhaalde fouten op {account_name}. "
                    "Controleer wachtwoord/server in Instellingen.",
                    duration_ms=6000,
                )
            except Exception:
                pass
        # Bij succes wordt teller gereset in _on_new_mail

    def _on_new_mail(self, account_name: str, count: int, is_initial: bool = False):
        """Meldt nieuwe mail via tray-balloon en butler-spraak, vraagt of de gebruiker wil openen."""
        # Reset error-teller voor dit account (succesvolle check)
        if hasattr(self, "_mail_error_count"):
            self._mail_error_count.pop(account_name, None)

        if is_initial:
            # Bij eerste check sinds opstart: vertel hoeveel ongelezen er zijn
            if count == 1:
                text = f"U heeft een ongelezen bericht in {account_name}."
            else:
                text = f"U heeft {count} ongelezen berichten in {account_name}."
        else:
            # Bij latere checks: alleen NIEUW binnengekomen
            if count == 1:
                text = _("new_mail_one", account=account_name)
            else:
                text = _("new_mail_many", count=count, account=account_name)
        try:
            self.tray.show_message(_("app_name"), text)
        except Exception:
            pass
        # Eerst de melding voorlezen + ballon tonen
        self.butler.speak(text)

        # Daarna: vraag of de gebruiker de mail wil openen
        # Wacht kort zodat de spraak van de melding voorbij kan zijn,
        # zodat de twee spraken niet over elkaar heen lopen.
        # We schatten op basis van tekstlengte (ongeveer 15 chars per seconde).
        wait_ms = max(1500, min(6000, len(text) * 80))
        QTimer.singleShot(wait_ms, self._ask_open_mail)

    def _ask_open_mail(self):
        """Vraag de gebruiker via dialoog + spraak of hij de mail wil openen."""
        # Eerst spraak (vraag) + dan de dialoog
        question = "Wilt u uw mail openen om de berichten te bekijken?"
        try:
            self.butler.speak(question)
        except Exception:
            pass

        # Korte vertraging zodat de vraag-spraak eerst klinkt
        QTimer.singleShot(2500, self._show_open_mail_dialog)

    def _show_open_mail_dialog(self):
        """Toon de ja/nee-dialoog na de spraak-vraag."""
        try:
            dlg = YesNoDialog(
                question="Wilt u uw mail openen om de berichten te bekijken?",
                title="Nieuwe berichten",
                yes_text="Ja, mail openen",
                no_text="Nee, later",
                parent=None,
            )
            if dlg.exec() == YesNoDialog.Accepted:
                try:
                    self.butler.speak("Goed, ik open uw mail.")
                except Exception:
                    pass
                self.show_email()
            else:
                try:
                    self.butler.speak("Oké, ik laat de berichten staan.")
                except Exception:
                    pass
        except Exception as e:
            print(f"[main] mail-vraag faalde: {e}")

    def _first_time_greeting(self):
        """Begroet de gebruiker bij het opstarten."""
        if config.get("first_run", True):
            QTimer.singleShot(1200, self._do_first_run_intro)
            config.set("first_run", False)
        else:
            # Eerste opstart van vandaag? Dan een uitgebreidere briefing
            today = datetime.now().strftime("%Y-%m-%d")
            last = config.get("last_briefing_date", "")
            if last != today:
                config.set("last_briefing_date", today)
                QTimer.singleShot(800, self._do_morning_briefing)
            else:
                QTimer.singleShot(800, self._do_greeting)

        # Ollama-check: na 4 seconden, zodat de begroeting eerst klinkt
        # en niet door een popup wordt onderbroken.
        # Ollama-check + voice-input na 4 seconden, na de begroeting
        QTimer.singleShot(4000, self._check_ollama_on_startup)
        QTimer.singleShot(5000, self.start_voice_input)
        # Update-check na 6 seconden (na alle andere startup-activiteiten)
        QTimer.singleShot(6000, self._check_for_update)

    def _check_ollama_on_startup(self):
        """
        Bij opstart: alleen detecteren wat de status van Ollama is.
        We starten Ollama NOOIT automatisch — dat doet de gebruiker zelf
        via de knop in Settings. Dit voorkomt vastlopers, dubbele processen
        en verrassingen.
        """
        try:
            check_ollama_on_startup(parent=None)
            self._detect_ollama_status()
        except Exception as e:
            print(f"[main] Ollama-check faalde: {e}")

    def _detect_ollama_status(self):
        """
        Eenvoudige niet-blokkerende detectie. Toont een korte ballon met
        de status zodat de gebruiker weet wat er aan de hand is. Stopt
        daar — geen auto-start, geen preload.
        """

        if ollama_is_available(timeout=2.0):
            try:
                models = ollama_list_models()
            except Exception:
                models = []
            n = len(models)
            self.butler.show_bubble(
                f"🟢 Ollama gedetecteerd — {n} model{'len' if n != 1 else ''} klaar voor gebruik.",
                duration_ms=3500,
            )
            # Als use_ollama AAN staat en preload is gewenst: doe dat zachtjes
            if config.get("use_ollama", False) and config.get("ollama_preload_at_startup", False):
                self._preload_ollama_quietly()
            return

        # Niet bereikbaar via API — kijk of proces wel draait (mogelijk warm-up)
        if _ollama_process_running_on_system():
            self.butler.show_bubble(
                "🟡 Ollama proces draait — wacht op verbinding...",
                duration_ms=3000,
            )
            return

        # Volledig niet beschikbaar — alleen melden als gebruiker Ollama gebruikt
        if config.get("use_ollama", False):
            if is_ollama_installed():
                # Vraag of we Ollama mogen starten (in plaats van alleen melden)
                QTimer.singleShot(800, self._ask_start_ollama)
            else:
                self.butler.show_bubble(
                    "⚪ Ollama is niet geïnstalleerd op deze pc.",
                    duration_ms=3500,
                )
        # Anders: stilte. Gebruiker weet niets van Ollama, en hoeft het ook niet te weten.

    def _ask_start_ollama(self):
        """Vraag de gebruiker of Ollama gestart mag worden bij opstart."""
        question = (
            "Ollama is geïnstalleerd op uw pc maar draait nu niet. "
            "Wilt u dat ik Ollama voor u opstart? Dat duurt ongeveer 15 seconden."
        )
        try:
            self.butler.speak(question)
        except Exception:
            pass
        # Korte vertraging voor de spraak
        QTimer.singleShot(4500, self._show_start_ollama_dialog)

    def _show_start_ollama_dialog(self):
        """Toon de ja/nee-dialoog na de spraak-vraag."""
        try:
            dlg = YesNoDialog(
                question=(
                    "Ollama is geïnstalleerd maar draait niet. "
                    "Wilt u dat ik Ollama voor u opstart?\n\n"
                    "Dat duurt ongeveer 15 seconden."
                ),
                title="Ollama opstarten?",
                yes_text="Ja, starten",
                no_text="Nee, laat maar",
                parent=None,
            )
            if dlg.exec() == YesNoDialog.Accepted:
                try:
                    self.butler.speak(
                        "Goed, ik start Ollama op. Een moment, dit kan tot 15 seconden duren."
                    )
                except Exception:
                    pass
                # Doe de start in een achtergrond-thread zodat UI niet bevriest
                self._start_ollama_in_background()
            else:
                try:
                    self.butler.speak("Oké, geen probleem. U kunt het later via instellingen doen.")
                except Exception:
                    pass
        except Exception as e:
            print(f"[main] ollama-vraag faalde: {e}")

    def _start_ollama_in_background(self):
        """Start Ollama in achtergrond + spraak-feedback als klaar."""
        from PySide6.QtCore import QThread, Signal as _Signal
        from PySide6.QtCore import QObject

        # Bewaar app als parent zodat de QThread niet vroegtijdig wordt
        # opgeruimd. We gebruiken een dummy QObject als parent omdat self
        # van DeskButlerApp geen QObject is.
        if not hasattr(self, "_thread_parent"):
            self._thread_parent = QObject()
        # Bewaar oude threads in lijst tot ze klaar zijn (anti-GC)
        if not hasattr(self, "_old_threads"):
            self._old_threads = []
        self._old_threads = [t for t in self._old_threads if t.isRunning()]
        if hasattr(self, "_ollama_bg_start_thread") and self._ollama_bg_start_thread is not None:
            if self._ollama_bg_start_thread.isRunning():
                self._old_threads.append(self._ollama_bg_start_thread)

        class _StartThread(QThread):
            done = _Signal(bool)
            def run(self):
                try:
                    ok = ollama_try_start()
                except Exception:
                    ok = False
                self.done.emit(ok)

        self._ollama_bg_start_thread = _StartThread(self._thread_parent)
        self._ollama_bg_start_thread.done.connect(self._on_ollama_bg_start_done)
        self._ollama_bg_start_thread.start()

    def _on_ollama_bg_start_done(self, ok: bool):
        """Callback na het opstarten van Ollama."""
        if ok:
            try:
                self.butler.speak("Ollama is opgestart en klaar voor gebruik.")
            except Exception:
                pass
        else:
            try:
                self.butler.speak(
                    "Het is niet gelukt om Ollama te starten. "
                    "U kunt het zelf proberen via instellingen, karakter en AI."
                )
            except Exception:
                pass

    def _preload_ollama_quietly(self):
        """Preload alleen als gebruiker dit expliciet aan heeft staan."""

        model = config.get("ollama_model", "")
        if not model:
            return

        def on_status(msg):
            QTimer.singleShot(0, lambda m=msg: self.butler.show_bubble(
                f"🧠 {m}", duration_ms=2200
            ))

        def on_done(ok):
            if ok:
                QTimer.singleShot(0, lambda: self.butler.show_bubble(
                    "✨ AI-model klaar voor gebruik!", duration_ms=2200
                ))

        ollama_preload_async(model=model, on_status=on_status, on_done=on_done)

    def _start_and_preload_ollama(self):
        """
        Behouden voor compatibiliteit met de Settings 'Start Ollama' knop.
        Wordt alleen aangeroepen wanneer de gebruiker daar expliciet om vraagt.
        """

        if ollama_is_available_with_retries(total_seconds=6.0):
            self.butler.show_bubble("🟢 Ollama draait al.", duration_ms=2500)
            if config.get("ollama_preload_at_startup", False):
                self._preload_ollama_quietly()
            return

        self.butler.show_bubble("🚀 Ollama wordt opgestart...", duration_ms=3000)
        if not ollama_try_start():
            self.butler.show_bubble(
                "⚠️ Ollama kon niet automatisch worden gestart. "
                "Controleer of Ollama is geïnstalleerd.",
                duration_ms=4000,
            )
            return

        if config.get("ollama_preload_at_startup", False):
            self._preload_ollama_quietly()

    def _do_greeting(self):
        self.butler.speak(greeting(short=False))

    def _do_first_run_intro(self):
        self.butler.speak(_("first_run_intro"))
        # Na de intro: leg klik-gedrag uit (gebeurt eenmalig)
        from PySide6.QtCore import QTimer
        QTimer.singleShot(7000, self._explain_click_behavior)

    def _explain_click_behavior(self):
        """Eenmalige uitleg over hoe je de butler bedient."""
        msg = (
            "Even kort over hoe u mij bedient: "
            "dubbelklik op mij om een vraag te stellen. "
            "Eén keer klikken maakt mij stil als ik aan het praten ben, "
            "of laat u mij verplaatsen door te slepen. "
            "Rechtsklik opent mijn menu."
        )
        self.butler.show_bubble(msg, duration_ms=8000)
        # Niet voorlezen — anders te veel tegelijk; alleen tonen

    def _do_morning_briefing(self):
        """Eerste opstart van de dag: groet + weer + herinneringen vandaag."""
        parts = [greeting(short=False)]

        # Weer voor huidige locatie (best-effort, niet blokkerend)
        try:
            w = get_weather(None)  # None = via IP
            if w and "error" not in w and w.get("temp") is not None:
                parts.append(
                    f"In {w['city']} is het nu {w['temp']} graden, {w['description']}."
                )
        except Exception as e:
            print(f"[briefing] weer faalde: {e}")

        # Herinneringen van vandaag
        try:
            todays = list_reminders_for_date(datetime.now().date())
            if todays:
                if len(todays) == 1:
                    parts.append(
                        f"U heeft één herinnering vandaag: {todays[0]['text']}."
                    )
                else:
                    parts.append(f"U heeft {len(todays)} herinneringen vandaag.")
                    for r in todays[:3]:
                        t = r.get("time", "")
                        parts.append(f"Om {t}: {r['text']}.")
        except Exception as e:
            print(f"[briefing] herinneringen faalden: {e}")

        # Mail wordt apart gemeld door mail_checker
        self.butler.speak(" ".join(parts))

    # ------------------------------------------------------------------
    # Show methods (lazy create)
    # ------------------------------------------------------------------
    def show_search(self):
        if self._search_win is None:
            self._search_win = SearchWindow()
            self._search_win.open_in_browser.connect(self._open_in_browser)
            self._search_win.set_butler_ref(self.butler)
        self._search_win.show()
        self._search_win.raise_()
        self._search_win.activateWindow()

    def _show_with_walk(self, win):
        """Toon een venster met walk-away/walk-back animatie van de butler."""
        if win is None:
            return
        # Butler weg, even wachten, dan venster tonen
        try:
            self.butler.walk_away()
        except Exception:
            pass
        QTimer.singleShot(450, lambda: (win.show(), win.raise_(), win.activateWindow()))

        # Connect hide event eenmalig zodat butler terugkomt
        if not getattr(win, "_walk_connected", False):
            win._walk_connected = True
            original_hide = win.hideEvent

            def patched_hide(event):
                try:
                    original_hide(event)
                except Exception:
                    pass
                # Even wachten zodat het venster echt weg is
                QTimer.singleShot(150, self.butler.walk_back)

            win.hideEvent = patched_hide

    def show_browser(self):
        is_first = self._browser_win is None
        if is_first:
            self.butler.show_bubble("🌐 Een moment, ik open de browser...", duration_ms=2500)
            try:
                self.butler.speak("Moment, ik open de browser.")
            except Exception:
                pass
        else:
            try:
                self.butler.speak("Browser geopend.")
            except Exception:
                pass
        QTimer.singleShot(700 if is_first else 200, self._do_show_browser)

    def _do_show_browser(self):
        if self._browser_win is None:
            self._browser_win = BrowserWindow()
        if self._browser_win.tabs.count() == 0:
            # Open de homepage van de GEKOZEN zoekmachine, niet altijd DuckDuckGo
            self._browser_win.open_url(get_engine_homepage())
        self._show_with_walk(self._browser_win)

    def _open_in_browser(self, url: str):
        if self._browser_win is None:
            self._browser_win = BrowserWindow()
        self._browser_win.open_url(url)

    def show_email(self):
        is_first = self._email_win is None
        if is_first:
            self.butler.show_bubble("✉️ Een moment, ik open uw mail...", duration_ms=2500)
            try:
                self.butler.speak("Moment, ik open uw mail. De berichten worden opgehaald.")
            except Exception:
                pass
        else:
            try:
                self.butler.speak("Mail-venster geopend, de berichten worden bijgewerkt.")
            except Exception:
                pass
        QTimer.singleShot(700 if is_first else 200, self._do_show_email)

    def _do_show_email(self):
        if self._email_win is None:
            self._email_win = EmailWindow()
        self._show_with_walk(self._email_win)

    def show_calendar(self):
        is_first = self._calendar_win is None
        if is_first:
            self.butler.show_bubble("📅 Een moment, ik open de agenda...", duration_ms=2500)
            try:
                self.butler.speak("Moment, ik open de agenda.")
            except Exception:
                pass
        else:
            try:
                self.butler.speak("Agenda geopend.")
            except Exception:
                pass
        QTimer.singleShot(700 if is_first else 200, self._do_show_calendar)

    def _do_show_calendar(self):
        if self._calendar_win is None:
            self._calendar_win = CalendarWindow()
        self._show_with_walk(self._calendar_win)

    def show_todo(self):
        is_first = self._todo_win is None
        if is_first:
            self._todo_win = TodoWindow()
            self.butler.show_bubble("📋 Een moment, ik open uw te-doen lijst...", duration_ms=2500)
        try:
            self.butler.speak("Een moment, ik open uw te-doen lijst.")
        except Exception:
            pass
        # Geef de butler tijd om bubble + spraak te starten voor venster opent
        QTimer.singleShot(700 if is_first else 200, self._do_show_todo)

    def _do_show_todo(self):
        if self._todo_win is None:
            self._todo_win = TodoWindow()
        self._todo_win.refresh()
        self._todo_win.show()
        self._todo_win.raise_()
        self._todo_win.activateWindow()

    def show_quickguide(self):
        is_first = self._guide_win is None
        if is_first:
            self._guide_win = QuickGuideWindow()
            self.butler.show_bubble("📖 Een moment, ik open de snelgids...", duration_ms=2500)
        try:
            self.butler.speak("Een moment, ik open de snelgids.")
        except Exception:
            pass
        QTimer.singleShot(700 if is_first else 200, self._do_show_quickguide)

    def _do_show_quickguide(self):
        if self._guide_win is None:
            self._guide_win = QuickGuideWindow()
        self._guide_win.show()
        self._guide_win.raise_()
        self._guide_win.activateWindow()

    def show_settings(self):
        """Open het Instellingen-venster met meteen visuele/auditieve feedback."""
        # Stap 1: meteen reageren (gebruiker zit niet te wachten zonder feedback)
        is_first_open = self._settings_win is None
        if is_first_open:
            # Eerste keer: opbouw kan 1-2 sec duren. Geef ballon + spraak.
            self.butler.show_bubble(
                "⚙️ Een moment, ik open de instellingen...",
                duration_ms=3000
            )
            try:
                self.butler.speak("Moment, ik open de instellingen voor u.")
            except Exception:
                pass
        else:
            # Heropenen: korte ballon + spraak zodat butler altijd reageert
            self.butler.show_bubble(
                "⚙️ Instellingen geopend.",
                duration_ms=2000
            )
            try:
                self.butler.speak("Instellingen geopend.")
            except Exception:
                pass

        # Stap 2: zwaarder werk via QTimer zodat UI eerst kan tekenen
        QTimer.singleShot(700 if is_first_open else 200, self._do_show_settings)

    def _do_show_settings(self):
        if self._settings_win is None:
            if self._browser_win is None:
                self._browser_win = BrowserWindow()
            self._settings_win = SettingsWindow(
                mail_checker=self.mail_checker,
                browser_window=self._browser_win,
            )
            # Verbind signalen voor live updates
            self._settings_win.character_changed.connect(self._on_character_changed)
            self._settings_win.engine_changed.connect(self._on_engine_changed)
            self._settings_win.ollama_changed.connect(self._on_ollama_changed)
            self._settings_win.request_ollama_stop.connect(self._on_request_ollama_stop)
        self._settings_win._populate_personal()
        self._settings_win._populate_voices()
        self._settings_win._populate_intervals()
        self._settings_win._populate_volumes()
        self._settings_win._populate_speeds()
        self._settings_win._populate_pitches()
        self._settings_win._populate_engines()
        self._settings_win._populate_characters()
        self._settings_win._populate_ollama()
        self._settings_win.show()
        self._settings_win.raise_()
        self._settings_win.activateWindow()

    def _on_character_changed(self):
        """Karakter is gewijzigd in Settings — herlaad de butler."""
        try:
            self.butler.reload_character()
            print("[main] butler herladen met nieuw karakter")
        except Exception as e:
            print(f"[main] karakter herladen faalde: {e}")

    def _on_engine_changed(self, engine_key: str):
        """Zoekmachine-keuze gewijzigd. Config wordt direct gelezen door
        web.py en browser_window.py — geen extra werk nodig."""
        print(f"[main] zoekmachine gewijzigd naar: {engine_key}")

    def _on_ollama_changed(self, enabled: bool):
        """
        Gebruiker heeft de toggle aan/uit gezet. We DOEN niks automatisch
        — de gebruiker kan zelf de Start/Stop knoppen gebruiken.
        Deze toggle bepaalt alleen of de zoek-pipeline Ollama mag gebruiken.
        """
        if enabled:
            # Korte detectie zodat gebruiker meteen weet of het werkt
            if ollama_is_available(timeout=2.0):
                self.butler.show_bubble(
                    "✓ AI ingeschakeld — Ollama draait. Klaar voor gebruik.",
                    duration_ms=3000,
                )
            else:
                self.butler.show_bubble(
                    "⚠️ AI ingeschakeld maar Ollama draait nog niet. "
                    "Klik 'Start Ollama' in Settings om te starten.",
                    duration_ms=4000,
                )
        else:
            self.butler.show_bubble("AI uitgeschakeld.", duration_ms=2000)

    def _on_request_ollama_stop(self):
        """Gebruiker klikte 'Stop Ollama' knop in Settings."""
        # Spraak-feedback dat het bezig is (kan een paar seconden duren)
        msg = "Een moment, ik stop Ollama. Dit kan even duren."
        try:
            self.butler.show_bubble("🛑 " + msg, duration_ms=3000)
            self.butler.speak(msg)
        except Exception:
            pass

        # Doe de eigenlijke stop in een achtergrond-thread
        from PySide6.QtCore import QThread, Signal as _Signal, QObject

        class _StopThread(QThread):
            done = _Signal(bool, str)
            def run(self):
                try:
                    ok, m = ollama_force_shutdown()
                    self.done.emit(ok, m)
                except Exception as e:
                    self.done.emit(False, str(e))

        self._ollama_stop_thread = _StopThread()
        self._ollama_stop_thread.done.connect(self._on_ollama_stop_done)
        self._ollama_stop_thread.start()

    def _on_ollama_stop_done(self, ok: bool, msg: str):
        """Callback nadat Stop-thread klaar is."""
        try:
            icon = '✓' if ok else '⚠️'
            self.butler.show_bubble(f"{icon} {msg}", duration_ms=4000)
            self.butler.speak(msg if ok else "Het is niet gelukt Ollama te stoppen.")
        except Exception:
            pass
        # Refresh status in Settings als die open is
        try:
            if self._settings_win is not None:
                self._settings_win._populate_ollama()
        except Exception:
            pass

    def show_about(self):
        try:
            self.butler.speak("Een moment, ik open het info-venster.")
        except Exception:
            pass
        dlg = AboutDialog(parent=None)
        dlg.open_in_browser.connect(self._open_in_browser)
        dlg.exec()

    def show_donation(self):
        try:
            self.butler.speak("Een moment, ik open het donatie-venster.")
        except Exception:
            pass
        dlg = DonationDialog(parent=None)
        dlg.open_in_browser.connect(self._open_in_browser)
        result = dlg.exec()
        # Als gebruiker annuleerde: bevestig dat
        if result == 0:  # QDialog.Rejected
            try:
                self.butler.speak("Oké, geen probleem.")
            except Exception:
                pass

    def show_contact(self):
        try:
            self.butler.speak("Een moment, ik open het contact-formulier.")
        except Exception:
            pass
        dlg = ContactDialog(parent=None)
        result = dlg.exec()
        if result == 0:  # afgesloten zonder verzenden
            try:
                self.butler.speak("Oké, contact-formulier gesloten.")
            except Exception:
                pass

    def _check_for_update(self):
        """Asynchrone update-check bij opstart."""
        try:
            self._update_worker = check_update_on_startup_async(
                self.butler, on_open_url=self._open_in_browser
            )
        except Exception as e:
            print(f"[main] update check faalde: {e}")

    # ------------------------------------------------------------------
    # Voice input ("Hé Alfred...")
    # ------------------------------------------------------------------
    def start_voice_input(self):
        """Start de microfoon-luisteraar (alleen als enabled en lib aanwezig)."""
        if not config.get("voice_input_enabled", False):
            return
        if not is_voice_input_available():
            print("[main] spraakherkenning niet beschikbaar (lib ontbreekt)")
            return
        if self._voice_input is not None:
            return  # Al actief

        def on_wake():
            # Visuele feedback: korte ballon + lichte knik
            try:
                from PySide6.QtCore import QTimer
                QTimer.singleShot(0, lambda: self.butler.show_bubble(
                    "🎤 Ik luister...", duration_ms=4000
                ))
            except Exception:
                pass

        def on_command(text: str):
            # Verwerk het commando alsof het in het zoekvenster was getypt
            from PySide6.QtCore import QTimer
            QTimer.singleShot(0, lambda: self._handle_voice_command(text))

        self._voice_input = VoiceInput(on_wake=on_wake, on_command=on_command)
        self._voice_input.start()

    def stop_voice_input(self):
        if self._voice_input is not None:
            self._voice_input.stop()
            self._voice_input = None

    def _handle_voice_command(self, command: str):
        """Voer een gesproken commando uit als zoek-actie."""
        if not command or not command.strip():
            return
        # Open zoekvenster en zet de query erin (gebruikt bestaande routing)
        if self._search_win is None:
            self._search_win = SearchWindow()
            self._search_win.open_in_browser.connect(self._open_in_browser)
            self._search_win.set_butler_ref(self.butler)
        self._search_win.show()
        self._search_win.raise_()
        # Vul de query in en trigger
        try:
            self._search_win.input.setPlainText(command)
            self._search_win._on_ask()
        except Exception as e:
            print(f"[main] voice command exec faalde: {e}")

    # ------------------------------------------------------------------
    def quit(self):
        """Sluit de app netjes af met afscheid en cleanup."""

        # Stop eerst andere lopende spraak zodat het afscheid prioriteit krijgt
        # (maar respecteer de wens van de gebruiker: wacht ook tot bestaande spraak echt klaar
        # is voordat we de afscheidsgroet starten)
        msg = farewell()
        try:
            # Toon ballon (visueel feedback, ook als geen geluid)
            if hasattr(self.butler, "show_bubble"):
                self.butler.show_bubble(msg, duration_ms=4000)
            # Wacht heel kort tot eventueel lopende spraak natuurlijk afrondt;
            # dan start de afscheidsgroet daarbovenop
            self.butler.speak(msg)
        except Exception as e:
            print(f"[quit] afscheid faalde: {e}")

        # Wacht tot de spraak ECHT klaar is voordat we afsluiten.
        # Pollen elke 200ms tot voice.is_speaking() False is.
        self._quit_started_at = time.time()
        self._wait_for_speech_then_quit()

    def _wait_for_speech_then_quit(self):
        """Polling-loop: wacht tot spraak klaar is, dan _do_quit aanroepen."""
        # Veiligheidsklep: maximaal 8 seconden wachten (zinnen zijn nooit langer)
        elapsed = time.time() - self._quit_started_at
        if elapsed > 8.0:
            print(f"[quit] timeout na {elapsed:.1f}s, sluit nu af")
            self._do_quit()
            return

        try:
            still_speaking = self.voice.is_speaking() if hasattr(self.voice, "is_speaking") else False
        except Exception:
            still_speaking = False

        if still_speaking:
            # Nog bezig met praten, wacht 200ms en check opnieuw
            QTimer.singleShot(200, self._wait_for_speech_then_quit)
        else:
            # Klaar — kleine pauze voor natuurlijk gevoel, dan afsluiten
            QTimer.singleShot(300, self._do_quit)

    def _do_quit(self):
        try:
            self.stop_voice_input()
            self.hotkeys.stop()
            self.scheduler.stop()
            self.mail_checker.stop()
            self.voice.stop()
            # Sluit het mail-venster netjes (stopt eventuele IMAP-thread)
            if self._email_win is not None:
                try:
                    self._email_win.close()
                except Exception as e:
                    print(f"[quit] email close faalde: {e}")
            # Ollama netjes stoppen als wij hem startten
            try:
                ollama_shutdown_if_we_started()
            except Exception as e:
                print(f"[quit] ollama shutdown faalde: {e}")
        except Exception:
            pass
        # Sluit de log netjes af voor we de Qt event loop verlaten
        try:
            close_logging()
        except Exception:
            pass
        self.app.quit()


# ----------------------------------------------------------------------
def main():
    # Qt6 doet hoge-DPI automatisch — geen attrs meer nodig.
    qapp = QApplication(sys.argv)

    # Vang Ctrl-C in console-mode
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Check of QSystemTrayIcon beschikbaar is
    from PySide6.QtWidgets import QSystemTrayIcon
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(
            None, "DeskButler",
            "Het systeemvak is niet beschikbaar op dit systeem.\n"
            "DeskButler heeft het systeemvak nodig om te werken."
        )
        sys.exit(1)

    butler_app = DeskButlerApp(qapp)
    sys.exit(qapp.exec())


if __name__ == "__main__":
    main()

