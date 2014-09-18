# -*- coding: iso-8859-1 -*-


class Code39:
    "Código 3 de 9 (alfanumérico)"

    def __init__(self, height=5.0, width=0.5):
        self.barChar = {}
        self.barChar['0'] = 'nnnwwnwnn'
        self.barChar['1'] = 'wnnwnnnnw'
        self.barChar['2'] = 'nnwwnnnnw'
        self.barChar['3'] = 'wnwwnnnnn'
        self.barChar['4'] = 'nnnwwnnnw'
        self.barChar['5'] = 'wnnwwnnnn'
        self.barChar['6'] = 'nnwwwnnnn'
        self.barChar['7'] = 'nnnwnnwnw'
        self.barChar['8'] = 'wnnwnnwnn'
        self.barChar['9'] = 'nnwwnnwnn'
        self.barChar['A'] = 'wnnnnwnnw'
        self.barChar['B'] = 'nnwnnwnnw'
        self.barChar['C'] = 'wnwnnwnnn'
        self.barChar['D'] = 'nnnnwwnnw'
        self.barChar['E'] = 'wnnnwwnnn'
        self.barChar['F'] = 'nnwnwwnnn'
        self.barChar['G'] = 'nnnnnwwnw'
        self.barChar['H'] = 'wnnnnwwnn'
        self.barChar['I'] = 'nnwnnwwnn'
        self.barChar['J'] = 'nnnnwwwnn'
        self.barChar['K'] = 'wnnnnnnww'
        self.barChar['L'] = 'nnwnnnnww'
        self.barChar['M'] = 'wnwnnnnwn'
        self.barChar['N'] = 'nnnnwnnww'
        self.barChar['O'] = 'wnnnwnnwn'
        self.barChar['P'] = 'nnwnwnnwn'
        self.barChar['Q'] = 'nnnnnnwww'
        self.barChar['R'] = 'wnnnnnwwn'
        self.barChar['S'] = 'nnwnnnwwn'
        self.barChar['T'] = 'nnnnwnwwn'
        self.barChar['U'] = 'wwnnnnnnw'
        self.barChar['V'] = 'nwwnnnnnw'
        self.barChar['W'] = 'wwwnnnnnn'
        self.barChar['X'] = 'nwnnwnnnw'
        self.barChar['Y'] = 'wwnnwnnnn'
        self.barChar['Z'] = 'nwwnwnnnn'
        self.barChar['-'] = 'nwnnnnwnw'
        self.barChar['.'] = 'wwnnnnwnn'
        self.barChar[' '] = 'nwwnnnwnn'
        self.barChar['*'] = 'nwnnwnwnn'
        self.barChar['$'] = 'nwnwnwnnn'
        self.barChar['/'] = 'nwnwnnnwn'
        self.barChar['+'] = 'nwnnnwnwn'
        self.barChar['%'] = 'nnnwnwnwn'

        self.height = height
        self.wide = width
        self.narrow = width / 3.0
        self.gap = self.narrow

    def render(self, pdf, xpos, ypos, text):
        pdf.SetFillColor(0)

        code = '*' + text.upper() + '*'
        for char in code:
            if not char in self.barChar.keys():
                raise RuntimeError('Caractér "%s" inválido para el código de barras 39: ' % char)

            seq = self.barChar[char]
            for bar in xrange(0, 9):
                if seq[bar] == 'n':
                    lineWidth = self.narrow
                else:
                    lineWidth = self.wide

                if bar % 2 == 0:
                    pdf.Rect(xpos, ypos, lineWidth, self.height, 'F')

                xpos += lineWidth

            xpos += self.gap


class Interleaved25:
    "Código Entrelazado 2 de 5 (numérico), la longitud debe ser par, sino agrega un 0"

    def __init__(self, height=10.0, width=1.0):
        self.height = height
        self.wide = width
        self.narrow = width / 3.0

        # wide/narrow codes for the digits
        self.barChar = {}
        self.barChar['0'] = 'nnwwn'
        self.barChar['1'] = 'wnnnw'
        self.barChar['2'] = 'nwnnw'
        self.barChar['3'] = 'wwnnn'
        self.barChar['4'] = 'nnwnw'
        self.barChar['5'] = 'wnwnn'
        self.barChar['6'] = 'nwwnn'
        self.barChar['7'] = 'nnnww'
        self.barChar['8'] = 'wnnwn'
        self.barChar['9'] = 'nwnwn'
        self.barChar['A'] = 'nn'
        self.barChar['Z'] = 'wn'

    def render(self, pdf, xpos, ypos, text):
        pdf.SetFillColor(0)
        code = text
        # add leading zero if code-length is odd
        if len(code) % 2 != 0:
            code = '0' + code

        # add start and stop codes
        code = 'AA' + code.lower() + 'ZA'

        for i in xrange(0, len(code), 2):
            # choose next pair of digits
            charBar = code[i];
            charSpace = code[i + 1];
            # check whether it is a valid digit
            if not charBar in self.barChar.keys():
                raise RuntimeError('Caractér "%s" inválido para el código de barras I25: ' % charBar)
            if not charSpace in self.barChar.keys():
                raise RuntimeError('Caractér "%s" inválido para el código de barras I25: ' % charSpace)

            # create a wide/narrow-sequence (first digit=bars, second digit=spaces)
            seq = ''
            for s in xrange(0, len(self.barChar[charBar])):
                seq += self.barChar[charBar][s] + self.barChar[charSpace][s]

            for bar in xrange(0, len(seq)):
                # set lineWidth depending on value
                if seq[bar] == 'n':
                    lineWidth = self.narrow
                else:
                    lineWidth = self.wide

                # draw every second value, because the second digit of the pair is represented by the spaces
                if bar % 2 == 0:
                    pdf.Rect(xpos, ypos, lineWidth, self.height, 'F')

                xpos += lineWidth


class BaseEAN:
    "Clase base para EAN y UPC"

    def __init__(self, height=16.0, width=0.35, length=13):
        self.length = length
        self.height = height
        self.width = width

        self.codes = {
            'A': {
                '0': '0001101', '1': '0011001', '2': '0010011', '3': '0111101', '4': '0100011',
                '5': '0110001', '6': '0101111', '7': '0111011', '8': '0110111', '9': '0001011'},
            'B': {
                '0': '0100111', '1': '0110011', '2': '0011011', '3': '0100001', '4': '0011101',
                '5': '0111001', '6': '0000101', '7': '0010001', '8': '0001001', '9': '0010111'},
            'C': {
                '0': '1110010', '1': '1100110', '2': '1101100', '3': '1000010', '4': '1011100',
                '5': '1001110', '6': '1010000', '7': '1000100', '8': '1001000', '9': '1110100'}}
        self.parities = {
            '0': ('A', 'A', 'A', 'A', 'A', 'A'),
            '1': ('A', 'A', 'B', 'A', 'B', 'B'),
            '2': ('A', 'A', 'B', 'B', 'A', 'B'),
            '3': ('A', 'A', 'B', 'B', 'B', 'A'),
            '4': ('A', 'B', 'A', 'A', 'B', 'B'),
            '5': ('A', 'B', 'B', 'A', 'A', 'B'),
            '6': ('A', 'B', 'B', 'B', 'A', 'A'),
            '7': ('A', 'B', 'A', 'B', 'A', 'B'),
            '8': ('A', 'B', 'A', 'B', 'B', 'A'),
            '9': ('A', 'B', 'B', 'A', 'B', 'A')}

    def GetCheckDigit(self, barcode):
        "Compute the check digit"  # TODO: No sirve para codigos de barra mas grandes (Code 39)
        s = 0
        for i in xrange(1, 12, 2):
            s += 3 * int(barcode[i])
        for i in xrange(0, 11, 2):
            s += int(barcode[i])
        r = s % 10
        if r > 0:
            r = 10 - r
        return str(r)

    def TestCheckDigit(self, string):
        "Test validity of check digit"  # TODO: sirve para codigos de barra mas grandes (Code 39)
        pairsSum = 0
        oddsSum = 0
        for pos, char in enumerate(string[:-1]):
            if (pos % 2) == 0:
                pairsSum += int(char)
            else:
                oddsSum += int(char)
        ret = (oddsSum * 3) + pairsSum

        return (ret + int(string[-1])) % 10 == 0

    def render(self, pdf, x, y, text):  # TODO: No sirve para codigos de barra mas grandes (Code 39)
        pdf.SetFillColor(0)
        barcode = text

        #Padding
        barcode = barcode.zfill(self.length - 1)
        if self.length == 12:
            barcode = '0' + barcode
        #Add or control the check digit
        if len(barcode) == 12:
            barcode += self.GetCheckDigit(barcode)
        elif not self.TestCheckDigit(barcode):
            raise RuntimeError('Dígito de Verificación Incorrecto para: %s' % barcode)

        #Convert digits to bars
        code = '101'
        p = self.parities[barcode[0]]
        for i in xrange(1, 7, 1):
            code += self.codes[p[i - 1]][barcode[i]]
        code += '01010'
        for i in xrange(7, 13, 1):
            code += self.codes['C'][barcode[i]]
        code += '101'
        #Draw bars
        for i in xrange(0, len(code), 1):
            if (code[i] == '1'):
                pdf.Rect(x + i * self.width, y, self.width, self.height, 'F')


class EAN13(BaseEAN):
    "Código EAN13 (numérico), completa con 0 a la izquierda hasta longitud 13, agrega o controla el dígito verificador"

    def __init__(self, height=16.0, width=0.35):
        BaseEAN.__init__(self, height, width, 13)


class UPC_A(BaseEAN):
    "Código UPC A (numérico), completa con 0 a la izquierda hasta longitud 12, agrega o controla el dígito verificador"

    def __init__(self, height=16.0, width=0.35):
        BaseEAN.__init__(self, height, width, 12)


class Codabar:
    "Código Codabar (numérico con códigos de control)"

    def __init__(self, height=16.0, width=0.35, start='A', end='A'):
        self.height = height
        self.width = width
        self.start = start
        self.end = end
        self.barChar = {
            '0': (6.5, 10.4, 6.5, 10.4, 6.5, 24.3, 17.9),
            '1': (6.5, 10.4, 6.5, 10.4, 17.9, 24.3, 6.5),
            '2': (6.5, 10.0, 6.5, 24.4, 6.5, 10.0, 18.6),
            '3': (17.9, 24.3, 6.5, 10.4, 6.5, 10.4, 6.5),
            '4': (6.5, 10.4, 17.9, 10.4, 6.5, 24.3, 6.5),
            '5': (17.9, 10.4, 6.5, 10.4, 6.5, 24.3, 6.5),
            '6': (6.5, 24.3, 6.5, 10.4, 6.5, 10.4, 17.9),
            '7': (6.5, 24.3, 6.5, 10.4, 17.9, 10.4, 6.5),
            '8': (6.5, 24.3, 17.9, 10.4, 6.5, 10.4, 6.5),
            '9': (18.6, 10.0, 6.5, 24.4, 6.5, 10.0, 6.5),
            '$': (6.5, 10.0, 18.6, 24.4, 6.5, 10.0, 6.5),
            '-': (6.5, 10.0, 6.5, 24.4, 18.6, 10.0, 6.5),
            ':': (16.7, 9.3, 6.5, 9.3, 16.7, 9.3, 14.7),
            '/': (14.7, 9.3, 16.7, 9.3, 6.5, 9.3, 16.7),
            '.': (13.6, 10.1, 14.9, 10.1, 17.2, 10.1, 6.5),
            '+': (6.5, 10.1, 17.2, 10.1, 14.9, 10.1, 13.6),
            'A': (6.5, 8.0, 19.6, 19.4, 6.5, 16.1, 6.5),
            'T': (6.5, 8.0, 19.6, 19.4, 6.5, 16.1, 6.5),
            'B': (6.5, 16.1, 6.5, 19.4, 6.5, 8.0, 19.6),
            'N': (6.5, 16.1, 6.5, 19.4, 6.5, 8.0, 19.6),
            'C': (6.5, 8.0, 6.5, 19.4, 6.5, 16.1, 19.6),
            '*': (6.5, 8.0, 6.5, 19.4, 6.5, 16.1, 19.6),
            'D': (6.5, 8.0, 6.5, 19.4, 19.6, 16.1, 6.5),
            'E': (6.5, 8.0, 6.5, 19.4, 19.6, 16.1, 6.5),
        }

    def render(self, pdf, xpos, ypos, text):
        pdf.SetFillColor(0)

        code = (self.start + text + self.end).upper()
        for char in code:
            if char not in self.barChar.keys():
                raise RuntimeError('Caractér "%s" inválido para el código de barras Codabar: ' % char)

            seq = self.barChar[char]
            for bar in xrange(0, 7):
                lineWidth = self.width * seq[bar] / 6.5
                if bar % 2 == 0:
                    pdf.Rect(xpos, ypos, lineWidth, self.height, 'F')

                xpos += lineWidth

            xpos += self.width * 10.4 / 6.5
