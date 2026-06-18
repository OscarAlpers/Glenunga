class Scene:
    def handle_event(self, event):
        pass
    def update(self):
        pass
    def draw(self, screen):
        pass

class SceneManager:
    def __init__(self, start_scene):
        self.current = start_scene
    def handle_event(self, event):
        self.current.handle_event(event)
    def update(self):
        self.current.update()
    def goto_scene(self, new_scene):
        self.current = new_scene
    def draw(self, screen):
        self.current.draw(screen)