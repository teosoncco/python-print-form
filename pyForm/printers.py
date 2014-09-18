# -*- coding: iso-8859-1 -*-

class Printer:

    def startPrint(self, linesPerPage):
        raise NotImplementedError

    def beginCompressed(self):
        raise NotImplementedError

    def endCompressed(self):
        raise NotImplementedError

    def beginEmphasized(self):
        return ''

    def endEmphasized(self):
        return ''

    def beginItalic(self):
        return ''

    def endItalic(self):
        return ''

    def beginUnderlining(self):
        return ''

    def endUnderlining(self):
        return ''

    def formFeed(self):
        return ''

    def getEncoding(self):
        return None

    def sendCodes(self, codes):
        """Recibe códigos como valores enteros y los envía a la impresora"""
        return "".join(map(chr, codes))


class OkiPosPrinter(Printer):
    name = 'OkiPos'

    def startPrint(self, linesPerPage):
        return chr(27) + chr(64) + chr(27) + chr(67) + chr(linesPerPage) + chr(18)

    def beginEmphasized(self):
        return chr(27) + chr(69)

    def endEmphasized(self):
        return chr(27) + chr(70)

    def beginCompressed(self):
        return chr(27) + chr(77) + chr(1)

    def endCompressed(self):
        return chr(27) + chr(77) + chr(0)

    def beginUnderlining(self):
        return chr(27) + chr(45) + chr(1)

    def endUnderlining(self):
        return chr(27) + chr(45) + chr(0)

    def formFeed(self):
        return chr(29) + chr(86) + chr(0)

    def getEncoding(self):
        return "ibm850"


class EpsonPrinter(Printer):
    name = 'Epson'

    def startPrint(self, linesPerPage):
        return chr(27) + chr(64) + chr(27) + chr(67) + chr(linesPerPage) + chr(18)

    def beginCompressed(self):
        return chr(15)

    def endCompressed(self):
        return chr(18)

    def beginEmphasized(self):
        return chr(27) + chr(69)

    def endEmphasized(self):
        return chr(27) + chr(70)

    def beginItalic(self):
        return chr(27) + chr(52)

    def endItalic(self):
        return chr(27) + chr(53)

    def beginUnderlining(self):
        return chr(27) + chr(45) + chr(1)

    def endUnderlining(self):
        return chr(27) + chr(45) + chr(0)

    def formFeed(self):
        return chr(12)

    def getEncoding(self):
        return "ibm850"


class HPPrinter(Printer):
    name = 'HP'

    def startPrint(self, linesPerPage):
        return chr(27) + chr(69) + chr(27) + chr(38) + chr(108) + str(linesPerPage).strip() + chr(80)

    def beginCompressed(self):
        return chr(27) + chr(40) + chr(115) + chr(49) + chr(54) + chr(72)

    def endCompressed(self):
        return chr(27) + chr(40) + chr(115) + chr(49) + chr(50) + chr(72)

    def formFeed(self):
        return chr(12)


class TagPrinter(Printer):
    name = 'Tags'

    def startPrint(self, linesPerPage):
        return "\\{startPrint %d}" % linesPerPage

    def beginCompressed(self):
        return "\\{beginCompressed}"

    def endCompressed(self):
        return "\\{endCompressed}"

    def beginEmphasized(self):
        return "\\{beginEmphasized}"

    def endEmphasized(self):
        return "\\{endEmphasized}"

    def beginItalic(self):
        return "\\{beginItalic}"

    def endItalic(self):
        return "\\{endItalic}"

    def beginUnderlining(self):
        return "\\{beginUnderlining}"

    def endUnderlining(self):
        return "\\{endUnderlining}"

    def formFeed(self):
        return "\\{formFeed}"

    def sendCodes(self, codes):
        """Recibe códigos como valores enteros y los envía a la impresora"""
        return "\\{sendCodes %s}" % ",".join(map(str, codes))


class NullPrinter(Printer):
    name = 'Sin marca'

    def startPrint(self, linesPerPage):
        return ""

    def beginCompressed(self):
        return ""

    def endCompressed(self):
        return ""

    def formFeed(self):
        return ""

printers = [EpsonPrinter(), HPPrinter(), NullPrinter(), TagPrinter(), OkiPosPrinter()]
