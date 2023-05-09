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

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Drenagens(output)'),
                QgsProcessing.TypeVectorLine
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        
        # Get the input sources for lines and polygons
        lines_source = self.parameterAsSource(parameters, self.INPUT1, context)
        polygons_source = self.parameterAsSource(parameters, self.INPUT2, context)
        
        # Calculate the total progress based on the number of features in the lines source
        total = 100.0 / lines_source.featureCount() if lines_source.featureCount() else 0
        
        # Get the fields from the lines source and append a new field for the output indicating if the line is inside a polygon
        lines_fields = lines_source.fields()
        lines_fields.append(QgsField('dentro_de_poligono', QVariant.Bool))
        
        # Get the sink for the output data and prepare it with the fields from the lines source
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT,
                            context, lines_fields, lines_source.wkbType(), lines_source.sourceCrs())
        
        # Get the features from the lines and polygons sources
        line_features = lines_source.getFeatures()
        polygons_features = polygons_source.getFeatures()
        
        # Loop through each line feature
        for j, feat_line in enumerate(line_features):
            
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break
            
            # Create a new feature for the output with the same fields as the lines source
            # and set False for the output field by default
            new_feat = QgsFeature(lines_fields)
            new_feat['dentro_de_poligono'] = False
            for field in lines_source.fields():
                new_feat[field.name()] = feat_line[field.name()]
            new_feat.setGeometry(QgsGeometry.fromWkt(feat_line.geometry().asWkt()))
            
            # Get the geometry of the line feature and create a bounding box 
            # to use for the request to get polygons that intersect with it
            geom_line = feat_line.geometry()
            bbox = geom_line.boundingBox()
            request = QgsFeatureRequest(bbox)
            
            # Loop through each polygon feature that intersects with the bounding box of the line feature
            for feat_polyg in polygons_source.getFeatures(request):
                
                # Stop the algorithm if cancel button has been clicked
                if feedback.isCanceled():
                    break
                
                # Get the geometry of the polygon feature and create a geometry engine 
                # for the line feature to test if it is inside the polygon
                geom_polyg = feat_polyg.geometry()
                line_geom_engine = QgsGeometry.createGeometryEngine(geom_line.constGet())
                line_geom_engine.prepareGeometry()
                
                # If the line is inside the polygon, set the output field to True
                if line_geom_engine.within(geom_polyg.constGet()):
                    new_feat['dentro_de_poligono'] = True 
            
            # Add the new feature to the sink for the output data
            sink.addFeature(new_feat, QgsFeatureSink.FastInsert)

            # Update the progress bar
            feedback.setProgress(int(j * total))

        # Return the ID of the output layer
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
