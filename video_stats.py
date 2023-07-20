class Video:
    def __init__(self, title, current_views):
        self.title = title
        self.current_views = current_views
        self.prev_views = 0
        self.views_added = 0

    def count_new_views(self):
        self.views_added = self.current_views - self.prev_views
    
    def update_views(self):
        self.prev_views = self.current_views

    