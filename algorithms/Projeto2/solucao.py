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
"""

__author__ = 'Grupo 3'
__date__ = '2023-03-20'
__copyright__ = '(C) 2023 by Grupo 3'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import math
import concurrent.futures
import os

from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsFeature, QgsFeatureRequest, QgsField, QgsFields,
                       QgsGeometry, QgsGeometryUtils, QgsPoint, QgsPointXY,
                       QgsProcessing, QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterNumber, QgsProject, QgsWkbTypes, 
                       QgsProcessingMultiStepFeedback, QgsProcessingAlgorithm)



class Projeto2Solucao(QgsProcessingAlgorithm):
    FLAGS = 'FLAGS'
    INPUT = 'INPUT'

#Inicia o algoritmo

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input'),
                [
                    QgsProcessing.TypeVectorLine,
                ]
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.FLAGS,
                self.tr('{0} Flags').format(self.displayName())
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        #Recebendo as linhas como vetores

        lines = self.parameterAsVectorLayer(
            parameters,
            'INPUT',
            context
        )
        self.prepareFlagSink(parameters, lines, QgsWkbTypes.Point, context)

        # Diicionario de pontos de entrada e saida
        DicionarioEntradaSaida = {}


        # Iteracao entre as linhas do dicionario

        lineCount = lines.featureCount()
        if lineCount == 0:
            return {self.FLAGS: self.flag_id}
        multiStepFeedback = QgsProcessingMultiStepFeedback(2, feedback)
        multiStepFeedback.setCurrentStep(0)
        multiStepFeedback.setProgressText(self.tr("Verificando estrtutura"))
        stepSize = 100/lineCount

        for current, line in enumerate(lines.getFeatures()):
            if multiStepFeedback.isCanceled():
                break
            geom = list(line.geometry().vertices())
            if len(geom) == 0:
                continue
            first_vertex = geom[0]
            last_vertex = geom[-1]

            if first_vertex.asWkt() not in DicionarioEntradaSaida:
                DicionarioEntradaSaida[first_vertex.asWkt()] = { "entrada": 0, "saida": 0}

            if last_vertex.asWkt() not in DicionarioEntradaSaida:
                DicionarioEntradaSaida[last_vertex.asWkt()] = { "entrada": 0, "saida": 0}
            
            DicionarioEntradaSaida[first_vertex.asWkt()]["saida"] += 1
            DicionarioEntradaSaida[last_vertex.asWkt()]["entrada"] += 1
            multiStepFeedback.setProgress(current * stepSize)
        
        multiStepFeedback.setCurrentStep(1)
        multiStepFeedback.setProgressText(self.tr("Raising flags..."))
        stepSize = 100/len(DicionarioEntradaSaida)
        #Iteracao no dicionario


        for current, (pointStr, entradaesaida) in enumerate(DicionarioEntradaSaida.items()):
            if multiStepFeedback.isCanceled():
                break
            errorMsg = self.Errolocal(entradaesaida)
            if errorMsg != '':
                self.flagFeature(
                    flagGeom= QgsGeometry.fromWkt(pointStr),
                    flagText=self.tr(errorMsg)
                )
            multiStepFeedback.setProgress(current * stepSize)

        return {self.FLAGS: self.flag_id}

    def Errolocal(self, entradaesaida):
        entrada = entradaesaida["entrada"]
        saida = entradaesaida["saida"]
        total = entrada + saida

        if total == 1:
            return ''
        if total >= 4:
            return '4 ou mais linhas conectadas no ponto'
        
        if (entrada == 0):
            return 'Há apenas saídas'

        if (saida == 0):
            return 'Há apenas entradas'

        return ''

    def name(self):
        """
        Solução do Projeto 2
        """
        return 'Solução do Projeto 2'

    def displayName(self):
        """
        Retorna o nome do algoritmo traduzido.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Projeto 2'


    def tr(self, string):
        return QCoreApplication.translate('Projeto2Solucao', string)

    def createInstance(self):
        return Projeto2Solucao()
