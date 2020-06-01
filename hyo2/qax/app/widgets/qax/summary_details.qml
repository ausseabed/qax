import QtQuick 2.12
import QtQuick.Window 2.2
import QtLocation 5.12
import QtPositioning 5.12
import QtQuick.Controls 1.4
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.3
import Qt.labs.qmlmodels 1.0

Pane {
  padding: 0
  id: mainPane

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
            spacing: 14

            ColumnLayout {
              Text {
                text: manager.name
                font.bold: true
              }
              Text {
                text: "Version: " + manager.version
              }
              Text {
                text: "Data level: " + manager.data_level
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
          anchors.fill: parent
          onClicked: {
            manager.selected_properties = {};
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
                anchors.fill: parent
                onClicked: {
                  manager.selected_properties = markerProperties
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


    TableView {
      id: idtable
      Layout.fillWidth: true
      model: manager.selected_properties_table

      TableViewColumn {
        role: "key"
        title: "key"
        width: idtable.width / 2
      }
      TableViewColumn {
        role: "value"
        title: "value"
        width: idtable.width / 2
        delegate: Text {
          font.bold: {
            var item = manager.selected_properties_table[styleData.row];
            if (item) {
              return item.changed;
            } else {
              return false;
            }
          }
          text: styleData.value
        }
      }
    }


  }


}
