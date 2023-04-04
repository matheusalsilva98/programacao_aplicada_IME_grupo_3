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

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingAlgorithm,
                       QgsWkbTypes,
                       QgsFeature,
                       QgsProcessingParameterMultipleLayers,
                       QgsGeometry,
                       QgsFields,
                       QgsVectorLayer,
                       QgsPointXY,
                       QgsField,
                       QgsProcessingException,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)
import numpy as np

class Projeto1SolucaoComplementar(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Declarando os nossos parâmetros que utilizaremos para a resolução da questão.

    OUTPUT = 'OUTPUT'
    INPUT = 'INPUT'

    def initAlgorithm(self, config):
        """
        Definindo os parâmetros de entrada (INPUT).
        """

        # Adicionando o parâmetro para processar multiplas camadas como entrada (INPUT).

        self.addParameter(
            QgsProcessingParameterMultipleLayers(
                self.INPUT,
                self.tr('Input layer'),
                layerType = QgsProcessing.TypeRaster
            )
        )

        # Adicionando o parâmetro de saída (OUTPUT).

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Teremos o efetivo desenvolvimento do algoritmo nessa etapa, resultando no
        nosso produto final.
        """

        # Criando a variável raster para receber uma lista de rasters de entrada (INPUT).
        listaRaster = self.parameterAsLayerList(parameters, self.INPUT, context)

        # Criando os atributos necessários da camada de saída chamando de fields, temos:

        fields = QgsFields()
        fields.append(QgsField("raster1", QVariant.String))
        fields.append(QgsField("raster2", QVariant.String))
        fields.append(QgsField("erro", QVariant.Double))

        # Criando a variável que irá receber os resultados obtidos a partir da comparação entre as camadas Raster.
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT,
                context, fields, QgsWkbTypes.Polygon, listaRaster[0].crs())
        

        # É criada a variável total para se avaliar o progresso do algoritmo.
        total = 100.0 / len(listaRaster) if len(listaRaster) else 0

        for current, i in enumerate(range(len(listaRaster))):
            # Caso o usuário deseje cancelar o processo, poderá.
            if feedback.isCanceled():
                break
            
            for current2, j in enumerate(range(len(listaRaster))):
                
                # Criando uma lista dos erros para conseguirmos calcular o EMQz a posteriori.
                lista_erros = []

                if i != j:
                    
                    # Armazenando em variáveis os quadriláteros que envolvem as imagens da iteração.
                    quadRasterI = listaRaster[i].extent()
                    quadRasterJ = listaRaster[j].extent()

                    # Criando 4 variáveis para cada quadrilátero que irá representar os vértices, teremos:
                    pontoI1 = f"{quadRasterI.xMinimum()} {quadRasterI.yMinimum()}"
                    pontoI2 = f"{quadRasterI.xMinimum()} {quadRasterI.yMaximum()}"
                    pontoI3 = f"{quadRasterI.xMaximum()} {quadRasterI.yMaximum()}"
                    pontoI4 = f"{quadRasterI.xMaximum()} {quadRasterI.yMinimum()}"

                    pontoJ1 = f"{quadRasterJ.xMinimum()} {quadRasterJ.yMinimum()}"
                    pontoJ2 = f"{quadRasterJ.xMinimum()} {quadRasterJ.yMaximum()}"
                    pontoJ3 = f"{quadRasterJ.xMaximum()} {quadRasterJ.yMaximum()}"
                    pontoJ4 = f"{quadRasterJ.xMaximum()} {quadRasterJ.yMinimum()}"

                    # Criando as variáveis quadFeatureI e quadFeatureJ para reservar as features 
                    # criadas com os vértices.
                    quadFeatureI = QgsFeature()
                    quadFeatureJ = QgsFeature()

                    # Ajeitando a geometria com o setGeometry() para conseguir adicionar os vértices.
                    quadFeatureI.setGeometry(QgsGeometry.fromWkt(f"POLYGON (({pontoI1}, {pontoI2}, {pontoI3}, {pontoI4}, {pontoI1}))"))
                    quadFeatureJ.setGeometry(QgsGeometry.fromWkt(f"POLYGON (({pontoJ1}, {pontoJ2}, {pontoJ3}, {pontoJ4}, {pontoJ1}))"))

                    # Verificando se há intersecção das duas geometrias.
                    if (quadFeatureI.geometry()).overlaps(quadFeatureJ.geometry()):
                        # Com o método 'intersection' resulta a geometria da interseção e armazenando na variável
                        # chamada de quadInterseccao.
                        quadInterseccao = (quadFeatureI.geometry()).intersection(quadFeatureJ.geometry())

                        # Realizando o Bounding Box da intersecção, podemos utilizar o método boundingBox() na
                        # Variável quadInterseccao.

                        bbox = quadInterseccao.boundingBox()

                        # Gerando as coordenadas das abcissas do bounding box, colocando em uma lista, em que construímos
                        # partindo do x mínimo até o x máximo do bounding box, realizando o mesmo com o y, além disso, a quantidade de elementos que será dado é o inteiro da diferença das abcissas.

                        coordX = np.linspace(bbox.xMinimum(), bbox.xMaximum(), num=int((bbox.xMaximum() - bbox.xMinimum())//200))

                        # Realizando o mesmo para o y, teremos:

                        coordY = np.linspace(bbox.yMinimum(), bbox.yMaximum(), num=int((bbox.yMaximum() - bbox.yMinimum())//200))

                        # Criando a variável que irá ser responsável por receber as coordenadas de todos os pontos que estão no bounding box, variando o x do mínimo para o máximo além do y do mínimo para o máximo.

                        tuplasCoordenadas = []

                        # Para adiconar na lista de coordenadas podemos fazer dois for, para percorrer todos os valores possíveis da coordenada x, com todos os possíveis valores da coordenada y.

                        for k in range(len(coordX)):
                            for l in range(len(coordY)):
                                tuplasCoordenadas.append(f"({coordX[k]} {coordY[l]})")

                        # Iterando sobre todas as coordenadas dos pontos presentes na intersecção dos rasters.

                        for coordenada in tuplasCoordenadas:
                            
                            ponto = QgsFeature()
                            ponto.setGeometry(QgsGeometry.fromWkt(f"POINT {coordenada}"))

                            if (ponto.geometry()).within(quadInterseccao):
                                
                                # Criando a feature chamada de flagFeature que irá receber esses pontos que estão na
                                # intersecção dos pontos e do polígono, que será o responsável por pegar o componen-
                                # te z de cada raster e irá anaalisar o ez_i, além do EMQz entre as imagens no final.
                                flagFeature = QgsFeature(fields)

                                flagFeature.setGeometry(QgsGeometry.fromWkt(quadInterseccao.asWkt()))

                                # Pegaremos então para calcular o erro do z, como o primeiro raster analisado como sendo
                                # o que temos por verdade, e o segundo raster com o z teste.
                                z_t = listaRaster[j].dataProvider().sample(QgsPointXY(ponto.geometry().asPoint()), 1)[0]
                                z_r = listaRaster[i].dataProvider().sample(QgsPointXY(ponto.geometry().asPoint()), 1)[0]

                                # Dessa forma, vamos preencher os atributos da feição feita.
                                flagFeature["raster1"] = f"{listaRaster[i].name()}"
                                flagFeature["raster2"] = f"{listaRaster[j].name()}"
                                flagFeature["erro"] = (z_t - z_r)

                                # Adicionando o elemento também na lista criada chamada de lista_erros.
                                lista_erros.append(flagFeature["erro"])


                                # Adiciona a feature na camada de saída.
                                sink.addFeature(flagFeature, QgsFeatureSink.FastInsert)
                                
                        # Pomemos agora, depois de adquirir todos os pontos na lista dos erros, chamada de lista_erros, podemos calcular o EMQz e 
                        # definir para qual PEC encaixa.
                        EMQz = 0
                        for ezi in lista_erros:
                            EMQz += ezi ** 2
                        EMQz = (EMQz/len(lista_erros)) ** (1/2)

                        # Informando na tabela do Log o valor do EMQz para os erros do ponto no tiff do raster e nos pontos de controle.
                        feedback.pushInfo(f"O valor da acurácia posicional relativa entre {listaRaster[i].name()} e {listaRaster[j].name()} altimétrica EMQz = {EMQz}\n")

                    # Criando um erro caso não haja intersecção entre as camadas.
                    else:
                        raise QgsProcessingException("Não há intersecção entre os Rasters.")

            # Progresso da barra na interface com o usuário.
            feedback.setProgress(int(current * total))

        # Retorno do processo realizado pelo algoritmo.
        return {self.OUTPUT: dest_id}

    def name(self):
        """
        Retorna o nome do algoritmo traduzido.
        """
        return 'Solução Complementar do Projeto 1'

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
        return 'Projeto 1'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return Projeto1SolucaoComplementar()
