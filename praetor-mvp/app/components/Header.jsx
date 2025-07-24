import Link from 'next/link';

export default function Header() {
  return (
    <header className="bg-white shadow-sm py-4 px-6 flex justify-between items-center">
      <h1 className="text-xl font-semibold">Praetor</h1>
      <nav className="space-x-4">
        <Link href="/">Home</Link>
        <Link href="/dashboard">Dashboard</Link>
        <Link href="/settings">Settings</Link>
        <Link href="/chat">🧠 Chat</Link>
      </nav>
    </header>
  );
}
