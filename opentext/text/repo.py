import os
from flask import current_app
from ConfigParser import ConfigParser
from mercurial import commands, ui, hg
from mercurial.hgweb import hgweb

class web_ui(ui.ui):

    def _data(self, untrusted):
        config = self._tcfg
        #config.add_section('ui')
        config.set('ui', 'debug', "False")
        config.set('ui', 'verbose', "False")
        config.set('ui', 'quiet', "True")
        config.set('ui', 'report_untrusted', "False")
        config.set('ui', 'traceback', "False")
        #config.add_section('trusted')
        #config.add_section('web')
        config.set('web', 'push_ssl', "False")
        config.set('web', 'allow_push', "*")
        return config
    
    def _is_trusted(self, fp, f):
        return True

    def plain(self, feature=None):
        return True

    def interactive(self):
        return False

    def formatted(self):
        return False

def open_repository(name, create=False):
    repo_base = current_app.config.get('REPOSITORY_BASE')
    repo_path = os.path.join(repo_base, name)
    return hg.repository(web_ui(), repo_path)

def wsgi_handler(repository):
    return hgweb(repository, baseui=repository.ui)
