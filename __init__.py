# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ProgramacaoAplicadaGrupo3
                                 A QGIS plugin
 Solução do Grupo 3
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-03-20
        copyright            : (C) 2023 by Grupo 3
        email                : matheus.silva@ime.eb.br
                               samuel.melo@ime.eb.br
                               reginaldo.filho@ime.eb.br
                               romeu.peris@ime.eb.br
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

__author__ = 'Grupo 3'
__date__ = '2023-03-20'
__copyright__ = '(C) 2023 by Grupo 3'


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load ProgramacaoAplicadaGrupo3 class from file ProgramacaoAplicadaGrupo3.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .programacao_aplicada_grupo_3 import ProgramacaoAplicadaGrupo3Plugin
    return ProgramacaoAplicadaGrupo3Plugin()
