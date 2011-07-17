from flask import Module, abort, request, redirect, url_for
from flask import render_template
from repo import open_repository, wsgi_handler
from package import Package
from lxml import html

text = Module(__name__, 'text')

HG_METHODS = ['GET', 'POST', 'PUT']

@text.route('/')
def index():
    return "Index"

def render_page(id, package, doc):
    fh = doc.fh()
    src = html.parse(fh)
    idx = package.spine.index(doc)
    title = src.findtext('//title')
    body = src.find('//body')
    body.tag = 'span'
    fh.close()
    return render_template('text/view.html',
            id = id,
            title = title,
            metadata = package.metadata,
            frwd = package.spine[idx+1] if len(package.spine)>idx else None,
            prev = package.spine[idx-1] if idx>0 else None,
            body = html.tostring(body))

@text.route('/<id>::<item>')
def item(id, item):
    repository = open_repository(id)
    pkg = Package(repository.root)
    item = pkg.item_by_id(item)
    if not item:
        abort(404)
    return redirect(url_for('view', id=id,
                    relpath=item.relpath))

@text.route('/<id>', methods=HG_METHODS)
@text.route('/<id>/<path:relpath>', methods=HG_METHODS)
def view(id, relpath=None):
    repository = open_repository(id)
    pkg = Package(repository.root)
    if 'cmd' in request.args:
        return repo(id, relpath or '/')
    if relpath is None:
        return redirect(url_for('view', id=id, 
            relpath=pkg.spine[0].relpath))
    
    doc = pkg.item_by_relpath(relpath)
    if not doc:
        abort(404)
    if doc.is_content:
        return render_page(id, pkg, doc)
    return doc.fh().read()

@text.route('/<id>.hg')
@text.route('/<id>.hg/<path:path>')
def repo(id, path='/'):
    repository = open_repository(id)
    request.environ['PATH_INFO'] = path
    base = url_for('repo', id=id)
    request.environ['SCRIPT_NAME'] = base
    return wsgi_handler(repository)

