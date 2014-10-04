import datetime, parsedatetime, markdown

from google.appengine.ext import ndb

MODEL=ndb.Model
REQUIRED_MESSAGE = "A value is required for this field."

class Recipe(MODEL):
    brew_date = ndb.DateProperty(required=True)
    slug = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    content = ndb.TextProperty(required=True)
    rendered_content = ndb.TextProperty(required=True)

class RecipeViewModel(object):
    def __init__(self, brew_date=None, name=None, content=None):
        self._rendered_content = None
        self._name = None
        self._content = None
        self._brew_date = None
        self._cal = parsedatetime.Calendar()
        self._invalid_date = False

        self.brew_date_value = None
        self.brew_date = brew_date
        self.name = name
        self.content = content

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value   

    @property
    def brew_date(self):
        return self._brew_date

    @brew_date.setter
    def brew_date(self, value):
        self._brew_date = value
        try:
            self.brew_date_value = datetime.date(*self._cal.parseDate(value)[:3])
        except:
            self._invalid_date = True

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content = value
        if (value):
            self._rendered_content = markdown.markdown(value)  
        else:
            self._rendered_content = None

    @property
    def rendered_content(self):
        return self._rendered_content  

    def validate(self):
        errors = {}

        if self._invalid_date:
            errors['brew_date'] = "You entered an invalid date format."
        else:
            if not self.brew_date:
                errors['brew_date'] = REQUIRED_MESSAGE

        if not self.name:
            errors['name'] = REQUIRED_MESSAGE

        if not self.content:
            errors['content'] = REQUIRED_MESSAGE

        valid = not errors

        return (valid, errors)
    

