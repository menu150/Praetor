import React from 'react';

export default function SkillToggle({ trigger, enabled, onChange }) {
  return (
    <label className="flex items-center space-x-2">
      <span className="capitalize">{trigger}</span>
      <input
        type="checkbox"
        checked={enabled}
        onChange={e => onChange(trigger, e.target.checked)}
        className="toggle toggle-primary"
      />
    </label>
  );
}
