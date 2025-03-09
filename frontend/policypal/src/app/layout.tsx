import { UserProvider } from '@/contexts/UserContext';
import './globals.css';
import Navbar from '@/components/Navbar';
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50">
        <UserProvider>
          <div className="flex flex-col min-h-screen">
            <header className="bg-blue-600 text-white">
              <div className="max-w-7xl mx-auto">
                <Navbar />
              </div>
            </header>
            <main className="flex-grow container mx-auto px-4 py-8">
              {children}
            </main>
            <footer className="bg-gray-100 py-4">
              <div className="container mx-auto px-4 text-center text-gray-600">
                <p>&copy; {new Date().getFullYear()} Policy Pal</p>
              </div>
            </footer>
          </div>
        </UserProvider>
      </body>
    </html>
  );
}