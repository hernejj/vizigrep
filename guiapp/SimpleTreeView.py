class SimpleTreeView:

    def __init__(self, gtkTreeView):
        self.tv = gtkTreeView
        self.enableOnSelectList = []
        self.disableOnSelectList = []
        self.selected_col_id = 0
        self.last_selected_item = None
        self.last_selected_path = None
        self.last_topmost_path = None
        self.last_topmost_y = None
        self.tv.connect("cursor-changed", self.selection_changed)
        
    def reload(self):
        raise Exception("This method must be subclassed!")
    
    def enableOnSelect(self, widgetList):
        self.enableOnSelectList += widgetList
        self.selection_changed(None)
    
    def disableOnSelect(self, widgetList):
        self.disableOnSelectList += widgetList
        self.selection_changed(None)
    
    def get_selected(self):
        model, itr = self.tv.get_selection().get_selected()
        if (itr == None): return None
        return model.get_value(itr, self.selected_col_id)
    
    def get_selected_path(self):
        model, itr = self.tv.get_selection().get_selected()
        if (itr == None): return None
        return model.get_path(itr)
    
    def get_topmost_path(self):
        r = self.tv.get_visible_range()
        if not r:
            return None
        return r[0]
    
    def set_topmost_path(self, path):
        if path:
            self.tv.scroll_to_cell(path)
    
    def get_topmost_y(self):
            self.app.log.debug('Remember TopMostY as {0}'.format(self.tv.get_visible_rect().y))
            return self.tv.get_visible_rect().y

    def set_topmost_y(self, y):
        if y:
            self.app.log.debug('Set TopMostY to {0}'.format(y))
            self.tv.scroll_to_point(-1, y)
    
    def select_something(self):
        # Try to select an exact match
        if self.last_selected_item and self.select_item(self.last_selected_item):
            self.set_topmost_y(self.last_topmost_y)
            return
        
        # Failing that, try to select the same position/index
        if self.last_selected_path:
            self.tv.set_cursor(self.last_selected_path)
        if self.get_selected_path() == self.last_selected_path: # Did it work?
            self.set_topmost_y(self.last_topmost_y)
            return
        
        # If all else fails try to select the first item
        if (len(self.tv.get_model()) > 0):
            self.tv.set_cursor(0)
            self.set_topmost_y(self.last_topmost_y)
        
    def select_topmost(self):
        if (len(self.tv.get_model()) > 0):
            self.tv.set_cursor(0)
    
    def search_for_item(self, model, itr, item):
        while itr:
            if model.iter_has_child(itr):
                r = self.search_for_item(model, model.iter_children(itr), item)
                if r:
                    return r
        
            if model.get_value(itr, self.selected_col_id) == item:
                return itr
            itr = model.iter_next(itr)
        return None
    
    # Selects the given item in the list. Returns true if the requested item was able to be selected. False otherwise.
    def select_item(self, item):
        model = self.tv.get_model()
        itr = model.get_iter_first()
        if (itr == None): return False
        
        itemItr = self.search_for_item(model, itr, item)
        if itemItr:
            self.select_path(model.get_path(itemItr))
            return True
        return False
    
    def select_path(self, path):
        self.tv.set_cursor(path)
        #tvsel = self.tv.get_selection()
        #tvsel.select_path(path)
        
    def remember_selection(self):
        self.last_selected_item = self.get_selected()
        self.last_selected_path = self.get_selected_path()
        self.last_topmost_y = self.get_topmost_y()
    
    def selection_changed(self, tv):
        if self.get_selected():
            enableList = self.enableOnSelectList
            disableList = self.disableOnSelectList
        else:
            enableList = self.disableOnSelectList
            disableList = self.enableOnSelectList
        
        for widget in enableList:
            widget.set_sensitive(True)
        for widget in disableList:
            widget.set_sensitive(False)
