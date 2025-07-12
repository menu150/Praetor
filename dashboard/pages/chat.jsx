import { useState } from 'react'

export default function Chat() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([])

  const sendMessage = async () => {
    if (!input.trim()) return

    setMessages([...messages, { role: 'user', content: input }])
    setInput('')

    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'ApiKey your_secure_key_here'
      },
      body: JSON.stringify({ message: input })
    })

    const data = await res.json()
    const reply = Array.isArray(data.response) ? data.response.join('\n') : data.response
    setMessages(prev => [...prev, { role: 'assistant', content: reply || 'Error' }])
  }

  return (
    <div style={{ padding: '2rem' }}>
      <h1>🧠 Praetor Chat</h1>
      <div style={{ border: '1px solid #ccc', padding: '1rem', height: '300px', overflowY: 'auto' }}>
        {messages.map((msg, i) => (
          <div key={i} style={{ marginBottom: '0.5rem', color: msg.role === 'user' ? 'black' : 'blue' }}>
            <strong>{msg.role === 'user' ? 'You' : 'Praetor'}:</strong> {msg.content}
          </div>
        ))}
      </div>
      <input
        value={input}
        onChange={e => setInput(e.target.value)}
        onKeyDown={e => e.key === 'Enter' && sendMessage()}
        placeholder="Type a message"
        style={{ width: '80%', padding: '0.5rem' }}
      />
      <button onClick={sendMessage} style={{ padding: '0.5rem' }}>Send</button>
    </div>
  )
}
