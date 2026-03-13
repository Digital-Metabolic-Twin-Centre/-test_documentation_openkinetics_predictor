import React from 'react';
import PropTypes from 'prop-types';
import { Card, Row, Col, Form, Button } from 'react-bootstrap';
import MethodDetails from './MethodDetails';
import ExperimentalSwitch from './ExperimentalSwitch';
import '../../../styles/components/PredictionTypeSelect.css';

/**
 * Method selection card shown after the user uploads a valid CSV file.
 *
 * Both the kcat method dropdown and the KM method dropdown are populated from
 * the backend registry (passed down via `allowedKcatMethods`, `allowedKmMethods`,
 * and `methods`).  No method names are hardcoded here.
 */
export default function MethodPicker({
  predictionType,
  allowedKcatMethods,
  allowedKmMethods,
  methods,
  kcatMethod,
  setKcatMethod,
  kmMethod,
  setKmMethod,
  csvFormatInfo,
  useExperimental,
  setUseExperimental,
  onSubmit,
  isSubmitting,
}) {
  const showKcat = predictionType === 'kcat' || predictionType === 'both';
  const showKm = predictionType === 'Km' || predictionType === 'both';

  /**
   * Return the label shown in the dropdown for a given method key.
   * Falls back to the key itself if the registry hasn't loaded yet.
   */
  const methodLabel = (key) =>
    methods?.[key]?.displayName ?? key;

  return (
    <Card className="section-container section-method-selection mb-4">
      <Card.Header as="h3" className="text-center">
        Select Prediction Method(s)
      </Card.Header>
      <Card.Body>
        <Row>
          {showKcat && (
            <Col md={showKm ? 6 : 12} className="mb-3 mb-md-0">
              <div className={`kave-select-wrapper ${kcatMethod ? 'is-selected' : ''}`}>
                <Form.Group controlId="kcatMethod" className="h-100">
                  <Form.Control
                    as="select"
                    disabled={!csvFormatInfo?.csv_type}
                    value={kcatMethod}
                    onChange={(e) => setKcatMethod(e.target.value)}
                    className="kave-select h-100"
                    required
                  >
                    <option value="">Select kcat method...</option>
                    {allowedKcatMethods.map((key) => (
                      <option key={key} value={key}>
                        {methodLabel(key)}
                      </option>
                    ))}
                  </Form.Control>
                </Form.Group>
              </div>
              {kcatMethod && (
                <MethodDetails methodKey={kcatMethod} methods={methods} citationOnly />
              )}
            </Col>
          )}

          {showKm && (
            <Col md={showKcat ? 6 : 12}>
              <div className={`kave-select-wrapper ${kmMethod ? 'is-selected' : ''}`}>
                <Form.Group controlId="kmMethod" className="h-100">
                  <Form.Control
                    as="select"
                    value={kmMethod}
                    disabled={!csvFormatInfo?.csv_type}
                    onChange={(e) => setKmMethod(e.target.value)}
                    className="kave-select h-100"
                    required
                  >
                    <option value="">Select KM method...</option>
                    {allowedKmMethods.map((key) => (
                      <option key={key} value={key}>
                        {methodLabel(key)}
                      </option>
                    ))}
                  </Form.Control>
                </Form.Group>
              </div>
              {kmMethod && (
                <MethodDetails methodKey={kmMethod} methods={methods} citationOnly />
              )}
            </Col>
          )}
        </Row>
      </Card.Body>

      {(kcatMethod || kmMethod) && (
        <Card.Footer className="d-flex justify-content-end align-items-center">
          <ExperimentalSwitch checked={useExperimental} onChange={setUseExperimental} />
          <Button
            className="kave-btn ms-3"
            onClick={onSubmit}
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Submitting…' : 'Submit Job'}
          </Button>
        </Card.Footer>
      )}
    </Card>
  );
}

MethodPicker.propTypes = {
  predictionType: PropTypes.string.isRequired,
  allowedKcatMethods: PropTypes.arrayOf(PropTypes.string).isRequired,
  allowedKmMethods: PropTypes.arrayOf(PropTypes.string).isRequired,
  methods: PropTypes.object,
  kcatMethod: PropTypes.string.isRequired,
  setKcatMethod: PropTypes.func.isRequired,
  kmMethod: PropTypes.string.isRequired,
  setKmMethod: PropTypes.func.isRequired,
  csvFormatInfo: PropTypes.object,
  useExperimental: PropTypes.bool.isRequired,
  setUseExperimental: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
  isSubmitting: PropTypes.bool.isRequired,
};
