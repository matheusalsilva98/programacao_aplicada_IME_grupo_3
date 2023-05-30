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

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtCore import QVariant
from qgis.core import (QgsProcessing,
                       QgsProcessingUtils,
                       QgsFeatureSink,
                       QgsGeometry,
                       QgsField,
                       QgsWkbTypes,
                       QgsFields,
                       QgsProcessingParameterNumber,
                       QgsFeature,
                       QgsProcessingMultiStepFeedback,
                       QgsSpatialIndex,
                       QgsFeatureRequest,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)
import math


class Projeto3SolucaoComplementar(QgsProcessingAlgorithm):
    """
    Esse projeto tem por finalidade desrotacionar os edifícios colocados de input e colocar como atributo o quanto
    foi desrotacionado
    """

    # Definindo os parâmetros que serão utilizados no programa
    OUTPUT = 'OUTPUT'
    INPUT_EDIFICIOS = 'INPUT_EDIFICIOS'
    INPUT_RODOVIAS = 'INPUT_RODOVIAS'

    def initAlgorithm(self, config):
        """
        Iniciando o algoritmo
        """

        # Adicionando o parâmetro dos edifícios
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_EDIFICIOS,
                self.tr('Camada dos edícios'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        # Adicionando o parâmetro das rodovias:
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_RODOVIAS,
                self.tr('Camada das rodovias'),
                [QgsProcessing.TypeVectorLine]
            )
        )
        

        # Adicionando o parâmetro da camada de saída
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Onde o algoritmo será processado
        """

        # Para a camada dos edifícios
        edificios = self.parameterAsSource(parameters, self.INPUT_EDIFICIOS, context)

        # Para a camada das rodovias
        rodovia = self.parameterAsSource(parameters, self.INPUT_RODOVIAS, context)

        # Criando o campo de saída da nossa feição que será apenas o quanto o edifício foi rotacionado para ficar perpendicular
        # em relação a parte da feição rodovia mais próxima:
        fields = QgsFields()
        fields.append(QgsField("Rotação", QVariant.Double))

        # Adicionando a camada de saída na variável sink
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT,
                context, fields, QgsWkbTypes.Point, edificios.sourceCrs())
        
        # Adicionando o multistepfeedback para poder mostrar na tela o carregamento
        multiStepFeedback = QgsProcessingMultiStepFeedback(7, feedback)
        multiStepFeedback.setCurrentStep(0)
        multiStepFeedback.setProgressText(self.tr("Verificando estrtutura"))
        
        
        # Inicialmente criando um dicionário tanto para as features dos edifícios quanto para as features das rodovias, 
        # onde iremos associar o id (chave) com a feature (valor)
        dictEdificios = {}
        dictRodovias = {}

        # Também criando o índice espacial
        ediIndiceSpacial = QgsSpatialIndex()
        rodIndiceSpacial = QgsSpatialIndex()

        # Iterando em cada dicionário e em cada índice espacial para acrescentar a feição com o seu índice
        for featEdi in edificios.getFeatures():
            dictEdificios[featEdi.id()] = featEdi
            ediIndiceSpacial.addFeature(featEdi)

        for featRodo in rodovia.getFeatures():
            dictRodovias[featRodo.id()] = featRodo
            rodIndiceSpacial.addFeature(featRodo)
        
        # Criando o dicionário para colocar o id (chave) e um dicionário como valor, onde o dicionário terá a chave o id
        edifRodo = {}

        for current, featE in enumerate(edificios.getFeatures()):
            # Caso o usuário deseje parar
            if feedback.isCanceled():
                break
            
            if featE.id() not in edifRodo:
                edifRodo[featE.id()] = {}
            
            for current1, featR in enumerate(rodovia.getFeatures()):
                # Caso o usuário deseje parar
                if feedback.isCanceled():
                    break

                # Calculando a distância das duas features, temos:
                dist = featE.geometry().distance(featR.geometry())

                # Acrescentando no dicionário, para o índice da feição do edifício
                edifRodo[featE.id()][featR.id()] = dist
                # Então para cada índice do edifício, teremos como valor um dicionário onde, nesse dicionário, teremos
                # a chave o índice da feature da rodovia e como valor a distância

        # Contando os casos temos:
        multiStepFeedback.setCurrentStep(1)

        # Criando um dicionário para armazenar o índice do edifício e qual o índice da rodovia que está mais próxima
        dictEdiProxRod = {}
        
        # Iremos percorrer agora esse dicionário incrementado e verificar qual é a menor distância e o id 
        # da feature da rodovia

        for current2, id in enumerate(list(edifRodo.keys())):
            # Caso o usuário deseja cancelar o processo:
            if feedback.isCanceled():
                break

            # Atribuindo um valor alto para que se mude com o percorrer do dicionário
            menor_dist = 9999

            # Vamos percorrer o dicionário com os índices da lista da iteração e encontrar qual é o índice 
            # da feature da rodovia que possui a menor distância do atual índice da feature do edifício da iteração
            for current3, (idR, distancia) in enumerate(list(edifRodo[id].items())):
                # Caso o usuário deseje cancelar o processo:
                if feedback.isCanceled():
                    break

                # Atribuindo um valor grande para a menor distância, que será substituída pelos valores que estão
                # presentes no dicionário
                if distancia < menor_dist:
                    menor_dist = distancia
                    menor_id = idR
            dictEdiProxRod[id] = menor_id

            # Outro multistep
            multiStepFeedback.setCurrentStep(2)

        # Outro multistep
        multiStepFeedback.setCurrentStep(3)

        # Dessa forma, podemos calcular então o vetor perpendicular à rodovia e que passa no centro do edifício
        # Criando um dicionário que irá adicionar o índice do edifício e esse vetor perpendicular associado como valor
        ediVetorPerp = {}
        
        # Percorrendo o dicionário criado que armazena o índice do edificio (chave) e o índice da feature rodovia (valor)
        # mais próximo:
        for current4, idEdi in enumerate(list(dictEdiProxRod.keys())):
            # Caso o usuário deseje cancelar o processo:
            if feedback.isCanceled():
                break

            # A geometria da rodovia pode ser feita acessando o dicionário criado para armazenar as rodovias
            gRodovia = dictRodovias[dictEdiProxRod[idEdi]].geometry()
            
            # A geometria do edifício pode ser feito acessando o dicionário criado para armazenar os edifícios
            gEdificio = dictEdificios[idEdi].geometry()
            
            # Coletando as coordenadas iniciais e finais da feature rodovia e as coordenadas do ponto que 
            # representa o edifício:
            xInicRodDir = float(f"{gRodovia}".split("(")[1].split(")")[0].split(", ")[0].split(" ")[0])          
            yInicRodDir = float(f"{gRodovia}".split("(")[1].split(")")[0].split(", ")[0].split(" ")[1])          
            xFinRodDir = float(f"{gRodovia}".split("(")[1].split(")")[0].split(", ")[1].split(" ")[0])
            yFinRodDir = float(f"{gRodovia}".split("(")[1].split(")")[0].split(", ")[1].split(" ")[1])

            # Para a coordenada do edifício, temos:
            xEdiDir = float(f"{gEdificio}".split("(")[1].split(")")[0].split(" ")[0])
            yEdiDir = float(f"{gEdificio}".split("(")[1].split(")")[0].split(" ")[1])

            # Encontrando a equação da reta da linestring, temos:
            # Coeficiente angular da linestring, por meio das coordenadas finais e iniciais:
            coefAng = (yFinRodDir - yInicRodDir) / (xFinRodDir - xInicRodDir)

            coefAngPerp = -(coefAng ** (-1)) # Coeficiente angular da reta que está na perpendicular da linestring da menor distância
            # direção que será movida o edifício.

            # Encontrando o ponto que quando se traça a perpendicular pelo edifício, corta a rodovia, temos:
            # Chamando os pontos da coordenada de xOrt e yOrt:
            xOrt = ((yEdiDir - yFinRodDir) - (coefAngPerp * xEdiDir) + (coefAng * xFinRodDir)) / (coefAng - coefAngPerp)
            yOrt = yEdiDir + coefAngPerp * (xOrt - xEdiDir)

            # Encontrando o vetor diretor que deverá ser feito o deslocamento, dado por:
            xVetorPerp = (xEdiDir - xOrt)
            yVetorPerp = (yEdiDir - yOrt)

            # Logo o vetor perpendicular é dado por:
            perp = (xVetorPerp, yVetorPerp)

            # Acrescendo ao dicionário criado para armazenar o índice e o vetor que é dado:
            ediVetorPerp[idEdi] = perp
        
        # Outro passo do multistepfeedback
        multiStepFeedback.setCurrentStep(4)

        # Iterando sobre esse último dicionário, agora para encontrar o ângulo que é feito entre o vetor perpendicular associado ao edifício 
        # e o vetor (0, 1) que representa o vetor vertical em relação ao qual é medido o ângulo, a nossa chave portanto do dicionário é
        # o id do edifício e o valor é o ângulo

        # Dicionário que será o id do edifício como chave e o valor como o ângulo
        dictEdiAng = {}

        # Iteração
        for current5, idP in enumerate(list(ediVetorPerp.keys())):
            # Caso o usuário deseje cancelar o processo:
            if feedback.isCanceled():
                break

            # Acessando os valores do dicionário ediVetorPerp:
            # Podemos calcular o ângulo por meio da igualdade do produto interno de dois vetores ser igual ao produto do cosseno entre eles
            # multiplicado pelo módulo desses vetores
            vetorPerp = ediVetorPerp[idP] # O vetor é uma tupla

            # Vamos fazer para simplificar que o ângulo de referência será dado pelo vetor vertical (0, 1)
            vetorVert = (0, 1) # Seu módulo é igual a 1

            # O cosseno do ângulo é dado por:
            cossenoAng = (vetorPerp[1] * vetorVert[1]) / ((vetorPerp[0] ** 2 + vetorPerp[1] ** 2) ** (1/2))

            # Extraindo esse ângulo, temos:
            arccosAng = math.acos(cossenoAng)

            # Transformando para graus, temos
            grausAng = (arccosAng * 180) / math.pi

            # Acrescentando no dicionário o índice e o valor do ângulo:
            dictEdiAng[idP] = grausAng
        
        # Outro passo do multistepfeedback
        multiStepFeedback.setCurrentStep(5)

        # Iterando sobre os edifícios para rotacioná-los de acordo com o ângulo calculado
        for current6, idU in enumerate(list(dictEdiAng.keys())):
            # Criando a feição de saída com o campo dos atributos que vai conter o ângulo necessário
            featSaida = QgsFeature(fields)

            # Adicionando em cada iteração o valor do atributo
            featSaida["Rotação"] = dictEdiAng[idU]

            featSaida.setGeometry(dictEdificios[idU].geometry())

            sink.addFeature(featSaida, QgsFeatureSink.FastInsert)
        
        # Outro passo do multistepfeedback
        multiStepFeedback.setCurrentStep(6)

        self.dest_id=dest_id

        # Retorna a nossa camada de saída
        return {self.OUTPUT: dest_id}
    
    def postProcessAlgorithm(self, context, feedback):
        output = QgsProcessingUtils.mapLayerFromString(self.dest_id, context)
        path='C:\\Users\\mathe\\OneDrive\\Área de Trabalho\\Trabalhos\\ProgAplicada\\Projeto3\\dados\\edificacoes.qml'
        output.loadNamedStyle(path)
        output.triggerRepaint()
        return {self.OUTPUT: self.dest_id}

    def name(self):
        """
        Retorna o nome do projeto
        """
        return 'Solução Complementar do Projeto 3'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
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
        return 'Projeto 3'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return Projeto3SolucaoComplementar()