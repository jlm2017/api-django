import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";
import { icons } from "feather-icons";

export const allIcons = Object.keys(icons);

export const RawFeatherIcon = styled.div.attrs(
  ({ name, strokeWidth, color, strokeLinecap, strokeLinejoin, svgStyle }) => {
    const attrs = {
      name,
      "stroke-width": strokeWidth,
      "stroke-linecap": strokeLinecap,
      "stroke-linejoin": strokeLinejoin,
    };
    if (typeof color !== "undefined") {
      attrs.color = color;
    }
    Object.keys(attrs).map((k) => attrs[k] === undefined && delete attrs[k]);

    if (svgStyle !== undefined) {
      attrs.style = Object.keys(svgStyle)
        .map((key) => {
          const cssKey = key.replace(/[A-Z]/g, (m) => `-${m.toLowerCase()}`);
          return `${cssKey}:${svgStyle[key]}`;
        })
        .join(";");
    }

    return {
      dangerouslySetInnerHTML: { __html: icons[name].toSvg(attrs) },
    };
  }
)`
  display: inline-flex;
  align-items: center;

  svg {
    position: relative;
    width: ${(props) => props.width};
    height: ${(props) => props.height};
    top: ${(props) => props.top};
  }
`;

RawFeatherIcon.propTypes = {
  name: PropTypes.oneOf(allIcons),
  color: PropTypes.string,
  width: PropTypes.string,
  height: PropTypes.string,
  strokeWidth: PropTypes.number,
  strokeLinecap: PropTypes.number,
  strokeLinejoin: PropTypes.number,
  style: PropTypes.objectOf(PropTypes.string),
};

/*
La taille de police de base est de 16 pixels.
Les grands icônes doivent faire 24 pixels (1.5rem)
Les petits icônes doivent faire 16 pixels (1rem)
 */

const FeatherIcon = ({ name, small, color, inline }) => {
  // stroke dimensions
  const strokeWidth = !small ? 2 : 1.33;

  // positionning dimensions
  const dimension = !small ? "1.5rem" : "1rem";

  const top = inline ? (!small ? "0.3rem" : "0.15rem") : "0";

  return (
    <RawFeatherIcon
      color={color}
      name={name}
      width={dimension}
      height={dimension}
      top={top}
      strokeWidth={strokeWidth}
    />
  );
};
FeatherIcon.propTypes = {
  name: PropTypes.oneOf(allIcons),
  small: PropTypes.bool,
  color: PropTypes.string,
  inline: PropTypes.bool,
};

FeatherIcon.defaultProps = {
  small: false,
  inline: false,
};

FeatherIcon.RawFeatherIcon = RawFeatherIcon;
FeatherIcon.allIcons = allIcons;

export default FeatherIcon;

export const IconList = styled.ul`
  padding-left: 1.5rem;
`;

export const IconListItem = styled.li`
  list-style: none;
  position: relative;
  margin-bottom: 0.5rem;
  &:before {
    // prettier-ignore
    content: url('data:image/svg+xml;utf8,${(props) =>
      icons[props.name].toSvg({ height: 16, color: "grey" })}');
    height: 1rem;
    position: absolute;
    top: 0.15rem;
    left: -1.75rem;
  }
`;
