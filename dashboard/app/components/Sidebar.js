import Link from 'next/link';

const navItems = ['Overview','Console','Skills','Integrations','Settings'];

export default function Sidebar() {
  return (
    <aside className="w-64 bg-white border-r p-4">
      <h2 className="text-xl font-bold mb-6">Praetor Dashboard</h2>
      <nav>
        <ul>
          {navItems.map(i=>(
            <li key={i} className="mb-2">
              <Link href={`/${i.toLowerCase()}`}>
                <a className="hover:text-blue-600">{i}</a>
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
}
