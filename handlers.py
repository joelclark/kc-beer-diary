import os
import urllib

from slugify import slugify
from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

from models import *

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")

class BaseRequestHandler(webapp2.RequestHandler):
    def dispatch(self):
        hostname = os.environ['HTTP_HOST']
        canonical = 'kentuckycreek.com'
        is_localhost = hostname.startswith('localhost')
        is_canonical = (hostname == canonical)

        if is_localhost or is_canonical:
            webapp2.RequestHandler.dispatch(self)
        else:
            path = self.request.path
            url = "http://%s%s" % (canonical, path)
            self.redirect(url, True)

BASE = BaseRequestHandler
JINJA = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def r(handler, template_name, args = {}):
    if not 'validation_errors' in args:
        args['validation_errors'] = {}

    args['current_user'] = users.get_current_user()
    args['is_admin'] = users.is_current_user_admin()

    template = JINJA.get_template(template_name)
    handler.response.write(template.render(args))

class HomepageHandler(BASE):
    def get(self):
        recipes = Recipe.query().order(-Recipe.brew_date).fetch(25)
        r(self, 'homepage.html', { 'recipes': recipes })

class LoginHandler(BASE):
    def get(self):
        user = users.get_current_user()
        if user:
            self.redirect('/logout')
        else:
            self.redirect(users.create_login_url('/'))

class LogoutHandler(BASE):
    def get(self):
        user = users.get_current_user()
        if user:
            self.redirect(users.create_logout_url('/'))
        else:
            self.redirect('/')

class RecipeEditor(BASE):
    def store_model(self, recipe, model):
        model.name = recipe.name
        model.brew_date = recipe.brew_date_value
        model.slug = slugify(recipe.name + " " + str(recipe.brew_date_value))
        model.content = recipe.content
        model.rendered_content = recipe.rendered_content
        model.put()
        self.redirect("/recipe/" + model.slug)

    def handle_post(self, model):
        validation_errors = {}
        recipe = RecipeViewModel(
            name=self.request.get('name'), 
            content=self.request.get('content'), 
            brew_date=self.request.get('brew_date'))

        valid, errors = recipe.validate()

        if valid:
            return self.store_model(recipe, model)         

        r(self, 'new-recipe.html', { 'validation_errors': errors, 'recipe': recipe })        

class NewRecipeHandler(RecipeEditor):
    def get(self):
        recipe = RecipeViewModel()
        r(self, 'new-recipe.html', { 'recipe': recipe })
    def post(self):
        self.handle_post(Recipe())

class EditRecipeHandler(RecipeEditor):
    def get(self, slug):
        model = Recipe.query(Recipe.slug == slug).get()
        recipe = RecipeViewModel(
            name=model.name, 
            content=model.content, 
            brew_date=model.brew_date.strftime('%m/%d/%Y')) # die die die
        r(self, 'new-recipe.html', { 'recipe': recipe })

    def post(self, slug):
        model = Recipe.query(Recipe.slug == slug).get()
        self.handle_post(model)        

class ShowRecipeHandler(BASE):
    def get(self, slug):
        recipe = Recipe.query(Recipe.slug == slug).get()
        r(self, 'show-recipe.html', { 'recipe': recipe })
