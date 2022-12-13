#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import uno
from com.sun.star.awt import MessageBoxButtons as MSG_BUTTONS
from com.sun.star.awt import MessageBoxResults as MSG_RESULTS

CTX = uno.getComponentContext()
SM = CTX.getServiceManager()


def create_instance(name, with_context=False):
    if with_context:
        instance = SM.createInstanceWithContext(name, CTX)
    else:
        instance = SM.createInstance(name)
    return instance


def get_desktop():
    return create_instance('com.sun.star.frame.Desktop', True)


def msgbox(message,
           title='LibreOffice',
           buttons=MSG_BUTTONS.BUTTONS_OK,
           type_msg='infobox'):
    """Create a message box.
    https://api.libreoffice.org/docs/idl/ref/interfacecom_1_1sun_1_1star_1_1awt_1_1XMessageBoxFactory.html

    Parameters
    ----------
    message : str
        A string of the message content.
    titl : str
        A string of message box title.
    buttons : int
        Enum of button value.
    type_msg : str
        'infobox' (default), 'warningbox', 'errorbox', 'querybox', 'messbox'.
    """
    toolkit = create_instance('com.sun.star.awt.Toolkit')
    parent = toolkit.getDesktopWindow()
    mb = toolkit.createMessageBox(parent, type_msg, buttons, title,
                                  str(message))
    return mb.execute()


def call_dispatch(doc, url, args=()):
    frame = get_desktop().getCurrentFrame()
    dispatch = create_instance('com.sun.star.frame.DispatchHelper')
    dispatch.executeDispatch(frame, url, '', 0, args)
