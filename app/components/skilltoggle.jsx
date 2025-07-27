/*
1) New React component: app/components/SkillToggle.jsx
*/
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

/*
2) API routes under dashboard/api/skills
*/
// GET /api/skills/index.js
import { get_connection, init_db } from '../../../memory_core';
export async function GET() {
  const conn = get_connection();
  const rows = conn.prepare(
    `SELECT trigger, action, path_or_command, enabled FROM skills`
  ).all();

  return new Response(JSON.stringify(rows), {
    headers: { 'Content-Type': 'application/json' }
  });
}

// POST /api/skills/toggle.js
import { get_connection } from '../../../memory_core';
export async function POST(req) {
  const { trigger, enabled } = await req.json();
  const conn = get_connection();
  conn.prepare(
    `UPDATE skills SET enabled = ? WHERE trigger = ?`
  ).run(enabled ? 1 : 0, trigger);

  return new Response(JSON.stringify({ trigger, enabled }), {
    headers: { 'Content-Type': 'application/json' }
  });
}

/*
3) Update dashboard UI: app/dashboard/page.jsx
*/
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
