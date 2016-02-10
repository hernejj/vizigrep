#!/usr/bin/python

import time
from gi.repository import Gtk, Gdk, GObject

# This class provides a clean and easy to use interface for displaying simple
# message boxes to the user and getting a button-clicked type response. It can be
# used in the main thread (gtk main) or in a 2ndary thread. All message boxes are
# modal which means the rest of the GUI is unresponsive while a message box is being
# displayed. Also, code execution blocks which waiting for the user's response to 
# the message box.
#
# THREADING NOTE: While each mbox function can work in a threaded environment, this
# class itself has 1 response variable, therefore, you should not be calling these
# functions simultaneously from multiple threads. One message box at a time!
#
# The recommended method of use is as follows:
#
# Create a mbox object and store it in your gui's main class, or in any class in
# which you intend to use message boxes.  When you wish to show a message box just
# call one of the mbox functions. Example
#
# response = mbox.error("Cereal port not found. Breakfast halted.")
#
# NOTE: The above call is meant to be used in the main thread (gtk.main()). If you
# call this function as shown in a 2ndary thread (any thread other than gtk.main())
# your program will deadlock. If you need to create a message box in a 2ndary thread
# then you'l need to ensure that you set the threaded property to True. Example:
#
# response = mbox.error("Cereal port not found. Breakfast halted.", threaded=True)
#
# All mbox functions return a response. The following are valid responses:
#
#   Gtk.ResponseType.CLOSE  - The "little X" was clicked and the window closed :)
#   Gtk.ResponseType.OK     - "OK" button clicked
#   Gtk.ResponseType.YES    - "YES" button clicked
#   Gtk.ResponseType.NO     - "NO" button clicked
#
#
class mbox: 
    # Indicates the user's response to the message box (which button was clicked).
    response = None
    log = None

    # Creates an "error" dialog with a window title "Error" and a single close
    # button. The given message is displayed to the user.
    def error(self, message_text, threaded=False):
       if self.log: self.log.error(message_text)
       return self.mbox(Gtk.MessageType.QUESTION, message_text, "Error", Gtk.ButtonsType.CLOSE, threaded)


    # Creates a dialog to ask the user a yes/no question. Yes and No buttons are
    # presented to the user.
    def question(self, message_text, threaded=False):
        return self.mbox(Gtk.MessageType.QUESTION, message_text, "", Gtk.ButtonsType.YES_NO, threaded)

    ############################################################################
    #################################### Internal ##############################
    ############################################################################

    # Create a new message box with the given parameters. msg_type allows you to
    # change the icon displayed in the dialog. Valid values are as follows:
    #
    #   Gtk.MessageType.ERROR
    #   Gtk.MessageType.QUESTION
    #   Gtk.MessageType.WARNING
    #   Gtk.MessageType.INFO
    #
    # Valid choices for buttons are:
    #
    #   Gtk.ButtonsType.CLOSE
    #   Gtk.ButtonsType.NONE
    #   Gtk.ButtonsType.OK
    #   Gtk.ButtonsType.CLOSE
    #   Gtk.ButtonsType.CANCEL
    #   Gtk.ButtonsType.YES_NO
    #   Gtk.ButtonsType.OK_CANCEL
    #
    def mbox(self, msg_type, message_text, window_title, buttons, threaded):
        if(threaded): return self.mbox_t(msg_type, message_text, window_title, buttons)
        else:         return self.mbox_nt(msg_type, message_text, window_title, buttons)

    ############################################################################
    # Non-threaded message box interface                                       #
    # Use in the gtk.main() thread                                             #
    ############################################################################
    def mbox_nt(self, msg_type, message_text, window_title, buttons):
    
        # Create message dailog
        mbox = Gtk.MessageDialog(type=msg_type, buttons=buttons, message_format=message_text)
        mbox.set_title("Error")
        mbox.set_modal(True)

        # Ensure message dialog is centered on screen
        mbox.set_position(Gtk.WindowPosition.CENTER)
        
        # Set window title, if it exists
        if (window_title != None): mbox.set_title(window_title)

        # Display  message box and collect response
        response = mbox.run()
        
        # Clean up and return user's response to caller
        mbox.destroy()
        return response

    ############################################################################
    # Threaded message box interface                                           #
    # Use in a thread other than your gtk.main() thread.                       #
    ############################################################################
    def mbox_t(self, msg_type, message_text, window_title, buttons):

        # Create message dialog
        mbox = Gtk.MessageDialog(type=msg_type, buttons=buttons, flags=Gtk.DialogFlags.MODAL, message_format=message_text)

        # Ensure message dialog is centered on screen
        mbox.set_position(Gtk.WindowPosition.CENTER)

        # Set window title, if it exists
        if (window_title != None): mbox.set_title(window_title)

        # Clear any previous response
        self.response = None

        # Show mbox
        #response = mbox.run()  # DO NOT USE! Causes hang if run in a thread!!
        mbox.connect('response', self.mbox_t_response)
        GObject.idle_add(mbox.show)

        # Await response, then return it  FIXME: Can I do this??
        while (self.response == None): time.sleep(0.1)  
        return self.response

    # The user clicked a button on the mbox. We'll save the response that indicates
    # which button the user clicked and destroy the mbox.
    def mbox_t_response(self, mbox, response_id):
        self.response = response_id  #fixme: need lock!
        mbox.destroy()
        return False

    # Creates an "error" dialog that terminates the gtk main loop when it is
    # closed.
    #
    # Note: This method is only intended for printing out exceptions that occur
    #       during initialization.
    def terminate(self, message_text, threaded=False):
        response = self.error(message_text, threaded)
        Gtk.main_quit()
        return response

