import PropTypes from "prop-types";
import React, { useCallback, useMemo, useState } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { useResponsiveMemo } from "@agir/front/genericComponents/grid";

import Button from "@agir/front/genericComponents/Button";
import Panel from "@agir/front/genericComponents/Panel";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import { EVENT_TYPES } from "./eventForm.config";

const StyledOption = styled.li`
  display: flex;
  flex-flow: row nowrap;
  height: 2.75rem;
  align-items: center;
  font-size: 0.813rem;
  line-height: 1.3;
  color: ${({ $selected }) => ($selected ? style.primary500 : style.black1000)};
  font-weight: ${({ $selected }) => ($selected ? 600 : 400)};
  cursor: ${({ $selected }) => ($selected ? "default" : "pointer")};

  button {
    display: ${({ $selected }) => ($selected ? "none" : "inline")};
    margin-left: auto;
  }

  span {
    color: ${style.primary500};
    display: inline-block;
    font-size: 1.5rem;
    padding-right: 0.5rem;
  }
`;

const StyledOptions = styled.div`
  display: flex;
  flex-flow: column nowrap;
  padding-top: 0.5rem;

  ul {
    padding: 0;
    list-style: none;

    strong {
      display: block;
      height: 2.75rem;
      font-weight: 600;
      font-size: 1rem;
      line-height: 1.5;
      display: flex;
      align-items: center;
    }
  }
`;

const StyledDefaultOption = styled.button``;
const StyledDefaultOptions = styled.div`
  display: flex;
  flex-flow: row wrap;
  gap: 0.5rem;

  button {
    border-radius: 0;
    border: none;
    box-shadow: none;
    padding: 0;
    background-color: transparent;
    font-size: 0.813rem;
    font-weight: 600;
    cursor: pointer;
    color: ${style.primary500};

    &[disabled],
    &[disabled]:hover {
      opacity: 0.5;
      cursor: default;
    }
  }

  ${StyledDefaultOption} {
    padding: 0.5rem 0.75rem;
    color: ${style.black1000};
    display: inline-grid;
    grid-gap: 0.5rem;
    grid-template-columns: auto auto auto;
    align-items: center;
    border: 1px solid ${style.black100};

    &:hover {
      background-color: ${style.black50};
    }

    &[disabled],
    &[disabled]:hover {
      opacity: 1;
      background-color: transparent;
      cursor: default;
    }
  }
`;

const StyledField = styled.div`
  label {
    font-size: 0.813rem;
    font-weight: 600;
    line-height: 1;
    padding: 4px 0;
  }
`;

const SubtypeOption = (props) => {
  const { option, onClick, selected } = props;

  const handleClick = useCallback(() => {
    onClick(option);
  }, [option, onClick]);

  return (
    <StyledOption
      $selected={selected}
      title={option.description}
      onClick={handleClick}
    >
      <span className={`fa fa-${option.iconName || "calendar"}`} />
      {option.description[0].toUpperCase()}
      {option.description.slice(1)}
      <Button type="button" color="choose" onClick={handleClick} small>
        Choisir
      </Button>
    </StyledOption>
  );
};

const DefaultOption = (props) => {
  const { option, onClick, selected, disabled } = props;

  const handleClick = useCallback(() => {
    onClick(option);
  }, [option, onClick]);

  return (
    <StyledDefaultOption
      type="button"
      title={option.description}
      color="choose"
      onClick={handleClick}
      disabled={disabled}
      small
    >
      <RawFeatherIcon
        name={selected ? "check" : "circle"}
        width="1rem"
        height="1rem"
      />
      <span
        className={`fa fa-${option.iconName || "calendar"}`}
        style={{ color: option.color }}
      />
      {option.description[0].toUpperCase()}
      {option.description.slice(1)}
    </StyledDefaultOption>
  );
};
SubtypeOption.propTypes = DefaultOption.propTypes = {
  option: PropTypes.shape({
    id: PropTypes.number,
    label: PropTypes.string,
    iconName: PropTypes.string,
    color: PropTypes.String,
    description: PropTypes.string,
  }),
  onClick: PropTypes.func,
  selected: PropTypes.bool,
  disabled: PropTypes.bool,
};

const SubtypeField = (props) => {
  const { onChange, value, name, error, disabled } = props;
  const [isPanelOpen, setIsPanelOpen] = useState(false);
  const openPanel = useCallback(() => {
    setIsPanelOpen(true);
  }, []);
  const closePanel = useCallback(() => {
    setIsPanelOpen(false);
  }, []);
  const panelPosition = useResponsiveMemo("right", "left");

  const handleChange = useCallback(
    (subtype) => {
      onChange(name, subtype);
      setIsPanelOpen(false);
    },
    [onChange, name]
  );

  const subtypes = useMemo(
    () => (Array.isArray(props.options) ? props.options : []),
    [props.options]
  );

  const options = useMemo(() => {
    const categories = { ...EVENT_TYPES };
    subtypes.forEach((subtype) => {
      const category =
        subtype.type && categories[subtype.type] ? subtype.type : "O";
      categories[category].subtypes = categories[category].subtypes || [];
      categories[category].subtypes.push(subtype);
    });

    return Object.values(categories).filter((category) =>
      Array.isArray(category.subtypes)
    );
  }, [subtypes]);

  const defaultOptions = useMemo(() => subtypes.slice(0, 4), [subtypes]);

  return (
    <StyledField>
      <label htmlFor={name}>Type d'événement</label>
      {error && (
        <p
          style={{
            color: style.redNSP,
            fontSize: "0.813rem",
          }}
        >
          {error}
        </p>
      )}
      <StyledDefaultOptions>
        {value ? (
          <DefaultOption
            key={value.id}
            option={value}
            onClick={openPanel}
            selected
          />
        ) : (
          defaultOptions.map((subtype) => (
            <DefaultOption
              key={subtype.id}
              onClick={handleChange}
              option={subtype}
              disabled={disabled}
            />
          ))
        )}
        <button onClick={openPanel} type="button" disabled={disabled}>
          {value ? "Changer" : "+ d'options"}
        </button>
      </StyledDefaultOptions>
      <Panel
        position={panelPosition}
        shouldShow={isPanelOpen}
        onClose={closePanel}
        onBack={closePanel}
        title="Type de l'événement"
        noScroll
      >
        <StyledOptions>
          {options.map((category) => (
            <ul key={category.label}>
              <strong title={category.description}>{category.label}</strong>
              {category.subtypes.map((subtype) => (
                <SubtypeOption
                  key={subtype.id}
                  onClick={handleChange}
                  option={subtype}
                  selected={!!value && value.id === subtype.id}
                />
              ))}
            </ul>
          ))}
        </StyledOptions>
      </Panel>
    </StyledField>
  );
};
SubtypeField.propTypes = {
  onChange: PropTypes.func.isRequired,
  value: PropTypes.object,
  name: PropTypes.string.isRequired,
  options: PropTypes.arrayOf(PropTypes.object),
  error: PropTypes.string,
  disabled: PropTypes.bool,
  required: PropTypes.bool,
};
export default SubtypeField;
