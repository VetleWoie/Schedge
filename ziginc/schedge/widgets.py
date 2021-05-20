from django import forms
from datetime import timedelta


class SplitDurationWidget(forms.MultiWidget):
    """
    A Widget that splits duration input into four number input boxes.
    """

    def __init__(self, attrs={"min": 0, "class": "duration-form"}):
        widgets = (
          
            forms.NumberInput(attrs=attrs),
            forms.NumberInput(attrs=attrs),
        )
        super().__init__(widgets, attrs)

    def render(self, name, value, attrs=None, renderer=None):
        """Render the widget as a table"""
        if not value:
            value = [False] * len(self.widgets)
        rendered_widgets = [
            x.render(name, value[i]) for i, x in enumerate(self.widgets)
        ]

        labels = ["Hours", "Minutes"]
        labeled = []
        for label, widget in zip(labels, rendered_widgets):
            labeled.append(f"<tr><td>{label}</td><td>{widget}</td></tr>")
        return '<table id="id_duration">' + "".join(labeled) + "</table>"

    def value_from_datadict(self,data,files,name):
        duration = dict(data).get(name)
        if duration:
            try:
                h, m = [int(s) if s else 0 for s in duration]
            except ValueError:
                return None
            minutes = m % 60
            hours = (h + m // 60) % 24
            return [h, m]
        return [1, 0]

    def decompress(self, value):
        """Decompresses timedelta and splits into seperate values
        
        Parameters
        ----------
        value : dt.timedelta
            Hours and minutes.
        """
        if value:
            d = value
            if d:
                hours = d.minutes // 60
                minutes = (d.minutes % 60)
                return [int(hours), int(minutes)]
        return [1, 0]


class MultiValueDurationField(forms.MultiValueField):

    widget = SplitDurationWidget

    def __init__(self, *args, **kwargs):
        fields = (
            forms.IntegerField(),
            forms.IntegerField(),
        )
        super().__init__(fields=fields, require_all_fields=True, *args, **kwargs)

    def compress(self, data_list):
        """Compresses the time date in to a timedelta"""
        if len(data_list) == 2:
            return timedelta(
                hours=int(data_list[0]),
                minutes=int(data_list[1]),
            )
        else:
            return timedelta(0)