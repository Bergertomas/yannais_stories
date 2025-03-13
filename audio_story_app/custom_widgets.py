from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import NumericProperty, ListProperty, BooleanProperty, StringProperty
import theme


class StylishButton(Button):
    corner_radius = NumericProperty(15)
    bg_color = ListProperty([0.3, 0.5, 0.9, 1])
    shadow_color = ListProperty([0, 0, 0, 0.3])
    shadow_offset = NumericProperty(2)

    def __init__(self, **kwargs):
        # Extract custom properties with defaults
        self.corner_radius = kwargs.pop('corner_radius', dp(15))
        self.bg_color = kwargs.pop('bg_color', theme.PRIMARY_COLOR)
        self.shadow_color = kwargs.pop('shadow_color', [0, 0, 0, 0.3])
        self.shadow_offset = kwargs.pop('shadow_offset', dp(2))

        # Initialize button
        super(StylishButton, self).__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)  # Transparent
        self.font_size = dp(16)

        # Bind to size and pos changes
        self.bind(size=self._update_canvas, pos=self._update_canvas)
        self._update_canvas()

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # Draw shadow first (slightly larger, slightly offset rectangle)
            Color(*self.shadow_color)
            RoundedRectangle(
                pos=[self.pos[0] + self.shadow_offset, self.pos[1] - self.shadow_offset],
                size=self.size,
                radius=[self.corner_radius]
            )

            # Draw main button background
            Color(*self.bg_color)
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self.corner_radius]
            )


class StoryButton(StylishButton):
    """Button specifically styled for story items"""

    def __init__(self, **kwargs):
        kwargs['corner_radius'] = dp(20)
        self.story_title = kwargs.pop('story_title', 'Untitled')
        super(StoryButton, self).__init__(**kwargs)
        self.text = self.story_title
        self.font_size = dp(18)


class NavigationButton(StylishButton):
    """Button specifically styled for navigation items"""
    icon = StringProperty('')

    def __init__(self, **kwargs):
        self.icon = kwargs.pop('icon', '')
        super(NavigationButton, self).__init__(**kwargs)
        self.corner_radius = dp(15)

        # Add icon representation here if needed
        # For now, just using text


class StylishLabel(Label):
    shadow_enabled = BooleanProperty(True)

    def __init__(self, **kwargs):
        self.shadow_enabled = kwargs.pop('shadow_enabled', True)
        self.is_title = kwargs.pop('is_title', False)
        super(StylishLabel, self).__init__(**kwargs)

        # Set default properties
        self.color = (1, 1, 1, 1)
        self.halign = 'center'
        self.valign = 'middle'
        self.font_size = dp(22) if self.is_title else dp(16)

        if self.shadow_enabled:
            self.bind(size=self._update_canvas, pos=self._update_canvas)
            self._update_canvas()

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        if self.shadow_enabled:
            with self.canvas.before:
                # Simple text shadow effect
                Color(0, 0, 0, 0.5)
                RoundedRectangle(
                    pos=[self.pos[0] + dp(1), self.pos[1] - dp(1)],
                    size=self.size,
                    radius=[5]
                )


class TitleLabel(StylishLabel):
    """Label specifically styled for titles"""

    def __init__(self, **kwargs):
        kwargs['is_title'] = True
        super(TitleLabel, self).__init__(**kwargs)
        self.font_size = dp(28)
        self.bold = True
        self.color = theme.GOLD_LIGHT


class SubtitleLabel(StylishLabel):
    """Label specifically styled for subtitles"""

    def __init__(self, **kwargs):
        super(SubtitleLabel, self).__init__(**kwargs)
        self.font_size = dp(16)
        self.color = theme.SECONDARY_TEXT_COLOR
