import os
from lxml import etree

ns = {
    'n':'urn:oasis:names:tc:opendocument:xmlns:container',
    'pkg':'http://www.idpf.org/2007/opf',
    'dc':'http://purl.org/dc/elements/1.1/'
    }

CONTENT_MIME = ['application/xhtml+xml', 'application/x-dtbook+xml',
                'text/x-oeb1-document']

ROOTFILE_PATH = 'n:rootfiles/n:rootfile/@full-path'
ITEM_PATH = '/pkg:package/pkg:manifest/pkg:item'

class ManifestItem(object):

    def __init__(self, elem, base_path, content_path):
        self.elem = elem
        self.base_path = base_path
        self.content_path = content_path
        self._doc = None
    
    @property
    def id(self):
        return self.elem.get('id')

    @property
    def media_type(self):
        return self.elem.get('media-type')

    @property
    def is_content(self):
        return self.media_type in CONTENT_MIME

    @property
    def href(self):
        return self.elem.get('href')
    
    @property
    def path(self):
        _path = os.path.join(self.content_path, self.href)
        _path = os.path.realpath(_path)
        if _path.startswith(self.base_path):
            return _path

    @property
    def relpath(self):
        return os.path.relpath(self.path, self.base_path)
    
    def fh(self):
        return open(self.path, 'rb')
    
    @property
    def doc(self):
        if self._doc is None:
            fh = self.fh()
            self._doc = etree.parse(fh)
            fh.close()
        return self._doc

    def __eq__(self, other):
        return self.id == other.id


class Package(object):

    def __init__(self, base_path):
        self.base_path = base_path
        self._container_doc = None
        self._content_doc = None
        self._spine = None

    @property
    def container(self):
        if self._container_doc is None:
            file_path = os.path.join(self.base_path, 'META-INF', 
                                     'container.xml')
            self._container_doc = etree.parse(file_path)
        return self._container_doc

    @property
    def rootfile(self):
        rootfiles = self.container.xpath(ROOTFILE_PATH, namespaces=ns)
        if not len(rootfiles):
            return None
        return rootfiles[0]

    @property
    def content(self):
        if self._content_doc is None:
            path = os.path.join(self.base_path, self.rootfile)
            self._content_doc = etree.parse(path)
        return self._content_doc

    @property
    def metadata(self):
        node = self.content.xpath('/pkg:package/pkg:metadata',
                                   namespaces=ns)[0]
        metadata = []
        for child in node:
            if child.text is None:
                continue
            metadata.append((child.tag.split('}', 1)[-1], 
                             child.text))
        # HACK
        return dict(metadata)
    
    @property
    def content_path(self):
        return os.path.dirname(os.path.join(
                    self.base_path, self.rootfile))

    @property
    def manifest(self):
        manifest = self.content.xpath(ITEM_PATH,
                                      namespaces=ns)
        items = []
        for item in manifest:
            items.append(ManifestItem(item, 
                self.base_path,
                self.content_path))
        return items
    
    def item_by_id(self, id):
        item = self.content.xpath(ITEM_PATH + "[@id=\"%s\"]" % id,
                                  namespaces=ns)[0]
        return ManifestItem(item, self.base_path, self.content_path)
    
    def item_by_href(self, href):
        item = self.content.xpath(ITEM_PATH + "[@href=\"%s\"]" % href,
                                  namespaces=ns)[0]
        return ManifestItem(item, self.base_path, self.content_path)

    def item_by_relpath(self, relpath):
        for item in self.manifest:
            if item.relpath == relpath:
                return item

    @property
    def spine_elem(self):
        return self.content.xpath("/pkg:package/pkg:spine", namespaces=ns)[0]
    
    @property
    def toc(self):
        return self.item_by_id(self.spine_elem.get('toc'))
    
    @property
    def spine(self):
        if self._spine is None:
            self._spine = [self.item_by_id(c.get('idref')) \
                    for c in self.spine_elem]
        return self._spine


    
