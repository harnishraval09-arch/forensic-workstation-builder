"""
Small shared visual-effects helpers. Qt stylesheets (QSS) don't
support CSS box-shadow, so elevation on cards has to be added
programmatically via QGraphicsDropShadowEffect instead.
"""

from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtGui import QColor


def apply_card_shadow(widget, blur=28, y_offset=8, alpha=70):
    """Attach a soft drop shadow to a card-like widget (QFrame etc.)."""
    effect = QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(blur)
    effect.setXOffset(0)
    effect.setYOffset(y_offset)
    color = QColor("#0b1c33")
    color.setAlpha(alpha)
    effect.setColor(color)
    widget.setGraphicsEffect(effect)
    return effect