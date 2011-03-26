# -*- coding: iso-8859-1 -*-

import traceback
from xml.dom.minidom import Node, parse
import os.path
from fierrotools.xmldomUtils import *

from fpdf.fpdf import FPDF
from rawtext import RawTextEngine
import barcodes

__version__ = "Lambda PyForm 1.1"
# TODO: Colores


class Parseable(object):

    def parse(self, node):
        pass

    def newObject(klass, node):
        o = klass()
        for x in klass.__slots__:
            setattr(o, x, None)
        o.parse(node)
        return o
    newObject = classmethod(newObject)


class Element(Parseable):
    __slots__ = ["name", "enabled", "top", "left"]

    def render(self, engine, offsetX=0, offsetY=0, globals=None, locals=None, defaults=None):
        pass

    def parse(self, node):
        self.name = getAttribute(node, "name", 'NONAME_%s' % id(self))
        self.visible = getAttribute(node, "visible", True)
        self.top = float(getAttribute(node, "top", 0))
        self.left = float(getAttribute(node, "left", 0))
        self.enabled = getAttribute(node, "enabled", 'True')

    def isEnabled(self, globals, locals):
        locals['self'] = self
        try:
            if locals["debug"]:
                return True
            else:
                return eval(self.enabled, globals, locals)
        except Exception, e:
            traceback.print_exc()
            raise RuntimeError("Error evaluando %s: %s\n%s" % (self.name, self.enabled, str(e)))

# Elementos "dibujables" básicos:


class Text(Element):
    __slots__ = Element.__slots__ + ["text", "font", "angle"]

    angle = 0 # Seteo el default para el atributo

    def evalText(self, globals, locals):
        locals['self'] = self
        try:
            if locals.get("debug"):
                return self.text
            else:
                if type(self.text) == unicode:
                    self.text = self.text.encode('latin1')
                #print "self.text",self.text
                ret = eval(self.text or "''", globals, locals)
                if ret is None:
                    return u''
                if not isinstance(ret, basestring):
                    ret = str(ret)
                return unicode(ret, "latin1")
        except Exception, e:
            traceback.print_exc()
            raise RuntimeError("Error evaluando Texto/Celda %s: %s\n%s" % (self.name, self.text, str(e)))

    def render(self, engine, offsetX=0, offsetY=0, globals=None, locals=None, defaults=None):
        if self.isEnabled(globals, locals):
            if self.angle:
                # setear angulo de rotación
                engine.Rotate(self.angle, self.left + offsetX, self.top + offsetY)
            if self.font:
                self.font.render(engine) # set font
            engine.Text(self.left + offsetX, self.top + offsetY,
                     self.evalText(globals, locals))
            if self.font and defaults.has_key("font"):
                # reestablecer la fuente por defecto
                defaults['font'].render(engine)
            if self.angle:
                # volver a horizontal (0 grados)
                engine.Rotate(0, self.left + offsetX, self.top + offsetY)

    def parse(self, node):
        Element.parse(self, node)
        self.text = getText(node).strip()
        f = getChildByName(node, "font")
        self.font = f and Font.newObject(f) or None
        self.angle = float(getAttribute(node, "angle", 0))


class Cell(Text):
    __slots__ = Text.__slots__ + ["align", "width", "height", "border", "fill", "multiline", "maxlines", "angle"]

    angle = 0 # Seteo el default para el atributo

    def render(self, engine, offsetX=0, offsetY=0, globals=None, locals=None, defaults=None):

        if self.isEnabled(globals, locals):
            text = self.evalText(globals, locals)
            if self.angle:
                # setear angulo de rotación
                engine.Rotate(self.angle, self.left + offsetX, self.top + offsetY)
            if self.font:
                self.font.render(engine) # set font
            if self.border:
                self.border.render(engine) # set line width
                border = self.border.style
            else:
                border = 0
            #print "cell %s align:%s border %s multicell=%s" % (self.name, self.align, border, self.multiline)
            if not self.multiline:
                engine.SetXY(self.left + offsetX, self.top + offsetY)
                # recorto el texto si se va del ancho
                #print engine.GetStringWidth(text), self.width
                text = text.split('\n')[0]
                while engine.GetStringWidth(text) > self.width - (engine.cMargin * 2):

                    if self.align == 'L':
                        text = text[0:-1]
                    elif self.align == 'R':
                        text = text[1:]
                    elif self.align == 'C':
                        text = text[1:-1]
                    else:
                        break

                engine.Cell(self.width, self.height,
                            text,
                            border, 0,
                            self.align, self.fill,
                             )
            else:
                engine.SetXY(self.left + offsetX, self.top + offsetY)

                # recorto el texto si se va del largo (maxlines)
                line = 1
                width = 0.0
                if text:
                    for i in xrange(0, len(text)):
                        c = text[i]
                        if c == '\n':
                            line += 1
                            width = 0.0
                        else:
                            w = engine.GetStringWidth(c)
                            if width + w > self.width - (engine.cMargin * 2):
                                line += 1
                                width = 0.0
                            width += w
                        if line > self.maxlines:
                            break
                    text = text[0:i]

                engine.MultiCell(self.width, self.height,
                                text,
                                border,
                                self.align, self.fill,
                         )
            if self.font and defaults.has_key("font"):
                # reestablecer la fuente por defecto
                defaults['font'].render(engine)
            if self.border and defaults.has_key("lineWidth"):
                # reestablecer el ancho de la linea
                defaults['lineWidth'].render(engine)
            if self.angle:
                # volver a horizontal (0 grados)
                engine.Rotate(0, self.left + offsetX, self.top + offsetY)

    def parse(self, node):
        Text.parse(self, node)
        self.align = getAttribute(node, "align", "left")[0].upper()
        self.width = float(getAttribute(node, "width", 0))
        self.height = float(getAttribute(node, "height", 0))
        self.fill = getAttribute(node, "fill", "false") == "true"
        self.multiline = getAttribute(node, "multiline", "false") == "true"
        self.maxlines = int(getAttribute(node, "maxlines", "0"))
        b = getChildByName(node, "border")
        self.border = b and Border.newObject(b) or None
        self.angle = float(getAttribute(node, "angle", 0))


class Barcode(Element):
    __slots__ = Element.__slots__ + ["text", "barcode"]

    def evalText(self, globals, locals):
        locals['self'] = self
        try:
            if locals.get("debug"):
                return self.text
            else:
                ret = eval(self.text or "''", globals, locals)
                if ret is None:
                    raise RuntimeError("None no permitido, debe ser un string")
                else:
                    return ret
        except Exception, e:
            traceback.print_exc()
            raise RuntimeError("Error evaluando Texto del Código de Barra %s: %s\n%s" % (self.name, self.text, str(e)))

    def render(self, engine, offsetX=0, offsetY=0, globals=None, locals=None, defaults=None):
        if self.isEnabled(globals, locals):
            if self.angle:
                # setear angulo de rotación
                engine.Rotate(self.angle, self.left + offsetX, self.top + offsetY)
            if self.barcode:
                self.barcode.render(engine,
                                      self.left + offsetX, self.top + offsetY,
                                      self.evalText(globals, locals))
            if self.angle:
                # volver a horizontal (0 grados)
                engine.Rotate(0, self.left + offsetX, self.top + offsetY)

    def parse(self, node):
        Element.parse(self, node)
        self.text = getText(node).strip()
        kwArgs = {}
        width = getAttribute(node, "width", None)
        if width:
            kwArgs['width'] = float(width)
        height = getAttribute(node, "height", None)
        if height:
            kwArgs['height'] = float(height)
        barcode = getAttribute(node, "barcode", "code39")
        if barcode == "code39":
            self.barcode = barcodes.Code39(**kwArgs)
        elif barcode == "interleaved25":
            self.barcode = barcodes.Interleaved25(**kwArgs)
        elif barcode == "ean13":
            self.barcode = barcodes.EAN13(**kwArgs)
        elif barcode == "upc_a":
            self.barcode = barcodes.UPC_A(**kwArgs)
        elif barcode == "codabar":
            self.barcode = barcodes.Codabar(**kwArgs)
        else:
            raise RuntimeError("Tipo de código de barras '%s' no disponible" % barcode)
        self.angle = float(getAttribute(node, "angle", 0))


class Line(Element):
    __slots__ = Element.__slots__ + ["width", "height", "lineWidth"]

    def render(self, engine, offsetX=0, offsetY=0, globals=None, locals=None, defaults=None):
        if self.isEnabled(globals, locals):
            if self.lineWidth:
                self.lineWidth.render(engine)
            engine.Line(self.left + offsetX,
                     self.top + offsetY,
                     self.left + self.width + offsetX,
                     self.top + self.height + offsetY)
            if self.lineWidth and defaults.has_key("lineWidth"):
                # reestablecer el ancho de la linea
                defaults['lineWidth'].render(engine)

    def parse(self, node):
        Element.parse(self, node)
        self.width = float(getAttribute(node, "width", 0))
        self.height = float(getAttribute(node, "height", 0))
        w = float(getAttribute(node, "lineWidth", 0.2))
        if w:
            self.lineWidth = LineWidth()
            self.lineWidth.width = w


class Rect(Line):
    __slots__ = Line.__slots__ + ["fill"]

    def render(self, engine, offsetX=0, offsetY=0, globals=None, locals=None, defaults=None):
        if self.isEnabled(globals, locals):
            if self.lineWidth:
                self.lineWidth.render(engine)
            if self.fill:
                style = "DF"
            else:
                style = "D"
            engine.Rect(self.left + offsetX,
                     self.top + offsetY,
                     self.width,
                     self.height,
                     style)
            if self.lineWidth and defaults.has_key("lineWidth"):
                # reestablecer el ancho de la linea
                defaults['lineWidth'].render(engine)

    def parse(self, node):
        Line.parse(self, node)
        self.fill = getAttribute(node, "fill", "false") == "true"


class Image(Element):
    __slots__ = Element.__slots__ + ["width", "height", "filename", "type"]

    angle = 0 # Seteo el default para el atributo

    def render(self, engine, offsetX=0, offsetY=0, globals=None, locals=None, defaults=None):
        if self.isEnabled(globals, locals):
            if self.angle:
                # setear angulo de rotación
                engine.Rotate(self.angle, self.left + offsetX, self.top + offsetY)
            engine.Image(eval(self.filename, globals, locals),
                      self.left + offsetX,
                      self.top + offsetY,
                      self.width,
                      self.height,
                      self.type)
            if self.angle:
                # volver a horizontal (0 grados)
                engine.Rotate(0, self.left + offsetX, self.top + offsetY)

    def parse(self, node):
        Element.parse(self, node)
        self.width = float(getAttribute(node, "width", 0))
        self.height = float(getAttribute(node, "height", 0))
        self.filename = getAttribute(node, "filename", "")
        self.type = getAttribute(node, "type", "")
        self.angle = float(getAttribute(node, "angle", 0))

# Helpers, no son elementos "dibujables":


class Font(Parseable):
    __slots__ = ["style", "family", "size"]

    def render(self, engine):
        engine.SetFont(self.family, self.style, self.size)

    def parse(self, node):
        self.style = ""
        if getAttribute(node, "bold", False) == "true": self.style += "B"
        if getAttribute(node, "italic", False) == "true": self.style += "I"
        if getAttribute(node, "underline", False) == "true": self.style += "U"
        if getAttribute(node, "compressed", False) == "true": self.style += "C"
        self.family = getAttribute(node, "family", "arial")
        self.size = float(getAttribute(node, "size", 12))


class LineWidth(Parseable):
    __slots__ = ["width"]

    def render(self, engine):
        if self.width:
            engine.SetLineWidth(self.width)

    def parse(self, node):
        self.width = float(getText(node))


class Border(Parseable):
    __slots__ = ["style", "lineWidth"]

    def __init__(self, style=None, lineWidth=None):
        self.style = style
        self.lineWidth = lineWidth

    def render(self, engine):
        if self.lineWidth:
            self.lineWidth.render(engine)

    def parse(self, node):
        self.style = ""
        if getAttribute(node, "left", "false") == "true": self.style += "L"
        if getAttribute(node, "top", "false") == "true": self.style += "T"
        if getAttribute(node, "right", "false") == "true": self.style += "R"
        if getAttribute(node, "bottom", "false") == "true": self.style += "B"
        if self.style == "":
            self.style = 0
        w = float(getAttribute(node, "lineWidth", 0.2))
        if w:
            self.lineWidth = LineWidth()
            self.lineWidth.width = w


class Color(Parseable):
    __slots__ = ["red", "blue", "green"]

    def parse(self, node):
        self.style = ""
        self.red = getAttribute(node, "red", 0)
        self.blue = getAttribute(node, "blue", 0)
        self.green = getAttribute(node, "green", 0)
        standard = getAttribute(node, "standard", "")
        if standard == "red":
            self.red = 255
        elif standard == "blue":
            self.blue = 255
        elif standard == "green":
            self.green = 255
        elif standard == "white":
            self.red = 255
            self.blue = 255
            self.green = 255


class ForegroundColor(Color):
    __slots__ = Color.__slots__

    def render(self, engine):
        engine.SetTextColor(self.red, self.blue, self.green)
        engine.SetDrawColor(self.red, self.blue, self.green)


class BackgroundColor(Color):
    __slots__ = Color.__slots__

    def render(self, engine):
        engine.SetFillColor(self.red, self.blue, self.green)


class Variable(Parseable):
    __slots__ = ["name", "value"]

    def eval(self, globals, locals):
        try:
            locals[self.name] = eval(self.value, globals, locals)
        except Exception, e:
            traceback.print_exc()
            raise RuntimeError("Error evaluando variable %s: %s\n%s" % (self.name, self.value, str(e)))

    def parse(self, node):
        self.name = getRequiredAttribute(node, "name")
        self.value = getRequiredAttribute(node, "value")

# Contenedores de Elementos


class Container(Element):
    __slots__ = Element.__slots__ + ["elements", "rows", "cols", "copies",
                                      "width", "height",
                                      "defaultFont", "defaultBorder",
                                      "variables",
                                    ]

    def __init__(self):
        self.containedClasses = {'text': Text, 'line': Line, 'rect': Rect, 'cell': Cell, 'image': Image, 'container': Container, 'barcode': Barcode}

    def render(self, engine, offsetX=0, offsetY=0, globals=None, locals=None, defaults=None):

        offsetX = offsetX + self.left
        offsetY = offsetY + self.top
        if self.defaultFont:
            self.defaultFont.render(engine)
            defaults['font'] = self.defaultFont
        if self.defaultLineWidth:
            self.defaultLineWidth.render(engine)
            defaults['lineWidth'] = self.defaultLineWidth

        for row in xrange(self.rows):
            for col in xrange(self.cols):
                locals['row'] = row
                locals['col'] = col

                if self.isEnabled(globals, locals):
                    if self.variables:
                        for var in self.variables.values():
                            var.eval(globals, locals)
                    for element in self.elements.values():
                        #print "rendering %s[%s,%s]: (%s,%s) " % (self.name,row,col,offsetX + row*self.width,offsetY + col*self.height)
                        element.render(engine, offsetX + col * self.width,
                                        offsetY + row * self.height,
                                        globals, locals,
                                        defaults)

    def parse(self, node):
        Element.parse(self, node)
        defaultFont = getChildByName(node, "defaultFont")
        self.defaultFont = defaultFont and Font.newObject(defaultFont) or None
        defaultLineWidth = getChildByName(node, "defaultLineWidth")
        self.defaultLineWidth = defaultLineWidth and LineWidth.newObject(defaultLineWidth) or None
        elements = getChildByName(node, "elements")
        self.elements = {}
        for element in elements.childNodes:
            if element.localName in self.containedClasses:
                e = self.containedClasses[element.localName].newObject(element)
                self.elements[e.name] = e
        self.rows = int(getAttribute(node, "rows", "1"))
        self.cols = int(getAttribute(node, "cols", "1"))
        self.copies = int(getAttribute(node, "copies", "1"))
        self.width = float(getAttribute(node, "width", 0))
        self.height = float(getAttribute(node, "height", 0))
        self.variables = {}
        vars = getChildByName(node, "variables")
        if vars:
            for var in vars.childNodes:
                if var.localName == 'variable':
                    v = Variable.newObject(var)
                    self.variables[v.name] = v


class Form(Parseable):
    __slots__ = ["variables", "bodies", "header", "pages",
                  "format", "orientation", "unit",
                  "title", "top", "left", "right",
                  "author", "subject", "creator",
                  "basedir", "engine", "collateCopies",
                ]

    def __init__(self, filename=None, bodies=None, pages=None,
                 format=None, orientation=None, unit=None,
                 title=None, top=None, left=None, author=None, subject=None, creator=None,
                 basedir=None, engine=None):
        if filename:
            xmldoc = parse(filename)
            f = xmldoc.getElementsByTagName("form")[0]
            self.parse(f)
            self.basedir = os.path.dirname(os.path.realpath(filename))
        else:
            self.bodies = bodies or {}
            self.pages = pages or 0
            self.format = format or "default"
            self.top = top or 0
            self.left = left or 0
            self.basedir = basedir
            self.engine = engine
            self.title = title or ""
            self.orientation = orientation or "default"
            self.author = author or ""
            self.subject = subject or ""
            self.creator = creator or ""
            self.collateCopies = False

    def render(self, filename, *args, **kwargs):

        # call the implementation
        if self.implementation:
            locals = self.implementation(self, *args, **kwargs)
        elif hasattr(self, 'locals'): # si inicializé el objeto "a mano"
            locals = self.locals
        else:
            locals = {}
        if self.engine == 'fpdf':
            engine = FPDF(self.orientation[0].upper(), self.unit, self.format)
        elif self.engine == 'text':
            engine = RawTextEngine(self.orientation[0].upper(), self.unit, self.format, printer=kwargs['printer'])
        if self.title:
            engine.SetTitle(eval(self.title, globals(), locals).encode("latin1").decode("utf8", "ignore"))

        engine.SetAuthor(self.author.encode("latin1").decode("utf8"))
        engine.SetSubject(self.subject.encode("latin1").decode("utf8"))
        engine.SetCreator(self.creator.encode("latin1").decode("utf8"))

        def renderPage(copy, page):
            engine.AddPage()
            engine.SetMargins(0, 0, 0)
            engine.SetAutoPageBreak(False)
            locals['pgno'] = page # 0: pagina 1, 1: pagina 2, 3: pagina 3
            locals['copy'] = copy # 0: original, 1: duplicado, 2: triplicado
            locals['pgabs'] = copy * self.pages + page
            locals['basedir'] = self.basedir
            locals['pages'] = int(self.pages)
            for var in self.variables.values():
                var.eval(globals(), locals)
            body.render(engine,
                            offsetX=self.left,
                            offsetY=self.top,
                            globals=globals(), locals=locals,
                            defaults={},
                        )

        for body in self.bodies.values():
            if not self.collateCopies:
                # no intercalar
                for copy in xrange(int(body.copies)):
                    for page in xrange(int(self.pages)):
                        renderPage(copy, page)
            else:
                # intercalar copias
                for page in xrange(int(self.pages)):
                    for copy in xrange(int(body.copies)):
                        renderPage(copy, page)
        engine.Output(filename)

    def parse(self, node):
        self.bodies = {}
        self.variables = {}
        for body in getChildsByName(node, "body"):
            b = Container.newObject(body)
            self.bodies[b.name] = b
        vars = getChildByName(node, "variables")
        for var in vars.childNodes:
            if var.localName == 'variable':
                v = Variable.newObject(var)
                self.variables[v.name] = v
        self.pages = 1
        self.format = getAttribute(node, "format", "A4")
        if self.format[0] == "(":
            self.format = eval(self.format)
        self.orientation = getAttribute(node, "orientation", "portrait")
        self.unit = getAttribute(node, "unit", "mm")
        self.author = getAttribute(node, "author", "")
        self.subject = getAttribute(node, "subject", "")
        self.creator = getAttribute(node, "creator", __version__)
        title = getChildByName(node, "title")
        self.title = title and getText(title) or "''"

        margins = getChildByName(node, "margins")
        if margins:
            self.top = float(getAttribute(margins, "top", "0"))
            self.left = float(getAttribute(margins, "left", "0"))
            self.right = float(getAttribute(margins, "right", "0"))

        impl = getChildByName(node, "implementation")
        self.implementation = None
        if impl:
            module = getAttribute(impl, "module", "")
            function = getAttribute(impl, "function", "")
            mod = __import__(module)
            components = module.split('.')
            for comp in components[1:]:
                mod = getattr(mod, comp)
            reload(mod)
            self.implementation = getattr(mod, function)

        self.engine = getAttribute(node, "engine", "fpdf")
        self.copies = float(getAttribute(margins, "copies", "1"))
        self.collateCopies = getAttribute(node, "collateCopies", "false") == "true"

if __name__ == "__main__":
    import os, sys
#    if len(sys.argv)<2:
#        print "El primer parametro debe ser un XML!"
#        fn = "PyFormTest.xml"
#    else:
    fn = sys.argv[1]

    from colofon.model.printer import EpsonPrinter

    f = Form(fn)

    if f.engine == "fpdf":
        fn = os.path.splitext(fn)[0] + os.path.extsep + "pdf"
        f.render(fn, {})
    else:
        fn = os.path.splitext(fn)[0] + os.path.extsep + "txt"
        f.render(fn, {}, printer=EpsonPrinter())

    try:
        os.startfile(fn)
    except:
        os.system("evince %s" % fn)
