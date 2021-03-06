import PropTypes from "prop-types";
import React, { useCallback, useEffect, useState } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import DateTimeField from "@agir/front/formComponents/DateTimeField";
import SelectField from "@agir/front/formComponents/SelectField";

import { EVENT_DEFAULT_DURATIONS } from "./eventForm.config";

const Field = styled.div`
  display: inline-grid;
  grid-template-columns: auto 160px;
  grid-auto-rows: auto auto;
  grid-gap: 0.5rem;

  @media (max-width: ${style.collapse}px) {
    display: grid;
    grid-template-columns: 1fr;
  }
`;

const DateField = (props) => {
  const { onChange, startTime, endTime, error, required, disabled } = props;
  const [duration, setDuration] = useState(EVENT_DEFAULT_DURATIONS[0]);

  const updateStartTime = useCallback(
    (startTime) => {
      let start = new Date(startTime).valueOf();
      let end = new Date(endTime).valueOf();
      if (duration && duration.value) {
        end = start + duration.value * 60000;
      }
      if (start > end) {
        end = start;
      }
      start = new Date(start).toISOString();
      end = new Date(end).toISOString();
      onChange(start, end);
    },
    [endTime, duration, onChange]
  );

  const updateDuration = useCallback((duration) => {
    setDuration(duration);
  }, []);

  const updateEndTime = useCallback(
    (endTime) => {
      let start = new Date(startTime).valueOf();
      let end = new Date(endTime).valueOf();
      if (start > end) {
        start = end;
      }
      start = new Date(start).toISOString();
      end = new Date(end).toISOString();
      onChange(start, end);
    },
    [startTime, onChange]
  );

  useEffect(() => {
    if (duration && duration.value) {
      updateStartTime(startTime);
    }
  }, [duration, updateStartTime, startTime]);

  return (
    <Field>
      <div>
        <DateTimeField
          label={`Date et heure ${
            duration.value === null ? "de début" : ""
          }`.trim()}
          value={startTime}
          onChange={updateStartTime}
          error={error}
          required={required}
          disabled={disabled}
        />
      </div>
      <div>
        <SelectField
          label="Durée"
          value={duration}
          onChange={updateDuration}
          options={EVENT_DEFAULT_DURATIONS}
          disabled={disabled}
        />
      </div>
      {duration.value === null && (
        <div>
          <DateTimeField
            label="Date et heure de fin"
            value={endTime}
            onChange={updateEndTime}
            disabled={disabled}
            required={required}
          />
        </div>
      )}
    </Field>
  );
};
DateField.propTypes = {
  onChange: PropTypes.func.isRequired,
  startTime: PropTypes.string,
  endTime: PropTypes.string,
  error: PropTypes.string,
  required: PropTypes.bool,
  disabled: PropTypes.bool,
};
export default DateField;
