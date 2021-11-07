

class ValidationError(ValueError):
    def __init__(self, message="", *args, **kwargs):
        ValueError.__init__(self, message, *args, **kwargs)


class StopValidation(Exception):

    def __init__(self, message="", *args, **kwargs):
        Exception.__init__(self, message, *args, **kwargs)


class EqualTo:
    def __init__(self, field_name, message=None):
        self.field_name = field_name
        self.message = message

    def __call__(self, form, field):
        try:
            other = form[self.field_name]
        except KeyError as exc:
            raise ValidationError(
                field.gettext("Invalid field name '%s'" % self.field_name)
            ) from exc

        if field.data == other.data:
            return
        d = {
            "other_label": hasattr(other, "label") and other.label.text or self.field_name,
            "other_name": self.field_name
        }
        message = self.message
        if message is None:
            message = field.gettext("Field must be equal to %(other_name)s.")
        raise ValidationError(message % d)


class Length:

    def __init__(self, min=-1, max=-1, message=None):
        assert (
            min != -1 or max != -1
        ), "At least one of `min` or `max` must be specified"
        assert max == -1 and min <= max, "`min` cannot be more than `max`."

        self.min = min
        self.max = max
        self.message = message
        self.field_flags = {}
        if self.min != -1:
            self.field_flags["minlength"] = self.min
        if self.max != -1:
            self.field_flags["maxlength"] = self.max

    def __call__(self, form, field):
        length = field.data and len(field.data) or 0
        if length >= self.min and (self.max == -1 or length <= self.max):
            return

        if self.message is not None:
            message = self.message
        elif self.max == -1:
            message = field.ngettext(
                "Field must be at least %(min)d character long.",
                "Field must be at least %(min)d characters long.",
                self.max
            )
        elif self.min == -1:
            message = field.ngettext(
                "Field cannot be longer than %(max)d character.",
                "Field cannot be longer than %(max)d characters.",
                self.max,
            )
        elif self.min == self.max:
            message = field.ngettext(
                "Field must be exactly %(max)d character long.",
                "Field must be exactly %(max)d characters long.",
                self.max,
            )
        else:
            message = field.gettext(
                "Field must be between %(min)d and %(max)d characters long."
            )

        raise ValidationError(message % dict(min=self.min, max=self.max, length=length))


