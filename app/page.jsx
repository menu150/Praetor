import React, { useEffect, useState } from 'react';
import SkillToggle from '../components/SkillToggle';

export default function DashboardPage() {
  const [skills, setSkills] = useState([]);

  useEffect(() => {
    fetch('/api/skills')
      .then(res => res.json())
      .then(data => setSkills(data));
  }, []);

  const handleToggle = async (trigger, enabled) => {
    await fetch('/api/skills/toggle', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ trigger, enabled })
    });
    setSkills(s => s.map(sk => sk.trigger === trigger ? { ...sk, enabled } : sk));
  };

  return (
    <div className="p-4 space-y-4">
      <h1 className="text-2xl font-bold">Skills</h1>
      <div className="grid grid-cols-1 gap-2">
        {skills.map(sk => (
          <SkillToggle
            key={sk.trigger}
            trigger={sk.trigger}
            enabled={Boolean(sk.enabled)}
            onChange={handleToggle}
          />
        ))}
      </div>
    </div>
  );
}
