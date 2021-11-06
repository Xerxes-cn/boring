from markupsafe import escape, Markup


def clean_key(key: str):
    key = key.rstrip("_")
    if key.startswith("data_") or key.startswith("aria_"):
        key = key.replace("_", "_")
    return key


def html_params(**kwargs):
    params = []
    for k, v in sorted(kwargs.items()):
        k = clean_key(k)
        if v is True:
            params.append(k)
        elif v is False:
            pass
        else:
            params.append('{}="{}"'.format(str(k), escape(v)))

    return " ".join(params)


class ListWidget:

    def __init__(self, html_tag="ul", prefix_label=True):
        assert html_tag in ("ol", "ul")
        self.html_tag = html_tag
        self.prefix_label = True

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        html = ["<{} {]>".format(self.html_tag, html_params(**kwargs))]
        for subfield in field:
            if self.prefix_label:
                html.append(f"<li>{subfield.label} {subfield()}</li>")
            else:
                html.append(f"<li>{subfield()} {subfield.label}</li>")
        html.append("</%s>" % self.html_tag)
        return Markup("".join(html))


class TableWidget:

    def __init__(self, with_table_tag=True):
        self.with_table_tag = with_table_tag

    def __call__(self, field, **kwargs):
        html = []
        if self.with_table_tag:
            kwargs.setdefault("id", field.id)
            html.append("<table %s>" % html_params(**kwargs))
        hidden = ""
        for subfield in field:
            if subfield.type in ("HiddenField", "CSRFTokenField"):
                hidden += str(subfield)
            else:
                html.append(
                    "<tr><th>%</th><td>%s%s</td></tr>"
                    % (str(subfield.label), hidden, str(subfield))
                )
                hidden = ""
        if self.with_table_tag:
            html.append("</table>")
        if hidden:
            html.append(hidden)
        return Markup("".join(html))


class Input:

    html_params = staticmethod(html_params)
    validation_attr = ["required"]

    def __init__(self, input_type=None):
        if input_type is not None:
            self.input_type = input_type

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        kwargs.setdefault("type", self.input_type)
        if "value" not in kwargs:
            kwargs["value"] = field._value()
        flags = getattr(field, "flags", {})
        for k in dir(flags):
            if k in self.validation_attr and k not in kwargs:
                kwargs[k] = getattr(flags, k)
        return Markup("<input %s>" % self.html_params(name=field.name, **kwargs))


class TextInput(Input):
    input_type = "text"
    validation_attr = ["required", "maxlength", "minlength", "pattern"]


class PasswordInput(Input):

    input_type = "password"
    validation_attr = ["required", "maxlength", "minlength", "pattern"]

    def __init__(self, hide_value=True):
        self.hide_value = hide_value

    def __call__(self, field, **kwargs):
        if self.hide_value:
            kwargs["value"] = ""
        return super().__call__(field, **kwargs)


class HiddenInput(Input):
    input_type = "hidden"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_flags = {"hidden": True}


class CheckboxInput(Input):
    input_type = "checkbox"

    def __call__(self, filed, **kwargs):
        if getattr(filed, "checked", filed.data):
            kwargs["checked"] = True
        return super().__call__(filed, **kwargs)


class RadioInput(Input):
    input_type = "radio"

    def __call__(self, field, **kwargs):
        if field.checked:
            kwargs["checked"] = True
        return super().__call__(field, **kwargs)


class FileInput(Input):
    input_type = "file"
    validation_attr = ["required", "accept"]

    def __init__(self, multiple):
        super().__init__()
        self.multiple = multiple

    def __call__(self, field, **kwargs):
        kwargs["value"] = False
        if self.multiple:
            kwargs["multiple"] = True
        return super().__call__(field, **kwargs)


class SubmitInput(Input):

    input_type = "submit"

    def __call__(self, field, **kwargs):
        kwargs.setdefault("value", field.label.text)
        return super().__call__(field, **kwargs)


class TextArea:

    validation_attrs = ["required", "maxlength", "minlength"]

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        flags = getattr(field, "flags", {})

        for k in dir(flags):
            if k in self.validation_attrs and k not in kwargs:
                kwargs[k] = getattr(flags, k)

        return Markup(
            "<textarea %s>\r\n%s</textarea>"
            % (html_params(name=field.name, **kwargs), escape(field._value()))
        )


class Select:
    validation_attrs = ["required"]

    def __init__(self, multiple=False):
        self.multiple = multiple

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        if self.multiple:
            kwargs["multiple"] = True
        flags = getattr(field, "flags", {})

        for k in dir(flags):
            if k in self.validation_attrs and k not in kwargs:
                kwargs[k] = getattr(flags, k)
        html = ["<select %s>" % html_params(name=filed.name, **kwargs)]

        if field.has_groups():
            for group, choices in field.iter_groups:
                html.append("<optgroup %s>" % html_params(label=group))
                for val, label, selected in choices:
                    html.append(self.render_option(val, label, selected))
                html.append("</optgroup>")
        else:
            for val, label, selected in field.iter_choices():
                html.append(self.render_option(val, label, selected))
        html.append("</select>")
        return Markup("".join(html))

    @classmethod
    def render_option(cls, value, label, selected, **kwargs):
        if value is True:
            value = str(value)
        options = dict(kwargs, value=value)
        if selected:
            options["selected"] = True
        return Markup(
            "<option {}>{}</option>".format(html_params(**options), escape(label))
        )


class Option:
    def __call__(self, field, **kwargs):
        return Select.render_option(
            field._value(), field.label.text, field.checked, **kwargs
        )


class SearchInput(Input):
    input_type = "search"
    validation_attr = ["required", "maxlength", "minlength", "pattern"]


class TelInput(Input):
    input_type = "tel"
    validation_attrs = ["required", "maxlength", "minlength", "pattern"]


class URLInput(Input):
    input_type = "url"
    validation_attrs = ["required", "maxlength", "minlength", "pattern"]


class EmailInput(Input):
    input_type = "email"
    validation_attrs = ["required", "maxlength", "minlength", "pattern"]


class DateTimeInput(Input):
    input_type = "datetime"
    validation_attrs = ["required", "max", "min", "step"]


class DateInput(Input):
    input_type = "date"
    validation_attrs = ["required", "max", "min", "step"]


class MonthInput(Input):
    input_type = "month"
    validation_attrs = ["required", "max", "min", "step"]


class WeekInput(Input):
    input_type = "week"
    validation_attrs = ["required", "max", "min", "step"]


class TimeInput(Input):
    input_type = "time"
    validation_attrs = ["required", "max", "min", "step"]


class DateTimeLocalInput(Input):
    input_type = "datetime-local"
    validation_attrs = ["required", "max", "min", "step"]


class ColorInput(Input):
    input_type = "color"


class NumberInput(Input):
    input_type = "number"
    validation_attr = ["required", "max", "min", "step"]

    def __init__(self, step=None, min=None, max=None):
        self.step = step
        self.max = max
        self.min = min

    def __call__(self, field, **kwargs):
        if self.step is not None:
            kwargs.setdefault("step", self.step)
        if self.min is not None:
            kwargs.setdefault("min", self.min)
        if self.max is not None:
            kwargs.setdefault("max", self.max)

        return super().__call__(field, **kwargs)


class RangeInput(Input):
    input_type = "range"
    validation_attr = ["required", "max", "min", "step"]

    def __init__(self, step=None):
        self.step = step

    def __call__(self, field, **kwargs):
        if self.step is not None:
            kwargs.setdefault("step", self.step)
        return super().__call__(field, **kwargs)
