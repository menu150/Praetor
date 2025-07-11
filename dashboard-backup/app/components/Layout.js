import Sidebar from './Sidebar';
import Header  from './Header';

export default function Layout({ children }) {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <main className="flex-1 bg-gray-100 p-6">
        <Header />
        {children}
      </main>
    </div>
  );
}
