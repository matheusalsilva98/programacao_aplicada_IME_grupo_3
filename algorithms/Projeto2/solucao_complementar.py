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
                       QgsFeatureSink,
                       QgsGeometry,
                       QgsField,
                       QgsFields,
                       QgsFeature,
                       QgsSpatialIndex,
                       QgsFeatureRequest,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)


class Projeto2SolucaoComplementar(QgsProcessingAlgorithm):
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

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT = 'OUTPUT'
    INPUT1 = 'INPUT1'
    INPUT2 = 'INPUT2'

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT1,
                self.tr('Drenagens'),
                [QgsProcessing.TypeVectorLine]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT2,
                self.tr('Massas de água'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Drenagens(output)'),
                QgsProcessing.TypeVectorLine
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        lines_source = self.parameterAsSource(parameters, self.INPUT1, context)
        polygons_source = self.parameterAsSource(parameters, self.INPUT2, context)

        # Compute the number of steps to display within the progress bar and
        # get features from source
        total = 100.0 / lines_source.featureCount() if lines_source.featureCount() else 0

        lines_fields = lines_source.fields()
        lines_fields.append(QgsField('dentro_de_poligono', QVariant.Bool))

        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT,
                            context, lines_fields, lines_source.wkbType(), lines_source.sourceCrs())

        line_features = lines_source.getFeatures()
        polygons_features = polygons_source.getFeatures()

        #polyg_source_id_dict = {}
        #polyg_source_spacial_idx = QgsSpatialIndex(polygons_source.getFeatures())

        for j, feat_line in enumerate(line_features):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break

            feat_line.setFields(lines_fields)
            feat_line['dentro_de_poligono'] = False
            
            new_feat = QgsFeature(lines_fields)
            
            for field in lines_fields:
                new_feat[field.name()] = feat_line[field.name()]

            new_feat.setGeometry(QgsGeometry.fromWkt(feat_line.geometry().asWkt()))

            geom_line = feat_line.geometry()
            bbox = geom_line.boundingBox()
            request = QgsFeatureRequest(bbox)

            for feat_polyg in polygons_source.getFeatures(request):
                # Stop the algorithm if cancel button has been clicked
                if feedback.isCanceled():
                    break

                #polyg_source_id_dict[feat_polyg.id()] = feat_polyg
                #polyg_source_spacial_idx.addFeature(feat_polyg)
                geom_polyg = feat_polyg.geometry()
                line_geom_engine = QgsGeometry.createGeometryEngine(geom_line.constGet())
                line_geom_engine.prepareGeometry()

                if line_geom_engine.within(geom_polyg.constGet()):
                    new_feat['dentro_de_poligono'] = True 

            sink.addFeature(new_feat, QgsFeatureSink.FastInsert)

            # Update the progress bar
            feedback.setProgress(int(j * total))


        return {self.OUTPUT: dest_id}



    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Solução Complementar do Projeto 2'

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
        return 'Projeto 2'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return Projeto2SolucaoComplementar()
