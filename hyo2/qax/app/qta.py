import logging
import os

import qtawesome as qta
from PySide2 import QtGui, QtCore, QtWidgets

logger = logging.getLogger(__name__)

raster_icon_warning = False


def icon(*names, **kwargs):
    try:
        qta.icon(*names, **kwargs)

    except qta.iconic_font.FontError:
        global raster_icon_warning
        if not raster_icon_warning:
            logger.info("Using raster icons")
            raster_icon_warning = True
        # patch to solve https://docs.microsoft.com/en-US/troubleshoot/windows-client/shell-experience/feature-to-block-untrusted-fonts
        media_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "media"))
        icon_path = os.path.join(media_folder, "%s.png" % names[0])
        if not os.path.exists(icon_path):
            raise RuntimeError('Unable to locate icon at %s' % icon_path)
        return QtGui.QIcon(icon_path)


class IconWidget(QtWidgets.QLabel):
    """
    IconWidget gives the ability to display an icon as a widget

    if supports the same arguments as icon()
    for example
    music_icon = qta.IconWidget('fa5s.music',
                                color='blue',
                                color_active='orange')

    it also have setIcon() and setIconSize() functions
    """

    def __init__(self, *names, **kwargs):
        super().__init__(parent=kwargs.get('parent'))
        self._icon = None
        self._size = QtCore.QSize(16, 16)
        self.setIcon(icon(*names, **kwargs))

    def setIcon(self, _icon):
        """
        set a new icon()

        Parameters
        ----------
        _icon: qtawesome.icon
            icon to set
        """
        self._icon = _icon
        self.setPixmap(_icon.pixmap(self._size))

    def setIconSize(self, size):
        """
        set icon size

        Parameters
        ----------
        size: QtCore.QSize
            size of the icon
        """
        self._size = size

    def update(self, *args, **kwargs):
        if self._icon:
            self.setPixmap(self._icon.pixmap(self._size))
        return super().update(*args, **kwargs)
