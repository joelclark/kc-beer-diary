#!/usr/bin/env python
from handlers import *

admin = webapp2.WSGIApplication([

    webapp2.Route(r'/recipes/new', handler=NewRecipeHandler, name="new-recipe"),
    webapp2.Route(r'/recipes/edit/<slug>', handler=EditRecipeHandler, name="edit-recipe"),

], debug=True)

app = webapp2.WSGIApplication([

    webapp2.Route(r'/', handler=HomepageHandler, name="home"),
    webapp2.Route(r'/login', handler=LoginHandler, name="login"),
    webapp2.Route(r'/logout', handler=LogoutHandler, name="logout"),
    webapp2.Route(r'/recipe/<slug>', handler=ShowRecipeHandler, name="show-recipe"),

], debug=True)
