import QtQuick 2.12
import QtQuick.Window 2.2
import QtLocation 5.12
import QtPositioning 5.12
import QtQuick.Controls 1.4
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.3

Pane {
  padding: 0
  // background: Rectangle {
  //   color: "#eeeeee"
  //   // color: "transparent"
  // }

  Plugin {
    id: mapPlugin
    name: "osm"
  }

  SplitView {
    orientation: Qt.Horizontal
    anchors.fill: parent
    id: mainLayout

    Pane {
      id: svitem
      width: mainLayout.width / 2
      Layout.maximumWidth: mainLayout.width / 2
      Layout.fillHeight: true

      ScrollView {
        height: svitem.height - svitem.padding * 2
        width: svitem.width - svitem.padding * 2
        id: detailsScrollView
        ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
        ScrollBar.vertical.policy: ScrollBar.AlwaysOn
        clip: true
        contentWidth: -1

        Pane {
          id: mypane
          width: detailsScrollView.width

          ColumnLayout {
            width: mypane.width - mypane.padding * 2

            Text {
              text: manager.name
              font.bold: true
              Layout.fillWidth: true
            }


            Text {
              text: "Input files:"
              color: "grey"
              Layout.fillWidth: true
            }

            Repeater {
              model: manager.input_files
              Text {
                text: modelData
                wrapMode: Text.Wrap
                Layout.fillWidth: true
              }
            }

            Text {
              text: "Messages:"
              color: "grey"
              Layout.fillWidth: true
            }

            Repeater {
              model: manager.messages
              Text {
                text: modelData
                wrapMode: Text.Wrap
                Layout.fillWidth: true
              }
            }

          }
        }

      }
    }






    ColumnLayout {
      Layout.fillWidth: true
      Layout.fillHeight: true


      Map {
        id: map
        plugin: mapPlugin
        Layout.fillWidth: true
        Layout.fillHeight: true
        zoomLevel: (maximumZoomLevel - minimumZoomLevel)*0.1
        copyrightsVisible: false
        center {
          // The Qt Company in Oslo
          latitude: -28.4924595
          longitude: 134.0719485
        }
        property Rectangle lastSelected: null

        MouseArea {
          drag.target: parent
          anchors.fill: parent
          onClicked: {
            if (map.lastSelected) {
              map.lastSelected.state = "";
            }
          }
        }

        MapItemView {
          model: markersModel
          delegate: MapQuickItem{
            anchorPoint: Qt.point(markerSize/2, markerSize/2)
            coordinate: QtPositioning.coordinate(markerPosition.x, markerPosition.y)
            zoomLevel: 0
            sourceItem: Rectangle{
              id: markerRect
              width:  markerSize
              height: markerSize
              radius: markerSize/2
              border.color: "white"
              color: markerColor
              border.width: 1

              MouseArea {
                drag.target: parent
                anchors.fill: parent
                onClicked: {
                  if (map.lastSelected) {
                    map.lastSelected.state = "";
                  }
                  markerRect.state == 'selected' ? markerRect.state = "" : markerRect.state = 'selected';
                  map.lastSelected = markerRect
                }
              }

              states: [
                State {
                  name: "selected"
                  PropertyChanges { target: markerRect; border.width: 4 }
                }
              ]
            }
          }
        }

        MapItemView {
          model: linesModel
          delegate: MapPolyline{
            path: lineCoordinates
            line.width: lineWidth
            line.color: lineColor
          }
        }

        // MapPolyline {
        //   line.width: 3
        //   line.color: 'green'
        //   path: [
        //     { latitude: -27, longitude: 153.0 },
        //     { latitude: -27, longitude: 154.1 },
        //     { latitude: -28, longitude: 153.5 },
        //     { latitude: -29, longitude: 153.5 }
        //   ]
        // }

        // Repeater {
        //   model: manager.map_lines
        //   MapPolyline {
        //     line.width: 3
        //     line.color: modelData.color
        //     path: modelData.points
        //   }
        // }

        // MapQuickItem {
        //   anchorPoint: Qt.point(2.5, 2.5)
        //   coordinate: QtPositioning.coordinate(-28, 153.5)
        //   // zoomLevel: 0
        //   sourceItem: Rectangle {
        //     width:  20
        //     height: 20
        //     radius: 10
        //     border.color: "white"
        //     color: "red"
        //     border.width: 1
        //   }
        // }

        //
        // Repeater {
        //   model: manager.map_points
        //   MapQuickItem{
        //     anchorPoint: Qt.point(modelData.size/2, modelData.size/2)
        //     coordinate: QtPositioning.coordinate(modelData.coordinate.latitude, modelData.coordinate.longitude)
        //     // zoomLevel: 0
        //     sourceItem: Rectangle {
        //       width:  modelData.size
        //       height: modelData.size
        //       radius: modelData.size / 2
        //       border.color: "white"
        //       color: modelData.color
        //       border.width: 1
        //     }
        //   }
        // }

        Button {
            id: fitButton
            text: "Fit"
            anchors.margins: 10
            anchors.bottom: parent.bottom
            anchors.top: scale.top
            anchors.right: parent.right
            onClicked: {
                map.fitViewportToMapItems()
            }
        }

        Slider {
          id: zoomSlider;
          z: map.z + 3
          from: map.minimumZoomLevel;
          to: map.maximumZoomLevel;
          anchors.margins: 10
          anchors.bottom: scale.top
          anchors.top: parent.top
          anchors.right: parent.right
          orientation : Qt.Vertical
          value: map.zoomLevel
          onValueChanged: {
            if (value >= 0)
              map.zoomLevel = value
          }
        }
      }
    }



  }





}
