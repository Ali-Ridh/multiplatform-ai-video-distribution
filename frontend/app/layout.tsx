import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Opus Dashboard',
  description: 'Video Pipeline Management Dashboard',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="font-sans bg-gray-50 text-gray-900">
        {children}
      </body>
    </html>
  );
}
