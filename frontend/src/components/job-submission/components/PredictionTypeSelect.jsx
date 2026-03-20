import React from 'react';
import PropTypes from 'prop-types';
import { Card, Form } from 'react-bootstrap';
import '../../../styles/components/PredictionTypeSelect.css';

const TARGET_OPTIONS = [
  { key: 'kcat', label: 'Turnover Number (kcat)' },
  { key: 'Km', label: 'Michaelis Constant (KM)' },
  { key: 'kcat/Km', label: 'Catalytic Efficiency (kcat/Km)' },
];

export default function PredictionTypeSelect({ value, onChange }) {
  const selected = new Set(value);

  const toggleTarget = (target) => {
    const next = selected.has(target)
      ? value.filter((t) => t !== target)
      : [...value, target];
    onChange(next);
  };

  return (
    <Card className="section-container section-how-to-use mb-4">
      <Card.Header as="h3" className="text-center">
        What would you like to predict?
      </Card.Header>
      <Card.Body className="d-flex flex-column gap-2">
        {TARGET_OPTIONS.map((option) => (
          <div
            key={option.key}
            className={`kave-target-wrapper ${selected.has(option.key) ? 'is-selected' : ''}`}
          >
            <Form.Check
              type="checkbox"
              id={`target-${option.key}`}
              checked={selected.has(option.key)}
              onChange={() => toggleTarget(option.key)}
              label={option.label}
              className="kave-target-check"
            />
          </div>
        ))}
      </Card.Body>
    </Card>
  );
}

PredictionTypeSelect.propTypes = {
  value: PropTypes.arrayOf(PropTypes.string).isRequired,
  onChange: PropTypes.func.isRequired,
};
