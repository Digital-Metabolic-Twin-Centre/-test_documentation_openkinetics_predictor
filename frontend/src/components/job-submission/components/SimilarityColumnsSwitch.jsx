import React from 'react';
import PropTypes from 'prop-types';
import { Form, OverlayTrigger, Tooltip } from 'react-bootstrap';
import { InfoCircleFill } from 'react-bootstrap-icons';

const SimilarityColumnsTooltip = (
  <Tooltip id="similarity-columns-tooltip" className="exp-tooltip">
    Add per-row kcat training-set similarity columns (mean and max) to the final
    output CSV. Disable this to skip the MMseqs enrichment step entirely.
  </Tooltip>
);

export default function SimilarityColumnsSwitch({ checked, onChange }) {
  return (
    <Form.Group controlId="includeSimilarityColumns" className="exp-switch-group">
      <div className="d-flex align-items-center gap-2">
        <Form.Check
          type="switch"
          label="Include similarity columns"
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
          className="exp-switch"
        />

        <OverlayTrigger
          placement="right"
          overlay={SimilarityColumnsTooltip}
          delay={{ show: 150, hide: 0 }}
          trigger={['hover', 'focus']}
        >
          <button
            type="button"
            className="exp-info-btn"
            aria-label="What does ‘Include similarity columns’ do?"
          >
            <InfoCircleFill size={16} aria-hidden="true" />
          </button>
        </OverlayTrigger>
      </div>
    </Form.Group>
  );
}

SimilarityColumnsSwitch.propTypes = {
  checked: PropTypes.bool.isRequired,
  onChange: PropTypes.func.isRequired,
};

