# -*- coding: iso-8859-1 -*-
import math

# implementaci�n ejemplo


def etiquetas(form, params):


    # variables:
    lalala = 'mariano'
    titulo = "Etiquetas Noveduc"
    items = ['nombre-%s' % i for i in xrange(100)]

    # calculos:
    form.bodies['hoja1'].elements['etiqueta'].elements['direccion'].text = "'nad��������'"
    form.pages = math.ceil(len(items) / float(form.bodies['hoja1'].elements['etiqueta'].rows * form.bodies['hoja1'].elements['etiqueta'].cols))

    return locals()
