class Video:
    def __init__(self, title, current_views):
        self.title = title
        self.current_views = current_views
        self.prev_views = 0     # view count at last api call
        self.views_added = 0    # views added since last api call
        self.today_views = 0    # views today
        self.views_at_wake = 0  # views at wake

    # def count_new_views(self):
    #     self.views_added = self.current_views - self.prev_views
    #     self.today_views = self.current_views - self.views_at_wake
    
    def update_views(self):
        self.prev_views = self.current_views

    