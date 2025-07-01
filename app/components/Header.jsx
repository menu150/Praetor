import Link from 'next/link';

export default function Header() {
  return (
    <header className="bg-white shadow-sm py-4 px-6 flex justify-between items-center">
      <h1 className="text-xl font-semibold">Praetor</h1>
      <nav className="space-x-4">
        <Link href="/"><a>Home</a></Link>
        <Link href="/dashboard"><a>Dashboard</a></Link>
        <Link href="/settings"><a>Settings</a></Link>
      </nav>
    </header>
  );
}
