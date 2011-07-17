from flask import Flask
from opentext.text import text
from opentext import default_settings

app = Flask(__name__)
app.config.from_object(default_settings)
app.config.from_envvar('OPENTEXT_CONF', silent=True)
app.register_module(text, url_prefix='/text')

