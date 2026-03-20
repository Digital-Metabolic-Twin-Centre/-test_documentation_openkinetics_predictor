import React from 'react';
import PropTypes from 'prop-types';
import { Card, Row, Col, Form, Button } from 'react-bootstrap';
import MethodDetails from './MethodDetails';
import ExperimentalSwitch from './ExperimentalSwitch';
import '../../../styles/components/PredictionTypeSelect.css';

const TARGET_ORDER = ['kcat', 'Km', 'kcat/Km'];

const TARGET_LABELS = {
  kcat: 'kcat',
  Km: 'KM',
  'kcat/Km': 'kcat/Km',
};

export default function MethodPicker({
  selectedTargets,
  allowedMethodsByTarget,
  methods,
  targetMethods,
  setTargetMethod,
  csvFormatInfo,
  useExperimental,
  setUseExperimental,
  onSubmit,
  isSubmitting,
  allSelectedTargetsHaveMethods,
}) {
  const visibleTargets = TARGET_ORDER.filter((target) => selectedTargets.includes(target));

  const methodLabel = (key) => methods?.[key]?.displayName ?? key;

  return (
    <Card className="section-container section-method-selection mb-4">
      <Card.Header as="h3" className="text-center">
        Select Prediction Method(s)
      </Card.Header>
      <Card.Body>
        <Row>
          {visibleTargets.map((target) => (
            <Col key={target} md={visibleTargets.length > 1 ? 6 : 12} className="mb-3">
              <div className={`kave-select-wrapper ${targetMethods[target] ? 'is-selected' : ''}`}>
                <Form.Group controlId={`method-${target.replace('/', '-')}`} className="h-100">
                  <Form.Label className="mb-2">
                    Method for {TARGET_LABELS[target]}
                  </Form.Label>
                  <Form.Control
                    as="select"
                    disabled={!csvFormatInfo?.csv_type}
                    value={targetMethods[target] || ''}
                    onChange={(e) => setTargetMethod(target, e.target.value)}
                    className="kave-select h-100"
                    required
                  >
                    <option value="">Select method...</option>
                    {(allowedMethodsByTarget[target] || []).map((key) => (
                      <option key={key} value={key}>
                        {methodLabel(key)}
                      </option>
                    ))}
                  </Form.Control>
                </Form.Group>
              </div>
              {targetMethods[target] && (
                <MethodDetails methodKey={targetMethods[target]} methods={methods} citationOnly />
              )}
            </Col>
          ))}
        </Row>
      </Card.Body>

      {visibleTargets.length > 0 && (
        <Card.Footer className="d-flex justify-content-end align-items-center">
          <ExperimentalSwitch checked={useExperimental} onChange={setUseExperimental} />
          <Button
            className="kave-btn ms-3"
            onClick={onSubmit}
            disabled={isSubmitting || !allSelectedTargetsHaveMethods}
          >
            {isSubmitting ? 'Submitting…' : 'Submit Job'}
          </Button>
        </Card.Footer>
      )}
    </Card>
  );
}

MethodPicker.propTypes = {
  selectedTargets: PropTypes.arrayOf(PropTypes.string).isRequired,
  allowedMethodsByTarget: PropTypes.object.isRequired,
  methods: PropTypes.object,
  targetMethods: PropTypes.object.isRequired,
  setTargetMethod: PropTypes.func.isRequired,
  csvFormatInfo: PropTypes.object,
  useExperimental: PropTypes.bool.isRequired,
  setUseExperimental: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
  isSubmitting: PropTypes.bool.isRequired,
  allSelectedTargetsHaveMethods: PropTypes.bool.isRequired,
};
