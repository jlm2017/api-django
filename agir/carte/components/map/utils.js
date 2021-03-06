import FontFaceOnload from "fontfaceonload";

export function getQueryParameterByName(name) {
  const url = window.location.href;
  name = name.replace(/[[\]]/g, "\\$&");
  const regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
    results = regex.exec(url);
  if (!results) return null;
  if (!results[2]) return "";
  return decodeURIComponent(results[2].replace(/\+/g, " "));
}

function deepAssign(target, source) {
  for (let key of Object.keys(source)) {
    if (typeof source[key] === "object") {
      if (!(key in target)) {
        target[key] = {};
      }
      deepAssign(target[key], source[key]);
    } else {
      target[key] = source[key];
    }
  }
}

export function element(tag, children = [], attrs = {}) {
  const elem = document.createElement(tag);
  children
    .map((e) => {
      if (e instanceof Element) {
        return e;
      } else if (e.constructor === String) {
        return document.createTextNode(e);
      }
      return element.apply(null, e);
    })
    .forEach((e) => elem.appendChild(e));
  deepAssign(elem, attrs);
  return elem;
}

export function fontIsLoaded(fontName) {
  return new Promise((resolve, reject) =>
    FontFaceOnload(fontName, {
      success: resolve,
      error: reject,
    })
  );
}

export const ARROW_SIZE = 20;
