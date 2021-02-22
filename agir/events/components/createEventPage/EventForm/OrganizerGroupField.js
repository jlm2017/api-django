import PropTypes from "prop-types";
import React, { useCallback } from "react";

import SelectField from "@agir/front/formComponents/SelectField";

const OrganizerGroupField = (props) => {
  const { onChange, value, name, groups, error, required, disabled } = props;

  const handleChange = useCallback(
    (selected) => {
      onChange && onChange(name, selected);
    },
    [name, onChange]
  );

  return (
    <SelectField
      label="Organisateur"
      id={name}
      name={name}
      value={value}
      onChange={handleChange}
      options={groups}
      placeholder="Choisissez un organisateur"
      required={required}
      disabled={disabled}
      error={error}
    />
  );
};
OrganizerGroupField.propTypes = {
  onChange: PropTypes.func.isRequired,
  value: PropTypes.object,
  name: PropTypes.string.isRequired,
  groups: PropTypes.arrayOf(PropTypes.object),
  error: PropTypes.string,
  required: PropTypes.bool,
  disabled: PropTypes.bool,
};
export default OrganizerGroupField;
