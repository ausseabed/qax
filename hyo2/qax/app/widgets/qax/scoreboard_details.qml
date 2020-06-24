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
            spacing: 14

            RowLayout {
              Layout.fillWidth: true
              Text {
                text: manager.name
                font.bold: true
              }
              Item {
                Layout.fillWidth: true
              }
              Text {
                text: "QA state:"
              }
              Text {
                text: manager.qa_state
                font.bold: true
              }
            }

            ColumnLayout {
              visible: manager.execution_status == 'completed'
              spacing: 4
              Text {
                text: "Messages:"
                color: "grey"
              }
              Repeater {
                model: manager.messages
                TextEdit {
                  text: modelData
                  wrapMode: Text.Wrap
                  Layout.fillWidth: true
                  readOnly: true
                  selectByMouse: true
                }
              }
            }

            ColumnLayout {
              visible: manager.execution_status == 'failed'
              spacing: 4
              Text {
                text: "Error Messages:"
                color: "red"
              }
              TextEdit {
                text: manager.execution_error_message
                wrapMode: Text.Wrap
                color: "red"
                opacity: 0.8
                Layout.fillWidth: true
                readOnly: true
                selectByMouse: true
              }
            }

            ColumnLayout {
              spacing: 4
              Text {
                text: "Input files:"
                color: "grey"
                Layout.fillWidth: true
              }
              Repeater {
                model: manager.input_files
                TextEdit {
                  text: modelData
                  wrapMode: Text.Wrap
                  Layout.fillWidth: true
                  readOnly: true
                  selectByMouse: true
                }
              }
            }



          }
        }

      }
    }


    TabView {
        Tab {
            title: "Data"
            ColumnLayout {
              anchors.fill: parent

              Button {
                visible: manager.data_available
                Layout.alignment: Qt.AlignRight
                text: "Expand all"
                onClicked: {
                  for(var i=0; i < dataModel.rowCount(); i++) {
                      var index = dataModel.index(i,0)
                      recurse_expand(index)
                  }
                }
                function recurse_expand(index) {
                  if(!dataTreeView.isExpanded(index)) {
                      dataTreeView.expand(index)
                  }
                  for(var i=0; i < dataModel.rowCount(index); i++) {
                      var cindex = dataModel.index(i,0, index)
                      recurse_expand(cindex)
                  }
                }

              }

              TreeView {
                id: dataTreeView
                visible: manager.data_available
                // anchors.fill: parent
                Layout.fillWidth: true
                Layout.fillHeight: true
                model: dataModel
                TableViewColumn {
                    role: "display"
                    title: "Name"
                }
              }
              Text {
                visible: !manager.data_available
                text: "No data avaliable for this check"
                color: "grey"
                anchors.horizontalCenter: parent.horizontalCenter
              }
            }
        }
        Tab {
            title: "Map"

            ColumnLayout {
              anchors.fill: parent

              Text {
                visible: !manager.map_data_available
                text: "No map data avaliable for this check"
                color: "grey"
                anchors.horizontalCenter: parent.horizontalCenter
              }

              SplitView {
                visible: manager.map_data_available
                orientation: Qt.Horizontal
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

        }
    }


  }


}
