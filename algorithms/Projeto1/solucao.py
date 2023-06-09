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
                       QgsWkbTypes,
                       QgsFields,
                       QgsField,
                       QgsFeature,
                       QgsProcessingParameterRasterLayer,
                       QgsGeometry,
                       QgsPointXY,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)


class Projeto1Solucao(QgsProcessingAlgorithm):
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
    PONTOS_CONTROLE = 'PONTOS_CONTROLE'
    INPUT = 'INPUT'

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # Adicionando o parâmetro de entrada como sendo do tipo Raster (INPUT).
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT,
                self.tr('Input layer'),
                [QgsProcessing.TypeRaster]
            )
        )
        
        # Adicionando o parâmetro que receberá os pontos de controle para comparativo com os pontos da imagem.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
            self.PONTOS_CONTROLE,
            self.tr('Pontos de controle'),
            [QgsProcessing.TypeVectorPoint]
            )
        )

        # Adicionando o parâmetro de saída (OUTPUT)
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Declarando a variável raster que receberá a entrada.
        raster = self.parameterAsRasterLayer(parameters, self.INPUT, context)

        # Declarando a variável pontos_controle que recebrá a camada dos pontos de controle.
        pontos_controle = self.parameterAsSource(parameters, self.PONTOS_CONTROLE, context)

        # Criando o atributo flag para as features de saída, do tipo númerico double (decimal).
        fields = QgsFields()
        fields.append(QgsField("erro", QVariant.Double))

        # Declarando a variável e o id que receberão a camada de saída.
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT,
                context, fields, QgsWkbTypes.Polygon, raster.crs())
        
        # Criando a variável retanguloRaster para receber o método extent na camada raster inserida como input.
        retanguloRaster = raster.extent()

        # Criando 4 variáveis, as quais vão receber os vértices adquiridos a partir do extent do raster.
        ponto1 = f'{retanguloRaster.xMinimum()} {retanguloRaster.yMinimum()}'
        ponto2 = f'{retanguloRaster.xMinimum()} {retanguloRaster.yMaximum()}'
        ponto3 = f'{retanguloRaster.xMaximum()} {retanguloRaster.yMaximum()}'
        ponto4 = f'{retanguloRaster.xMaximum()} {retanguloRaster.yMinimum()}'
        
        # Criando a variável retanguloFeatureRaster para receber a feature com as limitações do raster de entrada, que foram
        # obtido a partir da variável retanguloRaster.
        retanguloFeatureRaster = QgsFeature()
        # Incrementando as coordendas do boundingBox que se consegue a partir da variável retanguloRaster, podemos colocar geometria 
        # na nossa feature criada.
        retanguloFeatureRaster.setGeometry(QgsGeometry.fromWkt(f"POLYGON (({ponto1}, {ponto2}, {ponto3}, {ponto4}, {ponto1}))"))
        

        # Criando a variável total que medirá o progresso.
        total = 100.0 / pontos_controle.featureCount() if pontos_controle.featureCount() else 0
        # Pegando todos os pontos presentes na camada pontos de controle inserida a partir do csv.
        features = pontos_controle.getFeatures()

        # Criando uma variável que tem por finalidade armazenar os valores dos erros,  erros = z_t - z_r.
        lista_erros = []
#########################################################################################################
        for current, feature in enumerate(features):
            # Caso o usuário desejar, poderá cancelar o processo do código.
            if feedback.isCanceled():
                break
                
            # Analisando quais pontos na camada do pontos de controle estão dentro do retanguloFeatureRaster.
            if (feature.geometry()).within(retanguloFeatureRaster.geometry()):
                
                # Depois de analisado se cada ponto está dentro do retanguloFeatureRaster, que é o boundingBox do raster de entrada,
                # vamos criar as feições que serão adicionadas na camada de saída, com o atributo fields criado anteriormente.
                flagFeature = QgsFeature(fields)


                # Para completar o atributo dos pontos gerados, precisamos comparar o valor do z (altura) presente no arquivo tiff do raster
                # e do z que está presente no csv.
                # Inicialmente adquirindo o z presente no arquivo tiff do raster e armazenando na variável z_t, temos:
                z_t = raster.dataProvider().sample(QgsPointXY(feature.geometry().asPoint()), 1)[0]

                # Agora adquirindo o z presente na tabela de atributos da feature presente no pontos de controle, na iteração dada.
                z_r = feature["z"]

                # O atributo erro da feature que vai ser inserida na camada de saída será dada por : zt - zr
                flagFeature["erro"] = z_t - z_r


                # Arrumando a geometria para o ponto com as coordenadas dos pontos de controle.
                flagFeature.setGeometry(QgsGeometry.fromWkt(feature.geometry().asWkt()).buffer(180 * abs((z_t - z_r)), -1))

                
                # raioProporcionalAoErro = flagFeature.geometry().buffer(50, 25)
                # flagFeature.setGeometry(raioProporcionalAoErro)

                # Adicionando o elemento também na lista criada chamada de lista_erros.
                lista_erros.append(flagFeature["erro"])

                # Adicionando a feição gerada na variável de saída, que respeita as condições impostas.
                sink.addFeature(flagFeature, QgsFeatureSink.FastInsert)

            # Barra de progresso que aparece na interface do usuário.
            feedback.setProgress(int(current * total))
        
        # Podemos agora, depois de adquirir todos os pontos na lista dos erros, chamada de lista_erros, podemos calcular o EMQz e 
        # definir para qual PEC encaixa.
        EMQz = 0
        for ezi in lista_erros:
            EMQz += ezi ** 2
        EMQz = (EMQz/len(lista_erros)) ** (1/2)

        # Informando na tabela do Log o valor do EMQz para os erros do ponto no tiff do raster e nos pontos de controle.
        feedback.pushInfo(f"O valor da acurácia posicional absoluta altimétrica EMQz = {EMQz}\n")

        # Por fim, determinando em qual PEC se encaixa de acordo com os valores de EP fornecidos na tabela para cartas de 1:25000, teremos:
        if (EMQz < 1.67):
            Pec = "A" # Para o caso de ser menor que 1.67 o valor de EMQz.
        elif (EMQz < 3.33):
            Pec = "B" # Para o caso de ser maior ou igual a 1.67 ou menor que 3.33 o valor de EMQz.
        elif (EMQz < 4.0):
            Pec = "C" # Para o caso de ser maior ou igual a 3.33 ou menor que 4.0 o valor de EMQz.
        elif (EMQz < 5.0):
            Pec = "D" # Para o caso de ser maior ou igual a 4.0 e menor que 5.0 o valor de EMQz.
        else:
            Pec = "Não Conforme" # Para casos em que o EMQz possui valores maiores que 5.0 de EP.

        # Informando na tabela do Log o PEC associado de acordo com o EMQz calculado.
        feedback.pushInfo(f"A acurácia posicional absoluta altimétrica tabelada PEC = {Pec}\n")

        # O resultado do processo, em que a função do processAlgorithm irá retornar.
        return {self.OUTPUT: dest_id}

    def name(self):
        """
        Solução do Projeto1, que possui como objetivo calcular a acurácia posicional
        absoluta altimétrica (EMQz e PEC) de 6 modelos digitais de superfície. Devemos ter
        uma camada de entrada que será um raster, a camada comparativa será uma camada
        do tipo ponto.
        """
        return 'Solução do Projeto 1'

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
        return 'Projeto 1'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return Projeto1Solucao()