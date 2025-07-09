export const metadata = { title: 'Praetor Dashboard' };
export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <script src="https://cdn.tailwindcss.com"></script>
      </head>
      <body className="m-0 p-0">
        {children}
      </body>
    </html>
  );
}
