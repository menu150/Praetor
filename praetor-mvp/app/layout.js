import '../styles/globals.css';            // your Tailwind imports
import Header from './components/Header';
import Footer from './components/Footer';

export const metadata = {
  title: 'Praetor Dashboard',
  description: 'Your AI-driven operations hub',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col">
        <Header />
        <main className="flex-1 p-6">
          {children}
        </main>
        <Footer />
      </body>
    </html>
  );
}
