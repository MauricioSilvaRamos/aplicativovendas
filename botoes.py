from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import ButtonBehavior


class LabelButton(ButtonBehavior, Label):
    pass

class ImageButton(ButtonBehavior, Image):
    pass