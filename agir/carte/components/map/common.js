import Map from "ol/Map";
import View from "ol/View";
import TileLayer from "ol/layer/Tile";
import OSM from "ol/source/OSM";
import Style from "ol/style/Style";
import Text from "ol/style/Text";
import Fill from "ol/style/Fill";
import Icon from "ol/style/Icon";
import Overlay from "ol/Overlay";
import * as proj from "ol/proj";
import Feature from "ol/Feature";
import VectorSource from "ol/source/Vector";
import Point from "ol/geom/Point";
import VectorLayer from "ol/layer/Vector";
import Zoom from "ol/control/Zoom";
import fontawesome from "fontawesome";

import style from "@agir/front/genericComponents/_variables.scss";

import markerIcon from "./marker.svg";
import markerIconBg from "./marker_bg.svg";

import { element } from "./utils";

const ARROW_SIZE = 20;

export function setUpMap(elementId, layers) {
  const view = new View({
    center: proj.fromLonLat([2, 47]),
    zoom: 6,
  });
  return new Map({
    target: elementId,
    layers: [
      new TileLayer({
        source: new OSM({
          attributions: [
            '&#169; les contributeurs <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>',
          ],
        }),
      }),
      ...layers,
    ],
    view,
  });
}

export function fitBounds(map, bounds) {
  map
    .getView()
    .fit(proj.transformExtent(bounds, "EPSG:4326", "EPSG:3857"), map.getSize());
}

export function setUpPopup(map) {
  const popupElement = element("div", [], {
    className: "map_popup",
  });
  popupElement.addEventListener("mousedown", function (evt) {
    evt.stopPropagation();
  });

  const popup = new Overlay({
    element: popupElement,
    positioning: "bottom-center",
    offset: [0, -ARROW_SIZE],
    stopEvent: true,
  });

  map.addOverlay(popup);

  map.on("singleclick", function (evt) {
    popup.setPosition();
    map.forEachFeatureAtPixel(evt.pixel, function (feature) {
      const coords = feature.getGeometry().getCoordinates();
      if (feature.get("popupContent")) {
        popup.getElement().innerHTML = feature.get("popupContent");
        popup.setOffset([0, feature.get("popupAnchor")]);
        popup.setPosition(coords);
        return true;
      }
    });
  });

  map.on("pointermove", function (evt) {
    const hit = this.forEachFeatureAtPixel(evt.pixel, function (feature) {
      return !!feature.get("popupContent");
    });
    if (hit) {
      this.getTargetElement().style.cursor = "pointer";
    } else {
      this.getTargetElement().style.cursor = "";
    }
  });
}

export function makeStyle(config, options = {}) {
  options = Object.assign({ color: true }, options);

  if (config.color && config.iconName) {
    return [
      new Style({
        image: new Icon({
          opacity: 1,
          src: markerIcon,
          color: options.color ? config.color : style.primary500,
          scale: 0.75,
          anchor: [0.5, 1],
        }),
      }),
      new Style({
        image: new Icon({
          opacity: 1,
          src: markerIconBg,
          scale: 0.75,
          anchor: [0.5, 1],
        }),
      }),
      new Style({
        text: new Text({
          offsetY: -21,
          text: fontawesome(config.iconName),
          font: "normal 16px FontAwesome",
          fill: new Fill({
            color: "#FFFFFF",
          }),
          scale: 0.75,
        }),
      }),
    ];
  } else if (style.iconUrl && style.iconAnchor) {
    return new Style({
      image: new Icon({
        anchor: style.iconAnchor,
        anchorXUnits: "pixels",
        anchorYUnits: "pixels",
        opacity: 1,
        src: style.iconUrl,
      }),
    });
  }

  return null;
}

export function createMap(center, zoom, target, iconConfiguration, isStatic) {
  const styles = iconConfiguration
    ? makeStyle(iconConfiguration)
    : [
        new Style({
          image: new Icon({
            opacity: 1,
            src: markerIcon,
            color: style.primary500,
            scale: 0.75,
            anchor: [0.5, 1],
          }),
        }),
        new Style({
          image: new Icon({
            opacity: 1,
            src: markerIconBg,
            scale: 0.75,
            anchor: [0.5, 1],
          }),
        }),
      ];
  const feature = new Feature({
    geometry: new Point(proj.fromLonLat(center)),
  });
  feature.setStyle(styles);
  const map = new Map({
    target,
    controls: isStatic ? [] : [new Zoom()],
    interactions: isStatic ? [] : undefined,
    layers: [
      new TileLayer({
        source: new OSM({
          attributions: [
            '&#169; les contributeurs <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>',
          ],
        }),
      }),
      new VectorLayer({
        source: new VectorSource({ features: [feature] }),
      }),
    ],
    view: new View({
      center: proj.fromLonLat(center),
      zoom,
    }),
  });

  return map;
}
