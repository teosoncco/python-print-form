# -*- coding: iso-8859-1 -*-
import warnings
import types

# "Motor de dibujo" texto plano genérico para impresoras de matriz de punto


class RawTextEngine:

    def __init__(self, orientation='P', unit='chars', format='(132,36)', printer=None):
        if type(format) in types.StringTypes:
            format = eval(format)
        self.width = format[0]
        self.height = format[1]
        self.x = 0          # columna actual
        self.y = 0          # linea actual
        self.left = 0       # margen izquierdo (columnas en blanco)
        self.top = 0        # margen superior (lineas en blanco)
        self.cells = []     # celdas de la página actual
        self.page = 0       # página actual
        self.pages = {}     # paginas: {nro_pagina:Page}
        self.style = Style() # estilo actual
        self.cMargin = 0  # margen interior de la celdas que no se usa
        self.printer = printer

    def SetMargins(self, left, top, right=-1):
        self.left = left
        self.top = top

    def AddPage(self, orientation=''):
        self.x = self.left
        self.y = self.top
        self.page += 1
        self.pages[self.page] = Page()
        self.cells = self.pages[self.page].cells

    def SetXY(self, x, y):
        self.y = int(y)
        self.x = int(x)

    def GetStringWidth(self, s):
        return len(s)

    def SetFont(self, family, style='', size=0):
        self.style = Style(style, self.printer)

    def Write(self, h, txt, link=''):
        " Escribir un texto (genera una ''celda'' interna) "
        # no se llama desde pyForm, es usado internamente
        # Nota: la semantica del parametro h no es igual que en FPDF
        #       (se usa solo para las multiceldas)
        text = unicode(txt).encode("iso-8859-1", "ignore").rstrip()
        if text:
            self.cells.append(Cell(self.x, self.y, text, self.style))
        if not h:
            self.x += len(text)
        else:
            self.y += int(h)

    def Text(self, x, y, txt):
        " Escribir un texto en determinada posición "
        self.SetXY(x, y)
        self.Write(0, txt)

    def Cell(self, w, h=0, txt='', border=0, ln=0, align='', fill=0, link=''):
        " Escribir un texto en una celda (aplicando alineacion y tamaño) "
        width = int(w)
        if align == "L" or align == 'J':
            text = (txt + (" " * width))[0:width]
        elif align == "R":
            text = ((" " * width) + txt)[-width:]
        elif align == "C":
            text = ((" " * width) + txt + (" " * width))
            text = text[len(text) / 2 - width / 2:len(text) / 2 + width / 2]
        self.Write(ln and 1 or 0, text)

    def MultiCell(self, w, h, txt, border=0, align='J', fill=0):
        " Escribir un texto con multiples lineas verticales "
        s = ''
        for c in txt:
            if c == '\n':
                self.Cell(w, h, txt=s, align=align, ln=1, border=border, fill=fill)
                s = ''
            else:
                if self.GetStringWidth(s + c) > w:
                    self.Cell(w, h, txt=s, align=align, ln=1, border=border, fill=fill)
                    s = ''
                s += c
        if s:
            self.Cell(w, h, txt=s, align=align, ln=1, border=border, fill=fill)

    def Output(self, name='', dest=''):
        # comienzo la impresión (inicializo la impresora)
        buffer = self.printer.startPrint(self.height)

        # recorro las paginas (de 1 a la ultima pagina)
        for page in xrange(1, self.page + 1):

            # recorro las celdas verticalmente
            # (de y=0 a la cantidad de lineas o maximo de la hoja)
            if self.pages[page].cells:
                maxy = max([cell.y for cell in self.pages[page].cells]) + 1
            else:
                maxy = 0
            for y in xrange(0, min(maxy, self.height)):

                # filtro todas las celdas de la linea (y)
                cells = [cell for cell in self.pages[page].cells if cell.y == y]

                # las ordeno para procesarlas de izquierda a derecha
                cells.sort(lambda c1, c2: cmp(c1.x, c2.x))

                # tomo el primer estilo para los espacios
                if cells:
                    spaceStyle = cells[0].style

                output = "" # buffer temporal de la linea a imprimir
                x = 0       # columna inicial

                # recorro las celdas para la linea actual (si hay)
                for cell in cells:
                    if x < cell.x:
                        # genero el padding hasta la posición de la celda
                        output += spaceStyle.getCompressedBeginCode()
                        output += " " * (cell.x - x)
                        output += spaceStyle.getCompressedEndCode()
                        x = cell.x

                    if x > cell.x:
                        warnings.warn("Hay solapamiento de campos: %s" % (cell), RuntimeWarning)

                    if x + len(cell.text) > self.width:
                        warnings.warn("El texto excede el ancho de la página: %s" % (cell), RuntimeWarning)

                    output += cell.style.getBeginCode()
                    output += cell.text
                    output += cell.style.getEndCode()
                    x += len(cell.text) #actualizo la columna actual

                # fin de la linea actual (retorno de carro)
                buffer += output + "\n"

            # fin de la página actual
            buffer += self.printer.formFeed()

        file(name, "w").write(buffer)

    # metodos no implementados para compatibilidad con pyForm
    # (innecesarios por ahora)

    def SetTitle(this, title):
        pass

    def SetSubject(this, subject):
        pass

    def SetAuthor(this, author):
        pass

    def SetKeywords(this, keywords):
        pass

    def SetCreator(this, creator):
        pass

    def SetDrawColor(this, r, g=-1, b=-1):
        pass

    def SetFillColor(this, r, g=-1, b=-1):
        pass

    def SetTextColor(this, r, g=-1, b=-1):
        pass

    def SetLineWidth(this, width):
        pass

    def Line(this, x1, y1, x2, y2):
        pass

    def Rect(this, x, y, w, h, style=''):
        pass

    def Image(this, name, x, y, w=0, h=0, type='', link=''):
        pass

    def SetAutoPageBreak(this, auto, margin=0):
        pass

# Clases auxiliares:


class Page:

    def __init__(self):
        self.cells = []


class Cell:

    def __init__(self, x, y, text, style):
        self.x = x
        self.y = y
        self.text = text
        self.style = style

    def __str__(self):
        return "(%d,%d,'%s',%s)" % (self.x, self.y, self.text, self.style.style)


class Style:

    def __init__(self, style='', printer=None):
        self.style = style
        self.printer = printer

    def getBeginCode(self):
        code = ''
        if 'B' in self.style:
            code += self.printer.beginEmphasized()
        if 'I' in self.style:
            code += self.printer.beginItalic()
        if 'U' in self.style:
            code += self.printer.beginUnderlining()
        return code + self.getCompressedBeginCode()

    def getEndCode(self):
        code = ''
        if 'B' in self.style:
            code += self.printer.endEmphasized()
        if 'I' in self.style:
            code += self.printer.endItalic()
        if 'U' in self.style:
            code += self.printer.endUnderlining()
        return code + self.getCompressedEndCode()

    def getCompressedBeginCode(self):
        code = ''
        if 'C' in self.style:
            code += self.printer.beginCompressed()
        return code

    def getCompressedEndCode(self):
        code = ''
        if 'C' in self.style:
            code += self.printer.endCompressed()
        return code
